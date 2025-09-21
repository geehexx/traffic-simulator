from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import collections
import statistics
import time
from traffic_sim.core.vehicle import Vehicle
from traffic_sim.core.perception import PerceptionData


@dataclass
class SpeedHistogram:
    """Real-time speed histogram data."""

    bins: List[float]
    counts: List[int]
    mean_speed: float
    median_speed: float
    p25_speed: float
    p75_speed: float
    p95_speed: float


@dataclass
class HeadwayDistribution:
    """Real-time headway distribution data."""

    headways: List[float]
    mean_headway: float
    median_headway: float
    p25_headway: float
    p75_headway: float
    dangerous_headways: int  # < 1.0s
    critical_headways: int  # < 0.5s


@dataclass
class NearMissEvent:
    """Near-miss event data."""

    timestamp: float
    vehicle1_id: int
    vehicle2_id: int
    ttc: float  # Time to collision
    distance: float
    relative_speed: float


@dataclass
class IncidentLog:
    """Incident logging data."""

    timestamp: float
    event_type: str
    vehicle_id: int
    location_m: float
    speed_mps: float
    acceleration_mps2: float
    delta_v: float = 0.0
    ttc_at_impact: float = 0.0


class LiveAnalytics:
    """Real-time analytics collection and processing."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.speed_history: collections.deque = collections.deque(maxlen=1000)
        self.headway_history: collections.deque = collections.deque(maxlen=1000)
        self.near_miss_events: List[NearMissEvent] = []
        self.incident_log: List[IncidentLog] = []
        self.ttc_threshold = 1.5  # seconds
        self.dangerous_headway_threshold = 1.0  # seconds
        self.critical_headway_threshold = 0.5  # seconds

        # Performance tracking
        self.frame_times: collections.deque = collections.deque(maxlen=100)
        self.simulation_times: collections.deque = collections.deque(maxlen=100)
        self.last_update_time = time.time()

    def update_analytics(
        self, vehicles: List[Vehicle], perception_data: List[Optional[PerceptionData]], dt_s: float
    ) -> None:
        """Update all analytics with current simulation state."""
        current_time = time.time()

        # Update speed data
        self._update_speed_data(vehicles)

        # Update headway data
        self._update_headway_data(vehicles, perception_data)

        # Check for near-miss events
        self._check_near_misses(vehicles, perception_data, current_time)

        # Update performance metrics
        self._update_performance_metrics(dt_s, current_time)

        self.last_update_time = current_time

    def _update_speed_data(self, vehicles: List[Vehicle]) -> None:
        """Update speed histogram data."""
        speeds_kmh = [v.state.v_mps * 3.6 for v in vehicles]
        self.speed_history.extend(speeds_kmh)

    def _update_headway_data(
        self, vehicles: List[Vehicle], perception_data: List[Optional[PerceptionData]]
    ) -> None:
        """Update headway distribution data."""
        headways = []
        for i, perception in enumerate(perception_data):
            if (
                perception is not None
                and perception.leader_vehicle is not None
                and perception.leader_distance_m > 0
            ):
                # Calculate time headway: distance / speed
                if vehicles[i].state.v_mps > 0.1:  # Avoid division by zero
                    headway = perception.leader_distance_m / vehicles[i].state.v_mps
                    headways.append(headway)

        self.headway_history.extend(headways)

    def _check_near_misses(
        self,
        vehicles: List[Vehicle],
        perception_data: List[Optional[PerceptionData]],
        current_time: float,
    ) -> None:
        """Check for near-miss events based on TTC and headway."""
        for i, (vehicle, perception) in enumerate(zip(vehicles, perception_data)):
            if perception is not None and perception.leader_vehicle is not None:
                # Calculate TTC: distance / relative_speed
                relative_speed = vehicle.state.v_mps - perception.leader_vehicle.state.v_mps
                if relative_speed > 0.1:  # Approaching
                    ttc = perception.leader_distance_m / relative_speed

                    if ttc < self.ttc_threshold:
                        # Near-miss event
                        event = NearMissEvent(
                            timestamp=current_time,
                            vehicle1_id=i,
                            vehicle2_id=vehicles.index(perception.leader_vehicle),
                            ttc=ttc,
                            distance=perception.leader_distance_m,
                            relative_speed=relative_speed,
                        )
                        self.near_miss_events.append(event)

    def _update_performance_metrics(self, dt_s: float, current_time: float) -> None:
        """Update performance tracking metrics."""
        frame_time = current_time - self.last_update_time
        self.frame_times.append(frame_time)
        self.simulation_times.append(dt_s)

    def get_speed_histogram(self, num_bins: int = 20) -> SpeedHistogram:
        """Get current speed histogram data."""
        if not self.speed_history:
            return SpeedHistogram([], [], 0.0, 0.0, 0.0, 0.0, 0.0)

        speeds = list(self.speed_history)
        min_speed = min(speeds)
        max_speed = max(speeds)

        # Create bins
        bin_width = (max_speed - min_speed) / num_bins if max_speed > min_speed else 1.0
        bins = [min_speed + i * bin_width for i in range(num_bins + 1)]

        # Count speeds in each bin
        counts = [0] * num_bins
        for speed in speeds:
            bin_idx = min(int((speed - min_speed) / bin_width), num_bins - 1)
            counts[bin_idx] += 1

        # Calculate statistics
        mean_speed = statistics.mean(speeds)
        median_speed = statistics.median(speeds)
        p25_speed = statistics.quantiles(speeds, n=4)[0] if len(speeds) > 1 else mean_speed
        p75_speed = statistics.quantiles(speeds, n=4)[2] if len(speeds) > 1 else mean_speed
        p95_speed = statistics.quantiles(speeds, n=20)[18] if len(speeds) > 1 else mean_speed

        return SpeedHistogram(
            bins=bins,
            counts=counts,
            mean_speed=mean_speed,
            median_speed=median_speed,
            p25_speed=p25_speed,
            p75_speed=p75_speed,
            p95_speed=p95_speed,
        )

    def get_headway_distribution(self) -> HeadwayDistribution:
        """Get current headway distribution data."""
        if not self.headway_history:
            return HeadwayDistribution([], 0.0, 0.0, 0.0, 0.0, 0, 0)

        headways = list(self.headway_history)
        mean_headway = statistics.mean(headways)
        median_headway = statistics.median(headways)
        p25_headway = statistics.quantiles(headways, n=4)[0] if len(headways) > 1 else mean_headway
        p75_headway = statistics.quantiles(headways, n=4)[2] if len(headways) > 1 else mean_headway

        dangerous_headways = sum(1 for h in headways if h < self.dangerous_headway_threshold)
        critical_headways = sum(1 for h in headways if h < self.critical_headway_threshold)

        return HeadwayDistribution(
            headways=headways,
            mean_headway=mean_headway,
            median_headway=median_headway,
            p25_headway=p25_headway,
            p75_headway=p75_headway,
            dangerous_headways=dangerous_headways,
            critical_headways=critical_headways,
        )

    def get_near_miss_count(self) -> int:
        """Get total number of near-miss events."""
        return len(self.near_miss_events)

    def get_recent_near_misses(self, time_window_s: float = 60.0) -> int:
        """Get number of near-miss events in recent time window."""
        current_time = time.time()
        cutoff_time = current_time - time_window_s
        return sum(1 for event in self.near_miss_events if event.timestamp > cutoff_time)

    def get_performance_metrics(self) -> Dict[str, float]:
        """Get current performance metrics."""
        if not self.frame_times:
            return {"fps": 0.0, "avg_frame_time": 0.0, "avg_sim_time": 0.0}

        avg_frame_time = statistics.mean(self.frame_times)
        fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0

        avg_sim_time = statistics.mean(self.simulation_times) if self.simulation_times else 0.0

        return {"fps": fps, "avg_frame_time": avg_frame_time, "avg_sim_time": avg_sim_time}

    def log_incident(
        self,
        event_type: str,
        vehicle_id: int,
        location_m: float,
        speed_mps: float,
        acceleration_mps2: float,
        **kwargs,
    ) -> None:
        """Log an incident event."""
        incident = IncidentLog(
            timestamp=time.time(),
            event_type=event_type,
            vehicle_id=vehicle_id,
            location_m=location_m,
            speed_mps=speed_mps,
            acceleration_mps2=acceleration_mps2,
            **kwargs,
        )
        self.incident_log.append(incident)

    def get_incident_summary(self) -> Dict[str, Any]:
        """Get summary of recent incidents."""
        if not self.incident_log:
            return {"total_incidents": 0, "recent_incidents": 0, "incident_types": {}}

        current_time = time.time()
        recent_cutoff = current_time - 300.0  # 5 minutes

        recent_incidents = [i for i in self.incident_log if i.timestamp > recent_cutoff]
        incident_types: Dict[str, int] = {}

        for incident in self.incident_log:
            incident_types[incident.event_type] = incident_types.get(incident.event_type, 0) + 1

        return {
            "total_incidents": len(self.incident_log),
            "recent_incidents": len(recent_incidents),
            "incident_types": incident_types,
        }

    def clear_old_data(self, max_age_s: float = 300.0) -> None:
        """Clear old data to prevent memory buildup."""
        current_time = time.time()
        cutoff_time = current_time - max_age_s

        # Clear old near-miss events
        self.near_miss_events = [e for e in self.near_miss_events if e.timestamp > cutoff_time]

        # Clear old incidents
        self.incident_log = [i for i in self.incident_log if i.timestamp > cutoff_time]
