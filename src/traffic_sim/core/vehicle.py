from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
import random

from traffic_sim.core.driver import Driver


@dataclass
class VehicleSpec:
    name: str
    length_m: float
    width_m: float
    mass_kg: float


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
            self.internal.throttle_lag_filter = alpha * self.internal.actual_accel_mps2 + (1 - alpha) * self.internal.throttle_lag_filter
        else:
            self.internal.throttle_lag_filter = 0.0
        
        # Brake lag (for negative acceleration)
        if self.internal.actual_accel_mps2 < 0:
            tau_brake = self.driver.params.brake_lag_s
            alpha = dt_s / (tau_brake + dt_s) if tau_brake > 0 else 1.0
            self.internal.brake_lag_filter = alpha * self.internal.actual_accel_mps2 + (1 - alpha) * self.internal.brake_lag_filter
        else:
            self.internal.brake_lag_filter = 0.0
        
        # Final acceleration is the sum of throttle and brake responses
        self.state.a_mps2 = self.internal.throttle_lag_filter + self.internal.brake_lag_filter
    
    def set_commanded_acceleration(self, accel_mps2: float) -> None:
        """Set the commanded acceleration (what the controller wants)."""
        self.internal.commanded_accel_mps2 = accel_mps2


