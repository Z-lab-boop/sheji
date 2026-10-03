from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CadReportTests(unittest.TestCase):
    def test_expected_parts_and_envelope(self):
        report = json.loads(
            (ROOT / "03_cad" / "cad_report.json").read_text(encoding="utf-8")
        )
        self.assertEqual(report["assembly_bbox_mm"], [165.0, 120.0, 30.0])
        self.assertEqual(len(report["parts"]), 10)
        self.assertTrue(
            all(
                part["valid"] and part["solid_count"] == 1
                for part in report["parts"].values()
            )
        )

    def test_exchange_files_exist(self):
        self.assertTrue(
            (ROOT / "03_cad" / "bubushengdian_stamp_kit.FCStd").is_file()
        )
        self.assertTrue(
            (ROOT / "03_cad" / "bubushengdian_stamp_kit.step").is_file()
        )
        self.assertEqual(len(list((ROOT / "03_cad" / "meshes").glob("*.stl"))), 10)

    def test_report_records_folded_map_proxy(self):
        report = json.loads(
            (ROOT / "03_cad" / "cad_report.json").read_text(encoding="utf-8")
        )
        self.assertEqual(report["folded_map_proxy_mm"], [155.0, 110.0, 1.2])
        self.assertEqual(report["unfolded_map_artwork_mm"], [480.0, 330.0])


if __name__ == "__main__":
    unittest.main()
