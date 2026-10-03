"""Compose six editable A4 competition boards for the upgraded Jiewei concept."""

from __future__ import annotations

import json
from pathlib import Path
import sys


PROJECT_DIR = Path(__file__).resolve().parents[1]
OUT = PROJECT_DIR / "05_boards" / "src"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from design_config import BOARD, BOX, COLORS, CONCEPT_DISCLOSURE, PRODUCT_MODULE, PRODUCTS  # noqa: E402


W, H = BOARD.width_px, BOARD.height_px


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, value, size, fill, family="sans", weight=400, anchor="start", opacity=1.0, spacing=0):
    return f'<text x="{x}" y="{y}" class="{family}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}" opacity="{opacity}" letter-spacing="{spacing}">{esc(value)}</text>'


def lines(x, y, values, size, fill, gap, family="sans", weight=400):
    return "".join(text(x, y + i * gap, value, size, fill, family, weight) for i, value in enumerate(values))


def image(href, x, y, width, height, opacity=1.0):
    return f'<image href="{href}" x="{x}" y="{y}" width="{width}" height="{height}" opacity="{opacity}" preserveAspectRatio="xMidYMid meet"/>'


def panel(x, y, width, height, dark=False, radius=38):
    fill = COLORS["wall_ink"] if dark else "#FAF6EC"
    stroke = COLORS["moon_gold"] if dark else "#D6C7A8"
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>'


def header(number, title_value, subtitle, dark=False):
    ink = COLORS["paper_white"] if dark else COLORS["wall_ink"]
    return f'''
<g id="header">
 {text(160,178,f'{number:02d} / {BOARD.count:02d}',22,COLORS['moon_gold'],'latin',760,spacing=4)}
 {text(160,308,title_value,82,ink,'serif',780,spacing=2)}
 {text(162,374,subtitle,23,ink,'latin',480,opacity=.68,spacing=2)}
 <path d="M160 438 H2320" stroke="{COLORS['moon_gold']}" stroke-width="4" opacity=".72"/>
</g>'''


def footer(number, dark=False):
    ink = COLORS["paper_white"] if dark else COLORS["wall_ink"]
    return f'''
<g id="footer" opacity=".58"><path d="M160 3350 H2320" stroke="{ink}" stroke-width="2"/>
{text(160,3408,'JIEWEI · HANBAOFANG SIX FLAVOURS OF HANDAN · CONCEPT PROPOSAL',16,ink,'latin',520,spacing=2)}
{text(2320,3408,f'{number:02d}',16,COLORS['moon_gold'],'latin',720,'end',spacing=2)}</g>'''


def wrap(number, title_value, subtitle, body, dark=False):
    bg = COLORS["wall_ink"] if dark else COLORS["paper_white"]
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><style><![CDATA[
@font-face{{font-family:NSans;src:url('../../01_research/fonts/NotoSansSC[wght].ttf')}}
@font-face{{font-family:NSerif;src:url('../../01_research/fonts/NotoSerifSC[wght].ttf')}}
@font-face{{font-family:Inter;src:url('../../01_research/fonts/InterVariable.ttf')}}
.sans{{font-family:NSans,sans-serif}} .serif{{font-family:NSerif,serif}} .latin{{font-family:Inter,sans-serif}}
]]></style><filter id="shadow"><feDropShadow dx="0" dy="16" stdDeviation="20" flood-color="#081113" flood-opacity=".25"/></filter></defs>
<rect width="{W}" height="{H}" fill="{bg}"/>
<path d="M-100 3040 C520 2700 900 3400 1480 3080 S2240 2780 2620 3000" fill="none" stroke="{COLORS['moon_gold']}" stroke-width="3" opacity=".16"/>
{header(number,title_value,subtitle,dark)}{body}{footer(number,dark)}</svg>'''


def board_01():
    body = f'''
