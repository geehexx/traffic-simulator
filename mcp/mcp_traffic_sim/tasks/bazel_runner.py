"""Bazel command execution for MCP server."""

from __future__ import annotations

import subprocess
import time
from typing import List, Optional

from ..config import MCPConfig
from ..security import SecurityManager
from .schemas import TaskResult


class BazelRunner:
    """Execute Bazel commands with safety and output capture."""

    def __init__(self, config: MCPConfig, security: SecurityManager):
        """Initialize Bazel runner with configuration."""
        self.config = config
        self.security = security
        self.repo_path = config.repo_path

    def execute_command(
        self, command: str, args: Optional[List[str]] = None, timeout: Optional[int] = None
    ) -> TaskResult:
        """Execute a Bazel command with safety checks."""
        start_time = time.time()

        try:
            # Validate command
            is_valid, error = self.security.validate_task_command(command)
            if not is_valid:
                return TaskResult(
                    success=False,
                    command=command,
                    exit_code=1,
                    stdout="",
                    stderr=error or "Command not allowed",
                    duration_seconds=0,
                    error=error,
                )

            # Build full command
            full_args = [command] + (args or [])

            # Set timeout
            timeout_seconds = timeout or self.config.bazel_timeout

            # Execute command
            result = subprocess.run(
                full_args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )

            duration = time.time() - start_time

            # Redact tokens and truncate output
            stdout = self.security.redact_tokens(result.stdout)
            stdout = self.security.truncate_output(stdout)

            stderr = self.security.redact_tokens(result.stderr)
            stderr = self.security.truncate_output(stderr)

            return TaskResult(
                success=result.returncode == 0,
                command=command,
                exit_code=result.returncode,
                stdout=stdout,
                stderr=stderr,
                duration_seconds=duration,
            )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return TaskResult(
                success=False,
                command=command,
                exit_code=124,  # Timeout exit code
                stdout="",
                stderr=f"Command timed out after {timeout_seconds} seconds",
                duration_seconds=duration,
                error="Timeout",
            )
        except Exception as e:
            duration = time.time() - start_time
            return TaskResult(
                success=False,
                command=command,
                exit_code=1,
                stdout="",
                stderr=str(e),
                duration_seconds=duration,
                error=str(e),
            )

    def build(self, targets: Optional[List[str]] = None) -> TaskResult:
        """Run bazel build with optional targets."""
        args = targets if targets else ["//..."]
        return self.execute_command("bazel", ["build"] + args)

    def test(self, targets: Optional[List[str]] = None) -> TaskResult:
        """Run bazel test with optional targets."""
        args = targets if targets else ["//..."]
        return self.execute_command("bazel", ["test"] + args)

    def run(self, target: str, args: Optional[List[str]] = None) -> TaskResult:
        """Run bazel run with target and optional arguments."""
        bazel_args = ["run", target]
        if args:
            bazel_args.extend(["--"] + args)
        return self.execute_command("bazel", bazel_args)

    def clean(self) -> TaskResult:
        """Run bazel clean."""
        return self.execute_command("bazel", ["clean"])

    def query(self, query: str) -> TaskResult:
        """Run bazel query."""
        return self.execute_command("bazel", ["query", query])
