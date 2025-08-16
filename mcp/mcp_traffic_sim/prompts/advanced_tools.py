"""Advanced MCP tools for continuous improvement and optimization."""

from __future__ import annotations

import time
from typing import Any, Dict

from ..config import MCPConfig
from ..logging_util import MCPLogger
from ..security import SecurityManager
from .schemas import PromptMode, MetaOptimizerConfig
from .registry import PromptRegistryManager
from .datasets import DatasetManager, ExampleGenerator
from .continuous_improvement import ContinuousImprovementWorkflow
from .optimizers import AdvancedMetaOptimizer


class AdvancedPromptTools:
    """Advanced MCP tools for continuous improvement and optimization."""

    def __init__(self, config: MCPConfig, logger: MCPLogger, security: SecurityManager):
        """Initialize advanced prompt tools."""
        self.config = config
        self.logger = logger
        self.security = security

        # Initialize components
        self.registry_manager = PromptRegistryManager(
            registry_path=config.repo_path / "runs" / "prompts"
        )
        self.dataset_manager = DatasetManager(dataset_path=config.repo_path / "runs" / "datasets")
        self.continuous_workflow = ContinuousImprovementWorkflow(
            registry_manager=self.registry_manager,
            dataset_manager=self.dataset_manager,
            config=MetaOptimizerConfig(),
        )
        self.advanced_optimizer = AdvancedMetaOptimizer()
        self.example_generator = ExampleGenerator()

    def run_continuous_optimization(
        self,
        mode: str,
        optimization_strategy: str = "hybrid",
        auto_apply: bool = False,
    ) -> Dict[str, Any]:
        """Run continuous optimization with advanced strategies."""
        start_time = time.time()

        try:
            # Validate mode
            try:
                prompt_mode = PromptMode(mode)
            except ValueError:
                raise ValueError(
                    f"Invalid mode: {mode}. Valid modes: {[m.value for m in PromptMode]}"
                )

            # Run continuous optimization
            result = self.continuous_workflow.run_continuous_optimization(
                mode=prompt_mode,
                optimization_strategy=optimization_strategy,
            )

            # Apply if requested
            applied = False
            if auto_apply and result.winner_candidate:
                prompt_id = self.continuous_workflow.registry_manager.register_prompt(
                    content=result.winner_candidate.content,
                    mode=prompt_mode,
                    parameters=result.winner_candidate.parameters,
                    metadata=result.winner_candidate.metadata,
                )
                self.continuous_workflow.registry_manager.set_active_prompt(prompt_mode, prompt_id)
                applied = True

            response = {
                "success": True,
                "mode": mode,
                "strategy": optimization_strategy,
                "improvement_metrics": result.improvement_metrics,
                "applied": applied,
                "suggestions": result.next_optimization_suggestions,
                "summary": f"Continuous optimization completed: {optimization_strategy} strategy",
            }

            if result.winner_candidate:
                response["winner_candidate"] = {
                    "id": result.winner_candidate.id,
                    "content": result.winner_candidate.content[:200] + "..."
                    if len(result.winner_candidate.content) > 200
                    else result.winner_candidate.content,
                }

            duration = time.time() - start_time
            self.logger.log_operation(
                "advanced_prompt",
                "continuous_optimization",
                {"mode": mode, "strategy": optimization_strategy, "auto_apply": auto_apply},
                response,
                duration=duration,
            )

            return response

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to run continuous optimization: {e}"
            self.logger.log_operation(
                "advanced_prompt",
                "continuous_optimization",
                {"mode": mode, "strategy": optimization_strategy},
                error=error_msg,
                duration=duration,
            )
            raise RuntimeError(error_msg)

    def generate_training_data(
        self,
        mode: str,
        num_examples: int = 100,
        variety_level: str = "medium",
    ) -> Dict[str, Any]:
        """Generate training data for prompt optimization."""
        start_time = time.time()

        try:
            # Validate mode
            try:
                prompt_mode = PromptMode(mode)
            except ValueError:
                raise ValueError(
                    f"Invalid mode: {mode}. Valid modes: {[m.value for m in PromptMode]}"
                )

            # Generate examples
            examples = self.example_generator.generate_examples(
                mode=prompt_mode,
                num_examples=num_examples,
                variety_level=variety_level,
            )

            # Add to dataset
            added_count = self.dataset_manager.add_examples(examples, "training")

            result = {
                "success": True,
                "mode": mode,
                "examples_generated": len(examples),
                "examples_added": added_count,
                "variety_level": variety_level,
                "summary": f"Generated {len(examples)} training examples for {mode} mode",
            }

            duration = time.time() - start_time
            self.logger.log_operation(
                "advanced_prompt",
                "generate_training_data",
                {"mode": mode, "num_examples": num_examples, "variety_level": variety_level},
                result,
                duration=duration,
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to generate training data: {e}"
            self.logger.log_operation(
                "advanced_prompt",
                "generate_training_data",
                {"mode": mode, "num_examples": num_examples},
                error=error_msg,
                duration=duration,
            )
            raise RuntimeError(error_msg)

    def create_dataset_split(
        self,
        train_ratio: float = 0.8,
        validation_ratio: float = 0.1,
        test_ratio: float = 0.1,
        random_seed: int = 42,
    ) -> Dict[str, Any]:
        """Create training, validation, and test dataset splits."""
        start_time = time.time()

        try:
            # Load all examples
            training_data = self.dataset_manager.load_training_data()
            validation_data = self.dataset_manager.load_validation_data()
            test_data = self.dataset_manager.load_test_data()

            # Combine all examples
            all_examples = training_data + validation_data + test_data

            # Create new split
            split_result = self.dataset_manager.create_dataset(
                examples=all_examples,
                train_ratio=train_ratio,
                validation_ratio=validation_ratio,
                test_ratio=test_ratio,
                random_seed=random_seed,
            )

            result = {
                "success": True,
                "split_ratios": {
                    "training": train_ratio,
                    "validation": validation_ratio,
                    "test": test_ratio,
                },
                "dataset_sizes": split_result,
                "random_seed": random_seed,
                "summary": f"Created dataset split: {split_result['training']} training, {split_result['validation']} validation, {split_result['test']} test",
            }

            duration = time.time() - start_time
            self.logger.log_operation(
                "advanced_prompt",
                "create_dataset_split",
                {
                    "train_ratio": train_ratio,
                    "validation_ratio": validation_ratio,
                    "test_ratio": test_ratio,
                },
                result,
                duration=duration,
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to create dataset split: {e}"
            self.logger.log_operation(
                "advanced_prompt",
                "create_dataset_split",
                {
                    "train_ratio": train_ratio,
                    "validation_ratio": validation_ratio,
                    "test_ratio": test_ratio,
                },
                error=error_msg,
                duration=duration,
            )
            raise RuntimeError(error_msg)

    def get_dataset_stats(self) -> Dict[str, Any]:
        """Get dataset statistics."""
        start_time = time.time()

        try:
            stats = self.dataset_manager.get_dataset_stats()

            result = {
                "success": True,
                "dataset_stats": stats,
                "summary": f"Dataset stats: {stats['total_size']} total examples",
            }

            duration = time.time() - start_time
            self.logger.log_operation(
                "advanced_prompt",
                "get_dataset_stats",
                {},
                result,
                duration=duration,
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to get dataset stats: {e}"
            self.logger.log_operation(
                "advanced_prompt",
                "get_dataset_stats",
                {},
                error=error_msg,
                duration=duration,
            )
            raise RuntimeError(error_msg)

    def run_automated_optimization_cycle(self) -> Dict[str, Any]:
        """Run automated optimization cycle for all modes."""
        start_time = time.time()

        try:
            # Run automated optimization cycle
            results = self.continuous_workflow.run_automated_optimization_cycle()

            result = {
                "success": True,
                "optimization_results": results,
                "summary": f"Automated optimization cycle completed for {len(results)} modes",
            }

            duration = time.time() - start_time
            self.logger.log_operation(
                "advanced_prompt",
                "automated_optimization_cycle",
                {},
                result,
                duration=duration,
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to run automated optimization cycle: {e}"
            self.logger.log_operation(
                "advanced_prompt",
                "automated_optimization_cycle",
                {},
                error=error_msg,
                duration=duration,
            )
            raise RuntimeError(error_msg)

    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get optimization recommendations based on current state."""
        start_time = time.time()

        try:
            recommendations = self.continuous_workflow.get_optimization_recommendations()
            performance_metrics = self.continuous_workflow.get_performance_metrics()
            improvement_history = self.continuous_workflow.get_improvement_history()

            result = {
                "success": True,
                "recommendations": recommendations,
                "performance_metrics": performance_metrics,
                "improvement_history": improvement_history,
                "summary": f"Found {len(recommendations)} optimization recommendations",
            }

            duration = time.time() - start_time
            self.logger.log_operation(
                "advanced_prompt",
                "get_optimization_recommendations",
                {},
                result,
                duration=duration,
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to get optimization recommendations: {e}"
            self.logger.log_operation(
                "advanced_prompt",
                "get_optimization_recommendations",
                {},
                error=error_msg,
                duration=duration,
            )
            raise RuntimeError(error_msg)

    def evaluate_prompt_performance(
        self,
        mode: str,
        num_test_cases: int = 50,
    ) -> Dict[str, Any]:
        """Evaluate prompt performance on test cases."""
        start_time = time.time()

        try:
            # Validate mode
            try:
                prompt_mode = PromptMode(mode)
            except ValueError:
                raise ValueError(
                    f"Invalid mode: {mode}. Valid modes: {[m.value for m in PromptMode]}"
                )

            # Get test data
            test_data = self.dataset_manager.load_test_data()
            mode_test_data = [
                (input_data, output)
                for input_data, output in test_data
                if input_data.mode == prompt_mode
            ]

            # Limit test cases
            if len(mode_test_data) > num_test_cases:
                mode_test_data = mode_test_data[:num_test_cases]

            # Evaluate performance
            total_score = 0.0
            success_count = 0
            execution_times = []

            for input_data, expected_output in mode_test_data:
                # This would integrate with actual prompt execution
                # For now, use simplified evaluation
                case_start = time.time()

                # Simulate execution
                success = expected_output.success
                if success:
                    success_count += 1
                    total_score += 1.0

                case_duration = time.time() - case_start
                execution_times.append(case_duration)

            # Calculate metrics
            success_rate = success_count / len(mode_test_data) if mode_test_data else 0.0
            avg_execution_time = (
                sum(execution_times) / len(execution_times) if execution_times else 0.0
            )
            avg_score = total_score / len(mode_test_data) if mode_test_data else 0.0

            result = {
                "success": True,
                "mode": mode,
                "test_cases": len(mode_test_data),
                "success_rate": success_rate,
                "avg_score": avg_score,
                "avg_execution_time": avg_execution_time,
                "performance_grade": self._calculate_performance_grade(
                    success_rate, avg_score, avg_execution_time
                ),
                "summary": f"Performance evaluation: {success_rate:.2%} success rate, {avg_score:.2f} avg score",
            }

            duration = time.time() - start_time
            self.logger.log_operation(
                "advanced_prompt",
                "evaluate_performance",
                {"mode": mode, "num_test_cases": num_test_cases},
                result,
                duration=duration,
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to evaluate prompt performance: {e}"
            self.logger.log_operation(
                "advanced_prompt",
                "evaluate_performance",
                {"mode": mode, "num_test_cases": num_test_cases},
                error=error_msg,
                duration=duration,
            )
            raise RuntimeError(error_msg)

    def _calculate_performance_grade(
        self,
        success_rate: float,
        avg_score: float,
        avg_execution_time: float,
    ) -> str:
        """Calculate performance grade based on metrics."""

        # Grade based on success rate and score
        if success_rate >= 0.95 and avg_score >= 0.9:
            return "A"
        elif success_rate >= 0.9 and avg_score >= 0.8:
            return "B"
        elif success_rate >= 0.8 and avg_score >= 0.7:
            return "C"
        elif success_rate >= 0.7 and avg_score >= 0.6:
            return "D"
        else:
            return "F"
