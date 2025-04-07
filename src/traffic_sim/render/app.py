from __future__ import annotations

import arcade
from typing import Optional

from traffic_sim.config.loader import load_config, get_nested
from traffic_sim.core.simulation import Simulation
from traffic_sim.core.hud import draw_safety_panel
from traffic_sim.core.track import StadiumTrack


class TrafficSimWindow(arcade.Window):
    def __init__(self, width: int, height: int, title: str, cfg: dict):
        super().__init__(width=width, height=height, title=title, resizable=True)
        arcade.set_background_color(arcade.color.ASH_GREY)
        self.cfg = cfg
        self.hud_minimal: bool = get_nested(cfg, "render.hud_mode", "minimal") == "minimal"
        self.sim = Simulation(cfg)
        self.fixed_dt = float(get_nested(cfg, "physics.delta_t_s", 0.02))
        self.accumulator = 0.0

    def on_draw(self):
        self.clear()
        # Placeholder: draw HUD toggle hint and safety panel stub
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

        # Draw track (scaled to window)
        self._draw_track()
        # Draw vehicles (rectangles)
        self._draw_vehicles()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == getattr(arcade.key, get_nested(self.cfg, "render.hud_toggle_key", "H")):
            self.hud_minimal = not self.hud_minimal

    def on_resize(self, width: float, height: float):
        super().on_resize(width, height)

    def on_update(self, delta_time: float):
        # Fixed-step physics stepping
        self.accumulator += delta_time
        max_steps = int(1.0 / max(1e-6, self.fixed_dt))  # avoid spiral of death
        steps = 0
        while self.accumulator >= self.fixed_dt and steps < max_steps:
            self.sim.step(self.fixed_dt)
            self.accumulator -= self.fixed_dt
            steps += 1

    # --- internal drawing helpers ---
    def _world_to_screen(self, x_m: float, y_m: float) -> tuple[float, float]:
        # Fit stadium bbox to window with margin
        track: StadiumTrack = self.sim.track
        w_m, h_m = track.bbox_m()
        margin_px = 40.0
        scale_x = (self.width - 2 * margin_px) / max(1e-6, w_m)
        scale_y = (self.height - 2 * margin_px) / max(1e-6, h_m)
        scale = min(scale_x, scale_y)
        x_px = self.width * 0.5 + x_m * scale
        y_px = self.height * 0.5 + y_m * scale
        return x_px, y_px

    def _draw_track(self) -> None:
        track: StadiumTrack = self.sim.track
        R = track.radius_m
        S = track.straight_length_m
        # Approximate stadium by lines and arcs
        # Top and bottom straights
        x1, y1 = self._world_to_screen(-S * 0.5, +R)
        x2, y2 = self._world_to_screen(+S * 0.5, +R)
        arcade.draw_line(x1, y1, x2, y2, arcade.color.BLACK, 2)
        x3, y3 = self._world_to_screen(+S * 0.5, -R)
        x4, y4 = self._world_to_screen(-S * 0.5, -R)
        arcade.draw_line(x3, y3, x4, y4, arcade.color.BLACK, 2)
        # Right arc
        cx_r, cy_r = self._world_to_screen(S * 0.5, 0.0)
        arcade.draw_arc_outline(cx_r, cy_r, 2 * R * self._scale_px(), 2 * R * self._scale_px(), arcade.color.BLACK, 270, 90, 2)
        # Left arc
        cx_l, cy_l = self._world_to_screen(-S * 0.5, 0.0)
        arcade.draw_arc_outline(cx_l, cy_l, 2 * R * self._scale_px(), 2 * R * self._scale_px(), arcade.color.BLACK, 90, 270, 2)

    def _scale_px(self) -> float:
        track: StadiumTrack = self.sim.track
        w_m, h_m = track.bbox_m()
        margin_px = 40.0
        scale_x = (self.width - 2 * margin_px) / max(1e-6, w_m)
        scale_y = (self.height - 2 * margin_px) / max(1e-6, h_m)
        return min(scale_x, scale_y)

    def _draw_vehicles(self) -> None:
        scale = self._scale_px()
        for x_m, y_m, theta, length_m, width_m in self.sim.vehicle_draw_data():
            x, y = self._world_to_screen(x_m, y_m)
            arcade.draw_rectangle_filled(x, y, width_m * scale, length_m * scale, arcade.color.SKY_BLUE, angle=-(theta * 180.0 / 3.141592653589793))


def main(cfg_path: Optional[str] = None) -> None:
    cfg = load_config(cfg_path)
    window = TrafficSimWindow(1280, 720, "Traffic Simulator", cfg)
    arcade.run()


if __name__ == "__main__":
    main()


