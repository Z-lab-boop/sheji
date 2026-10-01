# 《步步生典》邯郸双节漫游章匣 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立一套可复现生成、可编辑、可审计的《步步生典》城市漫游章匣参赛包，包含参数化 CAD、印章与地图矢量、工程渲染、8 张 A4 展板和投稿文本。

**Architecture:** 项目放在独立目录 `bubushengdian_design/`。所有尺寸、色彩、文字和展板约束集中于 `scripts/design_config.py`；FreeCAD 是几何唯一来源，Blender 只读取审计后的 STL 渲染；SVG 展板由 Python 生成，再由浏览器导出 JPG/PDF；最终审计同时区分技术通过与人工路线复核门。

**Tech Stack:** Python 3.11、FreeCAD Python API、Blender 4.x Python API、Pillow、SVG、Node.js、Playwright、ImageMagick、Poppler、unittest。

**Spec:** `docs/superpowers/specs/2026-10-01-bubushengdian-city-stamp-kit-design.md`

## Global Constraints

- 闭合外形必须为 165 × 120 × 30 mm；外壳壁厚 1.8 mm；章盘单侧间隙 0.35 mm；抽拉行程 92 mm。
- 六枚模块章外形均为 32 × 32 × 23 mm，有效章面 26 × 26 mm。
- 基础四章为学步桥、回车巷、武灵丛台、邯郸市博物馆；限定两章为月满邯郸、山河同游。
- 最终提交为 8 张 2480 × 3508 px、300 dpi、RGB、单张小于 5 MB 的 A4 竖版 JPG，并保留 8 份 SVG/PDF。
- 渲染几何必须来自项目内生成并通过哈希记录的 STL；不允许生成式图像承担结构证明。
- 路线图必须标注“文化路线示意”；动态景点信息未经真人复核时，投稿状态保持候选稿。
- 既有 `suijian_design/` 和短视频目录不得修改。

---

### Task 1: 项目骨架、冻结参数与测试契约

**Files:**
- Create: `bubushengdian_design/README.md`
- Create: `bubushengdian_design/scripts/design_config.py`
- Create: `bubushengdian_design/tests/test_design_config.py`
- Create: `bubushengdian_design/01_research/sources.md`
- Copy: `suijian_design/01_research/fonts/*` → `bubushengdian_design/01_research/fonts/`

**Interfaces:**
- Produces: `PRODUCT: ProductSpec`, `BOARD: BoardSpec`, `COLORS: dict[str, str]`, `STAMP_NAMES: tuple[str, ...]`, `motion_offsets(progress: float) -> dict[str, tuple[float, float]]`, `validate_spec() -> list[str]`.
- Consumes: two approved design specs and the existing OFL-licensed font bundle.

- [ ] **Step 1: Write the failing parameter tests**

```python
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from design_config import BOARD, COLORS, PRODUCT, STAMP_NAMES, motion_offsets, validate_spec


class DesignConfigTests(unittest.TestCase):
    def test_frozen_product_contract(self):
        self.assertEqual((PRODUCT.width, PRODUCT.depth, PRODUCT.height), (165.0, 120.0, 30.0))
        self.assertEqual(PRODUCT.wall, 1.8)
        self.assertEqual(PRODUCT.clearance, 0.35)
        self.assertEqual(PRODUCT.travel, 92.0)

    def test_stamp_contract(self):
        self.assertEqual(len(STAMP_NAMES), 6)
        self.assertEqual((PRODUCT.stamp_width, PRODUCT.stamp_depth, PRODUCT.stamp_height), (32.0, 32.0, 23.0))
        self.assertEqual(PRODUCT.stamp_face, 26.0)

    def test_board_contract(self):
        self.assertEqual((BOARD.width_px, BOARD.height_px, BOARD.dpi, BOARD.count), (2480, 3508, 300, 8))
        self.assertEqual(BOARD.max_bytes, 5_000_000)

    def test_motion_is_clamped(self):
        self.assertEqual(motion_offsets(-1.0)["stamp_tray"], (0.0, 0.0))
        self.assertEqual(motion_offsets(2.0)["stamp_tray"], (92.0, 0.0))

    def test_spec_has_no_violations(self):
        self.assertEqual(validate_spec(), [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify RED**

Run: `python3 -m unittest bubushengdian_design/tests/test_design_config.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'design_config'`.

- [ ] **Step 3: Implement the frozen configuration**

Create dataclasses with these exact fields:

```python
@dataclass(frozen=True)
class ProductSpec:
    width: float = 165.0
    depth: float = 120.0
    height: float = 30.0
    corner_radius: float = 10.0
    wall: float = 1.8
    clearance: float = 0.35
    travel: float = 92.0
    stamp_width: float = 32.0
    stamp_depth: float = 32.0
    stamp_height: float = 23.0
    stamp_face: float = 26.0
    inkpad_width: float = 42.0
    inkpad_depth: float = 42.0
    inkpad_height: float = 12.0


