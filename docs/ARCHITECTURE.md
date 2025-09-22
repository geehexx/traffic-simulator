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
- **Live Analytics**: Real-time speed histogram, headway distribution, near-miss counter
- **Collision System**: Pymunk physics integration with lateral push effects and vehicle disable
- **Data Logging**: Comprehensive incident tracking, performance metrics, and CSV export

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

#### Driver Parameter Ranges

Core parameters with realistic distributions and bounds:
- **Reaction Time**: \( t_r \sim \mathcal{N}(2.5, 0.6) \) s → [0.8, 4.0]
- **Desired Headway**: \( T \sim \mathcal{N}(1.6, 0.5) \) s → [0.6, 3.0]
- **Comfortable Deceleration**: \( b_{\text{comf}} \sim \mathcal{N}(2.5, 0.7) \) m/s² → [1.0, 4.0]
- **Maximum Deceleration**: \( b_{\max} \sim \mathcal{N}(7.0, 1.0) \) m/s² → [4.0, 9.0]
- **Jerk Limit**: \( j_{\max} \sim \mathcal{N}(4.0, 1.0) \) m/s³ → [1.0, 7.0]
- **Throttle Lag**: \( \tau_{\text{throttle}} \sim \mathcal{N}(0.25, 0.10) \) s → [0.05, 1.0]
- **Brake Lag**: \( \tau_{\text{brake}} \sim \mathcal{N}(0.15, 0.07) \) s → [0.05, 1.0]
- **Aggression**: \( A \sim \mathcal{N}(0,1) \) (latent, transformed to rule adherence)
- **Rule Adherence**: \( R = \text{sigmoid}(A) \in [0, 1] \)

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

### 4. Vehicle Physics System {#id:vehicle-physics}
**File**: [vehicle.py](mdc:src/traffic_sim/core/vehicle.py)

The traffic simulator implements a comprehensive vehicle physics system that models realistic vehicle behavior through power, torque, aerodynamic drag, and friction constraints.

#### Core Physics Attributes

- **Power (kW)**: Engine power output affecting acceleration capabilities
- **Torque (Nm)**: Maximum torque affecting low-speed acceleration
- **Drag Area (CdA)**: Aerodynamic drag coefficient × frontal area (m²)
- **Wheelbase (m)**: Distance between front and rear axles
- **Tire Friction (μ)**: Coefficient of friction between tires and road
- **Brake Efficiency (η)**: Efficiency of braking system

#### Physics Calculations

The system implements several key physics calculations:

- **Acceleration Curves**: `a_max(v)` based on power and torque limits
- **Aerodynamic Drag**: `F_d = 0.5 * ρ * C_d * A * v²`
- **Physical Constraints**: `a ≥ -ημg` (braking limit)
- **Power/Torque Limits**: Realistic acceleration based on engine characteristics

```python
class Vehicle:
    def calculate_max_acceleration(self, velocity_mps: float) -> float:
        """Calculate max acceleration based on power and torque limits."""
        # Power limit: a_power = P / (m * v)
        # Torque limit: a_torque = T / (m * r_wheel)
        return min(power_limit, torque_limit)

    def calculate_aerodynamic_drag_force(self, velocity_mps: float) -> float:
        """Calculate aerodynamic drag force."""
        # F_d = 0.5 * ρ * C_d * A * v²
        return 0.5 * air_density * self.spec.drag_area_cda * velocity_mps**2

    def apply_physical_constraints(self, commanded_accel_mps2: float) -> float:
        """Apply physical braking constraint: a ≥ -ημg"""
        max_decel = -self.spec.tire_friction_mu * self.spec.brake_efficiency_eta * gravity
        return max(commanded_accel_mps2, max_decel)
```

#### Vehicle Types and Physics

Different vehicle types have distinct physics characteristics:

- **Sedans**: Balanced power/torque (100-200 kW), moderate drag (0.3-0.4 CdA)
  - Examples: Toyota Camry, Honda Accord, Ford Fusion
- **SUVs**: Higher mass, increased drag area (0.4-0.5 CdA), higher torque
  - Examples: Ford Explorer, Toyota Highlander, Honda CR-V
- **Trucks/Vans**: High torque (300-500 Nm), significant drag (0.6-0.8 CdA)
  - Examples: Ford F-150, Chevrolet Silverado 1500, Ram 1500, Ford Transit, Mercedes-Benz Sprinter, Ram ProMaster
- **Buses**: Very high mass (15,000+ kg), large drag area (1.0+ CdA)
  - Examples: Blue Bird All American, Thomas Saf-T-Liner, IC Bus CE
- **Motorbikes**: Low mass (200-300 kg), minimal drag (0.2-0.3 CdA), high power-to-weight ratio
  - Examples: Harley-Davidson Sportster, Yamaha YZF-R6, Honda CBR600RR

#### Default Vehicle Composition

The simulation uses a configurable vehicle mix with realistic distribution:
- **Sedans**: 55% (default)
- **SUVs**: 25% (default)
- **Trucks/Vans**: 10% (default)
- **Buses**: 5% (default)
- **Motorbikes**: 5% (default)

#### Performance Benchmarks

The physics system is designed to maintain:
- **≥30 FPS** with 20+ vehicles
- **10× speed factor** stability without instability
- **Deterministic replay** with fixed seeds

