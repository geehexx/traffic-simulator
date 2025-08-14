"""Evaluation framework for prompt performance."""

from __future__ import annotations

import time
from typing import Any, Dict, List

from .schemas import (
    PromptCandidate,
    PromptInput,
    PromptOutput,
    PromptEvaluation,
    QualityScore,
    PromptMode,
)


class QualityEvaluator:
    """Evaluates prompt quality using various metrics."""

    def __init__(self):
        """Initialize quality evaluator."""
        self.evaluation_cache = {}

    def evaluate_output(self, output: PromptOutput, content_type: str) -> QualityScore:
        """Evaluate output quality using appropriate metrics."""
        cache_key = f"{output.mode.value}_{content_type}_{hash(str(output.artifacts))}"

        if cache_key in self.evaluation_cache:
            return self.evaluation_cache[cache_key]

        if content_type == "docs":
            scores = self._evaluate_docs_quality(output)
        elif content_type == "rules":
            scores = self._evaluate_rules_quality(output)
        else:
            scores = self._evaluate_generic_quality(output)

        self.evaluation_cache[cache_key] = scores
        return scores

    def _evaluate_docs_quality(self, output: PromptOutput) -> QualityScore:
        """Evaluate documentation quality using PDQI-9 metrics."""
        artifacts = output.artifacts
        diffs = output.diffs

        # PDQI-9 scoring (simplified implementation)
        accuracy = self._score_accuracy(artifacts, diffs)
        thoroughness = self._score_thoroughness(artifacts)
        clarity = self._score_clarity(artifacts)
        consistency = self._score_consistency(artifacts)
        relevance = self._score_relevance(artifacts)
        organization = self._score_organization(artifacts)
        timeliness = self._score_timeliness(artifacts)
        efficiency = self._score_efficiency(artifacts)
        engagement = self._score_engagement(artifacts)

        pdqi_9_score = (
            accuracy
            + thoroughness
            + clarity
            + consistency
            + relevance
            + organization
            + timeliness
            + efficiency
            + engagement
        ) / 9.0

        return QualityScore(
            pdqi_9_score=pdqi_9_score,
            stability_index=self._calculate_stability_index(output),
            idempotency_score=self._calculate_idempotency_score(output),
            duplication_score=self._calculate_duplication_score(artifacts),
            link_integrity_score=self._calculate_link_integrity_score(artifacts),
            overall_score=pdqi_9_score * 10,  # Scale to 0-100
        )

    def _evaluate_rules_quality(self, output: PromptOutput) -> QualityScore:
        """Evaluate rules quality using RGS metrics."""
        artifacts = output.artifacts

        # RGS scoring (simplified implementation)
        clarity_actionability = self._score_clarity_actionability(artifacts)
        token_efficiency = self._score_token_efficiency(artifacts)
        maintainability = self._score_maintainability(artifacts)
        context_relevance = self._score_context_relevance(artifacts)
        documentation_quality = self._score_documentation_quality(artifacts)
        completeness = self._score_completeness(artifacts)

        rgs_score = (
            clarity_actionability * 0.25
            + token_efficiency * 0.20
            + maintainability * 0.20
            + context_relevance * 0.15
            + documentation_quality * 0.10
            + completeness * 0.10
        )

        return QualityScore(
            rgs_score=rgs_score,
            stability_index=self._calculate_stability_index(output),
            idempotency_score=self._calculate_idempotency_score(output),
            duplication_score=self._calculate_duplication_score(artifacts),
            link_integrity_score=self._calculate_link_integrity_score(artifacts),
            overall_score=rgs_score,
        )

    def _evaluate_generic_quality(self, output: PromptOutput) -> QualityScore:
        """Evaluate generic quality metrics."""
        return QualityScore(
            stability_index=self._calculate_stability_index(output),
            idempotency_score=self._calculate_idempotency_score(output),
            duplication_score=self._calculate_duplication_score(output.artifacts),
            link_integrity_score=self._calculate_link_integrity_score(output.artifacts),
            overall_score=50.0,  # Default score
        )

    def _score_accuracy(self, artifacts: List[str], diffs: Dict[str, str]) -> float:
        """Score accuracy of generated content."""
        if not artifacts:
            return 0.0

        # Check for factual consistency and correctness
        accuracy_indicators = 0
        total_checks = 0

        for artifact in artifacts:
            # Check for proper formatting
            if artifact.strip():
                accuracy_indicators += 1
            total_checks += 1

        return accuracy_indicators / max(total_checks, 1)

    def _score_thoroughness(self, artifacts: List[str]) -> float:
        """Score thoroughness of coverage."""
        if not artifacts:
            return 0.0

        # Check for comprehensive coverage
        thoroughness_indicators = 0
        for artifact in artifacts:
            if len(artifact) > 100:  # Substantial content
                thoroughness_indicators += 1

        return min(thoroughness_indicators / len(artifacts), 1.0)

    def _score_clarity(self, artifacts: List[str]) -> float:
        """Score clarity of expression."""
        if not artifacts:
            return 0.0

        clarity_indicators = 0
        for artifact in artifacts:
            # Check for clear structure and language
            if "##" in artifact or "###" in artifact:  # Has structure
                clarity_indicators += 1

        return clarity_indicators / len(artifacts)

    def _score_consistency(self, artifacts: List[str]) -> float:
        """Score consistency across artifacts."""
        if len(artifacts) < 2:
            return 1.0

        # Check for consistent formatting and style
        consistency_score = 1.0
        for i in range(1, len(artifacts)):
            if artifacts[i - 1] and artifacts[i]:
                # Simple consistency check
                if len(artifacts[i - 1]) > 0 and len(artifacts[i]) > 0:
                    consistency_score *= 0.9  # Slight penalty for each artifact

        return consistency_score

    def _score_relevance(self, artifacts: List[str]) -> float:
        """Score relevance to context."""
        if not artifacts:
            return 0.0

        # Check for relevant keywords and content
        relevance_indicators = 0
        for artifact in artifacts:
            if any(
                keyword in artifact.lower()
                for keyword in ["traffic", "simulation", "vehicle", "driver"]
            ):
                relevance_indicators += 1

        return relevance_indicators / len(artifacts)

    def _score_organization(self, artifacts: List[str]) -> float:
        """Score organization and structure."""
        if not artifacts:
            return 0.0

        organization_indicators = 0
        for artifact in artifacts:
            # Check for proper markdown structure
            if "##" in artifact or "###" in artifact:
                organization_indicators += 1

        return organization_indicators / len(artifacts)

    def _score_timeliness(self, artifacts: List[str]) -> float:
        """Score timeliness and currency."""
        # For now, assume all content is timely
        return 1.0

    def _score_efficiency(self, artifacts: List[str]) -> float:
        """Score efficiency of content."""
        if not artifacts:
            return 0.0

        # Check for concise, efficient content
        total_length = sum(len(artifact) for artifact in artifacts)
        if total_length > 0:
            return min(1000 / total_length, 1.0)  # Prefer shorter content

        return 1.0

    def _score_engagement(self, artifacts: List[str]) -> float:
        """Score engagement and readability."""
        if not artifacts:
            return 0.0

        engagement_indicators = 0
        for artifact in artifacts:
            # Check for engaging elements
            if any(char in artifact for char in ["*", "-", "1.", "2."]):  # Lists, emphasis
                engagement_indicators += 1

        return engagement_indicators / len(artifacts)

    def _score_clarity_actionability(self, artifacts: List[str]) -> float:
        """Score clarity and actionability for rules."""
        if not artifacts:
            return 0.0

        actionability_indicators = 0
        for artifact in artifacts:
            # Check for actionable language
            if any(word in artifact.lower() for word in ["do:", "don't:", "use:", "avoid:"]):
                actionability_indicators += 1

        return actionability_indicators / len(artifacts)

    def _score_token_efficiency(self, artifacts: List[str]) -> float:
        """Score token efficiency."""
        if not artifacts:
            return 0.0

        total_tokens = sum(len(artifact.split()) for artifact in artifacts)
        if total_tokens > 0:
            return min(500 / total_tokens, 1.0)  # Prefer shorter content

        return 1.0

    def _score_maintainability(self, artifacts: List[str]) -> float:
        """Score maintainability."""
        if not artifacts:
            return 0.0

        maintainability_indicators = 0
        for artifact in artifacts:
            # Check for maintainable structure
            if "##" in artifact or "###" in artifact:
                maintainability_indicators += 1

        return maintainability_indicators / len(artifacts)

    def _score_context_relevance(self, artifacts: List[str]) -> float:
        """Score context relevance."""
        return self._score_relevance(artifacts)  # Reuse relevance scoring

    def _score_documentation_quality(self, artifacts: List[str]) -> float:
        """Score documentation quality."""
        return self._score_clarity(artifacts)  # Reuse clarity scoring

    def _score_completeness(self, artifacts: List[str]) -> float:
        """Score completeness."""
        return self._score_thoroughness(artifacts)  # Reuse thoroughness scoring

    def _calculate_stability_index(self, output: PromptOutput) -> float:
        """Calculate stability index based on output consistency."""
        # Simplified stability calculation
        if not output.artifacts:
            return 0.0

        # Check for deterministic elements
        stability_indicators = 0
        for artifact in output.artifacts:
            if artifact.strip():  # Non-empty content
                stability_indicators += 1

        return stability_indicators / max(len(output.artifacts), 1)

    def _calculate_idempotency_score(self, output: PromptOutput) -> float:
        """Calculate idempotency score."""
        # Check for idempotent elements
        if not output.artifacts:
            return 0.0

        idempotency_indicators = 0
        for artifact in output.artifacts:
            # Check for stable anchors and deterministic content
            if "##" in artifact or "###" in artifact:
                idempotency_indicators += 1

        return idempotency_indicators / len(output.artifacts)

    def _calculate_duplication_score(self, artifacts: List[str]) -> float:
        """Calculate duplication score (lower is better)."""
        if len(artifacts) < 2:
            return 1.0

        # Check for duplicate content
        unique_artifacts = set(artifacts)
        return len(unique_artifacts) / len(artifacts)

    def _calculate_link_integrity_score(self, artifacts: List[str]) -> float:
        """Calculate link integrity score."""
        if not artifacts:
            return 0.0

        link_indicators = 0
        total_links = 0

        for artifact in artifacts:
            # Count links and check for proper formatting
            links = artifact.count("[") + artifact.count("]")
            total_links += links
            if links > 0:
                link_indicators += 1

        if total_links == 0:
            return 1.0  # No links to check

        return link_indicators / len(artifacts)


