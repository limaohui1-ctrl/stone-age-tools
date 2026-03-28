#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石器时代网络稳定性优化工具包 - 一键部署脚本
简化安装、配置和部署过程

功能:
1. 自动检测系统环境和依赖
2. 一键安装所有必要组件
3. 智能配置和优化
4. 验证安装和功能测试
5. 提供卸载和更新功能

设计原则:
- 简单易用，一键完成
- 智能检测，自动修复
- 完整验证，确保可用
- 跨平台支持，广泛兼容
"""

import os
import sys
import time
import json
import shutil
import logging
import platform
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('部署日志.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SystemInfo:
    """系统信息收集类"""
    
    @staticmethod
    def get_platform_info() -> Dict:
        """获取平台信息"""
        info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
        }
        
        # 添加更多详细信息
        if platform.system() == "Windows":
            info["windows_version"] = platform.win32_ver()
        elif platform.system() == "Linux":
            info["linux_distribution"] = platform.freedesktop_os_release() if hasattr(platform, 'freedesktop_os_release') else {}
        
        return info
    
    @staticmethod
    def check_python_version(min_version: Tuple[int, int] = (3, 8)) -> bool:
        """检查Python版本"""
        current = sys.version_info
        required = min_version
        
        if current.major > required[0] or (current.major == required[0] and current.minor >= required[1]):
            return True
        else:
            logger.error(f"Python版本过低: {current.major}.{current.minor}，需要 {required[0]}.{required[1]}+")
            return False
    
    @staticmethod
    def check_disk_space(path: str, required_mb: int = 100) -> Tuple[bool, float]:
        """检查磁盘空间"""
        try:
            if platform.system() == "Windows":
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(path), None, None, ctypes.pointer(free_bytes)
                )
                free_mb = free_bytes.value / (1024 * 1024)
            else:
                stat = os.statvfs(path)
                free_mb = (stat.f_bavail * stat.f_frsize) / (1024 * 1024)
            
            has_space = free_mb >= required_mb
            return has_space, free_mb
            
        except Exception as e:
            logger.warning(f"检查磁盘空间失败: {e}")
            return True, 0  # 假设有足够空间


class DependencyManager:
    """依赖管理类"""
    
    REQUIRED_PACKAGES = [
        "ping3>=3.0.0",  # 网络检测
    ]
    
    OPTIONAL_PACKAGES = [
        "matplotlib>=3.5.0",  # 图表绘制
        "pandas>=1.4.0",      # 数据分析
        "numpy>=1.21.0",      # 数值计算
    ]
    
    @staticmethod
    def check_pip_available() -> bool:
        """检查pip是否可用"""
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                          capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    @staticmethod
    def install_package(package_spec: str, upgrade: bool = False) -> bool:
        """安装Python包"""
        cmd = [sys.executable, "-m", "pip", "install"]
        
        if upgrade:
            cmd.append("--upgrade")
        
        cmd.append(package_spec)
        
        try:
            logger.info(f"安装包: {package_spec}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"安装成功: {package_spec}")
            logger.debug(f"输出: {result.stdout[:200]}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"安装失败 {package_spec}: {e}")
            logger.error(f"错误输出: {e.stderr}")
            return False
    
    @staticmethod
    def check_package_installed(package_name: str) -> bool:
        """检查包是否已安装"""
        try:
            __import__(package_name.replace("-", "_"))
            return True
        except ImportError:
            return False
    
    @staticmethod
    def install_all_required() -> Dict[str, bool]:
        """安装所有必需包"""
        results = {}
        
        if not DependencyManager.check_pip_available():
            logger.error("pip不可用，无法安装依赖")
            return {pkg: False for pkg in DependencyManager.REQUIRED_PACKAGES}
        
        for package_spec in DependencyManager.REQUIRED_PACKAGES:
            # 提取包名
            package_name = package_spec.split(">")[0].split("=")[0].strip()
            
            # 检查是否已安装
            if DependencyManager.check_package_installed(package_name):
                logger.info(f"包已安装: {package_name}")
                results[package_spec] = True
                continue
            
            # 安装包
            success = DependencyManager.install_package(package_spec)
            results[package_spec] = success
        
        return results
    
    @staticmethod
    def install_optional() -> Dict[str, bool]:
        """安装可选包"""
        results = {}
        
        for package_spec in DependencyManager.OPTIONAL_PACKAGES:
            package_name = package_spec.split(">")[0].split("=")[0].strip()
            
            if DependencyManager.check_package_installed(package_name):
                logger.info(f"可选包已安装: {package_name}")
                results[package_spec] = True
                continue
            
            success = DependencyManager.install_package(package_spec)
            results[package_spec] = success
        
        return results


class ConfigurationManager:
    """配置管理类"""
    
    DEFAULT_CONFIGS = {
        "集成配置.json": {
            "module_interaction": {
                "network_to_retry": True,
                "stuck_to_network": True,
                "retry_to_anti_stuck": True,
                "shared_state": True,
            },
            "performance_optimization": {
                "monitoring_interval": 3.0,
                "data_retention_days": 7,
                "max_log_size_mb": 100,
                "auto_cleanup": True,
            }
        },
        "网络监控配置.json": {
            "check_interval": 5.0,
            "ping_timeout": 3.0,
            "event_thresholds": {
                "high_latency": 200,
                "packet_loss_warning": 10,
                "packet_loss_critical": 30,
            }
        },
        "重试系统配置.json": {
            "default_strategy": "EXPONENTIAL_BACKOFF",
            "default_max_attempts": 5,
            "learning_enabled": True,
        },
        "防卡机制配置.json": {
            "monitoring_interval": 2.0,
            "detection_thresholds": {
                "position_stuck": 15.0,
                "network_stuck": 10.0,
                "logic_stuck": 60.0,
            }
        },
        "仪表板配置.json": {
            "monitoring_interval": 5.0,
            "alert_thresholds": {
                "network_latency": {"warning": 200, "critical": 500},
                "script_success_rate": {"warning": 0.8, "critical": 0.5},
            }
        }
    }
    
    @staticmethod
    def create_config_directory(config_dir: str = "配置") -> bool:
        """创建配置目录和文件"""
        try:
            # 创建配置目录
            os.makedirs(config_dir, exist_ok=True)
            logger.info(f"创建配置目录: {config_dir}")
            
            # 创建默认配置文件
            for config_name, config_data in ConfigurationManager.DEFAULT_CONFIGS.items():
                config_path = os.path.join(config_dir, config_name)
                
                if not os.path.exists(config_path):
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, ensure_ascii=False, indent=2)
                    logger.info(f"创建配置文件: {config_name}")
                else:
                    logger.info(f"配置文件已存在: {config_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"创建配置目录失败: {e}")
            return False
    
    @staticmethod
    def backup_existing_config(config_dir: str = "配置") -> Optional[str]:
        """备份现有配置"""
        if not os.path.exists(config_dir):
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"配置备份_{timestamp}"
            
            shutil.copytree(config_dir, backup_dir)
            logger.info(f"配置已备份到: {backup_dir}")
            
            return backup_dir
            
        except Exception as e:
            logger.error(f"备份配置失败: {e}")
            return None
    
    @staticmethod
    def create_example_scripts(scripts_dir: str = "示例脚本") -> bool:
        """创建示例脚本"""
        try:
            os.makedirs(scripts_dir, exist_ok=True)
            
            # 创建基础示例
            examples = {
                "基础集成示例.py": """#!/usr/bin/env python3
