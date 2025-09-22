from __future__ import annotations

import argparse
import os
import time

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation
from traffic_sim.core.profiling import get_profiler, run_with_cprofile


def run_steps(sim: Simulation, steps: int, dt: float) -> None:
    for _ in range(steps):
        sim.step(dt)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run simulation with profiler and dump CSV stats.")
    parser.add_argument("--steps", type=int, default=1000, help="Number of steps to run")
    parser.add_argument("--dt", type=float, default=0.02, help="Delta time per step (s)")
    parser.add_argument("--csv", type=str, default="profiling_stats.csv", help="CSV output path")
    parser.add_argument(
        "--cprofile", action="store_true", help="Also run cProfile and print top functions"
    )
    args = parser.parse_args(argv)

    cfg = load_config()
    cfg.setdefault("profiling", {})
    cfg["profiling"]["enabled"] = True

    sim = Simulation(cfg)

    profiler = get_profiler(reset=True)

    start = time.perf_counter()
    if args.cprofile:
        # Run under cProfile once
        stats_text = run_with_cprofile(run_steps, sim, args.steps, args.dt)
        print("\n=== cProfile (top) ===\n")
        print(stats_text)
    else:
        run_steps(sim, args.steps, args.dt)
    elapsed = time.perf_counter() - start

    # Dump CSV
    profiler.dump_csv(args.csv)
    print(f"Wrote profiler CSV: {os.path.abspath(args.csv)}")
    print(f"Elapsed: {elapsed:.3f}s for {args.steps} steps ({args.steps/elapsed:.1f} steps/s)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
