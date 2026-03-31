@echo off
chcp 65001 >nul
title 石器时代工具打包启动器
color 0A

echo ========================================
echo   石器时代工具打包启动器
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  需要管理员权限
    echo 请右键点击此文件，选择"以管理员身份运行"
    pause
    exit /b 1
)

echo ✅ 管理员权限确认

REM 设置工作目录
set WORK_DIR=C:\石器时代工具打包
echo 工作目录: %WORK_DIR%

REM 创建目录
if not exist "%WORK_DIR%" (
    mkdir "%WORK_DIR%"
    echo ✅ 创建工作目录
)

REM 进入工作目录
cd /d "%WORK_DIR%"

echo.
echo ========================================
echo   步骤1: 检查系统环境
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Python未安装
    echo 正在下载Python 3.8...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe' -OutFile 'python-3.8.10.exe'"
    echo 请手动安装Python 3.8.10
    start python-3.8.10.exe
    pause
    exit /b 1
) else (
    echo ✅ Python已安装
    python --version
)

REM 检查PyInstaller
pyinstaller --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  PyInstaller未安装，正在安装...
    pip install pyinstaller
    echo ✅ PyInstaller安装完成
) else (
    echo ✅ PyInstaller已安装
    pyinstaller --version
)

REM 检查Git
git --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Git未安装
    echo 正在下载Git...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.35.1.windows.1/Git-2.35.1-64-bit.exe' -OutFile 'Git-2.35.1-64-bit.exe'"
    echo 请手动安装Git
    start Git-2.35.1-64-bit.exe
    pause
    exit /b 1
) else (
    echo ✅ Git已安装
    git --version
)

echo.
echo ========================================
echo   步骤2: 克隆GitHub仓库
echo ========================================
echo.

set GITHUB_URL=https://github.com/limaohui1-ctrl/stone-age-tools.git

if not exist "stone-age-tools" (
    echo 正在克隆GitHub仓库...
    git clone %GITHUB_URL%
    if %errorLevel% neq 0 (
        echo ❌ 克隆失败
        echo 备用方案: 手动下载ZIP文件
        powershell -Command "Invoke-WebRequest -Uri 'https://github.com/limaohui1-ctrl/stone-age-tools/archive/refs/heads/main.zip' -OutFile 'stone-age-tools.zip'"
        powershell -Command "Expand-Archive -Path 'stone-age-tools.zip' -DestinationPath '.' -Force"
        ren stone-age-tools-main stone-age-tools
        echo ✅ 下载并解压完成
    ) else (
        echo ✅ 克隆成功
    )
) else (
    echo ✅ 仓库已存在，更新...
    cd stone-age-tools
    git pull
    cd ..
)

echo.
echo ========================================
echo   步骤3: 安装依赖库
echo ========================================
echo.

cd stone-age-tools

if exist "requirements.txt" (
    echo 正在安装Python依赖库...
    pip install -r requirements.txt
    echo ✅ 依赖库安装完成
) else (
    echo ⚠️  未找到requirements.txt，安装核心依赖...
    pip install psutil ping3 numpy matplotlib pyqt5 pandas opencv-python pytesseract
    echo ✅ 核心依赖安装完成
)

echo.
echo ========================================
echo   步骤4: 创建打包脚本
echo ========================================
echo.

