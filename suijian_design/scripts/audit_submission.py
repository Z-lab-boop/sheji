"""Build the source manifest and audit the complete Suijian submission package."""

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
    ("ref_competition", "https://zjideas.com/zjds/gycp/wcsj/32680.html", "competition requirements"),
    ("ref_maosui", "https://whly.hebei.gov.cn/c/2012-12-21/558082.html", "cultural fact"),
    ("ref_story_chain", "https://www.ccdi.gov.cn/zlhjn/202008/t20200821_17288.html", "cultural fact"),
    ("ref_market_context", "https://whly.hebei.gov.cn/c/2025-05-19/580864.html", "context only"),
    ("ref_award_context", "https://www.shejijingsai.com/2025/09/1433609.html", "context only"),
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
                if not path.is_file() or path in seen or path.name.startswith("proof"):
                    continue
                seen.add(path)
                basis = "project original"
                if asset_type == "font":
                    basis = "SIL OFL 1.1"
                rows.append(
                    {
                        "asset_id": f"asset_{counter:03d}",
                        "path": path.relative_to(ROOT).as_posix(),
                        "asset_type": asset_type,
                        "creator_or_source": "Suijian project" if asset_type != "font" else "Google Fonts",
                        "license_or_basis": basis,
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
            fieldnames=[
                "asset_id",
                "path",
                "asset_type",
                "creator_or_source",
                "license_or_basis",
                "sha256",
                "used_in",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def pdf_page_size(path: Path) -> tuple[int, str]:
    completed = subprocess.run(
        ["pdfinfo", str(path)], check=True, capture_output=True, text=True
    )
    pages = re.search(r"^Pages:\s+(\d+)", completed.stdout, re.MULTILINE)
    size = re.search(r"^Page size:\s+(.+)$", completed.stdout, re.MULTILINE)
    return int(pages.group(1)) if pages else 0, size.group(1).strip() if size else "unknown"


def audit() -> dict[str, object]:
    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    jpg_details = []
    for index in range(1, BOARD.count + 1):
        path = ROOT / f"05_boards/jpg/board_{index:02d}.jpg"
        if not path.exists():
            jpg_details.append({"path": path.name, "exists": False})
            continue
        with Image.open(path) as image:
            dpi = round(image.info.get("dpi", (0, 0))[0])
            jpg_details.append(
                {
                    "path": path.name,
                    "size": list(image.size),
                    "mode": image.mode,
                    "dpi": dpi,
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
    jpg_ok = len(jpg_details) == BOARD.count and all(
        item.get("size") == [BOARD.width_px, BOARD.height_px]
        and item.get("mode") == "RGB"
        and item.get("dpi") == BOARD.dpi
        and int(item.get("bytes", BOARD.max_bytes)) < BOARD.max_bytes
        for item in jpg_details
    )
    add("submission_jpgs", jpg_ok, jpg_details)

    pdf_details = []
    for index in range(1, BOARD.count + 1):
        path = ROOT / f"05_boards/pdf/board_{index:02d}.pdf"
        if path.exists():
            pages, size = pdf_page_size(path)
            pdf_details.append({"path": path.name, "pages": pages, "page_size": size, "bytes": path.stat().st_size})
    add(
        "a4_pdfs",
        len(pdf_details) == BOARD.count
        and all(item["pages"] == 1 and "A4" in str(item["page_size"]) for item in pdf_details),
        pdf_details,
    )

    required_editables = [
        ROOT / "03_cad/suijian_card_case.FCStd",
        ROOT / "03_cad/suijian_card_case.step",
        *sorted((ROOT / "03_cad/meshes").glob("*.stl")),
        *sorted((ROOT / "02_identity").glob("*.svg")),
        *sorted((ROOT / "05_boards/src").glob("board_*.svg")),
    ]
    add(
        "editable_sources",
        len(required_editables) == 18 and all(path.is_file() and path.stat().st_size > 0 for path in required_editables),
        [path.relative_to(ROOT).as_posix() for path in required_editables],
    )

    cad_report = json.loads((ROOT / "03_cad/cad_report.json").read_text(encoding="utf-8"))
    parts = cad_report["parts"]
    cad_ok = (
        cad_report["assembly_bbox_mm"] == [PRODUCT.width, PRODUCT.height, PRODUCT.depth]
        and len(parts) == 5
        and all(part["valid"] and part["solid_count"] == 1 for part in parts.values())
    )
    add("cad_geometry", cad_ok, {"bbox_mm": cad_report["assembly_bbox_mm"], "parts": list(parts)})

    public_text_files = [
        *sorted((ROOT / "02_identity").glob("*.svg")),
        *sorted((ROOT / "05_boards/src").glob("*.svg")),
        ROOT / "06_submission/work_description.md",
        ROOT / "06_submission/materials_and_pricing.md",
    ]
    forbidden = ["手机号", "身份证", "真实姓名待填", "TBD", "TODO"]
    hits: list[dict[str, str]] = []
    for path in public_text_files:
        content = path.read_text(encoding="utf-8", errors="ignore")
        for token in forbidden:
            if token in content:
                hits.append({"path": path.relative_to(ROOT).as_posix(), "token": token})
    add("privacy_tokens", not hits, hits or "no prohibited identity placeholders")

    rows = local_rows()
    write_manifest(rows)
    manifest_types = {row["asset_type"] for row in rows}
    expected_types = {"font", "identity", "cad", "render", "board_source", "board_jpg", "board_pdf", "submission_text", "external_reference"}
    add("source_manifest", expected_types <= manifest_types and len(rows) >= 50, {"rows": len(rows), "types": sorted(manifest_types)})

    report = {
        "project": "遂见——毛遂自荐青年名片匣",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if all(check["passed"] for check in checks) else "fail",
        "checks": checks,
        "boundaries": [
            "No physical prototype has been fabricated or tested.",
            "Pricing is an estimate, not a supplier quotation.",
            "Final entrant identity and organiser rules require human confirmation before submission.",
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = audit()
    print(json.dumps({"status": result["status"], "report": str(REPORT_PATH)}, ensure_ascii=False))
    sys.exit(0 if result["status"] == "pass" else 1)
