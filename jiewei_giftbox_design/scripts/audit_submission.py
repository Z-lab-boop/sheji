"""Audit the submission-safe Jiewei six-flavour concept package."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image

from design_config import BOARD, BOX, CONCEPT_DISCLOSURE, PRODUCT_MODULE, PRODUCTS


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "06_submission/source_manifest.csv"
REPORT_PATH = ROOT / "07_audit/audit_report.json"
MISSING_INPUTS = ["entrant_identity", "signed_registration_pdf"]
EXTERNAL_REFERENCES = [
    ("ref_competition", "https://www.zjideas.com/zjds/gycp/wcsj/32680.html", "competition requirements"),
    ("ref_idiom_hebei", "https://whly.hebei.gov.cn/c/2012-12-21/558082.html", "Handan idiom context"),
    ("ref_idiom_dictionary", "https://dict.idioms.moe.edu.tw/idiomView.jsp?ID=17170&la=0&webMd=2", "idiom meaning"),
    ("ref_hanbaofang_channels", "https://hdsswj.hd.gov.cn/gongzuodongtai/n4885.html", "Hanbaofang online sales channels"),
    ("ref_handan_categories", "https://hdsswj.hd.gov.cn/?a=view&p=5&r=3450", "six Handan regional product categories"),
    ("ref_jize_gi", "https://ipr.mofcom.gov.cn/article/gnxw/dlbz/202102/1959588.html", "Jize chili geographic product fact"),
    ("ref_weixian_standard", "https://std.samr.gov.cn/db/search/stdDBDetailed?id=2F905795AB653FA8E06397BE0A0A91D7", "Weixian pear standard fact"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def local_rows() -> list[dict[str, str]]:
    patterns = {
        "font": ["01_research/fonts/*"],
        "identity": ["02_identity/*.svg", "02_identity/*.json"],
        "cad": ["03_cad/*.FCStd", "03_cad/*.step", "03_cad/meshes/*.stl", "03_cad/cad_report.json"],
        "dieline_source": ["03_cad/dielines/*.svg", "03_cad/dielines/*.dxf", "03_cad/dielines/*.json"],
        "render": ["04_renders/*.png", "04_renders/render_manifest.json"],
        "board_source": ["05_boards/src/*.svg", "05_boards/src/*.json"],
        "board_jpg": ["05_boards/jpg/*.jpg", "05_boards/contact_sheet.jpg"],
        "board_pdf": ["05_boards/pdf/*.pdf"],
        "submission_text": ["06_submission/*.md"],
        "submission_data": ["06_submission/*.csv"],
    }
    rows = []
    seen = set()
    counter = 1
    for asset_type, globs in patterns.items():
        for pattern in globs:
            for path in sorted(ROOT.glob(pattern)):
                if not path.is_file() or path in seen:
                    continue
                seen.add(path)
                rows.append({
                    "asset_id": f"asset_{counter:03d}", "path": path.relative_to(ROOT).as_posix(), "asset_type": asset_type,
                    "creator_or_source": "Google Fonts" if asset_type == "font" else "Jiewei project",
                    "license_or_basis": "SIL OFL 1.1" if asset_type == "font" else "project original",
                    "sha256": sha256(path), "used_in": "submission concept package",
                })
                counter += 1
    for asset_id, url, purpose in EXTERNAL_REFERENCES:
        rows.append({"asset_id": asset_id, "path": url, "asset_type": "external_reference", "creator_or_source": "public webpage", "license_or_basis": "factual reference only; no embedded media", "sha256": "not-applicable-url-reference", "used_in": purpose})
    return rows


def write_manifest(rows) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["asset_id", "path", "asset_type", "creator_or_source", "license_or_basis", "sha256", "used_in"], lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def pdf_info(path: Path) -> tuple[int, str]:
    output = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True).stdout
    pages = re.search(r"^Pages:\s+(\d+)", output, re.MULTILINE)
    size = re.search(r"^Page size:\s+(.+)$", output, re.MULTILINE)
    return int(pages.group(1)) if pages else 0, size.group(1).strip() if size else "unknown"


def audit() -> dict[str, object]:
    checks = []
    def add(name, passed, detail): checks.append({"name": name, "passed": bool(passed), "detail": detail})

    jpgs = []
    for i in range(1, BOARD.count + 1):
        path = ROOT / f"05_boards/jpg/board_{i:02d}.jpg"
        if not path.exists():
            jpgs.append({"path": path.name, "exists": False}); continue
        with Image.open(path) as image:
            jpgs.append({"path": path.name, "size": list(image.size), "mode": image.mode, "dpi": round(image.info.get("dpi", (0, 0))[0]), "bytes": path.stat().st_size, "sha256": sha256(path)})
    add("submission_jpgs", len(jpgs) == 6 and all(v.get("size") == [BOARD.width_px, BOARD.height_px] and v.get("mode") == "RGB" and v.get("dpi") == 300 and int(v.get("bytes", BOARD.max_bytes)) < BOARD.max_bytes for v in jpgs), jpgs)

    pdfs = []
    for i in range(1, 7):
        path = ROOT / f"05_boards/pdf/board_{i:02d}.pdf"
        if path.exists():
            pages, size = pdf_info(path); pdfs.append({"path": path.name, "pages": pages, "page_size": size, "bytes": path.stat().st_size})
    add("a4_pdfs", len(pdfs) == 6 and all(v["pages"] == 1 and "A4" in v["page_size"] for v in pdfs), pdfs)
    svgs = sorted((ROOT / "05_boards/src").glob("board_*.svg"))
    svg_details = []
    for path in svgs:
        root = ET.parse(path).getroot()
        tags = [node.tag.rsplit("}", 1)[-1] for node in root.iter()]
        svg_details.append({"path": path.name, "elements": len(tags), "has_text": "text" in tags, "has_visual_content": "image" in tags or "path" in tags})
    add("editable_board_sources", len(svg_details) == 6 and all(v["elements"] > 20 and v["has_text"] and v["has_visual_content"] for v in svg_details), svg_details)

    render_manifest = json.loads((ROOT / "04_renders/render_manifest.json").read_text(encoding="utf-8"))
    required_renders = {
        "hero_closed.png", "hero_unlocked.png", "hero_open.png", "exploded.png", "product_family.png",
        "hand_opening.png", "retail_scene.png", "mid_autumn_variant.png", "national_day_variant.png",
    }
    add(
        "concept_renders",
        required_renders <= set(render_manifest["views"])
        and render_manifest["product_asset_status"] == "original_concept_secondary_packaging"
        and render_manifest["scene_status"] == "visualisation_not_product_photography",
        sorted(render_manifest["views"]),
    )

    step_files = sorted((ROOT / "03_cad").glob("jiewei_giftbox_*.step"))
    stls = sorted((ROOT / "03_cad/meshes").glob("*.stl"))
    exchange_ok = len(step_files) == 3 and len(stls) == 13 and all(b"ISO-10303-21" in p.read_bytes()[:256] for p in step_files)
    add("cad_exchange_files", exchange_ok, {"step": [p.name for p in step_files], "stl_count": len(stls)})
    cad = json.loads((ROOT / "03_cad/cad_report.json").read_text(encoding="utf-8"))
    parts = cad["parts"]
    add("cad_geometry", cad["closed_bbox_mm"] == [BOX.width, BOX.depth, BOX.height] and len(parts) == 13 and cad["release_margin_mm"] >= 1.0 and all(v["valid"] and v["solid_count"] == 1 for v in parts.values()), {"bbox": cad["closed_bbox_mm"], "parts": len(parts), "release_margin_mm": cad["release_margin_mm"]})

    dieline_dir = ROOT / "03_cad/dielines"
    stems = ("outer_sleeve", "wei_drawer", "zhao_tray", "lock_keys")
    dielines = [dieline_dir / f"{stem}.{ext}" for stem in stems for ext in ("svg", "dxf")]
    dieline_manifest = json.loads((dieline_dir / "dieline_manifest.json").read_text(encoding="utf-8"))
    add("dielines", all(p.is_file() and p.stat().st_size > 0 for p in dielines) and dieline_manifest["units"] == "mm" and all(v["calibration_square_mm"] == [10, 10] for v in dieline_manifest["files"].values()), [p.name for p in dielines])

    identity_manifest = json.loads((ROOT / "02_identity/identity_manifest.json").read_text(encoding="utf-8"))
    identity_text = (ROOT / "02_identity/concept_product_labels.svg").read_text(encoding="utf-8")
    board_missing = [p.name for p in svgs[3:] if CONCEPT_DISCLOSURE not in p.read_text(encoding="utf-8")]
    names_missing = [item.display_name for item in PRODUCTS if item.display_name not in identity_text]
    add(
        "concept_and_brand_disclosure",
        identity_manifest["brand_asset_status"] == "official_brief_named_target_no_logo_asset"
        and identity_manifest["product_asset_status"] == "original_concept_secondary_packaging"
        and CONCEPT_DISCLOSURE in identity_text
        and not board_missing
        and not names_missing,
        {"board_missing": board_missing, "product_names_missing": names_missing},
    )

    evidence_path = ROOT / "06_submission/concept_product_evidence.csv"
    with evidence_path.open(encoding="utf-8", newline="") as stream:
        evidence_rows = list(csv.DictReader(stream))
    add(
        "regional_category_evidence",
        len(evidence_rows) == 6
        and {row["category"] for row in evidence_rows} == {item.category for item in PRODUCTS}
        and all(row["evidence_state"] == "verified_category_only" and row["public_basis_url"].startswith("https://") for row in evidence_rows),
        evidence_rows,
    )

    licences = sorted((ROOT / "01_research/fonts").glob("OFL-*.txt"))
    add("font_licences", len(licences) == 3 and all(p.stat().st_size > 1000 for p in licences), [p.name for p in licences])

    public_files = [
        *svgs,
        *sorted((ROOT / "02_identity").glob("*.svg")),
        ROOT / "06_submission/work_description.md",
        ROOT / "06_submission/materials_and_pricing.md",
    ]
    prohibited = ["TBD", "TODO", "真实姓名待填", "热销", "已量产", "官方联名", "获得授权", "供应商报价已确认", "完成实体测试"]
    hits = []
    for path in public_files:
        content = path.read_text(encoding="utf-8", errors="ignore")
        for token in prohibited:
            if token in content: hits.append({"path": path.relative_to(ROOT).as_posix(), "token": token})
    add("prohibited_claims_and_placeholders", not hits, hits or "no prohibited public claim or identity placeholder")

    rows = local_rows(); write_manifest(rows)
    types = {row["asset_type"] for row in rows}
    needed = {"cad", "dieline_source", "render", "board_source", "board_jpg", "board_pdf", "submission_data", "external_reference"}
    add("source_manifest", needed <= types and len(rows) >= 70, {"rows": len(rows), "types": sorted(types)})

    technical_status = "pass" if all(check["passed"] for check in checks) else "fail"
    report = {
        "project": "解围——邯宝坊“六味邯郸”机关礼盒概念提案",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "technical_status": technical_status,
        "submission_status": "conditionally_ready_pending_identity_signature",
        "missing_inputs": MISSING_INPUTS,
        "checks": checks,
        "boundaries": [
            "All six visible products are original concept secondary packages based on verified regional categories.",
            "No existing Hanbaofang logo, third-party product photography, barcode, licence number, nutrition data or geographic-indication symbol is used.",
            "Module dimensions, cost and price are concept design values, not claims about existing products.",
            "Physical paperboard durability, transport performance and food compliance remain untested and are not claimed.",
            "Entrant identity and a personally signed registration PDF remain required before email submission.",
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = audit()
    print(json.dumps({"technical_status": result["technical_status"], "submission_status": result["submission_status"], "report": str(REPORT_PATH)}, ensure_ascii=False))
    sys.exit(0 if result["technical_status"] == "pass" else 1)
