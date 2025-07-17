"""
Headless Simulation Mode for Multiprocessing

This module provides a headless version of the simulation that can be safely
pickled for multiprocessing. It separates simulation logic from rendering
dependencies (Arcade/Pymunk) to avoid pickle errors.

Usage:
    from traffic_sim.core.simulation_headless import SimulationHeadless

    # Create headless simulation
    sim = SimulationHeadless(config)

    # Run simulation steps
    for _ in range(1000):
        sim.step(0.02)

    # Get results
    results = sim.get_results()
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import random
import numpy as np

from traffic_sim.core.track import StadiumTrack
from traffic_sim.config.loader import get_nested
from traffic_sim.core.vehicle import Vehicle, VehicleSpec, VehicleState
from traffic_sim.models.vehicle_specs import DEFAULT_CATALOG
from traffic_sim.core.driver import sample_driver_params, Driver
from traffic_sim.core.perception import PerceptionData
from traffic_sim.core.analytics import LiveAnalytics
from traffic_sim.core.logging import DataLogger
from traffic_sim.core.performance import get_performance_optimizer, pre_sort_vehicles
from traffic_sim.core.profiling import get_profiler
from traffic_sim.core.data_manager import VehicleDataManager
from traffic_sim.core.physics_numpy import PhysicsEngineNumpy
from traffic_sim.core.idm_vectorized import idm_accel_fallback_next_vehicle


@dataclass
class SimulationResults:
    """Results from headless simulation run."""

    simulation_time: float
    vehicle_count: int
    vehicles: List[Vehicle]
    perception_data: List[Optional[PerceptionData]]
    analytics_data: Dict[str, Any]
    performance_metrics: Dict[str, float]
    collision_events: List[Dict[str, Any]]
    step_count: int
    total_elapsed_time: float


class CollisionSystemHeadless:
    """Headless collision system without Pymunk dependencies."""

    def __init__(self, config: Dict[str, Any], track: StadiumTrack):
        self.config = config
        self.track = track
        self.collision_events: List[Dict[str, Any]] = []

        # Collision configuration
        self.use_pymunk_impulse = config.get("collisions", {}).get("use_pymunk_impulse", False)
        self.disable_time_s = config.get("collisions", {}).get("disable_time_s", 5.0)
        self.lateral_push = config.get("collisions", {}).get("lateral_push", True)

    def add_vehicle(self, vehicle: Vehicle, vehicle_id: int) -> None:
        """Add vehicle to collision system (headless version)."""
        # In headless mode, we don't need Pymunk physics
        # Just track collision events based on proximity
        pass

    def update_vehicle(self, vehicle: Vehicle, vehicle_id: int) -> None:
        """Update vehicle in collision system (headless version)."""
        # In headless mode, we don't need Pymunk physics
        pass

    def check_collisions(self, vehicles: List[Vehicle]) -> List[Dict[str, Any]]:
        """Check for collisions using simple proximity detection."""
        collision_events = []

        for i, vehicle1 in enumerate(vehicles):
            for j, vehicle2 in enumerate(vehicles[i + 1 :], i + 1):
                # Simple collision detection based on distance
                distance = abs(vehicle1.state.s_m - vehicle2.state.s_m)
                if distance < 5.0:  # 5m collision threshold
                    collision_events.append(
                        {
                            "vehicle1_id": i,
                            "vehicle2_id": j,
                            "distance": distance,
                            "timestamp": 0.0,  # Will be set by caller
                        }
                    )

        return collision_events

    def step_physics(self, dt_s: float) -> None:
        """Step physics simulation (headless version)."""
        # In headless mode, we don't need Pymunk physics
        pass

    def get_vehicle_visual_state(self, vehicle_id: int) -> Dict[str, Any]:
        """Get vehicle visual state (headless version)."""
        return {
            "is_disabled": False,
            "blink_state": False,
            "alpha": 1.0,
        }


class SimulationHeadless:
    """Headless simulation without rendering dependencies."""

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
        self.collision_system = CollisionSystemHeadless(cfg, self.track)
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
        self.step_count = 0
        self.total_elapsed_time = 0.0

        # NumPy-based physics engine integration (Phase 3)
        self._use_numpy_physics = bool(get_nested(cfg, "physics.numpy_engine_enabled", False))
        self.numpy_physics_engine = None
        if self._use_numpy_physics:
            # Placeholder: initialize with empty arrays, will be set up in future steps
            self.numpy_physics_engine = PhysicsEngineNumpy(
                vehicle_specs=np.empty((0,)), initial_state=np.empty((0,))
            )

    def _spawn_initial_vehicles(self) -> None:
        """Spawn initial vehicles for the simulation."""
        vehicle_count = int(get_nested(self.cfg, "vehicles.count", 20))
        vehicle_mix = get_nested(self.cfg, "vehicles.mix", {"sedan": 1.0})

        # Set random seeds for reproducibility
        master_seed = get_nested(self.cfg, "random.master_seed", 42)
        if master_seed is None:
            master_seed = 42
        master_seed = int(master_seed)

        color_seed = get_nested(self.cfg, "vehicles.color_random_seed", 42)
        if color_seed is None:
            color_seed = 42
        color_seed = int(color_seed)

        random.seed(master_seed)
        np.random.seed(master_seed)

        for i in range(vehicle_count):
            # Sample vehicle type from mix
            vehicle_type = np.random.choice(list(vehicle_mix.keys()), p=list(vehicle_mix.values()))

            # Get vehicle spec from catalog
            spec = None
            for entry in DEFAULT_CATALOG:
                if entry.type == vehicle_type:
                    spec = entry
                    break

            if spec is None:
                # Fallback to sedan if type not found
                spec = DEFAULT_CATALOG[0]  # First sedan entry

            # Sample driver parameters
            rng = random.Random(master_seed + i)  # Different seed for each vehicle
            driver_params = sample_driver_params(self.cfg, rng)
            driver = Driver(driver_params, rng)

            # Create vehicle state
            state = VehicleState(
                s_m=float(i * 10.0),  # 10m spacing
                v_mps=float(np.random.uniform(20, 30)),  # 20-30 m/s initial speed
                a_mps2=0.0,
            )

            # Convert VehicleCatalogEntry to VehicleSpec
            vehicle_spec = VehicleSpec(
                name=spec.name,
                length_m=spec.length_m,
                width_m=spec.width_m,
                mass_kg=spec.mass_kg,
                power_kw=spec.power_kw,
                torque_nm=spec.torque_nm,
                drag_area_cda=spec.drag_area_cda,
                wheelbase_m=spec.wheelbase_m,
                tire_friction_mu=spec.tire_friction_mu,
                brake_efficiency_eta=spec.brake_efficiency_eta,
            )

            # Create vehicle
            vehicle = Vehicle(vehicle_spec, state, driver)
            self.vehicles.append(vehicle)
            self.drivers.append(driver)

            # Add to collision system
            self.collision_system.add_vehicle(vehicle, i)

    def step(self, dt_s: float) -> None:
        """Step the simulation forward by dt_s seconds."""
        import time

        start_time = time.perf_counter()

        # Apply speed factor
        eff_dt = dt_s * self.speed_factor

        # Use the global profiler dynamically in case tests reset it
        profiler = get_profiler() if self._profiling_enabled else None
        if self._profiling_enabled and profiler is not None:
            with profiler.time_block("pre_sort_vehicles"):
                self.vehicles = pre_sort_vehicles(self.vehicles, self.simulation_time)
        else:
            self.vehicles = pre_sort_vehicles(self.vehicles, self.simulation_time)

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

        # Update vehicles
        self._update_vehicles(eff_dt)

        # Update simulation time
        self.simulation_time += eff_dt
        self.step_count += 1

        # Update total elapsed time
        self.total_elapsed_time += time.perf_counter() - start_time

    def _update_perception_data(self, eff_dt: float) -> None:
        """Update perception data for all vehicles."""
        self.perception_data = []

        for i, vehicle in enumerate(self.vehicles):
            perception = self._calculate_perception(vehicle, i)
            self.perception_data.append(perception)

    def _calculate_perception(self, vehicle: Vehicle, vehicle_idx: int) -> Optional[PerceptionData]:
        """Calculate perception data for a vehicle."""
        # Find the next vehicle in front
        next_vehicle = None
        min_distance = float("inf")

        for j, other_vehicle in enumerate(self.vehicles):
            if j == vehicle_idx:
                continue

            # Calculate distance along track
            distance = other_vehicle.state.s_m - vehicle.state.s_m
            if distance > 0 and distance < min_distance:
                min_distance = distance
                next_vehicle = other_vehicle

        if next_vehicle is None or min_distance > self.visual_range_m:
            return None

        # Calculate SSD (Stopping Sight Distance)
        v_mps = vehicle.state.v_mps
        reaction_time = 2.5  # seconds
        deceleration = 3.0  # m/s^2

        ssd = v_mps * reaction_time + (v_mps**2) / (2 * deceleration)

        # Check if occluded (simplified)
        is_occluded = min_distance < ssd * 0.5

        return PerceptionData(
            leader_vehicle=next_vehicle,
            leader_distance_m=min_distance,
            ssd_required_m=ssd,
            is_occluded=is_occluded,
            visual_range_m=self.visual_range_m,
        )

    def _handle_collision_events(self, collision_events: List[Dict[str, Any]]) -> None:
        """Handle collision events."""
        for event in collision_events:
            # In headless mode, we just log the collision
            self.collision_system.collision_events.append(event)

    def _update_vehicles(self, eff_dt: float) -> None:
        """Update all vehicles in the simulation."""
        # Get performance flags
        high_perf = bool(get_nested(self.cfg, "high_performance.enabled", True))
        use_vec_idm = bool(get_nested(self.cfg, "idm.vectorized", True))

        # Get speed limit
        speed_limit_mps = float(get_nested(self.cfg, "physics.speed_limit_mps", 30.0))

        # Vectorized IDM acceleration calculation
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
                    # Create arrays for IDM parameters
                    desired_speed_mps = np.full(n_arr, 30.0)  # 30 m/s desired speed
                    headway_T_s = np.full(n_arr, 1.5)  # 1.5s headway
                    comfort_brake_mps2 = np.full(n_arr, 3.0)  # 3 m/s^2 comfort brake

                    vec_accels = idm_accel_fallback_next_vehicle(
                        s_arr,
                        v_arr,
                        desired_speed_mps,
                        headway_T_s,
                        comfort_brake_mps2,
                        self.a_max,
                        self.idm_delta,
                        self.track.total_length_m,
                    )
            else:
                n_arr = len(self.vehicles)
                s_arr = np.fromiter((v.state.s_m for v in self.vehicles), dtype=float, count=n_arr)
                v_arr = np.fromiter(
                    (v.state.v_mps for v in self.vehicles), dtype=float, count=n_arr
                )
                # Create arrays for IDM parameters
                desired_speed_mps = np.full(n_arr, 30.0)  # 30 m/s desired speed
                headway_T_s = np.full(n_arr, 1.5)  # 1.5s headway
                comfort_brake_mps2 = np.full(n_arr, 3.0)  # 3 m/s^2 comfort brake

                vec_accels = idm_accel_fallback_next_vehicle(
                    s_arr,
                    v_arr,
                    desired_speed_mps,
                    headway_T_s,
                    comfort_brake_mps2,
                    self.a_max,
                    self.idm_delta,
                    self.track.total_length_m,
                )

        # Update each vehicle
        for i, vehicle in enumerate(self.vehicles):
            # Update speeding state
            if self._profiling_enabled and self._profiler is not None:
                with self._profiler.time_block("driver_update_speeding_state"):
                    vehicle.driver.update_speeding_state(eff_dt, speed_limit_mps)
            else:
                vehicle.driver.update_speeding_state(eff_dt, speed_limit_mps)

            # Get perception data
            perception = self.perception_data[i] if i < len(self.perception_data) else None

            # Calculate acceleration
            if vec_accels is not None:
                vehicle.state.a_mps2 = float(vec_accels[i]) if i < len(vec_accels) else 0.0
            else:
                if self._profiling_enabled and self._profiler is not None:
                    with self._profiler.time_block("idm_acceleration"):
                        self._calculate_idm_acceleration(
                            vehicle,
                            perception,
                            speed_limit_mps,
                            len(self.vehicles),
                            self.track.total_length_m,
                        )
                else:
                    self._calculate_idm_acceleration(
                        vehicle,
                        perception,
                        speed_limit_mps,
                        len(self.vehicles),
                        self.track.total_length_m,
                    )

            # Update internal state (jerk limiting, drivetrain lag)
            if self._profiling_enabled and self._profiler is not None:
                with self._profiler.time_block("vehicle_update_internal_state"):
                    vehicle.update_internal_state(eff_dt)
            else:
                vehicle.update_internal_state(eff_dt)

            # Update vehicle physics
            will_defer_physics = (
                high_perf and self._use_data_manager and self.data_manager is not None
            )
            if not will_defer_physics:
                if self._profiling_enabled and self._profiler is not None:
                    with self._profiler.time_block("update_vehicle_physics"):
                        self._update_vehicle_physics(vehicle, eff_dt, self.track.total_length_m)
                else:
                    self._update_vehicle_physics(vehicle, eff_dt, self.track.total_length_m)

        # Update collision system
        if self._profiling_enabled and self._profiler is not None:
            with self._profiler.time_block("step_physics"):
                self.collision_system.step_physics(eff_dt)
        else:
            self.collision_system.step_physics(eff_dt)

    def _calculate_idm_acceleration(
        self,
        vehicle: Vehicle,
        perception: Optional[PerceptionData],
        speed_limit_mps: float,
        n: int,
        L: float,
    ) -> float:
        """Calculate IDM acceleration for a vehicle."""
        if perception is None:
            # No leader, use speed limit
            return 0.0

        # Simple IDM calculation
        v = vehicle.state.v_mps
        v_leader = perception.leader_vehicle.state.v_mps if perception.leader_vehicle else v
        s = perception.leader_distance_m

        # IDM parameters
        v0 = speed_limit_mps  # Desired speed
        T = 1.5  # Time headway
        a_max = 1.5  # Maximum acceleration
        b = 3.0  # Comfortable deceleration
        s0 = 2.0  # Minimum spacing

        # IDM formula
        s_star = s0 + v * T + (v * (v - v_leader)) / (2 * np.sqrt(a_max * b))
        a = a_max * (1 - (v / v0) ** 4 - (s_star / s) ** 2)

        return float(a)

    def _update_vehicle_physics(self, vehicle: Vehicle, eff_dt: float, L: float) -> None:
        """Update vehicle physics."""
        # Simple physics update
        vehicle.state.s_m += vehicle.state.v_mps * eff_dt
        vehicle.state.v_mps += vehicle.state.a_mps2 * eff_dt

        # Wrap around track
        if vehicle.state.s_m > L:
            vehicle.state.s_m -= L
        elif vehicle.state.s_m < 0:
            vehicle.state.s_m += L

    def get_results(self) -> SimulationResults:
        """Get simulation results."""
        return SimulationResults(
            simulation_time=self.simulation_time,
            vehicle_count=len(self.vehicles),
            vehicles=self.vehicles.copy(),
            perception_data=self.perception_data.copy(),
            analytics_data=self.analytics.get_performance_metrics(),
            performance_metrics={
                "steps_per_second": self.step_count / max(self.total_elapsed_time, 0.001),
                "total_elapsed_time": self.total_elapsed_time,
                "step_count": self.step_count,
            },
            collision_events=self.collision_system.collision_events.copy(),
            step_count=self.step_count,
            total_elapsed_time=self.total_elapsed_time,
        )
