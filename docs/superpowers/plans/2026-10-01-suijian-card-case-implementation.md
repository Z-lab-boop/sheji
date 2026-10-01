# “遂见”毛遂自荐青年名片匣 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 产出一套可投稿、可编辑、可验证并具备实体打样依据的“遂见”青年名片匣参赛包。

**Architecture:** 以单一参数配置驱动 FreeCAD 参数化结构、Blender 产品渲染、SVG 展板和最终审计，避免不同图片中的造型与尺寸漂移。产品主体只使用 CAD 导出的几何体；生成式图像如被采用，仅作为不承担结构证明的场景背景，并在素材清单中记录。

**Tech Stack:** FreeCAD 1.1.1、Blender 5.2 LTS、Python 3.14/工作区 Python（Pillow 12.3、ReportLab 4.4）、Node.js/Playwright、SVG、ImageMagick 7、Ghostscript、内置 `unittest`

**Spec:** `docs/superpowers/specs/2026-10-01-suijian-card-case-design.md`

## Global Constraints

- 新作品全部位于 `suijian_design/`，不修改既有 `build_short_video.py`、`scenes/`、`audio/`、`metadata/`、`output/` 或 `tmp_segments/`。
- 闭合设计基线为 98 × 65 × 14 mm，圆角半径 8 mm；内托行程约 28 mm；卡片末段抬升约 7 mm。
- 主色固定为赵漆青 `#0D2F32`、鼎金 `#B68B48`、誓朱 `#A64032`、帛白 `#E8DFCC`、墨黑 `#16191A`。
- 参赛稿固定为 7 张 A4 竖版、2480 × 3508 px、300 dpi、RGB、JPG，单张小于 5 MB。
- 所有中文、尺寸和结构标注以矢量排版生成；生成模型不得绘制或篡改文字。
- 渲染中的产品几何必须来自同一批 CAD 输出；模型材料、量产材料、建议零售价和供应商报价严格区分。
- 作者、学校、指导教师、手机号等真实身份字段不虚构，也不进入公开场景图。
- 所有第三方字体、图像和参考资料必须记录来源、许可或使用边界。

---

## File Map

```text
suijian_design/
  README.md                              # 构建、目录和验收入口
  01_research/
    sources.md                           # 典故、赛事、竞品与许可来源
    fonts/                               # Noto Sans SC、Noto Serif SC、Inter 及 OFL
  02_identity/
    wordmark.svg                         # 定制“遂见”字标
    identity_card.svg                    # 数字身份卡示例
    portfolio_cards.svg                  # 三类作品展示卡
    packaging_dieline.svg                # 抽屉盒刀模
    identity_manifest.json               # 色值、字体和文件哈希
  03_cad/
    build_product.py                     # FreeCAD 参数化建模入口
    suijian_card_case.FCStd              # 参数化源模型
    suijian_card_case.step               # 通用交换模型
    meshes/*.stl                         # 分件网格
    cad_report.json                      # 尺寸、包围盒、体积和零件清单
  04_renders/
    render_product.py                    # Blender 批量渲染脚本
    *.png                                # 透明背景产品渲染
    render_manifest.json                 # 相机、几何哈希和输出规格
  05_boards/
    src/board_01.svg ... board_07.svg    # 可编辑展板源文件
    jpg/board_01.jpg ... board_07.jpg    # 投稿图
    pdf/board_01.pdf ... board_07.pdf    # 印刷与审阅文件
    contact_sheet.jpg                    # 七张总览
  06_submission/
    work_description.md                  # 报名表作品说明
    materials_and_pricing.md             # 材质、工艺、规格、价格边界
    source_manifest.csv                  # 素材、许可和哈希
  07_audit/
    audit_report.json                    # 机器审计结果
    visual_review.md                     # 人工视觉检查记录
  scripts/
    design_config.py                     # 唯一尺寸、颜色和文案来源
    build_identity.py                    # 生成字标、卡片和包装 SVG
    build_boards.py                      # 生成七张 SVG
    export_boards.mjs                    # Playwright 导出 JPG/PDF
    make_contact_sheet.py                # 生成总览图
    audit_submission.py                  # 投稿包机器检查
  tests/
    test_design_config.py
    test_cad_report.py
    test_render_outputs.py
    test_identity_outputs.py
    test_board_outputs.py
```

