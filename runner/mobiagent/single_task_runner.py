#!/usr/bin/env python3
"""
單任務運行器 - 用於處理單個任務而不是整個 task.json
"""

import argparse
import json
import os
import sys
from pathlib import Path

# 添加父目錄到 Python 路徑以導入 mobiagent 模組
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mobiagent import init, AndroidDevice, task_in_app, get_app_package_name


def run_single_task(
    task_description: str,
    service_ip: str = "localhost",
    decider_port: int = 8000,
    grounder_port: int = 8001,
    planner_port: int = 8002,
    data_dir: str = None
) -> int:
    """
    運行單個任務
    
    Args:
        task_description: 任務描述
        service_ip: 服務 IP
        decider_port: 決策服務端口
        grounder_port: 定位服務端口
        planner_port: 規劃服務端口
        data_dir: 數據目錄，如果為 None 則自動創建
        
    Returns:
        返回碼，0 表示成功
    """
    try:
        # 初始化服務
        init(service_ip, decider_port, grounder_port, planner_port)

        # 在創建新設備實例前，先嘗試重置現有的 UiAutomation 連接
        try:
            import uiautomator2 as u2
            # 嘗試重置現有的連接
            temp_device = u2.connect()
            temp_device.reset_uiautomator()
            print("已重置 UiAutomation 連接")
        except Exception as e:
            print(f"重置 UiAutomation 連接失敗 (可能沒有現有連接): {e}")

        # 創建 Android 設備實例
        device = AndroidDevice()
        print(f"連接到設備")
        
        # 設置數據目錄
        if data_dir is None:
            data_base_dir = os.path.join(os.path.dirname(__file__), 'data')
            if not os.path.exists(data_base_dir):
                os.makedirs(data_base_dir)
            
            # 找到下一個可用的目錄索引
            existing_dirs = [d for d in os.listdir(data_base_dir) 
                           if os.path.isdir(os.path.join(data_base_dir, d)) and d.isdigit()]
            if existing_dirs:
                data_index = max(int(d) for d in existing_dirs) + 1
            else:
                data_index = 1
            data_dir = os.path.join(data_base_dir, str(data_index))
            os.makedirs(data_dir)
        
        # 獲取應用包名和任務描述
        app_name, package_name, new_task_description = get_app_package_name(task_description)
        
        # 啟動應用
        device.app_start(package_name)
        print(f"開始任務 '{new_task_description}' 在應用 '{app_name}' 中")
        
        # 執行任務
        task_in_app(app_name, task_description, new_task_description, device, data_dir, True)

        print(f"任務完成，結果保存在: {data_dir}")

        # 任務完成後清理 UiAutomation 連接
        try:
            if device and hasattr(device, 'd'):
                device.d.reset_uiautomator()
                print("已清理 UiAutomation 連接")
        except Exception as e:
            print(f"清理 UiAutomation 連接失敗: {e}")

        return 0

    except Exception as e:
        print(f"任務執行失敗: {e}", file=sys.stderr)

        # 發生異常時也要嘗試清理
        try:
            import uiautomator2 as u2
            temp_device = u2.connect()
            temp_device.reset_uiautomator()
            print("已清理 UiAutomation 連接 (異常情況)")
        except Exception as cleanup_e:
            print(f"清理 UiAutomation 連接失敗 (異常情況): {cleanup_e}")

        return 1


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="MobiAgent 單任務運行器")
    parser.add_argument("--service_ip", type=str, default="localhost", 
                       help="服務 IP (默認: localhost)")
    parser.add_argument("--decider_port", type=int, default=8100, 
                       help="決策服務端口 (默認: 8100)")
    parser.add_argument("--grounder_port", type=int, default=8101, 
                       help="定位服務端口 (默認: 8101)")
    parser.add_argument("--planner_port", type=int, default=8102, 
                       help="規劃服務端口 (默認: 8102)")
    parser.add_argument("--data_dir", type=str, default=None, 
                       help="數據目錄 (默認: 自動創建)")
    parser.add_argument("task_description", 
                       help="任務描述")
    
    args = parser.parse_args()
    
    return run_single_task(
        task_description=args.task_description,
        service_ip=args.service_ip,
        decider_port=args.decider_port,
        grounder_port=args.grounder_port,
        planner_port=args.planner_port,
        data_dir=args.data_dir
    )


if __name__ == "__main__":
    sys.exit(main())
