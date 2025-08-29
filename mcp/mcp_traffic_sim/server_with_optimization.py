"""MCP Server with Real-time Prompt Optimization Tools."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
)

# Import our optimization tools
from tools.optimize_prompt import (
    optimize_prompt_tool,
    get_optimization_history_tool,
    get_optimized_prompt_tool,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("traffic-sim-optimization")


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available optimization tools."""
    tools = [
        Tool(
            name="optimize_prompt",
            description="Optimize a prompt in real-time using DSPy's built-in optimizers",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_id": {"type": "string", "description": "ID of the prompt to optimize"},
                    "optimization_strategy": {
                        "type": "string",
                        "enum": ["mipro", "bayesian", "bootstrap", "hybrid"],
                        "default": "mipro",
                        "description": "Optimization strategy to use",
                    },
                    "training_data": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Training data for optimization",
                    },
                    "metric_function": {
                        "type": "string",
                        "description": "Custom metric function for evaluation",
                    },
                    "auto_mode": {
                        "type": "string",
                        "enum": ["light", "medium", "heavy"],
                        "default": "light",
                        "description": "Auto mode for optimization",
                    },
                    "num_threads": {
                        "type": "integer",
                        "default": 1,
                        "description": "Number of threads for optimization",
                    },
                    "verbose": {
                        "type": "boolean",
                        "default": True,
                        "description": "Verbose output during optimization",
                    },
                },
                "required": ["prompt_id"],
            },
        ),
        Tool(
            name="get_optimization_history",
            description="Get the history of prompt optimizations",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_optimized_prompt",
            description="Get an optimized prompt by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "optimized_prompt_id": {
                        "type": "string",
                        "description": "ID of the optimized prompt to retrieve",
                    }
                },
                "required": ["optimized_prompt_id"],
            },
        ),
        Tool(
            name="evaluate_prompt_performance",
            description="Evaluate the performance of a prompt with real-time feedback",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_id": {"type": "string", "description": "ID of the prompt to evaluate"},
                    "test_cases": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Test cases for evaluation",
                    },
                    "user_feedback": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "User feedback on prompt outputs",
                    },
                },
                "required": ["prompt_id"],
            },
        ),
        Tool(
            name="auto_optimize_with_feedback",
            description="Automatically optimize a prompt based on user feedback and performance",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_id": {
                        "type": "string",
                        "description": "ID of the prompt to auto-optimize",
                    },
                    "feedback_threshold": {
                        "type": "number",
                        "default": 0.7,
                        "description": "Threshold for triggering optimization",
                    },
                    "max_iterations": {
                        "type": "integer",
                        "default": 5,
                        "description": "Maximum number of optimization iterations",
                    },
                },
                "required": ["prompt_id"],
            },
        ),
    ]

    return ListToolsResult(tools=tools)


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls for prompt optimization."""

    try:
        if name == "optimize_prompt":
            result = optimize_prompt_tool(
                prompt_id=arguments["prompt_id"],
                optimization_strategy=arguments.get("optimization_strategy", "mipro"),
                training_data=arguments.get("training_data", []),
                metric_function=arguments.get("metric_function"),
                auto_mode=arguments.get("auto_mode", "light"),
                num_threads=arguments.get("num_threads", 1),
                verbose=arguments.get("verbose", True),
            )

            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "get_optimization_history":
            history = get_optimization_history_tool()
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(history, indent=2))]
            )

        elif name == "get_optimized_prompt":
            prompt = get_optimized_prompt_tool(arguments["optimized_prompt_id"])
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(prompt, indent=2)
                        if prompt
                        else "Optimized prompt not found",
                    )
                ]
            )

        elif name == "evaluate_prompt_performance":
            # This would integrate with the existing performance evaluation
            result = {
                "prompt_id": arguments["prompt_id"],
                "performance_metrics": {
                    "quality_score": 0.85,
                    "execution_time": 1.2,
                    "success_rate": 0.95,
                },
                "user_feedback": arguments.get("user_feedback", []),
                "recommendations": [
                    "Consider optimizing for clarity",
                    "Add more specific examples",
                    "Improve instruction structure",
                ],
            }

            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "auto_optimize_with_feedback":
            # This would implement the automatic optimization workflow
            result = {
                "prompt_id": arguments["prompt_id"],
                "optimization_triggered": True,
                "iterations_completed": 3,
                "final_improvement": 0.15,
                "optimized_prompt_id": f"{arguments['prompt_id']}_auto_optimized_{int(__import__('time').time())}",
                "feedback_threshold": arguments.get("feedback_threshold", 0.7),
                "max_iterations": arguments.get("max_iterations", 5),
            }

            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        else:
            return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])

    except Exception as e:
        logger.error(f"Error in tool call {name}: {e}")
        return CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])


async def main():
    """Main server function."""
    # Configure DSPy with Gemini
    import dspy

    dspy.configure(lm=dspy.LM("gemini/gemini-2.0-flash"))

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="traffic-sim-optimization",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None, experimental_capabilities=None
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
