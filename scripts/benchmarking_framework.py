#!/usr/bin/env python3
"""
Unified Benchmarking Framework for Traffic Simulator

This framework consolidates all benchmarking functionality into a single,
high-performance system with parallel execution, real-time estimation,
and integration with modern benchmarking tools.

Usage:
    python scripts/benchmarking_framework.py --mode=benchmark
    python scripts/benchmarking_framework.py --mode=scale
    python scripts/benchmarking_framework.py --mode=monitor
    python scripts/benchmarking_framework.py --mode=profile
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
from pathlib import Path
import statistics
import sys
import time
import tracemalloc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation
from traffic_sim.core.profiling import get_profiler

import psutil


@dataclass
class BenchmarkConfig:
    """Configuration for a single benchmark run."""

    vehicles: int
    steps: int
    dt: float = 0.02
    speed_factor: float = 1.0
    warmup_steps: int = 100
    iterations: int = 1
    enable_profiling: bool = False
    enable_high_performance: bool = True
    enable_data_manager: bool = True
    enable_vectorized_idm: bool = True
    config_overrides: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkResult:
    """Result of a benchmark execution."""

    config: BenchmarkConfig
    elapsed_s: float
    steps_per_second: float
    vehicles_per_second: float
    efficiency: float
    avg_frame_ms: float
    p95_frame_ms: float
    cpu_percent: float
    memory_mb: float
    theoretical_fps: Optional[float] = None
    theoretical_throughput: Optional[float] = None
    confidence_score: Optional[float] = None
    profile_data: Optional[Dict[str, Any]] = None
    memory_profile: Optional[Dict[str, Any]] = None
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))


@dataclass
class SystemMetrics:
    """System resource utilization metrics."""

    cpu_utilization: float
    memory_utilization: float
    cpu_count: int
    memory_gb: float
    cache_efficiency: float
    io_wait: float


@dataclass
class TheoreticalPerformance:
    """Theoretical performance estimation with full resource utilization."""

    estimated_fps: float
    estimated_throughput: float
    confidence_score: float
    cpu_bottleneck: bool
    memory_bottleneck: bool
    io_bottleneck: bool


class RealTimeEstimator:
    """Estimate real-time performance with 100% CPU utilization."""

    def __init__(self):
        self.cpu_count = cpu_count()
        self.memory_gb = psutil.virtual_memory().total / (1024**3) if psutil else 8.0

    def estimate_theoretical_performance(
        self, result: BenchmarkResult, system_metrics: SystemMetrics
    ) -> TheoreticalPerformance:
        """Calculate theoretical performance with full resource utilization."""

        # CPU utilization correction
        cpu_correction = 1.0 / max(system_metrics.cpu_utilization, 0.1)

        # Memory bandwidth analysis
        memory_correction = self._analyze_memory_bandwidth(system_metrics)

        # Cache efficiency modeling
        cache_correction = self._model_cache_efficiency(system_metrics)

        # I/O wait analysis
        io_correction = self._analyze_io_bottlenecks(system_metrics)

        # Combined correction factors
        total_correction = cpu_correction * memory_correction * cache_correction * io_correction

        # Estimate theoretical performance
        estimated_fps = result.steps_per_second * total_correction
        estimated_throughput = result.vehicles_per_second * total_correction

        # Calculate confidence score based on system stability
        confidence_score = self._calculate_confidence(system_metrics)

        # Identify bottlenecks
        cpu_bottleneck = system_metrics.cpu_utilization > 0.8
        memory_bottleneck = system_metrics.memory_utilization > 0.8
        io_bottleneck = system_metrics.io_wait > 0.1

        return TheoreticalPerformance(
            estimated_fps=estimated_fps,
            estimated_throughput=estimated_throughput,
            confidence_score=confidence_score,
            cpu_bottleneck=cpu_bottleneck,
            memory_bottleneck=memory_bottleneck,
            io_bottleneck=io_bottleneck,
        )

    def _analyze_memory_bandwidth(self, metrics: SystemMetrics) -> float:
        """Analyze memory bandwidth utilization."""
        if metrics.memory_utilization < 0.5:
            return 1.0
        elif metrics.memory_utilization < 0.8:
            return 0.9
        else:
            return 0.7

    def _model_cache_efficiency(self, metrics: SystemMetrics) -> float:
        """Model cache efficiency impact."""
        return min(1.0, metrics.cache_efficiency)

    def _analyze_io_bottlenecks(self, metrics: SystemMetrics) -> float:
        """Analyze I/O bottlenecks."""
        if metrics.io_wait < 0.05:
            return 1.0
        elif metrics.io_wait < 0.1:
            return 0.95
        else:
            return 0.8

    def _calculate_confidence(self, metrics: SystemMetrics) -> float:
        """Calculate confidence score for theoretical estimation."""
        # Higher confidence with stable system metrics
        stability_score = 1.0 - abs(metrics.cpu_utilization - 0.5) * 2
        stability_score = max(0.0, min(1.0, stability_score))

        # Lower confidence with high I/O wait
        io_penalty = max(0.0, metrics.io_wait - 0.05) * 2

        return max(0.0, min(1.0, stability_score - io_penalty))


class SystemMonitor:
    """Monitor system resource utilization."""

    def __init__(self):
        self.process = psutil.Process() if psutil else None

    def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        if not psutil:
            return SystemMetrics(
                cpu_utilization=0.0,
                memory_utilization=0.0,
                cpu_count=cpu_count(),
                memory_gb=8.0,
                cache_efficiency=1.0,
                io_wait=0.0,
            )

        # CPU utilization
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_utilization = cpu_percent / 100.0

        # Memory utilization
        memory = psutil.virtual_memory()
        memory_utilization = memory.percent / 100.0

        # I/O wait (approximate)
        io_wait = 0.0  # Would need more sophisticated monitoring

        return SystemMetrics(
            cpu_utilization=cpu_utilization,
            memory_utilization=memory_utilization,
            cpu_count=cpu_count(),
            memory_gb=memory.total / (1024**3),
            cache_efficiency=1.0,  # Would need cache monitoring
            io_wait=io_wait,
        )


class BenchmarkRunner:
    """High-performance benchmark runner with parallel execution."""

    def __init__(self, max_workers: Optional[int] = None, timeout: float = 300.0):
        self.max_workers = max_workers or cpu_count()
        self.timeout = timeout
        self.executor = ProcessPoolExecutor(max_workers=self.max_workers)
        self.system_monitor = SystemMonitor()
        self.real_time_estimator = RealTimeEstimator()

    def run_single_benchmark(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Run a single benchmark with comprehensive metrics."""

        # Load and configure simulation
        cfg = load_config().copy()
        cfg.setdefault("vehicles", {})
        cfg["vehicles"]["count"] = config.vehicles
        cfg.setdefault("physics", {})
        cfg["physics"]["speed_factor"] = config.speed_factor
        cfg.setdefault("data_manager", {})
        cfg["data_manager"]["enabled"] = config.enable_data_manager
        cfg.setdefault("high_performance", {})
        cfg["high_performance"]["enabled"] = config.enable_high_performance
        cfg["high_performance"]["idm_vectorized"] = config.enable_vectorized_idm
        cfg.setdefault("profiling", {})
        cfg["profiling"]["enabled"] = config.enable_profiling

        # Apply config overrides
        for key, value in config.config_overrides.items():
            cfg[key] = value

        sim = Simulation(cfg)

        # Warmup
        for _ in range(config.warmup_steps):
            sim.step(config.dt)

        # Collect system metrics before benchmark
        system_metrics = self.system_monitor.collect_metrics()

        # Run benchmark
        frame_times = []
        start_time = time.perf_counter()

        for _ in range(config.steps):
            frame_start = time.perf_counter()
            sim.step(config.dt)
            frame_times.append(time.perf_counter() - frame_start)

        elapsed = time.perf_counter() - start_time

        # Calculate metrics
        steps_per_second = config.steps / elapsed
        vehicles_per_second = (config.vehicles * config.steps) / elapsed
        efficiency = vehicles_per_second / config.vehicles

        # Frame time statistics
        avg_frame_ms = statistics.mean(frame_times) * 1000.0
        p95_frame_ms = (
            statistics.quantiles(frame_times, n=20)[18] * 1000.0
            if len(frame_times) > 19
            else statistics.mean(frame_times) * 1000.0
        )

        # System metrics
        cpu_percent = system_metrics.cpu_utilization * 100
        memory_mb = system_metrics.memory_utilization * system_metrics.memory_gb * 1024

        # Real-time estimation
        theoretical_perf = self.real_time_estimator.estimate_theoretical_performance(
            BenchmarkResult(
                config=config,
                elapsed_s=elapsed,
                steps_per_second=steps_per_second,
                vehicles_per_second=vehicles_per_second,
                efficiency=efficiency,
                avg_frame_ms=avg_frame_ms,
                p95_frame_ms=p95_frame_ms,
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
            ),
            system_metrics,
        )

        # Collect profiling data if enabled
        profile_data = None
        if config.enable_profiling:
            profiler = get_profiler()
            profile_data = profiler.get_stats()

        # Memory profiling
        memory_profile = None
        if tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            memory_profile = {
                "current_mb": current / (1024 * 1024),
                "peak_mb": peak / (1024 * 1024),
            }

        return BenchmarkResult(
            config=config,
            elapsed_s=elapsed,
            steps_per_second=steps_per_second,
            vehicles_per_second=vehicles_per_second,
            efficiency=efficiency,
            avg_frame_ms=avg_frame_ms,
            p95_frame_ms=p95_frame_ms,
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            theoretical_fps=theoretical_perf.estimated_fps,
            theoretical_throughput=theoretical_perf.estimated_throughput,
            confidence_score=theoretical_perf.confidence_score,
            profile_data=profile_data,
            memory_profile=memory_profile,
        )

    def run_parallel_benchmarks(self, configs: List[BenchmarkConfig]) -> List[BenchmarkResult]:
        """Run multiple benchmarks in parallel."""
        print(f"Running {len(configs)} benchmarks in parallel with {self.max_workers} workers...")

        with self.executor as executor:
            future_to_config = {
                executor.submit(self.run_single_benchmark, config): config for config in configs
            }

            results = []
            for future in concurrent.futures.as_completed(future_to_config, timeout=self.timeout):
                config = future_to_config[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"✓ Completed: {config.vehicles} vehicles, {config.speed_factor}x speed")
                except Exception as exc:
                    print(f"✗ Benchmark failed for {config.vehicles} vehicles: {exc}")

            return results

    def run_scale_benchmark(
        self,
        vehicle_counts: List[int],
        speed_factors: List[float],
        steps: int = 1000,
        dt: float = 0.02,
        output_csv: str = "runs/scaling/scale_benchmark.csv",
    ) -> List[BenchmarkResult]:
        """Run comprehensive scale benchmarks."""

        configs = []
        for vehicle_count in vehicle_counts:
            for speed_factor in speed_factors:
                configs.append(
                    BenchmarkConfig(
                        vehicles=vehicle_count,
                        steps=steps,
                        dt=dt,
                        speed_factor=speed_factor,
                        enable_high_performance=True,
                        enable_data_manager=True,
                        enable_vectorized_idm=True,
                    )
                )

        print("=== Traffic Simulator Scale Benchmark ===")
        print(f"Testing {len(vehicle_counts)} vehicle counts × {len(speed_factors)} speed factors")
        print(f"Steps per test: {steps}, dt: {dt}")
        print(f"Parallel execution with {self.max_workers} workers")
        print()

        results = self.run_parallel_benchmarks(configs)

        # Write results to CSV
        if results:
            with open(output_csv, "w", newline="") as f:
                fieldnames = [
                    "vehicles",
                    "speed_factor",
                    "steps",
                    "dt",
                    "elapsed_s",
                    "steps_per_second",
                    "vehicles_per_second",
                    "efficiency",
                    "avg_frame_ms",
                    "p95_frame_ms",
                    "cpu_percent",
                    "memory_mb",
                    "theoretical_fps",
                    "theoretical_throughput",
                    "confidence_score",
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for result in results:
                    writer.writerow(
                        {
                            "vehicles": result.config.vehicles,
                            "speed_factor": result.config.speed_factor,
                            "steps": result.config.steps,
                            "dt": result.config.dt,
                            "elapsed_s": result.elapsed_s,
                            "steps_per_second": result.steps_per_second,
                            "vehicles_per_second": result.vehicles_per_second,
                            "efficiency": result.efficiency,
                            "avg_frame_ms": result.avg_frame_ms,
                            "p95_frame_ms": result.p95_frame_ms,
                            "cpu_percent": result.cpu_percent,
                            "memory_mb": result.memory_mb,
                            "theoretical_fps": result.theoretical_fps,
                            "theoretical_throughput": result.theoretical_throughput,
                            "confidence_score": result.confidence_score,
                        }
                    )

        print(f"\nResults written to {output_csv}")

        # Print summary
        print("\n=== Performance Summary ===")
        print("Vehicles | Speed | Steps/s | V·S/s | Efficiency | Theoretical FPS")
        print("---------|-------|---------|-------|-----------|----------------")
        for result in results:
            theoretical_fps_str = (
                f"{result.theoretical_fps:.1f}" if result.theoretical_fps else "N/A"
            )
            print(
                f"{result.config.vehicles:8d} | {result.config.speed_factor:5.1f} | "
                f"{result.steps_per_second:7.1f} | {result.vehicles_per_second:5.0f} | "
                f"{result.efficiency:10.2f} | {theoretical_fps_str:15s}"
            )

        return results


class BenchmarkingFramework:
    """Unified benchmarking framework for all performance testing."""

    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or cpu_count()
        self.runner = BenchmarkRunner(max_workers=self.max_workers)
        self.system_monitor = SystemMonitor()

    def run_benchmark(
        self, vehicles: int, steps: int, dt: float = 0.02, speed_factor: float = 1.0
    ) -> BenchmarkResult:
        """Run a single high-performance benchmark."""
        config = BenchmarkConfig(
            vehicles=vehicles,
            steps=steps,
            dt=dt,
            speed_factor=speed_factor,
            enable_high_performance=True,
            enable_data_manager=True,
            enable_vectorized_idm=True,
        )

        return self.runner.run_single_benchmark(config)

    def run_scale_benchmark(
        self,
        vehicle_counts: List[int],
        speed_factors: List[float],
        steps: int = 1000,
        dt: float = 0.02,
        output_csv: str = "runs/scaling/scale_benchmark.csv",
    ) -> List[BenchmarkResult]:
        """Run comprehensive scale benchmarks."""
        return self.runner.run_scale_benchmark(vehicle_counts, speed_factors, steps, dt, output_csv)

    def run_monitoring(
        self, duration_minutes: int = 5, vehicles: int = 100, speed_factor: float = 1.0
    ) -> List[BenchmarkResult]:
        """Run performance monitoring for specified duration."""
        print(f"Starting performance monitoring for {duration_minutes} minutes...")

        results = []
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)

        while time.time() < end_time:
            config = BenchmarkConfig(
                vehicles=vehicles, steps=1, dt=0.02, speed_factor=speed_factor, warmup_steps=0
            )

            result = self.runner.run_single_benchmark(config)
            results.append(result)

            # Print status every 10 steps
            if len(results) % 10 == 0:
                print(
                    f"Step {len(results)}: "
                    f"{result.steps_per_second:.1f} steps/s, "
                    f"{result.memory_mb:.1f} MB, "
                    f"{result.cpu_percent:.1f}% CPU"
                )

        self._print_monitoring_summary(results)
        return results

    def run_profiling(
        self,
        vehicles: int = 100,
        steps: int = 1000,
        dt: float = 0.02,
        speed_factor: float = 1.0,
        output_csv: str = "runs/profiling/profiling_stats.csv",
    ) -> BenchmarkResult:
        """Run profiling benchmark with detailed analysis."""

        # Enable profiling
        config = BenchmarkConfig(
            vehicles=vehicles,
            steps=steps,
            dt=dt,
            speed_factor=speed_factor,
            enable_profiling=True,
            enable_high_performance=True,
            enable_data_manager=True,
            enable_vectorized_idm=True,
        )

        # Start memory tracing
        tracemalloc.start()

        result = self.runner.run_single_benchmark(config)

        # Dump profiling data
        if result.profile_data:
            with open(output_csv, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["name", "total_s", "count", "avg_ms"])
                for name, stats in result.profile_data.items():
                    writer.writerow(
                        [
                            name,
                            f"{stats['total_s']:.9f}",
                            int(stats["count"]),
                            f"{stats['avg_ms']:.3f}",
                        ]
                    )
            print(f"Profiling data written to {output_csv}")

        return result

    def _print_monitoring_summary(self, results: List[BenchmarkResult]):
        """Print performance monitoring summary."""
        if not results:
            return

        avg_fps = sum(r.steps_per_second for r in results) / len(results)
        max_memory = max(r.memory_mb for r in results)
        avg_cpu = sum(r.cpu_percent for r in results) / len(results)

        print("\n=== Performance Summary ===")
        print(f"Average FPS: {avg_fps:.1f} steps/s")
        print(f"Peak Memory: {max_memory:.1f} MB")
        print(f"Average CPU: {avg_cpu:.1f}%")

        # Theoretical performance summary
        theoretical_fps_values = [r.theoretical_fps for r in results if r.theoretical_fps]
        if theoretical_fps_values:
            avg_theoretical = sum(theoretical_fps_values) / len(theoretical_fps_values)
            print(f"Average Theoretical FPS: {avg_theoretical:.1f}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Unified Benchmarking Framework")
    parser.add_argument(
        "--mode",
        choices=["benchmark", "scale", "monitor", "profile"],
        default="benchmark",
        help="Benchmark mode: benchmark (single), scale (comprehensive), monitor (real-time), profile (detailed)",
    )

    # Benchmark mode arguments
    parser.add_argument("--vehicles", type=int, default=100, help="Number of vehicles")
    parser.add_argument("--steps", type=int, default=1000, help="Number of steps")
    parser.add_argument("--dt", type=float, default=0.02, help="Delta time per step")
    parser.add_argument("--speed-factor", type=float, default=1.0, help="Speed factor")

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
    parser.add_argument(
        "--output", default="runs/scaling/scale_benchmark.csv", help="Output CSV file"
    )

    # Monitor mode arguments
    parser.add_argument(
        "--duration", "-d", type=int, default=5, help="Monitoring duration in minutes"
    )

    # Profile mode arguments
    parser.add_argument(
        "--profile-csv", default="runs/profiling/profiling_stats.csv", help="Profile output CSV"
    )

    # Parallel execution
    parser.add_argument("--max-workers", type=int, help="Maximum parallel workers")

    args = parser.parse_args()

    try:
        framework = BenchmarkingFramework(max_workers=args.max_workers)

        if args.mode == "benchmark":
            # Single benchmark mode
            result = framework.run_benchmark(args.vehicles, args.steps, args.dt, args.speed_factor)
            print(
                f"vehicles={result.config.vehicles} steps={result.config.steps} "
                f"dt={result.config.dt:.3f} sf={result.config.speed_factor:.1f} "
                f"total={result.elapsed_s:.3f}s fps={result.steps_per_second:.1f} "
                f"avg={result.avg_frame_ms:.3f}ms p95={result.p95_frame_ms:.3f}ms"
            )
            if result.theoretical_fps:
                print(
                    f"theoretical_fps={result.theoretical_fps:.1f} confidence={result.confidence_score:.2f}"
                )

        elif args.mode == "scale":
            # Scale benchmark mode
            framework.run_scale_benchmark(
                vehicle_counts=args.vehicle_counts,
                speed_factors=args.speed_factors,
                steps=args.steps,
                dt=args.dt,
                output_csv=args.output,
            )

        elif args.mode == "monitor":
            # Performance monitoring mode
            framework.run_monitoring(
                duration_minutes=args.duration,
                vehicles=args.vehicles,
                speed_factor=args.speed_factor,
            )

        elif args.mode == "profile":
            # Profiling mode
            result = framework.run_profiling(
                vehicles=args.vehicles,
                steps=args.steps,
                dt=args.dt,
                speed_factor=args.speed_factor,
                output_csv=args.profile_csv,
            )
            print(f"Profiling completed: {result.elapsed_s:.3f}s for {args.steps} steps")

    except KeyboardInterrupt:
        print("\n⏹️  Benchmarking interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error in benchmarking: {e}")
        sys.exit(1)


def ensure_runs_directory():
    """Ensure the runs directory structure exists."""
    runs_dir = Path("runs")
    runs_dir.mkdir(exist_ok=True)

    # Create subdirectories
    for subdir in ["profiling", "benchmarks", "performance", "scaling"]:
        (runs_dir / subdir).mkdir(exist_ok=True)


if __name__ == "__main__":
    ensure_runs_directory()
    main()
