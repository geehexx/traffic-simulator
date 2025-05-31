from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np


@dataclass
class VehicleDataView:
    """Lightweight view to a vehicle's row in the arrays."""

    index: int


class VehicleDataManager:
    """Pre-allocated, cache-friendly storage for vehicle state vectors.

    Layout (row-major):
      - positions: (N, 2) -> x, y (meters) or (s, 0) for track-based
      - velocities: (N, 2)
      - accelerations: (N, 2)
      - lengths: (N,)
      - widths: (N,)
      - active_mask: (N,)
    """

    def __init__(self, max_vehicles: int = 10000) -> None:
        self.max_vehicles = int(max_vehicles)
        self.positions = np.zeros((self.max_vehicles, 2), dtype=np.float32)
        self.velocities = np.zeros((self.max_vehicles, 2), dtype=np.float32)
        self.accelerations = np.zeros((self.max_vehicles, 2), dtype=np.float32)
        self.lengths = np.zeros(self.max_vehicles, dtype=np.float32)
        self.widths = np.zeros(self.max_vehicles, dtype=np.float32)
        self.active_mask = np.zeros(self.max_vehicles, dtype=bool)
        self.vehicle_count = 0

    def allocate(
        self,
        length_m: float,
        width_m: float,
        pos: Tuple[float, float] = (0.0, 0.0),
        vel: Tuple[float, float] = (0.0, 0.0),
    ) -> Optional[VehicleDataView]:
        if self.vehicle_count >= self.max_vehicles:
            return None
        i = self.vehicle_count
        self.vehicle_count += 1

        self.positions[i, :] = pos
        self.velocities[i, :] = vel
        self.accelerations[i, :] = 0.0
        self.lengths[i] = float(length_m)
        self.widths[i] = float(width_m)
        self.active_mask[i] = True
        return VehicleDataView(index=i)

    def free(self, view: VehicleDataView) -> None:
        i = view.index
        if 0 <= i < self.vehicle_count:
            self.active_mask[i] = False

    def step_kinematics(self, dt_s: float) -> None:
        # v += a * dt; x += v*dt + 0.5*a*dt^2
        a_active = self.accelerations[self.active_mask]
        v_active = self.velocities[self.active_mask]
        self.positions[self.active_mask] += v_active * dt_s + 0.5 * a_active * dt_s * dt_s
        self.velocities[self.active_mask] += a_active * dt_s
