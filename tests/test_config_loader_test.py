"""Tests for the config loader module."""

from __future__ import annotations

import os
import tempfile
from unittest.mock import patch

import yaml

from traffic_sim.config.loader import load_config, get_nested


class TestLoadConfig:
    """Test the load_config function."""

    def test_load_config_with_path(self) -> None:
        """Test loading config from a specific path."""
        config_data = {"test": "value", "nested": {"key": "value"}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            result = load_config(temp_path)
            assert result == config_data
        finally:
            os.unlink(temp_path)

    def test_load_config_with_none(self) -> None:
        """Test loading config with None path (should use default)."""
        with (
            patch("os.path.join") as mock_join,
            patch("builtins.open") as mock_open,
            patch("yaml.safe_load") as mock_yaml,
        ):
            mock_join.return_value = "config/config.yaml"
            mock_open.return_value.__enter__.return_value = "file_content"
            mock_yaml.return_value = {"default": "config"}

            result = load_config(None)

            mock_join.assert_called_once_with(os.getcwd(), "config", "config.yaml")
            assert result == {"default": "config"}

    def test_load_config_with_env_var(self) -> None:
        """Test loading config with environment variable override."""
        config_data = {"env": "config"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            with patch.dict(os.environ, {"TRAFFIC_SIM_CONFIG": temp_path}):
                result = load_config(None)
                assert result == config_data
        finally:
            os.unlink(temp_path)

    def test_load_config_empty_file(self) -> None:
        """Test loading config from empty file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            result = load_config(temp_path)
            assert result == {}
        finally:
            os.unlink(temp_path)


class TestGetNested:
    """Test the get_nested function."""

    def test_get_nested_simple_key(self) -> None:
        """Test getting a simple key."""
        cfg = {"key": "value"}
        result = get_nested(cfg, "key")
        assert result == "value"

    def test_get_nested_nested_key(self) -> None:
        """Test getting a nested key."""
        cfg = {"level1": {"level2": {"level3": "value"}}}
        result = get_nested(cfg, "level1.level2.level3")
        assert result == "value"

    def test_get_nested_missing_key(self) -> None:
        """Test getting a missing key returns default."""
        cfg = {"key": "value"}
        result = get_nested(cfg, "missing", "default")
        assert result == "default"

    def test_get_nested_missing_nested_key(self) -> None:
        """Test getting a missing nested key returns default."""
        cfg = {"level1": {"level2": "value"}}
        result = get_nested(cfg, "level1.level2.level3", "default")
        assert result == "default"

    def test_get_nested_non_dict_node(self) -> None:
        """Test getting nested key when intermediate node is not a dict."""
        cfg = {"level1": "not_a_dict"}
        result = get_nested(cfg, "level1.level2", "default")
        assert result == "default"

    def test_get_nested_empty_path(self) -> None:
        """Test getting with empty path."""
        cfg = {"key": "value"}
        result = get_nested(cfg, "", "default")
        assert result == "default"
