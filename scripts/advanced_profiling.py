#!/usr/bin/env python3
"""
Advanced Profiling and Memory Analysis Tools

Provides comprehensive profiling capabilities including memory analysis,
performance prediction, and scaling behavior modeling.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any, Dict, List
from dataclasses import dataclass, field

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation
from traffic_sim.core.profiling import get_profiler

try:
    import psutil
except ImportError:
    psutil = None

try:
    import numpy as np
except ImportError:
    np = None


@dataclass
class MemoryProfile:
    """Memory usage profile data."""

    current_mb: float
    peak_mb: float
    allocated_objects: int
    memory_growth_rate: float
    memory_leaks: List[Dict[str, Any]] = field(default_factory=list)
    heap_analysis: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformancePrediction:
    """Performance prediction for different scales."""

    target_vehicles: int
    predicted_fps: float
    predicted_memory_mb: float
    confidence_score: float
    scaling_factor: float
    bottleneck_type: str  # "cpu", "memory", "io", "cache"


@dataclass
class ScalingModel:
    """Scaling behavior model."""

    vehicle_counts: List[int]
    performance_metrics: List[float]
    scaling_coefficient: float
    complexity_order: str  # "linear", "quadratic", "logarithmic", "exponential"
    r_squared: float
    prediction_accuracy: float


class MemoryProfiler:
    """Advanced memory profiling with tracemalloc."""

    def __init__(self):
        self.snapshots: List[tracemalloc.Snapshot] = []
        self.start_tracing()

    def start_tracing(self):
        """Start memory tracing."""
        if not tracemalloc.is_tracing():
            tracemalloc.start()

    def take_snapshot(self, label: str = "") -> tracemalloc.Snapshot:
        """Take a memory snapshot."""
        snapshot = tracemalloc.take_snapshot()
        self.snapshots.append(snapshot)
        return snapshot

    def analyze_memory_usage(
        self, simulation: Simulation, duration_steps: int = 1000
    ) -> MemoryProfile:
        """Analyze memory usage during simulation."""

        # Take initial snapshot
        initial_snapshot = self.take_snapshot("initial")

        # Run simulation with periodic snapshots
        snapshot_interval = duration_steps // 10
        for i in range(duration_steps):
            simulation.step(0.02)

            if i % snapshot_interval == 0:
                self.take_snapshot(f"step_{i}")

        # Take final snapshot
        final_snapshot = self.take_snapshot("final")

        # Analyze memory usage
        current, peak = tracemalloc.get_traced_memory()

        # Calculate memory growth rate
        initial_size = len(initial_snapshot.traces)
        final_size = len(final_snapshot.traces)
        growth_rate = (
            float(final_size - initial_size) / duration_steps if duration_steps > 0 else 0.0
        )

        # Detect potential memory leaks
        memory_leaks = self._detect_memory_leaks(initial_snapshot, final_snapshot)

        # Heap analysis
        heap_analysis = self._analyze_heap_usage(final_snapshot)

        return MemoryProfile(
            current_mb=current / (1024 * 1024),
            peak_mb=peak / (1024 * 1024),
            allocated_objects=len(final_snapshot.traces),
            memory_growth_rate=growth_rate,
            memory_leaks=memory_leaks,
            heap_analysis=heap_analysis,
        )

    def _detect_memory_leaks(
        self, initial: tracemalloc.Snapshot, final: tracemalloc.Snapshot
    ) -> List[Dict[str, Any]]:
        """Detect potential memory leaks."""
        leaks = []

        # Compare snapshots to find growing allocations
        top_stats = final.compare_to(initial, "lineno")

        for stat in top_stats[:10]:  # Top 10 growing allocations
            if stat.size_diff > 1024:  # Growing by more than 1KB
                leaks.append(
                    {
                        "size_diff_kb": stat.size_diff / 1024,
                        "count_diff": stat.count_diff,
                        "traceback": str(stat.traceback),
                        "severity": "high" if stat.size_diff > 10240 else "medium",
                    }
                )

        return leaks

    def _analyze_heap_usage(self, snapshot: tracemalloc.Snapshot) -> Dict[str, Any]:
        """Analyze heap usage patterns."""
        stats = snapshot.statistics("lineno")

        total_size = sum(stat.size for stat in stats)
        total_count = sum(stat.count for stat in stats)

        # Find largest allocations
        largest_allocations = sorted(stats, key=lambda x: x.size, reverse=True)[:5]

        return {
            "total_size_mb": total_size / (1024 * 1024),
            "total_objects": total_count,
            "average_size_bytes": total_size / total_count if total_count > 0 else 0,
            "largest_allocations": [
                {
                    "size_mb": stat.size / (1024 * 1024),
                    "count": stat.count,
                    "traceback": str(stat.traceback),
                }
                for stat in largest_allocations
            ],
        }

    def generate_memory_report(self, output_file: str = "memory_report.json"):
        """Generate comprehensive memory report."""
        if not self.snapshots:
            return

        report = {
            "snapshot_count": len(self.snapshots),
            "memory_timeline": [],
            "peak_usage": 0.0,
            "total_growth": 0.0,
        }

        for i, _ in enumerate(self.snapshots):
            current, peak = tracemalloc.get_traced_memory()
            report["memory_timeline"].append(
                {"step": i, "current_mb": current / (1024 * 1024), "peak_mb": peak / (1024 * 1024)}
            )
            report["peak_usage"] = max(report["peak_usage"], peak / (1024 * 1024))

        if len(self.snapshots) > 1:
            initial_size = len(self.snapshots[0].traces)
            final_size = len(self.snapshots[-1].traces)
            report["total_growth"] = (final_size - initial_size) / (1024 * 1024)

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"Memory report generated: {output_file}")


class PerformancePredictor:
    """Predict performance under different conditions."""

    def __init__(self):
        self.scaling_models: Dict[str, ScalingModel] = {}

    def build_scaling_model(
        self, vehicle_counts: List[int], performance_metrics: List[float]
    ) -> ScalingModel:
        """Build a scaling model from benchmark data."""

        if np is None:
            # Fallback to simple linear model
            if len(vehicle_counts) < 2:
                return ScalingModel(
                    vehicle_counts=vehicle_counts,
                    performance_metrics=performance_metrics,
                    scaling_coefficient=1.0,
                    complexity_order="linear",
                    r_squared=1.0,
                    prediction_accuracy=1.0,
                )

            # Simple linear regression
            n = len(vehicle_counts)
            sum_x = sum(vehicle_counts)
            sum_y = sum(performance_metrics)
            sum_xy = sum(x * y for x, y in zip(vehicle_counts, performance_metrics))
            sum_x2 = sum(x * x for x in vehicle_counts)

            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n

            # Calculate R-squared
            y_mean = sum_y / n
            ss_tot = sum((y - y_mean) ** 2 for y in performance_metrics)
            ss_res = sum(
                (y - (slope * x + intercept)) ** 2
                for x, y in zip(vehicle_counts, performance_metrics)
            )
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

            return ScalingModel(
                vehicle_counts=vehicle_counts,
                performance_metrics=performance_metrics,
                scaling_coefficient=slope,
                complexity_order="linear",
                r_squared=r_squared,
                prediction_accuracy=r_squared,
            )

        # Use NumPy for more sophisticated analysis
        if np is not None and hasattr(np, "array"):
            x = np.array(vehicle_counts)
            y = np.array(performance_metrics)
        else:
            # Fallback to simple analysis
            return ScalingModel(
                vehicle_counts=vehicle_counts,
                performance_metrics=performance_metrics,
                scaling_coefficient=1.0,
                complexity_order="linear",
                r_squared=1.0,
                prediction_accuracy=1.0,
            )

        # Try different complexity models
        models = {
            "linear": np.polyfit(x, y, 1),
            "quadratic": np.polyfit(x, y, 2),
            "logarithmic": np.polyfit(np.log(x + 1), y, 1),
        }

        best_model = "linear"
        best_r_squared = 0

        for model_name, coeffs in models.items():
            if model_name == "linear":
                predicted = coeffs[0] * x + coeffs[1]
            elif model_name == "quadratic":
                predicted = coeffs[0] * x**2 + coeffs[1] * x + coeffs[2]
            elif model_name == "logarithmic":
                predicted = coeffs[0] * np.log(x + 1) + coeffs[1]

            ss_res = np.sum((y - predicted) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

            if r_squared > best_r_squared:
                best_r_squared = r_squared
                best_model = model_name

        return ScalingModel(
            vehicle_counts=vehicle_counts,
            performance_metrics=performance_metrics,
            scaling_coefficient=float(models[best_model][0]),
            complexity_order=best_model,
            r_squared=best_r_squared,
            prediction_accuracy=best_r_squared,
        )

    def predict_performance(
        self, model: ScalingModel, target_vehicles: int
    ) -> PerformancePrediction:
        """Predict performance for a given number of vehicles."""

        if model.complexity_order == "linear":
            predicted_fps = model.scaling_coefficient * target_vehicles + model.scaling_coefficient
        elif model.complexity_order == "quadratic":
            predicted_fps = model.scaling_coefficient * target_vehicles**2
        elif model.complexity_order == "logarithmic":
            if np is not None:
                predicted_fps = model.scaling_coefficient * np.log(target_vehicles + 1)
            else:
                predicted_fps = model.scaling_coefficient * target_vehicles
        else:
            predicted_fps = model.scaling_coefficient * target_vehicles

        # Estimate memory usage (rough approximation)
        predicted_memory = target_vehicles * 0.5  # 0.5 MB per vehicle

        # Determine bottleneck type
        bottleneck_type = "cpu"
        if predicted_memory > 1000:  # More than 1GB
            bottleneck_type = "memory"
        elif target_vehicles > 1000:
            bottleneck_type = "cache"

        return PerformancePrediction(
            target_vehicles=target_vehicles,
            predicted_fps=max(0, predicted_fps),
            predicted_memory_mb=predicted_memory,
            confidence_score=model.prediction_accuracy,
            scaling_factor=model.scaling_coefficient,
            bottleneck_type=bottleneck_type,
        )

    def analyze_scaling_behavior(self, benchmark_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze scaling behavior from benchmark results."""

        # Extract data
        vehicle_counts = [r["vehicles"] for r in benchmark_results]
        performance_metrics = [r["steps_per_second"] for r in benchmark_results]

        # Build scaling model
        model = self.build_scaling_model(vehicle_counts, performance_metrics)

        # Generate predictions for different scales
        prediction_scales = [100, 500, 1000, 2000, 5000]
        predictions = []

        for scale in prediction_scales:
            pred = self.predict_performance(model, scale)
            predictions.append(
                {
                    "vehicles": scale,
                    "predicted_fps": pred.predicted_fps,
                    "predicted_memory_mb": pred.predicted_memory_mb,
                    "confidence_score": pred.confidence_score,
                    "bottleneck_type": pred.bottleneck_type,
                }
            )

        return {
            "scaling_model": {
                "complexity_order": model.complexity_order,
                "scaling_coefficient": model.scaling_coefficient,
                "r_squared": model.r_squared,
                "prediction_accuracy": model.prediction_accuracy,
            },
            "predictions": predictions,
            "raw_data": {
                "vehicle_counts": vehicle_counts,
                "performance_metrics": performance_metrics,
            },
        }


