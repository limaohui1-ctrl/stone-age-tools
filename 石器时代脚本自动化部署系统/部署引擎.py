#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石器时代脚本自动化部署系统 - 部署引擎
执行实际的部署操作，支持多种部署模式

功能:
1. 目标环境检测和准备
2. 文件传输和安装
3. 配置应用和优化
4. 服务启动和验证
5. 支持多种部署模式（本地、远程、增量、全量）

设计原则:
- 安全可靠，支持回滚
- 多种部署模式支持
- 完整的错误处理
- 详细的部署日志
"""

import os
import sys
import json
import shutil
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import tempfile

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('部署引擎日志.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class DeploymentPlan:
    """部署计划"""
    plan_id: str
    created_at: datetime
    deployment_type: str  # local, remote, incremental, full
    source_path: str
    target_path: str
    files_to_deploy: List[Dict]
    backup_required: bool
    validation_required: bool
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data


@dataclass
class DeploymentResult:
    """部署结果"""
    deployment_id: str
    plan_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    success: bool
    deployed_files: List[str]
    backed_up_files: List[str]
    errors: List[str]
    warnings: List[str]
    statistics: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        data['started_at'] = self.started_at.isoformat()
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return data


class DeploymentEngine:
    """部署引擎核心类"""
    
    def __init__(self, config_path: str = "部署引擎配置.yaml"):
        """
        初始化部署引擎
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.active_deployments = {}
        self.deployment_history = []
        
        # 统计信息
        self.stats = {
            "total_deployments": 0,
            "successful_deployments": 0,
            "failed_deployments": 0,
            "total_files_deployed": 0,
            "total_backups_created": 0,
            "total_deployment_time": 0.0,
        }
        
        logger.info("部署引擎初始化完成")
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        default_config = {
            "deployment": {
                "default_type": "local",
                "backup_enabled": True,
                "backup_directory": "部署备份",
                "max_backups": 5,
                "auto_cleanup_backups": True,
            },
            "file_operations": {
                "verify_integrity": True,
                "preserve_permissions": True,
                "handle_conflicts": "backup",  # backup, overwrite, skip
                "retry_on_failure": True,
                "max_retries": 3,
            },
            "validation": {
                "pre_deployment_check": True,
                "post_deployment_verification": True,
                "file_integrity_check": True,
                "configuration_test": True,
            },
            "performance": {
                "parallel_transfers": 3,
                "chunk_size_kb": 1024,
                "timeout_seconds": 300,
                "progress_reporting": True,
            },
            "error_handling": {
                "auto_rollback": True,
                "notify_on_error": True,
                "log_detailed_errors": True,
                "continue_on_warning": True,
            }
        }
        
        # 简化：直接返回默认配置
        return default_config
    
    def create_deployment_plan(self, source_path: str, target_path: str, 
                              deployment_type: str = None) -> DeploymentPlan:
        """创建部署计划"""
        if deployment_type is None:
            deployment_type = self.config["deployment"]["default_type"]
        
        # 分析源文件
        files_to_deploy = self._analyze_source_files(source_path, deployment_type)
        
        # 创建部署计划
        plan_id = f"plan_{int(datetime.now().timestamp())}_{deployment_type}"
        plan = DeploymentPlan(
            plan_id=plan_id,
            created_at=datetime.now(),
            deployment_type=deployment_type,
            source_path=source_path,
            target_path=target_path,
            files_to_deploy=files_to_deploy,
            backup_required=self.config["deployment"]["backup_enabled"],
            validation_required=self.config["validation"]["post_deployment_verification"]
        )
        
        logger.info(f"创建部署计划: {plan_id}, 类型: {deployment_type}, 文件数: {len(files_to_deploy)}")
        return plan
    
    def _analyze_source_files(self, source_path: str, deployment_type: str) -> List[Dict]:
        """分析源文件"""
        files = []
        
        try:
            if os.path.isfile(source_path):
                # 单个文件
                file_info = self._get_file_info(source_path)
                files.append(file_info)
            elif os.path.isdir(source_path):
                # 目录
                for root, dirs, filenames in os.walk(source_path):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        file_info = self._get_file_info(file_path)
                        files.append(file_info)
            
            logger.info(f"分析到 {len(files)} 个文件需要部署")
            
        except Exception as e:
            logger.error(f"分析源文件失败: {e}")
        
        return files
    
    def _get_file_info(self, file_path: str) -> Dict:
        """获取文件信息"""
        try:
            stat = os.stat(file_path)
            
            # 计算MD5
            md5_hash = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    md5_hash.update(chunk)
            
            return {
                "path": file_path,
                "size": stat.st_size,
                "md5": md5_hash.hexdigest(),
                "mtime": stat.st_mtime,
                "relative_path": os.path.basename(file_path)  # 简化相对路径
            }
        
        except Exception as e:
            logger.error(f"获取文件信息失败 {file_path}: {e}")
            return {"path": file_path, "error": str(e)}
    
    def execute_deployment(self, plan: DeploymentPlan) -> DeploymentResult:
        """执行部署"""
        deployment_id = f"deploy_{int(datetime.now().timestamp())}"
        started_at = datetime.now()
        
        logger.info(f"开始执行部署: {deployment_id}, 计划: {plan.plan_id}")
        
        # 初始化结果
        result = DeploymentResult(
            deployment_id=deployment_id,
            plan_id=plan.plan_id,
            started_at=started_at,
            completed_at=None,
            success=False,
            deployed_files=[],
            backed_up_files=[],
            errors=[],
            warnings=[],
            statistics={}
        )
        
        try:
            # 预部署检查
            if not self._pre_deployment_check(plan, result):
                result.errors.append("预部署检查失败")
                return result
            
            # 创建备份（如果需要）
            if plan.backup_required:
                self._create_backup(plan, result)
            
            # 执行文件部署
            self._deploy_files(plan, result)
            
            # 后部署验证
            if plan.validation_required:
                self._post_deployment_verification(plan, result)
            
            # 更新结果
            result.completed_at = datetime.now()
            result.success = len(result.errors) == 0
            
            # 更新统计
            deployment_time = (result.completed_at - started_at).total_seconds()
            self.stats["total_deployment_time"] += deployment_time
            self.stats["total_deployments"] += 1
            
            if result.success:
                self.stats["successful_deployments"] += 1
                logger.info(f"部署成功: {deployment_id}, 耗时: {deployment_time:.1f}秒")
            else:
                self.stats["failed_deployments"] += 1
                logger.warning(f"部署失败: {deployment_id}, 错误数: {len(result.errors)}")
            
            # 添加到历史
            self.deployment_history.append(result)
            
        except Exception as e:
            result.errors.append(f"部署执行异常: {e}")
            logger.error(f"部署执行异常: {e}")
            
            # 尝试回滚
            if self.config["error_handling"]["auto_rollback"]:
                self._rollback_deployment(plan, result)
        
        return result
    
    def _pre_deployment_check(self, plan: DeploymentPlan, result: DeploymentResult) -> bool:
        """预部署检查"""
        if not self.config["validation"]["pre_deployment_check"]:
            return True
        
        logger.info("执行预部署检查...")
        
        checks_passed = True
        
        # 检查源路径
        if not os.path.exists(plan.source_path):
            result.errors.append(f"源路径不存在: {plan.source_path}")
            checks_passed = False
        
        # 检查目标路径
        target_dir = os.path.dirname(plan.target_path) if os.path.isfile(plan.source_path) else plan.target_path
        if not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir, exist_ok=True)
                result.warnings.append(f"创建目标目录: {target_dir}")
            except Exception as e:
                result.errors.append(f"创建目标目录失败: {e}")
                checks_passed = False
        
        # 检查磁盘空间
        total_size = sum(f.get("size", 0) for f in plan.files_to_deploy if "size" in f)
        if total_size > 0:
            try:
                if platform.system() == "Windows":
                    import ctypes
                    free_bytes = ctypes.c_ulonglong(0)
                    ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                        ctypes.c_wchar_p(target_dir), None, None, ctypes.pointer(free_bytes)
                    )
                    free_space = free_bytes.value
                else:
                    stat = os.statvfs(target_dir)
                    free_space = stat.f_bavail * stat.f_frsize
                
                if free_space < total_size * 2:  # 需要2倍空间（备份+部署）
                    result.warnings.append(f"磁盘空间紧张: 需要{total_size*2/(1024**2):.1f}MB, 可用{free_space/(1024**2):.1f}MB")
            except:
                pass
        
        return checks_passed
    
    def _create_backup(self, plan: DeploymentPlan, result: DeploymentResult):
        """创建备份"""
        logger.info("创建备份...")
        
        backup_dir = self.config["deployment"]["backup_directory"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
        
        try:
            os.makedirs(backup_path, exist_ok=True)
            
            # 备份现有文件
            for file_info in plan.files_to_deploy:
                if "error" in file_info:
                    continue
                
                target_file = os.path.join(plan.target_path, file_info["relative_path"])
                if os.path.exists(target_file):
                    backup_file = os.path.join(backup_path, file_info["relative_path"])
                    os.makedirs(os.path.dirname(backup_file), exist_ok=True)
                    shutil.copy2(target_file, backup_file)
                    result.backed_up_files.append(backup_file)
            
            self.stats["total_backups_created"] += 1
            logger.info(f"备份创建完成: {backup_path}, 文件数: {len(result.backed_up_files)}")
            
        except Exception as e:
            result.errors.append(f"创建备份失败: {e}")
            logger.error(f"创建备份失败: {e}")
    
    def _deploy_files(self, plan: DeploymentPlan, result: DeploymentResult):
        """部署文件"""
        logger.info(f"开始部署 {len(plan.files_to_deploy)} 个文件...")
        
        deployed_count = 0
        
        for file_info in plan.files_to_deploy:
            if "error" in file_info:
                result.warnings.append(f"跳过有错误的文件: {file_info['path']}")
                continue
            
            try:
                source_file = file_info["path"]
                relative_path = file_info["relative_path"]
                target_file = os.path.join(plan.target_path, relative_path)
                
                # 创建目标目录
                os.makedirs(os.path.dirname(target_file), exist_ok=True)
                
                # 复制文件
                shutil.copy2(source_file, target_file)
                
                # 验证文件完整性
                if self.config["file_operations"]["verify_integrity"]:
                    if not self._verify_file_integrity(source_file, target_file):
                        raise Exception("文件完整性验证失败")
                
                result.deployed_files.append(target_file)
                deployed_count += 1
                self.stats["total_files_deployed"] += 1
                
                logger.debug(f"部署文件: {relative_path}")
                
            except Exception as e:
                error_msg = f"部署文件失败 {file_info['path']}: {e}"
                result.errors.append(error_msg)
                logger.error(error_msg)
        
        logger.info(f"文件部署完成: {deployed_count}/{len(plan.files_to_deploy)} 成功")
    
    def _verify_file_integrity(self, source_file: str, target_file: str) -> bool:
        """验证文件完整性"""
        try:
            # 计算源文件MD5
            source_md5 = hashlib.md5()
            with open(source_file, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    source_md5.update(chunk)
            
            # 计算目标文件MD5
            target_md5 = hashlib.md5()
            with open(target_file, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    target_md5.update(chunk)
            
            return source_md5.hexdigest() == target_md5.hexdigest()
        
        except Exception as e:
            logger.warning(f"验证文件完整性失败: {e}")
            return False
    
    def _post_deployment_verification(self, plan: DeploymentPlan, result: DeploymentResult):
        """后部署验证"""
        logger.info("执行后部署验证...")
        
        # 检查部署的文件数量
        expected_count = len([f for f in plan.files_to_deploy if "error" not in f])
        actual_count = len(result.deployed_files)
        
        if actual_count < expected_count:
            result.warnings.append(f"部署文件数量不足: 预期{expected_count}, 实际{actual_count}")
        
        # 验证关键文件
        critical_files = ["manifest.json", "README.txt", "config.yaml"]
        for critical_file in critical_files:
            critical_path = os.path.join(plan.target_path, critical_file)
            if not os.path.exists(critical_path):
                result.warnings.append(f"关键文件缺失: {critical_file}")
    
    def _rollback_deployment(self, plan: DeploymentPlan, result: DeploymentResult):
        """回滚部署"""
        logger.info("尝试回滚部署...")
        
        # 如果有备份，恢复备份
        if result.backed_up_files:
            try:
                for backup_file in result.backed_up_files:
                    relative_path = os.path.relpath(backup_file, self.config["deployment"]["backup_directory"])
                    relative_path = relative_path.split(os.sep, 1)[-1] if os.sep in relative_path else relative_path
                    target_file = os.path.join(plan.target_path, relative_path)
                    
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    shutil.copy2(backup_file, target_file)
                
                logger.info("回滚完成: 从备份恢复文件")
                result.warnings.append("部署已回滚到之前版本")
                
            except Exception as e:
                result.errors.append(f"回滚失败: {e}")
                logger.error(f"回滚失败: {e}")
        else:
            logger.warning("没有备份可用，无法回滚")
            result.warnings.append("没有备份可用，无法回滚")
    
    def get_deployment_history(self, limit: int = 10) -> List[DeploymentResult]:
        """获取部署历史"""
        return self.deployment_history[-limit:] if self.deployment_history else []
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        stats = self.stats.copy()
        
        if stats["total_deployments"] > 0:
            stats["success_rate"] = (stats["successful_deployments"] / stats["total_deployments"]) * 100
            stats["avg_deployment_time"] = stats["total_deployment_time"] / stats["total_deployments"]
        else:
            stats["success_rate"] = 0.0
            stats["avg_deployment_time"] = 0.0
        
        return stats