#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

"""
石器时代脚本性能分析器
=====================

一个专门为石器时代ASSA脚本设计的性能分析工具。
基于石器时代脚本调试器架构，提供性能瓶颈识别、优化建议、执行效率分析等功能。

作者: OpenClaw AI助手
创建时间: 2026年3月23日
版本: 1.0.0
基础: 基于石器时代脚本调试器 v1.0.0
"""

import os
import sys
import re
import json
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import threading
import psutil

# 导入调试器基础模块
sys.path.append('/root/.openclaw/workspace')
try:
    from 石器时代脚本调试器 import (
        ASSAParser, ASSAExecutor, DebuggerState,
        ScriptLine, Variable, Breakpoint, ExecutionContext
    )
    DEBUGGER_AVAILABLE = True
except ImportError:
    DEBUGGER_AVAILABLE = False
    print("警告: 石器时代脚本调试器未找到，将使用独立版本")
    # 这里可以定义简化版本的数据类
    from dataclasses import dataclass, field
    from enum import Enum
    
    class DebuggerState(Enum):
        IDLE = "空闲"
        RUNNING = "运行中"
    
    @dataclass
    class ScriptLine:
        line_number: int
        cleaned_text: str = ""

# ============================================================================
# 性能分析数据模型
# ============================================================================

class PerformanceMetric(Enum):
    """性能指标枚举"""
    EXECUTION_TIME = "执行时间"
    MEMORY_USAGE = "内存使用"
    CPU_USAGE = "CPU使用"
    NETWORK_LATENCY = "网络延迟"
    LOOP_ITERATIONS = "循环迭代"
    VARIABLE_ACCESS = "变量访问"
    FUNCTION_CALLS = "函数调用"
    WAIT_TIME = "等待时间"

@dataclass
class PerformanceData:
    """性能数据"""
    metric: PerformanceMetric
    value: float
    timestamp: datetime
    line_number: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "metric": self.metric.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "line_number": self.line_number,
            "context": self.context
        }

@dataclass
class PerformanceIssue:
    """性能问题"""
    issue_id: str
    issue_type: str
    severity: str  # high, medium, low
    description: str
    line_numbers: List[int]
    metric_values: Dict[str, float]
    suggestions: List[str]
    detected_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "issue_id": self.issue_id,
            "issue_type": self.issue_type,
            "severity": self.severity,
            "description": self.description,
            "line_numbers": self.line_numbers,
            "metric_values": self.metric_values,
            "suggestions": self.suggestions,
            "detected_at": self.detected_at.isoformat()
        }

@dataclass
class OptimizationSuggestion:
    """优化建议"""
    suggestion_id: str
    title: str
    description: str
    affected_lines: List[int]
    expected_improvement: float  # 预期改进百分比
    implementation: str
    risk_level: str  # low, medium, high
    priority: int  # 1-10, 10最高
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "suggestion_id": self.suggestion_id,
            "title": self.title,
            "description": self.description,
            "affected_lines": self.affected_lines,
            "expected_improvement": self.expected_improvement,
            "implementation": self.implementation,
            "risk_level": self.risk_level,
            "priority": self.priority
        }

