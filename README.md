# 🚗 Traffic Simulator - Advanced 2D Traffic Simulation Platform

<div align="center">

![Traffic Simulator](https://img.shields.io/badge/Traffic-Simulator-blue?style=for-the-badge&logo=python)
![Python](https://img.shields.io/badge/Python-3.12+-green?style=for-the-badge&logo=python)
![Bazel](https://img.shields.io/badge/Build-Bazel-orange?style=for-the-badge&logo=bazel)
![Performance](https://img.shields.io/badge/Performance-30%2B%20FPS-brightgreen?style=for-the-badge)

**A cutting-edge 2D traffic simulation platform featuring advanced physics, AI-driven optimization, and enterprise-grade performance.**

</div>

## 🌟 **Exciting Features**

### 🚀 **Advanced Build System & Performance**
- **Bazel 7.1.1+ Integration**: Lightning-fast builds with integrated quality gates
- **Hybrid Architecture**: 95% Bazel + 5% Virtual Environment for optimal efficiency
- **Performance Targets**: 30+ FPS with 20+ vehicles, scales to 1000+ vehicles
- **Vectorized Physics**: NumPy-based calculations with optional Numba JIT compilation
- **Event-Driven Collision Detection**: O(n) collision checks with predictive scheduling

### 🧠 **AI-Powered Optimization**
- **DSPy Integration**: Real-time prompt optimization using MIPROv2 and BootstrapFewShot
- **MCP Server**: Model Context Protocol server with 6 optimization tools
- **Auto-Optimization**: Continuous improvement based on user feedback
- **Performance Analytics**: Real-time optimization tracking and metrics

### 🔬 **Advanced Physics & Simulation**
- **Intelligent Driver Model (IDM)**: Statistically realistic driver behavior with correlations
- **Gaussian Copula Sampling**: Realistic parameter distributions with correlations
- **Occlusion-Based Perception**: Dynamic visibility and SSD calculations
- **Pymunk Physics**: Realistic collision detection with lateral push effects
- **Adaptive Time Stepping**: Dynamic timestep scaling for high-speed factors

### 📊 **Enterprise-Grade Analytics**
- **Live HUD Analytics**: Real-time speed histograms, headway distributions, near-miss counters
- **Safety Analytics**: AASHTO/TxDOT-style curve speed calculations
- **Performance Monitoring**: Comprehensive metrics and incident tracking
- **Data Export**: CSV export with detailed simulation data
- **Unified Benchmarking**: Parallel execution with real-time estimation

### 🛠 **Developer Experience**
- **Comprehensive Testing**: Unit, integration, and performance tests
- **Quality Gates**: Pyright, Ruff, Bandit, Radon integration
- **Documentation**: Extensive guides and architecture documentation
- **Task Commands**: `task quality`, `task performance`, `task test`
- **Hot Reloading**: Development-friendly configuration management

## 🚀 **Quick Start**

### Prerequisites
- Python 3.12+
- Bazel 7.1.1+
- Git

### Installation & Running

```bash
# Clone the repository
git clone <repository-url>
cd traffic-simulator

# Run the simulator (Bazel - Primary)
bazel run //src/traffic_sim:traffic_sim_bin

# Run tests
bazel test //...

# Build all targets with quality gates
bazel build //...
```

### Development Commands

```bash
# Quality analysis
task quality              # Quality gates
task quality:monitor      # Detailed monitoring
task quality:analyze     # Comprehensive analysis

# Performance analysis
task performance          # Performance benchmark
task performance:scale    # Scale testing (20-1000+ vehicles)
task performance:monitor  # Real-time monitoring

# Testing
task test                 # Run all tests
task validate            # Validation testing
```

## 🎮 **Controls & Features**

### Interactive Controls
- **H**: Toggle between minimal and full HUD
- **ESC**: Exit simulator
- **Speed Factor**: Up to 10× simulation speed

### HUD Modes
- **Minimal**: Safety panel, perception summary, live analytics
- **Full**: Detailed vehicle overlays, perception heatmap, incident log, performance metrics

## ⚙️ **Configuration**

The simulator uses YAML configuration with comprehensive validation:

```yaml
# Track Configuration
track:
  length_m: 1000
  straight_fraction: 0.30
  speed_limit_kmh: 100
  safety_design_speed_kmh: 120

# Vehicle Mix
vehicles:
  count: 20
  mix:
    sedan: 0.55
    suv: 0.25
    truck_van: 0.10
    bus: 0.05
    motorbike: 0.05

# Driver Behavior (Statistical)
drivers:
  distributions:
    reaction_time_s: {mean: 2.5, std: 0.6, min: 0.8, max: 4.0}
    headway_T_s: {mean: 1.6, std: 0.5, min: 0.6, max: 3.0}
  correlations:
    A_T: -0.5        # Aggression vs Headway
    A_b_comf: 0.3    # Aggression vs Comfortable Deceleration
    R_A: -0.4        # Rule Adherence vs Aggression

# Performance Optimizations
performance:
  numpy_engine_enabled: true
  adaptive_timestep_enabled: true
  high_performance:
    enabled: true
    idm_vectorized: true
  collisions:
    event_scheduler_enabled: true
    event_horizon_s: 2.0
    guard_band_m: 5.0
```

## 🔧 **Advanced Features**

### 🧮 **Physics Engine**
- **Fixed Timestep**: Deterministic simulation with seeded RNGs
- **Vectorized Operations**: NumPy-based calculations for large datasets
- **Spatial Partitioning**: Efficient collision detection and neighbor finding
- **Object Pooling**: Memory-efficient object reuse
- **Event-Driven Collisions**: Predictive collision scheduling

### 🤖 **AI & Optimization**
- **DSPy Integration**: Real-time prompt optimization
- **MCP Server**: 6 optimization tools for continuous improvement
- **Auto-Optimization**: Threshold-based automatic prompt updates
- **Performance Tracking**: Complete optimization audit trail

### 📈 **Analytics & Monitoring**
- **Live Metrics**: Real-time performance monitoring
- **Safety Analytics**: AASHTO/TxDOT-style calculations
- **Incident Tracking**: Comprehensive collision and near-miss logging
- **Data Export**: CSV export with detailed simulation data
- **Benchmarking**: Unified framework with parallel execution

### 🏗️ **Build System**
- **Bazel Integration**: Lightning-fast builds with quality gates
- **Hybrid Architecture**: Optimal efficiency with minimal complexity
- **Quality Gates**: Integrated Pyright, Ruff, Bandit, Radon
- **Task Commands**: Unified interface for all operations

## 📊 **Performance Benchmarks**

### Current Performance
- **Baseline**: 30+ FPS with 20+ vehicles
- **Scalability**: 1000+ vehicles with linear CPU scaling
- **Memory**: Minimal runtime allocations
- **Build Time**: <2 minutes full rebuild, <30 seconds incremental

### Benchmarking Commands
```bash
# Single benchmark
bazel run //scripts:benchmarking_framework -- --mode=benchmark --vehicles 100 --steps 1000

# Scale testing
bazel run //scripts:benchmarking_framework -- --mode=scale --vehicle-counts 20 50 100 200

# Performance monitoring
bazel run //scripts:benchmarking_framework -- --mode=monitor --duration 5 --vehicles 100

# Advanced profiling
bazel run //scripts:benchmarking_framework -- --mode=profile --vehicles 100 --steps 1000
```

## 🧪 **Testing & Quality**

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end simulation testing
- **Deterministic Tests**: Reproducible behavior validation
- **Performance Tests**: 30+ FPS target verification

### Quality Gates
- **Type Safety**: Comprehensive type checking with Pyright
- **Code Quality**: Lint rules with Ruff
- **Security**: Security scanning with Bandit
- **Complexity**: Complexity analysis with Radon
- **Coverage**: ≥80% line coverage requirement

### Running Tests
```bash
# All tests
bazel test //...

# Specific test target
bazel test //tests:idm_test

# With verbose output
bazel test //... --test_output=all

# Run tests in parallel
bazel test //... --jobs=4
```

## 📚 **Documentation**

### Core Guides
- **[Architecture Guide](docs/ARCHITECTURE.md)**: System design and patterns
- **[Performance Guide](docs/PERFORMANCE_GUIDE.md)**: Optimization strategies
- **[Quality Standards](docs/QUALITY_STANDARDS.md)**: Code quality guidelines
- **[Benchmarking Guide](docs/BENCHMARKING_GUIDE.md)**: Performance testing
- **[Development Guide](docs/DEVELOPMENT.md)**: Development workflow

### Specialized Documentation
- **[MCP Integration](docs/MCP_INTEGRATION.md)**: Model Context Protocol setup
- **[Prompt Optimization](docs/PROMPT_OPTIMIZATION_GUIDE.md)**: DSPy integration
- **[Production System](docs/PRODUCTION_SYSTEM_GUIDE.md)**: Deployment guide

## 🚀 **Roadmap**

### Phase 4: Validation & Calibration (Current)
- ✅ Validation testing and edge case coverage
- ✅ Performance monitoring and baseline metrics
- ✅ Real-world calibration with traffic data

### Phase 5: Advanced Optimizations (Next)
- 🔄 GPU acceleration with CUDA integration
- 🔄 Multi-resolution modeling with LOD system
- 🔄 Distributed simulation architecture

### Phase 6: Production Readiness
- 📋 REST API development
- 📋 GraphQL integration
- 📋 Cloud deployment capabilities

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `bazel test //...`
6. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use comprehensive type hints
- Write comprehensive tests
- Document public APIs with Google-style docstrings

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 **Key Highlights**

- **🚀 Performance**: 30+ FPS with 20+ vehicles, scales to 1000+
- **🧠 AI-Powered**: DSPy integration with real-time optimization
- **⚡ Fast Builds**: Bazel integration with quality gates
- **🔬 Advanced Physics**: Vectorized calculations with event-driven collisions
- **📊 Rich Analytics**: Live HUD with comprehensive monitoring
- **🛠️ Developer-Friendly**: Extensive documentation and testing
- **🏗️ Enterprise-Ready**: Production-grade architecture and monitoring

---

<div align="center">

**Built with ❤️ for the traffic simulation community**

[![GitHub stars](https://img.shields.io/github/stars/your-repo/traffic-simulator?style=social)](https://github.com/your-repo/traffic-simulator)
[![GitHub forks](https://img.shields.io/github/forks/your-repo/traffic-simulator?style=social)](https://github.com/your-repo/traffic-simulator)
[![GitHub issues](https://img.shields.io/github/issues/your-repo/traffic-simulator)](https://github.com/your-repo/traffic-simulator/issues)

</div>
