# 《解围》投稿级升级 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将《解围》重构为证据边界清晰、视觉写实、CAD 与刀模一致、完成实名签字后即可投递赛道一初审的“六味邯郸”概念包装方案。

**Architecture:** 在现有 `jiewei_giftbox_design` 生成链上升级，而不是另建不可追溯的平行项目。`design_config.py` 作为六味模块、结构参数和措辞的唯一事实源，身份系统、CAD、渲染、展板、审计和最终 ZIP 依次消费该配置；旧版候选资料保留作审计历史，新版生成物替换推荐投稿入口。

**Tech Stack:** Python 3.14/工作区 Python（Pillow）、FreeCAD 1.1.1 Python API、SVG、DXF R12、Node.js/Playwright、Poppler、ImageMagick、`unittest`、ZIP/SHA-256。

**Spec:** `docs/superpowers/specs/2026-10-03-jiewei-submission-upgrade-design.md`

## Global Constraints

- 闭合包络固定为 `290 × 230 × 75 mm`；侧移 `42 mm`；中央托盘展示行程 `145 mm`；月璧窗口 `108 mm`。
- 六个原创概念模块统一外廓为 `68 × 62 × 44 mm`，布局为 `3 × 2`，数字装配间隙每侧 `1.0 mm`。
- 赛道一最终图片固定为 6 张 A4 竖幅 `2480 × 3508 px`、300 dpi、RGB JPG，单张小于 `5_000_000` 字节。
- 不嵌入第三方商品照片、现有邯宝坊 Logo、条码、许可证、营养数据或地理标志图形。
- 所有容量、净含量、成本和价格仅可标为“概念建议值”或“设计估算”。
- 设计完成后的投稿状态为 `conditionally_ready_pending_identity_signature`；没有实名信息和本人签字 PDF 时不得标记 `ready`。
- 现有 `hanbaofang_public_product_dossier.md` 与授权申请书只作历史证据，不进入新版推荐投稿 ZIP。

---

### Task 1: 冻结六味概念配置与真实性合同

**Files:**
- Modify: `jiewei_giftbox_design/scripts/design_config.py`
- Modify: `jiewei_giftbox_design/tests/test_design_config.py`

**Interfaces:**
- Produces: `PRODUCT_MODULE`, `PRODUCTS`, `CONCEPT_DISCLOSURE`，供身份、CAD、渲染、展板和审计脚本导入。
- Preserves: `BOX`, `BOARD`, `state_offsets(state: str)`。

- [ ] **Step 1: 将旧代理测试改为六味概念合同测试**

```python
def test_concept_product_contract(self):
    self.assertEqual(
        (PRODUCT_MODULE.width, PRODUCT_MODULE.depth, PRODUCT_MODULE.height, PRODUCT_MODULE.count),
        (68.0, 62.0, 44.0, 6),
    )
    self.assertTrue(PRODUCT_MODULE.is_concept)
    self.assertEqual(len(PRODUCTS), 6)
    self.assertEqual(
        [item.category for item in PRODUCTS],
        ["鸡泽辣椒", "魏县鸭梨", "涉县核桃", "武安小米", "永年大蒜", "大名小磨香油"],
    )
    self.assertEqual(CONCEPT_DISCLOSURE, "概念包装建议规格，投产前复核")
```

- [ ] **Step 2: 运行单测，确认因新接口尚不存在而失败**

Run: `/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest jiewei_giftbox_design.tests.test_design_config -v`  
Expected: `ImportError` 或 `NameError` 指向 `PRODUCT_MODULE`、`PRODUCTS`、`CONCEPT_DISCLOSURE`。

- [ ] **Step 3: 实现冻结配置**

```python
@dataclass(frozen=True)
class ProductModuleSpec:
    width: float = 68.0
    depth: float = 62.0
    height: float = 44.0
    count: int = 6
    is_concept: bool = True

@dataclass(frozen=True)
class ProductConcept:
    code: str
    category: str
    display_name: str
    color: str

CONCEPT_DISCLOSURE = "概念包装建议规格，投产前复核"
PRODUCT_MODULE = ProductModuleSpec()
PRODUCTS = (
    ProductConcept("A", "鸡泽辣椒", "椒起鸡泽", "#A83B32"),
    ProductConcept("B", "魏县鸭梨", "梨润魏州", "#819B79"),
    ProductConcept("C", "涉县核桃", "核藏太行", "#80644B"),
    ProductConcept("D", "武安小米", "粟映武安", "#C19A55"),
    ProductConcept("E", "永年大蒜", "蒜生永年", "#EEE4D0"),
    ProductConcept("F", "大名小磨香油", "油香大名", "#B97832"),
)
```

