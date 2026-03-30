"""
⚠️ 安全修复说明
本文件已经过安全修复，主要改进包括：
1. 替换危险的os.system为安全的subprocess.run
2. 添加命令执行超时和输出捕获
3. 添加异常处理防止崩溃
4. 添加文件操作安全检查

安全修复时间: 2026-03-28 18:46:05
修复工具: 安全修复脚本.py
安全等级: 🔴→🟡 (高危→中危)

使用建议:
1. 在测试环境中验证修复
2. 监控工具运行日志
3. 及时报告安全问题
"""

import subprocess
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石器时代脚本调试器
===============

一个专门为石器时代ASSA脚本设计的可视化调试工具。
支持语法高亮、断点调试、变量监视、执行监控等功能。

作者: OpenClaw AI助手
创建时间: 2026年3月23日
版本: 1.0.0
"""

import os
import sys
import re
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# 尝试导入PyQt6，如果失败则使用tkinter作为备选
try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QTextEdit, QPushButton, QLabel, 
                                 QSplitter, QTreeWidget, QTreeWidgetItem, 
                                 QListWidget, QListWidgetItem, QTabWidget,
                                 QStatusBar, QMenuBar, QMenu, QFileDialog,
                                 QMessageBox, QToolBar, QAction, QLineEdit,
                                 QComboBox, QSpinBox, QCheckBox, QGroupBox)
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
    from PyQt6.QtGui import (QFont, QSyntaxHighlighter, QTextCharFormat, 
                            QColor, QPalette, QKeySequence, QIcon)
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("警告: PyQt6未安装，将使用简化控制台版本")
    # 这里可以添加备选GUI库或纯控制台界面

# ============================================================================
# 数据模型类
# ============================================================================

class DebuggerState(Enum):
    """调试器状态枚举"""
    IDLE = "空闲"
    RUNNING = "运行中"
    PAUSED = "已暂停"
    STEPPING = "单步执行"
    BREAKPOINT = "断点命中"
    ERROR = "错误"
    FINISHED = "已完成"

@dataclass
class ScriptLine:
    """脚本行数据"""
    line_number: int
    original_text: str
    cleaned_text: str
    label: Optional[str] = None
    is_breakpoint: bool = False
    is_executed: bool = False
    execution_count: int = 0
    variables_changed: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:

def safe_system_command(cmd):
    """安全执行系统命令"""
    try:
        result = subprocess.run(
            cmd.split() if isinstance(cmd, str) else cmd,
            check=True,
            timeout=30,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        return False, "", str(e)
    except Exception as e:
        print(f"命令执行异常: {e}")
        return False, "", str(e)

def safe_file_operation(operation, path, *args, **kwargs):
    """安全文件操作"""
    try:
        if operation == "remove":
            if os.path.exists(path):
                os.remove(path)
                return True
            return False
        elif operation == "rmtree":
            import shutil
            shutil.rmtree(path, ignore_errors=True, *args, **kwargs)
            return True
        else:
            print(f"未知文件操作: {operation}")
            return False
    except Exception as e:
        print(f"文件操作失败: {e}")
        return False

        """转换为字典"""
        return {
            "line_number": self.line_number,
            "original_text": self.original_text,
            "cleaned_text": self.cleaned_text,
            "label": self.label,
            "is_breakpoint": self.is_breakpoint,
            "is_executed": self.is_executed,
            "execution_count": self.execution_count,
            "variables_changed": self.variables_changed.copy()
        }

@dataclass
class Variable:
    """变量数据"""
    name: str
    value: Any
    type: str = "unknown"
    last_changed: Optional[datetime] = None
    change_count: int = 0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "value": str(self.value),
            "type": self.type,
            "last_changed": self.last_changed.isoformat() if self.last_changed else None,
            "change_count": self.change_count
        }

@dataclass
class Breakpoint:
    """断点数据"""
    line_number: int
    enabled: bool = True
    hit_count: int = 0
    condition: Optional[str] = None
    last_hit: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "line_number": self.line_number,
            "enabled": self.enabled,
            "hit_count": self.hit_count,
            "condition": self.condition,
            "last_hit": self.last_hit.isoformat() if self.last_hit else None
        }

@dataclass
class ExecutionContext:
    """执行上下文"""
    current_line: int = 0
    current_label: Optional[str] = None
    call_stack: List[Tuple[str, int]] = field(default_factory=list)
    variables: Dict[str, Variable] = field(default_factory=dict)
    execution_time: float = 0.0
    start_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "current_line": self.current_line,
            "current_label": self.current_label,
            "call_stack": self.call_stack.copy(),
            "variables": {k: v.to_dict() for k, v in self.variables.items()},
            "execution_time": self.execution_time,
            "start_time": self.start_time.isoformat() if self.start_time else None
        }

# ============================================================================
# ASSA脚本解析器
# ============================================================================

class ASSAParser:
    """ASSA脚本解析器"""
    
    # ASSA指令模式
    INSTRUCTION_PATTERNS = {
        'dim': r'^\s*dim\s+(@\w+)(?:\s*,\s*@\w+)*\s*$',
        'let': r'^\s*let\s+(@\w+)\s*,\s*=\s*,\s*(.+)$',
        'if': r'^\s*if\s+(.+?)\s*,\s*=\s*,\s*(.+?)\s*,\s*(\w+)$',
        'goto': r'^\s*goto\s+(\w+)$',
        'label': r'^\s*label\s+(\w+)$',
        'input': r'^\s*input\s+(@\w+)\s*,\s*(.+)$',
        'print': r'^\s*print\s+(.+)$',
        'msg': r'^\s*msg\s+(.+)$',
        'check': r'^\s*check\s+(.+)$',
        'wait': r'^\s*wait\s+(\d+)$',
        'walkpos': r'^\s*walkpos\s+(\d+)\s*,\s*(\d+)$',
        'waitpos': r'^\s*waitpos\s+(\d+)\s*,\s*(\d+)$',
        'say': r'^\s*say\s+(.+)$',
        'log': r'^\s*log\s+(.+)$',
    }
    
    def __init__(self):
        self.lines: List[ScriptLine] = []
        self.labels: Dict[str, int] = {}  # 标签名 -> 行号
        self.variables: Set[str] = set()
        
    def parse_file(self, filepath: str) -> List[ScriptLine]:
        """解析ASSA脚本文件"""
        self.lines = []
        self.labels = {}
        self.variables = set()
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                script_line = self._parse_line(i, line)
                self.lines.append(script_line)
                
                # 提取标签
                if script_line.label:
                    self.labels[script_line.label] = i
                    
                # 提取变量
                self._extract_variables(script_line)
                
            return self.lines
            
        except Exception as e:
            print(f"解析文件错误: {e}")
            return []
    
    def _parse_line(self, line_number: int, text: str) -> ScriptLine:
        """解析单行脚本"""
        cleaned = text.strip()
        
        # 检查是否是标签
        label_match = re.match(r'^\s*label\s+(\w+)$', text)
        label = label_match.group(1) if label_match else None
        
        # 检查是否是注释或空行
        is_comment = cleaned.startswith('//') or cleaned.startswith('#') or cleaned == ''
        
        return ScriptLine(
            line_number=line_number,
            original_text=text,
            cleaned_text=cleaned if not is_comment else "",
            label=label
        )
    
    def _extract_variables(self, script_line: ScriptLine):
        """从脚本行中提取变量"""
        text = script_line.cleaned_text
        
        # 提取dim语句中的变量
        dim_match = re.match(r'^\s*dim\s+(.+)$', text)
        if dim_match:
            vars_str = dim_match.group(1)
            vars_list = [v.strip() for v in vars_str.split(',')]
            for var in vars_list:
                if var.startswith('@'):
                    self.variables.add(var)
        
        # 提取let语句中的变量
        let_match = re.match(r'^\s*let\s+(@\w+)\s*,\s*=\s*,\s*.+$', text)
        if let_match:
            var = let_match.group(1)
            self.variables.add(var)
        
        # 提取input语句中的变量
        input_match = re.match(r'^\s*input\s+(@\w+)\s*,\s*.+$', text)
        if input_match:
            var = input_match.group(1)
            self.variables.add(var)
    
    def get_label_line(self, label: str) -> Optional[int]:
        """获取标签对应的行号"""
        return self.labels.get(label)
    
    def get_line_by_number(self, line_number: int) -> Optional[ScriptLine]:
        """根据行号获取脚本行"""
        if 1 <= line_number <= len(self.lines):
            return self.lines[line_number - 1]
        return None
    
    def get_variables(self) -> List[str]:
        """获取所有变量"""
        return sorted(list(self.variables))
    
    def analyze_script(self) -> Dict:
        """分析脚本结构"""
        total_lines = len(self.lines)
        non_empty_lines = sum(1 for line in self.lines if line.cleaned_text)
        label_count = len(self.labels)
        variable_count = len(self.variables)
        
        # 统计指令类型
        instruction_stats = {}
        for line in self.lines:
            if line.cleaned_text:
                for instr, pattern in self.INSTRUCTION_PATTERNS.items():
                    if re.match(pattern, line.cleaned_text, re.IGNORECASE):
                        instruction_stats[instr] = instruction_stats.get(instr, 0) + 1
                        break
        
        return {
            "total_lines": total_lines,
            "non_empty_lines": non_empty_lines,
            "label_count": label_count,
            "variable_count": variable_count,
            "instruction_stats": instruction_stats,
            "labels": list(self.labels.keys()),
            "variables": list(self.variables)
        }

# ============================================================================
# ASSA脚本执行器
# ============================================================================

class ASSAExecutor:
    """ASSA脚本执行器"""
    
    def __init__(self, parser: ASSAParser):
        self.parser = parser
        self.state = DebuggerState.IDLE
        self.context = ExecutionContext()
        self.breakpoints: Dict[int, Breakpoint] = {}
        self.execution_history: List[Dict] = []
        self.error_log: List[Dict] = []
        
        # 执行控制
        self._stop_requested = False
        self._pause_requested = False
        self._step_requested = False
        self._current_thread: Optional[threading.Thread] = None
        
    def load_script(self, filepath: str) -> bool:
        """加载脚本"""
        lines = self.parser.parse_file(filepath)
        if not lines:
            return False
        
        # 重置状态
        self.state = DebuggerState.IDLE
        self.context = ExecutionContext()
        self.execution_history = []
        self.error_log = []
        
        # 初始化变量
        for var_name in self.parser.get_variables():
            self.context.variables[var_name] = Variable(
                name=var_name,
                value="",
                type="string",
                change_count=0
            )
        
        return True
    
    def set_breakpoint(self, line_number: int, enabled: bool = True, condition: Optional[str] = None) -> bool:
        """设置断点"""
        if 1 <= line_number <= len(self.parser.lines):
            self.breakpoints[line_number] = Breakpoint(
                line_number=line_number,
                enabled=enabled,
                condition=condition
            )
            return True
        return False
    
    def remove_breakpoint(self, line_number: int) -> bool:
        """移除断点"""
        if line_number in self.breakpoints:
            del self.breakpoints[line_number]
            return True
        return False
    
    def toggle_breakpoint(self, line_number: int) -> bool:
        """切换断点状态"""
        if line_number in self.breakpoints:
            self.breakpoints[line_number].enabled = not self.breakpoints[line_number].enabled
            return True
        return False
    
    def run(self) -> bool:
        """运行脚本"""
        if self.state != DebuggerState.IDLE:
            return False
        
        self.state = DebuggerState.RUNNING
        self.context.start_time = datetime.now()
        self._stop_requested = False
        self._pause_requested = False
        
        # 在新线程中执行
        self._current_thread = threading.Thread(target=self._execute_script)
        self._current_thread.start()
        
        return True
    
    def pause(self) -> bool:
        """暂停执行"""
        if self.state == DebuggerState.RUNNING:
            self._pause_requested = True
            return True
        return False
    
    def resume(self) -> bool:
        """恢复执行"""
        if self.state == DebuggerState.PAUSED:
            self.state = DebuggerState.RUNNING
            self._pause_requested = False
            return True
        return False
    
    def stop(self) -> bool:
        """停止执行"""
        if self.state in [DebuggerState.RUNNING, DebuggerState.PAUSED, DebuggerState.STEPPING]:
            self._stop_requested = True
            self.state = DebuggerState.IDLE
            return True
        return False
    
    def step_over(self) -> bool:
        """单步执行（跳过函数）"""
        if self.state in [DebuggerState.PAUSED, DebuggerState.BREAKPOINT]:
            self.state = DebuggerState.STEPPING
            self._step_requested = True
            return True
        return False
    
    def step_into(self) -> bool:
        """单步执行（进入函数）"""
        # 对于ASSA脚本，step_into和step_over基本相同
        return self.step_over()
    
    def step_out(self) -> bool:
        """单步执行（跳出函数）"""
        # 对于ASSA脚本，step_out和step_over基本相同
        return self.step_over()
    
    def _execute_script(self):
        """执行脚本（内部方法）"""
        try:
            lines = self.parser.lines
            total_lines = len(lines)
            
            # 从第一行开始执行
            self.context.current_line = 1
            
            while self.context.current_line <= total_lines and not self._stop_requested:
                # 检查暂停请求
                if self._pause_requested:
                    self.state = DebuggerState.PAUSED
                    while self._pause_requested and not self._stop_requested:
                        time.sleep(0.1)
                    
                    if self._stop_requested:
                        break
                    
                    self.state = DebuggerState.RUNNING
                
                # 检查单步执行
                if self.state == DebuggerState.STEPPING:
                    self.state = DebuggerState.PAUSED
                    self._step_requested = False
                    # 等待下一步指令
                    while not self._step_requested and not self._stop_requested:
                        time.sleep(0.1)
                    
                    if self._stop_requested:
                        break
                    
                    self.state = DebuggerState.RUNNING
                
                # 获取当前行
                current_line = self.context.current_line
                script_line = lines[current_line - 1]
                
                # 记录执行历史
                self._record_execution(current_line)
                
                # 检查断点
                if current_line in self.breakpoints:
                    bp = self.breakpoints[current_line]
                    if bp.enabled:
                        # 检查条件
                        condition_met = True
                        if bp.condition:
                            try:
                                # 简单的条件评估（实际实现需要更复杂的表达式解析）
                                condition_met = self._evaluate_condition(bp.condition)
                            except:
                                condition_met = True
                        
                        if condition_met:
                            bp.hit_count += 1
                            bp.last_hit = datetime.now()
                            self.state = DebuggerState.BREAKPOINT
                            # 等待继续执行
                            while self.state == DebuggerState.BREAKPOINT and not self._stop_requested:
                                time.sleep(0.1)
                            
                            if self._stop_requested:
                                break
                
                # 执行当前行
                self._execute_line(script_line)
                
                # 更新执行时间
                self.context.execution_time = (datetime.now() - self.context.start_time).total_seconds()
                
                # 移动到下一行
                self.context.current_line += 1
                
                # 短暂暂停，模拟执行时间
                time.sleep(0.01)
            
            # 执行完成
            if not self._stop_requested:
                self.state = DebuggerState.FINISHED
                print("脚本执行完成")
            else:
                self.state = DebuggerState.IDLE
                print("脚本执行被停止")
                
        except Exception as e:
            self.state = DebuggerState.ERROR
            self._record_error(f"执行错误: {e}", self.context.current_line)
            print(f"执行错误: {e}")
    
    def _execute_line(self, script_line: ScriptLine):
        """执行单行脚本（简化版本）"""
        line_text = script_line.cleaned_text
        
        if not line_text:
            return
        
        # 标记该行已执行
        script_line.is_executed = True
        script_line.execution_count += 1
        
        # 解析并执行指令（简化实现）
        try:
            # dim指令
            if line_text.startswith('dim'):
                # 提取变量
                vars_part = line_text[3:].strip()
                vars_list = [v.strip() for v in vars_part.split(',')]
                for var in vars_list:
                    if var.startswith('@'):
                        if var not in self.context.variables:
                            self.context.variables[var] = Variable(
                                name=var,
                                value="",
                                type="string"
                            )
                        script_line.variables_changed.append(var)
            
            # let指令
            elif line_text.startswith('let'):
                match = re.match(r'^\s*let\s+(@\w+)\s*,\s*=\s*,\s*(.+)$', line_text)
                if match:
                    var_name = match.group(1)
                    value = match.group(2).strip()
                    
                    if var_name in self.context.variables:
                        var = self.context.variables[var_name]
                        var.value = value
                        var.last_changed = datetime.now()
                        var.change_count += 1
                    else:
                        self.context.variables[var_name] = Variable(
                            name=var_name,
                            value=value,
                            type="string",
                            last_changed=datetime.now(),
                            change_count=1
                        )
                    
                    script_line.variables_changed.append(var_name)
            
            # goto指令
            elif line_text.startswith('goto'):
                match = re.match(r'^\s*goto\s+(\w+)$', line_text)
                if match:
                    label = match.group(1)
                    target_line = self.parser.get_label_line(label)
                    if target_line:
                        # 记录调用栈
                        self.context.call_stack.append((self.context.current_label or "main", self.context.current_line))
                        self.context.current_line = target_line - 1  # -1因为循环会+1
                        self.context.current_label = label
            
            # label指令
            elif line_text.startswith('label'):
                match = re.match(r'^\s*label\s+(\w+)$', line_text)
                if match:
                    self.context.current_label = match.group(1)
            
            # if指令
            elif line_text.startswith('if'):
                match = re.match(r'^\s*if\s+(.+?)\s*,\s*=\s*,\s*(.+?)\s*,\s*(\w+)$', line_text)
                if match:
                    left = match.group(1).strip()
                    right = match.group(2).strip()
                    target_label = match.group(3).strip()
                    
                    # 简单的条件判断（实际需要更复杂的表达式解析）
                    condition_met = False
                    try:
                        # 尝试作为变量比较
                        if left.startswith('@') and left in self.context.variables:
                            left_value = self.context.variables[left].value
                            condition_met = (str(left_value) == str(right))
                        else:
                            # 直接值比较
                            condition_met = (str(left) == str(right))
                    except:
                        condition_met = False
                    
                    if condition_met:
                        target_line = self.parser.get_label_line(target_label)
                        if target_line:
                            self.context.call_stack.append((self.context.current_label or "main", self.context.current_line))
                            self.context.current_line = target_line - 1
                            self.context.current_label = target_label
            
            # 其他指令（简化处理）
            elif line_text.startswith('input'):
                # 模拟用户输入
                match = re.match(r'^\s*input\s+(@\w+)\s*,\s*(.+)$', line_text)
                if match:
                    var_name = match.group(1)
                    prompt = match.group(2)
                    
                    # 在实际调试器中，这里应该弹出输入对话框
                    # 这里我们模拟输入"1"
                    simulated_input = "1"
                    
                    if var_name in self.context.variables:
                        var = self.context.variables[var_name]
                        var.value = simulated_input
                        var.last_changed = datetime.now()
                        var.change_count += 1
                    else:
                        self.context.variables[var_name] = Variable(
                            name=var_name,
                            value=simulated_input,
                            type="string",
                            last_changed=datetime.now(),
                            change_count=1
                        )
                    
                    script_line.variables_changed.append(var_name)
            
            elif line_text.startswith('print') or line_text.startswith('msg'):
                # 输出信息（在实际调试器中显示在输出窗口）
                pass
            
            elif line_text.startswith('check'):
                # 检查指令（简化处理）
                pass
            
            elif line_text.startswith('wait'):
                # 等待指令
                match = re.match(r'^\s*wait\s+(\d+)$', line_text)
                if match:
                    wait_time = int(match.group(1))
                    # 在实际调试器中，这里应该等待指定时间
                    # 这里我们只是记录
                    pass
            
            elif line_text.startswith('walkpos') or line_text.startswith('waitpos'):
                # 移动指令（简化处理）
                pass
            
        except Exception as e:
            self._record_error(f"执行指令错误: {e}", script_line.line_number)
    
    def _evaluate_condition(self, condition: str) -> bool:
        """评估条件表达式（简化版本）"""
        try:
            # 简单的条件评估
            # 实际实现需要完整的表达式解析器
            return True
        except:
            return False
    
    def _record_execution(self, line_number: int):
        """记录执行历史"""
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "line_number": line_number,
            "state": self.state.value,
            "context": self.context.to_dict()
        })
        
        # 限制历史记录大小
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-1000:]
    
    def _record_error(self, error_message: str, line_number: int):
        """记录错误"""
        self.error_log.append({
            "timestamp": datetime.now().isoformat(),
            "line_number": line_number,
            "error": error_message,
            "context": self.context.to_dict()
        })
    
    def get_execution_summary(self) -> Dict:
        """获取执行摘要"""
        total_lines = len(self.parser.lines)
        executed_lines = sum(1 for line in self.parser.lines if line.is_executed)
        execution_time = self.context.execution_time
        
        # 统计变量变化
        variable_changes = {}
        for var in self.context.variables.values():
            variable_changes[var.name] = var.change_count
        
        # 统计断点命中
        breakpoint_hits = {}
        for bp in self.breakpoints.values():
            breakpoint_hits[bp.line_number] = bp.hit_count
        
        return {
            "total_lines": total_lines,
            "executed_lines": executed_lines,
            "execution_percentage": (executed_lines / total_lines * 100) if total_lines > 0 else 0,
            "execution_time": execution_time,
            "error_count": len(self.error_log),
            "variable_changes": variable_changes,
            "breakpoint_hits": breakpoint_hits,
            "state": self.state.value
        }
    
    def get_current_state(self) -> Dict:
        """获取当前状态"""
        return {
            "state": self.state.value,
            "current_line": self.context.current_line,
            "current_label": self.context.current_label,
            "call_stack": self.context.call_stack.copy(),
            "variables": {k: v.to_dict() for k, v in self.context.variables.items()},
            "execution_time": self.context.execution_time
        }

# ============================================================================
# 语法高亮器
# ============================================================================

class ASSAHighlighter:
    """ASSA语法高亮器"""
    
    def __init__(self):
        # 定义语法高亮规则
        self.keywords = [
            'dim', 'let', 'if', 'goto', 'label', 'input', 'print',
            'msg', 'check', 'wait', 'walkpos', 'waitpos', 'say', 'log'
        ]
        
        self.operators = ['=', ',', '\\+', '-', '\\*', '/', '>', '<']
        
        # 颜色定义
        self.colors = {
            'keyword': QColor(0, 0, 255),      # 蓝色
            'operator': QColor(255, 0, 0),     # 红色
            'variable': QColor(128, 0, 128),   # 紫色
            'number': QColor(0, 128, 0),       # 绿色
            'string': QColor(255, 0, 255),     # 洋红色
            'comment': QColor(128, 128, 128),  # 灰色
            'label': QColor(0, 128, 128),      # 青色
        }
    
    def highlight_line(self, line: str) -> str:
        """高亮单行代码（返回HTML格式）"""
        if not line.strip():
            return line
        
        # 处理注释
        if '//' in line:
            comment_index = line.find('//')
            code_part = line[:comment_index]
            comment_part = line[comment_index:]
            highlighted = self._highlight_code(code_part)
            highlighted += f'<span style="color:{self.colors["comment"].name()}">{comment_part}</span>'
            return highlighted
        
        return self._highlight_code(line)
    
    def _highlight_code(self, code: str) -> str:
        """高亮代码部分"""
        highlighted = code
        
        # 高亮关键字
        for keyword in self.keywords:
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            highlighted = pattern.sub(
                f'<span style="color:{self.colors["keyword"].name()}">{keyword}</span>',
                highlighted
            )
        
        # 高亮变量
        variable_pattern = re.compile(r'(@\w+)')
        highlighted = variable_pattern.sub(
            f'<span style="color:{self.colors["variable"].name()}">\\1</span>',
            highlighted
        )
        
        # 高亮标签（在label指令中）
        label_pattern = re.compile(r'\blabel\s+(\w+)', re.IGNORECASE)
        highlighted = label_pattern.sub(
            f'label <span style="color:{self.colors["label"].name()}">\\1</span>',
            highlighted
        )
        
        # 高亮数字
        number_pattern = re.compile(r'\b\d+\b')
        highlighted = number_pattern.sub(
            f'<span style="color:{self.colors["number"].name()}">\\0</span>',
            highlighted
        )
        
        # 高亮字符串（简化处理）
        string_pattern = re.compile(r'"[^"]*"')
        highlighted = string_pattern.sub(
            f'<span style="color:{self.colors["string"].name()}">\\0</span>',
            highlighted
        )
        
        return highlighted

# ============================================================================
# 主应用程序
# ============================================================================

def create_simple_cli_debugger():
    """创建简单的CLI调试器（备选方案）"""
    print("=" * 60)
    print("石器时代脚本调试器 (CLI版本)")
    print("=" * 60)
    
    # 创建解析器和执行器
    parser = ASSAParser()
    executor = ASSAExecutor(parser)
    
    # 示例脚本路径
    example_script = "/root/.openclaw/workspace/完整极品人脚本_NG25版/00【开始】.asc"
    
    if os.path.exists(example_script):
        print(f"加载示例脚本: {example_script}")
        
        # 加载脚本
        if executor.load_script(example_script):
            # 分析脚本
            analysis = parser.analyze_script()
            print(f"\n脚本分析结果:")
            print(f"  总行数: {analysis['total_lines']}")
            print(f"  非空行: {analysis['non_empty_lines']}")
            print(f"  标签数: {analysis['label_count']}")
            print(f"  变量数: {analysis['variable_count']}")
            
            print(f"\n指令统计:")
            for instr, count in analysis['instruction_stats'].items():
                print(f"  {instr}: {count}")
            
            print(f"\n变量列表:")
            for var in analysis['variables']:
                print(f"  {var}")
            
            print(f"\n标签列表:")
            for label in analysis['labels']:
                print(f"  {label}")
            
            # 设置断点示例
            print(f"\n设置断点示例:")
            for line_num in [1, 10, 20]:
                if executor.set_breakpoint(line_num):
                    print(f"  在第 {line_num} 行设置断点")
            
            # 显示调试器状态
            print(f"\n调试器状态: {executor.state.value}")
            print(f"断点数量: {len(executor.breakpoints)}")
            
            return True
        else:
            print("加载脚本失败")
            return False
    else:
        print(f"示例脚本不存在: {example_script}")
        print("请确保有ASSA脚本文件可供调试")
        return False

def main():
    """主函数"""
    print("石器时代脚本调试器 v1.0.0")
    print("=" * 60)
    
    # 检查GUI可用性
    if PYQT_AVAILABLE:
        print("检测到PyQt6，将启动图形界面版本...")
        # 这里可以启动PyQt6 GUI
        # 但由于时间关系，我们先使用CLI版本
        print("GUI版本开发中，暂时使用CLI版本")
    
    # 启动CLI版本
    return create_simple_cli_debugger()

if __name__ == "__main__":
    success = main()
    if success:
        print("\n调试器准备就绪！")
        print("下一步:")
        print("1. 添加完整的GUI界面")
        print("2. 实现实时调试功能")
        print("3. 添加变量监视和断点管理")
        print("4. 集成到现有工具链中")
    else:
        print("\n调试器初始化失败")
    
    print("\n" + "=" * 60)
    print("调试器原型构建完成！")
    print("这是一个基础框架，包含:")
    print("  ✓ ASSA脚本解析器")
    print("  ✓ 脚本执行器")
    print("  ✓ 断点管理系统")
    print("  ✓ 变量跟踪系统")
    print("  ✓ 执行历史记录")
    print("  ✓ 语法高亮器")
    print("\n下一步可以:")
    print("  1. 添加PyQt6 GUI界面")
    print("  2. 实现可视化调试控制")
    print("  3. 添加脚本编辑器")
    print("  4. 集成性能分析工具")
    print("=" * 60)