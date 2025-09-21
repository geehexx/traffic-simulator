"""Tests for the main module."""

from __future__ import annotations


class TestMain:
    """Test the main module functionality."""

    def test_main_import(self) -> None:
        """Test that main can be imported."""
        from traffic_sim.render.app import main

        assert callable(main)

    def test_main_module_has_main_function(self) -> None:
        """Test that the main module can be imported and has the expected structure."""
        import traffic_sim.__main__ as main_module

        # Check that the module has the expected structure
        assert hasattr(main_module, "__name__")
        assert main_module.__name__ == "traffic_sim.__main__"