同时把 `COPY["category"]` 改为 `邯宝坊“六味邯郸”机关礼盒概念提案`，并让 `validate_spec()` 验证六个品类唯一、模块尺寸正确、展板数不超过 6。

- [ ] **Step 4: 运行测试并确认通过**

Run: `/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest jiewei_giftbox_design.tests.test_design_config -v`  
Expected: 5 个及以上测试全部 `OK`。

- [ ] **Step 5: 提交配置合同**

```bash
git add jiewei_giftbox_design/scripts/design_config.py jiewei_giftbox_design/tests/test_design_config.py
git commit -m "design: define Jiewei six-product concept contract"
```

### Task 2: 重做原创字标、双节外套与六件内包装

**Files:**
- Modify: `jiewei_giftbox_design/scripts/build_identity.py`
- Modify: `jiewei_giftbox_design/tests/test_identity_outputs.py`
- Generate: `jiewei_giftbox_design/02_identity/concept_product_labels.svg`
- Generate: `jiewei_giftbox_design/02_identity/identity_manifest.json`
- Modify: `jiewei_giftbox_design/02_identity/mid_autumn_sleeve.svg`
- Modify: `jiewei_giftbox_design/02_identity/national_day_sleeve.svg`

**Interfaces:**
- Consumes: `PRODUCTS`, `PRODUCT_MODULE`, `CONCEPT_DISCLOSURE`, `COLORS`, `COPY`。
- Produces: 四件可编辑 SVG 和身份清单；后续渲染与展板只读取这些原创资产。

- [ ] **Step 1: 写失败测试，要求六个产品名和概念状态进入 SVG/清单**

```python
def test_concept_labels_and_manifest(self):
    label_path = ROOT / "02_identity" / "concept_product_labels.svg"
    text = label_path.read_text(encoding="utf-8")
    for name in ("椒起鸡泽", "梨润魏州", "核藏太行", "粟映武安", "蒜生永年", "油香大名"):
        self.assertIn(name, text)
    self.assertIn("概念包装建议规格，投产前复核", text)
    manifest = json.loads((ROOT / "02_identity/identity_manifest.json").read_text(encoding="utf-8"))
    self.assertEqual(manifest["brand_asset_status"], "official_brief_named_target_no_logo_asset")
    self.assertEqual(manifest["product_asset_status"], "original_concept_secondary_packaging")
```

- [ ] **Step 2: 运行测试，确认旧 `proxy_product_labels.svg` 合同失败**

Run: `RUNTIME_PY=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3; "$RUNTIME_PY" -m unittest jiewei_giftbox_design.tests.test_identity_outputs -v`  
Expected: FAIL，缺少 `concept_product_labels.svg` 或新状态值。

- [ ] **Step 3: 修改生成器并生成资产**

将 `proxy_labels()` 改为 `concept_product_labels()`：每件模块使用 `68 × 62 mm` 正面、对应品类名/概念名/地域辅色和统一路线符号；背面仅画信息层级网格并写“信息示意”，不生成法定字段值。将外套旧文案“品牌区待授权资产/法定信息待真实文案”替换为“邯宝坊赛题概念提案/生产信息投产前复核”，保留原创字标而不仿制现有 Logo。

Run: `RUNTIME_PY=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3; "$RUNTIME_PY" jiewei_giftbox_design/scripts/build_identity.py`

- [ ] **Step 4: 验证 SVG 可解析且测试通过**

Run: `RUNTIME_PY=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3; "$RUNTIME_PY" -m unittest jiewei_giftbox_design.tests.test_identity_outputs -v`  
Expected: 全部 `OK`，四件 SVG 均可被 `ElementTree` 解析。

- [ ] **Step 5: 提交身份系统**

