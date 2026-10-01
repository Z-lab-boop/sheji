"""Frozen design constants shared by CAD, renders, boards, and audits."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductSpec:
    width: float = 98.0
    height: float = 65.0
    depth: float = 14.0
    corner_radius: float = 8.0
    wall: float = 1.8
    clearance: float = 0.35
    travel: float = 28.0
    lift: float = 7.0
    card_width: float = 90.0
    card_height: float = 54.0
    card_thickness: float = 0.30


@dataclass(frozen=True)
class BoardSpec:
    width_px: int = 2480
    height_px: int = 3508
    dpi: int = 300
    count: int = 7
    max_bytes: int = 5_000_000


PRODUCT = ProductSpec()
BOARD = BoardSpec()

COLORS = {
    "zhao_lacquer": "#0D2F32",
    "ding_gold": "#B68B48",
    "oath_vermilion": "#A64032",
    "silk_white": "#E8DFCC",
    "ink_black": "#16191A",
}

COPY = {
    "name_zh": "遂见",
    "name_en": "SUIJIAN",
    "category": "毛遂自荐青年名片匣",
    "tagline": "让才能，被看见",
    "culture_line": "锥处囊中，颖自见",
}


def validate_spec() -> list[str]:
    """Return violations of immutable product and submission constraints."""
    errors: list[str] = []
    if PRODUCT.wall <= PRODUCT.clearance:
        errors.append("wall must be greater than clearance")
    if PRODUCT.card_width + 2 * PRODUCT.clearance >= PRODUCT.width:
        errors.append("card width does not fit enclosure")
    if not 0 < PRODUCT.lift < PRODUCT.depth:
        errors.append("lift must fit product depth")
    if BOARD.count > 8:
        errors.append("board count exceeds competition limit")
    return errors

