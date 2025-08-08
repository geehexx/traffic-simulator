"""Pydantic schemas for task operations."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class TaskResult(BaseModel):
    """Base task execution result."""

    success: bool
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    artifacts: List[str] = Field(default_factory=list)
    error: Optional[str] = None


class QualityResult(BaseModel):
    """Quality analysis result."""

    success: bool
    mode: str  # "check", "monitor", "analyze"
    bazel_success: bool
    uv_fallback_used: bool
    quality_gates_passed: bool
    issues_found: int = 0
    artifacts: List[str] = Field(default_factory=list)
    error: Optional[str] = None


class TestResult(BaseModel):
    """Test execution result."""

    success: bool
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0
    bazel_success: bool
    uv_fallback_used: bool
    artifacts: List[str] = Field(default_factory=list)
    error: Optional[str] = None


class PerformanceResult(BaseModel):
    """Performance analysis result."""

    success: bool
    mode: str  # "benchmark", "scale", "monitor"
    duration: Optional[int] = None
    vehicle_counts: Optional[List[int]] = None
    fps_measurements: List[float] = Field(default_factory=list)
    memory_usage: List[float] = Field(default_factory=list)
    artifacts: List[str] = Field(default_factory=list)
    error: Optional[str] = None


class AnalysisResult(BaseModel):
    """Comprehensive analysis result."""

    success: bool
    quality_result: Optional[QualityResult] = None
    test_result: Optional[TestResult] = None
    performance_result: Optional[PerformanceResult] = None
    parallel_execution: bool = False
    total_duration: float = 0.0
    artifacts: List[str] = Field(default_factory=list)
    error: Optional[str] = None
