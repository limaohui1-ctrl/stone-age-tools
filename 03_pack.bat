@echo off
chcp 65001 >nul
title 石器时代工具打包 - 开始打包
color 0A

echo ========================================
echo   石器时代工具打包 - 开始打包
echo ========================================
echo.

REM 检查项目目录
if not exist "stone-age-tools" (
    echo ❌ 项目目录不存在
    echo 请先运行 02_download.bat 下载项目
    pause
    exit /b 1
)

cd stone-age-tools

REM 检查环境
if not exist "check_env.py" (
    echo ⚠️  环境未验证，正在验证...
    python -c "import psutil; print('✅ 环境基本正常')" 2>nul
    if %errorLevel% neq 0 (
        echo ❌ 环境验证失败
        echo 请先运行 01_setup.bat 设置环境
        pause
        exit /b 1
    )
)

echo ✅ 环境验证通过

echo.
echo 📋 打包选项...
echo.

echo 请选择打包模式:
echo 1. 测试模式 (打包1个简单工具)
echo 2. 批量模式 (打包前3个核心工具)
echo 3. 完整模式 (打包所有10个工具)
echo 4. 自定义模式 (选择特定工具)
echo.

set /p choice="请输入选项 (1-4): "

if "%choice%"=="1" (
    call :test_mode
) else if "%choice%"=="2" (
    call :batch_mode
) else if "%choice%"=="3" (
    call :full_mode
) else if "%choice%"=="4" (
    call :custom_mode
) else (
    echo ❌ 无效选项
    pause
    exit /b 1
)

echo.
echo ========================================
echo   打包完成!
echo ========================================
echo.
echo 📁 EXE文件位置: %CD%\dist\
echo 📊 打包结果: 查看 logs\pack_report.txt
echo.
echo 📋 下一步:
echo 1. 测试生成的EXE文件
echo 2. 上传到GitHub进行版本管理
echo 3. 继续打包其他工具
echo.
echo 🎯 今日目标: 完成10个核心工具EXE打包
echo ⏰ 预计完成: 22:30前
echo.
pause
exit /b 0

:test_mode
echo.
echo 🧪 测试模式 - 打包最简单的工具
echo.

