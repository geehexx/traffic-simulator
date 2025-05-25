from __future__ import annotations

import arcade
from typing import Dict, List, Tuple, Any, Optional
from traffic_sim.core.perception import PerceptionData
from traffic_sim.core.analytics_hud import AnalyticsHUD


class OptimizedHUD:
    """Optimized HUD using Text objects for better performance."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.text_objects: Dict[str, Any] = {}
        self.analytics_hud = AnalyticsHUD(config)
        self._create_text_objects()

    def _create_text_objects(self) -> None:
        """Pre-create Text objects to avoid recreation each frame."""
        # This would be implemented for high-frequency text updates
        pass

    def update(
        self, vehicles: List, perception_data: List[Optional[PerceptionData]], dt_s: float
    ) -> None:
        """Update HUD with current simulation state."""
        self.analytics_hud.update(vehicles, perception_data, dt_s)

    @staticmethod
    def draw_text_optimized(
        text: str, x: float, y: float, color: Tuple[int, int, int], font_size: int = 12
    ) -> None:
        """Use Text objects for better performance when possible."""
        # For now, fall back to draw_text but this could be optimized
        arcade.draw_text(text, x, y, color, font_size)


def draw_safety_panel(x: float, y: float, panel: Dict[str, float | bool]) -> None:
    radius_m = panel.get("radius_m", 0.0)
    v_safe_kmh = panel.get("v_safe_kmh", 0.0)
    length_needed_m = panel.get("length_needed_m", 0.0)
    unsafe = bool(panel.get("unsafe", False))

    text = f"R={radius_m:,.0f} m  V_safe={v_safe_kmh:,.0f} km/h  L_needed={length_needed_m:,.0f} m"
    arcade.draw_text(text, x, y, arcade.color.BLACK, 12)

    if unsafe:
        warn = (
            f"Unsafe curve of {radius_m:,.0f} m. Decrease speed to {v_safe_kmh:,.0f} km/h "
            f"or increase track length to {length_needed_m:,.0f} m."
        )
        arcade.draw_text(warn, x, y - 18, arcade.color.DARK_RED, 12)


def _calculate_perception_stats(
    perception_data: List[Optional[PerceptionData]],
) -> tuple[int, int, float, float, float]:
    """Calculate perception statistics."""
    total_vehicles = len(perception_data)
    occluded_count = sum(1 for p in perception_data if p is not None and p.is_occluded)
    valid_perceptions = [p for p in perception_data if p is not None]

    if not valid_perceptions:
        return total_vehicles, occluded_count, 0.0, 0.0, 0.0

    ssd_values = [p.ssd_required_m for p in valid_perceptions]
    avg_ssd = sum(ssd_values) / len(ssd_values)
    max_ssd = max(ssd_values)
    min_ssd = min(ssd_values)

    return total_vehicles, occluded_count, avg_ssd, max_ssd, min_ssd


def draw_perception_summary(
    x: float, y: float, perception_data: List[Optional[PerceptionData]]
) -> None:
    """Draw perception summary including SSD and occlusion statistics."""
    if not perception_data:
        return

    total_vehicles, occluded_count, avg_ssd, max_ssd, min_ssd = _calculate_perception_stats(
        perception_data
    )

    # Draw summary
    text = f"Perception: {occluded_count}/{total_vehicles} occluded, SSD: {avg_ssd:.1f}m (range: {min_ssd:.1f}-{max_ssd:.1f}m)"
    arcade.draw_text(text, x, y, arcade.color.DARK_BLUE, 12)


def draw_vehicle_perception_overlay(
    x: float, y: float, vehicle_idx: int, perception: Optional[PerceptionData], scale: float = 1.0
) -> None:
    """Draw per-vehicle perception overlay."""
    # Vehicle info
    base_y = y - vehicle_idx * 20 * scale

    # Leader info
    if perception is not None and perception.leader_vehicle is not None:
        leader_text = f"V{vehicle_idx}: Leader at {perception.leader_distance_m:.1f}m"
        if perception.is_occluded:
            leader_text += " (OCCLUDED)"
        color = arcade.color.DARK_RED if perception.is_occluded else arcade.color.DARK_GREEN
    else:
        leader_text = f"V{vehicle_idx}: No leader in range"
        color = arcade.color.GRAY

    arcade.draw_text(leader_text, x, base_y, color, 10 * scale)

    # SSD info
    if perception is not None:
        ssd_text = f"SSD: {perception.ssd_required_m:.1f}m"
        arcade.draw_text(ssd_text, x + 200 * scale, base_y, arcade.color.DARK_BLUE, 10 * scale)
    else:
        ssd_text = "SSD: N/A"
        arcade.draw_text(ssd_text, x + 200 * scale, base_y, arcade.color.GRAY, 10 * scale)


def draw_perception_heatmap(
    x: float,
    y: float,
    perception_data: List[Optional[PerceptionData]],
    width: float = 300,
    height: float = 100,
) -> None:
    """Draw a simple heatmap of SSD values using optimized rectangle drawing."""
    if not perception_data:
        return

    # Create a simple bar chart of SSD values
    valid_perceptions = [p for p in perception_data if p is not None]
    if not valid_perceptions:
        return

    bar_width = width / len(perception_data)
    max_ssd = max(p.ssd_required_m for p in valid_perceptions) if valid_perceptions else 1.0

    for i, perception in enumerate(perception_data):
        bar_x = x + i * bar_width

        if perception is not None:
            bar_height = (perception.ssd_required_m / max_ssd) * height
            # Color based on occlusion status
            color = arcade.color.RED if perception.is_occluded else arcade.color.GREEN
            # Draw rectangle using left, right, bottom, top coordinates
            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + bar_width * 0.8, y, y + bar_height, color
            )
            # Draw SSD value
            ssd_text = f"{perception.ssd_required_m:.0f}"
            arcade.draw_text(ssd_text, bar_x, y - 15, arcade.color.BLACK, 8)
        else:
            # Draw empty bar for None perception
            arcade.draw_lrbt_rectangle_filled(
                bar_x, bar_x + bar_width * 0.8, y, y + 5, arcade.color.GRAY
            )
            arcade.draw_text("N/A", bar_x, y - 15, arcade.color.GRAY, 8)


def draw_live_analytics(
    x: float, y: float, analytics_hud: AnalyticsHUD, minimal: bool = True
) -> None:
    """Draw live analytics data."""
    if minimal:
        analytics_hud.draw_minimal_analytics(x, y)
    else:
        analytics_hud.draw_full_analytics(x, y)


def draw_analytics_panel(
    x: float, y: float, analytics_hud: AnalyticsHUD, panel_type: str = "minimal"
) -> None:
    """Draw specific analytics panel."""
    if panel_type == "minimal":
        analytics_hud.draw_minimal_analytics(x, y)
    elif panel_type == "speed_histogram":
        analytics_hud.draw_speed_histogram(x, y)
    elif panel_type == "headway_distribution":
        analytics_hud.draw_headway_distribution(x, y)
    elif panel_type == "near_miss_counter":
        analytics_hud.draw_near_miss_counter(x, y)
    elif panel_type == "performance":
        analytics_hud.draw_performance_panel(x, y)
    elif panel_type == "incident_log":
        analytics_hud.draw_incident_log(x, y)
    elif panel_type == "full":
        analytics_hud.draw_full_analytics(x, y)
