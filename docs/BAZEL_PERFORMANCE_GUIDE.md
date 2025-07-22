# Bazel Performance Optimization Guide

## Overview

This guide provides comprehensive strategies for optimizing Bazel build performance in the traffic simulator project. The optimizations are designed to reduce build times, especially for full rebuilds.

## Quick Start

### Basic Performance Commands

```bash
# Fast build (recommended for development)
bazel build //... --config=fast

# Build with local disk cache
bazel build //... --config=cache

# Debug slow builds
bazel build //... --config=debug

# Profile build performance
bazel run //scripts:bazel_performance_monitor -- --target=//...
```

### Performance Monitoring

```bash
# Run full performance analysis
bazel run //scripts:bazel_performance_monitor

# Benchmark different configurations
bazel run //scripts:bazel_performance_monitor -- --benchmark-only

# Profile specific target
bazel run //scripts:bazel_performance_monitor -- --target=//src/traffic_sim:traffic_sim --profile-only
```

## Configuration Profiles

### 1. Fast Profile (`--config=fast`)
- **Jobs**: 16 (increased parallelism)
- **Memory**: 8GB heap
- **Optimizations**: UI deduplication, minimal output

```bash
bazel build //... --config=fast
```

### 2. Cache Profile (`--config=cache`)
- **Local Disk Cache**: `~/.cache/bazel-disk-cache`
- **Remote Downloads**: Top-level only
- **Benefits**: Faster incremental builds

```bash
bazel build //... --config=cache
```

### 3. Debug Profile (`--config=debug`)
- **Verbose Output**: Shows subcommands
- **Failure Details**: Detailed error messages
- **Use Case**: Troubleshooting slow builds

```bash
bazel build //... --config=debug
```

## Memory Optimizations

### JVM Settings
The optimized `.bazelrc` includes:
- **Heap Size**: 4GB (8GB for fast profile)
- **Garbage Collector**: G1GC for better performance
- **String Deduplication**: Reduces memory usage

### Memory Monitoring
```bash
# Monitor memory usage during builds
bazel build //... --config=debug --subcommands | grep -i memory
```

## Remote Caching Setup

### Local Disk Cache (Immediate)
```bash
# Enable local disk cache
bazel build //... --config=cache
```

### Remote Cache (Advanced)
1. **BuildBuddy** (Free tier available):
   ```bash
   # Uncomment in .bazelrc.remote
   bazel build //... --remote_cache=grpc://remote.buildbuddy.io
   ```

2. **Custom Remote Cache**:
   ```bash
   # Configure in .bazelrc.remote
   bazel build //... --remote_cache=grpc://your-cache-server:8080
   ```

## Build Optimization Strategies

### 1. Target Granularity
- **Fine-grained targets**: Better parallelization
- **Explicit dependencies**: Avoid unnecessary rebuilds
- **Modular structure**: Separate core, render, models

### 2. Dependency Optimization
```python
# Good: Explicit dependencies
py_library(
    name = "core",
    srcs = ["simulation.py", "vehicle.py"],
    deps = ["//src/traffic_sim/models:models"],
)

# Avoid: Glob patterns that include unnecessary files
py_library(
    name = "core",
    srcs = glob(["**/*.py"]),  # Too broad
)
```

### 3. Incremental Builds
```bash
# Use incremental builds when possible
bazel build //src/traffic_sim/core:core

# Avoid clean builds unless necessary
# bazel clean  # Only when needed
```

## Performance Monitoring

### 1. Build Profiling
```bash
# Generate build profile
bazel build //... --profile=build_profile.json

# Analyze profile
bazel run //scripts:bazel_performance_monitor -- --profile-only
```

### 2. Performance Reports
The performance monitor generates reports in `runs/bazel_performance/`:
- **Build time comparisons**
- **Phase analysis**
- **Slowest actions**
- **Optimization recommendations**

### 3. Continuous Monitoring
```bash
# Add to CI/CD pipeline
bazel run //scripts:bazel_performance_monitor -- --benchmark-only
```