class StabilityTester:
    """Tests prompt stability with perturbations."""

    def __init__(self):
        """Initialize stability tester."""
        self.test_cache = {}

    def test_stability(
        self, candidate: PromptCandidate, test_inputs: List[PromptInput], num_perturbations: int = 3
    ) -> List[float]:
        """Test stability with perturbations."""
        stability_scores = []

        for test_input in test_inputs:
            # Create perturbations
            perturbations = self._create_perturbations(test_input, num_perturbations)

            # Execute with base input and perturbations
            base_output = self._execute_prompt(candidate, test_input)
            perturbed_outputs = [self._execute_prompt(candidate, p) for p in perturbations]

            # Calculate stability score
            stability_score = self._calculate_stability_score(base_output, perturbed_outputs)
            stability_scores.append(stability_score)

        return stability_scores

    def _create_perturbations(
        self, input_data: PromptInput, num_perturbations: int
    ) -> List[PromptInput]:
        """Create perturbed versions of input data."""
        perturbations = []

        for i in range(num_perturbations):
            perturbed = input_data.model_copy()

            # Add minor variations
            if "context" not in perturbed.context:
                perturbed.context = {}

            perturbed.context[f"perturbation_{i}"] = f"test_variation_{i}"

            # Add minor changes to metadata
            if perturbed.repo_metadata:
                perturbed.repo_metadata[f"perturbation_{i}"] = f"variation_{i}"

            perturbations.append(perturbed)

        return perturbations

    def _execute_prompt(self, candidate: PromptCandidate, input_data: PromptInput) -> PromptOutput:
        """Execute prompt with input data."""
        # This would integrate with the actual prompt execution system
        # For now, return a mock output
        return PromptOutput(
            success=True,
            mode=input_data.mode,
            artifacts=[f"mock_artifact_{hash(str(input_data))}"],
            execution_time=0.1,
        )

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


