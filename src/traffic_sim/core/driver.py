from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Tuple
import random
import math


@dataclass
class DriverParams:
    """Driver parameters with realistic correlations and constraints."""

    reaction_time_s: float
    headway_T_s: float
    comfort_brake_mps2: float
    max_brake_mps2: float
    jerk_limit_mps3: float
    throttle_lag_s: float
    brake_lag_s: float
    aggression_z: float  # Latent aggression factor
    rule_adherence: float  # 0-1, higher = more rule-following
    desired_speed_mps: float  # v0 in IDM


@dataclass
class SpeedingState:
    """Two-state Markov chain for speeding behavior."""

    is_speeding: bool
    time_in_state_s: float
    overspeed_magnitude_kmh: float


class Driver:
    """Driver with behavioral parameters and speeding state."""

    def __init__(self, params: DriverParams, rng: random.Random):
        self.params = params
        self.rng = rng
        self.speeding = SpeedingState(
            is_speeding=False, time_in_state_s=0.0, overspeed_magnitude_kmh=0.0
        )
        self._update_speeding_rates()

    def _update_speeding_rates(self) -> None:
        """Update transition rates based on driver characteristics."""
        # Base rates from config
        self.lambda_off = 1.0 / 8.0  # Default episode duration
        self.lambda_on = 0.15 * self.lambda_off / (1.0 - 0.15)  # Default percent time

        # Adjust based on aggression and rule adherence
        aggression_factor = max(
            0.0, self.params.aggression_z
        )  # Only positive aggression increases speeding
        rule_factor = 1.0 - self.params.rule_adherence  # Higher rule adherence reduces speeding

        self.lambda_on *= (1.0 + aggression_factor) * rule_factor
        self.lambda_off *= 1.0 + rule_factor  # More rule-following = faster exit from speeding

    def update_speeding_state(self, dt_s: float, speed_limit_mps: float) -> None:
        """Update speeding state using two-state Markov chain."""
        self.speeding.time_in_state_s += dt_s

        # Check for state transition
        if self.speeding.is_speeding:
            # Currently speeding - check if should stop
            if self.rng.random() < self.lambda_off * dt_s:
                self.speeding.is_speeding = False
                self.speeding.time_in_state_s = 0.0
        else:
            # Currently compliant - check if should start speeding
            if self.rng.random() < self.lambda_on * dt_s:
                self.speeding.is_speeding = True
                self.speeding.time_in_state_s = 0.0
                # Sample overspeed magnitude
                self._sample_overspeed_magnitude()

    def _sample_overspeed_magnitude(self) -> None:
        """Sample overspeed magnitude based on driver characteristics."""
        # Base overspeed from config
        mean_base = 5.0
        mean_per_aggression = 4.0
        std = 3.0

        # Adjust mean based on aggression
        mean = mean_base + mean_per_aggression * max(0.0, self.params.aggression_z)

        # Sample and clamp
        overspeed = self.rng.gauss(mean, std)
        overspeed = max(0.0, min(25.0, overspeed))

        # Reduce by rule adherence
        overspeed *= 1.0 - self.params.rule_adherence

        self.speeding.overspeed_magnitude_kmh = overspeed

    def get_effective_speed_limit(self, speed_limit_mps: float) -> float:
        """Get effective speed limit considering current speeding state."""
        if not self.speeding.is_speeding:
            return speed_limit_mps

        # Add overspeed in m/s
        overspeed_mps = self.speeding.overspeed_magnitude_kmh / 3.6
        return speed_limit_mps + overspeed_mps


def _gaussian_copula_sample(
    rng: random.Random,
    means: list[float],
    stds: list[float],
    mins: list[float],
    maxs: list[float],
    correlation_matrix: list[list[float]],
) -> list[float]:
    """
    Sample correlated parameters using Gaussian copula.

    Args:
        rng: Random number generator
        means: List of means for each parameter
        stds: List of standard deviations for each parameter
        mins: List of minimum values for each parameter
        maxs: List of maximum values for each parameter
        correlation_matrix: Correlation matrix (symmetric, positive definite)

    Returns:
        List of sampled values, truncated to [min, max] ranges
    """
    n = len(means)

    # Generate independent standard normal samples
    z = [rng.gauss(0, 1) for _ in range(n)]

    # Apply correlation transformation
    # For simplicity, we'll use Cholesky decomposition approach
    # In practice, you might want to use a more robust method
    try:
        # Convert correlation matrix to covariance matrix
        cov_matrix = [
            [correlation_matrix[i][j] * stds[i] * stds[j] for j in range(n)] for i in range(n)
        ]

        # Simple approach: use the correlation matrix directly
        # This is a simplified version - for production use, implement proper Cholesky
        correlated_z = []
        for i in range(n):
            val = 0.0
            for j in range(n):
                val += correlation_matrix[i][j] * z[j]
            correlated_z.append(val)

        # Transform to desired distribution and truncate
        result = []
        for i in range(n):
            val = means[i] + stds[i] * correlated_z[i]
            val = max(mins[i], min(maxs[i], val))
            result.append(val)

        return result

    except Exception:
        # Fallback to independent sampling if correlation fails
        return [_trunc_gauss(rng, means[i], stds[i], mins[i], maxs[i]) for i in range(n)]


