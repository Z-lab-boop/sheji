"""Build the parametric Suijian card case and exchange files with FreeCAD."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import FreeCAD as App
import Import
import Mesh
import Part


CAD_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CAD_DIR.parent
SCRIPT_DIR = PROJECT_DIR / "scripts"
MESH_DIR = CAD_DIR / "meshes"
sys.path.insert(0, str(SCRIPT_DIR))

from design_config import PRODUCT


DOC = App.newDocument("SuijianCardCase")


def rounded_box(
    width: float,
    height: float,
    depth: float,
    radius: float,
    origin: App.Vector = App.Vector(0, 0, 0),
):
    """Return a rounded rectangular prism with planar top and bottom."""
    if radius <= 0 or radius * 2 >= min(width, height):
        raise ValueError("radius must fit width and height")
    x, y, z = origin.x, origin.y, origin.z
    horizontal = Part.makeBox(width - 2 * radius, height, depth, App.Vector(x + radius, y, z))
    vertical = Part.makeBox(width, height - 2 * radius, depth, App.Vector(x, y + radius, z))
    shape = horizontal.fuse(vertical)
    for cx, cy in (
        (x + radius, y + radius),
        (x + width - radius, y + radius),
        (x + radius, y + height - radius),
        (x + width - radius, y + height - radius),
    ):
        shape = shape.fuse(Part.makeCylinder(radius, depth, App.Vector(cx, cy, z)))
    return shape.removeSplitter()


def make_outer_shell(spec):
    """Create a five-sided rounded sleeve open at the positive-X edge."""
    outer = rounded_box(spec.width, spec.height, spec.depth, spec.corner_radius)
    cavity = Part.makeBox(
        spec.width,
        spec.height - 2 * spec.wall,
        spec.depth - 2 * spec.wall,
        App.Vector(spec.wall, spec.wall, spec.wall),
    )
    shell = outer.cut(cavity)

    # Nine shallow marks leave 1.35 mm of the 1.8 mm side wall intact.
    for index in range(9):
        mark = Part.makeBox(
            2.2,
            0.55,
            1.4,
            App.Vector(24.0 + index * 5.2, -0.05, 6.3),
        )
        shell = shell.cut(mark)
    return shell.removeSplitter()


def make_inner_tray(spec):
    """Create a low-friction card tray with side rails and a closed back stop."""
    x0 = spec.wall + spec.clearance
    y0 = spec.wall + spec.clearance
    z0 = spec.wall + spec.clearance
    tray_length = spec.width - spec.wall - 2 * spec.clearance
    tray_width = spec.height - 2 * (spec.wall + spec.clearance)
    base = Part.makeBox(tray_length, tray_width, 1.2, App.Vector(x0, y0, z0))
    rail_h = 2.8
    rail_w = 1.15
    left = Part.makeBox(tray_length, rail_w, rail_h, App.Vector(x0, y0, z0))
    right = Part.makeBox(
        tray_length,
        rail_w,
        rail_h,
        App.Vector(x0, y0 + tray_width - rail_w, z0),
    )
    back = Part.makeBox(1.2, tray_width, rail_h, App.Vector(x0, y0, z0))
    thumb_notch = Part.makeCylinder(
        9.5,
        2.2,
        App.Vector(spec.width - 4.0, spec.height / 2, z0 - 0.5),
        App.Vector(0, 0, 1),
    )
    return base.fuse(left).fuse(right).fuse(back).cut(thumb_notch).removeSplitter()


def make_lifter(spec):
    """Create the 18 mm wedge that produces the seven-millimetre card rise."""
    run = 18.0
    width = spec.card_height - 4.0
    points = [
        App.Vector(0, 0, 0),
        App.Vector(run, 0, 0),
        App.Vector(run, 0, spec.lift),
        App.Vector(0, 0, 0),
    ]
    wedge = Part.Face(Part.makePolygon(points)).extrude(App.Vector(0, width, 0))
    wedge.translate(App.Vector(spec.width - run - 3.0, (spec.height - width) / 2, 3.0))
    return wedge.removeSplitter()


def make_gold_accent(spec):
    """Create a clipped 17-degree metal accent set flush with the top face."""
    bar = Part.makeBox(76.0, 2.0, 0.55, App.Vector(11.0, 31.5, spec.depth - 0.55))
    bar.rotate(App.Vector(spec.width / 2, spec.height / 2, 0), App.Vector(0, 0, 1), 17.0)
    clip = Part.makeBox(
        spec.width - 4.0,
        spec.height - 4.0,
        0.55,
        App.Vector(2.0, 2.0, spec.depth - 0.55),
    )
    return bar.common(clip).removeSplitter()


def make_card_proxy(spec):
    """Create a standard-size paper card used for fit and presentation checks."""
    return Part.makeBox(
        spec.card_width,
        spec.card_height,
        spec.card_thickness,
        App.Vector(4.0, (spec.height - spec.card_height) / 2, 5.1),
    )


def add_feature(name: str, label: str, shape, color: tuple[float, float, float]):
    obj = DOC.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape
    obj.addProperty("App::PropertyString", "MaterialIntent", "Design")
    obj.addProperty("App::PropertyString", "ManufacturingIntent", "Design")
    if obj.ViewObject is not None:
        obj.ViewObject.ShapeColor = color
    return obj


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rounded_bbox(shape) -> list[float]:
    box = shape.BoundBox
    return [round(box.XLength, 3), round(box.YLength, 3), round(box.ZLength, 3)]


def export_part(name: str, obj) -> dict:
    """Export one STL and return deterministic audit metadata."""
    path = MESH_DIR / f"{name}.stl"
    Mesh.export([obj], str(path))
    return {
        "bbox_mm": rounded_bbox(obj.Shape),
        "volume_mm3": round(obj.Shape.Volume, 3),
        "solid_count": len(obj.Shape.Solids),
        "valid": bool(obj.Shape.isValid()),
        "manifold_expected": len(obj.Shape.Solids) == 1 and obj.Shape.isValid(),
        "sha256": sha256(path),
    }


def assembly_bbox(objects: dict[str, object]) -> list[float]:
    boxes = [obj.Shape.BoundBox for obj in objects.values()]
    x_min = min(box.XMin for box in boxes)
    y_min = min(box.YMin for box in boxes)
    z_min = min(box.ZMin for box in boxes)
    x_max = max(box.XMax for box in boxes)
    y_max = max(box.YMax for box in boxes)
    z_max = max(box.ZMax for box in boxes)
    return [round(x_max - x_min, 3), round(y_max - y_min, 3), round(z_max - z_min, 3)]


def main() -> None:
    CAD_DIR.mkdir(parents=True, exist_ok=True)
    MESH_DIR.mkdir(parents=True, exist_ok=True)

    shapes = {
        "outer_shell": make_outer_shell(PRODUCT),
        "inner_tray": make_inner_tray(PRODUCT),
        "lifter": make_lifter(PRODUCT),
        "gold_accent": make_gold_accent(PRODUCT),
        "card_proxy": make_card_proxy(PRODUCT),
    }
    appearances = {
        "outer_shell": (0.051, 0.184, 0.196),
        "inner_tray": (0.051, 0.184, 0.196),
        "lifter": (0.714, 0.545, 0.282),
        "gold_accent": (0.714, 0.545, 0.282),
        "card_proxy": (0.910, 0.875, 0.800),
    }
    labels = {
        "outer_shell": "Outer Shell — PC+ABS intent",
        "inner_tray": "Sliding Tray — PC+ABS intent",
        "lifter": "Lift Wedge — POM intent",
        "gold_accent": "17 degree Accent — anodised aluminium intent",
        "card_proxy": "90 × 54 mm Card Fit Proxy",
    }
    objects = {
        name: add_feature(name, labels[name], shape, appearances[name])
        for name, shape in shapes.items()
    }
    objects["outer_shell"].MaterialIntent = "PC+ABS, matte lacquer green"
    objects["outer_shell"].ManufacturingIntent = "Injection moulding; prototype by resin/FDM print"
    objects["inner_tray"].MaterialIntent = "PC+ABS"
    objects["lifter"].MaterialIntent = "POM low-friction wedge"
    objects["gold_accent"].MaterialIntent = "Anodised aluminium or painted resin prototype"
    objects["card_proxy"].MaterialIntent = "300–350 gsm paper"

    DOC.recompute()
    fcstd_path = CAD_DIR / "suijian_card_case.FCStd"
    step_path = CAD_DIR / "suijian_card_case.step"
    DOC.saveAs(str(fcstd_path))
    Import.export(list(objects.values()), str(step_path))

    report = {
        "document": "SuijianCardCase",
        "units": "mm",
        "design_baseline": {
            "width": PRODUCT.width,
            "height": PRODUCT.height,
            "depth": PRODUCT.depth,
            "wall": PRODUCT.wall,
            "clearance": PRODUCT.clearance,
            "travel": PRODUCT.travel,
            "lift": PRODUCT.lift,
        },
        "assembly_bbox_mm": assembly_bbox(objects),
        "parts": {name: export_part(name, obj) for name, obj in objects.items()},
        "exchange_files": {
            "fcstd_sha256": sha256(fcstd_path),
            "step_sha256": sha256(step_path),
        },
        "boundary": "Prototype geometry; not a production tolerance or supplier-validated design.",
    }
    (CAD_DIR / "cad_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "ok", "assembly_bbox_mm": report["assembly_bbox_mm"]}))


if __name__ == "__main__":
    main()