```bash
git add jiewei_giftbox_design/02_identity jiewei_giftbox_design/scripts/build_identity.py jiewei_giftbox_design/tests/test_identity_outputs.py
git commit -m "design: create original Jiewei six-flavor packaging identity"
```

### Task 3: 按概念模块重建 CAD、三状态 STEP 与刀模

**Files:**
- Modify: `jiewei_giftbox_design/03_cad/build_giftbox.py`
- Modify: `jiewei_giftbox_design/03_cad/build_dielines.py`
- Modify: `jiewei_giftbox_design/tests/test_cad_report.py`
- Modify: `jiewei_giftbox_design/tests/test_dielines.py`
- Generate: `jiewei_giftbox_design/03_cad/jiewei_giftbox.FCStd`
- Generate: `jiewei_giftbox_design/03_cad/jiewei_giftbox_{closed,unlocked,open}.step`
- Generate: `jiewei_giftbox_design/03_cad/meshes/*.stl`
- Generate: `jiewei_giftbox_design/03_cad/dielines/*.{svg,dxf,json}`
- Generate: `jiewei_giftbox_design/03_cad/cad_report.json`

**Interfaces:**
- Consumes: `BOX`, `PRODUCT_MODULE`, `PRODUCTS`, `CONCEPT_DISCLOSURE`, `state_offsets()`。
- Produces: 13 个有效实体；三个 STEP 状态；四套毫米级刀模；新版 CAD 报告。

- [ ] **Step 1: 写失败测试固定模块几何与报告状态**

```python
def test_six_concept_modules_are_modelled(self):
    report = json.loads((ROOT / "03_cad/cad_report.json").read_text(encoding="utf-8"))
    modules = [value for key, value in report["parts"].items() if key.startswith("concept_module_")]
    self.assertEqual(len(modules), 6)
    self.assertTrue(all(item["bbox_mm"] == [68.0, 62.0, 44.8] for item in modules))
    self.assertEqual(report["product_asset_status"], "original_concept_secondary_packaging")
```

刀模测试增加：`dieline_manifest["module_outer_mm"] == [68.0, 62.0, 44.0]`，且 `zhao_tray.svg` 不再包含“真实 SKU 到位后重算”。

- [ ] **Step 2: 运行测试，确认旧代理几何失败**

Run: `RUNTIME_PY=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3; "$RUNTIME_PY" -m unittest jiewei_giftbox_design.tests.test_cad_report jiewei_giftbox_design.tests.test_dielines -v`  
Expected: FAIL，旧报告只有 `sku_proxy_*` 且尺寸为 `60 × 60 × 35 mm`。

- [ ] **Step 3: 修改 FreeCAD 构建脚本**

将 `make_proxy(index)` 改为 `make_concept_module(index)`，按 `3 × 2` 阵列定位；模块主体使用 `68 × 62 × 44 mm`，正面浮雕层厚 `0.8 mm`，因此报告包络为 `68 × 62 × 44.8 mm`。对象命名为 `concept_module_A` 至 `concept_module_F`；`MaterialIntent` 写为 `Original concept secondary carton`；`EvidenceStatus` 写入 `CONCEPT_DISCLOSURE`。保持 13 个实体和既有外盒包络。

- [ ] **Step 4: 更新刀模说明与清单**

保留 `outer_sleeve`、`wei_drawer`、`zhao_tray`、`lock_keys` 四组输出；将中央托盘说明改为“3 × 2 概念模块阵列，单模块 68 × 62 × 44 mm，投产前按实际商品复核”，并在 JSON 清单增加 `module_outer_mm`。

- [ ] **Step 5: 用 FreeCAD 生成并复测**

Run: `/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd jiewei_giftbox_design/03_cad/build_giftbox.py`  
Run: `RUNTIME_PY=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3; "$RUNTIME_PY" jiewei_giftbox_design/03_cad/build_dielines.py`  
Run: `RUNTIME_PY=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3; "$RUNTIME_PY" -m unittest jiewei_giftbox_design.tests.test_cad_report jiewei_giftbox_design.tests.test_dielines -v`  
Expected: 全部 `OK`；三份 STEP 存在，13 份 STL 非空。

- [ ] **Step 6: 提交 CAD 与刀模**

```bash
git add jiewei_giftbox_design/03_cad jiewei_giftbox_design/tests/test_cad_report.py jiewei_giftbox_design/tests/test_dielines.py
git commit -m "cad: rebuild Jiewei tray for six concept modules"
```