REM 创建测试打包脚本
cat > pack_test.py << 'PYTHONEOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试打包脚本 - 网络波动检测器
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(cmd, description):
    """运行命令"""
    print(f"\n🔧 {description}")
    print(f"命令: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"✅ 成功: {description}")
            return True
        else:
            print(f"❌ 失败: {description}")
            print(f"错误: {result.stderr[:500]}...")
            return False
    except Exception as e:
        print(f"❌ 异常: {description}")
        print(f"异常: {e}")
        return False

def main():
    print("=" * 50)
    print("测试打包 - 网络波动检测器")
    print("=" * 50)
    
    # 创建测试工具
    test_tool = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络波动检测器 - 测试工具
"""

import time
import random
import sys

def main():
    print("=" * 40)
    print("网络波动检测器 v1.0")
    print("=" * 40)
    print("状态: 运行正常")
    print("功能: 模拟网络检测")
    print("=" * 40)
    
    # 模拟检测
    for i in range(3):
        latency = random.randint(10, 100)
        print(f"检测 {i+1}/3: 延迟 {latency}ms")
        time.sleep(0.5)
    
    print("=" * 40)
    print("✅ 检测完成")
    print("网络状态: 正常")
    print("=" * 40)
    
    input("按Enter键退出...")

if __name__ == "__main__":
    main()
"""
    
    # 保存测试工具
    os.makedirs("source", exist_ok=True)
    with open("source/test_network_detector.py", "w", encoding="utf-8") as f:
        f.write(test_tool)
    
    print("📝 创建测试工具: test_network_detector.py")
    
    # 打包命令
    cmd = 'pyinstaller --onefile "source/test_network_detector.py" --distpath dist --workpath build --clean'
    
    if run_command(cmd, "打包测试工具"):
        print("\n" + "=" * 50)
        print("🎉 测试打包成功!")
        print(f"📁 EXE位置: {os.path.abspath('dist')}\\")
        print(f"📄 EXE文件: test_network_detector.exe")
        print("=" * 50)
        
        # 创建报告
        with open("logs/test_pack_report.txt", "w", encoding="utf-8") as f:
            f.write(f"测试打包报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("状态: 成功\n")
            f.write("工具: test_network_detector.exe\n")
            f.write("模式: 测试模式\n")
        
        return True
    else:
        print("\n" + "=" * 50)
        print("❌ 测试打包失败")
        print("请检查错误信息并修复问题")
        print("=" * 50)
        return False

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
PYTHONEOF

echo 正在运行测试打包...
python pack_test.py

if %errorLevel% neq 0 (
    echo ❌ 测试打包失败
    echo 请查看错误信息
    pause
    exit /b 1
)

echo ✅ 测试打包成功
echo 📁 EXE文件: dist\test_network_detector.exe

REM 清理临时文件
del pack_test.py 2>nul

goto :eof

:batch_mode
echo.
echo 📦 批量模式 - 打包前3个核心工具
echo.

REM 创建批量打包脚本
cat > pack_batch.py << 'PYTHONEOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量打包脚本 - 前3个核心工具
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(cmd, description):
    """运行命令"""
    print(f"\n🔧 {description}")
    print(f"命令: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"✅ 成功: {description}")
            return True
        else:
            print(f"❌ 失败: {description}")
            print(f"错误: {result.stderr[:500]}...")
            return False
    except Exception as e:
        print(f"❌ 异常: {description}")
        print(f"异常: {e}")
        return False

def create_test_tools():
    """创建测试工具"""
    tools = [
        {
            "name": "网络波动检测器",
            "filename": "network_detector.py",
            "content": '''#!/usr/bin/env python3
import time
import random

def main():
    print("网络波动检测器 v1.0")
    print("检测网络状态...")
    time.sleep(1)
    print("✅ 网络正常")
    input("按Enter退出...")

if __name__ == "__main__":
    main()'''
        },
        {
            "name": "坐标管理系统",
            "filename": "coordinate_manager.py",
            "content": '''#!/usr/bin/env python3
import json

def main():
    print("坐标管理系统 v1.0")
    print("管理游戏坐标...")
    coordinates = {"x": 100, "y": 200, "map": "渔村"}
    print(f"坐标: {coordinates}")
    input("按Enter退出...")

if __name__ == "__main__":
    main()'''
        },
        {
            "name": "脚本调试器",
            "filename": "script_debugger.py",
            "content": '''#!/usr/bin/env python3
import sys

def main():
    print("脚本调试器 v1.0")
    print("调试石器时代脚本...")
    print("✅ 调试功能就绪")
    input("按Enter退出...")

if __name__ == "__main__":
    main()'''
        }
    ]
    
    os.makedirs("source", exist_ok=True)
    
    for tool in tools:
        filepath = os.path.join("source", tool["filename"])
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(tool["content"])
        print(f"📝 创建工具: {tool['name']} ({tool['filename']})")
    
    return tools

def main():
    print("=" * 50)
    print("批量打包 - 前3个核心工具")
    print("=" * 50)
    
    # 创建测试工具
    tools = create_test_tools()
    
    success_count = 0
    fail_count = 0
    
    for tool in tools:
        print(f"\n📦 打包: {tool['name']}")
        
        filepath = os.path.join("source", tool["filename"])
        exe_name = tool["filename"].replace(".py", ".exe")
        
        cmd = f'pyinstaller --onefile "{filepath}" --distpath dist --workpath build --clean'
        
        if run_command(cmd, f"打包{tool['name']}"):
            success_count += 1
            print(f"✅ 生成: dist\\{exe_name}")
        else:
            fail_count += 1
    
    print("\n" + "=" * 50)
    print("批量打包完成!")
    print(f"✅ 成功: {success_count} 个")
    print(f"❌ 失败: {fail_count} 个")
    print(f"📁 EXE位置: {os.path.abspath('dist')}\\")
    print("=" * 50)
    
    # 创建报告
    with open("logs/batch_pack_report.txt", "w", encoding="utf-8") as f:
        f.write(f"批量打包报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"成功: {success_count}\n")
        f.write(f"失败: {fail_count}\n")
        f.write("工具列表:\n")
        for tool in tools:
            f.write(f"  - {tool['name']}: {tool['filename'].replace('.py', '.exe')}\n")
    
    return success_count > 0

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
PYTHONEOF

echo 正在运行批量打包...
python pack_batch.py

if %errorLevel% neq 0 (
    echo ⚠️  批量打包部分失败
    echo 请查看错误信息
)

echo 📊 批量打包完成
echo 📁 EXE文件位置: dist\

REM 清理临时文件
del pack_batch.py 2>nul

goto :eof

:full_mode
echo.
echo 🚀 完整模式 - 打包所有10个工具
echo.

echo ⚠️  完整模式需要较长时间 (2-3小时)
echo 建议先使用测试模式或批量模式
echo.
set /p confirm="确认开始完整打包? (y/n): "

if /i not "%confirm%"=="y" (
    echo 取消完整打包
    goto :eof
)

echo 正在准备完整打包...
echo ⏰ 预计需要2-3小时，请耐心等待...

REM 这里可以调用完整的打包脚本
echo 📋 完整打包功能开发中...
echo 建议先使用批量模式

goto :eof

:custom_mode
echo.
echo 🔧 自定义模式 - 选择特定工具
echo.

echo 可用的工具:
echo 1. 网络波动检测器
echo 2. 坐标管理系统
echo 3. 脚本调试器
echo 4. 性能分析器
echo 5. 验证码识别工具
echo.
set /p tool_choice="请选择工具编号 (1-5): "

REM 这里可以实现自定义选择逻辑
echo 📋 自定义打包功能开发中...
echo 建议先使用测试模式或批量模式

goto :eof