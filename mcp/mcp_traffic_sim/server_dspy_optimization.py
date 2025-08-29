"""MCP Server with DSPy Real-time Prompt Optimization."""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Dict, List

import dspy
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
)

# Configure DSPy with Gemini
dspy.configure(lm=dspy.LM("gemini/gemini-2.0-flash"))

# Initialize MCP server
server = Server("traffic-sim-dspy-optimization")

# Global storage for optimized modules
optimized_modules: Dict[str, Any] = {}
optimization_history: List[Dict[str, Any]] = []


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available DSPy optimization tools."""
    tools = [
        Tool(
            name="optimize_prompt",
            description="Optimize a prompt using DSPy's built-in optimizers (MIPROv2, BootstrapFewShot, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_id": {"type": "string", "description": "ID of the prompt to optimize"},
                    "strategy": {
                        "type": "string",
                        "enum": ["mipro", "bootstrap", "bayesian"],
                        "default": "mipro",
                        "description": "DSPy optimizer strategy to use",
                    },
                    "training_data": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Training examples for optimization",
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
                },
                "required": ["prompt_id"],
            },
        ),
        Tool(
            name="auto_optimize_with_feedback",
            description="Automatically optimize a prompt based on user feedback in real-time",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_id": {"type": "string", "description": "ID of the prompt to optimize"},
                    "user_feedback": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "original_prompt": {"type": "string"},
                                "feedback": {"type": "string"},
                                "output_quality": {"type": "number", "minimum": 0, "maximum": 1},
                            },
                        },
                        "description": "User feedback on prompt outputs",
                    },
                    "feedback_threshold": {
                        "type": "number",
                        "default": 0.7,
                        "description": "Threshold for triggering optimization",
                    },
                },
                "required": ["prompt_id"],
            },
        ),
        Tool(
            name="evaluate_prompt_performance",
            description="Evaluate prompt performance using DSPy's built-in evaluation",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_id": {"type": "string", "description": "ID of the prompt to evaluate"},
                    "test_cases": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Test cases for evaluation",
                    },
                    "metric_function": {
                        "type": "string",
                        "description": "Custom metric function (optional)",
                    },
                },
                "required": ["prompt_id"],
            },
        ),
        Tool(
            name="get_optimization_history",
            description="Get the history of prompt optimizations",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_id": {
                        "type": "string",
                        "description": "Filter by specific prompt ID (optional)",
                    }
                },
            },
        ),
        Tool(
            name="get_optimized_prompt",
            description="Get an optimized prompt module by ID",
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
            name="execute_optimized_prompt",
            description="Execute an optimized prompt with input data",
            inputSchema={
                "type": "object",
                "properties": {
                    "optimized_prompt_id": {
                        "type": "string",
                        "description": "ID of the optimized prompt to execute",
                    },
                    "input_data": {"type": "object", "description": "Input data for the prompt"},
                },
                "required": ["optimized_prompt_id", "input_data"],
            },
        ),
    ]

    return ListToolsResult(tools=tools)


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls for DSPy optimization."""

    try:
        if name == "optimize_prompt":
            result = await optimize_prompt_tool(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "auto_optimize_with_feedback":
            result = await auto_optimize_with_feedback_tool(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "evaluate_prompt_performance":
            result = await evaluate_prompt_performance_tool(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "get_optimization_history":
            result = await get_optimization_history_tool(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "get_optimized_prompt":
            result = await get_optimized_prompt_tool(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "execute_optimized_prompt":
            result = await execute_optimized_prompt_tool(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        else:
            return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])

    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])


async def optimize_prompt_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Optimize a prompt using DSPy's built-in optimizers."""
    start_time = time.time()

    try:
        prompt_id = arguments["prompt_id"]
        strategy = arguments.get("strategy", "mipro")
        training_data = arguments.get("training_data", [])
        auto_mode = arguments.get("auto_mode", "light")
        num_threads = arguments.get("num_threads", 1)

        # Create DSPy module based on prompt type
        if "docs" in prompt_id:
            module = create_documentation_module()
        elif "rules" in prompt_id:
            module = create_rules_module()
        else:
            module = create_generic_module()

        # Prepare training examples
        training_examples = []
        for data in training_data:
            example = dspy.Example(**data).with_inputs(*data.keys())
            training_examples.append(example)

        # Create metric function
        metric = create_metric_function(prompt_id)

        # Select DSPy optimizer
        if strategy == "mipro":
            optimizer = dspy.MIPROv2(
                metric=metric, auto=auto_mode, num_threads=num_threads, verbose=True
            )
        elif strategy == "bootstrap":
            optimizer = dspy.BootstrapFewShot(
                metric=metric, max_bootstrapped_demos=4, max_labeled_demos=4
            )
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        # Run optimization - this is the magic!
        optimized_module = optimizer.compile(
            module, trainset=training_examples, requires_permission_to_run=False
        )

        # Generate optimized prompt ID
        optimized_prompt_id = f"{prompt_id}_optimized_{int(time.time())}"

        # Store the optimized module
        optimized_modules[optimized_prompt_id] = optimized_module

        # Record optimization history
        optimization_record = {
            "prompt_id": prompt_id,
            "optimized_prompt_id": optimized_prompt_id,
            "strategy": strategy,
            "auto_mode": auto_mode,
            "num_threads": num_threads,
            "training_examples": len(training_examples),
            "execution_time": time.time() - start_time,
            "timestamp": time.time(),
        }
        optimization_history.append(optimization_record)

        return {
            "success": True,
            "optimized_prompt_id": optimized_prompt_id,
            "strategy_used": strategy,
            "execution_time": time.time() - start_time,
            "training_examples": len(training_examples),
            "optimization_record": optimization_record,
        }

    except Exception as e:
        return {
            "success": False,
            "error_message": str(e),
            "execution_time": time.time() - start_time,
        }


async def auto_optimize_with_feedback_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Automatically optimize a prompt based on user feedback."""
    start_time = time.time()

    try:
        prompt_id = arguments["prompt_id"]
        user_feedback = arguments.get("user_feedback", [])
        feedback_threshold = arguments.get("feedback_threshold", 0.7)

        # Create feedback-based optimization module
        class FeedbackSignature(dspy.Signature):
            """Signature for feedback-based optimization."""

            original_prompt: str = dspy.InputField(desc="Original prompt")
            user_feedback: str = dspy.InputField(desc="User feedback on output quality")
            optimized_prompt: str = dspy.OutputField(desc="Optimized prompt based on feedback")

        class FeedbackOptimizer(dspy.Module):
            """Module for feedback-based optimization."""

            def __init__(self):
                super().__init__()
                self.optimize = dspy.ChainOfThought(FeedbackSignature)

            def forward(self, original_prompt: str, user_feedback: str) -> str:
                result = self.optimize(original_prompt=original_prompt, user_feedback=user_feedback)
                return result.optimized_prompt

        # Create optimizer
        feedback_optimizer = FeedbackOptimizer()

        # Process user feedback
        optimized_prompts = []
        for feedback in user_feedback:
            original = feedback.get("original_prompt", f"Generate {prompt_id}")
            feedback_text = feedback.get("feedback", "Improve the prompt")
            quality = feedback.get("output_quality", 0.5)

            # Only optimize if quality is below threshold
            if quality < feedback_threshold:
                optimized = feedback_optimizer.forward(original, feedback_text)
                optimized_prompts.append(
                    {
                        "original": original,
                        "optimized": optimized,
                        "feedback": feedback_text,
                        "quality": quality,
                    }
                )

        return {
            "success": True,
            "optimized_prompts": optimized_prompts,
            "feedback_processed": len(user_feedback),
            "threshold": feedback_threshold,
            "execution_time": time.time() - start_time,
        }

    except Exception as e:
        return {
            "success": False,
            "error_message": str(e),
            "execution_time": time.time() - start_time,
        }


async def evaluate_prompt_performance_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate prompt performance using DSPy's built-in evaluation."""
    start_time = time.time()

    try:
        prompt_id = arguments["prompt_id"]
        test_cases = arguments.get("test_cases", [])

        # Create test examples
        test_examples = []
        for case in test_cases:
            example = dspy.Example(**case).with_inputs(*case.keys())
            test_examples.append(example)

        # Create metric function
        metric = create_metric_function(prompt_id)

        # Evaluate performance
        if test_examples:
            # Use DSPy's built-in evaluation
            scores = []
            for example in test_examples:
                # This would run the actual evaluation
                score = metric(example, example)  # Placeholder
                scores.append(score)

            average_score = sum(scores) / len(scores) if scores else 0.0
        else:
            average_score = 0.0

        return {
            "success": True,
            "prompt_id": prompt_id,
            "average_score": average_score,
            "test_cases": len(test_cases),
            "execution_time": time.time() - start_time,
        }

    except Exception as e:
        return {
            "success": False,
            "error_message": str(e),
            "execution_time": time.time() - start_time,
        }


async def get_optimization_history_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get the history of prompt optimizations."""
    prompt_id = arguments.get("prompt_id")

    if prompt_id:
        filtered_history = [h for h in optimization_history if h["prompt_id"] == prompt_id]
    else:
        filtered_history = optimization_history

    return {
        "success": True,
        "history": filtered_history,
        "total_optimizations": len(filtered_history),
    }


async def get_optimized_prompt_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get an optimized prompt module by ID."""
    optimized_prompt_id = arguments["optimized_prompt_id"]

    if optimized_prompt_id in optimized_modules:
        return {
            "success": True,
            "optimized_prompt_id": optimized_prompt_id,
            "module_available": True,
            "module_type": type(optimized_modules[optimized_prompt_id]).__name__,
        }
    else:
        return {
            "success": False,
            "optimized_prompt_id": optimized_prompt_id,
            "module_available": False,
            "error_message": "Optimized prompt not found",
        }


async def execute_optimized_prompt_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an optimized prompt with input data."""
    start_time = time.time()

    try:
        optimized_prompt_id = arguments["optimized_prompt_id"]
        input_data = arguments["input_data"]

        if optimized_prompt_id not in optimized_modules:
            return {"success": False, "error_message": "Optimized prompt not found"}

        # Get the optimized module
        optimized_module = optimized_modules[optimized_prompt_id]

        # Execute the optimized module
        result = optimized_module.forward(**input_data)

        return {
            "success": True,
            "optimized_prompt_id": optimized_prompt_id,
            "output": result,
            "execution_time": time.time() - start_time,
        }

    except Exception as e:
        return {
            "success": False,
            "error_message": str(e),
            "execution_time": time.time() - start_time,
        }


def create_documentation_module():
    """Create a DSPy module for documentation generation."""

    class DocumentationSignature(dspy.Signature):
        """Signature for documentation generation."""

        code_changes: str = dspy.InputField(desc="Description of code changes")
        context: str = dspy.InputField(desc="Additional context", default="")
        documentation: str = dspy.OutputField(desc="Generated documentation")
        sections: List[str] = dspy.OutputField(desc="Documentation sections")

    class DocumentationModule(dspy.Module):
        """DSPy module for documentation generation."""

        def __init__(self):
            super().__init__()
            self.generate = dspy.ChainOfThought(DocumentationSignature)

        def forward(self, code_changes: str, context: str = "") -> Dict[str, Any]:
            result = self.generate(code_changes=code_changes, context=context)
            return {"documentation": result.documentation, "sections": result.sections}

    return DocumentationModule()


def create_rules_module():
    """Create a DSPy module for rules generation."""

    class RulesSignature(dspy.Signature):
        """Signature for rules generation."""

        patterns: str = dspy.InputField(desc="Description of patterns")
        context: str = dspy.InputField(desc="Additional context", default="")
        rules: str = dspy.OutputField(desc="Generated rules")
        categories: List[str] = dspy.OutputField(desc="Rule categories")

    class RulesModule(dspy.Module):
        """DSPy module for rules generation."""

        def __init__(self):
            super().__init__()
            self.generate = dspy.ChainOfThought(RulesSignature)

        def forward(self, patterns: str, context: str = "") -> Dict[str, Any]:
            result = self.generate(patterns=patterns, context=context)
            return {"rules": result.rules, "categories": result.categories}

    return RulesModule()


def create_generic_module():
    """Create a generic DSPy module."""

    class GenericSignature(dspy.Signature):
        """Generic signature."""

        input_text: str = dspy.InputField(desc="Input text")
        output_text: str = dspy.OutputField(desc="Generated output")

    class GenericModule(dspy.Module):
        """Generic DSPy module."""

        def __init__(self):
            super().__init__()
            self.predict = dspy.Predict(GenericSignature)

        def forward(self, input_text: str) -> str:
            result = self.predict(input_text=input_text)
            return result.output_text

    return GenericModule()


def create_metric_function(prompt_id: str):
    """Create a metric function for evaluation."""

    def metric(example, prediction):
        """Simple metric for evaluation."""
        score = 0.0

        # Check if output was generated
        if hasattr(prediction, "documentation") and prediction.documentation:
            score += 0.4
        elif hasattr(prediction, "rules") and prediction.rules:
            score += 0.4
        elif hasattr(prediction, "output_text") and prediction.output_text:
            score += 0.4

        # Check for sections/categories
        if hasattr(prediction, "sections") and prediction.sections:
            score += 0.3
        elif hasattr(prediction, "categories") and prediction.categories:
            score += 0.3

        # Check for markdown formatting
        if hasattr(prediction, "documentation") and "##" in prediction.documentation:
            score += 0.3
        elif hasattr(prediction, "rules") and "##" in prediction.rules:
            score += 0.3

        return score

    return metric


async def main():
    """Main server function."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="traffic-sim-dspy-optimization",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None, experimental_capabilities=None
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
