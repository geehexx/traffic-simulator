from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional
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


@dataclass
class PerceptionData:
    """Perception data for a vehicle including occlusion and SSD information."""

    leader_vehicle: Optional[Vehicle]
    leader_distance_m: float
    is_occluded: bool
    ssd_required_m: float
    visual_range_m: float


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
        self.safety_speed_kmh = float(get_nested(cfg, "track.safety_design_speed_kmh", 120.0))
        self.speed_factor = float(get_nested(cfg, "physics.speed_factor", 1.0))

        # Perception configuration
        self.visual_range_m = float(get_nested(cfg, "perception.visual_range_m", 200.0))
        self.occlusion_resolution_m = float(
            get_nested(cfg, "perception.occlusion_check_resolution", 0.5)
        )
        self.ssd_safety_margin = float(get_nested(cfg, "perception.ssd_safety_margin", 1.2))
        self.min_ssd_m = float(get_nested(cfg, "perception.min_ssd_m", 2.0))

        self.vehicles: List[Vehicle] = []
        self.drivers: List[Driver] = []
        self.perception_data: List[PerceptionData] = []
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
            # Driver sampling with enhanced parameters
            dparams = sample_driver_params(self.cfg, rng_driver)
            driver = Driver(dparams, rng_driver)
            self.drivers.append(driver)
            self.vehicles.append(Vehicle(spec, state, driver, color_rgb=color))

        # Initialize perception data
        self.perception_data = [
            PerceptionData(None, 0.0, False, 0.0, self.visual_range_m)
            for _ in range(len(self.vehicles))
        ]

    def _find_first_unobstructed_leader(
        self, follower_idx: int
    ) -> Tuple[Optional[Vehicle], float, bool]:
        """
        Find the first unobstructed leader within visual range.
        Returns (leader_vehicle, distance_m, is_occluded).
        """
        if len(self.vehicles) <= 1:
            return None, 0.0, False

        follower = self.vehicles[follower_idx]
        L = self.track.total_length_m

        # Check vehicles ahead in order of distance
        for i in range(1, len(self.vehicles)):
            leader_idx = (follower_idx + i) % len(self.vehicles)
            leader = self.vehicles[leader_idx]

            # Calculate distance along track
            distance = (leader.state.s_m - follower.state.s_m) % L

            # Check if within visual range
            if distance > self.visual_range_m:
                break

            # Check for occlusion using simplified line-of-sight
            if self._is_line_of_sight_clear(follower, leader, distance):
                return leader, distance, False
            else:
                # This leader is occluded, continue to next
                continue

        # No unobstructed leader found within visual range
        return None, 0.0, True

    def _is_line_of_sight_clear(self, follower: Vehicle, leader: Vehicle, distance: float) -> bool:
        """
        Simplified line-of-sight check. For stadium track, we assume line-of-sight
        is clear unless there's a vehicle blocking the path.
        """
        if distance < 1.0:  # Very close, always visible
            return True

        # For stadium track, line-of-sight is generally clear unless there's
        # a vehicle between follower and leader
        L = self.track.total_length_m
        follower_s = follower.state.s_m
        leader_s = leader.state.s_m

        # Check if any vehicle is between follower and leader
        for vehicle in self.vehicles:
            if vehicle == follower or vehicle == leader:
                continue

            vehicle_s = vehicle.state.s_m
            # Check if vehicle is between follower and leader
            if self._is_between_positions(follower_s, leader_s, vehicle_s, L):
                return False

        return True

    def _is_between_positions(
        self, start: float, end: float, check: float, track_length: float
    ) -> bool:
        """Check if 'check' position is between 'start' and 'end' on the track."""
        if start <= end:
            return start < check < end
        else:  # Wrapped around track
            return check > start or check < end

    def _calculate_dynamic_ssd(
        self, follower: Vehicle, leader: Optional[Vehicle], distance_m: float
    ) -> float:
        """
        Calculate dynamic Stopping Sight Distance using relative speed.
        Formula: g_req = max(s0, d_r + v_f²/(2b_f) - v_ℓ²/(2b_ℓ))
        """
        if leader is None:
            return self.min_ssd_m

        # Reaction distance: d_r = v_f * t_r
        reaction_time = follower.driver.params.reaction_time_s
        reaction_distance = follower.state.v_mps * reaction_time

        # Follower and leader deceleration capabilities
        b_f = follower.driver.params.comfort_brake_mps2
        b_l = leader.driver.params.comfort_brake_mps2

        # Dynamic SSD calculation
        v_f = follower.state.v_mps
        v_l = leader.state.v_mps

        # g_req = max(s0, d_r + v_f²/(2b_f) - v_ℓ²/(2b_ℓ))
        s0 = 2.0  # Standstill buffer
        g_req = max(s0, reaction_distance + (v_f**2) / (2.0 * b_f) - (v_l**2) / (2.0 * b_l))

        # Apply safety margin
        g_req *= self.ssd_safety_margin

        # Ensure minimum SSD
        return float(max(g_req, self.min_ssd_m))

    def step(self, dt_s: float) -> None:
        """Enhanced IDM controller with per-driver parameters, jerk limiting, drivetrain lag, and occlusion-based perception."""
        n = len(self.vehicles)
        if n == 0:
            return

        # Sort vehicles by position for proper following behavior
        self.vehicles.sort(key=lambda vv: vv.state.s_m)
        L = self.track.total_length_m
        sf = max(0.0, float(self.speed_factor))
        eff_dt = dt_s * sf

        # Get speed limit from config
        speed_limit_kmh = float(get_nested(self.cfg, "track.speed_limit_kmh", 100.0))
        speed_limit_mps = speed_limit_kmh / 3.6

        # Update perception data for all vehicles
        for i, vehicle in enumerate(self.vehicles):
            leader, distance, is_occluded = self._find_first_unobstructed_leader(i)
            ssd_required = self._calculate_dynamic_ssd(vehicle, leader, distance)

            # Update perception data
            self.perception_data[i] = PerceptionData(
                leader_vehicle=leader,
                leader_distance_m=distance,
                is_occluded=is_occluded,
                ssd_required_m=ssd_required,
                visual_range_m=self.visual_range_m,
            )

        # Update each vehicle
        for i, vehicle in enumerate(self.vehicles):
            # Update speeding state
            vehicle.driver.update_speeding_state(eff_dt, speed_limit_mps)

            # Get effective speed limit (considering speeding)
            effective_speed_limit = vehicle.driver.get_effective_speed_limit(speed_limit_mps)

            # Get perception data for this vehicle
            perception = self.perception_data[i]

            # IDM controller with per-driver parameters and perception
            if n == 1:
                # Single vehicle: maintain desired speed
                v0 = vehicle.driver.params.desired_speed_mps
                a_max = self.a_max
                a = a_max * (1.0 - (vehicle.state.v_mps / max(0.1, v0)) ** self.idm_delta)
            else:
                # Multi-vehicle: IDM following behavior with perception
                if perception.leader_vehicle is not None and not perception.is_occluded:
                    # Use perceived leader and SSD
                    leader = perception.leader_vehicle
                    s_gap = perception.leader_distance_m
                    ssd_required = perception.ssd_required_m
                else:
                    # Fallback to simple following (next vehicle in line)
                    leader_idx = (i + 1) % n
                    leader = self.vehicles[leader_idx]
                    s_gap = (leader.state.s_m - vehicle.state.s_m) % L
                    ssd_required = self.min_ssd_m

                # Per-driver parameters
                T = vehicle.driver.params.headway_T_s
                s0 = 2.0  # Standstill buffer (could be per-vehicle)
                b_comf = vehicle.driver.params.comfort_brake_mps2
                v0 = min(vehicle.driver.params.desired_speed_mps, effective_speed_limit)
                a_max = self.a_max

                # IDM desired gap - use SSD when available
                delta_v = vehicle.state.v_mps - leader.state.v_mps
                if perception.leader_vehicle is not None and not perception.is_occluded:
                    # Use SSD-based desired gap
                    s_star = max(ssd_required, s0 + vehicle.state.v_mps * T)
                else:
                    # Standard IDM desired gap
                    s_star = (
                        s0
                        + vehicle.state.v_mps * T
                        + (vehicle.state.v_mps * delta_v)
                        / (2.0 * (a_max**0.5) * (b_comf**0.5) + 1e-6)
                    )

                # IDM acceleration
                a = a_max * (
                    1.0
                    - (vehicle.state.v_mps / max(0.1, v0)) ** self.idm_delta
                    - (s_star / max(0.1, s_gap)) ** 2
                )

            # Set commanded acceleration
            vehicle.set_commanded_acceleration(a)

            # Update internal state (jerk limiting, drivetrain lag)
            vehicle.update_internal_state(eff_dt)

            # Update position and velocity
            v_new = max(0.0, vehicle.state.v_mps + vehicle.state.a_mps2 * eff_dt)
            s_new = (vehicle.state.s_m + v_new * eff_dt) % L

            vehicle.state.s_m = s_new
            vehicle.state.v_mps = v_new
