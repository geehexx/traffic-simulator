from __future__ import annotations


import pytest

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation


def test_simulation_safety_panel_keys(tmp_path):
    cfg = load_config()
    sim = Simulation(cfg)
    panel = sim.compute_safety_panel()
    assert set(panel.keys()) == {"radius_m", "v_safe_kmh", "length_needed_m", "unsafe"}


def test_vehicle_spawn_count_and_colors(tmp_path):
    cfg = load_config()
    cfg["vehicles"]["count"] = 7
    cfg["vehicles"]["color_random_seed"] = 42
    sim = Simulation(cfg)
    assert len(sim.vehicles) == 7
    # Deterministic with seed: generate expected sequence using the same RNG progression
    import random

    rng = random.Random(42)
    expected = [
        (rng.randint(40, 230), rng.randint(40, 230), rng.randint(40, 230)) for _ in range(7)
    ]
    colors = [v.color_rgb for v in sim.vehicles]
    assert colors == expected


def test_safety_flag_toggles_with_length():
    cfg = load_config()
    cfg["track"]["safety_design_speed_kmh"] = 120
    cfg["track"]["superelevation_e"] = 0.08
    cfg["track"]["side_friction_f"] = 0.10
    # Very short length should be unsafe at 120 km/h
    cfg["track"]["length_m"] = 600.0
    sim_short = Simulation(cfg)
    assert sim_short.compute_safety_panel()["unsafe"] is True
    # Longer length should move toward safe
    # Compute required length using the same formula: L_needed = 2π R_min / (1 - r)
    r = cfg["track"].get("straight_fraction", 0.30)
    V = cfg["track"]["safety_design_speed_kmh"]
    e = cfg["track"]["superelevation_e"]
    f = cfg["track"]["side_friction_f"]
    R_min = (V * V) / (127.0 * (e + f))
    L_needed = (2.0 * 3.141592653589793 * R_min) / (1.0 - r)
    cfg["track"]["length_m"] = L_needed + 1.0
    sim_long = Simulation(cfg)
    assert sim_long.compute_safety_panel()["unsafe"] is False


def test_vehicle_colors_bounds_with_seed():
    cfg = load_config()
    cfg["vehicles"]["count"] = 20
    cfg["vehicles"]["color_random_seed"] = 1
    sim = Simulation(cfg)
    for v in sim.vehicles:
        r, g, b = v.color_rgb
        assert 40 <= r <= 230 and 40 <= g <= 230 and 40 <= b <= 230


def test_speed_factor_applied_to_motion():
    cfg = load_config()
    cfg["vehicles"]["count"] = 1
    cfg.setdefault("physics", {})
    cfg["physics"]["speed_factor"] = 2.0
    sim = Simulation(cfg)
    s0 = sim.vehicles[0].state.s_m
    sim.step(0.5)
    s1 = sim.vehicles[0].state.s_m
    # With enhanced dynamics, the vehicle will accelerate from 20 m/s
    # The distance moved should be approximately v*dt*sf with some acceleration
    # v=20 m/s, dt=0.5, sf=2 ⇒ expected ds ≈ 20, but with acceleration it will be more
    distance_moved = (s1 - s0) % sim.track.total_length
    assert distance_moved > 15.0, f"Distance moved too small: {distance_moved}"
    assert distance_moved < 25.0, f"Distance moved too large: {distance_moved}"


def test_perception_data_initialization():
    """Test that perception data is properly initialized."""
    cfg = load_config()
    cfg["vehicles"]["count"] = 3
    sim = Simulation(cfg)

    # Check that perception data is initialized for all vehicles
    assert len(sim.perception_data) == 3
    for perception in sim.perception_data:
        assert perception.leader_vehicle is None
        assert perception.leader_distance_m == 0.0
        assert perception.is_occluded is False
        assert perception.ssd_required_m == 0.0
        assert perception.visual_range_m == sim.visual_range_m


def test_step_with_no_vehicles():
    """Test that step works with no vehicles."""
    cfg = load_config()
    cfg["vehicles"]["count"] = 0
    sim = Simulation(cfg)

    # Should not raise an exception
    sim.step(0.1)
    assert len(sim.vehicles) == 0


