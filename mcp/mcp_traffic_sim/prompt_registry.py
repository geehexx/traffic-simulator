"""DSPy-based prompt registry system."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from dspy_modules import DSPyPromptRegistry


class PromptConfig(BaseModel):
    """Configuration for a registered prompt."""

    prompt_id: str
    name: str
    description: str
    template: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    version: str = "1.0.0"
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    active: bool = True


class PromptExecutionResult(BaseModel):
    """Result of prompt execution."""

    prompt_id: str
    output: Any
    execution_time: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PromptRegistry:
    """DSPy-based registry for managing prompts."""

    def __init__(self, registry_path: Path):
        """Initialize DSPy prompt registry."""
        self.registry_path = registry_path
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.dspy_registry = DSPyPromptRegistry()
        self.prompts: Dict[str, PromptConfig] = {}
        self._load_registry()

    def _load_registry(self) -> None:
        """Load prompts from registry file."""
        registry_file = self.registry_path / "prompts.json"
        if registry_file.exists():
            try:
                with open(registry_file, "r") as f:
                    data = json.load(f)
                    for prompt_data in data.get("prompts", []):
                        prompt = PromptConfig(**prompt_data)
                        self.prompts[prompt.prompt_id] = prompt
            except Exception as e:
                print(f"Warning: Could not load registry: {e}")

    def _save_registry(self) -> None:
        """Save prompts to registry file."""
        registry_file = self.registry_path / "prompts.json"
        data = {"prompts": [prompt.dict() for prompt in self.prompts.values()]}
        with open(registry_file, "w") as f:
            json.dump(data, f, indent=2)

    def register_prompt(self, prompt_config: PromptConfig) -> str:
        """Register a new prompt."""
        self.prompts[prompt_config.prompt_id] = prompt_config
        self._save_registry()
        return prompt_config.prompt_id

    def get_prompt(self, prompt_id: str) -> Optional[PromptConfig]:
        """Get a prompt by ID."""
        return self.prompts.get(prompt_id)

    def list_prompts(self, tags: Optional[List[str]] = None) -> List[PromptConfig]:
        """List prompts, optionally filtered by tags."""
        prompts = list(self.prompts.values())
        if tags:
            prompts = [p for p in prompts if any(tag in p.tags for tag in tags)]
        return prompts

    def execute_prompt(self, prompt_id: str, input_data: Dict[str, Any]) -> PromptExecutionResult:
        """Execute a DSPy prompt with given input data."""
        start_time = time.time()

        try:
            # Map prompt_id to DSPy module
            module_mapping = {
                "generate_docs": "generate_docs",
                "generate_rules": "generate_rules",
                "hybrid_maintenance": "hybrid_maintenance",
                "optimize_prompt": "optimize_prompt",
                "evaluate_performance": "evaluate_performance",
            }

            dspy_module_name = module_mapping.get(prompt_id)
            if not dspy_module_name:
                return PromptExecutionResult(
                    prompt_id=prompt_id,
                    output=None,
                    execution_time=time.time() - start_time,
                    success=False,
                    error_message=f"Prompt '{prompt_id}' not found in DSPy registry",
                )

            # Execute DSPy module
            output = self.dspy_registry.execute_module(dspy_module_name, **input_data)

            return PromptExecutionResult(
                prompt_id=prompt_id,
                output=output,
                execution_time=time.time() - start_time,
                success=True,
                metadata={"dspy_module": dspy_module_name, "execution_type": "dspy_module"},
            )

        except Exception as e:
            return PromptExecutionResult(
                prompt_id=prompt_id,
                output=None,
                execution_time=time.time() - start_time,
                success=False,
                error_message=str(e),
            )