### Task 4: 生成写实产品图、手部开盒与场景图

**Files:**
- Modify: `jiewei_giftbox_design/04_renders/render_giftbox.py`
- Modify: `jiewei_giftbox_design/tests/test_render_outputs.py`
- Generate: `jiewei_giftbox_design/04_renders/product_family.png`
- Generate: `jiewei_giftbox_design/04_renders/hand_opening.png`
- Generate: `jiewei_giftbox_design/04_renders/retail_scene.png`
- Regenerate: `jiewei_giftbox_design/04_renders/*.png`
- Regenerate: `jiewei_giftbox_design/04_renders/render_manifest.json`

**Interfaces:**
- Consumes: 审计后的 STL、身份 SVG、`PRODUCTS` 色彩和概念披露。
- Produces: 展板使用的透明产品图和有背景场景图；清单声明几何来源及图像性质。

- [ ] **Step 1: 写失败测试固定新增画面和清单状态**

```python
REQUIRED = (
    "hero_closed.png", "hero_unlocked.png", "hero_open.png", "exploded.png",
    "product_family.png", "hand_opening.png", "retail_scene.png",
    "mid_autumn_variant.png", "national_day_variant.png",
)

def test_manifest_discloses_concept_products(self):
    data = json.loads((ROOT / "04_renders/render_manifest.json").read_text(encoding="utf-8"))
    self.assertEqual(data["product_asset_status"], "original_concept_secondary_packaging")
    self.assertEqual(data["geometry_basis"], "audited STL from concept_v2 CAD")
    self.assertEqual(data["scene_status"], "visualisation_not_product_photography")
```

- [ ] **Step 2: 运行测试确认新增画面缺失**

Run: `RUNTIME_PY=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3; "$RUNTIME_PY" -m unittest jiewei_giftbox_design.tests.test_render_outputs -v`  
Expected: FAIL，至少缺少 `product_family.png`、`hand_opening.png`、`retail_scene.png`。

- [ ] **Step 3: 升级渲染器**

在现有 CAD 投影基础上增加纸纤维噪声、包边高光、接触阴影、烫金方向反射和柔和自然侧光。`product_family.png` 展示六件统一内包装；`hand_opening.png` 使用原创程序化手部剪影/低细节中性手模表达尺度与动作，不冒充真人摄影；`retail_scene.png` 使用原创桌面、展架和环境光构成文旅门店概念场景。不得下载或嵌入第三方商品图。

- [ ] **Step 4: 生成并执行图像合同测试**

Run: `RUNTIME_PY=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3; "$RUNTIME_PY" jiewei_giftbox_design/04_renders/render_giftbox.py`  
Run: `RUNTIME_PY=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3; "$RUNTIME_PY" -m unittest jiewei_giftbox_design.tests.test_render_outputs -v`  
Expected: 全部 `OK`；九张要求图片为 `1800 × 1400`，色彩/Alpha 非空。

- [ ] **Step 5: 生成人工复核拼版**

Run: `magick montage jiewei_giftbox_design/04_renders/hero_closed.png jiewei_giftbox_design/04_renders/hero_open.png jiewei_giftbox_design/04_renders/product_family.png jiewei_giftbox_design/04_renders/hand_opening.png jiewei_giftbox_design/04_renders/retail_scene.png -thumbnail 720x560 -tile 3x2 -geometry +24+24 jiewei_giftbox_design/04_renders/render_contact_sheet.png`  
Expected: 拼版中无漂浮模块、破损文字、错误阴影或结构穿插。

- [ ] **Step 6: 提交渲染资产**

```bash
git add jiewei_giftbox_design/04_renders jiewei_giftbox_design/tests/test_render_outputs.py
git commit -m "design: render realistic Jiewei concept packaging scenes"
```

### Task 5: 重建六张投稿展板

**Files:**
- Modify: `jiewei_giftbox_design/scripts/build_boards.py`
- Modify: `jiewei_giftbox_design/tests/test_board_outputs.py`
- Regenerate: `jiewei_giftbox_design/05_boards/src/*.svg`
- Regenerate: `jiewei_giftbox_design/05_boards/jpg/*.jpg`
- Regenerate: `jiewei_giftbox_design/05_boards/pdf/*.pdf`
- Regenerate: `jiewei_giftbox_design/05_boards/contact_sheet.jpg`

