from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from traffic_sim.core.driver import Driver


@dataclass
class VehicleSpec:
    name: str
    length_m: float
    width_m: float
    mass_kg: float
    # Physics attributes
    power_kw: float  # Engine power in kilowatts
    torque_nm: float  # Maximum torque in Newton-meters
    drag_area_cda: float  # Drag coefficient × frontal area (m²)
    wheelbase_m: float  # Distance between front and rear axles
    tire_friction_mu: float  # Tire friction coefficient μ
    brake_efficiency_eta: float  # Brake efficiency η


@dataclass
class VehicleState:
    s_m: float  # arc length along track centerline
    v_mps: float
    a_mps2: float


@dataclass
class VehicleInternalState:
    """Internal state for jerk limiting and drivetrain lag."""

    commanded_accel_mps2: float  # What the controller wants
    actual_accel_mps2: float  # What actually happens after lag
    jerk_mps3: float  # Current jerk
    throttle_lag_filter: float  # First-order filter state
    brake_lag_filter: float  # First-order filter state


class Vehicle:
    def __init__(
        self,
        spec: VehicleSpec,
        state: VehicleState,
        driver: Driver,
        color_rgb: Optional[Tuple[int, int, int]] = None,
    ):
        self.spec = spec
        self.state = state
        self.driver = driver
        self.color_rgb: Tuple[int, int, int] = color_rgb or (100, 180, 255)
        self.internal = VehicleInternalState(
            commanded_accel_mps2=0.0,
            actual_accel_mps2=0.0,
            jerk_mps3=0.0,
            throttle_lag_filter=0.0,
            brake_lag_filter=0.0,
        )

    def update_internal_state(self, dt_s: float) -> None:
        """Update internal state with jerk limiting and drivetrain lag."""
        # Jerk limiting
        max_jerk = self.driver.params.jerk_limit_mps3
        desired_change = self.internal.commanded_accel_mps2 - self.internal.actual_accel_mps2

        # Clamp jerk to limits
        if desired_change > max_jerk * dt_s:
            actual_change = max_jerk * dt_s
        elif desired_change < -max_jerk * dt_s:
            actual_change = -max_jerk * dt_s
        else:
            actual_change = desired_change

        # Update actual acceleration with jerk limiting
        self.internal.actual_accel_mps2 += actual_change
        self.internal.jerk_mps3 = actual_change / dt_s if dt_s > 0 else 0.0

        # Apply drivetrain lag filters
        # Throttle lag (for positive acceleration)
        if self.internal.actual_accel_mps2 > 0:
            tau_throttle = self.driver.params.throttle_lag_s
            alpha = dt_s / (tau_throttle + dt_s) if tau_throttle > 0 else 1.0
            self.internal.throttle_lag_filter = (
                alpha * self.internal.actual_accel_mps2
                + (1 - alpha) * self.internal.throttle_lag_filter
            )
        else:
            self.internal.throttle_lag_filter = 0.0

        # Brake lag (for negative acceleration)
        if self.internal.actual_accel_mps2 < 0:
            tau_brake = self.driver.params.brake_lag_s
            alpha = dt_s / (tau_brake + dt_s) if tau_brake > 0 else 1.0
            self.internal.brake_lag_filter = (
                alpha * self.internal.actual_accel_mps2
                + (1 - alpha) * self.internal.brake_lag_filter
            )
        else:
            self.internal.brake_lag_filter = 0.0

        # Final acceleration is the sum of throttle and brake responses
        self.state.a_mps2 = self.internal.throttle_lag_filter + self.internal.brake_lag_filter

    def set_commanded_acceleration(self, accel_mps2: float) -> None:
        """Set the commanded acceleration (what the controller wants)."""
        self.internal.commanded_accel_mps2 = accel_mps2

    def calculate_max_acceleration(self, velocity_mps: float) -> float:
        """
        Calculate maximum acceleration based on power and torque limits.

        Args:
            velocity_mps: Current velocity in m/s

        Returns:
            Maximum achievable acceleration in m/s²
        """
        # Convert power to torque at current velocity
        # P = F * v = m * a * v, so a = P / (m * v)
        power_watts = self.spec.power_kw * 1000.0

        if velocity_mps > 0.1:  # Avoid division by zero
            power_limited_accel = power_watts / (self.spec.mass_kg * velocity_mps)
        else:
            power_limited_accel = float("inf")

        # Torque-limited acceleration (simplified model)
        # Assuming torque is applied at wheel radius ~0.3m
        wheel_radius = 0.3  # meters
        torque_limited_accel = (self.spec.torque_nm / wheel_radius) / self.spec.mass_kg

        # Return the more limiting factor
        return min(power_limited_accel, torque_limited_accel)

    def calculate_aerodynamic_drag_force(
        self, velocity_mps: float, air_density: float = 1.225
    ) -> float:
        """
        Calculate aerodynamic drag force.

        Args:
            velocity_mps: Vehicle velocity in m/s
            air_density: Air density in kg/m³ (default: 1.225 at sea level)

        Returns:
            Drag force in Newtons
        """
        # F_d = 0.5 * ρ * C_d * A * v²
        return 0.5 * air_density * self.spec.drag_area_cda * velocity_mps * velocity_mps

    def calculate_physical_constraint_limit(self, gravity_mps2: float = 9.81) -> float:
        """
        Calculate maximum deceleration based on physical constraints.

        Physical constraint: a ≥ -ημg

        Args:
            gravity_mps2: Gravitational acceleration in m/s²

        Returns:
            Maximum deceleration (most negative acceleration) in m/s²
        """
        return -self.spec.brake_efficiency_eta * self.spec.tire_friction_mu * gravity_mps2

    def apply_physical_constraints(
        self, commanded_accel_mps2: float, gravity_mps2: float = 9.81
    ) -> float:
        """
        Apply physical constraints to commanded acceleration.

        Args:
            commanded_accel_mps2: Desired acceleration in m/s²
            gravity_mps2: Gravitational acceleration in m/s²

        Returns:
            Constrained acceleration in m/s²
        """
        # Apply deceleration constraint: a ≥ -ημg
        min_decel = self.calculate_physical_constraint_limit(gravity_mps2)

        # Apply power/torque limits for positive acceleration
        if commanded_accel_mps2 > 0:
            max_accel = self.calculate_max_acceleration(self.state.v_mps)
            commanded_accel_mps2 = min(commanded_accel_mps2, max_accel)

        # Apply deceleration constraint
        return max(commanded_accel_mps2, min_decel)
