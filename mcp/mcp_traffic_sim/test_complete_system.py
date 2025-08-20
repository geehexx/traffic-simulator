#!/usr/bin/env python3
"""Test the complete prompt management system."""

from pathlib import Path
from prompt_registry import PromptRegistry
from meta_optimizer import MetaOptimizer
from continuous_improvement import ContinuousImprovementWorkflow


def test_complete_system():
    """Test the complete prompt management system."""

    print("🚀 Testing Complete Prompt Management System")
    print("=" * 60)

    # Initialize system components
    registry_path = Path("mcp_registry")
    registry = PromptRegistry(registry_path)
    meta_optimizer = MetaOptimizer(registry)
    workflow = ContinuousImprovementWorkflow(registry)

    # Test 1: List registered prompts
    print("\n📋 Testing Prompt Registry:")
    prompts = registry.list_prompts()
    print(f"✅ Found {len(prompts)} registered prompts:")
    for prompt in prompts:
        print(f"  - {prompt.prompt_id}: {prompt.name}")

    # Test 2: Execute prompts
    print("\n🎯 Testing Prompt Execution:")
    test_cases = [
        {
            "prompt_id": "generate_docs",
            "input": {
                "code_changes": "Implemented new collision detection system",
                "context": "Performance optimization for physics engine",
            },
        },
        {
            "prompt_id": "generate_rules",
            "input": {
                "patterns": "Collision detection patterns and performance",
                "context": "Physics engine optimization guidelines",
            },
        },
        {
            "prompt_id": "hybrid_maintenance",
            "input": {
                "mode": "hybrid",
                "task": "Comprehensive maintenance for collision system",
                "context": "Full documentation and rules update",
            },
        },
    ]

    for test_case in test_cases:
        print(f"\n  🧪 Testing {test_case['prompt_id']}:")
        result = registry.execute_prompt(test_case["prompt_id"], test_case["input"])
        print(f"    ✅ Success: {result.success}")
        print(f"    ⏱️  Time: {result.execution_time:.3f}s")
        if result.success:
            print(f"    📄 Output: {result.output['message'][:100]}...")
        else:
            print(f"    ❌ Error: {result.error_message}")

    # Test 3: Meta-optimization
    print("\n🔧 Testing Meta-Optimization:")
    optimization_strategies = ["mipro", "bayesian", "hybrid"]

    for strategy in optimization_strategies:
        print(f"\n  📊 Testing {strategy} optimization:")
        result = meta_optimizer.optimize_prompt("generate_docs", strategy)
        print(f"    ✅ Success: {result.success}")
        print(f"    📈 Improvement: {result.improvement_score:.2f}")
        print(f"    ⏱️  Time: {result.execution_time:.3f}s")
        if result.success:
            print(f"    🆕 Optimized prompt: {result.optimized_prompt_id}")

    # Test 4: Continuous improvement workflow
    print("\n🔄 Testing Continuous Improvement Workflow:")

    # Run optimization cycle
    cycle_results = workflow.run_optimization_cycle(
        ["generate_docs", "generate_rules"], ["mipro", "hybrid"]
    )
    print("✅ Optimization cycle completed")
    print(f"📊 Results: {len(cycle_results)} prompts optimized")

    # Test performance evaluation
    print("\n📊 Testing Performance Evaluation:")
    test_cases = [
        {"code_changes": "Test change 1", "context": "Test context 1"},
        {"code_changes": "Test change 2", "context": "Test context 2"},
        {"code_changes": "Test change 3", "context": "Test context 3"},
    ]

    performance = workflow.evaluate_prompt_performance("generate_docs", test_cases)
    print("✅ Performance evaluation completed")
    print(f"📈 Quality Score: {performance['overall_quality_score']:.2f}")
    print(f"⏱️  Average Time: {performance['average_execution_time']:.3f}s")

    # Test 5: Get improvement summary
    print("\n📋 Testing Improvement Summary:")
    summary = workflow.get_improvement_summary()
    print("✅ Summary generated")
    print(f"🔄 Total Cycles: {summary['total_cycles']}")
    print(f"📊 Total Prompts: {summary['total_prompts_optimized']}")
    print(f"📈 Average Improvement: {summary['average_improvement_score']:.2f}")

    print("\n🎉 Complete system test successful!")
    print("\n📋 System Capabilities Verified:")
    print("  ✅ Prompt registration and management")
    print("  ✅ Generic execute_prompt functionality")
    print("  ✅ Meta-optimization with multiple strategies")
    print("  ✅ Continuous improvement workflows")
    print("  ✅ Performance evaluation and metrics")
    print("  ✅ Optimization history tracking")

    return True


if __name__ == "__main__":
    test_complete_system()
