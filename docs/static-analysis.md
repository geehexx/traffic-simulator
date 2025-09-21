# Static Analysis Guide

This document provides a comprehensive guide to the static analysis tools and quality gates implemented in the traffic simulator project.

## Overview

The project uses a comprehensive static analysis framework with multiple tools to ensure code quality, type safety, security, and maintainability. The system includes automated quality gates that enforce standards before code can be committed or merged.

## Tools Overview

### 1. Type Checking

#### MyPy
- **Purpose**: Static type checking for Python
- **Configuration**: `mypy.ini`
- **Features**: Strict type checking, import validation, type inference
- **Usage**: `uv run mypy src/`

#### Pyright
- **Purpose**: Enhanced type checking with better IDE integration
- **Configuration**: `pyrightconfig.json`
- **Features**: Advanced type analysis, unused variable detection, override detection
- **Usage**: `uv run pyright src/`

### 2. Code Quality

#### Ruff
- **Purpose**: Fast Python linter and formatter
- **Configuration**: `pyproject.toml` (ruff section)
- **Features**: Linting, formatting, import sorting, type checking
- **Usage**: 
  - `uv run ruff check src/` (linting)
  - `uv run ruff format src/` (formatting)

#### Pylint
- **Purpose**: Comprehensive code quality analysis
- **Configuration**: `pylintrc`
- **Features**: Code quality scoring, style checking, error detection
- **Usage**: `uv run pylint src/ --rcfile=pylintrc`

### 3. Security Analysis

#### Bandit
- **Purpose**: Security vulnerability scanning
- **Configuration**: `bandit.yaml`
- **Features**: Security issue detection, vulnerability scanning
- **Usage**: `uv run bandit -r src/ -c bandit.yaml`

### 4. Complexity Analysis

#### Radon
- **Purpose**: Code complexity analysis
- **Configuration**: `radon.cfg`
- **Features**: Cyclomatic complexity, maintainability index
- **Usage**: `uv run radon cc src/ -a --min B`

## Quality Gates

### Configuration

Quality gates are defined in `quality_gates.yaml` with the following structure:

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

## Quality Thresholds

### Current Standards

| Tool | Threshold | Current Status |
|------|-----------|----------------|
| Ruff Linting | 0 errors, ≤5 warnings | ✅ Passing |
| Ruff Formatting | 0 issues | ✅ Passing |
| MyPy | 0 errors, ≤3 warnings | ⚠️ 1 issue |
| Pyright | 0 errors, ≤5 warnings | ❌ 17 issues |
| Pylint | ≥8.0/10 score | ✅ 9.3/10 |
| Bandit | 0 high/medium issues | ✅ 0 issues |
| Radon | 0 C/D/E/F complexity | ✅ 0 issues |
| Coverage | ≥80% line coverage | ❌ 67% |

### Quality Score
- **Current**: 76.9%
- **Target**: 80%+
- **Status**: ⚠️ Below threshold

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
Add rules to `pyproject.toml`:
```toml
[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "YTT", "S", "BLE", "FBT", "B", "A", "COM", "C4", "DTZ", "T10", "EM", "EXE", "FA", "ISC", "ICN", "G", "INP", "PIE", "T20", "PYI", "PT", "Q", "RSE", "RET", "SLF", "SLOT", "SIM", "TID", "TCH", "INT", "ARG", "PTH", "TD", "FIX", "ERA", "PD", "PGH", "PL", "TRY", "FLY", "NPY", "AIR", "PERF", "FURB", "LOG", "RUF"]
```

#### MyPy Rules
Add rules to `mypy.ini`:
```ini
[mypy]
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
```

## Best Practices

### 1. Type Annotations
- Always add type hints to function parameters and return values
- Use `from __future__ import annotations` for forward references
- Import types in `TYPE_CHECKING` blocks when only used for annotations

### 2. Code Quality
- Keep functions small and focused (max 50 lines)
- Maintain low cyclomatic complexity (max 10)
- Use descriptive variable and function names
- Add docstrings for public functions and classes

### 3. Security
- Avoid hardcoded secrets or passwords
- Use secure random number generators for cryptographic purposes
- Validate all inputs and sanitize outputs
- Keep dependencies up to date

### 4. Testing
- Maintain high test coverage (≥80%)
- Write unit tests for all public functions
- Use property-based testing for complex logic
- Test edge cases and error conditions

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

For questions or suggestions about the static analysis framework, please open an issue or discuss in the project's communication channels.
