from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from design_config import (
    BOARD,
    BOX,
    CONCEPT_DISCLOSURE,
    PRODUCT_MODULE,
    PRODUCTS,
    state_offsets,
    validate_spec,
)


class DesignConfigTests(unittest.TestCase):
    def test_box_contract(self):
        self.assertEqual((BOX.width, BOX.depth, BOX.height), (290.0, 230.0, 75.0))
        self.assertEqual((BOX.wei_travel, BOX.zhao_travel, BOX.moon_window_diameter), (42.0, 145.0, 108.0))
        self.assertEqual((BOX.board_thickness, BOX.wrap_thickness, BOX.clearance), (2.0, 0.18, 0.6))

    def test_concept_product_contract(self):
        self.assertEqual(
            (PRODUCT_MODULE.width, PRODUCT_MODULE.depth, PRODUCT_MODULE.height, PRODUCT_MODULE.count),
            (68.0, 62.0, 44.0, 6),
        )
        self.assertTrue(PRODUCT_MODULE.is_concept)
        self.assertEqual(len(PRODUCTS), 6)
        self.assertEqual(
            [item.category for item in PRODUCTS],
            ["鸡泽辣椒", "魏县鸭梨", "涉县核桃", "武安小米", "永年大蒜", "大名小磨香油"],
        )
        self.assertEqual(CONCEPT_DISCLOSURE, "概念包装建议规格，投产前复核")

    def test_state_contract(self):
        self.assertEqual(state_offsets("closed")["wei_drawer"], (0.0, 0.0, 0.0))
        self.assertEqual(state_offsets("unlocked")["wei_drawer"], (42.0, 0.0, 0.0))
        self.assertEqual(state_offsets("open")["zhao_tray"], (0.0, -145.0, 0.0))

    def test_board_contract(self):
        self.assertEqual((BOARD.width_px, BOARD.height_px, BOARD.dpi, BOARD.count), (2480, 3508, 300, 6))

    def test_spec_has_no_violations(self):
        self.assertEqual(validate_spec(), [])


if __name__ == "__main__":
    unittest.main()
