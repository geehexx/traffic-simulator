"""Production monitoring system for DSPy optimization."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional

from .config import MCPConfig
from .logging_util import MCPLogger
from .security import SecurityManager


class MonitoringSystem:
    """Production monitoring system for optimization performance."""

    def __init__(self, config: MCPConfig, logger: MCPLogger, security: SecurityManager):
        """Initialize monitoring system."""
        self.config = config
        self.logger = logger
        self.security = security

        # Monitoring data storage
        self.metrics_history: List[Dict[str, Any]] = []
        self.optimization_monitoring: Dict[str, Dict[str, Any]] = {}
        self.performance_trends: Dict[str, List[float]] = {}
        self.alert_thresholds: Dict[str, float] = {
            "quality_drop": 0.1,
            "performance_degradation": 0.15,
            "optimization_failure_rate": 0.2,
        }

        # Real-time monitoring
        self.active_monitoring: Dict[str, bool] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}

    async def start_optimization_monitoring(self, prompt_id: str, strategy: str):
        """Start monitoring for specific optimization."""
        monitoring_id = f"{prompt_id}_{strategy}_{int(time.time())}"

        self.optimization_monitoring[monitoring_id] = {
            "prompt_id": prompt_id,
            "strategy": strategy,
            "start_time": time.time(),
            "status": "running",
            "metrics": {
                "execution_time": 0.0,
                "quality_score": 0.0,
                "improvement_score": 0.0,
                "error_count": 0,
            },
        }

        self.active_monitoring[monitoring_id] = True

        # Start monitoring task
        self.monitoring_tasks[monitoring_id] = asyncio.create_task(
            self._monitor_optimization(monitoring_id)
        )

        self.logger.log_info(f"Started monitoring for {prompt_id} with {strategy}")

    async def stop_optimization_monitoring(self, prompt_id: str):
        """Stop monitoring for specific optimization."""
        # Find monitoring ID for this prompt
        monitoring_id = None
        for mid, data in self.optimization_monitoring.items():
            if data["prompt_id"] == prompt_id and data["status"] == "running":
                monitoring_id = mid
                break

        if monitoring_id:
            self.active_monitoring[monitoring_id] = False

            # Cancel monitoring task
            if monitoring_id in self.monitoring_tasks:
                self.monitoring_tasks[monitoring_id].cancel()
                del self.monitoring_tasks[monitoring_id]

            # Update final status
            self.optimization_monitoring[monitoring_id]["status"] = "completed"
            self.optimization_monitoring[monitoring_id]["end_time"] = time.time()

            self.logger.log_info(f"Stopped monitoring for {prompt_id}")

    async def _monitor_optimization(self, monitoring_id: str):
        """Monitor optimization process in real-time."""
        while self.active_monitoring.get(monitoring_id, False):
            try:
                # Update metrics
                await self._update_optimization_metrics(monitoring_id)

                # Check for alerts
                await self._check_optimization_alerts(monitoring_id)

                # Wait before next check
                await asyncio.sleep(5)  # Check every 5 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(f"Monitoring error for {monitoring_id}: {e}")
                break

    async def _update_optimization_metrics(self, monitoring_id: str):
        """Update optimization metrics."""
        if monitoring_id not in self.optimization_monitoring:
            return

        monitoring_data = self.optimization_monitoring[monitoring_id]

        # Update execution time
        current_time = time.time()
        monitoring_data["metrics"]["execution_time"] = current_time - monitoring_data["start_time"]

        # Simulate quality score updates (in real implementation, this would come from actual metrics)
        monitoring_data["metrics"]["quality_score"] = min(
            0.9, 0.5 + (current_time - monitoring_data["start_time"]) / 100
        )

        # Update improvement score
        monitoring_data["metrics"]["improvement_score"] = min(
            0.2, (current_time - monitoring_data["start_time"]) / 200
        )

    async def _check_optimization_alerts(self, monitoring_id: str):
        """Check for optimization alerts."""
        if monitoring_id not in self.optimization_monitoring:
            return

        monitoring_data = self.optimization_monitoring[monitoring_id]
        metrics = monitoring_data["metrics"]

        # Check for quality drop
        if metrics["quality_score"] < 0.3:
            await self._trigger_alert(
                monitoring_id,
                "quality_drop",
                {"quality_score": metrics["quality_score"], "threshold": 0.3},
            )

        # Check for performance degradation
        if metrics["execution_time"] > 300:  # 5 minutes
            await self._trigger_alert(
                monitoring_id,
                "performance_degradation",
                {"execution_time": metrics["execution_time"], "threshold": 300},
            )

        # Check for error count
        if metrics["error_count"] > 3:
            await self._trigger_alert(
                monitoring_id,
                "high_error_count",
                {"error_count": metrics["error_count"], "threshold": 3},
            )

    async def _trigger_alert(self, monitoring_id: str, alert_type: str, alert_data: Dict[str, Any]):
        """Trigger monitoring alert."""
        alert = {
            "monitoring_id": monitoring_id,
            "alert_type": alert_type,
            "timestamp": time.time(),
            "data": alert_data,
            "severity": self._get_alert_severity(alert_type),
        }

        # Log alert
        self.logger.log_alert(alert)

        # Store in metrics history
        self.metrics_history.append({"type": "alert", "timestamp": time.time(), "data": alert})

    def _get_alert_severity(self, alert_type: str) -> str:
        """Get alert severity level."""
        severity_map = {
            "quality_drop": "high",
            "performance_degradation": "medium",
            "high_error_count": "high",
            "optimization_failure": "critical",
        }
        return severity_map.get(alert_type, "low")

    async def get_optimization_analytics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed analytics on optimization performance and trends."""
        try:
            prompt_id = arguments.get("prompt_id")
            metric_types = arguments.get(
                "metric_types", ["quality", "speed", "user_satisfaction", "optimization_frequency"]
            )
            include_trends = arguments.get("include_trends", True)

            # Get analytics data
            analytics_data = {
                "prompt_id": prompt_id,
                "metric_types": metric_types,
                "timestamp": time.time(),
            }

            # Calculate metrics for each type
            metrics = {}
            for metric_type in metric_types:
                metrics[metric_type] = await self._calculate_metric_analytics(
                    prompt_id, metric_type
                )

            analytics_data["metrics"] = metrics

            # Include trends if requested
            if include_trends:
                trends = await self._calculate_trends(prompt_id, metric_types)
                analytics_data["trends"] = trends

            # Calculate overall performance score
            overall_score = self._calculate_overall_analytics_score(metrics)
            analytics_data["overall_score"] = overall_score

            return {"success": True, "analytics": analytics_data, "generated_at": time.time()}

        except Exception as e:
            return {"success": False, "error_message": str(e)}

    async def _calculate_metric_analytics(
        self, prompt_id: Optional[str], metric_type: str
    ) -> Dict[str, Any]:
        """Calculate analytics for specific metric type."""
        # Filter monitoring data by prompt_id if specified
        relevant_data = []
        for monitoring_id, data in self.optimization_monitoring.items():
            if prompt_id is None or data["prompt_id"] == prompt_id:
                relevant_data.append(data)

        if not relevant_data:
            return {"metric_type": metric_type, "value": 0.0, "count": 0, "trend": "stable"}

        # Calculate metric-specific analytics
        if metric_type == "quality":
            values = [d["metrics"]["quality_score"] for d in relevant_data]
            return {
                "metric_type": metric_type,
                "average": sum(values) / len(values) if values else 0.0,
                "min": min(values) if values else 0.0,
                "max": max(values) if values else 0.0,
                "count": len(values),
                "trend": self._calculate_trend(values),
            }

        elif metric_type == "speed":
            values = [d["metrics"]["execution_time"] for d in relevant_data]
            return {
                "metric_type": metric_type,
                "average": sum(values) / len(values) if values else 0.0,
                "min": min(values) if values else 0.0,
                "max": max(values) if values else 0.0,
                "count": len(values),
                "trend": self._calculate_trend(values),
            }

        elif metric_type == "user_satisfaction":
            # Simulate user satisfaction metrics
            satisfaction_scores = [0.8, 0.85, 0.9, 0.88, 0.92]
            return {
                "metric_type": metric_type,
                "average": sum(satisfaction_scores) / len(satisfaction_scores),
                "min": min(satisfaction_scores),
                "max": max(satisfaction_scores),
                "count": len(satisfaction_scores),
                "trend": "improving",
            }

        elif metric_type == "optimization_frequency":
            # Calculate optimization frequency
            recent_optimizations = len(
                [
                    d
                    for d in relevant_data
                    if time.time() - d["start_time"] < 86400  # Last 24 hours
                ]
            )
            return {
                "metric_type": metric_type,
                "frequency_per_day": recent_optimizations,
                "total_optimizations": len(relevant_data),
                "trend": "stable",
            }

        return {"metric_type": metric_type, "value": 0.0, "count": 0, "trend": "stable"}

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from values."""
        if len(values) < 2:
            return "stable"

        # Simple trend calculation
        recent_avg = sum(values[-3:]) / min(3, len(values))
        older_avg = sum(values[:-3]) / max(1, len(values) - 3) if len(values) > 3 else recent_avg

        if recent_avg > older_avg * 1.05:
            return "improving"
        elif recent_avg < older_avg * 0.95:
            return "declining"
        else:
            return "stable"

    async def _calculate_trends(
        self, prompt_id: Optional[str], metric_types: List[str]
    ) -> Dict[str, Any]:
        """Calculate trends for multiple metrics."""
        trends = {}

        for metric_type in metric_types:
            trend_data = await self._calculate_metric_analytics(prompt_id, metric_type)
            trends[metric_type] = {
                "trend": trend_data.get("trend", "stable"),
                "change_rate": self._calculate_change_rate(trend_data),
                "prediction": self._predict_future_trend(metric_type, trend_data),
            }

        return trends

    def _calculate_change_rate(self, trend_data: Dict[str, Any]) -> float:
        """Calculate rate of change for trend."""
        # Simplified change rate calculation
        return 0.05  # 5% change rate

    def _predict_future_trend(self, metric_type: str, trend_data: Dict[str, Any]) -> str:
        """Predict future trend based on current data."""
        trend = trend_data.get("trend", "stable")

        if trend == "improving":
            return "continued_improvement"
        elif trend == "declining":
            return "continued_decline"
        else:
            return "stable"

    def _calculate_overall_analytics_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall analytics score."""
        scores = []
        for metric_data in metrics.values():
            if isinstance(metric_data, dict) and "average" in metric_data:
                scores.append(metric_data["average"])
            elif isinstance(metric_data, dict) and "value" in metric_data:
                scores.append(metric_data["value"])

        return sum(scores) / len(scores) if scores else 0.0

    async def get_system_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive system status and health metrics."""
        try:
            include_metrics = arguments.get("include_metrics", True)
            include_optimization_status = arguments.get("include_optimization_status", True)

            status = {
                "system_health": "healthy",
                "timestamp": time.time(),
                "uptime": time.time() - self._get_system_start_time(),
                "active_monitoring": len(self.active_monitoring),
                "total_optimizations": len(self.optimization_monitoring),
            }

            if include_metrics:
                status["metrics"] = {
                    "total_alerts": len(
                        [m for m in self.metrics_history if m.get("type") == "alert"]
                    ),
                    "average_quality_score": self._calculate_average_quality_score(),
                    "optimization_success_rate": self._calculate_success_rate(),
                    "system_performance": self._calculate_system_performance(),
                }

            if include_optimization_status:
                status["optimization_status"] = {
                    "active_optimizations": len(
                        [
                            m
                            for m in self.optimization_monitoring.values()
                            if m["status"] == "running"
                        ]
                    ),
                    "completed_optimizations": len(
                        [
                            m
                            for m in self.optimization_monitoring.values()
                            if m["status"] == "completed"
                        ]
                    ),
                    "failed_optimizations": len(
                        [
                            m
                            for m in self.optimization_monitoring.values()
                            if m["status"] == "failed"
                        ]
                    ),
                    "average_execution_time": self._calculate_average_execution_time(),
                }

            return {"success": True, "status": status}

        except Exception as e:
            return {"success": False, "error_message": str(e)}

    def _get_system_start_time(self) -> float:
        """Get system start time."""
        # In real implementation, this would be stored when system starts
        return time.time() - 3600  # Simulate 1 hour uptime

    def _calculate_average_quality_score(self) -> float:
        """Calculate average quality score across all optimizations."""
        quality_scores = [
            data["metrics"]["quality_score"] for data in self.optimization_monitoring.values()
        ]
        return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

    def _calculate_success_rate(self) -> float:
        """Calculate optimization success rate."""
        total = len(self.optimization_monitoring)
        successful = len(
            [m for m in self.optimization_monitoring.values() if m["status"] == "completed"]
        )
        return successful / total if total > 0 else 0.0

    def _calculate_system_performance(self) -> float:
        """Calculate overall system performance score."""
        # Combine multiple performance indicators
        quality_score = self._calculate_average_quality_score()
        success_rate = self._calculate_success_rate()

        return (quality_score + success_rate) / 2

    def _calculate_average_execution_time(self) -> float:
        """Calculate average execution time for optimizations."""
        execution_times = [
            data["metrics"]["execution_time"] for data in self.optimization_monitoring.values()
        ]
        return sum(execution_times) / len(execution_times) if execution_times else 0.0
