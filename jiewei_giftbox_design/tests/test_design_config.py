from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from design_config import BOARD, BOX, SKU, state_offsets, validate_spec


class DesignConfigTests(unittest.TestCase):
    def test_box_contract(self):
        self.assertEqual((BOX.width, BOX.depth, BOX.height), (290.0, 230.0, 75.0))
        self.assertEqual((BOX.wei_travel, BOX.zhao_travel, BOX.moon_window_diameter), (42.0, 145.0, 108.0))
        self.assertEqual((BOX.board_thickness, BOX.wrap_thickness, BOX.clearance), (2.0, 0.18, 0.6))

    def test_proxy_contract_is_explicit(self):
        self.assertEqual((SKU.width, SKU.depth, SKU.height, SKU.count), (60.0, 60.0, 35.0, 6))
        self.assertTrue(SKU.is_proxy)
        self.assertEqual(SKU.label, "规格代理件，非实际商品包装")

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
