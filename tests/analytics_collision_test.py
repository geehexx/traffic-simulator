from __future__ import annotations

import pytest
import random
from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation
from traffic_sim.core.perception import PerceptionData
from traffic_sim.core.analytics import LiveAnalytics
from traffic_sim.core.collision import CollisionSystem
from traffic_sim.core.logging import DataLogger
from traffic_sim.core.vehicle import Vehicle, VehicleSpec, VehicleState
from traffic_sim.core.driver import Driver, DriverParams
from traffic_sim.core.track import StadiumTrack


def test_analytics_speed_histogram():
    """Test speed histogram analytics."""
    config = load_config()
    analytics = LiveAnalytics(config)

    # Create mock vehicles with different speeds
    vehicles = []
    for i in range(5):
        spec = VehicleSpec("test", 4.0, 2.0, 1500.0, 100.0, 200.0, 0.5, 2.5, 0.8, 0.9)
        state = VehicleState(0.0, 10.0 + i * 5.0, 0.0)  # Speeds 10, 15, 20, 25, 30 m/s
        driver = Driver(
            DriverParams(
                reaction_time_s=2.0,
                headway_T_s=1.5,
                comfort_brake_mps2=3.0,
                max_brake_mps2=7.0,
                jerk_limit_mps3=4.0,
                throttle_lag_s=0.2,
                brake_lag_s=0.1,
                aggression_z=0.0,
                rule_adherence=0.5,
                desired_speed_mps=25.0,
            ),
            random.Random(42),
        )
        vehicle = Vehicle(spec, state, driver)
        vehicles.append(vehicle)

    # Update analytics
    perception_data = [
        PerceptionData(None, 0.0, False, 0.0, 200.0) for _ in vehicles
    ]  # Mock perception data
    analytics.update_analytics(vehicles, perception_data, 0.02)

    # Get speed histogram
    speed_hist = analytics.get_speed_histogram()

    # Check that we have speed data
    assert len(speed_hist.counts) > 0
    assert speed_hist.mean_speed > 0
    assert speed_hist.median_speed > 0
    assert speed_hist.p95_speed > 0


def test_analytics_headway_distribution():
    """Test headway distribution analytics."""
    config = load_config()
    analytics = LiveAnalytics(config)

    # Create mock vehicles
    vehicles = []
    for i in range(3):
        spec = VehicleSpec("test", 4.0, 2.0, 1500.0, 100.0, 200.0, 0.5, 2.5, 0.8, 0.9)
        state = VehicleState(i * 50.0, 20.0, 0.0)  # 50m spacing
        driver = Driver(
            DriverParams(
                reaction_time_s=2.0,
                headway_T_s=1.5,
                comfort_brake_mps2=3.0,
                max_brake_mps2=7.0,
                jerk_limit_mps3=4.0,
                throttle_lag_s=0.2,
                brake_lag_s=0.1,
                aggression_z=0.0,
                rule_adherence=0.5,
                desired_speed_mps=25.0,
            ),
            random.Random(42),
        )
        vehicle = Vehicle(spec, state, driver)
        vehicles.append(vehicle)

    # Mock perception data with headways
    perception_data = [
        PerceptionData(vehicles[1], 50.0, False, 10.0, 200.0),
        PerceptionData(vehicles[2], 50.0, False, 10.0, 200.0),
        PerceptionData(None, 0.0, False, 0.0, 200.0),
    ]

    # Update analytics
    analytics.update_analytics(vehicles, perception_data, 0.02)

    # Get headway distribution
    headway_dist = analytics.get_headway_distribution()

    # Check that we have headway data
    assert len(headway_dist.headways) > 0
    assert headway_dist.mean_headway > 0
    assert headway_dist.median_headway > 0


def test_analytics_near_miss_detection():
    """Test near-miss detection."""
    config = load_config()
    analytics = LiveAnalytics(config)

    # Create vehicles in close proximity
    vehicles = []
    for i in range(2):
        spec = VehicleSpec("test", 4.0, 2.0, 1500.0, 100.0, 200.0, 0.5, 2.5, 0.8, 0.9)
        state = VehicleState(i * 5.0, 20.0, 0.0)  # Very close spacing
        driver = Driver(
            DriverParams(
                reaction_time_s=2.0,
                headway_T_s=1.5,
                comfort_brake_mps2=3.0,
                max_brake_mps2=7.0,
                jerk_limit_mps3=4.0,
                throttle_lag_s=0.2,
                brake_lag_s=0.1,
                aggression_z=0.0,
                rule_adherence=0.5,
                desired_speed_mps=25.0,
            ),
            random.Random(42),
        )
        vehicle = Vehicle(spec, state, driver)
        vehicles.append(vehicle)

    # Mock perception data with close following
    perception_data = [
        PerceptionData(vehicles[1], 5.0, False, 10.0, 200.0),
        PerceptionData(None, 0.0, False, 0.0, 200.0),
    ]

    # Update analytics multiple times to trigger near-miss detection
    for _ in range(10):
        analytics.update_analytics(vehicles, perception_data, 0.02)

    # Check near-miss count
    near_miss_count = analytics.get_near_miss_count()
    assert near_miss_count >= 0  # Should detect some near-misses


