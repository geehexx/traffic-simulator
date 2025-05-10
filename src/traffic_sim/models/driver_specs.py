from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DriverDistribution:
    mean: float
    std: float
    min: float
    max: float
