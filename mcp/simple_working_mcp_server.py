#!/usr/bin/env python3
"""Simple working MCP server for testing Cursor compatibility."""

import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, ListToolsResult, Tool, TextContent, ServerCapabilities
from mcp.server.models import InitializationOptions


# Create server
server = Server("simple-working-server")


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools."""
    return ListToolsResult(
        tools=[
            Tool(
                name="get_status",
                description="Get system status",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "include_metrics": {"type": "boolean", "default": True},
                        "include_optimization_status": {"type": "boolean", "default": True},
                    },
                },
            ),
            Tool(
                name="get_analytics",
                description="Get optimization analytics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt_id": {"type": "string"},
                        "metric_types": {"type": "array", "items": {"type": "string"}},
                        "include_trends": {"type": "boolean", "default": True},
                    },
                },
            ),
        ]
    )


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    """Handle tool calls."""
    try:
        if name == "get_status":
            result = {
                "success": True,
                "status": {
                    "system_health": "healthy",
                    "timestamp": 1234567890,
                    "uptime": 3600,
                    "active_monitoring": 0,
                    "total_optimizations": 0,
                    "metrics": {
                        "total_alerts": 0,
                        "average_quality_score": 0.0,
                        "optimization_success_rate": 0.0,
                        "system_performance": 0.0,
                    },
                    "optimization_status": {
                        "active_optimizations": 0,
                        "completed_optimizations": 0,
                        "failed_optimizations": 0,
                        "average_execution_time": 0.0,
                    },
                },
            }

            # Use the simplest possible response format
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "get_analytics":
            result = {
                "success": True,
                "analytics": {
                    "quality_metrics": {"average_score": 0.85, "trend": "improving"},
                    "performance_metrics": {"response_time": 0.5, "throughput": 100},
                    "optimization_metrics": {"total_optimizations": 0, "success_rate": 1.0},
                },
                "generated_at": 1234567890,
            }

            # Use the simplest possible response format
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        else:
            return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])

    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])


async def main():
    """Main server function."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="simple-working-server",
                server_version="1.0.0",
                capabilities=ServerCapabilities(tools={}),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
