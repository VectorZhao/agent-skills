#!/usr/bin/env python3
"""Read-only, limited geometry screening. Does NOT verify structural strength."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import numpy as np
import trimesh

SCALE_MM = {"mm": 1.0, "cm": 10.0, "m": 1000.0, "in": 25.4}


def audit_mesh(mesh: trimesh.Trimesh, units: str) -> dict:
    """Screen a copy of a triangular mesh without changing the source mesh."""
    if units not in SCALE_MM:
        raise ValueError("Units must be one of mm, cm, m, in")
    if not isinstance(mesh, trimesh.Trimesh):
        raise ValueError("Expected one triangle mesh, not a scene")
    if len(mesh.vertices) < 3 or len(mesh.faces) < 1:
        raise ValueError("Empty or insufficient triangle geometry")
    if not np.isfinite(mesh.vertices).all():
        raise ValueError("Vertex coordinates contain NaN or infinity")
    if np.any(mesh.faces < 0) or np.any(mesh.faces >= len(mesh.vertices)):
        raise ValueError("Invalid vertex index in faces")
    work = mesh.copy()
    work.apply_scale(SCALE_MM[units])
    # STL stores vertices per triangle. Merge coincident vertices for adjacency
    # checks; do not fill holes, reorient faces, or write a repaired model.
    work.merge_vertices()
    extents = np.asarray(work.extents, dtype=float)
    relative_scale = max(float(np.max(extents)), 1e-12)
    threshold = np.finfo(float).eps * relative_scale**2
    degenerate = int(np.count_nonzero(work.area_faces <= threshold))
    watertight = bool(work.is_watertight)
    winding = bool(work.is_winding_consistent)
    signed_volume = float(work.volume) if watertight else None
    issues = []
    if not watertight:
        issues.append("mesh_not_watertight")
    if not winding:
        issues.append("inconsistent_face_winding")
    if signed_volume is not None and signed_volume <= 0:
        issues.append("nonpositive_signed_volume")
    if degenerate:
        issues.append("degenerate_triangles")
    return {
        "status": "geometry_issues" if issues else "geometry_screened",
        "structural_validation": "not_performed",
        "input_units": units,
        "reported_units": "mm",
        "vertices_after_coincident_merge": int(len(work.vertices)),
        "triangles": int(len(work.faces)),
        "bounds_mm": work.bounds.tolist(),
        "extents_mm": extents.tolist(),
        "surface_area_mm2": float(work.area),
        "signed_volume_mm3": signed_volume,
        "watertight": watertight,
        "winding_consistent": winding,
        "degenerate_triangle_count": degenerate,
        "issues": issues,
        "not_checked": [
            "self_intersections", "minimum_wall_thickness", "internal_overlap",
            "actual_slicer_toolpaths", "printer_reach_and_clearance", "fit",
            "material_properties", "stress", "strength", "creep", "fatigue",
        ],
        "preprocessing": "A copy is scaled and coincident vertices merged; no hole repair or source modification.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mesh", type=Path)
    parser.add_argument("--units", required=True, choices=tuple(SCALE_MM))
    parser.add_argument("--json", dest="output", type=Path)
    args = parser.parse_args(argv)
    try:
        source = args.mesh.resolve(strict=True)
        if source.suffix.lower() not in {".stl", ".obj", ".ply"}:
            raise ValueError("Supported mesh formats: STL, OBJ, PLY")
        if args.output and args.output.resolve() == source:
            raise ValueError("JSON output must not overwrite the source mesh")
        loaded = trimesh.load(source, process=False)
        if isinstance(loaded, trimesh.Scene):
            raise ValueError("Multi-object scene is not supported; export each part separately")
        report = audit_mesh(loaded, args.units)
        report["input_file"] = source.name
        text = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False)
        if args.output:
            args.output.write_text(text + "\n", encoding="utf-8")
        print(text)
        return 0 if report["status"] == "geometry_screened" else 1
    except Exception as exc:
        print(f"Mesh audit failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