class AdvancedProfiler:
    """Advanced profiling with comprehensive analysis."""

    def __init__(self):
        self.memory_profiler = MemoryProfiler()
        self.performance_predictor = PerformancePredictor()

    def run_comprehensive_analysis(
        self, vehicles: int = 100, steps: int = 1000, output_dir: str = "profiling_analysis"
    ) -> Dict[str, Any]:
        """Run comprehensive profiling analysis."""

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Load configuration
        config = load_config()
        config["vehicles"]["count"] = vehicles
        config["high_performance"]["enabled"] = True
        config["data_manager"]["enabled"] = True
        config["profiling"]["enabled"] = True

        # Create simulation
        sim = Simulation(config)

        # Memory analysis
        print("Running memory analysis...")
        memory_profile = self.memory_profiler.analyze_memory_usage(sim, steps)

        # Generate memory report
        memory_report_file = output_path / "memory_report.json"
        self.memory_profiler.generate_memory_report(str(memory_report_file))

        # Performance profiling
        print("Running performance profiling...")
        profiler = get_profiler(reset=True)

        start_time = time.perf_counter()
        for _ in range(steps):
            sim.step(0.02)
        elapsed = time.perf_counter() - start_time

        # Get profiling stats
        profile_stats = profiler.get_stats()

        # Save profiling data
        profile_file = output_path / "profile_stats.csv"
        profiler.dump_csv(str(profile_file))

        # System metrics
        system_metrics = {}
        if psutil:
            process = psutil.Process()
            system_metrics = {
                "cpu_percent": process.cpu_percent(),
                "memory_mb": process.memory_info().rss / (1024 * 1024),
                "num_threads": process.num_threads(),
                "create_time": process.create_time(),
            }

        # Compile results
        results = {
            "simulation_config": {"vehicles": vehicles, "steps": steps, "elapsed_s": elapsed},
            "memory_profile": {
                "current_mb": memory_profile.current_mb,
                "peak_mb": memory_profile.peak_mb,
                "allocated_objects": memory_profile.allocated_objects,
                "memory_growth_rate": memory_profile.memory_growth_rate,
                "memory_leaks": memory_profile.memory_leaks,
            },
            "performance_profile": profile_stats,
            "system_metrics": system_metrics,
            "output_files": {
                "memory_report": str(memory_report_file),
                "profile_stats": str(profile_file),
            },
        }

        # Save comprehensive results
        results_file = output_path / "comprehensive_analysis.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"Comprehensive analysis completed. Results saved to {output_dir}")
        return results

    def run_scaling_analysis(
        self, vehicle_counts: List[int], steps: int = 1000, output_dir: str = "scaling_analysis"
    ) -> Dict[str, Any]:
        """Run scaling behavior analysis."""

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        benchmark_results = []

        # Run benchmarks for different vehicle counts
        for vehicles in vehicle_counts:
            print(f"Running benchmark for {vehicles} vehicles...")

            config = load_config()
            config["vehicles"]["count"] = vehicles
            config["high_performance"]["enabled"] = True
            config["data_manager"]["enabled"] = True

            sim = Simulation(config)

            # Warmup
            for _ in range(100):
                sim.step(0.02)

            # Benchmark
            start_time = time.perf_counter()
            for _ in range(steps):
                sim.step(0.02)
            elapsed = time.perf_counter() - start_time

            benchmark_results.append(
                {
                    "vehicles": vehicles,
                    "steps": steps,
                    "elapsed_s": elapsed,
                    "steps_per_second": steps / elapsed,
                    "vehicles_per_second": (vehicles * steps) / elapsed,
                }
            )

        # Analyze scaling behavior
        scaling_analysis = self.performance_predictor.analyze_scaling_behavior(benchmark_results)

        # Save results
        results_file = output_path / "scaling_analysis.json"
        with open(results_file, "w") as f:
            json.dump(
                {"benchmark_results": benchmark_results, "scaling_analysis": scaling_analysis},
                f,
                indent=2,
            )

        print(f"Scaling analysis completed. Results saved to {output_dir}")
        return scaling_analysis


