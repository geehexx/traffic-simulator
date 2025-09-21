from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple


@dataclass
class StadiumTrack:
    total_length_m: float
    straight_fraction: float  # r in [0,1)

    @property
    def radius_m(self) -> float:
        # R = L (1 - r) / (2π)
        return self.total_length_m * (1.0 - self.straight_fraction) / (2.0 * math.pi)

    @property
    def straight_length_m(self) -> float:
        # Each straight length S = r L / 2
        return self.straight_fraction * self.total_length_m / 2.0

    def safe_radius_min_m(self, design_speed_kmh: float, e: float, f: float) -> float:
        # R_min = V^2 / (127 (e + f)) with V in km/h
        return (design_speed_kmh ** 2) / (127.0 * (e + f))

    def safe_speed_kmh(self, e: float, f: float) -> float:
        # V_safe = sqrt(127 R (e + f))
        return math.sqrt(127.0 * self.radius_m * (e + f))

    def needed_length_for_radius_m(self, target_radius_m: float) -> float:
        # L_needed = 2π R_min / (1 - r)
        return (2.0 * math.pi * target_radius_m) / max(1e-6, (1.0 - self.straight_fraction))

    def warning_tuple(
        self, design_speed_kmh: float, e: float, f: float
    ) -> Tuple[float, float, float, bool]:
        """
        Returns (R_current, V_safe, L_needed, unsafe_flag)
        """
        r_cur = self.radius_m
        r_min = self.safe_radius_min_m(design_speed_kmh, e, f)
        v_safe = math.sqrt(127.0 * r_cur * (e + f))
        l_needed = self.needed_length_for_radius_m(r_min)
        return r_cur, v_safe, l_needed, (r_cur < r_min)


