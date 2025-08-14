"""DSPy modules for programmatic prompt management."""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import dspy
from dspy import Signature

from .schemas import (
    PromptInput,
    PromptOutput,
    PromptCandidate,
    PromptEvaluation,
    PromptMode,
    QualityScore,
)


class PromptSignature(Signature):
    """Signature for prompt execution."""

    input_data: str = dspy.InputField(desc="Structured input data for prompt execution")
    mode: str = dspy.InputField(desc="Execution mode (docs, rules, hybrid, etc.)")
    context: str = dspy.InputField(desc="Additional context and constraints")

    output: str = dspy.OutputField(desc="Structured output with artifacts, diffs, and decisions")


class QualityEvaluationSignature(Signature):
    """Signature for quality evaluation."""

    content: str = dspy.InputField(desc="Content to evaluate")
    content_type: str = dspy.InputField(desc="Type of content (docs, rules)")
    criteria: str = dspy.InputField(desc="Evaluation criteria and rubrics")

    scores: str = dspy.OutputField(desc="Quality scores in structured format")


class StabilityTestSignature(Signature):
    """Signature for stability testing."""

    prompt: str = dspy.InputField(desc="Prompt to test")
    test_inputs: str = dspy.InputField(desc="Standardized test inputs")
    perturbations: str = dspy.InputField(desc="Perturbation parameters")

    stability_index: str = dspy.OutputField(desc="Stability index and variance metrics")


class PromptExecutor(dspy.Module):
    """DSPy module for executing prompts with structured outputs."""

    def __init__(self, lm: Optional[dspy.LM] = None):
        super().__init__()
        self.lm = lm or dspy.OpenAI(model="gpt-4o")
        self.prompt_executor = dspy.ChainOfThought(PromptSignature)
        self.quality_evaluator = dspy.ChainOfThought(QualityEvaluationSignature)
        self.stability_tester = dspy.ChainOfThought(StabilityTestSignature)

    def forward(self, input_data: PromptInput) -> PromptOutput:
        """Execute prompt with structured input and output."""
        start_time = time.time()

        try:
            # Prepare input for DSPy
            input_str = self._serialize_input(input_data)

            # Execute prompt
            result = self.prompt_executor(
                input_data=input_str,
                mode=input_data.mode.value,
                context=self._build_context(input_data),
            )

            # Parse structured output
            output = self._parse_output(result.output, input_data.mode)

            # Add execution metadata
            output.execution_time = time.time() - start_time

            return output

        except Exception as e:
            return PromptOutput(
                success=False,
                mode=input_data.mode,
                error=str(e),
                execution_time=time.time() - start_time,
            )

    def _serialize_input(self, input_data: PromptInput) -> str:
        """Serialize structured input to string format."""
        import json

        return json.dumps(
            {
                "repo_metadata": input_data.repo_metadata,
                "git_signals": input_data.git_signals,
                "change_inventory": input_data.change_inventory,
                "chat_decisions": input_data.chat_decisions,
                "style_guide": input_data.style_guide,
                "constraints": input_data.constraints,
                "context": input_data.context,
            },
            indent=2,
        )

    def _build_context(self, input_data: PromptInput) -> str:
        """Build context string from input data."""
        context_parts = []

        if input_data.repo_metadata:
            context_parts.append(f"Repository: {input_data.repo_metadata.get('name', 'Unknown')}")

        if input_data.git_signals:
            context_parts.append(f"Git: {input_data.git_signals.get('branch', 'main')}")

        if input_data.change_inventory:
            context_parts.append(f"Changes: {len(input_data.change_inventory)} files")

        return " | ".join(context_parts)

    def _parse_output(self, output_str: str, mode: PromptMode) -> PromptOutput:
        """Parse structured output from string."""
        try:
            import json
            import re

            # Extract JSON from output (handle markdown formatting)
            json_match = re.search(r"```json\n(.*?)\n```", output_str, re.DOTALL)
            if json_match:
                output_data = json.loads(json_match.group(1))
            else:
                # Fallback: try to parse entire output as JSON
                output_data = json.loads(output_str)

            return PromptOutput(
                success=output_data.get("success", True),
                mode=mode,
                artifacts=output_data.get("artifacts", []),
                diffs=output_data.get("diffs", {}),
                quality_scores=self._parse_quality_scores(output_data.get("quality_scores")),
                coverage_decisions=output_data.get("coverage_decisions", []),
                consolidation_map=output_data.get("consolidation_map"),
                questions=output_data.get("questions", []),
                commit_message=output_data.get("commit_message"),
                error=output_data.get("error"),
            )

        except Exception as e:
            return PromptOutput(success=False, mode=mode, error=f"Failed to parse output: {e}")

    def _parse_quality_scores(
        self, scores_data: Optional[Dict[str, Any]]
    ) -> Optional[QualityScore]:
        """Parse quality scores from output data."""
        if not scores_data:
            return None

        return QualityScore(
            pdqi_9_score=scores_data.get("pdqi_9_score"),
            rgs_score=scores_data.get("rgs_score"),
            stability_index=scores_data.get("stability_index", 0.0),
            idempotency_score=scores_data.get("idempotency_score", 0.0),
            duplication_score=scores_data.get("duplication_score", 0.0),
            link_integrity_score=scores_data.get("link_integrity_score", 0.0),
            overall_score=scores_data.get("overall_score", 0.0),
        )


