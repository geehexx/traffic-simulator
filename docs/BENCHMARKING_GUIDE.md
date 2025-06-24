# Comprehensive Benchmarking Guide

This guide covers the unified benchmarking framework that replaces the individual performance test files with a high-performance, feature-rich system.

## Overview

The new benchmarking framework consolidates all performance testing into a single, powerful system that provides:

- **Parallel execution** with real-time performance estimation
- **External tool integration** (pytest-benchmark, ASV, Hyperfine, Py-Spy)
- **Advanced profiling** with memory analysis and scaling prediction
- **Comprehensive reporting** with statistical analysis and visualization

## Quick Start

### Basic Benchmarking

```bash
# Single benchmark
uv run python scripts/benchmarking_framework.py --mode=benchmark --vehicles 100 --steps 1000

# Scale testing
uv run python scripts/benchmarking_framework.py --mode=scale --vehicle-counts 20 50 100 200 --speed-factors 1.0 10.0 100.0

# Performance monitoring
uv run python scripts/benchmarking_framework.py --mode=monitor --duration 5 --vehicles 100

# Advanced profiling
uv run python scripts/benchmarking_framework.py --mode=profile --vehicles 100 --steps 1000
```

### Running Tests

```bash
# Run all benchmark tests
uv run python -m pytest tests/benchmark_tests.py -v

# Run specific test categories
uv run python -m pytest tests/benchmark_tests.py::TestPerformanceRegression -v
uv run python -m pytest tests/benchmark_tests.py::TestRealTimeEstimation -v
```

## Framework Components

### 1. Core Framework (`scripts/benchmarking_framework.py`)

The main benchmarking framework that provides:

- **BenchmarkRunner**: High-performance parallel execution
- **RealTimeEstimator**: Theoretical performance estimation with 100% CPU utilization
- **SystemMonitor**: Resource utilization monitoring
- **BenchmarkingFramework**: Unified interface for all benchmarking

#### Key Features

- **Parallel Execution**: Automatically utilizes all CPU cores
- **Real-Time Estimation**: Estimates performance with full resource utilization
- **Comprehensive Metrics**: CPU, memory, efficiency, and theoretical performance
- **Caching**: Intelligent caching for configurations and results

### 2. External Tools Integration (`scripts/external_tools.py`)

Integrates modern benchmarking frameworks:

- **pytest-benchmark**: Statistical analysis and historical tracking
- **ASV (Air Speed Velocity)**: Historical performance comparison
- **Hyperfine**: Command-line benchmarking with statistical analysis
- **Py-Spy**: Low-overhead profiling with flame graphs

### 3. Advanced Profiling (`scripts/advanced_profiling.py`)

Comprehensive profiling capabilities:

- **MemoryProfiler**: Advanced memory analysis with leak detection
- **PerformancePredictor**: Scaling behavior prediction
- **ScalingModel**: Mathematical modeling of performance scaling

### 4. Unified Tests (`tests/benchmark_tests.py`)

Consolidated test suite that replaces:

- `tests/performance_test.py`
- `tests/performance_smoke_test.py`
- `tests/performance_highperf_test.py`

## Configuration

### Benchmarking Configuration (`config/benchmarking.yaml`)

Comprehensive configuration for all benchmarking aspects:

```yaml
benchmarking:
  parallel_execution:
    enabled: true
    max_workers: null  # Auto-detect
    timeout_seconds: 300

  real_time_estimation:
    enabled: true
    cpu_utilization_threshold: 0.8
    memory_utilization_threshold: 0.9

  external_tools:
    pytest_benchmark:
      enabled: true
      iterations: 10
      warmup: 3

    hyperfine:
      enabled: true
      runs: 10
      warmup: 2
```

### Test Configurations

Predefined test configurations for different scenarios:

- **Smoke Tests**: Quick validation (5 vehicles, 200 steps)
- **Standard Benchmarks**: Normal testing (100 vehicles, 1000 steps)
- **High-Performance**: Stress testing (1000 vehicles, 100x speed)
- **Scale Testing**: Multi-vehicle analysis
- **Stress Testing**: Extreme conditions (5000 vehicles, 1000x speed)

## Usage Examples

### 1. Single Benchmark

