#!/usr/bin/env python3
"""
Comprehensive quality analysis script for the traffic simulator project.
Consolidates quality gates, monitoring, and static analysis functionality.

Usage:
    python scripts/quality_analysis.py --mode=check     # Quality gates enforcement
    python scripts/quality_analysis.py --mode=monitor   # Detailed quality monitoring
    python scripts/quality_analysis.py --mode=analyze  # Comprehensive static analysis
"""

import argparse
import subprocess
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict


@dataclass
class QualityGateResult:
    """Result of a quality gate check."""

    tool_name: str
    passed: bool
    issues: int
    max_allowed: int
    details: str
    severity: str = "info"


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


class QualityAnalysis:
    """Comprehensive quality analysis system."""

    def __init__(self, config_path: str = "config/quality_gates.yaml"):
        """Initialize quality analysis with configuration."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.results: List[QualityGateResult] = []
        self.metrics: List[QualityMetric] = []

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

    def run_command(self, cmd: List[str], cwd: str = None) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, check=False)
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", str(e)

    def check_ruff(self) -> QualityGateResult:
        """Check Ruff linting and formatting."""
        print("🔍 Checking Ruff linting...")

        # Check linting
        exit_code, stdout, _ = self.run_command(
            ["uv", "run", "ruff", "check", "src/", "--output-format=json"]
        )

        if exit_code == 0:
            issues = 0
        else:
            try:
                issues_data = json.loads(stdout) if stdout else []
                issues = len(issues_data)
            except json.JSONDecodeError:
                issues = -1

        # Check formatting
        format_exit_code, _, _ = self.run_command(
            ["uv", "run", "ruff", "format", "--check", "src/"]
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
        )

    def check_pyright(self) -> QualityGateResult:
        """Check Pyright type checking."""
        print("🔬 Checking Pyright type checking...")

        exit_code, stdout, _ = self.run_command(
            [
                "bash",
                "-c",
                "cd src && uv run pyright traffic_sim/",
            ]
        )

        if exit_code == 0:
            issues = 0
        else:
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
        )

    def check_bandit(self) -> QualityGateResult:
        """Check Bandit security analysis."""
        print("🔒 Checking Bandit security analysis...")

        exit_code, stdout, _ = self.run_command(
            ["uv", "run", "bandit", "-r", "src/", "-f", "json", "-c", "config/bandit.yaml"]
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
        )

    def check_radon(self) -> QualityGateResult:
        """Check Radon complexity analysis."""
        print("📊 Checking Radon complexity analysis...")

        exit_code, stdout, _ = self.run_command(
            ["uv", "run", "radon", "cc", "src/", "-a", "--min", "B"]
        )

        if exit_code == 0:
            # Count high complexity items
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
        )

    def check_coverage(self) -> QualityGateResult:
        """Check test coverage."""
        print("📈 Checking test coverage...")

        exit_code, stdout, _ = self.run_command(
            ["uv", "run", "pytest", "--cov=traffic_sim", "--cov-report=term-missing", "-q"]
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
        )

    def collect_ruff_metrics(self) -> List[QualityMetric]:
        """Collect Ruff linting metrics."""
        print("🔍 Collecting Ruff metrics...")

        # Linting metrics
        exit_code, stdout, _ = self.run_command(
            ["uv", "run", "ruff", "check", "src/", "--output-format=json"]
        )

        if exit_code == 0:
            issues = 0
        else:
            try:
                issues_data = json.loads(stdout) if stdout else []
                issues = len(issues_data)
            except json.JSONDecodeError:
                issues = -1

        # Formatting metrics
        format_exit_code, _, _ = self.run_command(
            ["uv", "run", "ruff", "format", "--check", "src/"]
        )
        format_issues = 1 if format_exit_code != 0 else 0

        max_allowed = self.config["tools"]["ruff"]["max_warnings"]

        return [
            QualityMetric(
                timestamp=datetime.now().isoformat(),
                tool="Ruff",
                metric_name="linting_issues",
                value=float(issues),
                threshold=float(max_allowed),
                passed=issues <= max_allowed,
                details=f"Linting issues: {issues}",
            ),
            QualityMetric(
                timestamp=datetime.now().isoformat(),
                tool="Ruff",
                metric_name="formatting_issues",
                value=float(format_issues),
                threshold=0.0,
                passed=format_issues == 0,
                details=f"Formatting issues: {format_issues}",
            ),
        ]

    def collect_pyright_metrics(self) -> List[QualityMetric]:
        """Collect Pyright type checking metrics."""
        print("🔬 Collecting Pyright metrics...")

        exit_code, stdout, _ = self.run_command(["uv", "run", "pyright", "src/"])

        if exit_code == 0:
            issues = 0
        else:
            error_lines = [line for line in stdout.split("\n") if "error:" in line]
            issues = len(error_lines)

        max_allowed = self.config["tools"]["pyright"]["max_warnings"]

        return [
            QualityMetric(
                timestamp=datetime.now().isoformat(),
                tool="Pyright",
                metric_name="type_errors",
                value=float(issues),
                threshold=float(max_allowed),
                passed=issues <= max_allowed,
                details=f"Type errors: {issues}",
            )
        ]

    def collect_bandit_metrics(self) -> List[QualityMetric]:
        """Collect Bandit security metrics."""
        print("🔒 Collecting Bandit metrics...")

        exit_code, stdout, _ = self.run_command(
            ["uv", "run", "bandit", "-r", "src/", "-f", "json", "-c", "config/bandit.yaml"]
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

        return [
            QualityMetric(
                timestamp=datetime.now().isoformat(),
                tool="Bandit",
                metric_name="security_issues",
                value=float(issues),
                threshold=float(max_allowed),
                passed=issues <= max_allowed,
                details=f"Security issues: {issues}",
            )
        ]

    def collect_radon_metrics(self) -> List[QualityMetric]:
        """Collect Radon complexity metrics."""
        print("📊 Collecting Radon metrics...")

        exit_code, stdout, _ = self.run_command(
            ["uv", "run", "radon", "cc", "src/", "-a", "--min", "B"]
        )

        if exit_code == 0:
            # Count complexity levels
            complexity_c = len([line for line in stdout.split("\n") if " - C " in line])
            complexity_d = len([line for line in stdout.split("\n") if " - D " in line])
            complexity_e = len([line for line in stdout.split("\n") if " - E " in line])
            complexity_f = len([line for line in stdout.split("\n") if " - F " in line])

            # Calculate average complexity
            lines = [line for line in stdout.split("\n") if " - " in line and "(" in line]
            if lines:
                complexities = []
                for line in lines:
                    try:
                        complexity = int(line.split("(")[1].split(")")[0])
                        complexities.append(complexity)
                    except (IndexError, ValueError):
                        continue
                avg_complexity = sum(complexities) / len(complexities) if complexities else 0.0
            else:
                avg_complexity = 0.0
        else:
            complexity_c = complexity_d = complexity_e = complexity_f = -1
            avg_complexity = -1.0

        max_avg = self.config["tools"]["radon"]["average_complexity_max"]

        return [
            QualityMetric(
                timestamp=datetime.now().isoformat(),
                tool="Radon",
                metric_name="complexity_c",
                value=float(complexity_c),
                threshold=0.0,
                passed=complexity_c == 0,
                details=f"Complexity C functions: {complexity_c}",
            ),
            QualityMetric(
                timestamp=datetime.now().isoformat(),
                tool="Radon",
                metric_name="complexity_d",
                value=float(complexity_d),
                threshold=0.0,
                passed=complexity_d == 0,
                details=f"Complexity D functions: {complexity_d}",
            ),
            QualityMetric(
                timestamp=datetime.now().isoformat(),
                tool="Radon",
                metric_name="complexity_e",
                value=float(complexity_e),
                threshold=0.0,
                passed=complexity_e == 0,
                details=f"Complexity E functions: {complexity_e}",
            ),
            QualityMetric(
                timestamp=datetime.now().isoformat(),
                tool="Radon",
                metric_name="complexity_f",
                value=float(complexity_f),
                threshold=0.0,
                passed=complexity_f == 0,
                details=f"Complexity F functions: {complexity_f}",
            ),
            QualityMetric(
                timestamp=datetime.now().isoformat(),
                tool="Radon",
                metric_name="average_complexity",
                value=avg_complexity,
                threshold=max_avg,
                passed=avg_complexity <= max_avg,
                details=f"Average complexity: {avg_complexity:.2f}",
            ),
        ]

    def collect_coverage_metrics(self) -> List[QualityMetric]:
        """Collect test coverage metrics."""
        print("📈 Collecting coverage metrics...")

        exit_code, stdout, _ = self.run_command(
            ["uv", "run", "pytest", "--cov=traffic_sim", "--cov-report=term-missing", "-q"]
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

        return [
            QualityMetric(
                timestamp=datetime.now().isoformat(),
                tool="Coverage",
                metric_name="line_coverage",
                value=coverage,
                threshold=min_coverage,
                passed=coverage >= min_coverage,
                details=f"Line coverage: {coverage:.1f}%",
            )
        ]

    def run_quality_gates(self) -> bool:
        """Run quality gates enforcement."""
        print("🚀 Running Quality Gates...\n")

        checks = [
            self.check_ruff,
            self.check_pyright,
            self.check_bandit,
            self.check_radon,
            self.check_coverage,
        ]

        all_passed = True

        for check in checks:
            try:
                result = check()
                self.results.append(result)
                if not result.passed:
                    all_passed = False
            except Exception as e:
                error_result = QualityGateResult(
                    tool_name=check.__name__.replace("check_", "").title(),
                    passed=False,
                    issues=-1,
                    max_allowed=0,
                    details=f"Error: {str(e)}",
                    severity="error",
                )
                self.results.append(error_result)
                all_passed = False

        return all_passed

    def collect_all_metrics(self) -> List[QualityMetric]:
        """Collect all quality metrics."""
        print("🚀 Collecting quality metrics...\n")

        all_metrics = []

        collectors = [
            self.collect_ruff_metrics,
            self.collect_pyright_metrics,
            self.collect_bandit_metrics,
            self.collect_radon_metrics,
            self.collect_coverage_metrics,
        ]

        for collector in collectors:
            try:
                metrics = collector()
                all_metrics.extend(metrics)
            except Exception as e:
                print(f"❌ Error collecting metrics from {collector.__name__}: {e}")

        return all_metrics

    def generate_report(self, metrics: List[QualityMetric]) -> QualityReport:
        """Generate comprehensive quality report."""
        timestamp = datetime.now().isoformat()

        # Calculate overall score
        passed_metrics = [m for m in metrics if m.passed]
        overall_score = (len(passed_metrics) / len(metrics)) * 100 if metrics else 0.0

        # Generate summary
        summary = {
            "total_metrics": len(metrics),
            "passed_metrics": len(passed_metrics),
            "failed_metrics": len(metrics) - len(passed_metrics),
            "overall_score": overall_score,
            "tools_analyzed": len(set(m.tool for m in metrics)),
        }

        # Generate recommendations
        recommendations = []

        failed_metrics = [m for m in metrics if not m.passed]
        if failed_metrics:
            recommendations.append(f"Address {len(failed_metrics)} failed quality metrics")

        # Tool-specific recommendations
        ruff_issues = [m for m in metrics if m.tool == "Ruff" and not m.passed]
        if ruff_issues:
            recommendations.append("Run 'uv run ruff check src/ --fix' to fix linting issues")
            recommendations.append("Run 'uv run ruff format src/' to fix formatting issues")

        pyright_issues = [m for m in metrics if m.tool == "Pyright" and not m.passed]
        if pyright_issues:
            recommendations.append("Run 'uv run pyright src/' to check type errors")

        coverage_issues = [m for m in metrics if m.tool == "Coverage" and not m.passed]
        if coverage_issues:
            recommendations.append("Increase test coverage to meet quality gates")

        return QualityReport(
            timestamp=timestamp,
            overall_score=overall_score,
            metrics=metrics,
            summary=summary,
            recommendations=recommendations,
        )

    def save_report(
        self, report: QualityReport, output_path: str = "runs/quality/quality_report.json"
    ):
        """Save quality report to file."""
        report_data = {
            "timestamp": report.timestamp,
            "overall_score": report.overall_score,
            "summary": report.summary,
            "metrics": [asdict(m) for m in report.metrics],
            "recommendations": report.recommendations,
        }

        with open(output_path, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"📄 Quality report saved to {output_path}")

    def print_gates_summary(self):
        """Print quality gates summary."""
        print("\n" + "=" * 60)
        print("📋 QUALITY GATES SUMMARY")
        print("=" * 60)

        passed_count = sum(1 for r in self.results if r.passed)
        total_count = len(self.results)

        for result in self.results:
            status_emoji = "✅" if result.passed else "❌"
            print(f"{status_emoji} {result.tool_name}: {result.details}")

        print(f"\n📊 Overall: {passed_count}/{total_count} checks passed")

        if passed_count == total_count:
            print("🎉 All quality gates passed!")
        else:
            print("❌ Some quality gates failed!")

        return passed_count == total_count

    def print_report(self, report: QualityReport):
        """Print quality report to console."""
        print("\n" + "=" * 60)
        print("📊 QUALITY MONITORING REPORT")
        print("=" * 60)
        print(f"📅 Timestamp: {report.timestamp}")
        print(f"📈 Overall Score: {report.overall_score:.1f}%")
        print(
            f"📊 Metrics: {report.summary['passed_metrics']}/{report.summary['total_metrics']} passed"
        )
        print(f"🔧 Tools Analyzed: {report.summary['tools_analyzed']}")

        print("\n📋 Detailed Metrics:")
        for metric in report.metrics:
            status = "✅" if metric.passed else "❌"
            print(f"  {status} {metric.tool} - {metric.metric_name}: {metric.details}")

        if report.recommendations:
            print("\n💡 Recommendations:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"  {i}. {rec}")

        print("\n" + "=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Comprehensive quality analysis")
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

    args = parser.parse_args()

    # Ensure runs directory exists
    runs_dir = Path("runs")
    runs_dir.mkdir(exist_ok=True)
    for subdir in ["profiling", "benchmarks", "performance", "scaling", "coverage", "quality"]:
        (runs_dir / subdir).mkdir(exist_ok=True)

    try:
        analysis = QualityAnalysis(args.config)

        if args.mode == "check":
            # Quality gates mode
            all_passed = analysis.run_quality_gates()
            analysis.print_gates_summary()

            if not all_passed:
                print("\n💡 To fix issues, run:")
                print("   uv run ruff check src/ --fix")
                print("   uv run ruff format src/")
                print("   uv run pyright src/")
                print("   uv run bandit -r src/ -c config/bandit.yaml")
                print("   uv run radon cc src/ -a --min B")
                print("   uv run pytest --cov=traffic_sim")

            sys.exit(0 if all_passed else 1)

        elif args.mode == "monitor":
            # Quality monitoring mode
            print("🚀 Starting quality monitoring...\n")
            metrics = analysis.collect_all_metrics()
            report = analysis.generate_report(metrics)
            analysis.print_report(report)
            analysis.save_report(report, args.output)

            # Exit with error code if quality score is too low
            if report.overall_score < 80:
                print(f"\n⚠️  Quality score {report.overall_score:.1f}% is below threshold (80%)")
                sys.exit(1)
            else:
                print(f"\n🎉 Quality score {report.overall_score:.1f}% meets standards!")
                sys.exit(0)

        elif args.mode == "analyze":
            # Comprehensive analysis mode
            print("🚀 Starting comprehensive static analysis...\n")
            metrics = analysis.collect_all_metrics()
            report = analysis.generate_report(metrics)
            analysis.print_report(report)
            analysis.save_report(report, args.output)

            # Determine overall status
            failed_metrics = [m for m in metrics if not m.passed]
            if failed_metrics:
                print(f"\n❌ Found {len(failed_metrics)} quality issues")
                sys.exit(1)
            else:
                print("\n🎉 All static analysis checks passed!")
                sys.exit(0)

    except KeyboardInterrupt:
        print("\n⏹️  Quality analysis interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error in quality analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
