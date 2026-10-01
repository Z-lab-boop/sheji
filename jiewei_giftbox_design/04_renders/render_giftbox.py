"""Render the Jiewei mechanism, seasonal CMF and engineering views from audited STL."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector


RENDER_DIR = Path(__file__).resolve().parent
PROJECT_DIR = RENDER_DIR.parent
MESH_DIR = PROJECT_DIR / "03_cad" / "meshes"
sys.path.insert(0, str(PROJECT_DIR / "scripts"))

from design_config import BOX, COLORS, SKU, state_offsets  # noqa: E402


MM = 0.001
PART_NAMES = (
    "outer_sleeve", "wei_drawer", "lock_key_left", "lock_key_right", "zhao_tray", "inner_liner", "moon_disc",
    "sku_proxy_01", "sku_proxy_02", "sku_proxy_03", "sku_proxy_04", "sku_proxy_05", "sku_proxy_06",
)
PROXY_NAMES = tuple(name for name in PART_NAMES if name.startswith("sku_proxy"))
WEI_PARTS = ("wei_drawer", "lock_key_left", "lock_key_right")
ZHAO_PARTS = ("zhao_tray", "inner_liner", *PROXY_NAMES)
VIEW_NAMES = (
    "hero_closed.png", "hero_unlocked.png", "hero_open.png",
    "sequence_01.png", "sequence_02.png", "sequence_03.png", "sequence_04.png",
    "exploded.png", "dieline_preview.png", "mid_autumn_variant.png", "national_day_variant.png", "ortho_top.png",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rgba(value: str, alpha: float = 1.0):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (alpha,)


def mat(name: str, color: str, metallic: float = 0.0, roughness: float = 0.58):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = rgba(color)
    node = material.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = rgba(color)
    node.inputs["Metallic"].default_value = metallic
    node.inputs["Roughness"].default_value = roughness
    return material


def point_at(obj, target=(0.0, 0.0, 0.03)):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def import_part(name: str, material):
    bpy.ops.wm.stl_import(filepath=str(MESH_DIR / f"{name}.stl"))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (MM, MM, MM)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.location += Vector((-BOX.width / 2 * MM, -BOX.depth / 2 * MM, 0))
    obj.data.materials.clear()
    obj.data.materials.append(material)
    bevel = obj.modifiers.new("Paperboard edge softness", "BEVEL")
    bevel.width = 0.55 * MM
    bevel.segments = 3
    return obj


def add_text(name: str, body: str, location, material, size: float, font_path: Path, align="LEFT"):
    curve = bpy.data.curves.new(name, type="FONT")
    curve.body = body
    curve.align_x = align
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.00008
    curve.bevel_depth = 0.00003
    curve.space_line = 0.86
    curve.font = bpy.data.fonts.load(str(font_path), check_existing=True)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.data.materials.append(material)
    return obj


def add_curve(name: str, points, material, width=0.0012):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.bevel_depth = width
    data.bevel_resolution = 3
    spline = data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, coords in zip(spline.points, points):
        point.co = (*coords, 1)
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def add_stage(material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=0.36, depth=0.008, location=(0, -0.055, -0.007))
    obj = bpy.context.object
    obj.name = "presentation_stage"
    obj.data.materials.append(material)
    bevel = obj.modifiers.new("Stage edge", "BEVEL")
    bevel.width = 0.005
    bevel.segments = 5
    return obj


def add_light(name, location, energy, size, color):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    point_at(obj, (0.0, -0.05, 0.025))


def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = True
    scene.render.resolution_percentage = 100
    scene.view_settings.exposure = -0.45
    scene.view_settings.look = "AgX - Medium Low Contrast"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("Jiewei World")
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.025, 0.035, 0.038, 1)
    background.inputs["Strength"].default_value = 0.16

    materials = {
        "wall": mat("Wall ink paper", COLORS["wall_ink"], 0.0, 0.5),
        "gold": mat("Moon gold foil", COLORS["moon_gold"], 0.48, 0.28),
        "red": mat("Route red", COLORS["route_red"], 0.0, 0.46),
        "green": mat("Mountain green", COLORS["mountain_green"], 0.0, 0.58),
        "paper": mat("Moon paper", COLORS["paper_white"], 0.0, 0.68),
        "proxy": mat("Neutral proxy", "#D8CEB8", 0.0, 0.7),
        "ink": mat("Disclosure ink", "#253234", 0.0, 0.5),
        "stage": mat("Warm stage", "#D8CEBA", 0.0, 0.72),
    }
    part_mats = {
        "outer_sleeve": materials["wall"], "wei_drawer": materials["red"],
        "lock_key_left": materials["red"], "lock_key_right": materials["red"],
        "zhao_tray": materials["green"], "inner_liner": materials["paper"], "moon_disc": materials["gold"],
        **{name: materials["proxy"] for name in PROXY_NAMES},
    }
    objects = {name: import_part(name, part_mats[name]) for name in PART_NAMES}
    stage = add_stage(materials["stage"])

    sans = PROJECT_DIR / "01_research/fonts/NotoSansSC[wght].ttf"
    serif = PROJECT_DIR / "01_research/fonts/NotoSerifSC[wght].ttf"
    labels = {}
    label_plates = {}
    for index, name in enumerate(PROXY_NAMES):
        x = (20 + (index % 3) * 63 + 30 - BOX.width / 2) * MM
        y = (48 + (index // 3) * 64 + 30 - BOX.depth / 2) * MM
        bpy.ops.mesh.primitive_cube_add(location=(x, y, 0.04915), scale=(0.025, 0.0095, 0.00025))
        plate = bpy.context.object
        plate.name = f"plate_{name}"
        plate.data.materials.append(materials["wall"])
        label_plates[name] = plate
        labels[name] = add_text(f"label_{name}", "规格代理件\n非实际商品包装", (x, y, 0.0495), materials["paper"], 0.0031, sans, "CENTER")

    branding = [
        add_text("jiewei_wordmark", "解围", (-0.118, -0.055, 0.0754), materials["paper"], 0.027, serif),
        add_text("jiewei_tag", "RELIEVE THE SIEGE", (-0.116, -0.082, 0.0754), materials["gold"], 0.006, sans),
        add_curve("shared_route", [(-0.118, 0.075, 0.0754), (-0.04, 0.075, 0.0754), (-0.04, 0.045, 0.0754), (0.085, 0.045, 0.0754), (0.085, 0.075, 0.0754), (0.125, 0.075, 0.0754)], materials["gold"], 0.0015),
    ]

    camera_data = bpy.data.cameras.new("Camera")
    camera = bpy.data.objects.new("Camera", camera_data)
    bpy.context.collection.objects.link(camera)
    scene.camera = camera
    camera.data.sensor_width = 36
    add_light("Key", (-0.30, -0.36, 0.48), 1.35, 0.30, (1.0, 0.84, 0.68))
    add_light("Fill", (0.34, -0.10, 0.30), 0.9, 0.24, (0.72, 0.88, 1.0))
    add_light("Rim", (0.12, 0.34, 0.42), 1.1, 0.22, (1.0, 0.70, 0.42))
    return scene, camera, objects, labels, label_plates, branding, materials, stage


def remember(objects):
    return {name: (obj.location.copy(), obj.hide_render) for name, obj in objects.items()}


def restore(objects, state):
    for name, obj in objects.items():
        location, hidden = state[name]
        obj.location = location.copy()
        obj.hide_render = hidden


def apply_state(objects, labels, label_plates, state: str, wei_ratio=1.0, zhao_ratio=1.0):
    offsets = state_offsets(state)
    wei = offsets["wei_drawer"][0] * wei_ratio * MM
    zhao = offsets["zhao_tray"][1] * zhao_ratio * MM
    for name in WEI_PARTS:
        objects[name].location.x += wei
    for name in ZHAO_PARTS:
        objects[name].location.y += zhao
    for name in PROXY_NAMES:
        labels[name].location.y += zhao
        label_plates[name].location.y += zhao


def set_camera(camera, location, target=(0.0, -0.035, 0.03), lens=64, ortho=None):
    camera.location = location
    point_at(camera, target)
    camera.data.lens = lens
    if ortho is None:
        camera.data.type = "PERSP"
    else:
        camera.data.type = "ORTHO"
        camera.data.ortho_scale = ortho


def render(scene, camera, filename: str, manifest):
    scene.render.resolution_x = 1800
    scene.render.resolution_y = 1400
    scene.render.filepath = str(RENDER_DIR / filename)
    bpy.ops.render.render(write_still=True)
    manifest["views"][filename] = {
        "size": [1800, 1400],
        "camera_location_m": [round(float(v), 5) for v in camera.location],
        "sha256": sha256(RENDER_DIR / filename),
    }


def add_dieline_preview(materials):
    extras = []
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0), scale=(0.30, 0.205, 0.0014))
    sheet = bpy.context.object
    sheet.name = "dieline_sheet"
    sheet.data.materials.append(materials["paper"])
    extras.append(sheet)
    for y in (-0.105, 0.02, 0.105):
        extras.append(add_curve(f"crease_{y}", [(-0.27, y, 0.002), (0.27, y, 0.002)], materials["green"], 0.0012))
    for x in (-0.20, -0.05, 0.10, 0.24):
        extras.append(add_curve(f"cut_{x}", [(x, -0.17, 0.0023), (x, 0.17, 0.0023)], materials["red"], 0.0014))
    extras.append(add_curve("cut_boundary", [(-0.28,-0.18,0.0023),(0.28,-0.18,0.0023),(0.28,0.18,0.0023),(-0.28,0.18,0.0023),(-0.28,-0.18,0.0023)], materials["red"], 0.0014))
    return extras


def add_season_label(text_value: str, material, font_path: Path):
    return add_text("season_label", text_value, (-0.11, 0.012, 0.0755), material, 0.0115, font_path)


def main() -> None:
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    scene, camera, objects, labels, label_plates, branding, materials, stage = setup_scene()
    all_dynamic = {
        **objects,
        **{f"label_{k}": v for k, v in labels.items()},
        **{f"plate_{k}": v for k, v in label_plates.items()},
    }
    base = remember(all_dynamic)
    manifest = {
        "geometry_basis": "audited STL",
        "cad_mesh_sha256": {name: sha256(MESH_DIR / f"{name}.stl") for name in PART_NAMES},
        "identity_assets": ["02_identity/mid_autumn_sleeve.svg", "02_identity/national_day_sleeve.svg", "02_identity/proxy_product_labels.svg"],
        "product_asset_status": "neutral_size_proxy",
        "proxy_label": SKU.label,
        "engine": scene.render.engine,
        "views": {},
        "boundary": "Digital paperboard and neutral-size-proxy render; no real brand asset, food product or physical validation is implied.",
    }

    set_camera(camera, (0.38, -0.40, 0.29), (0.0, 0.0, 0.035), 68)
    render(scene, camera, "hero_closed.png", manifest)

    restore(all_dynamic, base)
    apply_state(objects, labels, label_plates, "unlocked")
    set_camera(camera, (0.43, -0.42, 0.29), (0.025, 0.0, 0.035), 70)
    render(scene, camera, "hero_unlocked.png", manifest)

    restore(all_dynamic, base)
    apply_state(objects, labels, label_plates, "open")
    set_camera(camera, (0.44, -0.52, 0.34), (0.0, -0.09, 0.035), 72)
    render(scene, camera, "hero_open.png", manifest)

    sequence = (("closed", 0.0, 0.0), ("unlocked", 0.52, 0.0), ("unlocked", 1.0, 0.0), ("open", 1.0, 1.0))
    for index, (state, wei_ratio, zhao_ratio) in enumerate(sequence, 1):
        restore(all_dynamic, base)
        apply_state(objects, labels, label_plates, state, wei_ratio, zhao_ratio)
        set_camera(camera, (0.43, -0.47, 0.31), (0.0, -0.055, 0.032), 72)
        render(scene, camera, f"sequence_{index:02d}.png", manifest)

    restore(all_dynamic, base)
    explode = {
        "outer_sleeve": (0.0, 0.0, 0.13), "moon_disc": (0.0, 0.0, 0.18), "wei_drawer": (0.15, 0.0, 0.055),
        "lock_key_left": (0.10, 0.0, 0.09), "lock_key_right": (0.10, 0.0, 0.09), "zhao_tray": (0.0, -0.04, 0.0), "inner_liner": (0.0, -0.04, 0.045),
    }
    for name, offset in explode.items():
        objects[name].location += Vector(offset)
    for i, name in enumerate(PROXY_NAMES):
        objects[name].location.z += 0.075 + i * 0.008
        labels[name].location.z += 0.075 + i * 0.008
        label_plates[name].location.z += 0.075 + i * 0.008
    for obj in branding:
        obj.hide_render = True
    set_camera(camera, (0.48, -0.58, 0.48), (0.02, -0.03, 0.10), 76)
    render(scene, camera, "exploded.png", manifest)
    for obj in branding:
        obj.hide_render = False

    restore(all_dynamic, base)
    for obj in [*objects.values(), *labels.values(), *label_plates.values(), *branding, stage]:
        obj.hide_render = True
    dieline = add_dieline_preview(materials)
    set_camera(camera, (0.0, 0.0, 0.72), (0.0, 0.0, 0.0), 55, 0.72)
    render(scene, camera, "dieline_preview.png", manifest)
    for obj in dieline:
        bpy.data.objects.remove(obj, do_unlink=True)
    for obj in [*objects.values(), *labels.values(), *label_plates.values(), *branding, stage]:
        obj.hide_render = False

    serif = PROJECT_DIR / "01_research/fonts/NotoSerifSC[wght].ttf"
    restore(all_dynamic, base)
    season = add_season_label("月满中秋", materials["gold"], serif)
    set_camera(camera, (0.38, -0.40, 0.29), (0.0, 0.0, 0.035), 68)
    render(scene, camera, "mid_autumn_variant.png", manifest)
    bpy.data.objects.remove(season, do_unlink=True)

    restore(all_dynamic, base)
    objects["outer_sleeve"].data.materials[0] = materials["green"]
    for obj in branding:
        if obj.type == "CURVE" and obj.name == "shared_route":
            obj.data.materials[0] = materials["red"]
    season = add_season_label("山河同庆", materials["red"], serif)
    set_camera(camera, (0.38, -0.40, 0.29), (0.0, 0.0, 0.035), 68)
    render(scene, camera, "national_day_variant.png", manifest)
    bpy.data.objects.remove(season, do_unlink=True)
    objects["outer_sleeve"].data.materials[0] = materials["wall"]

    restore(all_dynamic, base)
    apply_state(objects, labels, label_plates, "open")
    set_camera(camera, (0.0, -0.04, 0.65), (0.0, -0.04, 0.0), 55, 0.62)
    render(scene, camera, "ortho_top.png", manifest)

    assert set(manifest["views"]) == set(VIEW_NAMES)
    (RENDER_DIR / "render_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "views": list(manifest["views"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
