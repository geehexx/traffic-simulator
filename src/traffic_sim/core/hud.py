from __future__ import annotations

import arcade
from typing import Dict


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


