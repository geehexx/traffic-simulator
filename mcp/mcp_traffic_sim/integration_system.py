"""Integration system for connecting DSPy optimization with existing traffic simulator."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List

from .config import MCPConfig
from .logging_util import MCPLogger
from .security import SecurityManager
from .production_optimizer import ProductionOptimizer
from .monitoring_system import MonitoringSystem
from .feedback_collector import FeedbackCollector
from .dashboard_generator import DashboardGenerator
from .alerting_system import AlertingSystem


class IntegrationSystem:
    """Integration system for connecting all optimization components."""

    def __init__(self, config: MCPConfig, logger: MCPLogger, security: SecurityManager):
        """Initialize integration system."""
        self.config = config
        self.logger = logger
        self.security = security

        # Initialize all components
        self.optimizer = ProductionOptimizer(config, logger, security)
        self.monitoring = MonitoringSystem(config, logger, security)
        self.feedback_collector = FeedbackCollector(config, logger, security)
        self.dashboard_generator = DashboardGenerator(config, logger, security)
        self.alerting = AlertingSystem(config, logger, security)

        # Integration state
        self.integration_status = "initializing"
        self.connected_components = []
        self.integration_metrics = {}

        # Start integration
        self._start_integration()

    def _start_integration(self):
        """Start integration process."""
        asyncio.create_task(self._integrate_components())

    async def _integrate_components(self):
        """Integrate all optimization components."""
        try:
            self.logger.log_info("Starting component integration...")

            # Connect optimizer with monitoring
            await self._connect_optimizer_monitoring()

            # Connect feedback collector with optimizer
            await self._connect_feedback_optimizer()

            # Connect monitoring with alerting
            await self._connect_monitoring_alerting()

            # Connect dashboard with all components
            await self._connect_dashboard_components()

            # Set up continuous improvement loop
            await self._setup_continuous_improvement()

            self.integration_status = "integrated"
            self.logger.log_info("Component integration completed successfully")

        except Exception as e:
            self.integration_status = "failed"
            self.logger.log_error(f"Integration failed: {e}")

    async def _connect_optimizer_monitoring(self):
        """Connect optimizer with monitoring system."""
        # Set up monitoring callbacks for optimizer
        self.optimizer.monitoring = self.monitoring

        # Connect optimization events to monitoring
        self.optimizer.on_optimization_start = self.monitoring.start_optimization_monitoring
        self.optimizer.on_optimization_complete = self.monitoring.stop_optimization_monitoring

        self.connected_components.append("optimizer-monitoring")
        self.logger.log_info("Connected optimizer with monitoring")

    async def _connect_feedback_optimizer(self):
        """Connect feedback collector with optimizer."""
        # Set up feedback processing for optimizer
        self.feedback_collector.on_optimization_trigger = self._handle_optimization_trigger

        # Connect feedback analysis to optimizer
        self.feedback_collector.optimizer = self.optimizer

        self.connected_components.append("feedback-optimizer")
        self.logger.log_info("Connected feedback collector with optimizer")

    async def _connect_monitoring_alerting(self):
        """Connect monitoring with alerting system."""
        # Set up alert triggers from monitoring
        self.monitoring.on_alert_trigger = self.alerting.trigger_alert

        # Connect monitoring metrics to alerting
        self.monitoring.alerting_system = self.alerting

        self.connected_components.append("monitoring-alerting")
        self.logger.log_info("Connected monitoring with alerting")

    async def _connect_dashboard_components(self):
        """Connect dashboard with all components."""
        # Set up dashboard data sources
        self.dashboard_generator.optimizer = self.optimizer
        self.dashboard_generator.monitoring = self.monitoring
        self.dashboard_generator.feedback_collector = self.feedback_collector
        self.dashboard_generator.alerting = self.alerting

        self.connected_components.append("dashboard-components")
        self.logger.log_info("Connected dashboard with all components")

    async def _setup_continuous_improvement(self):
        """Set up continuous improvement loop."""
        # Start continuous improvement task
        asyncio.create_task(self._continuous_improvement_loop())

        self.connected_components.append("continuous-improvement")
        self.logger.log_info("Set up continuous improvement loop")

    async def _continuous_improvement_loop(self):
        """Continuous improvement loop."""
        while True:
            try:
                # Check for optimization triggers
                await self._check_optimization_triggers()

                # Run optimization cycle if needed
                await self._run_optimization_cycle_if_needed()

                # Update integration metrics
                await self._update_integration_metrics()

                # Wait before next iteration
                await asyncio.sleep(300)  # Every 5 minutes

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(f"Error in continuous improvement loop: {e}")

    async def _check_optimization_triggers(self):
        """Check for optimization triggers."""
        # Check feedback-based triggers
        feedback_triggers = await self._check_feedback_triggers()

        # Check performance-based triggers
        performance_triggers = await self._check_performance_triggers()

        # Check time-based triggers
        time_triggers = await self._check_time_triggers()

        # Process triggers
        all_triggers = feedback_triggers + performance_triggers + time_triggers
        if all_triggers:
            await self._process_optimization_triggers(all_triggers)

    async def _check_feedback_triggers(self) -> List[Dict[str, Any]]:
        """Check feedback-based optimization triggers."""
        triggers = []

        # Get feedback summary
        feedback_summary = await self.feedback_collector.get_feedback_summary()

        if feedback_summary.get("success"):
            # Check for low quality feedback
            for prompt_data in feedback_summary.get("aggregates", {}).values():
                if prompt_data.get("average_quality", 1.0) < 0.7:
                    triggers.append(
                        {
                            "type": "feedback_quality",
                            "prompt_id": prompt_data.get("prompt_id"),
                            "trigger_data": prompt_data,
                            "priority": "high",
                        }
                    )

        return triggers

    async def _check_performance_triggers(self) -> List[Dict[str, Any]]:
        """Check performance-based optimization triggers."""
        triggers = []

        # Get system status
        system_status = await self.monitoring.get_system_status({})

        if system_status.get("success"):
            status = system_status["status"]

            # Check for performance degradation
            if status.get("metrics", {}).get("system_performance", 1.0) < 0.8:
                triggers.append(
                    {
                        "type": "performance_degradation",
                        "trigger_data": status["metrics"],
                        "priority": "medium",
                    }
                )

            # Check for high error rate
            if status.get("metrics", {}).get("optimization_success_rate", 1.0) < 0.8:
                triggers.append(
                    {
                        "type": "high_error_rate",
                        "trigger_data": status["metrics"],
                        "priority": "high",
                    }
                )

        return triggers

    async def _check_time_triggers(self) -> List[Dict[str, Any]]:
        """Check time-based optimization triggers."""
        triggers = []

        # Daily optimization cycle
        current_hour = time.localtime().tm_hour
        if current_hour == 2:  # 2 AM daily
            triggers.append(
                {
                    "type": "daily_optimization",
                    "trigger_data": {"hour": current_hour},
                    "priority": "low",
                }
            )

        # Weekly deep optimization
        current_weekday = time.localtime().tm_wday
        if current_weekday == 0 and current_hour == 3:  # Sunday 3 AM
            triggers.append(
                {
                    "type": "weekly_deep_optimization",
                    "trigger_data": {"weekday": current_weekday, "hour": current_hour},
                    "priority": "medium",
                }
            )

        return triggers

    async def _process_optimization_triggers(self, triggers: List[Dict[str, Any]]):
        """Process optimization triggers."""
        for trigger in triggers:
            try:
                trigger_type = trigger["type"]
                priority = trigger.get("priority", "low")

                if trigger_type == "feedback_quality":
                    await self._handle_feedback_quality_trigger(trigger)
                elif trigger_type == "performance_degradation":
                    await self._handle_performance_degradation_trigger(trigger)
                elif trigger_type == "high_error_rate":
                    await self._handle_high_error_rate_trigger(trigger)
                elif trigger_type == "daily_optimization":
                    await self._handle_daily_optimization_trigger(trigger)
                elif trigger_type == "weekly_deep_optimization":
                    await self._handle_weekly_deep_optimization_trigger(trigger)

                self.logger.log_info(f"Processed {trigger_type} trigger with priority {priority}")

            except Exception as e:
                self.logger.log_error(f"Error processing trigger {trigger['type']}: {e}")

    async def _handle_feedback_quality_trigger(self, trigger: Dict[str, Any]):
        """Handle feedback quality trigger."""
        prompt_id = trigger.get("prompt_id")
        if prompt_id:
            # Run optimization for specific prompt
            await self.optimizer.optimize_prompt_production(
                {
                    "prompt_id": prompt_id,
                    "strategy": "mipro",
                    "auto_mode": "medium",
                    "monitoring_enabled": True,
                }
            )

    async def _handle_performance_degradation_trigger(self, trigger: Dict[str, Any]):
        """Handle performance degradation trigger."""
        # Run performance optimization
        await self.optimizer.run_continuous_improvement_cycle(
            {"strategies": ["mipro", "bayesian"], "auto_deploy": True, "monitoring_interval": 1800}
        )

    async def _handle_high_error_rate_trigger(self, trigger: Dict[str, Any]):
        """Handle high error rate trigger."""
        # Run error-focused optimization
        await self.optimizer.run_continuous_improvement_cycle(
            {
                "strategies": ["hybrid"],
                "auto_deploy": False,  # Don't auto-deploy for error scenarios
                "monitoring_interval": 900,
            }
        )

    async def _handle_daily_optimization_trigger(self, trigger: Dict[str, Any]):
        """Handle daily optimization trigger."""
        # Run daily optimization cycle
        await self.optimizer.run_continuous_improvement_cycle(
            {"strategies": ["mipro"], "auto_deploy": True, "monitoring_interval": 3600}
        )

    async def _handle_weekly_deep_optimization_trigger(self, trigger: Dict[str, Any]):
        """Handle weekly deep optimization trigger."""
        # Run comprehensive optimization cycle
        await self.optimizer.run_continuous_improvement_cycle(
            {
                "strategies": ["mipro", "bayesian", "hybrid"],
                "auto_deploy": True,
                "monitoring_interval": 7200,
            }
        )

    async def _run_optimization_cycle_if_needed(self):
        """Run optimization cycle if conditions are met."""
        # Check if optimization is needed based on various factors
        needs_optimization = await self._assess_optimization_need()

        if needs_optimization:
            await self.optimizer.run_continuous_improvement_cycle(
                {
                    "strategies": ["mipro", "bayesian"],
                    "auto_deploy": True,
                    "monitoring_interval": 1800,
                }
            )

    async def _assess_optimization_need(self) -> bool:
        """Assess if optimization is needed."""
        # Check system performance
        system_status = await self.monitoring.get_system_status({})
        if system_status.get("success"):
            metrics = system_status["status"].get("metrics", {})
            if metrics.get("system_performance", 1.0) < 0.85:
                return True

        # Check feedback quality
        feedback_summary = await self.feedback_collector.get_feedback_summary()
        if feedback_summary.get("success"):
            for prompt_data in feedback_summary.get("aggregates", {}).values():
                if prompt_data.get("average_quality", 1.0) < 0.8:
                    return True

        return False

    async def _update_integration_metrics(self):
        """Update integration metrics."""
        self.integration_metrics = {
            "integration_status": self.integration_status,
            "connected_components": len(self.connected_components),
            "timestamp": time.time(),
            "uptime": time.time() - self._get_integration_start_time(),
        }

    def _get_integration_start_time(self) -> float:
        """Get integration start time."""
        # In real implementation, this would be stored when integration starts
        return time.time() - 3600  # Simulate 1 hour uptime

    async def _handle_optimization_trigger(self, trigger_data: Dict[str, Any]):
        """Handle optimization trigger from feedback collector."""
        prompt_id = trigger_data.get("prompt_id")
        if prompt_id:
            await self.optimizer.optimize_prompt_production(
                {
                    "prompt_id": prompt_id,
                    "strategy": "mipro",
                    "auto_mode": "medium",
                    "monitoring_enabled": True,
                }
            )

    async def get_integration_status(self) -> Dict[str, Any]:
        """Get integration system status."""
        return {
            "success": True,
            "integration_status": self.integration_status,
            "connected_components": self.connected_components,
            "metrics": self.integration_metrics,
            "component_status": {
                "optimizer": "active",
                "monitoring": "active",
                "feedback_collector": "active",
                "dashboard_generator": "active",
                "alerting": "active",
            },
        }

    async def shutdown(self):
        """Shutdown integration system."""
        # Shutdown all components
        await self.feedback_collector.shutdown()
        await self.alerting.shutdown()

        self.integration_status = "shutdown"
        self.logger.log_info("Integration system shutdown complete")
