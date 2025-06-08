# Commit Troubleshooting Guide

This guide addresses common pre-commit hook failures and provides solutions for maintaining code quality during the commit process.

## Table of Contents
- [Common Issues](#common-issues)
- [Quick Fixes](#quick-fixes)
- [Advanced Solutions](#advanced-solutions)
- [Prevention Strategies](#prevention-strategies)

## Common Issues

### 1. Type Checking Conflicts (MyPy vs Pyright)
**Problem**: MyPy and Pyright sometimes disagree on type annotations, especially with NumPy arrays and optional imports.

**Symptoms**:
- MyPy passes but Pyright fails with "Unnecessary type ignore comment"
- Pyright passes but MyPy fails with "Returning Any from function"

**Solution**:
```python
# Use specific error codes in type ignore comments
return self.state.copy()  # type: ignore[no-any-return]

# For optional imports, use import-not-found
import psutil  # type: ignore[import-not-found]
```

### 2. Executable Script Issues
**Problem**: Scripts with shebangs not marked as executable.

**Symptoms**:
- `check-shebang-scripts-are-executable` hook fails
- Scripts have `#!/usr/bin/env python3` but aren't executable

**Solution**:
```bash
# Make scripts executable
chmod +x scripts/script_name.py

# Or use git to set executable bit
git add --chmod=+x scripts/script_name.py
```

### 3. Unused Variable Warnings
**Problem**: Variables assigned but never used, especially in argument parsing.

**Symptoms**:
- `F841` error from Ruff: "Local variable 'args' is assigned to but never used"

**Solution**:
```python
# Instead of:
args = parser.parse_args()

# Use:
parser.parse_args()  # If args not needed
# Or:
args = parser.parse_args()
_ = args  # Explicitly mark as unused
```

### 4. Import Resolution Issues
**Problem**: Optional dependencies not available in development environment.

**Symptoms**:
- `reportMissingModuleSource` warnings for optional imports
- Import errors for packages like `numba`, `psutil`

**Solution**:
```python
# Use try/except with type ignore for optional imports
try:
    import numba  # type: ignore[import-not-found]
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
```

## Quick Fixes

### Run Pre-commit Hooks Manually
```bash
# Run all hooks
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run ruff --files src/traffic_sim/core/driver.py

# Update hooks
uv run pre-commit autoupdate
```

### Fix Common Formatting Issues
```bash
# Fix trailing whitespace and end-of-file issues
uv run pre-commit run trailing-whitespace --all-files
uv run pre-commit run end-of-file-fixer --all-files

# Format code
uv run ruff format src/
uv run black src/
```

### Fix Type Checking Issues
```bash
# Check MyPy issues
uv run mypy src/ --show-error-codes

# Check Pyright issues
uv run pyright src/

# Fix specific type issues
uv run mypy src/traffic_sim/core/physics_numpy.py --show-error-codes
```

## Advanced Solutions

### Bypass Hooks (Use Sparingly)
```bash
# Only when absolutely necessary
git commit --no-verify -m "commit message"

# Note: This bypasses all quality checks - use with caution
```

### Fix Complex Type Issues
```python
# For NumPy array return types, use proper type annotations
from typing import Any
import numpy as np

def step(self, actions: np.ndarray, dt: float) -> np.ndarray:
    # Implementation
    return self.state.copy()  # type: ignore[no-any-return]
```

### Handle Optional Dependencies
```python
# Create fallback decorators for optional dependencies
try:
    from numba import jit, njit  # type: ignore[import-not-found]
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

    def njit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
```

## Prevention Strategies

### Pre-commit Setup
```bash
# Install hooks
uv run pre-commit install

# Run before committing
uv run pre-commit run --all-files
```

### IDE Integration
- Configure your IDE to run Ruff/Black on save
- Enable type checking in your IDE
- Use pre-commit hooks in your IDE

### Development Workflow
1. **Before committing**: Run `uv run pre-commit run --all-files`
2. **Fix issues**: Address all hook failures
3. **Test locally**: Ensure all tests pass
4. **Commit**: Use conventional commit messages

### Common Commands Reference
```bash
# Quality checks
uv run python scripts/quality_gates.py
uv run python scripts/quality_monitor.py

# Linting and formatting
uv run ruff check src/ --fix
uv run ruff format src/
uv run black src/

# Type checking
uv run mypy src/ --show-error-codes
uv run pyright src/

# Security and complexity
uv run bandit -r src/ -c bandit.yaml
uv run radon cc src/ -a --min B
```

## Troubleshooting Checklist

### Before Committing
- [ ] Run `uv run pre-commit run --all-files`
- [ ] Fix all hook failures
- [ ] Ensure scripts are executable if they have shebangs
- [ ] Check for unused variables
- [ ] Verify type annotations are correct
- [ ] Test that changes work as expected

### Common Error Patterns
- **F841**: Unused variable - remove or mark as unused
- **E501**: Line too long - break into multiple lines
- **W293**: Trailing whitespace - remove whitespace
- **F401**: Unused import - remove unused imports
- **E402**: Import not at top - move imports to top

### Emergency Bypass
```bash
# Only use when absolutely necessary
git commit --no-verify -m "emergency: bypass hooks for critical fix"

# Follow up with proper fix
git commit --amend -m "proper: fix with proper quality checks"
```

## Best Practices

1. **Never bypass hooks routinely** - they catch real issues
2. **Fix issues immediately** - don't accumulate technical debt
3. **Use specific error codes** - make type ignore comments precise
4. **Keep hooks updated** - run `uv run pre-commit autoupdate` regularly
5. **Document exceptions** - explain why hooks are bypassed when necessary

## Getting Help

If you encounter persistent issues:
1. Check this guide for common solutions
2. Run `uv run pre-commit run --all-files` to see all issues
3. Use `--no-verify` only as a last resort
4. Document the issue for future reference
5. Consider updating project configuration if the issue is systemic
