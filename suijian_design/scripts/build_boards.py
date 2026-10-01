"""Compose seven editable A4 SVG competition boards from frozen assets."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from xml.sax.saxutils import escape


PROJECT_DIR = Path(__file__).resolve().parents[1]
BOARD_DIR = PROJECT_DIR / "05_boards" / "src"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from design_config import BOARD, COLORS, COPY, PRODUCT


W, H = BOARD.width_px, BOARD.height_px
BG = "#F3EEE2"
GRID = "#D5CBB8"


def image(path: str, x: int, y: int, width: int, height: int, opacity: float = 1.0, extra: str = "") -> str:
    return f'<image href="{path}" x="{x}" y="{y}" width="{width}" height="{height}" opacity="{opacity}" preserveAspectRatio="xMidYMid meet" {extra}/>'


def text(x: int, y: int, value: str, size: int, color: str, css: str = "sans", weight: int = 400, anchor: str = "start", opacity: float = 1.0, spacing: int | float = 0) -> str:
    return (
        f'<text class="{css}" x="{x}" y="{y}" fill="{color}" font-size="{size}" '
        f'font-weight="{weight}" text-anchor="{anchor}" opacity="{opacity}" '
        f'letter-spacing="{spacing}">{escape(value)}</text>'
    )


def multiline(x: int, y: int, lines: list[str], size: int, line_height: int, color: str, css: str = "sans", weight: int = 400, opacity: float = 1.0) -> str:
    tspans = "".join(
        f'<tspan x="{x}" dy="{0 if index == 0 else line_height}">{escape(line)}</tspan>'
        for index, line in enumerate(lines)
    )
    return f'<text class="{css}" x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" opacity="{opacity}">{tspans}</text>'


def pill(x: int, y: int, width: int, label: str, dark: bool = False) -> str:
    fill = COLORS["ding_gold"] if dark else COLORS["zhao_lacquer"]
    ink = COLORS["zhao_lacquer"] if dark else COLORS["silk_white"]
    return f'<g><rect x="{x}" y="{y}" width="{width}" height="62" rx="31" fill="{fill}"/>{text(x + width // 2, y + 41, label, 22, ink, "latin", 700, "middle", spacing=3)}</g>'


def shared_defs() -> str:
    return f"""
<defs>
  <filter id="shadow" x="-30%" y="-30%" width="160%" height="180%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="24" result="blur"/>
    <feOffset dy="34" result="offset"/>
    <feColorMatrix in="offset" type="matrix" values="0 0 0 0 0.02 0 0 0 0 0.12 0 0 0 0 0.13 0 0 0 .28 0"/>
    <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <linearGradient id="goldLine" x1="0" y1="1" x2="1" y2="0">
    <stop offset="0" stop-color="#8D672F"/><stop offset=".55" stop-color="{COLORS['ding_gold']}"/><stop offset="1" stop-color="#E0BD79"/>
  </linearGradient>
  <radialGradient id="deepGlow" cx="78%" cy="18%" r="84%">
    <stop offset="0" stop-color="#1C5557"/><stop offset=".56" stop-color="{COLORS['zhao_lacquer']}"/><stop offset="1" stop-color="#071E20"/>
  </radialGradient>
  <style>
    @font-face {{ font-family:'Noto Sans SC'; src:url('../../01_research/fonts/NotoSansSC%5Bwght%5D.ttf'); }}
    @font-face {{ font-family:'Noto Serif SC'; src:url('../../01_research/fonts/NotoSerifSC%5Bwght%5D.ttf'); }}
    @font-face {{ font-family:'Inter'; src:url('../../01_research/fonts/InterVariable.ttf'); }}
    .sans {{ font-family:'Noto Sans SC',sans-serif; }}
    .serif {{ font-family:'Noto Serif SC',serif; }}
    .latin {{ font-family:'Inter',sans-serif; }}
  </style>
</defs>
"""


def header(number: int, title: str, subtitle: str, dark: bool) -> str:
    ink = COLORS["silk_white"] if dark else COLORS["zhao_lacquer"]
    soft = COLORS["silk_white"] if dark else COLORS["ink_black"]
    return f"""
