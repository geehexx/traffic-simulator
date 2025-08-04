# Quality Standards Guide

This document provides comprehensive quality standards, static analysis tools, and testing guidelines for the traffic simulator project.

## Table of Contents
- [Overview](#overview)
- [Static Analysis Tools](#static-analysis-tools)
- [Quality Gates](#quality-gates)
- [Code Quality Standards](#code-quality-standards)
- [Testing Standards](#testing-standards)
- [Performance Standards](#performance-standards)
- [Security Standards](#security-standards)
- [Documentation Standards](#documentation-standards)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)

## Overview

The project uses a comprehensive static analysis framework with multiple tools to ensure code quality, type safety, security, and maintainability. The system includes automated quality gates that enforce standards before code can be committed or merged.

## Static Analysis Tools

### 1. Type Checking

#### Pyright
- **Purpose**: Fast, accurate type checking with excellent IDE integration
- **Configuration**: [pyproject.toml](mdc:pyproject.toml) (pyright section)
 - **Features**: Advanced type analysis, unused variable detection, override detection, fast type checking
- **Usage**: `bazel build //...` (integrated into Bazel)

### 2. Code Quality

#### Ruff
- **Purpose**: Fast Python linter and formatter
- **Configuration**: [pyproject.toml](mdc:pyproject.toml) (ruff section)
- **Features**: Linting, formatting, import sorting, type checking
- **Usage**:
  - `bazel build //...` (linting and formatting integrated into Bazel)

### 3. Security Analysis

#### Bandit
- **Purpose**: Security vulnerability scanning
- **Configuration**: [config/bandit.yaml](mdc:config/bandit.yaml)
- **Features**: Security issue detection, vulnerability scanning
- **Usage**: `bazel build //...` (integrated into Bazel)

### 4. Complexity Analysis

#### Radon
- **Purpose**: Code complexity analysis
- **Configuration**: Built-in thresholds
- **Features**: Cyclomatic complexity, maintainability index
- **Usage**: `bazel build //...` (integrated into Bazel)

## Configuration Reference

### Pyright Configuration
The project uses Pyright for type checking with the following configuration in `pyproject.toml`:

```toml
[tool.pyright]
include = ["src/"]
exclude = ["tests/", "scripts/", "**/__pycache__", "**/node_modules"]
pythonVersion = "3.10"
typeCheckingMode = "standard"
useLibraryCodeForTypes = true
reportMissingImports = true
reportMissingTypeStubs = false
reportUnnecessaryTypeIgnoreComment = true
```

### Quality Gates Thresholds
Current quality gates enforce the following standards:

```yaml
tools:
  pyright:
    max_errors: 0
    max_warnings: 3
    fail_on_any_error: true

  ruff:
    max_errors: 0
    max_warnings: 5
    max_info: 10
    fail_on_format_issues: true

  bandit:
    max_high_severity: 0
    max_medium_severity: 0
    max_low_severity: 3

  radon:
    max_complexity_C: 0
    max_complexity_D: 0
    max_complexity_E: 0
    max_complexity_F: 0
    average_complexity_max: 3.0
```

## IDE Integration

### VS Code Setup
For optimal development experience with Pyright:

1. **Install Python Extension**: Ensure the official Python extension is installed
2. **Configure Pyright**: Add to `settings.json`:
   ```json
   {
     "python.analysis.typeCheckingMode": "standard",
     "python.analysis.autoImportCompletions": true
   }
   ```
3. **Workspace Settings**: The project's `pyproject.toml` configuration will be automatically detected

### PyCharm Setup
1. **Enable Type Checking**: Go to Settings → Editor → Inspections → Python → Type checking
2. **Configure External Tools**: Add Pyright as an external tool for manual type checking
3. **Import Project**: Open the project root to automatically detect configuration

## Quality Analysis Workflow

### Automated Quality Gates
Quality gates run automatically on every commit via pre-commit hooks:

**Configuration**: Optimized for efficiency with `pass_filenames: false` to prevent multiple executions.

```bash
# Manual quality check (integrated into Bazel)
bazel build //...

# Detailed monitoring
bazel test //... --test_output=all

# Comprehensive analysis
bazel query //...
```

### Individual Tool Usage
```bash
# All quality checks integrated into Bazel
bazel build //...

# Run tests with coverage
bazel test //... --test_output=all

# Query build graph
bazel query //...
```

## Best Practices

### Type Safety
- Use `from __future__ import annotations` for forward compatibility
- Prefer specific type hints over `Any`
- Use `# type: ignore` sparingly and with specific error codes

### Code Quality
- Follow PEP 8 standards enforced by Ruff
- Keep functions under 50 lines and complexity ≤10
- Use Google-style docstrings for public APIs
- Organize imports: standard library, third-party, local

### Security
- Run Bandit regularly to catch security issues
- Avoid hardcoded secrets or credentials
- Use environment variables for configuration

### Performance
- Monitor complexity with Radon
- Use type hints to enable better IDE support
- Leverage Pyright's advanced type analysis for better code understanding

## Quality Gates

### Configuration

Quality gates are defined in [config/quality_gates.yaml](mdc:config/quality_gates.yaml) with the following structure:

```yaml
overall:
  max_critical_issues: 0
  max_high_issues: 0
  max_medium_issues: 5
  max_low_issues: 10
  max_total_issues: 15

tools:
  ruff:
    max_errors: 0
    max_warnings: 5
    max_info: 10
    fail_on_format_issues: true

  pyright:
    max_errors: 0
    max_warnings: 3
    fail_on_any_error: true

  # ... other tools
```

### Running Quality Gates

#### Manual Execution
```bash
# Run all quality gates (integrated into Bazel)
bazel build //...

# Run quality monitoring
bazel test //... --test_output=all

# Run comprehensive static analysis
bazel query //...
```

#### Quality Checks
Quality checks are integrated into Bazel:
```bash
# Quality checks are integrated into Bazel
bazel build //...

# Run tests with coverage
bazel test //... --test_output=all
```

#### CI/CD Pipeline
Quality gates run automatically in GitHub Actions on every push and pull request.

## Code Quality Standards

### Type Annotations
- Always add type hints to function parameters and return values
- Use `from __future__ import annotations` for forward references
- Import types in `TYPE_CHECKING` blocks when only used for annotations
- Use `Optional[T]` instead of `Union[T, None]`
- Prefer `List[T]` over `list[T]` for Python < 3.9 compatibility

### Import Organization
- Use `from __future__ import annotations` at the top
- Group imports: standard library, third-party, local imports
- Use `TYPE_CHECKING` for type-only imports
- Keep imports at the top of files

### Error Handling
- Use specific exception types, not bare `except:`
- Include context in error messages
- Use `raise ... from e` for exception chaining
- Log errors with appropriate levels

### Code Style
- Keep functions under 50 lines and classes under 200 lines
- Maintain cyclomatic complexity ≤10
- Use descriptive variable and function names
- Add docstrings for all public functions and classes
- Follow PEP 8 guidelines with 100 character line length

## Testing Standards

### Test Organization
- Unit tests in [idm_test.py](mdc:tests/idm_test.py) for IDM controller
- Integration tests in [sim_test.py](mdc:tests/sim_test.py) for simulation
- Track tests in [track_test.py](mdc:tests/track_test.py) for geometry
- Property tests for driver behavior validation

### Test File Naming
- All test files must end with `_test.py`
- Use descriptive names that indicate the module being tested
- Examples: `idm_test.py`, `sim_test.py`, `track_test.py`
- Avoid redundant prefixes like `test_` at the beginning

### Test Structure
- Use descriptive test names: `test_should_calculate_correct_acceleration_when_leading_vehicle_brakes`
- Group related tests in classes
- Use fixtures for common test data
- Follow Arrange-Act-Assert pattern

### Deterministic Testing
- Use fixed random seeds for reproducible tests
- Test with known inputs and expected outputs
- Validate simulation determinism across runs
- Use property-based testing for edge cases

### Coverage Requirements
- Maintain ≥70% line coverage
- Test all public functions and methods
- Cover error conditions and edge cases
- Test both success and failure paths
// Coverage values change over time; use CI reports for current metrics.

### Performance Testing
- Verify 30+ FPS target with 20+ vehicles
- Test memory usage and allocation patterns
- Profile simulation performance
- Validate deterministic behavior

### Mocking and Fixtures
- Use pytest fixtures for common setup
- Mock external dependencies appropriately
- Create realistic test data
- Use hypothesis for property-based testing

## Performance Standards

### Performance Targets
- **Frame Rate**: 30+ FPS with 20+ vehicles
- **Memory**: Minimal runtime allocations
- **Deterministic**: Fixed-step simulation
- **Scalability**: Support 50+ vehicles

### Acceptance Criteria (v0.4)
The simulation must meet the following acceptance criteria:
- **Window Scaling**: Window resizes maintain scaling
- **Performance**: ≥30 FPS on target hardware
- **Vehicle Behavior**: 20 vehicles circulate stably with realistic spacing
- **Driver Differences**: Statistical drivers produce measurable differences in headway, braking onset, overspeeding percent-time and episode durations
- **Perception**: Occlusion-based perception with dynamic SSD active
- **Safety Panel**: Displays R, V_safe, and L_needed; warning appears when unsafe
- **Determinism**: Deterministic replay under fixed seed; up to 10× speed factor stable
- **Collisions**: Create visual effect and disable vehicle for 5s
- **Analytics**: Live analytics display real-time speed histogram, headway distribution, and near-miss counter
- **Physics**: Collision system uses pymunk physics with lateral push effects and vehicle disable
- **Data Logging**: Exports comprehensive CSV data with configurable rates
- **Performance Metrics**: Tracking shows FPS, memory usage, and simulation timing

### Optimization Guidelines
- Minimize allocations in hot paths
- Use numpy for numerical computations
- Cache expensive calculations
- Profile before optimizing
- Target 30+ FPS for simulation

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

### Profiling & Benchmarks

- Profiling CLI: `scripts/profile_simulation.py` (CSV output, optional cProfile)
- Benchmark CLI: `scripts/performance_analysis.py --mode=benchmark` (vectorized flags enabled)
- Nightly profiling workflow: `.github/workflows/profile.yml`
- On-demand benchmark workflow: `.github/workflows/benchmark.yml`

### Feature Flags & Configuration

- **Event-Driven Collision Detection**: `collisions.event_scheduler_enabled` (default: false)
- **NumPy Physics Engine**: `physics.numpy_engine_enabled` (default: false)
- **High-Performance Mode**: `high_performance.enabled` (default: false)
- **Vectorized IDM**: `high_performance.idm_vectorized` (default: false)
- **Data Manager**: `data_manager.enabled` (default: false)

**Configuration Example**:
```yaml
collisions:
  event_scheduler_enabled: true
  event_horizon_s: 3.0
  guard_band_m: 0.3
  scheduler_max_follower_accel_mps2: 2.0
  scheduler_max_leader_brake_mps2: 4.0

physics:
  numpy_engine_enabled: true

high_performance:
  enabled: true
  idm_vectorized: true

data_manager:
  enabled: true
  max_vehicles: 10000
```

## Security Standards

### Security Best Practices
- No hardcoded secrets or passwords
- Use secure random generators for crypto purposes
- Validate all inputs and sanitize outputs
- Keep dependencies up to date
- Run security scans regularly

### Security Scanning
```bash
# Check security issues (integrated into Bazel)
bazel build //...

# Check for vulnerable dependencies
bazel query //...
```

## Documentation Standards

### Docstring Format
- Use Google-style docstrings
- Include Args, Returns, and Raises sections
- Provide examples for complex functions
- Document all public APIs

### Code Examples
- Use realistic examples from the codebase
- Include expected outputs
- Show both basic and advanced usage
- Update examples when code changes

### API Documentation
- Document all public functions and classes
- Include type information
- Provide usage examples
- Explain return values and exceptions

### Documentation Maintenance
- **Pattern**: Keep documentation in sync with code changes
- **Process**: Update when code changes, review regularly, validate accuracy
- **Tools**: Automated checks, manual review, user feedback
- **Reference**: [Documentation Guide](mdc:docs/DOCUMENTATION_GUIDE.md#maintenance-procedures)

## Usage Examples

### Fixing Common Issues

#### Type Checking Issues
```bash
# Fix Pyright issues (integrated into Bazel)
bazel build //...
```

#### Code Quality Issues
```bash
# Fix Ruff linting issues (integrated into Bazel)
bazel build //...

# Format code (integrated into Bazel)
bazel build //...
```

#### Security Issues
```bash
# Check security issues (integrated into Bazel)
bazel build //...
```

### Adding New Rules

#### Ruff Rules
Add rules to [pyproject.toml](mdc:pyproject.toml):
```toml
[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "YTT", "S", "BLE", "FBT", "B", "A", "COM", "C4", "DTZ", "T10", "EM", "EXE", "FA", "ISC", "ICN", "G", "INP", "PIE", "T20", "PYI", "PT", "Q", "RSE", "RET", "SLF", "SLOT", "SIM", "TID", "TCH", "INT", "ARG", "PTH", "TD", "FIX", "ERA", "PD", "PGH", "PL", "TRY", "FLY", "NPY", "AIR", "PERF", "FURB", "LOG", "RUF"]
```

#### Pyright Rules
Add rules to [pyproject.toml](mdc:pyproject.toml):
```toml
[tool.pyright]
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Check if py.typed marker exists
ls src/traffic_sim/py.typed

# Verify module structure
python -c "import traffic_sim.core.simulation"
```

#### Type Stub Issues
```bash
# Regenerate type stubs (integrated into Bazel)
bazel build //...
```

#### Pre-commit Hook Failures
```bash
# Quality checks are integrated into Bazel
bazel build //...

# Run tests with coverage
bazel test //... --test_output=all

# For comprehensive troubleshooting, see:
# docs/COMMIT_TROUBLESHOOTING.md
```

### Getting Help

1. **Check tool documentation**:
   - [Pyright](https://github.com/microsoft/pyright)
   - [Ruff](https://docs.astral.sh/ruff/)
   - [Bandit](https://bandit.readthedocs.io/)
   - [Radon](https://radon.readthedocs.io/)

2. **Run quality monitoring**:
   ```bash
   bazel test //... --test_output=all
   ```

3. **Check CI logs** for detailed error information

## Contributing

When contributing to the project:

1. **Run quality gates locally** before committing
2. **Fix all quality gate failures** before submitting PRs
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Follow the established code style** and patterns

## Continuous Improvement

The static analysis framework is continuously improved:

- **Regular updates** to tool versions and configurations
- **Threshold adjustments** based on project needs
- **New tool integration** as requirements evolve
- **Performance optimization** of analysis scripts
- **Documentation updates** to reflect changes

For questions or suggestions about the quality standards framework, please open an issue or discuss in the project's communication channels.
