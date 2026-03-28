#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石器时代脚本自动化部署系统 - 主程序
整合所有模块，提供完整的部署解决方案

功能:
1. 统一管理所有部署模块
2. 提供命令行和配置向导
3. 完整的部署流程管理
4. 与现有工具链集成
5. 详细的报告和日志

设计原则:
- 一体化解决方案，开箱即用
- 模块化设计，灵活配置
- 用户友好，易于使用
- 企业级质量，生产就绪
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入各个模块
try:
    from 打包引擎 import PackagingEngine, PackageManifest
    from 配置引擎 import ConfigurationEngine, Configuration
    from 部署引擎 import DeploymentEngine, DeploymentPlan, DeploymentResult
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有模块文件都在同一目录下")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('部署系统日志.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class StoneAgeDeploymentSystem:
    """石器时代部署系统主类"""
    
    def __init__(self, config_dir: str = "配置"):
        """
        初始化部署系统
        
        Args:
            config_dir: 配置目录路径
        """
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)
        
        # 初始化各个引擎
        self.packaging_engine = None
        self.configuration_engine = None
        self.deployment_engine = None
        
        # 状态跟踪
        self.status = {
            "initialized": False,
            "engines_loaded": {},
            "last_operation": None,
            "error_count": 0,
        }
        
        logger.info("石器时代部署系统初始化开始")
    
    def initialize_engines(self):
        """初始化所有引擎"""
        try:
            # 1. 初始化打包引擎
            packaging_config = os.path.join(self.config_dir, "打包配置.yaml")
            self.packaging_engine = PackagingEngine(packaging_config)
            self.status["engines_loaded"]["packaging"] = True
            logger.info("打包引擎初始化完成")
            
            # 2. 初始化配置引擎
            config_engine_config = os.path.join(self.config_dir, "配置引擎配置.yaml")
            self.configuration_engine = ConfigurationEngine(config_engine_config)
            self.status["engines_loaded"]["configuration"] = True
            logger.info("配置引擎初始化完成")
            
            # 3. 初始化部署引擎
            deployment_config = os.path.join(self.config_dir, "部署引擎配置.yaml")
            self.deployment_engine = DeploymentEngine(deployment_config)
            self.status["engines_loaded"]["deployment"] = True
            logger.info("部署引擎初始化完成")
            
            self.status["initialized"] = True
            self.status["last_operation"] = datetime.now()
            logger.info("所有引擎初始化完成，部署系统就绪")
            
        except Exception as e:
            logger.error(f"初始化引擎失败: {e}")
            self.status["error_count"] += 1
            raise
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "initialized": self.status["initialized"],
            "engines_loaded": self.status["engines_loaded"],
            "error_count": self.status["error_count"],
            "last_operation": self.status["last_operation"].isoformat() if self.status["last_operation"] else None,
        }
        
        # 添加各个引擎的状态
        if self.packaging_engine:
            status["packaging_engine"] = {
                "total_packages": self.packaging_engine.stats.get("total_packages", 0),
                "status": "运行正常",
            }
        
        if self.configuration_engine:
            status["configuration_engine"] = {
                "configurations_generated": self.configuration_engine.stats.get("configurations_generated", 0),
                "status": "运行正常",
            }
        
        if self.deployment_engine:
            stats = self.deployment_engine.get_statistics()
            status["deployment_engine"] = {
                "total_deployments": stats.get("total_deployments", 0),
                "success_rate": f"{stats.get('success_rate', 0):.1f}%",
                "status": "运行正常",
            }
        
        return status
    
    def package_script(self, source_dir: str, output_path: str, 
                      package_format: str = "zip") -> Dict:
        """打包脚本"""
        if not self.status["initialized"]:
            return {"error": "系统未初始化"}
        
        try:
            logger.info(f"开始打包脚本: {source_dir}")
            
            # 收集文件
            files = self.packaging_engine._collect_files(source_dir)
            
            # 分析依赖
            dependencies = self.packaging_engine._analyze_dependencies(files)
            
            # 创建包清单
            metadata = {
                "source_dir": source_dir,
                "package_format": package_format,
                "created_by": "石器时代部署系统",
                "version": "1.0.0",
            }
            
            manifest = self.packaging_engine._create_package_manifest(
                files, dependencies, metadata
            )
            
            # 验证包
            is_valid, errors = self.packaging_engine._validate_package(manifest)
            if not is_valid:
                return {"error": "包验证失败", "errors": errors}
            
            # 创建包
            if package_format == "zip":
                success = self.packaging_engine._create_zip_package(manifest, output_path)
            else:
                return {"error": f"不支持的打包格式: {package_format}"}
            
            if success:
                # 保存清单
                manifest_path = output_path.replace(f".{package_format}", "_manifest.json")
                manifest.save(manifest_path)
                
                result = {
                    "success": True,
                    "package_path": output_path,
                    "manifest_path": manifest_path,
                    "file_count": len(files),
                    "total_size": sum(f.size for f in files),
                    "dependencies": dependencies,
                }
                
                logger.info(f"打包成功: {output_path}")
                return result
            else:
                return {"error": "打包失败"}
            
        except Exception as e:
            logger.error(f"打包失败: {e}")
            return {"error": f"打包失败: {e}"}
    
    def configure_deployment(self, environment: str = "development") -> Dict:
        """配置部署"""
        if not self.status["initialized"]:
            return {"error": "系统未初始化"}
        
        try:
            logger.info(f"开始配置部署环境: {environment}")
            
            # 检测环境
            env_info = self.configuration_engine.detect_environment()
            
            # 生成配置
            configuration = self.configuration_engine.generate_configuration(environment)
            
            # 保存配置
            config_id = configuration.config_id
            config_path = os.path.join(self.config_dir, f"{config_id}.json")
            configuration.save(config_path)
            
            result = {
                "success": True,
                "config_id": config_id,
                "config_path": config_path,
                "environment": environment,
                "game_installed": env_info.game_installed,
                "validation_results": configuration.validation_results,
                "optimization_suggestions": configuration.optimization_suggestions,
            }
            
            logger.info(f"配置成功: {config_id}")
            return result
            
        except Exception as e:
            logger.error(f"配置失败: {e}")
            return {"error": f"配置失败: {e}"}
    
    def deploy_package(self, package_path: str, target_path: str, 
                      deployment_type: str = "local") -> Dict:
        """部署包"""
        if not self.status["initialized"]:
            return {"error": "系统未初始化"}
        
        try:
            logger.info(f"开始部署包: {package_path} -> {target_path}")
            
            # 创建部署计划
            plan = self.deployment_engine.create_deployment_plan(
                package_path, target_path, deployment_type
            )
            
            # 执行部署
            result = self.deployment_engine.execute_deployment(plan)
            
            # 准备返回结果
            deployment_result = {
                "success": result.success,
                "deployment_id": result.deployment_id,
                "plan_id": result.plan_id,
                "deployed_files": len(result.deployed_files),
                "backed_up_files": len(result.backed_up_files),
                "errors": result.errors,
                "warnings": result.warnings,
                "started_at": result.started_at.isoformat(),
                "completed_at": result.completed_at.isoformat() if result.completed_at else None,
            }
            
            if result.success:
                logger.info(f"部署成功: {result.deployment_id}")
            else:
                logger.warning(f"部署失败: {result.deployment_id}")
            
            return deployment_result
            
        except Exception as e:
            logger.error(f"部署失败: {e}")
            return {"error": f"部署失败: {e}"}
    
    def full_deployment_workflow(self, script_dir: str, target_path: str, 
                                environment: str = "development") -> Dict:
        """完整部署工作流"""
        logger.info("开始完整部署工作流")
        
        workflow_result = {
            "workflow_id": f"workflow_{int(datetime.now().timestamp())}",
            "started_at": datetime.now().isoformat(),
            "steps": [],
            "success": False,
            "errors": [],
        }
        
        try:
            # 步骤1: 配置环境
            workflow_result["steps"].append({
                "step": 1,
                "name": "环境配置",
                "started_at": datetime.now().isoformat(),
            })
            
            config_result = self.configure_deployment(environment)
            workflow_result["steps"][-1].update({
                "completed_at": datetime.now().isoformat(),
                "result": config_result,
            })
            
            if "error" in config_result:
                workflow_result["errors"].append(f"环境配置失败: {config_result['error']}")
                return workflow_result
            
            # 步骤2: 打包脚本
            workflow_result["steps"].append({
                "step": 2,
                "name": "脚本打包",
                "started_at": datetime.now().isoformat(),
            })
            
            package_path = os.path.join(target_path, f"部署包_{int(datetime.now().timestamp())}.zip")
            package_result = self.package_script(script_dir, package_path)
            workflow_result["steps"][-1].update({
                "completed_at": datetime.now().isoformat(),
                "result": package_result,
            })
            
            if "error" in package_result:
                workflow_result["errors"].append(f"脚本打包失败: {package_result['error']}")
                return workflow_result
            
            # 步骤3: 部署包
            workflow_result["steps"].append({
                "step": 3,
                "name": "包部署",
                "started_at": datetime.now().isoformat(),
            })
            
            deploy_result = self.deploy_package(package_path, target_path)
            workflow_result["steps"][-1].update({
                "completed_at": datetime.now().isoformat(),
                "result": deploy_result,
            })
            
            if "error" in deploy_result:
                workflow_result["errors"].append(f"包部署失败: {deploy_result['error']}")
                return workflow_result
            
            # 工作流成功
            workflow_result["success"] = True
            workflow_result["completed_at"] = datetime.now().isoformat()
            
            logger.info("完整部署工作流成功完成")
            
        except Exception as e:
            workflow_result["errors"].append(f"工作流执行异常: {e}")
            logger.error(f"工作流执行异常: {e}")
        
        return workflow_result
    
    def generate_report(self, workflow_id: str = None) -> Dict:
        """生成报告"""
        report = {
            "report_id": f"report_{int(datetime.now().timestamp())}",
            "generated_at": datetime.now().isoformat(),
            "system_status": self.get_system_status(),
            "recommendations": [],
        }
        
        # 这里可以添加更详细的报告内容
        # 例如：部署历史、性能统计、错误分析等
        
        # 生成建议
        status = self.get_system_status()
        
        if status.get("error_count", 0) > 0:
            report["recommendations"].append("检测到系统错误，建议检查日志文件")
        
        if self.deployment_engine:
            stats = self.deployment_engine.get_statistics()
            if stats.get("success_rate", 100) < 80:
                report["recommendations"].append("部署成功率较低，建议检查部署配置")
        
        if not report["recommendations"]:
            report["recommendations"].append("系统运行良好，继续保持当前配置")
        
        return report
    
    def run_demo(self):
        """运行演示示例"""
        logger.info("开始运行部署系统演示示例...")
        
        # 创建演示目录
        demo_dir = "演示部署"
        os.makedirs(demo_dir, exist_ok=True)
        
        # 创建演示脚本
        demo_script = os.path.join(demo_dir, "演示脚本.assa")
        with open(demo_script, 'w', encoding='utf-8') as f:
            f.write("""// 石器时代演示脚本
// 这是一个简单的演示脚本

function 演示函数()
    print("开始演示脚本")
    delay(1000)
    print("演示完成")
end

// 主程序
演示函数()
""")
        
        # 创建演示配置文件
        demo_config = os.path.join(demo_dir, "config.yaml")
        with open(demo_config, 'w', encoding='utf-8') as f:
            f.write("""# 演示配置文件
game:
  path: "C:/石器时代"
  version: "NG25"

network:
  timeout: 30
  retry_count: 3

logging:
  level: "INFO"
  file: "演示日志.log"
""")
        
        print("=" * 60)
        print("🚀 石器时代部署系统演示")
        print("=" * 60)
        
        # 步骤1: 系统状态
        print("\n📋 步骤1: 检查系统状态")
        status = self.get_system_status()
        print(f"  系统状态: {'就绪' if status['initialized'] else '未就绪'}")
        print(f"  加载的引擎: {', '.join([k for k, v in status['engines_loaded'].items() if v])}")
        
        # 步骤2: 环境配置演示
        print("\n📋 步骤2: 环境配置演示")
        config_result = self.configure_deployment("development")
        if "error" in config_result:
            print(f"  配置失败: {config_result['error']}")
        else:
            print(f"  配置成功: {config_result['config_id']}")
            print(f"  游戏安装: {'是' if config_result['game_installed'] else '否'}")
        
        # 步骤3: 打包演示
        print("\n📋 步骤3: 脚本打包演示")
        package_path = os.path.join(demo_dir, "演示包.zip")
        package_result = self.package_script(demo_dir, package_path)
        if "error" in package_result:
            print(f"  打包失败: {package_result['error']}")
        else:
            print(f"  打包成功: {package_result['package_path']}")
            print(f"  文件数量: {package_result['file_count']}")
            print(f"  总大小: {package_result['total_size']/(1024):.1f}KB")
        
        # 步骤4: 部署演示（模拟）
        print("\n📋 步骤4: 部署演示（模拟）")
        print("  部署目标: ./部署目标/")
        print("  部署类型: 本地部署")
        print("  状态: 模拟完成")
        
        # 步骤5: 生成报告
        print("\n📋 步骤5: 生成报告")
        report = self.generate_report()
        print(f"  报告ID: {report['report_id']}")
        print(f"  建议: {report['recommendations'][0]}")
        
        print("\n" + "=" * 60)
        print("✅ 演示示例运行完成")
        print("=" * 60)
        
        return {
            "demo_dir": demo_dir,
            "config_result": config_result,
            "package_result": package_result,
            "report": report,
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='石器时代脚本自动化部署系统')
    parser.add_argument('--mode', choices=['cli', 'demo', 'workflow', 'status'], 
                       default='cli', help='运行模式')
    parser.add_argument('--config', type=str, default='配置',
                       help='配置目录路径')
    parser.add_argument('--source', type=str,
                       help='源脚本目录路径')
    parser.add_argument('--target', type=str,
                       help='目标部署路径')
    parser.add_argument('--environment', type=str, default='development',
                       help='部署环境 (development, testing, production)')
    parser.add_argument('--report', action='store_true',
                       help='生成并保存报告')
    
    args = parser.parse_args()
    
    # 创建部署系统实例
    deployment_system = StoneAgeDeploymentSystem(args.config)
    
    try:
        # 初始化引擎
        deployment_system.initialize_engines()
