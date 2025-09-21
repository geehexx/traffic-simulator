#!/usr/bin/env python3
"""
Quality Gates enforcement script for the traffic simulator project.
Validates code quality against defined thresholds and enforces quality standards.
"""

import subprocess
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class QualityGateResult:
    """Result of a quality gate check."""
    tool_name: str
    passed: bool
    issues: int
    max_allowed: int
    details: str
    severity: str = "info"


class QualityGates:
    """Quality gates enforcement system."""
    
    def __init__(self, config_path: str = "quality_gates.yaml"):
        """Initialize quality gates with configuration."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.results: List[QualityGateResult] = []
    
    def _load_config(self) -> Dict[str, Any]:
        """Load quality gates configuration."""
        try:
            with open(self.config_path, 'r') as f:
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
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=cwd,
                check=False
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", str(e)
    
    def check_ruff(self) -> QualityGateResult:
        """Check Ruff linting and formatting."""
        print("🔍 Checking Ruff linting...")
        
        # Check linting
        exit_code, stdout, stderr = self.run_command(["uv", "run", "ruff", "check", "src/", "--output-format=json"])
        
        if exit_code == 0:
            issues = 0
        else:
            try:
                issues_data = json.loads(stdout) if stdout else []
                issues = len(issues_data)
            except json.JSONDecodeError:
                issues = -1
        
        # Check formatting
        format_exit_code, format_stdout, format_stderr = self.run_command(["uv", "run", "ruff", "format", "--check", "src/"])
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
            severity=severity
        )
    
    def check_mypy(self) -> QualityGateResult:
        """Check MyPy type checking."""
        print("🔬 Checking MyPy type checking...")
        
        exit_code, stdout, stderr = self.run_command(["uv", "run", "mypy", "src/", "--show-error-codes"])
        
        if exit_code == 0:
            issues = 0
        else:
            error_lines = [line for line in stdout.split('\n') if 'error:' in line]
            issues = len(error_lines)
        
        max_allowed = self.config["tools"]["mypy"]["max_warnings"]
        passed = issues <= max_allowed
        severity = "error" if not passed else "info"
        
        return QualityGateResult(
            tool_name="MyPy",
            passed=passed,
            issues=issues,
            max_allowed=max_allowed,
            details=stdout if issues > 0 else "No type errors found",
            severity=severity
        )
    
    def check_pyright(self) -> QualityGateResult:
        """Check Pyright type checking."""
        print("🔬 Checking Pyright type checking...")
        
        exit_code, stdout, stderr = self.run_command(["uv", "run", "pyright", "src/"])
        
        if exit_code == 0:
            issues = 0
        else:
            error_lines = [line for line in stdout.split('\n') if 'error' in line.lower()]
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
            severity=severity
        )
    
    def check_pylint(self) -> QualityGateResult:
        """Check Pylint code quality."""
        print("🔍 Checking Pylint code quality...")
        
        exit_code, stdout, stderr = self.run_command(["uv", "run", "pylint", "src/", "--rcfile=pylintrc"])
        
        if exit_code == 0:
            issues = 0
            score = 10.0
        else:
            # Extract score from output
            score_line = [line for line in stdout.split('\n') if 'Your code has been rated at' in line]
            if score_line:
                try:
                    score = float(score_line[0].split('rated at ')[1].split('/10')[0])
                except (IndexError, ValueError):
                    score = 0.0
            else:
                score = 0.0
            
            issue_lines = [line for line in stdout.split('\n') if ':' in line and any(x in line for x in ['error', 'warning', 'refactor', 'convention'])]
            issues = len(issue_lines)
        
        min_score = self.config["tools"]["pylint"]["min_score"]
        max_allowed = self.config["tools"]["pylint"]["max_warnings"]
        
        passed = score >= min_score and issues <= max_allowed
        severity = "error" if not passed else "info"
        
        return QualityGateResult(
            tool_name="Pylint",
            passed=passed,
            issues=issues,
            max_allowed=max_allowed,
            details=f"Score: {score:.1f}/10, Issues: {issues}",
            severity=severity
        )
    
    def check_bandit(self) -> QualityGateResult:
        """Check Bandit security analysis."""
        print("🔒 Checking Bandit security analysis...")
        
        exit_code, stdout, stderr = self.run_command(["uv", "run", "bandit", "-r", "src/", "-f", "json", "-c", "bandit.yaml"])
        
        if exit_code == 0:
            try:
                data = json.loads(stdout)
                issues = len(data.get('results', []))
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
            severity=severity
        )
    
    def check_radon(self) -> QualityGateResult:
        """Check Radon complexity analysis."""
        print("📊 Checking Radon complexity analysis...")
        
        exit_code, stdout, stderr = self.run_command(["uv", "run", "radon", "cc", "src/", "-a", "--min", "B"])
        
        if exit_code == 0:
            # Count high complexity items
            high_complexity = [line for line in stdout.split('\n') if any(x in line for x in [' - C ', ' - D ', ' - E ', ' - F '])]
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
            severity=severity
        )
    
    def check_coverage(self) -> QualityGateResult:
        """Check test coverage."""
        print("📈 Checking test coverage...")
        
        exit_code, stdout, stderr = self.run_command(["uv", "run", "pytest", "--cov=traffic_sim", "--cov-report=term-missing", "-q"])
        
        if exit_code == 0:
            # Extract coverage percentage from output
            coverage_line = [line for line in stdout.split('\n') if 'TOTAL' in line and '%' in line]
            if coverage_line:
                try:
                    coverage = float(coverage_line[0].split()[-1].replace('%', ''))
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
            severity=severity
        )
    
    def run_all_checks(self) -> bool:
        """Run all quality gate checks."""
        print("🚀 Running Quality Gates...\n")
        
        checks = [
            self.check_ruff,
            self.check_mypy,
            self.check_pyright,
            self.check_pylint,
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
                    tool_name=check.__name__.replace('check_', '').title(),
                    passed=False,
                    issues=-1,
                    max_allowed=0,
                    details=f"Error: {str(e)}",
                    severity="error"
                )
                self.results.append(error_result)
                all_passed = False
        
        return all_passed
    
    def print_summary(self):
        """Print quality gates summary."""
        print("\n" + "="*60)
        print("📋 QUALITY GATES SUMMARY")
        print("="*60)
        
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


def main():
    """Main entry point."""
    gates = QualityGates()
    
    try:
        all_passed = gates.run_all_checks()
        gates.print_summary()
        
        if not all_passed:
            print("\n💡 To fix issues, run:")
            print("   uv run ruff check src/ --fix")
            print("   uv run ruff format src/")
            print("   uv run mypy src/")
            print("   uv run pyright src/")
            print("   uv run pylint src/ --rcfile=pylintrc")
            print("   uv run bandit -r src/ -c bandit.yaml")
            print("   uv run radon cc src/ -a --min B")
            print("   uv run pytest --cov=traffic_sim")
        
        sys.exit(0 if all_passed else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Quality gates check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error running quality gates: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
