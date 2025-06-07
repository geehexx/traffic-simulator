#!/usr/bin/env python3
"""
Performance monitoring dashboard for traffic simulator.

Tracks real-time performance metrics and provides alerts for
performance degradation or issues.
"""

from __future__ import annotations

import argparse
import time
import psutil  # type: ignore[import-not-found]
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation


class PerformanceMonitor:
    """Monitor simulation performance metrics."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics: List[Dict[str, Any]] = []
        self.alerts: List[str] = []

    def collect_metrics(self, sim: Simulation, elapsed_time: float) -> Dict[str, Any]:
        """Collect performance metrics."""
        process = psutil.Process()

        return {
            "timestamp": time.time(),
            "elapsed_time": elapsed_time,
            "vehicle_count": len(sim.vehicles),
            "simulation_time": sim.simulation_time,
            "cpu_percent": process.cpu_percent(),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "steps_per_second": 1.0 / elapsed_time if elapsed_time > 0 else 0,
        }

    def check_alerts(self, metrics: Dict[str, Any]) -> List[str]:
        """Check for performance alerts."""
        alerts = []

        # FPS alert
        if metrics["steps_per_second"] < 30:
            alerts.append(f"Low FPS: {metrics['steps_per_second']:.1f} steps/s")

        # Memory alert
        if metrics["memory_mb"] > 1000:
            alerts.append(f"High memory usage: {metrics['memory_mb']:.1f} MB")

        # CPU alert
        if metrics["cpu_percent"] > 90:
            alerts.append(f"High CPU usage: {metrics['cpu_percent']:.1f}%")

        return alerts

    def run_monitoring(self, duration_minutes: int = 5):
        """Run performance monitoring for specified duration."""
        print(f"Starting performance monitoring for {duration_minutes} minutes...")

        sim = Simulation(self.config)
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)

        while time.time() < end_time:
            step_start = time.time()
            sim.step(0.02)
            step_elapsed = time.time() - step_start

            metrics = self.collect_metrics(sim, step_elapsed)
            self.metrics.append(metrics)

            # Check for alerts
            alerts = self.check_alerts(metrics)
            if alerts:
                self.alerts.extend(alerts)
                for alert in alerts:
                    print(f"⚠️  ALERT: {alert}")

            # Print status every 10 steps
            if len(self.metrics) % 10 == 0:
                print(
                    f"Step {len(self.metrics)}: "
                    f"{metrics['steps_per_second']:.1f} steps/s, "
                    f"{metrics['memory_mb']:.1f} MB, "
                    f"{metrics['cpu_percent']:.1f}% CPU"
                )

        self.print_summary()

    def print_summary(self):
        """Print performance summary."""
        if not self.metrics:
            return

        avg_fps = sum(m["steps_per_second"] for m in self.metrics) / len(self.metrics)
        max_memory = max(m["memory_mb"] for m in self.metrics)
        avg_cpu = sum(m["cpu_percent"] for m in self.metrics) / len(self.metrics)

        print("\n=== Performance Summary ===")
        print(f"Average FPS: {avg_fps:.1f} steps/s")
        print(f"Peak Memory: {max_memory:.1f} MB")
        print(f"Average CPU: {avg_cpu:.1f}%")
        print(f"Total Alerts: {len(self.alerts)}")

        if self.alerts:
            print("\nAlerts:")
            for alert in set(self.alerts):
                print(f"  - {alert}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Monitor traffic simulator performance")
    parser.add_argument(
        "--duration", "-d", type=int, default=5, help="Monitoring duration in minutes"
    )
    parser.add_argument(
        "--vehicles", "-v", type=int, default=100, help="Number of vehicles to simulate"
    )
    parser.add_argument(
        "--speed-factor", "-s", type=float, default=1.0, help="Simulation speed factor"
    )

    args = parser.parse_args()

    # Load and configure simulation
    config = load_config()
    config["vehicles"]["count"] = args.vehicles
    config["physics"]["speed_factor"] = args.speed_factor

    # Run monitoring
    monitor = PerformanceMonitor(config)
    monitor.run_monitoring(args.duration)


if __name__ == "__main__":
    main()
