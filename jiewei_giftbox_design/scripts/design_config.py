"""Frozen structure, proxy and submission parameters for the Jiewei gift box."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BoxSpec:
    width: float = 290.0
    depth: float = 230.0
    height: float = 75.0
    board_thickness: float = 2.0
    wrap_thickness: float = 0.18
    clearance: float = 0.6
    wei_travel: float = 42.0
    zhao_travel: float = 145.0
    moon_window_diameter: float = 108.0
    release_margin: float = 1.2


@dataclass(frozen=True)
class SKUProxySpec:
    width: float = 60.0
    depth: float = 60.0
    height: float = 35.0
    count: int = 6
    is_proxy: bool = True
    label: str = "规格代理件，非实际商品包装"


@dataclass(frozen=True)
class BoardSpec:
    width_px: int = 2480
    height_px: int = 3508
    dpi: int = 300
    count: int = 6
    max_bytes: int = 5_000_000


BOX = BoxSpec()
SKU = SKUProxySpec()
BOARD = BoardSpec()

COLORS = {
    "wall_ink": "#202F32",
    "moon_gold": "#C19A55",
    "route_red": "#A83B32",
    "mountain_green": "#586F66",
    "paper_white": "#EEE4D0",
    "soft_gray": "#858B86",
}

COPY = {
    "name": "解围",
    "english": "RELIEVE THE SIEGE",
    "category": "邯宝坊双节机关礼盒",
    "slogan": "侧移解锁，中央见礼",
    "proxy_label": SKU.label,
}


def state_offsets(state: str) -> dict[str, tuple[float, float, float]]:
    """Return configured part offsets for the three assembly states."""
    if state not in {"closed", "unlocked", "open"}:
        raise ValueError(f"unknown assembly state: {state}")
    wei = BOX.wei_travel if state in {"unlocked", "open"} else 0.0
    zhao = -BOX.zhao_travel if state == "open" else 0.0
    return {
        "outer_sleeve": (0.0, 0.0, 0.0),
        "wei_drawer": (wei, 0.0, 0.0),
        "lock_key_left": (wei, 0.0, 0.0),
        "lock_key_right": (wei, 0.0, 0.0),
        "zhao_tray": (0.0, zhao, 0.0),
        "inner_liner": (0.0, zhao, 0.0),
        "moon_disc": (0.0, 0.0, 0.0),
    }


def validate_spec() -> list[str]:
    errors: list[str] = []
    if (BOX.width, BOX.depth, BOX.height) != (290.0, 230.0, 75.0):
        errors.append("closed envelope changed")
    if not SKU.is_proxy or SKU.count != 6:
        errors.append("six neutral SKU proxies are required")
    if BOX.clearance <= 0 or BOX.board_thickness <= 0 or BOX.wrap_thickness <= 0:
        errors.append("material and clearance values must be positive")
    if BOX.wei_travel <= BOX.release_margin:
        errors.append("side travel cannot release the lock")
    if BOX.release_margin < 1.0:
        errors.append("release margin below 1 mm")
    if BOARD.count > 6:
        errors.append("board count exceeds Track 1 limit")
    return errors
