"""Structured logging utilities for MCP server."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class MCPLogger:
    """Structured logger for MCP operations."""

    def __init__(self, log_dir: Path):
        """Initialize logger with output directory."""
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log_operation(
        self,
        tool_name: str,
        operation: str,
        params: Dict[str, Any],
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        duration: Optional[float] = None,
    ) -> None:
        """Log a complete MCP operation."""
        timestamp = datetime.utcnow().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "tool_name": tool_name,
            "operation": operation,
            "params": params,
            "result": result,
            "error": error,
            "duration_seconds": duration,
        }

        # Write to daily log file
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"{tool_name}_{date_str}.jsonl"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

    def log_git_operation(
        self,
        operation: str,
        params: Dict[str, Any],
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        duration: Optional[float] = None,
    ) -> None:
        """Log Git-specific operation."""
        self.log_operation("git", operation, params, result, error, duration)

    def log_task_operation(
        self,
        operation: str,
        params: Dict[str, Any],
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        duration: Optional[float] = None,
    ) -> None:
        """Log task-specific operation."""
        self.log_operation("task", operation, params, result, error, duration)

    def get_recent_operations(self, tool_name: str, limit: int = 10) -> list[Dict[str, Any]]:
        """Get recent operations for a tool."""
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"{tool_name}_{date_str}.jsonl"

        if not log_file.exists():
            return []

        operations = []
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                try:
                    operations.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue

        return operations
