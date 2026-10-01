from pathlib import Path
import json
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class IdentityTests(unittest.TestCase):
    def test_all_svg_assets_are_editable(self):
        names = ("wordmark.svg", "mid_autumn_sleeve.svg", "national_day_sleeve.svg", "proxy_product_labels.svg")
        for name in names:
            path = ROOT / "02_identity" / name
            self.assertTrue(path.is_file())
            self.assertTrue(ET.parse(path).getroot().tag.endswith("svg"))

    def test_proxy_disclosure_is_embedded(self):
        text = (ROOT / "02_identity" / "proxy_product_labels.svg").read_text(encoding="utf-8")
        self.assertIn("规格代理件，非实际商品包装", text)
        manifest = json.loads((ROOT / "02_identity" / "identity_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["brand_asset_status"], "not_provided")


if __name__ == "__main__":
    unittest.main()
