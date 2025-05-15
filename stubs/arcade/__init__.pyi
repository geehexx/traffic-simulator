# Minimal type stubs for arcade library
from typing import Any, Union, List, Tuple

class Window:
    def __init__(
        self, width: int, height: int, title: str = ..., resizable: bool = ...
    ) -> None: ...
    def on_resize(self, width: int, height: int) -> None: ...
    def on_update(self, delta_time: float) -> None: ...
    def on_draw(self) -> None: ...
    def on_key_press(self, symbol: int, modifiers: int) -> None: ...
    def on_key_release(self, symbol: int, modifiers: int) -> None: ...
    def run(self) -> None: ...
    def close(self) -> None: ...
    def set_update_rate(self, rate: float) -> None: ...

class Sprite:
    def __init__(
        self,
        filename: str = ...,
        scale: float = ...,
        image_x: float = ...,
        image_y: float = ...,
        image_width: float = ...,
        image_height: float = ...,
        center_x: float = ...,
        center_y: float = ...,
        repeat_count_x: int = ...,
        repeat_count_y: int = ...,
        flipped_horizontally: bool = ...,
        flipped_vertically: bool = ...,
        flipped_diagonally: bool = ...,
        hit_box_algorithm: str = ...,
        hit_box_detail: float = ...,
        texture: Any = ...,
        angle: float = ...,
    ) -> None: ...
    def draw(self) -> None: ...
    def update(self) -> None: ...

class SpriteList:
    def __init__(
        self, use_spatial_hash: bool = ..., spatial_hash_cell_size: int = ..., is_static: bool = ...
    ) -> None: ...
    def append(self, item: Sprite) -> None: ...
    def draw(self) -> None: ...
    def update(self) -> None: ...

# Key constants
class key:
    H: int
    Q: int
    ESCAPE: int
    SPACE: int
    UP: int
    DOWN: int
    LEFT: int
    RIGHT: int

# Color constants
class color:
    WHITE: Tuple[int, int, int]
    BLACK: Tuple[int, int, int]
    RED: Tuple[int, int, int]
    GREEN: Tuple[int, int, int]
    BLUE: Tuple[int, int, int]
    ASH_GREY: Tuple[int, int, int]
    DARK_SLATE_GRAY: Tuple[int, int, int]
    DARK_RED: Tuple[int, int, int]
    DARK_BLUE: Tuple[int, int, int]
    DARK_GREEN: Tuple[int, int, int]
    GRAY: Tuple[int, int, int]

# Drawing functions
def draw_circle_filled(
    center_x: float, center_y: float, radius: float, color: Tuple[int, int, int]
) -> None: ...
def draw_line(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    color: Tuple[int, int, int],
    line_width: float = ...,
) -> None: ...
def draw_text(
    text: str,
    start_x: float,
    start_y: float,
    color: Tuple[int, int, int],
    font_size: float = ...,
    width: int = ...,
    align: str = ...,
    font_name: Union[str, Tuple[str, ...]] = ...,
    bold: bool = ...,
    italic: bool = ...,
    anchor_x: str = ...,
    anchor_y: str = ...,
    rotation: float = ...,
) -> None: ...
def draw_arc_outline(
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    color: Tuple[int, int, int],
    start_angle: float,
    end_angle: float,
    line_width: float = ...,
    tilt_angle: float = ...,
    num_segments: int = ...,
) -> None: ...
def draw_polygon_filled(
    point_list: List[Tuple[float, float]], color: Tuple[int, int, int]
) -> None: ...
def draw_lrbt_rectangle_filled(
    left: float, right: float, bottom: float, top: float, color: Tuple[int, int, int]
) -> None: ...
def draw_lrbt_rectangle_outline(
    left: float,
    right: float,
    bottom: float,
    top: float,
    color: Tuple[int, int, int],
    border_width: float = ...,
) -> None: ...
def draw_lbwh_rectangle_filled(
    left: float, bottom: float, width: float, height: float, color: Tuple[int, int, int]
) -> None: ...
def draw_lbwh_rectangle_outline(
    left: float,
    bottom: float,
    width: float,
    height: float,
    color: Tuple[int, int, int],
    border_width: float = ...,
) -> None: ...
def set_background_color(color: Tuple[int, int, int]) -> None: ...
def run() -> None: ...
