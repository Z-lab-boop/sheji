from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from design_config import BOARD, COLORS, COPY, PRODUCT, validate_spec


class DesignConfigTests(unittest.TestCase):
    def test_product_baseline(self):
        self.assertEqual(
            (PRODUCT.width, PRODUCT.height, PRODUCT.depth),
            (98.0, 65.0, 14.0),
        )
        self.assertEqual(PRODUCT.corner_radius, 8.0)
        self.assertEqual(PRODUCT.travel, 28.0)
        self.assertEqual(PRODUCT.lift, 7.0)

    def test_board_submission_contract(self):
        self.assertEqual(
            (BOARD.width_px, BOARD.height_px, BOARD.dpi),
            (2480, 3508, 300),
        )
        self.assertEqual(BOARD.count, 7)
        self.assertEqual(BOARD.max_bytes, 5_000_000)

    def test_palette_and_copy_are_frozen(self):
        self.assertEqual(COLORS["zhao_lacquer"], "#0D2F32")
        self.assertEqual(COLORS["ding_gold"], "#B68B48")
        self.assertEqual(COPY["name_zh"], "遂见")
        self.assertEqual(COPY["tagline"], "让才能，被看见")
        self.assertEqual(validate_spec(), [])


if __name__ == "__main__":
    unittest.main()