@dataclass(frozen=True)
class BoardSpec:
    width_px: int = 2480
    height_px: int = 3508
    dpi: int = 300
    count: int = 8
    max_bytes: int = 5_000_000
```

Set `STAMP_NAMES` to the six names in Global Constraints. `motion_offsets()` must apply smoothstep easing to `stamp_tray` only; `outer_case` and `map_compartment` remain stationary. `validate_spec()` must reject altered envelope, wall below 1.5 mm, clearance outside 0.2–0.6 mm, non-six stamp count, or more than eight boards.

- [ ] **Step 4: Record authoritative sources and copied font licences**

`sources.md` must include the competition page, the Hebei culture-and-tourism idiom article, the Handan cultural-tourism route article, the National Day tourism article, font filenames, licence basis and retrieval date. It must state that landmark opening hours and route details require human recheck.

- [ ] **Step 5: Run tests and verify GREEN**

Run: `python3 -m unittest bubushengdian_design/tests/test_design_config.py -v`  
Expected: 5 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add bubushengdian_design
git commit -m "feat: define Bubushengdian product contract"
```

### Task 2: 字标、六枚章面与折叠地图源文件

**Files:**
- Create: `bubushengdian_design/scripts/build_identity.py`
- Create: `bubushengdian_design/02_identity/wordmark.svg`
- Create: `bubushengdian_design/02_identity/stamp_faces.svg`
- Create: `bubushengdian_design/02_identity/folding_map.svg`
- Create: `bubushengdian_design/02_identity/identity_manifest.json`
- Create: `bubushengdian_design/tests/test_identity_outputs.py`

**Interfaces:**
- Consumes: `COLORS`, `STAMP_NAMES`, local font filenames.
- Produces: editable SVG assets and `identity_manifest.json` with `palette`, `fonts`, `stamp_ids`, `route_disclaimer`.

- [ ] **Step 1: Write failing identity tests**

