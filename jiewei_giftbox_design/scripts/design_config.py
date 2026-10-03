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
class ProductModuleSpec:
    width: float = 68.0
    depth: float = 62.0
    height: float = 44.0
    count: int = 6
    is_concept: bool = True


@dataclass(frozen=True)
class ProductConcept:
    code: str
    category: str
    display_name: str
    color: str


@dataclass(frozen=True)
class BoardSpec:
    width_px: int = 2480
    height_px: int = 3508
    dpi: int = 300
    count: int = 6
    max_bytes: int = 5_000_000


BOX = BoxSpec()
PRODUCT_MODULE = ProductModuleSpec()
CONCEPT_DISCLOSURE = "概念包装建议规格，投产前复核"
PRODUCTS = (
    ProductConcept("A", "鸡泽辣椒", "椒起鸡泽", "#A83B32"),
    ProductConcept("B", "魏县鸭梨", "梨润魏州", "#819B79"),
    ProductConcept("C", "涉县核桃", "核藏太行", "#80644B"),
    ProductConcept("D", "武安小米", "粟映武安", "#C19A55"),
    ProductConcept("E", "永年大蒜", "蒜生永年", "#EEE4D0"),
    ProductConcept("F", "大名小磨香油", "油香大名", "#B97832"),
)
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
    "category": "邯宝坊“六味邯郸”机关礼盒概念提案",
    "slogan": "侧移解锁，中央见礼",
    "concept_disclosure": CONCEPT_DISCLOSURE,
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
    if (
        not PRODUCT_MODULE.is_concept
        or (PRODUCT_MODULE.width, PRODUCT_MODULE.depth, PRODUCT_MODULE.height, PRODUCT_MODULE.count)
        != (68.0, 62.0, 44.0, 6)
    ):
        errors.append("six frozen concept modules are required")
    if len(PRODUCTS) != PRODUCT_MODULE.count or len({item.category for item in PRODUCTS}) != PRODUCT_MODULE.count:
        errors.append("six unique regional product concepts are required")
    if BOX.clearance <= 0 or BOX.board_thickness <= 0 or BOX.wrap_thickness <= 0:
        errors.append("material and clearance values must be positive")
    if BOX.wei_travel <= BOX.release_margin:
        errors.append("side travel cannot release the lock")
    if BOX.release_margin < 1.0:
        errors.append("release margin below 1 mm")
    if BOARD.count > 6:
        errors.append("board count exceeds Track 1 limit")
    return errors
