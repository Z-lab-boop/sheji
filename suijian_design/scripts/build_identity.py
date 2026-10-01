"""Generate the editable Suijian identity, card, and packaging SVG assets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from xml.sax.saxutils import escape


PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "02_identity"
FONT_DIR = PROJECT_DIR / "01_research" / "fonts"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from design_config import COLORS, COPY, PRODUCT


FONT_CSS = """
@font-face { font-family: 'Noto Sans SC'; src: url('../01_research/fonts/NotoSansSC%5Bwght%5D.ttf'); }
@font-face { font-family: 'Noto Serif SC'; src: url('../01_research/fonts/NotoSerifSC%5Bwght%5D.ttf'); }
@font-face { font-family: 'Inter'; src: url('../01_research/fonts/InterVariable.ttf'); }
.sans { font-family: 'Noto Sans SC', sans-serif; }
.serif { font-family: 'Noto Serif SC', serif; }
.latin { font-family: 'Inter', sans-serif; letter-spacing: .12em; }
""".strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def svg_document(view_box: str, body: str, title: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}" role="img" aria-labelledby="title desc">
  <title id="title">{escape(title)}</title>
  <desc id="desc">Editable vector artwork for the Suijian cultural product system.</desc>
  <style>{FONT_CSS}</style>
  {body}
</svg>
"""


def custom_mark(x: float, y: float, scale: float = 1.0, dark: bool = True) -> str:
    """Draw an original mark combining movement, sight, and a 17-degree point."""
    base = COLORS["silk_white"] if dark else COLORS["zhao_lacquer"]
    gold = COLORS["ding_gold"]
    red = COLORS["oath_vermilion"]
    return f"""
<g id="suijian-custom-mark" transform="translate({x} {y}) scale({scale})" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <path d="M28 176 C68 126 93 137 118 112 L206 112" stroke="{gold}" stroke-width="18"/>
  <path d="M26 196 C82 230 156 234 230 202" stroke="{base}" stroke-width="17"/>
  <path d="M114 40 H216 V164 M142 40 V132 H188 V40 M145 164 L125 205 M190 164 L218 202" stroke="{base}" stroke-width="16"/>
  <path d="M74 62 L238 14" stroke="{gold}" stroke-width="9"/>
  <circle cx="238" cy="14" r="9" fill="{red}" stroke="none"/>
</g>
"""


def build_wordmark() -> str:
    body = f"""
<rect width="1200" height="420" rx="36" fill="{COLORS['zhao_lacquer']}"/>
<path d="M0 335 L1200 335" stroke="{COLORS['ding_gold']}" stroke-width="2" opacity=".42"/>
{custom_mark(70, 70, 1.15, True)}
<g id="custom-lettering" transform="translate(390 78)">
  <text class="serif" x="0" y="170" fill="{COLORS['silk_white']}" font-size="158" font-weight="720" letter-spacing="18">{COPY['name_zh']}</text>
  <path d="M12 198 L372 90" stroke="{COLORS['ding_gold']}" stroke-width="7" opacity=".95"/>
  <circle cx="373" cy="90" r="8" fill="{COLORS['oath_vermilion']}"/>
</g>
<text class="latin" x="792" y="170" fill="{COLORS['ding_gold']}" font-size="38" font-weight="620">{COPY['name_en']}</text>
<text class="sans" x="793" y="228" fill="{COLORS['silk_white']}" font-size="30" font-weight="350" letter-spacing="5">让才能，被看见</text>
<text class="serif" x="70" y="378" fill="{COLORS['silk_white']}" font-size="20" opacity=".70" letter-spacing="3">锥处囊中，颖自见</text>
<text class="latin" x="1140" y="378" text-anchor="end" fill="{COLORS['silk_white']}" font-size="15" opacity=".52">HANDAN · 2026</text>
"""
    return svg_document("0 0 1200 420", body, "遂见品牌字标")


def demo_grid(x: int, y: int, module: int = 14) -> str:
    """Create a visibly labelled, intentionally non-scannable demo matrix."""
    rects: list[str] = []
    for row in range(17):
        for column in range(17):
            finder = (
                (row < 5 and column < 5)
                or (row < 5 and column > 11)
                or (row > 11 and column < 5)
            )
            noise = ((row * 11 + column * 7 + row * column) % 9) in {0, 2, 5}
            if finder or noise:
                rects.append(
                    f'<rect x="{x + column * module}" y="{y + row * module}" width="{module - 2}" height="{module - 2}" rx="1"/>'
                )
    return "\n".join(rects)