**Interfaces:**
- Consumes: 新版渲染、CAD 报告、六味配置和概念披露。
- Produces: 赛事初审直接使用的六张 JPG 及可编辑 SVG/PDF。

- [ ] **Step 1: 写失败测试固定新标题和真实性用语**

```python
def test_board_copy_matches_concept_submission(self):
    joined = "\n".join(
        (ROOT / f"05_boards/src/board_{index:02d}.svg").read_text(encoding="utf-8")
        for index in range(1, 7)
    )
    for token in ("六味邯郸", "椒起鸡泽", "梨润魏州", "核藏太行", "粟映武安", "蒜生永年", "油香大名"):
        self.assertIn(token, joined)
    self.assertIn("概念包装建议规格，投产前复核", joined)
    for prohibited in ("目前不能正式投稿", "BLOCKED", "真实 SKU", "待授权资产"):
        self.assertNotIn(prohibited, joined)
```

- [ ] **Step 2: 运行测试，确认旧第 6 张阻塞文案失败**

Run: `RUNTIME_PY=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3; "$RUNTIME_PY" -m unittest jiewei_giftbox_design.tests.test_board_outputs -v`  
Expected: FAIL，旧展板仍含 `BLOCKED` 和真实 SKU 缺口。

- [ ] **Step 3: 按规范重写六张 SVG**

固定标题顺序：`解围·六味邯郸`、`把典故变成必须遵守的动作`、`先解锁，再见礼`、`六地六味，一套包装语言`、`结构、材料与制造边界`、`双节应用与市场场景`。第 4 张使用 `product_family.png`；第 3 张使用 `hand_opening.png`；第 6 张使用 `retail_scene.png`。概念声明置于第 4、5、6 张页脚，不再把缺失证据作为主视觉。

- [ ] **Step 4: 导出 JPG/PDF 并制作拼版**

Run: `RUNTIME_PY=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3; "$RUNTIME_PY" jiewei_giftbox_design/scripts/build_boards.py`  
Run: `node jiewei_giftbox_design/scripts/export_boards.mjs`  
Run: `RUNTIME_PY=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3; "$RUNTIME_PY" jiewei_giftbox_design/scripts/make_contact_sheet.py`

- [ ] **Step 5: 验证像素、DPI、色彩、大小和 A4 PDF**

Run: `RUNTIME_PY=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3; "$RUNTIME_PY" -m unittest jiewei_giftbox_design.tests.test_board_outputs -v`  
Expected: 六张 JPG 与六份单页 A4 PDF 全部 `OK`，无禁止措辞。

- [ ] **Step 6: 打开拼版进行人工视觉复核并记录**

检查安全边距、标题层级、产品名、手部动作、纸材、阴影、数字单位和场景一致性；将结果写入 `jiewei_giftbox_design/07_audit/visual_review.md`。

- [ ] **Step 7: 提交展板**

```bash
git add jiewei_giftbox_design/05_boards jiewei_giftbox_design/07_audit/visual_review.md jiewei_giftbox_design/scripts/build_boards.py jiewei_giftbox_design/tests/test_board_outputs.py
git commit -m "design: rebuild Jiewei submission boards for six-flavor concept"
```

### Task 6: 更新作品说明、证据账本与提交审计

**Files:**
- Modify: `jiewei_giftbox_design/01_research/sources.md`
- Modify: `jiewei_giftbox_design/06_submission/work_description.md`
- Modify: `jiewei_giftbox_design/06_submission/materials_and_pricing.md`
- Create: `jiewei_giftbox_design/06_submission/concept_product_evidence.csv`
- Modify: `jiewei_giftbox_design/scripts/audit_submission.py`
- Modify: `jiewei_giftbox_design/tests/test_audit.py`
- Regenerate: `jiewei_giftbox_design/06_submission/source_manifest.csv`
- Regenerate: `jiewei_giftbox_design/07_audit/audit_report.json`

**Interfaces:**
- Consumes: 赛事规则、六类地域品类政府来源、所有新版生成物。
- Produces: `technical_status=pass`、`submission_status=conditionally_ready_pending_identity_signature` 的可审计报告。

