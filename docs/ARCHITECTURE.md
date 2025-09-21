# Architecture Guide

This document provides a comprehensive overview of the traffic simulator's architecture, design patterns, and technical implementation details.

## Table of Contents
- [System Overview](#system-overview)
- [Core Components](#core-components)
- [Design Patterns](#design-patterns)
- [Mathematical Foundations](#mathematical-foundations)
- [Performance Considerations](#performance-considerations)
- [State Management](#state-management)
- [Rendering Architecture](#rendering-architecture)
- [Configuration Architecture](#configuration-architecture)

## System Overview

The traffic simulator is a 2D Python application that simulates multi-vehicle traffic on a stadium-shaped loop. It combines realistic driver behavior modeling, dynamic safety analytics, and real-time visualization.

### Key Features
- **Stadium Track**: Parameterized geometry with safety calculations
- **Statistical Drivers**: Gaussian copula sampling with correlations
- **IDM Controller**: Intelligent Driver Model with per-driver parameters
- **Perception System**: Occlusion-based visibility and dynamic SSD
- **Safety Analytics**: AASHTO/TxDOT-style curve speed calculations
- **Live HUD**: Real-time safety panels and perception data

### Technology Stack
- **Rendering**: Arcade 3.3.x for 2D graphics
- **Physics**: Pymunk for collision detection and response
- **Data**: NumPy for numerical computations
- **Configuration**: YAML for human-readable settings
- **Testing**: Pytest with Hypothesis for property-based testing

## Core Components

### 1. Simulation Engine
**File**: [simulation.py](mdc:src/traffic_sim/core/simulation.py)

The main simulation loop that orchestrates all components:
- Fixed-step physics simulation (Δt = 0.02s)
- Vehicle state updates and collision detection
- Perception system and dynamic SSD calculation
- Event logging and performance monitoring

```python
class Simulation:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.vehicles: List[Vehicle] = []
        self.track = Track(config['track'])
        self.perception_data: List[PerceptionData] = []

    def step(self, dt_s: float) -> None:
        """Main simulation step with fixed timestep."""
        # Update vehicle states
        # Calculate perception and SSD
        # Handle collisions
        # Update HUD data
```

### 2. Driver Behavior Model
**File**: [driver.py](mdc:src/traffic_sim/core/driver.py)

Statistical driver model with correlated parameters:
- Gaussian copula sampling for realistic parameter correlations
- Per-driver IDM controller parameters
- Markov chain speeding behavior
- Jerk limiting and drivetrain lag

```python
@dataclass
class DriverParams:
    reaction_time_s: float
    headway_T_s: float
    comfort_brake_mps2: float
    max_brake_mps2: float
    jerk_limit_mps3: float
    # ... more parameters

class Driver:
    def update_speeding_state(self, dt_s: float, speed_limit_mps: float) -> None:
        """Update speeding state using Markov chain."""
        # Two-state Markov chain: Compliant ↔ Speeding
```

### 3. Vehicle Dynamics
**File**: [vehicle.py](mdc:src/traffic_sim/core/vehicle.py)

Vehicle physics and state management:
- IDM acceleration calculation
- Jerk limiting and drivetrain lag
- State updates with physical constraints
- Collision detection and response

```python
class Vehicle:
    def set_commanded_acceleration(self, accel_mps2: float) -> None:
        """Set commanded acceleration with jerk limiting."""
        # Apply jerk limit: ȧ ∈ [-j_max, +j_max]

    def update_internal_state(self, dt_s: float) -> None:
        """Update vehicle state with drivetrain lag."""
        # First-order filters for throttle/brake lag
```

### 4. Track Geometry
**File**: [track.py](mdc:src/traffic_sim/core/track.py)

Stadium track geometry and safety calculations:
- Parameterized track with total length and straight fraction
- Safety speed calculations per AASHTO/TxDOT standards
- Coordinate transformations between world and track space

```python
class Track:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.length_m = config['length_m']
        self.straight_fraction = config['straight_fraction']
        self.radius = self._calculate_radius()

    def _calculate_radius(self) -> float:
        """Calculate semicircle radius: R = L(1-r)/(2π)"""
        return self.length_m * (1 - self.straight_fraction) / (2 * math.pi)
```

### 5. Perception System
**File**: [simulation.py](mdc:src/traffic_sim/core/simulation.py)

Occlusion-based perception and dynamic SSD:
- Line-of-sight calculations for vehicle visibility
- Dynamic SSD calculation with relative speed
- Integration with IDM controller

```python
def _find_first_unobstructed_leader(self, vehicle_idx: int) -> Tuple[Optional[Vehicle], float, bool]:
    """Find first unobstructed leader with occlusion detection."""
    # Line-of-sight calculations
    # Dynamic SSD: g_req = max(s0, d_r + v_f²/(2b_f) - v_ℓ²/(2b_ℓ))
```

## Design Patterns

### 1. IDM Controller Pattern
The Intelligent Driver Model (IDM) is implemented as a per-driver controller:

```python
def calculate_idm_acceleration(
    v_f: float, v_l: float, s: float, params: DriverParams
) -> float:
    """
    IDM acceleration: a = a_max[1 - (v/v_0)^δ - (s*/s)²]
    where s* = s_0 + vT + vΔv/(2√(a_max b_comf))
    """
    s_star = params.min_gap_m + v_f * params.headway_T_s + \
             (v_f * (v_f - v_l)) / (2 * math.sqrt(params.max_accel_mps2 * params.comfort_brake_mps2))

    return params.max_accel_mps2 * (
        1 - (v_f / params.desired_speed_mps) ** params.idm_delta -
        (s_star / max(s, 0.1)) ** 2
    )
```

### 2. Perception Pattern
Occlusion-based perception with dynamic SSD:

```python
def calculate_dynamic_ssd(
    v_f: float, v_l: float, reaction_time: float,
    b_f: float, b_l: float
) -> float:
    """Calculate dynamic SSD with relative speed."""
    reaction_distance = v_f * reaction_time
    required_gap = max(
        self.min_ssd_m,
        reaction_distance + v_f**2/(2*b_f) - v_l**2/(2*b_l)
    )
    return required_gap
```

### 3. State Management Pattern
Immutable state objects with clear separation:

```python
@dataclass(frozen=True)
class VehicleState:
    s_m: float  # Position along track
    v_mps: float  # Velocity
    a_mps2: float  # Acceleration
    jerk_mps3: float  # Jerk

    def update(self, dt_s: float) -> 'VehicleState':
        """Return new state with updated values."""
        return VehicleState(
            s_m=self.s_m + self.v_mps * dt_s,
            v_mps=self.v_mps + self.a_mps2 * dt_s,
            a_mps2=self.a_mps2,  # Updated by controller
            jerk_mps3=self.jerk_mps3  # Updated by controller
        )
```

## Mathematical Foundations

### 1. Track Geometry
Stadium track with parameterized geometry:

- **Total Length**: L (meters)
- **Straight Fraction**: r (unitless, default 0.30)
- **Radius**: R = L(1-r)/(2π)
- **Straight Length**: S = rL/2

### 2. Safety Calculations
AASHTO/TxDOT-style curve speed calculations:

- **Minimum Safe Radius**: R_min = V²/(127(e + f))
- **Safe Speed**: V_safe = √(127R(e + f))
- **Required Length**: L_needed = 2πR_min/(1-r)

Where:
- V = design speed (km/h)
- e = superelevation (m/m)
- f = side friction factor (unitless)

### 3. IDM Equations
Intelligent Driver Model acceleration:

- **Acceleration**: a = a_max[1 - (v/v_0)^δ - (s*/s)²]
- **Desired Gap**: s* = s_0 + vT + vΔv/(2√(a_max b_comf))

Where:
- v = current velocity
- v_0 = desired velocity
- s = current gap
- T = time headway
- Δv = velocity difference

### 4. Dynamic SSD
Dynamic Stopping Sight Distance:

- **Reaction Distance**: d_r = v_f × t_r
- **Required Gap**: g_req = max(s_0, d_r + v_f²/(2b_f) - v_ℓ²/(2b_ℓ))

Where:
- v_f = follower velocity
- v_ℓ = leader velocity
- t_r = reaction time
- b_f, b_ℓ = deceleration rates

## Performance Considerations

### 1. Simulation Loop Optimization
- **Fixed Timestep**: Deterministic physics with accumulator
- **Vectorized Operations**: NumPy for numerical computations
- **Caching**: Expensive calculations (SSD, perception)
- **Profiling**: Regular performance monitoring

### 2. Rendering Optimization
- **Text Objects**: Pre-created HUD elements
- **Minimal Draw Calls**: Batch similar operations
- **Coordinate Caching**: Avoid repeated calculations
- **Frame Rate Independence**: Interpolation between states

### 3. Memory Management
- **Object Reuse**: Minimize allocations in hot paths
- **Pre-allocation**: Arrays with known sizes
- **Garbage Collection**: Minimize object creation
- **Memory Profiling**: Track usage patterns

### 4. Algorithm Optimization
- **Spatial Partitioning**: Efficient collision detection
- **Early Termination**: Perception range limits
- **Branchless Code**: Performance-critical paths
- **Fast Approximations**: Cached inverse sqrt

## State Management

### 1. Immutable State
State objects are immutable to ensure thread safety and prevent bugs:

```python
@dataclass(frozen=True)
class SimulationState:
    vehicles: Tuple[Vehicle, ...]
    time_s: float
    step_count: int

    def add_vehicle(self, vehicle: Vehicle) -> 'SimulationState':
        return SimulationState(
            vehicles=self.vehicles + (vehicle,),
            time_s=self.time_s,
            step_count=self.step_count
        )
```

### 2. State Updates
Clear separation between state and behavior:

```python
def update_vehicle_states(self, dt_s: float) -> None:
    """Update all vehicle states."""
    for vehicle in self.vehicles:
        # Calculate new acceleration
        accel = self._calculate_acceleration(vehicle)
        vehicle.set_commanded_acceleration(accel)

        # Update internal state
        vehicle.update_internal_state(dt_s)
```

### 3. Event Logging
Comprehensive event logging for debugging and analysis:

```python
@dataclass
class Event:
    timestamp: float
    event_type: str
    vehicle_id: int
    data: Dict[str, Any]

class EventLogger:
    def log_collision(self, vehicle1: Vehicle, vehicle2: Vehicle) -> None:
        """Log collision event with details."""
        event = Event(
            timestamp=self.simulation_time,
            event_type="collision",
            vehicle_id=vehicle1.id,
            data={"other_vehicle": vehicle2.id, "location": vehicle1.state.s_m}
        )
        self.events.append(event)
```

## Rendering Architecture

### 1. Arcade Integration
Arcade 3.3.x compatibility with type stubs:

```python
class TrafficSimWindow(arcade.Window):
    def __init__(self, simulation: Simulation) -> None:
        super().__init__(width=1200, height=800, title="Traffic Simulator")
        self.simulation = simulation
        self.hud = OptimizedHUD()

    def on_draw(self) -> None:
        """Render simulation and HUD."""
        self.clear()
        self._draw_track()
        self._draw_vehicles()
        self.hud.draw(self.simulation.perception_data)
```

### 2. Coordinate Systems
World coordinates (meters) to screen coordinates (pixels):

```python
def world_to_screen(self, world_pos: Tuple[float, float]) -> Tuple[float, float]:
    """Convert world coordinates to screen coordinates."""
    x, y = world_pos
    screen_x = (x - self.world_bounds[0]) * self.scale + self.screen_bounds[0]
    screen_y = (y - self.world_bounds[1]) * self.scale + self.screen_bounds[1]
    return screen_x, screen_y
```

### 3. HUD System
Optimized HUD with pre-created text objects:

```python
class OptimizedHUD:
    def __init__(self) -> None:
        self.text_objects = {}
        self._create_text_objects()

    def _create_text_objects(self) -> None:
        """Pre-create text objects for performance."""
        self.text_objects = {
            'fps': arcade.Text("FPS: 0", 10, 10, arcade.color.WHITE, 12),
            'vehicles': arcade.Text("Vehicles: 0", 10, 30, arcade.color.WHITE, 12),
            # ... more text objects
        }
```

## Configuration Architecture

### 1. YAML Configuration
Human-readable configuration with validation:

```yaml
track:
  length_m: 1000
  straight_fraction: 0.30
  speed_limit_kmh: 100
  safety_design_speed_kmh: 120

drivers:
  distributions:
    reaction_time_s: {mean: 2.5, std: 0.6, min: 0.8, max: 4.0}
    headway_T_s: {mean: 1.6, std: 0.5, min: 0.6, max: 3.0}
  correlations:
    A_T: -0.5
    A_b_comf: 0.3
```

### 2. Configuration Loading
Type-safe configuration loading with defaults:

```python
def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration with environment variable override."""
    if config_path is None:
        config_path = os.getenv('TRAFFIC_SIM_CONFIG', 'config/config.yaml')

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Apply defaults and validate
    config = apply_defaults(config)
    validate_config(config)

    return config
```

### 3. Environment Variables
Support for environment-specific overrides:

```bash
# Custom configuration
export TRAFFIC_SIM_CONFIG=config/production.yaml

# Debug logging
export TRAFFIC_SIM_LOG_LEVEL=DEBUG

# Performance monitoring
export TRAFFIC_SIM_PROFILE=true
```

This architecture guide provides comprehensive coverage of the traffic simulator's technical implementation, design patterns, and performance considerations.