<g id="header">
  {text(160, 188, f'{number:02d} / 07', 22, COLORS['ding_gold'], 'latin', 700, spacing=4)}
  {text(160, 318, title, 92, ink, 'serif', 720, spacing=4)}
  {text(162, 380, subtitle, 27, soft, 'sans', 350, opacity=.68, spacing=2)}
  <path d="M160 442 H2320" stroke="{COLORS['ding_gold']}" stroke-width="4" opacity=".65"/>
</g>
"""


def footer(number: int, dark: bool) -> str:
    ink = COLORS["silk_white"] if dark else COLORS["ink_black"]
    return f"""
<g id="footer" opacity=".56">
  <path d="M160 3294 H2320" stroke="{ink}" stroke-width="2" opacity=".34"/>
  {text(160, 3352, 'SUIJIAN · HANDAN IDIOM CULTURAL PRODUCT', 16, ink, 'latin', 560, spacing=3)}
  {text(2320, 3352, f'{number:02d}', 18, COLORS['ding_gold'], 'latin', 720, 'end', spacing=2)}
</g>
"""


def wrap(number: int, title: str, subtitle: str, body: str, dark: bool = False) -> str:
    background = "url(#deepGlow)" if dark else BG
    accent = f"""
<path d="M-180 3060 L2680 2210" stroke="{COLORS['ding_gold']}" stroke-width="4" opacity=".13"/>
<circle cx="2290" cy="170" r="12" fill="{COLORS['oath_vermilion']}"/>
"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<title>{escape(title)}</title>
{shared_defs()}
<rect width="{W}" height="{H}" fill="{background}"/>
{accent}
{header(number, title, subtitle, dark)}
{body}
{footer(number, dark)}
</svg>
"""


def board_01() -> str:
    body = f"""
<g id="hero">
  <ellipse cx="1320" cy="2320" rx="920" ry="235" fill="#041617" opacity=".36"/>
  {image('../../04_renders/hero_closed.png', 160, 610, 2160, 2160, extra='filter="url(#shadow)"')}
  <path d="M160 2660 H760" stroke="url(#goldLine)" stroke-width="12"/>
  {text(160, 2778, COPY['tagline'], 78, COLORS['silk_white'], 'serif', 700, spacing=5)}
  {text(162, 2844, COPY['culture_line'], 27, COLORS['ding_gold'], 'serif', 450, spacing=5)}
  {multiline(1540, 2735, ['以“囊—锥—颖—言”的动作链', '把毛遂自荐转译为现代青年社交产品'], 26, 44, COLORS['silk_white'], opacity=.72)}
  {pill(160, 3015, 278, 'CULTURAL PRODUCT', True)}
  {pill(466, 3015, 238, 'CAD VERIFIED', True)}
  {pill(732, 3015, 252, 'MODEL READY', True)}
</g>
"""
    return wrap(1, COPY["name_zh"], f"{COPY['category']} · {COPY['name_en']}", body, True)


def board_02() -> str:
    steps = [
        ("囊", "收纳", "深青外匣保护卡片", "01"),
        ("锥", "推动", "17°斜线引导动作", "02"),
        ("颖", "显现", "末段抬升便于抽取", "03"),
        ("言", "连接", "纸卡与数字身份并行", "04"),
    ]
    cards = []
    for index, (char, label, desc, number) in enumerate(steps):
        x = 160 + index * 555
        cards.append(
            f"""
<g transform="translate({x} 690)">
  <rect width="500" height="780" rx="40" fill="{'#FFFFFF' if index % 2 == 0 else COLORS['zhao_lacquer']}" stroke="{COLORS['ding_gold']}" stroke-width="3"/>
  {text(52, 82, number, 18, COLORS['ding_gold'], 'latin', 700, spacing=3)}
  {text(250, 365, char, 210, COLORS['zhao_lacquer'] if index % 2 == 0 else COLORS['silk_white'], 'serif', 700, 'middle')}
  <path d="M70 440 H430" stroke="{COLORS['ding_gold']}" stroke-width="6"/>
  {text(250, 535, label, 40, COLORS['zhao_lacquer'] if index % 2 == 0 else COLORS['silk_white'], 'serif', 650, 'middle', spacing=6)}
  {text(250, 603, desc, 23, COLORS['ink_black'] if index % 2 == 0 else COLORS['silk_white'], 'sans', 350, 'middle', opacity=.72)}
