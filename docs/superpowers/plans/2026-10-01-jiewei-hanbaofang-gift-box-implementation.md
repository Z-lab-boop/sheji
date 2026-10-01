# 《解围》邯宝坊双节机关礼盒 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立一套以“围魏救赵”两阶段解锁为核心的邯宝坊双节机关礼盒候选参赛包，包含参数化包装 CAD、刀模、三状态渲染、6 张 A4 展板与真实 SKU 投稿硬门。

**Architecture:** 项目放在独立目录 `jiewei_giftbox_design/`。结构参数与 SKU 代理状态集中于 `scripts/design_config.py`；FreeCAD 生成闭合、解锁、开启装配及 STEP/STL；独立刀模生成器输出 SVG/DXF；Blender 只使用审计后的结构网格；审计报告分离技术通过与“等待真实邯宝坊 SKU/授权”的投稿阻塞状态。

**Tech Stack:** Python 3.11、FreeCAD Python API、Blender 4.x Python API、Pillow、SVG/DXF、Node.js、Playwright、ImageMagick、Poppler、unittest。

**Spec:** `docs/superpowers/specs/2026-10-01-jiewei-hanbaofang-gift-box-design.md`

## Global Constraints

- 闭合参考尺寸为 290 × 230 × 75 mm；灰板厚度 2.0 mm；包纸厚度代理 0.18 mm；滑动基准间隙 0.6 mm/侧。
- 魏侧抽屉行程为 42 mm；赵中央托盘展示行程为 145 mm；月璧窗口直径为 108 mm。
- 概念阶段使用 6 个 60 × 60 × 35 mm 无品牌中性 SKU 代理件，任何图文均须标注“规格代理件，非实际商品包装”。
- 最终提交为不超过 6 张 2480 × 3508 px、300 dpi、RGB、单张小于 5 MB 的 A4 竖版 JPG，并保留 SVG/PDF/DXF/CAD。
- 食品名称、净含量、配料、生产者、品牌标志和商品照片不得虚构。
- 在真实 SKU、品牌授权和法定包装信息到位前，`submission_status` 必须保持 `blocked_pending_real_sku_and_brand_assets`。
- 既有 `suijian_design/`、`bubushengdian_design/` 和短视频目录不得修改。

---

### Task 1: 项目骨架、参数契约与代理状态

**Files:**
- Create: `jiewei_giftbox_design/README.md`
- Create: `jiewei_giftbox_design/scripts/design_config.py`
- Create: `jiewei_giftbox_design/tests/test_design_config.py`
- Create: `jiewei_giftbox_design/01_research/sources.md`
- Copy: `suijian_design/01_research/fonts/*` → `jiewei_giftbox_design/01_research/fonts/`

**Interfaces:**
- Produces: `BOX: BoxSpec`, `SKU: SKUProxySpec`, `BOARD: BoardSpec`, `COLORS`, `state_offsets(state: str) -> dict[str, tuple[float, float, float]]`, `validate_spec() -> list[str]`.
- Consumes: approved gift-box spec and local OFL font files.

- [ ] **Step 1: Write failing configuration tests**

