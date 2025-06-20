"""Performance regression smoke test using profiler stats.

This is intentionally lightweight and non-flaky: it asserts that
profiling is enabled, stats are produced, and total simulation time
per step remains within a generous bound on typical dev hardware.
"""

from __future__ import annotations


import pytest

import time

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation
from traffic_sim.core.profiling import get_profiler


def test_profiler_produces_stats_and_reasonable_step_time():
    cfg = load_config().copy()
    cfg.setdefault("profiling", {})
    cfg["profiling"]["enabled"] = True
    cfg.setdefault("vehicles", {}).setdefault("count", 5)

    sim = Simulation(cfg)

    steps = 200
    dt = 0.02

    profiler = get_profiler(reset=True)

    start = time.perf_counter()
    for _ in range(steps):
        sim.step(dt)
    elapsed = time.perf_counter() - start

    stats = profiler.get_stats()
    # Ensure some core blocks were measured
    assert any(
        name in stats
        for name in (
            "update_perception",
            "idm_acceleration",
            "update_vehicle_physics",
            "step_physics",
        )
    ), "Expected profiler to record core timing blocks"

    # Generous upper bound to avoid flakiness: < 3s for 200 small steps
    assert elapsed < 3.0, f"Performance smoke too slow: {elapsed:.2f}s"


if __name__ == "__main__":
    pytest.main([__file__])
