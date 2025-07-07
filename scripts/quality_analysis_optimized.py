#!/usr/bin/env python3
"""
Optimized Quality Analysis Script for Traffic Simulator
Implements parallel execution, caching, and performance optimizations.

Usage:
    python scripts/quality_analysis_optimized.py --mode=check     # Quality gates enforcement
    python scripts/quality_analysis_optimized.py --mode=monitor   # Detailed quality monitoring
    python scripts/quality_analysis_optimized.py --mode=analyze  # Comprehensive static analysis
"""

import argparse
import subprocess
import sys
import json
import yaml
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


@dataclass
class QualityGateResult:
    """Result of a quality gate check."""

    tool_name: str
    passed: bool
    issues: int
    max_allowed: int
    details: str
    severity: str = "info"
    execution_time: float = 0.0


@dataclass
class QualityMetric:
    """Quality metric data point."""

    timestamp: str
    tool: str
    metric_name: str
    value: float
    threshold: float
    passed: bool
    details: str


@dataclass
class QualityReport:
    """Comprehensive quality report."""

    timestamp: str
    overall_score: float
    metrics: List[QualityMetric]
    summary: Dict[str, Any]
    recommendations: List[str]


class CacheManager:
    """Manages caching for tool results to avoid redundant executions."""

    def __init__(self, cache_dir: Path = Path("runs/quality/cache")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()

    def _get_cache_key(self, tool: str, args: List[str], cwd: str = None) -> str:
        """Generate cache key for a tool execution."""
        key_data = f"{tool}:{':'.join(args)}:{cwd or ''}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get_cached_result(
        self, tool: str, args: List[str], cwd: str = None
    ) -> Optional[Tuple[int, str, str, float]]:
        """Get cached result if available and fresh."""
        cache_key = self._get_cache_key(tool, args, cwd)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r") as f:
                data = json.load(f)

            # Check if cache is fresh (less than 1 hour old)
            if time.time() - data["timestamp"] > 3600:
                cache_file.unlink()
                return None

            return data["exit_code"], data["stdout"], data["stderr"], data["execution_time"]
        except (json.JSONDecodeError, KeyError):
            cache_file.unlink()
            return None

    def cache_result(
        self,
        tool: str,
        args: List[str],
        exit_code: int,
        stdout: str,
        stderr: str,
        execution_time: float,
        cwd: str = None,
    ):
        """Cache a tool execution result."""
        cache_key = self._get_cache_key(tool, args, cwd)
        cache_file = self.cache_dir / f"{cache_key}.json"

        with self.lock:
            try:
                with open(cache_file, "w") as f:
                    json.dump(
                        {
                            "exit_code": exit_code,
                            "stdout": stdout,
                            "stderr": stderr,
                            "execution_time": execution_time,
                            "timestamp": time.time(),
                        },
                        f,
                    )
            except Exception:
                pass  # Ignore cache write errors


