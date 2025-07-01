# Performance Guide

This document provides comprehensive performance optimization guidelines, monitoring strategies, and best practices for the traffic simulator.

## Table of Contents
- [Performance Targets](#performance-targets)
- [Optimization Strategies](#optimization-strategies)
- [Monitoring & Profiling](#monitoring--profiling)
- [Memory Management](#memory-management)
- [Rendering Optimization](#rendering-optimization)
- [Simulation Optimization](#simulation-optimization)
- [Performance Testing](#performance-testing)
- [Troubleshooting](#troubleshooting)

## Performance Targets

### Core Targets
- **Primary**: 30+ FPS with 20+ vehicles (baseline)
- **Stretch**: 1000+ vehicles at 100-1000x speed factors
- **Frame Rate**: 30+ FPS with 20+ vehicles
- **Memory Usage**: Minimal runtime allocations
- **Determinism**: Reproducible behavior with fixed seeds
- **Scalability**: Support 50+ vehicles
- **High-Scale Performance**: 1000+ vehicles at 100-1000x speed factors

### Status Guidance
- **Document targets and procedures**, not hardware-specific results.
- **Validate determinism** with fixed-step simulation and seeded RNGs.
- **Track scalability** with scale tests (see Unified Benchmarking Framework).
- **Report quality gates** using the quality analysis scripts, without static “current” numbers.

## Optimization Strategies

### 1. Simulation Loop Optimization

#### Fixed Timestep Physics
```python
class Simulation:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.dt_s = config['physics']['delta_t_s']  # 0.02s
        self.accumulator = 0.0
        self.speed_factor = config['physics']['speed_factor']

    def step(self, frame_time: float) -> None:
        """Fixed timestep simulation with accumulator."""
        self.accumulator += frame_time * self.speed_factor

        while self.accumulator >= self.dt_s:
            self._physics_step(self.dt_s)
            self.accumulator -= self.dt_s
```

#### Vectorized Operations
```python
import numpy as np

def update_vehicle_positions(vehicles: List[Vehicle], dt_s: float) -> None:
    """Vectorized position updates for all vehicles."""
    positions = np.array([v.state.s_m for v in vehicles])
    velocities = np.array([v.state.v_mps for v in vehicles])

    # Vectorized update
    new_positions = positions + velocities * dt_s

    # Update vehicle states
    for i, vehicle in enumerate(vehicles):
        vehicle.state = vehicle.state._replace(s_m=new_positions[i])
```

### 2. Rendering Optimization

#### Text Object Caching
```python
class OptimizedHUD:
    def __init__(self) -> None:
        self.text_objects = {}
        self._create_text_objects()

    def _create_text_objects(self) -> None:
        """Pre-create text objects to avoid allocation in render loop."""
        self.text_objects = {
            'fps': arcade.Text("FPS: 0", 10, 10, arcade.color.WHITE, 12),
            'vehicles': arcade.Text("Vehicles: 0", 10, 30, arcade.color.WHITE, 12),
            'speed_hist': arcade.Text("Speed: 0", 10, 50, arcade.color.WHITE, 12),
        }

    def update_text(self, key: str, text: str) -> None:
        """Update pre-created text object."""
        if key in self.text_objects:
            self.text_objects[key].text = text
```

#### Efficient Drawing Functions
```python
def draw_vehicle_optimized(vehicle: Vehicle, scale: float) -> None:
    """Optimized vehicle drawing with cached calculations."""
    # Use appropriate drawing function based on coordinate system
    if vehicle.orientation == 0:
        # Horizontal vehicle - use draw_lbwh_rectangle_filled
        arcade.draw_lbwh_rectangle_filled(
            vehicle.screen_x - vehicle.length_px/2, vehicle.screen_y - vehicle.width_px/2,
            vehicle.length_px, vehicle.width_px,
            vehicle.color
        )
    else:
        # Rotated vehicle - use draw_polygon_filled
        points = vehicle.get_rotated_corners()
        arcade.draw_polygon_filled(points, vehicle.color)
```

### 3. Memory Management

#### Object Pooling
```python
class VehiclePool:
    def __init__(self, initial_size: int = 20) -> None:
        self.available = []
        self.in_use = set()
        self._create_initial_objects(initial_size)

    def get_vehicle(self) -> Vehicle:
        """Get vehicle from pool or create new one."""
        if self.available:
            vehicle = self.available.pop()
            self.in_use.add(vehicle)
            return vehicle
        else:
            return self._create_new_vehicle()

    def return_vehicle(self, vehicle: Vehicle) -> None:
        """Return vehicle to pool."""
        if vehicle in self.in_use:
            self.in_use.remove(vehicle)
            vehicle.reset()
            self.available.append(vehicle)
```

#### Pre-allocation
```python
class Simulation:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.max_vehicles = config['vehicles']['max_count']
        self.perception_data = np.zeros((self.max_vehicles, 4), dtype=np.float32)
        self.vehicle_positions = np.zeros(self.max_vehicles, dtype=np.float32)
        self.vehicle_velocities = np.zeros(self.max_vehicles, dtype=np.float32)
```

### 4. Algorithm Optimization

#### Spatial Partitioning
```python
class SpatialGrid:
    def __init__(self, world_size: float, cell_size: float) -> None:
        self.cell_size = cell_size
        self.grid_size = int(world_size / cell_size)
        self.grid = [[] for _ in range(self.grid_size * self.grid_size)]

    def add_vehicle(self, vehicle: Vehicle) -> None:
        """Add vehicle to appropriate grid cell."""
        cell_x = int(vehicle.state.s_m / self.cell_size) % self.grid_size
        cell_y = int(vehicle.state.s_m / self.cell_size) % self.grid_size
        cell_index = cell_y * self.grid_size + cell_x
        self.grid[cell_index].append(vehicle)

    def get_nearby_vehicles(self, vehicle: Vehicle, radius: float) -> List[Vehicle]:
        """Get vehicles within radius using spatial partitioning."""
        nearby = []
        cells_to_check = self._get_cells_in_radius(vehicle, radius)
        for cell_index in cells_to_check:
            nearby.extend(self.grid[cell_index])
        return nearby
```

### 5. Analytics Performance Optimization
- **Efficient Data Structures**: Use deque for rolling windows
- **Batch Processing**: Update analytics in batches, not every frame
- **Memory Bounds**: Limit history size to prevent memory growth
- **Statistical Caching**: Cache expensive statistical calculations

```python
class LiveAnalytics:
    def __init__(self, config: Dict[str, Any]):
        # Use bounded collections for memory efficiency
        self.speed_history = collections.deque(maxlen=1000)
        self.headway_history = collections.deque(maxlen=1000)

        # Batch processing configuration
        self.update_interval = 0.1  # Update every 100ms
        self.last_update = 0.0

    def update_analytics(self, vehicles: List[Vehicle],
                        perception_data: List[Optional[PerceptionData]],
                        dt_s: float) -> None:
        """Update analytics with configurable frequency."""
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            self._batch_update_analytics(vehicles, perception_data)
            self.last_update = current_time
```

### 6. Collision System Performance
- **Spatial Partitioning**: Use pymunk's built-in spatial indexing
- **Collision Filtering**: Skip unnecessary collision checks
- **Physics Stepping**: Use appropriate physics timestep
- **Memory Management**: Reuse collision shapes when possible

#### Event-Driven Collision Detection
```python
class CollisionEventScheduler:
    def __init__(self, horizon_s: float = 3.0, guard_band_m: float = 0.3):
        self.horizon_s = horizon_s
        self.guard_band_m = guard_band_m
        self._heap = []  # Priority queue for due times
        self._due_time_by_follower = {}
        self._version_by_follower = {}

    def update_adjacency_and_reschedule(self, vehicles, track_length_m, now_s,
                                       follower_to_leader, follower_max_accel,
                                       leader_max_brake, collision_threshold_m):
        """Update vehicle adjacency and reschedule collision checks."""
        # Only check pairs when collision is predicted within horizon
```

**Benefits**:
- **Predictive Scheduling**: Only check collision pairs when TTC < horizon
- **Reduced Overhead**: O(n) instead of O(n²) collision checks
- **Performance**: 200v=2.0fps, 500v=0.3fps with scheduler enabled

```python
class CollisionSystem:
    def __init__(self, config: Dict[str, Any], track: StadiumTrack):
        self.space = pymunk.Space()
        # Use spatial partitioning for efficient collision detection
        self.space.use_spatial_hash(10.0)  # 10m grid size

        # Collision filtering to reduce checks
        self.collision_filter = pymunk.ShapeFilter()
        self.collision_filter.group = 1  # Same group = no collision

    def add_vehicle(self, vehicle: Vehicle, vehicle_id: int) -> None:
        """Add vehicle with optimized collision setup."""
        # Reuse collision shapes for similar vehicles
        shape = self._get_or_create_shape(vehicle.spec)
        shape.filter = self.collision_filter
        self.space.add(body, shape)
```

### 7. Data Logging Performance
- **Asynchronous Logging**: Use background threads for CSV writing
- **Batch Writes**: Write multiple records at once
- **Compression**: Use compressed formats for large datasets
- **Selective Logging**: Log only necessary data at high rates

### 8. NumPy Physics Engine Performance
- **Vectorized Operations**: NumPy-based kinematics and dynamics
- **JIT Compilation**: Numba acceleration for critical routines (required dependency)
- **Memory Efficiency**: Pre-allocated arrays for state management
- **Feature Gating**: Safe rollout via `physics.numpy_engine_enabled` flag

```python
class PhysicsEngineNumpy:
    def step(self, actions: np.ndarray, dt: float,
             track_length: float = 1000.0) -> np.ndarray:
        """Vectorized physics step with NumPy operations."""
        # Arc-length kinematics: s += v*dt + 0.5*a*dt²
        # XY-velocity mode: x += vx*dt, y += vy*dt
```

**Benefits**:
- **Vectorized Operations**: NumPy-based kinematics and dynamics calculations
- **JIT Compilation**: Numba acceleration for critical routines
- **Memory Efficiency**: Pre-allocated arrays for state management
- **Dual-Mode Operation**: Arc-length and XY-velocity modes

```python
class DataLogger:
    def __init__(self, config: Dict[str, Any]):
        self.logging_config = config.get("logging", {})

        # Asynchronous logging setup
        self.log_queue = queue.Queue(maxsize=1000)
        self.log_thread = threading.Thread(target=self._log_worker, daemon=True)
        self.log_thread.start()

        # Batch writing configuration
        self.batch_size = self.logging_config.get("batch_size", 100)
        self.batch_buffer = []

    def _log_worker(self) -> None:
        """Background thread for CSV writing."""
        while True:
            try:
                data = self.log_queue.get(timeout=1.0)
                self._write_batch(data)
            except queue.Empty:
                continue
```

#### Cached Calculations
```python
class CachedCalculations:
    def __init__(self) -> None:
        self.sqrt_cache = {}
        self.trig_cache = {}

    def cached_sqrt(self, x: float) -> float:
        """Cached square root calculation."""
        if x not in self.sqrt_cache:
            self.sqrt_cache[x] = math.sqrt(x)
        return self.sqrt_cache[x]

    def cached_sin(self, x: float) -> float:
        """Cached sine calculation."""
        key = round(x, 6)  # Round to avoid floating point precision issues
        if key not in self.trig_cache:
            self.trig_cache[key] = math.sin(x)
        return self.trig_cache[key]
```

## Monitoring & Profiling

### 1. Performance Monitoring
```python
class PerformanceMonitor:
    def __init__(self) -> None:
        self.frame_times = []
        self.memory_usage = []
        self.simulation_times = []

    def start_frame(self) -> None:
        """Start timing a frame."""
        self.frame_start = time.time()

    def end_frame(self) -> None:
        """End timing a frame."""
        frame_time = time.time() - self.frame_start
        self.frame_times.append(frame_time)

        # Calculate FPS
        fps = 1.0 / frame_time if frame_time > 0 else 0
        if fps < 30:
            self._log_performance_warning(f"Low FPS: {fps:.1f}")

    def profile_simulation_step(self, func) -> None:
        """Profile a simulation step function."""
        start_time = time.time()
        result = func()
        end_time = time.time()

        step_time = end_time - start_time
        self.simulation_times.append(step_time)

        if step_time > 0.033:  # 30 FPS threshold
            self._log_performance_warning(f"Slow simulation step: {step_time:.3f}s")

        return result
```

### 2. Memory Profiling
```python
import tracemalloc

class MemoryProfiler:
    def __init__(self) -> None:
        tracemalloc.start()
        self.snapshots = []

    def take_snapshot(self, label: str) -> None:
        """Take a memory snapshot."""
        snapshot = tracemalloc.take_snapshot()
        self.snapshots.append((label, snapshot))

    def analyze_memory_usage(self) -> None:
        """Analyze memory usage patterns."""
        for label, snapshot in self.snapshots:
            top_stats = snapshot.statistics('lineno')
            print(f"\n=== {label} ===")
            for stat in top_stats[:10]:
                print(stat)
```

### 3. Performance Testing
```python
def test_performance_target():
    """Test that simulation meets 30+ FPS target."""
    cfg = load_config()
    sim = Simulation(cfg)

    # Warm up
    for _ in range(100):
        sim.step(0.02)

    # Performance test
    start_time = time.time()
    for _ in range(1000):
        sim.step(0.02)
    end_time = time.time()

    total_time = end_time - start_time
    fps_equivalent = 1000 / (total_time * 50)  # 50 steps per second

    assert fps_equivalent >= 30, f"Performance below target: {fps_equivalent:.1f} FPS"
    print(f"Performance test passed: {fps_equivalent:.1f} FPS")
```

## Memory Management

### 1. Allocation Minimization
```python
class AllocationTracker:
    def __init__(self) -> None:
        self.allocations = 0
        self.deallocations = 0

    def track_allocation(self, obj) -> None:
        """Track object allocation."""
        self.allocations += 1
        if self.allocations % 1000 == 0:
            print(f"Allocations: {self.allocations}, Deallocations: {self.deallocations}")

    def track_deallocation(self, obj) -> None:
        """Track object deallocation."""
        self.deallocations += 1
```

### 2. Garbage Collection Optimization
```python
import gc

class GCOptimizer:
    def __init__(self) -> None:
        self.gc_threshold = 1000
        self.allocation_count = 0

    def optimize_gc(self) -> None:
        """Optimize garbage collection timing."""
        self.allocation_count += 1

        if self.allocation_count >= self.gc_threshold:
            gc.collect()
            self.allocation_count = 0
```

## Rendering Optimization

### 1. Draw Call Batching
```python
class DrawCallBatcher:
    def __init__(self) -> None:
        self.rectangles = []
        self.circles = []
        self.lines = []

    def add_rectangle(self, x: float, y: float, width: float, height: float, color: Tuple[int, int, int]) -> None:
        """Add rectangle to batch."""
        self.rectangles.append((x, y, width, height, color))

    def flush(self) -> None:
        """Flush all batched draw calls."""
        # Draw all rectangles at once
        for x, y, width, height, color in self.rectangles:
            arcade.draw_lbwh_rectangle_filled(x, y, width, height, color)

        # Clear batches
        self.rectangles.clear()
        self.circles.clear()
        self.lines.clear()
```

### 2. Level of Detail
```python
class LODManager:
    def __init__(self) -> None:
        self.distance_thresholds = [50, 100, 200]  # meters
        self.lod_levels = ['high', 'medium', 'low', 'culled']

    def get_lod_level(self, distance: float) -> str:
        """Get level of detail based on distance."""
        for i, threshold in enumerate(self.distance_thresholds):
            if distance < threshold:
                return self.lod_levels[i]
        return self.lod_levels[-1]  # culled

    def render_vehicle(self, vehicle: Vehicle, distance: float) -> None:
        """Render vehicle with appropriate LOD."""
        lod = self.get_lod_level(distance)

        if lod == 'high':
            self._render_vehicle_detailed(vehicle)
        elif lod == 'medium':
            self._render_vehicle_simple(vehicle)
        elif lod == 'low':
            self._render_vehicle_minimal(vehicle)
        # culled - don't render
```

## Simulation Optimization

### 1. Early Termination
```python
def calculate_perception_optimized(vehicle: Vehicle, vehicles: List[Vehicle], max_range: float) -> Optional[Vehicle]:
    """Optimized perception calculation with early termination."""
    closest_leader = None
    closest_distance = float('inf')

    for other_vehicle in vehicles:
        if other_vehicle == vehicle:
            continue

        distance = abs(other_vehicle.state.s_m - vehicle.state.s_m)

        # Early termination if beyond range
        if distance > max_range:
            continue

        # Early termination if already found closer vehicle
        if distance >= closest_distance:
            continue

        # Check occlusion (expensive operation only if needed)
        if not is_occluded(vehicle, other_vehicle):
            closest_leader = other_vehicle
            closest_distance = distance

    return closest_leader
```

### 2. Cached Calculations
```python
class CalculationCache:
    def __init__(self, max_size: int = 1000) -> None:
        self.cache = {}
        self.max_size = max_size
        self.access_count = {}

    def get_cached_calculation(self, key: str, calculation_func) -> Any:
        """Get cached calculation or compute and cache."""
        if key in self.cache:
            self.access_count[key] = self.access_count.get(key, 0) + 1
            return self.cache[key]

        result = calculation_func()
        self._cache_result(key, result)
        return result

    def _cache_result(self, key: str, result: Any) -> None:
        """Cache result with LRU eviction."""
        if len(self.cache) >= self.max_size:
            # Remove least recently used
            lru_key = min(self.access_count.keys(), key=lambda k: self.access_count[k])
            del self.cache[lru_key]
            del self.access_count[lru_key]

        self.cache[key] = result
        self.access_count[key] = 0
```

## Quality Gates Integration

### Performance Quality Gates
The project integrates quality gates with performance monitoring to ensure consistent performance standards:

```yaml
# From quality_gates.yaml
performance:
  max_cyclomatic_complexity: 10
  max_cognitive_complexity: 15
  max_function_length: 50
  max_class_length: 200
```

### Quality Gates Status
- Use `uv run python scripts/quality_analysis.py --mode=check` for up-to-date status.
- Track coverage and tool pass/fail in CI artifacts instead of embedding static numbers.

### Running Quality Gates
```bash
# Run all quality gates including performance checks
uv run python scripts/quality_analysis.py --mode=check

# Run performance-specific quality checks
uv run python scripts/quality_analysis.py --mode=check --performance-only

# Run profiling session and dump CSV of timing blocks (feature-flagged)
uv run python scripts/profile_simulation.py --steps 1000 --dt 0.02 --csv profiling_stats.csv --cprofile

# Run high-performance benchmark (vectorized paths enabled via flags)
uv run python scripts/performance_analysis.py --mode=benchmark --vehicles 100 --steps 2000 --dt 0.02 --speed-factor 10.0
```

### 3. Advanced Performance Optimizations

The simulator includes several advanced performance optimizations to maintain 30+ FPS with 20+ vehicles:

#### Vehicle Pre-sorting
```python
class PerformanceOptimizer:
    def pre_sort_vehicles(self, vehicles: List[Vehicle], current_time: float,
                         force_resort: bool = False) -> List[Vehicle]:
        """Pre-sort vehicles by arc length with caching."""
        time_since_last_sort = current_time - self._last_sort_time
        if (not force_resort and
            self._sorted_vehicles is not None and
            time_since_last_sort < 0.1):
            return vehicles

        vehicles.sort(key=lambda v: v.state.s_m)
        self._sorted_vehicles = vehicles
        self._last_sort_time = current_time
        return vehicles
```

**Benefits**:
- **Caching**: Vehicles are pre-sorted by arc length with time-based caching
- **Efficiency**: Avoids frequent re-sorting when vehicle order is stable
- **Performance**: Reduces O(n log n) sorting to O(1) for cached results

#### Fast Approximations
```python
def fast_inverse_sqrt(self, x: float) -> float:
    """Fast approximation of 1/sqrt(x) using cached values."""
    if x <= 0:
        return 0.0

    x_rounded = round(x, 6)
    if x_rounded in self._inverse_sqrt_cache:
        self.cache_hits += 1
        return self._inverse_sqrt_cache[x_rounded]

    # Fast inverse square root approximation (Quake III algorithm)
    x_bytes = struct.pack('f', x)
    i = struct.unpack('I', x_bytes)[0]
    i = 0x5f3759df - (i >> 1)
    y_bytes = struct.pack('I', i)
    result = struct.unpack('f', y_bytes)[0]

    # One iteration of Newton's method for better accuracy
    result = result * (1.5 - 0.5 * x * result * result)

    self._inverse_sqrt_cache[x_rounded] = result
    self.cache_misses += 1
    return float(result)
```

**Benefits**:
- **Vectorized Physics and IDM (Phase 3/4 groundwork)**

  - Files: `src/traffic_sim/core/physics_vectorized.py`, `src/traffic_sim/core/idm_vectorized.py`
  - Flags:
    - `data_manager.enabled`: enable pre-allocated arrays for state experiments
    - `high_performance.enabled`: enable vectorized arc-length kinematics path
    - `high_performance.idm_vectorized`: use vectorized fallback IDM (leader = next vehicle) when perception is occluded/unavailable
  - Integration: feature-flagged in `src/traffic_sim/core/simulation.py`
  - Benchmarks: `scripts/performance_analysis.py --mode=benchmark`
- **Inverse Square Root**: Quake III algorithm with caching for distance calculations
- **Vectorization**: NumPy-based operations when available
- **Cache Management**: Intelligent cache cleanup to prevent memory bloat

#### Occlusion Caching
```python
def cache_occlusion_relationship(self, vehicle1_idx: int, vehicle2_idx: int,
                               is_occluded: bool) -> None:
    """Cache occlusion relationship between two vehicles."""
    self.occlusion_cache[(vehicle1_idx, vehicle2_idx)] = (is_occluded, time.time())

def get_cached_occlusion(self, vehicle1_idx: int, vehicle2_idx: int) -> Optional[bool]:
    """Get cached occlusion relationship."""
    key = (vehicle1_idx, vehicle2_idx)
    if key in self.occlusion_cache:
        is_occluded, timestamp = self.occlusion_cache[key]
        if (time.time() - timestamp) < self.occlusion_cache_max_age:
            self.occlusion_cache_hits += 1
            return is_occluded
    self.occlusion_cache_misses += 1
    return None
```

**Benefits**:
- **Relationship Caching**: Cached occlusion relationships between vehicles
- **Time-based Expiry**: Automatic cache invalidation after configurable time
- **Memory Efficient**: Bounded cache size with LRU eviction

#### Performance Benchmarks
- **≥30 FPS** with 20+ vehicles
- **10× speed factor** stability without instability
- **Deterministic replay** with fixed seeds
- **Cache hit rates**: >80% for inverse sqrt, >70% for occlusion

## Performance Testing

### Unified Benchmarking Framework
The project now includes a comprehensive benchmarking framework that consolidates all performance testing into a single, high-performance system.

#### Core Framework
- **Parallel Execution**: 3-5x performance improvement through automatic parallelization
- **Real-Time Estimation**: Theoretical performance modeling with 100% CPU utilization
- **Comprehensive Metrics**: CPU, memory, efficiency, and theoretical performance tracking
- **Intelligent Caching**: Configuration and result caching for improved performance

#### Usage
```bash
# Single benchmark
uv run python scripts/benchmarking_framework.py --mode=benchmark --vehicles 100 --steps 1000

# Scale testing
uv run python scripts/benchmarking_framework.py --mode=scale --vehicle-counts 20 50 100 200

# Performance monitoring
uv run python scripts/benchmarking_framework.py --mode=monitor --duration 5 --vehicles 100

# Advanced profiling
uv run python scripts/benchmarking_framework.py --mode=profile --vehicles 100 --steps 1000
```

#### External Tools Integration
- **pytest-benchmark**: Statistical analysis and historical tracking
- **ASV (Air Speed Velocity)**: Historical performance comparison
- **Hyperfine**: Command-line benchmarking with statistical analysis
- **Py-Spy**: Low-overhead profiling with flame graphs

#### Advanced Profiling
- **Memory Analysis**: Leak detection using tracemalloc
- **Performance Prediction**: Scaling behavior modeling
- **Resource Bottlenecks**: CPU, memory, and I/O bottleneck identification

**Reference**: [Benchmarking Guide](mdc:docs/BENCHMARKING_GUIDE.md)

### Legacy Performance Testing
The individual performance test files have been consolidated into the unified framework:
- `tests/performance_test.py` → `tests/benchmark_test.py`
- `tests/performance_smoke_test.py` → Integrated into unified framework
- `tests/performance_highperf_test.py` → Integrated into unified framework

**Migration**: Use `scripts/migrate_performance_tests.py` for automatic migration.

### 1. Automated Performance Tests
- **Validation Testing**: `scripts/validation_test.py`

```python
def test_simulation_performance():
    """Test simulation performance with various vehicle counts."""
    vehicle_counts = [5, 10, 20, 50, 100]

    for count in vehicle_counts:
        cfg = load_config()
        cfg['vehicles']['count'] = count

        sim = Simulation(cfg)

        # Warm up
        for _ in range(100):
            sim.step(0.02)

        # Performance test
        start_time = time.time()
        for _ in range(1000):
            sim.step(0.02)
        end_time = time.time()

        fps = 1000 / (end_time - start_time) / 50
        print(f"Vehicles: {count}, FPS: {fps:.1f}")

        assert fps >= 30, f"Performance below target for {count} vehicles: {fps:.1f} FPS"
```

### 2. Memory Usage Tests
```python
def test_memory_usage():
    """Test memory usage with increasing vehicle counts."""
    import psutil
    import os

    process = psutil.Process(os.getpid())

    vehicle_counts = [10, 20, 50, 100]
    memory_usage = []

    for count in vehicle_counts:
        cfg = load_config()
        cfg['vehicles']['count'] = count

        sim = Simulation(cfg)

        # Run simulation for a while
        for _ in range(1000):
            sim.step(0.02)

        memory_mb = process.memory_info().rss / 1024 / 1024
        memory_usage.append((count, memory_mb))

        print(f"Vehicles: {count}, Memory: {memory_mb:.1f} MB")

    # Check memory scaling
    for i in range(1, len(memory_usage)):
        prev_count, prev_memory = memory_usage[i-1]
        curr_count, curr_memory = memory_usage[i]

        memory_per_vehicle = (curr_memory - prev_memory) / (curr_count - prev_count)
        print(f"Memory per vehicle: {memory_per_vehicle:.2f} MB")
```

## Troubleshooting

### 1. Performance Issues
```python
def diagnose_performance_issues():
    """Diagnose common performance issues."""
    print("=== Performance Diagnosis ===")

    # Check frame rate
    frame_times = get_frame_times()
    avg_frame_time = sum(frame_times) / len(frame_times)
    fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0

    print(f"Average FPS: {fps:.1f}")

    if fps < 30:
        print("⚠️  Low FPS detected")

        # Check simulation step time
        sim_times = get_simulation_times()
        avg_sim_time = sum(sim_times) / len(sim_times)
        print(f"Average simulation step time: {avg_sim_time:.3f}s")

        if avg_sim_time > 0.033:
            print("⚠️  Slow simulation step detected")

        # Check memory usage
        memory_mb = get_memory_usage()
        print(f"Memory usage: {memory_mb:.1f} MB")

        if memory_mb > 100:
            print("⚠️  High memory usage detected")
```

### 2. Memory Leaks
```python
def detect_memory_leaks():
    """Detect potential memory leaks."""
    import gc

    initial_objects = len(gc.get_objects())

    # Run simulation for a while
    for _ in range(10000):
        sim.step(0.02)

    gc.collect()
    final_objects = len(gc.get_objects())

    object_growth = final_objects - initial_objects
    print(f"Object growth: {object_growth}")

    if object_growth > 1000:
        print("⚠️  Potential memory leak detected")

        # Find most common object types
        object_types = {}
        for obj in gc.get_objects():
            obj_type = type(obj).__name__
            object_types[obj_type] = object_types.get(obj_type, 0) + 1

        print("Most common object types:")
        for obj_type, count in sorted(object_types.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {obj_type}: {count}")
```

## Optimization Techniques
- **Event-Driven Collision Scheduler**: O(n) instead of O(n²) collision detection
- **NumPy Physics Engine**: Vectorized physics with Numba JIT acceleration
- **Adaptive Time Stepping**: Dynamic timestep scaling for high speed factors
- **Vectorized IDM Controller**: NumPy-based acceleration calculations
- **High-Performance Data Manager**: Efficient state management for 10,000+ vehicles

### Configuration
```yaml
physics:
  numpy_engine_enabled: true
  adaptive_timestep_enabled: true

high_performance:
  enabled: true
  idm_vectorized: true

collisions:
  event_scheduler_enabled: true
  event_horizon_s: 2.0
  guard_band_m: 0.2

data_manager:
  enabled: true
  max_vehicles: 10000
```

This performance guide provides comprehensive coverage of optimization strategies, monitoring techniques, and troubleshooting approaches for the traffic simulator.
