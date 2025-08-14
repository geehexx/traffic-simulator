"""Pydantic schemas for structured prompt outputs."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PromptMode(str, Enum):
    """Available prompt modes."""

    DOCS = "docs"
    RULES = "rules"
    HYBRID = "hybrid"
    ANALYZE = "analyze"
    PLAN_OPTIMIZE = "plan-optimize"
    REGENERATE = "regenerate"
    CONSOLIDATE = "consolidate"


class QualityScore(BaseModel):
    """Quality scoring results."""

    pdqi_9_score: Optional[float] = None  # For documentation
    rgs_score: Optional[float] = None  # For rules
    stability_index: float = Field(ge=0.0, le=1.0)
    idempotency_score: float = Field(ge=0.0, le=1.0)
    duplication_score: float = Field(ge=0.0, le=1.0)
    link_integrity_score: float = Field(ge=0.0, le=1.0)
    overall_score: float = Field(ge=0.0, le=100.0)


class PromptInput(BaseModel):
    """Structured input for prompt execution."""

    mode: PromptMode
    repo_metadata: Dict[str, Any] = Field(default_factory=dict)
    git_signals: Dict[str, Any] = Field(default_factory=dict)
    change_inventory: List[str] = Field(default_factory=list)
    chat_decisions: List[str] = Field(default_factory=list)
    style_guide: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)


class PromptOutput(BaseModel):
    """Structured output from prompt execution."""

    success: bool
    mode: PromptMode
    artifacts: List[str] = Field(default_factory=list)
    diffs: Dict[str, str] = Field(default_factory=dict)
    quality_scores: Optional[QualityScore] = None
    coverage_decisions: List[Dict[str, Any]] = Field(default_factory=list)
    consolidation_map: Optional[Dict[str, Any]] = None
    questions: List[str] = Field(default_factory=list)
    commit_message: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0


class PromptCandidate(BaseModel):
    """A prompt candidate for evaluation."""

    id: str
    content: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PromptEvaluation(BaseModel):
    """Evaluation results for a prompt candidate."""

    candidate_id: str
    quality_scores: QualityScore
    stability_tests: List[float] = Field(default_factory=list)
    pairwise_rankings: List[Dict[str, Any]] = Field(default_factory=list)
    execution_metrics: Dict[str, float] = Field(default_factory=dict)
    artifacts_generated: List[str] = Field(default_factory=list)
    evaluation_time: float = 0.0


class PromptOptimizationResult(BaseModel):
    """Result of prompt optimization process."""

    winner_candidate: PromptCandidate
    evaluation_results: List[PromptEvaluation]
    optimization_metadata: Dict[str, Any] = Field(default_factory=dict)
    improvement_metrics: Dict[str, float] = Field(default_factory=dict)
    next_optimization_suggestions: List[str] = Field(default_factory=list)


class PromptRegistry(BaseModel):
    """Registry of available prompts."""

    prompts: Dict[str, PromptCandidate] = Field(default_factory=dict)
    active_prompts: Dict[PromptMode, str] = Field(default_factory=dict)
    version_history: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MetaOptimizerConfig(BaseModel):
    """Configuration for meta-optimizer."""

    optimization_frequency: int = Field(default=7, description="Days between optimizations")
    candidate_count: int = Field(default=6, ge=4, le=10)
    stability_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    max_iterations: int = Field(default=3, ge=1, le=5)
    evaluation_timeout: int = Field(default=300, description="Seconds")
    auto_apply: bool = Field(default=False)
    backup_before_apply: bool = Field(default=True)
