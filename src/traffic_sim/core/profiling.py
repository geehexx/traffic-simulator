from __future__ import annotations

import time
import tracemalloc
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Callable, ContextManager, Type
from types import TracebackType
import csv
import io
import cProfile
import pstats


class _TimeBlock(ContextManager["_TimeBlock"]):
    """Context manager for timing named code blocks.

    Usage:
        with profiler.time_block("update_physics"):
            ...
    """

    def __init__(self, profiler: "PerformanceProfiler", name: str) -> None:
        self._profiler = profiler
        self._name = name
        self._start: float = 0.0

    def __enter__(self) -> "_TimeBlock":
        self._start = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> Optional[bool]:
        elapsed = time.perf_counter() - self._start
        self._profiler.record(self._name, elapsed)
        return None


@dataclass
class MemorySnapshot:
    label: str
    size_bytes: int
    peak_bytes: int


class MemoryTracker:
    """Lightweight memory tracker built on tracemalloc.

    - Start once per process; subsequent starts are no-ops.
    - Provides labeled snapshots for quick comparisons.
    """

    def __init__(self) -> None:
        # Start tracemalloc if not already tracing
        if not tracemalloc.is_tracing():
            tracemalloc.start()
        self._snapshots: list[MemorySnapshot] = []

    def snapshot(self, label: str) -> MemorySnapshot:
        current, peak = tracemalloc.get_traced_memory()
        snap = MemorySnapshot(label=label, size_bytes=current, peak_bytes=peak)
        self._snapshots.append(snap)
        return snap

    def get_snapshots(self) -> list[MemorySnapshot]:
        return list(self._snapshots)


@dataclass
class PerformanceProfiler:
    """Simple profiler for accumulating named timings and memory samples.

    Designed to be allocation-light and dependency-free (stdlib only).
    """

    timers_s: Dict[str, float] = field(default_factory=dict)
    counts: Dict[str, int] = field(default_factory=dict)
    memory: MemoryTracker = field(default_factory=MemoryTracker)

    def record(self, name: str, elapsed_s: float) -> None:
        self.timers_s[name] = self.timers_s.get(name, 0.0) + float(elapsed_s)
        self.counts[name] = self.counts.get(name, 0) + 1

    def time_block(self, name: str) -> _TimeBlock:
        return _TimeBlock(self, name)

    def profile_function(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            self.record(func.__name__, time.perf_counter() - start)

    def take_memory_snapshot(self, label: str) -> MemorySnapshot:
        return self.memory.snapshot(label)

    def get_stats(self) -> Dict[str, Dict[str, float]]:
        """Return aggregate timing stats per name.

        Returns:
            Dict mapping timer name to {total_s, count, avg_ms}.
        """
        stats: Dict[str, Dict[str, float]] = {}
        for name, total_s in self.timers_s.items():
            count = float(self.counts.get(name, 0))
            avg_ms = (total_s / count * 1000.0) if count > 0 else 0.0
            stats[name] = {"total_s": total_s, "count": count, "avg_ms": avg_ms}
        return stats

    # ---- CSV export ----
    def to_csv(self, file_like: io.TextIOBase) -> None:
        """Write timing stats to a CSV file-like object.

        Columns: name,total_s,count,avg_ms
        """
        writer = csv.writer(file_like)
        writer.writerow(["name", "total_s", "count", "avg_ms"])
        for name, totals in self.get_stats().items():
            writer.writerow(
                [name, f"{totals['total_s']:.9f}", int(totals["count"]), f"{totals['avg_ms']:.3f}"]
            )

    def dump_csv(self, path: str) -> None:
        with open(path, "w", newline="") as f:
            self.to_csv(f)


def run_with_cprofile(
    func: Callable[..., Any], *args: Any, sort_by: str = "cumulative", top: int = 50, **kwargs: Any
) -> str:
    """Execute a callable under cProfile and return formatted stats as a string.

    Args:
        func: Callable to execute
        sort_by: pstats sort key (e.g., 'cumulative', 'tottime')
        top: number of rows to include in the printed stats
    Returns:
        Stats table string.
    """
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        func(*args, **kwargs)
    finally:
        profiler.disable()

    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).strip_dirs().sort_stats(sort_by)
    ps.print_stats(top)
    return s.getvalue()


_GLOBAL_PROFILER: Optional[PerformanceProfiler] = None


def get_profiler(reset: bool = False) -> PerformanceProfiler:
    """Get a process-wide profiler instance.

    Args:
        reset: If True, reinitialize the global profiler.
    """
    global _GLOBAL_PROFILER
    if reset or _GLOBAL_PROFILER is None:
        _GLOBAL_PROFILER = PerformanceProfiler()
    return _GLOBAL_PROFILER
