#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石器时代工具打包进度跟踪系统
自动检测、跟踪和管理石器时代工具打包项目的进度
"""

import os
import json
import datetime
import glob
import hashlib
from pathlib import Path

class StoneAgeToolTracker:
    def __init__(self, workspace_path="/root/.openclaw/workspace"):
        self.workspace = Path(workspace_path)
        self.tracker_file = self.workspace / "stone_tool_progress.json"
        self.load_progress()
        
    def load_progress(self):
        """加载进度数据"""
        if self.tracker_file.exists():
            with open(self.tracker_file, 'r', encoding='utf-8') as f:
                self.progress = json.load(f)
        else:
            self.progress = {
                "last_updated": datetime.datetime.now().isoformat(),
                "total_tools": 0,
                "packaged_tools": 0,
                "failed_tools": 0,
                "tools": {},
                "categories": {},
                "stats": {
                    "total_size_mb": 0,
                    "avg_tool_size_mb": 0,
                    "success_rate": 0
                }
            }
    
    def save_progress(self):
        """保存进度数据"""
        self.progress["last_updated"] = datetime.datetime.now().isoformat()
        with open(self.tracker_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)
    
    def scan_tools(self):
        """扫描工作空间中的石器时代工具"""
        print("🔍 扫描石器时代工具...")
        
        # 定义工具模式
        tool_patterns = [
            "石器时代*.py",
            "NG25*.py", 
            "ASSA*.py",
            "*工具*.py",
            "*优化*.py",
            "*分析*.py"
        ]
        
        tools_found = []
        
        for pattern in tool_patterns:
            for filepath in glob.glob(str(self.workspace / pattern), recursive=True):
                filepath = Path(filepath)
                if filepath.is_file() and filepath.suffix == '.py':
                    # 排除一些非工具文件
                    if any(exclude in filepath.name for exclude in ["_test", "test_", "示例", "example"]):
                        continue
                    
                    tools_found.append(filepath)
        
        print(f"📊 找到 {len(tools_found)} 个工具文件")
        return tools_found
    
    def analyze_tool(self, tool_path):
        """分析单个工具"""
        tool_info = {
            "name": tool_path.name,
            "path": str(tool_path.relative_to(self.workspace)),
            "size_bytes": tool_path.stat().st_size,
            "size_mb": round(tool_path.stat().st_size / (1024*1024), 2),
            "modified": datetime.datetime.fromtimestamp(tool_path.stat().st_mtime).isoformat(),
            "category": self.detect_category(tool_path.name),
            "status": "未打包",  # 未打包, 打包中, 已打包, 失败
            "exe_path": None,
            "exe_size_mb": 0,
            "packaged_date": None,
            "notes": ""
        }
        
        # 检查是否有对应的EXE文件
        exe_patterns = [
            tool_path.with_suffix('.exe'),
            tool_path.parent / (tool_path.stem + '.exe'),
            self.workspace / "石器时代工具EXE优化_立即版" / (tool_path.stem + '.exe'),
            self.workspace / "石器时代工具_Win10专用版" / (tool_path.stem + '.exe')
        ]
        
        for exe_path in exe_patterns:
            if exe_path.exists():
                tool_info["status"] = "已打包"
                tool_info["exe_path"] = str(exe_path.relative_to(self.workspace))
                tool_info["exe_size_mb"] = round(exe_path.stat().st_size / (1024*1024), 2)
                tool_info["packaged_date"] = datetime.datetime.fromtimestamp(exe_path.stat().st_mtime).isoformat()
                break
        
        return tool_info
    
    def detect_category(self, filename):
        """检测工具类别"""
        filename_lower = filename.lower()
        
        categories = {
            "优化": ["优化", "enhance", "improve"],
            "分析": ["分析", "analyze", "analysis"],
            "网络": ["网络", "network", "net"],
            "调试": ["调试", "debug", "debugger"],
            "测试": ["测试", "test"],
            "打包": ["打包", "pack", "exe"],
            "监控": ["监控", "monitor", "watch"],
            "查询": ["查询", "search", "query"],
            "管理": ["管理", "manage", "admin"],
            "验证": ["验证", "verify", "validate"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in filename_lower for keyword in keywords):
                return category
        
        return "其他"
    
    def update_progress(self):
        """更新进度跟踪"""
        print("🔄 更新进度跟踪...")
        
        tools = self.scan_tools()
        self.progress["total_tools"] = len(tools)
        self.progress["packaged_tools"] = 0
        self.progress["failed_tools"] = 0
        self.progress["tools"] = {}
        self.progress["categories"] = {}
        
        total_size = 0
        
        for tool_path in tools:
            tool_info = self.analyze_tool(tool_path)
            tool_key = tool_info["name"]
            self.progress["tools"][tool_key] = tool_info
            
            # 更新类别统计
            category = tool_info["category"]
            if category not in self.progress["categories"]:
                self.progress["categories"][category] = {
                    "total": 0,
                    "packaged": 0,
                    "failed": 0
                }
            
            self.progress["categories"][category]["total"] += 1
            
            if tool_info["status"] == "已打包":
                self.progress["packaged_tools"] += 1
                self.progress["categories"][category]["packaged"] += 1
                total_size += tool_info["exe_size_mb"]
            elif tool_info["status"] == "失败":
                self.progress["failed_tools"] += 1
                self.progress["categories"][category]["failed"] += 1
        
        # 更新统计
        if self.progress["total_tools"] > 0:
            self.progress["stats"]["success_rate"] = round(
                (self.progress["packaged_tools"] / self.progress["total_tools"]) * 100, 1
            )
            self.progress["stats"]["total_size_mb"] = round(total_size, 2)
            self.progress["stats"]["avg_tool_size_mb"] = round(
                total_size / self.progress["packaged_tools"] if self.progress["packaged_tools"] > 0 else 0, 2
            )
        
        self.save_progress()
        print("✅ 进度跟踪已更新")
    
    def generate_report(self):
        """生成进度报告"""
        print("📋 生成进度报告...")
        
        report = f"""
