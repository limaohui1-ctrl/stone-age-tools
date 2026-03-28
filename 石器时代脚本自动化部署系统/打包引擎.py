#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石器时代脚本自动化部署系统 - 打包引擎
负责将ASSA脚本和相关资源打包为可部署单元

功能:
1. 脚本文件收集和整理
2. 资源文件（图片、配置等）打包
3. 依赖库分析和包含
4. 生成部署包（ZIP、EXE、安装程序等）
5. 包清单生成和版本管理

设计原则:
- 灵活支持多种打包格式
- 智能依赖分析
- 完整的错误处理
- 与现有工具链集成
"""

import os
import sys
import json
import shutil
import hashlib
import logging
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
import yaml

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('打包引擎日志.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    """文件信息"""
    path: str
    size: int
    md5: str
    mtime: datetime
    file_type: str  # script, resource, config, library, other
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        data['mtime'] = self.mtime.isoformat()
        return data


@dataclass
class PackageManifest:
    """包清单"""
    package_id: str
    version: str
    created_at: datetime
    files: List[FileInfo]
    dependencies: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['files'] = [f.to_dict() for f in self.files]
        return data
    
    def save(self, path: str):
        """保存到文件"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'PackageManifest':
        """从文件加载"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 转换时间字段
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        # 转换文件信息
        files = []
        for file_data in data['files']:
            file_data['mtime'] = datetime.fromisoformat(file_data['mtime'])
            files.append(FileInfo(**file_data))
        
        data['files'] = files
        return cls(**data)


class PackagingEngine:
    """打包引擎核心类"""
    
    # 支持的打包格式
    SUPPORTED_FORMATS = {
        'zip': 'ZIP压缩包',
        'exe': '可执行文件（需要EXE优化工具）',
        'dir': '目录结构（不压缩）',
        'tar': 'TAR归档（可选gzip/bzip2压缩）',
    }
    
    # 文件类型识别
    FILE_TYPES = {
        '.assa': 'script',
        '.lua': 'script',
        '.txt': 'config',
        '.json': 'config',
        '.yaml': 'config',
        '.yml': 'config',
        '.ini': 'config',
        '.png': 'resource',
        '.jpg': 'resource',
        '.jpeg': 'resource',
        '.gif': 'resource',
        '.bmp': 'resource',
        '.dll': 'library',
        '.so': 'library',
        '.dylib': 'library',
        '.py': 'library',
    }
    
    def __init__(self, config_path: str = "打包配置.yaml"):
        """
        初始化打包引擎
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.temp_dir = None
        self.current_manifest = None
        
        # 统计信息
        self.stats = {
            "total_packages": 0,
            "total_files": 0,
            "total_size": 0,
            "successful_packages": 0,
            "failed_packages": 0,
        }
        
        logger.info("打包引擎初始化完成")
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        default_config = {
            "packaging": {
                "default_format": "zip",
                "compression_level": 6,  # 0-9，0不压缩，9最大压缩
                "include_hidden_files": False,
                "follow_symlinks": False,
                "max_package_size_mb": 100,
            },
            "file_selection": {
                "include_patterns": ["*.assa", "*.lua", "*.txt", "*.json", "*.yaml", "*.png", "*.jpg"],
                "exclude_patterns": [".git", "__pycache__", "*.tmp", "*.log"],
                "min_file_size_kb": 1,
                "max_file_size_mb": 10,
            },
            "dependency_analysis": {
                "enabled": True,
                "scan_for_imports": True,
                "auto_include_dependencies": True,
                "dependency_whitelist": [],
                "dependency_blacklist": [],
            },
            "validation": {
                "validate_before_packaging": True,
                "check_file_integrity": True,
                "verify_dependencies": True,
                "generate_checksums": True,
            },
            "integration": {
                "with_exe_optimizer": True,
                "with_stability_toolkit": True,
                "auto_apply_optimizations": True,
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
    
    def _create_temp_directory(self) -> str:
        """创建临时目录"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            return self.temp_dir
        
        self.temp_dir = tempfile.mkdtemp(prefix="石器时代打包_")
        logger.info(f"创建临时目录: {self.temp_dir}")
        return self.temp_dir
    
    def _cleanup_temp_directory(self):
        """清理临时目录"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"清理临时目录: {self.temp_dir}")
                self.temp_dir = None
            except Exception as e:
                logger.warning(f"清理临时目录失败: {e}")
    
    def _get_file_info(self, file_path: str) -> Optional[FileInfo]:
        """获取文件信息"""
        try:
            stat = os.stat(file_path)
            
            # 计算MD5
            md5_hash = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    md5_hash.update(chunk)
            
            # 确定文件类型
            file_type = "other"
            for ext, type_name in self.FILE_TYPES.items():
                if file_path.lower().endswith(ext):
                    file_type = type_name
                    break
            
            return FileInfo(
                path=file_path,
                size=stat.st_size,
                md5=md5_hash.hexdigest(),
                mtime=datetime.fromtimestamp(stat.st_mtime),
                file_type=file_type
            )
        
        except Exception as e:
            logger.error(f"获取文件信息失败 {file_path}: {e}")
            return None
    
    def _collect_files(self, source_dir: str, recursive: bool = True) -> List[FileInfo]:
        """收集文件"""
        collected_files = []
        
        try:
            if not os.path.isdir(source_dir):
                logger.error(f"源目录不存在: {source_dir}")
                return collected_files
            
            logger.info(f"开始收集文件: {source_dir}")
            
            # 遍历目录
            for root, dirs, files in os.walk(source_dir):
                # 应用排除模式
                dirs[:] = [d for d in dirs if not self._should_exclude(d)]
                
                for filename in files:
                    file_path = os.path.join(root, filename)
                    
                    # 检查是否应该包含
                    if self._should_include(file_path):
                        file_info = self._get_file_info(file_path)
                        if file_info:
                            collected_files.append(file_info)
                
                # 如果不是递归模式，只处理顶层目录
                if not recursive:
                    break
            
            logger.info(f"收集到 {len(collected_files)} 个文件")
            
        except Exception as e:
            logger.error(f"收集文件失败: {e}")
        
        return collected_files
    
    def _should_include(self, file_path: str) -> bool:
        """检查是否应该包含文件"""
        filename = os.path.basename(file_path)
        
        # 检查排除模式
        for pattern in self.config["file_selection"]["exclude_patterns"]:
            if self._pattern_match(filename, pattern):
                return False
        
        # 检查包含模式
        for pattern in self.config["file_selection"]["include_patterns"]:
            if self._pattern_match(filename, pattern):
                # 检查文件大小限制
                try:
                    file_size = os.path.getsize(file_path)
                    min_size = self.config["file_selection"]["min_file_size_kb"] * 1024
                    max_size = self.config["file_selection"]["max_file_size_mb"] * 1024 * 1024
                    
                    if file_size < min_size:
                        logger.debug(f"文件太小被排除: {file_path} ({file_size} bytes)")
                        return False
                    
                    if file_size > max_size:
                        logger.debug(f"文件太大被排除: {file_path} ({file_size} bytes)")
                        return False
                    
                    return True
                except:
                    pass
        
        # 默认不包含
        return False
    
    def _should_exclude(self, dir_name: str) -> bool:
        """检查是否应该排除目录"""
        for pattern in self.config["file_selection"]["exclude_patterns"]:
            if self._pattern_match(dir_name, pattern):
                return True
        return False
    
    def _pattern_match(self, text: str, pattern: str) -> bool:
        """简单的通配符匹配"""
        if pattern.startswith("*"):
            return text.endswith(pattern[1:])
        elif pattern.endswith("*"):
            return text.startswith(pattern[:-1])
        else:
            return text == pattern
    
    def _analyze_dependencies(self, files: List[FileInfo]) -> List[str]:
        """分析依赖关系"""
        dependencies = []
        
        if not self.config["dependency_analysis"]["enabled"]:
            return dependencies
        
        logger.info("开始分析依赖关系...")
        
        try:
            # 分析ASSA脚本的导入语句
            for file_info in files:
                if file_info.file_type == "script":
                    deps = self._analyze_script_dependencies(file_info.path)
                    dependencies.extend(deps)
            
            # 去重
            dependencies = list(set(dependencies))
            
            # 应用白名单和黑名单
            whitelist = set(self.config["dependency_analysis"]["dependency_whitelist"])
            blacklist = set(self.config["dependency_analysis"]["dependency_blacklist"])
            
            filtered_deps = []
            for dep in dependencies:
                if dep in blacklist:
                    logger.debug(f"依赖被黑名单排除: {dep}")
                    continue
                
                if whitelist and dep not in whitelist:
                    logger.debug(f"依赖不在白名单中: {dep}")
                    continue
                
                filtered_deps.append(dep)
            
            logger.info(f"分析到 {len(filtered_deps)} 个依赖")
            return filtered_deps
            
        except Exception as e:
            logger.error(f"分析依赖关系失败: {e}")
            return dependencies
    
    def _analyze_script_dependencies(self, script_path: str) -> List[str]:
        """分析脚本依赖"""
        dependencies = []
        
        try:
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 简单的导入语句分析（针对ASSA脚本）
            # 这里可以根据实际脚本语法调整
            import_keywords = ["include", "require", "import", "load"]
            
            for line in content.split('\n'):
                line = line.strip()
                for keyword in import_keywords:
                    if keyword in line.lower():
                        # 提取文件名
                        # 这需要根据实际脚本语法调整
                        parts = line.split()
                        for part in parts:
                            if part.endswith('.assa') or part.endswith('.lua'):
                                dependencies.append(part.strip('"\''))
            
        except Exception as e:
            logger.debug(f"分析脚本依赖失败 {script_path}: {e}")
        
        return dependencies
    
    def _create_package_manifest(self, files: List[FileInfo], 
                                dependencies: List[str],
                                metadata: Dict) -> PackageManifest:
        """创建包清单"""
        package_id = f"package_{int(time.time())}_{hashlib.md5(str(files).encode()).hexdigest()[:8]}"
        
        manifest = PackageManifest(
            package_id=package_id,
            version=metadata.get("version", "1.0.0"),
            created_at=datetime.now(),
            files=files,
            dependencies=dependencies,
            metadata=metadata
        )
        
        return manifest
    
    def _validate_package(self, manifest: PackageManifest) -> Tuple[bool, List[str]]:
        """验证包"""
        errors = []
        
        if not manifest.files:
            errors.append("包中没有文件")
        
        # 检查文件完整性
        if self.config["validation"]["check_file_integrity"]:
            for file_info in manifest.files:
                if not os.path.exists(file_info.path):
                    errors.append(f"文件不存在: {file_info.path}")
                    continue
                
                # 验证MD5
                current_info = self._get_file_info(file_info.path)
                if current_info and current_info.md5 != file_info.md5:
                    errors.append(f"文件MD5不匹配: {file_info.path}")
        
        # 检查包大小
        total_size = sum(f.size for f in manifest.files)
        max_size = self.config["packaging"]["max_package_size_mb"] * 1024 * 1024
        
        if total_size > max_size:
            errors.append(f"包大小超过限制: {total_size/(1024*1024):.1f}MB > {self.config['packaging']['max_package_size_mb']}MB")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def _create_zip_package(self, manifest: PackageManifest, output_path: str) -> bool:
        """创建ZIP包"""
        try:
            logger.info(f"创建ZIP包: {output_path}")
            
            compression = zipfile.ZIP_DEFLATED
            compression_level = self.config["packaging"]["compression_level"]
            
            with zipfile.ZipFile(output_path, 'w', compression=compression, 
                               compresslevel=compression_level) as zipf:
                
                # 添加文件
                for file_info in manifest.files:
                    # 计算在ZIP中的相对路径
                    arcname = os.path.relpath(file_info.path, start=os.path.commonpath([f.path for f in manifest.files]))
                    zipf.write(file_info.path, arcname)
                    logger.debug(f"添加文件到ZIP: {arcname}")
                
                # 添加清单文件
                manifest_temp = os.path.join(self.temp_dir, "manifest.json")
                manifest.save(manifest_temp)
                zipf.write(manifest_temp, "manifest.json")
                
                # 添加README文件（如果存在）
                readme_files = ["README.md", "README.txt", "说明.txt"]
                for readme in readme_files:
                    for file_info in manifest.files:
                        if os.path.basename(file_info.path).lower() == readme.lower():
                            # 已经包含在文件中
                            break
                    else:
                        # 创建简单的README
                        readme_content = self._generate_readme(manifest)
                        readme_temp = os.path.join(self.temp_dir, "README.txt")
                        with open(readme_temp, 'w', encoding='utf-8') as f:
                            f.write(readme_content)
                        zipf.write(readme_temp, "README.txt")
                        break
            
            # 验证ZIP文件
            if self._validate_zip_file(output_path):
                logger.info(f"ZIP包创建成功: {output_path} ({os.path.getsize(output_path)/(1024*1024):.1f}MB)")
                return True
            else:
                logger.error(f"ZIP包验证失败: {output_path}")
                return False
            
        except Exception as e:
            logger.error(f"创建ZIP包失败: {e}")
            return False
    
    def _validate_zip_file(self, zip_path: str) -> bool:
        """验证ZIP文件"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                #