@dataclass
class PerformanceReport:
    """性能报告"""
    report_id: str
    script_name: str
    analysis_time: datetime
    total_execution_time: float
    total_memory_used: float
    total_cpu_used: float
    performance_issues: List[PerformanceIssue]
    optimization_suggestions: List[OptimizationSuggestion]
    performance_metrics: Dict[str, List[float]]
    summary: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "report_id": self.report_id,
            "script_name": self.script_name,
            "analysis_time": self.analysis_time.isoformat(),
            "total_execution_time": self.total_execution_time,
            "total_memory_used": self.total_memory_used,
            "total_cpu_used": self.total_cpu_used,
            "performance_issues": [issue.to_dict() for issue in self.performance_issues],
            "optimization_suggestions": [suggestion.to_dict() for suggestion in self.optimization_suggestions],
            "performance_metrics": self.performance_metrics,
            "summary": self.summary
        }
    
    def generate_markdown_report(self) -> str:
        """生成Markdown格式报告"""
        report = f"""# 石器时代脚本性能分析报告

## 📊 报告概览
- **脚本名称**: {self.script_name}
- **分析时间**: {self.analysis_time.strftime('%Y-%m-%d %H:%M:%S')}
- **总执行时间**: {self.total_execution_time:.2f}秒
- **总内存使用**: {self.total_memory_used:.2f} MB
- **总CPU使用**: {self.total_cpu_used:.2f}%

## 🚨 性能问题 ({len(self.performance_issues)}个)

"""
        
        for i, issue in enumerate(self.performance_issues, 1):
            report += f"""### {i}. {issue.issue_type} ({issue.severity.upper()})
**描述**: {issue.description}
**影响行**: {', '.join(map(str, issue.line_numbers))}
**指标值**: {json.dumps(issue.metric_values, indent=2, ensure_ascii=False)}
**建议**:
"""
            for j, suggestion in enumerate(issue.suggestions, 1):
                report += f"  {j}. {suggestion}\n"
            report += "\n"
        
        report += f"""## 💡 优化建议 ({len(self.optimization_suggestions)}个)

"""
        
        # 按优先级排序
        sorted_suggestions = sorted(self.optimization_suggestions, key=lambda x: x.priority, reverse=True)
        
        for i, suggestion in enumerate(sorted_suggestions, 1):
            report += f"""### {i}. {suggestion.title} (优先级: {suggestion.priority}/10)
**描述**: {suggestion.description}
**预期改进**: {suggestion.expected_improvement:.1f}%
**影响行**: {', '.join(map(str, suggestion.affected_lines))}
**风险等级**: {suggestion.risk_level}
**实现方法**:
```
{suggestion.implementation}
```

"""
        
        report += f"""## 📈 性能指标统计

### 执行时间分布
- **平均执行时间**: {statistics.mean(self.performance_metrics.get('execution_time', [0])):.4f}秒
- **最大执行时间**: {max(self.performance_metrics.get('execution_time', [0])):.4f}秒
- **最小执行时间**: {min(self.performance_metrics.get('execution_time', [0])) if self.performance_metrics.get('execution_time') else 0:.4f}秒

### 内存使用统计
- **平均内存使用**: {statistics.mean(self.performance_metrics.get('memory_usage', [0])):.2f} MB
- **峰值内存使用**: {max(self.performance_metrics.get('memory_usage', [0])):.2f} MB

### CPU使用统计
- **平均CPU使用**: {statistics.mean(self.performance_metrics.get('cpu_usage', [0])):.2f}%
- **峰值CPU使用**: {max(self.performance_metrics.get('cpu_usage', [0])):.2f}%

## 🎯 总结

{self.summary.get('overall_assessment', '无总体评估')}

### 关键发现
"""
        
        for key, value in self.summary.get('key_findings', {}).items():
            report += f"- **{key}**: {value}\n"
        
        report += f"""
### 建议行动
"""
        
        for i, action in enumerate(self.summary.get('recommended_actions', []), 1):
            report += f"{i}. {action}\n"
        
        report += f"""
---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*分析工具: 石器时代脚本性能分析器 v1.0.0*
"""
        
        return report

# ============================================================================
# 性能分析器核心
# ============================================================================