# 石器时代网络稳定性工具包 - 基础集成示例

from 网络波动检测器 import NetworkMonitor
from 智能重试系统 import IntelligentRetrySystem, RetryTask, RetryStrategy

# 1. 初始化网络监控
network_monitor = NetworkMonitor("配置/网络监控配置.json")
network_monitor.start_monitoring()

# 2. 初始化重试系统
retry_system = IntelligentRetrySystem("配置/重试系统配置.json")

# 3. 定义可能失败的操作
def risky_operation(param1, param2):
    import random
    if random.random() < 0.3:  # 30%失败率
        raise Exception("模拟操作失败")
    return f"操作成功: {param1}, {param2}"

# 4. 创建重试任务
task = RetryTask(
    task_id="demo_task",
    task_name="演示任务",
    function_to_retry=risky_operation,
    function_args=("参数1", "参数2"),
    max_attempts=3,
    strategy=RetryStrategy.EXPONENTIAL_BACKOFF
)

# 5. 执行带重试的任务
try:
    result = retry_system.execute_with_retry(task)
    print(f"任务结果: {result}")
except Exception as e:
    print(f"所有重试都失败: {e}")

# 6. 停止监控
network_monitor.stop_monitoring()
print("示例执行完成")
""",
                
                "ASSA脚本集成示例.py": """#!/usr/bin/env python3
# ASSA脚本集成示例

import time
from 防卡机制 import AntiStuckMechanism

