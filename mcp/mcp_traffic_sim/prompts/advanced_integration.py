"""Advanced MCP integration for continuous improvement and optimization."""

from __future__ import annotations

from typing import Any, Dict, List

from mcp.types import Tool

from .advanced_tools import AdvancedPromptTools
from .schemas import PromptMode


class AdvancedPromptIntegration:
    """Advanced integration layer for continuous improvement in MCP server."""

    def __init__(self, advanced_tools: AdvancedPromptTools):
        """Initialize advanced prompt integration."""
        self.advanced_tools = advanced_tools

    def get_tools(self) -> List[Tool]:
        """Get advanced MCP tools for continuous improvement."""
        return [
            Tool(
                name="run_continuous_optimization",
                description="Run continuous optimization with advanced strategies (MIPROv2, Bayesian, Hybrid)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "mode": {
                            "type": "string",
                            "enum": [mode.value for mode in PromptMode],
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
                            "enum": [mode.value for mode in PromptMode],
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
                name="create_dataset_split",
                description="Create training, validation, and test dataset splits",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "train_ratio": {
                            "type": "number",
                            "description": "Ratio for training data (default: 0.8)",
                        },
                        "validation_ratio": {
                            "type": "number",
                            "description": "Ratio for validation data (default: 0.1)",
                        },
                        "test_ratio": {
                            "type": "number",
                            "description": "Ratio for test data (default: 0.1)",
                        },
                        "random_seed": {
                            "type": "integer",
                            "description": "Random seed for reproducible splits",
                        },
                    },
                },
            ),
            Tool(
                name="get_dataset_stats",
                description="Get dataset statistics and distribution",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="run_automated_optimization_cycle",
                description="Run automated optimization cycle for all modes",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="get_optimization_recommendations",
                description="Get optimization recommendations based on current state",
                inputSchema={
                    "type": "object",
                    "properties": {},
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
                            "enum": [mode.value for mode in PromptMode],
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

    def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle advanced tool calls for continuous improvement."""
        try:
            if name == "run_continuous_optimization":
                return self.advanced_tools.run_continuous_optimization(
                    mode=arguments["mode"],
                    optimization_strategy=arguments.get("optimization_strategy", "hybrid"),
                    auto_apply=arguments.get("auto_apply", False),
                )
            elif name == "generate_training_data":
                return self.advanced_tools.generate_training_data(
                    mode=arguments["mode"],
                    num_examples=arguments.get("num_examples", 100),
                    variety_level=arguments.get("variety_level", "medium"),
                )
            elif name == "create_dataset_split":
                return self.advanced_tools.create_dataset_split(
                    train_ratio=arguments.get("train_ratio", 0.8),
                    validation_ratio=arguments.get("validation_ratio", 0.1),
                    test_ratio=arguments.get("test_ratio", 0.1),
                    random_seed=arguments.get("random_seed", 42),
                )
            elif name == "get_dataset_stats":
                return self.advanced_tools.get_dataset_stats()
            elif name == "run_automated_optimization_cycle":
                return self.advanced_tools.run_automated_optimization_cycle()
            elif name == "get_optimization_recommendations":
                return self.advanced_tools.get_optimization_recommendations()
            elif name == "evaluate_prompt_performance":
                return self.advanced_tools.evaluate_prompt_performance(
                    mode=arguments["mode"],
                    num_test_cases=arguments.get("num_test_cases", 50),
                )
            else:
                raise ValueError(f"Unknown advanced tool: {name}")

        except Exception as e:
            return {"success": False, "error": str(e), "tool": name}
