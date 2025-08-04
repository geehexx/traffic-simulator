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
# Run quality gates enforcement (integrated into Bazel)
bazel build //...

# With custom config
bazel build //... --config=config/custom_quality_gates.yaml
```

**Features:**
- Ruff linting and formatting checks
- Pyright type checking
- Bandit security scanning
- Radon complexity analysis
- Test coverage validation

### Monitor Mode (Detailed Monitoring)
```bash
# Run detailed quality monitoring (integrated into Bazel)
bazel test //... --test_output=all

# With custom output file (defaults to runs/quality/)
bazel test //... --test_output=all --output=runs/quality/quality_report.json
```

**Features:**
- Comprehensive quality metrics collection
- Detailed reporting with recommendations
- JSON output for integration
- Quality score calculation
- Tool-specific recommendations

### Analyze Mode (Comprehensive Analysis)
```bash
# Run comprehensive static analysis (integrated into Bazel)
bazel query //...

# With custom output (defaults to runs/quality/)
bazel query //... --output=runs/quality/analysis_report.json
```

**Features:**
- Full static analysis suite
- Detailed metrics and reporting
- Comprehensive quality assessment
- Integration-ready output formats

## Performance Analysis

The `scripts/performance_analysis.py` script has been superseded by the unified benchmarking framework. Use the new framework for all performance testing:

### Unified Benchmarking Framework

**All output is automatically saved to the `runs/` directory** with organized subdirectories:

```bash
# Single benchmark (saves to runs/scaling/)
bazel run //scripts:benchmarking_framework -- --mode=benchmark --vehicles 100 --steps 1000

# Scale testing (saves to runs/scaling/)
bazel run //scripts:benchmarking_framework -- --mode=scale --vehicle-counts 20 50 100 200

# Performance monitoring (saves to runs/performance/)
bazel run //scripts:benchmarking_framework -- --mode=monitor --duration 5 --vehicles 100

# Advanced profiling (saves to runs/profiling/)
bazel run //scripts:benchmarking_framework -- --mode=profile --vehicles 100 --steps 1000
```

### External Tools Integration
```bash
# pytest-benchmark integration
bazel run //scripts:external_tools -- --tool pytest

# Hyperfine benchmarking
bazel run //scripts:external_tools -- --tool hyperfine

# Py-Spy profiling
bazel run //scripts:external_tools -- --tool pyspy

# All tools
bazel run //scripts:external_tools -- --tool all
```

### Advanced Profiling

**All profiling output is saved to the `runs/` directory** with organized subdirectories:

```bash
# Memory analysis (saves to runs/profiling/)
bazel run //scripts:advanced_profiling -- --mode=memory --vehicles 100 --steps 1000

# Scaling analysis (saves to runs/scaling/)
bazel run //scripts:advanced_profiling -- --mode=scaling --vehicle-counts 10 20 50 100 200

# Comprehensive analysis (saves to runs/profiling/)
bazel run //scripts:advanced_profiling -- --mode=comprehensive --vehicles 100 --steps 1000
```

### Validation Testing
```bash
# Run validation tests
bazel test //tests:validation_test --test_output=all
```

**Reference**: [Benchmarking Guide](mdc:docs/BENCHMARKING_GUIDE.md)

## Specialized Scripts

### Advanced Profiling
```bash
# Memory analysis
bazel run //scripts:advanced_profiling -- --mode=memory --vehicles 100 --steps 1000

# Scaling analysis
bazel run //scripts:advanced_profiling -- --mode=scaling --vehicle-counts 10 20 50 100 200

# Comprehensive analysis
bazel run //scripts:advanced_profiling -- --mode=comprehensive --vehicles 100 --steps 1000
```

**Features:**
- Advanced memory profiling with leak detection
- Performance prediction and scaling analysis
- Resource bottleneck identification
- Mathematical modeling of performance behavior

### Validation Testing
```bash
# Run validation tests
bazel test //tests:validation_test --test_output=all
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
# Quality gates for CI (integrated into Bazel)
bazel build //...

# Performance validation
bazel run //scripts:benchmarking_framework -- --mode=benchmark --vehicles 20 --steps 1000
```

### Monitoring and Reporting
```bash
# Generate quality report (saves to runs/quality/)
bazel test //... --test_output=all --output=runs/quality/quality_report.json

# Run performance monitoring (saves to runs/performance/)
bazel run //scripts:benchmarking_framework -- --mode=monitor --duration 5

# Generate test coverage (saves to runs/coverage/)
bazel test //... --test_output=all
```

### Scale Testing
```bash
# Test performance across vehicle counts
bazel run //scripts:benchmarking_framework -- --mode=scale --vehicle-counts 20 50 100 200 500
```

## Configuration

### Quality Gates Configuration
Quality analysis uses `config/quality_gates.yaml` for thresholds and rules. Key settings:

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
