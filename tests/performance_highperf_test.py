from __future__ import annotations

import time

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation


def test_high_performance_flags_do_not_regress():
    cfg = load_config().copy()
    cfg.setdefault("profiling", {})
    cfg["profiling"]["enabled"] = True
    cfg.setdefault("vehicles", {})
    cfg["vehicles"]["count"] = 20
    cfg.setdefault("data_manager", {})
    cfg["data_manager"]["enabled"] = True
    cfg.setdefault("high_performance", {})
    cfg["high_performance"]["enabled"] = True
    cfg["high_performance"]["idm_vectorized"] = True

    sim = Simulation(cfg)

    steps = 500
    dt = 0.02

    start = time.perf_counter()
    for _ in range(steps):
        sim.step(dt)
    elapsed = time.perf_counter() - start

    # Soft bound to catch obvious regressions while avoiding flakiness
    assert elapsed < 10.0, f"High-performance path too slow: {elapsed:.2f}s"
