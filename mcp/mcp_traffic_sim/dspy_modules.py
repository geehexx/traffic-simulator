#!/usr/bin/env python3
"""DSPy modules for prompt management tasks."""

from __future__ import annotations

import dspy
from typing import Any, Dict, List, Optional

from dspy_signatures import (
    DocumentationGenerationSignature,
    RulesGenerationSignature,
    HybridMaintenanceSignature,
    PromptOptimizationSignature,
    PerformanceEvaluationSignature,
)


class DocumentationGenerator(dspy.Module):
    """DSPy module for generating documentation."""

    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(DocumentationGenerationSignature)

    def forward(self, code_changes: str, context: str = "") -> Dict[str, Any]:
        """Generate documentation for code changes."""
        result = self.generate(code_changes=code_changes, context=context)

        return {
            "documentation": result.documentation,
            "sections": result.sections,
            "metadata": {
                "module": "DocumentationGenerator",
                "input_code_changes": code_changes,
                "input_context": context,
            },
        }


class RulesGenerator(dspy.Module):
    """DSPy module for generating rules."""

    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(RulesGenerationSignature)

    def forward(self, patterns: str, context: str = "") -> Dict[str, Any]:
        """Generate rules for patterns."""
        result = self.generate(patterns=patterns, context=context)

        return {
            "rules": result.rules,
            "categories": result.categories,
            "metadata": {
                "module": "RulesGenerator",
                "input_patterns": patterns,
                "input_context": context,
            },
        }


class HybridMaintainer(dspy.Module):
    """DSPy module for hybrid maintenance tasks."""

    def __init__(self):
        super().__init__()
        self.maintain = dspy.ChainOfThought(HybridMaintenanceSignature)

    def forward(self, mode: str, task: str, context: str = "") -> Dict[str, Any]:
        """Perform hybrid maintenance task."""
        result = self.maintain(mode=mode, task=task, context=context)

        return {
            "content": result.content,
            "mode_used": result.mode_used,
            "sections": result.sections,
            "metadata": {
                "module": "HybridMaintainer",
                "input_mode": mode,
                "input_task": task,
                "input_context": context,
            },
        }


class PromptOptimizer(dspy.Module):
    """DSPy module for optimizing prompts."""

    def __init__(self):
        super().__init__()
        self.optimize = dspy.ChainOfThought(PromptOptimizationSignature)

    def forward(self, original_prompt: str, strategy: str, context: str = "") -> Dict[str, Any]:
        """Optimize a prompt using the specified strategy."""
        result = self.optimize(
            original_prompt=original_prompt, optimization_strategy=strategy, context=context
        )

        return {
            "optimized_prompt": result.optimized_prompt,
            "improvement_score": result.improvement_score,
            "optimization_metadata": result.optimization_metadata,
            "metadata": {
                "module": "PromptOptimizer",
                "input_original_prompt": original_prompt,
                "input_strategy": strategy,
                "input_context": context,
            },
        }


class PerformanceEvaluator(dspy.Module):
    """DSPy module for evaluating prompt performance."""

    def __init__(self):
        super().__init__()
        self.evaluate = dspy.ChainOfThought(PerformanceEvaluationSignature)

    def forward(self, prompt_id: str, test_cases: List[str]) -> Dict[str, Any]:
        """Evaluate prompt performance on test cases."""
        result = self.evaluate(prompt_id=prompt_id, test_cases=test_cases)

        return {
            "performance_metrics": result.performance_metrics,
            "quality_score": result.quality_score,
            "recommendations": result.recommendations,
            "metadata": {
                "module": "PerformanceEvaluator",
                "input_prompt_id": prompt_id,
                "input_test_cases": test_cases,
            },
        }


class DSPyPromptRegistry:
    """Registry for DSPy-based prompt management."""

    def __init__(self):
        """Initialize DSPy prompt registry."""
        self.modules = {
            "generate_docs": DocumentationGenerator(),
            "generate_rules": RulesGenerator(),
            "hybrid_maintenance": HybridMaintainer(),
            "optimize_prompt": PromptOptimizer(),
            "evaluate_performance": PerformanceEvaluator(),
        }

    def get_module(self, module_name: str) -> Optional[dspy.Module]:
        """Get a DSPy module by name."""
        return self.modules.get(module_name)

    def list_modules(self) -> List[str]:
        """List available DSPy modules."""
        return list(self.modules.keys())

    def execute_module(self, module_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a DSPy module with given parameters."""
        module = self.get_module(module_name)
        if not module:
            raise ValueError(f"Module '{module_name}' not found")

        return module.forward(**kwargs)
