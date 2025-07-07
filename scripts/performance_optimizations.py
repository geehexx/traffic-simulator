#!/usr/bin/env python3
"""
Performance Optimization Utilities for Traffic Simulator Tools
Provides caching, parallel execution, and other performance improvements.
"""

import hashlib
import json
import time
import threading
from pathlib import Path
from typing import Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess


class PerformanceOptimizer:
    """Centralized performance optimization utilities."""

    def __init__(self, cache_dir: Path = Path("runs/performance/cache")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()

    def get_cache_key(self, tool: str, args: list, cwd: str = None) -> str:
        """Generate cache key for tool execution."""
        key_data = f"{tool}:{':'.join(args)}:{cwd or ''}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get_cached_result(
        self, tool: str, args: list, cwd: str = None, max_age: int = 3600
    ) -> Optional[Tuple[int, str, str, float]]:
        """Get cached result if available and fresh."""
        cache_key = self.get_cache_key(tool, args, cwd)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r") as f:
                data = json.load(f)

            if time.time() - data["timestamp"] > max_age:
                cache_file.unlink()
                return None

            return data["exit_code"], data["stdout"], data["stderr"], data["execution_time"]
        except (json.JSONDecodeError, KeyError):
            cache_file.unlink()
            return None

    def cache_result(
        self,
        tool: str,
        args: list,
        exit_code: int,
        stdout: str,
        stderr: str,
        execution_time: float,
        cwd: str = None,
    ):
        """Cache tool execution result."""
        cache_key = self.get_cache_key(tool, args, cwd)
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
                pass

    def run_parallel_commands(
        self, commands: list, max_workers: int = 3
    ) -> Dict[str, Tuple[int, str, str, float]]:
        """Run multiple commands in parallel."""
        results = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_cmd = {
                executor.submit(self._run_single_command, cmd): cmd for cmd in commands
            }

            for future in as_completed(future_to_cmd):
                cmd = future_to_cmd[future]
                try:
                    result = future.result()
                    results[cmd["name"]] = result
                except Exception as e:
                    results[cmd["name"]] = (1, "", str(e), 0.0)

        return results

    def _run_single_command(self, cmd: dict) -> Tuple[int, str, str, float]:
        """Run a single command with caching."""
        start_time = time.time()

        # Check cache first
        cached = self.get_cached_result(cmd["tool"], cmd["args"], cmd.get("cwd"))
        if cached:
            return cached

        try:
            result = subprocess.run(
                cmd["args"], capture_output=True, text=True, cwd=cmd.get("cwd"), check=False
            )
            execution_time = time.time() - start_time

            # Cache the result
            self.cache_result(
                cmd["tool"],
                cmd["args"],
                result.returncode,
                result.stdout,
                result.stderr,
                execution_time,
                cmd.get("cwd"),
            )

            return result.returncode, result.stdout, result.stderr, execution_time
        except Exception as e:
            execution_time = time.time() - start_time
            return 1, "", str(e), execution_time


def create_fast_quality_script():
    """Create an ultra-fast quality script with minimal tool usage."""
    script_content = '''#!/usr/bin/env python3
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
    result = subprocess.run([
        "uv", "run", "ruff", "check", "src/",
        "--select=E,W,F", "--no-cache", "--quiet"
    ], capture_output=True, text=True)

    issues = len([line for line in result.stdout.split('\\n') if line.strip()])
    elapsed = time.time() - start

    print(f"   {issues} issues found ({elapsed:.1f}s)")
    return issues == 0, issues, elapsed


def run_fast_pyright():
    """Run fast Pyright check."""
    print("🔬 Fast Pyright check...")
    start = time.time()

    result = subprocess.run([
        "uv", "run", "pyright", "src/", "--outputjson", "--skipunannotated"
    ], capture_output=True, text=True)

    try:
        data = json.loads(result.stdout)
        issues = len(data.get('generalDiagnostics', []))
    except:
        issues = 1 if result.returncode != 0 else 0

    elapsed = time.time() - start
    print(f"   {issues} type errors found ({elapsed:.1f}s)")
    return issues == 0, issues, elapsed


def main():
    """Run ultra-fast quality checks."""
    print("⚡ Ultra-Fast Quality Check\\n")
    start_time = time.time()

    # Run checks in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(run_fast_ruff): "ruff",
            executor.submit(run_fast_pyright): "pyright"
        }

        results = {}
        for future in as_completed(futures):
            name = futures[future]
            try:
                results[name] = future.result()
            except Exception as e:
                results[name] = (False, 999, 0.0)

    total_time = time.time() - start_time

    # Summary
    print(f"\\n⚡ Total time: {total_time:.1f}s")

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
'''

    with open("scripts/quality_fast.py", "w") as f:
        f.write(script_content)

    # Make executable
    Path("scripts/quality_fast.py").chmod(0o755)


if __name__ == "__main__":
    create_fast_quality_script()
    print("✅ Created ultra-fast quality script")
