# AGENTS.md

## Standards Summary Table
| Area                | Section                        | Checklist/Validation |
|---------------------|--------------------------------|----------------------|
| Project Context     | Core Principles, Components    | See below            |
| Code Quality        | Code Quality Standards         | ✓                    |
| Configuration       | Configuration Patterns         | ✓                    |
| Documentation       | Documentation Patterns         | ✓                    |
| Performance         | Performance & Rendering        | ✓                    |
| Arcade API          | Arcade API Consistency         | ✓                    |
| Simulation          | Simulation Patterns            | ✓                    |
| Vehicle Physics     | Vehicle Physics Patterns       | ✓                    |
| Rule Generation     | Rule Generation Standard       | ✓                    |

---

## Project Context and Core Principles

**Deterministic Simulation:**
	- Use fixed-step physics and seeded random number generators for reproducibility.
	- *Why:* Ensures consistent results and debuggability.

**Performance Target:**
	- 30+ FPS with 20+ vehicles.
	- *How to Validate:* Run performance tests (see below).

**Reference:**
	- [Quality Standards](docs/QUALITY_STANDARDS.md)
	- [Architecture Guide](docs/ARCHITECTURE.md)

## Key Components

- **Simulation:** `src/traffic_sim/core/simulation.py` — Main simulation engine.
- **Drivers:** `src/traffic_sim/core/driver.py` — Driver logic and behavior.
- **Vehicles:** `src/traffic_sim/core/vehicle.py` — Vehicle models and physics.
- **Rendering:** `src/traffic_sim/render/app.py` — Arcade-based visualization.
- **Configuration:** `config/` — YAML config files.
- **Tests:** `tests/` — Test suite.
- **Documentation:** `docs/` — Guides and references.
- **NumPy Physics Engine:** `src/traffic_sim/core/physics_numpy.py` — High-performance, vectorized physics engine (Phase 3+).
- **Spatial Hash/Grid:** `src/traffic_sim/core/spatial_hash.py` — Broadphase collision detection utility for large-scale simulation.

---

## Streamlined Hybrid Architecture

The project uses a **streamlined hybrid approach** optimized for efficiency:

### Bazel Commands (Primary - 95% of workflow)
- **Building**: `bazel build //...` - Build all targets
- **Quality Checks**: `bazel build //...` - Integrated quality gates
- **CI/CD**: All automated processes use Bazel
- **Core Logic**: All simulation logic runs via Bazel

### Virtual Environment (Development Only - 5% of workflow)
- **Testing**: `uv run python -m pytest tests/` - Run tests with external dependencies
- **Scripts**: `uv run python scripts/benchmarking_framework.py` - Run scripts with dependencies
- **Development**: Only when external dependencies (numpy, arcade, pymunk) are needed

### Task Commands (Convenience Layer)
- **Quality**: `task quality` - Quality gates via Bazel
- **Performance**: `task performance` - Benchmarking via virtual environment
- **Testing**: `task test` - Testing via virtual environment

### Command Selection Guidelines
- **Use Bazel** for: Building, quality checks, CI/CD, core simulation logic
- **Use Virtual Environment** for: Development, testing, scripts with external dependencies
- **Use Task Commands** for: Convenience and automation

### Efficiency Benefits
- **95% Bazel**: All core functionality uses Bazel efficiently
- **5% Virtual Environment**: Only for external dependencies
- **Simplified**: No complex dependency management in Bazel
- **Fast**: Bazel handles most operations efficiently
- **Maintainable**: Clear separation of concerns

---

## Code Quality Standards

**Do:**
- Use `from __future__ import annotations` for type safety.
- Organize imports: standard library, third-party, local.
- Handle errors with specific exceptions and context.
- Enforce code style: max 100 chars/line, functions <50 lines, classes <200 lines.
- Use Google-style docstrings for public APIs.
- Use Pyright, Ruff, Bandit, Radon for quality gates.

**Don't:**
- Ignore linter/type errors.
- Use generic exceptions (e.g., `except Exception`).

**How to Validate:**
- Run `task quality` for quality gates via Bazel.
- Check with all listed tools.

**Example:**
```python
from __future__ import annotations

def foo(x: int) -> int:
		"""Adds one to x."""
		return x + 1
```

**Reference:** [Quality Standards Guide](docs/QUALITY_STANDARDS.md)

---

## Configuration Patterns

**Do:**
- Use YAML for configs, validated on load.
- Support `TRAFFIC_SIM_CONFIG` env var for custom config path.
- Document and validate config keys (e.g., HUD occlusion).
- Provide clear error messages for invalid config.

**How to Validate:**
- Check config loading and validation logic.
- Test with invalid and custom config paths.

**Example:**
```yaml
hud_occlusion: true
```

