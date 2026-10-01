from pathlib import Path
import json
import unittest
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("hero_closed.png", "hero_unlocked.png", "hero_open.png", "exploded.png", "mid_autumn_variant.png", "national_day_variant.png")


class RenderTests(unittest.TestCase):
    def test_required_images_are_visible(self):
        for name in REQUIRED:
            with Image.open(ROOT / "04_renders" / name) as image:
                self.assertEqual(image.size, (1800, 1400))
                self.assertEqual(image.mode, "RGBA")
                self.assertIsNotNone(ImageChops.difference(image.getchannel("A"), Image.new("L", image.size, 0)).getbbox())

    def test_manifest_discloses_proxy_products(self):
        data = json.loads((ROOT / "04_renders" / "render_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(data["product_asset_status"], "neutral_size_proxy")
        self.assertEqual(data["geometry_basis"], "audited STL")


if __name__ == "__main__":
    unittest.main()
