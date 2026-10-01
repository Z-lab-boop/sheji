"""Build the three-state Jiewei paperboard mechanism with FreeCAD."""

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
MESH_DIR = CAD_DIR / "meshes"
sys.path.insert(0, str(PROJECT_DIR / "scripts"))

from design_config import BOX, COLORS, SKU, state_offsets  # noqa: E402


def hex_rgb(value: str) -> tuple[float, float, float]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) / 255 for i in (0, 2, 4))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rounded_bbox(shape) -> list[float]:
    box = shape.BoundBox
    return [round(box.XLength, 3), round(box.YLength, 3), round(box.ZLength, 3)]


def make_outer_sleeve():
    outer = Part.makeBox(BOX.width, BOX.depth, BOX.height)
    t = BOX.board_thickness + BOX.wrap_thickness
    cavity = Part.makeBox(BOX.width - 2 * t, BOX.depth - 3.0, BOX.height - 2 * t, App.Vector(t, -1.0, t))
    shell = outer.cut(cavity)
    window = Part.makeCylinder(BOX.moon_window_diameter / 2, t + 2, App.Vector(BOX.width / 2, BOX.depth / 2, BOX.height - t - 1))
    return shell.cut(window).removeSplitter()


def make_wei_drawer():
    base = Part.makeBox(53.0, 180.0, 55.0, App.Vector(235.0, 25.0, 8.0))
    grip = Part.makeCylinder(14.0, 55.0, App.Vector(288.0, 115.0, 8.0))
    return base.cut(grip).removeSplitter()


def make_lock_key(y: float):
    head = Part.makeBox(31.8, 20.0, 8.0, App.Vector(203.2, y, 10.0))
    neck = Part.makeBox(8.0, 14.0, 8.0, App.Vector(231.0, y + 3.0, 10.0))
    return head.fuse(neck).removeSplitter()


def make_zhao_tray():
    tray = Part.makeBox(230.0, 200.0, 6.0, App.Vector(8.0, 15.0, 3.0))
    for y in (56.0, 156.0):
        tray = tray.cut(Part.makeBox(36.0, 24.0, 8.0, App.Vector(202.0, y - 2.0, 2.0)))
    front = Part.makeBox(230.0, 3.0, 18.0, App.Vector(8.0, 15.0, 3.0))
    return tray.fuse(front).removeSplitter()


def make_inner_liner():
    base = Part.makeBox(208.0, 138.0, 3.0, App.Vector(18.0, 44.0, 9.2))
    parts = [base]
    for x in (81.0, 143.0):
        parts.append(Part.makeBox(2.0, 138.0, 8.0, App.Vector(x, 44.0, 9.2)))
    parts.append(Part.makeBox(208.0, 2.0, 8.0, App.Vector(18.0, 112.0, 9.2)))
    liner = parts[0]
    for part in parts[1:]:
        liner = liner.fuse(part)
    return liner.removeSplitter()


def make_moon_disc():
    outer = Part.makeCylinder(54.0, 2.0, App.Vector(BOX.width / 2, BOX.depth / 2, 73.0))
    inner = Part.makeCylinder(47.0, 2.0, App.Vector(BOX.width / 2, BOX.depth / 2, 73.0))
    return outer.cut(inner).removeSplitter()


