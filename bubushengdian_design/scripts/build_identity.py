"""Generate the editable identity, stamp-face and folding-map SVG assets."""

from __future__ import annotations

import json
from pathlib import Path
import sys


PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "02_identity"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from design_config import COLORS, COPY, PRODUCT, STAMP_NAMES  # noqa: E402


def svg_document(width: int, height: int, body: str, view_box: str | None = None) -> str:
    box = view_box or f"0 0 {width} {height}"
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{box}">
  <defs>
    <style><![CDATA[
      .cn-serif {{ font-family: "Noto Serif SC", serif; }}
      .cn-sans {{ font-family: "Noto Sans SC", sans-serif; }}
      .latin {{ font-family: Inter, sans-serif; }}
    ]]></style>
    <filter id="paper" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence baseFrequency="0.9" numOctaves="2" seed="17" type="fractalNoise" result="n"/>
      <feColorMatrix in="n" type="saturate" values="0" result="g"/>
      <feBlend in="SourceGraphic" in2="g" mode="soft-light"/>
    </filter>
  </defs>
{body}
</svg>
'''


def build_wordmark() -> str:
    blue = COLORS["city_blue"]
    gold = COLORS["route_gold"]
    red = COLORS["seal_red"]
    paper = COLORS["moon_paper"]
    body = f'''
  <rect width="1600" height="700" rx="48" fill="{paper}"/>
  <g id="custom-route-mark" transform="translate(105 105)">
    <rect width="480" height="480" rx="80" fill="{blue}"/>
    <path d="M92 370 H190 V280 H286 V180 H390" fill="none" stroke="{gold}" stroke-width="24" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="92" cy="370" r="25" fill="{red}"/>
    <circle cx="190" cy="280" r="16" fill="{paper}"/>
    <circle cx="286" cy="180" r="16" fill="{paper}"/>
    <path d="M366 142 L426 180 L366 218 Z" fill="{gold}"/>
    <path d="M100 100 H260 M100 100 V205" stroke="{paper}" stroke-width="12" opacity=".3"/>
  </g>
  <g transform="translate(680 130)">
    <text x="0" y="220" class="cn-serif" font-size="210" font-weight="800" fill="{blue}" letter-spacing="18">步步生典</text>
    <path d="M4 286 H765" stroke="{gold}" stroke-width="8"/>
    <circle cx="742" cy="286" r="18" fill="{red}"/>
    <text x="4" y="360" class="latin" font-size="34" font-weight="650" fill="{blue}" letter-spacing="10">STEP INTO HANDAN</text>
    <text x="4" y="430" class="cn-sans" font-size="34" fill="{blue}" opacity=".72">每一步，都走进一则成语</text>
  </g>
'''
    return svg_document(1600, 700, body)


def stamp_icon(index: int, x: float, y: float, label: str) -> str:
    blue = COLORS["city_blue"]
    red = COLORS["seal_red"]
    gold = COLORS["route_gold"]
    motifs = (
        '<path d="M6 17 Q13 7 20 17 M4 17 H22 M8 17 V22 M18 17 V22"/>',
        '<path d="M5 20 H21 V8 H5 Z M9 20 V13 H17 V20 M3 8 H23"/>',
        '<path d="M5 21 H21 M7 21 V11 H19 V21 M10 11 V6 H16 V11 M4 11 H22"/>',
        '<circle cx="13" cy="13" r="8"/><path d="M13 5 V21 M5 13 H21"/>',
        '<path d="M5 15 A8 8 0 1 0 19 8 A7 7 0 0 1 5 15 Z"/><circle cx="20" cy="20" r="2"/>',
        '<path d="M4 20 L10 12 L14 16 L18 8 L23 20 Z M5 6 H21"/>',
    )
    accent = red if index in (1, 4) else gold
    return f'''
    <g id="stamp-{index + 1:02d}" transform="translate({x} {y})">
      <rect width="26" height="26" rx="3" fill="none" stroke="{blue}" stroke-width="0.8"/>
      <g fill="none" stroke="{blue}" stroke-width="0.8" stroke-linecap="round" stroke-linejoin="round">{motifs[index]}</g>
      <circle cx="22" cy="4" r="1.4" fill="{accent}"/>
      <text x="13" y="31" class="cn-sans" font-size="2.8" text-anchor="middle" fill="{blue}">{label}</text>
    </g>
'''


def build_stamp_faces() -> str:
    cards = []
    for index, name in enumerate(STAMP_NAMES):
        column = index % 3
        row = index // 3
        cards.append(stamp_icon(index, 8 + column * 34, 8 + row * 42, name))
    body = f'''
  <rect width="112" height="100" fill="{COLORS['moon_paper']}"/>
  <text x="8" y="96" class="latin" font-size="3.2" fill="{COLORS['stone_gray']}" letter-spacing=".5">26 × 26 MM · MONOCHROME STAMP FACES</text>
  {''.join(cards)}
