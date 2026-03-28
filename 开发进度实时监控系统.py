#!/usr/bin/env python3
"""
开发进度实时监控系统
自动监控和报告石器时代工具链的开发进度
"""

import os
import sys
import time
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading
import subprocess

class DevelopmentProgressMonitor:
    """开发进度监控器"""
    
    def __init__(self, workspace_path: str = "/root/.openclaw/workspace"):
        self.workspace_path = Path(workspace_path)
        self.progress_data = {
            "start_time": datetime.datetime.now().isoformat(),
            "last_update": datetime.datetime.now().isoformat(),
            "projects": {},
            "metrics": {},
            "alerts": []
        }
        
        # 定义监控的项目
        self.projects_to_monitor = {
            "石器时代网络稳定性优化工具包": {
                "path": "石器时代网络稳定性优化工具包",
                "files": ["主程序.py", "网络波动检测器.py", "智能重试系统.py", "防卡机制.py", "性能监控仪表板.py"],
                "status": "unknown",
                "progress": 0
            },
            "石器时代脚本自动化部署系统": {
                "path": "石器时代脚本自动化部署系统",
                "files": ["主程序.py", "打包引擎.py", "配置引擎.py", "部署引擎.py"],
                "status": "unknown",
                "progress": 0
            },
            "EXE优化工具": {
                "path": "",
                "files": ["快速EXE优化.py", "EXE优化与上传计划.md"],
                "status": "unknown",
                "progress": 0
            },
            "实时演示系统": {
                "path": "实时演示与反馈系统",
                "files": ["交互式演示.py"],
                "status": "unknown",
                "progress": 0
            },
            "用户展示包": {
                "path": "用户醒来展示包",
                "files": ["完整成果总结报告.md", "快速开始指南.md"],
                "status": "unknown",
                "progress": 0
            }
        }
        
        # 启动监控线程
        self.is_monitoring = False
        self.monitoring_thread = None
    
    def check_project_status(self, project_name: str, project_info: Dict) -> Dict:
        """检查项目状态"""
        status_info = {
            "name": project_name,
            "exists": False,
            "files_exist": [],
            "files_missing": [],
            "file_count": 0,
            "total_files": len(project_info["files"]),
            "last_modified": None,
            "size_kb": 0
        }
        
        # 检查项目目录
        if project_info["path"]:
            project_path = self.workspace_path / project_info["path"]
            if project_path.exists():
                status_info["exists"] = True
                
                # 检查文件
                for filename in project_info["files"]:
                    file_path = project_path / filename
                    if file_path.exists():
                        status_info["files_exist"].append(filename)
                        
                        # 获取文件信息
                        stat = file_path.stat()
                        if not status_info["last_modified"] or stat.st_mtime > status_info["last_modified"]:
                            status_info["last_modified"] = stat.st_mtime
                        status_info["size_kb"] += stat.st_size / 1024
                    else:
                        status_info["files_missing"].append(filename)
                
                status_info["file_count"] = len(status_info["files_exist"])
                
                # 计算进度
                if status_info["total_files"] > 0:
                    status_info["progress"] = (status_info["file_count"] / status_info["total_files"]) * 100
                
                # 确定状态
                if status_info["progress"] >= 90:
                    status_info["status"] = "completed"
                elif status_info["progress"] >= 50:
                    status_info["status"] = "in_progress"
                elif status_info["progress"] > 0:
                    status_info["status"] = "started"
                else:
                    status_info["status"] = "not_started"
            else:
                status_info["status"] = "directory_missing"
        else:
            # 检查分散的文件
            files_exist = []
            for filename in project_info["files"]:
                file_path = self.workspace_path / filename
                if file_path.exists():
                    files_exist.append(filename)
            
            status_info["files_exist"] = files_exist
            status_info["file_count"] = len(files_exist)
            
            if status_info["file_count"] > 0:
                status_info["exists"] = True
                if status_info["file_count"] == status_info["total_files"]:
                    status_info["status"] = "completed"
                    status_info["progress"] = 100
                else:
                    status_info["status"] = "partial"
                    status_info["progress"] = (status_info["file_count"] / status_info["total_files"]) * 100
            else:
                status_info["status"] = "not_started"
                status_info["progress"] = 0
        
        return status_info
    
    def check_exe_optimization_status(self) -> Dict:
        """检查EXE优化状态"""
        exe_status = {
            "name": "EXE优化进度",
            "status": "unknown",
            "optimized_tools": 0,
            "total_tools": 109,
            "output_directory_exists": False,
            "exe_files": [],
            "progress": 0
        }
        
        # 检查输出目录
        output_dir = self.workspace_path / "石器时代工具EXE优化"
        if output_dir.exists():
            exe_status["output_directory_exists"] = True
            
            # 查找EXE文件
            exe_files = list(output_dir.rglob("*.exe"))
            exe_status["exe_files"] = [str(f.relative_to(output_dir)) for f in exe_files]
            exe_status["optimized_tools"] = len(exe_files)
            
            if exe_status["total_tools"] > 0:
                exe_status["progress"] = (exe_status["optimized_tools"] / exe_status["total_tools"]) * 100
            
            if exe_status["progress"] >= 90:
                exe_status["status"] = "nearly_complete"
            elif exe_status["progress"] >= 50:
                exe_status["status"] = "in_progress"
            elif exe_status["progress"] > 0:
                exe_status["status"] = "started"
            else:
                exe_status["status"] = "directory_empty"
        else:
            exe_status["status"] = "not_started"
        
        return exe_status
    
    def check_gateway_status(self) -> Dict:
        """检查Gateway服务状态"""
        gateway_status = {
            "name": "OpenClaw Gateway",
            "status": "unknown",
            "is_running": False,
            "last_check": datetime.datetime.now().isoformat()
        }
        
        try:
            # 尝试检查服务状态
            result = subprocess.run(
                ["systemctl", "is-active", "openclaw-gateway"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                gateway_status["is_running"] = True
                gateway_status["status"] = "active"
            else:
                gateway_status["status"] = "inactive"
                
        except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError) as e:
            gateway_status["status"] = "check_failed"
            gateway_status["error"] = str(e)
        
        return gateway_status
    
    def calculate_overall_metrics(self) -> Dict:
        """计算整体指标"""
        total_projects = len(self.projects_to_monitor)
        completed_projects = 0
        total_progress = 0
        
        for project_name in self.projects_to_monitor:
            if project_name in self.progress_data["projects"]:
                project_data = self.progress_data["projects"][project_name]
                total_progress += project_data.get("progress", 0)
                
                if project_data.get("status") == "completed":
                    completed_projects += 1
        
        # 添加EXE优化状态
        if "EXE优化进度" in self.progress_data["projects"]:
            exe_data = self.progress_data["projects"]["EXE优化进度"]
            total_progress += exe_data.get("progress", 0)
            if exe_data.get("status") in ["completed", "nearly_complete"]:
                completed_projects += 1
        
        avg_progress = total_progress / (total_projects + 1)  # +1 for EXE优化
        
        metrics = {
            "total_projects": total_projects + 1,  # 包括EXE优化
            "completed_projects": completed_projects,
            "in_progress_projects": (total_projects + 1) - completed_projects,
            "average_progress": round(avg_progress, 1),
            "overall_status": "excellent" if avg_progress >= 80 else "good" if avg_progress >= 50 else "needs_attention"
        }
        
        return metrics
    
    def generate_alerts(self):
        """生成警报"""
        alerts = []
        
        # 检查Gateway状态
        if "OpenClaw Gateway" in self.progress_data["projects"]:
            gateway = self.progress_data["projects"]["OpenClaw Gateway"]
            if not gateway.get("is_running", False):
                alerts.append({
                    "level": "warning",
                    "message": "Gateway服务未运行，可能影响通信",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "action": "启动Gateway服务"
                })
        
        # 检查进度低的项目
        for project_name, project_data in self.progress_data["projects"].items():
            if project_name not in ["OpenClaw Gateway", "EXE优化进度"]:
                progress = project_data.get("progress", 0)
                if progress < 30:
                    alerts.append({
                        "level": "info",
                        "message": f"项目 '{project_name}' 进度较低 ({progress}%)",
                        "timestamp": datetime.datetime.now().isoformat(),
                        "action": f"检查并推进 {project_name} 项目"
                    })
        
        # 检查EXE优化
        if "EXE优化进度" in self.progress_data["projects"]:
            exe_data = self.progress_data["projects"]["EXE优化进度"]
            if exe_data.get("status") == "not_started":
                alerts.append({
                    "level": "warning",
                    "message": "EXE优化尚未开始",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "action": "启动EXE优化工具"
                })
        
        self.progress_data["alerts"] = alerts
    
    def update_progress(self):
        """更新进度数据"""
        self.progress_data["last_update"] = datetime.datetime.now().isoformat()
        
        # 检查所有项目
        for project_name, project_info in self.projects_to_monitor.items():
            status_info = self.check_project_status(project_name, project_info)
            self.progress_data["projects"][project_name] = status_info
        
        # 检查EXE优化状态
        exe_status = self.check_exe_optimization_status()
        self.progress_data["projects"]["EXE优化进度"] = exe_status
        
        # 检查Gateway状态
        gateway_status = self.check_gateway_status()
        self.progress_data["projects"]["OpenClaw Gateway"] = gateway_status
        
        # 计算整体指标
        self.progress_data["metrics"] = self.calculate_overall_metrics()
        
        # 生成警报
        self.generate_alerts()
    
    def generate_report(self) -> str:
        """生成进度报告"""
        report_lines = []
        
        # 标题
        report_lines.append("=" * 60)
        report_lines.append("🚀 石器时代工具链开发进度实时报告")
        report_lines.append("=" * 60)
        report_lines.append(f"报告时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"监控开始: {self.progress_data['start_time']}")
        report_lines.append(f"最后更新: {self.progress_data['last_update']}")
        report_lines.append("")
        
        # 整体指标
        metrics = self.progress_data["metrics"]
        report_lines.append("📊 整体开发指标")
        report_lines.append("-" * 40)
        report_lines.append(f"项目总数: {metrics.get('total_projects', 0)}")
        report_lines.append(f"已完成项目: {metrics.get('completed_projects', 0)}")
        report_lines.append(f"进行中项目: {metrics.get('in_progress_projects', 0)}")
        report_lines.append(f"平均进度: {metrics.get('average_progress', 0)}%")
        report_lines.append(f"整体状态: {metrics.get('overall_status', 'unknown')}")
        report_lines.append("")
        
        # 项目详情
        report_lines.append("📋 项目详情")
        report_lines.append("-" * 40)
        
        for project_name, project_data in self.progress_data["projects"].items():
            status_emoji = {
                "completed": "✅",
                "nearly_complete": "🟢",
                "in_progress": "🟡",
                "started": "🔵",
                "partial": "🟠",
                "not_started": "⚪",
                "directory_missing": "❌",
                "directory_empty": "📁",
                "active": "✅",
                "inactive": "🔴",
                "check_failed": "⚠️",
                "unknown": "❓"
            }.get(project_data.get("status", "unknown"), "❓")
            
            progress_bar = self._create_progress_bar(project_data.get("progress", 0))
            
            report_lines.append(f"{status_emoji} {project_name}")
            report_lines.append(f"   状态: {project_data.get('status', 'unknown')}")
            report_lines.append(f"   进度: {progress_bar} {project_data.get('progress', 0):.1f}%")
            
            if "file_count" in project_data:
                report_lines.append(f"   文件: {project_data.get('file_count', 0)}/{project_data.get('total_files', 0)}")
            
            if "optimized_tools" in project_data:
                report_lines.append(f"   EXE工具: {project_data.get('optimized_tools', 0)}/{project_data.get('total_tools', 0)}")
            
            if "is_running" in project_data:
                report_lines.append(f"   运行状态: {'运行中' if project_data.get('is_running') else '未运行'}")
            
            report_lines.append("")
        
        # 警报
        alerts = self.progress_data.get("alerts", [])
        if alerts:
            report_lines.append("🚨 警报与建议")
            report_lines.append("-" * 40)
            
            for alert in alerts:
                level_emoji = {
                    "warning": "⚠️",
                    "info": "ℹ️",
                    "error": "❌"
                }.get(alert.get("level", "info"), "ℹ️")
                
                report_lines.append(f"{level_emoji} {alert.get('message', '')}")
                if "action" in alert:
                    report_lines.append(f"   建议: {alert.get('action')}")
                report_lines.append("")
        
        # 下一步建议
        report_lines.append("🎯 下一步建议")
        report_lines.append("-" * 40)
        
        # 基于状态生成建议
        suggestions = []
        
        # Gateway建议
        if "OpenClaw Gateway" in self.progress_data["projects"]:
            gateway = self.progress_data["projects"]["OpenClaw Gateway"]
            if not gateway.get("is_running", False):
                suggestions.append("1. 启动OpenClaw Gateway服务以恢复通信")
        
        # EXE优化建议
        if "EXE优化进度" in self.progress_data["projects"]:
            exe_data = self.progress_data["projects"]["EXE优化进度"]
            if exe_data.get("status") in ["not_started", "directory_empty"]:
                suggestions.append("2. 运行快速EXE优化.py开始工具EXE优化")
            elif exe_data.get("progress", 0) < 50:
                suggestions.append("2. 继续EXE优化工作，当前进度较低")
        
        # 工具链测试建议
        completed_count = sum(1 for p in self.progress_data["projects"].values() 
                            if p.get("status") in ["completed", "nearly_complete"])
        if completed_count >= 3:
            suggestions.append("3. 开始工具链集成测试和功能验证")
        
        if not suggestions:
            suggestions.append("1. 继续当前开发工作，保持良好进度")
            suggestions.append("2. 考虑添加新功能或优化现有工具")
            suggestions.append("3. 准备GitHub上传和文档完善")
        
        for i, suggestion in enumerate(suggestions, 1):
            report_lines.append(f"{i}. {suggestion}")
        
        report_lines.append("")
        report_lines.append("=" * 60)
        report_lines.append("📝 报告结束 - 下次更新: 5分钟后")
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def _create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """创建进度条"""
        filled = int(width * percentage / 100)
        empty = width - filled
        return "[" + "█" * filled + "░" * empty + "]"
    
    def _monitoring_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                self.update_progress()
                
                # 生成并显示报告
                report = self.generate_report()
                print("\n" * 2)
                print(report)
                
                # 保存报告到文件
                report_file = self.workspace_path / "开发进度报告.md"
                with open(report_file, "w", encoding="utf-8") as f:
                    f.write(report)
                
                # 保存JSON数据
                json_file = self.workspace_path / "开发进度数据.json"
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(self.progress_data, f, indent=2, ensure_ascii=False)
                
                # 等待5分钟
                for _ in range(300):  # 5分钟 = 300秒
                    if not self.is_monitoring:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"监控循环异常: {e}")
                time.sleep(30)  # 异常后等待30秒
    
    def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            print("监控已经在运行")
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        print("开发进度监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        if not self.is_monitoring:
            print("监控未在运行")
            return
        
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        print("开发进度监控已停止")
    
    def get_current_report(self) -> str:
        """获取当前报告"""
        self.update_progress()
        return self.generate_report()
    
    def run_once(self):
        """运行一次并退出"""
        self.update_progress()
        report = self.generate_report()
        print(report)
        
        # 保存文件
        report_file = self.workspace_path / "开发进度报告.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        json_file = self.workspace_path / "开发进度数据.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(self.progress_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n报告已保存到: {report_file}")
        print(f"数据已保存到: {json_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="开发进度实时监控系统")
    parser.add_argument("--once", action="store_true", help="运行一次并退出")
    parser.add_argument("--start", action="store_true", help="启动持续监控")
    parser.add_argument("--stop", action="store_true", help="停止监控")
    parser.add_argument("--report", action="store_true", help="生成当前报告")
    
    args = parser.parse_args()
    
    monitor = DevelopmentProgressMonitor()
    
    if args.once:
        monitor.run_once()
    elif args.start:
        monitor.start_monitoring()
        try:
            # 保持主线程运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop_monitoring()
    elif args.stop:
        monitor.stop_monitoring()
    elif args.report:
        report = monitor.get_current_report()
        print(report)
    else:
        # 默认运行一次
        monitor.run_once()


if __name__ == "__main__":
    main()