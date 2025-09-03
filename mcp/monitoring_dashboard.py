#!/usr/bin/env python3
"""Performance monitoring dashboard for FastMCP server."""

import json
import time
from pathlib import Path
from datetime import datetime


class MonitoringDashboard:
    """Performance monitoring dashboard for optimization tracking."""

    def __init__(self, log_dir: Path):
        """Initialize monitoring dashboard."""
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.log_dir / "performance_metrics.json"
        self.alerts_file = self.log_dir / "alerts.json"

    def log_optimization(self, prompt_id: str, strategy: str, improvement_score: float):
        """Log optimization event."""
        event = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "event_type": "optimization",
            "prompt_id": prompt_id,
            "strategy": strategy,
            "improvement_score": improvement_score,
        }
        self._append_to_file(self.metrics_file, event)

    def log_performance_evaluation(
        self, prompt_id: str, accuracy_score: float, response_time: float
    ):
        """Log performance evaluation."""
        event = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "event_type": "performance_evaluation",
            "prompt_id": prompt_id,
            "accuracy_score": accuracy_score,
            "response_time": response_time,
        }
        self._append_to_file(self.metrics_file, event)

    def log_deployment(self, prompt_ids: list, environment: str, status: str):
        """Log deployment event."""
        event = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "event_type": "deployment",
            "prompt_ids": prompt_ids,
            "environment": environment,
            "status": status,
        }
        self._append_to_file(self.metrics_file, event)

    def create_alert(self, alert_type: str, message: str, severity: str = "warning"):
        """Create monitoring alert."""
        alert = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "resolved": False,
        }
        self._append_to_file(self.alerts_file, alert)

    def get_performance_summary(self) -> dict:
        """Get performance summary."""
        if not self.metrics_file.exists():
            return {"message": "No metrics available yet"}

        with open(self.metrics_file, "r") as f:
            events = [json.loads(line) for line in f if line.strip()]

        # Calculate summary statistics
        optimizations = [e for e in events if e.get("event_type") == "optimization"]
        evaluations = [e for e in events if e.get("event_type") == "performance_evaluation"]
        deployments = [e for e in events if e.get("event_type") == "deployment"]

        return {
            "total_optimizations": len(optimizations),
            "total_evaluations": len(evaluations),
            "total_deployments": len(deployments),
            "average_improvement": sum(e.get("improvement_score", 0) for e in optimizations)
            / max(len(optimizations), 1),
            "average_accuracy": sum(e.get("accuracy_score", 0) for e in evaluations)
            / max(len(evaluations), 1),
            "last_activity": max((e.get("timestamp", 0) for e in events), default=0),
        }

    def get_active_alerts(self) -> list:
        """Get active alerts."""
        if not self.alerts_file.exists():
            return []

        with open(self.alerts_file, "r") as f:
            alerts = [json.loads(line) for line in f if line.strip()]

        return [alert for alert in alerts if not alert.get("resolved", False)]

    def _append_to_file(self, file_path: Path, data: dict):
        """Append data to JSONL file."""
        with open(file_path, "a") as f:
            f.write(json.dumps(data) + "\n")


def main():
    """Test monitoring dashboard."""
    log_dir = Path("/home/gxx/projects/traffic-simulator/runs/mcp")
    dashboard = MonitoringDashboard(log_dir)

    # Test logging
    dashboard.log_optimization("test_prompt", "hybrid", 0.15)
    dashboard.log_performance_evaluation("test_prompt", 0.92, 1.2)
    dashboard.log_deployment(["test_prompt_v1"], "production", "successful")

    # Test alert
    dashboard.create_alert("quality_drop", "Quality score below threshold", "warning")

    # Get summary
    summary = dashboard.get_performance_summary()
    print("📊 Performance Summary:")
    print(json.dumps(summary, indent=2))

    # Get alerts
    alerts = dashboard.get_active_alerts()
    print(f"\n🚨 Active Alerts: {len(alerts)}")
    for alert in alerts:
        print(f"  - {alert['alert_type']}: {alert['message']}")


if __name__ == "__main__":
    main()
