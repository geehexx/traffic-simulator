from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any
import random


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


def _trunc_gauss(rng: random.Random, mean: float, std: float, min_v: float, max_v: float) -> float:
    # Simple rejection sampling for truncation
    for _ in range(100):
        v = rng.gauss(mean, std)
        if min_v <= v <= max_v:
            return v
    return max(min_v, min(max_v, mean))


def sample_driver_params(cfg: Dict[str, Any], rng: random.Random) -> DriverParams:
    dist = cfg.get("drivers", {}).get("distributions", {})
    def g(key: str, default: dict) -> dict:
        return dist.get(key, default)

    rt = g("reaction_time_s", {"mean": 2.5, "std": 0.6, "min": 0.8, "max": 4.0})
    T = g("headway_T_s", {"mean": 1.6, "std": 0.5, "min": 0.6, "max": 3.0})
    b_comf = g("comfort_brake_mps2", {"mean": 2.5, "std": 0.7, "min": 1.0, "max": 4.0})
    b_max = g("max_brake_mps2", {"mean": 7.0, "std": 1.0, "min": 4.0, "max": 9.0})
    j = g("jerk_limit_mps3", {"mean": 4.0, "std": 1.0, "min": 1.0, "max": 7.0})
    tl = g("throttle_lag_s", {"mean": 0.25, "std": 0.10, "min": 0.05, "max": 1.0})
    bl = g("brake_lag_s", {"mean": 0.15, "std": 0.07, "min": 0.05, "max": 1.0})

    return DriverParams(
        reaction_time_s=_trunc_gauss(rng, rt["mean"], rt["std"], rt["min"], rt["max"]),
        headway_T_s=_trunc_gauss(rng, T["mean"], T["std"], T["min"], T["max"]),
        comfort_brake_mps2=_trunc_gauss(rng, b_comf["mean"], b_comf["std"], b_comf["min"], b_comf["max"]),
        max_brake_mps2=_trunc_gauss(rng, b_max["mean"], b_max["std"], b_max["min"], b_max["max"]),
        jerk_limit_mps3=_trunc_gauss(rng, j["mean"], j["std"], j["min"], j["max"]),
        throttle_lag_s=_trunc_gauss(rng, tl["mean"], tl["std"], tl["min"], tl["max"]),
        brake_lag_s=_trunc_gauss(rng, bl["mean"], bl["std"], bl["min"], bl["max"]),
    )


