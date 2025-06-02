from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional
import random
import numpy as np

from traffic_sim.core.track import StadiumTrack
from traffic_sim.config.loader import get_nested
from traffic_sim.core.vehicle import Vehicle, VehicleSpec, VehicleState
from traffic_sim.models.vehicle_specs import DEFAULT_CATALOG, VehicleCatalogEntry
from traffic_sim.core.driver import sample_driver_params, Driver
from traffic_sim.core.perception import PerceptionData
from traffic_sim.core.analytics import LiveAnalytics
from traffic_sim.core.collision import CollisionSystem
from traffic_sim.core.logging import DataLogger
from traffic_sim.core.performance import get_performance_optimizer, pre_sort_vehicles
from traffic_sim.core.profiling import get_profiler
from traffic_sim.core.data_manager import VehicleDataManager
from traffic_sim.core.physics_vectorized import step_arc_kinematics
from traffic_sim.core.physics_numpy import PhysicsEngineNumpy
from traffic_sim.core.idm_vectorized import idm_accel_fallback_next_vehicle


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
        self.safety_speed_kmh = float(get_nested(cfg, "track.safety_design_speed_kmh", 120.0))
        self.speed_factor = float(get_nested(cfg, "physics.speed_factor", 1.0))

        # Perception configuration
        self.visual_range_m = float(get_nested(cfg, "perception.visual_range_m", 200.0))
        self.occlusion_resolution_m = float(
            get_nested(cfg, "perception.occlusion_check_resolution", 0.5)
        )
        self.ssd_safety_margin = float(get_nested(cfg, "perception.ssd_safety_margin", 1.2))
        self.min_ssd_m = float(get_nested(cfg, "perception.min_ssd_m", 2.0))

        # Window-limited occlusion config
        self.window_enabled = bool(get_nested(cfg, "perception.window_enabled", False))
        self.window_neighbors = int(get_nested(cfg, "perception.window_neighbors", 5))

        self.vehicles: List[Vehicle] = []
        self.drivers: List[Driver] = []
        self.perception_data: List[Optional[PerceptionData]] = []
        self.analytics = LiveAnalytics(cfg)
        self.collision_system = CollisionSystem(cfg, self.track)
        self.data_logger = DataLogger(cfg)
        self.performance_optimizer = get_performance_optimizer()
        # Profiling
        self._profiling_enabled = bool(get_nested(cfg, "profiling.enabled", False))
        self._profiler = get_profiler() if self._profiling_enabled else None
        # Phase 2 data manager flag
        self._use_data_manager = bool(get_nested(cfg, "data_manager.enabled", False))
        self.data_manager = (
            VehicleDataManager(int(get_nested(cfg, "data_manager.max_vehicles", 10000)))
            if self._use_data_manager
            else None
        )
        self._spawn_initial_vehicles()
        self.idm_delta = 4.0
        self.simulation_time = 0.0
        self.a_max = 1.5  # m/s^2 (scaffold)

        # NumPy-based physics engine integration (Phase 3)
        self._use_numpy_physics = bool(get_nested(cfg, "physics.numpy_engine_enabled", False))
        self.numpy_physics_engine = None
        if self._use_numpy_physics:
            # Placeholder: initialize with empty arrays, will be set up in future steps
            self.numpy_physics_engine = PhysicsEngineNumpy(
                vehicle_specs=np.empty((0,)), initial_state=np.empty((0,))
            )

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

    def _sample_vehicle_by_mix(self, rng: random.Random) -> VehicleCatalogEntry:
        """Sample a vehicle from the catalog based on configured mix percentages."""
        mix_config = get_nested(self.cfg, "vehicles.mix", {})

        # Create weighted list of vehicle types
        vehicle_types = []
        for vehicle_type, percentage in mix_config.items():
            count = int(percentage * 100)  # Convert to integer for sampling
            vehicle_types.extend([vehicle_type] * count)

        # Sample vehicle type
        if not vehicle_types:
            # Fallback to equal distribution if no mix configured
            vehicle_types = ["sedan", "suv", "truck_van", "bus", "motorbike"]

        selected_type = rng.choice(vehicle_types)

        # Find vehicles of the selected type
        available_vehicles = [v for v in DEFAULT_CATALOG if v.type == selected_type]

        if not available_vehicles:
            # Fallback to any vehicle if type not found
            available_vehicles = list(DEFAULT_CATALOG)

        return rng.choice(available_vehicles)

    def _spawn_initial_vehicles(self) -> None:
        count = int(get_nested(self.cfg, "vehicles.count", 20))
        color_seed = get_nested(self.cfg, "vehicles.color_random_seed", None)
        rng_color = random.Random(color_seed) if color_seed is not None else random.Random()
        driver_seed = get_nested(self.cfg, "random.master_seed", None)
        rng_driver = random.Random(driver_seed) if driver_seed is not None else random.Random()
        L = self.track.total_length_m
        spacing = L / max(1, count)
        for i in range(count):
            entry = self._sample_vehicle_by_mix(rng_driver)
            spec = VehicleSpec(
                name=entry.name,
                length_m=entry.length_m,
                width_m=entry.width_m,
                mass_kg=entry.mass_kg,
                power_kw=entry.power_kw,
                torque_nm=entry.torque_nm,
                drag_area_cda=entry.drag_area_cda,
                wheelbase_m=entry.wheelbase_m,
                tire_friction_mu=entry.tire_friction_mu,
                brake_efficiency_eta=entry.brake_efficiency_eta,
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
            vehicle = Vehicle(spec, state, driver, color_rgb=color)
            self.vehicles.append(vehicle)

            # Add vehicle to collision system
            self.collision_system.add_vehicle(vehicle, i)

        # Initialize perception data to match actual vehicle count
        self.perception_data = [
            PerceptionData(None, 0.0, False, 0.0, self.visual_range_m)
            for _ in range(len(self.vehicles))
        ]

    def _find_first_unobstructed_leader(
        self, follower_idx: int
    ) -> Tuple[Optional[Vehicle], float, bool]:
        """
        Find the first unobstructed leader within visual range.
        If window_enabled, only check up to window_neighbors ahead.
        Returns (leader_vehicle, distance_m, is_occluded).
        """
        if len(self.vehicles) <= 1:
            return None, 0.0, False

        follower = self.vehicles[follower_idx]
        L = self.track.total_length_m

        max_neighbors = len(self.vehicles) - 1
        if self.window_enabled:
            max_neighbors = min(self.window_neighbors, len(self.vehicles) - 1)

        # Check vehicles ahead in order of distance, up to max_neighbors
        for i in range(1, max_neighbors + 1):
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

        # No unobstructed leader found within visual range (or window)
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

    def _update_perception_data(self, eff_dt: float) -> None:
        """Update perception data for all vehicles."""
        for i, vehicle in enumerate(self.vehicles):
            leader, distance, is_occluded = self._find_first_unobstructed_leader(i)
            ssd_required = self._calculate_dynamic_ssd(vehicle, leader, distance)

            self.perception_data[i] = PerceptionData(
                leader_vehicle=leader,
                leader_distance_m=distance,
                is_occluded=is_occluded,
                ssd_required_m=ssd_required,
                visual_range_m=self.visual_range_m,
            )

    def _handle_collision_events(self, collision_events: List[Any]) -> None:
        """Handle collision events by logging them."""
        for event in collision_events:
            self.analytics.log_incident(
                event_type="collision",
                vehicle_id=event.vehicle1_id,
                location_m=event.location_m,
                speed_mps=self.vehicles[event.vehicle1_id].state.v_mps,
                acceleration_mps2=self.vehicles[event.vehicle1_id].state.a_mps2,
                delta_v=event.delta_v,
                ttc_at_impact=event.ttc_at_impact,
            )
            self.data_logger.log_collision(event)

    def _calculate_idm_acceleration(
        self,
        vehicle: Vehicle,
        perception: Optional[PerceptionData],
        effective_speed_limit: float,
        n: int,
        L: float,
    ) -> float:
        """Calculate IDM acceleration for a vehicle."""
        if n == 1:
            # Single vehicle: maintain desired speed
            v0 = vehicle.driver.params.desired_speed_mps
            a_max = self.a_max
            return float(a_max * (1.0 - (vehicle.state.v_mps / max(0.1, v0)) ** self.idm_delta))

        # Multi-vehicle: IDM following behavior with perception
        if (
            perception is not None
            and perception.leader_vehicle is not None
            and not perception.is_occluded
        ):
            # Use perceived leader and SSD
            leader = perception.leader_vehicle
            s_gap = perception.leader_distance_m
            ssd_required = perception.ssd_required_m
        else:
            # Fallback to simple following (next vehicle in line)
            vehicle_idx = self.vehicles.index(vehicle)
            leader_idx = (vehicle_idx + 1) % n
            leader = self.vehicles[leader_idx]
            s_gap = (leader.state.s_m - vehicle.state.s_m) % L
            ssd_required = self.min_ssd_m

        # Per-driver parameters
        T = vehicle.driver.params.headway_T_s
        s0 = 2.0  # Standstill buffer
        b_comf = vehicle.driver.params.comfort_brake_mps2
        v0 = min(vehicle.driver.params.desired_speed_mps, effective_speed_limit)
        a_max = self.a_max

        # IDM desired gap - use SSD when available
        delta_v = vehicle.state.v_mps - leader.state.v_mps
        if (
            perception is not None
            and perception.leader_vehicle is not None
            and not perception.is_occluded
        ):
            # Use SSD-based desired gap
            s_star = max(ssd_required, s0 + vehicle.state.v_mps * T)
        else:
            # Standard IDM desired gap
            s_star = (
                s0
                + vehicle.state.v_mps * T
                + (vehicle.state.v_mps * delta_v) / (2.0 * (a_max**0.5) * (b_comf**0.5) + 1e-6)
            )

        # IDM acceleration
        idm_accel = float(
            a_max
            * (
                1.0
                - (vehicle.state.v_mps / max(0.1, v0)) ** self.idm_delta
                - (s_star / max(0.1, s_gap)) ** 2
            )
        )

        # Apply physical constraints
        gravity_mps2 = float(get_nested(self.cfg, "physics.gravity_mps2", 9.81))
        return vehicle.apply_physical_constraints(idm_accel, gravity_mps2)

    def _update_vehicle_physics(self, vehicle: Vehicle, eff_dt: float, L: float) -> None:
        """Update vehicle physics (position, velocity, collision system)."""
        # Calculate aerodynamic drag force
        drag_force = vehicle.calculate_aerodynamic_drag_force(vehicle.state.v_mps)
        drag_accel = -drag_force / vehicle.spec.mass_kg  # Negative because it opposes motion

        # Apply drag to acceleration
        total_accel = vehicle.state.a_mps2 + drag_accel

        # Update position and velocity
        v_new = max(0.0, vehicle.state.v_mps + total_accel * eff_dt)
        s_new = (vehicle.state.s_m + v_new * eff_dt) % L

        vehicle.state.s_m = s_new
        vehicle.state.v_mps = v_new

        # Update collision system
        vehicle_idx = self.vehicles.index(vehicle)
        self.collision_system.update_vehicle_position(vehicle, vehicle_idx)

    def step(self, dt_s: float) -> None:
        """Enhanced IDM controller with per-driver parameters, jerk limiting, drivetrain lag, and occlusion-based perception."""
        n = len(self.vehicles)
        if n == 0:
            return

        # Update simulation time
        self.simulation_time += dt_s
        # Inform collision system of current time (for scheduler)
        if hasattr(self.collision_system, "update_time"):
            self.collision_system.update_time(self.simulation_time)

        # Pre-sort vehicles by position for proper following behavior (with caching)
        # Use the global profiler dynamically in case tests reset it
        profiler = get_profiler() if self._profiling_enabled else None
        if self._profiling_enabled and profiler is not None:
            with profiler.time_block("pre_sort_vehicles"):
                self.vehicles = pre_sort_vehicles(self.vehicles, self.simulation_time)
        else:
            self.vehicles = pre_sort_vehicles(self.vehicles, self.simulation_time)
        L = self.track.total_length_m
        sf = max(0.0, float(self.speed_factor))
        eff_dt = dt_s * sf

        # Get speed limit from config
        speed_limit_kmh = float(get_nested(self.cfg, "track.speed_limit_kmh", 100.0))
        speed_limit_mps = speed_limit_kmh / 3.6

        # Update perception data for all vehicles
        if self._profiling_enabled and profiler is not None:
            with profiler.time_block("update_perception"):
                self._update_perception_data(eff_dt)
        else:
            self._update_perception_data(eff_dt)

        # Update analytics
        if self._profiling_enabled and profiler is not None:
            with profiler.time_block("update_analytics"):
                self.analytics.update_analytics(self.vehicles, self.perception_data, eff_dt)
        else:
            self.analytics.update_analytics(self.vehicles, self.perception_data, eff_dt)

        # Check for collisions
        if self._profiling_enabled and profiler is not None:
            with profiler.time_block("check_collisions"):
                collision_events = self.collision_system.check_collisions(self.vehicles)
        else:
            collision_events = self.collision_system.check_collisions(self.vehicles)

        if self._profiling_enabled and profiler is not None:
            with profiler.time_block("handle_collision_events"):
                self._handle_collision_events(collision_events)
        else:
            self._handle_collision_events(collision_events)

        # Log simulation step data
        if self._profiling_enabled and profiler is not None:
            with profiler.time_block("log_step"):
                self.data_logger.log_simulation_step(
                    self.vehicles, self.perception_data, self.analytics, eff_dt
                )
        else:
            self.data_logger.log_simulation_step(
                self.vehicles, self.perception_data, self.analytics, eff_dt
            )

        # Update each vehicle
        # Optional vectorized IDM (fallback leader = next vehicle)
        use_vec_idm = bool(get_nested(self.cfg, "high_performance.idm_vectorized", False))
        vec_accels = None
        if use_vec_idm:
            if self._profiling_enabled and self._profiler is not None:
                with self._profiler.time_block("idm_acceleration_vectorized"):
                    n_arr = len(self.vehicles)
                    s_arr = np.fromiter(
                        (v.state.s_m for v in self.vehicles), dtype=float, count=n_arr
                    )
                    v_arr = np.fromiter(
                        (v.state.v_mps for v in self.vehicles), dtype=float, count=n_arr
                    )
                    v0_arr = np.fromiter(
                        (
                            min(v.driver.params.desired_speed_mps, speed_limit_mps)
                            for v in self.vehicles
                        ),
                        dtype=float,
                        count=n_arr,
                    )
                    T_arr = np.fromiter(
                        (v.driver.params.headway_T_s for v in self.vehicles),
                        dtype=float,
                        count=n_arr,
                    )
                    b_arr = np.fromiter(
                        (v.driver.params.comfort_brake_mps2 for v in self.vehicles),
                        dtype=float,
                        count=n_arr,
                    )
                    vec_accels = idm_accel_fallback_next_vehicle(
                        s_arr, v_arr, v0_arr, T_arr, b_arr, self.a_max, self.idm_delta, L
                    )
            else:
                n_arr = len(self.vehicles)
                s_arr = np.fromiter((v.state.s_m for v in self.vehicles), dtype=float, count=n_arr)
                v_arr = np.fromiter(
                    (v.state.v_mps for v in self.vehicles), dtype=float, count=n_arr
                )
                v0_arr = np.fromiter(
                    (
                        min(v.driver.params.desired_speed_mps, speed_limit_mps)
                        for v in self.vehicles
                    ),
                    dtype=float,
                    count=n_arr,
                )
                T_arr = np.fromiter(
                    (v.driver.params.headway_T_s for v in self.vehicles), dtype=float, count=n_arr
                )
                b_arr = np.fromiter(
                    (v.driver.params.comfort_brake_mps2 for v in self.vehicles),
                    dtype=float,
                    count=n_arr,
                )
                vec_accels = idm_accel_fallback_next_vehicle(
                    s_arr, v_arr, v0_arr, T_arr, b_arr, self.a_max, self.idm_delta, L
                )

        for i, vehicle in enumerate(self.vehicles):
            # Update speeding state
            if self._profiling_enabled and profiler is not None:
                with profiler.time_block("driver_update_speeding_state"):
                    vehicle.driver.update_speeding_state(eff_dt, speed_limit_mps)
            else:
                vehicle.driver.update_speeding_state(eff_dt, speed_limit_mps)

            # Get effective speed limit (considering speeding)
            effective_speed_limit = vehicle.driver.get_effective_speed_limit(speed_limit_mps)

            # Get perception data for this vehicle
            perception = self.perception_data[i]

            # Calculate IDM acceleration (vectorized fallback if enabled and perception occluded/absent)
            if use_vec_idm and (
                perception is None or perception.leader_vehicle is None or perception.is_occluded
            ):
                a = float(vec_accels[i]) if vec_accels is not None else 0.0
            else:
                if self._profiling_enabled and self._profiler is not None:
                    with self._profiler.time_block("idm_acceleration"):
                        a = self._calculate_idm_acceleration(
                            vehicle, perception, effective_speed_limit, n, L
                        )
                else:
                    a = self._calculate_idm_acceleration(
                        vehicle, perception, effective_speed_limit, n, L
                    )

            # Set commanded acceleration
            vehicle.set_commanded_acceleration(a)

            # Update internal state (jerk limiting, drivetrain lag)
            if self._profiling_enabled and profiler is not None:
                with profiler.time_block("vehicle_update_internal_state"):
                    vehicle.update_internal_state(eff_dt)
            else:
                vehicle.update_internal_state(eff_dt)

            # Update physics immediately unless we will defer to a vectorized engine
            will_defer_physics = self._use_numpy_physics or (
                bool(get_nested(self.cfg, "high_performance.enabled", False))
                and self._use_data_manager
            )
            if not will_defer_physics:
                if self._profiling_enabled and profiler is not None:
                    with profiler.time_block("update_vehicle_physics"):
                        self._update_vehicle_physics(vehicle, eff_dt, L)
                else:
                    self._update_vehicle_physics(vehicle, eff_dt, L)

        # Step physics simulation
        high_perf = bool(get_nested(self.cfg, "high_performance.enabled", False))
        if self._use_numpy_physics and self.numpy_physics_engine is not None:
            # Prepare arrays for NumPy engine
            n = len(self.vehicles)
            # Build vehicle_specs array: [mass_kg, power_kw, torque_nm, drag_area_cda, tire_friction_mu, brake_efficiency_eta]
            specs = np.zeros((n, 6), dtype=float)
            for i, v in enumerate(self.vehicles):
                specs[i, 0] = v.spec.mass_kg
                specs[i, 1] = v.spec.power_kw
                specs[i, 2] = v.spec.torque_nm
                specs[i, 3] = v.spec.drag_area_cda
                specs[i, 4] = v.spec.tire_friction_mu
                specs[i, 5] = v.spec.brake_efficiency_eta

            # Build state array: [s_m, v_mps, a_mps2, heading (optional, unused)]
            state = np.zeros((n, 4), dtype=float)
            for i, v in enumerate(self.vehicles):
                state[i, 0] = v.state.s_m
                state[i, 1] = v.state.v_mps
                state[i, 2] = v.state.a_mps2
                # state[i, 3] = 0.0  # heading unused

            # Commanded accelerations (from vehicle internal state)
            actions = np.array(
                [v.internal.commanded_accel_mps2 for v in self.vehicles], dtype=float
            )

            # (Re)initialize engine if vehicle count changes
            if (
                self.numpy_physics_engine.vehicle_specs.shape[0] != n
                or self.numpy_physics_engine.state.shape[0] != n
            ):
                self.numpy_physics_engine = PhysicsEngineNumpy(specs, state)
            else:
                self.numpy_physics_engine.vehicle_specs = specs
                self.numpy_physics_engine.state = state

            # Step physics
            updated_state = self.numpy_physics_engine.step(
                actions, eff_dt, track_length=self.track.total_length_m
            )

            # Write back to Vehicle objects
            for i, v in enumerate(self.vehicles):
                v.state.s_m = float(updated_state[i, 0])
                v.state.v_mps = float(updated_state[i, 1])
                v.state.a_mps2 = float(updated_state[i, 2])
        elif high_perf and self._use_data_manager and self.data_manager is not None:
            # Vectorized arc-length kinematics as Phase 3 groundwork
            if self._profiling_enabled and profiler is not None:
                with profiler.time_block("step_physics_vectorized"):
                    # Map current vehicle states into temporary arrays
                    n = len(self.vehicles)
                    s = np.fromiter((v.state.s_m for v in self.vehicles), dtype=float, count=n)
                    v_arr = np.fromiter(
                        (v.state.v_mps for v in self.vehicles), dtype=float, count=n
                    )
                    a_arr = np.fromiter(
                        (v.state.a_mps2 for v in self.vehicles), dtype=float, count=n
                    )
                    step_arc_kinematics(s, v_arr, a_arr, eff_dt, self.track.total_length_m)
                    # Write back
                    for i, veh in enumerate(self.vehicles):
                        veh.state.s_m = float(s[i])
                        veh.state.v_mps = float(v_arr[i])
            else:
                n = len(self.vehicles)
                s = np.fromiter((v.state.s_m for v in self.vehicles), dtype=float, count=n)
                v_arr = np.fromiter((v.state.v_mps for v in self.vehicles), dtype=float, count=n)
                a_arr = np.fromiter((v.state.a_mps2 for v in self.vehicles), dtype=float, count=n)
                step_arc_kinematics(s, v_arr, a_arr, eff_dt, self.track.total_length_m)
                for i, veh in enumerate(self.vehicles):
                    veh.state.s_m = float(s[i])
                    veh.state.v_mps = float(v_arr[i])
        else:
            if self._profiling_enabled and profiler is not None:
                with profiler.time_block("step_physics"):
                    self.collision_system.step_physics(eff_dt)
            else:
                self.collision_system.step_physics(eff_dt)

    def export_data(self, filename: Optional[str] = None) -> None:
        """Export all simulation data to CSV files."""
        self.data_logger.export_to_csv(filename)

    def get_logging_summary(self) -> Dict[str, Any]:
        """Get summary of logged data."""
        return self.data_logger.get_summary_stats()
