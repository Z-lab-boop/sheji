import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ASSETS = (
    "wordmark.svg",
    "identity_card.svg",
    "portfolio_cards.svg",
    "packaging_dieline.svg",
)


class IdentityTests(unittest.TestCase):
    def test_svg_assets_are_editable(self):
        for name in ASSETS:
            path = ROOT / "02_identity" / name
            root = ET.parse(path).getroot()
            self.assertIn("viewBox", root.attrib)
            self.assertNotIn("data:image", path.read_text(encoding="utf-8"))

    def test_manifest_records_palette_and_fonts(self):
        data = json.loads(
            (ROOT / "02_identity/identity_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(data["colors"]["zhao_lacquer"], "#0D2F32")
        self.assertEqual(
            set(data["fonts"]),
            {"Noto Sans SC", "Noto Serif SC", "Inter"},
        )


if __name__ == "__main__":
    unittest.main()