class EnhancedASSAScript:
    def __init__(self):
        self.anti_stuck = AntiStuckMechanism("配置/防卡机制配置.json")
        self.current_position = (100, 100)
        
    def run(self):
        print("开始执行增强版ASSA脚本")
        self.anti_stuck.start_monitoring()
        
        try:
            # 模拟脚本步骤
            steps = [
                ("移动到渔村", (50, 60)),
                ("与NPC对话", None),
                ("收集物品", None),
                ("返回起点", (100, 100)),
            ]
            
            for step_name, position in steps:
                print(f"执行步骤: {step_name}")
                
                if position:
                    # 记录位置
                    self.anti_stuck.record_position(position, "当前地图")
                    self.current_position = position
                    print(f"移动到位置: {position}")
                
                # 模拟执行时间
                time.sleep(2)
                
                # 防卡检查
                if self.anti_stuck.detect_stuck():
                    print("检测到卡顿，触发恢复机制")
                    recovery = self.anti_stuck.recover()
                    print(f"恢复动作: {recovery}")
        
        finally:
            self.anti_stuck.stop_monitoring()
            print("脚本执行完成")

if __name__ == "__main__":
    script = EnhancedASSAScript()
    script.run()
""",
                
                "性能监控示例.py": """#!/usr/bin/env python3
# 性能监控示例

from 性能监控仪表板 import PerformanceDashboard, MetricType
import random
import time

def demo_performance_monitoring():
    # 创建仪表板
    dashboard = PerformanceDashboard("配置/仪表板配置.json")
    
    print("开始性能监控演示...")
    
    # 模拟数据收集
    for i in range(20):
        # 模拟网络指标
        latency = 50 + random.random() * 100  # 50-150ms
        packet_loss = random.random() * 5     # 0-5%
        success_rate = 0.8 + random.random() * 0.2  # 80-100%
        
        # 添加指标
        dashboard.add_metric(MetricType.NETWORK_LATENCY, latency, "ms")
        dashboard.add_metric(MetricType.NETWORK_PACKET_LOSS, packet_loss, "%")
        dashboard.add_metric(MetricType.SCRIPT_SUCCESS_RATE, success_rate)
        
        # 获取摘要
        if i % 5 == 0:
            summary = dashboard.get_summary()
            print(f"第{i+1}次检查 - 性能评分: {summary['performance_scores']['overall_score']:.2f}")
        
        time.sleep(0.5)
    
    # 生成报告
    report = dashboard.generate_report(period_hours=1)
    print(f"监控报告生成完成，收集了{report['summary']['metrics_collected']}个指标")
    
    # 显示活跃警报
    if dashboard.active_alerts:
        print(f"活跃警报: {len(dashboard.active_alerts)}个")
        for alert in dashboard.active_alerts[:3]:  # 显示前3个
            print(f"  - {alert.message}")

if __name__ == "__main__":
    demo_performance_monitoring()
"""
            }
            
            # 写入示例文件
            for filename, content in examples.items():
                filepath = os.path.join(scripts_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"创建示例脚本: {filename}")
            
            return True
            
        except Exception as e:
            logger.error(f"创建示例脚本失败: {e}")
            return False


class DeploymentValidator:
    """部署验证类"""
    
    @staticmethod
    def validate_installation(install_dir: str) -> Dict[str, Any]:
        """验证安装"""
        validation_results = {
            "overall": False,
            "checks": {},
            "errors": [],
            "warnings": [],
        }
        
        try:
            # 检查目录结构
            required_dirs = ["配置"]
            required_files = [
                "网络波动检测器.py",
                "智能重试系统.py", 
                "防卡机制.py",
                "主程序.py",
                "使用指南.md",
            ]
            
            # 检查目录
            for dir_name in required_dirs:
                dir_path = os.path.join(install_dir, dir_name)
                if os.path.isdir(dir_path):
                    validation_results["checks"][f"目录_{dir_name}"] = True
                else:
                    validation_results["checks"][f"目录_{dir_name}"] = False
                    validation_results["errors"].append(f"缺少目录: {dir_name}")
            
            # 检查文件
            for file_name in required_files:
                file_path = os.path.join(install_dir, file_name)
                if os.path.isfile(file_path):
                    validation_results["checks"][f"文件_{file_name}"] = True
                else:
                    validation_results["checks"][f"文件_{file_name}"] = False
                    validation_results["errors"].append(f"缺少文件: {file_name}")
            
            # 检查Python模块导入
            import_checks = [
                ("网络波动检测器", "NetworkMonitor"),
                ("智能重试系统", "IntelligentRetrySystem"),
                ("防卡机制", "AntiStuckMechanism"),
            ]
            
            # 添加安装目录到Python路径
            sys.path.insert(0, install_dir)
            
            for module_name, class_name in import_checks:
                try:
                    module = __import__(module_name)
                    if hasattr(module, class_name):
                        validation_results["checks"][f"导入_{module_name}"] = True
                    else:
                        validation_results["checks"][f"导入_{module_name}"] = False
                        validation_results["errors"].append(f"模块{module_name}缺少类{class_name}")
                except ImportError as e:
                    validation_results["checks"][f"导入_{module_name}"] = False
                    validation_results["errors"].append(f"导入模块{module_name}失败: {e}")
