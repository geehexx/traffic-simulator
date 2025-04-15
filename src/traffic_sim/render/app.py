from __future__ import annotations

import arcade
from typing import Optional

from traffic_sim.config.loader import load_config, get_nested
from traffic_sim.core.simulation import Simulation
from traffic_sim.core.hud import draw_safety_panel


class TrafficSimWindow(arcade.Window):
    def __init__(self, width: int, height: int, title: str, cfg: dict):
        super().__init__(width=width, height=height, title=title, resizable=True)
        arcade.set_background_color(arcade.color.ASH_GREY)
        self.cfg = cfg
        self.hud_minimal: bool = get_nested(cfg, "render.hud_mode", "minimal") == "minimal"
        self.sim = Simulation(cfg)

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

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == getattr(arcade.key, get_nested(self.cfg, "render.hud_toggle_key", "H")):
            self.hud_minimal = not self.hud_minimal

    def on_resize(self, width: float, height: float):
        super().on_resize(width, height)


def main(cfg_path: Optional[str] = None) -> None:
    cfg = load_config(cfg_path)
    window = TrafficSimWindow(1280, 720, "Traffic Simulator", cfg)
    arcade.run()


if __name__ == "__main__":
    main()


