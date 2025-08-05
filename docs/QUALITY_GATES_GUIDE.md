# Quality Gates User Guide

This guide explains how to use the quality gates system to maintain code quality and ensure project standards.

## Table of Contents
- [Overview](#overview)
- [Running Quality Gates](#running-quality-gates)
- [Understanding Results](#understanding-results)
- [Fixing Issues](#fixing-issues)
- [Enforcement System](#enforcement-system)
- [Configuration](#configuration)

## Overview

The quality gates system enforces code quality standards through automated static analysis. It runs 7 different tools and ensures all code meets project standards before merging.

## Running Quality Gates

### Manual Execution
```bash
# Run all quality gates (integrated into Bazel)
bazel build //...

# Run quality monitoring
bazel test //... --test_output=all

# Run comprehensive analysis
bazel query //...
```

### Quality Checks
Quality checks are integrated into Bazel:
```bash
# Quality checks are integrated into Bazel
bazel build //...

# Run tests with coverage
bazel test //... --test_output=all
```

## Understanding Results

### Quality Gate Status
- **PASS**: All checks passed
- **FAIL**: One or more checks failed
- **WARN**: Some issues but within thresholds

### Status Reporting
- Use CI job artifacts or `bazel build //...` for up-to-date pass/fail and coverage (integrated into Bazel).
- Avoid embedding static numbers that drift over time.

## Fixing Issues

### Type Checking Issues
```bash
# Fix Pyright issues (integrated into Bazel)
bazel build //...
```

### Code Quality Issues
```bash
# Fix Ruff linting issues (integrated into Bazel)
bazel build //...

# Format code (integrated into Bazel)
bazel build //...
```

### Security Issues
```bash
# Check security issues (integrated into Bazel)
bazel build //...
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

## Enforcement System

The quality gates system includes comprehensive enforcement for commit messages, documentation, and rules:

### Commit Message Enforcement
- **Conventional Commits**: All commits must follow standardized format
- **Validation**: Automated via commitlint and pre-commit hooks
- **Types**: feat, fix, docs, style, refactor, test, chore, perf, ci, build, revert

### Documentation Enforcement
- **Markdown Validation**: Automated formatting and style checking
- **Link Checking**: Validates all internal and external links
- **Spell Checking**: Technical dictionary with project-specific terms
- **Quality Gates**: Integrated with Bazel build system

### Rules Enforcement
- **Structure Validation**: Automated frontmatter and format checking
- **Compliance**: Global rules limit (max 5), token limits, duplicate detection
- **Integration**: Pre-commit hooks and quality gates

### Manual Validation
```bash
# Run all enforcement checks
uv run pre-commit run --all-files

# Individual validation tools
npx commitlint --version
npx markdownlint docs/**/*.md
npx cspell "docs/**/*.md"
python3 scripts/validate_rules.py
```

## Troubleshooting

### Common Issues
1. **Import errors**: Check module structure and `__init__.py` files
2. **Type errors**: Verify type annotations and imports
3. **Formatting issues**: Run `ruff format` to fix
4. **Coverage issues**: Add tests for uncovered code
5. **Enforcement issues**: See [Enforcement Troubleshooting](docs/ENFORCEMENT_TROUBLESHOOTING.md)

### Getting Help
- Check tool documentation
- Review quality standards guide
- See enforcement troubleshooting guide
- Open issues for persistent problems
