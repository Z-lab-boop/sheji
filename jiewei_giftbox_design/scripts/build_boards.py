"""Compose six editable A4 competition boards for the Jiewei gift box."""

from __future__ import annotations

import json
from pathlib import Path
import sys


PROJECT_DIR = Path(__file__).resolve().parents[1]
OUT = PROJECT_DIR / "05_boards" / "src"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from design_config import BOARD, BOX, COLORS, COPY, SKU  # noqa: E402


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
 {text(160,308,title_value,88,ink,'serif',780,spacing=2)}
 {text(162,374,subtitle,24,ink,'latin',480,opacity=.62,spacing=2)}
 <path d="M160 438 H2320" stroke="{COLORS['moon_gold']}" stroke-width="4" opacity=".72"/>
</g>'''


def footer(number, dark=False):
    ink = COLORS["paper_white"] if dark else COLORS["wall_ink"]
    return f'''
<g id="footer" opacity=".54"><path d="M160 3350 H2320" stroke="{ink}" stroke-width="2"/>
{text(160,3408,'JIEWEI · HANBAOFANG FESTIVAL GIFT-BOX CONCEPT',16,ink,'latin',520,spacing=3)}
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
 <circle cx="1940" cy="850" r="360" fill="none" stroke="{COLORS['moon_gold']}" stroke-width="4" opacity=".24"/>
 {image('../../04_renders/hero_open.png',120,430,2240,1700)}
 <rect x="150" y="2100" width="2180" height="760" rx="56" fill="#172529" stroke="{COLORS['moon_gold']}" stroke-width="3"/>
 {text(240,2285,'解围',128,COLORS['paper_white'],'serif',820,spacing=9)}
 {text(246,2375,'RELIEVE THE SIEGE',24,COLORS['moon_gold'],'latin',680,spacing=6)}
 {text(240,2515,COPY['slogan'],49,COLORS['paper_white'],'sans',650)}
 {lines(240,2625,['把“围魏救赵”的行动顺序变成开盒逻辑：','先侧移解除锁定，再让中央礼品显现。'],29,COLORS['paper_white'],54,'sans',380)}
 <g transform="translate(1610 2290)" fill="none" stroke-linejoin="miter"><path d="M0 280 H180 V160 H380" stroke="{COLORS['route_red']}" stroke-width="18"/><path d="M380 160 V40 H590" stroke="{COLORS['moon_gold']}" stroke-width="18"/><circle cx="590" cy="40" r="20" fill="{COLORS['moon_gold']}" stroke="none"/></g>
 {text(160,3030,'290 × 230 × 75 mm',27,COLORS['paper_white'],'latin',700)}
 {text(850,3030,'42 mm 侧移解锁',27,COLORS['paper_white'],'sans',620)}
 {text(1510,3030,'145 mm 中央显现',27,COLORS['paper_white'],'sans',620)}
</g>'''
    return wrap(1,"解围","TWO-STAGE UNLOCKING · 邯宝坊双节机关礼盒候选方案",body,True)


def board_02():
    cards = [
        ("01","围","避开正面强攻","战国故事中，援军不直攻赵都之围，而转向魏国要害。"),
        ("02","移","先改变侧向状态","包装先拉“魏”侧抽屉 42 mm，使两枚锁钥片离开槽位。"),
        ("03","解","限制被真正解除","两处限位同时释放，中央托盘才获得运动自由度。"),
        ("04","见","赵礼中央显现","中央“赵”托盘前行 145 mm，六件礼品形成完整陈列面。"),
    ]
    blocks=[]
    for i,(n,g,t,d) in enumerate(cards):
        x=150+(i%2)*1110; y=570+(i//2)*730
        blocks.append(f'''<g transform="translate({x} {y})">{panel(0,0,1020,620)}<circle cx="118" cy="120" r="64" fill="{COLORS['wall_ink'] if i!=1 else COLORS['route_red']}"/>{text(118,143,g,52,COLORS['paper_white'],'serif',760,'middle')}{text(220,78,n,18,COLORS['moon_gold'],'latin',760,spacing=3)}{text(220,148,t,38,COLORS['wall_ink'],'serif',720)}{lines(80,286,[d[:17],d[17:34],d[34:]],25,COLORS['soft_gray'],47,'sans',390)}<path d="M80 504 H920" stroke="{COLORS['moon_gold']}" stroke-width="4" opacity=".48"/></g>''')
    body=f'''<g id="culture">{''.join(blocks)}
