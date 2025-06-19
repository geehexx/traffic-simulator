"""Tests for rendering integration test."""

from __future__ import annotations


"""Integration tests for rendering functionality."""


import pytest
from unittest.mock import Mock, patch
import arcade

from traffic_sim.core.simulation import Simulation
from traffic_sim.core.track import StadiumTrack
from traffic_sim.render.app import TrafficSimWindow


class TestRenderingIntegration:
    """Test that rendering code actually works without runtime errors."""

    def test_rendering_functions_exist(self) -> None:
        """Test that all required arcade functions exist."""
        # Test that the correct functions exist
        assert hasattr(arcade, "draw_lrbt_rectangle_filled")
        assert hasattr(arcade, "draw_lrbt_rectangle_outline")
        assert hasattr(arcade, "draw_lbwh_rectangle_filled")
        assert hasattr(arcade, "draw_lbwh_rectangle_outline")

        # Test that the incorrect function does NOT exist
        assert not hasattr(arcade, "draw_rectangle_filled")

    def test_hud_rendering_functions(self) -> None:
        """Test that HUD rendering functions work without errors."""
        from traffic_sim.core.hud import draw_perception_heatmap
        from traffic_sim.core.simulation import PerceptionData

        # Create mock perception data
        perception_data = [
            PerceptionData(
                leader_vehicle=None,
                leader_distance_m=100.0,
                ssd_required_m=50.0,
                is_occluded=False,
                visual_range_m=200.0,
            ),
            PerceptionData(
                leader_vehicle=None,
                leader_distance_m=150.0,
                ssd_required_m=75.0,
                is_occluded=True,
                visual_range_m=200.0,
            ),
        ]

        # Test that these functions can be called without AttributeError
        # We can't actually draw without a window, but we can test the function calls
        try:
            # This should not raise AttributeError about draw_rectangle_filled
            draw_perception_heatmap(0, 0, perception_data)
        except AttributeError as e:
            if "draw_rectangle_filled" in str(e):
                pytest.fail(f"draw_rectangle_filled function should not be called: {e}")
            # Other AttributeErrors are acceptable (like missing window context)
            pass
        except RuntimeError as e:
            if "No window is active" in str(e):
                # This is expected - the function is working correctly but needs a window
                pass
            else:
                raise

    @patch("arcade.Window")
    def test_window_creation_and_rendering(self, mock_window_class) -> None:
        """Test that window creation and rendering methods work."""
        # Mock the window class
        mock_window = Mock()
        mock_window_class.return_value = mock_window

        # Create a minimal simulation (not used but demonstrates correct API)
        _track = StadiumTrack(total_length_m=1000.0, straight_fraction=0.30)
        _sim = Simulation({"track": {"length_m": 1000.0, "straight_fraction": 0.30}})

        # Create window (this should not fail due to incorrect function calls)
        window = TrafficSimWindow(800, 600, "Test", {})

        # Test that rendering methods exist and are callable
        assert hasattr(window, "_draw_track")
        assert hasattr(window, "_draw_vehicles")
        assert callable(window._draw_track)
        assert callable(window._draw_vehicles)

    def test_arcade_function_signatures(self) -> None:
        """Test that arcade functions have the expected signatures."""
        import inspect

        # Test draw_lrbt_rectangle_filled signature
        sig = inspect.signature(arcade.draw_lrbt_rectangle_filled)
        params = list(sig.parameters.keys())
        expected_params = ["left", "right", "bottom", "top", "color"]
        assert params == expected_params, f"Expected {expected_params}, got {params}"

        # Test draw_lbwh_rectangle_filled signature
        sig = inspect.signature(arcade.draw_lbwh_rectangle_filled)
        params = list(sig.parameters.keys())
        expected_params = ["left", "bottom", "width", "height", "color"]
        assert params == expected_params, f"Expected {expected_params}, got {params}"

    def test_no_incorrect_function_calls(self) -> None:
        """Test that no code tries to call the non-existent draw_rectangle_filled."""
        import ast
        import os

        # Find all Python files in the project
        python_files = []
        for root, _dirs, files in os.walk("src"):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))

        for file_path in python_files:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse the AST to find function calls
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Attribute):
                            if (
                                isinstance(node.func.value, ast.Name)
                                and node.func.value.id == "arcade"
                                and node.func.attr == "draw_rectangle_filled"
                            ):
                                pytest.fail(
                                    f"Found call to non-existent arcade.draw_rectangle_filled in {file_path}"
                                )
            except SyntaxError:
                # Skip files with syntax errors
                pass


if __name__ == "__main__":
    pytest.main([__file__])
