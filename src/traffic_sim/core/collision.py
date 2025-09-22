from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
import pymunk
import time
from traffic_sim.core.vehicle import Vehicle
from traffic_sim.core.track import StadiumTrack


@dataclass
class CollisionEvent:
    """Collision event data."""

    timestamp: float
    vehicle1_id: int
    vehicle2_id: int
    location_m: float
    delta_v: float
    ttc_at_impact: float
    collision_type: str  # "rear_end", "side_swipe", "head_on"


@dataclass
class VehiclePhysicsState:
    """Physics state for pymunk integration."""

    body: pymunk.Body
    shape: pymunk.Poly
    is_disabled: bool
    disable_time_remaining: float
    original_position: Tuple[float, float]
    original_angle: float
    blink_timer: float  # For visual blinking effect
    blink_state: bool  # Current blink state


class CollisionSystem:
    """Collision detection and physics simulation using pymunk."""

    def __init__(self, config: Dict[str, Any], track: StadiumTrack):
        self.config = config
        self.track = track

        self.space = pymunk.Space()
        self.space.gravity = (0, 0)  # No gravity for 2D traffic simulation

        # Vehicle physics states
        self.vehicle_physics: Dict[int, VehiclePhysicsState] = {}
        self.collision_events: List[CollisionEvent] = []

        # Collision configuration
        self.use_pymunk_impulse = config.get("collisions", {}).get("use_pymunk_impulse", True)
        self.disable_time_s = config.get("collisions", {}).get("disable_time_s", 5.0)
        self.lateral_push = config.get("collisions", {}).get("lateral_push", True)

        # Collision detection parameters
        self.collision_threshold = 0.5  # meters
        self.ttc_threshold = 2.0  # seconds

    def add_vehicle(self, vehicle: Vehicle, vehicle_id: int) -> None:
        """Add vehicle to physics simulation."""
        # Create pymunk body
        mass = vehicle.spec.mass_kg
        moment = pymunk.moment_for_box(mass, (vehicle.spec.length_m, vehicle.spec.width_m))
        body = pymunk.Body(mass, moment)

        # Set initial position and angle
        x_m, y_m, theta = self.track.position_heading(vehicle.state.s_m)
        body.position = x_m, y_m
        body.angle = theta

        # Create collision shape
        half_width = vehicle.spec.width_m / 2
        half_length = vehicle.spec.length_m / 2
        vertices = [
            (-half_length, -half_width),
            (half_length, -half_width),
            (half_length, half_width),
            (-half_length, half_width),
        ]
        shape = pymunk.Poly(body, vertices)
        shape.friction = 0.7
        shape.elasticity = 0.3

        # Add to space
        self.space.add(body, shape)

        # Store physics state
        self.vehicle_physics[vehicle_id] = VehiclePhysicsState(
            body=body,
            shape=shape,
            is_disabled=False,
            disable_time_remaining=0.0,
            original_position=(x_m, y_m),
            original_angle=theta,
            blink_timer=0.0,
            blink_state=False,
        )

        # Set up collision handler
        handler = self.space.add_collision_handler(1, 1)  # Vehicle-vehicle collisions
        handler.begin = self._on_collision_begin

    def update_vehicle_position(self, vehicle: Vehicle, vehicle_id: int) -> None:
        """Update vehicle position in physics simulation."""
        if vehicle_id not in self.vehicle_physics:
            return

        physics_state = self.vehicle_physics[vehicle_id]

        if physics_state.is_disabled:
            # Update disable timer
            physics_state.disable_time_remaining -= 1.0 / 60.0  # Assuming 60 FPS

            # Update blink timer for visual effect
            physics_state.blink_timer += 1.0 / 60.0
            if physics_state.blink_timer >= 0.5:  # Blink every 0.5 seconds
                physics_state.blink_state = not physics_state.blink_state
                physics_state.blink_timer = 0.0

            if physics_state.disable_time_remaining <= 0:
                self._reenable_vehicle(vehicle_id)
            return

        # Update position and angle
        x_m, y_m, theta = self.track.position_heading(vehicle.state.s_m)
        physics_state.body.position = x_m, y_m
        physics_state.body.angle = theta

        # Apply lateral push if configured
        if self.lateral_push and abs(vehicle.state.a_mps2) > 2.0:
            # Apply lateral force based on acceleration
            lateral_force = vehicle.state.a_mps2 * 0.1  # Scale factor
            physics_state.body.apply_force_at_local_point(
                (0, lateral_force * physics_state.body.mass), (0, 0)
            )

    def check_collisions(self, vehicles: List[Vehicle]) -> List[CollisionEvent]:
        """Check for collisions and return collision events."""
        new_events = []

        # Simple collision detection based on distance
        for i, vehicle1 in enumerate(vehicles):
            for j, vehicle2 in enumerate(vehicles[i + 1 :], i + 1):
                if self._vehicles_colliding(vehicle1, vehicle2):
                    event = self._create_collision_event(vehicle1, vehicle2, i, j)
                    if event:
                        new_events.append(event)
                        self.collision_events.append(event)
                        self._handle_collision(vehicle1, vehicle2, i, j)

        return new_events

    def _vehicles_colliding(self, vehicle1: Vehicle, vehicle2: Vehicle) -> bool:
        """Check if two vehicles are colliding."""
        # Calculate distance along track
        L = self.track.total_length_m
        distance = abs(vehicle1.state.s_m - vehicle2.state.s_m) % L

        # Check if within collision threshold
        collision_distance = (
            vehicle1.spec.length_m + vehicle2.spec.length_m
        ) / 2 + self.collision_threshold
        return distance < collision_distance

    def _create_collision_event(
        self, vehicle1: Vehicle, vehicle2: Vehicle, id1: int, id2: int
    ) -> Optional[CollisionEvent]:
        """Create collision event data."""
        # Calculate relative speed and TTC
        relative_speed = abs(vehicle1.state.v_mps - vehicle2.state.v_mps)
        L = self.track.total_length_m
        distance = abs(vehicle1.state.s_m - vehicle2.state.s_m) % L

        ttc = distance / relative_speed if relative_speed > 0.1 else float("inf")

        # Calculate delta_v (speed change)
        delta_v = abs(vehicle1.state.v_mps - vehicle2.state.v_mps)

        # Determine collision type
        collision_type = self._determine_collision_type(vehicle1, vehicle2)

        return CollisionEvent(
            timestamp=time.time(),
            vehicle1_id=id1,
            vehicle2_id=id2,
            location_m=(vehicle1.state.s_m + vehicle2.state.s_m) / 2,
            delta_v=delta_v,
            ttc_at_impact=ttc,
            collision_type=collision_type,
        )

    def _determine_collision_type(self, vehicle1: Vehicle, vehicle2: Vehicle) -> str:
        """Determine type of collision based on relative positions and speeds."""
        # Simple heuristic - in a real implementation, this would be more sophisticated
        if abs(vehicle1.state.v_mps - vehicle2.state.v_mps) > 5.0:
            return "rear_end"
        elif abs(vehicle1.state.s_m - vehicle2.state.s_m) > self.track.total_length_m / 2:
            return "head_on"
        else:
            return "side_swipe"

    def _handle_collision(self, vehicle1: Vehicle, vehicle2: Vehicle, id1: int, id2: int) -> None:
        """Handle collision effects."""
        if not self.use_pymunk_impulse:
            return

        # Apply impulse to both vehicles
        if id1 in self.vehicle_physics and id2 in self.vehicle_physics:
            physics1 = self.vehicle_physics[id1]
            physics2 = self.vehicle_physics[id2]

            # Calculate impulse based on relative velocity
            relative_velocity = vehicle1.state.v_mps - vehicle2.state.v_mps
            impulse_magnitude = abs(relative_velocity) * 1000  # Scale factor

            # Apply lateral push
            if self.lateral_push:
                # Push vehicles apart laterally
                lateral_impulse = impulse_magnitude * 0.3
                physics1.body.apply_impulse_at_local_point((0, lateral_impulse), (0, 0))
                physics2.body.apply_impulse_at_local_point((0, -lateral_impulse), (0, 0))

            # Disable vehicles temporarily
            self._disable_vehicle(id1)
            self._disable_vehicle(id2)

    def _disable_vehicle(self, vehicle_id: int) -> None:
        """Disable vehicle for specified time."""
        if vehicle_id in self.vehicle_physics:
            physics_state = self.vehicle_physics[vehicle_id]
            physics_state.is_disabled = True
            physics_state.disable_time_remaining = self.disable_time_s
            physics_state.blink_timer = 0.0
            physics_state.blink_state = False

            # Make vehicle semi-transparent or add visual effect
            physics_state.shape.color = (255, 0, 0, 128)  # Red with transparency

    def _reenable_vehicle(self, vehicle_id: int) -> None:
        """Re-enable vehicle after disable period."""
        if vehicle_id in self.vehicle_physics:
            physics_state = self.vehicle_physics[vehicle_id]
            physics_state.is_disabled = False
            physics_state.disable_time_remaining = 0.0

            # Restore normal appearance
            physics_state.shape.color = (100, 180, 255, 255)  # Normal blue

    def _on_collision_begin(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data: Dict) -> bool:
        """Handle collision begin event."""
        # This is called by pymunk when collision begins
        # We can add additional collision handling here
        return True

    def get_collision_events(self) -> List[CollisionEvent]:
        """Get all collision events."""
        return self.collision_events.copy()

    def get_recent_collision_events(self, time_window_s: float = 60.0) -> List[CollisionEvent]:
        """Get recent collision events within time window."""
        current_time = time.time()
        cutoff_time = current_time - time_window_s
        return [event for event in self.collision_events if event.timestamp > cutoff_time]

    def clear_old_events(self, max_age_s: float = 300.0) -> None:
        """Clear old collision events to prevent memory buildup."""
        current_time = time.time()
        cutoff_time = current_time - max_age_s
        self.collision_events = [
            event for event in self.collision_events if event.timestamp > cutoff_time
        ]

    def step_physics(self, dt_s: float) -> None:
        """Step physics simulation."""
        if self.use_pymunk_impulse:
            self.space.step(dt_s)

    def get_vehicle_visual_state(self, vehicle_id: int) -> Dict[str, Any]:
        """
        Get visual state for rendering a vehicle.

        Args:
            vehicle_id: ID of the vehicle

        Returns:
            Dictionary containing visual state information
        """
        if vehicle_id not in self.vehicle_physics:
            return {"is_disabled": False, "blink_state": False, "alpha": 255}

        physics_state = self.vehicle_physics[vehicle_id]

        # Calculate alpha based on blink state
        alpha = 128 if physics_state.is_disabled else 255
        if physics_state.is_disabled and not physics_state.blink_state:
            alpha = 64  # Very transparent when blinking off

        return {
            "is_disabled": physics_state.is_disabled,
            "blink_state": physics_state.blink_state,
            "alpha": alpha,
            "disable_time_remaining": physics_state.disable_time_remaining,
        }

    def cleanup(self) -> None:
        """Clean up physics simulation."""
        # Remove all bodies and shapes
        for physics_state in self.vehicle_physics.values():
            self.space.remove(physics_state.body, physics_state.shape)

        self.vehicle_physics.clear()
        self.collision_events.clear()