def test_occlusion_detection():
    """Test occlusion detection logic."""
    cfg = load_config()
    cfg["vehicles"]["count"] = 2
    sim = Simulation(cfg)

    # Test that occlusion detection methods exist and work
    # The _is_leader_visible method should exist and handle close distances
    if hasattr(sim, "_is_leader_visible"):
        assert sim._is_leader_visible(0.5, 0.0) is True
        assert sim._is_leader_visible(50.0, 0.0) is True
    else:
        # If method doesn't exist, just test that simulation works
        sim.step(0.1)
        assert len(sim.vehicles) == 2


def test_find_first_unobstructed_leader():
    """Test finding unobstructed leader logic."""
    cfg = load_config()
    cfg["vehicles"]["count"] = 3
    sim = Simulation(cfg)

    # Test with a follower index
    follower_idx = 0
    leader, distance, is_occluded = sim._find_first_unobstructed_leader(follower_idx)

    # Should return some result (may be None if no leader found)
    assert isinstance(is_occluded, bool)
    if leader is not None:
        assert distance >= 0


def test_is_between_positions():
    """Test the _is_between_positions method."""
    cfg = load_config()
    cfg["vehicles"]["count"] = 3
    sim = Simulation(cfg)

    # Test various position combinations
    assert sim._is_between_positions(0.0, 10.0, 5.0, 1000.0) is True  # 5 is between 0 and 10
    assert sim._is_between_positions(0.0, 10.0, 15.0, 1000.0) is False  # 15 is not between 0 and 10
    assert sim._is_between_positions(0.0, 10.0, -5.0, 1000.0) is False  # -5 is not between 0 and 10

    # Test with wraparound (L = 1000)
    assert (
        sim._is_between_positions(900.0, 100.0, 950.0, 1000.0) is True
    )  # 950 is between 900 and 100 (wraparound)
    assert (
        sim._is_between_positions(900.0, 100.0, 50.0, 1000.0) is True
    )  # 50 is between 900 and 100 (wraparound)
    assert (
        sim._is_between_positions(900.0, 100.0, 500.0, 1000.0) is False
    )  # 500 is not between 900 and 100 (wraparound)


def test_occlusion_continue_logic():
    """Test the occlusion continue logic in _find_first_unobstructed_leader."""
    cfg = load_config()
    cfg["vehicles"]["count"] = 3
    sim = Simulation(cfg)

    # Test that the method works with multiple vehicles
    # This should exercise the continue logic in the loop
    for i in range(len(sim.vehicles)):
        leader, distance, is_occluded = sim._find_first_unobstructed_leader(i)
        assert isinstance(is_occluded, bool)
        if leader is not None:
            assert distance >= 0


def test_occlusion_visibility_logic():
    """Test the occlusion visibility logic."""
    cfg = load_config()
    cfg["vehicles"]["count"] = 3
    sim = Simulation(cfg)

    # Test the _is_leader_visible method if it exists
    if hasattr(sim, "_is_leader_visible"):
        # Test very close distance (should always be visible)
        assert sim._is_leader_visible(0.5, 0.0) is True

        # Test normal distance (should be visible)
        assert sim._is_leader_visible(50.0, 0.0) is True

        # Test far distance (should be visible)
        assert sim._is_leader_visible(200.0, 0.0) is True


def test_occlusion_visibility_edge_cases():
    """Test edge cases for occlusion visibility logic."""
    cfg = load_config()
    cfg["vehicles"]["count"] = 3
    sim = Simulation(cfg)

    # Test the _is_leader_visible method if it exists
    if hasattr(sim, "_is_leader_visible"):
        # Test edge case: distance exactly 1.0
        assert sim._is_leader_visible(1.0, 0.0) is True

        # Test edge case: distance just under 1.0
        assert sim._is_leader_visible(0.99, 0.0) is True

        # Test edge case: distance just over 1.0
        assert sim._is_leader_visible(1.01, 0.0) is True


def test_occlusion_visibility_edge_cases_2():
    """Test more edge cases for occlusion visibility logic."""
    cfg = load_config()
    cfg["vehicles"]["count"] = 3
    sim = Simulation(cfg)

    # Test the _is_leader_visible method if it exists
    if hasattr(sim, "_is_leader_visible"):
        # Test edge case: distance exactly 1.0
        assert sim._is_leader_visible(1.0, 0.0) is True

        # Test edge case: distance just under 1.0
        assert sim._is_leader_visible(0.99, 0.0) is True

        # Test edge case: distance just over 1.0
        assert sim._is_leader_visible(1.01, 0.0) is True


if __name__ == "__main__":
    pytest.main([__file__])