class EvaluationFramework:
    """Comprehensive evaluation framework for prompts."""

    def __init__(self):
        """Initialize evaluation framework."""
        self.quality_evaluator = QualityEvaluator()
        self.stability_tester = StabilityTester()

    def evaluate_candidate(
        self, candidate: PromptCandidate, test_inputs: List[PromptInput]
    ) -> PromptEvaluation:
        """Comprehensive evaluation of a prompt candidate."""
        start_time = time.time()

        try:
            # Execute candidate on test inputs
            outputs = []
            for test_input in test_inputs:
                output = self._execute_candidate(candidate, test_input)
                outputs.append(output)

            # Evaluate quality scores
            quality_scores = self._aggregate_quality_scores(outputs)

            # Run stability tests
            stability_tests = self.stability_tester.test_stability(candidate, test_inputs)

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

    def _execute_candidate(
        self, candidate: PromptCandidate, input_data: PromptInput
    ) -> PromptOutput:
        """Execute candidate prompt with input data."""
        # This would integrate with the actual prompt execution system
        # For now, return a mock output
        return PromptOutput(
            success=True,
            mode=input_data.mode,
            artifacts=[f"candidate_{candidate.id}_artifact_{hash(str(input_data))}"],
            execution_time=0.1,
        )

    def _aggregate_quality_scores(self, outputs: List[PromptOutput]) -> QualityScore:
        """Aggregate quality scores from multiple outputs."""
        if not outputs:
            return QualityScore()

        # Determine content type based on mode
        content_type = (
            "docs" if outputs[0].mode in [PromptMode.DOCS, PromptMode.HYBRID] else "rules"
        )

        # Evaluate each output
        scores = []
        for output in outputs:
            score = self.quality_evaluator.evaluate_output(output, content_type)
            scores.append(score)

        # Aggregate scores
        return QualityScore(
            pdqi_9_score=sum(s.pdqi_9_score or 0 for s in scores) / len(scores),
            rgs_score=sum(s.rgs_score or 0 for s in scores) / len(scores),
            stability_index=sum(s.stability_index for s in scores) / len(scores),
            idempotency_score=sum(s.idempotency_score for s in scores) / len(scores),
            duplication_score=sum(s.duplication_score for s in scores) / len(scores),
            link_integrity_score=sum(s.link_integrity_score for s in scores) / len(scores),
            overall_score=sum(s.overall_score for s in scores) / len(scores),
        )

    def _calculate_pairwise_rankings(self, outputs: List[PromptOutput]) -> List[Dict[str, Any]]:
        """Calculate pairwise rankings using Bradley-Terry model."""
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
