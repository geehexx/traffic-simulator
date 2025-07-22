#!/usr/bin/env python3
"""
Bazel Performance Monitoring Script

This script helps monitor and optimize Bazel build performance by:
1. Profiling build times
2. Analyzing build bottlenecks
3. Generating performance reports
4. Suggesting optimizations
"""

import json
import subprocess
import time
import argparse
from pathlib import Path
from typing import Dict, Optional


class BazelPerformanceMonitor:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root).resolve()
        self.results_dir = self.workspace_root / "runs" / "bazel_performance"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def run_build_with_profiling(self, target: str = "//...", profile_name: str = None) -> Dict:
        """Run a Bazel build with profiling enabled."""
        if profile_name is None:
            profile_name = f"build_profile_{int(time.time())}"

        profile_file = self.results_dir / f"{profile_name}.json"

        print(f"Running Bazel build with profiling: {target}")
        print(f"Profile will be saved to: {profile_file}")

        # Run build with profiling
        cmd = [
            "bazel",
            "build",
            target,
            "--profile",
            str(profile_file),
            "--experimental_profile_include_target_label",
            "--experimental_profile_include_primary_output",
        ]

        start_time = time.time()
        try:
            result = subprocess.run(
                cmd, cwd=self.workspace_root, capture_output=True, text=True, timeout=600
            )
            end_time = time.time()

            build_time = end_time - start_time

            # Parse profile if it exists
            profile_data = {}
            if profile_file.exists():
                try:
                    with open(profile_file, "r") as f:
                        profile_data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Warning: Could not parse profile file {profile_file}")

            return {
                "success": result.returncode == 0,
                "build_time": build_time,
                "profile_file": str(profile_file),
                "profile_data": profile_data,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "build_time": 600,
                "error": "Build timed out after 10 minutes",
                "profile_file": str(profile_file),
            }
        except Exception as e:
            return {
                "success": False,
                "build_time": 0,
                "error": str(e),
                "profile_file": str(profile_file),
            }

    def analyze_profile(self, profile_file: str) -> Dict:
        """Analyze a Bazel profile file and extract performance insights."""
        try:
            with open(profile_file, "r") as f:
                profile_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            return {"error": f"Could not read profile file: {e}"}

        analysis = {
            "total_build_time": 0,
            "phases": {},
            "slowest_actions": [],
            "memory_usage": {},
            "recommendations": [],
        }

        # Analyze trace events
        if "traceEvents" in profile_data:
            events = profile_data["traceEvents"]

            # Group events by phase
            phases = {}
            for event in events:
                if "name" in event and "dur" in event:
                    phase = event.get("cat", "unknown")
                    if phase not in phases:
                        phases[phase] = {"count": 0, "total_time": 0}
                    phases[phase]["count"] += 1
                    phases[phase]["total_time"] += event["dur"] / 1000  # Convert to seconds

            analysis["phases"] = phases

            # Find slowest actions
            slow_actions = [e for e in events if e.get("dur", 0) > 1000]  # > 1 second
            slow_actions.sort(key=lambda x: x.get("dur", 0), reverse=True)
            analysis["slowest_actions"] = slow_actions[:10]

        # Generate recommendations
        recommendations = []

        if analysis["phases"].get("action", {}).get("total_time", 0) > 30:
            recommendations.append("Consider using remote execution for long-running actions")

        if analysis["phases"].get("analysis", {}).get("total_time", 0) > 10:
            recommendations.append("Analysis phase is slow - check for circular dependencies")

        if len(analysis["slowest_actions"]) > 5:
            recommendations.append("Multiple slow actions detected - consider parallelization")

        analysis["recommendations"] = recommendations

        return analysis

    def benchmark_build_variants(self, target: str = "//...") -> Dict:
        """Benchmark different build configurations."""
        variants = {
            "default": [],
            "fast": ["--config=fast"],
            "cache": ["--config=cache"],
            "debug": ["--config=debug"],
        }

        results = {}

        for variant_name, flags in variants.items():
            print(f"\nBenchmarking variant: {variant_name}")

            cmd = ["bazel", "build", target] + flags
            start_time = time.time()

            try:
                result = subprocess.run(
                    cmd, cwd=self.workspace_root, capture_output=True, text=True, timeout=300
                )
                end_time = time.time()

                results[variant_name] = {
                    "build_time": end_time - start_time,
                    "success": result.returncode == 0,
                    "stdout_lines": len(result.stdout.split("\n")),
                    "stderr_lines": len(result.stderr.split("\n")),
                }

            except subprocess.TimeoutExpired:
                results[variant_name] = {"build_time": 300, "success": False, "error": "Timeout"}
            except Exception as e:
                results[variant_name] = {"build_time": 0, "success": False, "error": str(e)}

        return results

    def generate_report(self, results: Dict, output_file: Optional[str] = None) -> str:
        """Generate a performance report."""
        if output_file is None:
            output_file = self.results_dir / f"performance_report_{int(time.time())}.md"

        with open(output_file, "w") as f:
            f.write("# Bazel Performance Report\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Build times comparison
            if "benchmark_results" in results:
                f.write("## Build Time Comparison\n\n")
                f.write("| Configuration | Build Time | Success |\n")
                f.write("|---------------|------------|----------|\n")

                for variant, data in results["benchmark_results"].items():
                    status = "✅" if data["success"] else "❌"
                    f.write(f"| {variant} | {data['build_time']:.2f}s | {status} |\n")

                f.write("\n")

            # Profile analysis
            if "profile_analysis" in results:
                f.write("## Profile Analysis\n\n")
                analysis = results["profile_analysis"]

                if "phases" in analysis:
                    f.write("### Build Phases\n\n")
                    for phase, data in analysis["phases"].items():
                        f.write(
                            f"- **{phase}**: {data['total_time']:.2f}s ({data['count']} events)\n"
                        )
                    f.write("\n")

                if "slowest_actions" in analysis:
                    f.write("### Slowest Actions\n\n")
                    for i, action in enumerate(analysis["slowest_actions"][:5], 1):
                        name = action.get("name", "Unknown")
                        duration = action.get("dur", 0) / 1000
                        f.write(f"{i}. {name}: {duration:.2f}s\n")
                    f.write("\n")

                if "recommendations" in analysis:
                    f.write("### Recommendations\n\n")
                    for rec in analysis["recommendations"]:
                        f.write(f"- {rec}\n")
                    f.write("\n")

            # Optimization suggestions
            f.write("## Optimization Suggestions\n\n")
            f.write(
                "1. **Enable remote caching**: Use `bazel build --config=cache` for local disk cache\n"
            )
            f.write(
                "2. **Use fast profile**: Use `bazel build --config=fast` for maximum performance\n"
            )
            f.write(
                "3. **Enable remote execution**: Configure remote execution for distributed builds\n"
            )
            f.write("4. **Optimize dependencies**: Review and minimize unnecessary dependencies\n")
            f.write("5. **Use incremental builds**: Avoid clean builds when possible\n")

        return str(output_file)

    def run_full_analysis(self, target: str = "//...") -> str:
        """Run a complete performance analysis."""
        print("Starting Bazel performance analysis...")

        results = {}

        # Benchmark different configurations
        print("\n1. Benchmarking build variants...")
        results["benchmark_results"] = self.benchmark_build_variants(target)

        # Profile the default build
        print("\n2. Profiling default build...")
        profile_result = self.run_build_with_profiling(target)
        results["profile_result"] = profile_result

        # Analyze profile if available
        if profile_result.get("profile_file") and Path(profile_result["profile_file"]).exists():
            print("\n3. Analyzing profile...")
            results["profile_analysis"] = self.analyze_profile(profile_result["profile_file"])

        # Generate report
        print("\n4. Generating report...")
        report_file = self.generate_report(results)

        print(f"\nAnalysis complete! Report saved to: {report_file}")
        return report_file


def main():
    parser = argparse.ArgumentParser(description="Monitor Bazel build performance")
    parser.add_argument("--target", default="//...", help="Bazel target to build")
    parser.add_argument("--workspace", default=".", help="Workspace root directory")
    parser.add_argument("--profile-only", action="store_true", help="Only run profiling")
    parser.add_argument("--benchmark-only", action="store_true", help="Only run benchmarks")

    args = parser.parse_args()

    monitor = BazelPerformanceMonitor(args.workspace)

    if args.profile_only:
        result = monitor.run_build_with_profiling(args.target)
        print(f"Build completed in {result['build_time']:.2f}s")
        if result.get("profile_file"):
            print(f"Profile saved to: {result['profile_file']}")
    elif args.benchmark_only:
        results = monitor.benchmark_build_variants(args.target)
        print("\nBenchmark Results:")
        for variant, data in results.items():
            status = "✅" if data["success"] else "❌"
            print(f"  {variant}: {data['build_time']:.2f}s {status}")
    else:
        monitor.run_full_analysis(args.target)


if __name__ == "__main__":
    main()