def card_front(x: int, y: int) -> str:
    return f"""
<g id="identity-card-front" transform="translate({x} {y})">
  <rect width="900" height="540" rx="42" fill="{COLORS['zhao_lacquer']}"/>
  <path d="M-40 465 L940 174" stroke="{COLORS['ding_gold']}" stroke-width="12"/>
  <circle cx="840" cy="145" r="13" fill="{COLORS['oath_vermilion']}"/>
  {custom_mark(58, 48, .46, True)}
  <text class="serif" x="58" y="334" fill="{COLORS['silk_white']}" font-size="67" font-weight="680" letter-spacing="8">林知行</text>
  <text class="latin" x="60" y="382" fill="{COLORS['ding_gold']}" font-size="20" font-weight="620">LIN ZHIXING</text>
  <text class="sans" x="60" y="430" fill="{COLORS['silk_white']}" font-size="24" font-weight="350" letter-spacing="4">青年创作者</text>
  <text class="latin" x="60" y="470" fill="{COLORS['silk_white']}" font-size="15" opacity=".62">YOUNG CREATOR · PORTFOLIO 2026</text>
  <text class="latin" x="842" y="488" text-anchor="end" fill="{COLORS['silk_white']}" font-size="14" opacity=".48">DEMO IDENTITY</text>
</g>
"""


def card_back(x: int, y: int) -> str:
    matrix = demo_grid(600, 132, 14)
    return f"""
<g id="identity-card-back" transform="translate({x} {y})">
  <rect width="900" height="540" rx="42" fill="{COLORS['silk_white']}" stroke="{COLORS['zhao_lacquer']}" stroke-width="3"/>
  <path d="M58 85 H405" stroke="{COLORS['ding_gold']}" stroke-width="9"/>
  <text class="serif" x="58" y="176" fill="{COLORS['zhao_lacquer']}" font-size="50" font-weight="650">让作品先开口</text>
  <text class="sans" x="58" y="230" fill="{COLORS['ink_black']}" font-size="24" opacity=".76">轻触 NFC 或扫描演示矩阵</text>
  <text class="sans" x="58" y="286" fill="{COLORS['zhao_lacquer']}" font-size="22" font-weight="560">视觉叙事 · 产品系统 · 数字体验</text>
  <text class="latin" x="58" y="455" fill="{COLORS['ink_black']}" font-size="14" opacity=".58">NO PERSONAL DATA · NON-SCANNABLE DEMO</text>
  <g fill="{COLORS['zhao_lacquer']}">{matrix}</g>
  <rect x="625" y="245" width="185" height="48" rx="24" fill="{COLORS['oath_vermilion']}"/>
  <text class="latin" x="718" y="276" text-anchor="middle" fill="white" font-size="17" font-weight="700">DEMO</text>
</g>
"""


def build_identity_card() -> str:
    body = f"""
<rect width="2000" height="700" fill="#F4F0E7"/>
{card_front(70, 80)}
{card_back(1030, 80)}
<text class="latin" x="70" y="655" fill="{COLORS['ink_black']}" font-size="16" opacity=".56">90 × 54 mm · FRONT / BACK · FICTIONAL DEMO IDENTITY</text>
"""
    return svg_document("0 0 2000 700", body, "遂见数字身份卡正反面")


def build_portfolio_cards() -> str:
    labels = (
        ("01", "视觉叙事", "VISUAL STORY", "M64 394 C215 160 425 118 780 92"),
        ("02", "产品系统", "PRODUCT SYSTEM", "M62 120 H800 M62 238 H660 M62 356 H520"),
        ("03", "数字体验", "DIGITAL EXPERIENCE", "M78 420 C160 80 620 54 795 340"),
    )
    cards: list[str] = []
    for index, (number, title, english, path) in enumerate(labels):
        x = 60 + index * 940
        fill = COLORS["zhao_lacquer"] if index != 1 else COLORS["silk_white"]
        foreground = COLORS["silk_white"] if index != 1 else COLORS["zhao_lacquer"]
        cards.append(
            f"""
<g id="portfolio-card-{number}" transform="translate({x} 70)">
  <rect width="880" height="528" rx="38" fill="{fill}" stroke="{COLORS['ding_gold']}" stroke-width="3"/>
  <path d="{path}" fill="none" stroke="{COLORS['ding_gold']}" stroke-width="18" stroke-linecap="round" opacity=".82"/>
  <circle cx="{760 - index * 65}" cy="{106 + index * 104}" r="16" fill="{COLORS['oath_vermilion']}"/>
  <text class="latin" x="58" y="86" fill="{COLORS['ding_gold']}" font-size="20" font-weight="700">{number}</text>
  <text class="serif" x="58" y="430" fill="{foreground}" font-size="58" font-weight="680">{title}</text>
  <text class="latin" x="60" y="476" fill="{foreground}" font-size="15" opacity=".62">{english}</text>
</g>
"""
        )
    body = f"""
<rect width="2940" height="680" fill="#F4F0E7"/>
{''.join(cards)}
<text class="latin" x="60" y="646" fill="{COLORS['ink_black']}" font-size="15" opacity=".50">REPLACEABLE PORTFOLIO CARDS · 90 × 54 mm · EDITABLE VECTOR</text>
"""
    return svg_document("0 0 2940 680", body, "遂见作品展示卡系列")


