from pathlib import Path
import subprocess
import unittest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


class BoardTests(unittest.TestCase):
    def test_six_jpgs_meet_submission_contract(self):
        for index in range(1, 7):
            path = ROOT / "05_boards" / "jpg" / f"board_{index:02d}.jpg"
            with Image.open(path) as image:
                self.assertEqual(image.size, (2480, 3508))
                self.assertEqual(image.mode, "RGB")
                self.assertEqual(round(image.info["dpi"][0]), 300)
            self.assertLess(path.stat().st_size, 5_000_000)

    def test_six_pdfs_are_single_page_a4(self):
        for index in range(1, 7):
            path = ROOT / "05_boards" / "pdf" / f"board_{index:02d}.pdf"
            info = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True).stdout
            self.assertIn("Pages:           1", info)
            self.assertIn("A4", info)

    def test_board_copy_matches_concept_submission(self):
        joined = "\n".join(
            (ROOT / f"05_boards/src/board_{index:02d}.svg").read_text(encoding="utf-8")
            for index in range(1, 7)
        )
        for token in ("六味邯郸", "椒起鸡泽", "梨润魏州", "核藏太行", "粟映武安", "蒜生永年", "油香大名"):
            self.assertIn(token, joined)
        self.assertIn("概念包装建议规格，投产前复核", joined)
        for prohibited in ("目前不能正式投稿", "BLOCKED", "真实 SKU", "待授权资产"):
            self.assertNotIn(prohibited, joined)


if __name__ == "__main__":
    unittest.main()
