from __future__ import annotations

import numpy as np

from traffic_sim.core.physics_vectorized import step_arc_kinematics


def test_step_arc_kinematics_basic():
    n = 5
    L = 1000.0
    dt = 0.1

    s = np.zeros(n, dtype=np.float32)
    v = np.full(n, 10.0, dtype=np.float32)
    a = np.full(n, 2.0, dtype=np.float32)

    step_arc_kinematics(s, v, a, dt, L)

    # v = 10 + 2*0.1 = 10.2
    # s = 0 + 10.2*0.1 = 1.02
    np.testing.assert_allclose(v, 10.2, rtol=1e-5, atol=1e-6)
    np.testing.assert_allclose(s, 1.02, rtol=1e-5, atol=1e-6)


def test_step_arc_kinematics_mask_and_wrap():
    L = 50.0
    dt = 1.0

    s = np.array([0.0, 49.0, 25.0], dtype=np.float32)
    v = np.array([1.0, 3.0, 0.0], dtype=np.float32)
    a = np.array([0.0, 1.0, -5.0], dtype=np.float32)
    mask = np.array([True, True, False])

    step_arc_kinematics(s, v, a, dt, L, active_mask=mask)

    # idx0: v=1, s=1
    # idx1: v=3+1=4, s=49+4=53 -> 3
    # idx2: inactive -> unchanged
    np.testing.assert_allclose(v, [1.0, 4.0, 0.0], rtol=1e-6)
    np.testing.assert_allclose(s, [1.0, 3.0, 25.0], rtol=1e-6)
