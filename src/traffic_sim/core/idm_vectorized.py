from __future__ import annotations

from typing import cast
import numpy as np


def idm_accel_fallback_next_vehicle(
    s_m: np.ndarray,
    v_mps: np.ndarray,
    desired_speed_mps: np.ndarray,
    headway_T_s: np.ndarray,
    comfort_brake_mps2: np.ndarray,
    a_max: float,
    idm_delta: float,
    track_length_m: float,
) -> np.ndarray:
    """Vectorized IDM acceleration using fallback rule (next vehicle as leader).

    This mirrors the scalar fallback used when perception is unavailable.
    """
    n = s_m.shape[0]
    # Leader is the next index modulo n
    leader_idx = (np.arange(n) + 1) % n
    s_leader = s_m[leader_idx]
    v_leader = v_mps[leader_idx]

    # Gaps along track (wrap)
    s_gap = (s_leader - s_m) % track_length_m

    # Per-driver params
    T = headway_T_s
    b_comf = comfort_brake_mps2
    v0 = np.minimum(desired_speed_mps, np.maximum(desired_speed_mps, 0.0))

    # Avoid zero divisions
    v0_safe = np.maximum(v0, 0.1)
    s_gap_safe = np.maximum(s_gap, 0.1)

    delta_v = v_mps - v_leader

    # s* = s0 + vT + vΔv/(2*sqrt(a_max*b_comf)) ; s0=2.0
    s0 = 2.0
    sqrt_term = np.sqrt(np.maximum(a_max, 1e-9) * np.maximum(b_comf, 1e-9))
    s_star = s0 + v_mps * T + (v_mps * delta_v) / (2.0 * sqrt_term + 1e-9)

    acc = a_max * (1.0 - (v_mps / v0_safe) ** idm_delta - (s_star / s_gap_safe) ** 2)
    acc64 = acc.astype(np.float64)
    return cast(np.ndarray, acc64)
