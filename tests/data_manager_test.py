"""Tests for data manager test."""

from __future__ import annotations


"""Tests for data manager test."""

import pytest


import numpy as np

from traffic_sim.core.data_manager import VehicleDataManager


def test_allocate_and_step_kinematics():
    dm = VehicleDataManager(max_vehicles=10)

    v0 = dm.allocate(length_m=4.5, width_m=1.8, pos=(0.0, 0.0), vel=(10.0, 0.0))
    assert v0 is not None
    idx = v0.index

    # Set acceleration
    dm.accelerations[idx, :] = (1.0, 0.0)

    # Step for 1 second in 50 increments
    dt = 0.02
    for _ in range(50):
        dm.step_kinematics(dt)

    # Analytical: v = v0 + a t = 10 + 1*1 = 11 m/s
    # x = x0 + v0 t + 0.5 a t^2 = 0 + 10*1 + 0.5*1*1 = 10.5 m
    np.testing.assert_allclose(dm.velocities[idx, 0], 11.0, rtol=1e-4, atol=1e-3)
    np.testing.assert_allclose(dm.positions[idx, 0], 10.5, rtol=1e-4, atol=1e-3)


if __name__ == "__main__":
    pytest.main([__file__])
