import json
from pathlib import Path
import unittest

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "hero_closed.png": (2400, 2400),
    "hero_open.png": (2400, 2400),
    "interaction_01.png": (2400, 2400),
    "interaction_02.png": (2400, 2400),
    "interaction_03.png": (2400, 2400),
    "exploded.png": (2400, 2400),
    "detail_accent.png": (2400, 2400),
    "scale_view.png": (2400, 1800),
    "packaging_hero.png": (2400, 2400),
}


class RenderTests(unittest.TestCase):
    def test_images_are_rgba_and_nonempty(self):
        for name, size in EXPECTED.items():
            image = Image.open(ROOT / "04_renders" / name)
            self.assertEqual(image.size, size)
            self.assertEqual(image.mode, "RGBA")
            alpha = image.getchannel("A")
            self.assertIsNotNone(
                ImageChops.difference(alpha, Image.new("L", size, 0)).getbbox()
            )

    def test_manifest_uses_cad_hashes(self):
        manifest = json.loads(
            (ROOT / "04_renders/render_manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            set(manifest["mesh_sha256"]),
            {"outer_shell", "inner_tray", "lifter", "gold_accent", "card_proxy"},
        )


if __name__ == "__main__":
    unittest.main()
