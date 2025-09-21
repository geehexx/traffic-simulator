#!/usr/bin/env python3
"""
Quality monitoring and reporting script for the traffic simulator project.
Generates detailed reports and tracks quality metrics over time.
"""

import subprocess
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


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


class QualityMonitor:
    """Quality monitoring and reporting system."""

    def __init__(self, config_path: str = "quality_gates.yaml"):
        """Initialize quality monitor."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
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

    def run_command(self, cmd: List[str], cwd: str = None) -> tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, check=False)
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", str(e)

    def collect_ruff_metrics(self) -> List[QualityMetric]:
        """Collect Ruff linting metrics."""
        print("🔍 Collecting Ruff metrics...")

        # Linting metrics
        exit_code, stdout, stderr = self.run_command(
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
        format_exit_code, format_stdout, format_stderr = self.run_command(
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

    def collect_mypy_metrics(self) -> List[QualityMetric]:
        """Collect MyPy type checking metrics."""
        print("🔬 Collecting MyPy metrics...")

        exit_code, stdout, stderr = self.run_command(
            ["uv", "run", "mypy", "src/", "--show-error-codes"]
        )

        if exit_code == 0:
            issues = 0
        else:
            error_lines = [line for line in stdout.split("\n") if "error:" in line]
            issues = len(error_lines)

        max_allowed = self.config["tools"]["mypy"]["max_warnings"]

        return [
            QualityMetric(
                timestamp=datetime.now().isoformat(),
                tool="MyPy",
                metric_name="type_errors",
                value=float(issues),
                threshold=float(max_allowed),
                passed=issues <= max_allowed,
                details=f"Type errors: {issues}",
            )
        ]

    def collect_pyright_metrics(self) -> List[QualityMetric]:
        """Collect Pyright type checking metrics."""
        print("🔬 Collecting Pyright metrics...")

        exit_code, stdout, stderr = self.run_command(["uv", "run", "pyright", "src/"])

        if exit_code == 0:
            issues = 0
        else:
            error_lines = [line for line in stdout.split("\n") if "error" in line.lower()]
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

    def collect_pylint_metrics(self) -> List[QualityMetric]:
        """Collect Pylint code quality metrics."""
        print("🔍 Collecting Pylint metrics...")

        exit_code, stdout, stderr = self.run_command(
            ["uv", "run", "pylint", "src/", "--rcfile=pylintrc"]
        )

        if exit_code == 0:
            score = 10.0
            issues = 0
        else:
            # Extract score from output
            score_line = [
                line for line in stdout.split("\n") if "Your code has been rated at" in line
            ]
            if score_line:
                try:
                    score = float(score_line[0].split("rated at ")[1].split("/10")[0])
                except (IndexError, ValueError):
                    score = 0.0
            else:
                score = 0.0

            issue_lines = [
                line
                for line in stdout.split("\n")
                if ":" in line
                and any(x in line for x in ["error", "warning", "refactor", "convention"])
            ]
            issues = len(issue_lines)

        min_score = self.config["tools"]["pylint"]["min_score"]

        return [
            QualityMetric(
                timestamp=datetime.now().isoformat(),
                tool="Pylint",
                metric_name="quality_score",
                value=score,
                threshold=min_score,
                passed=score >= min_score,
                details=f"Quality score: {score:.1f}/10",
            ),
            QualityMetric(
                timestamp=datetime.now().isoformat(),
                tool="Pylint",
                metric_name="code_issues",
                value=float(issues),
                threshold=0.0,
                passed=issues == 0,
                details=f"Code issues: {issues}",
            ),
        ]

    def collect_bandit_metrics(self) -> List[QualityMetric]:
        """Collect Bandit security metrics."""
        print("🔒 Collecting Bandit metrics...")

        exit_code, stdout, stderr = self.run_command(
            ["uv", "run", "bandit", "-r", "src/", "-f", "json", "-c", "bandit.yaml"]
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

        exit_code, stdout, stderr = self.run_command(
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

        exit_code, stdout, stderr = self.run_command(
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

    def collect_all_metrics(self) -> List[QualityMetric]:
        """Collect all quality metrics."""
        print("🚀 Collecting quality metrics...\n")

        all_metrics = []

        collectors = [
            self.collect_ruff_metrics,
            self.collect_mypy_metrics,
            self.collect_pyright_metrics,
            self.collect_pylint_metrics,
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

        mypy_issues = [m for m in metrics if m.tool == "MyPy" and not m.passed]
        if mypy_issues:
            recommendations.append("Run 'uv run mypy src/' to check type errors")

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

    def save_report(self, report: QualityReport, output_path: str = "quality_report.json"):
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
    monitor = QualityMonitor()

    try:
        print("🚀 Starting quality monitoring...\n")

        metrics = monitor.collect_all_metrics()
        report = monitor.generate_report(metrics)

        monitor.print_report(report)
        monitor.save_report(report)

        # Exit with error code if quality score is too low
        if report.overall_score < 80:
            print(f"\n⚠️  Quality score {report.overall_score:.1f}% is below threshold (80%)")
            sys.exit(1)
        else:
            print(f"\n🎉 Quality score {report.overall_score:.1f}% meets standards!")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n⏹️  Quality monitoring interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error in quality monitoring: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
