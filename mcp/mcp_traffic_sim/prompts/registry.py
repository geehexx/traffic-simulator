"""Prompt registry and versioning system."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .schemas import (
    PromptCandidate,
    PromptMode,
    PromptRegistry,
)


class PromptRegistryManager:
    """Manages prompt registry with versioning and optimization."""

    def __init__(self, registry_path: Path):
        """Initialize registry manager."""
        self.registry_path = registry_path
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.registry_file = registry_path / "prompt_registry.json"
        self.backup_dir = registry_path / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        # Load existing registry or create new
        self.registry = self._load_registry()

    def _load_registry(self) -> PromptRegistry:
        """Load registry from file or create new."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return PromptRegistry(**data)
            except Exception as e:
                print(f"Warning: Failed to load registry: {e}")

        return PromptRegistry()

    def _save_registry(self) -> None:
        """Save registry to file with backup."""
        # Create backup
        if self.registry_file.exists():
            backup_file = self.backup_dir / f"registry_backup_{datetime.utcnow().isoformat()}.json"
            self.registry_file.rename(backup_file)

        # Save new registry
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(self.registry.model_dump(), f, indent=2, default=str)

    def register_prompt(
        self,
        content: str,
        mode: PromptMode,
        parameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Register a new prompt and return its ID."""
        prompt_id = str(uuid.uuid4())

        candidate = PromptCandidate(
            id=prompt_id, content=content, parameters=parameters or {}, metadata=metadata or {}
        )

        self.registry.prompts[prompt_id] = candidate
        self.registry.active_prompts[mode] = prompt_id

        # Add to version history
        self.registry.version_history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "action": "register",
                "prompt_id": prompt_id,
                "mode": mode.value,
                "metadata": metadata or {},
            }
        )

        self._save_registry()
        return prompt_id

    def get_prompt(self, prompt_id: str) -> Optional[PromptCandidate]:
        """Get prompt by ID."""
        return self.registry.prompts.get(prompt_id)

    def get_active_prompt(self, mode: PromptMode) -> Optional[PromptCandidate]:
        """Get active prompt for mode."""
        active_id = self.registry.active_prompts.get(mode)
        if active_id:
            return self.registry.prompts.get(active_id)
        return None

    def set_active_prompt(self, mode: PromptMode, prompt_id: str) -> bool:
        """Set active prompt for mode."""
        if prompt_id not in self.registry.prompts:
            return False

        self.registry.active_prompts[mode] = prompt_id

        # Add to version history
        self.registry.version_history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "action": "activate",
                "prompt_id": prompt_id,
                "mode": mode.value,
            }
        )

        self._save_registry()
        return True

    def update_prompt(
        self,
        prompt_id: str,
        content: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Update existing prompt."""
        if prompt_id not in self.registry.prompts:
            return False

        prompt = self.registry.prompts[prompt_id]

        if content is not None:
            prompt.content = content
        if parameters is not None:
            prompt.parameters.update(parameters)
        if metadata is not None:
            prompt.metadata.update(metadata)

        prompt.created_at = datetime.utcnow()

        # Add to version history
        self.registry.version_history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "action": "update",
                "prompt_id": prompt_id,
                "changes": {
                    "content_updated": content is not None,
                    "parameters_updated": parameters is not None,
                    "metadata_updated": metadata is not None,
                },
            }
        )

        self._save_registry()
        return True

    def list_prompts(self, mode: Optional[PromptMode] = None) -> List[PromptCandidate]:
        """List prompts, optionally filtered by mode."""
        prompts = list(self.registry.prompts.values())

        if mode:
            # Filter by mode (would need to track mode in metadata)
            prompts = [p for p in prompts if p.metadata.get("mode") == mode.value]

        return sorted(prompts, key=lambda p: p.created_at, reverse=True)

    def get_version_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get version history with limit."""
        return self.registry.version_history[-limit:]

    def export_prompt(self, prompt_id: str, export_path: Path) -> bool:
        """Export prompt to file."""
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            return False

        export_data = {
            "prompt": prompt.model_dump(),
            "exported_at": datetime.utcnow().isoformat(),
            "registry_version": len(self.registry.version_history),
        }

        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, default=str)

        return True

    def import_prompt(self, import_path: Path) -> Optional[str]:
        """Import prompt from file."""
        try:
            with open(import_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            prompt_data = data["prompt"]
            prompt_id = str(uuid.uuid4())  # Generate new ID

            candidate = PromptCandidate(
                id=prompt_id,
                content=prompt_data["content"],
                parameters=prompt_data.get("parameters", {}),
                metadata=prompt_data.get("metadata", {}),
            )

            self.registry.prompts[prompt_id] = candidate

            # Add to version history
            self.registry.version_history.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "action": "import",
                    "prompt_id": prompt_id,
                    "import_source": str(import_path),
                }
            )

            self._save_registry()
            return prompt_id

        except Exception as e:
            print(f"Failed to import prompt: {e}")
            return None

    def cleanup_old_backups(self, keep_days: int = 30) -> int:
        """Clean up old backup files."""
        cutoff_date = datetime.utcnow().timestamp() - (keep_days * 24 * 60 * 60)
        removed_count = 0

        for backup_file in self.backup_dir.glob("*.json"):
            if backup_file.stat().st_mtime < cutoff_date:
                backup_file.unlink()
                removed_count += 1

        return removed_count

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "total_prompts": len(self.registry.prompts),
            "active_prompts": len(self.registry.active_prompts),
            "version_history_entries": len(self.registry.version_history),
            "backup_files": len(list(self.backup_dir.glob("*.json"))),
            "registry_size_mb": self.registry_file.stat().st_size / (1024 * 1024)
            if self.registry_file.exists()
            else 0,
        }
