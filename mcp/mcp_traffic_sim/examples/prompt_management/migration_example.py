"""Example of migrating current prompts to the new system."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

from ..schemas import PromptCandidate, PromptMode, MetaOptimizerConfig
from ..registry import PromptRegistryManager
from ..meta_optimizer import MetaOptimizer


class PromptMigrationExample:
    """Example of migrating current prompts to the new system."""

    def __init__(self, registry_path: Path):
        """Initialize migration example."""
        self.registry_manager = PromptRegistryManager(registry_path)
        self.meta_optimizer = MetaOptimizer(
            registry_manager=self.registry_manager, config=MetaOptimizerConfig()
        )

    def migrate_super_prompt(self) -> str:
        """Migrate the super prompt to the new system."""
        # Load current super prompt content
        super_prompt_content = self._load_super_prompt_content()

        # Create prompt candidate
        super_prompt = PromptCandidate(
            content=super_prompt_content,
            parameters={
                "ape_methodology": True,
                "stability_threshold": 0.85,
                "dual_path_generation": True,
                "token_budget": {
                    "per_rule": "250-500 tokens",
                    "max_global_rules": 5,
                    "soft_cap": 500,
                    "hard_cap": 900,
                },
            },
            metadata={
                "source": "docs/prompts/generate-super.md",
                "version": "1.0",
                "migration_date": "2024-01-01",
                "optimization_history": [],
            },
        )

        # Register in registry
        prompt_id = self.registry_manager.register_prompt(
            content=super_prompt.content,
            mode=PromptMode.HYBRID,
            parameters=super_prompt.parameters,
            metadata=super_prompt.metadata,
        )

        # Set as active for hybrid mode
        self.registry_manager.set_active_prompt(PromptMode.HYBRID, prompt_id)

        return prompt_id

    def migrate_meta_optimizer_prompt(self) -> str:
        """Migrate the meta-optimizer prompt to the new system."""
        # Load current meta-optimizer prompt content
        meta_optimizer_content = self._load_meta_optimizer_content()

        # Create prompt candidate
        meta_optimizer_prompt = PromptCandidate(
            content=meta_optimizer_content,
            parameters={
                "optimization_criteria": [
                    "clarity_actionability",
                    "determinism_idempotency",
                    "breadth_context",
                    "consolidation_intelligence",
                    "dual_path_generation",
                    "scoring_integration",
                ],
                "artifact_quality_rubrics": {"docs": "PDQI-9", "rules": "RGS"},
                "stability_threshold": 0.85,
                "candidate_generation": {
                    "structural_variation": True,
                    "brevity_variation": True,
                    "targeting_variation": True,
                },
            },
            metadata={
                "source": "docs/prompts/generate-meta-optimizer.md",
                "version": "1.0",
                "migration_date": "2024-01-01",
                "optimization_history": [],
            },
        )

        # Register in registry
        prompt_id = self.registry_manager.register_prompt(
            content=meta_optimizer_prompt.content,
            mode=PromptMode.PLAN_OPTIMIZE,
            parameters=meta_optimizer_prompt.parameters,
            metadata=meta_optimizer_prompt.metadata,
        )

        return prompt_id

    def run_initial_optimization(self) -> Dict[str, Any]:
        """Run initial optimization on migrated prompts."""
        results = {}

        # Optimize hybrid prompt
        hybrid_result = self.meta_optimizer.optimize_prompts(
            mode=PromptMode.HYBRID, test_inputs=self._generate_test_inputs(PromptMode.HYBRID)
        )
        results["hybrid"] = hybrid_result

        # Optimize docs prompt
        docs_result = self.meta_optimizer.optimize_prompts(
            mode=PromptMode.DOCS, test_inputs=self._generate_test_inputs(PromptMode.DOCS)
        )
        results["docs"] = docs_result

        # Optimize rules prompt
        rules_result = self.meta_optimizer.optimize_prompts(
            mode=PromptMode.RULES, test_inputs=self._generate_test_inputs(PromptMode.RULES)
        )
        results["rules"] = rules_result

        return results

    def demonstrate_self_improvement(self) -> Dict[str, Any]:
        """Demonstrate self-improvement capabilities."""
        # Check if optimization is due
        should_optimize = self.meta_optimizer.should_optimize()

        if should_optimize:
            # Run optimization for all modes
            optimization_results = {}

            for mode in [PromptMode.DOCS, PromptMode.RULES, PromptMode.HYBRID]:
                result = self.meta_optimizer.optimize_prompts(
                    mode=mode, test_inputs=self._generate_test_inputs(mode)
                )
                optimization_results[mode.value] = result

            return {
                "optimization_triggered": True,
                "results": optimization_results,
                "next_optimization": "7 days from now",
            }
        else:
            return {
                "optimization_triggered": False,
                "next_optimization": "Optimization not due yet",
            }

    def demonstrate_structured_execution(self) -> Dict[str, Any]:
        """Demonstrate structured prompt execution."""
        # Example execution with structured input
        execution_result = {
            "mode": "docs",
            "repo_metadata": {
                "name": "traffic-simulator",
                "type": "simulation",
                "framework": "arcade",
            },
            "git_signals": {
                "branch": "main",
                "commit": "abc123",
                "staged_files": ["src/simulation.py"],
                "unstaged_files": ["docs/README.md"],
            },
            "change_inventory": ["src/simulation.py", "docs/README.md"],
            "chat_decisions": [
                "Add performance optimization section",
                "Update vehicle physics documentation",
            ],
            "style_guide": {"format": "markdown", "standards": "PDQI-9", "quality_gates": True},
            "constraints": {
                "security": "redact_tokens",
                "performance": "30fps_target",
                "deterministic": True,
            },
            "context": {"project_phase": "development", "focus_area": "performance"},
        }

        return execution_result

    def _load_super_prompt_content(self) -> str:
        """Load super prompt content from file."""
        # This would load from docs/prompts/generate-super.md
        return """