### 5. Visual Effects System {#id:visual-effects}
**File**: [collision.py](mdc:src/traffic_sim/core/collision.py)

The simulator includes visual effects for enhanced user experience and feedback.

#### Vehicle Disable Effects

- **Blinking Animation**: Disabled vehicles blink with configurable timing
- **Alpha Transparency**: Semi-transparent rendering during disable period
- **State Tracking**: Visual state management for rendering pipeline

```python
class CollisionSystem:
    def get_vehicle_visual_state(self, vehicle_id: int) -> Dict[str, Any]:
        """Get visual state for rendering a vehicle."""
        physics_state = self.vehicle_physics[vehicle_id]
        alpha = 128 if physics_state.is_disabled else 255
        if physics_state.is_disabled and not physics_state.blink_state:
            alpha = 64
        return {
            "is_disabled": physics_state.is_disabled,
            "blink_state": physics_state.blink_state,
            "alpha": alpha
        }
```

#### Collision Effects

- **Particle Effects**: Visual feedback for collision events
- **State Transitions**: Smooth visual state changes
- **Performance Optimized**: Efficient rendering with minimal impact

### 6. Track Geometry
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

### 6. Live Analytics System
**File**: [analytics.py](mdc:src/traffic_sim/core/analytics.py)

Real-time analytics collection and processing:
- Speed histogram with statistical measures (mean, median, percentiles)
- Headway distribution analysis with dangerous/critical thresholds
- Near-miss detection and counting based on TTC
- Performance metrics tracking (FPS, memory usage)
- Incident logging and categorization

```python
class LiveAnalytics:
    def __init__(self, config: Dict[str, Any]):
        self.speed_history = collections.deque(maxlen=1000)
        self.headway_history = collections.deque(maxlen=1000)
        self.near_miss_events: List[NearMissEvent] = []
        self.incident_log: List[IncidentLog] = []
        self.ttc_threshold = 1.5  # seconds

    def update_analytics(self, vehicles: List[Vehicle],
                        perception_data: List[Optional[PerceptionData]],
                        dt_s: float) -> None:
        """Update all analytics with current simulation state."""
        self._update_speed_data(vehicles)
        self._update_headway_data(vehicles, perception_data)
        self._check_near_misses(vehicles, perception_data, time.time())
```

### 7. Collision System
**File**: [collision.py](mdc:src/traffic_sim/core/collision.py)

Pymunk-based collision detection and physics simulation:
- Vehicle-vehicle collision detection with AABB overlap
- Physics-based impulse response with lateral push effects
- Vehicle disable system with configurable duration
- Collision event logging with delta-v and TTC data

```python
class CollisionSystem:
    def __init__(self, config: Dict[str, Any], track: StadiumTrack):
        self.space = pymunk.Space()
        self.vehicle_physics: Dict[int, VehiclePhysicsState] = {}
        self.collision_events: List[CollisionEvent] = []
        self.use_pymunk_impulse = config.get("collisions", {}).get("use_pymunk_impulse", True)
        self.disable_time_s = config.get("collisions", {}).get("disable_time_s", 5.0)

    def add_vehicle(self, vehicle: Vehicle, vehicle_id: int) -> None:
        """Add vehicle to physics simulation with collision shapes."""
        # Create pymunk body and collision shape
        # Set up collision handlers
        # Store physics state for disable/recovery
```

### 8. Data Logging System
**File**: [logging.py](mdc:src/traffic_sim/core/logging.py)

Comprehensive data logging with CSV export:
- Vehicle state snapshots with driver parameters
- Simulation aggregate data and performance metrics
- Incident and near-miss event logging
- Configurable logging rates for different data types
- CSV export with structured data format

```python
class DataLogger:
    def __init__(self, config: Dict[str, Any]):
        self.output_path = Path(config.get("logging", {}).get("output_path", "runs/run_001.csv"))
        self.aggregate_rate_hz = config.get("logging", {}).get("aggregate_rate_hz", 10)
        self.per_vehicle_rate_hz = config.get("logging", {}).get("per_vehicle_trace_rate_hz", 2)

    def log_simulation_step(self, vehicles: List[Vehicle],
                           perception_data: List[Optional[PerceptionData]],
                           analytics: LiveAnalytics, dt_s: float) -> None:
        """Log simulation step data with configurable rates."""
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
- **Quality Gates**: Automated quality enforcement

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
Optimized HUD with pre-created text objects and occlusion-aware panels:

#### HUD Occlusion Panel Features
The HUD system includes advanced occlusion-aware panels that provide real-time safety analytics:

- **Occlusion Detection**: Sector-based visibility analysis for each vehicle
- **SSD Metrics**: Dynamic Stopping Sight Distance calculations with occlusion factors
- **Performance Optimization**: 10Hz refresh rate independent of physics simulation
- **Deterministic Rendering**: Respects fixed-step simulation and seeded RNG requirements
- **Configuration Integration**: Toggle-able via configuration settings

#### HUD Rendering Architecture
```python
class OptimizedHUD:
    def __init__(self) -> None:
        self.text_objects = {}
        self.occlusion_data = None
        self.refresh_rate = 0.1  # 10Hz
        self.last_refresh = 0.0
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
