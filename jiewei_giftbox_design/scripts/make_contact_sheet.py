"""Build a review-only contact sheet from the six submission JPGs."""

from pathlib import Path
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
inputs = sorted((ROOT / "05_boards/jpg").glob("board_*.jpg"))
if len(inputs) != 6:
    raise SystemExit(f"expected 6 boards, found {len(inputs)}")
thumbs = []
for path in inputs:
    image = Image.open(path).convert("RGB")
    image.thumbnail((620, 877))
    thumbs.append(ImageOps.pad(image, (620, 877), color="#EEE4D0"))
sheet = Image.new("RGB", (2020, 1844), "#202F32")
for index, image in enumerate(thumbs):
    sheet.paste(image, (40 + (index % 3) * 660, 35 + (index // 3) * 900))
out = ROOT / "05_boards/contact_sheet.jpg"
sheet.save(out, quality=90, dpi=(150, 150))
print(f"created {out} {sheet.width}x{sheet.height}")
