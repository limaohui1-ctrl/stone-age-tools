            git_user or '未设置'}
            Git邮箱: {git_email or '未设置'}
            GitHub仓库: {self.config.github_repo}
            
            📝 **GitHub配置说明**
            1. 确保已登录GitHub账号
            2. 创建仓库: {self.config.github_repo}
            3. 配置Git用户信息（如未设置）
            4. 获取GitHub访问令牌（如需自动上传）
            
            💡 **快速设置命令**
            ```bash
            # 设置Git用户
            git config --global user.name "您的姓名"
            git config --global user.email "您的邮箱"
            
            # 创建GitHub仓库（需要手动在GitHub网站创建）
            # 然后添加远程仓库
            git remote add origin https://github.com/您的用户名/{self.config.github_repo}.git
            ```
            
            ⚠️ **注意**
            自动上传功能需要GitHub访问令牌，请在GitHub设置中生成。
            """
            
            return True, result_text.strip()
            
        except Exception as e:
            return False, f"GitHub配置检查失败: {str(e)}"
    
    # ============================================================================
    # QQ汇报设置
    # ============================================================================
    
    def setup_qq_report(self) -> Tuple[bool, str]:
        """设置QQ汇报"""
        self.current_stage = StartupStage.QQ_REPORT_SETUP
        
        if not self.config.qq_report_enabled:
            return True, "QQ汇报已禁用，跳过设置"
        
        try:
            # 检查QQ机器人配置
            qq_config_path = "/root/.openclaw/extensions/openclaw-qqbot/config.json"
            qq_configured = os.path.exists(qq_config_path)
            
            result_text = f"""
            💬 **QQ汇报设置**
            
            QQ汇报状态: {'已启用' if self.config.qq_report_enabled else '已禁用'}
            QQ机器人配置: {'已配置' if qq_configured else '未配置'}
            
            📋 **QQ汇报功能**
            1. 实时项目进度汇报
            2. 错误和警告通知
            3. 阶段完成提醒
            4. 最终报告发送
            
            ⚙️ **配置要求**
            1. QQ机器人已正确配置
            2. 与用户的QQ连接正常
            3. 消息发送权限已授权
            
            💡 **测试QQ汇报**
            启动监控系统后，会自动生成QQ汇报消息。
            请确保QQ机器人能正常接收和发送消息。
            """
            
            return True, result_text.strip()
            
        except Exception as e:
            return False, f"QQ汇报设置检查失败: {str(e)}"
    
    # ============================================================================
    # 测试运行
    # ============================================================================
    
    def test_run(self) -> Tuple[bool, str]:
        """测试运行"""
        self.current_stage = StartupStage.TEST_RUN
        
        if not os.path.exists(self.monitor_path):
            return False, f"监控系统文件不存在: {self.monitor_path}"
        
        try:
            # 测试监控系统基本功能
            test_commands = [
                ["python3", self.monitor_path, "--status"],
                ["python3", self.monitor_path, "--qq-report"]
            ]
            
            results = []
            for cmd in test_commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        results.append(f"✅ {cmd[-1]}: 成功")
                    else:
                        results.append(f"❌ {cmd[-1]}: 失败 - {result.stderr[:100]}")
                        
                except subprocess.TimeoutExpired:
                    results.append(f"❌ {cmd[-1]}: 超时")
                except Exception as e:
                    results.append(f"❌ {cmd[-1]}: 异常 - {str(e)}")
            
            # 生成测试报告
            success_count = sum(1 for r in results if r.startswith("✅"))
            total_count = len(results)
            
            result_text = f"""
            🧪 **测试运行完成**
            
            测试项目: {total_count} 项
            成功: {success_count} 项
            失败: {total_count - success_count} 项
            
            📊 **测试结果**
            {chr(10).join(results)}
            
            """
            
            if success_count == total_count:
                result_text += "✅ **所有测试通过，系统就绪！**"
            elif success_count >= total_count * 0.5:
                result_text += "⚠️ **部分测试通过，系统基本可用**"
            else:
                result_text += "❌ **测试失败较多，建议检查系统配置**"
            
            return success_count == total_count, result_text.strip()
            
        except Exception as e:
            return False, f"测试运行失败: {str(e)}"
    
    # ============================================================================
    # 完整启动
    # ============================================================================
    
    def full_start(self) -> Tuple[bool, str]:
        """完整启动"""
        self.current_stage = StartupStage.FULL_START
        
        try:
            # 检查所有前置条件
            checks = []
            
            # 1. 检查监控系统文件
            if os.path.exists(self.monitor_path):
                checks.append("✅ 监控系统文件存在")
            else:
                checks.append("❌ 监控系统文件不存在")
            
            # 2. 检查配置文件
            config_path = "/root/.openclaw/workspace/stoneage_packaging_config.json"
            if os.path.exists(config_path):
                checks.append("✅ 监控配置文件存在")
            else:
                checks.append("❌ 监控配置文件不存在")
            
            # 3. 检查Python环境
            python_check = subprocess.run(
                ['python3', '--version'],
                capture_output=True,
                text=True
            )
            if python_check.returncode == 0:
                checks.append(f"✅ Python环境: {python_check.stdout.strip()}")
            else:
                checks.append("❌ Python环境检查失败")
            
            # 4. 检查PyInstaller
            pyinstaller_check = subprocess.run(
                ['pyinstaller', '--version'],
                capture_output=True,
                text=True
            )
            if pyinstaller_check.returncode == 0:
                checks.append("✅ PyInstaller已安装")
            else:
                checks.append("❌ PyInstaller未安装")
            
            # 生成启动命令
            start_commands = [
                f"# 启动监控系统（完整流水线）",
                f"python3 {self.monitor_path} --run",
                "",
                f"# 启动监控循环（后台运行）",
                f"nohup python3 {self.monitor_path} --monitor > monitor.log 2>&1 &",
                "",
                f"# 生成项目报告",
                f"python3 {self.monitor_path} --report",
                "",
                f"# 查看当前状态",
                f"python3 {self.monitor_path} --status"
            ]
            
            # 生成启动报告
            all_passed = all(c.startswith("✅") for c in checks)
            
            result_text = f"""
            🚀 **完整启动准备完成**
            
            📋 **启动前检查**
            {chr(10).join(checks)}
            
            💻 **启动命令**
            ```bash
            {chr(10).join(start_commands)}
            ```
            
            📚 **相关文件**
            • 监控系统: {self.monitor_path}
            • 使用指南: {self.guide_path}
            • 项目配置: {self.config_path}
            • 监控配置: /root/.openclaw/workspace/stoneage_packaging_config.json
            
            🎯 **项目目标**
            在 {self.config.target_completion_time.strftime('%Y-%m-%d %H:%M:%S') if self.config.target_completion_time else '今天22:30'} 前完成所有工具打包工作。
            
            """
            
            if all_passed:
                result_text += "✅ **所有检查通过，可以开始项目执行！**"
            else:
                result_text += "⚠️ **部分检查未通过，建议先解决问题再开始**"
            
            return all_passed, result_text.strip()
            
        except Exception as e:
            return False, f"完整启动准备失败: {str(e)}"
    
    # ============================================================================
    # 故障排除
    # ============================================================================
    
    def troubleshoot(self, issue: Optional[str] = None) -> str:
        """故障排除"""
        self.current_stage = StartupStage.TROUBLESHOOTING
        
        common_issues = {
            "环境检查失败": [
                "1. 检查Python是否安装: `python3 --version`",
                "2. 安装PyInstaller: `pip3 install pyinstaller`",
                "3. 安装Git: `apt-get install git`",
                "4. 检查磁盘空间: `df -h /`"
            ],
            "监控系统无法启动": [
                "1. 检查文件权限: `chmod +x 石器时代工具打包自动化监控系统.py`",
                "2. 检查Python依赖: `pip3 install -r requirements.txt`",
                "3. 查看错误日志: `tail -f /tmp/stoneage_packaging_monitor.log`",
                "4. 运行测试: `python3 石器时代工具打包自动化监控系统.py --status`"
            ],
            "GitHub上传失败": [
                "1. 检查Git配置: `git config --list`",
                "2. 验证GitHub仓库权限",
                "3. 检查网络连接",
                "4. 使用SSH密钥替代HTTPS"
            ],
            "QQ汇报不工作": [
                "1. 检查QQ机器人配置",
                "2. 验证QQ连接状态",
                "3. 检查消息发送权限",
                "4. 查看QQ机器人日志"
            ],
            "打包过程卡住": [
                "1. 检查磁盘空间是否充足",
                "2. 查看进程状态: `ps aux | grep pyinstaller`",
                "3. 增加超时时间",
                "4. 分阶段执行打包"
            ]
        }
        
        if issue and issue in common_issues:
            solutions = common_issues[issue]
            result_text = f"""
            🔧 **故障排除: {issue}**
            
            💡 **解决方案**
            {chr(10).join(solutions)}
            
            📞 **进一步帮助**
            如果问题仍未解决，请提供:
            1. 错误日志内容
            2. 执行的具体命令
            3. 系统环境信息
            4. 已尝试的解决方法
            """
        else:
            # 显示所有常见问题
            result_text = """
            🔧 **常见故障排除**
            
            请选择您遇到的问题:
            """
            
            for i, (issue_name, _) in enumerate(common_issues.items(), 1):
                result_text += f"\n{i}. {issue_name}"
            
            result_text += """
            
            💡 **通用故障排除步骤**
            1. 查看日志文件: `/tmp/stoneage_packaging_monitor.log`
            2. 检查系统资源: `free -h && df -h`
            3. 验证环境配置: `python3 --version && git --version`
            4. 运行简单测试: `python3 石器时代工具打包自动化监控系统.py --status`
            
            📞 **获取帮助**
            提供详细错误信息以获得更准确的帮助。
            """
        
        return result_text.strip()
    
    # ============================================================================
    # 快速启动向导
    # ============================================================================
    
    def quick_start_wizard(self) -> str:
        """快速启动向导"""
        result_text = """
        🚀 **石器时代工具打包项目 - 快速启动向导**
        
        本向导将引导您快速启动项目。请按步骤执行:
        
        **步骤1: 环境检查**
        ```
        python3 石器时代工具打包项目启动助手.py --check
        ```
        
        **步骤2: 项目配置**
        ```
        python3 石器时代工具打包项目启动助手.py --configure
        ```
        
        **步骤3: 启动监控系统**
        ```
        # 完整流水线
        python3 石器时代工具打包自动化监控系统.py --run
        
        # 或后台监控
        nohup python3 石器时代工具打包自动化监控系统.py --monitor > monitor.log 2>&1 &
        ```
        
        **步骤4: 查看进度**
        ```
        # 查看状态
        python3 石器时代工具打包自动化监控系统.py --status
        
        # 生成报告
        python3 石器时代工具打包自动化监控系统.py --report
        ```
        
        **步骤5: 故障排除（如需要）**
        ```
        python3 石器时代工具打包项目启动助手.py --troubleshoot
        ```
        
        📚 **详细指南**
        完整的使用指南: 石器时代工具打包自动化监控系统_使用指南.md
        
        🆘 **获取帮助**
        遇到问题时，请提供错误信息和已尝试的步骤。
        """
        
        return result_text.strip()
    
    # ============================================================================
    # 命令行接口
    # ============================================================================
    
    def run_cli(self, args):
        """运行命令行接口"""
        import argparse
        
        parser = argparse.ArgumentParser(description='石器时代工具打包项目启动助手')
        parser.add_argument('--welcome', action='store_true', help='显示欢迎信息')
        parser.add_argument('--check', action='store_true', help='检查环境')
        parser.add_argument('--configure', action='store_true', help='配置项目')
        parser.add_argument('--setup', action='store_true', help='设置监控系统')
        parser.add_argument('--test', action='store_true', help='测试运行')
        parser.add_argument('--start', action='store_true', help='完整启动')
        parser.add_argument('--troubleshoot', metavar='ISSUE', nargs='?', const='', help='故障排除')
        parser.add_argument('--quick', action='store_true', help='快速启动向导')
        parser.add_argument('--stage', help='当前阶段')
        
        if len(sys.argv) == 1:
            parser.print_help()
            return
        
        args = parser.parse_args()
        
        if args.welcome:
            print(self.show_welcome())
        
        elif args.check:
            checks, summary = self.check_environment()
            print(summary)
            
            # 显示详细结果
            print("\n📋 详细检查结果:")
            for check in checks:
                status_icon = {
                    CheckStatus.PASSED: "✅",
                    CheckStatus.FAILED: "❌",
                    CheckStatus.WARNING: "⚠️",
                    CheckStatus.PENDING: "⏳",
                    CheckStatus.SKIPPED: "⏭️"
                }.get(check.status, "❓")
                
                print(f"{status_icon} {check.name}: {check.result or '无结果'}")
        
        elif args.configure:
            config, info = self.configure_project()
            print(info)
            
            # 显示当前配置
            print("\n⚙️ 当前配置:")
            for key, value in config.to_dict().items():
                if value is not None:
                    print(f"  {key}: {value}")
        
        elif args.setup:
            success, result = self.setup_monitor()
            print(result)
            
            if success:
                # 继续设置GitHub和QQ
                gh_success, gh_result = self.setup_github()
                print("\n" + gh_result)
                
                qq_success, qq_result = self.setup_qq_report()
                print("\n" + qq_result)
        
        elif args.test:
            success, result = self.test_run()
            print(result)
        
        elif args.start:
            success, result = self.full_start()
            print(result)
        
        elif args.troubleshoot is not None:
            issue = args.troubleshoot if args.troubleshoot != '' else None
            result = self.troubleshoot(issue)
            print(result)
        
        elif args.quick:
            result = self.quick_start_wizard()
            print(result)
        
        elif args.stage:
            print(f"当前阶段: {self.current_stage.value}")
        
        else:
            parser.print_help()

# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    starter = StoneAgeProjectStarter()
    
    # 如果直接运行，显示欢迎信息
    if len(sys.argv) == 1:
        print(starter.show_welcome())
        print("\n💡 使用 --help 查看所有命令")
    else:
        starter.run_cli(sys.argv)

if __name__ == "__main__":
    main()