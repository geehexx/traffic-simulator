#!/usr/bin/env python3
"""
Comprehensive static analysis script for the traffic simulator project.
Runs all static analysis tools and provides a summary report.
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Any


def run_command(cmd: List[str], cwd: str = None) -> tuple[int, str, str]:
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


def run_ruff_check() -> Dict[str, Any]:
    """Run ruff linting and return results."""
    print("🔍 Running Ruff linting...")
    exit_code, stdout, stderr = run_command(["uv", "run", "ruff", "check", "src/", "--output-format=json"])
    
    if exit_code == 0:
        return {"status": "PASS", "issues": 0, "output": stdout}
    else:
        try:
            issues = json.loads(stdout) if stdout else []
            return {"status": "FAIL", "issues": len(issues), "output": stdout}
        except json.JSONDecodeError:
            return {"status": "ERROR", "issues": -1, "output": stderr}


def run_ruff_format() -> Dict[str, Any]:
    """Run ruff formatting check and return results."""
    print("🎨 Running Ruff formatting check...")
    exit_code, stdout, stderr = run_command(["uv", "run", "ruff", "format", "--check", "src/"])
    
    if exit_code == 0:
        return {"status": "PASS", "issues": 0, "output": stdout}
    else:
        return {"status": "FAIL", "issues": -1, "output": stdout + stderr}


def run_mypy() -> Dict[str, Any]:
    """Run mypy type checking and return results."""
    print("🔬 Running MyPy type checking...")
    exit_code, stdout, stderr = run_command(["uv", "run", "mypy", "src/", "--show-error-codes"])
    
    if exit_code == 0:
        return {"status": "PASS", "issues": 0, "output": stdout}
    else:
        # Count error lines
        error_lines = [line for line in stdout.split('\n') if 'error:' in line]
        return {"status": "FAIL", "issues": len(error_lines), "output": stdout}


def run_pyright() -> Dict[str, Any]:
    """Run pyright type checking and return results."""
    print("🔬 Running Pyright type checking...")
    exit_code, stdout, stderr = run_command(["uv", "run", "pyright", "src/"])
    
    if exit_code == 0:
        return {"status": "PASS", "issues": 0, "output": stdout}
    else:
        # Count error lines
        error_lines = [line for line in stdout.split('\n') if 'error' in line.lower()]
        return {"status": "FAIL", "issues": len(error_lines), "output": stdout}


def run_pylint() -> Dict[str, Any]:
    """Run pylint code quality analysis and return results."""
    print("🔍 Running Pylint code quality analysis...")
    exit_code, stdout, stderr = run_command(["uv", "run", "pylint", "src/", "--rcfile=pylintrc"])
    
    if exit_code == 0:
        return {"status": "PASS", "issues": 0, "output": stdout}
    else:
        # Count issue lines
        issue_lines = [line for line in stdout.split('\n') if ':' in line and any(x in line for x in ['error', 'warning', 'refactor', 'convention'])]
        return {"status": "FAIL", "issues": len(issue_lines), "output": stdout}


def run_bandit() -> Dict[str, Any]:
    """Run bandit security analysis and return results."""
    print("🔒 Running Bandit security analysis...")
    exit_code, stdout, stderr = run_command(["uv", "run", "bandit", "-r", "src/", "-f", "json", "-c", "bandit.yaml"])
    
    if exit_code == 0:
        try:
            data = json.loads(stdout)
            issues = len(data.get('results', []))
            return {"status": "PASS" if issues == 0 else "WARN", "issues": issues, "output": stdout}
        except json.JSONDecodeError:
            return {"status": "ERROR", "issues": -1, "output": stderr}
    else:
        return {"status": "ERROR", "issues": -1, "output": stderr}


def run_radon() -> Dict[str, Any]:
    """Run radon complexity analysis and return results."""
    print("📊 Running Radon complexity analysis...")
    exit_code, stdout, stderr = run_command(["uv", "run", "radon", "cc", "src/", "-a", "--min", "B"])
    
    if exit_code == 0:
        # Count high complexity items
        high_complexity = [line for line in stdout.split('\n') if any(x in line for x in [' - C ', ' - D ', ' - E ', ' - F '])]
        return {"status": "PASS" if len(high_complexity) == 0 else "WARN", "issues": len(high_complexity), "output": stdout}
    else:
        return {"status": "ERROR", "issues": -1, "output": stderr}


def main():
    """Run all static analysis tools and provide a summary."""
    print("🚀 Starting comprehensive static analysis...\n")
    
    tools = {
        "Ruff Linting": run_ruff_check,
        "Ruff Formatting": run_ruff_format,
        "MyPy Type Checking": run_mypy,
        "Pyright Type Checking": run_pyright,
        "Pylint Code Quality": run_pylint,
        "Bandit Security": run_bandit,
        "Radon Complexity": run_radon,
    }
    
    results = {}
    total_issues = 0
    
    for tool_name, tool_func in tools.items():
        try:
            result = tool_func()
            results[tool_name] = result
            if result["issues"] > 0:
                total_issues += result["issues"]
        except Exception as e:
            results[tool_name] = {"status": "ERROR", "issues": -1, "output": str(e)}
    
    # Print summary
    print("\n" + "="*60)
    print("📋 STATIC ANALYSIS SUMMARY")
    print("="*60)
    
    for tool_name, result in results.items():
        status_emoji = {
            "PASS": "✅",
            "FAIL": "❌", 
            "WARN": "⚠️",
            "ERROR": "💥"
        }.get(result["status"], "❓")
        
        issues_text = f"{result['issues']} issues" if result["issues"] >= 0 else "unknown issues"
        print(f"{status_emoji} {tool_name}: {result['status']} ({issues_text})")
    
    print(f"\n📊 Total issues found: {total_issues}")
    
    # Determine overall status
    failed_tools = [name for name, result in results.items() if result["status"] == "FAIL"]
    error_tools = [name for name, result in results.items() if result["status"] == "ERROR"]
    
    if error_tools:
        print(f"\n💥 Tools with errors: {', '.join(error_tools)}")
        sys.exit(1)
    elif failed_tools:
        print(f"\n❌ Tools with failures: {', '.join(failed_tools)}")
        sys.exit(1)
    else:
        print("\n🎉 All static analysis tools passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