class PromptEvaluator(dspy.Module):
    """DSPy module for evaluating prompt candidates."""

    def __init__(self, lm: Optional[dspy.LM] = None):
        super().__init__()
        self.lm = lm or dspy.OpenAI(model="gpt-4o")
        self.quality_evaluator = dspy.ChainOfThought(QualityEvaluationSignature)
        self.stability_tester = dspy.ChainOfThought(StabilityTestSignature)

    def evaluate_candidate(
        self, candidate: PromptCandidate, test_inputs: List[PromptInput]
    ) -> PromptEvaluation:
        """Evaluate a prompt candidate against test inputs."""
        start_time = time.time()

        try:
            # Execute candidate on test inputs
            outputs = []
            for test_input in test_inputs:
                executor = PromptExecutor(self.lm)
                output = executor.forward(test_input)
                outputs.append(output)

            # Evaluate quality scores
            quality_scores = self._aggregate_quality_scores(outputs)

            # Run stability tests
            stability_tests = self._run_stability_tests(candidate, test_inputs)

            # Calculate pairwise rankings
            pairwise_rankings = self._calculate_pairwise_rankings(outputs)

            return PromptEvaluation(
                candidate_id=candidate.id,
                quality_scores=quality_scores,
                stability_tests=stability_tests,
                pairwise_rankings=pairwise_rankings,
                execution_metrics={
                    "avg_execution_time": sum(o.execution_time for o in outputs) / len(outputs),
                    "success_rate": sum(1 for o in outputs if o.success) / len(outputs),
                },
                artifacts_generated=[artifact for o in outputs for artifact in o.artifacts],
                evaluation_time=time.time() - start_time,
            )

        except Exception as e:
            return PromptEvaluation(
                candidate_id=candidate.id,
                quality_scores=QualityScore(),
                error=str(e),
                evaluation_time=time.time() - start_time,
            )

    def _aggregate_quality_scores(self, outputs: List[PromptOutput]) -> QualityScore:
        """Aggregate quality scores from multiple outputs."""
        if not outputs:
            return QualityScore()

        valid_scores = [o.quality_scores for o in outputs if o.quality_scores]
        if not valid_scores:
            return QualityScore()

        return QualityScore(
            pdqi_9_score=sum(s.pdqi_9_score or 0 for s in valid_scores) / len(valid_scores),
            rgs_score=sum(s.rgs_score or 0 for s in valid_scores) / len(valid_scores),
            stability_index=sum(s.stability_index for s in valid_scores) / len(valid_scores),
            idempotency_score=sum(s.idempotency_score for s in valid_scores) / len(valid_scores),
            duplication_score=sum(s.duplication_score for s in valid_scores) / len(valid_scores),
            link_integrity_score=sum(s.link_integrity_score for s in valid_scores)
            / len(valid_scores),
            overall_score=sum(s.overall_score for s in valid_scores) / len(valid_scores),
        )

    def _run_stability_tests(
        self, candidate: PromptCandidate, test_inputs: List[PromptInput]
    ) -> List[float]:
        """Run stability tests with perturbations."""
        stability_scores = []

        for test_input in test_inputs:
            # Create perturbations
            perturbations = self._create_perturbations(test_input)

            # Execute with perturbations
            executor = PromptExecutor(self.lm)
            base_output = executor.forward(test_input)

            perturbed_outputs = []
            for perturbed_input in perturbations:
                output = executor.forward(perturbed_input)
                perturbed_outputs.append(output)

            # Calculate stability score
            stability_score = self._calculate_stability_score(base_output, perturbed_outputs)
            stability_scores.append(stability_score)

        return stability_scores

    def _create_perturbations(self, input_data: PromptInput) -> List[PromptInput]:
        """Create perturbed versions of input data."""
        perturbations = []

        # Add minor variations to context
        for i in range(3):  # Create 3 perturbations
            perturbed = input_data.model_copy()
            if "context" not in perturbed.context:
                perturbed.context = {}
            perturbed.context[f"perturbation_{i}"] = f"minor_variation_{i}"
            perturbations.append(perturbed)

        return perturbations

    def _calculate_stability_score(
        self, base_output: PromptOutput, perturbed_outputs: List[PromptOutput]
    ) -> float:
        """Calculate stability score based on output consistency."""
        if not perturbed_outputs:
            return 1.0

        # Compare artifacts consistency
        base_artifacts = set(base_output.artifacts)
        consistent_count = 0

        for perturbed_output in perturbed_outputs:
            perturbed_artifacts = set(perturbed_output.artifacts)
            if base_artifacts == perturbed_artifacts:
                consistent_count += 1

        return consistent_count / len(perturbed_outputs)

    def _calculate_pairwise_rankings(self, outputs: List[PromptOutput]) -> List[Dict[str, Any]]:
        """Calculate pairwise rankings using Bradley-Terry model."""
        # Simplified implementation - would need full Bradley-Terry implementation
        rankings = []

        for i, output1 in enumerate(outputs):
            for j, output2 in enumerate(outputs[i + 1 :], i + 1):
                ranking = {
                    "output_1": i,
                    "output_2": j,
                    "preference": 1 if output1.overall_score > output2.overall_score else -1,
                    "confidence": abs(output1.overall_score - output2.overall_score) / 100.0,
                }
                rankings.append(ranking)

        return rankings


