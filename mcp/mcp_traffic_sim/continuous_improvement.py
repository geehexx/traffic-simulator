"""Continuous improvement workflow for prompt optimization."""

from __future__ import annotations

import time
from typing import Any, Dict, List

from prompt_registry import PromptRegistry
from meta_optimizer import MetaOptimizer


class ContinuousImprovementWorkflow:
    """Workflow for continuous prompt improvement."""

    def __init__(self, registry: PromptRegistry):
        """Initialize continuous improvement workflow."""
        self.registry = registry
        self.meta_optimizer = MetaOptimizer(registry)
        self.improvement_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Any] = {}

    def run_optimization_cycle(
        self, prompt_ids: List[str], strategies: List[str] = None
    ) -> Dict[str, Any]:
        """Run a complete optimization cycle for specified prompts."""
        if strategies is None:
            strategies = ["mipro", "bayesian", "hybrid"]

        cycle_start = time.time()
        results = {}

        print(f"🔄 Starting optimization cycle for {len(prompt_ids)} prompts")
        print(f"📋 Strategies: {', '.join(strategies)}")

        for prompt_id in prompt_ids:
            print(f"\n🎯 Optimizing prompt: {prompt_id}")
            prompt_results = {}

            for strategy in strategies:
                print(f"  📊 Running {strategy} optimization...")
                result = self.meta_optimizer.optimize_prompt(prompt_id, strategy)

                if result.success:
                    print(f"    ✅ Success: {result.improvement_score:.2f} improvement")
                    prompt_results[strategy] = result.dict()
                else:
                    print(f"    ❌ Failed: {result.error_message}")
                    prompt_results[strategy] = {"error": result.error_message}

            results[prompt_id] = prompt_results

        cycle_time = time.time() - cycle_start
        self._record_cycle(results, cycle_time)

        print(f"\n🎉 Optimization cycle completed in {cycle_time:.2f}s")
        return results

    def evaluate_prompt_performance(
        self, prompt_id: str, test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate prompt performance on test cases."""
        print(f"📊 Evaluating performance for prompt: {prompt_id}")

        prompt = self.registry.get_prompt(prompt_id)
        if not prompt:
            return {"error": f"Prompt '{prompt_id}' not found"}

        results = []
        total_time = 0

        for i, test_case in enumerate(test_cases):
            print(f"  🧪 Running test case {i+1}/{len(test_cases)}")

            start_time = time.time()
            execution_result = self.registry.execute_prompt(prompt_id, test_case)
            execution_time = time.time() - start_time
            total_time += execution_time

            results.append(
                {
                    "test_case": test_case,
                    "success": execution_result.success,
                    "execution_time": execution_time,
                    "output_quality": self._assess_output_quality(execution_result.output),
                    "error": execution_result.error_message,
                }
            )

        performance_metrics = {
            "prompt_id": prompt_id,
            "total_tests": len(test_cases),
            "successful_tests": sum(1 for r in results if r["success"]),
            "average_execution_time": total_time / len(test_cases),
            "overall_quality_score": sum(r["output_quality"] for r in results) / len(results),
            "results": results,
        }

        self.performance_metrics[prompt_id] = performance_metrics
        return performance_metrics

    def _assess_output_quality(self, output: Any) -> float:
        """Assess the quality of prompt output (mock implementation)."""
        if not output:
            return 0.0

        # Mock quality assessment based on output characteristics
        quality_score = 0.5  # Base score

        if isinstance(output, dict):
            if "message" in output:
                quality_score += 0.2
            if "template" in output:
                quality_score += 0.1
            if "input_schema" in output:
                quality_score += 0.1
            if "output_schema" in output:
                quality_score += 0.1

        return min(quality_score, 1.0)

    def _record_cycle(self, results: Dict[str, Any], cycle_time: float) -> None:
        """Record optimization cycle results."""
        cycle_record = {
            "timestamp": time.time(),
            "cycle_time": cycle_time,
            "prompts_optimized": len(results),
            "results": results,
            "best_improvements": self._get_best_improvements(results),
        }

        self.improvement_history.append(cycle_record)

    def _get_best_improvements(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get the best improvements from optimization results."""
        best_improvements = []

        for prompt_id, prompt_results in results.items():
            best_score = 0.0
            best_strategy = None

            for strategy, result in prompt_results.items():
                if isinstance(result, dict) and "improvement_score" in result:
                    if result["improvement_score"] > best_score:
                        best_score = result["improvement_score"]
                        best_strategy = strategy

            if best_strategy:
                best_improvements.append(
                    {
                        "prompt_id": prompt_id,
                        "strategy": best_strategy,
                        "improvement_score": best_score,
                    }
                )

        return sorted(best_improvements, key=lambda x: x["improvement_score"], reverse=True)

    def get_improvement_summary(self) -> Dict[str, Any]:
        """Get a summary of all improvements."""
        if not self.improvement_history:
            return {"message": "No optimization cycles completed yet"}

        total_cycles = len(self.improvement_history)
        total_prompts = sum(cycle["prompts_optimized"] for cycle in self.improvement_history)

        all_improvements = []
        for cycle in self.improvement_history:
            all_improvements.extend(cycle["best_improvements"])

        if all_improvements:
            best_overall = max(all_improvements, key=lambda x: x["improvement_score"])
            average_improvement = sum(imp["improvement_score"] for imp in all_improvements) / len(
                all_improvements
            )
        else:
            best_overall = None
            average_improvement = 0.0

        return {
            "total_cycles": total_cycles,
            "total_prompts_optimized": total_prompts,
            "best_overall_improvement": best_overall,
            "average_improvement_score": average_improvement,
            "performance_metrics": self.performance_metrics,
        }
