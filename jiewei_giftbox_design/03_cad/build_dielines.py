"""Generate millimetre-scale SVG and ASCII DXF packaging dielines."""

from __future__ import annotations

import json
from pathlib import Path
import sys


CAD_DIR = Path(__file__).resolve().parent
OUT = CAD_DIR / "dielines"
sys.path.insert(0, str(CAD_DIR.parent / "scripts"))

from design_config import BOX, PRODUCT_MODULE  # noqa: E402


LAYERS = {"cut": "#FF0000", "crease": "#0000FF", "glue": "#808080"}


def rect_segments(x: float, y: float, w: float, h: float) -> list[tuple[float, float, float, float]]:
    return [(x, y, x + w, y), (x + w, y, x + w, y + h), (x + w, y + h, x, y + h), (x, y + h, x, y)]


def svg_for(name: str, width: float, height: float, cut, crease, glue, notes: list[str]) -> str:
    lines = []
    for layer, segments in (("cut", cut), ("crease", crease)):
        for x1, y1, x2, y2 in segments:
            lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{layer}"/>')
    glue_shapes = "".join(f'<polygon points="{" ".join(f"{x},{y}" for x,y in poly)}" class="glue"/>' for poly in glue)
    note_text = "".join(f'<text x="20" y="{height - 18 + i * 5}" class="label">{note}</text>' for i, note in enumerate(notes))
    cal_x, cal_y = width - 28, 8
    calibration = "".join(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="cut"/>' for x1,y1,x2,y2 in rect_segments(cal_x, cal_y, 10, 10))
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}mm" height="{height}mm" viewBox="0 0 {width} {height}">
<style>
.cut{{stroke:{LAYERS['cut']};stroke-width:.25;fill:none;vector-effect:non-scaling-stroke}} .crease{{stroke:{LAYERS['crease']};stroke-width:.2;stroke-dasharray:3 2;fill:none;vector-effect:non-scaling-stroke}} .glue{{stroke:{LAYERS['glue']};stroke-width:.18;fill:{LAYERS['glue']};fill-opacity:.16;vector-effect:non-scaling-stroke}} .label{{font:3.8px sans-serif;fill:#202F32}}
</style>
<rect width="{width}" height="{height}" fill="#FFFDF8"/>
<g id="glue-zones">{glue_shapes}</g><g id="cut-lines">{''.join(lines)}</g>
<g id="calibration-square">{calibration}<text x="{cal_x}" y="{cal_y + 15}" class="label">10 mm</text></g>
<g id="grain-direction"><path d="M20 18 H70" stroke="#202F32" stroke-width=".5"/><path d="M70 18 l-6 -3 v6 z" fill="#202F32"/><text x="20" y="14" class="label">纹向 GRAIN</text></g>
<text x="20" y="30" class="label">{name} · 单位 mm · 灰板 {BOX.board_thickness} / 包纸代理 {BOX.wrap_thickness}</text>
{note_text}
</svg>
'''


def dxf_for(cut, crease, glue) -> str:
    lines = [
        "0", "SECTION", "2", "HEADER", "9", "$ACADVER", "1", "AC1009", "9", "$INSUNITS", "70", "4", "0", "ENDSEC",
        "0", "SECTION", "2", "TABLES", "0", "TABLE", "2", "LAYER", "70", "3",
        "0", "LAYER", "2", "CUT", "70", "0", "62", "1", "6", "CONTINUOUS",
        "0", "LAYER", "2", "CREASE", "70", "0", "62", "5", "6", "DASHED",
        "0", "LAYER", "2", "GLUE", "70", "0", "62", "8", "6", "CONTINUOUS",
        "0", "ENDTAB", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES",
    ]

    def add_line(layer: str, seg) -> None:
        x1, y1, x2, y2 = seg
        lines.extend(["0", "LINE", "8", layer, "10", str(x1), "20", str(y1), "30", "0", "11", str(x2), "21", str(y2), "31", "0"])

    for seg in cut:
        add_line("CUT", seg)
    for seg in crease:
        add_line("CREASE", seg)
    for poly in glue:
        closed = list(poly) + [poly[0]]
        for a, b in zip(closed, closed[1:]):
            add_line("GLUE", (a[0], a[1], b[0], b[1]))
    lines.extend(["0", "ENDSEC", "0", "EOF"])
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    defs = {}

    # Four-panel sleeve strip plus 15 mm internal glue tab.
    width, height = 765.0, 270.0
    cut = rect_segments(10, 40, 745, 230)
    crease = [(25, 40, 25, 270), (315, 40, 315, 270), (390, 40, 390, 270), (680, 40, 680, 270)]
    glue = [[(12, 45), (23, 45), (23, 265), (12, 265)]]
    defs["outer_sleeve"] = (width, height, cut, crease, glue, ["15 mm 裱糊搭口；窗口与品牌/法定信息在贴面层处理。"])

    width, height = 360.0, 320.0
    cut = rect_segments(20, 45, 320, 255)
    crease = [(35, 45, 35, 300), (325, 45, 325, 300), (35, 120, 325, 120), (35, 230, 325, 230)]
    glue = [[(22, 50), (33, 50), (33, 295), (22, 295)]]
    defs["wei_drawer"] = (width, height, cut, crease, glue, ["侧抽先行 42 mm；拉带位于右侧，不在刀模中虚构品牌文字。"])

    width, height = 340.0, 300.0
    cut = rect_segments(20, 45, 300, 235)
    crease = [(35, 45, 35, 280), (305, 45, 305, 280), (35, 80, 305, 80), (35, 245, 305, 245)]
    glue = [[(22, 50), (33, 50), (33, 275), (22, 275)]]
    defs["zhao_tray"] = (
        width,
        height,
        cut,
        crease,
        glue,
        ["中央托盘展示行程 145 mm；3 × 2 概念模块阵列，投产前按实际商品复核。"],
    )

    width, height = 190.0, 120.0
    cut = rect_segments(20, 40, 55, 26) + rect_segments(95, 40, 55, 26)
    crease = [(52, 40, 52, 66), (127, 40, 127, 66)]
    # Gray polygons are forbidden-glue zones and sit clear of red cut boundaries.
    glue = [[(27, 47), (45, 47), (45, 59), (27, 59)], [(102, 47), (120, 47), (120, 59), (102, 59)]]
    defs["lock_keys"] = (width, height, cut, crease, glue, ["灰色为禁止上胶区；两枚锁钥片共同限位中央托盘。"])

    manifest_files = {}
    for name, (width, height, cut, crease, glue, notes) in defs.items():
        # Include the calibration square in both editable formats.
        cal = rect_segments(width - 28, 8, 10, 10)
        svg = svg_for(name, width, height, cut, crease, glue, notes)
        dxf = dxf_for(cut + cal, crease, glue)
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
        (OUT / f"{name}.dxf").write_text(dxf, encoding="ascii")
        manifest_files[name] = {"sheet_mm": [width, height], "svg": f"{name}.svg", "dxf": f"{name}.dxf", "calibration_square_mm": [10, 10]}

    manifest = {
        "units": "mm",
        "layers": LAYERS,
        "glue_tab_mm": 15,
        "board_thickness_mm": BOX.board_thickness,
        "wrap_proxy_mm": BOX.wrap_thickness,
        "module_outer_mm": [PRODUCT_MODULE.width, PRODUCT_MODULE.depth, PRODUCT_MODULE.height],
        "files": manifest_files,
        "boundary": "Concept dielines; physical grain, wrap buildup and production tolerances require converter proofing.",
    }
    (OUT / "dieline_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "pairs": len(defs), "units": "mm"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
