from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation
from traffic_sim.core.driver import Driver, DriverParams, sample_driver_params
from traffic_sim.core.vehicle import Vehicle, VehicleSpec, VehicleState
import random
import pytest


def test_idm_braking_when_too_close():
    cfg = load_config()
    cfg["vehicles"]["count"] = 2
    sim = Simulation(cfg)
    # Place follower just behind leader with small gap and higher speed
    sim.vehicles[0].state.s_m = 0.0
    sim.vehicles[0].state.v_mps = 10.0
    sim.vehicles[1].state.s_m = 2.0  # small gap ahead (leader)
    sim.vehicles[1].state.v_mps = 0.5
    # Step the sim
    sim.step(0.2)
    # Expect follower acceleration to be negative (braking)
    assert sim.vehicles[0].state.a_mps2 < 0.0


def test_per_driver_parameters():
    """Test that different drivers have different parameters."""
    cfg = load_config()
    rng = random.Random(42)
    
    # Sample multiple drivers
    drivers = []
    for _ in range(10):
        params = sample_driver_params(cfg, rng)
        driver = Driver(params, rng)
        drivers.append(driver)
    
    # Check that parameters vary (not all identical)
    headways = [d.params.headway_T_s for d in drivers]
    reaction_times = [d.params.reaction_time_s for d in drivers]
    comfort_brakes = [d.params.comfort_brake_mps2 for d in drivers]
    
    # Should have variation in parameters
    assert len(set(headways)) > 1, "Headway parameters should vary"
    assert len(set(reaction_times)) > 1, "Reaction time parameters should vary"
    assert len(set(comfort_brakes)) > 1, "Comfort brake parameters should vary"
    
    # Check parameter ranges
    for driver in drivers:
        assert 0.6 <= driver.params.headway_T_s <= 3.0
        assert 0.8 <= driver.params.reaction_time_s <= 4.0
        assert 1.0 <= driver.params.comfort_brake_mps2 <= 4.0
        assert 4.0 <= driver.params.max_brake_mps2 <= 9.0
        assert 0.0 <= driver.params.rule_adherence <= 1.0


def test_speeding_behavior():
    """Test Markov chain speeding behavior."""
    cfg = load_config()
    rng = random.Random(42)
    
    # Create aggressive driver (high aggression, low rule adherence)
    params = DriverParams(
        reaction_time_s=2.0,
        headway_T_s=1.5,
        comfort_brake_mps2=3.0,
        max_brake_mps2=7.0,
        jerk_limit_mps3=4.0,
        throttle_lag_s=0.2,
        brake_lag_s=0.1,
        aggression_z=2.0,  # High aggression
        rule_adherence=0.2,  # Low rule adherence
        desired_speed_mps=30.0
    )
    
    driver = Driver(params, rng)
    speed_limit_mps = 25.0  # 90 km/h
    
    # Test initial state
    assert not driver.speeding.is_speeding
    assert driver.get_effective_speed_limit(speed_limit_mps) == speed_limit_mps
    
    # Simulate multiple time steps
    speeding_events = 0
    for _ in range(1000):
        driver.update_speeding_state(0.1, speed_limit_mps)
        if driver.speeding.is_speeding:
            speeding_events += 1
            # When speeding, effective speed limit should be higher
            assert driver.get_effective_speed_limit(speed_limit_mps) > speed_limit_mps
    
    # Aggressive driver should speed more often
    assert speeding_events > 50, f"Expected aggressive driver to speed more often, got {speeding_events} events"


def test_jerk_limiting():
    """Test that jerk is properly limited."""
    cfg = load_config()
    rng = random.Random(42)
    
    # Create driver with low jerk limit
    params = DriverParams(
        reaction_time_s=2.0,
        headway_T_s=1.5,
        comfort_brake_mps2=3.0,
        max_brake_mps2=7.0,
        jerk_limit_mps3=1.0,  # Low jerk limit
        throttle_lag_s=0.2,
        brake_lag_s=0.1,
        aggression_z=0.0,
        rule_adherence=0.5,
        desired_speed_mps=25.0
    )
    
    driver = Driver(params, rng)
    spec = VehicleSpec("test", 4.0, 2.0, 1500.0)
    state = VehicleState(0.0, 20.0, 0.0)
    vehicle = Vehicle(spec, state, driver)
    
    # Set high commanded acceleration
    vehicle.set_commanded_acceleration(10.0)  # Very high acceleration
    
    # Update with small time step
    dt = 0.01
    vehicle.update_internal_state(dt)
    
    # Jerk should be limited
    max_jerk = driver.params.jerk_limit_mps3
    expected_max_change = max_jerk * dt
    actual_change = vehicle.internal.actual_accel_mps2 - 0.0  # Compare to initial 0.0
    
    assert abs(actual_change) <= expected_max_change + 1e-6, f"Jerk limit exceeded: {abs(actual_change)} > {expected_max_change}"


