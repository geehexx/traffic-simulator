from __future__ import annotations

import csv
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path
from traffic_sim.core.vehicle import Vehicle
from traffic_sim.core.perception import PerceptionData
from traffic_sim.core.analytics import LiveAnalytics, IncidentLog, NearMissEvent
from traffic_sim.core.collision import CollisionEvent


@dataclass
class VehicleSnapshot:
    """Snapshot of vehicle state for logging."""

    timestamp: float
    vehicle_id: int
    position_m: float
    velocity_mps: float
    acceleration_mps2: float
    jerk_mps3: float
    is_speeding: bool
    overspeed_kmh: float
    leader_distance_m: float
    is_occluded: bool
    ssd_required_m: float
    driver_aggression: float
    driver_rule_adherence: float
    driver_reaction_time: float
    driver_headway: float


@dataclass
class SimulationSnapshot:
    """Snapshot of overall simulation state."""

    timestamp: float
    step_count: int
    total_vehicles: int
    avg_speed_kmh: float
    avg_headway_s: float
    near_miss_count: int
    collision_count: int
    fps: float
    memory_usage_mb: float


class DataLogger:
    """Comprehensive data logging system with CSV output."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logging_config = config.get("logging", {})

        # Output configuration
        self.output_path = Path(self.logging_config.get("output_path", "runs/run_001.csv"))
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # Logging rates
        self.aggregate_rate_hz = self.logging_config.get("aggregate_rate_hz", 10)
        self.per_vehicle_rate_hz = self.logging_config.get("per_vehicle_trace_rate_hz", 2)
        self.debug_rate_hz = self.logging_config.get("debug_rate_hz", 50)

        # Data storage
        self.vehicle_snapshots: List[VehicleSnapshot] = []
        self.simulation_snapshots: List[SimulationSnapshot] = []
        self.incident_log: List[IncidentLog] = []
        self.near_miss_events: List[NearMissEvent] = []
        self.collision_events: List[CollisionEvent] = []

        # Timing
        self.last_aggregate_log = 0.0
        self.last_vehicle_log = 0.0
        self.last_debug_log = 0.0
        self.step_count = 0

        # Performance tracking
        self.frame_times: List[float] = []
        self.memory_usage: List[float] = []

    def log_simulation_step(
        self,
        vehicles: List[Vehicle],
        perception_data: List[Optional[PerceptionData]],
        analytics: LiveAnalytics,
        dt_s: float,
    ) -> None:
        """Log simulation step data."""
        current_time = time.time()
        self.step_count += 1

        # Update performance metrics
        self._update_performance_metrics()

        # Aggregate logging (less frequent)
        if current_time - self.last_aggregate_log >= 1.0 / self.aggregate_rate_hz:
            self._log_aggregate_data(vehicles, perception_data, analytics, current_time)
            self.last_aggregate_log = current_time

        # Per-vehicle logging (more frequent)
        if current_time - self.last_vehicle_log >= 1.0 / self.per_vehicle_rate_hz:
            self._log_vehicle_data(vehicles, perception_data, current_time)
            self.last_vehicle_log = current_time

    def _update_performance_metrics(self) -> None:
        """Update performance tracking metrics."""
        # Placeholder values - would integrate with actual performance monitoring
        self.frame_times.append(1.0 / 60.0)  # Assume 60 FPS
        self.memory_usage.append(50.0)  # Assume 50MB

        # Keep only recent data
        if len(self.frame_times) > 1000:
            self.frame_times = self.frame_times[-500:]
        if len(self.memory_usage) > 1000:
            self.memory_usage = self.memory_usage[-500:]

    def _calculate_average_speed(self, vehicles: List[Vehicle]) -> float:
        """Calculate average speed of vehicles."""
        speeds = [v.state.v_mps * 3.6 for v in vehicles]  # Convert to km/h
        return sum(speeds) / len(speeds) if speeds else 0.0

    def _calculate_average_headway(
        self, vehicles: List[Vehicle], perception_data: List[Optional[PerceptionData]]
    ) -> float:
        """Calculate average headway from perception data."""
        headways = []
        for perception in perception_data:
            if self._is_valid_perception_for_headway(perception):
                # At this point we know perception is not None
                assert perception is not None
                headway = self._find_vehicle_headway(vehicles, perception)
                if headway is not None:
                    headways.append(headway)
        return sum(headways) / len(headways) if headways else 0.0

    def _is_valid_perception_for_headway(self, perception: Optional[PerceptionData]) -> bool:
        """Check if perception data is valid for headway calculation."""
        return (
            perception is not None
            and perception.leader_vehicle is not None
            and perception.leader_distance_m > 0
        )

    def _find_vehicle_headway(
        self, vehicles: List[Vehicle], perception: PerceptionData
    ) -> Optional[float]:
        """Find headway for a vehicle based on perception data."""
        for vehicle in vehicles:
            if hasattr(vehicle, "driver") and vehicle.state.v_mps > 0.1:
                return perception.leader_distance_m / vehicle.state.v_mps
        return None

    def _calculate_aggregate_stats(
        self, vehicles: List[Vehicle], perception_data: List[Optional[PerceptionData]]
    ) -> tuple[float, float]:
        """Calculate aggregate speed and headway statistics."""
        avg_speed = self._calculate_average_speed(vehicles)
        avg_headway = self._calculate_average_headway(vehicles, perception_data)
        return avg_speed, avg_headway

    def _calculate_performance_metrics(self) -> tuple[float, float]:
        """Calculate performance metrics."""
        fps = 1.0 / (sum(self.frame_times) / len(self.frame_times)) if self.frame_times else 0.0
        memory_mb = sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0.0
        return fps, memory_mb

    def _log_aggregate_data(
        self,
        vehicles: List[Vehicle],
        perception_data: List[Optional[PerceptionData]],
        analytics: LiveAnalytics,
        timestamp: float,
    ) -> None:
        """Log aggregate simulation data."""
        avg_speed, avg_headway = self._calculate_aggregate_stats(vehicles, perception_data)
        fps, memory_mb = self._calculate_performance_metrics()

        # Get analytics data
        near_miss_count = analytics.get_near_miss_count()
        collision_count = len(self.collision_events)

        snapshot = SimulationSnapshot(
            timestamp=timestamp,
            step_count=self.step_count,
            total_vehicles=len(vehicles),
            avg_speed_kmh=avg_speed,
            avg_headway_s=avg_headway,
            near_miss_count=near_miss_count,
            collision_count=collision_count,
            fps=fps,
            memory_usage_mb=memory_mb,
        )

        self.simulation_snapshots.append(snapshot)

    def _log_vehicle_data(
        self,
        vehicles: List[Vehicle],
        perception_data: List[Optional[PerceptionData]],
        timestamp: float,
    ) -> None:
        """Log per-vehicle data."""
        for i, (vehicle, perception) in enumerate(zip(vehicles, perception_data)):
            # Handle None perception data
            if perception is None:
                perception = PerceptionData(None, 0.0, False, 0.0, 200.0)

            snapshot = VehicleSnapshot(
                timestamp=timestamp,
                vehicle_id=i,
                position_m=vehicle.state.s_m,
                velocity_mps=vehicle.state.v_mps,
                acceleration_mps2=vehicle.state.a_mps2,
                jerk_mps3=vehicle.internal.jerk_mps3,
                is_speeding=vehicle.driver.speeding.is_speeding,
                overspeed_kmh=vehicle.driver.speeding.overspeed_magnitude_kmh,
                leader_distance_m=perception.leader_distance_m,
                is_occluded=perception.is_occluded,
                ssd_required_m=perception.ssd_required_m,
                driver_aggression=vehicle.driver.params.aggression_z,
                driver_rule_adherence=vehicle.driver.params.rule_adherence,
                driver_reaction_time=vehicle.driver.params.reaction_time_s,
                driver_headway=vehicle.driver.params.headway_T_s,
            )

            self.vehicle_snapshots.append(snapshot)

    def log_incident(self, incident: IncidentLog) -> None:
        """Log an incident event."""
        self.incident_log.append(incident)

    def log_near_miss(self, near_miss: NearMissEvent) -> None:
        """Log a near-miss event."""
        self.near_miss_events.append(near_miss)

    def log_collision(self, collision: CollisionEvent) -> None:
        """Log a collision event."""
        self.collision_events.append(collision)

    def export_to_csv(self, filename: Optional[str] = None) -> None:
        """Export all logged data to CSV files."""
        if filename is None:
            filename = str(self.output_path)

        base_path = Path(filename).with_suffix("")

        # Export simulation snapshots
        self._export_simulation_csv(f"{base_path}_simulation.csv")

        # Export vehicle snapshots
        self._export_vehicle_csv(f"{base_path}_vehicles.csv")

        # Export incidents
        self._export_incidents_csv(f"{base_path}_incidents.csv")

        # Export near-miss events
        self._export_near_misses_csv(f"{base_path}_near_misses.csv")

        # Export collision events
        self._export_collisions_csv(f"{base_path}_collisions.csv")

    def _export_simulation_csv(self, filename: str) -> None:
        """Export simulation snapshots to CSV."""
        if not self.simulation_snapshots:
            return

        with open(filename, "w", newline="") as csvfile:
            fieldnames = [
                field.name for field in self.simulation_snapshots[0].__dataclass_fields__.values()
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for snapshot in self.simulation_snapshots:
                writer.writerow(asdict(snapshot))

    def _export_vehicle_csv(self, filename: str) -> None:
        """Export vehicle snapshots to CSV."""
        if not self.vehicle_snapshots:
            return

        with open(filename, "w", newline="") as csvfile:
            fieldnames = [
                field.name for field in self.vehicle_snapshots[0].__dataclass_fields__.values()
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for snapshot in self.vehicle_snapshots:
                writer.writerow(asdict(snapshot))

    def _export_incidents_csv(self, filename: str) -> None:
        """Export incident log to CSV."""
        if not self.incident_log:
            return

        with open(filename, "w", newline="") as csvfile:
            fieldnames = [
                field.name for field in self.incident_log[0].__dataclass_fields__.values()
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for incident in self.incident_log:
                writer.writerow(asdict(incident))

    def _export_near_misses_csv(self, filename: str) -> None:
        """Export near-miss events to CSV."""
        if not self.near_miss_events:
            return

        with open(filename, "w", newline="") as csvfile:
            fieldnames = [
                field.name for field in self.near_miss_events[0].__dataclass_fields__.values()
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for event in self.near_miss_events:
                writer.writerow(asdict(event))

    def _export_collisions_csv(self, filename: str) -> None:
        """Export collision events to CSV."""
        if not self.collision_events:
            return

        with open(filename, "w", newline="") as csvfile:
            fieldnames = [
                field.name for field in self.collision_events[0].__dataclass_fields__.values()
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for event in self.collision_events:
                writer.writerow(asdict(event))

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics of logged data."""
        return {
            "total_simulation_snapshots": len(self.simulation_snapshots),
            "total_vehicle_snapshots": len(self.vehicle_snapshots),
            "total_incidents": len(self.incident_log),
            "total_near_misses": len(self.near_miss_events),
            "total_collisions": len(self.collision_events),
            "simulation_duration_s": (
                self.simulation_snapshots[-1].timestamp - self.simulation_snapshots[0].timestamp
                if self.simulation_snapshots
                else 0.0
            ),
            "avg_fps": (
                sum(s.fps for s in self.simulation_snapshots) / len(self.simulation_snapshots)
                if self.simulation_snapshots
                else 0.0
            ),
            "avg_memory_mb": (
                sum(s.memory_usage_mb for s in self.simulation_snapshots)
                / len(self.simulation_snapshots)
                if self.simulation_snapshots
                else 0.0
            ),
        }