class OptimizedQualityAnalysis:
    """Optimized quality analysis system with parallel execution and caching."""

    def __init__(self, config_path: str = "config/quality_gates.yaml"):
        """Initialize quality analysis with configuration."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.results: List[QualityGateResult] = []
        self.metrics: List[QualityMetric] = []
        self.cache_manager = CacheManager()

    def _load_config(self) -> Dict[str, Any]:
        """Load quality gates configuration."""
        try:
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ Configuration file {self.config_path} not found")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"❌ Error parsing configuration: {e}")
            sys.exit(1)

    def run_command_optimized(
        self, cmd: List[str], cwd: str = None, use_cache: bool = True
    ) -> Tuple[int, str, str, float]:
        """Run a command with caching and timing."""
        start_time = time.time()

        # Check cache first
        if use_cache:
            cached_result = self.cache_manager.get_cached_result(cmd[0], cmd, cwd)
            if cached_result is not None:
                print(f"⚡ Using cached result for {' '.join(cmd[:2])}...")
                return cached_result

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, check=False)
            execution_time = time.time() - start_time

            # Cache the result
            if use_cache:
                self.cache_manager.cache_result(
                    cmd[0],
                    cmd,
                    result.returncode,
                    result.stdout,
                    result.stderr,
                    execution_time,
                    cwd,
                )

            return result.returncode, result.stdout, result.stderr, execution_time
        except Exception as e:
            execution_time = time.time() - start_time
            return 1, "", str(e), execution_time

    def check_ruff_optimized(self) -> QualityGateResult:
        """Check Ruff linting and formatting with optimizations."""
        print("🔍 Checking Ruff linting...")
        # start_time = time.time()  # Unused variable

        # Use more efficient Ruff options
        exit_code, stdout, stderr, exec_time = self.run_command_optimized(
            ["uv", "run", "ruff", "check", "src/", "--output-format=json", "--no-cache"]
        )

        if exit_code == 0:
            issues = 0
        else:
            try:
                issues_data = json.loads(stdout) if stdout else []
                issues = len(issues_data)
            except json.JSONDecodeError:
                issues = -1

        # Check formatting with --diff for faster check
        format_exit_code, _, _, _ = self.run_command_optimized(
            ["uv", "run", "ruff", "format", "--check", "--diff", "src/"]
        )
        format_issues = 1 if format_exit_code != 0 else 0

        total_issues = issues + format_issues
        max_allowed = self.config["tools"]["ruff"]["max_warnings"]

        passed = total_issues <= max_allowed
        severity = "error" if not passed else "info"

        return QualityGateResult(
            tool_name="Ruff",
            passed=passed,
            issues=total_issues,
            max_allowed=max_allowed,
            details=f"Linting: {issues} issues, Formatting: {format_issues} issues",
            severity=severity,
            execution_time=exec_time,
        )

    def check_pyright_optimized(self) -> QualityGateResult:
        """Check Pyright type checking with optimizations."""
        print("🔬 Checking Pyright type checking...")

        # Use more efficient Pyright options
        exit_code, stdout, stderr, exec_time = self.run_command_optimized(
            ["uv", "run", "pyright", "src/", "--outputjson", "--skipunannotated"]
        )

        if exit_code == 0:
            issues = 0
        else:
            try:
                # Parse JSON output for more accurate counting
                if stdout.strip():
                    data = json.loads(stdout)
                    issues = len(data.get("generalDiagnostics", []))
                else:
                    error_lines = [line for line in stderr.split("\n") if "error:" in line]
                    issues = len(error_lines)
            except (json.JSONDecodeError, KeyError):
                error_lines = [line for line in stdout.split("\n") if "error:" in line]
                issues = len(error_lines)

        max_allowed = self.config["tools"]["pyright"]["max_warnings"]
        passed = issues <= max_allowed
        severity = "error" if not passed else "info"

        return QualityGateResult(
            tool_name="Pyright",
            passed=passed,
            issues=issues,
            max_allowed=max_allowed,
            details=stdout if issues > 0 else "No type errors found",
            severity=severity,
            execution_time=exec_time,
        )

    def check_bandit_optimized(self) -> QualityGateResult:
        """Check Bandit security analysis with optimizations."""
        print("🔒 Checking Bandit security analysis...")

        exit_code, stdout, stderr, exec_time = self.run_command_optimized(
            ["uv", "run", "bandit", "-r", "src/", "-f", "json", "-c", "config/bandit.yaml", "-q"]
        )

        if exit_code == 0:
            try:
                data = json.loads(stdout)
                issues = len(data.get("results", []))
            except json.JSONDecodeError:
                issues = 0
        else:
            issues = -1

        max_allowed = self.config["tools"]["bandit"]["max_low_severity"]
        passed = issues <= max_allowed
        severity = "error" if not passed else "info"

        return QualityGateResult(
            tool_name="Bandit",
            passed=passed,
            issues=issues,
            max_allowed=max_allowed,
            details=f"Security issues found: {issues}",
            severity=severity,
            execution_time=exec_time,
        )

    def check_radon_optimized(self) -> QualityGateResult:
        """Check Radon complexity analysis with optimizations."""
        print("📊 Checking Radon complexity analysis...")

        exit_code, stdout, stderr, exec_time = self.run_command_optimized(
            ["uv", "run", "radon", "cc", "src/", "-a", "--min", "B", "-j"]
        )

        if exit_code == 0:
            # Count high complexity items more efficiently
            high_complexity = [
                line
                for line in stdout.split("\n")
                if any(x in line for x in [" - C ", " - D ", " - E ", " - F "])
            ]
            issues = len(high_complexity)
        else:
            issues = -1

        max_allowed = self.config["tools"]["radon"]["max_complexity_C"]
        passed = issues <= max_allowed
        severity = "error" if not passed else "info"

        return QualityGateResult(
            tool_name="Radon",
            passed=passed,
            issues=issues,
            max_allowed=max_allowed,
            details=f"High complexity functions: {issues}",
            severity=severity,
            execution_time=exec_time,
        )

    def check_coverage_optimized(self) -> QualityGateResult:
        """Check test coverage with optimizations."""
        print("📈 Checking test coverage...")

        # Use faster coverage options
        exit_code, stdout, stderr, exec_time = self.run_command_optimized(
            [
                "uv",
                "run",
                "pytest",
                "--cov=traffic_sim",
                "--cov-report=term-missing",
                "-q",
                "--tb=short",
                "-x",
            ]
        )

        if exit_code == 0:
            # Extract coverage percentage from output
            coverage_line = [line for line in stdout.split("\n") if "TOTAL" in line and "%" in line]
            if coverage_line:
                try:
                    coverage = float(coverage_line[0].split()[-1].replace("%", ""))
                except (IndexError, ValueError):
                    coverage = 0.0
            else:
                coverage = 0.0
        else:
            coverage = 0.0

        min_coverage = self.config["coverage"]["min_line_coverage"]
        passed = coverage >= min_coverage
        severity = "error" if not passed else "info"

        return QualityGateResult(
            tool_name="Coverage",
            passed=passed,
            issues=int(100 - coverage),
            max_allowed=int(100 - min_coverage),
            details=f"Line coverage: {coverage:.1f}% (min: {min_coverage}%)",
            severity=severity,
            execution_time=exec_time,
        )

    def run_quality_gates_parallel(self) -> bool:
        """Run quality gates with parallel execution."""
        print("🚀 Running Quality Gates (Parallel)...\n")

        # Define checks with their functions
        checks = [
            ("Ruff", self.check_ruff_optimized),
            ("Pyright", self.check_pyright_optimized),
            ("Bandit", self.check_bandit_optimized),
            ("Radon", self.check_radon_optimized),
            ("Coverage", self.check_coverage_optimized),
        ]

        all_passed = True
        results = {}

        # Run checks in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all tasks
            future_to_check = {
                executor.submit(check_func): (name, check_func) for name, check_func in checks
            }

            # Collect results as they complete
            for future in as_completed(future_to_check):
                name, check_func = future_to_check[future]
                try:
                    result = future.result()
                    results[name] = result
                    self.results.append(result)
                    if not result.passed:
                        all_passed = False
                except Exception as e:
                    error_result = QualityGateResult(
                        tool_name=name,
                        passed=False,
                        issues=-1,
                        max_allowed=0,
                        details=f"Error: {str(e)}",
                        severity="error",
                        execution_time=0.0,
                    )
                    results[name] = error_result
                    self.results.append(error_result)
                    all_passed = False

        return all_passed

    def print_gates_summary(self):
        """Print quality gates summary with timing information."""
        print("\n" + "=" * 60)
        print("📋 QUALITY GATES SUMMARY")
        print("=" * 60)

        passed_count = sum(1 for r in self.results if r.passed)
        total_count = len(self.results)
        total_time = sum(r.execution_time for r in self.results)

        for result in self.results:
            status_emoji = "✅" if result.passed else "❌"
            print(
                f"{status_emoji} {result.tool_name}: {result.details} ({result.execution_time:.1f}s)"
            )

        print(f"\n📊 Overall: {passed_count}/{total_count} checks passed")
        print(f"⏱️  Total execution time: {total_time:.1f}s")

        if passed_count == total_count:
            print("🎉 All quality gates passed!")
        else:
            print("❌ Some quality gates failed!")

        return passed_count == total_count

    def clear_cache(self):
        """Clear the cache directory."""
        import shutil

        if self.cache_manager.cache_dir.exists():
            shutil.rmtree(self.cache_manager.cache_dir)
            print("🗑️  Cache cleared")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Optimized quality analysis")
    parser.add_argument(
        "--mode",
        choices=["check", "monitor", "analyze"],
        default="check",
        help="Analysis mode: check (gates), monitor (detailed), analyze (comprehensive)",
    )
    parser.add_argument(
        "--output", "-o", default="runs/quality/quality_report.json", help="Output file for reports"
    )
    parser.add_argument(
        "--config", "-c", default="config/quality_gates.yaml", help="Configuration file"
    )
    parser.add_argument("--clear-cache", action="store_true", help="Clear cache before running")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")

    args = parser.parse_args()

    # Ensure runs directory exists
    runs_dir = Path("runs")
    runs_dir.mkdir(exist_ok=True)
    for subdir in ["profiling", "benchmarks", "performance", "scaling", "coverage", "quality"]:
        (runs_dir / subdir).mkdir(exist_ok=True)

    try:
        analysis = OptimizedQualityAnalysis(args.config)

        if args.clear_cache:
            analysis.clear_cache()
            return

        if args.no_cache:
            analysis.cache_manager = None

        if args.mode == "check":
            # Quality gates mode with parallel execution
            start_time = time.time()
            all_passed = analysis.run_quality_gates_parallel()
            total_time = time.time() - start_time

            analysis.print_gates_summary()
            print(f"\n⚡ Total execution time: {total_time:.1f}s")

            if not all_passed:
                print("\n💡 To fix issues, run:")
                print("   uv run ruff check src/ --fix")
                print("   uv run ruff format src/")
                print("   uv run pyright src/")
                print("   uv run bandit -r src/ -c config/bandit.yaml")
                print("   uv run radon cc src/ -a --min B")
                print("   uv run pytest --cov=traffic_sim")

            sys.exit(0 if all_passed else 1)

        else:
            print("❌ Monitor and analyze modes not yet optimized")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️  Quality analysis interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error in quality analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
