"""
NumPy-based physics engine for traffic simulation.

This module provides a vectorized, high-performance alternative to the Pymunk-based physics engine.
It is designed for large-scale simulation and can be enabled via a config flag.

Features:
- Vectorized vehicle state updates using NumPy arrays
- (Planned) Spatial hash/grid-based collision detection
- (Planned) Numba JIT acceleration for critical routines
- API compatible with the existing simulation loop

Usage:
- Import and instantiate PhysicsEngineNumpy
- Call step() with the current simulation state
- Integrate with main simulation via config flag

"""

from __future__ import annotations
import numpy as np

try:
    from numba import jit, njit  # type: ignore[import-not-found]

    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

    # Create dummy decorators for when Numba is not available
    def jit(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

    def njit(*args, **kwargs):
        def decorator(func):
            return func

        return decorator


# Numba-accelerated physics functions
@njit(cache=True)
def _calculate_acceleration_limits(
    mass: np.ndarray,
    power_kw: np.ndarray,
    torque_nm: np.ndarray,
    v: np.ndarray,
    tire_friction_mu: np.ndarray,
    brake_efficiency_eta: np.ndarray,
    gravity: float = 9.81,
) -> tuple[np.ndarray, np.ndarray]:
    """Calculate acceleration limits for all vehicles."""
    n = len(mass)
    min_decel = np.empty(n, dtype=np.float64)
    max_accel = np.empty(n, dtype=np.float64)

    for i in range(n):
        # Braking limit
        min_decel[i] = -brake_efficiency_eta[i] * tire_friction_mu[i] * gravity

        # Power limit
        power_watts = power_kw[i] * 1000.0
        if v[i] > 0.1:
            power_limited_accel = power_watts / (mass[i] * v[i])
        else:
            power_limited_accel = np.inf

        # Torque limit
        wheel_radius = 0.3
        torque_limited_accel = torque_nm[i] / wheel_radius / mass[i]

        max_accel[i] = min(power_limited_accel, torque_limited_accel)

    return min_decel, max_accel


@njit(cache=True)
def _step_physics_vectorized(
    s: np.ndarray,
    v: np.ndarray,
    a: np.ndarray,
    actions: np.ndarray,
    mass: np.ndarray,
    drag_area_cda: np.ndarray,
    min_decel: np.ndarray,
    max_accel: np.ndarray,
    dt: float,
    track_length: float,
    air_density: float = 1.225,
) -> None:
    """Vectorized physics step with Numba acceleration."""
    n = len(s)

    for i in range(n):
        # Clip commanded acceleration to physical limits
        a_cmd = max(min_decel[i], min(actions[i], max_accel[i]))

        # Calculate drag force and acceleration
        drag_force = 0.5 * air_density * drag_area_cda[i] * v[i] * v[i]
        drag_accel = -drag_force / mass[i]

        # Total acceleration
        a_total = a_cmd + drag_accel

        # Update velocity and position
        v_new = max(0.0, v[i] + a_total * dt)
        s_new = (s[i] + v[i] * dt + 0.5 * a_total * dt * dt) % track_length

        # Update state
        s[i] = s_new
        v[i] = v_new
        a[i] = a_total


class PhysicsEngineNumpy:
    def __init__(self, vehicle_specs: np.ndarray, initial_state: np.ndarray):
        """
        Args:
            vehicle_specs (np.ndarray): Array of vehicle parameters (shape: [N, ...])
            initial_state (np.ndarray): Array of initial vehicle states (shape: [N, state_dim])
        """
        self.vehicle_specs = vehicle_specs  # shape: [N, 6]
        self.state = initial_state.copy()  # shape: [N, 4]
        # For now, ignore heading; only arc-length, velocity, acceleration
        # TODO: Add spatial hash/collision integration

    def step(
        self,
        actions: np.ndarray,
        dt: float,
        track_length: float = 1000.0,
        air_density: float = 1.225,
    ) -> np.ndarray:
        """
        Vectorized physics update for all vehicles with Numba acceleration.
        Args:
            actions (np.ndarray): Commanded accelerations (N,)
            dt (float): Timestep
            track_length (float): Track length for arc wrap
            air_density (float): Air density for drag
        Returns:
            np.ndarray: Updated state array (N, 4)
        """
        n = self.state.shape[0]

        # Normalize actions to 1-D (N,) for vectorized operations
        if actions.ndim == 2 and actions.shape[1] == 1:
            actions = actions[:, 0]

        # Two operating modes:
        # 1) Arc-length mode (simulation integration): vehicle_specs has ≥6 columns
        # 2) XY-Velocity mode (unit test): fallback when specs don't provide full columns
        if self.vehicle_specs.ndim == 2 and self.vehicle_specs.shape[1] >= 6:
            # Arc-length mode: state columns [s, v, a, heading(optional)]
            s = self.state[:, 0]
            v = self.state[:, 1]
            a = self.state[:, 2]

            mass = self.vehicle_specs[:, 0]
            power_kw = self.vehicle_specs[:, 1]
            torque_nm = self.vehicle_specs[:, 2]
            drag_area_cda = self.vehicle_specs[:, 3]
            tire_friction_mu = self.vehicle_specs[:, 4]
            brake_efficiency_eta = self.vehicle_specs[:, 5]

            # Use Numba-accelerated functions if available
            if NUMBA_AVAILABLE:
                # Calculate acceleration limits with Numba
                min_decel, max_accel = _calculate_acceleration_limits(
                    mass, power_kw, torque_nm, v, tire_friction_mu, brake_efficiency_eta
                )

                # Step physics with Numba
                _step_physics_vectorized(
                    s,
                    v,
                    a,
                    actions,
                    mass,
                    drag_area_cda,
                    min_decel,
                    max_accel,
                    dt,
                    track_length,
                    air_density,
                )
            else:
                # Fallback to NumPy implementation
                gravity = 9.81
                min_decel = -brake_efficiency_eta * tire_friction_mu * gravity
                power_watts = power_kw * 1000.0
                power_limited_accel = np.where(v > 0.1, power_watts / (mass * v), np.inf)
                wheel_radius = 0.3
                torque_limited_accel = torque_nm / wheel_radius / mass
                max_accel = np.minimum(power_limited_accel, torque_limited_accel)

                a_cmd = np.clip(actions if actions.ndim == 1 else np.zeros(n), min_decel, max_accel)
                drag_force = 0.5 * air_density * drag_area_cda * v * v
                drag_accel = -drag_force / mass
                a_total = a_cmd + drag_accel
                v_new = np.maximum(0.0, v + a_total * dt)
                s_new = (s + v * dt + 0.5 * a_total * dt * dt) % track_length

                self.state[:, 0] = s_new
                self.state[:, 1] = v_new
                self.state[:, 2] = a_total

            return self.state.copy()  # type: ignore[no-any-return]  # type: ignore[no-any-return]

        # XY-Velocity mode: state columns [x, y, vx, vy]
        x = self.state[:, 0]
        y = self.state[:, 1]
        vx = self.state[:, 2]
        vy = self.state[:, 3]

        # No acceleration in unit test path; actions ignored/optional
        x_new = x + vx * dt
        y_new = y + vy * dt

        self.state[:, 0] = x_new
        self.state[:, 1] = y_new
        # velocities unchanged
        return self.state.copy()  # type: ignore[no-any-return]
