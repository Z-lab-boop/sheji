from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from design_config import (  # noqa: E402
    BOARD,
    COLORS,
    PRODUCT,
    STAMP_NAMES,
    motion_offsets,
    validate_spec,
)


class DesignConfigTests(unittest.TestCase):
    def test_frozen_product_contract(self):
        self.assertEqual(
            (PRODUCT.width, PRODUCT.depth, PRODUCT.height),
            (165.0, 120.0, 30.0),
        )
        self.assertEqual(PRODUCT.wall, 1.8)
        self.assertEqual(PRODUCT.clearance, 0.35)
        self.assertEqual(PRODUCT.travel, 92.0)

    def test_stamp_contract(self):
        self.assertEqual(len(STAMP_NAMES), 6)
        self.assertEqual(
            (PRODUCT.stamp_width, PRODUCT.stamp_depth, PRODUCT.stamp_height),
            (32.0, 32.0, 23.0),
        )
        self.assertEqual(PRODUCT.stamp_face, 26.0)

    def test_board_contract(self):
        self.assertEqual(
            (BOARD.width_px, BOARD.height_px, BOARD.dpi, BOARD.count),
            (2480, 3508, 300, 8),
        )
        self.assertEqual(BOARD.max_bytes, 5_000_000)

    def test_motion_is_clamped(self):
        self.assertEqual(motion_offsets(-1.0)["stamp_tray"], (0.0, 0.0))
        self.assertEqual(motion_offsets(2.0)["stamp_tray"], (92.0, 0.0))
        self.assertEqual(motion_offsets(1.0)["outer_case"], (0.0, 0.0))

    def test_spec_has_no_violations(self):
        self.assertEqual(validate_spec(), [])

    def test_palette_supports_differentiated_identity(self):
        self.assertEqual(COLORS["city_blue"], "#173B46")
        self.assertEqual(COLORS["seal_red"], "#B23A32")


if __name__ == "__main__":
    unittest.main()
