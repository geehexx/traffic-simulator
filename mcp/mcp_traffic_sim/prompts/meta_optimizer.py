"""Meta-optimizer for self-improving prompts using DSPy."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from .schemas import (
    PromptCandidate,
    PromptInput,
    PromptOptimizationResult,
    PromptEvaluation,
    MetaOptimizerConfig,
    PromptMode,
)
from .dspy_modules import MetaOptimizer as DSPyMetaOptimizer
from .evaluator import EvaluationFramework
from .registry import PromptRegistryManager


class MetaOptimizer:
    """Meta-optimizer for self-improving prompts."""

    def __init__(
        self, registry_manager: PromptRegistryManager, config: Optional[MetaOptimizerConfig] = None
    ):
        """Initialize meta-optimizer."""
        self.registry_manager = registry_manager
        self.config = config or MetaOptimizerConfig()
        self.evaluation_framework = EvaluationFramework()
        self.dspy_optimizer = DSPyMetaOptimizer()
        self.optimization_history = []

    def should_optimize(self) -> bool:
        """Check if optimization should be triggered."""
        if not self.optimization_history:
            return True

        last_optimization = self.optimization_history[-1]
        days_since_last = (datetime.utcnow() - last_optimization["timestamp"]).days

        return days_since_last >= self.config.optimization_frequency

    def generate_candidates(
        self, base_prompt: PromptCandidate, mode: PromptMode
    ) -> List[PromptCandidate]:
        """Generate candidate prompts with systematic variation."""
        candidates = []

        # Structural variations
        candidates.extend(self._generate_structural_variations(base_prompt, mode))

        # Brevity variations
        candidates.extend(self._generate_brevity_variations(base_prompt, mode))

        # Targeting variations
        candidates.extend(self._generate_targeting_variations(base_prompt, mode))

        return candidates[: self.config.candidate_count]

    def _generate_structural_variations(
        self, base_prompt: PromptCandidate, mode: PromptMode
    ) -> List[PromptCandidate]:
        """Generate structural variations of the prompt."""
        variations = []

        # Hierarchical organization variation
        content = base_prompt.content
        if "## Role" in content:
            # Reorganize sections
            sections = content.split("##")
            if len(sections) > 1:
                reorganized = "##".join(sections[1:])  # Remove first empty section
                variations.append(
                    self._create_candidate(
                        reorganized, mode, {"variation": "hierarchical_reorganization"}
                    )
                )

        # Gate placement variation
        if "## Decision Policy" in content:
            # Move decision policy to different position
            lines = content.split("\n")
            decision_section = []
            other_lines = []
            in_decision = False

            for line in lines:
                if line.strip() == "## Decision Policy":
                    in_decision = True
                    decision_section.append(line)
                elif line.startswith("##") and in_decision:
                    in_decision = False
                    other_lines.append(line)
                elif in_decision:
                    decision_section.append(line)
                else:
                    other_lines.append(line)

            if decision_section:
                reorganized = "\n".join(other_lines[:5] + decision_section + other_lines[5:])
                variations.append(
                    self._create_candidate(reorganized, mode, {"variation": "gate_placement"})
                )

        return variations

    def _generate_brevity_variations(
        self, base_prompt: PromptCandidate, mode: PromptMode
    ) -> List[PromptCandidate]:
        """Generate brevity variations of the prompt."""
        variations = []

        content = base_prompt.content

        # Concise variant
        concise_content = self._create_concise_variant(content)
        if concise_content != content:
            variations.append(
                self._create_candidate(concise_content, mode, {"variation": "concise"})
            )

        # Comprehensive variant
        comprehensive_content = self._create_comprehensive_variant(content)
        if comprehensive_content != content:
            variations.append(
                self._create_candidate(comprehensive_content, mode, {"variation": "comprehensive"})
            )

        return variations

    def _generate_targeting_variations(
        self, base_prompt: PromptCandidate, mode: PromptMode
    ) -> List[PromptCandidate]:
        """Generate targeting variations of the prompt."""
        variations = []

        content = base_prompt.content

        # Broad scope variant
        broad_content = self._create_broad_scope_variant(content)
        if broad_content != content:
            variations.append(
                self._create_candidate(broad_content, mode, {"variation": "broad_scope"})
            )

        # Specific scope variant
        specific_content = self._create_specific_scope_variant(content)
        if specific_content != content:
            variations.append(
                self._create_candidate(specific_content, mode, {"variation": "specific_scope"})
            )

        return variations

    def _create_concise_variant(self, content: str) -> str:
        """Create concise variant by removing verbose sections."""
        lines = content.split("\n")
        concise_lines = []

        skip_sections = ["## References", "## Token & Word Budget"]
        skip = False

        for line in lines:
            if any(section in line for section in skip_sections):
                skip = True
            elif line.startswith("##") and skip:
                skip = False
                concise_lines.append(line)
            elif not skip:
                concise_lines.append(line)

        return "\n".join(concise_lines)

    def _create_comprehensive_variant(self, content: str) -> str:
        """Create comprehensive variant by adding detailed sections."""
        if "## Detailed Procedures" not in content:
            detailed_section = """
