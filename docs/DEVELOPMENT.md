# Development Notes (Checkpoint)

This document captures context at the current working checkpoint to aid future contributors.

## Current state
- Rendering: Stadium track (both arcs), vehicles as rotated rectangles aligned with motion.
- Input: H toggles extra HUD line; safety panel shows R, V_safe, L_needed and warning.
- Dynamics: Enhanced IDM with per-driver parameters, jerk limiting, drivetrain lag, and Markov chain speeding behavior.
- Config: YAML at `config/config.yaml` (override via `TRAFFIC_SIM_CONFIG`).
- Tooling: uv + Taskfile; pre-commit (ruff, black); CI (GitHub Actions) with coverage.
- Tests: geometry/safety/determinism/IDM braking pass, plus comprehensive per-driver parameter tests.

## Known constraints
- Using Arcade 3.3.x; rotated rectangles drawn via `draw_polygon_filled` for compatibility.
- Text rendering uses `draw_text`; migrate to `Text` objects for performance in future.

## Completed (Phase 1)
1. ✅ Enhanced driver parameter sampling with Gaussian copula correlation
2. ✅ Per-driver parameters (T, b_comf, v0, aggression, rule adherence) in IDM controller
3. ✅ Jerk limiting and drivetrain lag constraints for realistic vehicle dynamics
4. ✅ Two-state Markov chain for speeding behavior with configurable rates
5. ✅ Comprehensive test suite for all new features

## Next tasks (summary)
1. Implement occlusion-based perception and dynamic SSD; integrate into braking.
2. Add live HUD (speed histogram, headway, near-miss counter) with efficient updates.
3. Optional crash visualization stub (lateral shove + temporary disable).

## How to run
```bash
uv sync --extra dev
uv run python -m traffic_sim
```

## Tests
```bash
uv run python -m pytest --cov=traffic_sim --cov-report=term-missing
```
