"""Tests for logging test."""

from __future__ import annotations


"""Comprehensive tests for the logging module."""


import pytest

import tempfile
import os
from unittest.mock import Mock
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
    """Comprehensive tests for the DataLogger class."""

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

    def test_log_simulation_step_with_data(self) -> None:
        """Test logging simulation step with actual data."""
        config = {"logging": {"output_path": "test_output.csv"}}
        logger = DataLogger(config)

        # Create mock vehicles
        vehicle1 = Mock()
        vehicle1.state.v_mps = 25.0
        vehicle1.state.s_m = 100.0
        vehicle1.state.a_mps2 = 2.0
        vehicle1.internal.jerk_mps3 = 1.0
        vehicle1.driver.speeding.is_speeding = True
        vehicle1.driver.speeding.overspeed_magnitude_kmh = 5.0
        vehicle1.driver.params.aggression_z = 0.5
        vehicle1.driver.params.rule_adherence = 0.8
        vehicle1.driver.params.reaction_time_s = 2.0
        vehicle1.driver.params.headway_T_s = 1.5

        vehicles = [vehicle1]

        # Create mock perception data
        perception1 = Mock()
        perception1.leader_vehicle = None
        perception1.leader_distance_m = 0.0
        perception1.is_occluded = False
        perception1.ssd_required_m = 30.0
        perception_data = [perception1]

        # Create mock analytics
        analytics = Mock()
        analytics.get_near_miss_count.return_value = 3

        # Test logging
        logger.log_simulation_step(vehicles, perception_data, analytics, 0.02)

        # Verify data was logged
        assert len(logger.vehicle_snapshots) > 0
        assert len(logger.simulation_snapshots) > 0

    def test_log_incident(self) -> None:
        """Test logging incident events."""
        config = {"logging": {"output_path": "test_output.csv"}}
        logger = DataLogger(config)

        incident = Mock()
        incident.timestamp = 10.5
        incident.event_type = "collision"
        incident.vehicle_id = 1
        incident.location_m = 500.0
        incident.speed_mps = 25.0
        incident.acceleration_mps2 = 2.0
        incident.delta_v = 5.0
        incident.ttc_at_impact = 1.2

        logger.log_incident(incident)

        assert len(logger.incident_log) == 1
        assert logger.incident_log[0] == incident

    def test_log_near_miss(self) -> None:
        """Test logging near-miss events."""
        config = {"logging": {"output_path": "test_output.csv"}}
        logger = DataLogger(config)

        near_miss = Mock()
        near_miss.timestamp = 15.2
        near_miss.vehicle1_id = 1
        near_miss.vehicle2_id = 2
        near_miss.ttc = 1.5
        near_miss.distance = 750.0
        near_miss.relative_speed = 10.0

        logger.log_near_miss(near_miss)

        assert len(logger.near_miss_events) == 1
        assert logger.near_miss_events[0] == near_miss

    def test_log_collision(self) -> None:
        """Test logging collision events."""
        config = {"logging": {"output_path": "test_output.csv"}}
        logger = DataLogger(config)

        collision = Mock()
        collision.timestamp = 20.1
        collision.vehicle1_id = 1
        collision.vehicle2_id = 2
        collision.location_m = 1000.0
        collision.delta_v = 15.0
        collision.ttc_at_impact = 0.8

        logger.log_collision(collision)

        assert len(logger.collision_events) == 1
        assert logger.collision_events[0] == collision

    def test_export_to_csv_with_data(self) -> None:
        """Test CSV export with actual data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"logging": {"output_path": os.path.join(temp_dir, "test_output.csv")}}
            logger = DataLogger(config)

            # Add some test data
            logger.vehicle_snapshots.append(
                VehicleSnapshot(
                    timestamp=1.0,
                    vehicle_id=1,
                    position_m=100.0,
                    velocity_mps=25.0,
                    acceleration_mps2=2.0,
                    jerk_mps3=1.0,
                    is_speeding=False,
                    overspeed_kmh=0.0,
                    leader_distance_m=50.0,
                    is_occluded=False,
                    ssd_required_m=30.0,
                    driver_aggression=0.5,
                    driver_rule_adherence=0.8,
                    driver_reaction_time=2.0,
                    driver_headway=1.5,
                )
            )

            logger.simulation_snapshots.append(
                SimulationSnapshot(
                    timestamp=1.0,
                    step_count=100,
                    total_vehicles=20,
                    avg_speed_kmh=80.0,
                    avg_headway_s=2.0,
                    near_miss_count=5,
                    collision_count=1,
                    fps=60.0,
                    memory_usage_mb=45.0,
                )
            )

            # Export to CSV
            logger.export_to_csv()

            # Check that files were created
            assert os.path.exists(os.path.join(temp_dir, "test_output_vehicles.csv"))
            assert os.path.exists(os.path.join(temp_dir, "test_output_simulation.csv"))

    def test_get_summary_stats_with_data(self) -> None:
        """Test getting summary statistics with data."""
        config = {"logging": {"output_path": "test_output.csv"}}
        logger = DataLogger(config)

        # Add test data
        logger.vehicle_snapshots.append(
            VehicleSnapshot(
                timestamp=1.0,
                vehicle_id=1,
                position_m=100.0,
                velocity_mps=25.0,
                acceleration_mps2=2.0,
                jerk_mps3=1.0,
                is_speeding=False,
                overspeed_kmh=0.0,
                leader_distance_m=50.0,
                is_occluded=False,
                ssd_required_m=30.0,
                driver_aggression=0.5,
                driver_rule_adherence=0.8,
                driver_reaction_time=2.0,
                driver_headway=1.5,
            )
        )

        logger.simulation_snapshots.append(
            SimulationSnapshot(
                timestamp=1.0,
                step_count=100,
                total_vehicles=20,
                avg_speed_kmh=80.0,
                avg_headway_s=2.0,
                near_miss_count=5,
                collision_count=1,
                fps=60.0,
                memory_usage_mb=45.0,
            )
        )

        logger.simulation_snapshots.append(
            SimulationSnapshot(
                timestamp=2.0,
                step_count=200,
                total_vehicles=20,
                avg_speed_kmh=85.0,
                avg_headway_s=2.1,
                near_miss_count=7,
                collision_count=2,
                fps=58.0,
                memory_usage_mb=47.0,
            )
        )

        stats = logger.get_summary_stats()

        assert stats["total_simulation_snapshots"] == 2
        assert stats["total_vehicle_snapshots"] == 1
        assert stats["total_incidents"] == 0
        assert stats["total_near_misses"] == 0
        assert stats["total_collisions"] == 0
        assert stats["simulation_duration_s"] == 1.0  # 2.0 - 1.0
        assert stats["avg_fps"] == 59.0  # (60.0 + 58.0) / 2
        assert stats["avg_memory_mb"] == 46.0  # (45.0 + 47.0) / 2

    def test_get_summary_stats_empty(self) -> None:
        """Test getting summary statistics with no data."""
        config = {"logging": {"output_path": "test_output.csv"}}
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

    def test_calculate_average_speed_empty_vehicles(self) -> None:
        """Test average speed calculation with empty vehicles list."""
        config = {"logging": {"output_path": "test_output.csv"}}
        logger = DataLogger(config)

        avg_speed = logger._calculate_average_speed([])
        assert avg_speed == 0.0

    def test_calculate_average_headway_empty_data(self) -> None:
        """Test average headway calculation with empty perception data."""
        config = {"logging": {"output_path": "test_output.csv"}}
        logger = DataLogger(config)

        avg_headway = logger._calculate_average_headway([], [])
        assert avg_headway == 0.0

    def test_calculate_performance_metrics_empty_data(self) -> None:
        """Test performance metrics calculation with empty data."""
        config = {"logging": {"output_path": "test_output.csv"}}
        logger = DataLogger(config)

        fps, memory_mb = logger._calculate_performance_metrics()
        assert fps == 0.0
        assert memory_mb == 0.0

    def test_is_valid_perception_for_headway_valid(self) -> None:
        """Test valid perception check with valid data."""
        config = {"logging": {"output_path": "test_output.csv"}}
        logger = DataLogger(config)

        perception = Mock()
        perception.leader_vehicle = Mock()
        perception.leader_distance_m = 50.0

        assert logger._is_valid_perception_for_headway(perception) is True

    def test_is_valid_perception_for_headway_invalid(self) -> None:
        """Test valid perception check with invalid data."""
        config = {"logging": {"output_path": "test_output.csv"}}
        logger = DataLogger(config)

        # Test None perception
        assert logger._is_valid_perception_for_headway(None) is False

        # Test perception with no leader
        perception_no_leader = Mock()
        perception_no_leader.leader_vehicle = None
        perception_no_leader.leader_distance_m = 50.0
        assert logger._is_valid_perception_for_headway(perception_no_leader) is False

        # Test perception with zero distance
        perception_zero_distance = Mock()
        perception_zero_distance.leader_vehicle = Mock()
        perception_zero_distance.leader_distance_m = 0.0
        assert logger._is_valid_perception_for_headway(perception_zero_distance) is False

    def test_find_vehicle_headway_no_matching_vehicle(self) -> None:
        """Test headway calculation when no vehicle matches criteria."""
        config = {"logging": {"output_path": "test_output.csv"}}
        logger = DataLogger(config)

        perception = Mock()
        perception.leader_distance_m = 50.0

        # Vehicle with no driver attribute
        vehicle_no_driver = Mock()
        del vehicle_no_driver.driver

        # Vehicle with low speed
        vehicle_low_speed = Mock()
        vehicle_low_speed.driver = Mock()
        vehicle_low_speed.state.v_mps = 0.05  # Below threshold

        vehicles = [vehicle_no_driver, vehicle_low_speed]

        headway = logger._find_vehicle_headway(vehicles, perception)
        assert headway is None

    def test_find_vehicle_headway_matching_vehicle(self) -> None:
        """Test headway calculation with matching vehicle."""
        config = {"logging": {"output_path": "test_output.csv"}}
        logger = DataLogger(config)

        perception = Mock()
        perception.leader_distance_m = 50.0

        vehicle = Mock()
        vehicle.driver = Mock()
        vehicle.state.v_mps = 25.0  # Above threshold

        vehicles = [vehicle]

        headway = logger._find_vehicle_headway(vehicles, perception)
        expected_headway = 50.0 / 25.0  # distance / speed
        assert headway == expected_headway

    def test_logging_rates_configuration(self) -> None:
        """Test different logging rate configurations."""
        config = {
            "logging": {
                "aggregate_rate_hz": 5,
                "per_vehicle_trace_rate_hz": 1,
                "debug_rate_hz": 100,
            }
        }
        logger = DataLogger(config)

        assert logger.aggregate_rate_hz == 5
        assert logger.per_vehicle_rate_hz == 1
        assert logger.debug_rate_hz == 100

    def test_logging_rates_defaults(self) -> None:
        """Test default logging rate values."""
        config = {"logging": {}}
        logger = DataLogger(config)

        assert logger.aggregate_rate_hz == 10
        assert logger.per_vehicle_rate_hz == 2
        assert logger.debug_rate_hz == 50

    def test_step_count_increment(self) -> None:
        """Test step count increment."""
        config = {"logging": {"output_path": "test_output.csv"}}
        logger = DataLogger(config)

        initial_count = logger.step_count

        vehicles = []
        perception_data = []
        analytics = Mock()
        analytics.get_near_miss_count.return_value = 0

        logger.log_simulation_step(vehicles, perception_data, analytics, 0.02)

        assert logger.step_count == initial_count + 1


if __name__ == "__main__":
    pytest.main([__file__])