```python
from scripts.benchmarking_framework import BenchmarkingFramework

framework = BenchmarkingFramework()

# Run single benchmark
result = framework.run_benchmark(
    vehicles=100,
    steps=1000,
    dt=0.02,
    speed_factor=1.0
)

print(f"Performance: {result.steps_per_second:.1f} steps/s")
print(f"Theoretical FPS: {result.theoretical_fps:.1f}")
print(f"Confidence: {result.confidence_score:.2f}")
```

### 2. Parallel Scale Testing

```python
# Run comprehensive scale benchmarks
results = framework.run_scale_benchmark(
    vehicle_counts=[20, 50, 100, 200, 500, 1000],
    speed_factors=[1.0, 10.0, 100.0, 1000.0],
    steps=1000,
    output_csv="runs/scaling/scale_results.csv"
)

# Results include theoretical performance estimates
for result in results:
    print(f"{result.config.vehicles} vehicles: {result.steps_per_second:.1f} steps/s "
          f"(theoretical: {result.theoretical_fps:.1f})")
```

### 3. Advanced Profiling

```python
from scripts.advanced_profiling import AdvancedProfiler

profiler = AdvancedProfiler()

# Comprehensive analysis
results = profiler.run_comprehensive_analysis(
    vehicles=100,
    steps=1000,
    output_dir="runs/profiling/profiling_analysis"
)

# Memory analysis
memory_profile = profiler.memory_profiler.analyze_memory_usage(sim, 1000)
print(f"Peak memory: {memory_profile.peak_mb:.1f} MB")
print(f"Memory leaks: {len(memory_profile.memory_leaks)}")
```

### 4. External Tools Integration

```python
from scripts.external_tools import ExternalToolsIntegration

integration = ExternalToolsIntegration()

# Run comprehensive benchmark with all tools
test_cases = [
    {"name": "100_vehicles", "vehicles": 100, "steps": 1000},
    {"name": "500_vehicles", "vehicles": 500, "steps": 1000}
]

results = integration.run_comprehensive_benchmark(test_cases)
```

## Performance Optimization

### Real-Time Performance Estimation

The framework provides theoretical performance estimation by modeling what performance would be achieved with 100% CPU utilization:

```python
# Theoretical performance calculation
theoretical_fps = actual_fps * (1.0 / cpu_utilization) * cpu_correction_factor
```

### Parallel Execution

Automatic parallel execution across all CPU cores:

```python
# Configure parallel execution
framework = BenchmarkingFramework(max_workers=8)  # Use 8 workers

# Run multiple benchmarks in parallel
configs = [
    BenchmarkConfig(vehicles=100, steps=1000),
    BenchmarkConfig(vehicles=200, steps=1000),
    BenchmarkConfig(vehicles=500, steps=1000)
]

results = framework.runner.run_parallel_benchmarks(configs)
```

### Caching and Optimization

Intelligent caching for improved performance:

- **Configuration Caching**: Reuse simulation configurations
- **Result Caching**: Cache benchmark results
- **Simulation Caching**: Reuse simulation instances where possible

## Migration from Old Tests

### Automatic Migration

Use the migration script to transition from old performance tests:

```bash
# Check migration readiness
uv run python scripts/migrate_performance_tests.py --check-only

# Run migration
uv run python scripts/migrate_performance_tests.py

# Dry run (see what would be done)
uv run python scripts/migrate_performance_tests.py --dry-run
```

### Manual Migration

If automatic migration isn't suitable:

1. **Remove old test files**:
   - `tests/performance_test.py`
   - `tests/performance_smoke_test.py`
   - `tests/performance_highperf_test.py`

2. **Use new unified tests**:
   - `tests/benchmark_tests.py` (replaces all old tests)

3. **Update CI/CD configurations** to use new framework

## Dependencies

### Core Dependencies

```bash
# Install core benchmarking dependencies
uv add pytest-benchmark pyperf psutil numpy

# Install external tools (optional)
cargo install hyperfine  # Hyperfine
pip install py-spy       # Py-Spy profiling
```

### Full Dependencies

See `requirements-benchmarking.txt` for complete dependency list.

## Output and Reporting

### Runs Directory Structure

