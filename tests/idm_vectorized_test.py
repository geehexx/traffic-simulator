from __future__ import annotations

import numpy as np

from traffic_sim.core.idm_vectorized import idm_accel_fallback_next_vehicle


def test_idm_vectorized_matches_simple_synthetic_case():
    # Simple ring with 4 vehicles equally spaced
    n = 4
    L = 400.0
    s = np.array([0.0, 100.0, 200.0, 300.0], dtype=float)
    v = np.array([20.0, 20.0, 20.0, 20.0], dtype=float)
    v0 = np.array([30.0, 30.0, 30.0, 30.0], dtype=float)
    T = np.array([1.5, 1.5, 1.5, 1.5], dtype=float)
    b = np.array([2.0, 2.0, 2.0, 2.0], dtype=float)
    a_max = 1.5
    delta = 4.0

    acc = idm_accel_fallback_next_vehicle(s, v, v0, T, b, a_max, delta, L)

    # Symmetric setup -> equal accelerations, positive because below v0
    assert acc.shape == (n,)
    assert np.allclose(acc, acc[0])
    assert acc[0] > 0.0