---

### Task 1: Source-of-truth configuration and licensed assets

**Files:**
- Create: `suijian_design/README.md`
- Create: `suijian_design/scripts/design_config.py`
- Create: `suijian_design/tests/test_design_config.py`
- Create: `suijian_design/01_research/sources.md`
- Create: `suijian_design/01_research/fonts/`

**Interfaces:**
- Consumes: approved design spec.
- Produces: `ProductSpec`, `BoardSpec`, `COLORS`, `COPY`, `validate_spec()` used by every later Python task.

- [ ] **Step 1: Write the failing configuration test**

```python
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from design_config import BOARD, COLORS, COPY, PRODUCT, validate_spec


class DesignConfigTests(unittest.TestCase):
    def test_product_baseline(self):
        self.assertEqual((PRODUCT.width, PRODUCT.height, PRODUCT.depth), (98.0, 65.0, 14.0))
        self.assertEqual(PRODUCT.corner_radius, 8.0)
        self.assertEqual(PRODUCT.travel, 28.0)
        self.assertEqual(PRODUCT.lift, 7.0)

    def test_board_submission_contract(self):
        self.assertEqual((BOARD.width_px, BOARD.height_px, BOARD.dpi), (2480, 3508, 300))
        self.assertEqual(BOARD.count, 7)
        self.assertEqual(BOARD.max_bytes, 5_000_000)

    def test_palette_and_copy_are_frozen(self):
        self.assertEqual(COLORS["zhao_lacquer"], "#0D2F32")
        self.assertEqual(COLORS["ding_gold"], "#B68B48")
        self.assertEqual(COPY["name_zh"], "遂见")
        self.assertEqual(COPY["tagline"], "让才能，被看见")
        self.assertEqual(validate_spec(), [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and confirm the missing module failure**

Run:

```bash
/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest suijian_design/tests/test_design_config.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'design_config'`.

- [ ] **Step 3: Implement the frozen configuration**

Create dataclasses with these exact public fields:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ProductSpec:
    width: float = 98.0
    height: float = 65.0
    depth: float = 14.0
    corner_radius: float = 8.0
    wall: float = 1.8
    clearance: float = 0.35
    travel: float = 28.0
    lift: float = 7.0
    card_width: float = 90.0
    card_height: float = 54.0
    card_thickness: float = 0.30


@dataclass(frozen=True)
class BoardSpec:
    width_px: int = 2480
    height_px: int = 3508
    dpi: int = 300
    count: int = 7
    max_bytes: int = 5_000_000


PRODUCT = ProductSpec()
BOARD = BoardSpec()
COLORS = {
    "zhao_lacquer": "#0D2F32",
    "ding_gold": "#B68B48",
    "oath_vermilion": "#A64032",
    "silk_white": "#E8DFCC",
    "ink_black": "#16191A",
}
COPY = {
    "name_zh": "遂见",
    "name_en": "SUIJIAN",
    "category": "毛遂自荐青年名片匣",
    "tagline": "让才能，被看见",
    "culture_line": "锥处囊中，颖自见",
}


def validate_spec() -> list[str]:
    errors: list[str] = []
    if PRODUCT.wall <= PRODUCT.clearance:
        errors.append("wall must be greater than clearance")
    if PRODUCT.card_width + 2 * PRODUCT.clearance >= PRODUCT.width:
        errors.append("card width does not fit enclosure")
    if not 0 < PRODUCT.lift < PRODUCT.depth:
        errors.append("lift must fit product depth")
    if BOARD.count > 8:
        errors.append("board count exceeds competition limit")
    return errors
```

