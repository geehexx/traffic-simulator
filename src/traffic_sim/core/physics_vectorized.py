from __future__ import annotations

from typing import Optional
import numpy as np


def step_arc_kinematics(
    s_m: np.ndarray,
    v_mps: np.ndarray,
    a_mps2: np.ndarray,
    dt_s: float,
    track_length_m: float,
    active_mask: Optional[np.ndarray] = None,
) -> None:
    """Vectorized arc-length kinematics update.

    In-place update of s and v for active vehicles:
        v += a * dt
        s = (s + v * dt) mod L
    """
    if active_mask is None:
        # Assume all active
        v_mps += a_mps2 * dt_s
        np.maximum(v_mps, 0.0, out=v_mps)
        s_m += v_mps * dt_s
        np.remainder(s_m, track_length_m, out=s_m)
        return

    # Masked update
    v_mps[active_mask] += a_mps2[active_mask] * dt_s
    np.maximum(v_mps, 0.0, out=v_mps)
    s_m[active_mask] += v_mps[active_mask] * dt_s
    np.remainder(s_m, track_length_m, out=s_m)