```python
from pathlib import Path
import json
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class IdentityTests(unittest.TestCase):
    def test_editable_svg_assets(self):
        for name in ("wordmark.svg", "stamp_faces.svg", "folding_map.svg"):
            path = ROOT / "02_identity" / name
            self.assertTrue(path.is_file())
            root = ET.parse(path).getroot()
            self.assertTrue(root.tag.endswith("svg"))
            self.assertGreater(path.stat().st_size, 1000)

    def test_manifest_contract(self):
        data = json.loads((ROOT / "02_identity" / "identity_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["stamp_ids"]), 6)
        self.assertEqual(data["route_disclaimer"], "文化路线示意")
        self.assertEqual(data["palette"]["city_blue"], "#173B46")
```

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest bubushengdian_design/tests/test_identity_outputs.py -v`  
Expected: FAIL because the SVG and manifest files do not exist.

- [ ] **Step 3: Implement deterministic SVG generation**

`build_identity.py` must generate all three SVGs without raster dependencies. The six stamp faces must use 26 × 26 mm view boxes, monochrome paths, minimum stroke width 0.6 mm and identifiers `stamp-01` through `stamp-06`. `folding_map.svg` must use a 480 × 330 mm view box, a visible “文化路线示意” label, four factual landmark nodes and two seasonal modules. The wordmark must be paths or project-authored geometric strokes, not a live calligraphy font.

- [ ] **Step 4: Generate and test**

Run: `python3 bubushengdian_design/scripts/build_identity.py`  
Run: `python3 -m unittest bubushengdian_design/tests/test_identity_outputs.py -v`  
Expected: 2 tests PASS and three editable SVGs are present.

- [ ] **Step 5: Visually inspect SVGs**

Open each SVG in Chrome at 100% and at thumbnail scale. Confirm Chinese text is readable, six stamp designs remain distinct in monochrome, and the map does not imply geographic accuracy.

- [ ] **Step 6: Commit**

```bash
git add bubushengdian_design/02_identity bubushengdian_design/scripts/build_identity.py bubushengdian_design/tests/test_identity_outputs.py
git commit -m "feat: create Bubushengdian identity and stamp system"
```

### Task 3: FreeCAD 参数化章匣与中性格式导出

**Files:**
- Create: `bubushengdian_design/03_cad/build_product.py`
- Generate: `bubushengdian_design/03_cad/bubushengdian_stamp_kit.FCStd`
- Generate: `bubushengdian_design/03_cad/bubushengdian_stamp_kit.step`
- Generate: `bubushengdian_design/03_cad/meshes/*.stl`
- Generate: `bubushengdian_design/03_cad/cad_report.json`
- Create: `bubushengdian_design/03_cad/mechanism_notes.md`
- Create: `bubushengdian_design/tests/test_cad_report.py`

**Interfaces:**
- Consumes: `PRODUCT`, `STAMP_NAMES`.
- Produces: named solids `outer_case`, `stamp_tray`, `stamp_01`–`stamp_06`, `inkpad_case`, `map_proxy`; `cad_report.json` with per-part validity, volume, bbox and SHA-256.

- [ ] **Step 1: Write failing CAD report tests**

```python
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CadReportTests(unittest.TestCase):
    def test_expected_parts_and_envelope(self):
        report = json.loads((ROOT / "03_cad" / "cad_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["assembly_bbox_mm"], [165.0, 120.0, 30.0])
        self.assertEqual(len(report["parts"]), 10)
        self.assertTrue(all(part["valid"] and part["solid_count"] == 1 for part in report["parts"].values()))

    def test_exchange_files_exist(self):
        self.assertTrue((ROOT / "03_cad" / "bubushengdian_stamp_kit.FCStd").is_file())
        self.assertTrue((ROOT / "03_cad" / "bubushengdian_stamp_kit.step").is_file())
        self.assertEqual(len(list((ROOT / "03_cad" / "meshes").glob("*.stl"))), 10)
```

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest bubushengdian_design/tests/test_cad_report.py -v`  
Expected: FAIL because `cad_report.json` and exchange files do not exist.

- [ ] **Step 3: Implement named parametric solids**

Use FreeCAD Part workbenches only. Build the outer case from a filleted 165 × 120 × 30 mm solid minus an internal cavity; build the tray with six 32.7 × 32.7 mm cells and a separate inkpad cell; create six stamp handles from one helper with unique top relief; create the inkpad case and a 480 × 330 × 0.3 mm folded-map envelope proxy. Preserve a closed assembly envelope of exactly 165 × 120 × 30 mm.

- [ ] **Step 4: Export and record geometry**

Run:

```bash
/Applications/FreeCAD.app/Contents/Resources/bin/FreeCADCmd bubushengdian_design/03_cad/build_product.py
```

The script must save FCStd, export the full assembly STEP, export one STL per named solid, and write `cad_report.json` using SHA-256 hashes of every exchange file.

- [ ] **Step 5: Verify GREEN and re-import**

Run: `python3 -m unittest bubushengdian_design/tests/test_cad_report.py -v`  
Run a FreeCAD console check that reads the STEP and prints solid count plus bounding box.  
Expected: 10 valid solids; envelope 165 × 120 × 30 mm.

- [ ] **Step 6: Document mechanism boundaries**

`mechanism_notes.md` must distinguish verified digital geometry from unverified friction, print tolerance, ink contamination, child safety, 100-cycle travel and 1 m drop performance.

- [ ] **Step 7: Commit**

```bash
git add bubushengdian_design/03_cad bubushengdian_design/tests/test_cad_report.py
git commit -m "feat: build parametric Bubushengdian CAD"
```

### Task 4: CAD 驱动的产品与工程渲染

**Files:**
- Create: `bubushengdian_design/04_renders/render_product.py`
- Generate: `bubushengdian_design/04_renders/*.png`
- Generate: `bubushengdian_design/04_renders/render_manifest.json`
- Create: `bubushengdian_design/tests/test_render_outputs.py`

**Interfaces:**
- Consumes: the 10 audited STL files and `COLORS`, `motion_offsets()`.
- Produces: `hero_closed.png`, `hero_open.png`, `map_unfolded.png`, `stamp_grid.png`, `interaction_01.png`–`interaction_04.png`, `exploded.png`, `ortho_top.png`, `ortho_front.png`, `scale_view.png`, plus hashes and camera metadata.

- [ ] **Step 1: Write failing render tests**

```python
from pathlib import Path
import json
import unittest
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "hero_closed.png": (1800, 1400),
    "hero_open.png": (1800, 1400),
    "map_unfolded.png": (1800, 1400),
    "stamp_grid.png": (1800, 1400),
    "exploded.png": (1800, 1600),
    "ortho_top.png": (1800, 1200),
    "ortho_front.png": (1800, 1200),
    "scale_view.png": (1800, 1400),
}


class RenderTests(unittest.TestCase):
    def test_required_images_are_visible_rgba(self):
        for name, size in REQUIRED.items():
            with Image.open(ROOT / "04_renders" / name) as image:
                self.assertEqual(image.size, size)
                self.assertEqual(image.mode, "RGBA")
                self.assertIsNotNone(ImageChops.difference(image.getchannel("A"), Image.new("L", size, 0)).getbbox())

    def test_manifest_binds_cad_hashes(self):
        data = json.loads((ROOT / "04_renders" / "render_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["cad_mesh_sha256"]), 10)
        self.assertEqual(data["geometry_basis"], "audited STL")
```

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest bubushengdian_design/tests/test_render_outputs.py -v`  
Expected: FAIL because render files do not exist.

- [ ] **Step 3: Implement Blender scene and state system**

Import each STL without remodeling. Use orthographic cameras for engineering views and a 70–85 mm equivalent perspective for hero views. Apply城墨蓝 shell, 月纸白 map, 印泥朱 stamp faces and restrained 路标金 detail. Closed/open states must use `motion_offsets()`; the outer case stays fixed and the tray travels a maximum of 92 mm.

- [ ] **Step 4: Render final images**

Run:

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b --python bubushengdian_design/04_renders/render_product.py -- --final
```

Expected: all required images plus four interaction frames and a manifest are generated without deprecation warnings.

- [ ] **Step 5: Run tests and inspect contact sheet**

Run: `python3 -m unittest bubushengdian_design/tests/test_render_outputs.py -v`  
Create a temporary contact sheet and inspect full-size edges, missing meshes, legibility and state continuity.  
Expected: tests PASS and no geometry drift between views.

- [ ] **Step 6: Commit**

```bash
git add bubushengdian_design/04_renders bubushengdian_design/tests/test_render_outputs.py
git commit -m "feat: render Bubushengdian product states"
```

### Task 5: 八张 A4 展板与多格式导出

**Files:**
- Create: `bubushengdian_design/scripts/build_boards.py`
- Create: `bubushengdian_design/scripts/export_boards.mjs`
- Create: `bubushengdian_design/scripts/make_contact_sheet.py`
- Generate: `bubushengdian_design/05_boards/src/board_01.svg`–`board_08.svg`
- Generate: `bubushengdian_design/05_boards/jpg/board_01.jpg`–`board_08.jpg`
- Generate: `bubushengdian_design/05_boards/pdf/board_01.pdf`–`board_08.pdf`
- Generate: `bubushengdian_design/05_boards/contact_sheet.jpg`
- Create: `bubushengdian_design/tests/test_board_outputs.py`

**Interfaces:**
- Consumes: identity SVGs, render PNGs, `BOARD`, `COLORS`, frozen copy.
- Produces: exactly 8 editable SVG boards, 8 submission JPGs, 8 A4 PDFs and one contact sheet.

- [ ] **Step 1: Write failing board tests**

```python
from pathlib import Path
import subprocess
import unittest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


class BoardTests(unittest.TestCase):
    def test_jpg_contract(self):
        for index in range(1, 9):
            path = ROOT / "05_boards" / "jpg" / f"board_{index:02d}.jpg"
            with Image.open(path) as image:
                self.assertEqual(image.size, (2480, 3508))
                self.assertEqual(image.mode, "RGB")
                self.assertEqual(round(image.info["dpi"][0]), 300)
            self.assertLess(path.stat().st_size, 5_000_000)

    def test_pdf_contract(self):
        for index in range(1, 9):
            path = ROOT / "05_boards" / "pdf" / f"board_{index:02d}.pdf"
            info = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True).stdout
            self.assertIn("Pages:           1", info)
            self.assertIn("A4", info)
```

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest bubushengdian_design/tests/test_board_outputs.py -v`  
Expected: FAIL because board exports do not exist.

- [ ] **Step 3: Implement the eight-board narrative**

Follow the exact order in the spec. Use a consistent 160 px outer margin, 12-column grid, fixed header/footer, `01 / 08` numbering and a maximum of three typographic levels per panel. Board 2 must state the original meaning of 邯郸学步; Board 6 must label seasonal scenes as design applications; Board 8 must display prototype and human-review boundaries.

- [ ] **Step 4: Generate SVG, JPG, PDF and contact sheet**

Run:

```bash
python3 bubushengdian_design/scripts/build_boards.py
node bubushengdian_design/scripts/export_boards.mjs
python3 bubushengdian_design/scripts/make_contact_sheet.py
```

- [ ] **Step 5: Verify GREEN and visually inspect**

Run: `python3 -m unittest bubushengdian_design/tests/test_board_outputs.py -v`  
Render every PDF back to PNG in a `mktemp -d` directory and inspect the 8-page contact sheet for clipping, missing images, fonts, contrast and page sequence.

- [ ] **Step 6: Commit**

```bash
git add bubushengdian_design/05_boards bubushengdian_design/scripts/build_boards.py bubushengdian_design/scripts/export_boards.mjs bubushengdian_design/scripts/make_contact_sheet.py bubushengdian_design/tests/test_board_outputs.py
git commit -m "feat: compose Bubushengdian competition boards"
```

### Task 6: 投稿文本、来源清单与双状态审计

**Files:**
- Create: `bubushengdian_design/06_submission/work_description.md`
- Create: `bubushengdian_design/06_submission/materials_and_pricing.md`
- Generate: `bubushengdian_design/06_submission/source_manifest.csv`
- Create: `bubushengdian_design/scripts/audit_submission.py`
- Generate: `bubushengdian_design/07_audit/audit_report.json`
- Create: `bubushengdian_design/07_audit/visual_review.md`
- Create: `bubushengdian_design/tests/test_audit.py`

**Interfaces:**
- Consumes: all generated files, board constraints, local source notes.
- Produces: `technical_status: pass|fail`, `submission_status: candidate_pending_human_route_review`, SHA-256 manifest and human checklist.

- [ ] **Step 1: Write failing audit tests**

```python
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AuditTests(unittest.TestCase):
    def test_audit_statuses_are_honest(self):
        report = json.loads((ROOT / "07_audit" / "audit_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["technical_status"], "pass")
        self.assertEqual(report["submission_status"], "candidate_pending_human_route_review")
        self.assertTrue(all(check["passed"] for check in report["checks"]))

    def test_manifest_has_required_types(self):
        content = (ROOT / "06_submission" / "source_manifest.csv").read_text(encoding="utf-8")
        for token in ("cad", "render", "board_source", "board_jpg", "board_pdf", "external_reference"):
            self.assertIn(token, content)
```

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest bubushengdian_design/tests/test_audit.py -v`  
Expected: FAIL because the audit report does not exist.

- [ ] **Step 3: Write submission copy with evidence boundaries**

`work_description.md` must contain name, category, dimensions, design logic, use, advantages, culture, estimated pricing and market outlook. `materials_and_pricing.md` must separate concept model, small-batch production and retail-position estimates. Neither file may claim real sales, completed physical testing or verified live routes.

- [ ] **Step 4: Implement the audit**

Check exactly eight JPG/SVG/PDF files, A4/PDF page count, 300 dpi, RGB, file size, CAD report validity, exchange-file readability, required source types, prohibited identity placeholders and route disclaimer presence. Write LF-only CSV rows and JSON with both technical and submission statuses.

- [ ] **Step 5: Run the audit and full test suite**

Run:

```bash
python3 bubushengdian_design/scripts/audit_submission.py
python3 -m unittest discover -s bubushengdian_design/tests -p "test_*.py" -v
git diff --check
```

Expected: audit exits 0, all tests PASS, and `git diff --check` has no output.

- [ ] **Step 6: Complete visual review and commit**

Inspect JPGs, PDFs re-rendered to PNG, transparent render edges and the opened STEP/STL. Record date, checked artifacts and honest boundaries in `visual_review.md`, then commit:

```bash
git add bubushengdian_design
git commit -m "docs: finalize Bubushengdian submission candidate"
```

### Task 7: Final reproducibility verification

**Files:**
- Modify only if verification exposes a defect in the files above.

**Interfaces:**
- Consumes: the complete `bubushengdian_design/` tree.
- Produces: a clean branch commit with reproducible evidence.

- [ ] **Step 1: Rebuild from source scripts**

Run identity generation, FreeCAD CAD generation, Blender final rendering, board generation/export, contact sheet generation and audit in that order.

- [ ] **Step 2: Re-run all tests**

Run: `python3 -m unittest discover -s bubushengdian_design/tests -p "test_*.py" -v`  
Expected: all tests PASS with no deprecation warning.

- [ ] **Step 3: Verify exchange files externally**

Use FreeCADCmd to re-import the STEP and one representative STL; use `pdfinfo` on all eight PDFs and ImageMagick `identify` on all eight JPGs. Confirm counts, dimensions and colour modes match the frozen contract.

- [ ] **Step 4: Verify repository hygiene**

Run: `git status --short`, `git diff --check`, and inspect the final diff against the branch base. Confirm no files from `suijian_design/`, `audio/`, `metadata/`, `output/`, `scenes/` or `tmp_segments/` are staged.

- [ ] **Step 5: Commit verification-only fixes if required**

If verification changed tracked outputs, stage only `bubushengdian_design/`, rerun the affected tests, and commit with:

```bash
git commit -m "fix: resolve Bubushengdian verification findings"
```

