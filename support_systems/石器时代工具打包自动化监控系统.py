        elif stage == PackagingStage.DEPENDENCY_INSTALL:
            results = []
            for tool in self.project_status.tools:
                if tool.status == ToolStatus.COMPLETED:  # 只处理已收集源码的工具
                    tool.status = ToolStatus.IN_PROGRESS
                    tool.start_time = datetime.datetime.now()
                    success, message = self.install_dependencies(tool)
                    tool.end_time = datetime.datetime.now()
                    tool.status = ToolStatus.COMPLETED if success else ToolStatus.FAILED
                    if not success:
                        tool.error_message = message
                    results.append(f"{tool.name}: {'成功' if success else '失败'}")
                    self._save_status(self.project_status)
            
            return True, f"依赖安装完成: {', '.join(results)}"
        
        elif stage == PackagingStage.BUILD_PACKAGING:
            results = []
            for tool in self.project_status.tools:
                if tool.status == ToolStatus.COMPLETED:  # 只处理已安装依赖的工具
                    tool.status = ToolStatus.IN_PROGRESS
                    tool.start_time = datetime.datetime.now()
                    success, message = self.build_exe(tool)
                    tool.end_time = datetime.datetime.now()
                    tool.status = ToolStatus.COMPLETED if success else ToolStatus.FAILED
                    if not success:
                        tool.error_message = message
                    results.append(f"{tool.name}: {'成功' if success else '失败'}")
                    self._save_status(self.project_status)
            
            return True, f"构建打包完成: {', '.join(results)}"
        
        elif stage == PackagingStage.TESTING:
            results = []
            for tool in self.project_status.tools:
                if tool.status == ToolStatus.COMPLETED:  # 只处理已构建的工具
                    tool.status = ToolStatus.IN_PROGRESS
                    tool.start_time = datetime.datetime.now()
                    success, test_results = self.test_exe(tool)
                    tool.end_time = datetime.datetime.now()
                    tool.status = ToolStatus.COMPLETED if success else ToolStatus.FAILED
                    tool.test_results = test_results
                    if not success:
                        tool.error_message = "测试失败"
                    results.append(f"{tool.name}: {'成功' if success else '失败'}")
                    self._save_status(self.project_status)
            
            return True, f"测试验证完成: {', '.join(results)}"
        
        elif stage == PackagingStage.OPTIMIZATION:
            # 这里可以添加优化逻辑，如文件压缩、资源优化等
            logger.info("执行优化调整...")
            return True, "优化调整完成（模拟）"
        
        elif stage == PackagingStage.GITHUB_UPLOAD:
            if not self.project_status.auto_upload:
                return True, "自动上传已禁用，跳过此阶段"
            
            results = []
            for tool in self.project_status.tools:
                if tool.status == ToolStatus.COMPLETED:  # 只处理已测试的工具
                    tool.status = ToolStatus.IN_PROGRESS
                    tool.start_time = datetime.datetime.now()
                    success, message = self.upload_to_github(tool)
                    tool.end_time = datetime.datetime.now()
                    if success:
                        tool.status = ToolStatus.COMPLETED
                        tool.github_url = message.split(": ")[-1] if ": " in message else message
                    else:
                        tool.status = ToolStatus.FAILED
                        tool.error_message = message
                    results.append(f"{tool.name}: {'成功' if success else '失败'}")
                    self._save_status(self.project_status)
            
            return True, f"GitHub上传完成: {', '.join(results)}"
        
        elif stage == PackagingStage.FINAL_REPORT:
            # 生成最终报告
            qq_report = self.generate_qq_report()
            html_report = self.generate_html_report()
            
            # 保存报告
            report_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            html_path = os.path.join(self.report_dir, f"final_report_{report_time}.html")
            json_path = os.path.join(self.report_dir, f"final_report_{report_time}.json")
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_report)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.project_status.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"最终报告已保存: {html_path}, {json_path}")
            return True, f"最终报告生成完成，QQ汇报已准备"
        
        return False, f"未知阶段: {stage}"
    
    def run_full_pipeline(self) -> bool:
        """运行完整流水线"""
        logger.info("开始运行完整打包流水线")
        
        stages = [
            PackagingStage.ENVIRONMENT_CHECK,
            PackagingStage.SOURCE_COLLECTION,
            PackagingStage.DEPENDENCY_INSTALL,
            PackagingStage.BUILD_PACKAGING,
            PackagingStage.TESTING,
            PackagingStage.OPTIMIZATION,
            PackagingStage.GITHUB_UPLOAD,
            PackagingStage.FINAL_REPORT
        ]
        
        for stage in stages:
            logger.info(f"=== 开始阶段: {stage.value} ===")
            
            # 生成QQ汇报
            if self.project_status.qq_report_enabled:
                qq_report = self.generate_qq_report()
                logger.info(f"QQ汇报:\n{qq_report}")
            
            # 执行阶段
            success, message = self.run_stage(stage)
            
            if not success:
                logger.error(f"阶段 {stage.value} 失败: {message}")
                
                # 生成错误报告
                error_report = f"❌ **阶段失败报告**\n"
                error_report += f"阶段: {stage.value}\n"
                error_report += f"错误: {message}\n"
                error_report += f"时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                
                error_path = os.path.join(self.report_dir, f"error_{stage.name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
                with open(error_path, 'w', encoding='utf-8') as f:
                    f.write(error_report)
                
                logger.error(f"错误报告已保存: {error_path}")
                return False
            
            logger.info(f"阶段 {stage.value} 完成: {message}")
            
            # 保存状态
            self._save_status(self.project_status)
            
            # 短暂暂停
            time.sleep(2)
        
        logger.info("完整流水线执行完成")
        return True
    
    def monitor_loop(self, interval_seconds: int = 300) -> None:
        """监控循环（每5分钟检查一次）"""
        logger.info(f"启动监控循环，间隔: {interval_seconds}秒")
        
        try:
            while True:
                # 检查项目状态
                self.project_status.update_progress()
                
                # 生成QQ汇报
                if self.project_status.qq_report_enabled:
                    qq_report = self.generate_qq_report()
                    logger.info(f"定期QQ汇报:\n{qq_report}")
                
                # 检查是否超时
                remaining = self.project_status.get_remaining_time()
                if remaining is None:
                    logger.warning("项目已超过目标完成时间")
                    
                    # 生成超时报告
                    timeout_report = self.generate_qq_report()
                    timeout_report += "\n\n🚨 **项目超时警告**\n"
                    timeout_report += "项目已超过目标完成时间，建议检查进度并调整计划。"
                    
                    timeout_path = os.path.join(self.report_dir, f"timeout_warning_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
                    with open(timeout_path, 'w', encoding='utf-8') as f:
                        f.write(timeout_report)
                    
                    logger.warning(f"超时警告报告已保存: {timeout_path}")
                
                # 保存状态
                self._save_status(self.project_status)
                
                # 等待下一个检查周期
                logger.info(f"等待 {interval_seconds} 秒后再次检查...")
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            logger.info("监控循环被用户中断")
        except Exception as e:
            logger.error(f"监控循环异常: {e}")

# ============================================================================
# 命令行接口
# ============================================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='石器时代工具打包自动化监控系统')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--run', action='store_true', help='运行完整流水线')
    parser.add_argument('--monitor', action='store_true', help='启动监控循环')
    parser.add_argument('--report', action='store_true', help='生成报告')
    parser.add_argument('--qq-report', action='store_true', help='生成QQ汇报')
    parser.add_argument('--html-report', action='store_true', help='生成HTML报告')
    parser.add_argument('--status', action='store_true', help='显示当前状态')
    
    args = parser.parse_args()
    
    # 创建监控器
    monitor = StoneAgePackagingMonitor(args.config)
    
    if args.run:
        # 运行完整流水线
        success = monitor.run_full_pipeline()
        sys.exit(0 if success else 1)
    
    elif args.monitor:
        # 启动监控循环
        monitor.monitor_loop()
    
    elif args.report:
        # 生成所有报告
        qq_report = monitor.generate_qq_report()
        html_report = monitor.generate_html_report()
        
        print("=== QQ汇报 ===")
        print(qq_report)
        print("\n=== HTML报告 ===")
        print("HTML报告已生成，请查看文件")
        
        # 保存报告
        report_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        html_path = os.path.join(monitor.report_dir, f"report_{report_time}.html")
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print(f"HTML报告已保存: {html_path}")
    
    elif args.qq_report:
        # 生成QQ汇报
        report = monitor.generate_qq_report()
        print(report)
    
    elif args.html_report:
        # 生成HTML报告
        report = monitor.generate_html_report()
        
        report_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        html_path = os.path.join(monitor.report_dir, f"html_report_{report_time}.html")
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"HTML报告已保存: {html_path}")
    
    elif args.status:
        # 显示当前状态
        status = monitor.project_status
        status.update_progress()
        
        print("=== 项目状态 ===")
        print(f"项目名称: {status.project_name}")
        print(f"开始时间: {status.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"目标完成时间: {status.target_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"当前阶段: {status.current_stage.value}")
        print(f"进度: {status.get_progress_percentage():.1f}% ({status.completed_tools}/{status.total_tools})")
        
        remaining = status.get_remaining_time()
        if remaining:
            print(f"剩余时间: {str(remaining).split('.')[0]}")
        else:
            print("剩余时间: 已超时")
        
        print("\n=== 工具状态 ===")
        for tool in status.tools:
            print(f"{tool.name}: {tool.status.value}")
            if tool.error_message:
                print(f"  错误: {tool.error_message[:50]}...")
    
    else:
        # 显示帮助信息
        parser.print_help()
        
        print("\n使用示例:")
        print("  python3 石器时代工具打包自动化监控系统.py --run      # 运行完整流水线")
        print("  python3 石器时代工具打包自动化监控系统.py --monitor  # 启动监控循环")
        print("  python3 石器时代工具打包自动化监控系统.py --report   # 生成所有报告")
        print("  python3 石器时代工具打包自动化监控系统.py --status   # 显示当前状态")

if __name__ == "__main__":
    main()