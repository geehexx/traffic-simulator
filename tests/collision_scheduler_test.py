from __future__ import annotations

"""Tests for collision scheduler test."""

import pytest


from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation


def test_scheduler_parity_with_dense_detection_simple_case():
    # Base config
    base = load_config().copy()
    base.setdefault("vehicles", {})
    base["vehicles"]["count"] = 5

    # Dense
    cfg_dense = base.copy()
    cfg_dense.setdefault("collisions", {})
    cfg_dense["collisions"]["event_scheduler_enabled"] = False
    sim_dense = Simulation(cfg_dense)

    # Scheduler
    cfg_sched = base.copy()
    cfg_sched.setdefault("collisions", {})
    cfg_sched["collisions"]["event_scheduler_enabled"] = True
    sim_sched = Simulation(cfg_sched)

    # Arrange positions to create one likely collision
    sim_dense.vehicles[0].state.s_m = 0.0
    sim_dense.vehicles[1].state.s_m = 0.4
    sim_dense.vehicles[2].state.s_m = 100.0
    sim_dense.vehicles[3].state.s_m = 200.0
    sim_dense.vehicles[4].state.s_m = 300.0

    for i, v in enumerate(sim_sched.vehicles):
        v.state.s_m = sim_dense.vehicles[i].state.s_m

    # Step a few times and compare total collision events logged
    for _ in range(50):
        sim_dense.step(0.02)
        sim_sched.step(0.02)

    events_dense = sim_dense.collision_system.get_collision_events()
    events_sched = sim_sched.collision_system.get_collision_events()
    assert (len(events_dense) > 0) == (len(events_sched) > 0)


if __name__ == "__main__":
    pytest.main([__file__])
