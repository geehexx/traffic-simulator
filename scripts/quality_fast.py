#!/usr/bin/env python3
"""
Ultra-Fast Quality Check - Minimal tool usage for CI/CD
Only runs essential checks with maximum speed optimizations.
"""

import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def run_fast_ruff():
    """Run only essential Ruff checks."""
    print("🔍 Fast Ruff check...")
    start = time.time()

    # Only check for errors, skip warnings
    result = subprocess.run(
        ["uv", "run", "ruff", "check", "src/", "--select=E,W,F", "--no-cache", "--quiet"],
        capture_output=True,
        text=True,
    )

    issues = len([line for line in result.stdout.split("\n") if line.strip()])
    elapsed = time.time() - start

    print(f"   {issues} issues found ({elapsed:.1f}s)")
    return issues == 0, issues, elapsed


def run_fast_pyright():
    """Run fast Pyright check."""
    print("🔬 Fast Pyright check...")
    start = time.time()

    result = subprocess.run(
        ["uv", "run", "pyright", "src/", "--outputjson", "--skipunannotated"],
        capture_output=True,
        text=True,
    )

    try:
        data = json.loads(result.stdout)
        issues = len(data.get("generalDiagnostics", []))
    except Exception:
        issues = 1 if result.returncode != 0 else 0

    elapsed = time.time() - start
    print(f"   {issues} type errors found ({elapsed:.1f}s)")
    return issues == 0, issues, elapsed


def main():
    """Run ultra-fast quality checks."""
    print("⚡ Ultra-Fast Quality Check\n")
    start_time = time.time()

    # Run checks in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(run_fast_ruff): "ruff",
            executor.submit(run_fast_pyright): "pyright",
        }

        results = {}
        for future in as_completed(futures):
            name = futures[future]
            try:
                results[name] = future.result()
            except Exception:
                results[name] = (False, 999, 0.0)

    total_time = time.time() - start_time

    # Summary
    print(f"\n⚡ Total time: {total_time:.1f}s")

    all_passed = all(passed for passed, _, _ in results.values())
    if all_passed:
        print("✅ All fast checks passed!")
        sys.exit(0)
    else:
        print("❌ Some checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    import json

    main()
