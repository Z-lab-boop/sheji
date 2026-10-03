"""Frozen design and submission parameters for the Bubushengdian stamp kit."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductSpec:
    width: float = 165.0
    depth: float = 120.0
    height: float = 30.0
    corner_radius: float = 10.0
    wall: float = 1.8
    clearance: float = 0.35
    travel: float = 92.0
    stamp_width: float = 32.0
    stamp_depth: float = 32.0
    stamp_height: float = 23.0
    stamp_face: float = 26.0
    inkpad_width: float = 42.0
    inkpad_depth: float = 42.0
    inkpad_height: float = 12.0


@dataclass(frozen=True)
class BoardSpec:
    width_px: int = 2480
    height_px: int = 3508
    dpi: int = 300
    count: int = 8
    max_bytes: int = 5_000_000


PRODUCT = ProductSpec()
BOARD = BoardSpec()

STAMP_NAMES = (
    "学步桥",
    "回车巷",
    "武灵丛台",
    "邯郸市博物馆",
    "月满邯郸",
    "山河同游",
)

COLORS = {
    "city_blue": "#173B46",
    "stone_gray": "#787C78",
    "moon_paper": "#F0E7D4",
    "seal_red": "#B23A32",
    "route_gold": "#C29A55",
    "ink_black": "#172022",
}

COPY = {
    "name": "步步生典",
    "english": "STEP INTO HANDAN",
    "category": "邯郸双节漫游章匣",
    "slogan": "每一步，都走进一则成语",
    "reflection": "不摹他人步，自成一城路",
    "route_disclaimer": "文化路线示意",
}


def motion_offsets(progress: float) -> dict[str, tuple[float, float]]:
    """Return X/Y offsets in millimetres for the concept opening motion."""
    progress = max(0.0, min(1.0, progress))
    eased = progress * progress * (3.0 - 2.0 * progress)
    return {
        "outer_case": (0.0, 0.0),
        "map_compartment": (0.0, 0.0),
        "stamp_tray": (round(PRODUCT.travel * eased, 6), 0.0),
    }


def validate_spec() -> list[str]:
    """Return violations of the frozen design and competition contract."""
    errors: list[str] = []
    if (PRODUCT.width, PRODUCT.depth, PRODUCT.height) != (165.0, 120.0, 30.0):
        errors.append("product envelope changed")
    if PRODUCT.wall < 1.5:
        errors.append("wall is below concept-model minimum")
    if not 0.2 <= PRODUCT.clearance <= 0.6:
        errors.append("tray clearance is outside the testable range")
    if len(STAMP_NAMES) != 6:
        errors.append("stamp count must remain six")
    if BOARD.count > 8:
        errors.append("board count exceeds competition limit")
    return errors