- [ ] **Step 1: 写失败测试固定新投稿门**

```python
def test_status_is_conditionally_ready_only(self):
    report = json.loads((ROOT / "07_audit/audit_report.json").read_text(encoding="utf-8"))
    self.assertEqual(report["technical_status"], "pass")
    self.assertEqual(report["submission_status"], "conditionally_ready_pending_identity_signature")
    self.assertEqual(report["missing_inputs"], ["entrant_identity", "signed_registration_pdf"])
    self.assertNotIn("brand_assets_and_permission", report["missing_inputs"])
```

- [ ] **Step 2: 运行测试确认旧阻塞状态失败**

Run: `RUNTIME_PY=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3; "$RUNTIME_PY" -m unittest jiewei_giftbox_design.tests.test_audit -v`  
Expected: FAIL，旧报告仍为 `blocked_pending_real_sku_and_brand_assets`。

- [ ] **Step 3: 更新文案和证据表**

作品说明必须使用正式全名、六味模块、结构参数和“概念提案”边界；材料与价格只提供设计估算及假设。`concept_product_evidence.csv` 每行字段固定为：`concept_id,category,public_basis_url,evidence_state,allowed_claim,prohibited_claim`，六个品类状态为 `verified_category_only`。

- [ ] **Step 4: 修改审计器**

删除真实 SKU、品牌授权、法定食品文案作为初审阻塞条件；新增六味证据表完整性、概念声明、禁止 Logo/条码/许可证措辞、九张渲染、六张展板和新清单状态检查。报告边界固定为：数字设计和展示模型已完成；未声称投产、销售、食品合规或实体耐久测试。

- [ ] **Step 5: 运行审计和全项目测试**

Run: `RUNTIME_PY=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3; "$RUNTIME_PY" jiewei_giftbox_design/scripts/audit_submission.py`  
Run: `RUNTIME_PY=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3; "$RUNTIME_PY" -m unittest discover -s jiewei_giftbox_design/tests -p 'test_*.py'`  
Expected: 全部测试 `OK`；审计进程退出码 0，状态为 `conditionally_ready_pending_identity_signature`。

- [ ] **Step 6: 提交审计材料**

```bash
git add jiewei_giftbox_design/01_research jiewei_giftbox_design/06_submission jiewei_giftbox_design/07_audit jiewei_giftbox_design/scripts/audit_submission.py jiewei_giftbox_design/tests/test_audit.py
git commit -m "docs: make Jiewei concept claims submission-safe"
```

### Task 7: 替换投稿包和总交接包中的《解围》入口

**Files:**
- Modify: `competition_submission/build_submission_packages.py`
- Modify: `competition_submission/build_final_handoff.py`
- Modify: `competition_submission/README.md`
- Modify: `competition_submission/form_fill_text.md`
- Modify: `competition_submission/email_templates.md`
- Modify: `competition_submission/submission_readiness.md`
- Modify: `competition_submission/claim_evidence_ledger.csv`
- Modify: `competition_submission/rubric_matrix.csv`
- Modify: `deliverables/cad_models/README.md`
- Regenerate: `competition_submission/packages/*`
- Regenerate: `deliverables/cad_models/02_jiewei_giftbox_cad_model.zip`
- Regenerate: `deliverables/final_submission_handoff/*`
- Regenerate: `deliverables/和氏璧杯_三作品投稿与CAD交接总包_2026-10-03.zip`

**Interfaces:**
- Consumes: 新版审计报告、六张 JPG、作品说明和 CAD 文件。
- Produces: `赛道一_解围_待填写报名表后提交.zip`，并让总包显示三件作品均为“待实名签字”。

- [ ] **Step 1: 修改投稿项目状态和复制清单**

将《解围》的 `slug` 改为 `赛道一_解围_待填写报名表后提交`，`status` 改为 `conditionally_ready`，复制新版六张 JPG、官方报名表、作品说明、邮件模板和状态说明；不再复制授权申请书、真实 SKU 清单或旧阻塞说明。

- [ ] **Step 2: 更新报名表粘贴文本和邮件模板**