def test_drivetrain_lag():
    """Test that drivetrain lag filters work correctly."""
    cfg = load_config()
    rng = random.Random(42)
    
    # Create driver with high lag
    params = DriverParams(
        reaction_time_s=2.0,
        headway_T_s=1.5,
        comfort_brake_mps2=3.0,
        max_brake_mps2=7.0,
        jerk_limit_mps3=4.0,
        throttle_lag_s=1.0,  # High throttle lag
        brake_lag_s=0.5,     # High brake lag
        aggression_z=0.0,
        rule_adherence=0.5,
        desired_speed_mps=25.0
    )
    
    driver = Driver(params, rng)
    spec = VehicleSpec("test", 4.0, 2.0, 1500.0)
    state = VehicleState(0.0, 20.0, 0.0)
    vehicle = Vehicle(spec, state, driver)
    
    # Set commanded acceleration
    vehicle.set_commanded_acceleration(2.0)
    
    # Update multiple times
    for _ in range(10):
        vehicle.update_internal_state(0.1)
    
    # Due to lag, the actual acceleration should be less than commanded
    # The lag filters should show the delayed response
    assert vehicle.internal.throttle_lag_filter < vehicle.internal.actual_accel_mps2
    assert vehicle.state.a_mps2 < vehicle.internal.actual_accel_mps2


def test_enhanced_idm_stability():
    """Test that enhanced IDM maintains stability with per-driver parameters."""
    cfg = load_config()
    cfg["vehicles"]["count"] = 5
    sim = Simulation(cfg)
    
    # Set up vehicles in a line with varying speeds
    for i, vehicle in enumerate(sim.vehicles):
        vehicle.state.s_m = i * 50.0  # 50m spacing
        vehicle.state.v_mps = 20.0 + i * 2.0  # Varying speeds
    
    # Run simulation for many steps
    for _ in range(100):
        sim.step(0.02)
    
    # Check that vehicles maintain reasonable speeds and accelerations
    for vehicle in sim.vehicles:
        assert 0.0 <= vehicle.state.v_mps <= 50.0, f"Speed out of range: {vehicle.state.v_mps}"
        assert -10.0 <= vehicle.state.a_mps2 <= 5.0, f"Acceleration out of range: {vehicle.state.a_mps2}"
        assert abs(vehicle.internal.jerk_mps3) <= vehicle.driver.params.jerk_limit_mps3 + 1e-6, f"Jerk limit exceeded: {vehicle.internal.jerk_mps3}"


def test_deterministic_behavior():
    """Test that simulation is deterministic with fixed seed."""
    cfg = load_config()
    cfg["random"]["master_seed"] = 12345
    cfg["vehicles"]["count"] = 3
    
    # Run simulation twice with same seed
    sim1 = Simulation(cfg)
    sim2 = Simulation(cfg)
    
    # Run for several steps
    for _ in range(50):
        sim1.step(0.02)
        sim2.step(0.02)
    
    # Results should be identical
    for v1, v2 in zip(sim1.vehicles, sim2.vehicles):
        assert abs(v1.state.s_m - v2.state.s_m) < 1e-6
        assert abs(v1.state.v_mps - v2.state.v_mps) < 1e-6
        assert abs(v1.state.a_mps2 - v2.state.a_mps2) < 1e-6


def test_single_vehicle_behavior():
    """Test that single vehicle approaches desired speed."""
    cfg = load_config()
    cfg["vehicles"]["count"] = 1
    sim = Simulation(cfg)
    
    vehicle = sim.vehicles[0]
    initial_speed = vehicle.state.v_mps
    
    # Run for many steps
    for _ in range(200):  # More steps to allow convergence
        sim.step(0.02)
    
    # Vehicle should approach desired speed (with some tolerance for jerk/lag effects)
    desired_speed = vehicle.driver.params.desired_speed_mps
    assert abs(vehicle.state.v_mps - desired_speed) < 8.0, f"Speed {vehicle.state.v_mps} not close to desired {desired_speed}"
    
    # Speed should be positive and reasonable
    assert vehicle.state.v_mps > 0, "Speed should be positive"
    assert vehicle.state.v_mps < 50.0, "Speed should be reasonable"


