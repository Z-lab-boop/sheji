"""Build the parametric Bubushengdian stamp kit with FreeCAD."""

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

from design_config import COLORS, PRODUCT, STAMP_NAMES  # noqa: E402


DOC = App.newDocument("BubushengdianStampKit")


def rounded_box(
    width: float,
    depth: float,
    height: float,
    radius: float,
    origin: App.Vector = App.Vector(0, 0, 0),
):
    """Return a rounded rectangular prism whose axes are X, Y and Z."""
    if radius <= 0 or radius * 2 >= min(width, depth):
        raise ValueError("radius must fit the XY footprint")
    x, y, z = origin.x, origin.y, origin.z
    horizontal = Part.makeBox(
        width - 2 * radius, depth, height, App.Vector(x + radius, y, z)
    )
    vertical = Part.makeBox(
        width, depth - 2 * radius, height, App.Vector(x, y + radius, z)
    )
    shape = horizontal.fuse(vertical)
    for cx, cy in (
        (x + radius, y + radius),
        (x + width - radius, y + radius),
        (x + radius, y + depth - radius),
        (x + width - radius, y + depth - radius),
    ):
        shape = shape.fuse(Part.makeCylinder(radius, height, App.Vector(cx, cy, z)))
    return shape.removeSplitter()


def make_outer_case():
    """Five-sided protective shell, open at positive X for the stamp tray."""
    outer = rounded_box(
        PRODUCT.width,
        PRODUCT.depth,
        PRODUCT.height,
        PRODUCT.corner_radius,
    )
    cavity = Part.makeBox(
        PRODUCT.width,
        PRODUCT.depth - 2 * PRODUCT.wall,
        PRODUCT.height - 2 * PRODUCT.wall,
        App.Vector(PRODUCT.wall, PRODUCT.wall, PRODUCT.wall),
    )
    shell = outer.cut(cavity)
    route_inlay = Part.makeBox(
        68.0,
        1.2,
        0.6,
        App.Vector(42.0, PRODUCT.depth - 1.0, PRODUCT.height - 8.0),
    )
    shell = shell.cut(route_inlay)
    return shell.removeSplitter()


def make_stamp_tray():
    """Connected tray base, perimeter rails and low dividers for six modules."""
    x0, y0, z0 = 55.0, 3.0, 2.3
    length, depth = 108.0, 114.0
    base = Part.makeBox(length, depth, 1.5, App.Vector(x0, y0, z0))
    rail_h, rail_t = 4.0, 1.4
    parts = [
        base,
        Part.makeBox(length, rail_t, rail_h, App.Vector(x0, y0, z0)),
        Part.makeBox(
            length,
            rail_t,
            rail_h,
            App.Vector(x0, y0 + depth - rail_t, z0),
        ),
        Part.makeBox(rail_t, depth, rail_h, App.Vector(x0, y0, z0)),
        Part.makeBox(
            rail_t,
            depth,
            rail_h,
            App.Vector(x0 + length - rail_t, y0, z0),
        ),
    ]
    for x in (89.3, 122.6):
        parts.append(Part.makeBox(1.1, 68.0, 2.4, App.Vector(x, 5.0, z0 + 1.5)))
    parts.append(Part.makeBox(99.0, 1.1, 2.4, App.Vector(58.0, 38.0, z0 + 1.5)))
    parts.append(Part.makeBox(99.0, 1.1, 2.4, App.Vector(58.0, 72.0, z0 + 1.5)))
    tray = parts[0]
    for part in parts[1:]:
        tray = tray.fuse(part)
    finger_cut = Part.makeCylinder(
        11.0,
        8.0,
        App.Vector(x0 + length + 2.0, y0 + depth / 2, z0 - 1.0),
    )
    return tray.cut(finger_cut).removeSplitter()


