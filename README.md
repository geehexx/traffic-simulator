# Traffic Simulator

A 2D Python traffic simulation using Arcade with statistically realistic driver behavior, dynamic safety analytics, and live HUD.

## Table of Contents
- Overview
- Features
- Installation (uv)
- Usage
- Configuration
- Development
- Testing & CI
- Contributing
- License

## Overview
This project simulates vehicles circulating on a stadium-shaped track. Drivers are sampled from bell-curve distributions with correlations (reaction time, headway, aggression, rule adherence). Safety panels compute safe curve speed/length per AASHTO/TxDOT-style formulas. The renderer scales to window, supports 30+ FPS, and includes a minimal HUD with a toggle to rich analytics.

## Features
- Stadium track from total length; dynamic safe-speed/length analytics and warnings
- 20+ vehicles with random colors; configurable mix
- Parametric driver behavior; occlusion-based perception and dynamic SSD
- Deterministic fixed-step physics; speed factor up to 10×
- **Collision system with pymunk physics**: Lateral push effects and vehicle disable
- **Live HUD Analytics**: Real-time speed histogram, headway distribution, near-miss counter
- **Advanced Data Logging**: Incident tracking, performance metrics, CSV export
- **Enhanced HUD**: Speed/headway/TTC, incident log, safe-curve panel, perception data

## Installation (uv)
Requires Python 3.10+ and uv package manager.

```bash
# Clone the repository
git clone <repository-url>
cd traffic-simulator

# Install dependencies
uv sync --extra dev

# Run the simulator
uv run python -m traffic_sim
```

## Usage

### Basic Usage
```bash
# Run with default configuration
uv run python -m traffic_sim

# Run with custom config
TRAFFIC_SIM_CONFIG=config/my_config.yaml uv run python -m traffic_sim
```

### Controls
- **H**: Toggle between minimal and full HUD
- **ESC**: Exit simulator

### HUD Modes
- **Minimal**: Safety panel, perception summary, live analytics
- **Full**: Detailed vehicle overlays, perception heatmap, incident log, performance metrics

## Configuration

Configuration is stored in `config/config.yaml`. Key sections:

### Track Settings
```yaml
track:
  length_m: 1000
  straight_fraction: 0.30
  speed_limit_kmh: 100
  safety_design_speed_kmh: 120
```

### Vehicle Settings
```yaml
vehicles:
  count: 20
  mix:
    sedan: 0.55
    suv: 0.25
    truck_van: 0.10
    bus: 0.05
    motorbike: 0.05
```

### Driver Parameters
```yaml
drivers:
  distributions:
    reaction_time_s: {mean: 2.5, std: 0.6, min: 0.8, max: 4.0}
    headway_T_s: {mean: 1.6, std: 0.5, min: 0.6, max: 3.0}
    # ... more parameters
  correlations:
    A_T: -0.5
    A_b_comf: 0.3
    R_A: -0.4
```

### Perception Settings
```yaml
perception:
  visual_range_m: 200.0
  occlusion_check_resolution: 0.5
  ssd_safety_margin: 1.2
  min_ssd_m: 2.0
```

### Analytics Settings
```yaml
analytics:
  speed_histogram_bins: 20
  headway_dangerous_threshold: 1.0
  headway_critical_threshold: 0.5
  ttc_nearmiss_threshold: 1.5
  data_retention_seconds: 300
  performance_tracking: true
```

### Collision Settings
```yaml
collisions:
  use_pymunk_impulse: true
  disable_time_s: 5.0
  lateral_push: true
```

## Development

### Quick Start
```bash
# Setup development environment
uv sync --extra dev

# Install pre-commit hooks
uv run pre-commit install

# Run simulator
uv run python -m traffic_sim

# Run tests
uv run python -m pytest tests/ -v

# Run with coverage
uv run python -m pytest tests/ --cov=traffic_sim --cov-report=term-missing

# Run quality gates
uv run python scripts/quality_analysis.py --mode=check

# Export simulation data
uv run python -c "from traffic_sim.core.simulation import Simulation; from traffic_sim.config.loader import load_config; sim = Simulation(load_config()); [sim.step(0.02) for _ in range(1000)]; sim.export_data('my_simulation')"
```

### Static Analysis & Quality Gates

The project uses a comprehensive static analysis framework with automated quality gates:

#### Tools
- **MyPy & Pyright**: Type checking
- **Ruff**: Linting and formatting
- **Pylint**: Code quality analysis
- **Bandit**: Security scanning
- **Radon**: Complexity analysis

#### Quality Gates
- **Type Safety**: Comprehensive type checking
- **Code Quality**: Pylint score ≥8.0/10
- **Security**: No high/medium severity issues
- **Complexity**: No high complexity functions
- **Coverage**: ≥80% line coverage

#### Usage
```bash
# Run all quality gates
uv run python scripts/quality_analysis.py --mode=check

# Run quality monitoring
uv run python scripts/quality_analysis.py --mode=monitor

# Run comprehensive analysis
uv run python scripts/quality_analysis.py --mode=analyze
```

