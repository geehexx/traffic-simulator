#!/usr/bin/env python3
"""Test script to verify MCP tool fixes."""

import asyncio
import json
import sys
from pathlib import Path

# Add the mcp_traffic_sim module to path
sys.path.insert(0, str(Path(__file__).parent / "mcp_traffic_sim"))

from mcp_traffic_sim.config import MCPConfig
from mcp_traffic_sim.logging_util import MCPLogger
from mcp_traffic_sim.security import SecurityManager
from mcp_traffic_sim.monitoring_system import MonitoringSystem


async def test_analytics_tool():
    """Test the analytics tool to ensure it works properly."""
    print("🧪 Testing MCP Analytics Tool...")

    try:
        # Initialize components
        config = MCPConfig()
        logger = MCPLogger(config.log_dir)
        security = SecurityManager(config)
        monitoring = MonitoringSystem(config, logger, security)

        # Test analytics with minimal arguments
        test_arguments = {"metric_types": ["quality", "speed"], "include_trends": True}

        print("📊 Calling get_optimization_analytics...")
        result = await monitoring.get_optimization_analytics(test_arguments)

        print("✅ Analytics result:")
        print(json.dumps(result, indent=2, default=str))

        # Test with prompt_id
        test_arguments_with_id = {
            "prompt_id": "generate_docs",
            "metric_types": ["quality"],
            "include_trends": False,
        }

        print("\n📊 Calling get_optimization_analytics with prompt_id...")
        result_with_id = await monitoring.get_optimization_analytics(test_arguments_with_id)

        print("✅ Analytics result with prompt_id:")
        print(json.dumps(result_with_id, indent=2, default=str))

        return True

    except Exception as e:
        print(f"❌ Error testing analytics tool: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback

        traceback.print_exc()
        return False


async def test_system_status():
    """Test the system status tool."""
    print("\n🧪 Testing MCP System Status Tool...")

    try:
        # Initialize components
        config = MCPConfig()
        logger = MCPLogger(config.log_dir)
        security = SecurityManager(config)
        monitoring = MonitoringSystem(config, logger, security)

        # Test system status
        test_arguments = {"include_metrics": True, "include_optimization_status": True}

        print("📊 Calling get_system_status...")
        result = await monitoring.get_system_status(test_arguments)

        print("✅ System status result:")
        print(json.dumps(result, indent=2, default=str))

        return True

    except Exception as e:
        print(f"❌ Error testing system status tool: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting MCP Tool Fix Verification...")

    tests = [
        ("Analytics Tool", test_analytics_tool),
        ("System Status Tool", test_system_status),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Testing: {test_name}")
        print(f"{'='*50}")

        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print(f"\n{'='*50}")
    print("📋 TEST SUMMARY")
    print(f"{'='*50}")

    passed = 0
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
        if success:
            passed += 1

    print(f"\nResults: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All tests passed! MCP tools are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
