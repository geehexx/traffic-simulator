"""Tests for adaptive time test."""

from __future__ import annotations


"""Tests for adaptive time test."""

import pytest


from traffic_sim.core.adaptive_time import AdaptiveTimeStepper


def test_adaptive_dt_monotonic():
    ats = AdaptiveTimeStepper(base_dt=0.02, max_dt=0.1)
    assert ats.calculate_adaptive_dt(1.0, 100) == 0.02
    assert ats.calculate_adaptive_dt(10.0, 100) == 0.02 * (10.0 / 10.0)
    assert ats.calculate_adaptive_dt(100.0, 100) == 0.1  # capped by max_dt


if __name__ == "__main__":
    pytest.main([__file__])
