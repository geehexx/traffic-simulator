from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DriverParams:
    reaction_time_s: float
    headway_T_s: float
    comfort_brake_mps2: float
    max_brake_mps2: float
    jerk_limit_mps3: float
    throttle_lag_s: float
    brake_lag_s: float


class Driver:
    def __init__(self, params: DriverParams):
        self.params = params


