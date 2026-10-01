from pathlib import Path
import subprocess
import unittest
import xml.etree.ElementTree as ET

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


class BoardTests(unittest.TestCase):
    def test_jpg_contract(self):
        for index in range(1, 9):
            path = ROOT / "05_boards" / "jpg" / f"board_{index:02d}.jpg"
            with Image.open(path) as image:
                self.assertEqual(image.size, (2480, 3508))
                self.assertEqual(image.mode, "RGB")
                self.assertEqual(round(image.info["dpi"][0]), 300)
            self.assertLess(path.stat().st_size, 5_000_000)

    def test_pdf_contract(self):
        for index in range(1, 9):
            path = ROOT / "05_boards" / "pdf" / f"board_{index:02d}.pdf"
            info = subprocess.run(
                ["pdfinfo", str(path)], check=True, capture_output=True, text=True
            ).stdout
            self.assertIn("Pages:           1", info)
            self.assertIn("A4", info)

    def test_editable_sources_exist(self):
        for index in range(1, 9):
            path = ROOT / "05_boards" / "src" / f"board_{index:02d}.svg"
            self.assertTrue(path.is_file())
            root = ET.parse(path).getroot()
            elements = list(root.iter())
            self.assertTrue(root.tag.endswith("svg"))
            self.assertGreater(len(elements), 20)
            self.assertTrue(any(element.tag.endswith("text") for element in elements))
            image_count = sum(element.tag.endswith("image") for element in elements)
            path_count = sum(element.tag.endswith("path") for element in elements)
            self.assertTrue(image_count >= 1 or path_count >= 3)


if __name__ == "__main__":
    unittest.main()
