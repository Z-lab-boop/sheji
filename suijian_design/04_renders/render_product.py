"""Render a deterministic product image set from the audited CAD meshes."""

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

from design_config import COLORS, PRODUCT


PARTS = ("outer_shell", "inner_tray", "lifter", "gold_accent", "card_proxy")
MM = 0.001


def parse_args() -> str:
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return "proof" if "--proof" in args else "final"


def hex_rgb(value: str) -> tuple[float, float, float, float]:
    value = value.lstrip("#")
    rgb = tuple(int(value[index : index + 2], 16) / 255 for index in (0, 2, 4))
    # Convert sRGB into an approximate scene-linear value.
    linear = tuple(channel ** 2.2 for channel in rgb)
    return (*linear, 1.0)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def material(name: str, color: str, metallic: float, roughness: float):
    mat = bpy.data.materials.new(name=name)
    mat.diffuse_color = hex_rgb(color)
    mat.use_nodes = True
    node = mat.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = hex_rgb(color)
    node.inputs["Metallic"].default_value = metallic
    node.inputs["Roughness"].default_value = roughness
    node.inputs["IOR"].default_value = 1.46
    return mat


def load_part(name: str, path: Path):
    """Import one audited STL and return a consistently named Blender object."""
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=str(path))
    imported = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
    if len(imported) != 1:
        raise RuntimeError(f"expected one mesh for {name}, got {len(imported)}")
    obj = imported[0]
    obj.name = name
    obj.scale = (MM, MM, MM)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    if name not in {"card_proxy", "gold_accent"}:
        bevel = obj.modifiers.new(name="Micro bevel", type="BEVEL")
        bevel.width = 0.28
        bevel.segments = 3
        bevel.limit_method = "ANGLE"
    return obj


