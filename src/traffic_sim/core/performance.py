from __future__ import annotations

import struct
from typing import List, Dict, Tuple, Optional
from traffic_sim.core.vehicle import Vehicle


class PerformanceOptimizer:
    """Performance optimization utilities for the traffic simulation."""

    def __init__(self):
        # Cache for expensive calculations
        self._inverse_sqrt_cache: Dict[float, float] = {}
        self._occlusion_cache: Dict[Tuple[int, int], bool] = {}
        self._last_sort_time: float = 0.0
        self._sorted_vehicles: Optional[List[Vehicle]] = None

        # Performance counters
        self.cache_hits = 0
        self.cache_misses = 0

    def fast_inverse_sqrt(self, x: float) -> float:
        """
        Fast approximation of 1/sqrt(x) using cached values.

        Args:
            x: Input value (must be positive)

        Returns:
            Approximate value of 1/sqrt(x)
        """
        if x <= 0:
            return 0.0

        # Round to avoid floating point precision issues
        x_rounded = round(x, 6)

        if x_rounded in self._inverse_sqrt_cache:
            self.cache_hits += 1
            return self._inverse_sqrt_cache[x_rounded]

        # Fast inverse square root approximation
        # Using the famous Quake III algorithm
        x_bytes = struct.pack("f", x)
        i = struct.unpack("I", x_bytes)[0]
        i = 0x5F3759DF - (i >> 1)
        y_bytes = struct.pack("I", i)
        result = struct.unpack("f", y_bytes)[0]

        # One iteration of Newton's method for better accuracy
        result = result * (1.5 - 0.5 * x * result * result)

        self._inverse_sqrt_cache[x_rounded] = result
        self.cache_misses += 1

        # Limit cache size to prevent memory issues
        if len(self._inverse_sqrt_cache) > 1000:
            # Remove oldest entries (simple FIFO)
            keys_to_remove = list(self._inverse_sqrt_cache.keys())[:100]
            for key in keys_to_remove:
                del self._inverse_sqrt_cache[key]

        return float(result)

    def pre_sort_vehicles(
        self, vehicles: List[Vehicle], current_time: float, force_resort: bool = False
    ) -> List[Vehicle]:
        """
        Pre-sort vehicles by arc length with caching.

        Args:
            vehicles: List of vehicles to sort
            current_time: Current simulation time
            force_resort: Force resort even if recently sorted

        Returns:
            Sorted list of vehicles (same reference as input)
        """
        # Only resort if enough time has passed or forced
        time_since_last_sort = current_time - self._last_sort_time
        if (
            not force_resort and self._sorted_vehicles is not None and time_since_last_sort < 0.1
        ):  # 100ms cache
            return vehicles  # Return original list if cached

        # Sort by position along track (in place)
        vehicles.sort(key=lambda v: v.state.s_m)

        self._sorted_vehicles = vehicles
        self._last_sort_time = current_time

        return vehicles  # Return the same list reference

    def cache_occlusion_relationship(
        self, vehicle1_idx: int, vehicle2_idx: int, is_occluded: bool
    ) -> None:
        """
        Cache occlusion relationship between two vehicles.

        Args:
            vehicle1_idx: Index of first vehicle
            vehicle2_idx: Index of second vehicle
            is_occluded: Whether vehicle2 is occluded from vehicle1
        """
        key = (min(vehicle1_idx, vehicle2_idx), max(vehicle1_idx, vehicle2_idx))
        self._occlusion_cache[key] = is_occluded

    def get_cached_occlusion(self, vehicle1_idx: int, vehicle2_idx: int) -> Optional[bool]:
        """
        Get cached occlusion relationship.

        Args:
            vehicle1_idx: Index of first vehicle
            vehicle2_idx: Index of second vehicle

        Returns:
            Cached occlusion status or None if not cached
        """
        key = (min(vehicle1_idx, vehicle2_idx), max(vehicle1_idx, vehicle2_idx))
        return self._occlusion_cache.get(key)

    def clear_occlusion_cache(self) -> None:
        """Clear the occlusion cache."""
        self._occlusion_cache.clear()

    def vectorized_distance_calculation(
        self, positions: List[float], track_length: float
    ) -> List[float]:
        """
        Vectorized calculation of distances between consecutive vehicles.

        Args:
            positions: List of vehicle positions along track
            track_length: Total track length

        Returns:
            List of distances between consecutive vehicles
        """
        if len(positions) < 2:
            return []

        # Use numpy for vectorized operations if available
        try:
            import numpy as np

            positions_array = np.array(positions)

            # Calculate differences
            diffs = np.diff(positions_array)

            # Handle wrap-around for circular track
            diffs = np.where(diffs < 0, diffs + track_length, diffs)

            return list(diffs)
        except ImportError:
            # Fallback to pure Python
            distances = []
            for i in range(len(positions) - 1):
                diff = positions[i + 1] - positions[i]
                if diff < 0:
                    diff += track_length
                distances.append(diff)
            return distances

    def batch_update_vehicle_states(self, vehicles: List[Vehicle], dt_s: float) -> None:
        """
        Batch update vehicle states for better performance.

        Args:
            vehicles: List of vehicles to update
            dt_s: Time step in seconds
        """
        # Pre-calculate common values
        for vehicle in vehicles:
            # Update internal state
            vehicle.update_internal_state(dt_s)

    def get_performance_stats(self) -> Dict[str, float]:
        """
        Get performance statistics.

        Returns:
            Dictionary of performance metrics
        """
        total_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0.0

        return {
            "cache_hit_rate": cache_hit_rate,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "inverse_sqrt_cache_size": len(self._inverse_sqrt_cache),
            "occlusion_cache_size": len(self._occlusion_cache),
        }

    def clear_all_caches(self) -> None:
        """Clear all performance caches."""
        self._inverse_sqrt_cache.clear()
        self._occlusion_cache.clear()
        self._sorted_vehicles = None
        self.cache_hits = 0
        self.cache_misses = 0


# Global performance optimizer instance
_performance_optimizer = PerformanceOptimizer()


def get_performance_optimizer() -> PerformanceOptimizer:
    """Get the global performance optimizer instance."""
    return _performance_optimizer


def fast_inverse_sqrt(x: float) -> float:
    """Convenience function for fast inverse square root."""
    return _performance_optimizer.fast_inverse_sqrt(x)


def pre_sort_vehicles(
    vehicles: List[Vehicle], current_time: float, force_resort: bool = False
) -> List[Vehicle]:
    """Convenience function for pre-sorting vehicles."""
    return _performance_optimizer.pre_sort_vehicles(vehicles, current_time, force_resort)
