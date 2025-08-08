"""Security and allowlist management for MCP server."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from .config import MCPConfig


class SecurityManager:
    """Manages security policies and allowlists for MCP operations."""

    def __init__(self, config: MCPConfig):
        """Initialize security manager with configuration."""
        self.config = config
        self._git_allowlist_paths = config.get_git_allowlist_paths()
        self._task_allowlist_commands = config.get_task_allowlist_commands()

    def validate_git_path(self, path: str, repo_path: Path) -> bool:
        """Validate that a Git path is within allowed directories."""
        try:
            full_path = (repo_path / path).resolve()
            repo_path_resolved = repo_path.resolve()

            # Ensure path is within repo
            if not str(full_path).startswith(str(repo_path_resolved)):
                return False

            # Check against allowlist patterns
            relative_path = full_path.relative_to(repo_path_resolved)
            path_str = str(relative_path)

            return any(path_str.startswith(allowed) for allowed in self._git_allowlist_paths)

        except (ValueError, OSError):
            return False

    def validate_commit_message(self, message: str) -> tuple[bool, Optional[str]]:
        """Validate conventional commit message format."""
        if not self.config.conventional_commits:
            return True, None

        # Conventional commit pattern
        pattern = r"^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.+\))?: .+"

        if not re.match(pattern, message.strip()):
            return (
                False,
                "Commit message must follow conventional commit format: type(scope): description",
            )

        return True, None

    def validate_branch_name(self, branch_name: str) -> tuple[bool, Optional[str]]:
        """Validate branch name against naming convention."""
        if not re.match(self.config.branch_naming_pattern, branch_name):
            return False, f"Branch name must match pattern: {self.config.branch_naming_pattern}"

        return True, None

    def validate_task_command(self, command: str) -> tuple[bool, Optional[str]]:
        """Validate task command against allowlist."""
        # Check if any allowlisted command is a prefix of the given command

        # Check if any allowlisted command is a prefix of the given command
        for allowed in self._task_allowlist_commands:
            if command.startswith(allowed):
                return True, None

        return (
            False,
            f"Command not in allowlist. Allowed: {', '.join(self._task_allowlist_commands)}",
        )

    def redact_tokens(self, text: str) -> str:
        """Redact sensitive tokens from text."""
        if not self.config.redact_tokens:
            return text

        # Common token patterns
        patterns = [
            r"Bearer\s+[A-Za-z0-9\-._~+/]+=*",
            r"[A-Za-z0-9\-._~+/]+=*",  # Generic token pattern
            r"ghp_[A-Za-z0-9]{36}",  # GitHub personal access token
            r"gho_[A-Za-z0-9]{36}",  # GitHub OAuth token
            r"ghu_[A-Za-z0-9]{36}",  # GitHub user token
            r"ghs_[A-Za-z0-9]{36}",  # GitHub server token
            r"ghr_[A-Za-z0-9]{36}",  # GitHub refresh token
        ]

        redacted_text = text
        for pattern in patterns:
            redacted_text = re.sub(pattern, "[REDACTED]", redacted_text)

        return redacted_text

    def truncate_output(self, text: str) -> str:
        """Truncate output if it exceeds maximum size."""
        if len(text) <= self.config.max_output_size:
            return text

        truncated = text[: self.config.max_output_size]
        return f"{truncated}\n... [TRUNCATED - {len(text)} total chars]"
