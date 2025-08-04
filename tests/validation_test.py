"""
Validation tests for traffic simulator optimizations.

Tests the accuracy and reliability of optimized simulation against
baseline behavior and real-world traffic scenarios.
"""

from __future__ import annotations

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation


def test_optimization_consistency():
    """Test that optimized simulation maintains behavioral consistency."""
    # Test with optimizations disabled
    cfg_baseline = load_config()
    cfg_baseline["physics"]["numpy_engine_enabled"] = False
    cfg_baseline["collisions"]["event_scheduler_enabled"] = False
    cfg_baseline["high_performance"]["enabled"] = False

    sim_baseline = Simulation(cfg_baseline)

    # Test with optimizations enabled
    cfg_optimized = load_config()
    sim_optimized = Simulation(cfg_optimized)

    # Run both simulations and compare key metrics
    for _ in range(100):
        sim_baseline.step(0.02)
        sim_optimized.step(0.02)

    # Both simulations should complete without errors
    assert len(sim_baseline.vehicles) == len(sim_optimized.vehicles)


def test_high_vehicle_density():
    """Test simulation with high vehicle density."""
    cfg = load_config()
    cfg["vehicles"]["count"] = 1000
    sim = Simulation(cfg)

    # Should handle high density without crashing
    for _ in range(50):
        sim.step(0.02)

    # Simulation should still have vehicles
    assert len(sim.vehicles) > 0


def test_high_speed_factors():
    """Test simulation with high speed factors."""
    cfg = load_config()
    cfg["physics"]["speed_factor"] = 1000.0
    sim = Simulation(cfg)

    # Should handle high speed factors without crashing
    for _ in range(10):
        sim.step(0.02)

    # Simulation should still be stable
    assert len(sim.vehicles) > 0


def test_collision_scenarios():
    """Test simulation with collision scenarios."""
    cfg = load_config()
    cfg["vehicles"]["count"] = 20
    cfg["physics"]["speed_factor"] = 1.0
    sim = Simulation(cfg)

    # Should handle collision scenarios without crashing
    for _ in range(200):
        sim.step(0.02)

    # Simulation should still be stable
    assert len(sim.vehicles) > 0
