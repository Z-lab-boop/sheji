"""Render product, motion and engineering views from audited CAD meshes."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


RENDER_DIR = Path(__file__).resolve().parent
PROJECT_DIR = RENDER_DIR.parent
MESH_DIR = PROJECT_DIR / "03_cad" / "meshes"
SCRIPT_DIR = PROJECT_DIR / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from design_config import COLORS, PRODUCT, motion_offsets  # noqa: E402


MM = 0.001
PART_NAMES = (
    "outer_case",
    "stamp_tray",
    "stamp_01",
    "stamp_02",
    "stamp_03",
    "stamp_04",
    "stamp_05",
    "stamp_06",
    "inkpad_case",
    "map_proxy",
)
TRAY_CONTENTS = (
    "stamp_tray",
    "stamp_01",
    "stamp_02",
    "stamp_03",
    "stamp_04",
    "stamp_05",
    "stamp_06",
    "inkpad_case",
)
VIEW_SIZES = {
    "hero_closed.png": (1800, 1400),
    "hero_open.png": (1800, 1400),
    "map_unfolded.png": (1800, 1400),
    "stamp_grid.png": (1800, 1400),
    "exploded.png": (1800, 1600),
    "ortho_top.png": (1800, 1200),
    "ortho_front.png": (1800, 1200),
    "scale_view.png": (1800, 1400),
    "interaction_01.png": (1800, 1400),
    "interaction_02.png": (1800, 1400),
    "interaction_03.png": (1800, 1400),
    "interaction_04.png": (1800, 1400),
}


def hex_rgba(value: str, alpha: float = 1.0) -> tuple[float, float, float, float]:
    value = value.lstrip("#")
    rgb = [int(value[index : index + 2], 16) / 255 for index in (0, 2, 4)]
    return (*rgb, alpha)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def material(
    name: str,
    color: str,
    metallic: float = 0.0,
    roughness: float = 0.48,
):
    mat = bpy.data.materials.new(name=name)
    mat.diffuse_color = hex_rgba(color)
    node = mat.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = hex_rgba(color)
    node.inputs["Metallic"].default_value = metallic
    node.inputs["Roughness"].default_value = roughness
    return mat


def import_part(name: str, mat):
    bpy.ops.wm.stl_import(filepath=str(MESH_DIR / f"{name}.stl"))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (MM, MM, MM)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.location += Vector((-PRODUCT.width / 2 * MM, -PRODUCT.depth / 2 * MM, 0))
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new(name="Edge softening", type="BEVEL")
    bevel.width = 0.45 * MM
    bevel.segments = 3
    for polygon in obj.data.polygons:
        polygon.use_smooth = False
    return obj


def point_at(obj, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_area_light(name: str, location, energy: float, size: float, color) -> None:
    data = bpy.data.lights.new(name=name, type="AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    point_at(obj, (0.0, 0.0, 0.015))


def add_stage(stage_mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=0.19, depth=0.008, location=(0, 0, -0.006))
    stage = bpy.context.object
    stage.name = "presentation_plinth"
    stage.data.materials.append(stage_mat)
    bevel = stage.modifiers.new(name="Plinth edge", type="BEVEL")
    bevel.width = 0.004
    bevel.segments = 5
    return stage


def setup_scene():
    reset_scene()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.render.resolution_percentage = 100
    scene.render.image_settings.color_depth = "8"
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.view_settings.exposure = -0.35
    scene.view_settings.look = "AgX - Medium Low Contrast"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("Bubushengdian World")
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.035, 0.055, 0.06, 1.0)
    background.inputs["Strength"].default_value = 0.16

    materials = {
        "blue": material("City blue matte", COLORS["city_blue"], 0.06, 0.32),
        "paper": material("Moon paper", COLORS["moon_paper"], 0.0, 0.65),
        "red": material("Seal red", COLORS["seal_red"], 0.02, 0.42),
        "gold": material("Route gold", COLORS["route_gold"], 0.52, 0.26),
        "stone": material("Stone gray", COLORS["stone_gray"], 0.0, 0.58),
        "stage": material("Warm presentation stage", "#D9CEB9", 0.0, 0.68),
    }
    part_materials = {
        "outer_case": materials["blue"],
        "stamp_tray": materials["blue"],
        "stamp_01": materials["paper"],
        "stamp_02": materials["paper"],
        "stamp_03": materials["paper"],
        "stamp_04": materials["paper"],
        "stamp_05": materials["gold"],
        "stamp_06": materials["red"],
        "inkpad_case": materials["red"],
        "map_proxy": materials["paper"],
    }
    objects = {name: import_part(name, part_materials[name]) for name in PART_NAMES}
    stage = add_stage(materials["stage"])

    camera_data = bpy.data.cameras.new("Camera")
    camera = bpy.data.objects.new("Camera", camera_data)
    bpy.context.collection.objects.link(camera)
    scene.camera = camera
    camera.data.lens = 62
    camera.data.sensor_width = 36

    add_area_light("Key", (-0.20, -0.26, 0.34), 1.25, 0.22, (1.0, 0.86, 0.70))
    add_area_light("Fill", (0.28, -0.08, 0.22), 0.82, 0.18, (0.70, 0.88, 1.0))
    add_area_light("Rim", (0.08, 0.28, 0.32), 1.05, 0.16, (1.0, 0.72, 0.45))
    return scene, camera, objects, materials, stage


def remember(objects: dict[str, object]):
    return {
        name: (obj.location.copy(), obj.rotation_euler.copy(), obj.scale.copy(), obj.hide_render)
        for name, obj in objects.items()
    }


def restore(objects: dict[str, object], state) -> None:
    for name, obj in objects.items():
        location, rotation, scale, hidden = state[name]
        obj.location = location.copy()
        obj.rotation_euler = rotation.copy()
        obj.scale = scale.copy()
        obj.hide_render = hidden


def apply_open_state(objects: dict[str, object], progress: float) -> None:
    travel = motion_offsets(progress)["stamp_tray"][0] * MM
    for name in TRAY_CONTENTS:
        objects[name].location.x += travel


def object_center_world(obj) -> Vector:
    """Return the world-space centre of an object's evaluated bounding box."""
    return sum((obj.matrix_world @ Vector(corner) for corner in obj.bound_box), Vector()) / 8


