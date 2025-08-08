"""Pydantic schemas for Git operations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class GitStatus(BaseModel):
    """Git repository status information."""

    branch: str
    ahead: int = 0
    behind: int = 0
    staged_files: List[str] = Field(default_factory=list)
    unstaged_files: List[str] = Field(default_factory=list)
    untracked_files: List[str] = Field(default_factory=list)
    clean: bool = True


class GitDiff(BaseModel):
    """Git diff information."""

    diff_text: str
    file_changes: Dict[str, int] = Field(default_factory=dict)  # filename -> lines changed
    stats: Dict[str, Any] = Field(default_factory=dict)


class GitCommit(BaseModel):
    """Git commit information."""

    commit_hash: str
    message: str
    author: str
    timestamp: str
    files_changed: List[str] = Field(default_factory=list)


class GitSync(BaseModel):
    """Git sync operation result."""

    pull_success: bool
    push_success: bool
    conflicts: List[str] = Field(default_factory=list)
    changes_pulled: int = 0
    changes_pushed: int = 0
    error: Optional[str] = None


class GitCommitWorkflow(BaseModel):
    """Git commit workflow result."""

    success: bool
    commit_hash: Optional[str] = None
    files_staged: List[str] = Field(default_factory=list)
    diff_preview: Optional[str] = None
    validation_errors: List[str] = Field(default_factory=list)
    error: Optional[str] = None
