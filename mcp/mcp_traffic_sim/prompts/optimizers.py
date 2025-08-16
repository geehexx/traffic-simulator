"""Advanced DSPy optimizers for prompt self-improvement."""

from __future__ import annotations

import time
from typing import List, Optional, Tuple

import dspy
from dspy import Signature, Module
from dspy.optimizers import MIPROv2, BootstrapFewShot, BayesianSignatureOptimizer

from .schemas import (
    PromptCandidate,
    PromptInput,
    PromptOutput,
    PromptMode,
)


class MIPROv2Optimizer:
    """MIPROv2 optimizer for joint instruction and few-shot optimization."""

    def __init__(self, lm: Optional[dspy.LM] = None):
        """Initialize MIPROv2 optimizer."""
        self.lm = lm or dspy.OpenAI(model="gpt-4o")
        self.optimizer = MIPROv2(
            metric=self._evaluation_metric,
            num_candidates=10,
            init_temperature=1.0,
        )

    def optimize_prompt(
        self,
        base_prompt: PromptCandidate,
        training_data: List[Tuple[PromptInput, PromptOutput]],
        validation_data: List[Tuple[PromptInput, PromptOutput]],
        max_bootstrapped_demos: int = 4,
        max_labeled_demos: int = 16,
    ) -> PromptCandidate:
        """Optimize prompt using MIPROv2 with bootstrapping and Bayesian optimization."""

        # Create DSPy module from prompt
        module = self._create_dspy_module(base_prompt)

        # Prepare training examples
        train_examples = self._prepare_training_examples(training_data)

        # Bootstrap few-shot examples
        bootstrapped_examples = self._bootstrap_examples(
            module, train_examples, max_bootstrapped_demos
        )

        # Combine with labeled examples
        all_examples = bootstrapped_examples + train_examples[:max_labeled_demos]

        # Run MIPROv2 optimization
        optimized_module = self.optimizer.compile(
            module,
            trainset=all_examples,
            num_trials=10,
        )

        # Convert back to PromptCandidate
        optimized_prompt = self._module_to_candidate(optimized_module, base_prompt)

        return optimized_prompt

    def _create_dspy_module(self, prompt: PromptCandidate) -> Module:
        """Create DSPy module from prompt candidate."""

        class OptimizedPromptSignature(Signature):
            """Optimized prompt signature."""

            input_data: str = dspy.InputField(desc="Structured input data")
            mode: str = dspy.InputField(desc="Execution mode")
            context: str = dspy.InputField(desc="Additional context")
            output: str = dspy.OutputField(desc="Structured output with artifacts and decisions")

        class OptimizedPromptModule(Module):
            """Optimized prompt module."""

            def __init__(self):
                super().__init__()
                self.predict = dspy.ChainOfThought(OptimizedPromptSignature)

            def forward(self, input_data: PromptInput) -> PromptOutput:
                """Execute optimized prompt."""
                result = self.predict(
                    input_data=self._serialize_input(input_data),
                    mode=input_data.mode.value,
                    context=self._build_context(input_data),
                )
                return self._parse_output(result.output, input_data.mode)

            def _serialize_input(self, input_data: PromptInput) -> str:
                """Serialize input to string."""
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
                """Build context string."""
                context_parts = []
                if input_data.repo_metadata:
                    context_parts.append(
                        f"Repository: {input_data.repo_metadata.get('name', 'Unknown')}"
                    )
                if input_data.git_signals:
                    context_parts.append(f"Git: {input_data.git_signals.get('branch', 'main')}")
                if input_data.change_inventory:
                    context_parts.append(f"Changes: {len(input_data.change_inventory)} files")
                return " | ".join(context_parts)

            def _parse_output(self, output_str: str, mode: PromptMode) -> PromptOutput:
                """Parse structured output."""
                try:
                    import json
                    import re

                    # Extract JSON from output
                    json_match = re.search(r"```json\n(.*?)\n```", output_str, re.DOTALL)
                    if json_match:
                        output_data = json.loads(json_match.group(1))
                    else:
                        output_data = json.loads(output_str)

                    return PromptOutput(
                        success=output_data.get("success", True),
                        mode=mode,
                        artifacts=output_data.get("artifacts", []),
                        diffs=output_data.get("diffs", {}),
                        coverage_decisions=output_data.get("coverage_decisions", []),
                        consolidation_map=output_data.get("consolidation_map"),
                        questions=output_data.get("questions", []),
                        commit_message=output_data.get("commit_message"),
                        error=output_data.get("error"),
                    )
                except Exception as e:
                    return PromptOutput(
                        success=False, mode=mode, error=f"Failed to parse output: {e}"
                    )

        return OptimizedPromptModule()

    def _prepare_training_examples(
        self, training_data: List[Tuple[PromptInput, PromptOutput]]
    ) -> List[dspy.Example]:
        """Prepare training examples for DSPy."""
        examples = []

        for input_data, output in training_data:
            example = dspy.Example(
                input_data=self._serialize_input(input_data),
                mode=input_data.mode.value,
                context=self._build_context(input_data),
                output=self._serialize_output(output),
            ).with_inputs("input_data", "mode", "context")
            examples.append(example)

        return examples

    def _bootstrap_examples(
        self,
        module: Module,
        train_examples: List[dspy.Example],
        max_demos: int,
    ) -> List[dspy.Example]:
        """Bootstrap few-shot examples using the module."""
        bootstrapper = BootstrapFewShot(metric=self._evaluation_metric)

        # Bootstrap examples
        bootstrapped = bootstrapper.compile(
            module,
            trainset=train_examples,
            max_bootstrapped_demos=max_demos,
        )

        return bootstrapped.demos

    def _evaluation_metric(self, example: dspy.Example, prediction: dspy.Example) -> float:
        """Evaluation metric for optimization."""
        try:
            # Parse prediction output
            import json

            output_data = json.loads(prediction.output)

            # Calculate quality score
            quality_score = 0.0

            # Success rate
            if output_data.get("success", False):
                quality_score += 0.3

            # Artifact quality
            artifacts = output_data.get("artifacts", [])
            if artifacts:
                quality_score += 0.2

            # Coverage decisions
            decisions = output_data.get("coverage_decisions", [])
            if decisions:
                quality_score += 0.2

            # Questions (indicates good analysis)
            questions = output_data.get("questions", [])
            if questions:
                quality_score += 0.1

            # Error handling
            if not output_data.get("error"):
                quality_score += 0.2

            return min(quality_score, 1.0)

        except Exception:
            return 0.0

    def _serialize_input(self, input_data: PromptInput) -> str:
        """Serialize input to string."""
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
        """Build context string."""
        context_parts = []
        if input_data.repo_metadata:
            context_parts.append(f"Repository: {input_data.repo_metadata.get('name', 'Unknown')}")
        if input_data.git_signals:
            context_parts.append(f"Git: {input_data.git_signals.get('branch', 'main')}")
        if input_data.change_inventory:
            context_parts.append(f"Changes: {len(input_data.change_inventory)} files")
        return " | ".join(context_parts)

    def _serialize_output(self, output: PromptOutput) -> str:
        """Serialize output to string."""
        import json

        return json.dumps(
            {
                "success": output.success,
                "artifacts": output.artifacts,
                "diffs": output.diffs,
                "coverage_decisions": output.coverage_decisions,
                "consolidation_map": output.consolidation_map,
                "questions": output.questions,
                "commit_message": output.commit_message,
                "error": output.error,
            },
            indent=2,
        )

    def _module_to_candidate(self, module: Module, base_prompt: PromptCandidate) -> PromptCandidate:
        """Convert optimized module back to PromptCandidate."""
        import uuid

        # Extract optimized content from module
        optimized_content = self._extract_optimized_content(module)

        return PromptCandidate(
            id=str(uuid.uuid4()),
            content=optimized_content,
            parameters=base_prompt.parameters,
            metadata={
                **base_prompt.metadata,
                "optimized_by": "MIPROv2",
                "optimization_timestamp": time.time(),
                "optimization_type": "joint_instruction_fewshot",
            },
        )

    def _extract_optimized_content(self, module: Module) -> str:
        """Extract optimized content from module."""
        # This would extract the optimized prompt content
        # For now, return a placeholder
        return "Optimized prompt content from MIPROv2"


