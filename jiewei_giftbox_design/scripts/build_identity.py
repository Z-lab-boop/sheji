"""Generate deterministic editable SVG identity assets for Jiewei."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "02_identity"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from design_config import COLORS, CONCEPT_DISCLOSURE, COPY, PRODUCT_MODULE, PRODUCTS  # noqa: E402


def svg_shell(width: float, height: float, body: str) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}mm" height="{height}mm" viewBox="0 0 {width} {height}">
<defs>
  <style><![CDATA[
    @font-face {{ font-family: NSans; src: url('../01_research/fonts/NotoSansSC[wght].ttf'); }}
    @font-face {{ font-family: NSerif; src: url('../01_research/fonts/NotoSerifSC[wght].ttf'); }}
    @font-face {{ font-family: Inter; src: url('../01_research/fonts/InterVariable.ttf'); }}
    .sans {{ font-family: NSans, sans-serif; }} .serif {{ font-family: NSerif, serif; }} .latin {{ font-family: Inter, sans-serif; }}
  ]]></style>
</defs>
{body}
</svg>
'''


def wordmark() -> str:
    body = f'''
<rect width="240" height="95" rx="7" fill="{COLORS['paper_white']}"/>
<g id="route-symbol" transform="translate(12 12)" fill="none" stroke="{COLORS['wall_ink']}" stroke-width="5" stroke-linecap="square" stroke-linejoin="miter">
  <path d="M8 52 V8 H58 V30 H36"/>
  <path d="M36 30 H78 V8 H96 V58 H58 V46" stroke="{COLORS['route_red']}"/>
  <circle cx="96" cy="58" r="5" fill="{COLORS['moon_gold']}" stroke="none"/>
</g>
<text x="120" y="55" class="serif" font-size="38" font-weight="760" fill="{COLORS['wall_ink']}" letter-spacing="6">解围</text>
<text x="121" y="76" class="latin" font-size="7" font-weight="650" fill="{COLORS['moon_gold']}" letter-spacing="2">RELIEVE THE SIEGE</text>
'''
    return svg_shell(240, 95, body)


def common_sleeve(season: str) -> str:
    is_moon = season == "mid_autumn"
    bg = COLORS["wall_ink"] if is_moon else COLORS["mountain_green"]
    accent = COLORS["moon_gold"] if is_moon else COLORS["route_red"]
    season_cn = "月满中秋" if is_moon else "山河同庆"
    season_en = "MID-AUTUMN EDITION" if is_moon else "NATIONAL DAY EDITION"
    artwork = (
        f'<circle cx="205" cy="76" r="54" fill="none" stroke="{COLORS["moon_gold"]}" stroke-width="2"/>'
        f'<circle cx="205" cy="76" r="42" fill="{COLORS["moon_gold"]}" opacity=".12"/>'
        f'<path d="M24 154 C86 132 122 176 176 152 S244 126 282 150" fill="none" stroke="{COLORS["paper_white"]}" stroke-width="1.3" opacity=".45"/>'
        if is_moon
        else f'<path d="M18 122 L72 78 L110 111 L158 58 L218 116 L270 80" fill="none" stroke="{COLORS["paper_white"]}" stroke-width="2.2" opacity=".82"/>'
        f'<path d="M18 156 C70 120 122 192 180 146 S248 124 278 142" fill="none" stroke="{COLORS["moon_gold"]}" stroke-width="2" opacity=".72"/>'
    )
    body = f'''
<rect width="290" height="230" fill="{bg}"/>
<path d="M0 22 H88 V8 H164 V22 H290" fill="none" stroke="{accent}" stroke-width="2.2" opacity=".75"/>
<g id="shared-route" fill="none" stroke="{accent}" stroke-width="3.2" stroke-linecap="square"><path d="M24 186 H82 V164 H142 V190 H206 V168 H266"/><circle cx="266" cy="168" r="4" fill="{COLORS['moon_gold']}" stroke="none"/></g>
{artwork}
<text x="24" y="62" class="serif" font-size="31" font-weight="760" fill="{COLORS['paper_white']}" letter-spacing="4">解围</text>
<text x="25" y="79" class="latin" font-size="5.2" font-weight="650" fill="{COLORS['moon_gold']}" letter-spacing="1.8">RELIEVE THE SIEGE</text>
<text x="24" y="111" class="serif" font-size="14" font-weight="650" fill="{COLORS['paper_white']}">{season_cn}</text>
<text x="24" y="123" class="latin" font-size="4.7" fill="{COLORS['paper_white']}" opacity=".72" letter-spacing="1">{season_en}</text>
<g id="brief-target"><rect x="24" y="198" width="96" height="18" rx="2" fill="none" stroke="{COLORS['paper_white']}" stroke-width=".6" opacity=".62"/><text x="72" y="209" class="sans" text-anchor="middle" font-size="4.2" fill="{COLORS['paper_white']}" opacity=".82">邯宝坊赛题概念提案</text></g>
<g id="production-review"><rect x="164" y="198" width="102" height="18" rx="2" fill="none" stroke="{COLORS['paper_white']}" stroke-width=".6" opacity=".62"/><text x="215" y="209" class="sans" text-anchor="middle" font-size="4.2" fill="{COLORS['paper_white']}" opacity=".82">生产信息投产前复核</text></g>
<text x="266" y="222" class="sans" text-anchor="end" font-size="3.6" fill="{COLORS['paper_white']}" opacity=".58">六味邯郸 · ORIGINAL CONCEPT SERIES</text>
'''
    return svg_shell(290, 230, body)


def concept_product_labels() -> str:
    cards = []
    for index, product in enumerate(PRODUCTS):
        x = 8 + (index % 3) * 74
        y = 8 + (index // 3) * 70
        dark_text = COLORS["wall_ink"] if product.code != "A" else COLORS["paper_white"]
        secondary = COLORS["paper_white"] if product.code == "A" else COLORS["soft_gray"]
        cards.append(f'''
<g id="concept-{product.code}" transform="translate({x} {y})">
  <rect width="68" height="62" rx="4" fill="{product.color}" stroke="{COLORS['wall_ink']}" stroke-width=".7"/>
  <path d="M8 15 H28 V9 H46 V17 H60" fill="none" stroke="{COLORS['moon_gold']}" stroke-width="1.5"/>
  <text x="8" y="29" class="serif" font-size="7.8" font-weight="720" fill="{dark_text}">{product.display_name}</text>
  <text x="8" y="39" class="sans" font-size="4.3" fill="{secondary}">{product.category}</text>
  <text x="8" y="48" class="latin" font-size="3.6" fill="{secondary}">{PRODUCT_MODULE.width:.0f} × {PRODUCT_MODULE.depth:.0f} × {PRODUCT_MODULE.height:.0f} mm</text>
  <rect x="6" y="52" width="56" height="7" rx="1.5" fill="{COLORS['wall_ink']}" opacity=".92"/>
  <text x="34" y="57" class="sans" text-anchor="middle" font-size="2.8" fill="{COLORS['paper_white']}">信息示意 · {product.code}</text>
</g>''')
    disclosure = f'<text x="116" y="151" class="sans" text-anchor="middle" font-size="3.8" fill="{COLORS["soft_gray"]}">{CONCEPT_DISCLOSURE}</text>'
    return svg_shell(232, 158, f'<rect width="232" height="158" fill="#F7F2E8"/>{"".join(cards)}{disclosure}')


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    assets = {
        "wordmark.svg": wordmark(),
        "mid_autumn_sleeve.svg": common_sleeve("mid_autumn"),
        "national_day_sleeve.svg": common_sleeve("national_day"),
        "concept_product_labels.svg": concept_product_labels(),
    }
    for name, content in assets.items():
        (OUT / name).write_text(content, encoding="utf-8")
    manifest = {
        "project": COPY["name"],
        "palette": COLORS,
        "fonts": ["NotoSansSC[wght].ttf", "NotoSerifSC[wght].ttf", "InterVariable.ttf"],
        "brand_asset_status": "official_brief_named_target_no_logo_asset",
        "product_asset_status": "original_concept_secondary_packaging",
        "concept_disclosure": CONCEPT_DISCLOSURE,
        "product_modules": [
            {"code": item.code, "category": item.category, "display_name": item.display_name, "color": item.color}
            for item in PRODUCTS
        ],
        "reserved_zones": ["brief-target", "production-review"],
        "assets": list(assets),
    }
    (OUT / "identity_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "outputs": list(assets)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