</g>
"""
        )
    body = f"""
{''.join(cards)}
<g id="story-chain">
  {image('../../04_renders/exploded.png', 1050, 1510, 1280, 1280)}
  {text(160, 1670, '不是贴上一个成语', 58, COLORS['zhao_lacquer'], 'serif', 720)}
  {text(160, 1750, '而是让产品完成一次“脱颖而出”', 39, COLORS['ding_gold'], 'serif', 560)}
  {multiline(160, 1870, ['用户推动内托，卡片沿楔形结构抬升。', '动作本身成为典故的当代表达。'], 28, 52, COLORS['ink_black'], opacity=.70)}
  <rect x="160" y="2320" width="820" height="450" rx="36" fill="{COLORS['zhao_lacquer']}"/>
  {text(220, 2415, '文化依据', 27, COLORS['ding_gold'], 'sans', 650, spacing=4)}
  {multiline(220, 2495, ['毛遂自荐、脱颖而出、一言九鼎', '共同源自赵都邯郸的历史叙事。', '本设计不复原人物肖像，不虚构文物。'], 28, 56, COLORS['silk_white'], opacity=.86)}
  {text(160, 3060, '资料：河北省文化和旅游厅《邯郸成语典故文化》；中央纪委国家监委网站“一言九鼎”典故说明。', 18, COLORS['ink_black'], 'sans', 350, opacity=.52)}
</g>
"""
    return wrap(2, "从典故到交互", "CULTURE BECOMES ACTION · 文化不是装饰，而是使用方式", body)


def board_03() -> str:
    stages = [
        ("闭合", "01 · READY", "../../04_renders/interaction_01.png"),
        ("推出", "02 · MOVE", "../../04_renders/interaction_02.png"),
        ("显现", "03 · REVEAL", "../../04_renders/interaction_03.png"),
    ]
    panels = []
    for index, (zh, en, path) in enumerate(stages):
        x = 120 + index * 790
        panels.append(
            f"""
<g transform="translate({x} 690)">
  <rect width="740" height="1320" rx="48" fill="#F3EEE2" opacity=".98"/>
  {image(path, 10, 120, 720, 720)}
  {text(58, 920, zh, 66, COLORS['zhao_lacquer'], 'serif', 720)}
  {text(58, 978, en, 18, COLORS['ding_gold'], 'latin', 700, spacing=3)}
  <path d="M58 1032 H682" stroke="{COLORS['ding_gold']}" stroke-width="3"/>
  {multiline(58, 1110, [
      ['掌心尺寸，完整收纳', '磁吸止位形成闭合反馈'],
      ['拇指推动内托', '结构沿单一导轨移动'],
      ['末段抬升 7 mm', '三秒内完成展示与取卡'],
  ][index], 25, 48, COLORS['ink_black'], opacity=.70)}
</g>
"""
        )
    body = f"""
{''.join(panels)}
<g id="dimension-strip">
  <rect x="160" y="2190" width="2160" height="680" rx="46" fill="#071E20" stroke="{COLORS['ding_gold']}" stroke-width="3"/>
  {text(220, 2284, 'PRODUCT BASELINE', 18, COLORS['ding_gold'], 'latin', 720, spacing=4)}
  {text(220, 2440, '98 × 65 × 14', 105, COLORS['silk_white'], 'latin', 660, spacing=1)}
  {text(1030, 2440, 'mm', 36, COLORS['ding_gold'], 'latin', 560)}
  {text(220, 2520, '闭合尺寸 / PARAMETRIC CAD BASELINE', 21, COLORS['silk_white'], 'sans', 350, opacity=.58, spacing=2)}
  {text(1260, 2360, '28 mm', 66, COLORS['silk_white'], 'latin', 650)}
  {text(1260, 2425, '滑动行程 TRAVEL', 20, COLORS['ding_gold'], 'sans', 450, spacing=2)}
  {text(1740, 2360, '7 mm', 66, COLORS['silk_white'], 'latin', 650)}
  {text(1740, 2425, '末段抬升 LIFT', 20, COLORS['ding_gold'], 'sans', 450, spacing=2)}
  <path d="M1260 2538 H2190" stroke="{COLORS['ding_gold']}" stroke-width="3" opacity=".42"/>
  {text(1260, 2620, '兼容 90×54 mm / 85.6×54 mm 常用卡片', 24, COLORS['silk_white'], 'sans', 360, opacity=.74)}
  {text(1260, 2680, '建议容量 8–10 张 0.3 mm 纸质名片', 24, COLORS['silk_white'], 'sans', 360, opacity=.74)}
