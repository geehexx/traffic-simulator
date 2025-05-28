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

#### MyPy
- **Purpose**: Static type checking for Python
- **Configuration**: [mypy.ini](mdc:mypy.ini)
- **Features**: Strict type checking, import validation, type inference
- **Usage**: `uv run mypy src/`

#### Pyright
- **Purpose**: Enhanced type checking with better IDE integration
- **Configuration**: [pyrightconfig.json](mdc:pyrightconfig.json)
- **Features**: Advanced type analysis, unused variable detection, override detection
- **Usage**: `uv run pyright src/`

### 2. Code Quality

#### Ruff
- **Purpose**: Fast Python linter and formatter
- **Configuration**: [pyproject.toml](mdc:pyproject.toml) (ruff section)
- **Features**: Linting, formatting, import sorting, type checking
- **Usage**:
  - `uv run ruff check src/` (linting)
  - `uv run ruff format src/` (formatting)

#### Pylint
- **Purpose**: Comprehensive code quality analysis
- **Configuration**: [pylintrc](mdc:pylintrc)
- **Features**: Code quality scoring, style checking, error detection
- **Usage**: `uv run pylint src/ --rcfile=pylintrc`

### 3. Security Analysis

#### Bandit
- **Purpose**: Security vulnerability scanning
- **Configuration**: [bandit.yaml](mdc:bandit.yaml)
- **Features**: Security issue detection, vulnerability scanning
- **Usage**: `uv run bandit -r src/ -c bandit.yaml`

### 4. Complexity Analysis

#### Radon
- **Purpose**: Code complexity analysis
- **Configuration**: [radon.cfg](mdc:radon.cfg)
- **Features**: Cyclomatic complexity, maintainability index
- **Usage**: `uv run radon cc src/ -a --min B`

## Quality Gates

### Configuration

Quality gates are defined in [quality_gates.yaml](mdc:quality_gates.yaml) with the following structure:

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

  mypy:
    max_errors: 0
    max_warnings: 3
    fail_on_any_error: true

  # ... other tools
```

### Running Quality Gates

#### Manual Execution
```bash
# Run all quality gates
uv run python scripts/quality_gates.py

# Run quality monitoring
uv run python scripts/quality_monitor.py

# Run comprehensive static analysis
uv run python scripts/static_analysis.py
```

#### Pre-commit Hooks
Quality gates run automatically on every commit:
```bash
# Install pre-commit hooks
uv run pre-commit install

# Run on all files
uv run pre-commit run --all-files
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
- **Current**: 79% coverage (target: 70%)

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

## Security Standards

### Security Best Practices
- No hardcoded secrets or passwords
- Use secure random generators for crypto purposes
- Validate all inputs and sanitize outputs
- Keep dependencies up to date
- Run security scans regularly

### Security Scanning
```bash
# Check security issues
uv run bandit -r src/ -c bandit.yaml

# Check for vulnerable dependencies
uv run pip-audit
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

## Usage Examples

### Fixing Common Issues

#### Type Checking Issues
```bash
# Fix MyPy issues
uv run mypy src/ --show-error-codes

# Fix Pyright issues
uv run pyright src/
```

#### Code Quality Issues
```bash
# Fix Ruff linting issues
uv run ruff check src/ --fix

# Format code
uv run ruff format src/

# Fix Pylint issues
uv run pylint src/ --rcfile=pylintrc
```

#### Security Issues
```bash
# Check security issues
uv run bandit -r src/ -c bandit.yaml
```

### Adding New Rules

#### Ruff Rules
Add rules to [pyproject.toml](mdc:pyproject.toml):
```toml
[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "YTT", "S", "BLE", "FBT", "B", "A", "COM", "C4", "DTZ", "T10", "EM", "EXE", "FA", "ISC", "ICN", "G", "INP", "PIE", "T20", "PYI", "PT", "Q", "RSE", "RET", "SLF", "SLOT", "SIM", "TID", "TCH", "INT", "ARG", "PTH", "TD", "FIX", "ERA", "PD", "PGH", "PL", "TRY", "FLY", "NPY", "AIR", "PERF", "FURB", "LOG", "RUF"]
```

#### MyPy Rules
Add rules to [mypy.ini](mdc:mypy.ini):
```ini
[mypy]
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
# Regenerate type stubs
uv run stubgen -p arcade -o stubs
uv run stubgen -p pymunk -o stubs
```

#### Pre-commit Hook Failures
```bash
# Update pre-commit hooks
uv run pre-commit autoupdate

# Run specific hook
uv run pre-commit run ruff --files src/traffic_sim/core/driver.py
```

### Getting Help

1. **Check tool documentation**:
   - [MyPy](https://mypy.readthedocs.io/)
   - [Pyright](https://github.com/microsoft/pyright)
   - [Ruff](https://docs.astral.sh/ruff/)
   - [Pylint](https://pylint.pycqa.org/)
   - [Bandit](https://bandit.readthedocs.io/)
   - [Radon](https://radon.readthedocs.io/)

2. **Run quality monitoring**:
   ```bash
   uv run python scripts/quality_monitor.py
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