def make_stamp(index: int):
    """Create one rounded stamp handle with a unique tactile top marker."""
    column = index % 3
    row = index // 3
    x = 57.0 + column * 33.3
    y = 5.0 + row * 34.0
    z = 3.8
    handle = rounded_box(
        PRODUCT.stamp_width,
        PRODUCT.stamp_depth,
        PRODUCT.stamp_height,
        4.0,
        App.Vector(x, y, z),
    )
    marker_x = x + 8.0 + (index % 3) * 4.5
    marker_y = y + 8.0 + (index // 3) * 8.0
    marker = Part.makeCylinder(
        2.6,
        0.6,
        App.Vector(marker_x, marker_y, z + PRODUCT.stamp_height),
    )
    return handle.fuse(marker).removeSplitter()


def make_inkpad_case():
    return rounded_box(
        PRODUCT.inkpad_width,
        PRODUCT.inkpad_depth,
        PRODUCT.inkpad_height,
        5.0,
        App.Vector(58.0, 74.0, 3.8),
    )


def make_map_proxy():
    """Represent the 480 × 330 mm artwork in its folded storage state."""
    return rounded_box(155.0, 110.0, 1.2, 4.0, App.Vector(5.0, 5.0, 27.0))


def add_feature(name: str, label: str, shape, color: tuple[float, float, float]):
    obj = DOC.addObject("Part::Feature", name)
    obj.Label = label
    obj.Shape = shape
    obj.addProperty("App::PropertyString", "MaterialIntent", "Design")
    obj.addProperty("App::PropertyString", "ManufacturingIntent", "Design")
    if obj.ViewObject is not None:
        obj.ViewObject.ShapeColor = color
    return obj


def hex_rgb(value: str) -> tuple[float, float, float]:
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) / 255 for index in (0, 2, 4))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rounded_bbox(shape) -> list[float]:
    box = shape.BoundBox
    return [round(box.XLength, 3), round(box.YLength, 3), round(box.ZLength, 3)]


def export_part(name: str, obj) -> dict[str, object]:
    path = MESH_DIR / f"{name}.stl"
    Mesh.export([obj], str(path))
    return {
        "bbox_mm": rounded_bbox(obj.Shape),
        "volume_mm3": round(obj.Shape.Volume, 3),
        "solid_count": len(obj.Shape.Solids),
        "valid": bool(obj.Shape.isValid()),
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
        "outer_case": make_outer_case(),
        "stamp_tray": make_stamp_tray(),
        **{f"stamp_{index + 1:02d}": make_stamp(index) for index in range(6)},
        "inkpad_case": make_inkpad_case(),
        "map_proxy": make_map_proxy(),
    }
    blue = hex_rgb(COLORS["city_blue"])
    colors = {
        "outer_case": blue,
        "stamp_tray": blue,
        **{f"stamp_{index + 1:02d}": hex_rgb(COLORS["moon_paper"]) for index in range(6)},
        "inkpad_case": hex_rgb(COLORS["seal_red"]),
        "map_proxy": hex_rgb(COLORS["moon_paper"]),
    }
    labels = {
        "outer_case": "Protective outer case",
        "stamp_tray": "Sliding six-stamp tray",
        **{f"stamp_{index + 1:02d}": f"Stamp {index + 1:02d} — {STAMP_NAMES[index]}" for index in range(6)},
        "inkpad_case": "Isolated water-based ink pad case",
        "map_proxy": "Folded 480 × 330 mm route-map proxy",
    }
    objects = {
        name: add_feature(name, labels[name], shape, colors[name])
        for name, shape in shapes.items()
    }
    objects["outer_case"].MaterialIntent = "PC+ABS small-batch intent"
    objects["stamp_tray"].MaterialIntent = "PC+ABS or recycled ABS"
    for index in range(6):
        objects[f"stamp_{index + 1:02d}"].MaterialIntent = "ABS handle with replaceable rubber face"
    objects["inkpad_case"].MaterialIntent = "Standard water-based inkpad in ABS carrier"
    objects["map_proxy"].MaterialIntent = "FSC paper accordion fold"
    DOC.recompute()

    fcstd_path = CAD_DIR / "bubushengdian_stamp_kit.FCStd"
    step_path = CAD_DIR / "bubushengdian_stamp_kit.step"
    DOC.saveAs(str(fcstd_path))
    Import.export(list(objects.values()), str(step_path))
    report = {
        "document": "BubushengdianStampKit",
        "units": "mm",
        "assembly_bbox_mm": assembly_bbox(objects),
        "folded_map_proxy_mm": [155.0, 110.0, 1.2],
        "unfolded_map_artwork_mm": [480.0, 330.0],
        "parts": {name: export_part(name, obj) for name, obj in objects.items()},
        "exchange_files": {
            "fcstd_sha256": sha256(fcstd_path),
            "step_sha256": sha256(step_path),
        },
        "boundary": "Digital fit model; friction, ink contamination, child safety and durability remain unverified.",
    }
    (CAD_DIR / "cad_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "ok", "assembly_bbox_mm": report["assembly_bbox_mm"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
