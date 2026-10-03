from pathlib import Path
import json
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


class IdentityTests(unittest.TestCase):
    def test_editable_svg_assets(self):
        for name in ("wordmark.svg", "stamp_faces.svg", "folding_map.svg"):
            path = ROOT / "02_identity" / name
            self.assertTrue(path.is_file())
            root = ET.parse(path).getroot()
            self.assertTrue(root.tag.endswith("svg"))
            self.assertGreater(path.stat().st_size, 1000)

    def test_manifest_contract(self):
        data = json.loads(
            (ROOT / "02_identity" / "identity_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(len(data["stamp_ids"]), 6)
        self.assertEqual(data["route_disclaimer"], "文化路线示意")
        self.assertEqual(data["palette"]["city_blue"], "#173B46")
        self.assertEqual(data["stamp_face_mm"], [26, 26])


if __name__ == "__main__":
    unittest.main()
