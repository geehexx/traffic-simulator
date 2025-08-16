"""Training and validation dataset management for prompt optimization."""

from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .schemas import PromptInput, PromptOutput, PromptMode


class DatasetManager:
    """Manages training and validation datasets for prompt optimization."""

    def __init__(self, dataset_path: Path):
        """Initialize dataset manager."""
        self.dataset_path = dataset_path
        self.dataset_path.mkdir(parents=True, exist_ok=True)
        self.training_file = dataset_path / "training_data.jsonl"
        self.validation_file = dataset_path / "validation_data.jsonl"
        self.test_file = dataset_path / "test_data.jsonl"

    def create_dataset(
        self,
        examples: List[Tuple[PromptInput, PromptOutput]],
        train_ratio: float = 0.8,
        validation_ratio: float = 0.1,
        test_ratio: float = 0.1,
        random_seed: int = 42,
    ) -> Dict[str, int]:
        """Create training, validation, and test datasets."""

        # Validate ratios
        if abs(train_ratio + validation_ratio + test_ratio - 1.0) > 1e-6:
            raise ValueError("Ratios must sum to 1.0")

        # Shuffle examples
        random.seed(random_seed)
        shuffled_examples = examples.copy()
        random.shuffle(shuffled_examples)

        # Calculate split indices
        total_examples = len(shuffled_examples)
        train_end = int(total_examples * train_ratio)
        validation_end = train_end + int(total_examples * validation_ratio)

        # Split datasets
        train_examples = shuffled_examples[:train_end]
        validation_examples = shuffled_examples[train_end:validation_end]
        test_examples = shuffled_examples[validation_end:]

        # Save datasets
        self._save_dataset(train_examples, self.training_file)
        self._save_dataset(validation_examples, self.validation_file)
        self._save_dataset(test_examples, self.test_file)

        return {
            "training": len(train_examples),
            "validation": len(validation_examples),
            "test": len(test_examples),
            "total": total_examples,
        }

    def load_training_data(self) -> List[Tuple[PromptInput, PromptOutput]]:
        """Load training dataset."""
        return self._load_dataset(self.training_file)

    def load_validation_data(self) -> List[Tuple[PromptInput, PromptOutput]]:
        """Load validation dataset."""
        return self._load_dataset(self.validation_file)

    def load_test_data(self) -> List[Tuple[PromptInput, PromptOutput]]:
        """Load test dataset."""
        return self._load_dataset(self.test_file)

    def add_examples(
        self,
        examples: List[Tuple[PromptInput, PromptOutput]],
        dataset_type: str = "training",
    ) -> int:
        """Add new examples to dataset."""

        if dataset_type == "training":
            file_path = self.training_file
        elif dataset_type == "validation":
            file_path = self.validation_file
        elif dataset_type == "test":
            file_path = self.test_file
        else:
            raise ValueError(f"Unknown dataset type: {dataset_type}")

        # Load existing examples
        existing_examples = self._load_dataset(file_path)

        # Add new examples
        all_examples = existing_examples + examples

        # Save updated dataset
        self._save_dataset(all_examples, file_path)

        return len(examples)

    def get_dataset_stats(self) -> Dict[str, Any]:
        """Get dataset statistics."""
        training_data = self.load_training_data()
        validation_data = self.load_validation_data()
        test_data = self.load_test_data()

        # Calculate mode distribution
        mode_distribution = {}
        for dataset_name, dataset in [
            ("training", training_data),
            ("validation", validation_data),
            ("test", test_data),
        ]:
            mode_counts: Dict[str, int] = {}
            for input_data, _ in dataset:
                mode = input_data.mode.value
                mode_counts[mode] = mode_counts.get(mode, 0) + 1
            mode_distribution[dataset_name] = mode_counts

        return {
            "training_size": len(training_data),
            "validation_size": len(validation_data),
            "test_size": len(test_data),
            "total_size": len(training_data) + len(validation_data) + len(test_data),
            "mode_distribution": mode_distribution,
            "dataset_files": {
                "training": str(self.training_file),
                "validation": str(self.validation_file),
                "test": str(self.test_file),
            },
        }

    def _save_dataset(
        self,
        examples: List[Tuple[PromptInput, PromptOutput]],
        file_path: Path,
    ) -> None:
        """Save dataset to file."""
        with open(file_path, "w", encoding="utf-8") as f:
            for input_data, output in examples:
                example_data = {
                    "input": input_data.model_dump(),
                    "output": output.model_dump(),
                    "timestamp": datetime.utcnow().isoformat(),
                }
                f.write(json.dumps(example_data, default=str) + "\n")

    def _load_dataset(self, file_path: Path) -> List[Tuple[PromptInput, PromptOutput]]:
        """Load dataset from file."""
        examples: List[Tuple[PromptInput, PromptOutput]] = []

        if not file_path.exists():
            return examples

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        example_data = json.loads(line.strip())
                        input_data = PromptInput(**example_data["input"])
                        output = PromptOutput(**example_data["output"])
                        examples.append((input_data, output))
                    except Exception as e:
                        print(f"Warning: Failed to load example: {e}")
                        continue

        return examples


