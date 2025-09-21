"""Tests for the logging module."""

from __future__ import annotations

from traffic_sim.core.logging import DataLogger, VehicleSnapshot, SimulationSnapshot


class TestVehicleSnapshot:
    """Test the VehicleSnapshot dataclass."""

    def test_vehicle_snapshot_creation(self) -> None:
        """Test creating a vehicle snapshot with all fields."""
        snapshot = VehicleSnapshot(
            timestamp=1.5,
            vehicle_id=1,
            position_m=100.0,
            velocity_mps=25.0,
            acceleration_mps2=2.0,
            jerk_mps3=1.0,
            is_speeding=True,
            overspeed_kmh=5.0,
            leader_distance_m=50.0,
            is_occluded=False,
            ssd_required_m=30.0,
            driver_aggression=0.5,
            driver_rule_adherence=0.8,
            driver_reaction_time=2.0,
            driver_headway=1.5,
        )

        assert snapshot.timestamp == 1.5
        assert snapshot.vehicle_id == 1
        assert snapshot.position_m == 100.0
        assert snapshot.velocity_mps == 25.0
        assert snapshot.acceleration_mps2 == 2.0
        assert snapshot.jerk_mps3 == 1.0
        assert snapshot.is_speeding is True
        assert snapshot.overspeed_kmh == 5.0
        assert snapshot.leader_distance_m == 50.0
        assert snapshot.is_occluded is False
        assert snapshot.ssd_required_m == 30.0
        assert snapshot.driver_aggression == 0.5
        assert snapshot.driver_rule_adherence == 0.8
        assert snapshot.driver_reaction_time == 2.0
        assert snapshot.driver_headway == 1.5


class TestSimulationSnapshot:
    """Test the SimulationSnapshot dataclass."""

    def test_simulation_snapshot_creation(self) -> None:
        """Test creating a simulation snapshot with all fields."""
        snapshot = SimulationSnapshot(
            timestamp=2.0,
            step_count=100,
            total_vehicles=20,
            avg_speed_kmh=80.0,
            avg_headway_s=2.0,
            near_miss_count=5,
            collision_count=1,
            fps=60.0,
            memory_usage_mb=45.0,
        )

        assert snapshot.timestamp == 2.0
        assert snapshot.step_count == 100
        assert snapshot.total_vehicles == 20
        assert snapshot.avg_speed_kmh == 80.0
        assert snapshot.avg_headway_s == 2.0
        assert snapshot.near_miss_count == 5
        assert snapshot.collision_count == 1
        assert snapshot.fps == 60.0
        assert snapshot.memory_usage_mb == 45.0


class TestDataLogger:
    """Test the DataLogger class."""

    def test_logger_initialization(self) -> None:
        """Test that logger initializes with empty data structures."""
        config = {"logging": {"output_path": "test_output.csv"}}
        logger = DataLogger(config)

        assert logger.vehicle_snapshots == []
        assert logger.simulation_snapshots == []
        assert logger.incident_log == []
        assert logger.near_miss_events == []
        assert logger.collision_events == []
        assert logger.step_count == 0

    def test_logger_config_loading(self) -> None:
        """Test that logger loads configuration correctly."""
        config = {
            "logging": {
                "output_path": "custom_output.csv",
                "aggregate_rate_hz": 5,
                "per_vehicle_trace_rate_hz": 1,
                "debug_rate_hz": 100,
            }
        }
        logger = DataLogger(config)

        assert logger.output_path.name == "custom_output.csv"
        assert logger.aggregate_rate_hz == 5
        assert logger.per_vehicle_rate_hz == 1
        assert logger.debug_rate_hz == 100

    def test_get_summary_stats_empty(self) -> None:
        """Test summary stats with no data."""
        config = {"logging": {}}
        logger = DataLogger(config)
        stats = logger.get_summary_stats()

        assert stats["total_simulation_snapshots"] == 0
        assert stats["total_vehicle_snapshots"] == 0
        assert stats["total_incidents"] == 0
        assert stats["total_near_misses"] == 0
        assert stats["total_collisions"] == 0
        assert stats["simulation_duration_s"] == 0.0
        assert stats["avg_fps"] == 0.0
        assert stats["avg_memory_mb"] == 0.0
