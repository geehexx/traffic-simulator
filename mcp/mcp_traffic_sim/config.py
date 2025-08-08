"""Configuration management for MCP server."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

import yaml


class MCPConfig:
    """Configuration for MCP server operations."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration from file and environment variables."""
        self.repo_path = Path(os.getenv("MCP_REPO_PATH", "/home/gxx/projects/traffic-simulator"))
        self.log_dir = Path(os.getenv("MCP_LOG_DIR", str(self.repo_path / "runs" / "mcp")))
        self.confirm_required = os.getenv("MCP_CONFIRM_REQUIRED", "true").lower() == "true"
        self.max_timeout = int(os.getenv("MCP_MAX_TIMEOUT_S", "300"))

        # Load from config file if exists
        if config_path and config_path.exists():
            self._load_config_file(config_path)
        else:
            # Try default config location
            default_config = self.repo_path / "config" / "mcp.yaml"
            if default_config.exists():
                self._load_config_file(default_config)

    def _load_config_file(self, config_path: Path) -> None:
        """Load configuration from YAML file."""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f) or {}

            # Git configuration
            git_config = config_data.get("git", {})
            self.conventional_commits = git_config.get("conventional_commits", True)
            self.branch_naming_pattern = git_config.get(
                "branch_naming", r"^feat/|^fix/|^docs/|^style/|^refactor/|^test/|^chore/"
            )
            self.auto_conflict_resolution = git_config.get("auto_conflict_resolution", True)

            # Task configuration
            task_config = config_data.get("tasks", {})
            self.bazel_timeout = task_config.get("bazel_timeout", 300)
            self.uv_timeout = task_config.get("uv_timeout", 180)
            self.parallel_analysis = task_config.get("parallel_analysis", True)

            # Security configuration
            security_config = config_data.get("security", {})
            self.require_confirmation = security_config.get("require_confirmation", True)
            self.max_output_size = security_config.get("max_output_size", 1048576)  # 1MB
            self.redact_tokens = security_config.get("redact_tokens", True)

        except Exception as e:
            # Use defaults if config loading fails
            print(f"Warning: Failed to load config from {config_path}: {e}")

    def get_git_allowlist_paths(self) -> List[str]:
        """Get allowed paths for Git operations."""
        return ["src/", "config/", "docs/", "scripts/", "tests/"]

    def get_task_allowlist_commands(self) -> List[str]:
        """Get allowed commands for task execution."""
        return [
            "bazel build",
            "bazel test",
            "bazel run",
            "uv run pytest",
            "uv run pre-commit",
            "task quality",
            "task performance",
            "task profile",
        ]
