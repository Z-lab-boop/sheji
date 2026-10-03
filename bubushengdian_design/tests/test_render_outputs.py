from pathlib import Path
import json
import unittest

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "hero_closed.png": (1800, 1400),
    "hero_open.png": (1800, 1400),
    "map_unfolded.png": (1800, 1400),
    "stamp_grid.png": (1800, 1400),
    "exploded.png": (1800, 1600),
    "ortho_top.png": (1800, 1200),
    "ortho_front.png": (1800, 1200),
    "scale_view.png": (1800, 1400),
    "interaction_01.png": (1800, 1400),
    "interaction_02.png": (1800, 1400),
    "interaction_03.png": (1800, 1400),
    "interaction_04.png": (1800, 1400),
}


class RenderTests(unittest.TestCase):
    def test_required_images_are_visible_rgba(self):
        for name, size in REQUIRED.items():
            with Image.open(ROOT / "04_renders" / name) as image:
                self.assertEqual(image.size, size)
                self.assertEqual(image.mode, "RGBA")
                alpha = image.getchannel("A")
                self.assertIsNotNone(
                    ImageChops.difference(alpha, Image.new("L", size, 0)).getbbox()
                )

    def test_manifest_binds_cad_hashes(self):
        data = json.loads(
            (ROOT / "04_renders" / "render_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(len(data["cad_mesh_sha256"]), 10)
        self.assertEqual(data["geometry_basis"], "audited STL")
        self.assertEqual(set(data["views"]), set(REQUIRED))


if __name__ == "__main__":
    unittest.main()
