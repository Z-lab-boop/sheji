"""Build two competition-ready product posters from generated key visuals."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "sources"
OUTPUT_DIR = ROOT / "final"
PDF_OUTPUT_DIR = ROOT.parents[1] / "output/pdf"
WIDTH, HEIGHT = 2160, 3840

SERIF = (
    ROOT.parents[1]
    / "bubushengdian_design/01_research/fonts/NotoSerifSC[wght].ttf"
)
SANS = (
    ROOT.parents[1]
    / "bubushengdian_design/01_research/fonts/NotoSansSC[wght].ttf"
)


@dataclass(frozen=True)
class PosterSpec:
    source: str
    output: str
    title: str
    subtitle: str
    tagline: str
    descriptor: str
    chips: tuple[str, str, str]
    accent: str
    seal: str
    text_top: int


SPECS = (
    PosterSpec(
        source="bubushengdian_keyvisual.png",
        output="01_步步生典_产品海报.png",
        title="步步生典",
        subtitle="邯郸双节漫游章匣",
        tagline="一匣收城意 · 六章印旅程",
        descriptor="折叠地图 × 城市印章 × 抽拉收纳",
        chips=("165 × 120 × 30 mm", "6 枚主题印章", "参数化 CAD"),
        accent="#E4BD75",
        seal="邯郸",
        text_top=250,
    ),
    PosterSpec(
        source="jiewei_keyvisual.png",
        output="02_解围_产品海报.png",
        title="解围",
        subtitle="邯宝坊双节机关礼盒",
        tagline="以月为钥 · 抽启一城好礼",
        descriptor="侧抽解锁 × 中央展示 × 六礼同呈",
        chips=("290 × 230 × 75 mm", "三状态机关", "参数化 CAD"),
        accent="#E6C17B",
        seal="解围",
        text_top=250,
    ),
)


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def cover(image: Image.Image) -> Image.Image:
    scale = max(WIDTH / image.width, HEIGHT / image.height)
    size = (round(image.width * scale), round(image.height * scale))
    image = image.resize(size, Image.Resampling.LANCZOS)
    x = (image.width - WIDTH) // 2
    y = (image.height - HEIGHT) // 2
    return image.crop((x, y, x + WIDTH, y + HEIGHT)).convert("RGB")


def add_vertical_gradient(
    base: Image.Image,
    start_y: int,
    end_y: int,
    max_alpha: int,
    reverse: bool = False,
) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    span = max(1, end_y - start_y)
    for y in range(start_y, end_y):
        ratio = (y - start_y) / span
        if reverse:
            ratio = 1 - ratio
        alpha = round(max_alpha * ratio)
        draw.line((0, y, WIDTH, y), fill=(4, 14, 18, alpha), width=1)
    base.alpha_composite(overlay)


def draw_tracking_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    text_font: ImageFont.FreeTypeFont,
    fill: str,
    tracking: int,
) -> None:
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=text_font, fill=fill)
        bbox = draw.textbbox((x, y), char, font=text_font)
        x = bbox[2] + tracking


def rounded_panel(canvas: Image.Image, box: tuple[int, int, int, int]) -> None:
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle(
        box,
        radius=38,
        fill=(6, 22, 26, 188),
        outline=(230, 193, 123, 95),
        width=2,
    )
    layer = layer.filter(ImageFilter.GaussianBlur(0.35))
    canvas.alpha_composite(layer)


def build(spec: PosterSpec) -> Image.Image:
    source = Image.open(SOURCE_DIR / spec.source)
    image = cover(source)
    image = ImageEnhance.Color(image).enhance(0.94)
    image = ImageEnhance.Contrast(image).enhance(1.04)
    canvas = image.convert("RGBA")

    add_vertical_gradient(canvas, 0, 1260, 195, reverse=True)
    add_vertical_gradient(canvas, 2820, HEIGHT, 225)

    draw = ImageDraw.Draw(canvas)
    accent = spec.accent
    left = 160

    draw.rectangle((left, 170, left + 12, 710), fill=accent)
    draw_tracking_text(
        draw,
        (left + 58, 188),
        "中秋 × 国庆  ·  邯郸文化创意设计",
        font(SANS, 42),
        "#F0E7D7",
        5,
    )
    draw.text(
        (left + 50, spec.text_top + 65),
        spec.title,
        font=font(SERIF, 220),
        fill="#FFF7E8",
        stroke_width=1,
        stroke_fill="#FFF7E8",
    )
    draw.text(
        (left + 60, spec.text_top + 330),
        spec.subtitle,
        font=font(SANS, 68),
        fill=accent,
    )
    draw.line(
        (left + 60, spec.text_top + 450, left + 750, spec.text_top + 450),
        fill=accent,
        width=4,
    )

    seal_box = (WIDTH - 390, 220, WIDTH - 210, 400)
    draw.rounded_rectangle(
        seal_box,
        radius=14,
        fill=(140, 43, 35, 220),
        outline=(239, 202, 137, 210),
        width=4,
    )
    seal_font = font(SERIF, 70 if len(spec.seal) <= 2 else 54)
    seal_bbox = draw.textbbox((0, 0), spec.seal, font=seal_font)
    seal_w = seal_bbox[2] - seal_bbox[0]
    seal_h = seal_bbox[3] - seal_bbox[1]
    draw.text(
        ((seal_box[0] + seal_box[2] - seal_w) / 2,
         (seal_box[1] + seal_box[3] - seal_h) / 2 - seal_bbox[1]),
        spec.seal,
        font=seal_font,
        fill="#F9EBD2",
    )

    panel = (130, 3040, WIDTH - 130, 3650)
    rounded_panel(canvas, panel)
    draw = ImageDraw.Draw(canvas)
    draw.text((190, 3105), spec.tagline, font=font(SERIF, 92), fill="#FFF6E5")
    draw.text((194, 3238), spec.descriptor, font=font(SANS, 48), fill="#D9D7CC")

    chip_y = 3365
    x = 190
    for chip in spec.chips:
        chip_font = font(SANS, 38)
        bbox = draw.textbbox((0, 0), chip, font=chip_font)
        chip_w = bbox[2] - bbox[0] + 64
        draw.rounded_rectangle(
            (x, chip_y, x + chip_w, chip_y + 86),
            radius=43,
            fill="#122B2F",
            outline=accent,
            width=2,
        )
        draw.text((x + 32, chip_y + 17), chip, font=chip_font, fill="#F5E7CE")
        x += chip_w + 28

    draw_tracking_text(
        draw,
        (194, 3530),
        "CONCEPT DESIGN  ·  2026",
        font(SANS, 30),
        "#A9B1AE",
        5,
    )
    draw.text(
        (WIDTH - 700, 3520),
        "数字 CAD 已验证｜实体性能待打样",
        font=font(SANS, 30),
        fill="#A9B1AE",
    )

    return canvas.convert("RGB")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PDF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    posters: list[Image.Image] = []
    for spec in SPECS:
        poster = build(spec)
        poster.save(
            OUTPUT_DIR / spec.output,
            optimize=True,
            compress_level=9,
            dpi=(150, 150),
        )
        poster.save(
            OUTPUT_DIR / spec.output.replace(".png", ".jpg"),
            quality=94,
            subsampling=0,
            optimize=True,
            dpi=(150, 150),
        )
        posters.append(poster)

    posters[0].save(
        PDF_OUTPUT_DIR / "和氏璧杯_双节产品海报_打印版.pdf",
        save_all=True,
        append_images=posters[1:],
        resolution=150,
        quality=94,
    )

    preview_w = 720
    preview_h = round(HEIGHT * preview_w / WIDTH)
    gap = 36
    sheet = Image.new("RGB", (preview_w * 2 + gap, preview_h), "#0A1518")
    for index, poster in enumerate(posters):
        thumb = poster.resize((preview_w, preview_h), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (index * (preview_w + gap), 0))
    sheet.save(OUTPUT_DIR / "双海报预览.jpg", quality=92, optimize=True)

    for path in [*sorted(OUTPUT_DIR.iterdir()), PDF_OUTPUT_DIR / "和氏璧杯_双节产品海报_打印版.pdf"]:
        print(path)


if __name__ == "__main__":
    main()
