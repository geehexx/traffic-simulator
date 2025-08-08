"""uv command execution for MCP server."""

from __future__ import annotations

import subprocess
import time
from typing import List, Optional

from ..config import MCPConfig
from ..security import SecurityManager
from .schemas import TaskResult


class UvRunner:
    """Execute uv commands with safety and output capture."""

    def __init__(self, config: MCPConfig, security: SecurityManager):
        """Initialize uv runner with configuration."""
        self.config = config
        self.security = security
        self.repo_path = config.repo_path

    def execute_command(
        self, command: str, args: Optional[List[str]] = None, timeout: Optional[int] = None
    ) -> TaskResult:
        """Execute a uv command with safety checks."""
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
            full_args = ["uv", "run"] + command.split() + (args or [])

            # Set timeout
            timeout_seconds = timeout or self.config.uv_timeout

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

    def run_pytest(
        self, paths: Optional[List[str]] = None, maxfail: int = 0, verbose: bool = False
    ) -> TaskResult:
        """Run pytest with uv."""
        args = []
        if maxfail > 0:
            args.extend(["--maxfail", str(maxfail)])
        if verbose:
            args.append("-v")
        if paths:
            args.extend(paths)
        else:
            args.append("tests/")

        return self.execute_command("pytest", args)

    def run_precommit(self) -> TaskResult:
        """Run pre-commit with uv."""
        return self.execute_command("pre-commit", ["run", "--all-files"])

    def run_quality_analysis(self, mode: str = "check") -> TaskResult:
        """Run quality analysis with uv."""
        return self.execute_command("python", ["scripts/quality_analysis.py", "--mode", mode])
