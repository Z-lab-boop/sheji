"""Build a high-resolution visual-review contact sheet from all boards."""

import json
from pathlib import Path

from PIL import Image, ImageDraw


PROJECT_DIR = Path(__file__).resolve().parents[1]
BOARD_DIR = PROJECT_DIR / "05_boards"
THUMB_W = 600
THUMB_H = round(THUMB_W * 3508 / 2480)
GAP = 46
MARGIN = 64
COLUMNS = 3
ROWS = 3


def main() -> None:
    canvas = Image.new(
        "RGB",
        (
            MARGIN * 2 + COLUMNS * THUMB_W + (COLUMNS - 1) * GAP,
            MARGIN * 2 + ROWS * THUMB_H + (ROWS - 1) * GAP,
        ),
        "#173B46",
    )
    draw = ImageDraw.Draw(canvas)
    manifest = json.loads(
        (BOARD_DIR / "src" / "board_manifest.json").read_text(encoding="utf-8")
    )
    for index in range(1, manifest["count"] + 1):
        image = Image.open(BOARD_DIR / "jpg" / f"board_{index:02d}.jpg").convert("RGB")
        image.thumbnail((THUMB_W, THUMB_H), Image.Resampling.LANCZOS)
        column = (index - 1) % COLUMNS
        row = (index - 1) // COLUMNS
        x = MARGIN + column * (THUMB_W + GAP)
        y = MARGIN + row * (THUMB_H + GAP)
        canvas.paste(image, (x, y))
        draw.rectangle(
            (x, y, x + image.width - 1, y + image.height - 1),
            outline="#C29A55",
            width=4,
        )
    output = BOARD_DIR / "contact_sheet.jpg"
    canvas.save(output, quality=92, dpi=(150, 150), optimize=True)
    print(f"created {output} {canvas.size[0]}x{canvas.size[1]}")


if __name__ == "__main__":
    main()
