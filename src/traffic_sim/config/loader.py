from __future__ import annotations

import os
from typing import Any, Dict

import yaml


def load_config(config_path: str | None = None) -> Dict[str, Any]:
    """
    Load YAML configuration into a nested dict.

    - If config_path is None, defaults to 'config/config.yaml' relative to CWD.
    - Environment variable override: TRAFFIC_SIM_CONFIG
    """
    chosen_path = (
        config_path
        or os.environ.get("TRAFFIC_SIM_CONFIG")
        or os.path.join(os.getcwd(), "config", "config.yaml")
    )
    with open(chosen_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def get_nested(cfg: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Small helper to retrieve nested keys like 'track.length_m'."""
    node: Any = cfg
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node


