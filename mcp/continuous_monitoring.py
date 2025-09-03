#!/usr/bin/env python3
"""Continuous monitoring system for FastMCP platform."""

import json
import time
import threading
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import psutil


class ContinuousMonitor:
    """Continuous monitoring system for FastMCP platform."""

    def __init__(self, log_dir: Path, monitoring_interval: int = 60):
        """Initialize continuous monitor."""
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.monitoring_interval = monitoring_interval
        self.monitoring_active = False
        self.monitoring_thread = None
        self.metrics_history = []
        self.alerts = []

    def start_monitoring(self):
        """Start continuous monitoring."""
        if self.monitoring_active:
            print("⚠️  Monitoring already active")
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

        print(f"🔍 Continuous monitoring started (interval: {self.monitoring_interval}s)")

    def stop_monitoring(self):
        """Stop continuous monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        print("⏹️  Continuous monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect metrics
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)

                # Check for alerts
                self._check_alerts(metrics)

                # Save metrics
                self._save_metrics(metrics)

                # Cleanup old metrics (keep last 24 hours)
                self._cleanup_old_metrics()

            except Exception as e:
                print(f"❌ Monitoring error: {e}")

            time.sleep(self.monitoring_interval)

    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect system and application metrics."""
        timestamp = time.time()

        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # Process metrics
        process_metrics = self._get_process_metrics()

        # Application metrics
        app_metrics = self._get_application_metrics()

        return {
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "disk_percent": disk.percent,
                "disk_free": disk.free,
            },
            "process": process_metrics,
            "application": app_metrics,
        }

    def _get_process_metrics(self) -> Dict[str, Any]:
        """Get process-specific metrics."""
        try:
            # Find FastMCP process
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
                if "python" in proc.info["name"].lower() and "fastmcp" in " ".join(proc.cmdline()):
                    return {
                        "pid": proc.info["pid"],
                        "cpu_percent": proc.info["cpu_percent"],
                        "memory_mb": proc.info["memory_info"].rss / 1024 / 1024,
                        "status": "running",
                    }
        except Exception as e:
            print(f"⚠️  Process metrics error: {e}")

        return {"pid": None, "cpu_percent": 0, "memory_mb": 0, "status": "not_found"}

    def _get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific metrics."""
        try:
            # Check if FastMCP server is responding
            server_status = self._check_server_health()

            # Get optimization metrics
            optimization_metrics = self._get_optimization_metrics()

            return {
                "server_status": server_status,
                "optimization_metrics": optimization_metrics,
                "last_activity": self._get_last_activity(),
            }
        except Exception as e:
            print(f"⚠️  Application metrics error: {e}")
            return {"server_status": "error", "optimization_metrics": {}, "last_activity": None}

    def _check_server_health(self) -> str:
        """Check FastMCP server health."""
        try:
            # Check if server process is running
            for proc in psutil.process_iter(["name", "cmdline"]):
                if "python" in proc.info["name"].lower():
                    cmdline = " ".join(proc.cmdline())
                    if "fastmcp" in cmdline:
                        return "healthy"
            return "not_running"
        except Exception as e:
            return f"error: {str(e)}"

    def _get_optimization_metrics(self) -> Dict[str, Any]:
        """Get optimization-specific metrics."""
        try:
            # Read optimization history
            history_file = self.log_dir / "optimization_history.json"
            if history_file.exists():
                with open(history_file, "r") as f:
                    history = json.load(f)

                return {
                    "total_optimizations": len(history),
                    "last_optimization": history[-1] if history else None,
                    "average_improvement": sum(h.get("improvement_score", 0) for h in history)
                    / max(len(history), 1),
                }
            else:
                return {
                    "total_optimizations": 0,
                    "last_optimization": None,
                    "average_improvement": 0,
                }
        except Exception as e:
            return {
                "total_optimizations": 0,
                "last_optimization": None,
                "average_improvement": 0,
                "error": str(e),
            }

    def _get_last_activity(self) -> Optional[float]:
        """Get last activity timestamp."""
        try:
            # Check log files for last activity
            log_files = list(self.log_dir.glob("*.log"))
            if log_files:
                latest_file = max(log_files, key=lambda f: f.stat().st_mtime)
                return latest_file.stat().st_mtime
            return None
        except Exception:
            return None

    def _check_alerts(self, metrics: Dict[str, Any]):
        """Check for alert conditions."""
        alerts = []

        # CPU alert
        if metrics["system"]["cpu_percent"] > 80:
            alerts.append(
                {
                    "type": "high_cpu",
                    "message": f"High CPU usage: {metrics['system']['cpu_percent']:.1f}%",
                    "severity": "warning",
                    "timestamp": metrics["timestamp"],
                }
            )

        # Memory alert
        if metrics["system"]["memory_percent"] > 85:
            alerts.append(
                {
                    "type": "high_memory",
                    "message": f"High memory usage: {metrics['system']['memory_percent']:.1f}%",
                    "severity": "warning",
                    "timestamp": metrics["timestamp"],
                }
            )

        # Disk alert
        if metrics["system"]["disk_percent"] > 90:
            alerts.append(
                {
                    "type": "low_disk",
                    "message": f"Low disk space: {metrics['system']['disk_percent']:.1f}%",
                    "severity": "critical",
                    "timestamp": metrics["timestamp"],
                }
            )

        # Server status alert
        if metrics["application"]["server_status"] != "healthy":
            alerts.append(
                {
                    "type": "server_down",
                    "message": f"Server status: {metrics['application']['server_status']}",
                    "severity": "critical",
                    "timestamp": metrics["timestamp"],
                }
            )

        # Add new alerts
        for alert in alerts:
            self.alerts.append(alert)
            print(f"🚨 ALERT: {alert['message']}")

    def _save_metrics(self, metrics: Dict[str, Any]):
        """Save metrics to file."""
        try:
            metrics_file = self.log_dir / "continuous_metrics.jsonl"
            with open(metrics_file, "a") as f:
                f.write(json.dumps(metrics) + "\n")
        except Exception as e:
            print(f"⚠️  Metrics save error: {e}")

    def _cleanup_old_metrics(self):
        """Cleanup old metrics (keep last 24 hours)."""
        try:
            cutoff_time = time.time() - (24 * 3600)  # 24 hours ago

            # Cleanup metrics history
            self.metrics_history = [m for m in self.metrics_history if m["timestamp"] > cutoff_time]

            # Cleanup old metrics file
            metrics_file = self.log_dir / "continuous_metrics.jsonl"
            if metrics_file.exists():
                temp_file = self.log_dir / "continuous_metrics_temp.jsonl"
                with open(metrics_file, "r") as infile, open(temp_file, "w") as outfile:
                    for line in infile:
                        try:
                            data = json.loads(line.strip())
                            if data.get("timestamp", 0) > cutoff_time:
                                outfile.write(line)
                        except json.JSONDecodeError:
                            continue

                temp_file.replace(metrics_file)

        except Exception as e:
            print(f"⚠️  Cleanup error: {e}")

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        return {
            "monitoring_active": self.monitoring_active,
            "monitoring_interval": self.monitoring_interval,
            "metrics_count": len(self.metrics_history),
            "alerts_count": len(self.alerts),
            "recent_alerts": self.alerts[-5:] if self.alerts else [],
        }

    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for specified hours."""
        cutoff_time = time.time() - (hours * 3600)
        recent_metrics = [m for m in self.metrics_history if m["timestamp"] > cutoff_time]

        if not recent_metrics:
            return {"message": "No metrics available for specified period"}

        # Calculate summary statistics
        cpu_values = [m["system"]["cpu_percent"] for m in recent_metrics]
        memory_values = [m["system"]["memory_percent"] for m in recent_metrics]

        return {
            "period_hours": hours,
            "metrics_count": len(recent_metrics),
            "cpu": {
                "average": sum(cpu_values) / len(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values),
            },
            "memory": {
                "average": sum(memory_values) / len(memory_values),
                "max": max(memory_values),
                "min": min(memory_values),
            },
            "alerts": len([a for a in self.alerts if a["timestamp"] > cutoff_time]),
        }


def main():
    """Test continuous monitoring system."""
    log_dir = Path("/home/gxx/projects/traffic-simulator/runs/mcp")
    monitor = ContinuousMonitor(log_dir, monitoring_interval=30)

    print("🔍 Testing Continuous Monitoring System...")

    # Test metrics collection
    metrics = monitor._collect_metrics()
    print("✅ Metrics collection test:")
    print(json.dumps(metrics, indent=2))

    # Test monitoring status
    status = monitor.get_monitoring_status()
    print("\n✅ Monitoring status:")
    print(json.dumps(status, indent=2))

    # Test metrics summary
    summary = monitor.get_metrics_summary(hours=1)
    print("\n✅ Metrics summary:")
    print(json.dumps(summary, indent=2))

    print("\n🎉 Continuous monitoring system ready!")


if __name__ == "__main__":
    main()