For detailed information, see [Quality Standards Guide](docs/QUALITY_STANDARDS.md), [Development Guide](docs/DEVELOPMENT.md), and [Scripts Guide](docs/SCRIPTS_GUIDE.md).

## Scripts & Analysis Tools

The project includes consolidated analysis tools for quality and performance testing:

### Quality Analysis
```bash
# Quality gates enforcement
uv run python scripts/quality_analysis.py --mode=check

# Detailed quality monitoring
uv run python scripts/quality_analysis.py --mode=monitor

# Comprehensive static analysis
uv run python scripts/quality_analysis.py --mode=analyze
```

### Performance Analysis
```bash
# High-performance benchmark
uv run python scripts/performance_analysis.py --mode=benchmark

# Scale performance testing
uv run python scripts/performance_analysis.py --mode=scale

# Real-time performance monitoring
uv run python scripts/performance_analysis.py --mode=monitor
```

### Task Commands
```bash
# Quality analysis
task quality              # Quality gates
task quality:monitor      # Detailed monitoring
task quality:analyze      # Comprehensive analysis

# Performance analysis (Unified Benchmarking Framework)
task performance          # Performance benchmark
task performance:scale    # Scale testing
task performance:monitor  # Real-time monitoring
task performance:profile # Advanced profiling

# Specialized tools
task validate             # Validation testing
task benchmark            # Unified benchmarking framework
task benchmark:external   # External tools integration
task benchmark:advanced   # Advanced profiling
```

### Project Structure
- **Core**: `src/traffic_sim/core/` - Simulation logic, vehicles, drivers
- **Config**: `config/config.yaml` - Configuration files
- **Tests**: `tests/` - Test suite
- **Models**: `src/traffic_sim/models/` - Vehicle and driver specifications
- **Render**: `src/traffic_sim/render/` - Arcade rendering and UI
- **Scripts**: `scripts/` - Analysis and benchmarking tools

### Key Components
- **Simulation**: Main simulation loop with IDM controller
- **Driver**: Per-driver parameters with Gaussian copula correlation
- **Vehicle**: Dynamics with jerk limiting and drivetrain lag
- **Perception**: Occlusion detection and dynamic SSD calculation
- **Track**: Stadium geometry with safety calculations
- **Analytics**: Live data collection and real-time visualization
- **Benchmarking**: Unified framework with parallel execution and real-time estimation

### Unified Benchmarking Framework
The project includes a comprehensive benchmarking system for performance optimization:

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

**Features:**
- **Parallel Execution**: 3-5x performance improvement through automatic parallelization
- **Real-Time Estimation**: Theoretical performance modeling with 100% CPU utilization
- **External Tools**: Integration with pytest-benchmark, ASV, Hyperfine, Py-Spy
- **Advanced Profiling**: Memory analysis, performance prediction, scaling modeling

**Reference**: [Benchmarking Guide](mdc:docs/BENCHMARKING_GUIDE.md)

## Testing & CI

### Running Tests
```bash
# All tests
uv run python -m pytest tests/ -v

# Specific test file
uv run python -m pytest tests/idm_test.py -v

# With coverage
uv run python -m pytest tests/ --cov=traffic_sim --cov-report=html
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end simulation testing
- **Deterministic Tests**: Reproducible behavior validation
- **Performance Tests**: 30+ FPS target verification

### CI/CD
- GitHub Actions workflow runs on every push
- Pre-commit hooks for code quality
- Automated testing with coverage reporting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write comprehensive tests
- Document public APIs

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Performance

- **Target**: 30+ FPS with 20 vehicles
- **Current**: 300+ FPS equivalent (10x target on development hardware)
- **Memory**: <50MB for 20 vehicles
- **Deterministic**: Fixed-step simulation with seeded RNGs
- **Quality Gates**: 6/7 checks passing (MyPy duplicate module issue remains)

## Recent Updates

### Phase 3 (Completed)
- ✅ **Live HUD Analytics**: Real-time speed histogram, headway distribution, near-miss counter
- ✅ **Crash Visualization**: Pymunk physics integration with lateral push effects and vehicle disable
- ✅ **Advanced Data Logging**: Incident tracking, performance metrics, CSV export
- ✅ **Enhanced Analytics HUD**: Performance monitoring and incident logging
- ✅ **Comprehensive Test Suite**: Full coverage for new analytics and collision systems

### Phase 2 (Completed)
- ✅ Occlusion-based perception system
- ✅ Dynamic SSD calculation with relative speed
- ✅ Enhanced HUD with perception data
- ✅ Comprehensive test coverage

### Phase 1 (Completed)
- ✅ Enhanced driver parameter sampling
- ✅ Per-driver IDM controller
- ✅ Jerk limiting and drivetrain lag
- ✅ Markov chain speeding behavior