<g id="cover">
 <circle cx="1940" cy="820" r="350" fill="none" stroke="{COLORS['moon_gold']}" stroke-width="4" opacity=".24"/>
 {image('../../04_renders/hero_open.png',100,420,2280,1650)}
 <rect x="150" y="2050" width="2180" height="820" rx="56" fill="#172529" stroke="{COLORS['moon_gold']}" stroke-width="3"/>
 {text(240,2240,'解围',122,COLORS['paper_white'],'serif',820,spacing=9)}
 {text(246,2325,'RELIEVE THE SIEGE',23,COLORS['moon_gold'],'latin',680,spacing=5)}
 {text(240,2460,'六味邯郸 · 邯宝坊机关礼盒概念提案',43,COLORS['paper_white'],'serif',650)}
 {lines(240,2570,['把“围魏救赵”的行动顺序变成开盒逻辑：','先侧移解除锁定，再让六地风物在中央显现。'],28,COLORS['paper_white'],52,'sans',380)}
 <g transform="translate(1590 2280)" fill="none"><path d="M0 300 H180 V170 H380" stroke="{COLORS['route_red']}" stroke-width="18"/><path d="M380 170 V50 H610" stroke="{COLORS['moon_gold']}" stroke-width="18"/><circle cx="610" cy="50" r="20" fill="{COLORS['moon_gold']}" stroke="none"/></g>
 {text(180,3020,f'{BOX.width:.0f} × {BOX.depth:.0f} × {BOX.height:.0f} mm',27,COLORS['paper_white'],'latin',700)}
 {text(850,3020,'42 mm 侧移解锁',27,COLORS['paper_white'],'sans',620)}
 {text(1510,3020,'145 mm 中央显现',27,COLORS['paper_white'],'sans',620)}
</g>'''
    return wrap(1, "解围·六味邯郸", "TWO-STAGE UNLOCKING · ORIGINAL CONCEPT PACKAGING SYSTEM", body, True)


def board_02():
    cards = [
        ("01", "围", "避开正面强攻", "典故中的关键不是战争图像，而是先改变外围条件。"),
        ("02", "移", "侧向状态先改变", "红色“魏”侧抽屉先移动 42 mm，带动双锁钥片。"),
        ("03", "解", "两点限制同时释放", "获得 1.2 mm 数字释放余量后，中央托盘可以运动。"),
        ("04", "见", "六地风物中央显现", "“赵”托盘前行 145 mm，六味模块形成完整陈列面。"),
    ]
    blocks = []
    for index, (number, glyph, title_value, description) in enumerate(cards):
        x = 150 + (index % 2) * 1110
        y = 570 + (index // 2) * 730
        blocks.append(f'''<g transform="translate({x} {y})">{panel(0,0,1020,620)}<circle cx="118" cy="120" r="64" fill="{COLORS['wall_ink'] if index != 1 else COLORS['route_red']}"/>{text(118,143,glyph,52,COLORS['paper_white'],'serif',760,'middle')}{text(220,78,number,18,COLORS['moon_gold'],'latin',760,spacing=3)}{text(220,148,title_value,37,COLORS['wall_ink'],'serif',720)}{lines(80,286,[description[:17],description[17:34],description[34:]],25,COLORS['soft_gray'],47,'sans',390)}<path d="M80 504 H920" stroke="{COLORS['moon_gold']}" stroke-width="4" opacity=".48"/></g>''')
    body = f'''<g id="culture">{"".join(blocks)}
<rect x="150" y="2130" width="2130" height="760" rx="52" fill="{COLORS['wall_ink']}"/>
{text(230,2280,'不是贴一幅古画，而是把成语变成动作约束',43,COLORS['paper_white'],'serif',720)}
<path d="M250 2550 H720 V2440 H1210 V2600 H1710 V2470 H2170" fill="none" stroke="{COLORS['route_red']}" stroke-width="15"/><circle cx="2170" cy="2470" r="22" fill="{COLORS['moon_gold']}"/>
{text(250,2720,'围合',24,COLORS['paper_white'],'sans',620)}{text(770,2720,'侧移',24,COLORS['paper_white'],'sans',620)}{text(1260,2720,'解锁',24,COLORS['paper_white'],'sans',620)}{text(2170,2720,'中央见礼',24,COLORS['paper_white'],'sans',620,'end')}
{text(160,3030,'机构借用“围魏救赵”的行动关系，不复原具体战争场景。',21,COLORS['soft_gray'],'sans',400)}</g>'''
    return wrap(2, "把典故变成必须遵守的动作", "IDIOM TO MECHANISM · 围—移—解—见", body)


def board_03():
    states = [
        ("sequence_01.png", "01 · 闭锁", "双锁钥片占据槽位"),
        ("sequence_03.png", "02 · 侧移", "42 mm 后限制释放"),
        ("sequence_04.png", "03 · 显现", "中央托盘前行 145 mm"),
    ]
    blocks = []
    for index, (img, title_value, description) in enumerate(states):
        x = 120 + index * 755
        blocks.append(f'''<g transform="translate({x} 1740)">{panel(0,0,700,820)}{image('../../04_renders/'+img,20,30,660,540)}{text(45,650,title_value,31,COLORS['wall_ink'],'serif',720)}{text(45,710,description,21,COLORS['soft_gray'],'sans',430)}</g>''')
    body = f'''<g id="opening-experience">
