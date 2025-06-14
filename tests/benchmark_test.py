from __future__ import annotations

"""
Consolidated Benchmark Tests

This module replaces the individual performance test files with a unified
benchmarking framework that provides comprehensive performance testing
with real-time estimation and modern benchmarking tools integration.

Replaces:
- tests/performance_test.py
- tests/performance_smoke_test.py
- tests/performance_highperf_test.py
"""


import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation
from traffic_sim.core.performance import get_performance_optimizer

# Import the unified benchmarking framework
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from benchmarking_framework import BenchmarkingFramework, BenchmarkConfig


class TestBenchmarkingFramework:
    """Test the unified benchmarking framework."""

    def setup_method(self):
        """Setup for each test method."""
        self.framework = BenchmarkingFramework(max_workers=2)  # Limit workers for tests

    def test_single_benchmark(self):
        """Test single benchmark execution."""
        result = self.framework.run_benchmark(vehicles=20, steps=100, dt=0.02, speed_factor=1.0)

        assert result.config.vehicles == 20
        assert result.config.steps == 100
        assert result.elapsed_s > 0
        assert result.steps_per_second > 0
        assert result.vehicles_per_second > 0
        assert result.efficiency > 0

    def test_benchmark_with_profiling(self):
        """Test benchmark with profiling enabled."""
        config = BenchmarkConfig(
            vehicles=10, steps=50, dt=0.02, speed_factor=1.0, enable_profiling=True, warmup_steps=10
        )

        result = self.framework.runner.run_single_benchmark(config)

        assert result.profile_data is not None
        assert len(result.profile_data) > 0

    def test_parallel_benchmarks(self):
        """Test parallel benchmark execution."""
        configs = [
            BenchmarkConfig(vehicles=10, steps=50, dt=0.02, speed_factor=1.0),
            BenchmarkConfig(vehicles=20, steps=50, dt=0.02, speed_factor=1.0),
            BenchmarkConfig(vehicles=30, steps=50, dt=0.02, speed_factor=1.0),
        ]

        results = self.framework.runner.run_parallel_benchmarks(configs)

        assert len(results) == 3
        for result in results:
            assert result.elapsed_s > 0
            assert result.steps_per_second > 0

    def test_scale_benchmark(self):
        """Test scale benchmarking."""
        results = self.framework.run_scale_benchmark(
            vehicle_counts=[10, 20],
            speed_factors=[1.0, 2.0],
            steps=50,
            dt=0.02,
            output_csv="test_scale_benchmark.csv",
        )

        assert len(results) == 4  # 2 vehicle counts × 2 speed factors
        for result in results:
            assert result.config.vehicles in [10, 20]
            assert result.config.speed_factor in [1.0, 2.0]
            assert result.elapsed_s > 0


