# Development Guide

This document provides a comprehensive guide for developing the traffic simulator project, including setup, workflow, and best practices.

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
```

## Development Workflow

### 1. Code Quality Standards

The project enforces high code quality through automated static analysis:

#### Pre-commit Hooks
Quality gates run automatically on every commit:
- **Ruff**: Linting and formatting
- **MyPy**: Type checking
- **Pyright**: Enhanced type checking
- **Pylint**: Code quality analysis
- **Bandit**: Security scanning
- **Radon**: Complexity analysis

#### Quality Gates
All code must pass quality gates before merging:
- **Type Safety**: Comprehensive type checking
- **Code Quality**: Pylint score ≥8.0/10
- **Security**: No high/medium severity issues
- **Complexity**: No high complexity functions
- **Coverage**: ≥80% line coverage

### 2. Development Commands

#### Running the Simulator
```bash
# Run the simulator
uv run python -m traffic_sim

# Run with specific configuration
uv run python -m traffic_sim --config config/custom.yaml
```

#### Testing
```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run with coverage
uv run python -m pytest --cov=traffic_sim --cov-report=term-missing

# Run specific test file
uv run python -m pytest tests/test_idm.py -v
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

### 4. Configuration

#### Main Configuration
- **`config/config.yaml`**: Main simulation configuration
- **`pyproject.toml`**: Project metadata and tool configuration
- **`mypy.ini`**: MyPy type checking configuration
- **`pyrightconfig.json`**: Pyright type checking configuration
- **`pylintrc`**: Pylint code quality configuration
- **`bandit.yaml`**: Bandit security analysis configuration
- **`radon.cfg`**: Radon complexity analysis configuration
- **`quality_gates.yaml`**: Quality gates thresholds

#### Environment Variables
```bash
# Optional: Set custom configuration path
export TRAFFIC_SIM_CONFIG=config/custom.yaml

# Optional: Set log level
export TRAFFIC_SIM_LOG_LEVEL=DEBUG
```

### 5. Testing Strategy

#### Test Types
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end simulation testing
- **Property Tests**: Hypothesis-based testing
- **Performance Tests**: Timing and memory usage

#### Test Organization
```python
# tests/test_idm.py - IDM controller tests
# tests/test_sim.py - Simulation integration tests
# tests/test_track.py - Track geometry tests
# tests/test_track_properties.py - Track property tests
```

#### Writing Tests
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

### 6. Code Style Guidelines

#### Type Annotations
```python
from __future__ import annotations
from typing import List, Dict, Optional, Tuple

def process_vehicles(vehicles: List[Vehicle], config: Dict[str, Any]) -> Optional[Result]:
    """Process vehicles with given configuration."""
    pass
```

#### Docstrings
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

#### Error Handling
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

### 7. Performance Considerations

#### Optimization Guidelines
- **Minimize allocations** in hot paths
- **Use numpy** for numerical computations
- **Cache expensive calculations**
- **Profile before optimizing**

#### Performance Testing
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

### 8. Debugging

#### Debug Mode
```bash
# Run with debug logging
uv run python -m traffic_sim --debug

# Run with specific log level
uv run python -m traffic_sim --log-level DEBUG
```

#### Common Issues
1. **Type checking errors**: Check imports and type annotations
2. **Import errors**: Verify module structure and `__init__.py` files
3. **Performance issues**: Profile and optimize hot paths
4. **Test failures**: Check test data and assertions

### 9. Contributing

#### Pull Request Process
1. **Create feature branch** from `main`
2. **Implement changes** with tests
3. **Run quality gates** locally
4. **Update documentation** as needed
5. **Submit pull request** with description
6. **Address review feedback**
7. **Merge after approval**

#### Commit Message Format
```
type: brief description

Detailed description of changes made.
- Bullet point for specific changes
- Another bullet point if needed

Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### 10. CI/CD Pipeline

#### GitHub Actions
The project uses GitHub Actions for continuous integration:

- **Quality Gates**: Run on every push and PR
- **Testing**: Run tests on multiple Python versions
- **Coverage**: Generate and report test coverage
- **Security**: Scan for vulnerabilities

#### Pre-commit Hooks
Quality gates run locally before commits:
```bash
# Install hooks
uv run pre-commit install

# Run on all files
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run ruff --files src/traffic_sim/core/driver.py
```

### 11. Documentation

#### Code Documentation
- **Docstrings**: All public functions and classes
- **Type hints**: All function signatures
- **Comments**: Complex logic and algorithms
- **README**: Project overview and setup

#### API Documentation
- **Module docstrings**: Package and module descriptions
- **Class docstrings**: Class purpose and usage
- **Method docstrings**: Parameters, returns, and examples

### 12. Maintenance

#### Regular Tasks
- **Update dependencies**: Keep tools and libraries current
- **Review quality metrics**: Monitor and improve code quality
- **Update documentation**: Keep docs in sync with code
- **Performance monitoring**: Track and optimize performance

#### Monitoring
```bash
# Check quality metrics
uv run python scripts/quality_monitor.py

# Generate quality report
uv run python scripts/quality_monitor.py > quality_report.json

# Check test coverage
uv run python -m pytest --cov=traffic_sim --cov-report=html
```

## Getting Help

### Resources
- **Documentation**: `docs/` directory
- **Static Analysis Guide**: `docs/static-analysis.md`
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

This development guide should help you contribute effectively to the traffic simulator project while maintaining high code quality standards.
