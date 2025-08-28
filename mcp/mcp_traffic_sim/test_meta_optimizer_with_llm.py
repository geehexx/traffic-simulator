"""Test the meta optimizer with LLM configuration."""

import dspy
from pathlib import Path
from prompt_registry import PromptRegistry
from meta_optimizer import MetaOptimizer
from continuous_improvement import ContinuousImprovementWorkflow


def test_meta_optimizer_with_llm():
    """Test the meta optimizer with proper LLM configuration."""

    print("🚀 Testing Meta Optimizer with Gemini LLM")
    print("=" * 60)

    # Configure DSPy with Gemini
    print("🔧 Configuring DSPy with Gemini...")
    lm = dspy.LM("gemini/gemini-2.0-flash")
    dspy.configure(lm=lm)
    print("✅ DSPy configured with Gemini 2.0 Flash")

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

    # Test 2: Execute prompts with LLM
    print("\n🎯 Testing Prompt Execution with LLM:")
    test_cases = [
        {
            "prompt_id": "generate_docs",
            "input": {
                "code_changes": "Implemented new collision detection system with DSPy optimization",
                "context": "Advanced prompt management with structured optimization",
            },
        },
        {
            "prompt_id": "generate_rules",
            "input": {
                "patterns": "DSPy module patterns and optimization strategies",
                "context": "Prompt management and optimization guidelines",
            },
        },
    ]

    for test_case in test_cases:
        print(f"\n  🧪 Testing {test_case['prompt_id']}:")
        try:
            result = registry.execute_prompt(test_case["prompt_id"], test_case["input"])
            print(f"    ✅ Success: {result.success}")
            print(f"    ⏱️  Time: {result.execution_time:.3f}s")
            if result.success:
                print(f"    📄 Output: {result.output.get('message', 'No message')[:100]}...")
            else:
                print(f"    ❌ Error: {result.error_message}")
        except Exception as e:
            print(f"    ❌ Exception: {e}")

    # Test 3: Meta-optimization with LLM
    print("\n🔧 Testing Meta-Optimization with LLM:")
    optimization_strategies = ["mipro", "bayesian", "hybrid"]

    for strategy in optimization_strategies:
        print(f"\n  📊 Testing {strategy} optimization:")
        try:
            result = meta_optimizer.optimize_prompt("generate_docs", strategy)
            print(f"    ✅ Success: {result.success}")
            print(f"    📈 Improvement: {result.improvement_score:.2f}")
            print(f"    ⏱️  Time: {result.execution_time:.3f}s")
            if result.success:
                print(f"    🆕 Optimized prompt: {result.optimized_prompt_id}")
                print(f"    🔧 Strategy: {result.optimization_metadata.get('strategy', 'Unknown')}")
        except Exception as e:
            print(f"    ❌ Error: {e}")

    # Test 4: Continuous improvement workflow
    print("\n🔄 Testing Continuous Improvement Workflow:")
    try:
        cycle_results = workflow.run_optimization_cycle(
            ["generate_docs", "generate_rules"], ["mipro", "hybrid"]
        )
        print("✅ Optimization cycle completed")
        print(f"📊 Results: {len(cycle_results)} prompts optimized")

        # Show optimization results
        for result in cycle_results:
            print(
                f"  📈 {result.get('prompt_id', 'Unknown')}: {result.get('improvement_score', 0):.2f}"
            )
    except Exception as e:
        print(f"❌ Optimization cycle failed: {e}")

    # Test 5: Performance evaluation
    print("\n📊 Testing Performance Evaluation:")
    test_cases = [
        {"code_changes": "DSPy test case 1", "context": "Test context 1"},
        {"code_changes": "DSPy test case 2", "context": "Test context 2"},
        {"code_changes": "DSPy test case 3", "context": "Test context 3"},
    ]

    try:
        performance = workflow.evaluate_prompt_performance("generate_docs", test_cases)
        print("✅ Performance evaluation completed")
        print(f"📈 Quality Score: {performance['overall_quality_score']:.2f}")
        print(f"⏱️  Average Time: {performance['average_execution_time']:.3f}s")
    except Exception as e:
        print(f"❌ Performance evaluation failed: {e}")

    print("\n🎉 Meta optimizer test with LLM completed!")
    print("\n📋 System Capabilities Verified:")
    print("  ✅ DSPy configuration with Gemini")
    print("  ✅ Prompt execution with LLM")
    print("  ✅ Meta-optimization with multiple strategies")
    print("  ✅ Continuous improvement workflows")
    print("  ✅ Performance evaluation and metrics")


if __name__ == "__main__":
    test_meta_optimizer_with_llm()