</g>
"""
    return wrap(3, "三秒完成一次自荐", "ONE MOTION · 三个状态使用同一套 CAD 几何与相机语言", body, True)


def board_04() -> str:
    callouts = [
        ("01", "外匣", "PC+ABS 量产设想", 190, 1700),
        ("02", "内托", "单一导轨 / 0.35 mm 间隙", 1620, 1510),
        ("03", "抬升片", "POM 低摩擦楔形结构", 1650, 2040),
        ("04", "金属饰条", "17°斜向视觉识别", 170, 2220),
        ("05", "卡片", "纸卡与 NFC 独立卡位", 1560, 2550),
    ]
    callout_svg = []
    for number, title, desc, x, y in callouts:
        callout_svg.append(
            f"""
<g transform="translate({x} {y})">
  <circle cx="0" cy="0" r="34" fill="{COLORS['oath_vermilion']}"/>
  {text(0, 8, number, 15, '#FFFFFF', 'latin', 720, 'middle')}
  {text(58, -2, title, 28, COLORS['zhao_lacquer'], 'serif', 650)}
  {text(58, 36, desc, 19, COLORS['ink_black'], 'sans', 350, opacity=.64)}
</g>
"""
        )
    body = f"""
<g id="exploded-engineering">
  <ellipse cx="1230" cy="1700" rx="760" ry="220" fill="#0D2F32" opacity=".10"/>
  {image('../../04_renders/exploded.png', 320, 470, 1840, 1840)}
  {''.join(callout_svg)}
</g>
<g id="engineering-strip">
  <rect x="160" y="2760" width="2160" height="360" rx="36" fill="{COLORS['zhao_lacquer']}"/>
  {text(220, 2845, 'ENGINEERING CREDIBILITY', 18, COLORS['ding_gold'], 'latin', 720, spacing=4)}
  {text(220, 2940, '1.8 mm', 58, COLORS['silk_white'], 'latin', 650)}
  {text(220, 2990, '基准壁厚', 20, COLORS['silk_white'], 'sans', 350, opacity=.64)}
  {text(650, 2940, '0.35 mm', 58, COLORS['silk_white'], 'latin', 650)}
  {text(650, 2990, '滑动面基准间隙', 20, COLORS['silk_white'], 'sans', 350, opacity=.64)}
  {text(1180, 2940, '5 SOLIDS', 58, COLORS['silk_white'], 'latin', 650)}
  {text(1180, 2990, 'STEP 重新打开验证', 20, COLORS['silk_white'], 'sans', 350, opacity=.64)}
  {text(1760, 2940, 'FCStd / STEP / STL', 30, COLORS['silk_white'], 'latin', 650)}
  {text(1760, 2990, '可编辑与可打样源文件', 20, COLORS['silk_white'], 'sans', 350, opacity=.64)}
</g>
"""
    return wrap(4, "结构不是效果图", "PARAMETRIC ENGINEERING · 尺寸、零件与导出文件可重新生成", body)


def board_05() -> str:
    swatches = [
        ("赵漆青", COLORS["zhao_lacquer"], "#0D2F32"),
        ("鼎金", COLORS["ding_gold"], "#B68B48"),
        ("誓朱", COLORS["oath_vermilion"], "#A64032"),
        ("帛白", COLORS["silk_white"], "#E8DFCC"),
    ]
    swatch_svg = []
    for index, (name, color, code) in enumerate(swatches):
        x = 160 + index * 410
        swatch_svg.append(
            f"""
