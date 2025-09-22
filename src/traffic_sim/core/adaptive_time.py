from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AdaptiveTimeStepper:
    base_dt: float = 0.02
    max_dt: float = 0.1

    def calculate_adaptive_dt(self, speed_factor: float, vehicle_count: int) -> float:
        if speed_factor >= 100.0:
            return self.max_dt
        if speed_factor >= 10.0:
            return min(self.max_dt, self.base_dt * (speed_factor / 10.0))
        return self.base_dt
