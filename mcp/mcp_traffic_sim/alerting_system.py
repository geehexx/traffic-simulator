"""Alerting system for optimization monitoring and notifications."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .config import MCPConfig
from .logging_util import MCPLogger
from .security import SecurityManager


class AlertRule(BaseModel):
    """Alert rule configuration."""

    rule_id: str
    name: str
    description: str
    condition: str  # e.g., "quality_score < 0.7"
    threshold: float
    severity: str = "medium"  # low, medium, high, critical
    enabled: bool = True
    notification_channels: List[str] = Field(default_factory=lambda: ["dashboard", "logs"])
    cooldown_period: int = 300  # seconds
    last_triggered: Optional[float] = None


class Alert(BaseModel):
    """Alert instance."""

    alert_id: str
    rule_id: str
    severity: str
    message: str
    timestamp: float
    data: Dict[str, Any] = Field(default_factory=dict)
    status: str = "active"  # active, acknowledged, resolved
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[float] = None


class NotificationChannel(BaseModel):
    """Notification channel configuration."""

    channel_id: str
    name: str
    type: str  # dashboard, email, slack, webhook
    enabled: bool = True
    configuration: Dict[str, Any] = Field(default_factory=dict)


class AlertingSystem:
    """Alerting system for optimization monitoring."""

    def __init__(self, config: MCPConfig, logger: MCPLogger, security: SecurityManager):
        """Initialize alerting system."""
        self.config = config
        self.logger = logger
        self.security = security

        # Alert storage
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []

        # Notification channels
        self.notification_channels: Dict[str, NotificationChannel] = {}

        # Alert processing
        self.alert_queue: asyncio.Queue = asyncio.Queue()
        self.processing_tasks: List[asyncio.Task] = []

        # Initialize default rules and channels
        self._initialize_default_rules()
        self._initialize_default_channels()

        # Background processing will be started when needed
        self._background_processing_started = False

    def _initialize_default_rules(self):
        """Initialize default alert rules."""
        default_rules = [
            {
                "rule_id": "quality_drop",
                "name": "Quality Score Drop",
                "description": "Alert when quality score drops below 0.7",
                "condition": "quality_score < 0.7",
                "threshold": 0.7,
                "severity": "high",
                "notification_channels": ["dashboard", "logs"],
            },
            {
                "rule_id": "performance_degradation",
                "name": "Performance Degradation",
                "description": "Alert when execution time exceeds 5 minutes",
                "condition": "execution_time > 300",
                "threshold": 300,
                "severity": "medium",
                "notification_channels": ["dashboard", "logs"],
            },
            {
                "rule_id": "optimization_failure",
                "name": "Optimization Failure",
                "description": "Alert when optimization fails",
                "condition": "optimization_failed == true",
                "threshold": 1.0,
                "severity": "critical",
                "notification_channels": ["dashboard", "logs"],
            },
            {
                "rule_id": "high_error_rate",
                "name": "High Error Rate",
                "description": "Alert when error rate exceeds 20%",
                "condition": "error_rate > 0.2",
                "threshold": 0.2,
                "severity": "high",
                "notification_channels": ["dashboard", "logs"],
            },
            {
                "rule_id": "feedback_volume_spike",
                "name": "Feedback Volume Spike",
                "description": "Alert when feedback volume spikes significantly",
                "condition": "feedback_volume > 50",
                "threshold": 50,
                "severity": "medium",
                "notification_channels": ["dashboard"],
            },
        ]

        for rule_data in default_rules:
            rule = AlertRule(**rule_data)
            self.alert_rules[rule.rule_id] = rule

    def _initialize_default_channels(self):
        """Initialize default notification channels."""
        default_channels = [
            {
                "channel_id": "dashboard",
                "name": "Dashboard Notifications",
                "type": "dashboard",
                "enabled": True,
                "configuration": {"auto_display": True, "duration": 30},
            },
            {
                "channel_id": "logs",
                "name": "Log Notifications",
                "type": "logs",
                "enabled": True,
                "configuration": {"log_level": "WARNING"},
            },
        ]

        for channel_data in default_channels:
            channel = NotificationChannel(**channel_data)
            self.notification_channels[channel.channel_id] = channel

    def _start_background_processing(self):
        """Start background alert processing tasks."""
        # Start alert processor
        self.processing_tasks.append(asyncio.create_task(self._process_alert_queue()))

        # Start alert checker
        self.processing_tasks.append(asyncio.create_task(self._check_alert_conditions()))

        # Start alert cleanup
        self.processing_tasks.append(asyncio.create_task(self._cleanup_old_alerts()))

    async def configure_alerting(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Configure alerting rules and notification channels."""
        try:
            alert_types = arguments.get("alert_types", [])
            notification_channels = arguments.get("notification_channels", ["dashboard", "logs"])

            # Update alert rules
            for alert_type in alert_types:
                if "type" in alert_type and "threshold" in alert_type:
                    rule_id = alert_type["type"]
                    if rule_id in self.alert_rules:
                        self.alert_rules[rule_id].threshold = alert_type["threshold"]
                        self.alert_rules[rule_id].enabled = alert_type.get("enabled", True)
                        self.alert_rules[rule_id].notification_channels = notification_channels

            # Update notification channels
            for channel_id in notification_channels:
                if channel_id not in self.notification_channels:
                    # Create new channel
                    self.notification_channels[channel_id] = NotificationChannel(
                        channel_id=channel_id,
                        name=f"{channel_id.title()} Notifications",
                        type=channel_id,
                        enabled=True,
                    )
                else:
                    # Enable existing channel
                    self.notification_channels[channel_id].enabled = True

            return {
                "success": True,
                "alert_rules": len(self.alert_rules),
                "notification_channels": len(self.notification_channels),
                "enabled_rules": len([r for r in self.alert_rules.values() if r.enabled]),
                "enabled_channels": len(
                    [c for c in self.notification_channels.values() if c.enabled]
                ),
            }

        except Exception as e:
            return {"success": False, "error_message": str(e)}

    async def trigger_alert(self, rule_id: str, data: Dict[str, Any]) -> Optional[str]:
        """Trigger alert for specific rule."""
        # Start background processing if not already started
        if not self._background_processing_started:
            self._start_background_processing()
            self._background_processing_started = True

        if rule_id not in self.alert_rules:
            return None

        rule = self.alert_rules[rule_id]

        # Check if rule is enabled
        if not rule.enabled:
            return None

        # Check cooldown period
        if rule.last_triggered and time.time() - rule.last_triggered < rule.cooldown_period:
            return None

        # Create alert
        alert = Alert(
            alert_id=f"alert_{int(time.time())}_{len(self.active_alerts)}",
            rule_id=rule_id,
            severity=rule.severity,
            message=f"{rule.name}: {rule.description}",
            timestamp=time.time(),
            data=data,
        )

        # Store alert
        self.active_alerts[alert.alert_id] = alert
        self.alert_history.append(alert)

        # Update rule last triggered
        rule.last_triggered = time.time()

        # Add to processing queue
        await self.alert_queue.put(alert)

        self.logger.log_alert(
            {
                "alert_id": alert.alert_id,
                "rule_id": rule_id,
                "severity": rule.severity,
                "message": alert.message,
            }
        )

        return alert.alert_id

    async def _process_alert_queue(self):
        """Process alerts from queue."""
        while True:
            try:
                # Get alert from queue
                alert = await self.alert_queue.get()

                # Send notifications
                await self._send_notifications(alert)

                # Mark task as done
                self.alert_queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(f"Error processing alert: {e}")

    async def _send_notifications(self, alert: Alert):
        """Send notifications for alert."""
        rule = self.alert_rules[alert.rule_id]

        for channel_id in rule.notification_channels:
            if channel_id in self.notification_channels:
                channel = self.notification_channels[channel_id]
                if channel.enabled:
                    await self._send_notification_to_channel(alert, channel)

    async def _send_notification_to_channel(self, alert: Alert, channel: NotificationChannel):
        """Send notification to specific channel."""
        if channel.type == "dashboard":
            await self._send_dashboard_notification(alert, channel)
        elif channel.type == "logs":
            await self._send_log_notification(alert, channel)
        elif channel.type == "email":
            await self._send_email_notification(alert, channel)
        elif channel.type == "slack":
            await self._send_slack_notification(alert, channel)
        elif channel.type == "webhook":
            await self._send_webhook_notification(alert, channel)

    async def _send_dashboard_notification(self, alert: Alert, channel: NotificationChannel):
        """Send dashboard notification."""
        notification = {
            "type": "alert",
            "alert_id": alert.alert_id,
            "severity": alert.severity,
            "message": alert.message,
            "timestamp": alert.timestamp,
            "data": alert.data,
        }

        # Store notification for dashboard display
        self.logger.log_dashboard_notification(notification)

    async def _send_log_notification(self, alert: Alert, channel: NotificationChannel):
        """Send log notification."""
        log_level = channel.configuration.get("log_level", "WARNING")

        if log_level == "ERROR":
            self.logger.log_error(f"ALERT [{alert.severity.upper()}]: {alert.message}")
        elif log_level == "WARNING":
            self.logger.log_warning(f"ALERT [{alert.severity.upper()}]: {alert.message}")
        else:
            self.logger.log_info(f"ALERT [{alert.severity.upper()}]: {alert.message}")

    async def _send_email_notification(self, alert: Alert, channel: NotificationChannel):
        """Send email notification."""
        # In real implementation, this would send actual email
        self.logger.log_info(f"Email notification sent for alert {alert.alert_id}")

    async def _send_slack_notification(self, alert: Alert, channel: NotificationChannel):
        """Send Slack notification."""
        # In real implementation, this would send to Slack
        self.logger.log_info(f"Slack notification sent for alert {alert.alert_id}")

    async def _send_webhook_notification(self, alert: Alert, channel: NotificationChannel):
        """Send webhook notification."""
        # In real implementation, this would send HTTP request
        self.logger.log_info(f"Webhook notification sent for alert {alert.alert_id}")

    async def _check_alert_conditions(self):
        """Check alert conditions periodically."""
        while True:
            try:
                # Check each enabled rule
                for rule_id, rule in self.alert_rules.items():
                    if rule.enabled:
                        await self._evaluate_rule_condition(rule_id, rule)

                # Wait before next check
                await asyncio.sleep(60)  # Check every minute

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(f"Error checking alert conditions: {e}")

    async def _evaluate_rule_condition(self, rule_id: str, rule: AlertRule):
        """Evaluate specific rule condition."""
        # Get current system metrics
        metrics = await self._get_current_metrics()

        # Evaluate condition
        condition_met = await self._evaluate_condition(rule.condition, metrics)

        if condition_met:
            await self.trigger_alert(rule_id, metrics)

    async def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        # In real implementation, this would get actual metrics
        return {
            "quality_score": 0.75,
            "execution_time": 120,
            "optimization_failed": False,
            "error_rate": 0.05,
            "feedback_volume": 25,
            "timestamp": time.time(),
        }

    async def _evaluate_condition(self, condition: str, metrics: Dict[str, Any]) -> bool:
        """Evaluate alert condition."""
        # Simple condition evaluation (in real implementation, use proper expression evaluator)
        try:
            # Replace variables with actual values
            eval_condition = condition
            for key, value in metrics.items():
                eval_condition = eval_condition.replace(key, str(value))

            # Evaluate condition
            return eval(eval_condition)
        except Exception:
            return False

    async def _cleanup_old_alerts(self):
        """Clean up old alerts."""
        while True:
            try:
                # Remove alerts older than 7 days
                cutoff_time = time.time() - (7 * 24 * 3600)

                # Remove from active alerts
                old_active_alerts = [
                    alert_id
                    for alert_id, alert in self.active_alerts.items()
                    if alert.timestamp < cutoff_time
                ]
                for alert_id in old_active_alerts:
                    del self.active_alerts[alert_id]

                # Remove from history
                self.alert_history = [
                    alert for alert in self.alert_history if alert.timestamp >= cutoff_time
                ]

                # Wait before next cleanup
                await asyncio.sleep(3600)  # Every hour

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(f"Error cleaning up old alerts: {e}")

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> Dict[str, Any]:
        """Acknowledge an alert."""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = "acknowledged"
                alert.acknowledged_by = acknowledged_by

                return {
                    "success": True,
                    "alert_id": alert_id,
                    "status": "acknowledged",
                    "acknowledged_by": acknowledged_by,
                }
            else:
                return {"success": False, "error": "Alert not found"}

        except Exception as e:
            return {"success": False, "error_message": str(e)}

    async def resolve_alert(self, alert_id: str, resolved_by: str) -> Dict[str, Any]:
        """Resolve an alert."""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = "resolved"
                alert.resolved_at = time.time()

                # Remove from active alerts
                del self.active_alerts[alert_id]

                return {
                    "success": True,
                    "alert_id": alert_id,
                    "status": "resolved",
                    "resolved_by": resolved_by,
                    "resolved_at": alert.resolved_at,
                }
            else:
                return {"success": False, "error": "Alert not found"}

        except Exception as e:
            return {"success": False, "error_message": str(e)}

    async def get_active_alerts(self) -> Dict[str, Any]:
        """Get all active alerts."""
        return {
            "success": True,
            "active_alerts": [
                {
                    "alert_id": alert.alert_id,
                    "rule_id": alert.rule_id,
                    "severity": alert.severity,
                    "message": alert.message,
                    "timestamp": alert.timestamp,
                    "status": alert.status,
                    "acknowledged_by": alert.acknowledged_by,
                }
                for alert in self.active_alerts.values()
            ],
            "total_count": len(self.active_alerts),
        }

    async def get_alert_history(self, time_range: str = "24h") -> Dict[str, Any]:
        """Get alert history for specified time range."""
        try:
            # Calculate time boundaries
            now = time.time()
            if time_range == "1h":
                start_time = now - 3600
            elif time_range == "24h":
                start_time = now - 86400
            elif time_range == "7d":
                start_time = now - (7 * 86400)
            elif time_range == "30d":
                start_time = now - (30 * 86400)
            else:
                start_time = now - 86400  # Default to 24h

            # Filter alerts by time range
            filtered_alerts = [
                alert for alert in self.alert_history if start_time <= alert.timestamp <= now
            ]

            # Calculate statistics
            severity_counts = {}
            for alert in filtered_alerts:
                severity_counts[alert.severity] = severity_counts.get(alert.severity, 0) + 1

            return {
                "success": True,
                "time_range": time_range,
                "total_alerts": len(filtered_alerts),
                "severity_distribution": severity_counts,
                "alerts": [
                    {
                        "alert_id": alert.alert_id,
                        "rule_id": alert.rule_id,
                        "severity": alert.severity,
                        "message": alert.message,
                        "timestamp": alert.timestamp,
                        "status": alert.status,
                    }
                    for alert in filtered_alerts
                ],
            }

        except Exception as e:
            return {"success": False, "error_message": str(e)}

    async def shutdown(self):
        """Shutdown alerting system."""
        # Cancel all processing tasks
        for task in self.processing_tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self.processing_tasks, return_exceptions=True)

        self.logger.log_info("Alerting system shutdown complete")