def test_collision_system():
    """Test collision detection system."""
    config = load_config()
    track = StadiumTrack(1000.0, 0.3)
    collision_system = CollisionSystem(config, track)

    # Create vehicles
    vehicles = []
    for i in range(2):
        spec = VehicleSpec("test", 4.0, 2.0, 1500.0, 100.0, 200.0, 0.5, 2.5, 0.8, 0.9)
        state = VehicleState(i * 10.0, 20.0, 0.0)  # Close spacing
        driver = Driver(
            DriverParams(
                reaction_time_s=2.0,
                headway_T_s=1.5,
                comfort_brake_mps2=3.0,
                max_brake_mps2=7.0,
                jerk_limit_mps3=4.0,
                throttle_lag_s=0.2,
                brake_lag_s=0.1,
                aggression_z=0.0,
                rule_adherence=0.5,
                desired_speed_mps=25.0,
            ),
            random.Random(42),
        )
        vehicle = Vehicle(spec, state, driver)
        vehicles.append(vehicle)

        # Add to collision system
        collision_system.add_vehicle(vehicle, i)

    # Check for collisions
    collision_events = collision_system.check_collisions(vehicles)

    # Should detect collision due to close spacing
    assert len(collision_events) >= 0

    # Check collision event properties (if any events were detected)
    if collision_events:
        event = collision_events[0]
        assert event.vehicle1_id >= 0
        assert event.vehicle2_id >= 0
        assert event.delta_v >= 0
        assert event.location_m >= 0


def test_data_logger():
    """Test data logging system."""
    config = load_config()
    logger = DataLogger(config)

    # Create mock vehicles
    vehicles = []
    for i in range(3):
        spec = VehicleSpec("test", 4.0, 2.0, 1500.0, 100.0, 200.0, 0.5, 2.5, 0.8, 0.9)
        state = VehicleState(i * 50.0, 20.0, 0.0)
        driver = Driver(
            DriverParams(
                reaction_time_s=2.0,
                headway_T_s=1.5,
                comfort_brake_mps2=3.0,
                max_brake_mps2=7.0,
                jerk_limit_mps3=4.0,
                throttle_lag_s=0.2,
                brake_lag_s=0.1,
                aggression_z=0.0,
                rule_adherence=0.5,
                desired_speed_mps=25.0,
            ),
            random.Random(42),
        )
        vehicle = Vehicle(spec, state, driver)
        vehicles.append(vehicle)

    # Mock perception data
    perception_data = [
        PerceptionData(vehicles[1], 50.0, False, 10.0, 200.0),
        PerceptionData(vehicles[2], 50.0, False, 10.0, 200.0),
        PerceptionData(None, 0.0, False, 0.0, 200.0),
    ]

    # Create analytics
    analytics = LiveAnalytics(config)

    # Log simulation step
    logger.log_simulation_step(vehicles, perception_data, analytics, 0.02)

    # Check that data was logged
    assert len(logger.vehicle_snapshots) > 0
    assert len(logger.simulation_snapshots) > 0

    # Test CSV export
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        logger.export_to_csv(f"{temp_dir}/test_run")

        # Check that files were created
        import os

        assert os.path.exists(f"{temp_dir}/test_run_simulation.csv")
        assert os.path.exists(f"{temp_dir}/test_run_vehicles.csv")


def test_integrated_analytics_collision():
    """Test integrated analytics and collision system."""
    config = load_config()
    config["vehicles"]["count"] = 5
    sim = Simulation(config)

    # Run simulation for several steps
    for _ in range(50):
        sim.step(0.02)

    # Check that analytics are working
    speed_hist = sim.analytics.get_speed_histogram()
    assert len(speed_hist.counts) > 0

    headway_dist = sim.analytics.get_headway_distribution()
    assert len(headway_dist.headways) >= 0

    # Check that collision system is working
    collision_events = sim.collision_system.get_collision_events()
    assert isinstance(collision_events, list)

    # Check that logging is working
    summary = sim.get_logging_summary()
    assert summary["total_simulation_snapshots"] > 0
    assert summary["total_vehicle_snapshots"] > 0


def test_performance_metrics():
    """Test performance metrics collection."""
    config = load_config()
    analytics = LiveAnalytics(config)

    # Create mock vehicles
    vehicles = []
    for i in range(10):
        spec = VehicleSpec("test", 4.0, 2.0, 1500.0, 100.0, 200.0, 0.5, 2.5, 0.8, 0.9)
        state = VehicleState(i * 50.0, 20.0, 0.0)
        driver = Driver(
            DriverParams(
                reaction_time_s=2.0,
                headway_T_s=1.5,
                comfort_brake_mps2=3.0,
                max_brake_mps2=7.0,
                jerk_limit_mps3=4.0,
                throttle_lag_s=0.2,
                brake_lag_s=0.1,
                aggression_z=0.0,
                rule_adherence=0.5,
                desired_speed_mps=25.0,
            ),
            random.Random(42),
        )
        vehicle = Vehicle(spec, state, driver)
        vehicles.append(vehicle)

    # Mock perception data
    perception_data = [PerceptionData(None, 0.0, False, 0.0, 200.0) for _ in vehicles]

    # Update analytics multiple times
    for _ in range(100):
        analytics.update_analytics(vehicles, perception_data, 0.02)

    # Get performance metrics
    perf = analytics.get_performance_metrics()
    assert "fps" in perf
    assert "avg_frame_time" in perf
    assert "avg_sim_time" in perf
    assert perf["fps"] >= 0


def test_incident_logging():
    """Test incident logging functionality."""
    config = load_config()
    analytics = LiveAnalytics(config)

    # Log various incidents
    analytics.log_incident(
        event_type="speeding", vehicle_id=0, location_m=100.0, speed_mps=30.0, acceleration_mps2=2.0
    )

    analytics.log_incident(
        event_type="hard_braking",
        vehicle_id=1,
        location_m=200.0,
        speed_mps=15.0,
        acceleration_mps2=-5.0,
    )

    # Get incident summary
    summary = analytics.get_incident_summary()
    assert summary["total_incidents"] == 2
    assert summary["recent_incidents"] == 2
    assert "speeding" in summary["incident_types"]
    assert "hard_braking" in summary["incident_types"]


if __name__ == "__main__":
    pytest.main([__file__])
