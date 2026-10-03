"""Compose eight editable A4 competition boards for Bubushengdian."""

from __future__ import annotations

import json
from pathlib import Path
import sys


PROJECT_DIR = Path(__file__).resolve().parents[1]
BOARD_DIR = PROJECT_DIR / "05_boards" / "src"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from design_config import BOARD, COLORS, COPY, PRODUCT, STAMP_NAMES  # noqa: E402


W, H = BOARD.width_px, BOARD.height_px


def esc(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def text(
    x: float,
    y: float,
    value: str,
    size: float,
    fill: str,
    family: str = "sans",
    weight: int = 400,
    anchor: str = "start",
    opacity: float = 1.0,
    spacing: float = 0.0,
) -> str:
    return (
        f'<text x="{x}" y="{y}" class="{family}" font-size="{size}" '
        f'font-weight="{weight}" text-anchor="{anchor}" fill="{fill}" '
        f'opacity="{opacity}" letter-spacing="{spacing}">{esc(value)}</text>'
    )


def image(href: str, x: float, y: float, width: float, height: float, opacity: float = 1.0) -> str:
    return (
        f'<image href="{href}" x="{x}" y="{y}" width="{width}" height="{height}" '
        f'opacity="{opacity}" preserveAspectRatio="xMidYMid meet"/>'
    )


def card(x: float, y: float, width: float, height: float, dark: bool = False, radius: int = 38) -> str:
    fill = COLORS["city_blue"] if dark else "#FAF6EC"
    stroke = COLORS["route_gold"] if dark else "#D7C7A8"
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>'


def wrapped_lines(x: float, y: float, lines: list[str], size: float, fill: str, gap: float, family: str = "sans", weight: int = 400) -> str:
    return "".join(text(x, y + index * gap, line, size, fill, family, weight) for index, line in enumerate(lines))


def header(number: int, title: str, subtitle: str, dark: bool) -> str:
    ink = COLORS["moon_paper"] if dark else COLORS["city_blue"]
    soft = COLORS["moon_paper"] if dark else COLORS["stone_gray"]
    return f'''
<g id="header">
  {text(160, 178, f'{number:02d} / {BOARD.count:02d}', 22, COLORS['route_gold'], 'latin', 750, spacing=4)}
  {text(160, 308, title, 90, ink, 'serif', 780, spacing=2)}
  {text(162, 372, subtitle, 25, soft, 'latin', 480, opacity=.72, spacing=2)}
  <path d="M160 438 H2320" stroke="{COLORS['route_gold']}" stroke-width="4" opacity=".68"/>
</g>
'''


def footer(number: int, dark: bool) -> str:
    color = COLORS["moon_paper"] if dark else COLORS["city_blue"]
    return f'''
<g id="footer" opacity=".55">
  <path d="M160 3350 H2320" stroke="{color}" stroke-width="2"/>
  {text(160, 3408, 'BUBUSHENGDIAN · HANDAN CULTURAL WALK', 16, color, 'latin', 540, spacing=4)}
  {text(2320, 3408, f'{number:02d}', 16, COLORS['route_gold'], 'latin', 700, 'end', spacing=2)}
</g>
'''


def wrap(number: int, title: str, subtitle: str, body: str, dark: bool = False) -> str:
    background = COLORS["city_blue"] if dark else COLORS["moon_paper"]
    accent = COLORS["route_gold"]
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <style><![CDATA[
    @font-face {{ font-family: NotoSansLocal; src: url('../../01_research/fonts/NotoSansSC[wght].ttf'); }}
    @font-face {{ font-family: NotoSerifLocal; src: url('../../01_research/fonts/NotoSerifSC[wght].ttf'); }}
    @font-face {{ font-family: InterLocal; src: url('../../01_research/fonts/InterVariable.ttf'); }}
    .sans {{ font-family: NotoSansLocal, sans-serif; }}
    .serif {{ font-family: NotoSerifLocal, serif; }}
    .latin {{ font-family: InterLocal, sans-serif; }}
  ]]></style>
  <linearGradient id="softGold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E8D29B"/><stop offset="1" stop-color="{accent}"/></linearGradient>
  <filter id="shadow"><feDropShadow dx="0" dy="18" stdDeviation="20" flood-color="#071B20" flood-opacity=".22"/></filter>
</defs>
<rect width="{W}" height="{H}" fill="{background}"/>
<path d="M-160 3020 C540 2600 760 3420 1450 3140 S2260 2700 2700 3020" fill="none" stroke="{accent}" stroke-width="3" opacity=".18"/>
{header(number, title, subtitle, dark)}
{body}
{footer(number, dark)}
</svg>
'''


def board_01() -> str:
    body = f'''
<g id="hero">
  <circle cx="1960" cy="810" r="380" fill="none" stroke="{COLORS['route_gold']}" stroke-width="3" opacity=".25"/>
  <circle cx="1960" cy="810" r="260" fill="{COLORS['route_gold']}" opacity=".07"/>
  {image('../../04_renders/hero_open.png', 180, 520, 2150, 1520)}
  <rect x="160" y="2090" width="2160" height="690" rx="52" fill="#102F38" stroke="{COLORS['route_gold']}" stroke-width="3"/>
  {text(240, 2230, COPY['name'], 118, COLORS['moon_paper'], 'serif', 820, spacing=6)}
  {text(246, 2314, COPY['english'], 22, COLORS['route_gold'], 'latin', 650, spacing=7)}
  {text(240, 2460, COPY['slogan'], 48, COLORS['moon_paper'], 'sans', 620)}
  {wrapped_lines(240, 2572, ['一只可收纳六枚模块章的城市漫游工具，', '展开为路线图，归位成一幅完整的邯郸路径。'], 28, COLORS['moon_paper'], 52, 'sans', 360)}
  <g transform="translate(1660 2235)">
    <path d="M0 260 H180 V150 H350 V55 H510" fill="none" stroke="url(#softGold)" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="0" cy="260" r="24" fill="{COLORS['seal_red']}"/>
    <circle cx="180" cy="150" r="15" fill="{COLORS['moon_paper']}"/>
    <circle cx="350" cy="55" r="15" fill="{COLORS['moon_paper']}"/>
  </g>
  <g transform="translate(160 2870)">
    {text(0, 0, '165 × 120 × 30 mm', 30, COLORS['city_blue'], 'latin', 720)}
    {text(650, 0, '6 枚可替换印章', 30, COLORS['city_blue'], 'sans', 620)}
    {text(1260, 0, '480 × 330 mm 折叠地图', 30, COLORS['city_blue'], 'sans', 620)}
  </g>
</g>
'''
    return wrap(1, "步步生典", "HANDAN CULTURAL WALK · 邯郸双节漫游章匣", body)


def board_02() -> str:
    steps = [
        ("01", "学", "典故本义", "盲目模仿他人步法，反而失去自己的本领。"),
        ("02", "走", "当代反思", "旅行不是复制攻略，而是亲自理解一座城市。"),
        ("03", "印", "产品动作", "抵达文化节点，取章、蘸印、完成一枚印记。"),
        ("04", "记", "个人路线", "日期、地点与一句感受共同形成自己的邯郸。"),
    ]
    blocks = []
    for index, (number, glyph, title_value, desc) in enumerate(steps):
        x = 160 + (index % 2) * 1110
        y = 660 + (index // 2) * 760
        blocks.append(f'''
<g transform="translate({x} {y})">
  <rect width="1020" height="640" rx="44" fill="#FAF6EC" stroke="#D4C29C" stroke-width="3"/>
  <circle cx="120" cy="120" r="62" fill="{COLORS['city_blue']}"/>
  {text(120, 142, glyph, 54, COLORS['moon_paper'], 'serif', 760, 'middle')}
  {text(220, 84, number, 18, COLORS['route_gold'], 'latin', 760, spacing=3)}
  {text(220, 150, title_value, 42, COLORS['city_blue'], 'serif', 720)}
  {wrapped_lines(80, 285, [desc[:15], desc[15:]], 28, COLORS['ink_black'], 52, 'sans', 380)}
  <path d="M80 500 H920" stroke="{COLORS['route_gold']}" stroke-width="5" opacity=".45"/>
  {text(80, 560, ['从故事出发','把理解变成行动','让路线留下痕迹','不摹他人步，自成一城路'][index], 21, COLORS['stone_gray'], 'sans', 500, spacing=1)}
</g>''')
    body = f'''
<g id="culture-translation">
  {''.join(blocks)}
  <rect x="160" y="2200" width="2160" height="680" rx="50" fill="{COLORS['city_blue']}"/>
  {text(230, 2310, '文化不是贴图，而是一段可完成的行为', 44, COLORS['moon_paper'], 'serif', 720)}
  <path d="M250 2550 C660 2260 860 2780 1230 2500 S1820 2320 2190 2540" fill="none" stroke="{COLORS['route_gold']}" stroke-width="12" stroke-linecap="round" stroke-dasharray="2 26"/>
  {text(250, 2740, '走到现场', 26, COLORS['moon_paper'], 'sans', 620)}
  {text(850, 2740, '完成印记', 26, COLORS['moon_paper'], 'sans', 620)}
  {text(1450, 2740, '写下理解', 26, COLORS['moon_paper'], 'sans', 620)}
  {text(2180, 2740, '形成自己的路线', 26, COLORS['moon_paper'], 'sans', 620, 'end')}
  {text(160, 3010, '典故说明依据河北省文化和旅游厅公开资料；文化路线示意，不代表实时导航。', 21, COLORS['stone_gray'], 'sans', 380)}
</g>
'''
    return wrap(2, "从学步，到走出自己的路", "IDIOM TO INTERACTION · 准确保留典故本义", body)


def board_03() -> str:
    body = f'''
<g id="states">
  <g transform="translate(130 560)">{card(0,0,700,1560)}{image('../../04_renders/interaction_01.png', 20, 90, 660, 690)}{text(60, 900, '01 · 收纳', 37, COLORS['city_blue'], 'serif', 720)}{wrapped_lines(60, 970, ['闭合时保持克制轮廓，','地图与印台分别隔离。'], 24, COLORS['stone_gray'], 48)}</g>
  <g transform="translate(890 560)">{card(0,0,700,1560)}{image('../../04_renders/interaction_03.png', 20, 90, 660, 690)}{text(60, 900, '02 · 抽拉', 37, COLORS['city_blue'], 'serif', 720)}{wrapped_lines(60, 970, ['章盘沿单向导轨显露，','最大展示行程 92 mm。'], 24, COLORS['stone_gray'], 48)}</g>
  <g transform="translate(1650 560)">{card(0,0,700,1560)}{image('../../04_renders/interaction_04.png', 20, 90, 660, 690)}{text(60, 900, '03 · 取章', 37, COLORS['city_blue'], 'serif', 720)}{wrapped_lines(60, 970, ['六枚模块章独立取用，','归位后拼成城市路径。'], 24, COLORS['stone_gray'], 48)}</g>
  <rect x="130" y="2240" width="2220" height="710" rx="48" fill="{COLORS['city_blue']}"/>
  {image('../../04_renders/hero_open.png', 1180, 2240, 1100, 710)}
  {text(210, 2370, '一次完整使用，不依赖手机', 44, COLORS['moon_paper'], 'serif', 720)}
  {wrapped_lines(210, 2470, ['拉出地图 → 选择节点 → 取章蘸印', '完成记录 → 擦净章面 → 归位收纳'], 28, COLORS['moon_paper'], 60, 'sans', 400)}
  {text(210, 2735, '抽拉行程', 18, COLORS['route_gold'], 'sans', 620)}
  {text(210, 2820, '92 mm', 54, COLORS['moon_paper'], 'latin', 760)}
  {text(530, 2735, '单枚章体', 18, COLORS['route_gold'], 'sans', 620)}
  {text(530, 2820, '32 × 32 × 23', 44, COLORS['moon_paper'], 'latin', 760)}
</g>
'''
    return wrap(3, "四步完成一次城市印记", "USE FLOW · 收纳、抽拉、取章、归位", body)


def board_04() -> str:
    body = f'''
<g id="engineering">
  <rect x="120" y="530" width="1420" height="1730" rx="52" fill="{COLORS['city_blue']}"/>
  {image('../../04_renders/exploded.png', 120, 590, 1420, 1470)}
  {text(200, 2140, '10 个实体 · FCStd / STEP / STL', 24, COLORS['moon_paper'], 'latin', 620)}
  <g transform="translate(1600 530)">
    {card(0,0,750,820)}
    {text(50, 80, 'TOP', 17, COLORS['route_gold'], 'latin', 720, spacing=3)}
    {image('../../04_renders/ortho_top.png', 28, 120, 694, 480)}
    {text(375, 690, '165 × 120 mm', 26, COLORS['city_blue'], 'latin', 700, 'middle')}
    {text(50, 760, '圆角 R10 · 闭合包络', 21, COLORS['stone_gray'], 'sans', 420)}
  </g>
  <g transform="translate(1600 1440)">
    {card(0,0,750,820)}
    {text(50, 80, 'FRONT', 17, COLORS['route_gold'], 'latin', 720, spacing=3)}
    {image('../../04_renders/ortho_front.png', 28, 120, 694, 480)}
    {text(375, 690, '总高 30 mm', 26, COLORS['city_blue'], 'sans', 700, 'middle')}
    {text(50, 760, '壁厚 1.8 mm · 基准间隙 0.35 mm', 21, COLORS['stone_gray'], 'sans', 420)}
  </g>
  <rect x="120" y="2360" width="2230" height="590" rx="48" fill="#FAF6EC" stroke="#D4C29C" stroke-width="3"/>
  {text(190, 2470, '结构分工', 38, COLORS['city_blue'], 'serif', 720)}
  {text(190, 2570, '外匣', 22, COLORS['route_gold'], 'sans', 700)}{text(190, 2620, '保护与单向导向', 24, COLORS['ink_black'], 'sans', 420)}
  {text(680, 2570, '章盘', 22, COLORS['route_gold'], 'sans', 700)}{text(680, 2620, '六章与印台定位', 24, COLORS['ink_black'], 'sans', 420)}
  {text(1170, 2570, '章柄', 22, COLORS['route_gold'], 'sans', 700)}{text(1170, 2620, '可替换 26 mm 章面', 24, COLORS['ink_black'], 'sans', 420)}
  {text(1730, 2570, '地图代理', 22, COLORS['route_gold'], 'sans', 700)}{text(1730, 2620, '折叠态尺寸校核', 24, COLORS['ink_black'], 'sans', 420)}
  {wrapped_lines(190, 2760, ['数字模型已验证实体、包络与导出可读性；摩擦、耐折、污染和儿童安全仍需样机测试。'], 23, COLORS['stone_gray'], 42)}
</g>
'''
    return wrap(4, "结构不是效果图", "ENGINEERING · 参数化装配与明确验证边界", body)


def board_05() -> str:
    labels = ["学步桥", "回车巷", "武灵丛台", "邯郸市博物馆", "月满邯郸", "山河同游"]
    label_cards = []
    for index, label in enumerate(labels):
        x = 150 + (index % 3) * 760
        y = 2140 + (index // 3) * 320
        label_cards.append(f'''
<g transform="translate({x} {y})">
  <rect width="680" height="250" rx="34" fill="#FAF6EC" stroke="#D4C29C" stroke-width="3"/>
  <circle cx="86" cy="125" r="48" fill="{COLORS['seal_red'] if index in (0,4) else COLORS['city_blue']}"/>
  {text(86, 136, f'{index+1:02d}', 22, COLORS['moon_paper'], 'latin', 760, 'middle')}
  {text(165, 105, label, 30, COLORS['city_blue'], 'serif', 700)}
  {text(165, 160, '基础文化章' if index < 4 else '双节限定章', 19, COLORS['stone_gray'], 'sans', 480)}
</g>''')
    body = f'''
<g id="stamp-system">
  <rect x="120" y="530" width="1360" height="1450" rx="52" fill="{COLORS['city_blue']}"/>
  {image('../../04_renders/stamp_grid.png', 130, 600, 1340, 1050)}
  {text(200, 1770, '六枚归位，拼成一幅城市路径', 36, COLORS['moon_paper'], 'serif', 700)}
  {text(200, 1840, '单枚 32 × 32 × 23 mm · 有效章面 26 × 26 mm', 22, COLORS['route_gold'], 'latin', 520)}
  <rect x="1540" y="530" width="810" height="1450" rx="52" fill="#FAF6EC" stroke="#D4C29C" stroke-width="3"/>
  {image('../../02_identity/stamp_faces.svg', 1580, 610, 730, 800)}
  {text(1610, 1510, '章面制造约束', 34, COLORS['city_blue'], 'serif', 700)}
  {wrapped_lines(1610, 1590, ['单色矢量路径', '最细线宽 ≥ 0.6 mm', '最小反白间距 ≥ 0.8 mm', '章面可替换，章柄持续使用'], 22, COLORS['stone_gray'], 48)}
  {''.join(label_cards)}
  {text(150, 2890, '限定章用于节日场景，不虚构新的历史典故。基础四章的节点名称在投稿前再次人工核对。', 21, COLORS['stone_gray'], 'sans', 420)}
</g>
'''
    return wrap(5, "六枚章，一座城", "STAMP SYSTEM · 基础文化章与双节限定章", body)


def board_06() -> str:
    body = f'''
<g id="festival-scenarios">
  <g transform="translate(120 540)">
    <rect width="1080" height="1850" rx="56" fill="#102F38"/>
    <circle cx="780" cy="370" r="240" fill="{COLORS['route_gold']}" opacity=".16"/>
    <circle cx="780" cy="370" r="160" fill="none" stroke="{COLORS['route_gold']}" stroke-width="5"/>
    {text(80, 105, 'MID-AUTUMN', 18, COLORS['route_gold'], 'latin', 720, spacing=4)}
    {text(80, 185, '月下邯郸', 52, COLORS['moon_paper'], 'serif', 740)}
    {image('../../02_identity/folding_map.svg', 55, 280, 970, 760)}
    {text(80, 1150, '夜游路线卡', 30, COLORS['moon_paper'], 'sans', 650)}
    {wrapped_lines(80, 1220, ['月相金线只改变路线图层，', '章匣结构与全年版保持一致。'], 24, COLORS['moon_paper'], 50, 'sans', 360)}
    {image('../../04_renders/map_unfolded.png', 80, 1390, 920, 360)}
  </g>
  <g transform="translate(1280 540)">
    <rect width="1080" height="1850" rx="56" fill="#FAF6EC" stroke="#D4C29C" stroke-width="3"/>
    <path d="M680 190 L770 80 L850 170 L940 45 L1020 190 Z" fill="none" stroke="{COLORS['seal_red']}" stroke-width="9"/>
    {text(80, 105, 'NATIONAL DAY', 18, COLORS['seal_red'], 'latin', 720, spacing=4)}
    {text(80, 185, '山河同游', 52, COLORS['city_blue'], 'serif', 740)}
    {image('../../04_renders/hero_open.png', 45, 260, 990, 820)}
    {text(80, 1150, '黄金周城市漫游', 30, COLORS['city_blue'], 'sans', 650)}
    {wrapped_lines(80, 1220, ['提高印泥朱与路线节点比例，', '不使用国旗变形或泛庆典贴图。'], 24, COLORS['stone_gray'], 50, 'sans', 360)}
    {image('../../04_renders/scale_view.png', 80, 1390, 920, 360)}
  </g>
  <rect x="120" y="2490" width="2240" height="480" rx="46" fill="{COLORS['city_blue']}"/>
  {text(200, 2610, '节日是场景，不是文化替代', 40, COLORS['moon_paper'], 'serif', 720)}
  {wrapped_lines(200, 2700, ['产品全年可售；中秋与国庆只替换两枚限定章和一张路线卡。', '所有活动、营业时间与优惠信息均不写入固定展板，避免动态信息失真。'], 25, COLORS['moon_paper'], 55, 'sans', 360)}
</g>
'''
    return wrap(6, "一匣两季，全年可用", "SEASONAL EDITIONS · 中秋夜游与国庆漫游", body)


def board_07() -> str:
    scenarios = [
        ("01", "青年漫游", "不按模板打卡，按兴趣选择节点。", "#173B46"),
        ("02", "亲子研学", "把典故理解变成一次可完成的任务。", "#A83B32"),
        ("03", "城市礼赠", "章、地图和记录共同构成可持续纪念。", "#586F66"),
    ]
    blocks = []
    for index, (number, title_value, desc, color) in enumerate(scenarios):
        x = 130 + index * 750
        blocks.append(f'''
<g transform="translate({x} 650)">
  <rect width="690" height="1260" rx="50" fill="#FAF6EC" stroke="#D4C29C" stroke-width="3"/>
  <rect width="690" height="410" rx="50" fill="{color}"/>
  {text(60, 90, number, 19, COLORS['route_gold'], 'latin', 760, spacing=3)}
  {text(60, 185, title_value, 44, COLORS['moon_paper'], 'serif', 720)}
  <path d="M60 260 H560" stroke="{COLORS['route_gold']}" stroke-width="5"/>
  {wrapped_lines(60, 510, [desc[:14], desc[14:]], 26, COLORS['city_blue'], 52, 'sans', 400)}
  {text(60, 720, ['SELECT','LEARN','KEEP'][index], 18, COLORS['route_gold'], 'latin', 720, spacing=4)}
  {text(60, 805, ['选择一条路','理解一则典故','留下个人记录'][index], 30, COLORS['city_blue'], 'sans', 650)}
  {wrapped_lines(60, 900, [['轻量、离线、可独立完成。','路线不是任务清单。'],['操作动作帮助记忆，','不把学习做成说教。'],['扩展章可持续购买，','盒体不因节日废弃。']][index], 22, COLORS['stone_gray'], 48)}
</g>''')
    body = f'''
<g id="scenarios">
  {''.join(blocks)}
  <rect x="130" y="2040" width="2190" height="900" rx="54" fill="{COLORS['city_blue']}"/>
  {image('../../04_renders/hero_open.png', 1080, 2010, 1180, 860)}
  {text(210, 2190, '不是纪念章的终点，', 44, COLORS['moon_paper'], 'serif', 720)}
  {text(210, 2260, '而是理解城市的起点。', 44, COLORS['moon_paper'], 'serif', 720)}
  {text(210, 2410, 'TARGET', 18, COLORS['route_gold'], 'latin', 720, spacing=4)}
  {wrapped_lines(210, 2485, ['18–35 岁城市游客', '亲子研学家庭', '高校社团与博物馆教育'], 25, COLORS['moon_paper'], 52, 'sans', 380)}
</g>
'''
    return wrap(7, "把城市带回去，也把理解留下", "SCENARIOS · 漫游、研学与城市礼赠", body)


def board_08() -> str:
    body = f'''
<g id="landing">
  <rect x="120" y="530" width="2240" height="900" rx="56" fill="{COLORS['city_blue']}"/>
  {image('../../04_renders/hero_closed.png', 1090, 500, 1210, 880)}
  {text(210, 670, '从数字模型，到可验证样机', 48, COLORS['moon_paper'], 'serif', 740)}
  {text(210, 785, '01', 20, COLORS['route_gold'], 'latin', 760)}{text(280, 785, '树脂 / FDM 首件', 27, COLORS['moon_paper'], 'sans', 620)}
  {text(210, 875, '02', 20, COLORS['route_gold'], 'latin', 760)}{text(280, 875, '三档滑动间隙试件', 27, COLORS['moon_paper'], 'sans', 620)}
  {text(210, 965, '03', 20, COLORS['route_gold'], 'latin', 760)}{text(280, 965, '章面与印台污染测试', 27, COLORS['moon_paper'], 'sans', 620)}
  {text(210, 1055, '04', 20, COLORS['route_gold'], 'latin', 760)}{text(280, 1055, '路线与信息人工复核', 27, COLORS['moon_paper'], 'sans', 620)}
  {text(210, 1210, '当前完成：CAD、STEP、STL、渲染与投稿版式', 21, COLORS['route_gold'], 'sans', 500)}
  <g transform="translate(120 1550)">
    {card(0,0,700,700)}{text(60, 95, 'CMF', 18, COLORS['route_gold'], 'latin', 720, spacing=3)}{text(60, 175, '材料与工艺', 38, COLORS['city_blue'], 'serif', 700)}{wrapped_lines(60, 280, ['小批量：3D 打印外匣', '硅胶 / 光敏章面', 'FSC 折页地图', '标准水性印台'], 24, COLORS['stone_gray'], 55)}
  </g>
  <g transform="translate(890 1550)">
    {card(0,0,700,700)}{text(60, 95, 'PRICE', 18, COLORS['route_gold'], 'latin', 720, spacing=3)}{text(60, 175, '定位估算', 38, COLORS['city_blue'], 'serif', 700)}{text(60, 310, '¥159–199', 52, COLORS['city_blue'], 'latin', 760)}{text(60, 365, '完整六章套装', 22, COLORS['stone_gray'], 'sans', 500)}{text(60, 490, '¥39–59', 52, COLORS['seal_red'], 'latin', 760)}{text(60, 545, '双章主题补充组', 22, COLORS['stone_gray'], 'sans', 500)}
  </g>
  <g transform="translate(1660 1550)">
    {card(0,0,700,700)}{text(60, 95, 'FILES', 18, COLORS['route_gold'], 'latin', 720, spacing=3)}{text(60, 175, '可编辑交付', 38, COLORS['city_blue'], 'serif', 700)}{wrapped_lines(60, 280, ['FreeCAD / STEP / STL', 'SVG / PDF / JPG', '字体与来源清单', '生成哈希与审计报告'], 24, COLORS['stone_gray'], 55)}
  </g>
  <rect x="120" y="2370" width="2240" height="590" rx="50" fill="#102F38"/>
  {text(200, 2490, 'VALIDATION BOUNDARY', 18, COLORS['route_gold'], 'latin', 760, spacing=4)}
  {text(200, 2580, '技术文件可复现，不等于实体性能已验证', 40, COLORS['moon_paper'], 'serif', 700)}
  {wrapped_lines(200, 2690, ['未完成：100 次抽拉、耐折、印泥污染、儿童安全与 1 m 跌落。', '文化路线示意；动态景点信息仍须真人核对，当前状态为投稿候选稿。'], 25, COLORS['moon_paper'], 56, 'sans', 360)}
  <circle cx="2150" cy="2660" r="110" fill="none" stroke="{COLORS['seal_red']}" stroke-width="8"/>
  {text(2150, 2648, '诚实', 34, COLORS['moon_paper'], 'serif', 760, 'middle')}{text(2150, 2695, '可继续验证', 18, COLORS['route_gold'], 'sans', 520, 'middle')}
</g>
'''
    return wrap(8, "可落地，也保留验证边界", "DELIVERY · 材料、价格、文件与下一步", body)


def main() -> None:
    BOARD_DIR.mkdir(parents=True, exist_ok=True)
    boards = [
        board_01(),
        board_02(),
        board_03(),
        board_04(),
        board_05(),
        board_06(),
        board_07(),
        board_08(),
    ]
    for index, content in enumerate(boards, start=1):
        (BOARD_DIR / f"board_{index:02d}.svg").write_text(content, encoding="utf-8")
    manifest = {
        "count": len(boards),
        "size_px": [W, H],
        "dpi": BOARD.dpi,
        "titles": [
            "步步生典",
            "从学步，到走出自己的路",
            "四步完成一次城市印记",
            "结构不是效果图",
            "六枚章，一座城",
            "一匣两季，全年可用",
            "把城市带回去，也把理解留下",
            "可落地，也保留验证边界",
        ],
        "route_disclaimer": COPY["route_disclaimer"],
        "product_envelope_mm": [PRODUCT.width, PRODUCT.depth, PRODUCT.height],
    }
    (BOARD_DIR / "board_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