def test_correlation_sampling():
    """Test that parameter correlations are maintained."""
    cfg = load_config()
    rng = random.Random(42)
    
    # Sample many drivers
    drivers = []
    for _ in range(100):
        params = sample_driver_params(cfg, rng)
        driver = Driver(params, rng)
        drivers.append(driver)
    
    # Check correlation between aggression and headway (should be negative)
    aggression_values = [d.params.aggression_z for d in drivers]
    headway_values = [d.params.headway_T_s for d in drivers]
    
    # Calculate correlation coefficient
    n = len(drivers)
    mean_aggression = sum(aggression_values) / n
    mean_headway = sum(headway_values) / n
    
    numerator = sum((a - mean_aggression) * (h - mean_headway) for a, h in zip(aggression_values, headway_values))
    denominator = (sum((a - mean_aggression) ** 2 for a in aggression_values) * 
                  sum((h - mean_headway) ** 2 for h in headway_values)) ** 0.5
    
    if denominator > 0:
        correlation = numerator / denominator
        # Should be negative correlation (aggressive drivers have shorter headways)
        assert correlation < 0, f"Expected negative correlation, got {correlation}"


def test_occlusion_detection():
    """Test occlusion detection system."""
    cfg = load_config()
    cfg["vehicles"]["count"] = 3
    sim = Simulation(cfg)
    
    # Position vehicles in a line with one occluded
    sim.vehicles[0].state.s_m = 0.0    # Follower
    sim.vehicles[1].state.s_m = 50.0   # Middle vehicle (occluder)
    sim.vehicles[2].state.s_m = 100.0  # Leader
    
    # Test occlusion detection
    leader, distance, is_occluded = sim._find_first_unobstructed_leader(0)
    
    # Should find the middle vehicle as leader (not the far one)
    assert leader is not None, "Should find a leader"
    assert leader == sim.vehicles[1], "Should find the middle vehicle as leader"
    assert distance == 50.0, f"Distance should be 50m, got {distance}"
    assert not is_occluded, "Should not be occluded for close vehicle"


def test_ssd_calculation():
    """Test dynamic SSD calculation."""
    cfg = load_config()
    cfg["vehicles"]["count"] = 2
    sim = Simulation(cfg)
    
    # Setup follower and leader
    follower = sim.vehicles[0]
    leader = sim.vehicles[1]
    
    # Set speeds and parameters
    follower.state.v_mps = 20.0  # 20 m/s
    leader.state.v_mps = 15.0    # 15 m/s
    follower.driver.params.reaction_time_s = 2.0
    follower.driver.params.comfort_brake_mps2 = 3.0
    leader.driver.params.comfort_brake_mps2 = 3.0
    
    # Calculate SSD
    ssd = sim._calculate_dynamic_ssd(follower, leader, 100.0)
    
    # Should be positive and reasonable
    assert ssd > 0, "SSD should be positive"
    assert ssd > sim.min_ssd_m, f"SSD should be at least min_ssd ({sim.min_ssd_m})"
    
    # Test with no leader
    ssd_no_leader = sim._calculate_dynamic_ssd(follower, None, 0.0)
    assert ssd_no_leader == sim.min_ssd_m, "SSD with no leader should be min_ssd"


def test_perception_integration():
    """Test that perception data is properly integrated into simulation."""
    cfg = load_config()
    cfg["vehicles"]["count"] = 3
    sim = Simulation(cfg)
    
    # Position vehicles
    sim.vehicles[0].state.s_m = 0.0
    sim.vehicles[1].state.s_m = 50.0
    sim.vehicles[2].state.s_m = 100.0
    
    # Step simulation to update perception data
    sim.step(0.02)
    
    # Check that perception data is populated
    assert len(sim.perception_data) == 3, "Should have perception data for all vehicles"
    
    # Check first vehicle's perception
    perception = sim.perception_data[0]
    assert perception.leader_vehicle is not None, "Should have a leader"
    assert perception.leader_distance_m > 0, "Should have positive distance"
    assert perception.ssd_required_m > 0, "Should have positive SSD"
    assert not perception.is_occluded, "Should not be occluded"


def test_ssd_integration_with_idm():
    """Test that SSD is properly integrated into IDM controller."""
    cfg = load_config()
    cfg["vehicles"]["count"] = 2
    sim = Simulation(cfg)
    
    # Setup vehicles with different speeds
    sim.vehicles[0].state.s_m = 0.0
    sim.vehicles[0].state.v_mps = 25.0  # Fast follower
    sim.vehicles[1].state.s_m = 30.0
    sim.vehicles[1].state.v_mps = 15.0  # Slower leader
    
    # Set up driver parameters for strong braking
    sim.vehicles[0].driver.params.comfort_brake_mps2 = 4.0
    sim.vehicles[0].driver.params.reaction_time_s = 2.0
    
    # Step simulation
    sim.step(0.02)
    
    # Check that follower is braking due to SSD requirements
    follower_accel = sim.vehicles[0].state.a_mps2
    assert follower_accel < 0, f"Follower should be braking, got acceleration {follower_accel}"