<rect x="150" y="2130" width="2130" height="760" rx="52" fill="{COLORS['wall_ink']}"/>
{text(230,2280,'不是战争插画，而是顺序与约束的结构转译',43,COLORS['paper_white'],'serif',720)}
<path d="M250 2550 H720 V2440 H1210 V2600 H1710 V2470 H2170" fill="none" stroke="{COLORS['route_red']}" stroke-width="15"/><circle cx="2170" cy="2470" r="22" fill="{COLORS['moon_gold']}"/>
{text(250,2720,'围合',24,COLORS['paper_white'],'sans',620)}{text(770,2720,'侧移',24,COLORS['paper_white'],'sans',620)}{text(1260,2720,'解锁',24,COLORS['paper_white'],'sans',620)}{text(2170,2720,'中央显现',24,COLORS['paper_white'],'sans',620,'end')}
{text(160,3030,'典故逻辑依据公开成语资料核对；机构借用行动关系，不复原具体战争场景。',21,COLORS['soft_gray'],'sans',400)}</g>'''
    return wrap(2,"把典故变成必须遵守的动作","IDIOM TO MECHANISM · 围魏救赵的两阶段结构",body)


def board_03():
    states=[('sequence_01.png','01 · 闭锁','两枚锁钥片占据槽位'),('sequence_02.png','02 · 侧移','红色侧抽开始右移'),('sequence_03.png','03 · 释放','42 mm 后获得 1.2 mm 余量'),('sequence_04.png','04 · 显现','中央托盘再前行 145 mm')]
    blocks=[]
    for i,(img,t,d) in enumerate(states):
        x=140+(i%2)*1120; y=560+(i//2)*920
        blocks.append(f'''<g transform="translate({x} {y})">{panel(0,0,1060,820)}{image('../../04_renders/'+img,25,45,1010,600)}{text(54,690,t,34,COLORS['wall_ink'],'serif',720)}{text(54,748,d,22,COLORS['soft_gray'],'sans',430)}</g>''')
    body=f'''<g id="sequence">{''.join(blocks)}
<rect x="140" y="2480" width="2180" height="430" rx="44" fill="{COLORS['wall_ink']}"/>
{text(220,2605,'动作规则',20,COLORS['moon_gold'],'latin',720,spacing=3)}{text(220,2690,'侧抽不到位，中央托盘不应开启',41,COLORS['paper_white'],'serif',720)}
{text(220,2780,'所有画面内商品均为：',22,COLORS['paper_white'],'sans',420)}{text(625,2780,SKU.label,25,COLORS['route_red'],'sans',700)}
{text(2150,2690,'42 → 145',54,COLORS['moon_gold'],'latin',760,'end')}{text(2150,2750,'mm / mm',18,COLORS['paper_white'],'latin',500,'end')}</g>'''
    return wrap(3,"先解锁，再见礼","OPENING SEQUENCE · 两个方向、两个行程、一个明确顺序",body)


def board_04():
    body=f'''<g id="engineering">
