from __future__ import annotations


import pytest

import numpy as np
from traffic_sim.core.physics_numpy import PhysicsEngineNumpy


def test_physics_engine_numpy_physics():
    # Vehicle: mass, power, torque, drag, tire_mu, brake_eta
    specs = np.array(
        [
            [1000, 100, 200, 0.5, 0.8, 0.9],
            [2000, 200, 400, 1.0, 0.7, 0.8],
        ]
    )
    # State: s_m, v_mps, a_mps2, heading
    state = np.array(
        [
            [0.0, 10.0, 0.0, 0.0],
            [5.0, 20.0, 0.0, 0.0],
        ]
    )
    engine = PhysicsEngineNumpy(specs, state)
    # Commanded accelerations: try to accelerate both vehicles
    actions = np.array([5.0, 5.0])
    dt = 1.0
    track_length = 100.0
    updated = engine.step(actions, dt, track_length)
    # Both vehicles should move forward, velocity should increase, acceleration should be limited by power/torque
    assert updated[0, 0] > 0.0 and updated[1, 0] > 5.0
    assert updated[0, 1] > 10.0 and updated[1, 1] > 20.0
    # Acceleration should not exceed physical limits
    assert updated[0, 2] <= 5.0 and updated[1, 2] <= 5.0
    print("PhysicsEngineNumpy physics test passed.")


if __name__ == "__main__":
    pytest.main([__file__])
