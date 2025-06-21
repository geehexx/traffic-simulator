# Scripts Guide

This guide covers the consolidated analysis scripts available in the traffic simulator project.

## Table of Contents
- [Quality Analysis](#quality-analysis)
- [Performance Analysis](#performance-analysis)
- [Specialized Scripts](#specialized-scripts)
- [Task Commands](#task-commands)
- [Usage Examples](#usage-examples)

## Quality Analysis

The `scripts/quality_analysis.py` script provides comprehensive quality analysis with three modes:

### Check Mode (Quality Gates)
```bash
# Run quality gates enforcement
uv run python scripts/quality_analysis.py --mode=check

# With custom config
uv run python scripts/quality_analysis.py --mode=check --config custom_quality_gates.yaml
```

**Features:**
- Ruff linting and formatting checks
- Pyright type checking
- Bandit security scanning
- Radon complexity analysis
- Test coverage validation

### Monitor Mode (Detailed Monitoring)
```bash
# Run detailed quality monitoring
uv run python scripts/quality_analysis.py --mode=monitor

# With custom output file
uv run python scripts/quality_analysis.py --mode=monitor --output quality_report.json
```

**Features:**
- Comprehensive quality metrics collection
- Detailed reporting with recommendations
- JSON output for integration
- Quality score calculation
- Tool-specific recommendations

### Analyze Mode (Comprehensive Analysis)
```bash
# Run comprehensive static analysis
uv run python scripts/quality_analysis.py --mode=analyze

# With custom output
uv run python scripts/quality_analysis.py --mode=analyze --output analysis_report.json
```

**Features:**
- Full static analysis suite
- Detailed metrics and reporting
- Comprehensive quality assessment
- Integration-ready output formats

## Performance Analysis

The `scripts/performance_analysis.py` script has been superseded by the unified benchmarking framework. Use the new framework for all performance testing:

### Unified Benchmarking Framework
```bash
# Single benchmark
uv run python scripts/benchmarking_framework.py --mode=benchmark --vehicles 100 --steps 1000

# Scale testing
uv run python scripts/benchmarking_framework.py --mode=scale --vehicle-counts 20 50 100 200

# Performance monitoring
uv run python scripts/benchmarking_framework.py --mode=monitor --duration 5 --vehicles 100

# Advanced profiling
uv run python scripts/benchmarking_framework.py --mode=profile --vehicles 100 --steps 1000
```

### External Tools Integration
```bash
# pytest-benchmark integration
uv run python scripts/external_tools.py --tool pytest

# Hyperfine benchmarking
uv run python scripts/external_tools.py --tool hyperfine

# Py-Spy profiling
uv run python scripts/external_tools.py --tool pyspy

# All tools
uv run python scripts/external_tools.py --tool all
```

### Advanced Profiling
```bash
# Memory analysis
uv run python scripts/advanced_profiling.py --mode=memory --vehicles 100 --steps 1000

# Scaling analysis
uv run python scripts/advanced_profiling.py --mode=scaling --vehicle-counts 10 20 50 100 200

# Comprehensive analysis
uv run python scripts/advanced_profiling.py --mode=comprehensive --vehicles 100 --steps 1000
```

### Migration Support
```bash
# Check migration readiness
uv run python scripts/migrate_performance_tests.py --check-only

# Run migration
uv run python scripts/migrate_performance_tests.py

# Dry run (see what would be done)
uv run python scripts/migrate_performance_tests.py --dry-run
```

**Reference**: [Benchmarking Guide](mdc:docs/BENCHMARKING_GUIDE.md)

## Specialized Scripts

### Advanced Profiling
```bash
# Memory analysis
uv run python scripts/advanced_profiling.py --mode=memory --vehicles 100 --steps 1000

# Scaling analysis
uv run python scripts/advanced_profiling.py --mode=scaling --vehicle-counts 10 20 50 100 200

# Comprehensive analysis
uv run python scripts/advanced_profiling.py --mode=comprehensive --vehicles 100 --steps 1000
```

**Features:**
- Advanced memory profiling with leak detection
- Performance prediction and scaling analysis
- Resource bottleneck identification
- Mathematical modeling of performance behavior

### Validation Testing
```bash
# Run validation tests
uv run python scripts/validation_test.py --verbose
```

**Features:**
- Behavioral consistency testing
- Edge case validation
- Optimization accuracy verification
- Comprehensive validation suite

## Task Commands

The project includes convenient task commands for all analysis tools:

### Quality Analysis Tasks
```bash
task quality              # Quality gates enforcement
task quality:monitor      # Detailed quality monitoring
task quality:analyze      # Comprehensive static analysis
```

### Performance Analysis Tasks
```bash
task performance          # Performance benchmark
task performance:scale    # Scale performance testing
task performance:monitor  # Real-time performance monitoring
```

### Specialized Tasks
```bash
task profile              # Simulation profiling
task validate             # Validation testing
```

## Usage Examples

### Development Workflow
```bash
# 1. Run quality gates before committing
task quality

# 2. Run performance benchmark
task performance

# 3. Run comprehensive analysis
task quality:analyze
task performance:scale
```

### CI/CD Integration
```bash
# Quality gates for CI
uv run python scripts/quality_analysis.py --mode=check

# Performance validation
uv run python scripts/performance_analysis.py --mode=benchmark --vehicles 20 --steps 1000
```

### Monitoring and Reporting
```bash
# Generate quality report
uv run python scripts/quality_analysis.py --mode=monitor --output quality_report.json

# Run performance monitoring
uv run python scripts/performance_analysis.py --mode=monitor --duration 5
```

### Scale Testing
```bash
# Test performance across vehicle counts
uv run python scripts/performance_analysis.py --mode=scale --vehicle-counts 20 50 100 200 500
```

## Configuration

### Quality Gates Configuration
Quality analysis uses `quality_gates.yaml` for thresholds and rules. Key settings:

```yaml
tools:
  ruff:
    max_warnings: 5
  pyright:
    max_warnings: 3
  bandit:
    max_low_severity: 3
  radon:
    max_complexity_C: 0
    average_complexity_max: 3.0

coverage:
  min_line_coverage: 70
```

### Performance Configuration
Performance analysis uses the main simulation configuration. Key settings:

```yaml
physics:
  speed_factor: 10.0
  delta_t_s: 0.02

vehicles:
  count: 20

high_performance:
  enabled: true
  idm_vectorized: true
```

## Output Formats

### Quality Analysis Output
- **Console**: Human-readable summary with status indicators
- **JSON**: Structured data for integration and reporting
- **Exit Codes**: 0 for success, 1 for failures

### Performance Analysis Output
- **Console**: Performance metrics and summary
- **CSV**: Structured data for analysis and visualization
- **Real-time**: Live monitoring with alerts

## Integration

### Pre-commit Hooks
Quality analysis integrates with pre-commit hooks for automated quality enforcement.

### CI/CD Pipelines
All scripts are designed for CI/CD integration with appropriate exit codes and output formats.

### Development Tools
Scripts provide comprehensive analysis for development workflows and quality assurance.