<g transform="translate({x} 2640)">
  <rect width="350" height="170" rx="26" fill="{color}" stroke="{COLORS['ding_gold']}" stroke-width="2"/>
  {text(0, 224, name, 25, COLORS['silk_white'], 'sans', 520)}
  {text(350, 224, code, 16, COLORS['ding_gold'], 'latin', 560, 'end', spacing=2)}
</g>
"""
        )
    body = f"""
<g id="cmf-hero">
  {image('../../04_renders/detail_accent.png', 80, 500, 1440, 1440)}
  <rect x="1390" y="610" width="930" height="780" rx="44" fill="#F3EEE2"/>
  {image('../../02_identity/wordmark.svg', 1440, 680, 830, 300)}
  {text(1450, 1080, '视觉识别不依赖泛国潮纹样', 38, COLORS['zhao_lacquer'], 'serif', 680)}
  {multiline(1450, 1150, ['圆角长方体控制整体秩序', '17°金线承担锥锋与行动方向', '九枚侧边压纹回应“一言九鼎”'], 24, 48, COLORS['ink_black'], opacity=.68)}
</g>
<g id="detail-system">
  <rect x="160" y="1740" width="2160" height="690" rx="46" fill="#071E20"/>
  {text(220, 1832, 'CMF / DETAIL SYSTEM', 18, COLORS['ding_gold'], 'latin', 720, spacing=4)}
  {image('../../04_renders/hero_closed.png', 150, 1790, 870, 610)}
  {text(1040, 1945, '65%', 74, COLORS['silk_white'], 'latin', 650)}
  {text(1040, 2002, '赵漆青主体', 22, COLORS['silk_white'], 'sans', 350, opacity=.62)}
  {text(1390, 1945, '25%', 74, COLORS['silk_white'], 'latin', 650)}
  {text(1390, 2002, '帛白信息层', 22, COLORS['silk_white'], 'sans', 350, opacity=.62)}
  {text(1740, 1945, '8%', 74, COLORS['silk_white'], 'latin', 650)}
  {text(1740, 2002, '鼎金结构点', 22, COLORS['silk_white'], 'sans', 350, opacity=.62)}
  {text(2040, 1945, '≤2%', 74, COLORS['silk_white'], 'latin', 650)}
  {text(2040, 2002, '誓朱提示', 22, COLORS['silk_white'], 'sans', 350, opacity=.62)}
  <path d="M1040 2085 H2180" stroke="{COLORS['ding_gold']}" stroke-width="4" opacity=".56"/>
  {text(1040, 2170, 'MATTE PC+ABS', 23, COLORS['silk_white'], 'latin', 560, spacing=3)}
  {text(1450, 2170, 'ANODISED ALUMINIUM', 23, COLORS['silk_white'], 'latin', 560, spacing=3)}
  {text(1990, 2170, 'PAPER', 23, COLORS['silk_white'], 'latin', 560, spacing=3)}
</g>
{''.join(swatch_svg)}
"""
    return wrap(5, "克制的当代赵文化", "FORM & CMF · 深青、鼎金、誓朱构成可延展的产品语言", body, True)


def board_06() -> str:
    panels = []
    scenarios = [
        ("校园招聘", "CAMPUS RECRUITMENT", "作品与身份一次呈现", "../../04_renders/hero_open.png"),
        ("创意展会", "CREATIVE EXHIBITION", "三秒建立面对面连接", "../../04_renders/scale_view.png"),
        ("作品交流", "PORTFOLIO REVIEW", "纸卡与数字主页并行", "../../04_renders/hero_closed.png"),
    ]
    for index, (zh, en, desc, asset) in enumerate(scenarios):
        x = 120 + index * 790
        background = COLORS["zhao_lacquer"] if index != 1 else "#FFFFFF"
        foreground = COLORS["silk_white"] if index != 1 else COLORS["zhao_lacquer"]
        scene = (
            '<circle cx="370" cy="250" r="94" fill="#B68B48" opacity=".22"/><path d="M190 570 C230 350 510 350 550 570" fill="none" stroke="#B68B48" stroke-width="20" opacity=".34"/>'
            if index == 0
            else '<path d="M95 230 H645 V570 H95 Z M170 310 H570 M170 385 H480" fill="none" stroke="#B68B48" stroke-width="18" opacity=".26"/>'
            if index == 1
            else '<rect x="110" y="230" width="520" height="310" rx="24" fill="none" stroke="#B68B48" stroke-width="18" opacity=".28"/><path d="M220 610 H520" stroke="#B68B48" stroke-width="20" opacity=".28"/>'
        )
        panels.append(
            f"""
