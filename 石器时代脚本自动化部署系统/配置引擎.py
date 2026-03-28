#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石器时代脚本自动化部署系统 - 配置引擎
智能生成和验证部署配置，支持多环境配置

功能:
1. 环境检测（游戏版本、客户端路径等）
2. 配置模板管理和应用
3. 配置验证和优化建议
4. 多环境配置支持（开发、测试、生产）
5. 与稳定性工具包配置集成

设计原则:
- 智能检测，自动配置
- 模板驱动，灵活定制
- 完整验证，确保正确
- 多环境支持，一键切换
"""

import os
import sys
import json
import yaml
import logging
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
import shutil

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('配置引擎日志.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class EnvironmentInfo:
    """环境信息"""
    os_name: str
    os_version: str
    python_version: str
    game_installed: bool
    game_path: Optional[str]
    game_version: Optional[str]
    available_disk_gb: float
    available_memory_gb: float
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class Configuration:
    """配置数据类"""
    config_id: str
    created_at: datetime
    environment: str  # development, testing, production
    settings: Dict[str, Any]
    validation_results: List[Dict]
    optimization_suggestions: List[str]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data
    
    def save(self, path: str):
        """保存到文件"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'Configuration':
        """从文件加载"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 转换时间字段
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


class ConfigurationEngine:
    """配置引擎核心类"""
    
    # 默认配置模板
    DEFAULT_TEMPLATES = {
        "development": {
            "description": "开发环境配置",
            "settings": {
                "logging": {
                    "level": "DEBUG",
                    "file_path": "./logs/development.log",
                    "max_size_mb": 100,
                    "backup_count": 5
                },
                "performance": {
                    "monitoring_enabled": True,
                    "detailed_metrics": True,
                    "auto_optimization": False
                },
                "validation": {
                    "strict_mode": False,
                    "auto_fix": True,
                    "warnings_as_errors": False
                },
                "stability": {
                    "network_monitoring": True,
                    "anti_stuck": True,
                    "retry_system": True,
                    "alert_threshold": "medium"
                }
            }
        },
        "testing": {
            "description": "测试环境配置",
            "settings": {
                "logging": {
                    "level": "INFO",
                    "file_path": "./logs/testing.log",
                    "max_size_mb": 50,
                    "backup_count": 3
                },
                "performance": {
                    "monitoring_enabled": True,
                    "detailed_metrics": True,
                    "auto_optimization": True
                },
                "validation": {
                    "strict_mode": True,
                    "auto_fix": False,
                    "warnings_as_errors": True
                },
                "stability": {
                    "network_monitoring": True,
                    "anti_stuck": True,
                    "retry_system": True,
                    "alert_threshold": "high"
                }
            }
        },
        "production": {
            "description": "生产环境配置",
            "settings": {
                "logging": {
                    "level": "WARNING",
                    "file_path": "./logs/production.log",
                    "max_size_mb": 20,
                    "backup_count": 1
                },
                "performance": {
                    "monitoring_enabled": True,
                    "detailed_metrics": False,
                    "auto_optimization": True
                },
                "validation": {
                    "strict_mode": True,
                    "auto_fix": False,
                    "warnings_as_errors": True
                },
                "stability": {
                    "network_monitoring": True,
                    "anti_stuck": True,
                    "retry_system": True,
                    "alert_threshold": "critical"
                }
            }
        }
    }
    
    # 游戏检测路径（Windows）
    GAME_PATHS_WINDOWS = [
        "C:/石器时代",
        "C:/Program Files/石器时代",
        "C:/Program Files (x86)/石器时代",
        "D:/石器时代",
        "E:/石器时代",
    ]
    
    # 游戏检测路径（Linux/macOS）
    GAME_PATHS_LINUX = [
        "~/石器时代",
        "~/games/石器时代",
        "/opt/石器时代",
    ]
    
    def __init__(self, config_path: str = "配置引擎配置.yaml"):
        """
        初始化配置引擎
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.templates = self._load_templates()
        self.environment_info = None
        self.current_configuration = None
        
        # 统计信息
        self.stats = {
            "configurations_generated": 0,
            "validations_performed": 0,
            "optimizations_suggested": 0,
            "errors_detected": 0,
        }
        
        logger.info("配置引擎初始化完成")
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        default_config = {
            "environment_detection": {
                "auto_detect": True,
                "game_detection": True,
                "resource_check": True,
                "performance_benchmark": False,
            },
            "template_management": {
                "default_environment": "development",
                "template_directory": "配置模板",
                "auto_create_templates": True,
                "template_validation": True,
            },
            "validation": {
                "validate_on_generate": True,
                "check_requirements": True,
                "verify_paths": True,
                "test_integrations": True,
            },
            "optimization": {
                "auto_optimize": True,
                "suggest_improvements": True,
                "apply_best_practices": True,
                "performance_tuning": True,
            },
            "integration": {
                "with_stability_toolkit": True,
                "with_network_monitor": True,
                "with_performance_dashboard": True,
                "auto_configure_integrations": True,
            }
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}
                    default_config.update(user_config)
                logger.info(f"从 {config_path} 加载配置")
            else:
                logger.info(f"配置文件 {config_path} 不存在，使用默认配置")
                # 保存默认配置
                os.makedirs(os.path.dirname(config_path) or '.', exist_ok=True)
                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(default_config, f, default_flow_style=False)
        
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
        
        return default_config
    
    def _load_templates(self) -> Dict:
        """加载配置模板"""
        templates = self.DEFAULT_TEMPLATES.copy()
        template_dir = self.config["template_management"]["template_directory"]
        
        try:
            if os.path.isdir(template_dir):
                for filename in os.listdir(template_dir):
                    if filename.endswith(('.yaml', '.yml', '.json')):
                        template_path = os.path.join(template_dir, filename)
                        
                        try:
                            if filename.endswith('.json'):
                                with open(template_path, 'r', encoding='utf-8') as f:
                                    template_data = json.load(f)
                            else:
                                with open(template_path, 'r', encoding='utf-8') as f:
                                    template_data = yaml.safe_load(f)
                            
                            # 提取环境名称（从文件名或配置中）
                            env_name = os.path.splitext(filename)[0]
                            if isinstance(template_data, dict) and 'environment' in template_data:
                                env_name = template_data['environment']
                            
                            templates[env_name] = template_data
                            logger.info(f"加载模板: {env_name}")
                            
                        except Exception as e:
                            logger.warning(f"加载模板文件失败 {filename}: {e}")
            
            elif self.config["template_management"]["auto_create_templates"]:
                # 自动创建模板目录
                os.makedirs(template_dir, exist_ok=True)
                for env_name, template in templates.items():
                    template_path = os.path.join(template_dir, f"{env_name}.yaml")
                    with open(template_path, 'w', encoding='utf-8') as f:
                        yaml.dump(template, f, default_flow_style=False)
                    logger.info(f"创建模板: {env_name}")
        
        except Exception as e:
            logger.error(f"加载模板失败: {e}")
        
        return templates
    
    def detect_environment(self) -> EnvironmentInfo:
        """检测环境信息"""
        logger.info("开始检测环境信息...")
        
        # 操作系统信息
        os_name = platform.system()
        os_version = platform.release()
        python_version = platform.python_version()
        
        # 游戏检测
        game_installed = False
        game_path = None
        game_version = None
        
        if self.config["environment_detection"]["game_detection"]:
            game_path, game_version = self._detect_game_installation()
            game_installed = game_path is not None
        
        # 资源检测
        available_disk_gb = 0.0
        available_memory_gb = 0.0
        
        if self.config["environment_detection"]["resource_check"]:
            available_disk_gb = self._get_available_disk()
            available_memory_gb = self._get_available_memory()
        
        # 创建环境信息对象
        env_info = EnvironmentInfo(
            os_name=os_name,
            os_version=os_version,
            python_version=python_version,
            game_installed=game_installed,
            game_path=game_path,
            game_version=game_version,
            available_disk_gb=available_disk_gb,
            available_memory_gb=available_memory_gb
        )
        
        self.environment_info = env_info
        logger.info(f"环境检测完成: {os_name} {os_version}, 游戏安装: {game_installed}")
        
        return env_info
    
    def _detect_game_installation(self) -> Tuple[Optional[str], Optional[str]]:
        """检测游戏安装"""
        game_paths = []
        
        # 根据操作系统选择检测路径
        if platform.system() == "Windows":
            game_paths = self.GAME_PATHS_WINDOWS
        else:
            game_paths = self.GAME_PATHS_LINUX
        
        # 扩展用户主目录路径
        expanded_paths = []
        for path in game_paths:
            if path.startswith("~"):
                expanded_paths.append(os.path.expanduser(path))
            else:
                expanded_paths.append(path)
        
        # 检查每个路径
        for path in expanded_paths:
            if os.path.exists(path):
                logger.info(f"检测到游戏路径: {path}")
                
                # 尝试检测游戏版本
                version = self._detect_game_version(path)
                return path, version
        
        logger.info("未检测到游戏安装")
        return None, None
    
    def _detect_game_version(self, game_path: str) -> Optional[str]:
        """检测游戏版本"""
        try:
            # 检查常见的版本文件
            version_files = [
                "version.txt",
                "VERSION",
                "游戏版本.txt",
                "石器时代版本.txt",
            ]
            
            for version_file in version_files:
                file_path = os.path.join(game_path, version_file)
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().strip()
                        if content:
                            return content
            
            # 检查可执行文件版本
            exe_files = [
                "石器时代.exe",
                "stoneage.exe",
                "sq.exe",
            ]
            
            for exe_file in exe_files:
                exe_path = os.path.join(game_path, exe_file)
                if os.path.exists(exe_path):
                    # 这里可以添加更复杂的版本检测逻辑
                    # 暂时返回文件修改时间作为版本标识
                    mtime = os.path.getmtime(exe_path)
                    return datetime.fromtimestamp(mtime).strftime("%Y%m%d")
        
        except Exception as e:
            logger.debug(f"检测游戏版本失败: {e}")
        
        return "未知版本"
    
    def _get_available_disk(self) -> float:
        """获取可用磁盘空间（GB）"""
        try:
            if platform.system() == "Windows":
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(os.path.expanduser("~")), 
                    None, None, ctypes.pointer(free_bytes)
                )
                free_gb = free_bytes.value / (1024**3)
            else:
                stat = os.statvfs(os.path.expanduser("~"))
                free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            
            return round(free_gb, 1)
        
        except Exception as e:
            logger.warning(f"获取磁盘空间失败: {e}")
            return 0.0
    
    def _get_available_memory(self) -> float:
        """获取可用内存（GB）"""
        try:
            if platform.system() == "Windows":
                import ctypes
                kernel32 = ctypes.windll.kernel32
                c_ulong = ctypes.c_ulong
                
                class MEMORYSTATUS(ctypes.Structure):
                    _fields_ = [
                        ('dwLength', c_ulong),
                        ('dwMemoryLoad', c_ulong),
                        ('dwTotalPhys', c_ulong),
                        ('dwAvailPhys', c_ulong),
                        ('dwTotalPageFile', c_ulong),
                        ('dwAvailPageFile', c_ulong),
                        ('dwTotalVirtual', c_ulong),
                        ('dwAvailVirtual', c_ulong)
                    ]
                
                memoryStatus = MEMORYSTATUS()
                memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUS)
                kernel32.GlobalMemoryStatus(ctypes.byref(memoryStatus))
                
                available_gb = memoryStatus.dwAvailPhys / (1024**3)
            
            elif platform.system() == "Linux":
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if 'MemAvailable' in line:
                            parts = line.split()
                            available_kb = int(parts[1])
                            available_gb = available_kb / (1024**2)
                            break
                    else:
                        available_gb = 0.0
            
            else:  # macOS
                import subprocess
                output = subprocess.check_output(['sysctl', '-n', 'hw.memsize']).decode().strip()
                total_bytes = int(output)
                # macOS没有直接的可用内存信息，这里返回总内存
                available_gb = total_bytes / (1024**3) * 0.5  # 假设50%可用
            
            return round(available_gb, 1)
        
        except Exception as e:
            logger.warning(f"获取内存信息失败: {e}")
            return 0.0
    
    def generate_configuration(self, environment: str = None, 
                              custom_settings: Dict = None) -> Configuration:
        """生成配置"""
        # 确定环境
        if environment is None:
            environment = self.config["template_management"]["default_environment"]
        
        if environment not in self.templates:
            logger.warning(f"环境 {environment} 没有模板，使用默认环境")
            environment = self.config["template_management"]["default_environment"]
        
        logger.info(f"为环境 {environment} 生成配置")
        
        # 获取基础模板
        template = self.templates[environment]
        settings = template.get("settings", {}).copy()
        
        # 应用自定义设置
        if custom_settings:
            self._merge_settings(settings, custom_settings)
        
        # 应用环境特定调整
        settings = self._apply_environment_adjustments(settings, environment)
        
        # 创建配置对象
        config_id = f"config_{int(datetime.now().timestamp())}_{environment}"
        configuration = Configuration(
            config_id=config_id,
            created_at=datetime.now(),
            environment=environment,
            settings=settings,
            validation_results=[],
            optimization_suggestions=[]
        )
        
        # 验证配置
        if self.config["validation"]["validate_on_generate"]:
            validation_results = self.validate_configuration(configuration)
            configuration.validation_results = validation_results
        