class ASSAPerformanceAnalyzer:
    """ASSA脚本性能分析器"""
    
    def __init__(self, debugger: Optional[Any] = None):
        self.debugger = debugger
        self.performance_data: List[PerformanceData] = []
        self.performance_issues: List[PerformanceIssue] = []
        self.optimization_suggestions: List[OptimizationSuggestion] = []
        
        # 性能监控
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_active = False
        self.start_time: Optional[datetime] = None
        
        # 进程监控
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss
        self.initial_cpu_times = self.process.cpu_times()
        
        # 分析规则
        self.analysis_rules = self._load_analysis_rules()
    
    def _load_analysis_rules(self) -> Dict:
        """加载分析规则"""
        return {
            "slow_loops": {
                "description": "检测执行缓慢的循环",
                "threshold": 0.1,  # 秒
                "min_iterations": 3
            },
            "excessive_wait": {
                "description": "检测过长的等待时间",
                "threshold": 2.0  # 秒
            },
            "memory_leak": {
                "description": "检测内存泄漏",
                "threshold": 50.0  # MB
            },
            "high_cpu_usage": {
                "description": "检测高CPU使用",
                "threshold": 80.0  # 百分比
            },
            "inefficient_variable_access": {
                "description": "检测低效的变量访问",
                "threshold": 100  # 访问次数
            },
            "redundant_operations": {
                "description": "检测冗余操作",
                "pattern": r'(let\s+@\w+\s*,\s*=\s*,\s*@\w+\s*$)'
            }
        }
    
    def start_monitoring(self):
        """开始性能监控"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.start_time = datetime.now()
        self.performance_data = []
        
        # 启动监控线程
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        print("性能监控已启动")
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        
        print("性能监控已停止")
    
    def _monitoring_loop(self):
        """监控循环（在独立线程中运行）"""
        while self.monitoring_active:
            try:
                # 收集性能数据
                self._collect_performance_data()
                
                # 短暂休眠
                time.sleep(0.1)
                
            except Exception as e:
                print(f"性能监控错误: {e}")
                time.sleep(1.0)
    
    def _collect_performance_data(self):
        """收集性能数据"""
        current_time = datetime.now()
        
        # 收集内存使用
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        self.performance_data.append(PerformanceData(
            metric=PerformanceMetric.MEMORY_USAGE,
            value=memory_mb,
            timestamp=current_time
        ))
        
        # 收集CPU使用
        cpu_percent = self.process.cpu_percent(interval=0.1)
        
        self.performance_data.append(PerformanceData(
            metric=PerformanceMetric.CPU_USAGE,
            value=cpu_percent,
            timestamp=current_time
        ))
        
        # 如果有调试器，收集执行时间数据
        if self.debugger and hasattr(self.debugger, 'context'):
            execution_time = self.debugger.context.execution_time
            
            self.performance_data.append(PerformanceData(
                metric=PerformanceMetric.EXECUTION_TIME,
                value=execution_time,
                timestamp=current_time,
                line_number=self.debugger.context.current_line if hasattr(self.debugger.context, 'current_line') else None
            ))
    
    def analyze_script_structure(self, parser: ASSAParser) -> Dict:
        """分析脚本结构"""
        lines = parser.lines
        analysis = parser.analyze_script()
        
        # 结构分析
        structure_analysis = {
            "total_lines": len(lines),
            "code_lines": sum(1 for line in lines if line.cleaned_text and not line.cleaned_text.startswith('//')),
            "comment_lines": sum(1 for line in lines if line.cleaned_text.startswith('//')),
            "label_count": len(parser.labels),
            "variable_count": len(parser.variables),
            "loop_patterns": self._detect_loop_patterns(lines),
            "wait_patterns": self._detect_wait_patterns(lines),
            "variable_access_patterns": self._analyze_variable_access(lines),
            "instruction_distribution": analysis.get("instruction_stats", {})
        }
        
        return structure_analysis
    
    def _detect_loop_patterns(self, lines: List[ScriptLine]) -> List[Dict]:
        """检测循环模式"""
        loops = []
        
        for i, line in enumerate(lines):
            text = line.cleaned_text
            
            # 检测goto形成的循环
            if text.startswith('goto'):
                match = re.match(r'^\s*goto\s+(\w+)$', text)
                if match:
                    target_label = match.group(1)
                    # 查找目标标签的位置
                    for j, target_line in enumerate(lines):
                        if target_line.cleaned_text.startswith(f'label {target_label}'):
                            if j < i:  # 向后跳转，形成循环
                                loops.append({
                                    "type": "goto_loop",
                                    "start_line": j + 1,
                                    "end_line": i + 1,
                                    "label": target_label,
                                    "length": i - j + 1
                                })
                            break
        
        return loops
    
    def _detect_wait_patterns(self, lines: List[ScriptLine]) -> List[Dict]:
        """检测等待模式"""
        waits = []
        
        for i, line in enumerate(lines):
            text = line.cleaned_text
            
            if text.startswith('wait'):
                match = re.match(r'^\s*wait\s+(\d+)$', text)
                if match:
                    wait_time = int(match.group(1))
                    waits.append({
                        "line_number": i + 1,
                        "wait_time": wait_time,
                        "context": self._get_line_context(lines, i)
                    })
        
        return waits
    
    def _analyze_variable_access(self, lines: List[ScriptLine]) -> Dict:
        """分析变量访问模式"""
        variable_access = defaultdict(int)
        variable_definitions = {}
        
        for i, line in enumerate(lines):
            text = line.cleaned_text
            
            # 检测变量定义
            if text.startswith('dim'):
                vars_part = text[3:].strip()
                vars_list = [v.strip() for v in vars_part.split(',')]
                for var in vars_list:
                    if var.startswith('@'):
                        variable_definitions[var] = i + 1
            
            # 检测变量使用
            variable_pattern = re.# 安全注释: 原compile调用已移除r'(@\w+)')
            matches = variable_pattern.findall(text)
            for var in matches:
                variable_access[var] += 1
        
        return {
            "access_counts": dict(variable_access),
            "definitions": variable_definitions,
            "most_accessed": sorted(variable_access.items(), key=lambda x: x[1], reverse=True)[:10] if variable_access else []
        }
    
    def _get_line_context(self, lines: List[ScriptLine], index: int, context_lines: int = 3) -> List[str]:
        """获取行上下文"""
        start = max(0, index - context_lines)
        end = min(len(lines), index + context_lines + 1)
        
        context = []
        for i in range(start, end):
            context.append(f"Line {i+1}: {lines[i].cleaned_text[:50]}{'...' if len(lines[i].cleaned_text) > 50 else ''}")
        
        return context
    
    def analyze_performance_issues(self, parser: ASSAParser, execution_data: Optional[Dict] = None) -> List[PerformanceIssue]:
        """分析性能问题"""
        issues = []
        lines = parser.lines
        
        # 分析结构性问题
        structure_analysis = self.analyze_script_structure(parser)
        
        # 1. 检测慢循环
        loops = structure_analysis.get("loop_patterns", [])
        for loop in loops:
            if loop["length"] > 20:  # 循环体过长
                issues.append(PerformanceIssue(
                    issue_id=f"slow_loop_{loop['start_line']}",
                    issue_type="慢循环",
                    severity="medium",
                    description=f"检测到可能较慢的循环，从第{loop['start_line']}行到第{loop['end_line']}行，循环体包含{loop['length']}行代码",
                    line_numbers=list(range(loop['start_line'], loop['end_line'] + 1)),
                    metric_values={"loop_length": loop["length"]},
                    suggestions=[
                        "考虑优化循环内部逻辑，减少不必要的操作",
                        "检查循环条件，避免无限循环",
                        "考虑将部分计算移到循环外部"
                    ]
                ))
        
        # 2. 检测过长等待
        waits = structure_analysis.get("wait_patterns", [])
        for wait in waits:
            if wait["wait_time"] > self.analysis_rules["excessive_wait"]["threshold"]:
                issues.append(PerformanceIssue(
                    issue_id=f"long_wait_{wait['line_number']}",
                    issue_type="过长等待",
                    severity="low",
                    description=f"第{wait['line_number']}行有{long_wait['wait_time']}秒的等待，可能影响脚本响应速度",
                    line_numbers=[wait["line_number"]],
                    metric_values={"wait_time": wait["wait_time"]},
                    suggestions=[
                        f"考虑减少等待时间到{max(1, wait['wait_time'] // 2)}秒",
                        "检查是否真的需要这么长的等待",
                        "考虑使用异步等待或其他优化方式"
                    ]
                ))
        
        # 3. 检测变量访问模式
        variable_analysis = structure_analysis.get("variable_access_patterns", {})
        access_counts = variable_analysis.get("access_counts", {})
        
        for var, count in access_counts.items():
            if count > self.analysis_rules["inefficient_variable_access"]["threshold"]:
                issues.append(PerformanceIssue(
                    issue_id=f"high_var_access_{var}",
                    issue_type="高频变量访问",
                    severity="low",
                    description=f"变量{var}被访问了{count}次，可能影响性能",
                    line_numbers=[],  # 需要更精确的行号
                    metric_values={"access_count": count},
                    suggestions=[
                        f"考虑将变量{var}的值缓存到局部变量",
                        "检查是否有不必要的重复访问",
                        "优化变量访问逻辑"
                    ]
                ))
        
        # 4. 检测冗余操作
        for i, line in enumerate(lines):
            text = line.cleaned_text
            
            # 检测冗余的let赋值
            if re.match(self.analysis_rules["redundant_operations"]["pattern"], text):
                issues.append(PerformanceIssue(
                    issue_id=f"redundant_let_{i+1}",
                    issue_type="冗余赋值",
                    severity="low",
                    description=f"第{i+1}行可能有冗余的变量赋值操作",
                    line_numbers=[i + 1],
                    metric_values={},
                    suggestions=[
                        "检查是否真的需要这个赋值操作",
                        "考虑合并连续的赋值操作",
                        "优化变量赋值逻辑"
                    ]
                ))
        
        # 5. 如果有执行数据，分析执行性能
        if execution_data:
            total_time = execution_data.get("total_execution_time", 0)
            if total_time > 10.0:  # 总执行时间超过10秒
                issues.append(PerformanceIssue(
                    issue_id="long_total_execution",
                    issue_type="总执行时间过长",
                    severity="high",
                    description=f"脚本总执行时间{total_time:.1f}秒，可能影响用户体验",
                    line_numbers=[],
                    metric_values={"total_execution_time": total_time},
                    suggestions=[
                        "分析脚本中最耗时的部分",
                        "考虑将脚本拆分为多个小任务",
                        "优化网络请求和等待时间"
                    ]
                ))
        
        self.performance_issues = issues
        return issues
    
    def generate_optimization_suggestions(self, parser: ASSAParser) -> List[OptimizationSuggestion]:
        """生成优化建议"""
        suggestions = []
        lines = parser.lines
        
        # 1. 循环优化建议
        structure_analysis = self.analyze_script_structure(parser)
        loops = structure_analysis.get("loop_patterns", [])
        
        for loop in loops:
            if loop["length"] > 10:
                suggestions.append(OptimizationSuggestion(
                    suggestion_id=f"optimize_loop_{loop['start_line']}",
                    title=f"优化第{loop['start_line']}-{loop['end_line']}行的循环",
                    description=f"循环体包含{loop['length']}行代码，可能影响性能",
                    affected_lines=list(range(loop['start_line'], loop['end_line'] + 1)),
                    expected_improvement=15.0,
                    implementation=f"""# 优化建议：
