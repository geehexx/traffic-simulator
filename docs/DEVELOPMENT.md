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
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- Git

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd traffic-simulator

# Install dependencies
uv sync --extra dev

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run python -m pytest tests/ -v

# Run simulator
uv run python -m traffic_sim
```

For detailed setup instructions, see [README.md](mdc:README.md).

## Development Workflow

### 1. Code Quality Standards

The project enforces high code quality through automated static analysis. See [Quality Standards Guide](mdc:docs/QUALITY_STANDARDS.md) for detailed tool usage.

#### Pre-commit Hooks
Quality gates run automatically on every commit:
- **Ruff**: Linting and formatting
- **MyPy**: Type checking
- **Pyright**: Enhanced type checking
- **Pylint**: Code quality analysis
- **Bandit**: Security scanning
- **Radon**: Complexity analysis

#### Quality Gates
All code must pass quality gates before merging. See [quality_gates.yaml](mdc:quality_gates.yaml) for thresholds:
- **Type Safety**: Comprehensive type checking
- **Code Quality**: Pylint score ≥8.0/10
- **Security**: No high/medium severity issues
- **Complexity**: No high complexity functions
- **Coverage**: ≥70% line coverage

### 2. Development Commands

#### Running the Simulator
```bash
# Run the simulator
uv run python -m traffic_sim

# Run with specific configuration
uv run python -m traffic_sim --config config/custom.yaml

# Run with debug logging
uv run python -m traffic_sim --debug
```

#### Testing
```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run with coverage
uv run python -m pytest --cov=traffic_sim --cov-report=term-missing

# Run specific test file
uv run python -m pytest tests/test_idm.py -v

# Run performance tests
uv run python -m pytest tests/ -k performance -v
```

#### Static Analysis
```bash
# Run all quality gates
uv run python scripts/quality_gates.py

# Run quality monitoring
uv run python scripts/quality_monitor.py

# Run comprehensive analysis
uv run python scripts/static_analysis.py
```

#### Code Formatting
```bash
# Format code
uv run ruff format src/

# Fix linting issues
uv run ruff check src/ --fix

# Check formatting
uv run ruff format --check src/
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
└── pyproject.toml           # Project configuration
```

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
# tests/test_idm.py - IDM controller tests
# tests/test_sim.py - Simulation integration tests
# tests/test_track.py - Track geometry tests
# tests/test_track_properties.py - Track property tests
```

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
uv run python -m pytest tests/ -k performance -v

# Profile specific functions
uv run python -c "
import cProfile
from traffic_sim.core.simulation import Simulation
cProfile.run('Simulation(config).step(0.02)')
"
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

For detailed architecture information, see [Architecture Guide](mdc:docs/ARCHITECTURE.md).

## Configuration Management

### Main Configuration
- **`config/config.yaml`**: Main simulation configuration
- **`pyproject.toml`**: Project metadata and tool configuration
- **`quality_gates.yaml`**: Quality gates thresholds

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
uv run python -m traffic_sim --debug

# Run with specific log level
uv run python -m traffic_sim --log-level DEBUG
```

### Common Issues
1. **Type checking errors**: Check imports and type annotations
2. **Import errors**: Verify module structure and `__init__.py` files
3. **Performance issues**: Profile and optimize hot paths
4. **Test failures**: Check test data and assertions

### Debugging Tools
```bash
# Check quality metrics
uv run python scripts/quality_monitor.py

# Generate quality report
uv run python scripts/quality_monitor.py > quality_report.json

# Check test coverage
uv run python -m pytest --cov=traffic_sim --cov-report=html
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

## CI/CD Pipeline

### GitHub Actions
The project uses GitHub Actions for continuous integration:
- **Quality Gates**: Run on every push and PR
- **Testing**: Run tests on multiple Python versions
- **Coverage**: Generate and report test coverage
- **Security**: Scan for vulnerabilities

### Pre-commit Hooks
Quality gates run locally before commits:
```bash
# Install hooks
uv run pre-commit install

# Run on all files
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run ruff --files src/traffic_sim/core/driver.py
```

## Getting Help

### Resources
- **Documentation**: `docs/` directory
- **Quality Standards**: [Quality Standards Guide](mdc:docs/QUALITY_STANDARDS.md)
- **Architecture**: [Architecture Guide](mdc:docs/ARCHITECTURE.md)
- **Performance**: [Performance Guide](mdc:docs/PERFORMANCE_GUIDE.md)
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions

### Common Commands Reference
```bash
# Development
uv run python -m traffic_sim                    # Run simulator
uv run python -m pytest tests/ -v              # Run tests
uv run python scripts/quality_gates.py         # Check quality

# Code quality
uv run ruff check src/ --fix                   # Fix linting
uv run ruff format src/                        # Format code
uv run mypy src/                              # Type check
uv run pyright src/                           # Enhanced type check

# Analysis
uv run python scripts/static_analysis.py       # Full analysis
uv run python scripts/quality_monitor.py      # Quality monitoring
```

This development guide provides comprehensive coverage of all aspects of developing the traffic simulator project while maintaining high code quality standards.
