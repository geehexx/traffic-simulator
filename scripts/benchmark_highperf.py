from __future__ import annotations

import argparse
import statistics
import time

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation


def run_benchmark(vehicles: int, steps: int, dt: float, speed_factor: float) -> dict[str, float]:
    cfg = load_config().copy()
    cfg.setdefault("vehicles", {})
    cfg["vehicles"]["count"] = vehicles
    cfg.setdefault("physics", {})
    cfg["physics"]["speed_factor"] = speed_factor
    cfg.setdefault("data_manager", {})
    cfg["data_manager"]["enabled"] = True
    cfg.setdefault("high_performance", {})
    cfg["high_performance"]["enabled"] = True
    cfg["high_performance"]["idm_vectorized"] = True

    sim = Simulation(cfg)

    frame_times = []
    start = time.perf_counter()
    for _ in range(steps):
        f0 = time.perf_counter()
        sim.step(dt)
        frame_times.append(time.perf_counter() - f0)
    total = time.perf_counter() - start

    fps_equiv = steps / total / (1.0 / dt)
    return {
        "vehicles": float(vehicles),
        "steps": float(steps),
        "dt": dt,
        "speed_factor": speed_factor,
        "total_s": total,
        "fps_equiv": fps_equiv,
        "avg_frame_ms": statistics.mean(frame_times) * 1000.0,
        "p95_frame_ms": (
            statistics.quantiles(frame_times, n=20)[18] * 1000.0
            if len(frame_times) > 19
            else statistics.mean(frame_times) * 1000.0
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="High-performance benchmark")
    parser.add_argument("--vehicles", type=int, default=100)
    parser.add_argument("--steps", type=int, default=1000)
    parser.add_argument("--dt", type=float, default=0.02)
    parser.add_argument("--speed-factor", type=float, default=10.0)
    args = parser.parse_args(argv)

    stats = run_benchmark(args.vehicles, args.steps, args.dt, args.speed_factor)
    print(
        f"vehicles={int(stats['vehicles'])} steps={int(stats['steps'])} dt={stats['dt']:.3f} "
        f"sf={stats['speed_factor']:.1f} total={stats['total_s']:.3f}s fps_eq={stats['fps_equiv']:.1f} "
        f"avg={stats['avg_frame_ms']:.3f}ms p95={stats['p95_frame_ms']:.3f}ms"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
