from __future__ import annotations

import arcade
from typing import Optional, Tuple

from traffic_sim.config.loader import load_config, get_nested
from traffic_sim.core.simulation import Simulation
from traffic_sim.core.hud import (
    draw_safety_panel,
    draw_perception_summary,
    draw_vehicle_perception_overlay,
    draw_perception_heatmap,
)
from traffic_sim.core.track import StadiumTrack


class TrafficSimWindow(arcade.Window):
    def __init__(self, width: int, height: int, title: str, cfg: dict):
        super().__init__(width=width, height=height, title=title, resizable=True)
        arcade.set_background_color(arcade.color.ASH_GREY)
        self.cfg = cfg
        self.hud_minimal: bool = get_nested(cfg, "render.hud_mode", "minimal") == "minimal"
        self.sim = Simulation(cfg)
        # Fixed-step physics with accumulator
        self.fixed_dt = float(get_nested(cfg, "physics.delta_t_s", 0.02))
        self.accumulator = 0.0

    def on_draw(self) -> None:
        self.clear()
        # HUD toggle hint and safety panel
        margin = 10
        arcade.draw_text(
            "Traffic Simulator (scaffold)",
            margin,
            self.height - 30,
            arcade.color.BLACK,
            16,
        )
        arcade.draw_text(
            "Press H to toggle HUD",
            margin,
            self.height - 55,
            arcade.color.DARK_SLATE_GRAY,
            12,
        )
        panel = self.sim.compute_safety_panel()
        draw_safety_panel(margin, self.height - 85, panel)

        # Draw perception summary
        if hasattr(self.sim, "perception_data") and self.sim.perception_data:
            draw_perception_summary(margin, self.height - 115, self.sim.perception_data)

        # Draw track and vehicles
        self._draw_track()
        self._draw_vehicles()

        # Optional extra HUD when toggled to full
        if not self.hud_minimal:
            arcade.draw_text(
                f"HUD: full | vehicles={len(self.sim.vehicles)}",
                margin,
                self.height - 145,
                arcade.color.DARK_SLATE_GRAY,
                12,
            )

            # Draw detailed perception information
            if hasattr(self.sim, "perception_data") and self.sim.perception_data:
                # Draw perception heatmap
                draw_perception_heatmap(margin, self.height - 200, self.sim.perception_data)

                # Draw per-vehicle overlays (first 10 vehicles to avoid clutter)
                overlay_y = self.height - 320
                for i, perception in enumerate(self.sim.perception_data[:10]):
                    draw_vehicle_perception_overlay(margin, overlay_y, i, perception)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        # Normalize to uppercase letter key
        desired = get_nested(self.cfg, "render.hud_toggle_key", "H").upper()
        if symbol == getattr(arcade.key, desired, arcade.key.H):
            self.hud_minimal = not self.hud_minimal

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)

    def on_update(self, delta_time: float) -> None:
        # Fixed-step stepping for determinism
        self.accumulator += delta_time
        max_steps = int(1.0 / max(1e-6, self.fixed_dt))
        steps = 0
        while self.accumulator >= self.fixed_dt and steps < max_steps:
            self.sim.step(self.fixed_dt)
            self.accumulator -= self.fixed_dt
            steps += 1

    # --- Drawing helpers ---
    def _scale_px(self) -> float:
        track: StadiumTrack = self.sim.track
        w_m, h_m = track.bbox_m()
        margin_px = 40.0
        scale_x = (self.width - 2 * margin_px) / max(1e-6, w_m)
        scale_y = (self.height - 2 * margin_px) / max(1e-6, h_m)
        return min(scale_x, scale_y)

    def _world_to_screen(self, x_m: float, y_m: float) -> Tuple[float, float]:
        scale = self._scale_px()
        x_px = self.width * 0.5 + x_m * scale
        y_px = self.height * 0.5 + y_m * scale
        return x_px, y_px

    def _draw_track(self) -> None:
        track: StadiumTrack = self.sim.track
        R = track.radius_m
        S = track.straight_length_m
        # Top straight
        x1, y1 = self._world_to_screen(-S * 0.5, +R)
        x2, y2 = self._world_to_screen(+S * 0.5, +R)
        arcade.draw_line(x1, y1, x2, y2, arcade.color.BLACK, 2)
        # Bottom straight
        x3, y3 = self._world_to_screen(+S * 0.5, -R)
        x4, y4 = self._world_to_screen(-S * 0.5, -R)
        arcade.draw_line(x3, y3, x4, y4, arcade.color.BLACK, 2)
        # Right arc
        scale = self._scale_px()
        cx_r, cy_r = self._world_to_screen(S * 0.5, 0.0)
        # Right semicircle: angles -90 to 90
        arcade.draw_arc_outline(
            cx_r, cy_r, 2 * R * scale, 2 * R * scale, arcade.color.BLACK, -90, 90, 2
        )
        # Left arc
        cx_l, cy_l = self._world_to_screen(-S * 0.5, 0.0)
        arcade.draw_arc_outline(
            cx_l, cy_l, 2 * R * scale, 2 * R * scale, arcade.color.BLACK, 90, 270, 2
        )

    def _draw_vehicles(self) -> None:
        track: StadiumTrack = self.sim.track
        scale = self._scale_px()
        for v in self.sim.vehicles:
            x_m, y_m, theta = track.position_heading(v.state.s_m)
            x, y = self._world_to_screen(x_m, y_m)
            # Draw vehicle as a rotated rectangle using polygon based on center, size, angle
            # Ensure vehicle length aligns with travel direction: use length along x pre-rotation
            h = v.spec.length_m * scale
            w = v.spec.width_m * scale
            import math

            ang = theta
            ca = math.cos(ang)
            sa = math.sin(ang)
            # dx along local forward (length), dy along lateral (width)
            dx = h / 2.0
            dy = w / 2.0
            # Rectangle corners around center (±dx, ±dy), rotated by ang
            corners = [
                (x + (-dx) * ca - (-dy) * sa, y + (-dx) * sa + (-dy) * ca),
                (x + (dx) * ca - (-dy) * sa, y + (dx) * sa + (-dy) * ca),
                (x + (dx) * ca - (dy) * sa, y + (dx) * sa + (dy) * ca),
                (x + (-dx) * ca - (dy) * sa, y + (-dx) * sa + (dy) * ca),
            ]
            arcade.draw_polygon_filled(corners, v.color_rgb)


def main(cfg_path: Optional[str] = None) -> None:
    cfg = load_config(cfg_path)
    _window = TrafficSimWindow(1280, 720, "Traffic Simulator", cfg)
    arcade.run()


if __name__ == "__main__":
    main()
