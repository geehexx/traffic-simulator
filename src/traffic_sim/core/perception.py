from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from traffic_sim.core.vehicle import Vehicle


@dataclass
class PerceptionData:
    """Perception data for a vehicle including occlusion and SSD information."""

    leader_vehicle: Optional[Vehicle]
    leader_distance_m: float
    is_occluded: bool
    ssd_required_m: float
    visual_range_m: float
