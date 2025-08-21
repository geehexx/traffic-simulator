#!/usr/bin/env python3
"""DSPy Signatures for prompt management tasks."""

from __future__ import annotations

import dspy
from typing import List


class DocumentationGenerationSignature(dspy.Signature):
    """Signature for documentation generation task."""

    code_changes: str = dspy.InputField(desc="Description of the code changes made")
    context: str = dspy.InputField(desc="Additional context about the changes", default="")
    documentation: str = dspy.OutputField(desc="Generated documentation content")
    sections: List[str] = dspy.OutputField(desc="List of documentation sections created")


class RulesGenerationSignature(dspy.Signature):
    """Signature for rules generation task."""

    patterns: str = dspy.InputField(desc="Description of the patterns to create rules for")
    context: str = dspy.InputField(desc="Additional context about the patterns", default="")
    rules: str = dspy.OutputField(desc="Generated rules content")
    categories: List[str] = dspy.OutputField(desc="List of rule categories created")


class HybridMaintenanceSignature(dspy.Signature):
    """Signature for hybrid maintenance task."""

    mode: str = dspy.InputField(desc="Maintenance mode: docs, rules, or hybrid")
    task: str = dspy.InputField(desc="Description of the maintenance task")
    context: str = dspy.InputField(desc="Additional context for the task", default="")
    content: str = dspy.OutputField(desc="Generated content")
    mode_used: str = dspy.OutputField(desc="The mode that was used for generation")
    sections: List[str] = dspy.OutputField(desc="List of content sections created")


class PromptOptimizationSignature(dspy.Signature):
    """Signature for prompt optimization task."""

    original_prompt: str = dspy.InputField(desc="Original prompt to optimize")
    optimization_strategy: str = dspy.InputField(desc="Optimization strategy to use")
    context: str = dspy.InputField(desc="Context for optimization", default="")
    optimized_prompt: str = dspy.OutputField(desc="Optimized prompt")
    improvement_score: float = dspy.OutputField(desc="Improvement score (0.0-1.0)")
    optimization_metadata: str = dspy.OutputField(desc="Metadata about the optimization")


class PerformanceEvaluationSignature(dspy.Signature):
    """Signature for performance evaluation task."""

    prompt_id: str = dspy.InputField(desc="ID of the prompt to evaluate")
    test_cases: List[str] = dspy.InputField(desc="Test cases for evaluation")
    performance_metrics: str = dspy.OutputField(desc="Performance metrics and scores")
    quality_score: float = dspy.OutputField(desc="Overall quality score (0.0-1.0)")
    recommendations: List[str] = dspy.OutputField(desc="Recommendations for improvement")
