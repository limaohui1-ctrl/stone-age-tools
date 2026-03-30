#!/usr/bin/env python3
import platform
import sys
import os

# Windows 10兼容性检查
if hasattr(sys, 'getwindowsversion'):
    win_version = sys.getwindowsversion()
    if win_version.major < 10:
        print("⚠️  警告: 需要Windows 10或更高版本")
        print(f"当前系统: Windows {win_version.major}.{win_version.minor}")
        input("按Enter键继续...")

# -*- coding: utf-8 -*-
"""
石器时代网络稳定性优化工具包 - 集成示例
展示如何将稳定性工具包集成到现有的ASSA脚本中

功能:
1. 演示基本集成模式
2. 展示网络感知的脚本执行
3. 实现自动错误恢复
4. 提供性能监控和报告

设计原则:
- 实际可用的示例代码
- 清晰的集成模式
- 完整的错误处理
- 易于理解和修改
"""

import time
import json
import logging
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# 导入稳定性工具包模块
try:
    from 网络波动检测器 import NetworkMonitor, NetworkStatus
    from 智能重试系统 import IntelligentRetrySystem, RetryTask, RetryStrategy, RetryResult
    from 防卡机制 import AntiStuckMechanism, StuckType, RecoveryAction
    from 主程序 import StabilityOptimizationSuite
except ImportError as e:
    print(f"导入稳定性工具包失败: {e}")
    print("请确保所有模块文件都在同一目录下")
    # 创建模拟类以便示例能运行
    class NetworkMonitor:
        def __init__(self, config=None): pass
        def start_monitoring(self): print("网络监控启动")
        def stop_monitoring(self): print("网络监控停止")
        def get_current_status(self): return "EXCELLENT"
    
    class IntelligentRetrySystem:
        def __init__(self, config=None): pass
        def execute_with_retry(self, task): return task.function_to_retry(*task.function_args, **task.function_kwargs)
    
    class RetryTask:
        def __init__(self, **kwargs): self.__dict__.update(kwargs)
    
    class RetryStrategy:
        EXPONENTIAL_BACKOFF = "指数退避"
    
    class AntiStuckMechanism:
        def __init__(self, config=None): pass
        def start_monitoring(self): print("防卡监控启动")
        def stop_monitoring(self): print("防卡监控停止")
        def record_position(self, pos, map_name=None): pass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('集成示例日志.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ASSAScriptSimulator:
    """ASSA脚本模拟器，用于演示目的"""
    
    def __init__(self):
        self.current_position = (100, 100)  # 当前位置(x,y)
        self.current_map = "渔村"
        self.script_step = 0
        self.inventory = {}
        self.network_quality = 0.9  # 网络质量(0-1)
        self.simulate_network_issues = True  # 是否模拟网络问题
        
    def move_to(self, x: int, y: int) -> bool:
        """移动到指定位置"""
        logger.info(f"移动到位置 ({x}, {y})")
        
        # 模拟网络问题
        if self.simulate_network_issues and random.random() > self.network_quality:
            logger.warning("移动失败: 网络问题")
            return False
        
        # 模拟移动时间
        time.sleep(0.5 + random.random() * 1.0)
        
        self.current_position = (x, y)
        logger.info(f"移动完成，当前位置: ({x}, {y})")
        return True
    
    def talk_to_npc(self, npc_name: str) -> bool:
        """与NPC对话"""
        logger.info(f"与NPC {npc_name} 对话")
        
        # 模拟网络问题
        if self.simulate_network_issues and random.random() > self.network_quality:
            logger.warning(f"与NPC {npc_name} 对话失败: 网络问题")
            return False
        
        # 模拟对话时间
        time.sleep(1.0 + random.random() * 2.0)
        
        logger.info(f"与NPC {npc_name} 对话完成")
        return True
    
    def collect_item(self, item_name: str) -> bool:
        """收集物品"""
        logger.info(f"收集物品: {item_name}")
        
        # 模拟网络问题
        if self.simulate_network_issues and random.random() > self.network_quality:
            logger.warning(f"收集物品 {item_name} 失败: 网络问题")
            return False
        
        # 模拟收集时间
        time.sleep(0.8 + random.random() * 1.5)
        
        # 添加到背包
        self.inventory[item_name] = self.inventory.get(item_name, 0) + 1
        logger.info(f"收集完成，{item_name} 数量: {self.inventory[item_name]}")
        return True
    
    def fight_monster(self, monster_name: str) -> bool:
        """战斗"""
        logger.info(f"与 {monster_name} 战斗")
        
        # 模拟网络问题（战斗更容易失败）
        if self.simulate_network_issues and random.random() > (self.network_quality * 0.8):
            logger.warning(f"与 {monster_name} 战斗失败: 网络延迟")
            return False
        
        # 模拟战斗时间
        time.sleep(2.0 + random.random() * 3.0)
        
        # 50%几率获得战利品
        if random.random() > 0.5:
            loot = f"{monster_name}的战利品"
            self.inventory[loot] = self.inventory.get(loot, 0) + 1
            logger.info(f"战斗胜利，获得: {loot}")
        else:
            logger.info(f"战斗胜利，未获得战利品")
        
        return True
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "position": self.current_position,
            "map": self.current_map,
            "step": self.script_step,
            "inventory": self.inventory,
            "network_quality": self.network_quality,
        }


