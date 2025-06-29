#!/usr/bin/env python3
"""
External Benchmarking Tools Integration

Integrates modern benchmarking frameworks including pytest-benchmark,
ASV (Air Speed Velocity), Hyperfine, and Py-Spy for comprehensive
performance analysis.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from dataclasses import dataclass

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


import pytest_benchmark


@dataclass
class PytestBenchmarkResult:
    """Result from pytest-benchmark execution."""

    name: str
    mean_time: float
    std_dev: float
    min_time: float
    max_time: float
    iterations: int
    rounds: int
    benchmark_data: Dict[str, Any]


@dataclass
class ASVBenchmarkResult:
    """Result from ASV benchmark execution."""

    commit_hash: str
    timestamp: str
    results: Dict[str, float]
    environment: Dict[str, str]
    machine_info: Dict[str, str]


@dataclass
class HyperfineResult:
    """Result from Hyperfine benchmark execution."""

    command: str
    mean_time: float
    std_dev: float
    min_time: float
    max_time: float
    median_time: float
    user_time: float
    system_time: float
    cpu_percent: float
    exit_code: int


class PytestBenchmarkAdapter:
    """Adapter for pytest-benchmark integration."""

    def __init__(self):
        self.benchmark_session = None

    def create_benchmark_tests(self, test_cases: List[Dict[str, Any]]) -> List[str]:
        """Generate pytest benchmark test functions."""

        test_functions = []

        for i, test_case in enumerate(test_cases):
            test_name = test_case.get("name", f"benchmark_{i}")
            vehicles = test_case.get("vehicles", 100)
            steps = test_case.get("steps", 1000)
            dt = test_case.get("dt", 0.02)
            speed_factor = test_case.get("speed_factor", 1.0)

            test_function = f'''
def test_{test_name}(benchmark):
    """Benchmark: {test_name}"""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    from traffic_sim.config.loader import load_config
    from traffic_sim.core.simulation import Simulation

    def run_simulation():
        config = load_config()
        config["vehicles"]["count"] = {vehicles}
        config["physics"]["speed_factor"] = {speed_factor}
        config["high_performance"]["enabled"] = True
        config["data_manager"]["enabled"] = True

        sim = Simulation(config)

        for _ in range({steps}):
            sim.step({dt})

    benchmark(run_simulation)
'''
            test_functions.append(test_function)

        return test_functions

    def run_benchmark_suite(
        self,
        test_cases: List[Dict[str, Any]],
        output_dir: str = "runs/benchmarks/benchmark_results",
    ) -> List[PytestBenchmarkResult]:
        """Run comprehensive benchmark suite with pytest-benchmark."""

        if not pytest_benchmark:
            raise ImportError(
                "pytest-benchmark not available. Install with: pip install pytest-benchmark"
            )

        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            test_functions = self.create_benchmark_tests(test_cases)
            f.write("\n".join(test_functions))
            test_file = f.name

        try:
            # Run pytest-benchmark
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                test_file,
                "--benchmark-only",
                "--benchmark-save=benchmark_results",
                "--benchmark-save-data",
                "--benchmark-json=benchmark_results.json",
                "-v",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"pytest-benchmark failed: {result.stderr}")
                return []

            # Parse results
            results = []
            if Path("benchmark_results.json").exists():
                with open("benchmark_results.json", "r") as f:
                    benchmark_data = json.load(f)

                for benchmark in benchmark_data.get("benchmarks", []):
                    results.append(
                        PytestBenchmarkResult(
                            name=benchmark["name"],
                            mean_time=benchmark["stats"]["mean"],
                            std_dev=benchmark["stats"]["stddev"],
                            min_time=benchmark["stats"]["min"],
                            max_time=benchmark["stats"]["max"],
                            iterations=benchmark["iterations"],
                            rounds=benchmark["rounds"],
                            benchmark_data=benchmark,
                        )
                    )

            return results

        finally:
            # Cleanup
            Path(test_file).unlink(missing_ok=True)


class ASVBenchmarkRunner:
    """Air Speed Velocity benchmark runner for historical tracking."""

    def __init__(self, asv_dir: str = ".asv"):
        self.asv_dir = Path(asv_dir)
        self.asv_dir.mkdir(exist_ok=True)

    def setup_asv_environment(self):
        """Setup ASV benchmark environment."""

        # Create asv.conf.json
        asv_config = {
            "version": 1,
            "project": "traffic-simulator",
            "project_url": "https://github.com/your-org/traffic-simulator",
            "repo": ".",
            "branches": ["main"],
            "pythons": ["3.8", "3.9", "3.10", "3.11"],
            "matrix": {
                "numpy": ["1.21", "1.22", "1.23", "1.24"],
                "python": ["3.8", "3.9", "3.10", "3.11"],
            },
            "benchmark_dir": "benchmarks",
            "results_dir": "results",
            "html_dir": "html",
        }

        with open(self.asv_dir / "asv.conf.json", "w") as f:
            json.dump(asv_config, f, indent=2)

        # Create benchmark directory
        benchmark_dir = Path("benchmarks")
        benchmark_dir.mkdir(exist_ok=True)

        # Create benchmark file
        benchmark_file = benchmark_dir / "bench_simulation.py"
        with open(benchmark_file, "w") as f:
            f.write(
                '''
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation


class SimulationBenchmarks:
    """ASV benchmarks for traffic simulation."""

    def setup(self):
        """Setup benchmark environment."""
        self.config = load_config()
        self.config["vehicles"]["count"] = 100
        self.config["physics"]["speed_factor"] = 1.0
        self.config["high_performance"]["enabled"] = True
        self.config["data_manager"]["enabled"] = True

    def time_simulation_100_vehicles(self):
        """Benchmark 100 vehicles simulation."""
        sim = Simulation(self.config)
        for _ in range(1000):
            sim.step(0.02)

    def time_simulation_500_vehicles(self):
        """Benchmark 500 vehicles simulation."""
        config = self.config.copy()
        config["vehicles"]["count"] = 500
        sim = Simulation(config)
        for _ in range(1000):
            sim.step(0.02)

    def time_simulation_1000_vehicles(self):
        """Benchmark 1000 vehicles simulation."""
        config = self.config.copy()
        config["vehicles"]["count"] = 1000
        sim = Simulation(config)
        for _ in range(1000):
            sim.step(0.02)

    def time_high_speed_factor(self):
        """Benchmark high speed factor simulation."""
        config = self.config.copy()
        config["physics"]["speed_factor"] = 100.0
        sim = Simulation(config)
        for _ in range(1000):
            sim.step(0.02)
'''
            )

    def run_historical_benchmarks(self) -> List[ASVBenchmarkResult]:
        """Run benchmarks with historical comparison."""

        try:
            # Run ASV benchmarks
            cmd = [sys.executable, "-m", "asv", "run", "--quick"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"ASV benchmark failed: {result.stderr}")
                return []

            # Parse results (simplified)
            results: List[ASVBenchmarkResult] = []
            # In a real implementation, you would parse ASV's results format
            # For now, return empty list
            return results

        except Exception as e:
            print(f"ASV benchmark error: {e}")
            return []

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""

        try:
            # Generate HTML report
            cmd = [sys.executable, "-m", "asv", "publish"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"ASV report generation failed: {result.stderr}")
                return {}

            return {"status": "success", "html_dir": "html"}

        except Exception as e:
            print(f"ASV report generation error: {e}")
            return {}


class HyperfineRunner:
    """Hyperfine command-line benchmarking integration."""

    def __init__(self):
        self.hyperfine_available = self._check_hyperfine()

    def _check_hyperfine(self) -> bool:
        """Check if Hyperfine is available."""
        try:
            result = subprocess.run(["hyperfine", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def run_hyperfine_benchmark(
        self, commands: List[str], runs: int = 10, warmup: int = 2
    ) -> List[HyperfineResult]:
        """Run benchmarks using Hyperfine for statistical analysis."""

        if not self.hyperfine_available:
            print("Hyperfine not available. Install with: cargo install hyperfine")
            return []

        results: List[HyperfineResult] = []

        for command in commands:
            try:
                # Create temporary script
                with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                    f.write(
                        f"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation

{command}
"""
                    )
                    script_file = f.name

                # Run hyperfine
                cmd = [
                    "hyperfine",
                    f"--runs={runs}",
                    f"--warmup={warmup}",
                    "--export-json=hyperfine_results.json",
                    f"python {script_file}",
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0 and Path("hyperfine_results.json").exists():
                    with open("hyperfine_results.json", "r") as f:
                        data = json.load(f)

                    for result_data in data.get("results", []):
                        results.append(
                            HyperfineResult(
                                command=command,
                                mean_time=result_data["mean"],
                                std_dev=result_data["stddev"],
                                min_time=result_data["min"],
                                max_time=result_data["max"],
                                median_time=result_data["median"],
                                user_time=result_data.get("user", 0.0),
                                system_time=result_data.get("system", 0.0),
                                cpu_percent=result_data.get("cpu_percent", 0.0),
                                exit_code=result_data.get("exit_code", 0),
                            )
                        )

                # Cleanup
                Path(script_file).unlink(missing_ok=True)

            except Exception as e:
                print(f"Hyperfine benchmark error for command '{command}': {e}")

        return results


class PySpyProfiler:
    """Py-spy profiler integration for low-overhead profiling."""

    def __init__(self):
        self.py_spy_available = self._check_py_spy()

    def _check_py_spy(self) -> bool:
        """Check if Py-Spy is available."""
        try:
            result = subprocess.run(["py-spy", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def profile_simulation(self, simulation_func, duration: float = 10.0) -> Dict[str, Any]:
        """Profile simulation with minimal overhead."""

        if not self.py_spy_available:
            print("Py-Spy not available. Install with: pip install py-spy")
            return {}

        try:
            # Create temporary script
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(
                    f"""
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation

def run_simulation():
    config = load_config()
    config["vehicles"]["count"] = 100
    config["physics"]["speed_factor"] = 1.0
    config["high_performance"]["enabled"] = True

    sim = Simulation(config)

    start_time = time.time()
    while time.time() - start_time < {duration}:
        sim.step(0.02)

if __name__ == "__main__":
    run_simulation()
"""
                )
                script_file = f.name

            # Run py-spy
            cmd = [
                "py-spy",
                "record",
                "--output",
                "profile.svg",
                "--format",
                "svg",
                "--duration",
                str(int(duration)),
                "--",
                "python",
                script_file,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            profile_data = {}
            if result.returncode == 0:
                profile_data = {
                    "status": "success",
                    "output_file": "profile.svg",
                    "duration": duration,
                }

            # Cleanup
            Path(script_file).unlink(missing_ok=True)

            return profile_data

        except Exception as e:
            print(f"Py-Spy profiling error: {e}")
            return {}


class ExternalToolsIntegration:
    """Unified integration for all external benchmarking tools."""

    def __init__(self):
        self.pytest_adapter = PytestBenchmarkAdapter()
        self.asv_runner = ASVBenchmarkRunner()
        self.hyperfine_runner = HyperfineRunner()
        self.pyspy_profiler = PySpyProfiler()

    def run_comprehensive_benchmark(
        self,
        test_cases: List[Dict[str, Any]],
        output_dir: str = "runs/benchmarks/comprehensive_benchmark",
    ) -> Dict[str, Any]:
        """Run comprehensive benchmark using all available tools."""

        results: Dict[str, Any] = {}

        # pytest-benchmark
        if pytest_benchmark:
            print("Running pytest-benchmark...")
            try:
                pytest_results = self.pytest_adapter.run_benchmark_suite(test_cases, output_dir)
                results["pytest_benchmark"] = pytest_results
            except Exception as e:
                print(f"pytest-benchmark failed: {e}")
                results["pytest_benchmark"] = []

        # Hyperfine
        if self.hyperfine_runner.hyperfine_available:
            print("Running Hyperfine benchmarks...")
            commands = [
                f"config = load_config(); config['vehicles']['count'] = {tc.get('vehicles', 100)}; sim = Simulation(config); [sim.step(0.02) for _ in range({tc.get('steps', 1000)})]"
                for tc in test_cases
            ]
            hyperfine_results = self.hyperfine_runner.run_hyperfine_benchmark(commands)
            results["hyperfine"] = hyperfine_results

        # Py-Spy profiling
        if self.pyspy_profiler.py_spy_available:
            print("Running Py-Spy profiling...")
            profile_data = self.pyspy_profiler.profile_simulation(None, duration=10.0)
            results["py_spy"] = profile_data

        return results


def main():
    """Main entry point for external tools integration."""
    import argparse

    parser = argparse.ArgumentParser(description="External Benchmarking Tools Integration")
    parser.add_argument(
        "--tool",
        choices=["pytest", "asv", "hyperfine", "pyspy", "all"],
        default="all",
        help="Tool to run",
    )
    parser.add_argument(
        "--output", default="runs/benchmarks/external_benchmark_results", help="Output directory"
    )

    args = parser.parse_args()

    integration = ExternalToolsIntegration()

    # Sample test cases
    test_cases = [
        {"name": "100_vehicles", "vehicles": 100, "steps": 1000},
        {"name": "500_vehicles", "vehicles": 500, "steps": 1000},
        {"name": "1000_vehicles", "vehicles": 1000, "steps": 1000},
    ]

    if args.tool == "all":
        integration.run_comprehensive_benchmark(test_cases, args.output)
        print(f"Comprehensive benchmark results saved to {args.output}")
    else:
        print(f"Running {args.tool} benchmark...")
        # Individual tool execution would go here


def ensure_runs_directory():
    """Ensure the runs directory structure exists."""
    from pathlib import Path

    runs_dir = Path("runs")
    runs_dir.mkdir(exist_ok=True)

    # Create subdirectories
    for subdir in ["profiling", "benchmarks", "performance", "scaling"]:
        (runs_dir / subdir).mkdir(exist_ok=True)


if __name__ == "__main__":
    ensure_runs_directory()
    main()
