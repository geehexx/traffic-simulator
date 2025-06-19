"""Tests for collision prefilter test."""

from __future__ import annotations


"""Tests for collision prefilter test."""

import pytest


from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation


def test_collision_prefilter_does_not_change_detection():
    # Base config
    cfg = load_config().copy()
    cfg.setdefault("vehicles", {})
    cfg["vehicles"]["count"] = 3

    # Run without prefilter
    cfg_no = cfg.copy()
    cfg_no.setdefault("collisions", {})
    cfg_no["collisions"]["prefilter_enabled"] = False
    sim_no = Simulation(cfg_no)
    # Place vehicles to ensure one collision scenario (very close)
    sim_no.vehicles[0].state.s_m = 0.0
    sim_no.vehicles[1].state.s_m = 0.3
    sim_no.vehicles[2].state.s_m = sim_no.track.total_length_m / 2.0
    events_no = sim_no.collision_system.check_collisions(sim_no.vehicles)

    # Run with prefilter
    cfg_yes = cfg.copy()
    cfg_yes.setdefault("collisions", {})
    cfg_yes["collisions"]["prefilter_enabled"] = True
    cfg_yes["collisions"]["prefilter_cell_m"] = 10.0
    sim_yes = Simulation(cfg_yes)
    sim_yes.vehicles[0].state.s_m = 0.0
    sim_yes.vehicles[1].state.s_m = 0.3
    sim_yes.vehicles[2].state.s_m = sim_yes.track.total_length_m / 2.0
    events_yes = sim_yes.collision_system.check_collisions(sim_yes.vehicles)

    # Both should detect at least one collision and equal counts
    assert len(events_no) >= 1
    assert len(events_no) == len(events_yes)


if __name__ == "__main__":
    pytest.main([__file__])