```python
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from design_config import BOARD, BOX, SKU, state_offsets, validate_spec


class DesignConfigTests(unittest.TestCase):
    def test_box_contract(self):
        self.assertEqual((BOX.width, BOX.depth, BOX.height), (290.0, 230.0, 75.0))
        self.assertEqual((BOX.wei_travel, BOX.zhao_travel, BOX.moon_window_diameter), (42.0, 145.0, 108.0))
        self.assertEqual((BOX.board_thickness, BOX.wrap_thickness, BOX.clearance), (2.0, 0.18, 0.6))

    def test_proxy_contract_is_explicit(self):
        self.assertEqual((SKU.width, SKU.depth, SKU.height, SKU.count), (60.0, 60.0, 35.0, 6))
        self.assertTrue(SKU.is_proxy)
        self.assertEqual(SKU.label, "规格代理件，非实际商品包装")

    def test_state_contract(self):
        self.assertEqual(state_offsets("closed")["wei_drawer"], (0.0, 0.0, 0.0))
        self.assertEqual(state_offsets("unlocked")["wei_drawer"], (42.0, 0.0, 0.0))
        self.assertEqual(state_offsets("open")["zhao_tray"], (0.0, -145.0, 0.0))

    def test_board_contract(self):
        self.assertEqual((BOARD.width_px, BOARD.height_px, BOARD.dpi, BOARD.count), (2480, 3508, 300, 6))

    def test_spec_has_no_violations(self):
        self.assertEqual(validate_spec(), [])
```

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest jiewei_giftbox_design/tests/test_design_config.py -v`  
Expected: FAIL with missing `design_config`.

- [ ] **Step 3: Implement frozen dataclasses and state machine**

Define `BoxSpec`, `SKUProxySpec` and `BoardSpec` with exact Global Constraints. `state_offsets()` must accept only `closed`, `unlocked`, `open`; `open` retains the 42 mm side-drawer offset and adds 145 mm central-tray movement. Invalid state names must raise `ValueError`. `validate_spec()` must reject a false `is_proxy`, more than six boards, insufficient release travel, non-positive clearances or altered envelope.

- [ ] **Step 4: Record sources and evidence limits**

`sources.md` must include the competition page, Hebei idiom source, Education Ministry idiom dictionary, Hebei article confirming邯宝坊 as a local-products retail context, font licences and a statement that no official邯宝坊 SKU/brand package is currently present.

- [ ] **Step 5: Verify GREEN and commit**

Run: `python3 -m unittest jiewei_giftbox_design/tests/test_design_config.py -v`  
Expected: 5 tests PASS.

```bash
git add jiewei_giftbox_design
git commit -m "feat: define Jiewei gift-box contract"
```

### Task 2: 礼盒字标、双节外套与图形系统

**Files:**
- Create: `jiewei_giftbox_design/scripts/build_identity.py`
- Generate: `jiewei_giftbox_design/02_identity/wordmark.svg`
- Generate: `jiewei_giftbox_design/02_identity/mid_autumn_sleeve.svg`
- Generate: `jiewei_giftbox_design/02_identity/national_day_sleeve.svg`
- Generate: `jiewei_giftbox_design/02_identity/proxy_product_labels.svg`
- Generate: `jiewei_giftbox_design/02_identity/identity_manifest.json`
- Create: `jiewei_giftbox_design/tests/test_identity_outputs.py`

**Interfaces:**
- Consumes: `COLORS`, `SKU.label`, local fonts.
- Produces: two seasonal sleeve graphics sharing one mechanism identity; every product proxy face includes the proxy label.

- [ ] **Step 1: Write failing identity tests**

```python
from pathlib import Path
import json
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class IdentityTests(unittest.TestCase):
    def test_all_svg_assets_are_editable(self):
        names = ("wordmark.svg", "mid_autumn_sleeve.svg", "national_day_sleeve.svg", "proxy_product_labels.svg")
        for name in names:
            path = ROOT / "02_identity" / name
            self.assertTrue(path.is_file())
            self.assertTrue(ET.parse(path).getroot().tag.endswith("svg"))

    def test_proxy_disclosure_is_embedded(self):
        text = (ROOT / "02_identity" / "proxy_product_labels.svg").read_text(encoding="utf-8")
        self.assertIn("规格代理件，非实际商品包装", text)
        manifest = json.loads((ROOT / "02_identity" / "identity_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["brand_asset_status"], "not_provided")
```

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest jiewei_giftbox_design/tests/test_identity_outputs.py -v`  
Expected: FAIL because identity outputs do not exist.

- [ ] **Step 3: Implement deterministic SVG assets**

Generate the geometric “解围” wordmark, a shared three-segment route graphic, a restrained moon-gold Mid-Autumn sleeve, a river-mountain National Day sleeve and six neutral proxy labels. Do not draw or approximate a邯宝坊 logo. Sleeve SVGs must include reserved rectangles named `brand-zone` and `legal-copy-zone` but show only neutral labels in concept renders.

- [ ] **Step 4: Generate, test and inspect**

Run: `python3 jiewei_giftbox_design/scripts/build_identity.py`  
Run: `python3 -m unittest jiewei_giftbox_design/tests/test_identity_outputs.py -v`  
Expected: tests PASS. Inspect both sleeves at full size and thumbnail size; confirm the two editions share composition and differ only in seasonal layer.

- [ ] **Step 5: Commit**

```bash
git add jiewei_giftbox_design/02_identity jiewei_giftbox_design/scripts/build_identity.py jiewei_giftbox_design/tests/test_identity_outputs.py
git commit -m "feat: create Jiewei seasonal identity system"
```

### Task 3: FreeCAD 三状态机关礼盒与代理内衬

**Files:**
- Create: `jiewei_giftbox_design/03_cad/build_giftbox.py`
- Generate: `jiewei_giftbox_design/03_cad/jiewei_giftbox.FCStd`
- Generate: `jiewei_giftbox_design/03_cad/jiewei_giftbox_closed.step`
- Generate: `jiewei_giftbox_design/03_cad/jiewei_giftbox_unlocked.step`
- Generate: `jiewei_giftbox_design/03_cad/jiewei_giftbox_open.step`
- Generate: `jiewei_giftbox_design/03_cad/meshes/*.stl`
- Generate: `jiewei_giftbox_design/03_cad/cad_report.json`
- Create: `jiewei_giftbox_design/03_cad/mechanism_notes.md`
- Create: `jiewei_giftbox_design/tests/test_cad_report.py`

**Interfaces:**
- Consumes: `BOX`, `SKU`, `state_offsets()`.
- Produces: named parts `outer_sleeve`, `wei_drawer`, `lock_key_left`, `lock_key_right`, `zhao_tray`, `inner_liner`, `moon_disc`, `sku_proxy_01`–`sku_proxy_06`; three assembly states and hashes.

- [ ] **Step 1: Write failing CAD tests**

```python
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CadReportTests(unittest.TestCase):
    def test_closed_envelope_and_parts(self):
        report = json.loads((ROOT / "03_cad" / "cad_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["closed_bbox_mm"], [290.0, 230.0, 75.0])
        self.assertEqual(len(report["parts"]), 13)
        self.assertTrue(all(part["valid"] and part["solid_count"] == 1 for part in report["parts"].values()))

    def test_release_margin(self):
        report = json.loads((ROOT / "03_cad" / "cad_report.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(report["release_margin_mm"], 1.0)

    def test_three_step_files_exist(self):
        for state in ("closed", "unlocked", "open"):
            self.assertTrue((ROOT / "03_cad" / f"jiewei_giftbox_{state}.step").is_file())
```

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest jiewei_giftbox_design/tests/test_cad_report.py -v`  
Expected: FAIL because CAD outputs do not exist.

- [ ] **Step 3: Implement paperboard proxy solids and interlock**

Use FreeCAD Part workbenches. Model 2.0 mm paperboard layers as solids with 0.18 mm wrap allowance. The closed state must physically overlap lock keys with two tray slots; the unlocked state must move the side drawer 42 mm and clear both slots by at least 1.0 mm; the open state must retain the side offset and move the central tray 145 mm forward. Six product proxies must fit the parametric liner with 1.0 mm cell clearance.

- [ ] **Step 4: Generate native and exchange files**

Run:

```bash
/Applications/FreeCAD.app/Contents/Resources/bin/FreeCADCmd jiewei_giftbox_design/03_cad/build_giftbox.py
```

Expected: one FCStd, three STEP assemblies, 13 STL parts and one JSON report.

- [ ] **Step 5: Verify GREEN and re-import states**

Run: `python3 -m unittest jiewei_giftbox_design/tests/test_cad_report.py -v`  
Use FreeCADCmd to read all three STEP files and confirm solid counts; confirm only configured moving parts change coordinates.

- [ ] **Step 6: Document unverified physical behavior**

`mechanism_notes.md` must cover paper swelling, wrap buildup, lock-key tearing, tray sag, full-load friction, 30-cycle opening, drop and vibration as unverified prototype work.

- [ ] **Step 7: Commit**

```bash
git add jiewei_giftbox_design/03_cad jiewei_giftbox_design/tests/test_cad_report.py
git commit -m "feat: build parametric Jiewei gift-box CAD"
```

### Task 4: 包装刀模 SVG/DXF

**Files:**
- Create: `jiewei_giftbox_design/03_cad/build_dielines.py`
- Generate: `jiewei_giftbox_design/03_cad/dielines/outer_sleeve.svg`
- Generate: `jiewei_giftbox_design/03_cad/dielines/wei_drawer.svg`
- Generate: `jiewei_giftbox_design/03_cad/dielines/zhao_tray.svg`
- Generate: `jiewei_giftbox_design/03_cad/dielines/lock_keys.svg`
- Generate: matching `.dxf` files
- Generate: `jiewei_giftbox_design/03_cad/dielines/dieline_manifest.json`
- Create: `jiewei_giftbox_design/tests/test_dielines.py`

**Interfaces:**
- Consumes: `BOX` and part dimensions from `cad_report.json`.
- Produces: cut layers in red, crease layers in blue, glue zones in gray and explicit units in millimetres.

- [ ] **Step 1: Write failing dieline tests**

```python
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DielineTests(unittest.TestCase):
    def test_svg_and_dxf_pairs_exist(self):
        for stem in ("outer_sleeve", "wei_drawer", "zhao_tray", "lock_keys"):
            self.assertTrue((ROOT / "03_cad" / "dielines" / f"{stem}.svg").is_file())
            self.assertTrue((ROOT / "03_cad" / "dielines" / f"{stem}.dxf").is_file())

    def test_manifest_has_line_semantics(self):
        data = json.loads((ROOT / "03_cad" / "dielines" / "dieline_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(data["units"], "mm")
        self.assertEqual(data["layers"], {"cut": "#FF0000", "crease": "#0000FF", "glue": "#808080"})
```

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest jiewei_giftbox_design/tests/test_dielines.py -v`  
Expected: FAIL because dielines do not exist.

- [ ] **Step 3: Implement dieline generation**

Generate millimetre-scale SVG and ASCII DXF polylines for every part. Include 15 mm glue tabs, board-thickness compensation, labelled grain direction and a 10 mm calibration square. Lock-key forbidden-glue areas must be separate gray polygons and must not overlap red cut paths.

- [ ] **Step 4: Generate, test and inspect**

Run: `python3 jiewei_giftbox_design/03_cad/build_dielines.py`  
Run: `python3 -m unittest jiewei_giftbox_design/tests/test_dielines.py -v`  
Expected: tests PASS. Open SVGs and re-import DXFs into FreeCAD; measure the calibration square as 10 × 10 mm.

- [ ] **Step 5: Commit**

```bash
git add jiewei_giftbox_design/03_cad/dielines jiewei_giftbox_design/03_cad/build_dielines.py jiewei_giftbox_design/tests/test_dielines.py
git commit -m "feat: generate Jiewei packaging dielines"
```

### Task 5: 三状态渲染与双节 CMF

**Files:**
- Create: `jiewei_giftbox_design/04_renders/render_giftbox.py`
- Generate: `jiewei_giftbox_design/04_renders/*.png`
- Generate: `jiewei_giftbox_design/04_renders/render_manifest.json`
- Create: `jiewei_giftbox_design/tests/test_render_outputs.py`

**Interfaces:**
- Consumes: audited STL parts, `state_offsets()`, both sleeve SVGs and proxy label SVG.
- Produces: `hero_closed.png`, `hero_unlocked.png`, `hero_open.png`, `sequence_01.png`–`sequence_04.png`, `exploded.png`, `dieline_preview.png`, `mid_autumn_variant.png`, `national_day_variant.png`, `ortho_top.png` and manifest.

- [ ] **Step 1: Write failing render tests**

```python
from pathlib import Path
import json
import unittest
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("hero_closed.png", "hero_unlocked.png", "hero_open.png", "exploded.png", "mid_autumn_variant.png", "national_day_variant.png")


class RenderTests(unittest.TestCase):
    def test_required_images_are_visible(self):
        for name in REQUIRED:
            with Image.open(ROOT / "04_renders" / name) as image:
                self.assertEqual(image.size, (1800, 1400))
                self.assertEqual(image.mode, "RGBA")
                self.assertIsNotNone(ImageChops.difference(image.getchannel("A"), Image.new("L", image.size, 0)).getbbox())

    def test_manifest_discloses_proxy_products(self):
        data = json.loads((ROOT / "04_renders" / "render_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(data["product_asset_status"], "neutral_size_proxy")
        self.assertEqual(data["geometry_basis"], "audited STL")
```

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest jiewei_giftbox_design/tests/test_render_outputs.py -v`  
Expected: FAIL because render outputs do not exist.

- [ ] **Step 3: Implement Blender state rendering**

Import audited STL parts only. Use state offsets from the configuration, with the outer sleeve fixed. Apply paperboard edge softness without changing silhouette. Every visible product proxy must carry the disclosure label. Render the Mid-Autumn and National Day versions from identical camera, geometry and lighting so the comparison isolates the sleeve layer.

- [ ] **Step 4: Render and verify**

Run:

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b --python jiewei_giftbox_design/04_renders/render_giftbox.py -- --final
python3 -m unittest jiewei_giftbox_design/tests/test_render_outputs.py -v
```

Expected: tests PASS; sequence images clearly show side pull before central pull; no render implies real branded goods.

- [ ] **Step 5: Inspect and commit**

Inspect a contact sheet and full-resolution sequence images for mechanism continuity, paper intersections, label readability and CMF restraint, then commit:

```bash
git add jiewei_giftbox_design/04_renders jiewei_giftbox_design/tests/test_render_outputs.py
git commit -m "feat: render Jiewei gift-box states"
```

### Task 6: 六张赛道一展板与多格式导出

**Files:**
- Create: `jiewei_giftbox_design/scripts/build_boards.py`
- Create: `jiewei_giftbox_design/scripts/export_boards.mjs`
- Create: `jiewei_giftbox_design/scripts/make_contact_sheet.py`
- Generate: `jiewei_giftbox_design/05_boards/src/board_01.svg`–`board_06.svg`
- Generate: `jiewei_giftbox_design/05_boards/jpg/board_01.jpg`–`board_06.jpg`
- Generate: `jiewei_giftbox_design/05_boards/pdf/board_01.pdf`–`board_06.pdf`
- Generate: `jiewei_giftbox_design/05_boards/contact_sheet.jpg`
- Create: `jiewei_giftbox_design/tests/test_board_outputs.py`

**Interfaces:**
- Consumes: identity, dielines, renders, `BOARD`, proxy disclosure.
- Produces: exactly six A4 SVG/JPG/PDF boards and one contact sheet.

- [ ] **Step 1: Write failing board tests**

```python
from pathlib import Path
import subprocess
import unittest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


class BoardTests(unittest.TestCase):
    def test_six_jpgs_meet_submission_contract(self):
        for index in range(1, 7):
            path = ROOT / "05_boards" / "jpg" / f"board_{index:02d}.jpg"
            with Image.open(path) as image:
                self.assertEqual(image.size, (2480, 3508))
                self.assertEqual(image.mode, "RGB")
                self.assertEqual(round(image.info["dpi"][0]), 300)
            self.assertLess(path.stat().st_size, 5_000_000)

    def test_six_pdfs_are_single_page_a4(self):
        for index in range(1, 7):
            path = ROOT / "05_boards" / "pdf" / f"board_{index:02d}.pdf"
            info = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True).stdout
            self.assertIn("Pages:           1", info)
            self.assertIn("A4", info)
```

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest jiewei_giftbox_design/tests/test_board_outputs.py -v`  
Expected: FAIL because board outputs do not exist.

- [ ] **Step 3: Implement the six-board story**

Use the exact six-board order from the spec, `01 / 06` numbering and a consistent 160 px margin. Board 2 must accurately explain围魏救赵; Board 3 must show the locked side-first sequence; Board 4 must combine exploded structure and dieline; Board 5 must compare seasonal sleeves on the same product; Board 6 must display the proxy disclosure and real-SKU submission gate prominently.

- [ ] **Step 4: Generate and export**

Run:

```bash
python3 jiewei_giftbox_design/scripts/build_boards.py
node jiewei_giftbox_design/scripts/export_boards.mjs
python3 jiewei_giftbox_design/scripts/make_contact_sheet.py
```

- [ ] **Step 5: Verify and visually inspect**

Run: `python3 -m unittest jiewei_giftbox_design/tests/test_board_outputs.py -v`  
Re-render all PDFs to PNG in a temporary directory and inspect the six-page contact sheet for clipping, missing proxies, accidental logo simulation and sequence ambiguity.

- [ ] **Step 6: Commit**

```bash
git add jiewei_giftbox_design/05_boards jiewei_giftbox_design/scripts/build_boards.py jiewei_giftbox_design/scripts/export_boards.mjs jiewei_giftbox_design/scripts/make_contact_sheet.py jiewei_giftbox_design/tests/test_board_outputs.py
git commit -m "feat: compose Jiewei competition boards"
```

### Task 7: 投稿文本、清单与投稿阻塞审计

**Files:**
- Create: `jiewei_giftbox_design/06_submission/work_description.md`
- Create: `jiewei_giftbox_design/06_submission/materials_and_pricing.md`
- Create: `jiewei_giftbox_design/06_submission/real_sku_input_checklist.md`
- Generate: `jiewei_giftbox_design/06_submission/source_manifest.csv`
- Create: `jiewei_giftbox_design/scripts/audit_submission.py`
- Generate: `jiewei_giftbox_design/07_audit/audit_report.json`
- Create: `jiewei_giftbox_design/07_audit/visual_review.md`
- Create: `jiewei_giftbox_design/tests/test_audit.py`

**Interfaces:**
- Consumes: complete project artifacts.
- Produces: `technical_status: pass|fail`, `submission_status: blocked_pending_real_sku_and_brand_assets`, explicit missing-input list and SHA-256 manifest.

- [ ] **Step 1: Write failing audit tests**

```python
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AuditTests(unittest.TestCase):
    def test_statuses_preserve_submission_gate(self):
        report = json.loads((ROOT / "07_audit" / "audit_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["technical_status"], "pass")
        self.assertEqual(report["submission_status"], "blocked_pending_real_sku_and_brand_assets")
        self.assertEqual(report["missing_inputs"], ["actual_sku_dimensions", "brand_assets_and_permission", "legal_food_copy", "entrant_identity"])

    def test_proxy_disclosure_survives_public_boards(self):
        for index in range(1, 7):
            svg = (ROOT / "05_boards" / "src" / f"board_{index:02d}.svg").read_text(encoding="utf-8")
            if index in (3, 4, 5, 6):
                self.assertIn("规格代理件", svg)
```

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest jiewei_giftbox_design/tests/test_audit.py -v`  
Expected: FAIL because audit outputs do not exist.

- [ ] **Step 3: Write submission and SKU intake documents**

`work_description.md` must explain the side-first mechanism, cultural basis, materials, dimensions and uses without naming an invented food product. `materials_and_pricing.md` must preserve the 80–160 yuan concept-model and 18–32 yuan target packaging ranges as estimates. `real_sku_input_checklist.md` must request measured dimensions, weight, product count, packaging images, vector logo, permitted brand colours, legal copy and authorisation contact.

- [ ] **Step 4: Implement technical audit and submission gate**

Check six JPG/SVG/PDF files, dimensions, dpi, RGB, file size, three STEP states, 13 STL files, four SVG/DXF dieline pairs, proxy labels, source licences and prohibited placeholders. Technical checks may pass, but the submission status must remain blocked while the four missing inputs listed in the test are absent.

- [ ] **Step 5: Run audit and full suite**

Run:

```bash
python3 jiewei_giftbox_design/scripts/audit_submission.py
python3 -m unittest discover -s jiewei_giftbox_design/tests -p "test_*.py" -v
git diff --check
```

Expected: audit exits 0 for technical validity, all tests PASS, and the report remains explicit about submission blocking.

- [ ] **Step 6: Complete visual review and commit**

Inspect JPGs, PDF re-renders, CAD states and dielines; document that proxy products are visible and correctly disclosed. Commit:

```bash
git add jiewei_giftbox_design
git commit -m "docs: finalize Jiewei technical candidate"
```

### Task 8: Final reproducibility verification

**Files:**
- Modify only if verification exposes a defect in the files above.

**Interfaces:**
- Consumes: complete `jiewei_giftbox_design/` tree.
- Produces: clean, reproducible candidate artifacts without weakening the real-SKU gate.

- [ ] **Step 1: Rebuild everything from scripts**

Run identity, CAD, dieline, Blender, board, contact-sheet and audit scripts in dependency order.

- [ ] **Step 2: Run all tests**

Run: `python3 -m unittest discover -s jiewei_giftbox_design/tests -p "test_*.py" -v`  
Expected: all tests PASS.

- [ ] **Step 3: Re-import neutral formats**

Use FreeCADCmd to open each STEP and one STL, re-import each DXF and measure its calibration square; use `pdfinfo` on six PDFs and `identify` on six JPGs.

- [ ] **Step 4: Review truthfulness**

Search public-facing SVG and Markdown files for `热销`, `已量产`, `真实产品`, `供应商报价`, `测试通过` and any fabricated brand claim. Confirm every visible proxy product on boards 3–6 is labelled.

- [ ] **Step 5: Verify repository hygiene**

Run `git status --short` and `git diff --check`; inspect the diff against the branch base. Confirm no unrelated project or video files are staged.

- [ ] **Step 6: Commit verification-only fixes if required**

If tracked outputs changed after fixes, rerun affected tests and commit only the `jiewei_giftbox_design/` tree:

```bash
git commit -m "fix: resolve Jiewei verification findings"
```

