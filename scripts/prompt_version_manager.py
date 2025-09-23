#!/usr/bin/env python3
"""
Simplified Prompt Version Manager
Demonstrates deterministic naming and simplified manifest structure.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class PromptVersionManager:
    """Simplified prompt version manager with deterministic naming."""

    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.manifest_path = self.prompts_dir / "manifest.json"

    def get_prompt_id(self, main_prompt_id: str, version: str) -> str:
        """Generate deterministic prompt ID: {main_prompt_id}_v{version}"""
        return f"{main_prompt_id}_v{version.replace('.', '_')}"

    def get_filename(self, main_prompt_id: str, version: str) -> str:
        """Generate deterministic filename: {main_prompt_id}_v{version}.json"""
        return f"{main_prompt_id}_v{version.replace('.', '_')}.json"

    def load_manifest(self) -> Dict[str, Any]:
        """Load manifest.json"""
        if not self.manifest_path.exists():
            return {"manifest_version": "2.0.0", "prompts": {}}

        with open(self.manifest_path, "r") as f:
            return json.load(f)

    def save_manifest(self, manifest: Dict[str, Any]) -> None:
        """Save manifest.json"""
        with open(self.manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

    def get_current_version(self, main_prompt_id: str) -> Optional[str]:
        """Get current version for a prompt"""
        manifest = self.load_manifest()
        if main_prompt_id in manifest.get("prompts", {}):
            return manifest["prompts"][main_prompt_id].get("current_version")
        return None

    def list_versions(self, main_prompt_id: str) -> List[Dict[str, Any]]:
        """List all versions for a prompt"""
        manifest = self.load_manifest()
        if main_prompt_id not in manifest.get("prompts", {}):
            return []

        prompt_data = manifest["prompts"][main_prompt_id]
        versions = []

        for version, data in prompt_data.get("versions", {}).items():
            prompt_id = self.get_prompt_id(main_prompt_id, version)
            filename = self.get_filename(main_prompt_id, version)
            file_path = self.prompts_dir / filename

            versions.append(
                {
                    "version": version,
                    "prompt_id": prompt_id,
                    "filename": filename,
                    "status": data.get("status", "unknown"),
                    "exists": file_path.exists(),
                    "performance": data.get("performance", {}),
                    "tags": data.get("tags", []),
                }
            )

        return versions

    def create_version(
        self, main_prompt_id: str, version: str, prompt_data: Dict[str, Any]
    ) -> bool:
        """Create a new version of a prompt"""
        # Generate deterministic filename
        filename = self.get_filename(main_prompt_id, version)
        file_path = self.prompts_dir / filename

        # Save prompt file (without prompt_id - derived from filename)
        prompt_content = {k: v for k, v in prompt_data.items() if k != "prompt_id"}
        with open(file_path, "w") as f:
            json.dump(prompt_content, f, indent=2)

        # Update manifest
        manifest = self.load_manifest()
        if main_prompt_id not in manifest["prompts"]:
            manifest["prompts"][main_prompt_id] = {
                "name": prompt_data.get("name", ""),
                "description": prompt_data.get("description", ""),
                "current_version": version,
                "versions": {},
            }

        # Add version to manifest
        manifest["prompts"][main_prompt_id]["versions"][version] = {
            "status": "active",
            "performance": prompt_data.get("performance", {}),
            "tags": prompt_data.get("tags", []),
        }

        # Update current version
        manifest["prompts"][main_prompt_id]["current_version"] = version

        self.save_manifest(manifest)
        return True

    def deploy_version(self, main_prompt_id: str, version: str) -> bool:
        """Deploy a specific version as the main version"""
        manifest = self.load_manifest()
        if main_prompt_id not in manifest["prompts"]:
            return False

        if version not in manifest["prompts"][main_prompt_id]["versions"]:
            return False

        # Set previous version as backup
        current_version = manifest["prompts"][main_prompt_id]["current_version"]
        if current_version and current_version != version:
            manifest["prompts"][main_prompt_id]["versions"][current_version]["status"] = "backup"

        # Deploy new version
        manifest["prompts"][main_prompt_id]["current_version"] = version
        manifest["prompts"][main_prompt_id]["versions"][version]["status"] = "active"

        # Add to deployment history
        if "deployment_history" not in manifest["prompts"][main_prompt_id]:
            manifest["prompts"][main_prompt_id]["deployment_history"] = []

        manifest["prompts"][main_prompt_id]["deployment_history"].append(
            {"version": version, "deployed_at": "2025-10-02T03:35:00Z"}
        )

        self.save_manifest(manifest)
        return True

    def get_active_prompt_id(self, main_prompt_id: str) -> Optional[str]:
        """Get the active prompt ID for a main prompt"""
        current_version = self.get_current_version(main_prompt_id)
        if current_version:
            return self.get_prompt_id(main_prompt_id, current_version)
        return None


def main():
    """Demonstrate the simplified version management system"""
    manager = PromptVersionManager()

    print("🔧 Simplified Prompt Version Manager")
    print("=" * 50)

    # List current versions
    print("\n📋 Current Versions for 'generate_docs':")
    versions = manager.list_versions("generate_docs")
    for version_info in versions:
        status_emoji = (
            "🟢"
            if version_info["status"] == "active"
            else "🔵"
            if version_info["status"] == "backup"
            else "⚪"
        )
        print(
            f"  {status_emoji} {version_info['version']} - {version_info['status']} - {version_info['filename']}"
        )

    # Show deterministic naming
    print("\n🏷️  Deterministic Naming Convention:")
    print("  Main Prompt ID: generate_docs")
    print("  Version: 2.2.0")
    print(f"  Generated Prompt ID: {manager.get_prompt_id('generate_docs', '2.2.0')}")
    print(f"  Generated Filename: {manager.get_filename('generate_docs', '2.2.0')}")

    # Show current active prompt
    active_id = manager.get_active_prompt_id("generate_docs")
    print(f"\n🎯 Active Prompt ID: {active_id}")

    print("\n✅ Simplified System Benefits:")
    print("  • No redundant prompt_id in JSON files")
    print("  • Deterministic naming from filename")
    print("  • Simplified manifest structure")
    print("  • Automatic version derivation")
    print("  • Cleaner file organization")


if __name__ == "__main__":
    main()