## Detailed Procedures

### Input Validation
- Validate all required inputs are present
- Check for missing context or constraints
- Verify git signals are current and accurate

### Quality Assurance
- Run PDQI-9 evaluation for documentation
- Apply RGS scoring for rules
- Perform stability testing with perturbations
- Validate link integrity and cross-references

### Output Generation
- Generate deterministic, idempotent outputs
- Ensure minimal diffs and stable anchors
- Apply consolidation logic for duplicates
- Validate against project standards
"""
            content += detailed_section

        return content

    def _create_broad_scope_variant(self, content: str) -> str:
        """Create broad scope variant."""
        # Add broader applicability
        if "## Scope" not in content:
            scope_section = """
## Scope
- Universal applicability across all project components
- Handles any documentation or rule maintenance task
- Adapts to different project phases and contexts
"""
            content = content.replace("## Role", "## Scope" + scope_section + "\n## Role")

        return content

    def _create_specific_scope_variant(self, content: str) -> str:
        """Create specific scope variant."""
        # Add specific targeting
        if "## Specific Targeting" not in content:
            targeting_section = """
## Specific Targeting
- Focus on traffic simulation domain
- Prioritize performance and rendering guidelines
- Emphasize Arcade API consistency
- Target specific file patterns and modules
"""
            content = content.replace(
                "## Role", "## Specific Targeting" + targeting_section + "\n## Role"
            )

        return content

    def _create_candidate(
        self, content: str, mode: PromptMode, metadata: Dict[str, Any]
    ) -> PromptCandidate:
        """Create a prompt candidate."""
        import uuid

        return PromptCandidate(
            id=str(uuid.uuid4()),
            content=content,
            metadata={
                "mode": mode.value,
                "created_by": "meta_optimizer",
                "timestamp": datetime.utcnow().isoformat(),
                **metadata,
            },
        )

    def optimize_prompts(
        self, mode: PromptMode, test_inputs: Optional[List[PromptInput]] = None
    ) -> PromptOptimizationResult:
        """Optimize prompts for a specific mode."""
        start_time = time.time()

        try:
            # Get current active prompt
            active_prompt = self.registry_manager.get_active_prompt(mode)
            if not active_prompt:
                raise ValueError(f"No active prompt found for mode: {mode}")

            # Generate test inputs if not provided
            if not test_inputs:
                test_inputs = self._generate_test_inputs(mode)

            # Generate candidates
            candidates = self.generate_candidates(active_prompt, mode)

            # Evaluate candidates
            evaluations = []
            for candidate in candidates:
                evaluation = self.evaluation_framework.evaluate_candidate(candidate, test_inputs)
                evaluations.append(evaluation)

            # Select winner
            winner = self._select_winner(evaluations)

            # Generate improvement suggestions
            suggestions = self._generate_improvement_suggestions(evaluations, winner)

            # Create optimization result
            result = PromptOptimizationResult(
                winner_candidate=winner,
                evaluation_results=evaluations,
                optimization_metadata={
                    "mode": mode.value,
                    "candidates_generated": len(candidates),
                    "test_inputs_used": len(test_inputs),
                    "optimization_time": time.time() - start_time,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                improvement_metrics=self._calculate_improvement_metrics(active_prompt, winner),
                next_optimization_suggestions=suggestions,
            )

            # Record optimization history
            self.optimization_history.append(
                {
                    "timestamp": datetime.utcnow(),
                    "mode": mode.value,
                    "candidates_evaluated": len(candidates),
                    "winner_id": winner.id,
                    "improvement_score": result.improvement_metrics.get("overall_improvement", 0.0),
                }
            )

            return result

        except Exception as e:
            return PromptOptimizationResult(
                winner_candidate=None,
                evaluation_results=[],
                optimization_metadata={"error": str(e)},
                improvement_metrics={},
                next_optimization_suggestions=[f"Fix error: {e}"],
            )

    def _generate_test_inputs(self, mode: PromptMode) -> List[PromptInput]:
        """Generate standardized test inputs for evaluation."""
        test_inputs = []

        # Standard test scenarios
        scenarios = [
            {
                "mode": mode,
                "repo_metadata": {"name": "traffic-simulator", "type": "simulation"},
                "git_signals": {"branch": "main", "commit": "abc123"},
                "change_inventory": ["src/simulation.py", "docs/README.md"],
                "chat_decisions": ["Add performance optimization", "Update documentation"],
                "style_guide": {"format": "markdown", "standards": "PDQI-9"},
                "constraints": {"security": "redact_tokens", "performance": "30fps_target"},
            },
            {
                "mode": mode,
                "repo_metadata": {"name": "traffic-simulator", "type": "simulation"},
                "git_signals": {"branch": "feature/new-physics", "commit": "def456"},
                "change_inventory": ["src/physics.py", ".cursor/rules/physics.mdc"],
                "chat_decisions": ["Implement new physics engine", "Update rules"],
                "style_guide": {"format": "markdown", "standards": "RGS"},
                "constraints": {"deterministic": "true", "performance": "vectorized"},
            },
        ]

        for scenario in scenarios:
            test_input = PromptInput(**scenario)
            test_inputs.append(test_input)

        return test_inputs

    def _select_winner(self, evaluations: List[PromptEvaluation]) -> PromptCandidate:
        """Select winning candidate based on evaluation criteria."""
        if not evaluations:
            raise ValueError("No evaluations provided")

        # Filter by stability threshold
        stable_evaluations = [
            e
            for e in evaluations
            if e.quality_scores.stability_index >= self.config.stability_threshold
        ]

        if not stable_evaluations:
            # If no stable candidates, return the best overall
            return max(evaluations, key=lambda e: e.quality_scores.overall_score).candidate_id

        # Select best stable candidate
        winner_eval = max(stable_evaluations, key=lambda e: e.quality_scores.overall_score)
        return winner_eval.candidate_id

    def _generate_improvement_suggestions(
        self, evaluations: List[PromptEvaluation], winner: PromptCandidate
    ) -> List[str]:
        """Generate improvement suggestions based on evaluation results."""
        suggestions = []

        if not evaluations:
            suggestions.append("No evaluations available for improvement suggestions")
            return suggestions

        # Find winner evaluation
        winner_eval = next((e for e in evaluations if e.candidate_id == winner.id), None)
        if not winner_eval:
            suggestions.append("Winner evaluation not found")
            return suggestions

        # Analyze weaknesses
        if winner_eval.quality_scores.stability_index < 0.9:
            suggestions.append("Improve prompt stability with more deterministic instructions")

        if winner_eval.quality_scores.idempotency_score < 0.8:
            suggestions.append("Enhance idempotency with stable anchors and deterministic ordering")

        if winner_eval.quality_scores.duplication_score < 0.7:
            suggestions.append("Reduce duplication with better consolidation logic")

        if winner_eval.quality_scores.link_integrity_score < 0.8:
            suggestions.append("Improve link integrity and cross-reference validation")

        # Performance suggestions
        avg_execution_time = winner_eval.execution_metrics.get("avg_execution_time", 0)
        if avg_execution_time > 5.0:
            suggestions.append("Optimize execution time with more efficient prompt structure")

        success_rate = winner_eval.execution_metrics.get("success_rate", 1.0)
        if success_rate < 0.9:
            suggestions.append("Improve success rate with better error handling and validation")

        return suggestions

    def _calculate_improvement_metrics(
        self, original: PromptCandidate, winner: PromptCandidate
    ) -> Dict[str, float]:
        """Calculate improvement metrics."""
        # This would compare original vs winner performance
        # For now, return mock metrics
        return {
            "overall_improvement": 0.15,
            "stability_improvement": 0.08,
            "quality_improvement": 0.12,
            "efficiency_improvement": 0.05,
        }

    def apply_optimization(
        self,
        optimization_result: PromptOptimizationResult,
        mode: PromptMode,
        auto_apply: bool = False,
    ) -> bool:
        """Apply optimization result to registry."""
        if not optimization_result.winner_candidate:
            return False

        if not auto_apply and not self.config.auto_apply:
            # Store for manual review
            self._store_pending_optimization(optimization_result, mode)
            return False

        try:
            # Register new prompt
            prompt_id = self.registry_manager.register_prompt(
                content=optimization_result.winner_candidate.content,
                mode=mode,
                parameters=optimization_result.winner_candidate.parameters,
                metadata=optimization_result.winner_candidate.metadata,
            )

            # Set as active
            self.registry_manager.set_active_prompt(mode, prompt_id)

            # Create backup if configured
            if self.config.backup_before_apply:
                self._create_backup(mode)

            return True

        except Exception as e:
            print(f"Failed to apply optimization: {e}")
            return False

    def _store_pending_optimization(
        self, optimization_result: PromptOptimizationResult, mode: PromptMode
    ) -> None:
        """Store optimization result for manual review."""
        # This would store the result in a pending state
        # Implementation depends on storage requirements
        pass

    def _create_backup(self, mode: PromptMode) -> None:
        """Create backup of current prompt before applying optimization."""
        # This would create a backup of the current active prompt
        # Implementation depends on backup requirements
        pass

    def get_optimization_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get optimization history."""
        return self.optimization_history[-limit:]

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics."""
        if not self.optimization_history:
            return {"total_optimizations": 0}

        total_optimizations = len(self.optimization_history)
        avg_improvement = (
            sum(h.get("improvement_score", 0) for h in self.optimization_history)
            / total_optimizations
        )

        return {
            "total_optimizations": total_optimizations,
            "average_improvement": avg_improvement,
            "last_optimization": self.optimization_history[-1]["timestamp"].isoformat(),
            "optimization_frequency_days": self.config.optimization_frequency,
        }
