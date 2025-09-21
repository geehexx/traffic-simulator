from __future__ import annotations

import arcade
from typing import List, Dict, Any, Optional
from traffic_sim.core.analytics import LiveAnalytics


class AnalyticsHUD:
    """Enhanced HUD for displaying live analytics data."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.analytics = LiveAnalytics(config)
        self.text_objects: Dict[str, Any] = {}
        self._create_text_objects()

    def _create_text_objects(self) -> None:
        """Pre-create text objects for performance optimization."""
        # This will be implemented for high-frequency updates
        pass

    def update(self, vehicles: List, perception_data: List[Optional[Any]], dt_s: float) -> None:
        """Update analytics with current simulation state."""
        self.analytics.update_analytics(vehicles, perception_data, dt_s)

    def draw_minimal_analytics(self, x: float, y: float) -> None:
        """Draw minimal analytics panel."""
        # Speed histogram summary
        speed_hist = self.analytics.get_speed_histogram()
        speed_text = f"Speed: {speed_hist.mean_speed:.1f} km/h (med: {speed_hist.median_speed:.1f})"
        arcade.draw_text(speed_text, x, y, arcade.color.DARK_BLUE, 12)

        # Headway summary
        headway_dist = self.analytics.get_headway_distribution()
        headway_text = f"Headway: {headway_dist.median_headway:.1f}s (dangerous: {headway_dist.dangerous_headways})"
        arcade.draw_text(headway_text, x, y - 20, arcade.color.DARK_GREEN, 12)

        # Near-miss counter
        near_miss_count = self.analytics.get_near_miss_count()
        recent_near_misses = self.analytics.get_recent_near_misses()
        near_miss_text = f"Near-misses: {near_miss_count} total, {recent_near_misses} recent"
        arcade.draw_text(near_miss_text, x, y - 40, arcade.color.DARK_RED, 12)

        # Performance metrics
        perf = self.analytics.get_performance_metrics()
        perf_text = f"FPS: {perf['fps']:.1f} | Sim: {perf['avg_sim_time'] * 1000:.1f}ms"
        arcade.draw_text(perf_text, x, y - 60, arcade.color.GRAY, 10)

    def draw_speed_histogram(
        self, x: float, y: float, width: float = 300, height: float = 150
    ) -> None:
        """Draw real-time speed histogram."""
        speed_hist = self.analytics.get_speed_histogram()

        if not speed_hist.bins or not speed_hist.counts:
            arcade.draw_text("No speed data", x, y, arcade.color.GRAY, 12)
            return

        # Draw histogram bars
        bin_width = width / len(speed_hist.counts)
        max_count = max(speed_hist.counts) if speed_hist.counts else 1

        for i, count in enumerate(speed_hist.counts):
            bar_x = x + i * bin_width
            bar_height = (count / max_count) * height if max_count > 0 else 0

            # Color based on speed range
            speed_center = (speed_hist.bins[i] + speed_hist.bins[i + 1]) / 2
            if speed_center < 30:
                color = arcade.color.GREEN
            elif speed_center < 60:
                color = arcade.color.YELLOW
            else:
                color = arcade.color.RED

            # Draw bar
            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + bin_width * 0.8, y, y + bar_height, color
            )

        # Draw speed statistics
        stats_text = f"Mean: {speed_hist.mean_speed:.1f} | Med: {speed_hist.median_speed:.1f} | P95: {speed_hist.p95_speed:.1f}"
        arcade.draw_text(stats_text, x, y - 20, arcade.color.BLACK, 10)

        # Draw axis labels
        arcade.draw_text("Speed (km/h)", x, y - 35, arcade.color.BLACK, 10)
        arcade.draw_text("Count", x - 30, y + height // 2, arcade.color.BLACK, 10)

    def draw_headway_distribution(
        self, x: float, y: float, width: float = 300, height: float = 150
    ) -> None:
        """Draw real-time headway distribution."""
        headway_dist = self.analytics.get_headway_distribution()

        if not headway_dist.headways:
            arcade.draw_text("No headway data", x, y, arcade.color.GRAY, 12)
            return

        # Create histogram bins
        max_headway = max(headway_dist.headways) if headway_dist.headways else 5.0
        num_bins = 20
        bin_width = width / num_bins
        headway_bin_width = max_headway / num_bins

        # Count headways in each bin
        bins = [0] * num_bins
        for headway in headway_dist.headways:
            bin_idx = min(int(headway / headway_bin_width), num_bins - 1)
            bins[bin_idx] += 1

        max_count = max(bins) if bins else 1

        # Draw histogram bars
        for i, count in enumerate(bins):
            bar_x = x + i * bin_width
            bar_height = (count / max_count) * height if max_count > 0 else 0

            # Color based on headway range
            headway_center = (i + 0.5) * headway_bin_width
            if headway_center < 0.5:
                color = arcade.color.RED  # Critical
            elif headway_center < 1.0:
                color = arcade.color.ORANGE  # Dangerous
            else:
                color = arcade.color.GREEN  # Safe

            # Draw bar
            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + bin_width * 0.8, y, y + bar_height, color
            )

        # Draw headway statistics
        stats_text = f"Med: {headway_dist.median_headway:.1f}s | Danger: {headway_dist.dangerous_headways} | Critical: {headway_dist.critical_headways}"
        arcade.draw_text(stats_text, x, y - 20, arcade.color.BLACK, 10)

        # Draw axis labels
        arcade.draw_text("Headway (s)", x, y - 35, arcade.color.BLACK, 10)
        arcade.draw_text("Count", x - 30, y + height // 2, arcade.color.BLACK, 10)

    def draw_near_miss_counter(self, x: float, y: float) -> None:
        """Draw near-miss counter with recent activity."""
        total_near_misses = self.analytics.get_near_miss_count()
        recent_near_misses = self.analytics.get_recent_near_misses()

        # Main counter
        counter_text = f"Near-misses: {total_near_misses}"
        color = arcade.color.DARK_RED if total_near_misses > 0 else arcade.color.GREEN
        arcade.draw_text(counter_text, x, y, color, 14)

        # Recent activity
        recent_text = f"Recent (5min): {recent_near_misses}"
        recent_color = arcade.color.RED if recent_near_misses > 0 else arcade.color.GRAY
        arcade.draw_text(recent_text, x, y - 20, recent_color, 12)

        # Rate indicator
        if recent_near_misses > 10:
            rate_text = "HIGH RISK"
            rate_color = arcade.color.RED
        elif recent_near_misses > 5:
            rate_text = "ELEVATED"
            rate_color = arcade.color.ORANGE
        else:
            rate_text = "NORMAL"
            rate_color = arcade.color.GREEN

        arcade.draw_text(rate_text, x, y - 40, rate_color, 12)

    def draw_performance_panel(self, x: float, y: float) -> None:
        """Draw performance monitoring panel."""
        perf = self.analytics.get_performance_metrics()

        # FPS indicator
        fps_color = arcade.color.GREEN if perf["fps"] >= 30 else arcade.color.RED
        fps_text = f"FPS: {perf['fps']:.1f}"
        arcade.draw_text(fps_text, x, y, fps_color, 12)

        # Frame time
        frame_time_text = f"Frame: {perf['avg_frame_time'] * 1000:.1f}ms"
        arcade.draw_text(frame_time_text, x, y - 15, arcade.color.GRAY, 10)

        # Simulation time
        sim_time_text = f"Sim: {perf['avg_sim_time'] * 1000:.1f}ms"
        arcade.draw_text(sim_time_text, x, y - 30, arcade.color.GRAY, 10)

    def draw_incident_log(self, x: float, y: float, max_events: int = 10) -> None:
        """Draw recent incident log."""
        incident_summary = self.analytics.get_incident_summary()

        # Summary
        summary_text = f"Incidents: {incident_summary['total_incidents']} total, {incident_summary['recent_incidents']} recent"
        arcade.draw_text(summary_text, x, y, arcade.color.DARK_BLUE, 12)

        # Recent incidents (last few)
        recent_incidents = self.analytics.incident_log[-max_events:]
        for i, incident in enumerate(recent_incidents):
            incident_text = (
                f"{incident.event_type} - V{incident.vehicle_id} at {incident.location_m:.0f}m"
            )
            arcade.draw_text(incident_text, x, y - 20 - i * 15, arcade.color.BLACK, 10)

    def draw_full_analytics(self, x: float, y: float) -> None:
        """Draw full analytics dashboard."""
        # Speed histogram
        self.draw_speed_histogram(x, y, 300, 120)

        # Headway distribution
        self.draw_headway_distribution(x + 320, y, 300, 120)

        # Near-miss counter
        self.draw_near_miss_counter(x, y - 150)

        # Performance panel
        self.draw_performance_panel(x + 200, y - 150)

        # Incident log
        self.draw_incident_log(x, y - 200)

    def clear_old_data(self) -> None:
        """Clear old analytics data to prevent memory buildup."""
        self.analytics.clear_old_data()
