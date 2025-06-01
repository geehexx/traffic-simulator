from __future__ import annotations

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation


def test_perception_window_flag_limits_checks_without_behavior_change_when_clear():
    cfg = load_config().copy()
    cfg.setdefault("vehicles", {})
    cfg["vehicles"]["count"] = 10

    # Without windowing
    cfg_a = cfg.copy()
    cfg_a.setdefault("perception", {})
    cfg_a["perception"]["window_enabled"] = False
    sim_a = Simulation(cfg_a)

    # With windowing
    cfg_b = cfg.copy()
    cfg_b.setdefault("perception", {})
    cfg_b["perception"]["window_enabled"] = True
    cfg_b["perception"]["window_neighbors"] = 3
    sim_b = Simulation(cfg_b)

    # Spread vehicles evenly so occlusion path is trivial (leaders are visible)
    L = sim_a.track.total_length_m
    spacing = L / 10
    for i in range(10):
        sim_a.vehicles[i].state.s_m = i * spacing
        sim_b.vehicles[i].state.s_m = i * spacing

    sim_a._update_perception_data(0.02)
    sim_b._update_perception_data(0.02)

    # Leaders and distances should match for each vehicle
    for i in range(10):
        pa = sim_a.perception_data[i]
        pb = sim_b.perception_data[i]
        assert pa is not None and pb is not None
        assert (pa.leader_vehicle is None) == (pb.leader_vehicle is None)
        if pa.leader_vehicle is not None and pb.leader_vehicle is not None:
            assert abs(pa.leader_distance_m - pb.leader_distance_m) < 1e-9