# 石器时代工具打包进度报告
**生成时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**最后更新**: {self.progress.get('last_updated', '未知')}

## 📊 总体进度
- **总工具数**: {self.progress['total_tools']}
- **已打包**: {self.progress['packaged_tools']}
- **打包失败**: {self.progress['failed_tools']}
- **打包成功率**: {self.progress['stats']['success_rate']}%
- **总打包大小**: {self.progress['stats']['total_size_mb']} MB
- **平均工具大小**: {self.progress['stats']['avg_tool_size_mb']} MB

## 🗂️ 分类统计
"""
        
        for category, stats in self.progress.get("categories", {}).items():
            category_success_rate = round(
                (stats.get("packaged", 0) / stats.get("total", 1)) * 100, 1
            ) if stats.get("total", 0) > 0 else 0
            
            report += f"- **{category}**: {stats.get('total', 0)}个工具, {stats.get('packaged', 0)}个已打包 ({category_success_rate}%)\n"
        
        report += "\n## 🎯 下一步建议\n"
        
        # 根据进度给出建议
        success_rate = self.progress['stats']['success_rate']
        if success_rate < 30:
            report += "1. **优先打包核心工具**: 先打包最常用的工具\n"
            report += "2. **检查依赖问题**: 确保所有依赖都已安装\n"
            report += "3. **批量测试**: 使用批量打包脚本提高效率\n"
        elif success_rate < 70:
            report += "1. **优化打包配置**: 调整打包参数减少文件大小\n"
            report += "2. **分类打包**: 按类别分批打包便于管理\n"
            report += "3. **创建安装包**: 考虑创建完整的安装程序\n"
        else:
            report += "1. **创建分发包**: 将所有EXE打包成zip分发\n"
            report += "2. **编写使用文档**: 为每个工具创建说明文档\n"
            report += "3. **自动化部署**: 设置自动打包和发布流程\n"
        
        report += "\n## 📁 最近更新的工具\n"
        
        # 显示最近更新的工具
        tools_sorted = sorted(
            self.progress["tools"].values(),
            key=lambda x: x.get("packaged_date") or x.get("modified") or "",
            reverse=True
        )[:10]
        
        for tool in tools_sorted:
            status_emoji = "✅" if tool["status"] == "已打包" else "⏳" if tool["status"] == "打包中" else "❌"
            report += f"- {status_emoji} **{tool['name']}** ({tool['category']}) - {tool['status']}"
            if tool.get("exe_size_mb"):
                report += f" ({tool['exe_size_mb']} MB)"
            report += "\n"
        
        return report
    
    def check_problems(self):
        """检查潜在问题"""
        print("🔍 检查潜在问题...")
        
        problems = []
        
        # 检查大文件
        for tool_name, tool_info in self.progress["tools"].items():
            if tool_info.get("exe_size_mb", 0) > 50:  # 超过50MB
                problems.append(f"⚠️ 工具 '{tool_name}' 的EXE文件过大: {tool_info['exe_size_mb']} MB")
        
        # 检查长时间未更新的工具
        one_month_ago = datetime.datetime.now() - datetime.timedelta(days=30)
        for tool_name, tool_info in self.progress["tools"].items():
            if tool_info["status"] == "未打包":
                modified_date = datetime.datetime.fromisoformat(tool_info["modified"].replace('Z', '+00:00'))
                if modified_date < one_month_ago:
                    problems.append(f"📅 工具 '{tool_name}' 已超过30天未打包")
        
        # 检查重复工具
        tool_names = list(self.progress["tools"].keys())
        name_counts = {}
        for name in tool_names:
            base_name = name.split('_')[0].split('.')[0]
            name_counts[base_name] = name_counts.get(base_name, 0) + 1
        
        for base_name, count in name_counts.items():
            if count > 3:
                problems.append(f"🔁 发现多个 '{base_name}' 相关工具 ({count}个)，考虑合并或清理")
        
        return problems

def main():
    """主函数"""
    print("=" * 60)
    print("🛠️  石器时代工具打包进度跟踪系统")
    print("=" * 60)
    
    tracker = StoneAgeToolTracker()
    
    while True:
        print("\n请选择操作:")
        print("1. 扫描并更新进度")
        print("2. 查看进度报告")
        print("3. 检查潜在问题")
        print("4. 导出报告到文件")
        print("5. 退出")
        
        choice = input("\n请输入选项 (1-5): ").strip()
        
        if choice == "1":
            tracker.update_progress()
            print("✅ 进度已更新")
            
        elif choice == "2":
            report = tracker.generate_report()
            print(report)
            
        elif choice == "3":
            problems = tracker.check_problems()
            if problems:
                print("🚨 发现以下潜在问题:")
                for problem in problems:
                    print(f"  • {problem}")
            else:
                print("✅ 未发现明显问题")
                
        elif choice == "4":
            report = tracker.generate_report()
            report_file = tracker.workspace / "石器时代工具打包进度报告.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ 报告已保存到: {report_file}")
            
        elif choice == "5":
            print("👋 退出系统")
            break
            
        else:
            print("❌ 无效选项，请重新选择")

if __name__ == "__main__":
    main()