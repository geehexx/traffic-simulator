from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import random

from traffic_sim.core.track import StadiumTrack
from traffic_sim.config.loader import get_nested
from traffic_sim.core.vehicle import Vehicle, VehicleSpec, VehicleState
from traffic_sim.models.vehicle_specs import DEFAULT_CATALOG
from traffic_sim.core.driver import sample_driver_params, Driver


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
        self.speed_factor = float(get_nested(cfg, "physics.speed_factor", 1.0))

        self.vehicles: List[Vehicle] = []
        self.drivers: List[Driver] = []
        self._spawn_initial_vehicles()
        self.idm_delta = 4.0
        self.a_max = 1.5  # m/s^2 (scaffold)

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

    def _spawn_initial_vehicles(self) -> None:
        count = int(get_nested(self.cfg, "vehicles.count", 20))
        color_seed = get_nested(self.cfg, "vehicles.color_random_seed", None)
        rng_color = random.Random(color_seed) if color_seed is not None else random.Random()
        driver_seed = get_nested(self.cfg, "random.master_seed", None)
        rng_driver = random.Random(driver_seed) if driver_seed is not None else random.Random()
        L = self.track.total_length_m
        spacing = L / max(1, count)
        for i in range(count):
            entry = DEFAULT_CATALOG[i % len(DEFAULT_CATALOG)]
            spec = VehicleSpec(
                name=entry.name,
                length_m=entry.length_m,
                width_m=entry.width_m,
                mass_kg=entry.mass_kg,
            )
            state = VehicleState(s_m=i * spacing, v_mps=20.0, a_mps2=0.0)
            color = (
                rng_color.randint(40, 230),
                rng_color.randint(40, 230),
                rng_color.randint(40, 230),
            )
            self.vehicles.append(Vehicle(spec, state, color_rgb=color))
            # Driver sampling (placeholder parameters)
            dparams = sample_driver_params(self.cfg, rng_driver)
            self.drivers.append(Driver(dparams))

    def step(self, dt_s: float) -> None:
        # Simple IDM-like single-lane behavior
        n = len(self.vehicles)
        if n == 0:
            return
        if n == 1:
            # Uniform motion for single vehicle to keep baseline and tests stable
            v0 = self.vehicles[0]
            eff_dt = dt_s * max(0.0, float(self.speed_factor))
            v0.state.s_m = (v0.state.s_m + v0.state.v_mps * eff_dt) % self.track.total_length_m
            v0.state.a_mps2 = 0.0
            return
        self.vehicles.sort(key=lambda vv: vv.state.s_m)
        L = self.track.total_length_m
        sf = max(0.0, float(self.speed_factor))
        eff_dt = dt_s * sf
        leaders = [(i + 1) % n for i in range(n)]
        new_states: List[Tuple[float, float, float]] = []
        for i, v in enumerate(self.vehicles):
            leader = self.vehicles[leaders[i]]
            s_gap = (leader.state.s_m - v.state.s_m) % L
            T = 1.5
            s0 = 2.0
            b_comf = 2.5
            v0 = 27.0
            s_star = s0 + v.state.v_mps * T + (v.state.v_mps * (v.state.v_mps - leader.state.v_mps)) / (
                2.0 * (self.a_max ** 0.5) * (b_comf ** 0.5) + 1e-6
            )
            a = self.a_max * (
                1.0
                - (v.state.v_mps / max(0.1, v0)) ** self.idm_delta
                - (s_star / max(0.1, s_gap)) ** 2
            )
            v_new = max(0.0, v.state.v_mps + a * eff_dt)
            s_new = (v.state.s_m + v_new * eff_dt) % L
            new_states.append((s_new, v_new, a))
        for v, (s_new, v_new, a) in zip(self.vehicles, new_states):
            v.state.s_m, v.state.v_mps, v.state.a_mps2 = s_new, v_new, a


