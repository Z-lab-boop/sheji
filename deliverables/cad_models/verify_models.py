"""Re-open the delivered FreeCAD and STEP files and verify solid geometry."""

from __future__ import annotations

import json
from pathlib import Path

import FreeCAD as App
import Part


ROOT = Path(__file__).resolve().parents[2]


def bbox(shape) -> list[float]:
    box = shape.BoundBox
    return [round(box.XLength, 3), round(box.YLength, 3), round(box.ZLength, 3)]


def verify_fcstd(relative: str, minimum_shapes: int) -> dict[str, object]:
    path = ROOT / relative
    doc = App.openDocument(str(path))
    doc.recompute()
    shapes = [
        obj.Shape
        for obj in doc.Objects
        if hasattr(obj, "Shape") and not obj.Shape.isNull()
    ]
    result = {
        "path": relative,
        "shape_objects": len(shapes),
        "valid": len(shapes) >= minimum_shapes and all(shape.isValid() for shape in shapes),
    }
    App.closeDocument(doc.Name)
    return result


def verify_step(relative: str, minimum_solids: int) -> dict[str, object]:
    path = ROOT / relative
    shape = Part.read(str(path))
    return {
        "path": relative,
        "solid_count": len(shape.Solids),
        "bbox_mm": bbox(shape),
        "valid": shape.isValid() and len(shape.Solids) >= minimum_solids,
    }


def main() -> None:
    results = {
        "bubushengdian_fcstd": verify_fcstd(
            "bubushengdian_design/03_cad/bubushengdian_stamp_kit.FCStd", 10
        ),
        "bubushengdian_step": verify_step(
            "bubushengdian_design/03_cad/bubushengdian_stamp_kit.step", 10
        ),
        "jiewei_fcstd": verify_fcstd(
            "jiewei_giftbox_design/03_cad/jiewei_giftbox.FCStd", 13
        ),
        "jiewei_closed_step": verify_step(
            "jiewei_giftbox_design/03_cad/jiewei_giftbox_closed.step", 13
        ),
        "jiewei_unlocked_step": verify_step(
            "jiewei_giftbox_design/03_cad/jiewei_giftbox_unlocked.step", 13
        ),
        "jiewei_open_step": verify_step(
            "jiewei_giftbox_design/03_cad/jiewei_giftbox_open.step", 13
        ),
    }
    print(json.dumps(results, ensure_ascii=False, indent=2))
    if not all(item["valid"] for item in results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
