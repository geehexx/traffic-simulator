# Traffic Simulator

A 2D Python traffic simulation using `arcade` + `pymunk`, with statistically realistic driver behavior, dynamic safety analytics, and a scalable renderer. This project targets deterministic physics with an optional 10× speed factor and live HUD analytics.

## Table of Contents
- Overview
- Features
- Installation (uv)
- Usage
- Configuration
- Development
- Testing & CI
- Contributing
- License

## Overview
Vehicles circulate on a stadium-shaped track whose total length is configurable. Drivers are sampled from bell-curve distributions (reaction time, headway, aggression, rule adherence) with sensible bounds and correlations. A safety panel computes minimum safe curve radius and safe speeds based on standard highway-style formulas (AASHTO-aligned via TxDOT). The renderer scales to the window and maintains at least 30 FPS.

## Features
- Stadium track from total length; dynamic safe-speed/length analytics and warning string
- 20 vehicles (default) with random colors; configurable mix by type
- Parametric driver behavior; occlusion-based perception and dynamic stopping sight distance (SSD)
- Deterministic fixed-step physics; speed factor up to 10×
- Basic collisions with lateral push and temporary disable
- HUD: speed/headway/TTC summaries, incident log, safe-curve panel

## Installation (uv)
Requires Python 3.10+ and `uv`.

```bash
# Install uv (see docs: https://docs.astral.sh/uv/)
# Example via pipx:
pipx install uv

# From project root, create/sync environment with dev extras
uv sync --extra dev
```

## Usage
```bash
# Run the simulator
uv run python -m traffic_sim

# List available tasks (requires Taskfile)
task -l
```

### Controls
- H: Toggle full HUD info.

### Troubleshooting
- On WSL2/Linux you may see PipeWire/ALSA warnings; visuals still work.
- Arcade 3.3.x: we draw vehicles using `draw_polygon_filled` for rotation support; a performance warning about `draw_text` is expected until HUD is migrated to Text objects.

## Configuration
Edit `config/config.yaml` to adjust:
- Track: `length_m`, `straight_fraction`, `superelevation_e`, `side_friction_f`, `safety_design_speed_kmh`, `speed_limit_kmh`
- Vehicles: `count`, `mix`, `color_random_seed`
- Drivers: distribution parameters, correlations, overspeed model
- Physics/render: `delta_t_s`, `speed_factor`, `target_fps`, HUD toggles

Override the config path via environment variable:

```bash
export TRAFFIC_SIM_CONFIG=/absolute/path/to/config.yaml
```

## Development
We use `uv` and Taskfile to streamline workflows.

```bash
# Ensure dev environment and hooks
uv sync --extra dev
uv run pre-commit install

# Lint & format
uv run ruff check src tests
uv run black --check src tests

# Run
uv run python -m traffic_sim
```

Tasks (Taskfile):
- `task setup` — `uv sync --extra dev`
- `task test` — run pytest with coverage
- `task run` — start the simulator
- `task lint` / `task format` — static checks / formatting
- `task precommit:run` — run hooks on all files

## Testing & CI
- Tests use `pytest` and Hypothesis; coverage via `pytest-cov`.
- CI runs via GitHub Actions across OSes (Ubuntu, macOS, Windows) and Python 3.10/3.11, using uv for dependency management.

```bash
uv run python -m pytest --cov=traffic_sim --cov-report=term-missing
```

## Contributing
- Use feature branches and open PRs. Include tests and keep changes focused.
- Run `uv run pre-commit run --all-files` before committing.

## License
This project is licensed under the terms in `LICENSE`.