作品名称统一为“解围——邯宝坊‘六味邯郸’机关礼盒概念提案”；说明包含 `290 × 230 × 75 mm`、六模块 `68 × 62 × 44 mm`、材料和设计边界，正文不声称品牌联名、真实 SKU 或量产。

- [ ] **Step 3: 更新总包状态**

`build_final_handoff.py` 将《解围》输出名改为 `03_赛道一_解围_待实名签字.zip`；总说明写明三件作品均需实名与本人签字，其中《解围》为概念包装提案。清单应有 3 个 `conditionally_ready`、0 个 `blocked`、其余为 `reference`。

- [ ] **Step 4: 重建全部 ZIP**

Run: `RUNTIME_PY=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3; "$RUNTIME_PY" competition_submission/build_submission_packages.py`  
Run: `RUNTIME_PY=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3; "$RUNTIME_PY" competition_submission/build_final_handoff.py`

- [ ] **Step 5: 验证压缩包、状态和哈希**

```bash
unzip -t competition_submission/packages/赛道一_解围_待填写报名表后提交.zip
unzip -t deliverables/和氏璧杯_三作品投稿与CAD交接总包_2026-10-03.zip
python3 - <<'PY'
import csv
from pathlib import Path
rows = list(csv.DictReader(Path("deliverables/final_submission_handoff/FINAL_MANIFEST.csv").open(encoding="utf-8-sig")))
assert sum(row["submission_status"] == "conditionally_ready" for row in rows) == 3
assert not any(row["submission_status"] == "blocked" for row in rows)
print("manifest status: PASS")
PY
```

Expected: 两个 ZIP 均无 CRC 错误；清单断言输出 `PASS`。

- [ ] **Step 6: 提交投稿包**

```bash
git add competition_submission deliverables/cad_models deliverables/final_submission_handoff deliverables/和氏璧杯_三作品投稿与CAD交接总包_2026-10-03.zip
git commit -m "package: upgrade Jiewei to conditionally ready submission"
```

### Task 8: 最终回归、FreeCAD 复核与 PR 更新

**Files:**
- Verify only: 全仓库与生成包

**Interfaces:**
- Consumes: Tasks 1–7 的冻结产物。
- Produces: 可追溯测试结果、最终哈希和已推送 PR 提交。

- [ ] **Step 1: 运行三件作品全部测试**

```bash
RUNTIME_PY=/Users/zzz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
"$RUNTIME_PY" -m unittest discover -s suijian_design/tests -p 'test_*.py'
"$RUNTIME_PY" -m unittest discover -s bubushengdian_design/tests -p 'test_*.py'
"$RUNTIME_PY" -m unittest discover -s jiewei_giftbox_design/tests -p 'test_*.py'
```

Expected: 三组测试全部 `OK`。

- [ ] **Step 2: 用 FreeCAD 命令行重新验证模型**

Run: `/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd deliverables/cad_models/verify_models.py`  
Expected: 退出码 0；三件 FCStd/STEP 可读。

- [ ] **Step 3: 做文件与 Git 质量检查**

```bash
git diff --check
git status --short
shasum -a 256 deliverables/和氏璧杯_三作品投稿与CAD交接总包_2026-10-03.zip
```

Expected: `git diff --check` 无输出；工作树只包含计划内生成物或已提交后为空；记录总包 SHA-256。

- [ ] **Step 4: 推送并核验 PR 头提交**

```bash
git push https://github.com/Z-lab-boop/sheji.git codex/handan-double-festival-build
git ls-remote https://github.com/Z-lab-boop/sheji.git refs/heads/codex/handan-double-festival-build
gh pr view 2 --repo Z-lab-boop/sheji --json url,state,headRefOid,mergeable
```

Expected: 远端分支 SHA 与本地 `HEAD` 一致，PR #2 保持打开。

## Plan self-review

- Spec coverage: 六味定位、统一模块、结构、写实视觉、六张展板、投稿材料、真实性边界、验证与旧版迁移均有对应任务。
- Placeholder scan: 本计划无占位标记、延后实现语句、跨任务模糊引用或未定义接口。
- Type consistency: 全链路统一使用 `PRODUCT_MODULE`、`PRODUCTS`、`CONCEPT_DISCLOSURE` 和 `conditionally_ready_pending_identity_signature`。
- Scope: 所有任务服务同一生成链和同一投稿包，不拆成独立项目。
