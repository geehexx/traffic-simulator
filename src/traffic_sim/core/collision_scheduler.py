from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Dict, List, Tuple

from traffic_sim.core.vehicle import Vehicle


@dataclass(frozen=True)
class PairKey:
    follower_idx: int
    leader_idx: int


class CollisionEventScheduler:
    """Event scheduler for follower→leader collision gating.

    Maintains a min-heap of (due_time, version, follower_idx) entries. The current
    leader for a follower comes from adjacency (sorted order). Each reschedule
    increments the follower's version to invalidate stale heap entries.
    """

    def __init__(
        self,
        horizon_s: float = 3.0,
        guard_band_m: float = 0.3,
    ) -> None:
        self.horizon_s = float(horizon_s)
        self.guard_band_m = float(guard_band_m)

        self._heap: List[Tuple[float, int, int]] = []  # (due_time, version, follower_idx)
        self._version_by_follower: Dict[int, int] = {}
        self._leader_by_follower: Dict[int, int] = {}
        self._due_time_by_follower: Dict[int, float] = {}

    def clear(self) -> None:
        self._heap.clear()
        self._version_by_follower.clear()
        self._leader_by_follower.clear()
        self._due_time_by_follower.clear()

    def update_adjacency_and_reschedule(
        self,
        vehicles: List[Vehicle],
        track_length_m: float,
        now_s: float,
        follower_to_leader: List[int] | None = None,
        follower_max_accel: float = 2.0,
        leader_max_brake: float = 4.0,
        collision_threshold_m: float = 0.5,
    ) -> None:
        n = len(vehicles)
        if n <= 1:
            self.clear()
            return

        if follower_to_leader is None:
            follower_to_leader = [(i + 1) % n for i in range(n)]

        # Rebuild versions for any mapping changes and reschedule due times
        for follower_idx in range(n):
            leader_idx = follower_to_leader[follower_idx]
            prev_leader = self._leader_by_follower.get(follower_idx)
            if prev_leader != leader_idx:
                # Mapping changed -> bump version to invalidate stale entries
                self._version_by_follower[follower_idx] = (
                    self._version_by_follower.get(follower_idx, 0) + 1
                )
                self._leader_by_follower[follower_idx] = leader_idx

            # Compute conservative next due time
            due_time = self._predict_due_time(
                vehicles[follower_idx],
                vehicles[leader_idx],
                track_length_m,
                now_s,
                follower_max_accel,
                leader_max_brake,
                collision_threshold_m + self.guard_band_m,
            )
            self._due_time_by_follower[follower_idx] = due_time
            version = self._version_by_follower.get(follower_idx, 0)
            heapq.heappush(self._heap, (due_time, version, follower_idx))

    def pop_due_pairs(self, now_s: float) -> List[Tuple[int, int]]:
        """Return list of (follower_idx, leader_idx) pairs whose due_time ≤ now_s.

        Stale entries (version mismatch) are skipped.
        """
        due: List[Tuple[int, int]] = []
        while self._heap and self._heap[0][0] <= now_s:
            _, version, follower_idx = heapq.heappop(self._heap)
            if self._version_by_follower.get(follower_idx) != version:
                continue  # stale
            leader_idx = self._leader_by_follower.get(follower_idx)
            if leader_idx is None:
                continue
            due.append((follower_idx, leader_idx))
        return due

    def _predict_due_time(
        self,
        follower: Vehicle,
        leader: Vehicle,
        track_length_m: float,
        now_s: float,
        follower_max_accel: float,
        leader_max_brake: float,
        collision_distance_m: float,
    ) -> float:
        """Conservative earliest time the follower-leader gap could reach the collision distance.

        Gap dynamics along the arc:
            g(t) = g0 + (v_l - v_f) t + 0.5 (a_l - a_f) t^2
        We use conservative accelerations a_f = +follower_max_accel, a_l = -leader_max_brake.
        If no positive root exists within horizon, schedule at horizon.
        """
        # Initial gap forward from follower to leader
        g0 = (leader.state.s_m - follower.state.s_m) % track_length_m
        C = g0 - collision_distance_m
        if C <= 0:
            return now_s  # already overlapping under guard band

        B = leader.state.v_mps - follower.state.v_mps
        A = 0.5 * ((-leader_max_brake) - (follower_max_accel))  # a_l - a_f

        # Solve A t^2 + B t + C = 0 for smallest t ≥ 0.
        # Handle degenerate cases.
        if abs(A) < 1e-9:
            if B >= 0.0:
                return now_s + self.horizon_s
            t = -C / B
            return now_s + t if t >= 0.0 else now_s + self.horizon_s

        disc = B * B - 4.0 * A * C
        if disc < 0.0:
            return now_s + self.horizon_s
        sqrt_disc = disc**0.5
        t1 = (-B - sqrt_disc) / (2.0 * A)
        t2 = (-B + sqrt_disc) / (2.0 * A)
        # We want the smallest non-negative root
        candidates = [t for t in (t1, t2) if t >= 0.0]
        if not candidates:
            return now_s + self.horizon_s
        t_min = min(candidates)
        if t_min > self.horizon_s:
            return now_s + self.horizon_s
        return float(now_s + t_min)
