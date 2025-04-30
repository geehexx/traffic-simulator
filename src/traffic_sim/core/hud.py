from __future__ import annotations

import arcade
from typing import Dict, List
from traffic_sim.core.simulation import PerceptionData


def draw_safety_panel(x: float, y: float, panel: Dict[str, float | bool]) -> None:
    radius_m = panel.get("radius_m", 0.0)
    v_safe_kmh = panel.get("v_safe_kmh", 0.0)
    length_needed_m = panel.get("length_needed_m", 0.0)
    unsafe = bool(panel.get("unsafe", False))

    text = (
        f"R={radius_m:,.0f} m  V_safe={v_safe_kmh:,.0f} km/h  L_needed={length_needed_m:,.0f} m"
    )
    arcade.draw_text(text, x, y, arcade.color.BLACK, 12)

    if unsafe:
        warn = (
            f"Unsafe curve of {radius_m:,.0f} m. Decrease speed to {v_safe_kmh:,.0f} km/h "
            f"or increase track length to {length_needed_m:,.0f} m."
        )
        arcade.draw_text(warn, x, y - 18, arcade.color.DARK_RED, 12)


def draw_perception_summary(x: float, y: float, perception_data: List[PerceptionData]) -> None:
    """Draw perception summary including SSD and occlusion statistics."""
    if not perception_data:
        return
        
    # Calculate statistics
    total_vehicles = len(perception_data)
    occluded_count = sum(1 for p in perception_data if p.is_occluded)
    avg_ssd = sum(p.ssd_required_m for p in perception_data) / total_vehicles
    max_ssd = max(p.ssd_required_m for p in perception_data)
    min_ssd = min(p.ssd_required_m for p in perception_data)
    
    # Draw summary
    text = f"Perception: {occluded_count}/{total_vehicles} occluded, SSD: {avg_ssd:.1f}m (range: {min_ssd:.1f}-{max_ssd:.1f}m)"
    arcade.draw_text(text, x, y, arcade.color.DARK_BLUE, 12)


def draw_vehicle_perception_overlay(x: float, y: float, vehicle_idx: int, 
                                  perception: PerceptionData, scale: float = 1.0) -> None:
    """Draw per-vehicle perception overlay."""
    # Vehicle info
    base_y = y - vehicle_idx * 20 * scale
    
    # Leader info
    if perception.leader_vehicle is not None:
        leader_text = f"V{vehicle_idx}: Leader at {perception.leader_distance_m:.1f}m"
        if perception.is_occluded:
            leader_text += " (OCCLUDED)"
        color = arcade.color.DARK_RED if perception.is_occluded else arcade.color.DARK_GREEN
    else:
        leader_text = f"V{vehicle_idx}: No leader in range"
        color = arcade.color.GRAY
    
    arcade.draw_text(leader_text, x, base_y, color, 10 * scale)
    
    # SSD info
    ssd_text = f"SSD: {perception.ssd_required_m:.1f}m"
    arcade.draw_text(ssd_text, x + 200 * scale, base_y, arcade.color.DARK_BLUE, 10 * scale)


def draw_perception_heatmap(x: float, y: float, perception_data: List[PerceptionData], 
                          width: float = 300, height: float = 100) -> None:
    """Draw a simple heatmap of SSD values."""
    if not perception_data:
        return
        
    # Create a simple bar chart of SSD values
    bar_width = width / len(perception_data)
    max_ssd = max(p.ssd_required_m for p in perception_data) if perception_data else 1.0
    
    for i, perception in enumerate(perception_data):
        bar_x = x + i * bar_width
        bar_height = (perception.ssd_required_m / max_ssd) * height
        
        # Color based on occlusion status
        color = arcade.color.RED if perception.is_occluded else arcade.color.GREEN
        
        # Draw bar
        arcade.draw_lbwh_rectangle_filled(
            bar_x, y, 
            bar_width * 0.8, bar_height, color
        )
        
        # Draw SSD value
        ssd_text = f"{perception.ssd_required_m:.0f}"
        arcade.draw_text(ssd_text, bar_x, y - 15, arcade.color.BLACK, 8)


