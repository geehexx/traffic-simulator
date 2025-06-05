#!/usr/bin/env python3
"""
Scale benchmark script for traffic simulator performance testing.

Tests performance at various vehicle counts and speed factors to identify
bottlenecks and validate optimization effectiveness.
"""

from __future__ import annotations

import argparse
import csv
import time
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation


def run_scale_benchmark(
    vehicle_counts: list[int],
    speed_factors: list[float],
    steps: int = 1000,
    dt: float = 0.02,
    output_csv: str = "scale_benchmark.csv",
) -> None:
    """Run comprehensive scale benchmarks."""
    
    results = []
    
    print("=== Traffic Simulator Scale Benchmark ===")
    print(f"Testing {len(vehicle_counts)} vehicle counts × {len(speed_factors)} speed factors")
    print(f"Steps per test: {steps}, dt: {dt}")
    print()
    
    for vehicle_count in vehicle_counts:
        for speed_factor in speed_factors:
            print(f"Testing {vehicle_count} vehicles at {speed_factor}x speed...", end=" ")
            
            # Load base config
            config = load_config()
            
            # Override vehicle count and speed factor
            config["vehicles"]["count"] = vehicle_count
            config["physics"]["speed_factor"] = speed_factor
            
            # Create simulation
            sim = Simulation(config)
            
            # Warmup (let simulation stabilize)
            for _ in range(100):
                sim.step(dt)
            
            # Benchmark
            start_time = time.perf_counter()
            for _ in range(steps):
                sim.step(dt)
            end_time = time.perf_counter()
            
            elapsed = end_time - start_time
            steps_per_second = steps / elapsed
            vehicles_per_second = (vehicle_count * steps) / elapsed
            
            print(f"{steps_per_second:.1f} steps/s ({vehicles_per_second:.0f} v·s/s)")
            
            results.append({
                "vehicles": vehicle_count,
                "speed_factor": speed_factor,
                "steps": steps,
                "dt": dt,
                "elapsed_s": elapsed,
                "steps_per_second": steps_per_second,
                "vehicles_per_second": vehicles_per_second,
                "efficiency": vehicles_per_second / vehicle_count,  # v·s/s per vehicle
            })
    
    # Write results to CSV
    with open(output_csv, "w", newline="") as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    print(f"\nResults written to {output_csv}")
    
    # Print summary
    print("\n=== Performance Summary ===")
    print("Vehicles | Speed | Steps/s | V·S/s | Efficiency")
    print("---------|-------|---------|-------|-----------")
    for result in results:
        print(f"{result['vehicles']:8d} | {result['speed_factor']:5.1f} | "
              f"{result['steps_per_second']:7.1f} | {result['vehicles_per_second']:5.0f} | "
              f"{result['efficiency']:10.2f}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Scale benchmark for traffic simulator")
    parser.add_argument("--vehicle-counts", nargs="+", type=int, 
                       default=[20, 50, 100, 200, 500, 1000],
                       help="Vehicle counts to test")
    parser.add_argument("--speed-factors", nargs="+", type=float,
                       default=[1.0, 10.0, 100.0, 1000.0],
                       help="Speed factors to test")
    parser.add_argument("--steps", type=int, default=1000,
                       help="Number of simulation steps per test")
    parser.add_argument("--dt", type=float, default=0.02,
                       help="Simulation timestep")
    parser.add_argument("--output", default="scale_benchmark.csv",
                       help="Output CSV file")
    
    args = parser.parse_args()
    
    run_scale_benchmark(
        vehicle_counts=args.vehicle_counts,
        speed_factors=args.speed_factors,
        steps=args.steps,
        dt=args.dt,
        output_csv=args.output,
    )


if __name__ == "__main__":
    main()
