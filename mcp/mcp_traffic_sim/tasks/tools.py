"""Task MCP tool handlers."""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from ..config import MCPConfig
from ..logging_util import MCPLogger
from ..security import SecurityManager
from .bazel_runner import BazelRunner
from .uv_runner import UvRunner


class TaskTools:
    """Task MCP tool implementations."""

    def __init__(self, config: MCPConfig, logger: MCPLogger, security: SecurityManager):
        """Initialize task tools with configuration and dependencies."""
        self.config = config
        self.logger = logger
        self.security = security
        self.bazel_runner = BazelRunner(config, security)
        self.uv_runner = UvRunner(config, security)
        self.runs_dir = config.repo_path / "runs"
        self.runs_dir.mkdir(exist_ok=True)

    def run_quality(self, mode: str = "check", fallback_to_uv: bool = False) -> Dict[str, Any]:
        """Run quality analysis with Bazel primary, uv fallback."""
        start_time = time.time()

        try:
            # Try Bazel first (primary workflow)
            bazel_result = self.bazel_runner.build()
            bazel_success = bazel_result.success

            # Fall back to uv if Bazel fails and fallback is enabled
            uv_fallback_used = False
            if not bazel_success and fallback_to_uv:
                uv_result = self.uv_runner.run_precommit()
                uv_fallback_used = True
                quality_success = uv_result.success
            else:
                quality_success = bazel_success

            # Create artifacts directory
            quality_dir = self.runs_dir / "quality"
            quality_dir.mkdir(exist_ok=True)

            # Save Bazel output
            bazel_log = quality_dir / f"bazel_{mode}_{int(time.time())}.log"
            with open(bazel_log, "w") as f:
                f.write(f"STDOUT:\n{bazel_result.stdout}\n\nSTDERR:\n{bazel_result.stderr}")

            artifacts = [str(bazel_log)]

            # Save uv output if used
            if uv_fallback_used:
                uv_log = quality_dir / f"uv_{mode}_{int(time.time())}.log"
                with open(uv_log, "w") as f:
                    f.write(f"STDOUT:\n{uv_result.stdout}\n\nSTDERR:\n{uv_result.stderr}")
                artifacts.append(str(uv_log))

            result = {
                "success": quality_success,
                "mode": mode,
                "bazel_success": bazel_success,
                "uv_fallback_used": uv_fallback_used,
                "quality_gates_passed": quality_success,
                "issues_found": 0 if quality_success else 1,  # Simplified
                "artifacts": artifacts,
                "summary": f"Quality {mode}: {'✓' if quality_success else '✗'} "
                f"(Bazel: {'✓' if bazel_success else '✗'}, "
                f"UV fallback: {'✓' if uv_fallback_used else '✗'})",
            }

            if not quality_success:
                result["error"] = "Quality analysis failed"

            duration = time.time() - start_time
            self.logger.log_task_operation(
                "quality",
                {"mode": mode, "fallback_to_uv": fallback_to_uv},
                result,
                duration=duration,
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to run quality analysis: {e}"
            self.logger.log_task_operation(
                "quality",
                {"mode": mode, "fallback_to_uv": fallback_to_uv},
                error=error_msg,
                duration=duration,
            )
            raise RuntimeError(error_msg)

    def run_tests(
        self,
        targets: Optional[List[str]] = None,
        maxfail: int = 0,
        verbose: bool = False,
        fallback_to_uv: bool = False,
    ) -> Dict[str, Any]:
        """Run tests with Bazel primary, uv fallback for debugging."""
        start_time = time.time()

        try:
            # Try Bazel first (primary workflow)
            bazel_result = self.bazel_runner.test(targets)
            bazel_success = bazel_result.success

            # Fall back to uv if Bazel fails and fallback is enabled
            uv_fallback_used = False
            if not bazel_success and fallback_to_uv:
                uv_result = self.uv_runner.run_pytest(targets, maxfail, verbose)
                uv_fallback_used = True
                test_success = uv_result.success
            else:
                test_success = bazel_success

            # Create artifacts directory
            test_dir = self.runs_dir / "tests"
            test_dir.mkdir(exist_ok=True)

            # Save Bazel output
            bazel_log = test_dir / f"bazel_test_{int(time.time())}.log"
            with open(bazel_log, "w") as f:
                f.write(f"STDOUT:\n{bazel_result.stdout}\n\nSTDERR:\n{bazel_result.stderr}")

            artifacts = [str(bazel_log)]

            # Save uv output if used
            if uv_fallback_used:
                uv_log = test_dir / f"uv_test_{int(time.time())}.log"
                with open(uv_log, "w") as f:
                    f.write(f"STDOUT:\n{uv_result.stdout}\n\nSTDERR:\n{uv_result.stderr}")
                artifacts.append(str(uv_log))

            # Parse test results (simplified)
            tests_run = 0
            tests_passed = 0
            tests_failed = 0

            if bazel_success:
                # Parse Bazel test output for counts
                output_lines = bazel_result.stdout.split("\n")
                for line in output_lines:
                    if "test" in line.lower() and (
                        "passed" in line.lower() or "failed" in line.lower()
                    ):
                        tests_run += 1
                        if "passed" in line.lower():
                            tests_passed += 1
                        else:
                            tests_failed += 1

            result = {
                "success": test_success,
                "tests_run": tests_run,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "tests_skipped": 0,
                "bazel_success": bazel_success,
                "uv_fallback_used": uv_fallback_used,
                "artifacts": artifacts,
                "summary": f"Tests: {tests_passed}/{tests_run} passed "
                f"(Bazel: {'✓' if bazel_success else '✗'}, "
                f"UV fallback: {'✓' if uv_fallback_used else '✗'})",
            }

            if not test_success:
                result["error"] = "Test execution failed"

            duration = time.time() - start_time
            self.logger.log_task_operation(
                "tests",
                {
                    "targets": targets,
                    "maxfail": maxfail,
                    "verbose": verbose,
                    "fallback_to_uv": fallback_to_uv,
                },
                result,
                duration=duration,
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to run tests: {e}"
            self.logger.log_task_operation(
                "tests",
                {
                    "targets": targets,
                    "maxfail": maxfail,
                    "verbose": verbose,
                    "fallback_to_uv": fallback_to_uv,
                },
                error=error_msg,
                duration=duration,
            )
            raise RuntimeError(error_msg)

    def run_performance(
        self,
        mode: str = "benchmark",
        duration: Optional[int] = None,
        vehicle_counts: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Run performance analysis with benchmarking."""
        start_time = time.time()

        try:
            # Build task command
            task_args = ["performance"]
            if mode == "scale":
                task_args.append(":scale")
            elif mode == "monitor":
                task_args.append(":monitor")

            # Execute task command
            task_result = self.bazel_runner.execute_command("task", task_args)

            # Create artifacts directory
            perf_dir = self.runs_dir / "performance"
            perf_dir.mkdir(exist_ok=True)

            # Save output
            perf_log = perf_dir / f"performance_{mode}_{int(time.time())}.log"
            with open(perf_log, "w") as f:
                f.write(f"STDOUT:\n{task_result.stdout}\n\nSTDERR:\n{task_result.stderr}")

            artifacts = [str(perf_log)]

            # Parse performance metrics (simplified)
            fps_measurements = []
            memory_usage = []

            if task_result.success:
                # Look for FPS and memory metrics in output
                output_lines = task_result.stdout.split("\n")
                for line in output_lines:
                    if "fps" in line.lower() or "fps" in line.lower():
                        try:
                            fps = float(line.split()[0])
                            fps_measurements.append(fps)
                        except (ValueError, IndexError):
                            pass
                    elif "memory" in line.lower():
                        try:
                            memory = float(line.split()[0])
                            memory_usage.append(memory)
                        except (ValueError, IndexError):
                            pass

            result = {
                "success": task_result.success,
                "mode": mode,
                "duration": duration,
                "vehicle_counts": vehicle_counts,
                "fps_measurements": fps_measurements,
                "memory_usage": memory_usage,
                "artifacts": artifacts,
                "summary": f"Performance {mode}: {'✓' if task_result.success else '✗'}, "
                f"FPS samples: {len(fps_measurements)}, "
                f"Memory samples: {len(memory_usage)}",
            }

            if not task_result.success:
                result["error"] = "Performance analysis failed"

            duration_seconds = time.time() - start_time
            self.logger.log_task_operation(
                "performance",
                {"mode": mode, "duration": duration, "vehicle_counts": vehicle_counts},
                result,
                duration=duration_seconds,
            )

            return result

        except Exception as e:
            duration_seconds = time.time() - start_time
            error_msg = f"Failed to run performance analysis: {e}"
            self.logger.log_task_operation(
                "performance",
                {"mode": mode, "duration": duration, "vehicle_counts": vehicle_counts},
                error=error_msg,
                duration=duration_seconds,
            )
            raise RuntimeError(error_msg)

    def run_analysis(
        self,
        include_quality: bool = True,
        include_performance: bool = True,
        include_profiling: bool = False,
        parallel: bool = True,
    ) -> Dict[str, Any]:
        """Run comprehensive analysis combining multiple operations."""
        start_time = time.time()

        try:
            results = {}
            artifacts = []

            # Run operations
            if include_quality:
                quality_result = self.run_quality()
                results["quality"] = quality_result
                artifacts.extend(quality_result.get("artifacts", []))

            if include_performance:
                performance_result = self.run_performance()
                results["performance"] = performance_result
                artifacts.extend(performance_result.get("artifacts", []))

            # Determine overall success
            all_success = all(result.get("success", False) for result in results.values())

            total_duration = time.time() - start_time

            result = {
                "success": all_success,
                "quality_result": results.get("quality"),
                "performance_result": results.get("performance"),
                "parallel_execution": parallel,
                "total_duration": total_duration,
                "artifacts": artifacts,
                "summary": f"Comprehensive analysis: {'✓' if all_success else '✗'}, "
                f"Duration: {total_duration:.1f}s, "
                f"Operations: {len(results)}",
            }

            if not all_success:
                result["error"] = "One or more analysis operations failed"

            self.logger.log_task_operation(
                "analysis",
                {
                    "include_quality": include_quality,
                    "include_performance": include_performance,
                    "include_profiling": include_profiling,
                    "parallel": parallel,
                },
                result,
                duration=total_duration,
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to run comprehensive analysis: {e}"
            self.logger.log_task_operation(
                "analysis",
                {
                    "include_quality": include_quality,
                    "include_performance": include_performance,
                    "include_profiling": include_profiling,
                    "parallel": parallel,
                },
                error=error_msg,
                duration=duration,
            )
            raise RuntimeError(error_msg)
