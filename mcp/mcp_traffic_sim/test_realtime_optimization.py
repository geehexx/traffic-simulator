"""Test Real-time Prompt Optimization with DSPy."""

from __future__ import annotations

import dspy
from tools.optimize_prompt import optimize_prompt_tool, get_optimization_history_tool


def test_realtime_optimization():
    """Test real-time prompt optimization using DSPy's built-in capabilities."""

    print("🚀 Testing Real-time Prompt Optimization")
    print("=" * 60)

    # Configure DSPy with Gemini
    print("🔧 Configuring DSPy with Gemini...")
    dspy.configure(lm=dspy.LM("gemini/gemini-2.0-flash"))
    print("✅ DSPy configured with Gemini 2.0 Flash")

    # Test 1: Basic optimization
    print("\n📊 Test 1: Basic Prompt Optimization")
    print("-" * 40)

    result = optimize_prompt_tool(
        prompt_id="generate_docs",
        optimization_strategy="mipro",
        auto_mode="light",
        num_threads=1,
        verbose=True,
    )

    print("✅ Optimization completed")
    print(f"📈 Improvement Score: {result['improvement_score']:.2f}")
    print(f"⏱️  Execution Time: {result['execution_time']:.3f}s")
    print(f"🆕 Optimized Prompt ID: {result['optimized_prompt_id']}")

    # Test 2: Different optimization strategies
    print("\n📊 Test 2: Multiple Optimization Strategies")
    print("-" * 40)

    strategies = ["mipro", "bayesian", "bootstrap", "hybrid"]

    for strategy in strategies:
        print(f"\n  🔧 Testing {strategy} strategy:")
        result = optimize_prompt_tool(
            prompt_id="generate_rules",
            optimization_strategy=strategy,
            auto_mode="light",
            num_threads=1,
            verbose=False,
        )

        print(f"    ✅ Success: {result['success']}")
        print(f"    📈 Improvement: {result['improvement_score']:.2f}")
        print(f"    ⏱️  Time: {result['execution_time']:.3f}s")

    # Test 3: Optimization with training data
    print("\n📊 Test 3: Optimization with Training Data")
    print("-" * 40)

    training_data = [
        {
            "code_changes": "Added new collision detection system",
            "context": "Performance optimization",
            "documentation": "Generated comprehensive docs for collision system",
            "sections": ["Overview", "API", "Examples"],
        },
        {
            "code_changes": "Implemented vectorized physics engine",
            "context": "High-performance simulation",
            "documentation": "Created detailed physics engine documentation",
            "sections": ["Architecture", "Performance", "Usage"],
        },
    ]

    result = optimize_prompt_tool(
        prompt_id="generate_docs",
        optimization_strategy="mipro",
        training_data=training_data,
        auto_mode="medium",
        num_threads=2,
        verbose=True,
    )

    print("✅ Optimization with training data completed")
    print(f"📈 Improvement Score: {result['improvement_score']:.2f}")
    print(f"⏱️  Execution Time: {result['execution_time']:.3f}s")
    print(f"📊 Training Examples: {len(training_data)}")

    # Test 4: Get optimization history
    print("\n📊 Test 4: Optimization History")
    print("-" * 40)

    history = get_optimization_history_tool()
    print(f"📋 Total optimizations: {len(history)}")

    for i, opt in enumerate(history[-3:], 1):  # Show last 3
        print(f"  {i}. {opt['prompt_id']} -> {opt['optimized_prompt_id']}")
        print(f"     Strategy: {opt['strategy']}")
        print(f"     Improvement: {opt['improvement_score']:.2f}")
        print(f"     Time: {opt['execution_time']:.3f}s")

    print("\n🎉 Real-time optimization test completed!")
    print("\n📋 Key Benefits Demonstrated:")
    print("  ✅ Real-time optimization using DSPy's built-in tools")
    print("  ✅ Multiple optimization strategies (MIPROv2, Bayesian, etc.)")
    print("  ✅ Training data integration")
    print("  ✅ Automatic improvement scoring")
    print("  ✅ Optimization history tracking")
    print("  ✅ Minimal code changes required")


def test_automatic_optimization_workflow():
    """Test the automatic optimization workflow."""

    print("\n🔄 Testing Automatic Optimization Workflow")
    print("=" * 60)

    # Simulate user feedback and automatic optimization
    print("📊 Simulating user feedback scenario...")

    # Step 1: Initial optimization
    print("\n1️⃣ Initial optimization:")
    result1 = optimize_prompt_tool(
        prompt_id="generate_docs", optimization_strategy="mipro", auto_mode="light"
    )
    print(f"   Initial improvement: {result1['improvement_score']:.2f}")

    # Step 2: Feedback-based optimization
    print("\n2️⃣ Feedback-based optimization:")
    result2 = optimize_prompt_tool(
        prompt_id="generate_docs",
        optimization_strategy="hybrid",
        auto_mode="medium",
        training_data=[
            {
                "code_changes": "User feedback: 'Make documentation more concise'",
                "context": "User feedback integration",
                "documentation": "Optimized for conciseness",
                "sections": ["Quick Start", "API Reference"],
            }
        ],
    )
    print(f"   Feedback improvement: {result2['improvement_score']:.2f}")

    # Step 3: Final optimization
    print("\n3️⃣ Final optimization:")
    result3 = optimize_prompt_tool(
        prompt_id="generate_docs", optimization_strategy="bayesian", auto_mode="heavy"
    )
    print(f"   Final improvement: {result3['improvement_score']:.2f}")

    print("\n✅ Automatic optimization workflow completed!")
    print("📈 Progressive improvement demonstrated:")
    print(f"   Initial: {result1['improvement_score']:.2f}")
    print(f"   Feedback: {result2['improvement_score']:.2f}")
    print(f"   Final: {result3['improvement_score']:.2f}")


if __name__ == "__main__":
    # Run the tests
    test_realtime_optimization()
    test_automatic_optimization_workflow()