def add_curve(name: str, points, bevel: float, mat):
    curve_data = bpy.data.curves.new(name=name, type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.bevel_depth = bevel
    curve_data.bevel_resolution = 4
    spline = curve_data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, coordinates in zip(spline.points, points):
        point.co = (*coordinates, 1.0)
    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def add_map_artwork(materials):
    extras = []
    bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 0.001), scale=(0.24, 0.165, 0.001))
    sheet = bpy.context.object
    sheet.name = "unfolded_map_artwork"
    sheet.data.materials.append(materials["paper"])
    bevel = sheet.modifiers.new(name="Paper edge", type="BEVEL")
    bevel.width = 0.003
    bevel.segments = 4
    extras.append(sheet)
    points = [(-0.19, -0.06, 0.004), (-0.08, 0.035, 0.004), (0.035, -0.02, 0.004), (0.17, 0.055, 0.004)]
    extras.append(add_curve("map_route", points, 0.0024, materials["gold"]))
    for index, point in enumerate(points):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.010, location=point)
        node = bpy.context.object
        node.name = f"map_node_{index + 1}"
        node.data.materials.append(materials["red"] if index in (0, 3) else materials["blue"])
        extras.append(node)
    for x in (-0.08, 0.08):
        extras.append(add_curve(f"fold_{x}", [(x, -0.16, 0.003), (x, 0.16, 0.003)], 0.0005, materials["stone"]))
    return extras


def set_camera(camera, location, target=(0.0, 0.0, 0.02), lens=62, ortho=None):
    camera.location = location
    point_at(camera, target)
    camera.data.lens = lens
    if ortho is None:
        camera.data.type = "PERSP"
    else:
        camera.data.type = "ORTHO"
        camera.data.ortho_scale = ortho


def render(scene, filename: str, size: tuple[int, int], manifest: dict, camera) -> None:
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.filepath = str(RENDER_DIR / filename)
    bpy.ops.render.render(write_still=True)
    manifest["views"][filename] = {
        "size": list(size),
        "camera_location_m": [round(value, 5) for value in camera.location],
        "sha256": sha256(RENDER_DIR / filename),
    }


