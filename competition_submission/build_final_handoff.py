#!/usr/bin/env python3
"""Build three submission handoff packages and the complete CAD/model archive."""

from __future__ import annotations

import csv
import hashlib
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUBMISSION_PACKAGES = ROOT / "competition_submission" / "packages"
CAD_PACKAGES = ROOT / "deliverables" / "cad_models"
HANDOFF_DIR = ROOT / "deliverables" / "final_submission_handoff"
HANDOFF_ZIP = ROOT / "deliverables" / "和氏璧杯_三作品投稿与CAD交接总包_2026-10-03.zip"
FIXED_TIME = (2026, 10, 3, 0, 0, 0)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_zip(target: Path, files: list[tuple[Path, Path]]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source, archive_path in sorted(files, key=lambda item: item[1].as_posix()):
            info = zipfile.ZipInfo(archive_path.as_posix(), FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, source.read_bytes())


def collect_tree(path: Path, archive_root: Path) -> list[tuple[Path, Path]]:
    return [
        (source, archive_root / source.relative_to(path))
        for source in sorted(path.rglob("*"))
        if source.is_file()
    ]


def build_cad_package(project_name: str, target_name: str, render_names: tuple[str, ...]) -> Path:
    project = ROOT / project_name
    files: list[tuple[Path, Path]] = [
        (project / "README.md", Path(project_name) / "README.md"),
        (project / "scripts/design_config.py", Path(project_name) / "scripts/design_config.py"),
        (CAD_PACKAGES / "README.md", Path("deliverables/cad_models/README.md")),
        (CAD_PACKAGES / "verify_models.py", Path("deliverables/cad_models/verify_models.py")),
    ]
    files.extend(collect_tree(project / "03_cad", Path(project_name) / "03_cad"))
    for name in render_names:
        source = project / "04_renders" / name
        files.append((source, Path(project_name) / "04_renders" / name))
    target = CAD_PACKAGES / target_name
    write_zip(target, files)
    return target


def update_cad_hashes(cad_paths: list[Path]) -> None:
    content = "".join(f"{sha256(path)}  {path.name}\n" for path in cad_paths)
    (CAD_PACKAGES / "SHA256SUMS.txt").write_text(content, encoding="utf-8")


def build_handoff() -> tuple[Path, Path]:
    cad_paths = [
        build_cad_package(
            "suijian_design",
            "00_suijian_card_case_cad_model.zip",
            ("hero_closed.png", "hero_open.png", "exploded.png", "scale_view.png"),
        ),
        build_cad_package(
            "bubushengdian_design",
            "01_bubushengdian_stamp_kit_cad_model.zip",
            ("hero_closed.png", "hero_open.png", "exploded.png", "ortho_top.png", "scale_view.png"),
        ),
        build_cad_package(
            "jiewei_giftbox_design",
            "02_jiewei_giftbox_cad_model.zip",
            (
                "hero_closed.png",
                "hero_unlocked.png",
                "hero_open.png",
                "exploded.png",
                "ortho_top.png",
                "dieline_preview.png",
                "product_family.png",
                "hand_opening.png",
                "retail_scene.png",
            ),
        ),
    ]
    update_cad_hashes(cad_paths)

    if HANDOFF_DIR.exists():
        shutil.rmtree(HANDOFF_DIR)
    (HANDOFF_DIR / "CAD与模型备查").mkdir(parents=True)

    submission_sources = [
        (
            SUBMISSION_PACKAGES / "赛道二_遂见_待填写报名表后提交.zip",
            HANDOFF_DIR / "01_赛道二_遂见_待实名签字.zip",
        ),
        (
            SUBMISSION_PACKAGES / "赛道二_步步生典_待填写报名表后提交.zip",
            HANDOFF_DIR / "02_赛道二_步步生典_待实名签字.zip",
        ),
        (
            SUBMISSION_PACKAGES / "赛道一_解围_待填写报名表后提交.zip",
            HANDOFF_DIR / "03_赛道一_解围_待实名签字.zip",
        ),
    ]
    for source, target in submission_sources:
        shutil.copy2(source, target)
    for source in cad_paths:
        shutil.copy2(source, HANDOFF_DIR / "CAD与模型备查" / source.name)
    for source in (
        CAD_PACKAGES / "和氏璧杯_CAD与模型详细说明书.docx",
        ROOT / "output" / "pdf" / "和氏璧杯_CAD与模型详细说明书.pdf",
    ):
        shutil.copy2(source, HANDOFF_DIR / "CAD与模型备查" / source.name)

    status = """2026“和氏璧杯”三作品投稿交接说明

一、三件作品均可进入实名签字环节
1. 《遂见》：7张A4 JPG已通过像素、RGB、300dpi和单张小于5MB检查。
2. 《步步生典》：8张A4 JPG已通过同项检查，文化节点公开来源已复核。
3. 《解围》：6张A4 JPG已通过同项检查，定位为面向邯宝坊命题的原创“六味邯郸”概念二次包装系统。
4. 《遂见》和《步步生典》分别投稿至赛道二邮箱 1513538702@qq.com；《解围》投稿至赛道一邮箱 198233612@qq.com。每件作品单独发送一封邮件。

发送前必须由参赛者完成：
- 在各自压缩包内的官方报名表填写真实姓名、身份证号、手机、邮箱、学校/单位、作者顺序和指导教师（如有）。
- 亲自核对原创、知识产权及组委会授权条款并签字。
- 同时保留填写后的Word版和签字PDF版。
- 解压对应投稿包；邮件仅附报名表Word、签字PDF和该作品的JPG，不附CAD备查包。
- 邮件主题使用“真实姓名+学校（单位）+手机”。

二、《解围》的概念边界
《解围》不宣称使用任何真实在售SKU，也未使用邯宝坊Logo、现售商品图、条码、许可证或法定食品文案。六个68×62×44毫米模块是基于邯郸公开地域品类设计的原创概念二次包装，不代表已获品牌联名授权或已实现量产。报名表中应保留这一口径。

三、CAD与模型
“CAD与模型备查”仅用于保留可编辑源文件及入围后的模型/打样准备，初审邮件不要求附带。FCStd用于FreeCAD编辑，STEP用于跨软件交换，STL用于3D打印，DXF/SVG用于《解围》包装刀模。

当前状态：三件作品均为“有条件可提交”，共同缺参赛者真实身份、签名和已填写的官方报名表。任何空白报名表、自动审计通过或压缩包生成均不等于已经正式投稿。
"""
    (HANDOFF_DIR / "提交前总说明_请先阅读.txt").write_text(status, encoding="utf-8")

    files = sorted(path for path in HANDOFF_DIR.rglob("*") if path.is_file())
    with (HANDOFF_DIR / "FINAL_MANIFEST.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["relative_path", "sha256", "bytes", "submission_status"])
        for path in files:
            relative = path.relative_to(HANDOFF_DIR).as_posix()
            if path.parent == HANDOFF_DIR and path.suffix == ".zip":
                status_label = "conditionally_ready"
            else:
                status_label = "reference"
            writer.writerow([relative, sha256(path), path.stat().st_size, status_label])

    files = sorted(path for path in HANDOFF_DIR.rglob("*") if path.is_file())
    (HANDOFF_DIR / "SHA256SUMS.txt").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(HANDOFF_DIR).as_posix()}\n" for path in files),
        encoding="utf-8",
    )
    files = sorted(path for path in HANDOFF_DIR.rglob("*") if path.is_file())
    write_zip(HANDOFF_ZIP, [(path, path.relative_to(HANDOFF_DIR)) for path in files])
    return HANDOFF_DIR, HANDOFF_ZIP


if __name__ == "__main__":
    directory, archive = build_handoff()
    print(directory)
    print(archive)
