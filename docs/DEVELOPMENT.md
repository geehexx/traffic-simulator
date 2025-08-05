# Development Guide

This comprehensive guide covers all aspects of developing the traffic simulator project, from setup to deployment.

## Table of Contents
- [Quick Start](#quick-start)
- [Development Workflow](#development-workflow)
- [Code Quality Standards](#code-quality-standards)
- [Testing Strategy](#testing-strategy)
- [Performance Guidelines](#performance-guidelines)
- [Architecture Overview](#architecture-overview)
- [Configuration Management](#configuration-management)
- [Debugging & Troubleshooting](#debugging--troubleshooting)
- [Contributing Guidelines](#contributing-guidelines)

## Quick Start

### Prerequisites
- Python 3.12+
- [Bazel 7.1.1+](https://bazel.build/) build system
- Git

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd traffic-simulator

# Run tests with Bazel
bazel test //...

# Run simulator
bazel run //src/traffic_sim:traffic_sim_bin
```

For detailed setup instructions, see [README.md](mdc:README.md).

### Development Dependencies
For local development with external dependencies (numpy, arcade, etc.):
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install pytest pytest-xdist pytest-cov pytest-mock
pip install numpy pyyaml arcade pymunk psutil numba hypothesis
```

**Note**: The build system uses simplified dependency management. External packages are installed in the virtual environment for development and testing.

### Headless Simulation Mode
For multiprocessing and benchmarking without rendering dependencies:

#### Basic Usage
```bash
# Run headless simulation
python scripts/benchmarking_framework.py --mode=benchmark --vehicles 100 --steps 1000

# Run scale benchmarking
python scripts/benchmarking_framework.py --mode=scale --vehicle-counts 20 50 100
```

#### Advanced Usage
```python
from traffic_sim.core.simulation_headless import SimulationHeadless
import yaml

# Load configuration
with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

# Create headless simulation
sim = SimulationHeadless(config)

# Run simulation with profiling
for step in range(1000):
    sim.step(dt=0.02)

    # Get performance metrics
    if step % 100 == 0:
        results = sim.get_results()
        print(f"Step {step}: {results.performance_metrics['steps_per_second']:.1f} steps/s")
```

#### Performance Benchmarks
**Expected Performance** (on modern hardware):
- **100 vehicles**: 2000+ steps/second
- **500 vehicles**: 800+ steps/second
- **1000 vehicles**: 400+ steps/second

**Benefits**:
- True multiprocessing (no GIL limitations)
- No Arcade/Pymunk dependencies in worker processes
- Proper CPU core scaling for benchmarks
- Linear scaling with CPU cores

## Development Workflow

### 1. Code Quality Standards

The project enforces high code quality through automated static analysis. See [Quality Standards Guide](mdc:docs/QUALITY_STANDARDS.md) for detailed tool usage.

#### Pre-commit Hooks
Quality gates run automatically on every commit:
- **Ruff**: Linting and formatting
- **Pyright**: Type checking with optimized configuration
- **Bandit**: Security scanning
- **Radon**: Complexity analysis

**Configuration**: Uses `pass_filenames: false` to prevent multiple executions and optimize performance.

#### Quality Gates
All code must pass quality gates before merging. See [config/quality_gates.yaml](mdc:config/quality_gates.yaml) for thresholds:
- **Type Safety**: Comprehensive type checking
- **Security**: No high/medium severity issues
- **Complexity**: No high complexity functions
- **Coverage**: ≥70% line coverage

### 2. Development Commands

#### Running the Simulator
```bash
# Run the simulator
bazel run //src/traffic_sim:traffic_sim_bin

# Run with specific configuration
bazel run //src/traffic_sim:traffic_sim_bin -- --config config/custom.yaml

# Run with debug logging
bazel run //src/traffic_sim:traffic_sim_bin -- --debug
```

#### Testing
```bash
# Run all tests
bazel test //...

# Run specific test target
bazel test //tests:all_tests

# Run tests with verbose output
bazel test //... --test_output=all

# Run tests in parallel
bazel test //... --jobs=4
```

#### Building
```bash
# Build all targets
bazel build //...

# Build specific target
bazel build //src/traffic_sim:traffic_sim

# Build with verbose output
bazel build //... --verbose_failures
```

#### Code Quality
```bash
# Quality checks are integrated into Bazel build system
bazel build //...                    # Build with quality gates
bazel test //...                     # Run tests with quality checks
```

### 3. Project Structure

```
traffic-simulator/
├── src/traffic_sim/          # Main source code
│   ├── core/                 # Core simulation logic
│   │   ├── driver.py         # Driver behavior models
│   │   ├── vehicle.py        # Vehicle dynamics
│   │   ├── simulation.py     # Main simulation engine
│   │   ├── track.py          # Track geometry
│   │   ├── hud.py            # HUD rendering
│   │   └── logging.py        # Event logging
│   ├── config/               # Configuration management
│   ├── models/               # Data models and specifications
│   ├── render/               # Rendering and visualization
│   └── __main__.py           # Entry point
├── tests/                    # Test suite
├── config/                   # Configuration files
├── docs/                     # Documentation
├── scripts/                  # Utility scripts
├── stubs/                    # Type stubs for external libraries
├── .github/workflows/        # CI/CD workflows
├── third_party/pip/          # Bazel pip dependencies
├── MODULE.bazel              # Bazel module configuration
├── WORKSPACE.bazel           # Bazel workspace configuration
├── .bazelrc                  # Bazel configuration
└── pyproject.toml           # Project configuration
```

## Commit Message Standards

### Conventional Commits Format
All commit messages must follow the Conventional Commits specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Commit Types
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools
- **perf**: A code change that improves performance
- **ci**: Changes to CI configuration files and scripts
- **build**: Changes that affect the build system or external dependencies
- **revert**: Reverts a previous commit

### Examples
```bash
feat: add support for vehicle physics optimization
fix(rendering): resolve HUD occlusion calculation bug
docs: update performance guide with new benchmarks
style: format code according to project standards
refactor: extract common validation logic
test: add unit tests for collision detection
chore: update dependencies to latest versions
perf: optimize spatial hash collision detection
ci: add automated performance testing
build: update Bazel to version 7.1.1
revert: revert "feat: add experimental feature"
```

### Commit Message Rules
- **Type**: Must be lowercase, one of the allowed types
- **Scope**: Optional, lowercase, describes the area of change
- **Description**: Lowercase, max 72 characters, no period at end
- **Body**: Optional, explains what and why, max 100 characters per line
- **Footer**: Optional, references issues or breaking changes

## Code Quality Standards

### Type Annotations
```python
from __future__ import annotations
from typing import List, Dict, Optional, Tuple

def process_vehicles(vehicles: List[Vehicle], config: Dict[str, Any]) -> Optional[Result]:
    """Process vehicles with given configuration."""
    pass
```

### Docstrings
```python
def calculate_idm_acceleration(
    v_f: float,
    v_l: float,
    s: float,
    params: DriverParams
) -> float:
    """
    Calculate IDM acceleration based on current state.

    Args:
        v_f: Following vehicle velocity (m/s)
        v_l: Leading vehicle velocity (m/s)
        s: Distance to leading vehicle (m)
        params: Driver parameters

    Returns:
        Calculated acceleration (m/s²)
    """
    pass
```

### Error Handling
```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise RuntimeError("Operation failed") from e
```

For detailed quality standards, see [Quality Standards Guide](mdc:docs/QUALITY_STANDARDS.md).

## Testing Strategy

### Test Types
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end simulation testing
- **Property Tests**: Hypothesis-based testing
- **Performance Tests**: Timing and memory usage

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end simulation testing
- **Deterministic Tests**: Reproducible behavior validation
- **Performance Tests**: 30+ FPS target verification
- **Regression Tests**: HUD functionality and crash prevention

### Test Organization
```python
# tests/idm_test.py - IDM controller tests
# tests/sim_test.py - Simulation integration tests
# tests/track_test.py - Track geometry tests
# tests/track_properties_test.py - Track property tests
# tests/benchmark_test.py - Unified benchmarking tests
# tests/validation_test.py - Behavioral consistency tests
```

### Benchmarking Framework
The project uses a unified benchmarking framework for comprehensive performance testing:

**Benchmarking Framework:**
- **Unified Framework**: `scripts/benchmarking_framework.py`
- **External Tools**: `scripts/external_tools.py`
- **Advanced Profiling**: `scripts/advanced_profiling.py`
- **Test Suite**: `tests/benchmark_test.py`

**Reference**: [Benchmarking Guide](mdc:docs/BENCHMARKING_GUIDE.md)

### Writing Tests
```python
import pytest
from traffic_sim.core.driver import Driver, DriverParams

def test_driver_initialization():
    """Test driver initialization with valid parameters."""
    params = DriverParams(
        reaction_time_s=2.0,
        headway_T_s=1.5,
        comfort_brake_mps2=3.0,
        max_brake_mps2=8.0,
        jerk_limit_mps3=4.0,
        throttle_lag_s=0.2,
        brake_lag_s=0.1,
        aggression_z=0.0,
        rule_adherence=0.8,
        desired_speed_mps=25.0
    )
    driver = Driver(params, random.Random(42))
    assert driver.params == params
```

### Deterministic Testing
```python
def test_deterministic_behavior():
    """Test that simulation is deterministic with fixed seeds."""
    cfg["random"]["master_seed"] = 12345
    sim1, sim2 = Simulation(cfg), Simulation(cfg)
    for _ in range(50):
        sim1.step(0.02)
        sim2.step(0.02)
    # Results should be identical
    for v1, v2 in zip(sim1.vehicles, sim2.vehicles):
        assert abs(v1.state.s_m - v2.state.s_m) < 1e-6
```

### Performance Testing
```python
def test_performance_target():
    """Test that simulation meets 30+ FPS target."""
    cfg = load_config()
    sim = Simulation(cfg)
    start_time = time.time()
    for _ in range(1000):
        sim.step(0.02)
    end_time = time.time()
    fps_equivalent = 1000 / (end_time * 50)
    assert fps_equivalent >= 30, f"Performance below target: {fps_equivalent:.1f} FPS"
```

## Performance Guidelines

### Optimization Strategies
- **Minimize allocations** in hot paths
- **Use numpy** for numerical computations
- **Cache expensive calculations**
- **Profile before optimizing**

### Performance Testing
```bash
# Run performance tests
bazel test //... --test_filter=performance

# Profile specific functions
bazel run //scripts:benchmarking_framework -- --mode=profile --vehicles 100 --steps 1000
```

For detailed performance guidelines, see [Performance Guide](mdc:docs/PERFORMANCE_GUIDE.md).

## Architecture Overview

### Core Components
- **Simulation**: Main simulation loop with IDM controller
- **Driver**: Per-driver parameters with Gaussian copula correlation
- **Vehicle**: Dynamics with jerk limiting and drivetrain lag
- **Perception**: Occlusion detection and dynamic SSD calculation
- **Track**: Stadium geometry with safety calculations

### Design Patterns
- **IDM Controller**: Intelligent Driver Model with per-driver parameters
- **Perception System**: Occlusion-based visibility and dynamic SSD
- **State Management**: Immutable state objects where possible
- **Rendering**: Arcade-based visualization with performance optimization

For HUD occlusion UI guidance, see project documentation:
[Architecture Guide – Rendering Architecture](mdc:docs/ARCHITECTURE.md#rendering-architecture) and
[Performance Guide – Rendering Optimization](mdc:docs/PERFORMANCE_GUIDE.md#rendering-optimization)

For detailed architecture information, see [Architecture Guide](mdc:docs/ARCHITECTURE.md).

## Configuration Management

### Main Configuration
- **`config/config.yaml`**: Main simulation configuration
- **`pyproject.toml`**: Project metadata and tool configuration
- **`config/quality_gates.yaml`**: Quality gates thresholds

### Environment Variables
```bash
# Optional: Set custom configuration path
export TRAFFIC_SIM_CONFIG=config/custom.yaml

# Optional: Set log level
export TRAFFIC_SIM_LOG_LEVEL=DEBUG
```

### Configuration Patterns
```python
def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration with environment variable override."""
    if config_path is None:
        config_path = os.getenv('TRAFFIC_SIM_CONFIG', 'config/config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)
```

## Debugging & Troubleshooting

### Debug Mode
```bash
# Run with debug logging
bazel run //src/traffic_sim:traffic_sim_bin -- --debug

# Run with specific log level
bazel run //src/traffic_sim:traffic_sim_bin -- --log-level DEBUG
```

### Common Issues
1. **Type checking errors**: Check imports and type annotations
2. **Import errors**: Verify module structure and `__init__.py` files
3. **Performance issues**: Profile and optimize hot paths
4. **Test failures**: Check test data and assertions
5. **Commit issues**: Pre-commit hook failures and quality gate problems

### Debugging Tools
```bash
# Check quality metrics (integrated into Bazel)
bazel test //... --test_output=all

# Generate quality report
bazel test //... --test_output=all > quality_report.json

# Check test coverage
bazel test //... --test_output=all

# Troubleshoot commit issues
# See docs/COMMIT_TROUBLESHOOTING.md for detailed solutions
bazel build //...
```

## Contributing Guidelines

### Pull Request Process
1. **Create feature branch** from `main`
2. **Implement changes** with tests
3. **Run quality gates** locally
4. **Update documentation** as needed
5. **Submit pull request** with description
6. **Address review feedback**
7. **Merge after approval**

### Commit Message Format
```
type: brief description

Detailed description of changes made.
- Bullet point for specific changes
- Another bullet point if needed

Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write comprehensive tests
- Document public APIs

## Bazel Workflow

### Build System
The project uses Bazel for fast, reliable, and hermetic builds:
- **Deterministic Builds**: Reproducible builds across environments
- **Incremental Builds**: Only rebuild what changed
- **Parallel Execution**: Automatic parallelization of build tasks
- **Dependency Management**: Automatic dependency resolution
- **Remote Caching**: BuildBuddy integration for team collaboration

### Bazel Commands
```bash
# Build all targets
bazel build //...

# Fast build (16 jobs, 8GB memory)
bazel build //... --config=fast

# Build with local disk cache
bazel build //... --config=cache

# Build with BuildBuddy remote cache
bazel build //... --config=remote --remote_header=x-buildbuddy-api-key="$BUILD_BUDDY_API_KEY"

# Run all tests
bazel test //...

# Run specific target
bazel run //src/traffic_sim:traffic_sim_bin

# Clean build artifacts
bazel clean

# Query build graph
bazel query //...

# Show dependencies
bazel query --output=graph //src/traffic_sim:traffic_sim
```

### BuildBuddy Setup
1. **Get API Key**: Visit [BuildBuddy Dashboard](https://app.buildbuddy.io/settings/api-keys)
2. **Set Environment Variable**: Add to your shell profile
   ```bash
   echo 'export BUILD_BUDDY_API_KEY=your_api_key_here' >> ~/.bashrc
   source ~/.bashrc
   ```
3. **Monitor Builds**: Visit [BuildBuddy Dashboard](https://app.buildbuddy.io/invocation/)

### Bazel Configuration
- **`.bazelrc`**: Global build and test flags
- **`MODULE.bazel`**: Module dependencies and toolchain configuration
- **`WORKSPACE.bazel`**: Workspace-level configuration
- **`BUILD.bazel`**: Target-specific build rules

## CI/CD Pipeline

### GitHub Actions
The project uses GitHub Actions with Bazel for continuous integration:
- **Bazel Tests**: Run all tests using Bazel
- **Bazel Build**: Verify all targets build successfully
- **Python 3.12**: Single Python version for consistency
- **Linux Only**: Simplified matrix for faster CI

### Bazel CI Configuration
```yaml
# .github/workflows/ci.yml
- name: Setup Bazel
  uses: bazelbuild/setup-bazelisk@v2
- name: Run Bazel tests
  run: bazel test //... --jobs=4
- name: Run Bazel build
  run: bazel build //...
```

### Pre-commit Hooks (Development Assurance)
```bash
# Pre-commit hooks provide development assurance by running quality checks
# before commits. They complement Bazel by catching issues early in development.

# Install hooks (recommended for development)
uv run pre-commit install

# Run hooks manually
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run ruff --files src/traffic_sim/core/driver.py
```

## Performance Optimization Workflow

### Validation and Testing
- **Behavioral Consistency**: Run `bazel test //tests:all_tests` to verify optimization accuracy
- **Performance Monitoring**: Use `bazel run //scripts:benchmarking_framework -- --mode=monitor` for continuous monitoring
- **Scale Testing**: Execute `bazel run //scripts:benchmarking_framework -- --mode=scale` for comprehensive performance analysis

### Optimization Techniques
- **Event-Driven Collision**: Reduces collision checks by 90% (O(n) vs O(n²))
- **NumPy Physics**: Vectorized physics with Numba JIT acceleration
- **Adaptive Timestep**: Dynamic scaling for high speed factors
- **Vectorized IDM**: NumPy-based acceleration calculations

### Performance Targets
- **Baseline**: 30+ FPS with 20+ vehicles
- **Scale**: 1000+ vehicles at 100-1000x speed factors
- **Memory**: < 2GB for large simulations
- **Accuracy**: 99.9% simulation accuracy

### Configuration Management
```yaml
# Enable all optimizations
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

## Getting Help

### Resources
- **Documentation**: `docs/` directory
- **Documentation Guide**: [Comprehensive Documentation Standards](mdc:docs/DOCUMENTATION_GUIDE.md)
- **Quality Standards**: [Quality Standards Guide](mdc:docs/QUALITY_STANDARDS.md)
- **Architecture**: [Architecture Guide](mdc:docs/ARCHITECTURE.md)
- **Performance**: [Performance Guide](mdc:docs/PERFORMANCE_GUIDE.md)
- **Enforcement Troubleshooting**: [Enforcement System Troubleshooting](mdc:docs/ENFORCEMENT_TROUBLESHOOTING.md)
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions

### Common Commands Reference
```bash
# Development
bazel run //src/traffic_sim:traffic_sim_bin    # Run simulator
bazel test //...                               # Run tests
bazel build //...                              # Build all targets

# Bazel specific
bazel query //...                              # Query build graph
bazel clean                                    # Clean build artifacts
bazel test //... --jobs=4                      # Run tests in parallel

```

This development guide provides comprehensive coverage of all aspects of developing the traffic simulator project while maintaining high code quality standards.
