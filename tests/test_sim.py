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
    expected = [(rng.randint(40,230), rng.randint(40,230), rng.randint(40,230)) for _ in range(7)]
    colors = [v.color_rgb for v in sim.vehicles]
    assert colors == expected


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
    cfg["physics"]["speed_factor"] = 2.0
    sim = Simulation(cfg)
    s0 = sim.vehicles[0].state.s_m
    sim.step(0.5)
    s1 = sim.vehicles[0].state.s_m
    # v=20 m/s, dt=0.5, sf=2 ⇒ ds=20
    assert pytest.approx((s1 - s0) % sim.track.total_length, rel=1e-6) == 20.0


