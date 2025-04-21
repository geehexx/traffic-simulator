# Development Notes (Checkpoint)

This document captures context at the current working checkpoint to aid future contributors.

## Current state
- Rendering: Stadium track (both arcs), vehicles as rotated rectangles aligned with motion.
- Input: H toggles extra HUD line; safety panel shows R, V_safe, L_needed and warning.
- Dynamics: Basic single-lane IDM-like control; single-vehicle uniform motion.
- Config: YAML at `config/config.yaml` (override via `TRAFFIC_SIM_CONFIG`).
- Tooling: uv + Taskfile; pre-commit (ruff, black); CI (GitHub Actions) with coverage.
- Tests: geometry/safety/determinism/IDM braking pass.

## Known constraints
- Using Arcade 3.3.x; rotated rectangles drawn via `draw_polygon_filled` for compatibility.
- Text rendering uses `draw_text`; migrate to `Text` objects for performance in future.

## Next tasks (summary)
1. Replace scaffold constants with per-driver parameters (T, b_comf, v0) and add jerk/lag clamps.
2. Implement occlusion-based perception and dynamic SSD; integrate into braking.
3. Add live HUD (speed histogram, headway, near-miss counter) with efficient updates.
4. Optional crash visualization stub (lateral shove + temporary disable).

## How to run
```bash
uv sync --extra dev
uv run python -m traffic_sim
```

## Tests
```bash
uv run python -m pytest --cov=traffic_sim --cov-report=term-missing
```
