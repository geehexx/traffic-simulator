# Quality Gates User Guide

This guide explains how to use the quality gates system to maintain code quality and ensure project standards.

## Table of Contents
- [Overview](#overview)
- [Running Quality Gates](#running-quality-gates)
- [Understanding Results](#understanding-results)
- [Fixing Issues](#fixing-issues)
- [Configuration](#configuration)

## Overview

The quality gates system enforces code quality standards through automated static analysis. It runs 7 different tools and ensures all code meets project standards before merging.

## Running Quality Gates

### Manual Execution
```bash
# Run all quality gates
uv run python scripts/quality_analysis.py --mode=check

# Run quality monitoring
uv run python scripts/quality_analysis.py --mode=monitor

# Run comprehensive analysis
uv run python scripts/quality_analysis.py --mode=analyze
```

### Pre-commit Hooks
Quality gates run automatically on every commit:
```bash
# Install pre-commit hooks
uv run pre-commit install

# Run on all files
uv run pre-commit run --all-files
```

## Understanding Results

### Quality Gate Status
- **PASS**: All checks passed
- **FAIL**: One or more checks failed
- **WARN**: Some issues but within thresholds

### Status Reporting
- Use CI job artifacts or `uv run python scripts/quality_analysis.py --mode=check` for up-to-date pass/fail and coverage.
- Avoid embedding static numbers that drift over time.

## Fixing Issues

### Type Checking Issues
```bash
# Fix Pyright issues
uv run pyright src/
```

### Code Quality Issues
```bash
# Fix Ruff linting issues
uv run ruff check src/ --fix

# Format code
uv run ruff format src/

```

### Security Issues
```bash
# Check security issues
uv run bandit -r src/ -c config/bandit.yaml
```

## Configuration

Quality gates are configured in `config/quality_gates.yaml`:
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
  # ... other tools
```

## Troubleshooting

### Common Issues
1. **Import errors**: Check module structure and `__init__.py` files
2. **Type errors**: Verify type annotations and imports
3. **Formatting issues**: Run `ruff format` to fix
4. **Coverage issues**: Add tests for uncovered code

### Getting Help
- Check tool documentation
- Review quality standards guide
- Open issues for persistent problems
