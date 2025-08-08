"""Git MCP tool handlers."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional


from ..config import MCPConfig
from ..logging_util import MCPLogger
from ..security import SecurityManager
from .adapter import GitAdapter


class GitTools:
    """Git MCP tool implementations."""

    def __init__(self, config: MCPConfig, logger: MCPLogger, security: SecurityManager):
        """Initialize Git tools with configuration and dependencies."""
        self.config = config
        self.logger = logger
        self.security = security
        self._git_adapter = None

    def _get_adapter(self) -> GitAdapter:
        """Get or create Git adapter."""
        if self._git_adapter is None:
            self._git_adapter = GitAdapter(self.config.repo_path)
        return self._git_adapter

    def git_status(self, repo_path: Optional[str] = None) -> Dict[str, Any]:
        """Get current Git repository status."""
        start_time = time.time()

        try:
            # Use provided path or default
            path = Path(repo_path) if repo_path else self.config.repo_path

            # Create adapter for this path
            adapter = GitAdapter(path)
            status = adapter.get_status()

            result = {
                "branch": status.branch,
                "ahead": status.ahead,
                "behind": status.behind,
                "staged_files": status.staged_files,
                "unstaged_files": status.unstaged_files,
                "untracked_files": status.untracked_files,
                "clean": status.clean,
                "summary": f"Branch: {status.branch}, "
                f"Staged: {len(status.staged_files)}, "
                f"Unstaged: {len(status.unstaged_files)}, "
                f"Untracked: {len(status.untracked_files)}",
            }

            duration = time.time() - start_time
            self.logger.log_git_operation(
                "status", {"repo_path": str(path)}, result, duration=duration
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to get git status: {e}"
            self.logger.log_git_operation(
                "status", {"repo_path": repo_path}, error=error_msg, duration=duration
            )
            raise RuntimeError(error_msg)

    def git_sync(
        self,
        pull_first: bool = True,
        push_after: bool = True,
        rebase: bool = False,
        confirm: bool = False,
    ) -> Dict[str, Any]:
        """Sync repository with remote (pull and push)."""
        start_time = time.time()

        try:
            # Check confirmation if required
            if self.config.confirm_required and not confirm:
                raise ValueError("Confirmation required for sync operation. Set confirm=True.")

            adapter = self._get_adapter()
            sync_result = adapter.sync_repository(pull_first, push_after, rebase)

            result = {
                "pull_success": sync_result.pull_success,
                "push_success": sync_result.push_success,
                "conflicts": sync_result.conflicts,
                "changes_pulled": sync_result.changes_pulled,
                "changes_pushed": sync_result.changes_pushed,
                "summary": f"Pull: {'✓' if sync_result.pull_success else '✗'}, "
                f"Push: {'✓' if sync_result.push_success else '✗'}, "
                f"Conflicts: {len(sync_result.conflicts)}",
            }

            if sync_result.error:
                result["error"] = sync_result.error

            duration = time.time() - start_time
            self.logger.log_git_operation(
                "sync",
                {"pull_first": pull_first, "push_after": push_after, "rebase": rebase},
                result,
                duration=duration,
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to sync repository: {e}"
            self.logger.log_git_operation(
                "sync",
                {"pull_first": pull_first, "push_after": push_after, "rebase": rebase},
                error=error_msg,
                duration=duration,
            )
            raise RuntimeError(error_msg)

    def git_commit_workflow(
        self,
        message: str,
        paths: Optional[List[str]] = None,
        signoff: bool = False,
        preview: bool = True,
    ) -> Dict[str, Any]:
        """Complete commit workflow with staging and validation."""
        start_time = time.time()

        try:
            # Validate commit message
            is_valid, validation_error = self.security.validate_commit_message(message)
            if not is_valid:
                raise ValueError(validation_error)

            # Validate paths if provided
            if paths:
                for path in paths:
                    if not self.security.validate_git_path(path, self.config.repo_path):
                        raise ValueError(f"Path not allowed: {path}")

            adapter = self._get_adapter()
            workflow_result = adapter.commit_workflow(message, paths, signoff, preview)

            result = {
                "success": workflow_result.success,
                "commit_hash": workflow_result.commit_hash,
                "files_staged": workflow_result.files_staged,
                "diff_preview": workflow_result.diff_preview,
                "validation_errors": workflow_result.validation_errors,
                "summary": f"Commit: {'✓' if workflow_result.success else '✗'}, "
                f"Files staged: {len(workflow_result.files_staged)}",
            }

            if workflow_result.error:
                result["error"] = workflow_result.error

            duration = time.time() - start_time
            self.logger.log_git_operation(
                "commit_workflow",
                {"message": message, "paths": paths, "signoff": signoff, "preview": preview},
                result,
                duration=duration,
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to execute commit workflow: {e}"
            self.logger.log_git_operation(
                "commit_workflow",
                {"message": message, "paths": paths, "signoff": signoff, "preview": preview},
                error=error_msg,
                duration=duration,
            )
            raise RuntimeError(error_msg)

    def git_diff(
        self, paths: Optional[List[str]] = None, staged: bool = False, against: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get diff for specified paths or all changes."""
        start_time = time.time()

        try:
            # Validate paths if provided
            if paths:
                for path in paths:
                    if not self.security.validate_git_path(path, self.config.repo_path):
                        raise ValueError(f"Path not allowed: {path}")

            adapter = self._get_adapter()
            diff_result = adapter.get_diff(paths, staged)

            # Redact tokens and truncate if needed
            diff_text = self.security.redact_tokens(diff_result.diff_text)
            diff_text = self.security.truncate_output(diff_text)

            result = {
                "diff_text": diff_text,
                "file_changes": diff_result.file_changes,
                "stats": diff_result.stats,
                "summary": f"Files changed: {len(diff_result.file_changes)}, "
                f"Lines: {len(diff_text.splitlines())}",
            }

            duration = time.time() - start_time
            self.logger.log_git_operation(
                "diff",
                {"paths": paths, "staged": staged, "against": against},
                result,
                duration=duration,
            )

            return result

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Failed to get git diff: {e}"
            self.logger.log_git_operation(
                "diff",
                {"paths": paths, "staged": staged, "against": against},
                error=error_msg,
                duration=duration,
            )
            raise RuntimeError(error_msg)
