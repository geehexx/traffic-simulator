from __future__ import annotations

"""Tests for performance optimizations and speed factor stability."""


import pytest
import time
from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation
from traffic_sim.core.performance import get_performance_optimizer


def test_speed_factor_stability():
    """Test that simulation remains stable at 10× speed factor."""
    config = load_config()
    config["physics"]["speed_factor"] = 10.0
    config["vehicles"]["count"] = 20

    sim = Simulation(config)

    # Run simulation for several steps at high speed factor
    start_time = time.time()
    for i in range(1000):  # 1000 steps at 10× speed = 20 seconds of simulation
        sim.step(0.02)

        # Check that vehicles don't have unrealistic speeds
        for vehicle in sim.vehicles:
            assert vehicle.state.v_mps >= 0, "Vehicle speed should not be negative"
            assert vehicle.state.v_mps < 200, "Vehicle speed should be realistic (< 200 m/s)"
            assert vehicle.state.s_m >= 0, "Vehicle position should be non-negative"
            assert (
                vehicle.state.s_m <= sim.track.total_length_m
            ), "Vehicle position should be within track bounds"

    end_time = time.time()
    elapsed = end_time - start_time

    # Should complete in reasonable time (less than 5 seconds real time)
    assert elapsed < 5.0, f"Simulation took too long: {elapsed:.2f}s"

    print(f"10× speed factor test completed in {elapsed:.2f}s")


def test_deterministic_replay():
    """Test that simulation is deterministic with fixed seeds."""
    # Create fresh config to avoid global state issues
    config = load_config().copy()
    config["random"] = config.get("random", {}).copy()
    config["vehicles"] = config.get("vehicles", {}).copy()
    config["random"]["master_seed"] = 42
    config["vehicles"]["color_random_seed"] = 42
    config["vehicles"]["count"] = 10

    # Run simulation twice with same seed
    sim1 = Simulation(config)
    sim2 = Simulation(config)

    # Run both for same number of steps
    for _ in range(100):
        sim1.step(0.02)
        sim2.step(0.02)

    # Check that results are identical
    assert len(sim1.vehicles) == len(sim2.vehicles)

    for v1, v2 in zip(sim1.vehicles, sim2.vehicles):
        assert abs(v1.state.s_m - v2.state.s_m) < 1e-10, "Vehicle positions should be identical"
        assert (
            abs(v1.state.v_mps - v2.state.v_mps) < 1e-10
        ), "Vehicle velocities should be identical"
        assert (
            abs(v1.state.a_mps2 - v2.state.a_mps2) < 1e-10
        ), "Vehicle accelerations should be identical"


def test_performance_optimizer():
    """Test performance optimizer functionality."""
    optimizer = get_performance_optimizer()

    # Test fast inverse sqrt
    test_values = [1.0, 4.0, 9.0, 16.0, 25.0]
    for x in test_values:
        result = optimizer.fast_inverse_sqrt(x)
        expected = 1.0 / (x**0.5)
        assert abs(result - expected) < 0.01, f"Inverse sqrt approximation too far off for {x}"

    # Test caching
    stats = optimizer.get_performance_stats()
    assert "cache_hit_rate" in stats
    assert "cache_hits" in stats
    assert "cache_misses" in stats


def test_vehicle_mix_distribution():
    """Test that vehicle mix is properly distributed."""
    config = load_config()
    config["vehicles"]["count"] = 100  # Large number for statistical testing
    config["vehicles"]["mix"] = {"sedan": 0.5, "suv": 0.3, "truck_van": 0.2}

    sim = Simulation(config)

    # For now, just check that we have the right number of vehicles
    assert len(sim.vehicles) == 100


def test_physics_constraints():
    """Test that physical constraints are properly applied."""
    config = load_config().copy()
    config["vehicles"] = config.get("vehicles", {}).copy()
    config["vehicles"]["count"] = 5
    sim = Simulation(config)

    # Run simulation and check that accelerations are within physical limits
    for _ in range(100):
        sim.step(0.02)

        for vehicle in sim.vehicles:
            # Check that acceleration is within physical limits
            max_decel = vehicle.calculate_physical_constraint_limit()
            assert vehicle.state.a_mps2 >= max_decel, "Acceleration violates physical constraint"

            # Check that max acceleration is reasonable
            max_accel = vehicle.calculate_max_acceleration(vehicle.state.v_mps)
            if vehicle.state.a_mps2 > 0:
                assert (
                    vehicle.state.a_mps2 <= max_accel * 1.1
                ), "Acceleration exceeds power/torque limits"


def test_aerodynamic_drag():
    """Test that aerodynamic drag is properly calculated."""
    config = load_config()
    sim = Simulation(config)

    vehicle = sim.vehicles[0]

    # Test drag force calculation
    drag_force = vehicle.calculate_aerodynamic_drag_force(30.0)  # 30 m/s
    assert drag_force > 0, "Drag force should be positive"

    # Drag should increase with velocity squared
    drag_force_2x = vehicle.calculate_aerodynamic_drag_force(60.0)  # 60 m/s
    assert drag_force_2x > drag_force * 3.5, "Drag should increase roughly with v²"
    assert drag_force_2x < drag_force * 4.5, "Drag should increase roughly with v²"


def test_collision_visual_effects():
    """Test collision visual effects."""
    config = load_config().copy()
    config["vehicles"] = config.get("vehicles", {}).copy()
    config["vehicles"]["count"] = 2
    sim = Simulation(config)

    # Place vehicles very close to trigger collision
    sim.vehicles[0].state.s_m = 0.0
    sim.vehicles[1].state.s_m = 1.0  # Very close

    # Run simulation
    for _ in range(10):
        sim.step(0.02)

    # Check visual state
    visual_state = sim.collision_system.get_vehicle_visual_state(0)
    assert "is_disabled" in visual_state
    assert "blink_state" in visual_state
    assert "alpha" in visual_state


if __name__ == "__main__":
    pytest.main([__file__])