<rect x="120" y="520" width="2240" height="1080" rx="52" fill="{COLORS['wall_ink']}"/>{image('../../04_renders/hand_opening.png',100,500,2280,1100)}
{text(200,1490,'手部只表达尺度与侧移动作 · DIGITAL VISUALISATION',20,COLORS['paper_white'],'latin',520,spacing=2)}
{"".join(blocks)}
<rect x="120" y="2660" width="2240" height="320" rx="42" fill="#172529"/>
{text(200,2790,'动作规则',19,COLORS['moon_gold'],'latin',720,spacing=3)}{text(200,2880,'侧抽不到位，中央托盘不能开启',38,COLORS['paper_white'],'serif',720)}
{text(2150,2865,'42 → 145 mm',48,COLORS['moon_gold'],'latin',760,'end')}</g>'''
    return wrap(3, "先解锁，再见礼", "OPENING EXPERIENCE · 两个方向、一个不可跳步的顺序", body)


def board_04():
    cards = []
    for index, product in enumerate(PRODUCTS):
        x = 130 + (index % 3) * 745
        y = 1880 + (index // 3) * 410
        label_color = COLORS["paper_white"] if product.code == "A" else COLORS["wall_ink"]
        cards.append(f'''<g transform="translate({x} {y})"><rect width="690" height="350" rx="38" fill="{product.color}" stroke="#D6C7A8" stroke-width="3"/>{text(48,76,product.code,18,COLORS['moon_gold'],'latin',760,spacing=2)}{text(48,150,product.display_name,39,label_color,'serif',760)}{text(48,205,product.category,22,label_color,'sans',500,opacity=.82)}{text(48,290,f'{PRODUCT_MODULE.width:.0f} × {PRODUCT_MODULE.depth:.0f} × {PRODUCT_MODULE.height:.0f} mm',19,label_color,'latin',620)}</g>''')
    body = f'''<g id="product-family">
<rect x="120" y="520" width="2240" height="1240" rx="54" fill="#A99C8A"/>{image('../../04_renders/product_family.png',100,500,2280,1280)}
{text(190,1680,'统一模块，不同地域性格：路线、山形、谷粒、瓣形与旋磨纹在同一网格中变化。',22,COLORS['paper_white'],'sans',500)}
{"".join(cards)}
<rect x="130" y="2770" width="2180" height="220" rx="34" fill="{COLORS['wall_ink']}"/>
{text(200,2860,'ORIGINAL SECONDARY PACKAGING SYSTEM',17,COLORS['moon_gold'],'latin',720,spacing=3)}
{text(200,2935,CONCEPT_DISCLOSURE,27,COLORS['paper_white'],'sans',650)}</g>'''
    return wrap(4, "六地六味，一套包装语言", "PRODUCT FAMILY · 六个原创概念模块", body)


def board_05():
    body = f'''<g id="engineering">
