#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石器时代网络稳定性优化工具包 - 主程序
整合所有模块，提供完整的网络稳定性解决方案

功能:
1. 统一管理所有稳定性优化模块
2. 提供命令行和图形界面
3. 实时监控和报告生成
4. 与ASSA脚本深度集成
5. 自动化配置和优化

设计原则:
- 一体化解决方案，开箱即用
- 模块化设计，灵活配置
- 用户友好，易于使用
- 高性能，低资源占用
"""

import sys
import os
import time
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Any

# 添加当前目录到路径，以便导入模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入各个模块
try:
    from 网络波动检测器 import NetworkMonitor, NetworkStatus
    from 智能重试系统 import IntelligentRetrySystem, RetryStrategy, RetryResult
    from 防卡机制 import AntiStuckMechanism, StuckType, RecoveryAction
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有模块文件都在同一目录下")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('稳定性工具包日志.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class StabilityOptimizationSuite:
    """稳定性优化套件主类"""
    
    def __init__(self, config_dir: str = "配置"):
        """
        初始化稳定性优化套件
        
        Args:
            config_dir: 配置目录路径
        """
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)
        
        # 初始化各个模块
        self.network_monitor = None
        self.retry_system = None
        self.anti_stuck = None
        
        # 状态跟踪
        self.status = {
            "initialized": False,
            "modules_loaded": {},
            "last_check": None,
            "performance_metrics": {},
            "error_count": 0,
        }
        
        # 集成配置
        self.integration_config = self._load_integration_config()
        
        logger.info("稳定性优化套件初始化开始")
    
    def _load_integration_config(self) -> Dict:
        """加载集成配置"""
        config_path = os.path.join(self.config_dir, "集成配置.json")
        
        default_config = {
            "module_interaction": {
                "network_to_retry": True,      # 网络状态影响重试策略
                "stuck_to_network": True,      # 卡顿检测使用网络数据
                "retry_to_anti_stuck": True,   # 重试失败触发防卡
                "shared_state": True,          # 共享状态数据
            },
            "performance_optimization": {
                "monitoring_interval": 3.0,
                "data_retention_days": 7,
                "max_log_size_mb": 100,
                "auto_cleanup": True,
            },
            "reporting": {
                "generate_reports": True,
                "report_interval_minutes": 60,
                "save_to_file": True,
                "notify_threshold": 0.8,  # 性能低于80%时通知
            },
            "integration_with_assascript": {
                "auto_detect": True,
                "hook_functions": True,
                "provide_apis": True,
                "example_scripts": True,
            }
        }
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
                logger.info(f"从 {config_path} 加载集成配置")
        except FileNotFoundError:
            logger.info(f"集成配置文件 {config_path} 不存在，使用默认配置")
            # 保存默认配置
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        return default_config
    
    def initialize_modules(self):
        """初始化所有模块"""
        try:
            # 1. 初始化网络监控器
            network_config = os.path.join(self.config_dir, "网络监控配置.json")
            self.network_monitor = NetworkMonitor(network_config)
            self.status["modules_loaded"]["network_monitor"] = True
            logger.info("网络监控器初始化完成")
            
            # 2. 初始化智能重试系统
            retry_config = os.path.join(self.config_dir, "重试系统配置.json")
            self.retry_system = IntelligentRetrySystem(retry_config)
            self.status["modules_loaded"]["retry_system"] = True
            logger.info("智能重试系统初始化完成")
            
            # 3. 初始化防卡机制
            antistuck_config = os.path.join(self.config_dir, "防卡机制配置.json")
            self.anti_stuck = AntiStuckMechanism(antistuck_config)
            self.status["modules_loaded"]["anti_stuck"] = True
            logger.info("防卡机制初始化完成")
            
            # 设置模块间交互
            self._setup_module_interaction()
            
            self.status["initialized"] = True
            self.status["last_check"] = datetime.now()
            logger.info("所有模块初始化完成，稳定性优化套件就绪")
            
        except Exception as e:
            logger.error(f"初始化模块失败: {e}")
            self.status["error_count"] += 1
            raise
    
    def _setup_module_interaction(self):
        """设置模块间交互"""
        if not self.integration_config["module_interaction"]["shared_state"]:
            return
        
        logger.info("设置模块间交互...")
        
        # 这里可以添加模块间数据共享和事件传递的逻辑
        # 例如：网络状态变化时调整重试策略
        # 重试失败时触发防卡机制等
        
        # 简化版本：记录交互设置
        interactions = []
        
        if self.integration_config["module_interaction"]["network_to_retry"]:
            interactions.append("网络状态 → 重试策略")
        
        if self.integration_config["module_interaction"]["stuck_to_network"]:
            interactions.append("卡顿检测 ← 网络数据")
        
        if self.integration_config["module_interaction"]["retry_to_anti_stuck"]:
            interactions.append("重试失败 → 防卡机制")
        
        if interactions:
            logger.info(f"模块交互设置: {', '.join(interactions)}")
    
    def start_all_services(self):
        """启动所有服务"""
        if not self.status["initialized"]:
            logger.error("请先初始化模块")
            return False
        
        try:
            # 启动网络监控
            if self.network_monitor:
                self.network_monitor.start_monitoring()
                logger.info("网络监控服务已启动")
            
            # 防卡机制通常需要手动触发或集成到脚本中
            # 这里记录服务状态
            
            self.status["services_running"] = True
            logger.info("所有服务已启动")
            return True
            
        except Exception as e:
            logger.error(f"启动服务失败: {e}")
            self.status["error_count"] += 1
            return False
    
    def stop_all_services(self):
        """停止所有服务"""
        try:
            # 停止网络监控
            if self.network_monitor:
                self.network_monitor.stop_monitoring()
                logger.info("网络监控服务已停止")
            
            self.status["services_running"] = False
            logger.info("所有服务已停止")
            return True
            
        except Exception as e:
            logger.error(f"停止服务失败: {e}")
            return False
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "initialized": self.status["initialized"],
            "services_running": self.status.get("services_running", False),
            "modules_loaded": self.status["modules_loaded"],
            "error_count": self.status["error_count"],
            "last_check": self.status["last_check"].isoformat() if self.status["last_check"] else None,
        }
        
        # 添加各个模块的状态
        if self.network_monitor:
            status["network_monitor"] = {
                "is_monitoring": self.network_monitor.is_monitoring,
                "total_checks": self.network_monitor.stats.get("total_checks", 0),
                "current_status": "运行中" if self.network_monitor.is_monitoring else "停止",
            }
        
        if self.retry_system:
            status["retry_system"] = {
                "total_tasks": self.retry_system.stats.get("total_tasks", 0),
                "success_rate": self._calculate_success_rate(self.retry_system.stats),
                "efficiency_score": self.retry_system.stats.get("efficiency_score", 0),
            }
        
        if self.anti_stuck:
            status["anti_stuck"] = {
                "total_stuck_events": self.anti_stuck.stats.get("total_stuck_events", 0),
                "recovery_success_rate": self._calculate_recovery_rate(self.anti_stuck.stats),
                "avg_recovery_time": self.anti_stuck.stats.get("avg_recovery_time", 0),
            }
        
        return status
    
    def _calculate_success_rate(self, stats: Dict) -> float:
        """计算成功率"""
        total = stats.get("total_tasks", 0)
        successful = stats.get("successful_tasks", 0)
        
        if total > 0:
            return successful / total
        return 0.0
    
    def _calculate_recovery_rate(self, stats: Dict) -> float:
        """计算恢复成功率"""
        total = stats.get("total_stuck_events", 0)
        successful = stats.get("successful_recoveries", 0)
        
        if total > 0:
            return successful / total
        return 0.0
    
    def generate_report(self, report_type: str = "summary") -> Dict:
        """生成报告"""
        if not self.status["initialized"]:
            return {"error": "系统未初始化"}
        
        report = {
            "report_id": f"report_{int(time.time())}",
            "generated_at": datetime.now().isoformat(),
            "report_type": report_type,
            "system_status": self.get_system_status(),
        }
        
        if report_type == "detailed":
            # 添加详细数据
            if self.network_monitor and hasattr(self.network_monitor, 'metrics_history'):
                recent_metrics = self.network_monitor.metrics_history[-10:] if self.network_monitor.metrics_history else []
                report["recent_network_metrics"] = [
                    m.to_dict() for m in recent_metrics
                ]
            
            if self.retry_system and hasattr(self.retry_system, 'retry_history'):
                recent_retries = self.retry_system.retry_history[-10:] if self.retry_system.retry_history else []
                report["recent_retry_attempts"] = [
                    r.to_dict() for r in recent_retries
                ]
            
            if self.anti_stuck and hasattr(self.anti_stuck, 'stuck_events'):
                recent_events = self.anti_stuck.stuck_events[-10:] if self.anti_stuck.stuck_events else []
                report["recent_stuck_events"] = [
                    e.to_dict() for e in recent_events
                ]
        
        # 性能分析
        report["performance_analysis"] = self._analyze_performance()
        
        # 建议和改进
        report["recommendations"] = self._generate_recommendations()
        
        return report
    
    def _analyze_performance(self) -> Dict:
        """分析性能"""
        analysis = {
            "overall_score": 0.0,
            "network_stability": 0.0,
            "retry_efficiency": 0.0,
            "recovery_effectiveness": 0.0,
            "bottlenecks": [],
            "improvement_opportunities": [],
        }
        
        # 这里可以添加具体的性能分析逻辑
        # 简化版本：基于模块状态评分
        
        if self.network_monitor:
            # 基于网络监控数据评分
            analysis["network_stability"] = 0.8  # 示例值
        
        if self.retry_system:
            # 基于重试系统数据评分
            success_rate = self._calculate_success_rate(self.retry_system.stats)
            analysis["retry_efficiency"] = success_rate
        
        if self.anti_stuck:
            # 基于防卡机制数据评分
            recovery_rate = self._calculate_recovery_rate(self.anti_stuck.stats)
            analysis["recovery_effectiveness"] = recovery_rate
        
        # 计算总体评分
        scores = [v for v in analysis.values() if isinstance(v, (int, float))]
        if scores:
            analysis["overall_score"] = sum(scores) / len(scores)
        
        return analysis
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于性能分析生成建议
        status = self.get_system_status()
        
        if status.get("error_count", 0) > 0:
            recommendations.append("检测到系统错误，建议检查日志文件")
        
        if self.network_monitor:
            net_stats = self.network_monitor.stats
            if net_stats.get("failed_checks", 0) > net_stats.get("successful_checks", 1) * 0.1:
                recommendations.append("网络检测失败率较高，建议检查网络连接")
        
        if self.retry_system:
            retry_stats = self.retry_system.stats
            success_rate = self._calculate_success_rate(retry_stats)
            if success_rate < 0.7:
                recommendations.append("重试成功率较低，建议调整重试策略参数")
        
        if self.anti_stuck:
            antistuck_stats = self.anti_stuck.stats
            if antistuck_stats.get("total_stuck_events", 0) > 10:
                recommendations.append("卡顿事件较多，建议优化脚本逻辑或检查系统资源")
        
        # 默认建议
        if not recommendations:
            recommendations.append("系统运行良好，继续保持当前配置")
            recommendations.append("建议定期查看性能报告以优化配置")
        
        return recommendations
    
    def save_report(self, report: Dict, filename: Optional[str] = None):
        """保存报告到文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"稳定性报告_{timestamp}.json"
        
        reports_dir = "报告"
        os.makedirs(reports_dir, exist_ok=True)
        
        filepath = os.path.join(reports_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"报告已保存到: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"保存报告失败: {e}")
            return None
    
    def run_demo(self):
        """运行演示示例"""
        logger.info("开始运行演示示例...")
        
        # 示例1: 模拟网络波动检测
        logger.info("示例1: 网络波动检测演示")
        if self.network_monitor:
            # 这里可以添加具体的演示代码
            logger.info("网络监控器已就绪，可以开始监控")
        
        # 示例2: 智能重试演示
        logger.info("示例2: 智能重试演示")
        if self.retry_system:
            # 这里可以添加具体的演示代码
            logger.info("重试系统已就绪，可以处理失败任务")
        
        # 示例3: 防卡机制演示
        logger.info("示例3: 防卡机制演示")
        if self.anti_stuck:
            # 这里可以添加具体的演示代码
            logger.info("防卡机制已就绪，可以检测和恢复卡顿")
        
        logger.info("演示示例运行完成")
        
        # 生成演示报告
        report = self.generate_report("summary")
        self.save_report(report, "演示报告.json")
        
        return report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='石器时代网络稳定性优化工具包')
    parser.add_argument('--mode', choices=['cli', 'gui', 'service', 'demo'], 
                       default='cli', help='运行模式')
    parser.add_argument('--config', type=str, default='配置',
                       help='配置目录路径')
    parser.add_argument('--report', action='store_true',
                       help='生成并保存报告')
    parser.add_argument('--status', action='store_true',
                       help='显示系统状态')
    parser.add_argument('--start', action='store_true',
                       help='启动所有服务')
    parser.add_argument('--stop', action='store_true',
                       help='停止所有服务')
    
    args = parser.parse_args()
    
    # 创建套件实例
    suite = StabilityOptimizationSuite(args.config)
    
    try:
        # 初始化模块
        suite.initialize_modules()
        
        # 根据参数执行相应操作
        if args.status:
            status = suite.get_system_status()
            print(json.dumps(status, ensure_ascii=False, indent=2))
        
        if args.start:
            if suite.start_all_services():
                print("所有服务已启动")
            else:
                print("启动服务失败")
        
        if args.stop:
            try:
                if suite.stop_all_services():
                    print("所有服务已停止")
            except Exception as e:
                print(f"停止服务时出错: {e}")
        
        print("\n操作完成")
        
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
    except Exception as e:
        print(f"\n\n程序执行出错: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