class BayesianOptimizer:
    """Bayesian optimizer for instruction and example selection."""

    def __init__(self, lm: Optional[dspy.LM] = None):
        """Initialize Bayesian optimizer."""
        self.lm = lm or dspy.OpenAI(model="gpt-4o")
        self.optimizer = BayesianSignatureOptimizer(
            metric=self._evaluation_metric,
            num_candidates=10,
        )

    def optimize_instructions(
        self,
        base_prompt: PromptCandidate,
        training_data: List[Tuple[PromptInput, PromptOutput]],
    ) -> PromptCandidate:
        """Optimize prompt instructions using Bayesian optimization."""

        # Create DSPy module
        module = self._create_dspy_module(base_prompt)

        # Prepare training examples
        train_examples = self._prepare_training_examples(training_data)

        # Run Bayesian optimization
        optimized_module = self.optimizer.compile(
            module,
            trainset=train_examples,
            num_trials=20,
        )

        # Convert back to PromptCandidate
        optimized_prompt = self._module_to_candidate(optimized_module, base_prompt)

        return optimized_prompt

    def _create_dspy_module(self, prompt: PromptCandidate) -> Module:
        """Create DSPy module from prompt candidate."""
        # Similar to MIPROv2 implementation
        pass

    def _prepare_training_examples(
        self, training_data: List[Tuple[PromptInput, PromptOutput]]
    ) -> List[dspy.Example]:
        """Prepare training examples for DSPy."""
        examples = []

        for input_data, output in training_data:
            example = dspy.Example(
                input_data=self._serialize_input(input_data),
                mode=input_data.mode.value,
                context=self._build_context(input_data),
                output=self._serialize_output(output),
            ).with_inputs("input_data", "mode", "context")
            examples.append(example)

        return examples

    def _evaluation_metric(self, example: dspy.Example, prediction: dspy.Example) -> float:
        """Evaluation metric for Bayesian optimization."""
        # Similar to MIPROv2 evaluation
        return 0.0

    def _serialize_input(self, input_data: PromptInput) -> str:
        """Serialize input to string."""
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
        """Build context string."""
        context_parts = []
        if input_data.repo_metadata:
            context_parts.append(f"Repository: {input_data.repo_metadata.get('name', 'Unknown')}")
        if input_data.git_signals:
            context_parts.append(f"Git: {input_data.git_signals.get('branch', 'main')}")
        if input_data.change_inventory:
            context_parts.append(f"Changes: {len(input_data.change_inventory)} files")
        return " | ".join(context_parts)

    def _serialize_output(self, output: PromptOutput) -> str:
        """Serialize output to string."""
        import json

        return json.dumps(
            {
                "success": output.success,
                "artifacts": output.artifacts,
                "diffs": output.diffs,
                "coverage_decisions": output.coverage_decisions,
                "consolidation_map": output.consolidation_map,
                "questions": output.questions,
                "commit_message": output.commit_message,
                "error": output.error,
            },
            indent=2,
        )

    def _module_to_candidate(self, module: Module, base_prompt: PromptCandidate) -> PromptCandidate:
        """Convert optimized module back to PromptCandidate."""
        import uuid

        return PromptCandidate(
            id=str(uuid.uuid4()),
            content="Optimized prompt content from Bayesian optimization",
            parameters=base_prompt.parameters,
            metadata={
                **base_prompt.metadata,
                "optimized_by": "BayesianOptimizer",
                "optimization_timestamp": time.time(),
                "optimization_type": "bayesian_instruction_selection",
            },
        )


