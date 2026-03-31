        if resource.memory_percent > 70:
            advice_list.append({
                "type": "性能优化",
                "title": "内存使用率较高",
                "description": f"内存使用率{resource.memory_percent:.1f}%，可能影响系统稳定性",
                "action": "清理内存缓存，关闭不必要的应用程序"
            })
        
        if resource.disk_usage_percent > 80:
            advice_list.append({
                "type": "存储优化",
                "title": "磁盘空间紧张",
                "description": f"磁盘使用率{resource.disk_usage_percent:.1f}%，可能影响文件操作",
                "action": "清理临时文件，删除不必要的文件"
            })
        
        # 基于项目状态提供建议
        project_files = [
            f for f in os.listdir("/root/.openclaw/workspace")
            if f.startswith("石器时代") and f.endswith(".py")
        ]
        
        if len(project_files) < 3:
            advice_list.append({
                "type": "项目准备",
                "title": "项目文件可能不完整",
                "description": f"发现{len(project_files)}个石器时代项目文件",
                "action": "检查是否所有必要的系统文件都已创建"
            })
        
        return advice_list
    
    # ============================================================================
    # 报告生成
    # ============================================================================
    
    def generate_support_report(self) -> Dict[str, Any]:
        """生成支持报告"""
        # 诊断问题
        issues = self.diagnose_problems()
        
        # 获取优化建议
        advice_list = self.provide_optimization_advice()
        
        # 获取资源状态
        resource = self.monitor_system_resources()
        
        # 计算统计数据
        critical_issues = sum(1 for i in issues if i.severity == ProblemSeverity.CRITICAL)
        high_issues = sum(1 for i in issues if i.severity == ProblemSeverity.HIGH)
        medium_issues = sum(1 for i in issues if i.severity == ProblemSeverity.MEDIUM)
        low_issues = sum(1 for i in issues if i.severity == ProblemSeverity.LOW)
        
        resolved_issues = sum(1 for i in self.issues if i.status == "已解决")
        total_issues = len(self.issues)
        
        # 生成报告
        report = {
            "report_time": datetime.datetime.now().isoformat(),
            "system_status": {
                "cpu_percent": resource.cpu_percent,
                "memory_percent": resource.memory_percent,
                "disk_usage_percent": resource.disk_usage_percent,
                "process_count": resource.process_count
            },
            "issue_summary": {
                "total_issues": total_issues,
                "resolved_issues": resolved_issues,
                "critical_issues": critical_issues,
                "high_issues": high_issues,
                "medium_issues": medium_issues,
                "low_issues": low_issues
            },
            "current_issues": [issue.to_dict() for issue in issues[:10]],  # 只显示最近10个问题
            "optimization_advice": advice_list,
            "project_time": {
                "current_time": datetime.datetime.now().isoformat(),
                "target_completion": "2026-03-31T22:30:00",
                "hours_remaining": (datetime.datetime(2026, 3, 31, 22, 30, 0) - datetime.datetime.now()).total_seconds() / 3600
            }
        }
        
        # 保存报告文件
        report_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.support_dir, f"support_report_{report_time}.json")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"生成支持报告: {report_path}")
        return report
    
    def generate_human_readable_report(self) -> str:
        """生成人类可读的报告"""
        report = self.generate_support_report()
        
        report_text = f"""
        📊 **石器时代工具打包项目 - 实时支持报告**
        
        ⏰ 报告时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        🖥️ **系统状态**
        • CPU使用率: {report['system_status']['cpu_percent']:.1f}%
        • 内存使用率: {report['system_status']['memory_percent']:.1f}%
        • 磁盘使用率: {report['system_status']['disk_usage_percent']:.1f}%
        • 进程数量: {report['system_status']['process_count']}
        
        ⚠️ **问题摘要**
        • 总计问题: {report['issue_summary']['total_issues']}
        • 已解决问题: {report['issue_summary']['resolved_issues']}
        • 严重问题: {report['issue_summary']['critical_issues']}
        • 高优先级问题: {report['issue_summary']['high_issues']}
        • 中优先级问题: {report['issue_summary']['medium_issues']}
        • 低优先级问题: {report['issue_summary']['low_issues']}
        
        ⏳ **项目时间**
        • 当前时间: {datetime.datetime.now().strftime('%H:%M:%S')}
        • 目标完成: 22:30:00
        • 剩余时间: {report['project_time']['hours_remaining']:.1f}小时
        
        """
        
        # 添加当前问题
        if report['current_issues']:
            report_text += "🔍 **当前问题**\n"
            for issue in report['current_issues'][:5]:  # 只显示前5个问题
                severity_icon = {
                    "严重": "🔴",
                    "高": "🟠",
                    "中": "🟡",
                    "低": "🟢",
                    "信息": "🔵"
                }.get(issue['severity'], "⚪")
                
                report_text += f"{severity_icon} {issue['title']}\n"
                report_text += f"   类型: {issue['type']}\n"
                report_text += f"   描述: {issue['description']}\n"
                if issue['solution']:
                    report_text += f"   解决方案: {issue['solution']}\n"
                report_text += "\n"
        
        # 添加优化建议
        if report['optimization_advice']:
            report_text += "💡 **优化建议**\n"
            for advice in report['optimization_advice'][:3]:  # 只显示前3个建议
                report_text += f"• {advice['title']}: {advice['description']}\n"
                report_text += f"  建议操作: {advice['action']}\n\n"
        
        # 添加系统就绪状态
        critical_files = [
            "/root/.openclaw/workspace/石器时代工具打包自动化监控系统.py",
            "/root/.openclaw/workspace/石器时代工具打包项目启动助手.py",
            "/root/.openclaw/workspace/石器时代工具打包项目演示验证系统.py"
        ]
        
        missing_files = [f for f in critical_files if not os.path.exists(f)]
        
        if not missing_files:
            report_text += "✅ **系统就绪状态: 完全就绪**\n"
        elif len(missing_files) == 1:
            report_text += "⚠️ **系统就绪状态: 基本就绪**\n"
            report_text += f"   缺失文件: {os.path.basename(missing_files[0])}\n"
        else:
            report_text += "❌ **系统就绪状态: 需要修复**\n"
            report_text += f"   缺失文件: {len(missing_files)}个\n"
        
        report_text += f"""
        🚀 **快速开始命令**
        1. 演示验证: python3 石器时代工具打包项目演示验证系统.py --demo
        2. 环境检查: python3 石器时代工具打包项目启动助手.py --check
        3. 项目配置: python3 石器时代工具打包项目启动助手.py --configure
        4. 开始监控: python3 石器时代工具打包自动化监控系统.py --run
        
        📞 **支持信息**
        • 支持系统: 石器时代工具打包项目实时支持系统
        • 日志文件: /tmp/stoneage_realtime_support.log
        • 报告目录: {self.support_dir}
        
        **实时支持系统已启动，将持续监控项目状态并提供支持。** 🛡️
        """
        
        return report_text.strip()
    
    # ============================================================================
    # 实时监控循环
    # ============================================================================
    
    def start_realtime_monitoring(self, interval_seconds: int = 300):
        """启动实时监控循环"""
        logger.info(f"启动实时监控，检查间隔: {interval_seconds}秒")
        
        try:
            while True:
                # 生成报告
                report = self.generate_human_readable_report()
                print("\n" + "="*60)
                print(report)
                print("="*60 + "\n")
                
                # 等待下一次检查
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            logger.info("实时监控已停止")
        except Exception as e:
            logger.error(f"实时监控失败: {e}")
    
    # ============================================================================
    # 命令行接口
    # ============================================================================
    
    def run_cli(self):
        """运行命令行接口"""
        import argparse
        
        parser = argparse.ArgumentParser(description='石器时代工具打包项目实时支持系统')
        parser.add_argument('--monitor', action='store_true', help='启动实时监控')
        parser.add_argument('--report', action='store_true', help='生成支持报告')
        parser.add_argument('--diagnose', action='store_true', help='诊断问题')
        parser.add_argument('--advice', action='store_true', help='获取优化建议')
        parser.add_argument('--interval', type=int, default=300, help='监控间隔秒数（默认300秒）')
        
        if len(sys.argv) == 1:
            parser.print_help()
            return
        
        args = parser.parse_args()
        
        if args.monitor:
            self.start_realtime_monitoring(args.interval)
        
        elif args.report:
            report = self.generate_human_readable_report()
            print(report)
        
        elif args.diagnose:
            issues = self.diagnose_problems()
            if issues:
                print("🔍 **诊断发现问题:**")
                for issue in issues:
                    print(f"• {issue.title} ({issue.severity.value}): {issue.description}")
                    if issue.solution:
                        print(f"  解决方案: {issue.solution}")
                    print()
            else:
                print("✅ 未发现问题")
        
        elif args.advice:
            advice_list = self.provide_optimization_advice()
            if advice_list:
                print("💡 **优化建议:**")
                for advice in advice_list:
                    print(f"• {advice['title']}: {advice['description']}")
                    print(f"  建议操作: {advice['action']}")
                    print()
            else:
                print("✅ 当前无需优化")
        
        else:
            parser.print_help()

# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    support = StoneAgeRealtimeSupport()
    
    # 如果直接运行，显示欢迎信息
    if len(sys.argv) == 1:
        print("=== 石器时代工具打包项目实时支持系统 ===")
        print("")
        print("💡 使用 --help 查看所有命令")
        print("💡 使用 --monitor 启动实时监控")
        print("💡 使用 --report 生成支持报告")
        print("💡 使用 --diagnose 诊断问题")
        print("💡 使用 --advice 获取优化建议")
    else:
        support.run_cli()

if __name__ == "__main__":
    main()