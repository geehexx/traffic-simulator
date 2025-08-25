"""Production-Ready DSPy Optimization MCP Server for Traffic Simulator."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict

import dspy
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
    ServerCapabilities,
)

# Import our production components
from .config import MCPConfig
from .logging_util import MCPLogger
from .security import SecurityManager
from .production_optimizer import ProductionOptimizer
from .monitoring_system import MonitoringSystem
from .feedback_collector import FeedbackCollector
from .dashboard_generator import DashboardGenerator
from .alerting_system import AlertingSystem

# Configure DSPy with Gemini for production
dspy.configure(lm=dspy.LM("gemini/gemini-2.0-flash"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("traffic-sim-production-optimization")

# Global instances
config = MCPConfig()
logger_util = MCPLogger(config.log_dir)
security = SecurityManager(config)
optimizer = ProductionOptimizer(config, logger_util, security)
monitoring = MonitoringSystem(config, logger_util, security)
feedback_collector = FeedbackCollector(config, logger_util, security)
dashboard_generator = DashboardGenerator(config, logger_util, security)
alerting = AlertingSystem(config, logger_util, security)


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available production DSPy optimization tools."""
    tools = [
        # Core Optimization Tools
        Tool(
            name="optimize_prompt",
            description="Production-grade prompt optimization using DSPy with comprehensive monitoring",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_id": {"type": "string", "description": "ID of the prompt to optimize"},
                    "strategy": {
                        "type": "string",
                        "enum": ["mipro", "bootstrap", "bayesian", "hybrid"],
                        "default": "mipro",
                        "description": "DSPy optimizer strategy",
                    },
                    "training_data": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Training examples for optimization",
                    },
                    "auto_mode": {
                        "type": "string",
                        "enum": ["light", "medium", "heavy"],
                        "default": "medium",
                        "description": "Optimization intensity",
                    },
                    "monitoring_enabled": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable real-time monitoring",
                    },
                },
                "required": ["prompt_id"],
            },
        ),
        # Real-time Feedback Optimization
        Tool(
            name="auto_optimize_feedback",
            description="Production-grade real-time optimization based on user feedback with monitoring",
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
                                "user_id": {"type": "string"},
                                "timestamp": {"type": "number"},
                            },
                        },
                        "description": "User feedback data",
                    },
                    "feedback_threshold": {
                        "type": "number",
                        "default": 0.7,
                        "description": "Quality threshold for triggering optimization",
                    },
                    "auto_deploy": {
                        "type": "boolean",
                        "default": True,
                        "description": "Automatically deploy optimized prompts",
                    },
                },
                "required": ["prompt_id"],
            },
        ),
        # Performance Evaluation
        Tool(
            name="evaluate_performance",
            description="Comprehensive performance evaluation with detailed metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_id": {"type": "string", "description": "ID of the prompt to evaluate"},
                    "test_cases": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Test cases for evaluation",
                    },
                    "evaluation_metrics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["quality", "speed", "accuracy", "user_satisfaction"],
                        "description": "Metrics to evaluate",
                    },
                    "baseline_comparison": {
                        "type": "boolean",
                        "default": True,
                        "description": "Compare against baseline performance",
                    },
                },
                "required": ["prompt_id"],
            },
        ),
        # Continuous Improvement
        Tool(
            name="run_improvement_cycle",
            description="Run automated continuous improvement cycle for all prompts",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific prompts to optimize (optional, optimizes all if not provided)",
                    },
                    "strategies": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["mipro", "bayesian", "hybrid"],
                        "description": "Optimization strategies to use",
                    },
                    "auto_deploy": {
                        "type": "boolean",
                        "default": True,
                        "description": "Automatically deploy improvements",
                    },
                    "monitoring_interval": {
                        "type": "integer",
                        "default": 3600,
                        "description": "Monitoring interval in seconds",
                    },
                },
            },
        ),
        # Monitoring and Analytics
        Tool(
            name="get_dashboard",
            description="Generate comprehensive performance dashboard with real-time metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard_type": {
                        "type": "string",
                        "enum": ["overview", "detailed", "trends", "alerts"],
                        "default": "overview",
                        "description": "Type of dashboard to generate",
                    },
                    "time_range": {
                        "type": "string",
                        "enum": ["1h", "24h", "7d", "30d"],
                        "default": "24h",
                        "description": "Time range for dashboard data",
                    },
                    "include_predictions": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include performance predictions",
                    },
                },
            },
        ),
        Tool(
            name="get_analytics",
            description="Get detailed analytics on optimization performance and trends",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_id": {
                        "type": "string",
                        "description": "Specific prompt to analyze (optional)",
                    },
                    "metric_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": [
                            "quality",
                            "speed",
                            "user_satisfaction",
                            "optimization_frequency",
                        ],
                        "description": "Types of metrics to analyze",
                    },
                    "include_trends": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include trend analysis",
                    },
                },
            },
        ),
        # Alerting and Notifications
        Tool(
            name="configure_alerts",
            description="Configure alerting rules for optimization system",
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_types": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "threshold": {"type": "number"},
                                "enabled": {"type": "boolean"},
                            },
                        },
                        "description": "Alert configuration",
                    },
                    "notification_channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["dashboard", "logs"],
                        "description": "Notification channels",
                    },
                },
            },
        ),
        # System Management
        Tool(
            name="get_status",
            description="Get comprehensive system status and health metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_metrics": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include detailed metrics",
                    },
                    "include_optimization_status": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include optimization status",
                    },
                },
            },
        ),
        Tool(
            name="deploy_prompts",
            description="Deploy optimized prompts to production with rollback capability",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Prompts to deploy",
                    },
                    "deployment_strategy": {
                        "type": "string",
                        "enum": ["immediate", "gradual", "canary"],
                        "default": "gradual",
                        "description": "Deployment strategy",
                    },
                    "rollback_on_failure": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable automatic rollback on failure",
                    },
                },
            },
        ),
    ]

    return ListToolsResult(tools=tools)


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle production tool calls."""

    try:
        if name == "optimize_prompt":
            result = await optimizer.optimize_prompt_production(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "auto_optimize_feedback":
            result = await optimizer.auto_optimize_with_feedback_production(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "evaluate_performance":
            result = await optimizer.evaluate_prompt_performance_production(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "run_improvement_cycle":
            result = await optimizer.run_continuous_improvement_cycle(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "get_dashboard":
            result = await dashboard_generator.generate_dashboard(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "get_analytics":
            result = await monitoring.get_optimization_analytics(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "configure_alerts":
            result = await alerting.configure_alerting(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "get_status":
            result = await monitoring.get_system_status(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "deploy_prompts":
            result = await optimizer.deploy_optimized_prompts(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        else:
            return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])

    except Exception as e:
        logger.error(f"Error in production tool {name}: {str(e)}")
        return CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])


async def main():
    """Main production server function."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="traffic-sim-production-optimization",
                server_version="2.0.0",
                capabilities=ServerCapabilities(tools={}),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
