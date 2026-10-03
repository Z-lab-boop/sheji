from pathlib import Path
import json
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class IdentityTests(unittest.TestCase):
    def test_all_svg_assets_are_editable(self):
        names = ("wordmark.svg", "mid_autumn_sleeve.svg", "national_day_sleeve.svg", "concept_product_labels.svg")
        for name in names:
            path = ROOT / "02_identity" / name
            self.assertTrue(path.is_file())
            self.assertTrue(ET.parse(path).getroot().tag.endswith("svg"))

    def test_concept_labels_and_manifest(self):
        text = (ROOT / "02_identity" / "concept_product_labels.svg").read_text(encoding="utf-8")
        for name in ("椒起鸡泽", "梨润魏州", "核藏太行", "粟映武安", "蒜生永年", "油香大名"):
            self.assertIn(name, text)
        self.assertIn("概念包装建议规格，投产前复核", text)
        manifest = json.loads((ROOT / "02_identity" / "identity_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["brand_asset_status"], "official_brief_named_target_no_logo_asset")
        self.assertEqual(manifest["product_asset_status"], "original_concept_secondary_packaging")


if __name__ == "__main__":
    unittest.main()
