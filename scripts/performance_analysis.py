#!/usr/bin/env python3
"""
Comprehensive performance analysis script for the traffic simulator project.
Consolidates benchmark, scale testing, and performance monitoring functionality.

Usage:
    python scripts/performance_analysis.py --mode=benchmark    # High-performance benchmark
    python scripts/performance_analysis.py --mode=scale       # Scale testing
    python scripts/performance_analysis.py --mode=monitor     # Real-time monitoring
"""

from __future__ import annotations

import argparse
import csv
import statistics
import time
import sys
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation

try:
    import psutil  # type: ignore[import-not-found]
except ImportError:
    psutil = None


@dataclass
class PerformanceMetrics:
    """Performance metrics data point."""

    timestamp: str
    vehicles: int
    speed_factor: float
    steps: int
    dt: float
    elapsed_s: float
    steps_per_second: float
    vehicles_per_second: float
    efficiency: float
    cpu_percent: float
    memory_mb: float
    avg_frame_ms: float
    p95_frame_ms: float


class PerformanceAnalysis:
    """Comprehensive performance analysis system."""

    def __init__(self):
        """Initialize performance analysis."""
        self.metrics: List[PerformanceMetrics] = []
        self.alerts: List[str] = []

    def run_benchmark(
        self, vehicles: int, steps: int, dt: float, speed_factor: float
    ) -> Dict[str, float]:
        """Run high-performance benchmark."""
        cfg = load_config().copy()
        cfg.setdefault("vehicles", {})
        cfg["vehicles"]["count"] = vehicles
        cfg.setdefault("physics", {})
        cfg["physics"]["speed_factor"] = speed_factor
        cfg.setdefault("data_manager", {})
        cfg["data_manager"]["enabled"] = True
        cfg.setdefault("high_performance", {})
        cfg["high_performance"]["enabled"] = True
        cfg["high_performance"]["idm_vectorized"] = True

        sim = Simulation(cfg)

        frame_times = []
        start = time.perf_counter()
        for _ in range(steps):
            f0 = time.perf_counter()
            sim.step(dt)
            frame_times.append(time.perf_counter() - f0)
        total = time.perf_counter() - start

        fps_equiv = steps / total / (1.0 / dt)
        return {
            "vehicles": float(vehicles),
            "steps": float(steps),
            "dt": dt,
            "speed_factor": speed_factor,
            "total_s": total,
            "fps_equiv": fps_equiv,
            "avg_frame_ms": statistics.mean(frame_times) * 1000.0,
            "p95_frame_ms": (
                statistics.quantiles(frame_times, n=20)[18] * 1000.0
                if len(frame_times) > 19
                else statistics.mean(frame_times) * 1000.0
            ),
        }

    def run_scale_benchmark(
        self,
        vehicle_counts: list[int],
        speed_factors: list[float],
        steps: int = 1000,
        dt: float = 0.02,
        output_csv: str = "scale_benchmark.csv",
    ) -> None:
        """Run comprehensive scale benchmarks."""
        results = []

        print("=== Traffic Simulator Scale Benchmark ===")
        print(f"Testing {len(vehicle_counts)} vehicle counts × {len(speed_factors)} speed factors")
        print(f"Steps per test: {steps}, dt: {dt}")
        print()

        for vehicle_count in vehicle_counts:
            for speed_factor in speed_factors:
                print(f"Testing {vehicle_count} vehicles at {speed_factor}x speed...", end=" ")

                # Load base config
                config = load_config()

                # Override vehicle count and speed factor
                config["vehicles"]["count"] = vehicle_count
                config["physics"]["speed_factor"] = speed_factor

                # Create simulation
                sim = Simulation(config)

                # Warmup (let simulation stabilize)
                for _ in range(100):
                    sim.step(dt)

                # Benchmark
                start_time = time.perf_counter()
                for _ in range(steps):
                    sim.step(dt)
                end_time = time.perf_counter()

                elapsed = end_time - start_time
                steps_per_second = steps / elapsed
                vehicles_per_second = (vehicle_count * steps) / elapsed

                print(f"{steps_per_second:.1f} steps/s ({vehicles_per_second:.0f} v·s/s)")

                results.append(
                    {
                        "vehicles": vehicle_count,
                        "speed_factor": speed_factor,
                        "steps": steps,
                        "dt": dt,
                        "elapsed_s": elapsed,
                        "steps_per_second": steps_per_second,
                        "vehicles_per_second": vehicles_per_second,
                        "efficiency": vehicles_per_second / vehicle_count,  # v·s/s per vehicle
                    }
                )

        # Write results to CSV
        with open(output_csv, "w", newline="") as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)

        print(f"\nResults written to {output_csv}")

        # Print summary
        print("\n=== Performance Summary ===")
        print("Vehicles | Speed | Steps/s | V·S/s | Efficiency")
        print("---------|-------|---------|-------|-----------")
        for result in results:
            print(
                f"{result['vehicles']:8d} | {result['speed_factor']:5.1f} | "
                f"{result['steps_per_second']:7.1f} | {result['vehicles_per_second']:5.0f} | "
                f"{result['efficiency']:10.2f}"
            )

    def collect_metrics(self, sim: Simulation, elapsed_time: float) -> Dict[str, Any]:
        """Collect performance metrics."""
        if psutil:
            process = psutil.Process()
            cpu_percent = process.cpu_percent()
            memory_mb = process.memory_info().rss / 1024 / 1024
        else:
            cpu_percent = 0.0
            memory_mb = 0.0

        return {
            "timestamp": time.time(),
            "elapsed_time": elapsed_time,
            "vehicle_count": len(sim.vehicles),
            "simulation_time": sim.simulation_time,
            "cpu_percent": cpu_percent,
            "memory_mb": memory_mb,
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

    def run_monitoring(
        self, duration_minutes: int = 5, vehicles: int = 100, speed_factor: float = 1.0
    ):
        """Run performance monitoring for specified duration."""
        print(f"Starting performance monitoring for {duration_minutes} minutes...")

        # Load and configure simulation
        config = load_config()
        config["vehicles"]["count"] = vehicles
        config["physics"]["speed_factor"] = speed_factor

        sim = Simulation(config)
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)

        while time.time() < end_time:
            step_start = time.time()
            sim.step(0.02)
            step_elapsed = time.time() - step_start

            metrics = self.collect_metrics(sim, step_elapsed)
            self.metrics.append(
                PerformanceMetrics(
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                    vehicles=metrics["vehicle_count"],
                    speed_factor=speed_factor,
                    steps=1,
                    dt=0.02,
                    elapsed_s=step_elapsed,
                    steps_per_second=metrics["steps_per_second"],
                    vehicles_per_second=(
                        metrics["vehicle_count"] / step_elapsed if step_elapsed > 0 else 0
                    ),
                    efficiency=metrics["vehicle_count"] / step_elapsed if step_elapsed > 0 else 0,
                    cpu_percent=metrics["cpu_percent"],
                    memory_mb=metrics["memory_mb"],
                    avg_frame_ms=step_elapsed * 1000.0,
                    p95_frame_ms=step_elapsed * 1000.0,
                )
            )

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

        self.print_monitoring_summary()

    def print_monitoring_summary(self):
        """Print performance monitoring summary."""
        if not self.metrics:
            return

        avg_fps = sum(m.steps_per_second for m in self.metrics) / len(self.metrics)
        max_memory = max(m.memory_mb for m in self.metrics)
        avg_cpu = sum(m.cpu_percent for m in self.metrics) / len(self.metrics)

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
    parser = argparse.ArgumentParser(description="Comprehensive performance analysis")
    parser.add_argument(
        "--mode",
        choices=["benchmark", "scale", "monitor"],
        default="benchmark",
        help="Analysis mode: benchmark (high-perf), scale (scalability), monitor (real-time)",
    )

    # Benchmark mode arguments
    parser.add_argument("--vehicles", type=int, default=100, help="Number of vehicles")
    parser.add_argument("--steps", type=int, default=1000, help="Number of steps")
    parser.add_argument("--dt", type=float, default=0.02, help="Delta time per step")
    parser.add_argument("--speed-factor", type=float, default=10.0, help="Speed factor")

    # Scale mode arguments
    parser.add_argument(
        "--vehicle-counts",
        nargs="+",
        type=int,
        default=[20, 50, 100, 200, 500, 1000],
        help="Vehicle counts to test",
    )
    parser.add_argument(
        "--speed-factors",
        nargs="+",
        type=float,
        default=[1.0, 10.0, 100.0, 1000.0],
        help="Speed factors to test",
    )
    parser.add_argument("--output", default="scale_benchmark.csv", help="Output CSV file")

    # Monitor mode arguments
    parser.add_argument(
        "--duration", "-d", type=int, default=5, help="Monitoring duration in minutes"
    )

    args = parser.parse_args()

    try:
        analysis = PerformanceAnalysis()

        if args.mode == "benchmark":
            # High-performance benchmark mode
            stats = analysis.run_benchmark(args.vehicles, args.steps, args.dt, args.speed_factor)
            print(
                f"vehicles={int(stats['vehicles'])} steps={int(stats['steps'])} dt={stats['dt']:.3f} "
                f"sf={stats['speed_factor']:.1f} total={stats['total_s']:.3f}s fps_eq={stats['fps_equiv']:.1f} "
                f"avg={stats['avg_frame_ms']:.3f}ms p95={stats['p95_frame_ms']:.3f}ms"
            )

        elif args.mode == "scale":
            # Scale benchmark mode
            analysis.run_scale_benchmark(
                vehicle_counts=args.vehicle_counts,
                speed_factors=args.speed_factors,
                steps=args.steps,
                dt=args.dt,
                output_csv=args.output,
            )

        elif args.mode == "monitor":
            # Performance monitoring mode
            analysis.run_monitoring(
                duration_minutes=args.duration,
                vehicles=args.vehicles,
                speed_factor=args.speed_factor,
            )

    except KeyboardInterrupt:
        print("\n⏹️  Performance analysis interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error in performance analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