'''
    return svg_document(112, 100, body, "0 0 112 100")


def build_folding_map() -> str:
    blue = COLORS["city_blue"]
    paper = COLORS["moon_paper"]
    red = COLORS["seal_red"]
    gold = COLORS["route_gold"]
    gray = COLORS["stone_gray"]
    nodes = (
        (72, 110, "01", "学步桥", "邯郸学步"),
        (168, 172, "02", "回车巷", "负荆请罪"),
        (260, 96, "03", "武灵丛台", "胡服骑射"),
        (360, 158, "04", "邯郸市博物馆", "和氏璧文化入口"),
    )
    node_svg = []
    for x, y, number, title, subtitle in nodes:
        node_svg.append(
            f'''<g transform="translate({x} {y})">
  <circle r="13" fill="{paper}" stroke="{gold}" stroke-width="2"/>
  <text y="2.5" class="latin" text-anchor="middle" font-size="6" font-weight="750" fill="{blue}">{number}</text>
  <text x="20" y="-1" class="cn-serif" font-size="7" font-weight="700" fill="{paper}">{title}</text>
  <text x="20" y="9" class="cn-sans" font-size="4" fill="{paper}" opacity=".7">{subtitle}</text>
</g>'''
        )
    body = f'''
  <rect width="480" height="330" fill="{paper}" filter="url(#paper)"/>
  <rect x="18" y="18" width="444" height="294" rx="12" fill="{blue}"/>
  <path d="M72 110 C110 84 130 186 168 172 S220 112 260 96 S325 177 360 158" fill="none" stroke="{gold}" stroke-width="4" stroke-linecap="round" stroke-dasharray="1 9"/>
  {''.join(node_svg)}
  <g transform="translate(38 38)">
    <text class="cn-serif" font-size="18" font-weight="800" fill="{paper}" letter-spacing="2">步步生典</text>
    <text y="18" class="latin" font-size="4.2" fill="{gold}" letter-spacing="1.2">HANDAN CULTURAL WALK · DAY / NIGHT</text>
  </g>
  <g transform="translate(38 238)">
    <rect width="190" height="48" rx="7" fill="{paper}" opacity=".96"/>
    <circle cx="22" cy="24" r="11" fill="none" stroke="{gold}" stroke-width="2"/>
    <path d="M18 29 A9 9 0 1 0 27 17 A8 8 0 0 1 18 29 Z" fill="{gold}"/>
    <text x="43" y="20" class="cn-serif" font-size="7" font-weight="700" fill="{blue}">月满邯郸 · 中秋夜游章</text>
    <text x="43" y="33" class="cn-sans" font-size="4" fill="{gray}">限定模块，不虚构历史典故</text>
  </g>
  <g transform="translate(248 238)">
    <rect width="190" height="48" rx="7" fill="{paper}" opacity=".96"/>
    <path d="M14 33 L24 19 L32 27 L40 13 L48 33 Z" fill="none" stroke="{red}" stroke-width="2"/>
    <text x="58" y="20" class="cn-serif" font-size="7" font-weight="700" fill="{blue}">山河同游 · 国庆漫游章</text>
    <text x="58" y="33" class="cn-sans" font-size="4" fill="{gray}">假日场景，不替代成语主线</text>
  </g>
  <g stroke="{red}" stroke-width="0.6" stroke-dasharray="3 3" opacity=".7">
    <path d="M160 18 V312"/><path d="M320 18 V312"/>
  </g>
  <text x="450" y="302" class="cn-sans" font-size="4.5" text-anchor="end" fill="{paper}" opacity=".6">{COPY['route_disclaimer']}</text>
'''
    return svg_document(480, 330, body, "0 0 480 330")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = {
        "wordmark.svg": build_wordmark(),
        "stamp_faces.svg": build_stamp_faces(),
        "folding_map.svg": build_folding_map(),
    }
    for name, content in outputs.items():
        (OUTPUT_DIR / name).write_text(content, encoding="utf-8")
    manifest = {
        "project": COPY["name"],
        "palette": COLORS,
        "fonts": ["Noto Serif SC", "Noto Sans SC", "Inter"],
        "stamp_ids": [f"stamp-{index:02d}" for index in range(1, 7)],
        "stamp_names": list(STAMP_NAMES),
        "stamp_face_mm": [int(PRODUCT.stamp_face), int(PRODUCT.stamp_face)],
        "route_disclaimer": COPY["route_disclaimer"],
        "source_rule": "Project-authored vectors; no external images embedded.",
    }
    (OUTPUT_DIR / "identity_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "ok", "outputs": list(outputs)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
