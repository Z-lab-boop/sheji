from pathlib import Path
import unittest

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


class BoardTests(unittest.TestCase):
    def test_all_submission_jpegs(self):
        for index in range(1, 8):
            path = ROOT / f"05_boards/jpg/board_{index:02d}.jpg"
            with Image.open(path) as image:
                self.assertEqual(image.size, (2480, 3508))
                self.assertEqual(image.mode, "RGB")
                self.assertEqual(round(image.info.get("dpi", (0, 0))[0]), 300)
            self.assertLess(path.stat().st_size, 5_000_000)

    def test_sources_and_pdfs_exist(self):
        for index in range(1, 8):
            self.assertTrue(
                (ROOT / f"05_boards/src/board_{index:02d}.svg").is_file()
            )
            self.assertTrue(
                (ROOT / f"05_boards/pdf/board_{index:02d}.pdf").is_file()
            )


if __name__ == "__main__":
    unittest.main()
