from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from traffic_sim.core.track import StadiumTrack
from traffic_sim.config.loader import get_nested
from traffic_sim.core.vehicle import Vehicle, VehicleSpec, VehicleState
from traffic_sim.models.vehicle_specs import DEFAULT_CATALOG


@dataclass
class SimulationConfig:
    length_m: float
    straight_fraction: float
    e: float
    f: float
    safety_design_speed_kmh: float


class Simulation:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        track_cfg = cfg.get("track", {})
        self.track = StadiumTrack(
            total_length_m=float(track_cfg.get("length_m", 1000.0)),
            straight_fraction=float(track_cfg.get("straight_fraction", 0.30)),
        )
        self.safety_e = float(get_nested(cfg, "track.superelevation_e", 0.08))
        self.safety_f = float(get_nested(cfg, "track.side_friction_f", 0.10))
        self.safety_speed_kmh = float(
            get_nested(cfg, "track.safety_design_speed_kmh", 120.0)
        )
        self.vehicles: List[Vehicle] = []
        self._spawn_initial_vehicles()

    def compute_safety_panel(self) -> Dict[str, float | bool]:
        r_cur, v_safe, l_needed, unsafe = self.track.warning_tuple(
            self.safety_speed_kmh, self.safety_e, self.safety_f
        )
        return {
            "radius_m": r_cur,
            "v_safe_kmh": v_safe,
            "length_needed_m": l_needed,
            "unsafe": unsafe,
        }

    # --- Spawning and updates (very simple scaffold) ---
    def _spawn_initial_vehicles(self) -> None:
        count = int(get_nested(self.cfg, "vehicles.count", 20))
        L = self.track.total_length
        spacing = L / max(1, count)
        # Use a subset of catalog entries, cycle if needed
        for i in range(count):
            entry = DEFAULT_CATALOG[i % len(DEFAULT_CATALOG)]
            spec = VehicleSpec(
                name=entry.name,
                length_m=entry.length_m,
                width_m=entry.width_m,
                mass_kg=entry.mass_kg,
            )
            state = VehicleState(s_m=i * spacing, v_mps=20.0, a_mps2=0.0)
            self.vehicles.append(Vehicle(spec, state))

    def step(self, dt_s: float) -> None:
        # Temporary scaffold: uniform motion around the loop
        for v in self.vehicles:
            v.state.s_m = (v.state.s_m + v.state.v_mps * dt_s) % self.track.total_length

    def vehicle_draw_data(self) -> List[Tuple[float, float, float, float, float]]:
        """Return list of (x,y,theta,length,width) for drawing."""
        out: List[Tuple[float, float, float, float, float]] = []
        for v in self.vehicles:
            x, y, theta = self.track.position_heading(v.state.s_m)
            out.append((x, y, theta, v.spec.length_m, v.spec.width_m))
        return out


