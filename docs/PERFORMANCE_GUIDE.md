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
- **Frame Rate**: 30+ FPS with 20+ vehicles
- **Memory Usage**: Minimal runtime allocations
- **Determinism**: Reproducible behavior with fixed seeds
- **Scalability**: Support 50+ vehicles

### Current Performance
- **Achieved**: 300+ FPS equivalent (10x target)
- **Memory**: <50MB for 20 vehicles
- **Deterministic**: Fixed-step simulation with seeded RNGs
- **Scalable**: Tested up to 100 vehicles

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
        # Horizontal vehicle - use draw_rectangle_filled
        arcade.draw_rectangle_filled(
            vehicle.screen_x, vehicle.screen_y,
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
            arcade.draw_rectangle_filled(x, y, width, height, color)

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

## Performance Testing

### 1. Automated Performance Tests
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

This performance guide provides comprehensive coverage of optimization strategies, monitoring techniques, and troubleshooting approaches for the traffic simulator.
