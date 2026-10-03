"""Build the source manifest and audit the Bubushengdian submission package."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

from design_config import BOARD, PRODUCT


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "06_submission/source_manifest.csv"
REPORT_PATH = ROOT / "07_audit/audit_report.json"

EXTERNAL_REFERENCES = [
    ("ref_competition", "https://www.zjideas.com/zjds/gycp/wcsj/32680.html", "competition requirements"),
    ("ref_idiom", "https://whly.hebei.gov.cn/c/2012-12-21/558082.html", "cultural fact"),
    ("ref_route", "https://whly.hebei.gov.cn/c/2025-05-19/580864.html", "cultural-tourism context"),
    ("ref_holiday", "https://whly.hebei.gov.cn/c/2024-10-10/578473.html", "holiday scenario context"),
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
        "cad": ["03_cad/*.FCStd", "03_cad/*.step", "03_cad/meshes/*.stl", "03_cad/*.json"],
        "render": ["04_renders/*.png", "04_renders/render_manifest.json"],
        "board_source": ["05_boards/src/*.svg", "05_boards/src/*.json"],
        "board_jpg": ["05_boards/jpg/*.jpg", "05_boards/contact_sheet.jpg"],
        "board_pdf": ["05_boards/pdf/*.pdf"],
        "submission_text": ["06_submission/*.md"],
    }
    rows: list[dict[str, str]] = []
    seen: set[Path] = set()
    counter = 1
    for asset_type, globs in patterns.items():
        for pattern in globs:
            for path in sorted(ROOT.glob(pattern)):
                if not path.is_file() or path in seen:
                    continue
                seen.add(path)
                rows.append(
                    {
                        "asset_id": f"asset_{counter:03d}",
                        "path": path.relative_to(ROOT).as_posix(),
                        "asset_type": asset_type,
                        "creator_or_source": "Google Fonts" if asset_type == "font" else "Bubushengdian project",
                        "license_or_basis": "SIL OFL 1.1" if asset_type == "font" else "project original",
                        "sha256": sha256(path),
                        "used_in": "submission package",
                    }
                )
                counter += 1
    for asset_id, url, purpose in EXTERNAL_REFERENCES:
        rows.append(
            {
                "asset_id": asset_id,
                "path": url,
                "asset_type": "external_reference",
                "creator_or_source": "public webpage",
                "license_or_basis": "factual reference only; no embedded media",
                "sha256": "not-applicable-url-reference",
                "used_in": purpose,
            }
        )
    return rows


def write_manifest(rows: list[dict[str, str]]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["asset_id", "path", "asset_type", "creator_or_source", "license_or_basis", "sha256", "used_in"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def pdf_page_size(path: Path) -> tuple[int, str]:
    completed = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True)
    pages = re.search(r"^Pages:\s+(\d+)", completed.stdout, re.MULTILINE)
    size = re.search(r"^Page size:\s+(.+)$", completed.stdout, re.MULTILINE)
    return int(pages.group(1)) if pages else 0, size.group(1).strip() if size else "unknown"


def audit() -> dict[str, object]:
    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    jpg_details: list[dict[str, object]] = []
    for index in range(1, BOARD.count + 1):
        path = ROOT / f"05_boards/jpg/board_{index:02d}.jpg"
        if not path.exists():
            jpg_details.append({"path": path.name, "exists": False})
            continue
        with Image.open(path) as image:
            jpg_details.append(
                {
                    "path": path.name,
                    "size": list(image.size),
                    "mode": image.mode,
                    "dpi": round(image.info.get("dpi", (0, 0))[0]),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
    add(
        "submission_jpgs",
        len(jpg_details) == BOARD.count
        and all(
            item.get("size") == [BOARD.width_px, BOARD.height_px]
            and item.get("mode") == "RGB"
            and item.get("dpi") == BOARD.dpi
            and int(item.get("bytes", BOARD.max_bytes)) < BOARD.max_bytes
            for item in jpg_details
        ),
        jpg_details,
    )

    pdf_details: list[dict[str, object]] = []
    for index in range(1, BOARD.count + 1):
        path = ROOT / f"05_boards/pdf/board_{index:02d}.pdf"
        if path.exists():
            pages, size = pdf_page_size(path)
            pdf_details.append({"path": path.name, "pages": pages, "page_size": size, "bytes": path.stat().st_size})
    add(
        "a4_pdfs",
        len(pdf_details) == BOARD.count and all(item["pages"] == 1 and "A4" in str(item["page_size"]) for item in pdf_details),
        pdf_details,
    )

    editables = [
        ROOT / "03_cad/bubushengdian_stamp_kit.FCStd",
        ROOT / "03_cad/bubushengdian_stamp_kit.step",
        *sorted((ROOT / "03_cad/meshes").glob("*.stl")),
        *sorted((ROOT / "02_identity").glob("*.svg")),
        *sorted((ROOT / "05_boards/src").glob("board_*.svg")),
    ]
    add(
        "editable_sources",
        len(editables) == 23 and all(path.is_file() and path.stat().st_size > 0 for path in editables),
        [path.relative_to(ROOT).as_posix() for path in editables],
    )

    fcstd = ROOT / "03_cad/bubushengdian_stamp_kit.FCStd"
    step = ROOT / "03_cad/bubushengdian_stamp_kit.step"
    exchange_ok = fcstd.read_bytes()[:2] == b"PK" and b"ISO-10303-21" in step.read_bytes()[:256]
    add("exchange_file_signatures", exchange_ok, {"fcstd": "ZIP/OpenDocument", "step": "ISO-10303-21"})

    cad_report = json.loads((ROOT / "03_cad/cad_report.json").read_text(encoding="utf-8"))
    parts = cad_report["parts"]
    cad_ok = (
        cad_report["assembly_bbox_mm"] == [PRODUCT.width, PRODUCT.depth, PRODUCT.height]
        and len(parts) == 10
        and all(part["valid"] and part["solid_count"] == 1 for part in parts.values())
    )
    add("cad_geometry", cad_ok, {"bbox_mm": cad_report["assembly_bbox_mm"], "parts": list(parts)})

    render_manifest = json.loads((ROOT / "04_renders/render_manifest.json").read_text(encoding="utf-8"))
    render_hashes = render_manifest.get("cad_mesh_sha256", {})
    hash_ok = len(render_hashes) == 10 and all(render_hashes.get(name) == part["sha256"] for name, part in parts.items())
    add("render_geometry_traceability", hash_ok, {"geometry_basis": render_manifest.get("geometry_basis"), "mesh_count": len(render_hashes)})

    public_files = [
        *sorted((ROOT / "02_identity").glob("*.svg")),
        *sorted((ROOT / "05_boards/src").glob("*.svg")),
        ROOT / "06_submission/work_description.md",
        ROOT / "06_submission/materials_and_pricing.md",
    ]
    forbidden = ["手机号", "身份证", "真实姓名待填", "TBD", "TODO"]
    hits: list[dict[str, str]] = []
    for path in public_files:
        content = path.read_text(encoding="utf-8", errors="ignore")
        for token in forbidden:
            if token in content:
                hits.append({"path": path.relative_to(ROOT).as_posix(), "token": token})
    add("privacy_tokens", not hits, hits or "no prohibited identity placeholders")

    disclaimer_files = [ROOT / "02_identity/folding_map.svg", ROOT / "05_boards/src/board_02.svg", ROOT / "05_boards/src/board_08.svg"]
    missing_disclaimers = [path.relative_to(ROOT).as_posix() for path in disclaimer_files if "文化路线示意" not in path.read_text(encoding="utf-8")]
    add("route_disclaimer", not missing_disclaimers, missing_disclaimers or "present in map and disclosure boards")

    rows = local_rows()
    write_manifest(rows)
    manifest_types = {row["asset_type"] for row in rows}
    required_types = {"cad", "render", "board_source", "board_jpg", "board_pdf", "external_reference"}
    add("source_manifest", required_types <= manifest_types and len(rows) >= 60, {"rows": len(rows), "types": sorted(manifest_types)})

    technical_status = "pass" if all(check["passed"] for check in checks) else "fail"
    report = {
        "project": "步步生典——邯郸双节漫游章匣",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "technical_status": technical_status,
        "submission_status": "candidate_pending_human_route_review",
        "checks": checks,
        "boundaries": [
            "文化路线为示意，动态景点信息和准确游线须由真人复核。",
            "尚未制作或测试实物，数字几何不等同量产验证。",
            "价格为设计估算，并非供应商报价或真实销售数据。",
            "参赛者身份与主办方最终规则须在投稿前人工确认。",
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = audit()
    print(json.dumps({"technical_status": result["technical_status"], "report": str(REPORT_PATH)}, ensure_ascii=False))
    sys.exit(0 if result["technical_status"] == "pass" else 1)
