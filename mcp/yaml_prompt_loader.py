#!/usr/bin/env python3
"""
YAML Prompt Loader for MCP Traffic Simulator
Handles loading YAML prompt files with front matter and converts them to JSON format internally.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Tuple


class YAMLPromptLoader:
    """Loads YAML prompt files with front matter and converts to JSON format."""

    def __init__(self, prompts_dir: Path):
        self.prompts_dir = prompts_dir

    def parse_yaml_with_front_matter(self, content: str) -> Tuple[Dict[str, Any], str]:
        """Parse YAML content with front matter, returning metadata and template."""
        # Split content by front matter delimiters
        parts = content.split("---", 2)

        if len(parts) < 3:
            # No front matter, treat entire content as template
            return {}, content.strip()

        # Parse front matter (between first two ---)
        front_matter_content = parts[1].strip()
        template_content = parts[2].strip()

        try:
            front_matter = yaml.safe_load(front_matter_content) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML front matter: {e}")

        return front_matter, template_content

    def load_prompt(self, prompt_id: str) -> Dict[str, Any]:
        """Load a prompt from YAML file and convert to JSON format."""
        # Try YAML file first
        yaml_file = self.prompts_dir / f"{prompt_id}.yaml"
        json_file = self.prompts_dir / f"{prompt_id}.json"

        if yaml_file.exists():
            return self._load_yaml_prompt(yaml_file)
        elif json_file.exists():
            return self._load_json_prompt(json_file)
        else:
            raise FileNotFoundError(f"Prompt not found: {prompt_id}")

    def _load_yaml_prompt(self, yaml_file: Path) -> Dict[str, Any]:
        """Load prompt from YAML file."""
        with open(yaml_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse front matter and template
        front_matter, template = self.parse_yaml_with_front_matter(content)

        # Combine front matter and template into JSON structure
        prompt_data = front_matter.copy()
        prompt_data["template"] = template

        return prompt_data

    def _load_json_prompt(self, json_file: Path) -> Dict[str, Any]:
        """Load prompt from JSON file (fallback)."""
        with open(json_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_prompts(self) -> list:
        """List all available prompts (both YAML and JSON)."""
        prompts = []

        # Find all YAML files
        for yaml_file in self.prompts_dir.glob("*.yaml"):
            if yaml_file.name != "manifest.yaml":  # Skip manifest
                prompt_id = yaml_file.stem
                try:
                    prompt_data = self.load_prompt(prompt_id)
                    prompts.append(
                        {
                            "prompt_id": prompt_id,
                            "name": prompt_data.get("name", prompt_id),
                            "description": prompt_data.get("description", ""),
                            "version": prompt_data.get("version", "1.0.0"),
                            "active": prompt_data.get("active", True),
                            "tags": prompt_data.get("tags", []),
                            "file_type": "yaml",
                        }
                    )
                except Exception as e:
                    print(f"Warning: Could not load prompt {prompt_id}: {e}")

        # Find all JSON files (for backward compatibility)
        for json_file in self.prompts_dir.glob("*.json"):
            if json_file.name != "manifest.json":  # Skip manifest
                prompt_id = json_file.stem
                # Skip if we already have a YAML version
                if not (self.prompts_dir / f"{prompt_id}.yaml").exists():
                    try:
                        prompt_data = self._load_json_prompt(json_file)
                        prompts.append(
                            {
                                "prompt_id": prompt_id,
                                "name": prompt_data.get("name", prompt_id),
                                "description": prompt_data.get("description", ""),
                                "version": prompt_data.get("version", "1.0.0"),
                                "active": prompt_data.get("active", True),
                                "tags": prompt_data.get("tags", []),
                                "file_type": "json",
                            }
                        )
                    except Exception as e:
                        print(f"Warning: Could not load prompt {prompt_id}: {e}")

        return prompts

    def save_prompt_as_yaml(self, prompt_id: str, prompt_data: Dict[str, Any]) -> None:
        """Save a prompt as YAML with front matter."""
        yaml_file = self.prompts_dir / f"{prompt_id}.yaml"

        # Extract template
        template = prompt_data.pop("template", "")

        # Create YAML content with front matter
        yaml_content = []
        yaml_content.append("---")
        yaml_content.append(yaml.dump(prompt_data, default_flow_style=False, sort_keys=False))
        yaml_content.append("---")
        yaml_content.append("")
        if template:
            yaml_content.append(template)

        # Write file
        with open(yaml_file, "w", encoding="utf-8") as f:
            f.write("\n".join(yaml_content))

    def convert_json_to_yaml(self, json_file: Path) -> Path:
        """Convert a JSON prompt file to YAML format."""
        yaml_file = json_file.with_suffix(".yaml")

        # Load JSON data
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Save as YAML
        self.save_prompt_as_yaml(json_file.stem, data)

        return yaml_file
