#!/usr/bin/env python3
"""Simple MCP server for testing."""

import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, ListToolsResult, Tool, TextContent


# Create server
server = Server("test-server")


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools."""
    return ListToolsResult(
        tools=[
            Tool(
                name="test_status",
                description="Test status tool",
                inputSchema={
                    "type": "object",
                    "properties": {"include_metrics": {"type": "boolean", "default": True}},
                },
            )
        ]
    )


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    """Handle tool calls."""
    if name == "test_status":
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

        return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])

    return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])


async def main():
    """Main server function."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
