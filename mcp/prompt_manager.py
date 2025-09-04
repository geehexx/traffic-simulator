#!/usr/bin/env python3
"""Simple prompt manager with git-based version control."""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class PromptManager:
    """Simple prompt manager with git-based version control."""

    def __init__(self, prompts_dir: str = "prompts"):
        """Initialize prompt manager."""
        self.prompts_dir = Path(prompts_dir)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)

    def git_commit(self, message: str) -> bool:
        """Commit changes to git with a message."""
        try:
            # Add all changes
            subprocess.run(["git", "add", "."], check=True, cwd=self.prompts_dir)

            # Commit with message
            subprocess.run(["git", "commit", "-m", message], check=True, cwd=self.prompts_dir)

            print(f"✅ Committed: {message}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Git commit failed: {e}")
            return False

    def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Get a prompt by ID."""
        prompt_file = self.prompts_dir / f"{prompt_id}.json"
        if not prompt_file.exists():
            return None

        with open(prompt_file, "r") as f:
            return json.load(f)

    def save_prompt(self, prompt_data: Dict[str, Any], commit: bool = True) -> bool:
        """Save a prompt and optionally commit to git."""
        prompt_id = prompt_data["prompt_id"]
        prompt_file = self.prompts_dir / f"{prompt_id}.json"

        # Update version and timestamp
        if "version" in prompt_data:
            # Increment version
            version_parts = prompt_data["version"].split(".")
            version_parts[-1] = str(int(version_parts[-1]) + 1)
            prompt_data["version"] = ".".join(version_parts)
        else:
            prompt_data["version"] = "1.0.0"

        prompt_data["last_modified"] = datetime.now().isoformat()

        # Save to file
        with open(prompt_file, "w") as f:
            json.dump(prompt_data, f, indent=2)

        print(f"✅ Saved prompt: {prompt_id} (v{prompt_data['version']})")

        # Commit to git if requested
        if commit:
            message = f"Update prompt {prompt_id} to v{prompt_data['version']}"
            return self.git_commit(message)

        return True

    def optimize_prompt(self, prompt_id: str, optimization_data: Dict[str, Any]) -> bool:
        """Optimize a prompt with new data."""
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            print(f"❌ Prompt not found: {prompt_id}")
            return False

        # Apply optimization
        if "template" in optimization_data:
            prompt["template"] = optimization_data["template"]

        if "metadata" not in prompt:
            prompt["metadata"] = {}

        prompt["metadata"]["optimization_history"] = prompt["metadata"].get(
            "optimization_history", []
        )
        prompt["metadata"]["optimization_history"].append(
            {"timestamp": datetime.now().isoformat(), "optimization_data": optimization_data}
        )

        # Save optimized prompt
        return self.save_prompt(prompt)

    def list_prompts(self) -> List[Dict[str, Any]]:
        """List all prompts."""
        prompts = []
        for prompt_file in self.prompts_dir.glob("*.json"):
            if prompt_file.name == "index.json":
                continue

            with open(prompt_file, "r") as f:
                prompt_data = json.load(f)
                prompts.append(
                    {
                        "prompt_id": prompt_data["prompt_id"],
                        "name": prompt_data["name"],
                        "version": prompt_data.get("version", "1.0.0"),
                        "active": prompt_data.get("active", True),
                        "last_modified": prompt_data.get("last_modified", "unknown"),
                    }
                )

        return sorted(prompts, key=lambda x: x["prompt_id"])

    def execute_prompt(self, prompt_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a prompt with input data."""
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            return {"error": f"Prompt not found: {prompt_id}"}

        # This is a placeholder - in a real implementation, this would
        # call the actual LLM with the prompt template and input data
        template = prompt["template"]

        # Simple template substitution
        for key, value in input_data.items():
            template = template.replace(f"{{{key}}}", str(value))

        return {
            "prompt_id": prompt_id,
            "template": template,
            "input_data": input_data,
            "execution_timestamp": datetime.now().isoformat(),
        }


def main():
    """Test the prompt manager."""
    manager = PromptManager()

    print("📋 Available prompts:")
    for prompt in manager.list_prompts():
        print(f"  - {prompt['prompt_id']}: {prompt['name']} (v{prompt['version']})")

    # Test document generation prompt
    print("\n🧪 Testing document generation prompt...")
    result = manager.execute_prompt(
        "generate_docs",
        {
            "code_changes": "Added new MCP server optimization features",
            "context": "This is a test of the migrated prompt system",
        },
    )

    print("✅ Prompt execution result:")
    print(f"Template: {result['template'][:100]}...")


if __name__ == "__main__":
    main()