class EnhancedASSAWithStability:
    """增强版ASSA脚本，集成稳定性工具包"""
    
    def __init__(self, use_stability_tools: bool = True):
        """
        初始化增强版ASSA脚本
        
        Args:
            use_stability_tools: 是否使用稳定性工具包
        """
        self.assa = ASSAScriptSimulator()
        self.use_stability_tools = use_stability_tools
        
        if use_stability_tools:
            logger.info("初始化稳定性工具包...")
            self._init_stability_tools()
        else:
            logger.info("使用基础版ASSA脚本（无稳定性工具）")
    
    def _init_stability_tools(self):
        """初始化稳定性工具"""
        try:
            # 1. 初始化网络监控器
            self.network_monitor = NetworkMonitor("配置/网络监控配置.json")
            
            # 2. 初始化智能重试系统
            self.retry_system = IntelligentRetrySystem("配置/重试系统配置.json")
            
            # 3. 初始化防卡机制
            self.anti_stuck = AntiStuckMechanism("配置/防卡机制配置.json")
            
            # 4. 初始化完整套件（可选）
            self.stability_suite = StabilityOptimizationSuite("配置")
            self.stability_suite.initialize_modules()
            
            logger.info("稳定性工具包初始化完成")
            
        except Exception as e:
            logger.error(f"初始化稳定性工具包失败: {e}")
            logger.warning("将回退到基础模式")
            self.use_stability_tools = False
    
    def run_quest(self, quest_name: str):
        """运行任务（集成稳定性工具）"""
        logger.info(f"开始任务: {quest_name}")
        start_time = time.time()
        
        if self.use_stability_tools:
            # 使用增强版：集成稳定性工具
            success = self._run_quest_enhanced(quest_name)
        else:
            # 使用基础版：原始ASSA脚本
            success = self._run_quest_basic(quest_name)
        
        elapsed = time.time() - start_time
        status = "成功" if success else "失败"
        
        logger.info(f"任务 {quest_name} {status}，耗时: {elapsed:.1f}秒")
        
        # 生成报告
        if self.use_stability_tools:
            self._generate_quest_report(quest_name, success, elapsed)
        
        return success
    
    def _run_quest_basic(self, quest_name: str) -> bool:
        """基础版任务执行（无稳定性工具）"""
        logger.info("使用基础版执行任务")
        
        try:
            # 任务步骤
            steps = [
                ("移动到渔村仓库", lambda: self.assa.move_to(50, 60)),
                ("与仓库管理员对话", lambda: self.assa.talk_to_npc("仓库管理员")),
                ("移动到渔村外", lambda: self.assa.move_to(120, 80)),
                ("收集5个苹果", lambda: self._collect_items_basic("苹果", 5)),
                ("与渔村长老对话", lambda: self.assa.talk_to_npc("渔村长老")),
                ("击败3只哥布林", lambda: self._fight_monsters_basic("哥布林", 3)),
                ("返回渔村", lambda: self.assa.move_to(50, 60)),
                ("任务完成对话", lambda: self.assa.talk_to_npc("任务管理员")),
            ]
            
            for step_name, step_func in steps:
                logger.info(f"执行步骤: {step_name}")
                self.assa.script_step += 1
                
                if not step_func():
                    logger.error(f"步骤失败: {step_name}")
                    return False
                
                # 基础版：简单等待
                time.sleep(1.0)
            
            return True
            
        except Exception as e:
            logger.error(f"任务执行异常: {e}")
            return False
    
    def _run_quest_enhanced(self, quest_name: str) -> bool:
        """增强版任务执行（集成稳定性工具）"""
        logger.info("使用增强版执行任务（集成稳定性工具）")
        
        # 启动稳定性监控
        self._start_stability_monitoring()
        
        try:
            # 使用智能重试系统包装任务
            task = RetryTask(
                task_id=f"quest_{quest_name}",
                task_name=quest_name,
                function_to_retry=self._execute_quest_steps,
                function_args=(quest_name,),
                max_attempts=3,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                success_condition=lambda result: result is True,
                on_retry=lambda attempt, delay, ctx: logger.info(f"第{attempt}次重试，等待{delay:.1f}秒"),
            )
            
            # 执行带重试的任务
            result = self.retry_system.execute_with_retry(task)
            
            return result
            
        except Exception as e:
            logger.error(f"增强版任务执行异常: {e}")
            return False
        
        finally:
            # 停止稳定性监控
            self._stop_stability_monitoring()
    
    def _execute_quest_steps(self, quest_name: str) -> bool:
        """执行任务步骤（被重试系统包装）"""
        # 检查网络状态
        if hasattr(self, 'network_monitor'):
            net_status = self.network_monitor.get_current_status()
            if net_status == "DISCONNECTED":
                logger.warning("网络断开，暂停执行")
                return False
        
        # 任务步骤（增强版）
        steps = [
            ("移动到渔村仓库", self._enhanced_move, (50, 60)),
            ("与仓库管理员对话", self._enhanced_talk, ("仓库管理员",)),
            ("移动到渔村外", self._enhanced_move, (120, 80)),
            ("收集5个苹果", self._enhanced_collect, ("苹果", 5)),
            ("与渔村长老对话", self._enhanced_talk, ("渔村长老",)),
            ("击败3只哥布林", self._enhanced_fight, ("哥布林", 3)),
            ("返回渔村", self._enhanced_move, (50, 60)),
            ("任务完成对话", self._enhanced_talk, ("任务管理员",)),
        ]
        
        for step_name, step_func, step_args in steps:
            logger.info(f"执行增强步骤: {step_name}")
            self.assa.script_step += 1
            
            # 记录位置（防卡机制）
            if step_func == self._enhanced_move:
                self._record_position(step_args[0], step_args[1])
            
            # 执行步骤
            if not step_func(*step_args):
                logger.error(f"增强步骤失败: {step_name}")
                
                # 触发防卡恢复
                if hasattr(self, 'anti_stuck'):
                    recovery = self.anti_stuck.detect_and_recover()
                    logger.info(f"防卡恢复动作: {recovery}")
                
                return False
            
            # 增强版：智能等待（基于网络状态）
            self._smart_wait()
        
        return True
    
    def _enhanced_move(self, x: int, y: int) -> bool:
        """增强版移动（集成稳定性）"""
        # 创建重试任务
        task = RetryTask(
            task_id=f"move_{x}_{y}",
            task_name=f"移动到({x},{y})",
            function_to_retry=self.assa.move_to,
            function_args=(x, y),
            max_attempts=2,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        )
        
        try:
            return self.retry_system.execute_with_retry(task)
        except:
            return False
    
    def _enhanced_talk(self, npc_name: str) -> bool:
        """增强版对话（集成稳定性）"""
        # 检查网络状态
        if hasattr(self, 'network_monitor'):
            status = self.network_monitor.get_current_status()
            if status in ["POOR", "UNSTABLE", "DISCONNECTED"]:
                logger.warning(f"网络状态{status}，延迟对话")
                time.sleep(5.0)
        
        task = RetryTask(
            task_id=f"talk_{npc_name}",
            task_name=f"与{npc_name}对话",
            function_to_retry=self.assa.talk_to_npc,
            function_args=(npc_name,),
            max_attempts=2,
        )
        
        try:
            return self.retry_system.execute_with_retry(task)
        except:
            return False
    
    def _enhanced_collect(self, item_name: str, count: int) -> bool:
        """增强版收集（集成稳定性）"""
        success_count = 0
        
        for i in range(count):
            logger.info(f"收集 {item_name} ({i+1}/{count})")
            
            task = RetryTask(
                task_id=f"collect_{item_name}_{i}",
                task_name=f"收集{item_name}",
                function_to_retry=self.assa.collect_item,
                function_args=(item_name,),
                max_attempts=2,
            )
            
            try:
                if self.retry_system.execute_with_retry(task):
                    success_count += 1
            except:
                pass
            
            # 防卡检查
            if hasattr(self, 'anti_stuck'):
                self.anti_stuck.record_position(self.assa.current_position)
        
        return success_count >= count * 0.8  # 80%成功率即算成功
    
    def _enhanced_fight(self, monster_name: str, count: int) -> bool:
        """增强版战斗（集成稳定性）"""
        success_count = 0
        
        for i in range(count):
            logger.info(f"战斗 {monster_name} ({i+1}/{count})")
            
            # 战斗前检查网络
            if hasattr(self, 'network_monitor'):
                net_status = self.network_monitor.get_current_status()
                if net_status == "DISCONNECTED":
                    logger.warning("网络断开，暂停战斗")
                    return False
            
            task = RetryTask(
                task_id=f"fight_{monster_name}_{i}",
                task_name=f"与{monster_name}战斗",
                function_to_retry=self.assa.fight_monster,
                function_args=(monster_name,),
                max_attempts=2,
            )
            
            try:
                if self.retry_system.execute_with_retry(task):
                    success_count += 1
            except:
                pass
        
        return success_count >= count * 0.7  # 70%成功率即算成功
    
    def _collect_items_basic(self, item_name: str, count: int) -> bool:
        """基础版收集"""
        for i in range(count):
            if not self.assa.collect_item(item_name):
                return False
        return True
    
    def _fight_monsters_basic(self, monster_name: str, count: int) -> bool:
        """基础版战斗"""
        for i in range(count):
            if not self.assa.fight_monster(monster_name):
                return False
        return True
    
    def _start_stability_monitoring(self):
        """启动稳定性监控"""
        if not self.use_stability_tools:
            return
        
        try:
            if hasattr(self, 'network_monitor'):
                self.network_monitor.start_monitoring()
            
            if hasattr(self, 'anti_stuck'):
                self.anti_stuck.start_monitoring()
            
            if hasattr(self, 'stability_suite'):
                self.stability_suite.start_all_services()
            
            logger.info("稳定性监控已启动")
            
        except Exception as e:
            logger.error(f"启动稳定性监控失败: {e}")
    
    def _stop_stability_monitoring(self):
        """停止稳定性监控"""
        if not self.use_stability_tools:
            return
        
        try:
            if self.network_monitor:
                self.network_monitor.stop_monitoring()
            if self.retry_system:
                self.retry_system.stop()
            if self.anti_stuck:
                self.anti_stuck.stop_monitoring()
            
            print("稳定性监控已停止")
        except Exception as e:
            print(f"停止监控时出错: {e}")

def main():
    """主函数 - 演示集成示例"""
    print("石器时代脚本集成示例")
    print("=" * 50)
    
    # 创建集成示例
    example = StoneAgeScriptExample(use_stability_tools=True)
    
    # 启动稳定性监控
    example.start_stability_monitoring()
    
    # 模拟脚本执行
    print("\n模拟脚本执行...")
    example.execute_script_part("渔村到加加村")
    example.execute_script_part("加加村到奇努伊村")
    example.execute_script_part("奇努伊村到渔村")
    
    # 停止监控
    example.stop_stability_monitoring()
    
    print("\n集成示例演示完成!")
    print("这个示例展示了如何将稳定性工具集成到现有脚本中。")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())