def _trunc_gauss(rng: random.Random, mean: float, std: float, min_v: float, max_v: float) -> float:
    """Simple rejection sampling for truncated normal distribution."""
    for _ in range(100):
        v = rng.gauss(mean, std)
        if min_v <= v <= max_v:
            return v
    return max(min_v, min(max_v, mean))


def sample_driver_params(cfg: Dict[str, Any], rng: random.Random) -> DriverParams:
    """
    Sample driver parameters using Gaussian copula for realistic correlations.

    Implements the v0 specification for driver parameter sampling with:
    - Correlated parameters using Gaussian copula
    - Realistic parameter ranges and distributions
    - Aggression and rule adherence factors
    """
    dist = cfg.get("drivers", {}).get("distributions", {})
    correlations = cfg.get("drivers", {}).get("correlations", {})

    def g(key: str, default: Dict[str, Any]) -> Dict[str, Any]:
        return dist.get(key, default)

    # Parameter definitions
    param_names = [
        "reaction_time_s",
        "headway_T_s",
        "comfort_brake_mps2",
        "max_brake_mps2",
        "jerk_limit_mps3",
        "throttle_lag_s",
        "brake_lag_s",
        "aggression_z",
        "rule_adherence_z",
    ]

    # Extract parameter configs
    param_configs = []
    for name in param_names:
        config = g(
            name,
            {
                "reaction_time_s": {"mean": 2.5, "std": 0.6, "min": 0.8, "max": 4.0},
                "headway_T_s": {"mean": 1.6, "std": 0.5, "min": 0.6, "max": 3.0},
                "comfort_brake_mps2": {"mean": 2.5, "std": 0.7, "min": 1.0, "max": 4.0},
                "max_brake_mps2": {"mean": 7.0, "std": 1.0, "min": 4.0, "max": 9.0},
                "jerk_limit_mps3": {"mean": 4.0, "std": 1.0, "min": 1.0, "max": 7.0},
                "throttle_lag_s": {"mean": 0.25, "std": 0.10, "min": 0.05, "max": 1.0},
                "brake_lag_s": {"mean": 0.15, "std": 0.07, "min": 0.05, "max": 1.0},
                "aggression_z": {"mean": 0.0, "std": 1.0, "min": -3.0, "max": 3.0},
                "rule_adherence_z": {"mean": 0.0, "std": 1.0, "min": -3.0, "max": 3.0},
            }[name],
        )
        param_configs.append(config)

    # Build correlation matrix
    n_params = len(param_names)
    corr_matrix = [[1.0 if i == j else 0.0 for j in range(n_params)] for i in range(n_params)]

    # Set correlations based on config
    corr_matrix[0][1] = corr_matrix[1][0] = correlations.get("A_T", -0.5)  # Aggression vs Headway
    corr_matrix[0][2] = corr_matrix[2][0] = correlations.get(
        "A_b_comf", 0.3
    )  # Aggression vs Comfort braking
    corr_matrix[0][8] = corr_matrix[8][0] = correlations.get(
        "R_A", -0.4
    )  # Rule adherence vs Aggression
    corr_matrix[0][0] = correlations.get(
        "distraction_t_reaction", 0.5
    )  # Distraction vs Reaction time

    # Extract means, stds, mins, maxs
    means = [config["mean"] for config in param_configs]
    stds = [config["std"] for config in param_configs]
    mins = [config["min"] for config in param_configs]
    maxs = [config["max"] for config in param_configs]

    # Sample correlated parameters
    sampled_values = _gaussian_copula_sample(rng, means, stds, mins, maxs, corr_matrix)

    # Convert rule adherence from z-score to 0-1 range using sigmoid
    rule_adherence_z = sampled_values[8]
    rule_adherence = 1.0 / (1.0 + math.exp(-rule_adherence_z))

    # Sample desired speed (v0) - this could be correlated with aggression
    # For now, use a simple distribution
    v0_mean = 27.0  # m/s (97 km/h)
    v0_std = 3.0
    v0_min = 20.0
    v0_max = 35.0
    desired_speed_mps = _trunc_gauss(rng, v0_mean, v0_std, v0_min, v0_max)

    return DriverParams(
        reaction_time_s=sampled_values[0],
        headway_T_s=sampled_values[1],
        comfort_brake_mps2=sampled_values[2],
        max_brake_mps2=sampled_values[3],
        jerk_limit_mps3=sampled_values[4],
        throttle_lag_s=sampled_values[5],
        brake_lag_s=sampled_values[6],
        aggression_z=sampled_values[7],
        rule_adherence=rule_adherence,
        desired_speed_mps=desired_speed_mps,
    )
