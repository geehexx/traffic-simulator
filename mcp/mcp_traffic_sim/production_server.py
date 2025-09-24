"""Production-Ready DSPy Optimization MCP Server for Traffic Simulator."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import dspy
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
    ServerCapabilities,
)

# Import our production components
from .config import MCPConfig
from .logging_util import MCPLogger
from .security import SecurityManager
from .production_optimizer import ProductionOptimizer
from .monitoring_system import MonitoringSystem
from .feedback_collector import FeedbackCollector
from .dashboard_generator import DashboardGenerator
from .alerting_system import AlertingSystem
from .advanced_file_manager import AdvancedFileManager

# Configure DSPy with Gemini for production
dspy.configure(lm=dspy.LM("gemini/gemini-2.0-flash"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("traffic-sim-production-optimization")

# Global instances
config = MCPConfig()
logger_util = MCPLogger(config.log_dir)
security = SecurityManager(config)
optimizer = ProductionOptimizer(config, logger_util, security)
monitoring = MonitoringSystem(config, logger_util, security)
feedback_collector = FeedbackCollector(config, logger_util, security)
dashboard_generator = DashboardGenerator(config, logger_util, security)


class SemanticVersion:
    """Semantic versioning helper class."""

    def __init__(self, version: str):
        """Initialize with version string (e.g., '1.2.3')."""
        self.version = version
        self.major, self.minor, self.patch = self._parse_version(version)

    def _parse_version(self, version: str) -> Tuple[int, int, int]:
        """Parse version string into major, minor, patch."""
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version)
        if not match:
            raise ValueError(f"Invalid semantic version: {version}")
        return int(match.group(1)), int(match.group(2)), int(match.group(3))

    def increment_major(self) -> str:
        """Increment major version (breaking changes)."""
        return f"{self.major + 1}.0.0"

    def increment_minor(self) -> str:
        """Increment minor version (new features, backward compatible)."""
        return f"{self.major}.{self.minor + 1}.0"

    def increment_patch(self) -> str:
        """Increment patch version (bug fixes, backward compatible)."""
        return f"{self.major}.{self.minor}.{self.patch + 1}"

    def __str__(self) -> str:
        return self.version


class PromptVersionManager:
    """Prompt version management with semantic versioning."""

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

    def get_latest_version(self, main_prompt_id: str) -> Optional[str]:
        """Get the latest version for a prompt."""
        manifest = self.load_manifest()
        if main_prompt_id not in manifest.get("prompts", {}):
            return None

        versions = list(manifest["prompts"][main_prompt_id]["versions"].keys())
        if not versions:
            return None

        # Sort versions semantically
        semantic_versions = [SemanticVersion(v) for v in versions]
        semantic_versions.sort(key=lambda x: (x.major, x.minor, x.patch))
        return str(semantic_versions[-1])

    def get_next_version(self, main_prompt_id: str, increment_type: str = "minor") -> str:
        """Get the next version for a prompt based on increment type."""
        latest_version = self.get_latest_version(main_prompt_id)
        if not latest_version:
            return "1.0.0"

        current = SemanticVersion(latest_version)

        if increment_type == "major":
            return current.increment_major()
        elif increment_type == "minor":
            return current.increment_minor()
        elif increment_type == "patch":
            return current.increment_patch()
        else:
            raise ValueError(f"Invalid increment type: {increment_type}")

    def create_version(
        self,
        main_prompt_id: str,
        prompt_data: Dict[str, Any],
        version: Optional[str] = None,
        increment_type: str = "minor",
    ) -> str:
        """Create a new version of a prompt with semantic versioning."""
        if version is None:
            version = self.get_next_version(main_prompt_id, increment_type)

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
            "status": "draft",
            "performance": prompt_data.get("performance", {}),
            "tags": prompt_data.get("tags", []),
            "created_at": datetime.now().isoformat(),
        }

        self.save_manifest(manifest)
        return version

    def deploy_version(self, main_prompt_id: str, version: str) -> bool:
        """Deploy a specific version as the main version."""
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
            {"version": version, "deployed_at": datetime.now().isoformat(), "deployed_by": "system"}
        )

        self.save_manifest(manifest)
        return True


# Initialize prompt version manager
prompt_version_manager = PromptVersionManager()
alerting = AlertingSystem(config, logger_util, security)
file_manager = AdvancedFileManager(config, logger_util)


async def remove_prompts_from_system(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Remove one or more prompts from the system by their IDs."""
    from pathlib import Path

    prompt_ids = arguments.get("prompt_ids", [])
    reason = arguments.get("reason", "No reason provided")

    removed_prompts = []
    failed_removals = []

    # Get the prompts directory
    prompts_dir = Path("prompts")
    if not prompts_dir.exists():
        return {
            "success": False,
            "error": "Prompts directory not found",
            "removed_prompts": [],
            "failed_removals": [],
            "total_removed": 0,
        }

    for prompt_id in prompt_ids:
        prompt_file = prompts_dir / f"{prompt_id}.json"

        if prompt_file.exists():
            try:
                # Remove the prompt file
                prompt_file.unlink()
                removed_prompts.append(prompt_id)
                logger_util.info(f"Removed prompt: {prompt_id} (Reason: {reason})")
            except Exception as e:
                failed_removals.append({"prompt_id": prompt_id, "error": str(e)})
                logger_util.error(f"Failed to remove prompt {prompt_id}: {str(e)}")
        else:
            failed_removals.append({"prompt_id": prompt_id, "error": "Prompt file not found"})
            logger_util.warning(f"Prompt file not found: {prompt_id}")

    return {
        "success": len(failed_removals) == 0,
        "removed_prompts": removed_prompts,
        "failed_removals": failed_removals,
        "total_removed": len(removed_prompts),
        "reason": reason,
    }


