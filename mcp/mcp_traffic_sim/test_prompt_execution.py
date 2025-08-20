#!/usr/bin/env python3
"""Test prompt execution functionality."""

from pathlib import Path
from prompt_registry import PromptRegistry


def test_prompt_execution():
    """Test the execute_prompt functionality."""

    # Initialize registry
    registry_path = Path("mcp_registry")
    registry = PromptRegistry(registry_path)

    print("🧪 Testing Prompt Execution")
    print("=" * 50)

    # Test 1: Execute documentation prompt
    print("\n📝 Testing Documentation Prompt:")
    docs_result = registry.execute_prompt(
        "generate_docs",
        {
            "code_changes": "Added new vehicle physics engine with NumPy optimization",
            "context": "Performance improvement for large-scale simulations",
        },
    )

    print(f"✅ Success: {docs_result.success}")
    print(f"⏱️  Execution Time: {docs_result.execution_time:.3f}s")
    if docs_result.success:
        print(f"📄 Output: {docs_result.output['message']}")
    else:
        print(f"❌ Error: {docs_result.error_message}")

    # Test 2: Execute rules prompt
    print("\n📋 Testing Rules Prompt:")
    rules_result = registry.execute_prompt(
        "generate_rules",
        {
            "patterns": "NumPy vectorized operations for performance",
            "context": "Physics engine optimization patterns",
        },
    )

    print(f"✅ Success: {rules_result.success}")
    print(f"⏱️  Execution Time: {rules_result.execution_time:.3f}s")
    if rules_result.success:
        print(f"📄 Output: {rules_result.output['message']}")
    else:
        print(f"❌ Error: {rules_result.error_message}")

    # Test 3: Execute hybrid prompt
    print("\n🔄 Testing Hybrid Prompt:")
    hybrid_result = registry.execute_prompt(
        "hybrid_maintenance",
        {
            "mode": "hybrid",
            "task": "Update documentation and rules for new physics engine",
            "context": "Comprehensive maintenance for performance improvements",
        },
    )

    print(f"✅ Success: {hybrid_result.success}")
    print(f"⏱️  Execution Time: {hybrid_result.execution_time:.3f}s")
    if hybrid_result.success:
        print(f"📄 Output: {hybrid_result.output['message']}")
    else:
        print(f"❌ Error: {hybrid_result.error_message}")

    # Test 4: Test error handling
    print("\n❌ Testing Error Handling:")
    error_result = registry.execute_prompt("nonexistent_prompt", {"test": "data"})

    print(f"✅ Success: {error_result.success}")
    print(f"⏱️  Execution Time: {error_result.execution_time:.3f}s")
    if not error_result.success:
        print(f"❌ Expected Error: {error_result.error_message}")

    print("\n🎉 All prompt execution tests completed!")
    return True


if __name__ == "__main__":
    test_prompt_execution()
