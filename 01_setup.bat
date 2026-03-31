@echo off
chcp 65001 >nul
title 石器时代工具打包 - 环境设置
color 0A

echo ========================================
echo   石器时代工具打包 - 环境设置
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

echo.
echo 📋 检查系统环境...
echo.

REM 检查Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Python未安装
    echo 正在下载Python 3.8.10...
    
    REM 下载Python安装包
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe' -OutFile 'python-3.8.10.exe'"
    
    if exist "python-3.8.10.exe" (
        echo ✅ Python安装包下载完成
        echo 请手动运行安装程序，确保勾选"Add Python to PATH"
        start python-3.8.10.exe
        echo.
        echo 安装完成后，请重新运行此脚本
        pause
        exit /b 1
    ) else (
        echo ❌ 下载失败，请手动下载Python
        echo 下载地址: https://www.python.org/downloads/release/python-3810/
        pause
        exit /b 1
    )
) else (
    echo ✅ Python已安装
    python --version
)

REM 检查pip
pip --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ pip未安装或未配置
    echo 正在尝试修复...
    python -m ensurepip --default-pip
    echo ✅ pip修复完成
) else (
    echo ✅ pip已安装
    pip --version
)

echo.
echo 🔧 安装核心依赖库...
echo.

REM 使用国内镜像源加速
set PIP_MIRROR=https://pypi.tuna.tsinghua.edu.cn/simple

echo 安装PyInstaller...
pip install -i %PIP_MIRROR% pyinstaller
if %errorLevel% neq 0 (
    echo ⚠️  PyInstaller安装失败，尝试标准源...
    pip install pyinstaller
)

echo 安装核心工具依赖...
pip install -i %PIP_MIRROR% psutil ping3 numpy
if %errorLevel% neq 0 (
    echo ⚠️  部分依赖安装失败，继续安装其他...
)

echo 安装GUI依赖...
pip install -i %PIP_MIRROR% pyqt5
if %errorLevel% neq 0 (
    echo ⚠️  PyQt5安装失败，跳过...
)

echo 安装数据处理依赖...
pip install -i %PIP_MIRROR% pandas matplotlib
if %errorLevel% neq 0 (
    echo ⚠️  数据处理依赖安装失败，跳过...
)

echo 安装图像处理依赖...
pip install -i %PIP_MIRROR% opencv-python
if %errorLevel% neq 0 (
    echo ⚠️  OpenCV安装失败，跳过...
)

echo 安装OCR依赖...
pip install -i %PIP_MIRROR% pytesseract
if %errorLevel% neq 0 (
    echo ⚠️  Tesseract安装失败，跳过...
)

echo.
echo 📁 创建项目目录结构...
echo.

REM 创建目录结构
mkdir dist 2>nul
mkdir build 2>nul
mkdir logs 2>nul
mkdir source 2>nul
mkdir tools 2>nul

echo ✅ 目录结构创建完成

echo.
echo 📝 创建环境验证脚本...
echo.

REM 创建环境验证脚本
cat > check_env.py << 'PYTHONEOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境验证脚本
"""

import sys
import platform
import subprocess
from datetime import datetime

def check_python():
    """检查Python环境"""
    print("🔍 检查Python环境...")
    print(f"Python版本: {sys.version}")
    print(f"平台: {platform.platform()}")
    return True

def check_dependencies():
    """检查依赖库"""
    print("\n🔍 检查依赖库...")
    
    dependencies = [
        ("psutil", "系统监控"),
        ("ping3", "网络检测"),
        ("numpy", "数值计算"),
        ("PyQt5", "GUI界面"),
        ("pandas", "数据处理"),
        ("matplotlib", "图表绘制"),
        ("opencv-python", "图像处理"),
        ("pytesseract", "OCR识别"),
        ("pyinstaller", "打包工具")
    ]
    
    missing = []
    for dep, desc in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} ({desc}) - 已安装")
        except ImportError:
            print(f"❌ {dep} ({desc}) - 未安装")
            missing.append(dep)
    
    if missing:
        print(f"\n⚠️  缺失依赖: {', '.join(missing)}")
        print("运行以下命令安装:")
        print(f"pip install {' '.join(missing)}")
        return False
    else:
        print("\n✅ 所有依赖库已安装")
        return True

def check_pyinstaller():
    """检查PyInstaller"""
    print("\n🔍 检查PyInstaller...")
    try:
        result = subprocess.run(["pyinstaller", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PyInstaller版本: {result.stdout.strip()}")
            return True
        else:
            print("❌ PyInstaller检查失败")
            return False
    except Exception as e:
        print(f"❌ PyInstaller异常: {e}")
        return False

def main():
    print("=" * 50)
    print("石器时代工具打包 - 环境验证")
    print("=" * 50)
    
    all_ok = True
    
    # 检查各项
    if not check_python():
        all_ok = False
    
    if not check_dependencies():
        all_ok = False
    
    if not check_pyinstaller():
        all_ok = False
    
    print("\n" + "=" * 50)
    if all_ok:
        print("🎉 环境验证通过，可以开始打包!")
    else:
        print("⚠️  环境验证失败，请修复问题后重试")
    
    print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    return all_ok

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
PYTHONEOF

echo ✅ 环境验证脚本创建完成

echo.
echo 🧪 运行环境验证...
echo.

python check_env.py
if %errorLevel% neq 0 (
    echo ❌ 环境验证失败
    echo 请查看上面的错误信息并修复问题
    pause
    exit /b 1
)

echo.
echo ========================================
echo   环境设置完成!
echo ========================================
echo.
echo ✅ Python环境就绪
echo ✅ 依赖库安装完成
echo ✅ 目录结构创建完成
echo ✅ 环境验证通过
echo.
echo 📋 下一步:
echo 1. 运行 02_download.bat 下载项目文件
echo 2. 运行 03_pack.bat 开始打包
echo.
echo 🎯 今日目标: 完成10个核心工具EXE打包
echo ⏰ 预计完成: 22:30前
echo.
pause