class MetaOptimizer(dspy.Module):
    """DSPy module for meta-optimization of prompts."""

    def __init__(self, lm: Optional[dspy.LM] = None):
        super().__init__()
        self.lm = lm or dspy.OpenAI(model="gpt-4o")
        self.evaluator = PromptEvaluator(lm)
        self.optimizer = dspy.ReAct("optimize_prompts")

    def optimize_prompts(
        self,
        candidates: List[PromptCandidate],
        test_inputs: List[PromptInput],
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Optimize prompt candidates using DSPy optimization."""
        try:
            # Evaluate all candidates
            evaluations = []
            for candidate in candidates:
                evaluation = self.evaluator.evaluate_candidate(candidate, test_inputs)
                evaluations.append(evaluation)

            # Select winner based on criteria
            winner = self._select_winner(evaluations, config)

            # Generate improvement suggestions
            suggestions = self._generate_improvement_suggestions(evaluations, winner)

            return {
                "winner": winner,
                "evaluations": evaluations,
                "improvement_suggestions": suggestions,
                "optimization_metadata": {
                    "candidates_evaluated": len(candidates),
                    "test_inputs_used": len(test_inputs),
                    "optimization_time": time.time(),
                },
            }

        except Exception as e:
            return {
                "error": str(e),
                "winner": None,
                "evaluations": [],
                "improvement_suggestions": [],
            }

    def _select_winner(
        self, evaluations: List[PromptEvaluation], config: Dict[str, Any]
    ) -> Optional[PromptEvaluation]:
        """Select winning candidate based on evaluation criteria."""
        if not evaluations:
            return None

        stability_threshold = config.get("stability_threshold", 0.85)

        # Filter by stability threshold
        stable_evaluations = [
            e for e in evaluations if e.quality_scores.stability_index >= stability_threshold
        ]

        if not stable_evaluations:
            # If no stable candidates, return the best overall
            return max(evaluations, key=lambda e: e.quality_scores.overall_score)

        # Select best stable candidate
        return max(stable_evaluations, key=lambda e: e.quality_scores.overall_score)

    def _generate_improvement_suggestions(
        self, evaluations: List[PromptEvaluation], winner: Optional[PromptEvaluation]
    ) -> List[str]:
        """Generate improvement suggestions based on evaluation results."""
        suggestions = []

        if not winner:
            suggestions.append("No stable candidates found - consider reducing complexity")
            return suggestions

        # Analyze weaknesses
        if winner.quality_scores.stability_index < 0.9:
            suggestions.append("Improve prompt stability with more deterministic instructions")

        if winner.quality_scores.idempotency_score < 0.8:
            suggestions.append("Enhance idempotency with stable anchors and deterministic ordering")

        if winner.quality_scores.duplication_score < 0.7:
            suggestions.append("Reduce duplication with better consolidation logic")

        return suggestions