def make_proxy(index: int):
    x = 20.0 + (index % 3) * 63.0
    y = 48.0 + (index // 3) * 64.0
    z = 13.0
    body = Part.makeBox(SKU.width, SKU.depth, SKU.height, App.Vector(x, y, z))
    bevel = Part.makeBox(SKU.width - 8.0, 1.2, 0.8, App.Vector(x + 4.0, y + SKU.depth - 1.2, z + SKU.height))
    return body.fuse(bevel).removeSplitter()


def build_shapes() -> dict[str, object]:
    return {
        "outer_sleeve": make_outer_sleeve(),
        "wei_drawer": make_wei_drawer(),
        "lock_key_left": make_lock_key(55.0),
        "lock_key_right": make_lock_key(155.0),
        "zhao_tray": make_zhao_tray(),
        "inner_liner": make_inner_liner(),
        "moon_disc": make_moon_disc(),
        **{f"sku_proxy_{i + 1:02d}": make_proxy(i) for i in range(SKU.count)},
    }


def add_feature(doc, name: str, shape, color: tuple[float, float, float]):
    obj = doc.addObject("Part::Feature", name)
    obj.Label = name.replace("_", " ").title()
    obj.Shape = shape
    obj.addProperty("App::PropertyString", "MaterialIntent", "Design")
    obj.addProperty("App::PropertyString", "EvidenceStatus", "Design")
    obj.MaterialIntent = "2.0 mm paperboard proxy" if not name.startswith("sku_proxy") else "Neutral 60 × 60 × 35 mm SKU proxy"
    obj.EvidenceStatus = SKU.label if name.startswith("sku_proxy") else "Digital fit model only"
    if obj.ViewObject is not None:
        obj.ViewObject.ShapeColor = color
    return obj


def position_for(name: str, state: str) -> tuple[float, float, float]:
    offsets = state_offsets(state)
    if name.startswith("sku_proxy"):
        return offsets["zhao_tray"]
    return offsets.get(name, (0.0, 0.0, 0.0))


def export_state(shapes: dict[str, object], state: str) -> dict[str, object]:
    doc = App.newDocument(f"Jiewei_{state}")
    state_objects = []
    positions = {}
    for name, shape in shapes.items():
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape.copy()
        offset = position_for(name, state)
        obj.Placement.Base = App.Vector(*offset)
        positions[name] = list(offset)
        state_objects.append(obj)
    doc.recompute()
    path = CAD_DIR / f"jiewei_giftbox_{state}.step"
    Import.export(state_objects, str(path))
    App.closeDocument(doc.Name)
    return {"path": path.name, "sha256": sha256(path), "positions_mm": positions}


def assembly_bbox(shapes: dict[str, object], state: str) -> list[float]:
    extents = []
    for name, shape in shapes.items():
        box = shape.BoundBox
        dx, dy, dz = position_for(name, state)
        extents.append((box.XMin + dx, box.YMin + dy, box.ZMin + dz, box.XMax + dx, box.YMax + dy, box.ZMax + dz))
    return [
        round(max(v[3] for v in extents) - min(v[0] for v in extents), 3),
        round(max(v[4] for v in extents) - min(v[1] for v in extents), 3),
        round(max(v[5] for v in extents) - min(v[2] for v in extents), 3),
    ]


def main() -> None:
    CAD_DIR.mkdir(parents=True, exist_ok=True)
    MESH_DIR.mkdir(parents=True, exist_ok=True)
    shapes = build_shapes()
    doc = App.newDocument("JieweiGiftBox")
    palette = {
        "outer_sleeve": hex_rgb(COLORS["wall_ink"]),
        "wei_drawer": hex_rgb(COLORS["route_red"]),
        "lock_key_left": hex_rgb(COLORS["route_red"]),
        "lock_key_right": hex_rgb(COLORS["route_red"]),
        "zhao_tray": hex_rgb(COLORS["mountain_green"]),
        "inner_liner": hex_rgb(COLORS["paper_white"]),
        "moon_disc": hex_rgb(COLORS["moon_gold"]),
        **{f"sku_proxy_{i + 1:02d}": hex_rgb("#E6DDCA") for i in range(SKU.count)},
    }
    objects = {name: add_feature(doc, name, shape, palette[name]) for name, shape in shapes.items()}
    doc.recompute()

    fcstd = CAD_DIR / "jiewei_giftbox.FCStd"
    doc.saveAs(str(fcstd))
    parts = {}
    for name, obj in objects.items():
        path = MESH_DIR / f"{name}.stl"
        Mesh.export([obj], str(path))
        parts[name] = {
            "bbox_mm": rounded_bbox(obj.Shape),
            "volume_mm3": round(obj.Shape.Volume, 3),
            "solid_count": len(obj.Shape.Solids),
            "valid": bool(obj.Shape.isValid()),
            "sha256": sha256(path),
        }
    states = {state: export_state(shapes, state) for state in ("closed", "unlocked", "open")}
    report = {
        "document": "JieweiGiftBox",
        "units": "mm",
        "closed_bbox_mm": assembly_bbox(shapes, "closed"),
        "state_bbox_mm": {state: assembly_bbox(shapes, state) for state in states},
        "release_margin_mm": BOX.release_margin,
        "lock_logic": {
            "closed": "two lock keys occupy tray slots",
            "unlocked": "42 mm side motion clears both slots",
            "open": "side remains released while central tray advances 145 mm",
        },
        "parts": parts,
        "states": states,
        "fcstd_sha256": sha256(fcstd),
        "product_asset_status": "neutral_size_proxy",
        "proxy_label": SKU.label,
        "boundary": "Paperboard fit model only; load, friction, tear, drop and transport behavior remain unverified.",
    }
    (CAD_DIR / "cad_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "closed_bbox_mm": report["closed_bbox_mm"], "parts": len(parts)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
