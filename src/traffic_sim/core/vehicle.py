from __future__ import annotations

from dataclasses import dataclass


@dataclass
class VehicleSpec:
    name: str
    length_m: float
    width_m: float
    mass_kg: float


@dataclass
class VehicleState:
    s_m: float  # arc length along track centerline
    v_mps: float
    a_mps2: float


class Vehicle:
    def __init__(self, spec: VehicleSpec, state: VehicleState, color_rgb: tuple[int, int, int] | None = None):
        self.spec = spec
        self.state = state
        self.color_rgb: tuple[int, int, int] = color_rgb or (100, 180, 255)