def main():
    """Main entry point for advanced profiling."""
    parser = argparse.ArgumentParser(description="Advanced Profiling and Memory Analysis")
    parser.add_argument(
        "--mode",
        choices=["memory", "scaling", "comprehensive"],
        default="comprehensive",
        help="Analysis mode",
    )
    parser.add_argument("--vehicles", type=int, default=100, help="Number of vehicles")
    parser.add_argument("--steps", type=int, default=1000, help="Number of steps")
    parser.add_argument("--output", default="profiling_analysis", help="Output directory")
    parser.add_argument(
        "--vehicle-counts",
        nargs="+",
        type=int,
        default=[10, 20, 50, 100, 200],
        help="Vehicle counts for scaling analysis",
    )

    args = parser.parse_args()

    profiler = AdvancedProfiler()

    try:
        if args.mode == "memory":
            # Memory analysis only
            config = load_config()
            config["vehicles"]["count"] = args.vehicles
            sim = Simulation(config)

            memory_profile = profiler.memory_profiler.analyze_memory_usage(sim, args.steps)
            profiler.memory_profiler.generate_memory_report(f"{args.output}/memory_report.json")

            print(f"Memory analysis completed. Peak usage: {memory_profile.peak_mb:.1f} MB")

        elif args.mode == "scaling":
            # Scaling analysis
            scaling_analysis = profiler.run_scaling_analysis(
                args.vehicle_counts, args.steps, args.output
            )
            print(
                f"Scaling analysis completed. Model: {scaling_analysis['scaling_model']['complexity_order']}"
            )

        else:
            # Comprehensive analysis
            results = profiler.run_comprehensive_analysis(args.vehicles, args.steps, args.output)
            print(
                f"Comprehensive analysis completed. Peak memory: {results['memory_profile']['peak_mb']:.1f} MB"
            )

    except KeyboardInterrupt:
        print("\n⏹️  Profiling interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error in profiling: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