<rect x="120" y="520" width="1420" height="1600" rx="52" fill="{COLORS['wall_ink']}"/>{image('../../04_renders/exploded.png',120,530,1420,1300)}{text(190,1960,'13 个实体 · 3 个 STEP 状态 · 13 份 STL',25,COLORS['paper_white'],'latin',620)}
<g transform="translate(1600 520)">{panel(0,0,760,760)}{text(55,82,'DIELINE',18,COLORS['moon_gold'],'latin',720,spacing=3)}{image('../../04_renders/dieline_preview.png',30,110,700,500)}{text(55,665,'红：裁切｜蓝：压痕｜灰：裱糊 / 禁胶',20,COLORS['soft_gray'],'sans',450)}</g>
<g transform="translate(1600 1360)">{panel(0,0,760,760)}{text(55,85,'LOCK LOGIC',18,COLORS['moon_gold'],'latin',720,spacing=3)}{text(55,175,'双锁钥片',42,COLORS['wall_ink'],'serif',720)}{lines(55,270,['闭合：两点同时限位','侧移：42 mm 清除槽位','释放余量：1.2 mm','开启：中央托盘前行 145 mm'],24,COLORS['soft_gray'],62,'sans',430)}</g>
<rect x="120" y="2240" width="2240" height="680" rx="48" fill="#FAF6EC" stroke="#D6C7A8" stroke-width="3"/>
{text(190,2360,'关键参数',38,COLORS['wall_ink'],'serif',720)}
{text(190,2480,'2.0 mm',45,COLORS['wall_ink'],'latin',760)}{text(190,2535,'灰板厚度',20,COLORS['soft_gray'],'sans',450)}
{text(650,2480,'0.18 mm',45,COLORS['wall_ink'],'latin',760)}{text(650,2535,'包纸厚度代理',20,COLORS['soft_gray'],'sans',450)}
{text(1160,2480,'0.6 mm / 侧',45,COLORS['wall_ink'],'latin',760)}{text(1160,2535,'滑动基准间隙',20,COLORS['soft_gray'],'sans',450)}
{text(1760,2480,'Ø108 mm',45,COLORS['wall_ink'],'latin',760)}{text(1760,2535,'月璧窗口',20,COLORS['soft_gray'],'sans',450)}
{lines(190,2680,['数字模型验证分件、包络、行程与中性格式可读性；纸板膨胀、裱糊累积、','满载摩擦、锁片撕裂、30 次开合、跌落与运输振动仍须实体样机验证。'],23,COLORS['soft_gray'],50,'sans',400)}
{text(190,2850,SKU.label,23,COLORS['route_red'],'sans',700)}</g>'''
    return wrap(4,"结构与刀模，同一套证据","ENGINEERING · 从参数化装配到毫米级包装展开",body)


def board_05():
    body=f'''<g id="seasonal">
<g transform="translate(120 540)">{panel(0,0,1080,1780,True)}{image('../../04_renders/mid_autumn_variant.png',20,70,1040,900)}{text(70,1090,'月满中秋',52,COLORS['paper_white'],'serif',740)}{text(72,1140,'MID-AUTUMN EDITION',18,COLORS['moon_gold'],'latin',650,spacing=3)}{lines(70,1260,['月宣白 × 赵月金','以月璧窗口形成节庆焦点','保留相同侧移解锁动作'],25,COLORS['paper_white'],58,'sans',400)}<circle cx="870" cy="1390" r="105" fill="none" stroke="{COLORS['moon_gold']}" stroke-width="5"/></g>
<g transform="translate(1280 540)">{panel(0,0,1080,1780)}{image('../../04_renders/national_day_variant.png',20,70,1040,900)}{text(70,1090,'山河同庆',52,COLORS['wall_ink'],'serif',740)}{text(72,1140,'NATIONAL DAY EDITION',18,COLORS['route_red'],'latin',650,spacing=3)}{lines(70,1260,['河山青 × 迂回朱','山线与路径强调共同出发','不堆叠旗帜或战争符号'],25,COLORS['soft_gray'],58,'sans',400)}<path d="M760 1480 L850 1380 L930 1460 L1020 1330" fill="none" stroke="{COLORS['route_red']}" stroke-width="6"/></g>
<rect x="120" y="2420" width="2240" height="500" rx="48" fill="{COLORS['wall_ink']}"/>{text(200,2540,'一个机构，两层节庆表达',42,COLORS['paper_white'],'serif',720)}{lines(200,2640,['共享字标、月璧窗口、路线构图、品牌区与法定信息区；只切换季节图层与 CMF。','品牌区待授权资产｜法定信息区待真实文案｜不得仿制邯宝坊未提供的官方标志。'],23,COLORS['paper_white'],52,'sans',380)}{text(200,2820,SKU.label,23,COLORS['route_red'],'sans',700)}</g>'''
    return wrap(5,"双节不是两套无关包装","SEASONAL CMF · 中秋与国庆共享同一机关身份",body)


def board_06():
    body=f'''<g id="gate">