<g transform="translate({x} 650)">
  <rect width="740" height="1850" rx="52" fill="{background}" stroke="{COLORS['ding_gold']}" stroke-width="3"/>
  {scene}
  {image(asset, 20, 330, 700, 760)}
  <path d="M62 1145 H678" stroke="{COLORS['ding_gold']}" stroke-width="5"/>
  {text(62, 1260, zh, 54, foreground, 'serif', 700)}
  {text(64, 1312, en, 16, COLORS['ding_gold'], 'latin', 700, spacing=3)}
  {text(62, 1400, desc, 24, foreground, 'sans', 350, opacity=.68)}
  {text(62, 1580, ['初次见面', '展台交流', '作品讨论'][index], 22, COLORS['ding_gold'], 'sans', 560, spacing=3)}
  {multiline(62, 1640, [
      ['取出—推出—递交', '动作明确，不需要额外教学'],
      ['实体名片保留仪式感', 'NFC/二维码承载更多内容'],
      ['产品保持安静', '让作品与对话成为主角'],
  ][index], 23, 46, foreground, opacity=.62)}
</g>
"""
        )
    body = f"""
{''.join(panels)}
<g id="audience">
  {text(160, 2695, '为主动表达的人设计', 58, COLORS['zhao_lacquer'], 'serif', 720)}
  {text(160, 2760, '设计学生 · 青年创作者 · 独立从业者 · 城市文化礼赠', 26, COLORS['ink_black'], 'sans', 360, opacity=.64, spacing=3)}
  <path d="M160 2842 H2320" stroke="{COLORS['ding_gold']}" stroke-width="4"/>
  {text(160, 2945, '产品不代替表达', 34, COLORS['zhao_lacquer'], 'serif', 620)}
  {text(160, 3000, '它只让第一步更自然。', 34, COLORS['ding_gold'], 'serif', 620)}
</g>
"""
    return wrap(6, "从“自荐”到“被看见”", "SCENARIO SYSTEM · 用真实动作连接校园、展会与作品交流", body)


def board_07() -> str:
    body = f"""
<g id="package-and-market">
  {image('../../04_renders/packaging_hero.png', 70, 500, 1450, 1450)}
  <rect x="1390" y="650" width="930" height="910" rx="50" fill="#F3EEE2"/>
  {text(1450, 750, '从模型到产品', 58, COLORS['zhao_lacquer'], 'serif', 700)}
  {text(1450, 812, 'PROTOTYPE → PRODUCTION', 16, COLORS['ding_gold'], 'latin', 720, spacing=3)}
  <path d="M1450 870 H2260" stroke="{COLORS['ding_gold']}" stroke-width="4"/>
  {text(1450, 958, '打样模型', 30, COLORS['zhao_lacquer'], 'serif', 650)}
  {multiline(1450, 1015, ['树脂/FDM 3D打印', '喷涂与薄铝片饰件', '现成 NTAG213 演示卡'], 22, 44, COLORS['ink_black'], opacity=.68)}
  {text(1880, 958, '量产设想', 30, COLORS['zhao_lacquer'], 'serif', 650)}
  {multiline(1880, 1015, ['PC+ABS 注塑外壳', 'POM低摩擦抬升片', '纸浆模塑包装内托'], 22, 44, COLORS['ink_black'], opacity=.68)}
  <rect x="1450" y="1260" width="750" height="180" rx="28" fill="{COLORS['zhao_lacquer']}"/>
  {text(1495, 1320, '建议零售价估算', 20, COLORS['ding_gold'], 'sans', 520, spacing=3)}
  {text(1495, 1402, '¥99–129 / ¥149–199', 40, COLORS['silk_white'], 'latin', 650)}