def add_area(name: str, location: tuple[float, float, float], energy: float, size: float, color: tuple[float, float, float]):
    light_data = bpy.data.lights.new(name=name, type="AREA")
    light_data.energy = energy
    light_data.shape = "DISK"
    light_data.size = size
    light_data.color = color
    light_obj = bpy.data.objects.new(name, light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = tuple(value * MM for value in location)
    point_at(light_obj, tuple(value * MM for value in (49.0, 32.5, 5.0)))
    return light_obj


def point_at(obj, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def setup_camera():
    data = bpy.data.cameras.new("ProductCamera")
    data.lens = 62
    data.sensor_width = 36
    data.clip_start = 0.01
    data.clip_end = 10.0
    data.dof.use_dof = False
    camera = bpy.data.objects.new("ProductCamera", data)
    bpy.context.collection.objects.link(camera)
    bpy.context.scene.camera = camera
    return camera


def add_packaging(materials: dict[str, object]):
    """Add an honest concept package made from simple, clearly separate geometry."""
    bpy.ops.mesh.primitive_cube_add(
        location=tuple(value * MM for value in (22.0, 32.5, 20.0)),
        scale=tuple(value * MM for value in (58.0, 40.0, 14.0)),
    )
    sleeve = bpy.context.object
    sleeve.name = "concept_package_sleeve"
    sleeve.data.materials.append(materials["paper"])
    bevel = sleeve.modifiers.new(name="Package edge", type="BEVEL")
    bevel.width = 2.5 * MM
    bevel.segments = 5

    bpy.ops.mesh.primitive_cube_add(
        location=tuple(value * MM for value in (75.0, 32.5, 16.0)),
        scale=tuple(value * MM for value in (48.0, 33.0, 9.0)),
    )
    drawer = bpy.context.object
    drawer.name = "concept_package_drawer"
    drawer.data.materials.append(materials["green"])
    bevel = drawer.modifiers.new(name="Drawer edge", type="BEVEL")
    bevel.width = 2.0 * MM
    bevel.segments = 4
    return [sleeve, drawer]


def setup_scene():
    reset_scene()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.resolution_percentage = 100
    scene.render.image_settings.compression = 28
    scene.render.use_file_extension = True
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.use_stamp = False
    scene.render.pixel_aspect_x = 1
    scene.render.pixel_aspect_y = 1
    scene.render.resolution_x = 600
    scene.render.resolution_y = 600
    scene.render.resolution_percentage = 100
    scene.render.image_settings.color_mode = "RGBA"
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.055, 0.070, 0.070, 1.0)
    background.inputs["Strength"].default_value = 0.05
    scene.view_settings.exposure = -0.25
    try:
        scene.view_settings.look = "AgX - Medium Low Contrast"
    except TypeError:
        pass

    materials = {
        "green": material("Zhao lacquer green", COLORS["zhao_lacquer"], 0.08, 0.38),
        "gold": material("Ding brushed gold", COLORS["ding_gold"], 0.78, 0.28),
        "red": material("Oath vermilion", COLORS["oath_vermilion"], 0.05, 0.32),
        "paper": material("Silk white paper", COLORS["silk_white"], 0.0, 0.62),
    }
    objects = {name: load_part(name, MESH_DIR / f"{name}.stl") for name in PARTS}
    objects["outer_shell"].data.materials.append(materials["green"])
    objects["inner_tray"].data.materials.append(materials["green"])
    objects["lifter"].data.materials.append(materials["gold"])
    objects["gold_accent"].data.materials.append(materials["gold"])
    objects["card_proxy"].data.materials.append(materials["paper"])

    camera = setup_camera()
    add_area("Key softbox", (70.0, -95.0, 145.0), 1.05, 92.0 * MM, (1.0, 0.90, 0.78))
    add_area("Fill softbox", (-65.0, 85.0, 95.0), 0.78, 75.0 * MM, (0.68, 0.82, 1.0))
    add_area("Gold rim", (155.0, 115.0, 80.0), 0.92, 65.0 * MM, (1.0, 0.68, 0.34))
    return scene, camera, objects, materials


def remember(objects: dict[str, object]) -> dict[str, tuple[Vector, object, Vector]]:
    return {
        name: (obj.location.copy(), obj.rotation_euler.copy(), obj.scale.copy())
        for name, obj in objects.items()
    }


def restore(objects: dict[str, object], base: dict[str, tuple[Vector, object, Vector]]) -> None:
    for name, obj in objects.items():
        location, rotation, scale = base[name]
        obj.location = location.copy()
        obj.rotation_euler = rotation.copy()
        obj.scale = scale.copy()
        obj.hide_render = False


def set_open_state(objects: dict[str, object], progress: float) -> None:
    """Apply controlled travel and card lift without changing source meshes."""
    progress = max(0.0, min(1.0, progress))
    ease = progress * progress * (3.0 - 2.0 * progress)
    for name in ("inner_tray", "lifter", "gold_accent", "card_proxy"):
        objects[name].location.x += PRODUCT.travel * MM * ease
    objects["card_proxy"].location.z += PRODUCT.lift * MM * ease
    objects["card_proxy"].rotation_euler.y = math.radians(-4.0 * ease)


def render_view(
    scene,
    camera,
    filename: str,
    camera_location: tuple[float, float, float],
    target: tuple[float, float, float],
    size: tuple[int, int],
    manifest: dict,
) -> None:
    camera.location = tuple(value * MM for value in camera_location)
    point_at(camera, tuple(value * MM for value in target))
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.filepath = str(RENDER_DIR / filename)
    bpy.ops.render.render(write_still=True)
    manifest["views"][filename] = {
        "camera_location": list(camera_location),
        "target": list(target),
        "size": list(size),
        "lens_mm": camera.data.lens,
    }


def render_final(scene, camera, objects, materials, manifest) -> None:
    base = remember(objects)
    views = [
        ("hero_closed.png", 0.0, (178, -128, 116), (49, 32.5, 5.8), (2400, 2400)),
        ("hero_open.png", 1.0, (198, -140, 120), (62, 32.5, 7.2), (2400, 2400)),
        ("interaction_01.png", 0.0, (190, -152, 100), (49, 32.5, 5.5), (2400, 2400)),
        ("interaction_02.png", 0.52, (190, -152, 100), (56, 32.5, 6.0), (2400, 2400)),
        ("interaction_03.png", 1.0, (190, -152, 100), (62, 32.5, 7.0), (2400, 2400)),
    ]
    for filename, progress, camera_location, target, size in views:
        restore(objects, base)
        set_open_state(objects, progress)
        render_view(scene, camera, filename, camera_location, target, size, manifest)

    restore(objects, base)
    objects["outer_shell"].location.z += 24 * MM
    objects["gold_accent"].location.z += 42 * MM
    objects["inner_tray"].location.z += 4 * MM
    objects["lifter"].location.z += 15 * MM
    objects["card_proxy"].location.z += 31 * MM
    render_view(scene, camera, "exploded.png", (205, -175, 145), (50, 32.5, 23), (2400, 2400), manifest)

    restore(objects, base)
    render_view(scene, camera, "detail_accent.png", (91, -45, 62), (48, 31, 12.8), (2400, 2400), manifest)

    restore(objects, base)
    set_open_state(objects, 0.78)
    render_view(scene, camera, "scale_view.png", (226, -187, 112), (58, 32.5, 6.5), (2400, 1800), manifest)

    restore(objects, base)
    set_open_state(objects, 0.35)
    package_objects = add_packaging(materials)
    for obj in package_objects:
        obj.location.y += 83 * MM
        obj.location.x -= 12 * MM
        obj.location.z += 2 * MM
    render_view(scene, camera, "packaging_hero.png", (235, -195, 170), (50, 70, 16), (2400, 2400), manifest)


def main() -> None:
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    mode = parse_args()
    scene, camera, objects, materials = setup_scene()
    manifest = {
        "blender_version": bpy.app.version_string,
        "engine": scene.render.engine,
        "mesh_sha256": {name: sha256(MESH_DIR / f"{name}.stl") for name in PARTS},
        "views": {},
        "geometry_rule": "All product parts are imported from the audited CAD STL set.",
        "packaging_rule": "Packaging is a clearly labelled concept primitive, not production tooling.",
    }
    if mode == "proof":
        set_open_state(objects, 0.72)
        render_view(scene, camera, "proof.png", (190, -145, 105), (58, 32.5, 6.5), (600, 600), manifest)
    else:
        render_final(scene, camera, objects, materials, manifest)
    (RENDER_DIR / "render_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