<rect x="120" y="520" width="2240" height="760" rx="56" fill="{COLORS['wall_ink']}"/>{image('../../04_renders/hero_open.png',1120,490,1180,760)}{text(210,660,'TECHNICAL CANDIDATE',18,COLORS['moon_gold'],'latin',760,spacing=4)}{text(210,760,'技术候选稿',56,COLORS['paper_white'],'serif',760)}{text(210,850,'目前不能正式投稿',48,COLORS['route_red'],'serif',760)}{lines(210,955,['结构、刀模、渲染与展板已完成；','真实商品和品牌授权尚未进入项目。'],25,COLORS['paper_white'],52,'sans',390)}
<g transform="translate(120 1400)">{panel(0,0,700,780)}{text(55,90,'MISSING 01',18,COLORS['moon_gold'],'latin',720,spacing=2)}{text(55,170,'真实 SKU',38,COLORS['wall_ink'],'serif',720)}{lines(55,270,['实测长宽高与重量','商品数量与排列优先级','六面包装照片','运输与防护要求'],23,COLORS['soft_gray'],57,'sans',420)}</g>
<g transform="translate(890 1400)">{panel(0,0,700,780)}{text(55,90,'MISSING 02',18,COLORS['moon_gold'],'latin',720,spacing=2)}{text(55,170,'品牌与法定信息',38,COLORS['wall_ink'],'serif',720)}{lines(55,270,['矢量 Logo 与授权范围','可用品牌色和禁用方式','食品名称 / 净含量 / 配料','生产者与责任边界'],23,COLORS['soft_gray'],57,'sans',420)}</g>
<g transform="translate(1660 1400)">{panel(0,0,700,780)}{text(55,90,'MISSING 03',18,COLORS['moon_gold'],'latin',720,spacing=2)}{text(55,170,'投稿身份',38,COLORS['wall_ink'],'serif',720)}{lines(55,270,['作者 / 学校 / 指导教师','真实联系方式','最终文件命名规则','主办方最新报名表'],23,COLORS['soft_gray'],57,'sans',420)}</g>
<rect x="120" y="2320" width="2240" height="620" rx="50" fill="#172529"/>{text(200,2450,'COST POSITION',18,COLORS['moon_gold'],'latin',720,spacing=3)}{text(200,2550,'¥80–160',48,COLORS['paper_white'],'latin',760)}{text(200,2610,'概念样机包装，不含食品',20,COLORS['paper_white'],'sans',420)}{text(720,2550,'¥18–32',48,COLORS['paper_white'],'latin',760)}{text(720,2610,'量产目标区间，需供应商重算',20,COLORS['paper_white'],'sans',420)}{text(200,2760,'醒目标注',20,COLORS['moon_gold'],'sans',700)}{text(200,2840,SKU.label,36,COLORS['route_red'],'sans',760)}{text(2160,2840,'BLOCKED',34,COLORS['moon_gold'],'latin',760,'end')}</g>'''
    return wrap(6,"把缺失资料写在作品里","DELIVERY GATE · 技术通过，不等于可以绕过真实商品与授权",body,True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    boards=[board_01(),board_02(),board_03(),board_04(),board_05(),board_06()]
    for i,content in enumerate(boards,1):
        (OUT/f"board_{i:02d}.svg").write_text(content,encoding="utf-8")
    manifest={"count":6,"size_px":[W,H],"dpi":BOARD.dpi,"proxy_label":SKU.label,"titles":["解围","把典故变成必须遵守的动作","先解锁，再见礼","结构与刀模，同一套证据","双节不是两套无关包装","把缺失资料写在作品里"]}
    (OUT/"board_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":"ok","boards":6},ensure_ascii=False))


if __name__=="__main__":
    main()