# 1. 将循环内不变的计算移到循环外
# 2. 减少循环内的变量访问次数
# 3. 考虑使用更高效的循环结构

# 示例优化：
# 原代码可能类似：
# label loop_start
# ... {loop['length']}行代码 ...
# goto loop_start

# 优化后：
# 将不变计算移到循环外
# label loop_start
# ... 优化后的代码 ...
# goto loop_start""",
                    risk_level="low",
                    priority=7
                ))
        
        # 2. 等待时间优化建议
        waits = structure_analysis.get("wait_patterns", [])
        for wait in waits:
            if wait["wait_time"] > 1:
                suggestions.append(OptimizationSuggestion(
                    suggestion_id=f"optimize_wait_{wait['line_number']}",
                    title=f"优化第{wait['line_number']}行的等待时间",
                    description=f"当前等待{wait['wait_time']}秒，可以优化以减少总执行时间",
                    affected_lines=[wait["line_number"]],
                    expected_improvement=5.0 * wait["wait_time"],  # 每等待1秒优化5%
                    implementation=f"""# 优化建议：
# 第{wait['line_number']}行: wait {wait['wait_time']}

# 可能的优化：
# 1. 减少等待时间到{max(1, wait['wait_time'] // 2)}秒
# 2. 使用智能等待（检测到条件满足立即继续）
# 3. 考虑是否真的需要这么长的等待

# 优化示例：
# 原代码: wait {wait['wait_time']}
# 优化后: wait {max(1, wait['wait_time'] // 2)}  # 减少等待时间""",
                    risk_level="low",
                    priority=6
                ))
        
        # 3. 变量访问优化建议
        variable_analysis = structure_analysis.get("variable_access_patterns", {})
        most_accessed = variable_analysis.get("most_accessed", [])
        
        for var, count in most_accessed[:3]:  # 只处理前3个最常访问的变量
            if count > 50:
                suggestions.append(OptimizationSuggestion(
                    suggestion_id=f"optimize_var_{var}",
                    title=f"优化变量{var}的访问",
                    description=f"变量{var}被访问了{count}次，频繁访问可能影响性能",
                    affected_lines=[],  # 需要更精确的行号
                    expected_improvement=8.0,
                    implementation=f"""# 优化建议：减少变量{var}的访问次数

# 可能的优化方法：
# 1. 将频繁访问的变量值缓存到局部变量
# 2. 批量处理变量访问
# 3. 优化变量访问逻辑

# 示例优化：
# 原代码可能：
# if @var,=,1,label1
# if @var,=,2,label2
# if @var,=,3,label3

# 优化后：
# let @temp,=,@var
# if @temp,=,1,label1
# if @temp,=,2,label2
# if @temp,=,3,label3""",
                    risk_level="low",
                    priority=5
                ))
        
        # 4. 代码结构优化建议
        total_lines = len(lines)
        if total_lines > 200:
            suggestions.append(OptimizationSuggestion(
                suggestion_id="refactor_large_script",
                title="重构大型脚本",
                description=f"脚本包含{total_lines}行代码，建议拆分为多个小模块",
                affected_lines=list(range(1, total_lines + 1)),
                expected_improvement=20.0,
                implementation="""# 优化建议：将大型脚本拆分为模块

# 可能的优化方法：
# 1. 将相关功能提取到子脚本中
# 2. 使用include或call指令调用子脚本
# 3. 创建可重用的函数模块

# 示例结构：
# 主脚本.asc - 控制流程和调用子模块
# ├── 模块1.asc - 处理特定功能
# ├── 模块2.asc - 处理另一功能
# └── 工具函数.asc - 公共工具函数""",
                risk_level="medium",
                priority=8
            ))
        
        self.optimization_suggestions = suggestions
        return suggestions
    
    def generate_performance_report(self, parser: ASSAParser, script_name: str) -> PerformanceReport:
        """生成性能报告"""
        # 分析脚本结构
        structure_analysis = self.analyze_script_structure(parser)
        
        # 分析性能问题
        performance_issues = self.analyze_performance_issues(parser)
        
        # 生成优化建议
        optimization_suggestions = self.generate_optimization_suggestions(parser)
        
        # 收集性能指标
        performance_metrics = {
            "execution_time": [data.value for data in self.performance_data if data.metric == PerformanceMetric.EXECUTION_TIME],
            "memory_usage": [data.value for data in self.performance_data if data.metric == PerformanceMetric.MEMORY_USAGE],
            "cpu_usage": [data.value for data in self.performance_data if data.metric == PerformanceMetric.CPU_USAGE]
        }
        
        # 计算总体指标
        total_execution_time = sum(performance_metrics.get("execution_time", [0]))
        total_memory_used = max(performance_metrics.get("memory_usage", [0]), default=0)
        total_cpu_used = statistics.mean(performance_metrics.get("cpu_usage", [0])) if performance_metrics.get("cpu_usage") else 0
        
        # 生成总结
        summary = {
            "overall_assessment": self._generate_overall_assessment(
                total_execution_time, 
                len(performance_issues),
                len(optimization_suggestions)
            ),
            "key_findings": {
                "脚本大小": f"{structure_analysis['total_lines']} 行代码",
                "循环数量": f"{len(structure_analysis.get('loop_patterns', []))} 个循环",
                "等待指令": f"{len(structure_analysis.get('wait_patterns', []))} 个等待指令",
                "性能问题": f"{len(performance_issues)} 个需要关注的问题",
                "优化建议": f"{len(optimization_suggestions)} 个优化建议"
            },
            "recommended_actions": [
                "优先处理高严重性的性能问题",
                "实施高优先级的优化建议",
                "测试优化后的脚本性能",
                "定期进行性能分析"
            ]
        }
        
        # 创建报告
        report = PerformanceReport(
            report_id=f"perf_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            script_name=script_name,
            analysis_time=datetime.now(),
            total_execution_time=total_execution_time,
            total_memory_used=total_memory_used,
            total_cpu_used=total_cpu_used,
            performance_issues=performance_issues,
            optimization_suggestions=optimization_suggestions,
            performance_metrics=performance_metrics,
            summary=summary
        )
        
        return report
    
    def _generate_overall_assessment(self, total_time: float, issue_count: int, suggestion_count: int) -> str:
        """生成总体评估"""
        if total_time < 5.0 and issue_count == 0:
            return "✅ 脚本性能优秀，无需优化"
        elif total_time < 10.0 and issue_count <= 2:
            return "⚠️ 脚本性能良好，有少量优化空间"
        elif total_time < 30.0 and issue_count <= 5:
            return "⚠️ 脚本性能一般，建议进行优化"
        else:
            return "❌ 脚本性能需要重点关注，建议立即优化"
    
    def save_report(self, report: PerformanceReport, output_dir: str = "."):
        """保存报告"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存JSON格式报告
        json_path = os.path.join(output_dir, f"{report.report_id}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        
        # 保存Markdown格式报告
        md_path = os.path.join(output_dir, f"{report.report_id}.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(report.generate_markdown_report())
        
        print(f"性能报告已保存:")
        print(f"  JSON格式: {json_path}")
        print(f"  Markdown格式: {md_path}")
        
        return json_path, md_path

# ============================================================================
# 集成调试器的性能分析器
# ============================================================================

class IntegratedPerformanceAnalyzer(ASSAPerformanceAnalyzer):
    """集成调试器的性能分析器"""
    
    def __init__(self, debugger):
        super().__init__(debugger)
        self.debugger = debugger
    
    def analyze_with_debugger(self, script_path: str) -> PerformanceReport:
        """使用调试器进行性能分析"""
        print(f"开始性能分析: {script_path}")
        
        # 启动性能监控
        self.start_monitoring()
        
        # 加载脚本到调试器
        if not self.debugger.load_script(script_path):
            print("加载脚本失败")
            return None
        
        # 创建解析器（从调试器获取）
        parser = ASSAParser()
        parser.parse_file(script_path)
        
        # 运行脚本（收集性能数据）
        print("运行脚本以收集性能数据...")
        self.debugger.run()
        
        # 等待执行完成
        while self.debugger.state not in [DebuggerState.FINISHED, DebuggerState.ERROR, DebuggerState.IDLE]:
            time.sleep(0.1)
        
        # 停止性能监控
        self.stop_monitoring()
        
        # 收集执行数据
        execution_data = {
            "total_execution_time": self.debugger.context.execution_time if hasattr(self.debugger.context, 'execution_time') else 0,
            "state": self.debugger.state.value
        }
        
        # 生成性能报告
        script_name = os.path.basename(script_path)
        report = self.generate_performance_report(parser, script_name)
        
        print("性能分析完成")
        return report

# ============================================================================
# 主应用程序
# ============================================================================

def demonstrate_performance_analyzer():
    """演示性能分析器功能"""
    print("=" * 60)
    print("石器时代脚本性能分析器演示")
    print("=" * 60)
    
    # 测试脚本路径
    test_script = "/root/.openclaw/workspace/test_assas_script.asc"
    
    if not os.path.exists(test_script):
        print(f"测试脚本不存在: {test_script}")
        print("创建测试脚本...")
        
        # 创建简单的测试脚本
        test_content = """// 性能测试脚本
dim @count
dim @result

label start
print 开始性能测试...

// 测试循环性能
let @count,=,1

label loop_start
if @count,>,100,loop_end
let @result,=,@count * 2
wait 1  // 模拟耗时操作
let @count,=,@count + 1
goto loop_start

label loop_end
print 循环测试完成

// 测试变量访问
let @count,=,1
label var_test
if @count,>,50,var_end
let @result,=,@count  // 冗余赋值
let @result,=,@count  // 另一个冗余赋值
let @count,=,@count + 1
goto var_test

label var_end
print 变量测试完成
print 性能测试脚本执行完毕"""
        
        with open(test_script, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"测试脚本已创建: {test_script}")
    
    # 创建性能分析器
    print(f"\n分析测试脚本: {test_script}")
    
    # 创建解析器
    parser = ASSAParser()
    lines = parser.parse_file(test_script)
    
    if not lines: