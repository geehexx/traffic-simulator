"""MCP server entrypoint for traffic simulator."""

from __future__ import annotations

import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

from .config import MCPConfig
from .git.tools import GitTools
from .logging_util import MCPLogger
from .prompts.tools import PromptTools
from .prompts.advanced_tools import AdvancedPromptTools
from .security import SecurityManager
from .tasks.tools import TaskTools


class TrafficSimMCPServer:
    """Main MCP server for traffic simulator operations."""

    def __init__(self):
        """Initialize MCP server with configuration and tools."""
        self.config = MCPConfig()
        self.logger = MCPLogger(self.config.log_dir)
        self.security = SecurityManager(self.config)

        # Initialize tool handlers
        self.git_tools = GitTools(self.config, self.logger, self.security)
        self.task_tools = TaskTools(self.config, self.logger, self.security)
        self.prompt_tools = PromptTools(self.config, self.logger, self.security)
        self.advanced_prompt_tools = AdvancedPromptTools(self.config, self.logger, self.security)

        # Create MCP server
        self.server = Server("traffic-sim")
        self._register_tools()

    def _register_tools(self) -> None:
        """Register all MCP tools with the server."""

        # Git tools
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="git_status",
                    description="Get current Git repository status including branch, staged/unstaged files",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "repo_path": {
                                "type": "string",
                                "description": "Repository path (optional, defaults to configured repo)",
                            }
                        },
                    },
                ),
                Tool(
                    name="git_sync",
                    description="Sync repository with remote (pull and push) with conflict resolution",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pull_first": {
                                "type": "boolean",
                                "description": "Pull changes first (default: true)",
                            },
                            "push_after": {
                                "type": "boolean",
                                "description": "Push changes after pull (default: true)",
                            },
                            "rebase": {
                                "type": "boolean",
                                "description": "Use rebase instead of merge (default: false)",
                            },
                            "confirm": {
                                "type": "boolean",
                                "description": "Confirm operation (required if MCP_CONFIRM_REQUIRED=true)",
                            },
                        },
                    },
                ),
                Tool(
                    name="git_commit_workflow",
                    description="Complete commit workflow with staging, diff preview, and validation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Commit message (conventional commit format)",
                            },
                            "paths": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific paths to stage (optional, stages all if not provided)",
                            },
                            "signoff": {
                                "type": "boolean",
                                "description": "Add signoff to commit (default: false)",
                            },
                            "preview": {
                                "type": "boolean",
                                "description": "Show diff preview before commit (default: true)",
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
                                "description": "Specific paths to diff (optional)",
                            },
                            "staged": {
                                "type": "boolean",
                                "description": "Show staged changes (default: false)",
                            },
                            "against": {
                                "type": "string",
                                "description": "Compare against specific commit/branch (optional)",
                            },
                        },
                    },
                ),
                # Task tools
                Tool(
                    name="run_quality",
                    description="Run quality analysis with Bazel primary, uv fallback for debugging",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "mode": {
                                "type": "string",
                                "enum": ["check", "monitor", "analyze"],
                                "description": "Quality analysis mode (default: check)",
                            },
                            "fallback_to_uv": {
                                "type": "boolean",
                                "description": "Fall back to uv if Bazel fails (default: false)",
                            },
                        },
                    },
                ),
                Tool(
                    name="run_tests",
                    description="Run tests with Bazel primary, uv fallback for specific test debugging",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "targets": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific test targets (optional)",
                            },
                            "maxfail": {
                                "type": "integer",
                                "description": "Maximum number of failures before stopping (default: 0)",
                            },
                            "verbose": {
                                "type": "boolean",
                                "description": "Verbose output (default: false)",
                            },
                            "fallback_to_uv": {
                                "type": "boolean",
                                "description": "Fall back to uv if Bazel fails (default: false)",
                            },
                        },
                    },
                ),
                Tool(
                    name="run_performance",
                    description="Run performance analysis with benchmarking and scaling",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "mode": {
                                "type": "string",
                                "enum": ["benchmark", "scale", "monitor"],
                                "description": "Performance analysis mode (default: benchmark)",
                            },
                            "duration": {
                                "type": "integer",
                                "description": "Test duration in seconds (optional)",
                            },
                            "vehicle_counts": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Vehicle counts for scaling tests (optional)",
                            },
                        },
                    },
                ),
                Tool(
                    name="run_analysis",
                    description="Run comprehensive analysis combining quality, performance, and profiling",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_quality": {
                                "type": "boolean",
                                "description": "Include quality analysis (default: true)",
                            },
                            "include_performance": {
                                "type": "boolean",
                                "description": "Include performance analysis (default: true)",
                            },
                            "include_profiling": {
                                "type": "boolean",
                                "description": "Include profiling analysis (default: false)",
                            },
                            "parallel": {
                                "type": "boolean",
                                "description": "Run operations in parallel (default: true)",
                            },
                        },
                    },
                ),
                # Prompt Management Tools
                Tool(
                    name="execute_prompt",
                    description="Execute a registered prompt with given input data.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt_id": {
                                "type": "string",
                                "description": "ID of the prompt to execute.",
                            },
                            "input_data": {
                                "type": "object",
                                "description": "Input data for the prompt, adhering to its schema.",
                            },
                        },
                        "required": ["prompt_id", "input_data"],
                    },
                ),
                Tool(
                    name="register_prompt",
                    description="Register a new prompt configuration.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt_id": {"type": "string"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "template": {"type": "string"},
                            "input_schema": {"type": "object"},
                            "output_schema": {"type": "object"},
                            "version": {"type": "string"},
                            "tags": {"type": "array", "items": {"type": "string"}},
                            "metadata": {"type": "object"},
                        },
                        "required": [
                            "prompt_id",
                            "name",
                            "description",
                            "template",
                            "input_schema",
                            "output_schema",
                        ],
                    },
                ),
                Tool(
                    name="list_prompts",
                    description="List all registered prompts, optionally filtered by tags.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional list of tags to filter prompts.",
                            },
                        },
                    },
                ),
                Tool(
                    name="optimize_prompts",
                    description="Trigger the meta-optimization process for specified prompts.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of prompt IDs to optimize.",
                            },
                            "num_bootstrapped_examples": {
                                "type": "integer",
                                "description": "Number of few-shot examples to bootstrap (default: 5).",
                            },
                            "num_optimizer_trials": {
                                "type": "integer",
                                "description": "Number of optimization trials (default: 10).",
                            },
                        },
                        "required": ["prompt_ids"],
                    },
                ),
                Tool(
                    name="run_continuous_optimization",
                    description="Run continuous optimization with advanced strategies (MIPROv2, Bayesian, Hybrid)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "mode": {
                                "type": "string",
                                "enum": ["docs", "rules", "hybrid"],
                                "description": "Prompt mode to optimize",
                            },
                            "optimization_strategy": {
                                "type": "string",
                                "enum": ["mipro", "bayesian", "hybrid"],
                                "description": "Optimization strategy to use",
                            },
                            "auto_apply": {
                                "type": "boolean",
                                "description": "Automatically apply optimization results",
                            },
                        },
                        "required": ["mode"],
                    },
                ),
                Tool(
                    name="generate_training_data",
                    description="Generate training data for prompt optimization",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "mode": {
                                "type": "string",
                                "enum": ["docs", "rules", "hybrid"],
                                "description": "Prompt mode for training data",
                            },
                            "num_examples": {
                                "type": "integer",
                                "description": "Number of examples to generate",
                            },
                            "variety_level": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "Level of variety in generated examples",
                            },
                        },
                        "required": ["mode"],
                    },
                ),
                Tool(
                    name="evaluate_prompt_performance",
                    description="Evaluate prompt performance on test cases",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "mode": {
                                "type": "string",
                                "enum": ["docs", "rules", "hybrid"],
                                "description": "Prompt mode to evaluate",
                            },
                            "num_test_cases": {
                                "type": "integer",
                                "description": "Number of test cases to use",
                            },
                        },
                        "required": ["mode"],
                    },
                ),
            ]

        # Register tool handlers
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> dict:
            """Handle tool calls."""
            try:
                if name == "git_status":
                    return self.git_tools.git_status(arguments.get("repo_path"))
                elif name == "git_sync":
                    return self.git_tools.git_sync(
                        pull_first=arguments.get("pull_first", True),
                        push_after=arguments.get("push_after", True),
                        rebase=arguments.get("rebase", False),
                        confirm=arguments.get("confirm", False),
                    )
                elif name == "git_commit_workflow":
                    return self.git_tools.git_commit_workflow(
                        message=arguments["message"],
                        paths=arguments.get("paths"),
                        signoff=arguments.get("signoff", False),
                        preview=arguments.get("preview", True),
                    )
                elif name == "git_diff":
                    return self.git_tools.git_diff(
                        paths=arguments.get("paths"),
                        staged=arguments.get("staged", False),
                        against=arguments.get("against"),
                    )
                elif name == "run_quality":
                    return self.task_tools.run_quality(
                        mode=arguments.get("mode", "check"),
                        fallback_to_uv=arguments.get("fallback_to_uv", False),
                    )
                elif name == "run_tests":
                    return self.task_tools.run_tests(
                        targets=arguments.get("targets"),
                        maxfail=arguments.get("maxfail", 0),
                        verbose=arguments.get("verbose", False),
                        fallback_to_uv=arguments.get("fallback_to_uv", False),
                    )
                elif name == "run_performance":
                    return self.task_tools.run_performance(
                        mode=arguments.get("mode", "benchmark"),
                        duration=arguments.get("duration"),
                        vehicle_counts=arguments.get("vehicle_counts"),
                    )
                elif name == "run_analysis":
                    return self.task_tools.run_analysis(
                        include_quality=arguments.get("include_quality", True),
                        include_performance=arguments.get("include_performance", True),
                        include_profiling=arguments.get("include_profiling", False),
                        parallel=arguments.get("parallel", True),
                    )
                # Prompt Management Tools
                elif name == "execute_prompt":
                    return self.prompt_tools.execute_prompt(
                        prompt_id=arguments["prompt_id"], input_data=arguments["input_data"]
                    )
                elif name == "register_prompt":
                    return self.prompt_tools.register_prompt(arguments)
                elif name == "list_prompts":
                    return self.prompt_tools.list_prompts(tags=arguments.get("tags"))
                elif name == "optimize_prompts":
                    return self.prompt_tools.optimize_prompts(
                        prompt_ids=arguments["prompt_ids"],
                        num_bootstrapped_examples=arguments.get("num_bootstrapped_examples", 5),
                        num_optimizer_trials=arguments.get("num_optimizer_trials", 10),
                    )
                elif name == "run_continuous_optimization":
                    return self.advanced_prompt_tools.run_continuous_optimization(
                        mode=arguments["mode"],
                        optimization_strategy=arguments.get("optimization_strategy", "hybrid"),
                        auto_apply=arguments.get("auto_apply", False),
                    )
                elif name == "generate_training_data":
                    return self.advanced_prompt_tools.generate_training_data(
                        mode=arguments["mode"],
                        num_examples=arguments.get("num_examples", 100),
                        variety_level=arguments.get("variety_level", "medium"),
                    )
                elif name == "evaluate_prompt_performance":
                    return self.advanced_prompt_tools.evaluate_prompt_performance(
                        mode=arguments["mode"],
                        num_test_cases=arguments.get("num_test_cases", 50),
                    )
                else:
                    raise ValueError(f"Unknown tool: {name}")

            except Exception as e:
                # Log error and re-raise
                self.logger.log_operation(
                    "error", "tool_call", {"tool": name, "arguments": arguments}, error=str(e)
                )
                raise

    async def run(self) -> None:
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream, self.server.create_initialization_options()
            )


async def main() -> None:
    """Main entrypoint for MCP server."""
    server = TrafficSimMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
