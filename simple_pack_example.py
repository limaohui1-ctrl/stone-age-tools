#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单打包示例 - 石器时代工具打包
"""

import os
import sys
import subprocess
from datetime import datetime

def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("石器时代工具打包示例")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def check_environment():
    """检查环境"""
    print("🔍 检查打包环境...")
    
    # 检查Python
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True)
        print(f"✅ Python版本: {result.stdout.strip()}")
    except:
        print("❌ Python检查失败")
        return False
    
    # 检查PyInstaller
    try:
        result = subprocess.run(["pyinstaller", "--version"], 
                              capture_output=True, text=True)
        print(f"✅ PyInstaller版本: {result.stdout.strip()}")
    except:
        print("❌ PyInstaller未安装，请运行: pip install pyinstaller")
        return False
    
    return True

def create_simple_tool():
    """创建简单的测试工具"""
    print("\n📝 创建简单测试工具...")
    
    tool_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石器时代网络波动检测器 - 简单示例
"""

import time
import random

def main():
    print("=" * 40)
    print("石器时代网络波动检测器 v1.0")
    print("=" * 40)
    print("功能: 模拟网络延迟检测")
    print("状态: 运行中...")
    print("=" * 40)
    
    # 模拟网络检测
    for i in range(5):
        latency = random.randint(20, 150)
        packet_loss = random.random() * 5
        print(f"检测 {i+1}/5: 延迟 {latency}ms, 丢包率 {packet_loss:.1f}%")
        time.sleep(0.3)
    
    print("=" * 40)
    print("✅ 检测完成")
    print("网络状态: 正常 (建议优化)")
    print("=" * 40)
    
    input("按Enter键退出...")

if __name__ == "__main__":
    main()
'''
    
    # 创建工具目录
    os.makedirs("tools", exist_ok=True)
    
    # 保存工具文件
    tool_path = "tools/simple_network_detector.py"
    with open(tool_path, "w", encoding="utf-8") as f:
        f.write(tool_code)
    
    print(f"✅ 创建工具: {tool_path}")
    return tool_path

def pack_tool(tool_path):
    """打包工具"""
    print(f"\n📦 打包工具: {os.path.basename(tool_path)}")
    
    # 创建输出目录
    os.makedirs("dist", exist_ok=True)
    os.makedirs("build", exist_ok=True)
    
    # 打包命令
    cmd = [
        "pyinstaller",
        "--onefile",  # 单文件模式
        "--windowed",  # 窗口模式 (不显示控制台)
        f"--distpath=dist",
        f"--workpath=build",
        "--clean",  # 清理缓存
        tool_path
    ]
    
    print(f"命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 打包成功!")
            
            # 检查生成的EXE文件
            exe_name = os.path.basename(tool_path).replace(".py", ".exe")
            exe_path = os.path.join("dist", exe_name)
            
            if os.path.exists(exe_path):
                size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
                print(f"📁 EXE文件: {exe_path}")
                print(f"📊 文件大小: {size:.1f} MB")
                return True
            else:
                print("❌ EXE文件未生成")
                return False
        else:
            print("❌ 打包失败")
            print(f"错误: {result.stderr[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ 打包异常: {e}")
        return False

def main():
    """主函数"""
    print_banner()
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请修复问题后重试")
        return False
    
    # 创建简单工具
    tool_path = create_simple_tool()
    
    # 打包工具
    success = pack_tool(tool_path)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 示例打包成功完成!")
        print("\n下一步:")
        print("1. 运行 dist/simple_network_detector.exe 测试")
        print("2. 查看其他工具源代码: source/ 目录")
        print("3. 使用批量打包脚本: 03_pack.bat")
    else:
        print("❌ 示例打包失败")
        print("\n建议:")
        print("1. 检查Python和PyInstaller安装")
        print("2. 查看错误信息并修复")
        print("3. 使用简化打包命令重试")
    
    print("=" * 60)
    return success

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)