**Reference:** [Development Guide: Configuration](docs/DEVELOPMENT.md#configuration-management)
**Cursor Indexing:** [Cursor Rules Guide: Strategic Indexing](docs/CURSOR_RULES.md#strategic-indexing-configuration)

---

## Documentation Patterns

**Do:**
- Use clear markdown structure, headings, and code examples.
- Use Google-style docstrings for public APIs.
- Keep documentation in sync with codebase.

**How to Validate:**
- Review docs for structure and up-to-date content.
- Check for Google-style docstrings in code.

**Example:**
```python
def bar(y: float) -> float:
		"""Multiply y by 2.
		Args:
				y (float): Input value.
		Returns:
				float: Doubled value.
		"""
		return y * 2
```

**Reference:** [Quality Standards: Documentation](docs/QUALITY_STANDARDS.md#documentation-standards)

---

## Performance & Rendering Standards

**Performance:**
- Target 30+ FPS with 20+ vehicles, minimal allocations.
- Use fixed timestep, vectorized operations, object pooling, spatial partitioning.
- Automated performance tests and analytics optimizations.

**Rendering:**
- Use valid Arcade APIs, text batching, and minimal allocations.
- Separate simulation and rendering state.
- HUD: minimal/full modes, occlusion-aware, performance targets.
- Avoid per-frame recomputation of expensive metrics in render loop.

**How to Validate:**
- Run performance and rendering integration tests.
- Profile allocations and frame rate.

**Checklist:**
- [ ] 30+ FPS with 20+ vehicles
- [ ] Minimal per-frame allocations
- [ ] No per-frame recomputation of expensive metrics

**Reference:** [Performance Guide](docs/PERFORMANCE_GUIDE.md)

---

## Arcade API Consistency

**Do:**
- Only use valid Arcade functions (e.g., `draw_lrbt_rectangle_filled`).
- Maintain type stubs in sync with Arcade version.
- Test documentation and integration for function existence.

**Don't:**
- Use deprecated or non-existent Arcade functions.

**How to Validate:**
- Verify function exists: `hasattr(arcade, 'function_name')`
- Check function signature: `inspect.signature(arcade.function_name)`

**Checklist:**
- [ ] All Arcade calls are valid and tested
- [ ] Type stubs match installed Arcade version

**Reference:** [Arcade 3.3.2 Documentation](https://arcade.academy/)

---

## Simulation Patterns

**Do:**
- Use immutable state objects where possible.
- Use fixed timestep, vectorized operations.
- Follow design patterns: IDM controller, perception, analytics, collision, logging.

**How to Validate:**
- Review for immutable state and vectorized ops.
- Check for correct use of design patterns.

**Reference:** [Architecture Guide: Core Components](docs/ARCHITECTURE.md#core-components)

---

## Vehicle Physics Patterns

**Do:**
- Use dataclasses for vehicle specs with physics attributes.
- Implement physics formulas for acceleration, drag, constraints.
- Cache expensive calculations, define realistic values per vehicle type.
- For large-scale simulation, prefer vectorized NumPy-based physics (see `physics_numpy.py`).
- Use spatial hash/grid for broadphase collision checks (see `spatial_hash.py`).
- Integrate Numba JIT for critical routines if available.
- Gate new engine with `physics.numpy_engine_enabled` config flag for safe rollout.

**How to Validate:**
- Check for dataclass usage and correct formulas.
- Review caching and catalog entries.
- Ensure NumPy engine is tested, benchmarked, and gated by config.

**Example:**
```python
@dataclass
class VehicleSpec:
		power_kw: float
		drag_area_cda: float
		# ...
```

**NumPy Physics Engine Example:**
```python
from traffic_sim.core.physics_numpy import PhysicsEngineNumpy
engine = PhysicsEngineNumpy(vehicle_specs, initial_state)
state = engine.step(actions, dt)
```

**Reference:** [VehicleSpec](src/traffic_sim/core/vehicle.py#L1)

---

## Rule Generation Standard

**Do:**
- Write rules that are clear, concise, maintainable, and context-relevant.
- Use actionable examples, references, and modular structure.

**How to Validate:**
- Review for clarity, actionability, and modularity.

**Reference:** [Rule Generation Standard](.cursor/rules/rule-generation-standard.mdc)

---

## How to Update This File

1. Review all standards and update as project evolves.
2. Link to new documentation or code sections as needed.
3. Keep checklists and examples current.
4. Confirm with team before major changes.
5. For new engine/optimization phases, document config flags, test/benchmark requirements, and integration points.

---

### Migration Note
These rules were migrated from `.cursor/rules/*.mdc` files used in Cursor. They are now consolidated for Copilot agent context. Some automated enforcement features may not be available, but these serve as strong guidance for code generation and review.
