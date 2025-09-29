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
    from numba import njit

    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False


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
        Vectorized physics update for all vehicles.
        Args:
            actions (np.ndarray): Commanded accelerations (N,)
            dt (float): Timestep
            track_length (float): Track length for arc wrap
            air_density (float): Air density for drag
        Returns:
            np.ndarray: Updated state array (N, 4)
        """
        s = self.state[:, 0]
        v = self.state[:, 1]
        # a = self.state[:, 2]  # Unused
        # Vehicle specs
        mass = self.vehicle_specs[:, 0]
        power_kw = self.vehicle_specs[:, 1]
        torque_nm = self.vehicle_specs[:, 2]
        drag_area_cda = self.vehicle_specs[:, 3]
        tire_friction_mu = self.vehicle_specs[:, 4]
        brake_efficiency_eta = self.vehicle_specs[:, 5]

        # 1. Apply physical constraints (vectorized)
        # Deceleration: a >= -ημg
        gravity = 9.81
        min_decel = -brake_efficiency_eta * tire_friction_mu * gravity

        # Power/torque limits for positive accel
        power_watts = power_kw * 1000.0
        power_limited_accel = np.where(v > 0.1, power_watts / (mass * v), np.inf)
        wheel_radius = 0.3
        torque_limited_accel = torque_nm / wheel_radius / mass
        max_accel = np.minimum(power_limited_accel, torque_limited_accel)

        # Clamp commanded acceleration
        a_cmd = np.clip(actions, min_decel, max_accel)

        # 2. Aerodynamic drag (vectorized)
        drag_force = 0.5 * air_density * drag_area_cda * v * v
        drag_accel = -drag_force / mass

        # 3. Total acceleration
        a_total = a_cmd + drag_accel

        # 4. Update velocity (no negative speeds)
        v_new = np.maximum(0.0, v + a_total * dt)

        # 5. Update position (arc-length, wrap around track)
        s_new = (s + v_new * dt) % track_length

        # 6. Write back
        self.state[:, 0] = s_new
        self.state[:, 1] = v_new
        self.state[:, 2] = a_total
        # (Optional) heading unchanged

        return self.state