**All profiling and benchmark output is automatically saved to the `runs/` directory.** This directory is organized by analysis type:

```
runs/
├── profiling/               # Profiling analysis outputs
│   ├── profiling_stats*.csv
│   └── profiling_analysis/
├── benchmarks/              # Benchmark results
│   ├── benchmark_results/
│   └── comprehensive_benchmark/
├── performance/             # Performance analysis outputs
│   └── *_performance*.csv
└── scaling/                 # Scaling analysis outputs
    ├── scale_benchmark*.csv
    └── scaling_analysis/
```

**Important:** Always use the `runs/` directory for any profiling or benchmark output. The directory is configured in `config/benchmarking.yaml` and all scripts default to this location.

### CSV Output

All benchmarks generate CSV output with comprehensive metrics:

```csv
vehicles,speed_factor,steps,dt,elapsed_s,steps_per_second,vehicles_per_second,efficiency,avg_frame_ms,p95_frame_ms,cpu_percent,memory_mb,theoretical_fps,theoretical_throughput,confidence_score
100,1.0,1000,0.02,0.456,2192.98,219298.0,2192.98,0.456,0.523,45.2,128.5,4867.2,486720.0,0.85
```

### JSON Reports

Detailed JSON reports for analysis:

```json
{
  "simulation_config": {
    "vehicles": 100,
    "steps": 1000,
    "elapsed_s": 0.456
  },
  "memory_profile": {
    "current_mb": 128.5,
    "peak_mb": 145.2,
    "memory_leaks": []
  },
  "performance_profile": {
    "update_perception": {"total_s": 0.123, "count": 1000, "avg_ms": 0.123}
  }
}
```

### HTML Reports

Visual reports with charts and analysis (when using external tools).

## Best Practices

### 1. Benchmark Design

- **Warmup**: Always include warmup steps to stabilize performance
- **Multiple Iterations**: Run multiple iterations for statistical significance
- **Consistent Environment**: Use consistent system conditions
- **Resource Monitoring**: Monitor CPU, memory, and I/O utilization

### 2. Performance Analysis

- **Statistical Significance**: Use appropriate statistical tests
- **Trend Analysis**: Track performance over time
- **Regression Detection**: Set up automated regression detection
- **Scaling Analysis**: Understand performance scaling behavior

### 3. CI/CD Integration

- **Automated Testing**: Integrate benchmarks into CI/CD pipeline
- **Performance Gates**: Set performance thresholds
- **Regression Alerts**: Alert on performance regressions
- **Historical Tracking**: Maintain performance history

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Memory Issues**: Adjust vehicle counts for available memory
3. **Timeout Issues**: Increase timeout for large benchmarks
4. **Parallel Issues**: Reduce worker count if system is unstable

### Performance Issues

1. **Low Performance**: Check system resource utilization
2. **Inconsistent Results**: Ensure system stability
3. **Memory Leaks**: Use memory profiling to identify issues
4. **Scaling Problems**: Analyze scaling behavior models

## Advanced Features

### Custom Benchmark Configurations

```python
# Custom benchmark configuration
config = BenchmarkConfig(
    vehicles=100,
    steps=1000,
    dt=0.02,
    speed_factor=1.0,
    enable_profiling=True,
    enable_high_performance=True,
    config_overrides={
        "physics": {"delta_t_s": 0.01},
        "collisions": {"event_scheduler_enabled": True}
    }
)
```

### Performance Prediction

```python
# Build scaling model
model = performance_predictor.build_scaling_model(
    vehicle_counts=[10, 20, 50, 100],
    performance_metrics=[1000, 800, 600, 400]
)

# Predict performance at different scales
prediction = performance_predictor.predict_performance(model, 500)
print(f"Predicted FPS for 500 vehicles: {prediction.predicted_fps:.1f}")
```

### Memory Analysis

```python
# Advanced memory profiling
memory_profile = memory_profiler.analyze_memory_usage(sim, 1000)
print(f"Memory leaks detected: {len(memory_profile.memory_leaks)}")
print(f"Peak memory usage: {memory_profile.peak_mb:.1f} MB")
```

This comprehensive benchmarking framework provides all the tools needed for thorough performance analysis and optimization of the traffic simulator.
