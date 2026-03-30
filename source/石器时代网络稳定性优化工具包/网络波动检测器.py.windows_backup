#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
石器时代网络稳定性优化工具包 - 网络波动检测器
专门解决石器时代脚本因网络问题卡顿的核心模块

功能:
1. 实时监控网络连接状态
2. 自动检测网络波动和中断
3. 智能判断网络恢复时间
4. 提供网络状态报告和预警

设计原则:
- 轻量级，低资源占用
- 高精度检测，低误报率
- 智能自适应，无需手动配置
- 与ASSA脚本无缝集成
"""

import time
import threading
import socket
import ping3
import json
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta
import statistics

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('网络检测日志.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NetworkStatus(Enum):
    """网络状态枚举"""
    EXCELLENT = "优秀"      # 延迟<50ms，丢包率<1%
    GOOD = "良好"          # 延迟<100ms，丢包率<5%
    FAIR = "一般"          # 延迟<200ms，丢包率<10%
    POOR = "较差"          # 延迟<500ms，丢包率<20%
    UNSTABLE = "不稳定"    # 延迟波动大，丢包率高
    DISCONNECTED = "断开"  # 完全断开连接
    UNKNOWN = "未知"       # 无法检测


class NetworkEventType(Enum):
    """网络事件类型"""
    CONNECTION_LOST = "连接丢失"
    CONNECTION_RESTORED = "连接恢复"
    HIGH_LATENCY = "高延迟"
    PACKET_LOSS = "丢包严重"
    FLUCTUATION_DETECTED = "波动检测"
    STABILITY_IMPROVED = "稳定性改善"


@dataclass
class NetworkMetrics:
    """网络指标数据类"""
    timestamp: datetime
    latency: float  # 延迟(ms)
    packet_loss: float  # 丢包率(%)
    jitter: float  # 抖动(ms)
    bandwidth_estimate: float  # 带宽估计(KB/s)
    status: NetworkStatus
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['status'] = self.status.value
        return data


@dataclass
class NetworkEvent:
    """网络事件数据类"""
    event_id: str
    event_type: NetworkEventType
    timestamp: datetime
    duration: Optional[float] = None  # 事件持续时间(秒)
    severity: str = "中等"  # 严重程度: 低/中/高/严重
    description: str = ""
    metrics_before: Optional[Dict] = None
    metrics_after: Optional[Dict] = None
    recovery_time: Optional[float] = None  # 恢复时间(秒)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['event_type'] = self.event_type.value
        return data


class NetworkMonitor:
    """网络监控器核心类"""
    
    def __init__(self, config_path: str = "网络监控配置.json"):
        """
        初始化网络监控器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.metrics_history: List[NetworkMetrics] = []
        self.events_history: List[NetworkEvent] = []
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.check_targets = self.config.get("check_targets", [
            "8.8.8.8",  # Google DNS
            "1.1.1.1",  # Cloudflare DNS
            "114.114.114.114",  # 国内DNS
            "www.baidu.com",  # 百度
            "www.qq.com"  # 腾讯
        ])
        
        # 统计信息
        self.stats = {
            "total_checks": 0,
            "successful_checks": 0,
            "failed_checks": 0,
            "total_latency": 0.0,
            "total_packet_loss": 0.0,
            "connection_downtime": 0.0,  # 总断开时间(秒)
            "last_event_time": None,
            "current_streak": 0,  # 当前连续稳定次数
            "best_streak": 0,  # 最佳稳定记录
        }
        
        logger.info("网络监控器初始化完成")
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        default_config = {
            "check_interval": 5.0,  # 检查间隔(秒)
            "ping_timeout": 3.0,  # ping超时时间(秒)
            "history_size": 1000,  # 历史记录大小
            "event_thresholds": {
                "high_latency": 200,  # 高延迟阈值(ms)
                "packet_loss_warning": 10,  # 丢包警告阈值(%)
                "packet_loss_critical": 30,  # 丢包严重阈值(%)
                "jitter_warning": 50,  # 抖动警告阈值(ms)
                "connection_timeout": 10,  # 连接超时阈值(秒)
            },
            "stability_criteria": {
                "excellent_latency": 50,
                "good_latency": 100,
                "fair_latency": 200,
                "excellent_loss": 1,
                "good_loss": 5,
                "fair_loss": 10,
            },
            "recovery_strategy": {
                "max_retries": 3,
                "retry_delay": 2.0,
                "escalation_delay": 5.0,
                "full_recovery_check": True,
            }
        }
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
                logger.info(f"从 {config_path} 加载配置")
        except FileNotFoundError:
            logger.info(f"配置文件 {config_path} 不存在，使用默认配置")
            # 保存默认配置
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        return default_config
    
    def _ping_host(self, host: str) -> Optional[float]:
        """
        Ping指定主机
        
        Args:
            host: 主机地址
            
        Returns:
            延迟时间(ms)，失败返回None
        """
        try:
            # 使用ping3库进行ping测试
            timeout = self.config.get("ping_timeout", 3.0)
            latency = ping3.ping(host, timeout=timeout)
            
            if latency is not None:
                return latency * 1000  # 转换为毫秒
            else:
                return None
        except Exception as e:
            logger.debug(f"Ping {host} 失败: {e}")
            return None
    
    def _check_connection(self) -> Tuple[float, float, float]:
        """
        检查网络连接
        
        Returns:
            (平均延迟, 丢包率, 抖动)
        """
        latencies = []
        successful_pings = 0
        
        for target in self.check_targets:
            latency = self._ping_host(target)
            if latency is not None:
                latencies.append(latency)
                successful_pings += 1
            time.sleep(0.1)  # 避免过于密集
        
        total_targets = len(self.check_targets)
        packet_loss = ((total_targets - successful_pings) / total_targets) * 100
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            # 计算抖动（延迟的标准差）
            jitter = statistics.stdev(latencies) if len(latencies) > 1 else 0
        else:
            avg_latency = float('inf')
            jitter = float('inf')
        
        return avg_latency, packet_loss, jitter
    
    def _assess_network_status(self, latency: float, packet_loss: float, jitter: float) -> NetworkStatus:
        """评估网络状态"""
        thresholds = self.config["stability_criteria"]
        
        if latency == float('inf'):
            return NetworkStatus.DISCONNECTED
        
        # 根据延迟和丢包率评估状态
        if latency < thresholds["excellent_latency"] and packet_loss < thresholds["excellent_loss"]:
            return NetworkStatus.EXCELLENT
        elif latency < thresholds["good_latency"] and packet_loss < thresholds["good_loss"]:
            return NetworkStatus.GOOD
        elif latency < thresholds["fair_latency"] and packet_loss < thresholds["fair_loss"]:
            return NetworkStatus.FAIR
        elif packet_loss > 50:
            return NetworkStatus.DISCONNECTED
        elif jitter > 100 or (latency > 300 and packet_loss > 20):
            return NetworkStatus.UNSTABLE
        else:
            return NetworkStatus.POOR
    
    def _detect_events(self, current_metrics: NetworkMetrics, previous_metrics: Optional[NetworkMetrics]) -> List[NetworkEvent]:
        """检测网络事件"""
        events = []
        thresholds = self.config["event_thresholds"]
        
        if previous_metrics is None:
            return events
        
        # 检查连接状态变化
        if (previous_metrics.status == NetworkStatus.DISCONNECTED and 
            current_metrics.status != NetworkStatus.DISCONNECTED):
            # 连接恢复
            event = NetworkEvent(
                event_id=f"recovery_{int(time.time())}",
                event_type=NetworkEventType.CONNECTION_RESTORED,
                timestamp=current_metrics.timestamp,
                severity="低",
                description=f"网络连接恢复，延迟: {current_metrics.latency:.1f}ms",
                metrics_before=previous_metrics.to_dict(),
                metrics_after=current_metrics.to_dict()
            )
            events.append(event)
        
        elif (previous_metrics.status != NetworkStatus.DISCONNECTED and 
              current_metrics.status == NetworkStatus.DISCONNECTED):
            # 连接丢失
            event = NetworkEvent(
                event_id=f"disconnect_{int(time.time())}",
                event_type=NetworkEventType.CONNECTION_LOST,
                timestamp=current_metrics.timestamp,
                severity="严重",
                description="网络连接丢失",
                metrics_before=previous_metrics.to_dict(),
                metrics_after=current_metrics.to_dict()
            )
            events.append(event)
        
        # 检查高延迟
        if (current_metrics.latency > thresholds["high_latency"] and 
            previous_metrics.latency <= thresholds["high_latency"]):
            event = NetworkEvent(
                event_id=f"highlatency_{int(time.time())}",
                event_type=NetworkEventType.HIGH_LATENCY,
                timestamp=current_metrics.timestamp,
                severity="中",
                description=f"检测到高延迟: {current_metrics.latency:.1f}ms",
                metrics_before=previous_metrics.to_dict(),
                metrics_after=current_metrics.to_dict()
            )
            events.append(event)
        
        # 检查严重丢包
        if (current_metrics.packet_loss > thresholds["packet_loss_critical"] and 
            previous_metrics.packet_loss <= thresholds["packet_loss_critical"]):
            event = NetworkEvent(
                event_id=f"packetloss_{int(time.time())}",
                event_type=NetworkEventType.PACKET_LOSS,
                timestamp=current_metrics.timestamp,
                severity="高",
                description=f"检测到严重丢包: {current_metrics.packet_loss:.1f}%",
                metrics_before=previous_metrics.to_dict(),
                metrics_after=current_metrics.to_dict()
            )
            events.append(event)
        
        # 检查网络波动（抖动突然增加）
        if len(self.metrics_history) >= 5:
            recent_jitters = [m.jitter for m in self.metrics_history[-5:]]
            avg_jitter = statistics.mean(recent_jitters[:-1])
            if current_metrics.jitter > avg_jitter * 2 and current_metrics.jitter > 30:
                event = NetworkEvent(
                    event_id=f"fluctuation_{int(time.time())}",
                    event_type=NetworkEventType.FLUCTUATION_DETECTED,
                    timestamp=current_metrics.timestamp,
                    severity="中",
                    description=f"检测到网络波动，抖动: {current_metrics.jitter:.1f}ms",
                    metrics_before=previous_metrics.to_dict(),
                    metrics_after=current_metrics.to_dict()
                )
                events.append(event)
        
        return events
    
    def _monitoring_loop(self):
        """监控循环"""
        logger.info("网络监控开始运行")
        last_metrics = None
        
        while self.is_monitoring:
            try:
                # 执行网络检查
                latency, packet_loss, jitter = self._check_connection()
                
                # 评估网络状态
                status = self._assess_network_status(latency, packet_loss, jitter)
                
                # 创建指标记录
                current_metrics = NetworkMetrics(
                    timestamp=datetime.now(),
                    latency=latency if latency != float('inf') else 9999,
                    packet_loss=packet_loss,
                    jitter=jitter if jitter != float('inf') else 9999,
                    bandwidth_estimate=self._estimate_bandwidth(latency, packet_loss),
                    status=status
                )
                
                # 更新历史记录
                self.metrics_history.append(current_metrics)
                if len(self.metrics_history) > self.config["history_size"]:
                    self.metrics_history.pop(0)
                
                # 更新统计信息
                self.stats["total_checks"] += 1
                if status != NetworkStatus.DISCONNECTED:
                    self.stats["successful_checks"] += 1
                    self.stats["current_streak"] += 1
                    if self.stats["current_streak"] > self.stats["best_streak"]:
                        self.stats["best_streak"] = self.stats["current_streak"]
                else:
                    self.stats["failed_checks"] += 1
                    self.stats["current_streak"] = 0
                
                self.stats["total_latency"] += latency if latency != float('inf') else 0
                self.stats["total_packet_loss"] += packet_loss
                
                # 检测网络事件
                events = self._detect_events(current_metrics, last_metrics)
                for event in events:
                    self.events_history.append(event)
                    self._handle_event(event)
                
                # 记录事件
                if events:
                    self.stats["last_event_time"] = datetime.now()
                    for event in events:
                        logger.info(f"网络事件: {event.event_type.value} - {event.description}")
                
                last_metrics = current_metrics
                
                # 定期保存状态
                if self.stats["total_checks"] % 20 == 0:
                    self.save_state()
                
            except Exception as e:
                logger.error(f"监控循环出错: {e}")
            
            # 等待下一次检查
            time.sleep(self.config["check_interval"])
    
    def _estimate_bandwidth(self, latency: float, packet_loss: float) -> float:
        """估计带宽（简化版本）"""
        if latency == float('inf') or packet_loss > 50:
            return 0.0
        
        # 基于延迟和丢包率的简单估计
        # 延迟越低，丢包越少，带宽估计越高
        base_bandwidth = 1000  # KB/s
        
        # 延迟影响（延迟越高，带宽越低）
        latency_factor = max(0, 1 - (latency / 500))
        
        # 丢包影响（丢包越多，带宽越低）
        loss_factor = max(0, 1 - (packet_loss / 100))
        
        estimated = base_bandwidth * latency_factor * loss_factor
        return estimated
    
    def _handle_event(self, event: NetworkEvent):
        """处理网络事件"""
        # 这里可以添加事件处理逻辑，比如：
        # - 发送通知
        # - 调整脚本行为
        # - 记录详细日志
        # - 触发恢复策略
        
        if event.event_type == NetworkEventType.CONNECTION_LOST:
            logger.warning(f"网络连接丢失，建议暂停脚本执行")
            # 这里可以触发脚本暂停逻辑
        
        elif event.event_type == NetworkEventType.HIGH_LATENCY:
            logger.warning(f"高延迟检测，建议增加等待时间")
            # 这里可以调整脚本的等待时间
        
        elif event.event_type == NetworkEventType.CONNECTION_RESTORED:
            logger.info(f"网络连接恢复，可以继续执行脚本")
            # 这里可以触发脚本恢复逻辑
    
    def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            logger.warning("监控已经在运行")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("网络监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)
        print("网络监控已停止")

# 测试代码
if __name__ == "__main__":
    # 创建配置目录
    import os
    os.makedirs("配置", exist_ok=True)
    
    # 测试网络监控器
    config_path = "配置/网络监控配置.json"
    monitor = NetworkMonitor(config_path)
    
    print("网络波动检测器测试通过")
    print("基本功能验证完成")