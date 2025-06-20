from __future__ import annotations


import pytest

from traffic_sim.models.driver_specs import DriverDistribution


class TestDriverDistribution:
    """Test the DriverDistribution dataclass."""

    def test_distribution_creation(self) -> None:
        """Test creating a driver distribution with all fields."""
        dist = DriverDistribution(mean=0.5, std=0.1, min=0.0, max=1.0)

        assert dist.mean == 0.5
        assert dist.std == 0.1
        assert dist.min == 0.0
        assert dist.max == 1.0

    def test_distribution_immutable(self) -> None:
        """Test that distribution is immutable (frozen dataclass)."""
        dist = DriverDistribution(mean=0.5, std=0.1, min=0.0, max=1.0)

        # Should not be able to modify fields
        with pytest.raises(AttributeError):
            dist.mean = 0.6

    def test_distribution_equality(self) -> None:
        """Test that distributions with same values are equal."""
        dist1 = DriverDistribution(0.5, 0.1, 0.0, 1.0)
        dist2 = DriverDistribution(0.5, 0.1, 0.0, 1.0)
        dist3 = DriverDistribution(0.6, 0.1, 0.0, 1.0)

        assert dist1 == dist2
        assert dist1 != dist3


def test_driver_creation():
    """Test creating a driver with parameters."""
    from traffic_sim.core.driver import Driver, DriverParams
    import random

    params = DriverParams(
        headway_T_s=1.5,
        reaction_time_s=0.5,
        comfort_brake_mps2=2.0,
        max_brake_mps2=8.0,
        jerk_limit_mps3=2.0,
        throttle_lag_s=0.1,
        brake_lag_s=0.1,
        aggression_z=0.2,
        rule_adherence=0.8,
        desired_speed_mps=25.0,
    )

    rng = random.Random(42)
    driver = Driver(params, rng)

    assert driver.params == params
    assert driver.rng == rng
    assert driver.speeding.is_speeding is False
    assert driver.lambda_off > 0
    assert driver.lambda_on > 0


def test_sample_driver_params():
    """Test sampling driver parameters."""
    from traffic_sim.core.driver import sample_driver_params
    import random

    # Test with a simple config
    cfg = {
        "drivers": {
            "headway_T_s": {"mean": 1.5, "std": 0.2, "min": 0.5, "max": 3.0},
            "reaction_time_s": {"mean": 0.5, "std": 0.1, "min": 0.2, "max": 1.0},
            "comfort_brake_mps2": {"mean": 2.0, "std": 0.5, "min": 1.0, "max": 4.0},
            "max_brake_mps2": {"mean": 8.0, "std": 1.0, "min": 5.0, "max": 12.0},
            "jerk_limit_mps3": {"mean": 2.0, "std": 0.5, "min": 1.0, "max": 4.0},
            "throttle_lag_s": {"mean": 0.1, "std": 0.02, "min": 0.05, "max": 0.2},
            "brake_lag_s": {"mean": 0.1, "std": 0.02, "min": 0.05, "max": 0.2},
            "aggression_z": {"mean": 0.0, "std": 1.0, "min": -2.0, "max": 2.0},
            "rule_adherence": {"mean": 0.8, "std": 0.1, "min": 0.5, "max": 1.0},
            "desired_speed_mps": {"mean": 25.0, "std": 5.0, "min": 15.0, "max": 35.0},
        }
    }

    rng = random.Random(42)
    params = sample_driver_params(cfg, rng)

    # Check that all required parameters are present and have reasonable values
    assert hasattr(params, "headway_T_s")
    assert hasattr(params, "reaction_time_s")
    assert hasattr(params, "comfort_brake_mps2")
    assert hasattr(params, "max_brake_mps2")
    assert hasattr(params, "jerk_limit_mps3")
    assert hasattr(params, "throttle_lag_s")
    assert hasattr(params, "brake_lag_s")
    assert hasattr(params, "aggression_z")
    assert hasattr(params, "rule_adherence")
    assert hasattr(params, "desired_speed_mps")

    # Check that values are within reasonable ranges (allow some tolerance for sampling)
    assert 0.1 <= params.headway_T_s <= 5.0
    assert 0.1 <= params.reaction_time_s <= 3.0
    assert 0.5 <= params.comfort_brake_mps2 <= 6.0
    assert 3.0 <= params.max_brake_mps2 <= 15.0
    assert 0.5 <= params.jerk_limit_mps3 <= 6.0
    assert 0.01 <= params.throttle_lag_s <= 0.5
    assert 0.01 <= params.brake_lag_s <= 0.5
    assert -3.0 <= params.aggression_z <= 3.0
    assert 0.1 <= params.rule_adherence <= 1.0
    assert 10.0 <= params.desired_speed_mps <= 50.0


def test_sample_driver_params_exception_handling():
    """Test that sample_driver_params handles exceptions gracefully."""
    from traffic_sim.core.driver import sample_driver_params
    import random

    # Test with invalid config that should trigger exception handling
    cfg = {
        "drivers": {
            "headway_T_s": {"mean": 1.5, "std": 0.2, "min": 0.5, "max": 3.0},
            # Missing other required parameters to trigger exception
        }
    }

    rng = random.Random(42)
    # This should not raise an exception due to the try-except block
    params = sample_driver_params(cfg, rng)

    # Should still return a valid DriverParams object
    assert hasattr(params, "headway_T_s")
    assert hasattr(params, "reaction_time_s")
    assert hasattr(params, "comfort_brake_mps2")
    assert hasattr(params, "max_brake_mps2")
    assert hasattr(params, "jerk_limit_mps3")
    assert hasattr(params, "throttle_lag_s")
    assert hasattr(params, "brake_lag_s")
    assert hasattr(params, "aggression_z")
    assert hasattr(params, "rule_adherence")
    assert hasattr(params, "desired_speed_mps")


if __name__ == "__main__":
    pytest.main([__file__])