</g>
<g id="market-system">
  <rect x="160" y="1850" width="2160" height="1120" rx="52" fill="#071E20" stroke="{COLORS['ding_gold']}" stroke-width="3"/>
  {text(220, 1940, 'MARKET & DELIVERY', 18, COLORS['ding_gold'], 'latin', 720, spacing=4)}
  {text(220, 2068, '一件产品，三种进入市场的方式', 52, COLORS['silk_white'], 'serif', 700)}
  <path d="M220 2140 H2260" stroke="{COLORS['ding_gold']}" stroke-width="3" opacity=".46"/>
  <g transform="translate(220 2240)">
    <circle cx="66" cy="66" r="66" fill="{COLORS['ding_gold']}"/><text class="latin" x="66" y="76" text-anchor="middle" fill="{COLORS['zhao_lacquer']}" font-size="25" font-weight="800">01</text>
    {text(170, 40, '城市礼物', 33, COLORS['silk_white'], 'serif', 650)}
    {text(170, 92, '邯郸道、文创旗舰店、博物馆商店', 22, COLORS['silk_white'], 'sans', 350, opacity=.62)}
  </g>
  <g transform="translate(220 2480)">
    <circle cx="66" cy="66" r="66" fill="{COLORS['ding_gold']}"/><text class="latin" x="66" y="76" text-anchor="middle" fill="{COLORS['zhao_lacquer']}" font-size="25" font-weight="800">02</text>
    {text(170, 40, '青年职业礼赠', 33, COLORS['silk_white'], 'serif', 650)}
    {text(170, 92, '毕业季、招聘活动、创意展会', 22, COLORS['silk_white'], 'sans', 350, opacity=.62)}
  </g>
  <g transform="translate(1240 2240)">
    <circle cx="66" cy="66" r="66" fill="{COLORS['ding_gold']}"/><text class="latin" x="66" y="76" text-anchor="middle" fill="{COLORS['zhao_lacquer']}" font-size="25" font-weight="800">03</text>
    {text(170, 40, '机构定制', 33, COLORS['silk_white'], 'serif', 650)}
    {text(170, 92, '院校、文化机构、设计团队', 22, COLORS['silk_white'], 'sans', 350, opacity=.62)}
  </g>
  <g transform="translate(1240 2480)">
    <circle cx="66" cy="66" r="66" fill="{COLORS['oath_vermilion']}"/><text class="latin" x="66" y="76" text-anchor="middle" fill="#FFFFFF" font-size="25" font-weight="800">!</text>
    {text(170, 40, '事实边界', 33, COLORS['silk_white'], 'serif', 650)}
    {text(170, 92, '尚未供应商询价、量产或市场销售', 22, COLORS['silk_white'], 'sans', 350, opacity=.62)}
  </g>
  {text(220, 2835, '所有价格均为建议零售价估算；最终结构、公差与成本需通过实体打样及供应商评估确认。', 20, COLORS['silk_white'], 'sans', 350, opacity=.54)}
</g>
"""
    return wrap(7, "可落地，也诚实", "PRODUCTISATION · 清楚区分模型、量产设想与市场估算", body, True)


def main() -> None:
    BOARD_DIR.mkdir(parents=True, exist_ok=True)
    boards = [board_01(), board_02(), board_03(), board_04(), board_05(), board_06(), board_07()]
    for index, content in enumerate(boards, start=1):
        (BOARD_DIR / f"board_{index:02d}.svg").write_text(content, encoding="utf-8")
    manifest = {
        "count": len(boards),
        "size_px": [W, H],
        "dpi": BOARD.dpi,
        "titles": ["遂见", "从典故到交互", "三秒完成一次自荐", "结构不是效果图", "克制的当代赵文化", "从自荐到被看见", "可落地，也诚实"],
        "cad_baseline_mm": [PRODUCT.width, PRODUCT.height, PRODUCT.depth],
        "source_rule": "All product imagery references the audited render set; text is editable SVG text.",
    }
    (BOARD_DIR / "board_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
