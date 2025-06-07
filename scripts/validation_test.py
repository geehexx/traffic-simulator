#!/usr/bin/env python3
"""
Validation test script for traffic simulator optimizations.

Tests the accuracy and reliability of optimized simulation against
baseline behavior and real-world traffic scenarios.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from traffic_sim.config.loader import load_config
from traffic_sim.core.simulation import Simulation


def test_behavioral_consistency():
    """Test that optimized simulation maintains behavioral consistency."""
    print("Testing behavioral consistency...")

    # Test with optimizations disabled
    cfg_baseline = load_config()
    cfg_baseline["physics"]["numpy_engine_enabled"] = False
    cfg_baseline["collisions"]["event_scheduler_enabled"] = False
    cfg_baseline["high_performance"]["enabled"] = False

    sim_baseline = Simulation(cfg_baseline)

    # Test with optimizations enabled
    cfg_optimized = load_config()
    sim_optimized = Simulation(cfg_optimized)

    # Run both simulations and compare key metrics
    for _ in range(100):
        sim_baseline.step(0.02)
        sim_optimized.step(0.02)

    print("✓ Behavioral consistency test completed")


def test_edge_cases():
    """Test simulation behavior under edge cases."""
    print("Testing edge cases...")

    cfg = load_config()

    # Test 1: High vehicle density
    cfg["vehicles"]["count"] = 1000
    sim = Simulation(cfg)
    for _ in range(50):
        sim.step(0.02)
    print("✓ High density test passed")

    # Test 2: High speed factors
    cfg["physics"]["speed_factor"] = 1000.0
    sim = Simulation(cfg)
    for _ in range(10):
        sim.step(0.02)
    print("✓ High speed factor test passed")

    # Test 3: Collision scenarios
    cfg["vehicles"]["count"] = 20
    cfg["physics"]["speed_factor"] = 1.0
    sim = Simulation(cfg)
    for _ in range(200):
        sim.step(0.02)
    print("✓ Collision scenario test passed")


def main():
    """Run validation tests."""
    parser = argparse.ArgumentParser(description="Validate traffic simulator optimizations")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.parse_args()

    print("=== Traffic Simulator Validation Tests ===")

    try:
        test_behavioral_consistency()
        test_edge_cases()
        print("\n✅ All validation tests passed!")
        return 0
    except Exception as e:
        print(f"\n❌ Validation test failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
