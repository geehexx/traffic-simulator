"""Simple Real-time Prompt Optimization using DSPy's built-in capabilities."""

from __future__ import annotations

import dspy
import time
from typing import Any, Dict, List


def test_dspy_realtime_optimization():
    """Test real-time prompt optimization using DSPy's built-in optimizers."""

    print("🚀 Testing DSPy Real-time Prompt Optimization")
    print("=" * 60)

    # Configure DSPy with Gemini
    print("🔧 Configuring DSPy with Gemini...")
    dspy.configure(lm=dspy.LM("gemini/gemini-2.0-flash"))
    print("✅ DSPy configured with Gemini 2.0 Flash")

    # Test 1: Create a simple DSPy module
    print("\n📊 Test 1: Creating DSPy Module")
    print("-" * 40)

    class DocumentationSignature(dspy.Signature):
        """Generate documentation for code changes."""

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

    # Create the module
    doc_module = DocumentationModule()
    print("✅ Documentation module created")

    # Test 2: Create training data
    print("\n📊 Test 2: Creating Training Data")
    print("-" * 40)

    # Create training examples
    training_examples = [
        dspy.Example(
            code_changes="Added new collision detection system",
            context="Performance optimization",
            documentation="## Collision Detection System\n\nThis system provides efficient collision detection for the traffic simulator...",
            sections=["Overview", "API", "Examples"],
        ).with_inputs("code_changes", "context"),
        dspy.Example(
            code_changes="Implemented vectorized physics engine",
            context="High-performance simulation",
            documentation="## Vectorized Physics Engine\n\nThe physics engine uses NumPy vectorization for optimal performance...",
            sections=["Architecture", "Performance", "Usage"],
        ).with_inputs("code_changes", "context"),
    ]

    print(f"✅ Created {len(training_examples)} training examples")

    # Test 3: Define evaluation metric
    print("\n📊 Test 3: Setting Up Evaluation")
    print("-" * 40)

    def documentation_metric(example, prediction):
        """Metric for evaluating documentation quality."""
        score = 0.0

        # Check if documentation was generated
        if hasattr(prediction, "documentation") and prediction.documentation:
            score += 0.4

        # Check if sections were provided
        if hasattr(prediction, "sections") and prediction.sections:
            score += 0.3

        # Check for markdown formatting
        if hasattr(prediction, "documentation") and "##" in prediction.documentation:
            score += 0.3

        return score

    print("✅ Evaluation metric defined")

    # Test 4: Run MIPROv2 optimization
    print("\n📊 Test 4: Running MIPROv2 Optimization")
    print("-" * 40)

    try:
        # Create MIPROv2 optimizer
        optimizer = dspy.MIPROv2(
            metric=documentation_metric, auto="light", num_threads=1, verbose=True
        )

        print("🔧 Running MIPROv2 optimization...")
        start_time = time.time()

        # Compile the optimized module
        optimized_module = optimizer.compile(
            doc_module, trainset=training_examples, requires_permission_to_run=False
        )

        optimization_time = time.time() - start_time
        print(f"✅ MIPROv2 optimization completed in {optimization_time:.3f}s")

        # Test 5: Compare original vs optimized
        print("\n📊 Test 5: Comparing Original vs Optimized")
        print("-" * 40)

        test_input = {
            "code_changes": "Implemented new vehicle physics system",
            "context": "Advanced physics simulation",
        }

        # Test original module
        print("🧪 Testing original module...")
        original_result = doc_module.forward(**test_input)
        print(f"   Original output: {original_result['documentation'][:100]}...")

        # Test optimized module
        print("🧪 Testing optimized module...")
        optimized_result = optimized_module.forward(**test_input)
        print(f"   Optimized output: {optimized_result['documentation'][:100]}...")

        # Test 6: Run other optimizers
        print("\n📊 Test 6: Testing Other Optimizers")
        print("-" * 40)

        # BootstrapFewShot optimizer
        print("🔧 Testing BootstrapFewShot...")
        bootstrap_optimizer = dspy.BootstrapFewShot(
            metric=documentation_metric, max_bootstrapped_demos=2, max_labeled_demos=2
        )

        bootstrap_optimized = bootstrap_optimizer.compile(doc_module, trainset=training_examples)

        bootstrap_result = bootstrap_optimized.forward(**test_input)
        print(f"   Bootstrap output: {bootstrap_result['documentation'][:100]}...")

        # Bayesian optimizer
        print("🔧 Testing BayesianSignatureOptimizer...")
        bayesian_optimizer = dspy.BayesianSignatureOptimizer(metric=documentation_metric)

        bayesian_optimized = bayesian_optimizer.compile(doc_module, trainset=training_examples)

        bayesian_result = bayesian_optimized.forward(**test_input)
        print(f"   Bayesian output: {bayesian_result['documentation'][:100]}...")

        print("\n🎉 DSPy real-time optimization test completed!")
        print("\n📋 Key Benefits Demonstrated:")
        print("  ✅ Real-time optimization using DSPy's built-in MIPROv2")
        print("  ✅ Multiple optimization strategies (BootstrapFewShot, Bayesian)")
        print("  ✅ Automatic prompt generation and optimization")
        print("  ✅ Training data integration")
        print("  ✅ Evaluation metrics")
        print("  ✅ Minimal code changes required")
        print("  ✅ Production-ready optimization")

        return {
            "success": True,
            "optimization_time": optimization_time,
            "original_result": original_result,
            "optimized_result": optimized_result,
            "bootstrap_result": bootstrap_result,
            "bayesian_result": bayesian_result,
        }

    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        return {"success": False, "error": str(e)}


def test_automatic_optimization_workflow():
    """Test automatic optimization workflow with user feedback."""

    print("\n🔄 Testing Automatic Optimization Workflow")
    print("=" * 60)

    # Configure DSPy
    dspy.configure(lm=dspy.LM("gemini/gemini-2.0-flash"))

    # Create a simple feedback-based optimization
    class FeedbackSignature(dspy.Signature):
        """Optimize prompt based on user feedback."""

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

    # Test feedback-based optimization
    feedback_optimizer = FeedbackOptimizer()

    original_prompt = "Generate documentation for code changes"
    user_feedback = "Make the documentation more concise and include code examples"

    print("🔧 Running feedback-based optimization...")
    optimized_prompt = feedback_optimizer.forward(original_prompt, user_feedback)

    print(f"📝 Original: {original_prompt}")
    print(f"📝 Optimized: {optimized_prompt}")

    print("\n✅ Automatic optimization workflow completed!")
    print("📈 Feedback-based optimization demonstrated")


if __name__ == "__main__":
    # Run the tests
    result = test_dspy_realtime_optimization()
    test_automatic_optimization_workflow()

    if result.get("success"):
        print("\n🎯 Final Results:")
        print(f"   Optimization Time: {result['optimization_time']:.3f}s")
        print(f"   Original Output Length: {len(result['original_result']['documentation'])}")
        print(f"   Optimized Output Length: {len(result['optimized_result']['documentation'])}")
        print(
            f"   Improvement: {len(result['optimized_result']['documentation']) / len(result['original_result']['documentation']):.2f}x"
        )