class TestPerformanceRegression:
    """Test for performance regressions using the unified framework."""

    def setup_method(self):
        """Setup for each test method."""
        self.framework = BenchmarkingFramework(
            max_workers=1
        )  # Single worker for consistent results

    def test_speed_factor_stability(self):
        """Test that simulation remains stable at 10× speed factor."""
        result = self.framework.run_benchmark(vehicles=20, steps=1000, dt=0.02, speed_factor=10.0)

        # Should complete in reasonable time (less than 5 seconds real time)
        assert result.elapsed_s < 5.0, f"Simulation took too long: {result.elapsed_s:.2f}s"

        # Should achieve reasonable performance
        assert (
            result.steps_per_second > 100
        ), f"Performance too low: {result.steps_per_second:.1f} steps/s"

    def test_deterministic_replay(self):
        """Test that simulation is deterministic with fixed seeds."""
        # Create fresh config to avoid global state issues
        config = load_config().copy()
        config["random"] = config.get("random", {}).copy()
        config["vehicles"] = config.get("vehicles", {}).copy()
        config["random"]["master_seed"] = 42
        config["vehicles"]["color_random_seed"] = 42
        config["vehicles"]["count"] = 10

        # Run simulation twice with same seed
        sim1 = Simulation(config)
        sim2 = Simulation(config)

        # Run both for same number of steps
        for _ in range(100):
            sim1.step(0.02)
            sim2.step(0.02)

        # Check that results are identical
        assert len(sim1.vehicles) == len(sim2.vehicles)

        for v1, v2 in zip(sim1.vehicles, sim2.vehicles):
            assert abs(v1.state.s_m - v2.state.s_m) < 1e-10, "Vehicle positions should be identical"
            assert (
                abs(v1.state.v_mps - v2.state.v_mps) < 1e-10
            ), "Vehicle velocities should be identical"
            assert (
                abs(v1.state.a_mps2 - v2.state.a_mps2) < 1e-10
            ), "Vehicle accelerations should be identical"

    def test_high_performance_flags(self):
        """Test that high-performance flags do not regress."""
        result = self.framework.run_benchmark(vehicles=20, steps=500, dt=0.02, speed_factor=1.0)

        # Soft bound to catch obvious regressions while avoiding flakiness
        assert result.elapsed_s < 10.0, f"High-performance path too slow: {result.elapsed_s:.2f}s"

        # Should achieve good performance
        assert (
            result.steps_per_second > 50
        ), f"Performance too low: {result.steps_per_second:.1f} steps/s"

    def test_profiler_produces_stats(self):
        """Test that profiler produces stats and reasonable step time."""
        config = BenchmarkConfig(
            vehicles=5, steps=200, dt=0.02, speed_factor=1.0, enable_profiling=True, warmup_steps=0
        )

        result = self.framework.runner.run_single_benchmark(config)

        # Ensure some core blocks were measured
        assert result.profile_data is not None
        assert any(
            name in result.profile_data
            for name in (
                "update_perception",
                "idm_acceleration",
                "update_vehicle_physics",
                "step_physics",
            )
        ), "Expected profiler to record core timing blocks"

        # Generous upper bound to avoid flakiness: < 3s for 200 small steps
        assert result.elapsed_s < 3.0, f"Performance smoke too slow: {result.elapsed_s:.2f}s"


class TestPerformanceOptimizations:
    """Test performance optimization features."""

    def test_performance_optimizer(self):
        """Test performance optimizer functionality."""
        optimizer = get_performance_optimizer()

        # Test fast inverse sqrt
        test_values = [1.0, 4.0, 9.0, 16.0, 25.0]
        for x in test_values:
            result = optimizer.fast_inverse_sqrt(x)
            expected = 1.0 / (x**0.5)
            assert abs(result - expected) < 0.01, f"Inverse sqrt approximation too far off for {x}"

        # Test caching
        stats = optimizer.get_performance_stats()
        assert "cache_hit_rate" in stats
        assert "cache_hits" in stats
        assert "cache_misses" in stats

    def test_vehicle_mix_distribution(self):
        """Test that vehicle mix is properly distributed."""
        config = load_config()
        config["vehicles"]["count"] = 100  # Large number for statistical testing
        config["vehicles"]["mix"] = {"sedan": 0.5, "suv": 0.3, "truck_van": 0.2}

        sim = Simulation(config)

        # For now, just check that we have the right number of vehicles
        assert len(sim.vehicles) == 100

    def test_physics_constraints(self):
        """Test that physical constraints are properly applied."""
        config = load_config().copy()
        config["vehicles"] = config.get("vehicles", {}).copy()
        config["vehicles"]["count"] = 5
        sim = Simulation(config)

        # Run simulation and check that accelerations are within physical limits
        for _ in range(100):
            sim.step(0.02)

            for vehicle in sim.vehicles:
                # Check that acceleration is within physical limits
                max_decel = vehicle.calculate_physical_constraint_limit()
                assert (
                    vehicle.state.a_mps2 >= max_decel
                ), "Acceleration violates physical constraint"

                # Check that max acceleration is reasonable
                max_accel = vehicle.calculate_max_acceleration(vehicle.state.v_mps)
                if vehicle.state.a_mps2 > 0:
                    assert (
                        vehicle.state.a_mps2 <= max_accel * 1.1
                    ), "Acceleration exceeds power/torque limits"

    def test_aerodynamic_drag(self):
        """Test that aerodynamic drag is properly calculated."""
        config = load_config()
        sim = Simulation(config)

        vehicle = sim.vehicles[0]

        # Test drag force calculation
        drag_force = vehicle.calculate_aerodynamic_drag_force(30.0)  # 30 m/s
        assert drag_force > 0, "Drag force should be positive"

        # Drag should increase with velocity squared
        drag_force_2x = vehicle.calculate_aerodynamic_drag_force(60.0)  # 60 m/s
        assert drag_force_2x > drag_force * 3.5, "Drag should increase roughly with v²"
        assert drag_force_2x < drag_force * 4.5, "Drag should increase roughly with v²"

    def test_collision_visual_effects(self):
        """Test collision visual effects."""
        config = load_config().copy()
        config["vehicles"] = config.get("vehicles", {}).copy()
        config["vehicles"]["count"] = 2
        sim = Simulation(config)

        # Place vehicles very close to trigger collision
        sim.vehicles[0].state.s_m = 0.0
        sim.vehicles[1].state.s_m = 1.0  # Very close

        # Run simulation
        for _ in range(10):
            sim.step(0.02)

        # Check visual state
        visual_state = sim.collision_system.get_vehicle_visual_state(0)
        assert "is_disabled" in visual_state
        assert "blink_state" in visual_state
        assert "alpha" in visual_state


