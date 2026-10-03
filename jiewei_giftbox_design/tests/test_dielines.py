from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DielineTests(unittest.TestCase):
    def test_svg_and_dxf_pairs_exist(self):
        for stem in ("outer_sleeve", "wei_drawer", "zhao_tray", "lock_keys"):
            self.assertTrue((ROOT / "03_cad" / "dielines" / f"{stem}.svg").is_file())
            self.assertTrue((ROOT / "03_cad" / "dielines" / f"{stem}.dxf").is_file())

    def test_manifest_has_line_semantics(self):
        data = json.loads((ROOT / "03_cad" / "dielines" / "dieline_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(data["units"], "mm")
        self.assertEqual(data["layers"], {"cut": "#FF0000", "crease": "#0000FF", "glue": "#808080"})
        self.assertEqual(data["module_outer_mm"], [68.0, 62.0, 44.0])
        tray = (ROOT / "03_cad/dielines/zhao_tray.svg").read_text(encoding="utf-8")
        self.assertNotIn("真实 SKU 到位后重算", tray)


if __name__ == "__main__":
    unittest.main()