## Troubleshooting Slow Builds

### 1. Identify Bottlenecks
```bash
# Debug build with subcommands
bazel build //... --config=debug

# Profile specific phases
bazel build //... --profile=profile.json --experimental_profile_include_target_label
```

### 2. Common Issues
- **Analysis phase slow**: Check for circular dependencies
- **Action phase slow**: Consider remote execution
- **Memory issues**: Increase heap size or reduce parallelism

### 3. Optimization Checklist
- [ ] Use `--config=fast` for development
- [ ] Enable local disk cache with `--config=cache`
- [ ] Check for unnecessary dependencies
- [ ] Use incremental builds when possible
- [ ] Monitor memory usage
- [ ] Profile slow builds

## Advanced Optimizations

### 1. Remote Execution
For large teams or CI/CD:
```bash
# Configure remote execution
bazel build //... --remote_executor=grpc://your-executor:8080
```

### 2. Persistent Workers
For repeated actions:
```bash
# Enable persistent workers (automatic in Bazel 7.1.1)
bazel build //... --experimental_persistent_javac
```

### 3. Build Without the Bytes
```bash
# Skip downloading intermediate files
bazel build //... --remote_download_minimal
```

## Performance Targets

### Development Workflow
- **Incremental builds**: < 10 seconds
- **Full rebuilds**: < 2 minutes
- **Test runs**: < 30 seconds

### CI/CD Pipeline
- **Clean builds**: < 5 minutes
- **Test suite**: < 2 minutes
- **Quality checks**: < 1 minute

## Monitoring and Alerts

### 1. Performance Regression Detection
```bash
# Compare build times
bazel run //scripts:bazel_performance_monitor -- --benchmark-only
```

### 2. Memory Usage Monitoring
```bash
# Check memory usage
bazel build //... --config=debug | grep -i memory
```

### 3. Build Time Tracking
The performance monitor tracks:
- Build time trends
- Phase breakdowns
- Action durations
- Memory usage patterns

## Best Practices

### 1. Development
- Use `--config=fast` for daily development
- Enable local disk cache
- Avoid clean builds unless necessary
- Profile slow builds regularly

### 2. CI/CD
- Use remote caching when available
- Enable parallel execution
- Monitor build times
- Set up performance regression alerts

### 3. Team Collaboration
- Share cache configurations
- Document performance optimizations
- Regular performance reviews
- Update optimization strategies

## Configuration Files

### `.bazelrc` (Main Configuration)
- Common settings for all builds
- Performance profiles
- Memory optimizations

### `.bazelrc.remote` (Remote Caching)
- Remote cache configuration
- Authentication settings
- Remote execution setup

### `scripts/bazel_performance_monitor.py`
- Performance monitoring tool
- Build profiling
- Optimization recommendations

## Troubleshooting

### Common Issues
1. **Out of memory**: Increase heap size or reduce jobs
2. **Slow analysis**: Check for circular dependencies
3. **Cache misses**: Verify cache configuration
4. **Remote failures**: Check network and authentication

### Debug Commands
```bash
# Verbose build output
bazel build //... --config=debug

# Memory usage
bazel build //... --host_jvm_args=-XX:+PrintGCDetails

# Profile analysis
bazel run //scripts:bazel_performance_monitor -- --profile-only
```

## Performance Metrics

### Key Metrics to Track
- **Build time**: Total build duration
- **Analysis time**: Dependency analysis phase
- **Action time**: Compilation and execution phase
- **Memory usage**: Peak memory consumption
- **Cache hit rate**: Percentage of cached actions

### Target Performance
- **Development builds**: < 30 seconds
- **CI builds**: < 5 minutes
- **Full rebuilds**: < 2 minutes
- **Memory usage**: < 4GB peak

## Conclusion

These optimizations should significantly improve your Bazel build performance. Start with the basic profiles (`--config=fast`, `--config=cache`) and gradually implement advanced features like remote caching as needed.

For ongoing performance monitoring, use the performance monitoring script regularly to track improvements and identify new optimization opportunities.
