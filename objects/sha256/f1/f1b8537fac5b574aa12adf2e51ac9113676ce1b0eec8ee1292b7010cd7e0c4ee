"""Package the rolling-idler fix (goal: independent ZIP + SHA-256 + MANIFEST).

Collects the new version directory, the patchers/probes that belong to it and the evidence
logs, writes MANIFEST.sha256 + validation/static_report.json, and produces a ZIP outside the
repo.  Read-only with respect to the delivered asset and to every existing log.

  python incoming/mod4_rolling_20260913/tools/package_rolling_fix.py [--zip /home/egde/MOD4_rolling_idlers_20260913.zip]
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

REPO = Path(__file__).resolve().parents[3]
VER = REPO / "incoming" / "mod4_rolling_20260913"
MEMBERS = [
    "incoming/mod4_rolling_20260913/README.md",
    "incoming/mod4_rolling_20260913/TASK_LIST.md",
    "incoming/mod4_rolling_20260913/chassis_mod4/isaac/robot.usd",
    "incoming/mod4_rolling_20260913/chassis_mod4/isaac/import_contract.json",
    "incoming/mod4_rolling_20260913/chassis_mod4/isaac/robot_cfg.py",
    "incoming/mod4_rolling_20260913/chassis_mod4/isaac/meshes.usdc",
    "incoming/mod4_rolling_20260913/chassis_mod4/isaac/scene.usda",
    "incoming/mod4_rolling_20260913/tools/build_rolling_rollers_usd.py",
    "incoming/mod4_rolling_20260913/tools/make_rolling_contract.py",
    "migration/linux/patch_guide_sensor_regex.py",
    "migration/linux/patch_leg_pi.py",
    "migration/linux/patch_usd_override.py",
    "migration/linux/patch_scripts_use_rolling_plant.py",
    "migration/linux/make_idler_usd.py",
    "migration/linux/make_tyre_compliance_usd.py",
    "migration/linux/check_usd_closure_consistency.py",
    "migration/linux/tunnel_tuning.env",
    "migration/linux/run_special_phases_v3.sh",
    "isaac/mod4/probe_tunnel_cross_pi.py",
    "isaac/mod4/probe_crouch_kp.py",
    "isaac/mod4/probe_crouch_geometry.py",
    "isaac/mod4/probe_rolling_plant.py",
    "isaac/mod4/probe_material_check.py",
    "docs/MOD4_ROLLING_STATUS_20260913.md",
]
EVIDENCE = [
    "docs/probe_crouch_kp.log", "docs/probe_crouch_kp2.log", "docs/probe_crouch_kp3.log",
    "docs/probe_crouch_pi.log", "docs/probe_tunnel_cross_pi.log",
    "docs/probe_crouch_sweep.log", "docs/probe_crouch_geometry_press.log",
]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", default=str(Path.home() / "MOD4_rolling_idlers_20260913.zip"))
    args = ap.parse_args()

    present, missing = [], []
    for rel in MEMBERS:
        p = REPO / rel
        (present if p.is_file() else missing).append(rel)

    man_lines = ["%s  %s" % (sha256(REPO / r), r) for r in present]
    (VER / "MANIFEST.sha256").write_text("\n".join(man_lines) + "\n", encoding="utf8")
    print("[pkg] MANIFEST.sha256: %d files (%d missing)" % (len(present), len(missing)))
    for m in missing:
        print("[pkg]   MISSING %s" % m)

    report = {"schema": "mod4.rolling_idlers.v1",
              "delivered_usd_sha256": sha256(REPO / "incoming/mod4_fixed_20260912/chassis_mod4/isaac/robot.usd"),
              "rolling_usd_sha256": sha256(VER / "chassis_mod4/isaac/robot.usd"),
              "rolling_contract_sha256": sha256(VER / "chassis_mod4/isaac/import_contract.json"),
              "files": {r: sha256(REPO / r) for r in present},
              "missing": missing}
    try:
        from pxr import Usd, UsdPhysics
        st = Usd.Stage.Open(str(VER / "chassis_mod4/isaac/robot.usd"), Usd.Stage.LoadAll)
        report["counts"] = {
            "bodies": len([p for p in st.Traverse() if p.HasAPI(UsdPhysics.RigidBodyAPI)]),
            "tree_joints": len([p for p in st.Traverse() if p.GetTypeName() in
                                ("PhysicsRevoluteJoint", "PhysicsPrismaticJoint")]),
            "closures": len([p for p in st.Traverse() if p.GetTypeName() == "PhysicsSphericalJoint"]),
            "fixed_joints": len([p for p in st.Traverse() if p.GetTypeName() == "PhysicsFixedJoint"]),
            "colliders": len([p for p in st.Traverse() if p.GetTypeName() in
                              ("Cylinder", "Cube", "Sphere", "Capsule")]),
            "visual_meshes": len([p for p in st.Traverse() if p.GetTypeName() == "Mesh"]),
            "roller_joints": len([p for p in st.Traverse()
                                  if p.GetName().startswith("guide_roller_")
                                  and p.GetTypeName() == "PhysicsRevoluteJoint"]),
        }
    except Exception as exc:                                   # pragma: no cover
        report["counts_error"] = repr(exc)
    (VER / "validation").mkdir(exist_ok=True)
    (VER / "validation/static_report.json").write_text(json.dumps(report, indent=1), encoding="utf8")
    print("[pkg] static_report.json: %s" % json.dumps(report.get("counts", {})))

    zpath = Path(args.zip)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in present:
            z.write(REPO / rel, rel)
        for rel in EVIDENCE:
            if (REPO / rel).is_file():
                z.write(REPO / rel, rel)
        z.write(VER / "MANIFEST.sha256", "incoming/mod4_rolling_20260913/MANIFEST.sha256")
        z.write(VER / "validation/static_report.json",
                "incoming/mod4_rolling_20260913/validation/static_report.json")
    print("[pkg] zip=%s bytes=%d sha256=%s" % (zpath, zpath.stat().st_size, sha256(zpath)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())