- [ ] **Step 4: Acquire and document open fonts**

Download Noto Sans SC and Noto Serif SC from the official Google Fonts repository, together with their `OFL.txt`; download Inter from its official release or Google Fonts source. Save the exact download URLs, retrieval date, SHA-256 and license in `01_research/sources.md`. Do not install fonts globally.

Required font files:

```text
NotoSansSC[wght].ttf
NotoSerifSC[wght].ttf
InterVariable.ttf
OFL-NotoSansSC.txt
OFL-NotoSerifSC.txt
OFL-Inter.txt
```

- [ ] **Step 5: Run tests and commit**

Run the `unittest` command from Step 2. Expected: 3 tests PASS.

```bash
git add suijian_design/README.md suijian_design/scripts/design_config.py suijian_design/tests/test_design_config.py suijian_design/01_research
git commit -m "feat: establish Suijian design system"
```

---

### Task 2: Parametric product model and geometry audit

**Files:**
- Create: `suijian_design/tests/test_cad_report.py`
- Create: `suijian_design/03_cad/build_product.py`
- Generate: `suijian_design/03_cad/suijian_card_case.FCStd`
- Generate: `suijian_design/03_cad/suijian_card_case.step`
- Generate: `suijian_design/03_cad/meshes/*.stl`
- Generate: `suijian_design/03_cad/cad_report.json`

**Interfaces:**
- Consumes: `PRODUCT` from `scripts/design_config.py`.
- Produces: named solids `outer_shell`, `inner_tray`, `lifter`, `gold_accent`, `card_proxy`; millimetre units; a JSON report with `bbox_mm`, `volume_mm3`, `sha256` and `manifold_expected` per part.

- [ ] **Step 1: Write the failing CAD report test**

```python
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CadReportTests(unittest.TestCase):
    def test_expected_parts_and_dimensions(self):
        report = json.loads((ROOT / "03_cad/cad_report.json").read_text("utf-8"))
        self.assertEqual(report["assembly_bbox_mm"], [98.0, 65.0, 14.0])
        self.assertEqual(
            set(report["parts"]),
            {"outer_shell", "inner_tray", "lifter", "gold_accent", "card_proxy"},
        )
        for part in report["parts"].values():
            self.assertGreater(part["volume_mm3"], 0)
            self.assertEqual(len(part["sha256"]), 64)

    def test_exchange_files_exist(self):
        self.assertTrue((ROOT / "03_cad/suijian_card_case.FCStd").is_file())
        self.assertTrue((ROOT / "03_cad/suijian_card_case.step").is_file())
        for name in ("outer_shell", "inner_tray", "lifter", "gold_accent", "card_proxy"):
            self.assertTrue((ROOT / f"03_cad/meshes/{name}.stl").is_file())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and confirm missing artifacts**

Run:

```bash
/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest suijian_design/tests/test_cad_report.py -v
```

Expected: FAIL because `cad_report.json` and exchange files do not exist.

- [ ] **Step 3: Implement the FreeCAD model**

`build_product.py` must:

1. import `PRODUCT` by adding `suijian_design/scripts` to `sys.path`;
2. build the rounded outer shell as a fused rounded box minus a translated inner cavity;
3. build an inner tray with two continuous side rails and a 28 mm allowed translation;
4. build the lifter as a shallow wedge whose top rise is 7 mm over the final 18 mm of travel;
5. build the gold accent as a separate 0.7 mm inset strip at 17°;
6. add nine equal side reliefs to the shell without breaking minimum 1.2 mm residual wall thickness;
7. export each named solid to STL, the assembly to STEP, and the document to FCStd;
8. write the exact JSON schema consumed by the test.

Critical construction helpers:

```python
def rounded_box(width: float, height: float, depth: float, radius: float):
    """Return a fused Part.Shape with planar top/bottom and rounded XY corners."""


