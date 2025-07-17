#!/usr/bin/env python3
"""
Fixed Benchmarking Framework for Traffic Simulator

This framework uses proper multiprocessing with headless simulation to avoid
pickle errors while maintaining true parallelism across CPU cores.

Usage:
    python scripts/benchmarking_framework_fixed.py --mode=benchmark
    python scripts/benchmarking_framework_fixed.py --mode=scale
    python scripts/benchmarking_framework_fixed.py --mode=monitor
    python scripts/benchmarking_framework_fixed.py --mode=profile
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation_headless import SimulationHeadless

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


def run_single_benchmark_worker(config: BenchmarkConfig) -> BenchmarkResult:
    """Worker function for running a single benchmark (pickle-safe)."""
    print(f"Running benchmark: {config.vehicles} vehicles, {config.steps} steps")

    # Load configuration with overrides
    sim_config = load_config()
    sim_config.update(config.config_overrides)

    # Set benchmark-specific config
    sim_config["vehicles"]["count"] = config.vehicles
    sim_config["physics"]["speed_factor"] = config.speed_factor
    sim_config["high_performance"]["enabled"] = config.enable_high_performance
    sim_config["data_manager"]["enabled"] = config.enable_data_manager
    sim_config["profiling"]["enabled"] = config.enable_profiling

    # Only set IDM config if it exists
    if "idm" in sim_config:
        sim_config["idm"]["vectorized"] = config.enable_vectorized_idm

    # Initialize headless simulation
    simulation = SimulationHeadless(sim_config)

    # Warmup
    for _ in range(config.warmup_steps):
        simulation.step(config.dt)

    # Reset timing for actual benchmark
    start_time = time.perf_counter()
    start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

    # Run benchmark
    for _ in range(config.steps):
        simulation.step(config.dt)

    # Calculate metrics
    end_time = time.perf_counter()
    end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

    elapsed_s = end_time - start_time
    steps_per_second = config.steps / elapsed_s
    vehicles_per_second = (config.vehicles * config.steps) / elapsed_s
    efficiency = steps_per_second / (config.vehicles * 1000)  # Normalized efficiency
    avg_frame_ms = (elapsed_s / config.steps) * 1000
    p95_frame_ms = avg_frame_ms * 1.2  # Approximate P95
    cpu_percent = psutil.cpu_percent()
    memory_mb = end_memory - start_memory

    # Extract profile data if available
    profile_data = None
    if config.enable_profiling and hasattr(simulation, "_profiler") and simulation._profiler:
        profile_data = simulation._profiler.get_stats()

    # Memory profile
    memory_profile = {
        "start_mb": start_memory,
        "end_mb": end_memory,
        "peak_mb": end_memory,
        "delta_mb": memory_mb,
    }

    return BenchmarkResult(
        config=config,
        elapsed_s=elapsed_s,
        steps_per_second=steps_per_second,
        vehicles_per_second=vehicles_per_second,
        efficiency=efficiency,
        avg_frame_ms=avg_frame_ms,
        p95_frame_ms=p95_frame_ms,
        cpu_percent=cpu_percent,
        memory_mb=memory_mb,
        profile_data=profile_data,
        memory_profile=memory_profile,
    )


class FixedBenchmarkRunner:
    """Fixed benchmark runner with proper multiprocessing."""

    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or min(cpu_count(), 4)  # Limit to 4 workers for stability

    def run_single_benchmark(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Run a single benchmark."""
        return run_single_benchmark_worker(config)

    def run_parallel_benchmarks(self, configs: List[BenchmarkConfig]) -> List[BenchmarkResult]:
        """Run multiple benchmarks in parallel using multiprocessing."""
        print(f"Running {len(configs)} benchmarks in parallel with {self.max_workers} workers...")

        results = []
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(run_single_benchmark_worker, config): config for config in configs
            }

            for future in futures:
                try:
                    result = future.result(timeout=300)  # 5 minute timeout
                    results.append(result)
                    print(f"✓ Benchmark completed: {result.config.vehicles} vehicles")
                except Exception as e:
                    config = futures[future]
                    print(f"✗ Benchmark failed for {config.vehicles} vehicles: {e}")

        return results

    def run_scale_benchmark(
        self,
        vehicle_counts: List[int],
        speed_factors: List[float],
        steps: int,
        dt: float,
        output_csv: str,
    ) -> List[BenchmarkResult]:
        """Run scale benchmarking across vehicle counts and speed factors."""
        print("=== Traffic Simulator Scale Benchmark ===")
        print(f"Testing {len(vehicle_counts)} vehicle counts × {len(speed_factors)} speed factors")
        print(f"Steps per test: {steps}, dt: {dt}")
        print(f"Parallel execution with {self.max_workers} workers")

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
                    )
                )

        # Run benchmarks
        results = self.run_parallel_benchmarks(configs)

        # Save results to CSV
        self._save_results_to_csv(results, output_csv)

        # Print summary
        self._print_scale_summary(results)

        return results

    def _save_results_to_csv(self, results: List[BenchmarkResult], filename: str) -> None:
        """Save benchmark results to CSV file."""
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "vehicles",
                    "speed_factor",
                    "steps",
                    "elapsed_s",
                    "steps_per_second",
                    "vehicles_per_second",
                    "efficiency",
                    "avg_frame_ms",
                    "cpu_percent",
                    "memory_mb",
                ]
            )

            for result in results:
                writer.writerow(
                    [
                        result.config.vehicles,
                        result.config.speed_factor,
                        result.config.steps,
                        result.elapsed_s,
                        result.steps_per_second,
                        result.vehicles_per_second,
                        result.efficiency,
                        result.avg_frame_ms,
                        result.cpu_percent,
                        result.memory_mb,
                    ]
                )

        print(f"Results written to {filename}")

    def _print_scale_summary(self, results: List[BenchmarkResult]) -> None:
        """Print scale benchmark summary."""
        print("\n=== Performance Summary ===")
        print(
            f"{'Vehicles':<10} {'Speed':<8} {'Steps/s':<10} {'V·S/s':<10} {'Efficiency':<12} {'Theoretical FPS':<15}"
        )
        print("-" * 80)

        for result in results:
            theoretical_fps = result.theoretical_fps or 0.0
            print(
                f"{result.config.vehicles:<10} {result.config.speed_factor:<8.1f} "
                f"{result.steps_per_second:<10.1f} {result.vehicles_per_second:<10.1f} "
                f"{result.efficiency:<12.3f} {theoretical_fps:<15.1f}"
            )