## Role

You are the Enterprise Docs & Rules Maintainer (Super‑Prompt). You keep both documentation pages and Cursor rules accurate, consistent, and AI‑optimized by analyzing repository signals (git diffs: staged/unstaged, recent commits/tags), chat/issue decisions, and style/taxonomy guides. You produce deterministic, idempotent, minimal diffs for documentation and `.cursor/rules/*.mdc`. When inputs are missing, ask targeted questions and use explicit TBD placeholders—never invent facts. Prompts are exempt from the docs→rules link restriction (see Link Policy).

## Modes

- docs: Maintain documentation only (pages, guides, APIs, examples).
- rules: Maintain Cursor rules only (`.cursor/rules/*.mdc` per taxonomy).
- hybrid: When both are impacted, update docs and rules together with shared insights.

## Objectives

- Detect changes and decide per topic: Add/Update/Remove/Consolidate/Split (rules only).
- Produce deterministic, idempotent edits with stable anchors/frontmatter; safe to re‑run.
- Enforce quality standards (PDQI‑9 for docs; RGS for rules); maximize token efficiency; avoid duplication via consolidation.
- Default to dry‑run: propose plan and diffs; apply only when explicitly authorized.
"""

    def _load_meta_optimizer_content(self) -> str:
        """Load meta-optimizer prompt content from file."""
        # This would load from docs/prompts/generate-meta-optimizer.md
        return """
## Role

You are the Enterprise Docs & Rules Meta‑Optimizer. You design and run a thorough, long‑running optimization loop that (a) improves the prompt(s) used to maintain documentation and rules, and (b) improves the resulting documentation and rules themselves. You leverage full repository context, history, and external research when appropriate. You are deterministic and idempotent, producing minimal diffs when applying changes. Prompts may reference rules and docs; respect project link policies for generated artifacts.

## Purpose

Create and operate a repeatable, high‑reasoning APE workflow that continuously refines both:
- The maintenance prompt(s) themselves (plan/prompt quality), and
- The documentation and rule artifacts produced by those prompts (artifact quality),

by generating multiple candidates, running in‑memory dry‑runs, scoring with defined rubrics, stability‑testing, and selecting winners. Always compare "Update/Consolidate from existing" vs "Full Re‑generation from scratch" and choose the better outcome per target.
"""

    def _generate_test_inputs(self, mode: PromptMode) -> list:
        """Generate test inputs for evaluation."""
        # This would generate realistic test scenarios
        return [
            {
                "mode": mode.value,
                "repo_metadata": {"name": "traffic-simulator", "type": "simulation"},
                "git_signals": {"branch": "main", "commit": "abc123"},
                "change_inventory": ["src/simulation.py", "docs/README.md"],
                "chat_decisions": ["Add performance optimization", "Update documentation"],
                "style_guide": {"format": "markdown", "standards": "PDQI-9"},
                "constraints": {"security": "redact_tokens", "performance": "30fps_target"},
            }
        ]


def main():
    """Run migration example."""
    # Initialize migration
    migration = PromptMigrationExample(Path("runs/prompts"))

    # Migrate prompts
    print("Migrating super prompt...")
    super_prompt_id = migration.migrate_super_prompt()
    print(f"Super prompt migrated: {super_prompt_id}")

    print("Migrating meta-optimizer prompt...")
    meta_optimizer_id = migration.migrate_meta_optimizer_prompt()
    print(f"Meta-optimizer prompt migrated: {meta_optimizer_id}")

    # Run initial optimization
    print("Running initial optimization...")
    optimization_results = migration.run_initial_optimization()
    print(f"Optimization results: {json.dumps(optimization_results, indent=2)}")

    # Demonstrate self-improvement
    print("Demonstrating self-improvement...")
    improvement_demo = migration.demonstrate_self_improvement()
    print(f"Self-improvement demo: {json.dumps(improvement_demo, indent=2)}")

    # Demonstrate structured execution
    print("Demonstrating structured execution...")
    execution_demo = migration.demonstrate_structured_execution()
    print(f"Structured execution demo: {json.dumps(execution_demo, indent=2)}")


if __name__ == "__main__":
    main()