def main() -> None:
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    scene, camera, objects, materials, stage = setup_scene()
    base = remember(objects)
    manifest = {
        "geometry_basis": "audited STL",
        "supplementary_artwork": "02_identity/folding_map.svg",
        "cad_mesh_sha256": {
            name: sha256(MESH_DIR / f"{name}.stl") for name in PART_NAMES
        },
        "engine": scene.render.engine,
        "views": {},
        "boundary": "Concept motion only; no physical friction, wear or child-safety validation is claimed.",
    }

    set_camera(camera, (0.235, -0.265, 0.205), (0.0, 0.0, 0.016), 66)
    render(scene, "hero_closed.png", VIEW_SIZES["hero_closed.png"], manifest, camera)

    restore(objects, base)
    apply_open_state(objects, 1.0)
    set_camera(camera, (0.32, -0.29, 0.225), (0.04, 0.0, 0.018), 66)
    render(scene, "hero_open.png", VIEW_SIZES["hero_open.png"], manifest, camera)

    restore(objects, base)
    for obj in objects.values():
        obj.hide_render = True
    stage.hide_render = True
    map_objects = add_map_artwork(materials)
    set_camera(camera, (0.0, 0.0, 0.62), (0.0, 0.0, 0.0), 55, 0.58)
    render(scene, "map_unfolded.png", VIEW_SIZES["map_unfolded.png"], manifest, camera)
    for obj in map_objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    stage.hide_render = False

    restore(objects, base)
    for name, obj in objects.items():
        obj.hide_render = not name.startswith("stamp_") or name == "stamp_tray"
    grid_positions = [(-0.055, -0.037, 0.0), (0.0, -0.037, 0.0), (0.055, -0.037, 0.0), (-0.055, 0.037, 0.0), (0.0, 0.037, 0.0), (0.055, 0.037, 0.0)]
    for index, position in enumerate(grid_positions, start=1):
        obj = objects[f"stamp_{index:02d}"]
        target = Vector((position[0], position[1], PRODUCT.stamp_height * MM / 2))
        obj.location += target - object_center_world(obj)
    set_camera(camera, (0.0, -0.28, 0.22), (0.0, 0.0, 0.02), 70)
    render(scene, "stamp_grid.png", VIEW_SIZES["stamp_grid.png"], manifest, camera)

    restore(objects, base)
    explode = {
        "outer_case": (0.0, 0.0, 0.070),
        "map_proxy": (0.0, 0.0, 0.110),
        "stamp_tray": (0.0, 0.0, 0.0),
        "inkpad_case": (0.06, 0.0, 0.035),
    }
    for name, offset in explode.items():
        objects[name].location += Vector(offset)
    for index in range(6):
        objects[f"stamp_{index + 1:02d}"].location.z += (0.028 + index * 0.006)
    set_camera(camera, (0.29, -0.34, 0.30), (0.0, 0.0, 0.065), 72)
    render(scene, "exploded.png", VIEW_SIZES["exploded.png"], manifest, camera)

    restore(objects, base)
    set_camera(camera, (0.0, 0.0, 0.46), (0.0, 0.0, 0.0), 55, 0.22)
    render(scene, "ortho_top.png", VIEW_SIZES["ortho_top.png"], manifest, camera)

    restore(objects, base)
    set_camera(camera, (0.0, -0.42, 0.015), (0.0, 0.0, 0.015), 55, 0.22)
    render(scene, "ortho_front.png", VIEW_SIZES["ortho_front.png"], manifest, camera)

    restore(objects, base)
    apply_open_state(objects, 0.68)
    set_camera(camera, (0.26, -0.31, 0.17), (0.02, 0.0, 0.014), 78)
    render(scene, "scale_view.png", VIEW_SIZES["scale_view.png"], manifest, camera)

    for index, progress in enumerate((0.0, 0.33, 0.66, 1.0), start=1):
        restore(objects, base)
        apply_open_state(objects, progress)
        set_camera(camera, (0.26, -0.30, 0.19), (0.02, 0.0, 0.016), 68)
        name = f"interaction_{index:02d}.png"
        render(scene, name, VIEW_SIZES[name], manifest, camera)

    (RENDER_DIR / "render_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "ok", "views": list(manifest["views"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