def build_packaging_dieline() -> str:
    cut = COLORS["oath_vermilion"]
    fold = "#3A79B8"
    body = f"""
<rect width="2400" height="1600" fill="#FAF8F2"/>
<g id="legend" transform="translate(100 92)">
  <text class="serif" x="0" y="0" fill="{COLORS['zhao_lacquer']}" font-size="52" font-weight="700">遂见 · 抽屉礼盒刀模</text>
  <text class="latin" x="0" y="46" fill="{COLORS['ink_black']}" font-size="16" opacity=".58">MODEL / NOT FOR PRODUCTION · FINISHED 128 × 86 × 24 mm</text>
  <path d="M0 92 H120" stroke="{cut}" stroke-width="5"/><text class="sans" x="140" y="101" font-size="22">切线 CUT</text>
  <path d="M320 92 H440" stroke="{fold}" stroke-width="4" stroke-dasharray="20 12"/><text class="sans" x="460" y="101" font-size="22">折线 FOLD</text>
</g>
<g id="sleeve-dieline" transform="translate(150 330)">
  <text class="latin" x="0" y="-42" fill="{COLORS['zhao_lacquer']}" font-size="20" font-weight="700">OUTER SLEEVE</text>
  <path d="M0 0 H1280 V240 H2140 V520 H1280 V760 H0 Z" fill="none" stroke="{cut}" stroke-width="5"/>
  <path d="M1280 0 V760 M0 240 H2140 M0 520 H2140" fill="none" stroke="{fold}" stroke-width="4" stroke-dasharray="20 12"/>
  <rect x="60" y="300" width="1120" height="160" rx="24" fill="{COLORS['zhao_lacquer']}"/>
  <path d="M90 435 L1120 128" stroke="{COLORS['ding_gold']}" stroke-width="9"/>
  <text class="serif" x="110" y="405" fill="{COLORS['silk_white']}" font-size="68" font-weight="700">遂见</text>
  <text class="sans" x="380" y="406" fill="{COLORS['silk_white']}" font-size="25" letter-spacing="4">让才能，被看见</text>
</g>
<g id="drawer-dieline" transform="translate(210 1190)">
  <text class="latin" x="0" y="-38" fill="{COLORS['zhao_lacquer']}" font-size="20" font-weight="700">INNER DRAWER</text>
  <path d="M0 0 H240 V-120 H1520 V0 H1760 V280 H1520 V400 H240 V280 H0 Z" fill="none" stroke="{cut}" stroke-width="5"/>
  <path d="M240 0 V280 M1520 0 V280 M240 0 H1520 M240 280 H1520" fill="none" stroke="{fold}" stroke-width="4" stroke-dasharray="20 12"/>
  <path d="M804 0 A76 76 0 0 0 956 0" fill="none" stroke="{cut}" stroke-width="5"/>
</g>
<text class="sans" x="2240" y="1515" text-anchor="end" fill="{COLORS['ink_black']}" font-size="20" opacity=".58">结构尺寸需在实体打样后校正 · 当前为概念模型刀模</text>
"""
    return svg_document("0 0 2400 1600", body, "遂见包装概念刀模")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    assets = {
        "wordmark.svg": build_wordmark(),
        "identity_card.svg": build_identity_card(),
        "portfolio_cards.svg": build_portfolio_cards(),
        "packaging_dieline.svg": build_packaging_dieline(),
    }
    for filename, content in assets.items():
        (OUTPUT_DIR / filename).write_text(content, encoding="utf-8")

    font_files = {
        "Noto Sans SC": FONT_DIR / "NotoSansSC[wght].ttf",
        "Noto Serif SC": FONT_DIR / "NotoSerifSC[wght].ttf",
        "Inter": FONT_DIR / "InterVariable.ttf",
    }
    manifest = {
        "colors": COLORS,
        "fonts": {name: {"path": str(path.relative_to(PROJECT_DIR)), "sha256": sha256(path), "license": "SIL OFL 1.1"} for name, path in font_files.items()},
        "assets": {
            filename: {
                "sha256": sha256(OUTPUT_DIR / filename),
                "viewBox": content.split('viewBox="', 1)[1].split('"', 1)[0],
                "editable": True,
            }
            for filename, content in assets.items()
        },
        "product_baseline_mm": [PRODUCT.width, PRODUCT.height, PRODUCT.depth],
        "privacy": "All displayed identity information is fictional and the demo matrix is intentionally non-scannable.",
    }
    (OUTPUT_DIR / "identity_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