class ExampleGenerator:
    """Generates training examples for prompt optimization."""

    def __init__(self):
        """Initialize example generator."""
        self.example_templates = self._load_example_templates()

    def generate_examples(
        self,
        mode: PromptMode,
        num_examples: int = 100,
        variety_level: str = "medium",
    ) -> List[Tuple[PromptInput, PromptOutput]]:
        """Generate training examples for a specific mode."""

        examples: List[Tuple[PromptInput, PromptOutput]] = []

        for i in range(num_examples):
            # Generate input
            input_data = self._generate_input_example(mode, variety_level)

            # Generate corresponding output
            output = self._generate_output_example(input_data, mode)

            examples.append((input_data, output))

        return examples

    def _generate_input_example(
        self,
        mode: PromptMode,
        variety_level: str,
    ) -> PromptInput:
        """Generate input example."""

        # Repository metadata variations
        repo_metadata = self._generate_repo_metadata(variety_level)

        # Git signals variations
        git_signals = self._generate_git_signals(variety_level)

        # Change inventory variations
        change_inventory = self._generate_change_inventory(mode, variety_level)

        # Chat decisions variations
        chat_decisions = self._generate_chat_decisions(mode, variety_level)

        # Style guide variations
        style_guide = self._generate_style_guide(mode, variety_level)

        # Constraints variations
        constraints = self._generate_constraints(variety_level)

        # Context variations
        context = self._generate_context(mode, variety_level)

        return PromptInput(
            mode=mode,
            repo_metadata=repo_metadata,
            git_signals=git_signals,
            change_inventory=change_inventory,
            chat_decisions=chat_decisions,
            style_guide=style_guide,
            constraints=constraints,
            context=context,
        )

    def _generate_output_example(
        self,
        input_data: PromptInput,
        mode: PromptMode,
    ) -> PromptOutput:
        """Generate output example."""

        # Generate artifacts based on mode
        artifacts = self._generate_artifacts(input_data, mode)

        # Generate diffs
        diffs = self._generate_diffs(input_data, mode)

        # Generate coverage decisions
        coverage_decisions = self._generate_coverage_decisions(input_data, mode)

        # Generate consolidation map
        consolidation_map = self._generate_consolidation_map(input_data, mode)

        # Generate questions
        questions = self._generate_questions(input_data, mode)

        # Generate commit message
        commit_message = self._generate_commit_message(input_data, mode)

        return PromptOutput(
            success=True,
            mode=mode,
            artifacts=artifacts,
            diffs=diffs,
            coverage_decisions=coverage_decisions,
            consolidation_map=consolidation_map,
            questions=questions,
            commit_message=commit_message,
        )

    def _generate_repo_metadata(self, variety_level: str) -> Dict[str, Any]:
        """Generate repository metadata."""
        base_metadata = {
            "name": "traffic-simulator",
            "type": "simulation",
            "framework": "arcade",
        }

        if variety_level == "high":
            base_metadata.update(
                {
                    "version": "1.2.3",
                    "language": "python",
                    "license": "MIT",
                    "description": "2D traffic simulation with realistic vehicle behavior",
                }
            )

        return base_metadata

    def _generate_git_signals(self, variety_level: str) -> Dict[str, Any]:
        """Generate git signals."""
        branches = ["main", "feature/new-physics", "fix/collision-detection", "docs/update"]
        commits = ["abc123", "def456", "ghi789", "jkl012"]

        return {
            "branch": random.choice(branches),
            "commit": random.choice(commits),
            "staged_files": random.sample(
                ["src/simulation.py", "src/vehicle.py", "tests/test_simulation.py"],
                random.randint(0, 2),
            ),
            "unstaged_files": random.sample(
                ["docs/README.md", "config/simulation.yaml"], random.randint(0, 2)
            ),
        }

    def _generate_change_inventory(
        self,
        mode: PromptMode,
        variety_level: str,
    ) -> List[str]:
        """Generate change inventory."""

        if mode == PromptMode.DOCS:
            return random.sample(
                [
                    "docs/README.md",
                    "docs/ARCHITECTURE.md",
                    "docs/PERFORMANCE_GUIDE.md",
                    "docs/QUALITY_STANDARDS.md",
                ],
                random.randint(1, 3),
            )
        elif mode == PromptMode.RULES:
            return random.sample(
                [
                    ".cursor/rules/simulation-patterns.mdc",
                    ".cursor/rules/vehicle-physics-patterns.mdc",
                    ".cursor/rules/performance-optimization.mdc",
                ],
                random.randint(1, 2),
            )
        else:  # HYBRID
            return random.sample(
                [
                    "docs/README.md",
                    ".cursor/rules/simulation-patterns.mdc",
                    "src/simulation.py",
                    "tests/test_simulation.py",
                ],
                random.randint(2, 4),
            )

    def _generate_chat_decisions(
        self,
        mode: PromptMode,
        variety_level: str,
    ) -> List[str]:
        """Generate chat decisions."""

        if mode == PromptMode.DOCS:
            decisions = [
                "Add performance optimization section",
                "Update vehicle physics documentation",
                "Improve code examples",
                "Add troubleshooting guide",
            ]
        elif mode == PromptMode.RULES:
            decisions = [
                "Update simulation patterns",
                "Add new physics constraints",
                "Improve code quality rules",
                "Add performance guidelines",
            ]
        else:  # HYBRID
            decisions = [
                "Update both docs and rules",
                "Add comprehensive examples",
                "Improve cross-references",
                "Update quality standards",
            ]

        return random.sample(decisions, random.randint(1, 3))

    def _generate_style_guide(
        self,
        mode: PromptMode,
        variety_level: str,
    ) -> Dict[str, Any]:
        """Generate style guide."""

        if mode == PromptMode.DOCS:
            return {
                "format": "markdown",
                "standards": "PDQI-9",
                "quality_gates": True,
                "examples": "comprehensive",
            }
        elif mode == PromptMode.RULES:
            return {
                "format": "markdown",
                "standards": "RGS",
                "quality_gates": True,
                "examples": "minimal",
            }
        else:  # HYBRID
            return {
                "format": "markdown",
                "standards": "PDQI-9+RGS",
                "quality_gates": True,
                "examples": "balanced",
            }

    def _generate_constraints(self, variety_level: str) -> Dict[str, Any]:
        """Generate constraints."""
        constraints = {
            "security": "redact_tokens",
            "performance": "30fps_target",
            "deterministic": True,
        }

        if variety_level == "high":
            constraints.update(
                {
                    "memory_limit": "512MB",
                    "timeout": "300s",
                    "quality_threshold": 0.85,
                }
            )

        return constraints

    def _generate_context(
        self,
        mode: PromptMode,
        variety_level: str,
    ) -> Dict[str, Any]:
        """Generate context."""
        context = {
            "project_phase": random.choice(["development", "testing", "production"]),
            "focus_area": random.choice(["performance", "quality", "maintenance"]),
        }

        if variety_level == "high":
            context.update(
                {
                    "urgency": random.choice(["low", "medium", "high"]),
                    "complexity": random.choice(["simple", "moderate", "complex"]),
                    "stakeholders": random.choice(["developers", "users", "maintainers"]),
                }
            )

        return context

    def _generate_artifacts(
        self,
        input_data: PromptInput,
        mode: PromptMode,
    ) -> List[str]:
        """Generate artifacts."""

        if mode == PromptMode.DOCS:
            return [
                "Updated README.md with new performance section",
                "Added troubleshooting guide",
                "Improved code examples",
            ]
        elif mode == PromptMode.RULES:
            return [
                "Updated simulation-patterns.mdc",
                "Added physics-constraints.mdc",
                "Improved quality-guidelines.mdc",
            ]
        else:  # HYBRID
            return [
                "Updated README.md and simulation-patterns.mdc",
                "Added comprehensive examples",
                "Improved cross-references",
            ]

    def _generate_diffs(
        self,
        input_data: PromptInput,
        mode: PromptMode,
    ) -> Dict[str, str]:
        """Generate diffs."""

        diffs = {}

        for file_path in input_data.change_inventory:
            if file_path.endswith(".md"):
                diffs[file_path] = (
                    f"# Updated {file_path}\n\n+ Added new section\n- Removed outdated content"
                )
            elif file_path.endswith(".mdc"):
                diffs[file_path] = "---\n+ Added new rule\n- Removed deprecated rule"

        return diffs

    def _generate_coverage_decisions(
        self,
        input_data: PromptInput,
        mode: PromptMode,
    ) -> List[Dict[str, Any]]:
        """Generate coverage decisions."""

        decisions = []

        for file_path in input_data.change_inventory:
            decision = {
                "file": file_path,
                "action": random.choice(["add", "update", "remove"]),
                "reason": f"Based on changes in {file_path}",
                "priority": random.choice(["low", "medium", "high"]),
            }
            decisions.append(decision)

        return decisions

    def _generate_consolidation_map(
        self,
        input_data: PromptInput,
        mode: PromptMode,
    ) -> Optional[Dict[str, Any]]:
        """Generate consolidation map."""

        if mode == PromptMode.RULES and len(input_data.change_inventory) > 1:
            return {
                "source_files": input_data.change_inventory,
                "target_file": "consolidated-rules.mdc",
                "consolidation_strategy": "merge_related_rules",
            }

        return None

    def _generate_questions(
        self,
        input_data: PromptInput,
        mode: PromptMode,
    ) -> List[str]:
        """Generate questions."""

        questions = []

        if not input_data.chat_decisions:
            questions.append("What specific changes are needed?")

        if mode == PromptMode.DOCS:
            questions.append("What documentation standards should be followed?")
        elif mode == PromptMode.RULES:
            questions.append("What rule patterns should be applied?")

        return questions

    def _generate_commit_message(
        self,
        input_data: PromptInput,
        mode: PromptMode,
    ) -> str:
        """Generate commit message."""

        if mode == PromptMode.DOCS:
            return "docs: update documentation with new examples and troubleshooting guide"
        elif mode == PromptMode.RULES:
            return "rules: update simulation patterns and physics constraints"
        else:  # HYBRID
            return "docs: update documentation and rules with comprehensive improvements"

    def _load_example_templates(self) -> Dict[str, Any]:
        """Load example templates."""
        return {
            "repo_metadata_templates": [
                {"name": "traffic-simulator", "type": "simulation"},
                {"name": "physics-engine", "type": "library"},
                {"name": "rendering-system", "type": "component"},
            ],
            "git_signals_templates": [
                {"branch": "main", "commit": "abc123"},
                {"branch": "feature/new-physics", "commit": "def456"},
                {"branch": "fix/collision", "commit": "ghi789"},
            ],
            "change_inventory_templates": {
                "docs": ["docs/README.md", "docs/ARCHITECTURE.md"],
                "rules": [".cursor/rules/simulation-patterns.mdc"],
                "hybrid": ["docs/README.md", ".cursor/rules/simulation-patterns.mdc"],
            },
        }