class FixedBenchmarkingFramework:
    """Fixed benchmarking framework with proper multiprocessing."""

    def __init__(self, max_workers: Optional[int] = None):
        self.runner = FixedBenchmarkRunner(max_workers)

    def run_benchmark(
        self, vehicles: int, steps: int, dt: float = 0.02, speed_factor: float = 1.0, **kwargs
    ) -> BenchmarkResult:
        """Run a single benchmark."""
        config = BenchmarkConfig(
            vehicles=vehicles, steps=steps, dt=dt, speed_factor=speed_factor, **kwargs
        )
        return self.runner.run_single_benchmark(config)

    def run_scale_benchmark(
        self,
        vehicle_counts: List[int],
        speed_factors: List[float],
        steps: int,
        dt: float,
        output_csv: str,
    ) -> List[BenchmarkResult]:
        """Run scale benchmarking."""
        return self.runner.run_scale_benchmark(vehicle_counts, speed_factors, steps, dt, output_csv)

    def run_parallel_benchmarks(self, configs: List[BenchmarkConfig]) -> List[BenchmarkResult]:
        """Run parallel benchmarks."""
        return self.runner.run_parallel_benchmarks(configs)


def main():
    """Main entry point for the benchmarking framework."""
    parser = argparse.ArgumentParser(description="Fixed Benchmarking Framework")
    parser.add_argument(
        "--mode",
        choices=["benchmark", "scale", "monitor", "profile"],
        default="benchmark",
        help="Benchmarking mode",
    )
    parser.add_argument("--vehicles", type=int, default=100, help="Number of vehicles")
    parser.add_argument("--steps", type=int, default=1000, help="Number of simulation steps")
    parser.add_argument("--dt", type=float, default=0.02, help="Time step (seconds)")
    parser.add_argument("--speed-factor", type=float, default=1.0, help="Speed factor")
    parser.add_argument(
        "--vehicle-counts",
        nargs="+",
        type=int,
        default=[20, 50, 100],
        help="Vehicle counts for scale testing",
    )
    parser.add_argument(
        "--speed-factors",
        nargs="+",
        type=float,
        default=[1.0, 2.0, 5.0],
        help="Speed factors for scale testing",
    )
    parser.add_argument(
        "--output", type=str, default="benchmark_results.csv", help="Output CSV file"
    )
    parser.add_argument("--workers", type=int, default=None, help="Number of worker processes")

    args = parser.parse_args()

    framework = FixedBenchmarkingFramework(max_workers=args.workers)

    if args.mode == "benchmark":
        result = framework.run_benchmark(
            vehicles=args.vehicles, steps=args.steps, dt=args.dt, speed_factor=args.speed_factor
        )
        print(f"Benchmark completed: {result.steps_per_second:.1f} steps/s")

    elif args.mode == "scale":
        results = framework.run_scale_benchmark(
            vehicle_counts=args.vehicle_counts,
            speed_factors=args.speed_factors,
            steps=args.steps,
            dt=args.dt,
            output_csv=args.output,
        )
        print(f"Scale benchmark completed: {len(results)} tests")

    else:
        print(f"Mode '{args.mode}' not yet implemented")


if __name__ == "__main__":
    main()
