"""Continuous improvement workflow with automated evaluation."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .schemas import (
    PromptCandidate,
    PromptInput,
    PromptOutput,
    PromptMode,
    PromptOptimizationResult,
    MetaOptimizerConfig,
)
from .optimizers import AdvancedMetaOptimizer
from .datasets import DatasetManager, ExampleGenerator
from .registry import PromptRegistryManager
from .evaluator import EvaluationFramework


class ContinuousImprovementWorkflow:
    """Continuous improvement workflow with automated evaluation."""

    def __init__(
        self,
        registry_manager: PromptRegistryManager,
        dataset_manager: DatasetManager,
        config: Optional[MetaOptimizerConfig] = None,
    ):
        """Initialize continuous improvement workflow."""
        self.registry_manager = registry_manager
        self.dataset_manager = dataset_manager
        self.config = config or MetaOptimizerConfig()
        self.advanced_optimizer = AdvancedMetaOptimizer()
        self.example_generator = ExampleGenerator()
        self.evaluation_framework = EvaluationFramework()
        self.improvement_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Any] = {}

    def should_trigger_optimization(self) -> bool:
        """Check if optimization should be triggered based on various criteria."""

        # Time-based trigger
        if self._is_time_based_trigger():
            return True

        # Performance-based trigger
        if self._is_performance_based_trigger():
            return True

        # Data-based trigger
        if self._is_data_based_trigger():
            return True

        return False

    def _is_time_based_trigger(self) -> bool:
        """Check if optimization is due based on time."""
        if not self.improvement_history:
            return True

        last_optimization = self.improvement_history[-1]
        days_since_last = (datetime.utcnow() - last_optimization["timestamp"]).days

        return days_since_last >= self.config.optimization_frequency

    def _is_performance_based_trigger(self) -> bool:
        """Check if optimization is needed based on performance degradation."""

        # Check if quality scores have degraded
        if self.performance_metrics.get("quality_score", 1.0) < 0.8:
            return True

        # Check if execution time has increased
        if self.performance_metrics.get("execution_time", 0) > 10.0:
            return True

        # Check if success rate has decreased
        if self.performance_metrics.get("success_rate", 1.0) < 0.9:
            return True

        return False

    def _is_data_based_trigger(self) -> bool:
        """Check if optimization is needed based on new data availability."""

        # Check if new training data is available
        training_data = self.dataset_manager.load_training_data()
        if len(training_data) > self.performance_metrics.get("last_training_size", 0):
            return True

        # Check if validation performance has degraded
        validation_data = self.dataset_manager.load_validation_data()
        if validation_data:
            current_performance = self._evaluate_on_validation(validation_data)
            if current_performance < self.performance_metrics.get("validation_performance", 1.0):
                return True

        return False

    def run_continuous_optimization(
        self,
        mode: PromptMode,
        optimization_strategy: str = "hybrid",
    ) -> PromptOptimizationResult:
        """Run continuous optimization for a specific mode."""

        start_time = time.time()

        try:
            # Get current active prompt
            active_prompt = self.registry_manager.get_active_prompt(mode)
            if not active_prompt:
                raise ValueError(f"No active prompt found for mode: {mode}")

            # Prepare training and validation data
            training_data = self._prepare_training_data(mode)
            validation_data = self._prepare_validation_data(mode)

            # Run advanced optimization
            optimized_prompt = self.advanced_optimizer.optimize_prompt_advanced(
                base_prompt=active_prompt,
                training_data=training_data,
                validation_data=validation_data,
                optimization_strategy=optimization_strategy,
            )

            # Evaluate optimized prompt
            evaluation_result = self._evaluate_optimized_prompt(optimized_prompt, validation_data)

            # Create optimization result
            result = PromptOptimizationResult(
                winner_candidate=optimized_prompt,
                evaluation_results=[evaluation_result],
                optimization_metadata={
                    "mode": mode.value,
                    "strategy": optimization_strategy,
                    "training_examples": len(training_data),
                    "validation_examples": len(validation_data),
                    "optimization_time": time.time() - start_time,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                improvement_metrics=self._calculate_improvement_metrics(
                    active_prompt, optimized_prompt, evaluation_result
                ),
                next_optimization_suggestions=self._generate_suggestions(evaluation_result),
            )

            # Record improvement history
            self.improvement_history.append(
                {
                    "timestamp": datetime.utcnow(),
                    "mode": mode.value,
                    "strategy": optimization_strategy,
                    "improvement_score": result.improvement_metrics.get("overall_improvement", 0.0),
                    "training_size": len(training_data),
                    "validation_size": len(validation_data),
                }
            )

            # Update performance metrics
            self._update_performance_metrics(evaluation_result)

            return result

        except Exception as e:
            return PromptOptimizationResult(
                winner_candidate=None,
                evaluation_results=[],
                optimization_metadata={"error": str(e)},
                improvement_metrics={},
                next_optimization_suggestions=[f"Fix error: {e}"],
            )

    def _prepare_training_data(self, mode: PromptMode) -> List[Tuple[PromptInput, PromptOutput]]:
        """Prepare training data for optimization."""

        # Load existing training data
        training_data = self.dataset_manager.load_training_data()

        # Filter by mode
        mode_training_data = [
            (input_data, output) for input_data, output in training_data if input_data.mode == mode
        ]

        # Generate additional examples if needed
        if len(mode_training_data) < 20:  # Minimum training examples
            additional_examples = self.example_generator.generate_examples(
                mode=mode,
                num_examples=50,
                variety_level="high",
            )
            mode_training_data.extend(additional_examples)

            # Save additional examples
            self.dataset_manager.add_examples(additional_examples, "training")

        return mode_training_data

    def _prepare_validation_data(self, mode: PromptMode) -> List[Tuple[PromptInput, PromptOutput]]:
        """Prepare validation data for optimization."""

        # Load existing validation data
        validation_data = self.dataset_manager.load_validation_data()

        # Filter by mode
        mode_validation_data = [
            (input_data, output)
            for input_data, output in validation_data
            if input_data.mode == mode
        ]

        # Generate additional examples if needed
        if len(mode_validation_data) < 10:  # Minimum validation examples
            additional_examples = self.example_generator.generate_examples(
                mode=mode,
                num_examples=20,
                variety_level="medium",
            )
            mode_validation_data.extend(additional_examples)

            # Save additional examples
            self.dataset_manager.add_examples(additional_examples, "validation")

        return mode_validation_data

    def _evaluate_optimized_prompt(
        self,
        optimized_prompt: PromptCandidate,
        validation_data: List[Tuple[PromptInput, PromptOutput]],
    ) -> Any:
        """Evaluate optimized prompt on validation data."""

        # Convert validation data to test inputs
        test_inputs = [input_data for input_data, _ in validation_data]

        # Evaluate using evaluation framework
        evaluation = self.evaluation_framework.evaluate_candidate(optimized_prompt, test_inputs)

        return evaluation

    def _calculate_improvement_metrics(
        self,
        original: PromptCandidate,
        optimized: PromptCandidate,
        evaluation: Any,
    ) -> Dict[str, float]:
        """Calculate improvement metrics."""

        # Calculate quality improvement
        quality_improvement = 0.0
        if evaluation.quality_scores:
            quality_improvement = evaluation.quality_scores.overall_score / 100.0

        # Calculate stability improvement
        stability_improvement = 0.0
        if evaluation.quality_scores:
            stability_improvement = evaluation.quality_scores.stability_index

        # Calculate execution time improvement
        execution_time_improvement = 0.0
        if evaluation.execution_metrics:
            avg_time = evaluation.execution_metrics.get("avg_execution_time", 0)
            execution_time_improvement = max(0, 1.0 - (avg_time / 10.0))  # Normalize to 0-1

        # Calculate success rate improvement
        success_rate_improvement = 0.0
        if evaluation.execution_metrics:
            success_rate_improvement = evaluation.execution_metrics.get("success_rate", 0)

        # Calculate overall improvement
        overall_improvement = (
            quality_improvement * 0.4
            + stability_improvement * 0.3
            + execution_time_improvement * 0.2
            + success_rate_improvement * 0.1
        )

        return {
            "overall_improvement": overall_improvement,
            "quality_improvement": quality_improvement,
            "stability_improvement": stability_improvement,
            "execution_time_improvement": execution_time_improvement,
            "success_rate_improvement": success_rate_improvement,
        }

    def _generate_suggestions(self, evaluation: Any) -> List[str]:
        """Generate improvement suggestions based on evaluation."""

        suggestions = []

        if evaluation.quality_scores:
            if evaluation.quality_scores.stability_index < 0.9:
                suggestions.append("Improve prompt stability with more deterministic instructions")

            if evaluation.quality_scores.idempotency_score < 0.8:
                suggestions.append(
                    "Enhance idempotency with stable anchors and deterministic ordering"
                )

            if evaluation.quality_scores.duplication_score < 0.7:
                suggestions.append("Reduce duplication with better consolidation logic")

            if evaluation.quality_scores.link_integrity_score < 0.8:
                suggestions.append("Improve link integrity and cross-reference validation")

        if evaluation.execution_metrics:
            avg_execution_time = evaluation.execution_metrics.get("avg_execution_time", 0)
            if avg_execution_time > 5.0:
                suggestions.append("Optimize execution time with more efficient prompt structure")

            success_rate = evaluation.execution_metrics.get("success_rate", 1.0)
            if success_rate < 0.9:
                suggestions.append("Improve success rate with better error handling and validation")

        return suggestions

    def _update_performance_metrics(self, evaluation: Any) -> None:
        """Update performance metrics based on evaluation."""

        if evaluation.quality_scores:
            self.performance_metrics["quality_score"] = (
                evaluation.quality_scores.overall_score / 100.0
            )
            self.performance_metrics["stability_index"] = evaluation.quality_scores.stability_index

        if evaluation.execution_metrics:
            self.performance_metrics["execution_time"] = evaluation.execution_metrics.get(
                "avg_execution_time", 0
            )
            self.performance_metrics["success_rate"] = evaluation.execution_metrics.get(
                "success_rate", 1.0
            )

        # Update dataset sizes
        training_data = self.dataset_manager.load_training_data()
        validation_data = self.dataset_manager.load_validation_data()
        self.performance_metrics["last_training_size"] = len(training_data)
        self.performance_metrics["validation_performance"] = self._evaluate_on_validation(
            validation_data
        )

    def _evaluate_on_validation(
        self,
        validation_data: List[Tuple[PromptInput, PromptOutput]],
    ) -> float:
        """Evaluate current performance on validation data."""

        if not validation_data:
            return 1.0

        # Simplified validation evaluation
        total_score = 0.0

        for input_data, expected_output in validation_data:
            # This would integrate with actual prompt execution
            # For now, use a simplified scoring
            score = 0.0

            if expected_output.success:
                score += 0.4

            if expected_output.artifacts:
                score += 0.3

            if expected_output.coverage_decisions:
                score += 0.2

            if not expected_output.error:
                score += 0.1

            total_score += score

        return total_score / len(validation_data)

    def get_improvement_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get improvement history."""
        return self.improvement_history[-limit:]

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.performance_metrics.copy()

    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations based on current state."""

        recommendations = []

        # Check if optimization is due
        if self.should_trigger_optimization():
            recommendations.append("Optimization is due - run continuous optimization")

        # Check performance metrics
        if self.performance_metrics.get("quality_score", 1.0) < 0.8:
            recommendations.append("Quality score is low - consider prompt optimization")

        if self.performance_metrics.get("execution_time", 0) > 10.0:
            recommendations.append("Execution time is high - optimize prompt efficiency")

        if self.performance_metrics.get("success_rate", 1.0) < 0.9:
            recommendations.append("Success rate is low - improve error handling")

        # Check dataset size
        training_data = self.dataset_manager.load_training_data()
        if len(training_data) < 50:
            recommendations.append("Training dataset is small - generate more examples")

        return recommendations

    def run_automated_optimization_cycle(self) -> Dict[str, Any]:
        """Run automated optimization cycle for all modes."""

        results = {}

        for mode in [PromptMode.DOCS, PromptMode.RULES, PromptMode.HYBRID]:
            if self.should_trigger_optimization():
                try:
                    result = self.run_continuous_optimization(
                        mode=mode, optimization_strategy="hybrid"
                    )
                    results[mode.value] = {
                        "success": True,
                        "improvement_score": result.improvement_metrics.get(
                            "overall_improvement", 0.0
                        ),
                        "suggestions": result.next_optimization_suggestions,
                    }
                except Exception as e:
                    results[mode.value] = {
                        "success": False,
                        "error": str(e),
                    }
            else:
                results[mode.value] = {
                    "success": True,
                    "message": "Optimization not needed",
                }

        return results
