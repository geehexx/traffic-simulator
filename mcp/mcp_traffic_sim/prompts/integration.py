"""Integration with main MCP server for prompt management."""

from __future__ import annotations

from typing import Any, Dict, List

from mcp.types import Tool

from .tools import PromptTools
from .schemas import PromptMode


class PromptIntegration:
    """Integration layer for prompt management in MCP server."""

    def __init__(self, prompt_tools: PromptTools):
        """Initialize prompt integration."""
        self.prompt_tools = prompt_tools

    def get_tools(self) -> List[Tool]:
        """Get MCP tools for prompt management."""
        return [
            Tool(
                name="execute_prompt",
                description="Execute a prompt with structured input and output using DSPy",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "mode": {
                            "type": "string",
                            "enum": [mode.value for mode in PromptMode],
                            "description": "Prompt execution mode (docs, rules, hybrid, etc.)",
                        },
                        "repo_metadata": {
                            "type": "object",
                            "description": "Repository metadata (name, type, etc.)",
                        },
                        "git_signals": {
                            "type": "object",
                            "description": "Git signals (branch, commit, etc.)",
                        },
                        "change_inventory": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of changed files",
                        },
                        "chat_decisions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Chat decisions and requirements",
                        },
                        "style_guide": {
                            "type": "object",
                            "description": "Style guide and standards",
                        },
                        "constraints": {
                            "type": "object",
                            "description": "Constraints and limitations",
                        },
                        "context": {"type": "object", "description": "Additional context"},
                    },
                    "required": ["mode"],
                },
            ),
            Tool(
                name="register_prompt",
                description="Register a new prompt in the registry",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Prompt content"},
                        "mode": {
                            "type": "string",
                            "enum": [mode.value for mode in PromptMode],
                            "description": "Prompt mode",
                        },
                        "parameters": {"type": "object", "description": "Prompt parameters"},
                        "metadata": {"type": "object", "description": "Prompt metadata"},
                    },
                    "required": ["content", "mode"],
                },
            ),
            Tool(
                name="get_active_prompt",
                description="Get the active prompt for a mode",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "mode": {
                            "type": "string",
                            "enum": [mode.value for mode in PromptMode],
                            "description": "Prompt mode",
                        }
                    },
                    "required": ["mode"],
                },
            ),
            Tool(
                name="optimize_prompts",
                description="Optimize prompts using meta-optimizer with DSPy",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "mode": {
                            "type": "string",
                            "enum": [mode.value for mode in PromptMode],
                            "description": "Prompt mode to optimize",
                        },
                        "auto_apply": {
                            "type": "boolean",
                            "description": "Automatically apply optimization results",
                        },
                        "test_inputs": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Test inputs for evaluation",
                        },
                    },
                    "required": ["mode"],
                },
            ),
            Tool(
                name="list_prompts",
                description="List prompts in the registry",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "mode": {
                            "type": "string",
                            "enum": [mode.value for mode in PromptMode],
                            "description": "Filter by mode (optional)",
                        }
                    },
                },
            ),
            Tool(
                name="get_optimization_stats",
                description="Get optimization statistics and history",
                inputSchema={"type": "object", "properties": {}},
            ),
        ]

    def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls for prompt management."""
        try:
            if name == "execute_prompt":
                return self.prompt_tools.execute_prompt(
                    mode=arguments["mode"],
                    repo_metadata=arguments.get("repo_metadata"),
                    git_signals=arguments.get("git_signals"),
                    change_inventory=arguments.get("change_inventory"),
                    chat_decisions=arguments.get("chat_decisions"),
                    style_guide=arguments.get("style_guide"),
                    constraints=arguments.get("constraints"),
                    context=arguments.get("context"),
                )
            elif name == "register_prompt":
                return self.prompt_tools.register_prompt(
                    content=arguments["content"],
                    mode=arguments["mode"],
                    parameters=arguments.get("parameters"),
                    metadata=arguments.get("metadata"),
                )
            elif name == "get_active_prompt":
                return self.prompt_tools.get_active_prompt(mode=arguments["mode"])
            elif name == "optimize_prompts":
                return self.prompt_tools.optimize_prompts(
                    mode=arguments["mode"],
                    auto_apply=arguments.get("auto_apply", False),
                    test_inputs=arguments.get("test_inputs"),
                )
            elif name == "list_prompts":
                return self.prompt_tools.list_prompts(mode=arguments.get("mode"))
            elif name == "get_optimization_stats":
                return self.prompt_tools.get_optimization_stats()
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            return {"success": False, "error": str(e), "tool": name}
