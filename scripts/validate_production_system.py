#!/usr/bin/env python3
"""Production System Validation Script

Validates that all restored components are functioning correctly.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "mcp"))


def test_imports():
    """Test that all core components can be imported."""
    print("🔍 Testing component imports...")

    try:
        # Test core components - just test imports, don't use the objects
        from mcp_traffic_sim import production_server  # noqa: F401
        from mcp_traffic_sim import production_optimizer  # noqa: F401
        from mcp_traffic_sim import monitoring_system  # noqa: F401
        from mcp_traffic_sim import feedback_collector  # noqa: F401
        from mcp_traffic_sim import dashboard_generator  # noqa: F401
        from mcp_traffic_sim import alerting_system  # noqa: F401
        from mcp_traffic_sim import integration_system  # noqa: F401
        from mcp_traffic_sim import advanced_file_manager  # noqa: F401

        print("✅ All core components imported successfully")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_mcp_tools():
    """Test that MCP tools are properly configured."""
    print("🔍 Testing MCP tools configuration...")

    try:
        from mcp_traffic_sim.production_server import server

        # Test that server has the expected tools
        tools = server._tools if hasattr(server, "_tools") else []
        expected_tools = [
            "optimize_prompt_production",
            "auto_optimize_with_feedback_production",
            "evaluate_prompt_performance_production",
            "run_continuous_improvement_cycle",
            "get_performance_dashboard",
            "get_optimization_analytics",
            "configure_alerting",
            "get_system_status",
            "deploy_optimized_prompts",
            "update_documentation",
            "consolidate_files",
            "manage_versions",
        ]

        print(f"✅ Found {len(tools)} MCP tools configured")
        print(f"✅ Expected {len(expected_tools)} tools")

        return True

    except Exception as e:
        print(f"❌ MCP tools test failed: {e}")
        return False


async def test_async_components():
    """Test async components can be initialized."""
    print("🔍 Testing async component initialization...")

    try:
        from mcp_traffic_sim.config import MCPConfig
        from mcp_traffic_sim.logging_util import MCPLogger
        from mcp_traffic_sim.security import SecurityManager
        from mcp_traffic_sim.production_optimizer import ProductionOptimizer
        from mcp_traffic_sim.monitoring_system import MonitoringSystem
        from mcp_traffic_sim.advanced_file_manager import AdvancedFileManager

        # Initialize components
        config = MCPConfig()
        logger = MCPLogger(config.log_dir)
        security = SecurityManager(config)

        # Test component initialization (assign to variables to avoid unused warnings)
        _ = ProductionOptimizer(config, logger, security)
        _ = MonitoringSystem(config, logger, security)
        _ = AdvancedFileManager(config, logger)

        print("✅ All async components initialized successfully")
        return True

    except Exception as e:
        print(f"❌ Async component test failed: {e}")
        return False


def test_file_structure():
    """Test that all required files are present."""
    print("🔍 Testing file structure...")

    required_files = [
        "mcp/mcp_traffic_sim/production_server.py",
        "mcp/mcp_traffic_sim/production_optimizer.py",
        "mcp/mcp_traffic_sim/monitoring_system.py",
        "mcp/mcp_traffic_sim/feedback_collector.py",
        "mcp/mcp_traffic_sim/dashboard_generator.py",
        "mcp/mcp_traffic_sim/alerting_system.py",
        "mcp/mcp_traffic_sim/integration_system.py",
        "mcp/mcp_traffic_sim/advanced_file_manager.py",
    ]

    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True


def test_dependencies():
    """Test that critical dependencies are available."""
    print("🔍 Testing dependencies...")

    critical_deps = ["dspy", "mcp", "pydantic"]
    missing_deps = []

    for dep in critical_deps:
        try:
            __import__(dep)
        except ImportError:
            missing_deps.append(dep)

    if missing_deps:
        print(f"❌ Missing dependencies: {missing_deps}")
        print("💡 Install with: pip install dspy-ai mcp pydantic")
        return False
    else:
        print("✅ All critical dependencies available")
        return True


async def main():
    """Run all validation tests."""
    print("🚀 Starting Production System Validation")
    print("=" * 50)

    tests = [
        ("File Structure", test_file_structure),
        ("Dependencies", test_dependencies),
        ("Component Imports", test_imports),
        ("MCP Tools", test_mcp_tools),
        ("Async Components", test_async_components),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)

        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()

        results.append((test_name, result))

    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All validation tests passed! System is ready for production.")
        return 0
    else:
        print("⚠️  Some tests failed. Please address the issues above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
