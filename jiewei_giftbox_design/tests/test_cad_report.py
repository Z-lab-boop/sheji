from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CadReportTests(unittest.TestCase):
    def test_closed_envelope_and_parts(self):
        report = json.loads((ROOT / "03_cad" / "cad_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["closed_bbox_mm"], [290.0, 230.0, 75.0])
        self.assertEqual(len(report["parts"]), 13)
        self.assertTrue(all(part["valid"] and part["solid_count"] == 1 for part in report["parts"].values()))

    def test_release_margin(self):
        report = json.loads((ROOT / "03_cad" / "cad_report.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(report["release_margin_mm"], 1.0)

    def test_three_step_files_exist(self):
        for state in ("closed", "unlocked", "open"):
            self.assertTrue((ROOT / "03_cad" / f"jiewei_giftbox_{state}.step").is_file())

    def test_six_concept_modules_are_modelled(self):
        report = json.loads((ROOT / "03_cad" / "cad_report.json").read_text(encoding="utf-8"))
        modules = [value for key, value in report["parts"].items() if key.startswith("concept_module_")]
        self.assertEqual(len(modules), 6)
        self.assertTrue(all(item["bbox_mm"] == [68.0, 62.0, 44.8] for item in modules))
        self.assertEqual(report["product_asset_status"], "original_concept_secondary_packaging")


if __name__ == "__main__":
    unittest.main()
