#!/usr/bin/env python3
"""Validate competition boards and build clearly labelled candidate packages."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "competition_submission" / "packages"
FORM = ROOT / "competition_submission" / "forms" / "2026和氏璧杯_官方报名表_空白.doc"
MAX_BYTES = 5 * 1024 * 1024
EXPECTED_SIZE = (2480, 3508)
EXPECTED_DPI = 300


@dataclass(frozen=True)
class Project:
    slug: str
    title: str
    status: str
    board_dir: Path
    board_count: int
    description: Path
    notice: str


PROJECTS = (
    Project(
        slug="赛道二_遂见_待填写报名表后提交",
        title="遂见",
        status="conditionally_ready",
        board_dir=ROOT / "suijian_design" / "05_boards" / "jpg",
        board_count=7,
        description=ROOT / "suijian_design" / "06_submission" / "work_description.md",
        notice=(
            "这是投稿候选附件包，不是已提交证明。发送前须填写并签署官方报名表，"
            "同时保存Word版与PDF版，并由参赛者完成终稿、原创及授权条款确认。\n"
        ),
    ),
    Project(
        slug="赛道二_步步生典_待填写报名表后提交",
        title="步步生典",
        status="conditionally_ready",
        board_dir=ROOT / "bubushengdian_design" / "05_boards" / "jpg",
        board_count=8,
        description=ROOT / "bubushengdian_design" / "06_submission" / "work_description.md",
        notice=(
            "这是投稿候选附件包，不是已提交证明。发送前须填写并签署官方报名表，"
            "同时保存Word版与PDF版，并由参赛者完成终稿与授权条款确认。\n"
        ),
    ),
    Project(
        slug="赛道一_解围_禁止直接投稿_缺真实SKU与授权",
        title="解围",
        status="blocked",
        board_dir=ROOT / "jiewei_giftbox_design" / "05_boards" / "jpg",
        board_count=6,
        description=ROOT / "jiewei_giftbox_design" / "06_submission" / "work_description.md",
        notice=(
            "禁止直接投稿：当前六件内装均为中性尺寸代理。须先取得邯宝坊真实SKU、"
            "品牌书面许可、法定食品文案，重建结构与版式并完成复核。包内已附公开证据档案、"
            "商品证据表和待回填签章的申请书；空白申请书不等于已授权。\n"
        ),
    ),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_board(path: Path) -> dict:
    identify = shutil.which("identify") or shutil.which("magick")
    if not identify:
        raise RuntimeError("ImageMagick identify/magick is required to inspect JPEG metadata")
    command = [identify]
    if Path(identify).name == "magick":
        command.append("identify")
    command += ["-format", "%w|%h|%[colorspace]|%x|%y|%U|%m", str(path)]
    fields = subprocess.check_output(command, text=True).strip().split("|")
    if len(fields) != 7:
        raise RuntimeError(f"unexpected ImageMagick output for {path}")
    width, height, colorspace, x_dpi, y_dpi, units, image_format = fields
    size = (int(width), int(height))
    mode = "RGB" if colorspace.lower() in {"rgb", "srgb"} else colorspace
    dpi = (round(float(x_dpi)), round(float(y_dpi)))
    checks = {
        "size": size == EXPECTED_SIZE,
        "mode": mode == "RGB",
        "dpi": dpi == (EXPECTED_DPI, EXPECTED_DPI),
        "format": image_format == "JPEG" and path.suffix.lower() in {".jpg", ".jpeg"},
        "units": units == "PixelsPerInch",
        "max_bytes": path.stat().st_size <= MAX_BYTES,
    }
    return {
        "file": path.name,
        "size": list(size),
        "mode": mode,
        "dpi": list(dpi),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "checks": checks,
        "passed": all(checks.values()),
    }


def write_deterministic_zip(source_dir: Path, target: Path) -> None:
    fixed_time = (2026, 10, 2, 0, 0, 0)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in sorted(p for p in source_dir.rglob("*") if p.is_file()):
            relative = source.relative_to(source_dir)
            info = zipfile.ZipInfo(str(relative), fixed_time)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, source.read_bytes())


def build_project(project: Project) -> tuple[dict, Path]:
    boards = sorted(project.board_dir.glob("board_*.jpg"))
    if len(boards) != project.board_count:
        raise RuntimeError(f"{project.title}: expected {project.board_count} boards, found {len(boards)}")
    results = [validate_board(path) for path in boards]
    if not all(item["passed"] for item in results):
        raise RuntimeError(f"{project.title}: board validation failed")

    target_dir = OUT / project.slug
    target_dir.mkdir(parents=True, exist_ok=True)
    for old in target_dir.iterdir():
        if old.is_file():
            old.unlink()
        elif old.is_dir():
            shutil.rmtree(old)

    for index, board in enumerate(boards, 1):
        shutil.copy2(board, target_dir / f"{project.title}_{index:02d}.jpg")
    shutil.copy2(project.description, target_dir / f"{project.title}_作品说明.md")
    shutil.copy2(
        ROOT / "competition_submission" / "form_fill_text.md",
        target_dir / "官方报名表_作品说明粘贴文本.md",
    )
    shutil.copy2(
        ROOT / "competition_submission" / "email_templates.md",
        target_dir / "投稿邮件模板_未发送.md",
    )
    if project.title == "步步生典":
        shutil.copy2(
            ROOT / "competition_submission" / "route_verification_2026-10-02.md",
            target_dir / "步步生典_文化节点复核.md",
        )
    if project.title == "解围":
        coordination_dir = ROOT / "jiewei_giftbox_design" / "06_submission"
        shutil.copy2(
            coordination_dir / "hanbaofang_public_product_dossier.md",
            target_dir / "邯宝坊商品公开证据档案.md",
        )
        shutil.copy2(
            coordination_dir / "hanbaofang_product_evidence.csv",
            target_dir / "邯宝坊商品证据表.csv",
        )
        shutil.copy2(
            coordination_dir / "邯宝坊产品资料与参赛授权申请书.docx",
            target_dir / "邯宝坊产品资料与参赛授权申请书_待回填签章.docx",
        )
    shutil.copy2(FORM, target_dir / "官方报名表_空白_须填写签字并另存PDF.doc")
    (target_dir / "提交状态_请先阅读.txt").write_text(project.notice, encoding="utf-8")

    zip_path = OUT / f"{project.slug}.zip"
    write_deterministic_zip(target_dir, zip_path)
    return {
        "project": project.title,
        "status": project.status,
        "board_count": len(results),
        "boards": results,
        "package": zip_path.name,
        "package_sha256": sha256(zip_path),
    }, zip_path


def main() -> int:
    if not FORM.exists():
        raise FileNotFoundError(FORM)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    reports = []
    zip_paths = []
    for project in PROJECTS:
        report, zip_path = build_project(project)
        reports.append(report)
        zip_paths.append(zip_path)

    audit = {
        "competition": "2026和氏璧杯成语之都大学生创意奖",
        "rules_verified_on": "2026-10-02",
        "requirements": {
            "page": "A4 portrait",
            "pixels": list(EXPECTED_SIZE),
            "dpi": EXPECTED_DPI,
            "mode": "RGB",
            "format": "JPG",
            "max_bytes_per_image": MAX_BYTES,
        },
        "projects": reports,
        "overall_status": "conditionally_ready_two_projects_and_one_blocked_project",
    }
    (OUT / "audit_report.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    with (OUT / "PACKAGE_MANIFEST.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["file", "sha256", "bytes"])
        for path in zip_paths:
            writer.writerow([path.name, sha256(path), path.stat().st_size])

    (OUT / "SHA256SUMS.txt").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in zip_paths), encoding="utf-8"
    )
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