def make_outer_shell(spec):
    """Return a hollow shell with one open short edge and no face thinner than spec.wall."""


def make_inner_tray(spec):
    """Return a tray that fits shell cavity with spec.clearance on each sliding face."""


def make_lifter(spec):
    """Return a wedge that raises the card proxy by spec.lift at full travel."""


def export_part(name: str, shape, mesh_dir: Path) -> dict:
    """Export STL and return bbox, volume and sha256 metadata."""
```

- [ ] **Step 4: Build and verify geometry**

Run:

```bash
printf '%s\n' "p='suijian_design/03_cad/build_product.py'; exec(compile(open(p,'rb').read(),p,'exec'),{'__file__':p,'__name__':'__main__'})" | /Applications/FreeCAD.app/Contents/Resources/bin/FreeCADCmd -c
/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest suijian_design/tests/test_cad_report.py -v
```

Expected: FreeCAD exits 0 and both CAD tests PASS. Reopen the STEP with FreeCADCmd in a separate check and verify it contains five solids.

- [ ] **Step 5: Commit**

```bash
git add suijian_design/03_cad suijian_design/tests/test_cad_report.py
git commit -m "feat: model Suijian card case"
```

---

### Task 3: Consistent product rendering

**Files:**
- Create: `suijian_design/tests/test_render_outputs.py`
- Create: `suijian_design/04_renders/render_product.py`
- Generate: `suijian_design/04_renders/*.png`
- Generate: `suijian_design/04_renders/render_manifest.json`

**Interfaces:**
- Consumes: five STL files and palette from `design_config.py`.
- Produces: `hero_closed.png`, `hero_open.png`, `interaction_01.png`, `interaction_02.png`, `interaction_03.png`, `exploded.png`, `detail_accent.png`, `scale_view.png`, `packaging_hero.png`; all 2400 × 2400 RGBA PNG except `scale_view.png`, which is 2400 × 1800.

- [ ] **Step 1: Write the failing render test**

```python
import json
from pathlib import Path
import unittest
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "hero_closed.png": (2400, 2400),
    "hero_open.png": (2400, 2400),
    "interaction_01.png": (2400, 2400),
    "interaction_02.png": (2400, 2400),
    "interaction_03.png": (2400, 2400),
    "exploded.png": (2400, 2400),
    "detail_accent.png": (2400, 2400),
    "scale_view.png": (2400, 1800),
    "packaging_hero.png": (2400, 2400),
}


class RenderTests(unittest.TestCase):
    def test_images_are_rgba_and_nonempty(self):
        for name, size in EXPECTED.items():
            image = Image.open(ROOT / "04_renders" / name)
            self.assertEqual(image.size, size)
            self.assertEqual(image.mode, "RGBA")
            self.assertIsNotNone(ImageChops.difference(image.getchannel("A"), Image.new("L", size, 0)).getbbox())

    def test_manifest_uses_cad_hashes(self):
        manifest = json.loads((ROOT / "04_renders/render_manifest.json").read_text("utf-8"))
        self.assertEqual(set(manifest["mesh_sha256"]), {"outer_shell", "inner_tray", "lifter", "gold_accent", "card_proxy"})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Confirm the render test fails**

Run with the workspace Python. Expected: FAIL because renders do not exist.

- [ ] **Step 3: Implement the Blender renderer**

The renderer must reset the scene, import the exact STL parts, assign physically based materials from the frozen palette, use a 70 mm lens for hero/detail images, use a three-light studio rig and enable transparent film. The open and interaction frames must translate only `inner_tray`, `lifter`, `gold_accent` and `card_proxy`; the shell remains fixed.

Required public helpers:

```python
def load_part(name: str, path: Path):
    """Import one STL, set object name and return the Blender object."""


def material(name: str, hex_color: str, metallic: float, roughness: float):
    """Create one Principled BSDF material with deterministic values."""


def set_open_state(objects: dict, progress: float) -> None:
    """Apply 0..1 travel and lift without changing part mesh data."""


def render_view(filename: str, camera_location: tuple[float, float, float], target: tuple[float, float, float], size: tuple[int, int]) -> None:
    """Render one transparent PNG and record camera values in the manifest."""
```

Use Cycles with deterministic seed and 256 samples; if the first 600 × 600 proof render exceeds 90 seconds, switch final renders to Eevee with 64 temporal samples and record the engine in the manifest.

- [ ] **Step 4: Render proof, inspect, then render final set**

Run:

```bash
blender --background --python suijian_design/04_renders/render_product.py -- --proof
blender --background --python suijian_design/04_renders/render_product.py -- --final
```

Inspect the proof for clipping, inverted normals, material banding and implausible part intersections before launching finals.

- [ ] **Step 5: Run tests and commit**

Run `test_render_outputs.py`; expected: all tests PASS.

```bash
git add suijian_design/04_renders suijian_design/tests/test_render_outputs.py
git commit -m "feat: render Suijian product system"
```

---

### Task 4: Identity, card and packaging system

**Files:**
- Create: `suijian_design/tests/test_identity_outputs.py`
- Create: `suijian_design/scripts/build_identity.py`
- Generate: `suijian_design/02_identity/*.svg`
- Generate: `suijian_design/02_identity/identity_manifest.json`

**Interfaces:**
- Consumes: `COLORS`, `COPY`, local OFL fonts and product dimensions.
- Produces: four editable SVG assets with 100% vector text/shapes; a manifest recording font filenames, SHA-256, viewBox and colors.

- [ ] **Step 1: Write the failing identity test**

```python
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ("wordmark.svg", "identity_card.svg", "portfolio_cards.svg", "packaging_dieline.svg")


class IdentityTests(unittest.TestCase):
    def test_svg_assets_are_editable(self):
        for name in ASSETS:
            path = ROOT / "02_identity" / name
            root = ET.parse(path).getroot()
            self.assertIn("viewBox", root.attrib)
            self.assertNotIn("data:image", path.read_text("utf-8"))

    def test_manifest_records_palette_and_fonts(self):
        data = json.loads((ROOT / "02_identity/identity_manifest.json").read_text("utf-8"))
        self.assertEqual(data["colors"]["zhao_lacquer"], "#0D2F32")
        self.assertEqual(set(data["fonts"]), {"Noto Sans SC", "Noto Serif SC", "Inter"})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Confirm the missing asset failure**

Run with workspace Python. Expected: FAIL because SVGs do not exist.

- [ ] **Step 3: Implement the vector identity generator**

`wordmark.svg` must use a custom geometric mark built from the `辶` movement curve, a 17° diagonal “锥锋” and a simplified `见` frame. The accompanying “遂见” lettering may be based on Noto Serif SC under OFL, but must be converted to paths or retained as editable text with the font packaged; the diagonal cut and red endpoint are separate editable vectors.

The identity card must use fictional, non-personal content only:

```text
林知行 / LIN ZHIXING
青年创作者 / YOUNG CREATOR
PORTFOLIO 2026
二维码区域标注为 DEMO，不编码真实网址
```

The packaging dieline must include cut lines, fold lines, glue area, finished size and a visible `MODEL / NOT FOR PRODUCTION` layer label.

- [ ] **Step 4: Generate, parse and visually preview SVG assets**

Run:

```bash
/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 suijian_design/scripts/build_identity.py
/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest suijian_design/tests/test_identity_outputs.py -v
```

Expected: four parseable SVGs and passing tests.

- [ ] **Step 5: Commit**

```bash
git add suijian_design/02_identity suijian_design/scripts/build_identity.py suijian_design/tests/test_identity_outputs.py
git commit -m "feat: create Suijian identity and packaging"
```

---

### Task 5: Seven-board submission narrative and exports

**Files:**
- Create: `suijian_design/tests/test_board_outputs.py`
- Create: `suijian_design/scripts/build_boards.py`
- Create: `suijian_design/scripts/export_boards.mjs`
- Create: `suijian_design/scripts/make_contact_sheet.py`
- Generate: `suijian_design/05_boards/src/*.svg`
- Generate: `suijian_design/05_boards/jpg/*.jpg`
- Generate: `suijian_design/05_boards/pdf/*.pdf`
- Generate: `suijian_design/05_boards/contact_sheet.jpg`

**Interfaces:**
- Consumes: transparent renders, identity SVGs, `design_config.py`, CAD report.
- Produces: seven editable boards and two submission/print formats with one-to-one numbering.

- [ ] **Step 1: Write the failing board test**

```python
from pathlib import Path
import unittest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


class BoardTests(unittest.TestCase):
    def test_all_submission_jpegs(self):
        for index in range(1, 8):
            path = ROOT / f"05_boards/jpg/board_{index:02d}.jpg"
            image = Image.open(path)
            self.assertEqual(image.size, (2480, 3508))
            self.assertEqual(image.mode, "RGB")
            self.assertLess(path.stat().st_size, 5_000_000)
            self.assertEqual(round(image.info.get("dpi", (0, 0))[0]), 300)

    def test_sources_and_pdfs_exist(self):
        for index in range(1, 8):
            self.assertTrue((ROOT / f"05_boards/src/board_{index:02d}.svg").is_file())
            self.assertTrue((ROOT / f"05_boards/pdf/board_{index:02d}.pdf").is_file())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Confirm missing board failure**

Run with workspace Python. Expected: FAIL on `board_01.jpg`.

- [ ] **Step 3: Implement the board builder**

Use a consistent 12-column grid with 160 px outer margins, 80 px gutters, a 10 px gold rule, title baseline at y=260 and footer baseline at y=3320. Every board must contain one dominant message and no more than three secondary text blocks.

Required exact narrative:

1. `board_01`: hero closed/open render, “遂见”, “让才能，被看见”.
2. `board_02`: “囊—锥—颖—言” four-step culture-to-interaction mapping and source footnotes.
3. `board_03`: closed/open/取卡 three-state sequence with 98 × 65 × 14 mm.
4. `board_04`: exploded view, 28 mm travel, 7 mm lift, 1.8 mm wall, 0.35 mm clearance, NFC-safe location.
5. `board_05`: CMF swatches, 17° accent, nine reliefs, wordmark and card details.
6. `board_06`: recruitment, exhibition and portfolio scenarios using consistent CAD product composites.
7. `board_07`: packaging, target audience, prototype/production distinction, estimated price bands and sales context.

All board copy must be drawn from frozen configuration or a board-specific constant dictionary in `build_boards.py`; prohibit ad hoc manual text in the exported SVGs.

- [ ] **Step 4: Export SVGs through Chromium**

`export_boards.mjs` must use bundled Playwright, wait for `document.fonts.ready`, open each local SVG at 2480 × 3508, save a lossless screenshot first, then use ImageMagick to encode RGB JPEG under 5 MB while preserving 300 dpi metadata. Each SVG is also wrapped in an A4 page and printed to PDF.

Run:

```bash
/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 suijian_design/scripts/build_boards.py
NODE_PATH=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules /Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node suijian_design/scripts/export_boards.mjs
/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 suijian_design/scripts/make_contact_sheet.py
```

- [ ] **Step 5: Run board tests and inspect the contact sheet**

Run `test_board_outputs.py`; expected: all tests PASS. Inspect `contact_sheet.jpg` at full resolution for grid drift, clipped text, unreadable captions, repeated render angles and inconsistent shadows.

- [ ] **Step 6: Commit**

```bash
git add suijian_design/05_boards suijian_design/scripts/build_boards.py suijian_design/scripts/export_boards.mjs suijian_design/scripts/make_contact_sheet.py suijian_design/tests/test_board_outputs.py
git commit -m "feat: compose Suijian competition boards"
```

---

### Task 6: Submission copy, provenance and final audit

**Files:**
- Create: `suijian_design/06_submission/work_description.md`
- Create: `suijian_design/06_submission/materials_and_pricing.md`
- Create: `suijian_design/06_submission/source_manifest.csv`
- Create: `suijian_design/scripts/audit_submission.py`
- Generate: `suijian_design/07_audit/audit_report.json`
- Create: `suijian_design/07_audit/visual_review.md`

**Interfaces:**
- Consumes: every source and output artifact from Tasks 1–5.
- Produces: a human-readable submission text pack, machine-readable provenance and a final pass/fail report.

- [ ] **Step 1: Write the audit script before final copy**

The script must fail with a non-zero exit status if any condition fails:

```python
checks = {
    "board_count": 7,
    "jpeg_dimensions": [2480, 3508],
    "jpeg_mode": "RGB",
    "jpeg_dpi": 300,
    "jpeg_max_bytes": 5_000_000,
    "required_cad_parts": ["outer_shell", "inner_tray", "lifter", "gold_accent", "card_proxy"],
    "required_source_formats": [".FCStd", ".step", ".stl", ".svg", ".pdf", ".jpg"],
    "forbidden_identity_tokens": ["手机号", "身份证", "真实姓名待填", "TBD", "TODO"],
}
```

It must compute SHA-256 for all final deliverables and write individual check results plus a top-level `status` of `pass` or `fail` to `audit_report.json`.

- [ ] **Step 2: Write submission copy with factual boundaries**

`work_description.md` must contain these labeled fields: 作品名称、作品类别、设计说明、文化来源、使用方式、优势特点、规格、建议材料、预计单价、市场前景、AI与数字工具使用说明、原创声明。It must call price figures “建议零售价估算”, not “市场售价” or “供应商报价”.

`materials_and_pricing.md` must separate prototype materials from production assumptions and state that no supplier quotation or production test has yet been completed.

- [ ] **Step 3: Generate provenance manifest**

The CSV columns are exactly:

```text
asset_id,path,asset_type,creator_or_source,license_or_basis,sha256,used_in
```

Every font, render, identity asset, board source, final board and external reference must have one row. CAD renders list `project-generated` as creator and reference their STL hash.

- [ ] **Step 4: Run full mechanical verification**

Run:

```bash
/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s suijian_design/tests -v
/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 suijian_design/scripts/audit_submission.py
pdfinfo suijian_design/05_boards/pdf/board_01.pdf
magick identify -verbose suijian_design/05_boards/jpg/board_01.jpg
```

Expected: every unit test PASS, audit exits 0 with `status: pass`, PDF reports A4 portrait size, JPEG reports 2480 × 3508, RGB and 300 dpi.

- [ ] **Step 5: Perform visual review**

Review the full-resolution contact sheet and all seven boards individually. Record pass/fail for typography, alignment, text clipping, Chinese punctuation, product geometry consistency, interaction sequence, material realism, dimension legibility, source footnotes, privacy and absence of generative artifacts. Any failed item must be fixed and the full export/audit rerun.

- [ ] **Step 6: Commit final package**

```bash
git add suijian_design/06_submission suijian_design/07_audit suijian_design/scripts/audit_submission.py
git commit -m "docs: finalize Suijian submission package"
```

---

## Final Verification Gate

Before declaring the work complete:

1. compare `git status --short` with the pre-existing untracked video files and confirm no old project file was added or changed;
2. run the full `unittest` suite and `audit_submission.py` again from a clean process;
3. reopen STEP and one STL in FreeCADCmd, and render one board through a fresh Chromium process;
4. inspect all seven boards, not only the contact sheet;
5. report product/model/render/submission facts separately from estimates and future physical validation;
6. do not claim the work is submitted, shortlisted, manufactured or market-tested.