async def create_prompt_version(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new version of a prompt with semantic versioning."""
    try:
        main_prompt_id = arguments.get("main_prompt_id")
        prompt_data = arguments.get("prompt_data", {})
        increment_type = arguments.get("increment_type", "minor")
        version = arguments.get("version")

        if not main_prompt_id:
            return {"success": False, "error": "main_prompt_id is required"}

        # Create the version
        created_version = prompt_version_manager.create_version(
            main_prompt_id=main_prompt_id,
            prompt_data=prompt_data,
            version=version,
            increment_type=increment_type,
        )

        # Get the generated prompt ID and filename
        prompt_id = prompt_version_manager.get_prompt_id(main_prompt_id, created_version)
        filename = prompt_version_manager.get_filename(main_prompt_id, created_version)

        logger_util.info(f"Created prompt version: {prompt_id} (v{created_version})")

        return {
            "success": True,
            "version": created_version,
            "prompt_id": prompt_id,
            "filename": filename,
            "increment_type": increment_type,
            "status": "draft",
        }

    except Exception as e:
        logger_util.error(f"Failed to create prompt version: {str(e)}")
        return {"success": False, "error": str(e)}


async def deploy_prompt_version(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Deploy a specific version as the main version."""
    try:
        main_prompt_id = arguments.get("main_prompt_id")
        version = arguments.get("version")

        if not main_prompt_id or not version:
            return {"success": False, "error": "main_prompt_id and version are required"}

        # Check if this is a major version increment
        current_version = prompt_version_manager.get_latest_version(main_prompt_id)
        if current_version:
            current = SemanticVersion(current_version)
            new = SemanticVersion(version)

            # If major version increment, this is a breaking change
            if new.major > current.major:
                logger_util.warning(
                    f"Major version increment detected: {current_version} → {version}"
                )

        # Deploy the version
        success = prompt_version_manager.deploy_version(main_prompt_id, version)

        if success:
            prompt_id = prompt_version_manager.get_prompt_id(main_prompt_id, version)
            logger_util.info(f"Deployed prompt version: {prompt_id} (v{version})")

            return {
                "success": True,
                "version": version,
                "prompt_id": prompt_id,
                "status": "active",
                "breaking_change": new.major > current.major if current_version else False,
            }
        else:
            return {"success": False, "error": "Failed to deploy version"}

    except Exception as e:
        logger_util.error(f"Failed to deploy prompt version: {str(e)}")
        return {"success": False, "error": str(e)}


async def list_prompt_versions(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """List all versions for a prompt with semantic versioning."""
    try:
        main_prompt_id = arguments.get("main_prompt_id")

        if not main_prompt_id:
            return {"success": False, "error": "main_prompt_id is required"}

        # Get versions from manifest
        manifest = prompt_version_manager.load_manifest()
        if main_prompt_id not in manifest.get("prompts", {}):
            return {"success": True, "versions": [], "total": 0}

        prompt_data = manifest["prompts"][main_prompt_id]
        versions = []

        for version, data in prompt_data.get("versions", {}).items():
            prompt_id = prompt_version_manager.get_prompt_id(main_prompt_id, version)
            filename = prompt_version_manager.get_filename(main_prompt_id, version)
            file_path = prompt_version_manager.prompts_dir / filename

            versions.append(
                {
                    "version": version,
                    "prompt_id": prompt_id,
                    "filename": filename,
                    "status": data.get("status", "unknown"),
                    "exists": file_path.exists(),
                    "performance": data.get("performance", {}),
                    "tags": data.get("tags", []),
                    "created_at": data.get("created_at", "unknown"),
                }
            )

        # Sort by semantic version
        versions.sort(
            key=lambda x: SemanticVersion(x["version"]).major * 10000
            + SemanticVersion(x["version"]).minor * 100
            + SemanticVersion(x["version"]).patch
        )

        return {
            "success": True,
            "versions": versions,
            "total": len(versions),
            "current_version": prompt_data.get("current_version"),
        }

    except Exception as e:
        logger_util.error(f"Failed to list prompt versions: {str(e)}")
        return {"success": False, "error": str(e)}


async def get_next_version(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get the next version for a prompt based on increment type."""
    try:
        main_prompt_id = arguments.get("main_prompt_id")
        increment_type = arguments.get("increment_type", "minor")

        if not main_prompt_id:
            return {"success": False, "error": "main_prompt_id is required"}

        # Get current version
        current_version = prompt_version_manager.get_latest_version(main_prompt_id)

        # Get next version
        next_version = prompt_version_manager.get_next_version(main_prompt_id, increment_type)

        return {
            "success": True,
            "current_version": current_version,
            "next_version": next_version,
            "increment_type": increment_type,
            "prompt_id": prompt_version_manager.get_prompt_id(main_prompt_id, next_version),
            "filename": prompt_version_manager.get_filename(main_prompt_id, next_version),
        }

    except Exception as e:
        logger_util.error(f"Failed to get next version: {str(e)}")
        return {"success": False, "error": str(e)}


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available production DSPy optimization tools."""
    tools = [
        # Core Optimization Tools
        Tool(
            name="optimize_prompt_production",
            description="Production-grade prompt optimization using DSPy with comprehensive monitoring",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_id": {"type": "string", "description": "ID of the prompt to optimize"},
                    "strategy": {
                        "type": "string",
                        "enum": ["mipro", "bootstrap", "bayesian", "hybrid"],
                        "default": "mipro",
                        "description": "DSPy optimizer strategy",
                    },
                    "training_data": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Training examples for optimization",
                    },
                    "auto_mode": {
                        "type": "string",
                        "enum": ["light", "medium", "heavy"],
                        "default": "medium",
                        "description": "Optimization intensity",
                    },
                    "monitoring_enabled": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable real-time monitoring",
                    },
                },
                "required": ["prompt_id"],
            },
        ),
        # Real-time Feedback Optimization
        Tool(
            name="auto_optimize_with_feedback_production",
            description="Production-grade real-time optimization based on user feedback with monitoring",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_id": {"type": "string", "description": "ID of the prompt to optimize"},
                    "user_feedback": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "original_prompt": {"type": "string"},
                                "feedback": {"type": "string"},
                                "output_quality": {"type": "number", "minimum": 0, "maximum": 1},
                                "user_id": {"type": "string"},
                                "timestamp": {"type": "number"},
                            },
                        },
                        "description": "User feedback data",
                    },
                    "feedback_threshold": {
                        "type": "number",
                        "default": 0.7,
                        "description": "Quality threshold for triggering optimization",
                    },
                    "auto_deploy": {
                        "type": "boolean",
                        "default": True,
                        "description": "Automatically deploy optimized prompts",
                    },
                },
                "required": ["prompt_id"],
            },
        ),
        # Performance Evaluation
        Tool(
            name="evaluate_prompt_performance_production",
            description="Comprehensive performance evaluation with detailed metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_id": {"type": "string", "description": "ID of the prompt to evaluate"},
                    "test_cases": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Test cases for evaluation",
                    },
                    "evaluation_metrics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["quality", "speed", "accuracy", "user_satisfaction"],
                        "description": "Metrics to evaluate",
                    },
                    "baseline_comparison": {
                        "type": "boolean",
                        "default": True,
                        "description": "Compare against baseline performance",
                    },
                },
                "required": ["prompt_id"],
            },
        ),
        # Continuous Improvement
        Tool(
            name="run_continuous_improvement_cycle",
            description="Run automated continuous improvement cycle for all prompts",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific prompts to optimize (optional, optimizes all if not provided)",
                    },
                    "strategies": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["mipro", "bayesian", "hybrid"],
                        "description": "Optimization strategies to use",
                    },
                    "auto_deploy": {
                        "type": "boolean",
                        "default": True,
                        "description": "Automatically deploy improvements",
                    },
                    "monitoring_interval": {
                        "type": "integer",
                        "default": 3600,
                        "description": "Monitoring interval in seconds",
                    },
                },
            },
        ),
        # Monitoring and Analytics
        Tool(
            name="get_performance_dashboard",
            description="Generate comprehensive performance dashboard with real-time metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard_type": {
                        "type": "string",
                        "enum": ["overview", "detailed", "trends", "alerts"],
                        "default": "overview",
                        "description": "Type of dashboard to generate",
                    },
                    "time_range": {
                        "type": "string",
                        "enum": ["1h", "24h", "7d", "30d"],
                        "default": "24h",
                        "description": "Time range for dashboard data",
                    },
                    "include_predictions": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include performance predictions",
                    },
                },
            },
        ),
        Tool(
            name="get_optimization_analytics",
            description="Get detailed analytics on optimization performance and trends",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_id": {
                        "type": "string",
                        "description": "Specific prompt to analyze (optional)",
                    },
                    "metric_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": [
                            "quality",
                            "speed",
                            "user_satisfaction",
                            "optimization_frequency",
                        ],
                        "description": "Types of metrics to analyze",
                    },
                    "include_trends": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include trend analysis",
                    },
                },
            },
        ),
        # Alerting and Notifications
        Tool(
            name="configure_alerting",
            description="Configure alerting rules for optimization system",
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_types": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "threshold": {"type": "number"},
                                "enabled": {"type": "boolean"},
                            },
                        },
                        "description": "Alert configuration",
                    },
                    "notification_channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["dashboard", "logs"],
                        "description": "Notification channels",
                    },
                },
            },
        ),
        # System Management
        Tool(
            name="get_system_status",
            description="Get comprehensive system status and health metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_metrics": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include detailed metrics",
                    },
                    "include_optimization_status": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include optimization status",
                    },
                },
            },
        ),
        Tool(
            name="deploy_optimized_prompts",
            description="Deploy optimized prompts to production with rollback capability",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Prompts to deploy",
                    },
                    "deployment_strategy": {
                        "type": "string",
                        "enum": ["immediate", "gradual", "canary"],
                        "default": "gradual",
                        "description": "Deployment strategy",
                    },
                    "rollback_on_failure": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable automatic rollback on failure",
                    },
                },
            },
        ),
        # Advanced File Management Tools
        Tool(
            name="update_documentation",
            description="Update existing documentation with intelligent merging and DSPy optimization",
            inputSchema={
                "type": "object",
                "properties": {
                    "changes": {
                        "type": "object",
                        "description": "Documentation changes to apply",
                    },
                    "strategy": {
                        "type": "string",
                        "enum": ["hybrid", "bayesian", "joint", "mipro"],
                        "default": "hybrid",
                        "description": "Optimization strategy for updates",
                    },
                    "quality_validation": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable quality validation (PDQI-9, RGS)",
                    },
                },
                "required": ["changes"],
            },
        ),
        Tool(
            name="consolidate_files",
            description="Consolidate related files with quality standards and DSPy optimization",
            inputSchema={
                "type": "object",
                "properties": {
                    "strategy": {
                        "type": "string",
                        "enum": ["hybrid", "bayesian", "joint", "mipro"],
                        "default": "hybrid",
                        "description": "Consolidation strategy",
                    },
                    "target_files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific files to consolidate (optional)",
                    },
                    "quality_standards": {
                        "type": "object",
                        "properties": {
                            "pdqi9_compliance": {"type": "boolean", "default": True},
                            "rgs_compliance": {"type": "boolean", "default": True},
                        },
                        "description": "Quality standards to enforce",
                    },
                },
            },
        ),
        Tool(
            name="manage_versions",
            description="Version control with rollback capabilities and comprehensive tracking",
            inputSchema={
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Files to version control",
                    },
                    "create_snapshot": {
                        "type": "boolean",
                        "default": True,
                        "description": "Create version snapshot",
                    },
                    "track_dependencies": {
                        "type": "boolean",
                        "default": True,
                        "description": "Track file dependencies",
                    },
                    "enable_rollback": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable rollback functionality",
                    },
                },
            },
        ),
        # Prompt Management Tools
        Tool(
            name="remove_prompts",
            description="Remove one or more prompts from the system by their IDs",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of prompt IDs to remove",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for removing the prompts",
                    },
                },
                "required": ["prompt_ids"],
            },
        ),
        Tool(
            name="create_prompt_version",
            description="Create a new version of a prompt with semantic versioning",
            inputSchema={
                "type": "object",
                "properties": {
                    "main_prompt_id": {
                        "type": "string",
                        "description": "Main prompt ID (e.g., 'generate_docs')",
                    },
                    "prompt_data": {
                        "type": "object",
                        "description": "Prompt data (name, description, template, etc.)",
                    },
                    "increment_type": {
                        "type": "string",
                        "enum": ["major", "minor", "patch"],
                        "description": "Version increment type (default: minor)",
                    },
                    "version": {
                        "type": "string",
                        "description": "Specific version to create (optional)",
                    },
                },
                "required": ["main_prompt_id", "prompt_data"],
            },
        ),
        Tool(
            name="deploy_prompt_version",
            description="Deploy a specific version as the main version",
            inputSchema={
                "type": "object",
                "properties": {
                    "main_prompt_id": {
                        "type": "string",
                        "description": "Main prompt ID",
                    },
                    "version": {
                        "type": "string",
                        "description": "Version to deploy",
                    },
                },
                "required": ["main_prompt_id", "version"],
            },
        ),
        Tool(
            name="list_prompt_versions",
            description="List all versions for a prompt with semantic versioning",
            inputSchema={
                "type": "object",
                "properties": {
                    "main_prompt_id": {
                        "type": "string",
                        "description": "Main prompt ID",
                    },
                },
                "required": ["main_prompt_id"],
            },
        ),
        Tool(
            name="get_next_version",
            description="Get the next version for a prompt based on increment type",
            inputSchema={
                "type": "object",
                "properties": {
                    "main_prompt_id": {
                        "type": "string",
                        "description": "Main prompt ID",
                    },
                    "increment_type": {
                        "type": "string",
                        "enum": ["major", "minor", "patch"],
                        "description": "Version increment type",
                    },
                },
                "required": ["main_prompt_id", "increment_type"],
            },
        ),
    ]

    return ListToolsResult(tools=tools)


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle production tool calls."""

    try:
        if name == "optimize_prompt_production":
            result = await optimizer.optimize_prompt_production(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "auto_optimize_with_feedback_production":
            result = await optimizer.auto_optimize_with_feedback_production(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "evaluate_prompt_performance_production":
            result = await optimizer.evaluate_prompt_performance_production(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "run_continuous_improvement_cycle":
            result = await optimizer.run_continuous_improvement_cycle(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "get_performance_dashboard":
            result = await dashboard_generator.generate_dashboard(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "get_optimization_analytics":
            result = await monitoring.get_optimization_analytics(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "configure_alerting":
            result = await alerting.configure_alerting(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "get_system_status":
            result = await monitoring.get_system_status(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        elif name == "deploy_optimized_prompts":
            result = await optimizer.deploy_optimized_prompts(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        # Advanced File Management Tools
        elif name == "update_documentation":
            result = await file_manager.update_documentation(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result.__dict__, indent=2))]
            )

        elif name == "consolidate_files":
            result = await file_manager.consolidate_files(arguments.get("strategy", "hybrid"))
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result.__dict__, indent=2))]
            )

        elif name == "manage_versions":
            result = await file_manager.manage_versions(arguments.get("files", []))
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result.__dict__, indent=2))]
            )

        elif name == "remove_prompts":
            result = await remove_prompts_from_system(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        elif name == "create_prompt_version":
            result = await create_prompt_version(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        elif name == "deploy_prompt_version":
            result = await deploy_prompt_version(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        elif name == "list_prompt_versions":
            result = await list_prompt_versions(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        elif name == "get_next_version":
            result = await get_next_version(arguments)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        else:
            return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])

    except Exception as e:
        logger.error(f"Error in production tool {name}: {str(e)}")
        return CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])


async def main():
    """Main production server function."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="traffic-sim-production-optimization",
                server_version="2.0.0",
                capabilities=ServerCapabilities(tools={}),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