REM 创建批量打包脚本
cat > batch_pack_day1.py << 'PYTHONEOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石器时代工具 - 第1天批量打包脚本
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(cmd, description):
    """运行命令并显示进度"""
    print(f"\n🔧 {description}")
    print(f"命令: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"✅ 成功: {description}")
            return True
        else:
            print(f"❌ 失败: {description}")
            print(f"错误: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 异常: {description}")
        print(f"异常: {e}")
        return False

def main():
    print("=" * 50)
    print("石器时代工具 - 第1天批量打包")
    print("=" * 50)
    
    # 创建目录
    os.makedirs("dist", exist_ok=True)
    os.makedirs("build", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    tools_to_pack = [
        {
            "name": "网络波动检测器",
            "path": "source/石器时代网络稳定性优化工具包/网络波动检测器.py",
            "spec": "source/石器时代网络稳定性优化工具包/网络波动检测器.spec"
        },
        {
            "name": "脚本调试器", 
            "path": "source/石器时代脚本调试器.py",
            "spec": None
        },
        {
            "name": "性能分析器",
            "path": "source/石器时代脚本性能分析器.py",
            "spec": None
        }
    ]
    
    success_count = 0
    fail_count = 0
    
    for tool in tools_to_pack:
        print(f"\n📦 打包: {tool['name']}")
        
        # 检查文件是否存在
        if not os.path.exists(tool["path"]):
            print(f"⚠️  文件不存在: {tool['path']}")
            fail_count += 1
            continue
        
        # 使用spec文件或直接打包
        if tool["spec"] and os.path.exists(tool["spec"]):
            cmd = f'pyinstaller "{tool["spec"]}" --distpath dist --workpath build --clean'
        else:
            cmd = f'pyinstaller --onefile --windowed "{tool["path"]}" --distpath dist --workpath build --clean'
        
        if run_command(cmd, f"打包{tool['name']}"):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "=" * 50)
    print("打包完成!")
    print(f"✅ 成功: {success_count} 个")
    print(f"❌ 失败: {fail_count} 个")
    print(f"📁 EXE文件位置: dist/")
    print("=" * 50)
    
    # 创建结果报告
    with open("logs/pack_report.txt", "w", encoding="utf-8") as f:
        f.write(f"打包报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"成功: {success_count}\n")
        f.write(f"失败: {fail_count}\n")
        f.write(f"EXE位置: dist/\n")
    
    return success_count > 0

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
PYTHONEOF

echo ✅ 打包脚本创建完成

echo.
echo ========================================
echo   步骤5: 创建使用指南
echo ========================================
echo.

cat > README_WINDOWS.md << 'EOF'
# 🚀 Windows打包使用指南

## 快速开始

### 1. 运行启动脚本
双击 `start_packing.bat` 文件，选择"以管理员身份运行"。

### 2. 自动环境检查
脚本会自动检查并安装:
- ✅ Python 3.8
- ✅ PyInstaller
- ✅ Git
- ✅ 所有依赖库

### 3. 自动克隆仓库
从GitHub自动克隆所有源代码:
- 仓库: https://github.com/limaohui1-ctrl/stone-age-tools
- 位置: C:\石器时代工具打包\stone-age-tools

### 4. 开始打包
运行批量打包脚本:
```cmd
cd C:\石器时代工具打包\stone-age-tools
python batch_pack_day1.py
```

## 包含的工具

### 第1天打包目标 (10个核心工具)
1. 🎯 **网络稳定性增强工具包** (5个EXE)
2. 🔧 **脚本开发工具** (3个EXE)
3. 🔤 **验证码识别工具** (1个EXE)
4. 📍 **坐标管理系统** (1个EXE)

## 文件结构

```
C:\石器时代工具打包\
├── stone-age-tools\          # GitHub仓库
│   ├── source\              # 源代码
│   ├── dist\                # 生成的EXE文件
│   ├── build\               # 打包临时文件
│   ├── logs\                # 日志文件
│   ├── batch_pack_day1.py   # 批量打包脚本
│   └── README_WINDOWS.md    # 本文件
├── start_packing.bat        # 启动脚本
└── 使用说明.txt             # 简单说明
```

## 手动步骤 (如果需要)

### 安装Python
如果自动安装失败，手动下载:
https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe

### 安装Git
如果自动安装失败，手动下载:
https://github.com/git-for-windows/git/releases/download/v2.35.1.windows.1/Git-2.35.1-64-bit.exe

### 安装依赖库
```cmd
pip install psutil ping3 numpy matplotlib pyqt5 pandas opencv-python pytesseract
```

## 问题解决

### Q1: 管理员权限错误
右键点击 `start_packing.bat` → "以管理员身份运行"

### Q2: 网络连接问题
检查防火墙设置，或使用VPN

### Q3: 依赖安装失败
使用国内镜像:
```cmd
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### Q4: 打包失败
查看 `logs/` 目录下的错误日志

## 技术支持
如有问题，请通过QQ联系。

---

**开始时间**: 立即开始
**预计完成**: 今天22:30前
**目标**: 10个核心工具EXE + GitHub上传
