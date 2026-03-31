@echo off
chcp 65001 >nul
title 石器时代工具打包 - 项目下载
color 0A

echo ========================================
echo   石器时代工具打包 - 项目下载
echo ========================================
echo.

REM 检查是否已运行环境设置
if not exist "check_env.py" (
    echo ⚠️  请先运行 01_setup.bat 设置环境
    pause
    exit /b 1
)

echo 📋 检查网络连接...
echo.

REM 测试网络连接
ping -n 1 8.8.8.8 >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ 网络连接失败
    echo 请检查网络连接后重试
    pause
    exit /b 1
)

echo ✅ 网络连接正常

echo.
echo 📥 下载选项...
echo.

echo 请选择下载方式:
echo 1. 从GitHub克隆 (推荐，需要Git)
echo 2. 下载ZIP文件 (备用)
echo 3. 使用本地已有文件
echo.

set /p choice="请输入选项 (1-3): "

if "%choice%"=="1" (
    call :download_git
) else if "%choice%"=="2" (
    call :download_zip
) else if "%choice%"=="3" (
    call :use_local
) else (
    echo ❌ 无效选项
    pause
    exit /b 1
)

echo.
echo ========================================
echo   项目下载完成!
echo ========================================
echo.
echo ✅ 项目文件准备就绪
echo 📁 项目位置: %CD%\stone-age-tools\
echo 📋 包含工具: 10个核心石器时代工具
echo.
echo 📋 下一步:
echo 运行 03_pack.bat 开始打包
echo.
echo 🎯 今日目标: 完成10个核心工具EXE打包
echo ⏰ 预计完成: 22:30前
echo.
pause
exit /b 0

:download_git
echo.
echo 🔄 从GitHub克隆项目...
echo.

REM 检查Git
git --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Git未安装
    echo 正在下载Git...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.35.1.windows.1/Git-2.35.1-64-bit.exe' -OutFile 'Git-2.35.1-64-bit.exe'"
    
    if exist "Git-2.35.1-64-bit.exe" (
        echo ✅ Git安装包下载完成
        echo 请手动运行安装程序
        start Git-2.35.1-64-bit.exe
        echo.
        echo 安装完成后，请重新运行此脚本
        pause
        exit /b 1
    ) else (
        echo ❌ Git下载失败，请使用ZIP下载方式
        pause
        exit /b 1
    )
)

echo ✅ Git已安装: 
git --version

REM 设置GitHub仓库
set GITHUB_URL=https://github.com/limaohui1-ctrl/stone-age-tools.git

if exist "stone-age-tools" (
    echo ⚠️  项目目录已存在，更新...
    cd stone-age-tools
    git pull
    cd ..
    echo ✅ 项目更新完成
) else (
    echo 正在克隆仓库: %GITHUB_URL%
    git clone %GITHUB_URL%
    
    if %errorLevel% neq 0 (
        echo ❌ 克隆失败，尝试使用ZIP下载
        call :download_zip
        exit /b 0
    )
    
    echo ✅ 项目克隆完成
)

REM 检查项目结构
if exist "stone-age-tools\source" (
    echo ✅ 项目结构完整
) else (
    echo ⚠️  项目结构不完整，正在修复...
    
    REM 创建标准目录结构
    cd stone-age-tools
    mkdir source 2>nul
    mkdir dist 2>nul
    mkdir build 2>nul
    mkdir logs 2>nul
    cd ..
    
    echo ✅ 项目结构修复完成
)

goto :eof

:download_zip
echo.
echo 📦 下载ZIP文件...
echo.

set ZIP_URL=https://github.com/limaohui1-ctrl/stone-age-tools/archive/refs/heads/main.zip

echo 正在下载项目ZIP文件...
powershell -Command "Invoke-WebRequest -Uri '%ZIP_URL%' -OutFile 'stone-age-tools.zip'"

if not exist "stone-age-tools.zip" (
    echo ❌ ZIP文件下载失败
    echo 备用方案: 手动下载
    echo 下载地址: %ZIP_URL%
    pause
    exit /b 1
)

echo ✅ ZIP文件下载完成

echo 正在解压文件...
powershell -Command "Expand-Archive -Path 'stone-age-tools.zip' -DestinationPath '.' -Force"

if exist "stone-age-tools-main" (
    ren stone-age-tools-main stone-age-tools
    echo ✅ 文件解压完成
) else (
    echo ❌ 解压失败
    pause
    exit /b 1
)

REM 清理ZIP文件
del stone-age-tools.zip 2>nul

echo ✅ 项目下载完成

goto :eof

:use_local
echo.
echo 📁 使用本地已有文件...
echo.

if exist "stone-age-tools" (
    echo ✅ 使用现有项目目录
) else (
    echo ❌ 未找到本地项目目录
    echo 请先下载项目文件
    pause
    exit /b 1
)

echo ✅ 本地项目准备就绪

goto :eof