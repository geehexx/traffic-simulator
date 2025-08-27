"""MCP Server for Traffic Simulator Git and Task Operations."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import ServerCapabilities
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
)

# Import our tools
from .config import MCPConfig
from .logging_util import MCPLogger
from .security import SecurityManager
from .git.tools import GitTools
from .tasks.tools import TaskTools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("traffic-sim")

# Global instances
config = MCPConfig()
logger_util = MCPLogger(config.log_dir)
security = SecurityManager(config)
git_tools = GitTools(config, logger_util, security)
task_tools = TaskTools(config, logger_util, security)


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available MCP tools."""
    tools = [
        # Git Tools
        Tool(
            name="git_status",
            description="Get current repository status",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Repository path (optional, uses default if not provided)",
                    }
                },
            },
        ),
        Tool(
            name="git_sync",
            description="Sync with remote (pull/push with conflict resolution)",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Repository path (optional, uses default if not provided)",
                    },
                    "auto_resolve": {
                        "type": "boolean",
                        "default": True,
                        "description": "Automatically resolve conflicts",
                    },
                },
            },
        ),
        Tool(
            name="git_commit_workflow",
            description="Complete commit workflow with staging and validation",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Commit message"},
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific files to commit (optional, commits all if not provided)",
                    },
                    "repo_path": {
                        "type": "string",
                        "description": "Repository path (optional, uses default if not provided)",
                    },
                },
                "required": ["message"],
            },
        ),
        Tool(
            name="git_diff",
            description="Get diff for specified paths or all changes",
            inputSchema={
                "type": "object",
                "properties": {
                    "paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific paths to diff (optional, shows all changes if not provided)",
                    },
                    "repo_path": {
                        "type": "string",
                        "description": "Repository path (optional, uses default if not provided)",
                    },
                },
            },
        ),
        # Task Tools
        Tool(
            name="run_quality",
            description="Quality analysis with Bazel primary, uv fallback",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["check", "monitor", "analyze"],
                        "default": "check",
                        "description": "Quality analysis mode",
                    },
                    "fallback_to_uv": {
                        "type": "boolean",
                        "default": False,
                        "description": "Fall back to uv if Bazel fails",
                    },
                },
            },
        ),
        Tool(
            name="run_tests",
            description="Test execution with Bazel primary, uv fallback",
            inputSchema={
                "type": "object",
                "properties": {
                    "fallback_to_uv": {
                        "type": "boolean",
                        "default": False,
                        "description": "Fall back to uv if Bazel fails",
                    },
                    "test_pattern": {
                        "type": "string",
                        "description": "Specific test pattern to run (optional)",
                    },
                },
            },
        ),
        Tool(
            name="run_performance",
            description="Performance benchmarking and scaling analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["benchmark", "scale", "monitor"],
                        "default": "benchmark",
                        "description": "Performance analysis mode",
                    },
                    "vehicle_count": {
                        "type": "integer",
                        "default": 20,
                        "description": "Number of vehicles for scaling test",
                    },
                },
            },
        ),
        Tool(
            name="run_analysis",
            description="Comprehensive analysis combining multiple operations",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_quality": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include quality analysis",
                    },
                    "include_tests": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include test execution",
                    },
                    "include_performance": {
                        "type": "boolean",
                        "default": False,
                        "description": "Include performance analysis",
                    },
                },
            },
        ),
    ]

    return ListToolsResult(tools=tools)


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls."""

    try:
        if name == "git_status":
            result = git_tools.git_status(arguments.get("repo_path"))
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "git_sync":
            result = git_tools.git_sync(
                arguments.get("repo_path"), arguments.get("auto_resolve", True)
            )
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "git_commit_workflow":
            result = git_tools.git_commit_workflow(
                arguments["message"], arguments.get("files"), arguments.get("repo_path")
            )
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "git_diff":
            result = git_tools.git_diff(arguments.get("paths"), arguments.get("repo_path"))
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "run_quality":
            result = task_tools.run_quality(
                arguments.get("mode", "check"), arguments.get("fallback_to_uv", False)
            )
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "run_tests":
            result = task_tools.run_tests(
                arguments.get("fallback_to_uv", False), arguments.get("test_pattern")
            )
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "run_performance":
            result = task_tools.run_performance(
                arguments.get("mode", "benchmark"), arguments.get("vehicle_count", 20)
            )
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "run_analysis":
            result = task_tools.run_analysis(
                arguments.get("include_quality", True),
                arguments.get("include_tests", True),
                arguments.get("include_performance", False),
            )
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        else:
            return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])

    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])


async def main():
    """Main server function."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="traffic-sim",
                server_version="1.0.0",
                capabilities=ServerCapabilities(tools={}),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
