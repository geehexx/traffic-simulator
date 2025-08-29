"""Prompt Integration Workflow for Optimized Prompts."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List

from prompt_registry import PromptRegistry
from meta_optimizer import MetaOptimizer
from continuous_improvement import ContinuousImprovementWorkflow


class PromptIntegrationWorkflow:
    """Workflow for integrating optimized prompts back into the system."""

    def __init__(self, registry_path: Path):
        """Initialize the integration workflow."""
        self.registry = PromptRegistry(registry_path)
        self.meta_optimizer = MetaOptimizer(self.registry)
        self.workflow = ContinuousImprovementWorkflow(self.registry)

    def analyze_optimized_prompts(self) -> Dict[str, Any]:
        """Analyze the current optimized prompts and their performance."""
        print("🔍 Analyzing Optimized Prompts")
        print("=" * 50)

        # Get all prompts
        all_prompts = self.registry.list_prompts()
        optimized_prompts = [p for p in all_prompts if "optimized" in p.prompt_id]
        original_prompts = [
            p
            for p in all_prompts
            if "optimized" not in p.prompt_id and p.prompt_id != "hybrid_maintenance"
        ]

        print(f"📊 Found {len(optimized_prompts)} optimized prompts:")
        for prompt in optimized_prompts:
            print(f"  - {prompt.prompt_id}: {prompt.name}")
            print(f"    Strategy: {prompt.metadata.get('optimization_strategy', 'Unknown')}")
            print(f"    Original: {prompt.metadata.get('original_prompt_id', 'Unknown')}")
            print(f"    Version: {prompt.version}")

        print(f"\n📋 Found {len(original_prompts)} original prompts:")
        for prompt in original_prompts:
            print(f"  - {prompt.prompt_id}: {prompt.name}")

        return {
            "optimized_prompts": optimized_prompts,
            "original_prompts": original_prompts,
            "total_prompts": len(all_prompts),
        }

    def create_integration_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a plan for integrating optimized prompts."""
        print("\n📋 Creating Integration Plan")
        print("=" * 50)

        plan = {
            "integration_strategy": "gradual_replacement",
            "steps": [],
            "rollback_plan": [],
            "testing_plan": [],
        }

        # Step 1: Validate optimized prompts
        plan["steps"].append(
            {
                "step": 1,
                "action": "validate_optimized_prompts",
                "description": "Validate that optimized prompts are working correctly",
                "targets": [p.prompt_id for p in analysis["optimized_prompts"]],
            }
        )

        # Step 2: Performance comparison
        plan["steps"].append(
            {
                "step": 2,
                "action": "performance_comparison",
                "description": "Compare performance between original and optimized prompts",
                "targets": ["generate_docs", "generate_rules"],
            }
        )

        # Step 3: Gradual replacement
        plan["steps"].append(
            {
                "step": 3,
                "action": "gradual_replacement",
                "description": "Replace original prompts with optimized versions",
                "targets": ["generate_docs", "generate_rules"],
            }
        )

        # Step 4: Update active prompts
        plan["steps"].append(
            {
                "step": 4,
                "action": "update_active_prompts",
                "description": "Update the system to use optimized prompts as active",
                "targets": ["generate_docs_optimized_v1", "generate_rules_optimized_v1"],
            }
        )

        # Rollback plan
        plan["rollback_plan"] = [
            {
                "action": "restore_original_prompts",
                "description": "Restore original prompts if issues arise",
                "targets": ["generate_docs", "generate_rules"],
            }
        ]

        # Testing plan
        plan["testing_plan"] = [
            {
                "action": "test_prompt_execution",
                "description": "Test that optimized prompts execute correctly",
                "test_cases": [
                    {"code_changes": "Test change 1", "context": "Test context 1"},
                    {"patterns": "Test pattern 1", "context": "Test context 1"},
                ],
            },
            {
                "action": "performance_validation",
                "description": "Validate that performance improvements are maintained",
                "metrics": ["execution_time", "quality_score", "success_rate"],
            },
        ]

        print("✅ Integration plan created")
        for step in plan["steps"]:
            print(f"  {step['step']}. {step['action']}: {step['description']}")

        return plan

    def execute_integration_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the integration plan."""
        print("\n🚀 Executing Integration Plan")
        print("=" * 50)

        results = {"success": True, "steps_completed": [], "errors": [], "performance_metrics": {}}

        for step in plan["steps"]:
            print(f"\n📋 Step {step['step']}: {step['action']}")

            try:
                if step["action"] == "validate_optimized_prompts":
                    result = self._validate_optimized_prompts(step["targets"])
                    results["steps_completed"].append(step["step"])

                elif step["action"] == "performance_comparison":
                    result = self._compare_performance(step["targets"])
                    results["performance_metrics"].update(result)
                    results["steps_completed"].append(step["step"])

                elif step["action"] == "gradual_replacement":
                    result = self._replace_prompts_gradually(step["targets"])
                    results["steps_completed"].append(step["step"])

                elif step["action"] == "update_active_prompts":
                    result = self._update_active_prompts(step["targets"])
                    results["steps_completed"].append(step["step"])

                print(f"  ✅ {step['action']} completed successfully")

            except Exception as e:
                print(f"  ❌ {step['action']} failed: {e}")
                results["errors"].append(f"Step {step['step']}: {e}")
                results["success"] = False

        return results

    def _validate_optimized_prompts(self, targets: List[str]) -> Dict[str, Any]:
        """Validate that optimized prompts are working correctly."""
        print("  🔍 Validating optimized prompts...")

        validation_results = {}

        for target in targets:
            try:
                # Test the optimized prompt
                if "docs" in target:
                    result = self.registry.execute_prompt(
                        target, {"code_changes": "Test validation", "context": "Validation test"}
                    )
                elif "rules" in target:
                    result = self.registry.execute_prompt(
                        target, {"patterns": "Test validation", "context": "Validation test"}
                    )

                validation_results[target] = {
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "error": result.error_message if not result.success else None,
                }

                print(f"    ✅ {target}: {'Success' if result.success else 'Failed'}")

            except Exception as e:
                validation_results[target] = {"success": False, "error": str(e)}
                print(f"    ❌ {target}: {e}")

        return validation_results

    def _compare_performance(self, targets: List[str]) -> Dict[str, Any]:
        """Compare performance between original and optimized prompts."""
        print("  📊 Comparing performance...")

        comparison_results = {}

        for target in targets:
            original_id = target
            optimized_id = f"{target}_optimized_v1"

            # Test original prompt
            original_result = self.registry.execute_prompt(
                original_id, {"code_changes": "Performance test", "context": "Test context"}
            )

            # Test optimized prompt
            optimized_result = self.registry.execute_prompt(
                optimized_id, {"code_changes": "Performance test", "context": "Test context"}
            )

            comparison_results[target] = {
                "original": {
                    "success": original_result.success,
                    "execution_time": original_result.execution_time,
                },
                "optimized": {
                    "success": optimized_result.success,
                    "execution_time": optimized_result.execution_time,
                },
                "improvement": {
                    "time_reduction": original_result.execution_time
                    - optimized_result.execution_time,
                    "success_rate": optimized_result.success and original_result.success,
                },
            }

            print(
                f"    📈 {target}: {comparison_results[target]['improvement']['time_reduction']:.3f}s improvement"
            )

        return comparison_results

    def _replace_prompts_gradually(self, targets: List[str]) -> Dict[str, Any]:
        """Replace original prompts with optimized versions gradually."""
        print("  🔄 Replacing prompts gradually...")

        replacement_results = {}

        for target in targets:
            optimized_id = f"{target}_optimized_v1"

            # Get the optimized prompt
            optimized_prompt = self.registry.get_prompt(optimized_id)
            if not optimized_prompt:
                print(f"    ❌ Optimized prompt {optimized_id} not found")
                continue

            # Create a new version of the original prompt with optimized content
            original_prompt = self.registry.get_prompt(target)
            if not original_prompt:
                print(f"    ❌ Original prompt {target} not found")
                continue

            # Update the original prompt with optimized content
            original_prompt.template = optimized_prompt.template
            original_prompt.version = "2.0.0"
            original_prompt.metadata.update(
                {
                    "optimization_strategy": optimized_prompt.metadata.get("optimization_strategy"),
                    "optimization_timestamp": optimized_prompt.metadata.get(
                        "optimization_timestamp"
                    ),
                    "version_history": original_prompt.metadata.get("version_history", [])
                    + ["2.0.0"],
                }
            )

            # Save the updated prompt
            self.registry._save_registry()

            replacement_results[target] = {
                "success": True,
                "new_version": "2.0.0",
                "optimization_strategy": optimized_prompt.metadata.get("optimization_strategy"),
            }

            print(f"    ✅ {target} updated with optimized content")

        return replacement_results

    def _update_active_prompts(self, targets: List[str]) -> Dict[str, Any]:
        """Update the system to use optimized prompts as active."""
        print("  🎯 Updating active prompts...")

        activation_results = {}

        for target in targets:
            # Set the optimized prompt as active
            prompt = self.registry.get_prompt(target)
            if prompt:
                prompt.active = True
                activation_results[target] = {"active": True}
                print(f"    ✅ {target} set as active")
            else:
                activation_results[target] = {"active": False, "error": "Prompt not found"}
                print(f"    ❌ {target} not found")

        # Save the registry
        self.registry._save_registry()

        return activation_results

    def generate_integration_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive integration report."""
        report = []
        report.append("# Prompt Integration Report")
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        report.append("## Summary")
        report.append(f"- Integration Success: {'✅ Yes' if results['success'] else '❌ No'}")
        report.append(f"- Steps Completed: {len(results['steps_completed'])}")
        report.append(f"- Errors: {len(results['errors'])}")
        report.append("")

        if results["errors"]:
            report.append("## Errors")
            for error in results["errors"]:
                report.append(f"- {error}")
            report.append("")

        if results["performance_metrics"]:
            report.append("## Performance Metrics")
            for target, metrics in results["performance_metrics"].items():
                report.append(f"### {target}")
                if "improvement" in metrics:
                    improvement = metrics["improvement"]
                    report.append(f"- Time Reduction: {improvement['time_reduction']:.3f}s")
                    report.append(
                        f"- Success Rate: {'✅' if improvement['success_rate'] else '❌'}"
                    )
                report.append("")

        report.append("## Next Steps")
        report.append("1. Monitor system performance with optimized prompts")
        report.append("2. Collect user feedback on prompt quality")
        report.append("3. Run additional optimization cycles if needed")
        report.append("4. Update documentation with new prompt versions")

        return "\n".join(report)

    def run_complete_integration_workflow(self) -> Dict[str, Any]:
        """Run the complete integration workflow."""
        print("🚀 Starting Complete Prompt Integration Workflow")
        print("=" * 60)

        # Step 1: Analyze optimized prompts
        analysis = self.analyze_optimized_prompts()

        # Step 2: Create integration plan
        plan = self.create_integration_plan(analysis)

        # Step 3: Execute integration plan
        results = self.execute_integration_plan(plan)

        # Step 4: Generate report
        report = self.generate_integration_report(results)

        # Save report
        report_path = Path("mcp_registry/integration_report.md")
        with open(report_path, "w") as f:
            f.write(report)

        print(f"\n📄 Integration report saved to: {report_path}")
        print("\n🎉 Integration workflow completed!")

        return {"analysis": analysis, "plan": plan, "results": results, "report": report}


def main():
    """Main function to run the integration workflow."""
    registry_path = Path("mcp_registry")
    workflow = PromptIntegrationWorkflow(registry_path)

    # Run the complete workflow
    results = workflow.run_complete_integration_workflow()

    # Print summary
    print("\n📋 Integration Summary:")
    print(f"✅ Success: {results['results']['success']}")
    print(f"📊 Steps Completed: {len(results['results']['steps_completed'])}")
    print(f"❌ Errors: {len(results['results']['errors'])}")

    if results["results"]["performance_metrics"]:
        print("\n📈 Performance Improvements:")
        for target, metrics in results["results"]["performance_metrics"].items():
            if "improvement" in metrics:
                improvement = metrics["improvement"]
                print(f"  {target}: {improvement['time_reduction']:.3f}s faster")


if __name__ == "__main__":
    main()
