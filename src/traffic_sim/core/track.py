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

    # --- Geometry helpers for rendering and kinematics ---
    @property
    def total_length(self) -> float:
        return self.total_length_m

    def bbox_m(self) -> Tuple[float, float]:
        """Return (width_m, height_m) of the stadium's bounding box."""
        R = self.radius_m
        S = self.straight_length_m
        return S + 2.0 * R, 2.0 * R

    def position_heading(self, s_m: float) -> Tuple[float, float, float]:
        """
        Map arc length s (meters) along centerline to (x, y, theta) in meters/radians.
        Stadium is centered at origin with straights along +x/-x at y=±R.
        Path order: top straight (west→east), right semicircle (top→bottom, clockwise),
        bottom straight (east→west), left semicircle (bottom→top, counterclockwise).
        """
        L = self.total_length_m
        R = self.radius_m
        S = self.straight_length_m
        s = s_m % L

        # Segment lengths
        seg1 = S
        seg2 = S + math.pi * R
        seg3 = S + math.pi * R + S
        # seg4 = L

        if s < seg1:
            # Top straight: x from -S/2 → +S/2 at y=+R
            x = -S * 0.5 + s
            y = +R
            theta = 0.0  # east
            return x, y, theta
        if s < seg2:
            # Right semicircle: center at (S/2, 0), angle from π/2 → -π/2
            t = s - seg1
            angle = math.pi * 0.5 - (t / R)
            x = (S * 0.5) + R * math.cos(angle)
            y = 0.0 + R * math.sin(angle)
            theta = angle - math.pi * 0.5
            return x, y, theta
        if s < seg3:
            # Bottom straight: x from +S/2 → -S/2 at y=-R
            t = s - seg2
            x = (S * 0.5) - t
            y = -R
            theta = math.pi  # west
            return x, y, theta
        # Left semicircle: center at (-S/2, 0), angle from -π/2 → +π/2
        t = s - seg3
        angle = -math.pi * 0.5 + (t / R)
        x = (-S * 0.5) + R * math.cos(angle)
        y = 0.0 + R * math.sin(angle)
        theta = angle - math.pi * 0.5
        return x, y, theta


