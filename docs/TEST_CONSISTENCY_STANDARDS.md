# Test File Consistency Standards

This document defines the consistency standards for test files in the traffic-simulator project to ensure all test files are directly runnable and follow a uniform structure.

## Overview

All test files in the `tests/` directory must follow these standards to ensure:
- **Direct execution**: Every test file can be run individually with `python tests/test_file.py`
- **Consistent structure**: Uniform imports, docstrings, and execution patterns
- **Pre-commit enforcement**: Automated checking via pre-commit hooks

## Standards

### 1. File Structure

Every test file must have the following structure in order:

```python
"""Brief description of what this test file covers."""

from __future__ import annotations

import pytest

# Other imports...

# Test functions and classes...

if __name__ == "__main__":
    pytest.main([__file__])
```

### 2. Required Elements

#### **Docstring**
- Must be the first line of the file
- Should briefly describe what the test file covers
- Format: `"""Brief description of what this test file covers."""`

#### **Future Annotations**
- Must include `from __future__ import annotations` at the top
- Enables forward references and better type checking

#### **Pytest Import**
- Must import `pytest` module
- Required for the main execution block

#### **Main Execution Block**
- Must include `if __name__ == "__main__": pytest.main([__file__])`
- Enables direct execution of individual test files
- Uses `[__file__]` only (no additional arguments like `-v`)

### 3. Prohibited Elements

#### **Shebang Lines**
- Test files should NOT start with `#!/usr/bin/env python3`
- Not needed for test files (unlike executable scripts)

#### **Additional Arguments**
- The main block should use `pytest.main([__file__])` only
- No additional flags like `-v`, `--verbose`, etc.

### 4. Import Organization

Follow this import order:
1. `from __future__ import annotations`
2. Standard library imports
3. Third-party imports (including `pytest`)
4. Local imports (from `traffic_sim.*`)

Example:
```python
"""Tests for the simulation module."""

from __future__ import annotations

import pytest
import tempfile
from unittest.mock import patch

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation
```

## Enforcement

### Pre-commit Hook

The standards are enforced via a pre-commit hook that:
- Runs automatically on all test files
- Checks for compliance with all standards
- Prevents commits if any test file fails the checks

### Manual Checking

You can manually check test file consistency:

```bash
# Check specific files (integrated into Bazel)
bazel test //tests:test_file

# Check all test files
bazel test //...
```

### Automatic Fixing

Use the automatic fixer to update test files:

```bash
# Fix all test files (integrated into Bazel)
bazel build //...
```

## Examples

### ✅ Correct Test File

```python
"""Tests for the simulation module."""

from __future__ import annotations

import pytest

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation


def test_simulation_creation():
    """Test that simulation can be created."""
    cfg = load_config()
    sim = Simulation(cfg)
    assert sim is not None


if __name__ == "__main__":
    pytest.main([__file__])
```

### ❌ Incorrect Test File

```python
#!/usr/bin/env python3  # ❌ No shebang lines
"""Tests for the simulation module."""

# ❌ Missing future annotations
import pytest

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation


def test_simulation_creation():
    """Test that simulation can be created."""
    cfg = load_config()
    sim = Simulation(cfg)
    assert sim is not None


# ❌ Missing main block
```

## Benefits

### For Developers
- **Direct execution**: Run individual test files during development
- **Consistent structure**: Easy to understand and maintain
- **Automated enforcement**: No manual checking required

### For CI/CD
- **Reliable testing**: All test files can be executed independently
- **Consistent behavior**: Uniform test execution across environments
- **Easy debugging**: Individual test file execution for troubleshooting

### For Code Quality
- **Type safety**: Future annotations enable better type checking
- **Maintainability**: Consistent structure across all test files
- **Documentation**: Clear docstrings explain test file purpose

## Migration

If you have existing test files that don't meet these standards:

1. **Automatic fix**: Run `bazel build //...` (integrated into Bazel)
2. **Manual review**: Check the changes and adjust as needed
3. **Verification**: Run the consistency checker to ensure compliance

## Tools

### `scripts/check_test_consistency.py`
- Checks test files for compliance with standards
- Reports specific issues found
- Used by pre-commit hooks

### `scripts/fix_test_consistency.py`
- Automatically fixes common consistency issues
- Adds missing imports, docstrings, and main blocks
- Reorganizes imports and removes shebang lines

## Related Documentation

- [Quality Standards](QUALITY_STANDARDS.md) - Overall code quality guidelines
- [Development Guide](DEVELOPMENT.md) - Development workflow and practices
- [Testing Guide](TESTING.md) - Testing strategies and best practices