def test_perception_deterministic():
    """Test that perception system is deterministic."""
    cfg = load_config()
    cfg["vehicles"]["count"] = 5
    cfg["random"]["master_seed"] = 12345
    sim1 = Simulation(cfg)
    sim2 = Simulation(cfg)
    
    # Step both simulations
    for _ in range(10):
        sim1.step(0.02)
        sim2.step(0.02)
    
    # Check that perception data is identical
    for i, (p1, p2) in enumerate(zip(sim1.perception_data, sim2.perception_data)):
        assert p1.leader_distance_m == p2.leader_distance_m, f"Distance mismatch for vehicle {i}"
        assert p1.is_occluded == p2.is_occluded, f"Occlusion mismatch for vehicle {i}"
        assert abs(p1.ssd_required_m - p2.ssd_required_m) < 1e-6, f"SSD mismatch for vehicle {i}"


def test_visual_range_limits():
    """Test that visual range limits are respected."""
    cfg = load_config()
    cfg["perception"]["visual_range_m"] = 50.0  # Short range
    cfg["vehicles"]["count"] = 3
    sim = Simulation(cfg)
    
    # Position vehicles far apart
    sim.vehicles[0].state.s_m = 0.0
    sim.vehicles[1].state.s_m = 30.0   # Within range
    sim.vehicles[2].state.s_m = 80.0   # Outside range
    
    # Test perception
    leader, distance, is_occluded = sim._find_first_unobstructed_leader(0)
    
    # Should find the closer vehicle, not the far one
    assert leader is not None, "Should find a leader"
    assert distance <= 50.0, f"Distance should be within visual range, got {distance}"
    assert leader == sim.vehicles[1], "Should find the closer vehicle"


def test_ssd_safety_margin():
    """Test that SSD safety margin is applied correctly."""
    cfg = load_config()
    cfg["perception"]["ssd_safety_margin"] = 1.5
    cfg["vehicles"]["count"] = 2
    sim = Simulation(cfg)
    
    # Setup vehicles
    follower = sim.vehicles[0]
    leader = sim.vehicles[1]
    follower.state.v_mps = 20.0
    leader.state.v_mps = 15.0
    
    # Calculate SSD
    ssd = sim._calculate_dynamic_ssd(follower, leader, 100.0)
    
    # Calculate expected SSD without safety margin
    reaction_time = follower.driver.params.reaction_time_s
    reaction_distance = follower.state.v_mps * reaction_time
    b_f = follower.driver.params.comfort_brake_mps2
    b_l = leader.driver.params.comfort_brake_mps2
    v_f = follower.state.v_mps
    v_l = leader.state.v_mps
    
    expected_ssd = max(2.0, reaction_distance + (v_f**2) / (2.0 * b_f) - (v_l**2) / (2.0 * b_l))
    expected_ssd *= 1.5  # Apply safety margin
    
    # Check that safety margin is applied
    assert abs(ssd - expected_ssd) < 1e-6, f"SSD should include safety margin: {ssd} vs {expected_ssd}"


def test_hud_data_preparation():
    """Test that HUD data preparation works correctly."""
    from traffic_sim.core.simulation import PerceptionData
    
    # Create test perception data
    perception_data = [
        PerceptionData(None, 0.0, False, 5.0, 200.0),
        PerceptionData(None, 50.0, True, 10.0, 200.0),
        PerceptionData(None, 100.0, False, 15.0, 200.0)
    ]
    
    # Test data calculations that would be used in HUD
    total_vehicles = len(perception_data)
    occluded_count = sum(1 for p in perception_data if p.is_occluded)
    avg_ssd = sum(p.ssd_required_m for p in perception_data) / total_vehicles
    max_ssd = max(p.ssd_required_m for p in perception_data)
    min_ssd = min(p.ssd_required_m for p in perception_data)
    
    # Verify calculations
    assert total_vehicles == 3
    assert occluded_count == 1
    assert avg_ssd == 10.0
    assert max_ssd == 15.0
    assert min_ssd == 5.0


def test_hud_toggle_integration():
    """Test that HUD toggle works without crashing in simulation."""
    cfg = load_config()
    cfg["vehicles"]["count"] = 3
    sim = Simulation(cfg)
    
    # Step simulation to populate perception data
    sim.step(0.02)
    
    # Test that perception data is available for HUD
    assert len(sim.perception_data) == 3, "Should have perception data for all vehicles"
    
    # Test that perception data has expected structure
    for i, perception in enumerate(sim.perception_data):
        assert hasattr(perception, 'leader_vehicle')
        assert hasattr(perception, 'leader_distance_m')
        assert hasattr(perception, 'is_occluded')
        assert hasattr(perception, 'ssd_required_m')
        assert hasattr(perception, 'visual_range_m')
        assert perception.visual_range_m == sim.visual_range_m


if __name__ == "__main__":
    pytest.main([__file__])