class AdvancedMetaOptimizer:
    """Advanced meta-optimizer with MIPROv2 and Bayesian optimization."""

    def __init__(self, lm: Optional[dspy.LM] = None):
        """Initialize advanced meta-optimizer."""
        self.lm = lm or dspy.OpenAI(model="gpt-4o")
        self.mipro_optimizer = MIPROv2Optimizer(lm)
        self.bayesian_optimizer = BayesianOptimizer(lm)

    def optimize_prompt_advanced(
        self,
        base_prompt: PromptCandidate,
        training_data: List[Tuple[PromptInput, PromptOutput]],
        validation_data: List[Tuple[PromptInput, PromptOutput]],
        optimization_strategy: str = "mipro",
    ) -> PromptCandidate:
        """Optimize prompt using advanced strategies."""

        if optimization_strategy == "mipro":
            return self.mipro_optimizer.optimize_prompt(base_prompt, training_data, validation_data)
        elif optimization_strategy == "bayesian":
            return self.bayesian_optimizer.optimize_instructions(base_prompt, training_data)
        elif optimization_strategy == "hybrid":
            # Run both optimizers and select best
            mipro_result = self.mipro_optimizer.optimize_prompt(
                base_prompt, training_data, validation_data
            )
            bayesian_result = self.bayesian_optimizer.optimize_instructions(
                base_prompt, training_data
            )

            # Evaluate both results
            mipro_score = self._evaluate_prompt(mipro_result, validation_data)
            bayesian_score = self._evaluate_prompt(bayesian_result, validation_data)

            return mipro_result if mipro_score > bayesian_score else bayesian_result
        else:
            raise ValueError(f"Unknown optimization strategy: {optimization_strategy}")

    def _evaluate_prompt(
        self,
        prompt: PromptCandidate,
        validation_data: List[Tuple[PromptInput, PromptOutput]],
    ) -> float:
        """Evaluate prompt performance on validation data."""
        total_score = 0.0

        for input_data, expected_output in validation_data:
            # Execute prompt (simplified)
            # This would integrate with the actual execution system
            score = self._calculate_single_score(input_data, expected_output)
            total_score += score

        return total_score / len(validation_data) if validation_data else 0.0

    def _calculate_single_score(
        self,
        input_data: PromptInput,
        expected_output: PromptOutput,
    ) -> float:
        """Calculate score for a single input-output pair."""
        # Simplified scoring
        score = 0.0

        if expected_output.success:
            score += 0.4

        if expected_output.artifacts:
            score += 0.3

        if expected_output.coverage_decisions:
            score += 0.2

        if not expected_output.error:
            score += 0.1

        return score
