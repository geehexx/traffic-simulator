#!/usr/bin/env python3
"""
Optimized Benchmarking Framework for Traffic Simulator
Fixes multiprocessing issues and adds performance optimizations.

Usage:
    python scripts/benchmarking_framework_optimized.py --mode=benchmark
    python scripts/benchmarking_framework_optimized.py --mode=scale
    python scripts/benchmarking_framework_optimized.py --mode=monitor
    python scripts/benchmarking_framework_optimized.py --mode=profile
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import statistics
import sys
import time
import tracemalloc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import threading

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation

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


class OptimizedBenchmarkRunner:
    """Optimized benchmark runner with threading instead of multiprocessing."""

    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.lock = threading.Lock()

    def run_single_benchmark(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Run a single benchmark with optimizations."""
        print(f"Running benchmark: {config.vehicles} vehicles, {config.steps} steps")

        # Load configuration with overrides
        sim_config = load_config()
        sim_config.update(config.config_overrides)

        # Set benchmark-specific config
        sim_config["vehicles"]["count"] = config.vehicles
        sim_config["physics"]["speed_factor"] = config.speed_factor
        sim_config["high_performance"]["enabled"] = config.enable_high_performance
        sim_config["data_manager"]["enabled"] = config.enable_data_manager
        # Only set IDM config if it exists
        if "idm" in sim_config:
            sim_config["idm"]["vectorized"] = config.enable_vectorized_idm

        # Initialize simulation
        simulation = Simulation(sim_config)

        # Warmup
        if config.warmup_steps > 0:
            for _ in range(config.warmup_steps):
                simulation.step(config.dt)

        # Reset for actual benchmark
        simulation = Simulation(sim_config)

        # Start monitoring
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024

        if config.enable_profiling:
            tracemalloc.start()

        # Run benchmark
        frame_times = []
        for step in range(config.steps):
            step_start = time.time()
            simulation.step(config.dt)
            frame_times.append((time.time() - step_start) * 1000)

        # Stop monitoring
        elapsed_s = time.time() - start_time
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_mb = end_memory - start_memory

        # Calculate metrics
        steps_per_second = config.steps / elapsed_s
        vehicles_per_second = (config.vehicles * config.steps) / elapsed_s
        efficiency = steps_per_second / config.vehicles

        # Frame time statistics
        avg_frame_ms = statistics.mean(frame_times)
        p95_frame_ms = statistics.quantiles(frame_times, n=20)[18]  # 95th percentile

        # CPU usage
        cpu_percent = psutil.cpu_percent()

        # Theoretical performance
        theoretical_fps = 1000 / avg_frame_ms if avg_frame_ms > 0 else 0
        theoretical_throughput = theoretical_fps * config.vehicles

        # Confidence score based on consistency
        frame_std = statistics.stdev(frame_times) if len(frame_times) > 1 else 0
        confidence_score = max(0, 1 - (frame_std / avg_frame_ms)) if avg_frame_ms > 0 else 0

        # Profile data
        profile_data = None
        memory_profile = None

        if config.enable_profiling:
            tracemalloc.stop()
            current, peak = tracemalloc.get_traced_memory()
            memory_profile = {
                "current_mb": current / 1024 / 1024,
                "peak_mb": peak / 1024 / 1024,
                "memory_delta_mb": memory_mb,
            }

        result = BenchmarkResult(
            config=config,
            elapsed_s=elapsed_s,
            steps_per_second=steps_per_second,
            vehicles_per_second=vehicles_per_second,
            efficiency=efficiency,
            avg_frame_ms=avg_frame_ms,
            p95_frame_ms=p95_frame_ms,
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            theoretical_fps=theoretical_fps,
            theoretical_throughput=theoretical_throughput,
            confidence_score=confidence_score,
            profile_data=profile_data,
            memory_profile=memory_profile,
        )

        with self.lock:
            self.results.append(result)

        return result

    def run_parallel_benchmarks(
        self, configs: List[BenchmarkConfig], max_workers: int = 2
    ) -> List[BenchmarkResult]:
        """Run multiple benchmarks in parallel using threading."""
        print(f"Running {len(configs)} benchmarks in parallel with {max_workers} workers...")

        results = []

        # Use threading instead of multiprocessing to avoid pickle issues
        with threading.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.run_single_benchmark, config): config for config in configs
            }

            for future in futures:
                try:
                    result = future.result()
                    results.append(result)
                    print(
                        f"✅ Benchmark completed: {result.config.vehicles} vehicles, {result.steps_per_second:.1f} steps/s"
                    )
                except Exception as e:
                    config = futures[future]
                    print(f"❌ Benchmark failed for {config.vehicles} vehicles: {e}")

        return results

    def run_scale_benchmark(
        self,
        vehicle_counts: List[int],
        speed_factors: List[float],
        steps: int,
        dt: float,
        output_csv: str = None,
    ) -> List[BenchmarkResult]:
        """Run scale benchmark with multiple vehicle counts and speed factors."""
        print("=== Traffic Simulator Scale Benchmark ===")
        print(f"Testing {len(vehicle_counts)} vehicle counts × {len(speed_factors)} speed factors")
        print(f"Steps per test: {steps}, dt: {dt}")

        # Generate all combinations
        configs = []
        for vehicles in vehicle_counts:
            for speed_factor in speed_factors:
                configs.append(
                    BenchmarkConfig(
                        vehicles=vehicles,
                        steps=steps,
                        dt=dt,
                        speed_factor=speed_factor,
                        warmup_steps=min(50, steps // 10),  # Adaptive warmup
                        iterations=1,
                    )
                )

        print("Parallel execution with 2 workers")
        results = self.run_parallel_benchmarks(configs, max_workers=2)

        # Save results
        if output_csv:
            self.save_results_csv(results, output_csv)

        # Print summary
        self.print_scale_summary(results)

        return results

    def save_results_csv(self, results: List[BenchmarkResult], filename: str):
        """Save benchmark results to CSV."""
        with open(filename, "w", newline="") as csvfile:
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
                "confidence_score",
                "timestamp",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
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
                        "confidence_score": result.confidence_score,
                        "timestamp": result.timestamp,
                    }
                )

        print(f"Results written to {filename}")

    def print_scale_summary(self, results: List[BenchmarkResult]):
        """Print scale benchmark summary."""
        print("\n=== Performance Summary ===")
        print("Vehicles | Speed | Steps/s | V·S/s | Efficiency | Theoretical FPS")
        print("---------|-------|---------|-------|-----------|----------------")

        for result in results:
            print(
                f"{result.config.vehicles:8d} | {result.config.speed_factor:5.1f} | "
                f"{result.steps_per_second:7.1f} | {result.vehicles_per_second:6.1f} | "
                f"{result.efficiency:10.3f} | {result.theoretical_fps:15.1f}"
            )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Optimized benchmarking framework")
    parser.add_argument(
        "--mode",
        choices=["benchmark", "scale", "monitor", "profile"],
        default="benchmark",
        help="Benchmark mode",
    )
    parser.add_argument("--vehicles", type=int, default=20, help="Number of vehicles")
    parser.add_argument("--steps", type=int, default=1000, help="Number of simulation steps")
    parser.add_argument("--dt", type=float, default=0.02, help="Time step")
    parser.add_argument("--speed-factor", type=float, default=1.0, help="Speed factor")
    parser.add_argument(
        "--vehicle-counts",
        nargs="+",
        type=int,
        default=[10, 20, 50],
        help="Vehicle counts for scale benchmark",
    )
    parser.add_argument(
        "--speed-factors",
        nargs="+",
        type=float,
        default=[1.0, 2.0],
        help="Speed factors for scale benchmark",
    )
    parser.add_argument("--output", "-o", help="Output CSV file")
    parser.add_argument("--workers", type=int, default=2, help="Number of parallel workers")

    args = parser.parse_args()

    # Ensure runs directory exists
    runs_dir = Path("runs")
    runs_dir.mkdir(exist_ok=True)
    for subdir in ["profiling", "benchmarks", "performance", "scaling"]:
        (runs_dir / subdir).mkdir(exist_ok=True)

    runner = OptimizedBenchmarkRunner()

    try:
        if args.mode == "benchmark":
            config = BenchmarkConfig(
                vehicles=args.vehicles, steps=args.steps, dt=args.dt, speed_factor=args.speed_factor
            )
            result = runner.run_single_benchmark(config)
            print(f"\nBenchmark completed: {result.steps_per_second:.1f} steps/s")

        elif args.mode == "scale":
            output_file = args.output or f"runs/scaling/scale_benchmark_{int(time.time())}.csv"
            runner.run_scale_benchmark(
                vehicle_counts=args.vehicle_counts,
                speed_factors=args.speed_factors,
                steps=args.steps,
                dt=args.dt,
                output_csv=output_file,
            )

        else:
            print(f"Mode '{args.mode}' not yet implemented in optimized version")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️  Benchmark interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error in benchmark: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