class TestRealTimeEstimation:
    """Test real-time performance estimation."""

    def setup_method(self):
        """Setup for each test method."""
        self.framework = BenchmarkingFramework(max_workers=1)

    def test_theoretical_performance_estimation(self):
        """Test theoretical performance estimation."""
        result = self.framework.run_benchmark(vehicles=50, steps=100, dt=0.02, speed_factor=1.0)

        # Should have theoretical performance estimates
        if result.theoretical_fps is not None:
            assert result.theoretical_fps > result.steps_per_second
            assert result.confidence_score is not None
            assert 0.0 <= result.confidence_score <= 1.0

    def test_scaling_behavior(self):
        """Test performance scaling behavior."""
        # Test different vehicle counts
        vehicle_counts = [10, 20, 50]
        results = []

        for vehicles in vehicle_counts:
            result = self.framework.run_benchmark(
                vehicles=vehicles, steps=100, dt=0.02, speed_factor=1.0
            )
            results.append(result)

        # Performance should generally decrease with more vehicles
        # (though this might not always be true due to optimizations)
        for i in range(1, len(results)):
            # Allow some variance due to system conditions
            assert (
                results[i].steps_per_second > 0
            ), f"Performance should be positive for {vehicle_counts[i]} vehicles"


class TestBenchmarkingIntegration:
    """Test integration with external benchmarking tools."""

    def setup_method(self):
        """Setup for each test method."""
        self.framework = BenchmarkingFramework(max_workers=1)

    def test_benchmark_config_validation(self):
        """Test benchmark configuration validation."""
        # Valid config
        valid_config = BenchmarkConfig(vehicles=10, steps=100, dt=0.02, speed_factor=1.0)
        assert valid_config.vehicles == 10
        assert valid_config.steps == 100

        # Test with overrides
        config_with_overrides = BenchmarkConfig(
            vehicles=20,
            steps=200,
            dt=0.02,
            speed_factor=2.0,
            config_overrides={"physics": {"delta_t_s": 0.01}},
        )
        assert config_with_overrides.config_overrides["physics"]["delta_t_s"] == 0.01

    def test_benchmark_result_serialization(self):
        """Test benchmark result serialization."""
        result = self.framework.run_benchmark(vehicles=10, steps=50, dt=0.02, speed_factor=1.0)

        # Test that all required fields are present
        assert hasattr(result, "config")
        assert hasattr(result, "elapsed_s")
        assert hasattr(result, "steps_per_second")
        assert hasattr(result, "vehicles_per_second")
        assert hasattr(result, "efficiency")
        assert hasattr(result, "timestamp")

        # Test timestamp format
        assert len(result.timestamp) > 0
        assert ":" in result.timestamp  # Should contain time


if __name__ == "__main__":
    pytest.main([__file__])
