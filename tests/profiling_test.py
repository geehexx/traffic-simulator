"""Tests for profiling test."""

from __future__ import annotations


"""Tests for profiling test."""

import pytest


import time

from traffic_sim.core.profiling import PerformanceProfiler, get_profiler


def test_profile_function_and_time_block():
    profiler = PerformanceProfiler()

    def work(x: int) -> int:
        total = 0
        for i in range(x):
            total += i
        return total

    # profile_function
    result = profiler.profile_function(work, 1000)
    assert result == sum(range(1000))

    stats = profiler.get_stats()
    assert "work" in stats
    assert stats["work"]["count"] == 1
    assert stats["work"]["total_s"] >= 0.0

    # time_block
    with profiler.time_block("sleep_short"):
        time.sleep(0.001)

    stats = profiler.get_stats()
    assert "sleep_short" in stats
    assert stats["sleep_short"]["count"] == 1
    assert stats["sleep_short"]["total_s"] >= 0.0


def test_memory_snapshot():
    profiler = get_profiler(reset=True)
    snap1 = profiler.take_memory_snapshot("before")
    # allocate some memory
    data = [bytearray(1024) for _ in range(100)]  # 100 KB
    # Access first byte to ensure allocation is used
    assert data[0][0] == 0
    snap2 = profiler.take_memory_snapshot("after")

    assert snap1.label == "before"
    assert snap2.label == "after"
    # Peak should be non-decreasing and positive
    assert snap2.peak_bytes >= snap1.peak_bytes
    assert snap2.peak_bytes > 0


if __name__ == "__main__":
    pytest.main([__file__])
