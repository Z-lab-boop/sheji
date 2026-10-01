import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CadReportTests(unittest.TestCase):
    def test_expected_parts_and_dimensions(self):
        report = json.loads(
            (ROOT / "03_cad/cad_report.json").read_text(encoding="utf-8")
        )
        self.assertEqual(report["assembly_bbox_mm"], [98.0, 65.0, 14.0])
        self.assertEqual(
            set(report["parts"]),
            {"outer_shell", "inner_tray", "lifter", "gold_accent", "card_proxy"},
        )
        for part in report["parts"].values():
            self.assertGreater(part["volume_mm3"], 0)
            self.assertEqual(len(part["sha256"]), 64)

    def test_exchange_files_exist(self):
        self.assertTrue((ROOT / "03_cad/suijian_card_case.FCStd").is_file())
        self.assertTrue((ROOT / "03_cad/suijian_card_case.step").is_file())
        for name in (
            "outer_shell",
            "inner_tray",
            "lifter",
            "gold_accent",
            "card_proxy",
        ):
            self.assertTrue((ROOT / f"03_cad/meshes/{name}.stl").is_file())


if __name__ == "__main__":
    unittest.main()
