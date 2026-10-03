from pathlib import Path
import json
import unittest
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "hero_closed.png",
    "hero_unlocked.png",
    "hero_open.png",
    "exploded.png",
    "product_family.png",
    "hand_opening.png",
    "retail_scene.png",
    "mid_autumn_variant.png",
    "national_day_variant.png",
)


class RenderTests(unittest.TestCase):
    def test_required_images_are_visible(self):
        for name in REQUIRED:
            with Image.open(ROOT / "04_renders" / name) as image:
                self.assertEqual(image.size, (1800, 1400))
                self.assertEqual(image.mode, "RGBA")
                self.assertIsNotNone(ImageChops.difference(image.getchannel("A"), Image.new("L", image.size, 0)).getbbox())

    def test_manifest_discloses_concept_products(self):
        data = json.loads((ROOT / "04_renders" / "render_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(data["product_asset_status"], "original_concept_secondary_packaging")
        self.assertEqual(data["geometry_basis"], "audited STL from concept_v2 CAD")
        self.assertEqual(data["scene_status"], "visualisation_not_product_photography")


if __name__ == "__main__":
    unittest.main()