<rect x="120" y="520" width="1420" height="1500" rx="52" fill="{COLORS['wall_ink']}"/>{image('../../04_renders/exploded.png',120,540,1420,1200)}{text(190,1900,'13 个实体 · 3 个 STEP 状态 · 13 份 STL',24,COLORS['paper_white'],'latin',620)}
<g transform="translate(1600 520)">{panel(0,0,760,700)}{text(55,82,'DIELINE',18,COLORS['moon_gold'],'latin',720,spacing=3)}{image('../../04_renders/dieline_preview.png',30,100,700,470)}{text(55,625,'红：裁切｜蓝：压痕｜灰：裱糊',20,COLORS['soft_gray'],'sans',450)}</g>
<g transform="translate(1600 1290)">{panel(0,0,760,730)}{text(55,85,'LOCK LOGIC',18,COLORS['moon_gold'],'latin',720,spacing=3)}{text(55,175,'双锁钥片',40,COLORS['wall_ink'],'serif',720)}{lines(55,270,['闭合：两点同时限位','侧移：42 mm 清除槽位','释放余量：1.2 mm','开启：中央前行 145 mm'],23,COLORS['soft_gray'],60,'sans',430)}</g>
<rect x="120" y="2140" width="2240" height="840" rx="48" fill="#FAF6EC" stroke="#D6C7A8" stroke-width="3"/>
{text(190,2260,'材料与关键参数',38,COLORS['wall_ink'],'serif',720)}
{text(190,2380,'2.0 mm',43,COLORS['wall_ink'],'latin',760)}{text(190,2435,'灰板',19,COLORS['soft_gray'],'sans',450)}
{text(620,2380,'0.18 mm',43,COLORS['wall_ink'],'latin',760)}{text(620,2435,'包纸设计基线',19,COLORS['soft_gray'],'sans',450)}
{text(1120,2380,'1.0 mm / 侧',43,COLORS['wall_ink'],'latin',760)}{text(1120,2435,'概念模块装配间隙',19,COLORS['soft_gray'],'sans',450)}
{text(1780,2380,'Ø108 mm',43,COLORS['wall_ink'],'latin',760)}{text(1780,2435,'月璧窗口',19,COLORS['soft_gray'],'sans',450)}
{lines(190,2610,['灰板裱艺术纸，局部烫金或金色油墨；内衬建议纸浆模塑或折叠白卡。','数字模型验证结构、行程和交换格式；纸板耐久与运输性能须在决赛样机阶段验证。'],22,COLORS['soft_gray'],52,'sans',400)}
{text(190,2850,CONCEPT_DISCLOSURE,23,COLORS['route_red'],'sans',700)}</g>'''
    return wrap(5, "结构、材料与制造边界", "ENGINEERING · 从参数化装配到毫米级包装展开", body)


def board_06():
    body = f'''<g id="market-scene">
<rect x="120" y="520" width="2240" height="1160" rx="54" fill="#8F8373"/>{image('../../04_renders/retail_scene.png',100,500,2280,1200)}
<g transform="translate(120 1780)">{panel(0,0,1080,820,True)}{image('../../04_renders/mid_autumn_variant.png',20,35,1040,500)}{text(65,625,'月满中秋',44,COLORS['paper_white'],'serif',740)}{text(65,690,'月宣白 × 赵月金',22,COLORS['moon_gold'],'sans',520)}{text(65,750,'共享结构，只切换外套与局部印刷层',21,COLORS['paper_white'],'sans',420)}</g>
<g transform="translate(1280 1780)">{panel(0,0,1080,820)}{image('../../04_renders/national_day_variant.png',20,35,1040,500)}{text(65,625,'山河同庆',44,COLORS['wall_ink'],'serif',740)}{text(65,690,'河山青 × 迂回朱',22,COLORS['route_red'],'sans',620)}{text(65,750,'文旅门店、节庆礼赠与城市伴手礼场景',21,COLORS['soft_gray'],'sans',420)}</g>
<rect x="120" y="2700" width="2240" height="300" rx="42" fill="#172529"/>
{text(190,2810,'MARKET CONVERSION',17,COLORS['moon_gold'],'latin',720,spacing=3)}
{text(190,2890,'模块化内装便于按渠道与节令调整；成本与价格均为设计估算，须由生产主体复核。',24,COLORS['paper_white'],'sans',460)}
{text(190,2960,CONCEPT_DISCLOSURE,22,COLORS['route_red'],'sans',700)}</g>'''
    return wrap(6, "双节应用与市场场景", "SEASONAL CMF · ONE STRUCTURE, TWO FESTIVAL EXPRESSIONS", body, True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    boards = [board_01(), board_02(), board_03(), board_04(), board_05(), board_06()]
    for index, content in enumerate(boards, 1):
        (OUT / f"board_{index:02d}.svg").write_text(content, encoding="utf-8")
    manifest = {
        "count": 6,
        "size_px": [W, H],
        "dpi": BOARD.dpi,
        "product_asset_status": "original_concept_secondary_packaging",
        "concept_disclosure": CONCEPT_DISCLOSURE,
        "titles": [
            "解围·六味邯郸",
            "把典故变成必须遵守的动作",
            "先解锁，再见礼",
            "六地六味，一套包装语言",
            "结构、材料与制造边界",
            "双节应用与市场场景",
        ],
    }
    (OUT / "board_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "boards": 6}, ensure_ascii=False))


if __name__ == "__main__":
    main()
