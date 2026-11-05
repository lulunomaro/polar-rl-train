#!/usr/bin/env python3
"""One-shot MOD4v2 asset derivation from the pinned P0 specification.

Requires only the existing pxr Python environment and the standard library.
Does not import Isaac, MuJoCo, training code or model weights. All writes are
confined to this builder's new assets/MJCF outputs and BUILD_RECEIPT.json.
Existing outputs are not overwritten; a failed build is retained for inspection.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import sys
import traceback
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

from pxr import Sdf, Usd, UsdPhysics

ROOT = Path(__file__).resolve().parent
SPEC_PATH = ROOT / "MECHANICAL_LIMITS_SPEC_V2.json"
USD_OUT = ROOT / "package/assets/robot.usd"
CONTRACT_OUT = ROOT / "package/assets/import_contract.json"
MJCF_OUT = ROOT / "package/mjcf/scene.xml"
MESH_OUT = ROOT / "package/mjcf/assets"
RECEIPT_OUT = ROOT / "BUILD_RECEIPT.json"
VERSION = "mod4v2.p0.mechanical_limits.20261105"
SIDES = ("left", "right")
ACTIVE_AND_FOLLOWER = {"hip", "crank", "drive_hip_spin", "drive_input_spin"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def owned_path(path: Path) -> Path:
    resolved = path.resolve()
    check(resolved.is_relative_to(ROOT), f"Output outside owned root: {resolved}")
    return resolved


def write_json_new(path: Path, value: dict) -> None:
    owned_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")


def finite_or_null(value: float) -> float | None:
    return float(value) if math.isfinite(value) else None


def xml_number(value: float | None, lower: bool) -> str:
    return ("-inf" if lower else "inf") if value is None else format(value, ".17g")


def usd_invariants(stage: Usd.Stage, changed_joint_names: set[str]) -> dict:
    """Small structural/physical signature; no simulation or generated inventory."""
    bodies, joints, shape_types, filters = {}, {}, [], {}
    for p in stage.Traverse():
        path = str(p.GetPath())
        if p.HasAPI(UsdPhysics.RigidBodyAPI):
            bodies[path] = {
                a.GetName(): str(a.Get()) for a in p.GetAttributes()
                if a.HasAuthoredValueOpinion()
            }
        rel = p.GetRelationship("physics:filteredPairs")
        if rel:
            filters[path] = [str(t) for t in rel.GetTargets()]
        if p.IsA(UsdPhysics.Joint):
            attrs = {}
            for a in p.GetAttributes():
                if (p.GetName() in changed_joint_names
                        and a.GetName() in {"physics:lowerLimit", "physics:upperLimit"}):
                    continue
                if a.HasAuthoredValueOpinion():
                    attrs[a.GetName()] = str(a.Get())
            joints[path] = {
                "type": p.GetTypeName(), "schemas": str(p.GetMetadata("apiSchemas")),
                "attrs": attrs,
                "relationships": {r.GetName(): [str(t) for t in r.GetTargets()]
                                  for r in p.GetRelationships()},
            }
        if p.GetTypeName() in {"Mesh", "Capsule", "Cube", "Cylinder", "Sphere"}:
            shape_types.append((path, p.GetTypeName(), p.HasAPI(UsdPhysics.CollisionAPI)))
    return {"bodies": bodies, "joints": joints, "shape_types": shape_types,
            "filtered_pairs": filters}


def xml_structure(element: ET.Element, edited_names: set[str]) -> tuple:
    attrs = dict(element.attrib)
    if element.tag == "compiler":
        attrs.pop("meshdir", None)
    if element.tag == "joint" and attrs.get("name") in edited_names:
        attrs.pop("range", None)
        attrs.pop("limited", None)
        if attrs["name"].endswith("_gas_slide"):
            attrs.pop("springref", None)
    return (element.tag, tuple(sorted(attrs.items())),
            tuple(xml_structure(child, edited_names) for child in element))


def build(receipt: dict) -> None:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    spec_sha = sha256(SPEC_PATH)
    source = spec["source"]
    usd_source = Path(source["USD"])
    contract_source = Path(source["contract"])
    mjcf_source = Path(source["MJCF"])
    source_hashes = {str(p): sha256(p) for p in
                     (usd_source, contract_source, mjcf_source, SPEC_PATH)}
    check(source_hashes[str(usd_source)] == source["USD_SHA256"], "Pinned USD SHA mismatch")
    check(source_hashes[str(contract_source)] == source["contract_SHA256"],
          "Pinned contract SHA mismatch")
    contract_old = json.loads(contract_source.read_text(encoding="utf-8"))
    xml_old_text = mjcf_source.read_text(encoding="utf-8")
    xml_old = ET.fromstring(xml_old_text)
    check(xml_old.find("compiler").get("angle") == "radian", "Source MJCF must be radians")
    check(len(xml_old.findall("./worldbody//body")) == 31, "Source MJCF body count is not 31")
    bounds = spec["per_side_joint_bounds_SI"]
    names = {f"{side}_{key}" for side in SIDES for key in bounds}
    check(len(names) == 20, "Expected exactly 20 bound-edited joints")
    for name in names:
        check(name in contract_old["joints"], f"Missing source contract joint: {name}")
    for out in (USD_OUT, CONTRACT_OUT, MJCF_OUT, MESH_OUT):
        owned_path(out)
        check(not out.exists(), f"Existing output retained; no overwrite: {out}")

    meshdir_old = Path(xml_old.find("compiler").get("meshdir", ""))
    if not meshdir_old.is_absolute():
        meshdir_old = mjcf_source.parent / meshdir_old
    mesh_sources = {}
    for mesh in xml_old.findall("./asset/mesh"):
        rel = Path(mesh.get("file"))
        check(not rel.is_absolute() and ".." not in rel.parts, f"Unexpected mesh reference: {rel}")
        src = (meshdir_old / rel).resolve()
        check(src.is_file(), f"Missing referenced mesh: {src}")
        mesh_sources[rel.as_posix()] = src
    receipt.update({"spec_sha256": spec_sha, "source_files_sha256": source_hashes,
                    "source_inputs_read_only": True, "version": VERSION})

    stage_old = Usd.Stage.Open(str(usd_source), Usd.Stage.LoadNone)
    check(bool(stage_old), "Source USD did not open")
    invariant_old = usd_invariants(stage_old, names)
    check(len(invariant_old["bodies"]) == 31, "Source USD body count is not 31")
    check(len(invariant_old["joints"]) == 36, "Source USD joint count is not 36")
    # The pinned v1 asset has inline geometry, not external texture/mesh assets.
    for p in stage_old.Traverse():
        for a in p.GetAttributes():
            if a.HasAuthoredValueOpinion() and a.GetTypeName() in (
                    Sdf.ValueTypeNames.Asset, Sdf.ValueTypeNames.AssetArray):
                check(not a.Get(), f"Unexpected external USD asset dependency: {a.GetPath()}")

    flat = stage_old.Flatten()
    stage = Usd.Stage.Open(flat)
    limit_receipt = {}
    for side in SIDES:
        for key, (low, high) in bounds.items():
            name = f"{side}_{key}"
            prim = stage.GetPrimAtPath(f"/Robot/joints/{name}")
            check(bool(prim), f"Missing USD joint: {name}")
            angular = key != "gas_slide"
            joint = UsdPhysics.RevoluteJoint(prim) if angular else UsdPhysics.PrismaticJoint(prim)
            before = [joint.GetLowerLimitAttr().Get(), joint.GetUpperLimitAttr().Get()]
            lo = -math.inf if low is None else math.degrees(low) if angular else low
            hi = math.inf if high is None else math.degrees(high) if angular else high
            joint.GetLowerLimitAttr().Set(lo)
            joint.GetUpperLimitAttr().Set(hi)
            check(UsdPhysics.Joint(prim).GetJointEnabledAttr().Get() is True,
                  f"Disabled source joint: {name}")
            limit_receipt[name] = {"limits_si": [low, high],
                                   "USD_unit": "degree" if angular else "m",
                                   "USD_before": before,
                                   "USD_after": [finite_or_null(joint.GetLowerLimitAttr().Get()),
                                                 finite_or_null(joint.GetUpperLimitAttr().Get())],
                                   "continuous": key in ACTIVE_AND_FOLLOWER,
                                   "joint_enabled": True,
                                   "joint_enabled_authored": UsdPhysics.Joint(prim).GetJointEnabledAttr().HasAuthoredValueOpinion()}
    layer_data = dict(flat.customLayerData)
    layer_data.update({"mod4_asset_version": VERSION, "source_usd_sha256": source["USD_SHA256"],
                       "mechanical_limits_spec_sha256": spec_sha,
                       "runtime_verified": False, "hardware_stroke_calibrated": False})
    flat.customLayerData = layer_data
    USD_OUT.parent.mkdir(parents=True, exist_ok=True)
    check(flat.Export(str(USD_OUT)), "USD export failed")

    # Preserve source XML verbatim except the selected joint tags and meshdir.
    replaced = set()
    gas_fix = {}
    def replace_joint(match: re.Match) -> str:
        elem = ET.fromstring(match.group(0))
        name = elem.get("name")
        if name not in names:
            return match.group(0)
        side, key = name.split("_", 1)
        low, high = bounds[key]
        if low is None and high is None:
            elem.set("limited", "false")
            elem.attrib.pop("range", None)
        else:
            elem.set("limited", "true")
            elem.set("range", f"{xml_number(low, True)} {xml_number(high, False)}")
        if key == "gas_slide":
            target = spec["gas_law"][f"{side}_target_position_m"]
            old_ref = float(elem.get("springref", "0"))
            check(float(elem.get("stiffness")) == spec["gas_law"]["stiffness_N_m"],
                  f"Source gas stiffness mismatch: {name}")
            check(float(elem.get("damping")) == spec["gas_law"]["damping_N_s_m"],
                  f"Source gas damping mismatch: {name}")
            elem.set("springref", format(target, ".17g"))
            gas_fix[name] = {"legacy_MJCF_springref_m": old_ref,
                             "v2_MJCF_springref_m": target,
                             "constant_force_delta_from_legacy_MJCF_N":
                                 spec["gas_law"]["stiffness_N_m"] * (target - old_ref),
                             "USD_force_law_changed": False,
                             "legacy_MJCF_force_law_changed": True}
        replaced.add(name)
        return ET.tostring(elem, encoding="unicode", short_empty_elements=True)
    xml_text = re.sub(r"<joint\b[^>]*?/>", replace_joint, xml_old_text)
    check(replaced == names, f"MJCF edited joint names mismatch: {names - replaced}")
    def replace_compiler(match: re.Match) -> str:
        elem = ET.fromstring(match.group(0))
        elem.set("meshdir", "assets")
        return ET.tostring(elem, encoding="unicode", short_empty_elements=True)
    xml_text, compiler_count = re.subn(r"<compiler\b[^>]*?/>", replace_compiler, xml_text)
    check(compiler_count == 1, "Expected exactly one compiler tag")
    xml_new = ET.fromstring(xml_text)
    check(xml_structure(xml_old, names) == xml_structure(xml_new, names),
          "MJCF structural invariants changed outside limits/springref/meshdir")
    MJCF_OUT.parent.mkdir(parents=True, exist_ok=True)
    with MJCF_OUT.open("x", encoding="utf-8", newline="\n") as f:
        f.write(xml_text)
    mesh_receipt = []
    for rel, src in sorted(mesh_sources.items()):
        dest = owned_path(MESH_OUT / rel)
        dest.parent.mkdir(parents=True, exist_ok=True)
        check(not dest.exists(), f"Mesh destination already exists: {dest}")
        shutil.copyfile(src, dest)
        mesh_hash = sha256(src)
        check(sha256(dest) == mesh_hash, f"Mesh byte mismatch: {rel}")
        mesh_receipt.append({"path": dest.relative_to(ROOT).as_posix(),
                             "sha256": mesh_hash, "bytes": dest.stat().st_size})

    reopened = Usd.Stage.Open(str(USD_OUT), Usd.Stage.LoadNone)
    check(usd_invariants(reopened, names) == invariant_old,
          "USD body/joint/schema/filter/shape invariants changed outside selected limits")
    check(not reopened.GetRootLayer().subLayerPaths, "Output USD is not independent")
    gas_receipt = {}
    for side in SIDES:
        name = f"{side}_gas_slide"
        prim = reopened.GetPrimAtPath(f"/Robot/joints/{name}")
        drive = UsdPhysics.DriveAPI(prim, "linear")
        native_target = drive.GetTargetPositionAttr().Get()
        target = spec["gas_law"][f"{side}_target_position_m"]
        check(drive.GetStiffnessAttr().Get() == 2000.0 and drive.GetDampingAttr().Get() == 3.0,
              f"Gas k/d changed: {name}")
        check(math.isclose(native_target, target, rel_tol=0, abs_tol=1e-8),
              f"Native USD/contract gas target mismatch exceeds float tolerance: {name}")
        gas_receipt[name] = dict(gas_fix[name], USD_native_target_position_m=native_target,
                                 contract_target_position_m=target,
                                 USD_contract_float_force_difference_N=2000 * (native_target-target),
                                 stiffness_N_m=2000.0, damping_N_s_m=3.0)

    usd_hash, mjcf_hash = sha256(USD_OUT), sha256(MJCF_OUT)
    contract = copy.deepcopy(contract_old)
    historical = {key: copy.deepcopy(contract_old.get(key)) for key in (
        "format_version", "source_mjcf_sha256", "source_usd_sha256", "source_usd_path",
        "derived_from", "enhancement", "training_window", "tendon_translation")}
    contract.update({"format_version": 2, "version": VERSION, "asset_version": "MOD4v2-P0",
                     "source_mjcf_sha256": mjcf_hash, "mjcf_sha256": mjcf_hash,
                     "source_usd_sha256": source["USD_SHA256"], "source_usd_path": source["USD"],
                     "output_usd_sha256": usd_hash, "output_usd_path": "robot.usd",
                     "mjcf_path": "../mjcf/scene.xml", "runtime_tested": False,
                     "legacy_v1_metadata": historical,
                     "inherited_from": {"version": "v1", "USD": source["USD"],
                                        "USD_SHA256": source["USD_SHA256"],
                                        "contract": source["contract"],
                                        "contract_SHA256": source["contract_SHA256"],
                                        "MJCF": source["MJCF"],
                                        "MJCF_SHA256": source_hashes[str(mjcf_source)]},
                     "joint_limit_semantics": {
                         "units": "radian for hinge, metre for slide",
                         "null_lower_endpoint": "negative infinity",
                         "null_upper_endpoint": "positive infinity",
                         "whole_limits_si_null": "No scalar position range; consult joint type",
                         "continuous": "No arbitrary absolute position hard bounds; assembled geometry still applies"}})
    contract["legacy_operating_provenance"] = {
        "enforced_by_default": False,
        "per_joint_limits_si": {n: copy.deepcopy(j.get("limits_si"))
                                for n, j in contract_old["joints"].items()},
        "training_window": copy.deepcopy(contract_old["training_window"]),
        "gas_wrapper_upper_m": spec["gas_extension_evidence"]["reject_400N_wrapper_early_upper_m"]}
    for side in SIDES:
        for key, pair in bounds.items():
            j = contract["joints"][f"{side}_{key}"]
            j["limits_si"] = copy.deepcopy(pair)
            j["continuous"] = key in ACTIVE_AND_FOLLOWER
            j["limited"] = any(x is not None for x in pair)
            j["joint_enabled"] = True
            j["joint_enabled_source"] = "USD schema fallback, unchanged"
            j["lower_limit_enabled"], j["upper_limit_enabled"] = pair[0] is not None, pair[1] is not None
            j["limit_basis"] = ("continuous_active_or_mimic_follower" if key in ACTIVE_AND_FOLLOWER
                                else "CAD_lower_and_restored_upstream_uncalibrated_upper" if key == "gas_slide"
                                else "one_sided_equivalent_of_shared_CAD_stop_group")
    contract["training_window"].update({"enforced_by_default": False, "provenance_only": True})
    contract["mechanical_limits_v2"] = {
        "spec_schema": spec["schema"], "spec_sha256": spec_sha,
        "coordinate_convention": copy.deepcopy(spec["coordinate_convention"]),
        "per_side_joint_bounds_SI": copy.deepcopy(bounds),
        "stop_evidence": copy.deepcopy(spec["stop_evidence"]),
        "gas_extension_evidence": copy.deepcopy(spec["gas_extension_evidence"]),
        "gas_law": copy.deepcopy(spec["gas_law"]), "gas_MJCF_consistency_fix": gas_receipt,
        "training_soft_margin_enabled_by_default": False,
        "runtime_verified": False, "not_claimed": copy.deepcopy(spec["not_claimed"])}
    contract["tendon_translation"] = (
        "No tendons. V2 applies CAD-backed one-sided shared-stop bounds, restored upstream gas upper, "
        "and continuous active/mimic axes in both formats. Legacy operating limits are provenance only.")
    enhancement = contract["enhancement"]
    enhancement.update({"version": "v2-P0-mechanical-limits", "source_root_sha256": source["USD_SHA256"],
                        "source_contract_sha256": source["contract_SHA256"],
                        "output_usd_sha256": usd_hash, "gas400_wrapper_preserved": False,
                        "gas400_force_law_preserved": True, "runtime_verified": False})
    for field in ("bodies", "closures", "mimics", "filters", "geometry", "effort_limits_nm",
                  "actuated_joint_names", "gas_springs", "leg_motor", "wheel_motor",
                  "roller_joints", "roller_parameters"):
        check(contract[field] == contract_old[field], f"Unexpected contract invariant change: {field}")
    write_json_new(CONTRACT_OUT, contract)
    check(all(sha256(Path(path)) == value for path, value in source_hashes.items()),
          "A source input changed during build")
    receipt.update({"status": "BUILT_STATIC_PENDING_MUJOCO_AND_PHYSX_VALIDATION",
                    "outputs": {"USD": {"path": USD_OUT.relative_to(ROOT).as_posix(), "sha256": usd_hash},
                                "MJCF": {"path": MJCF_OUT.relative_to(ROOT).as_posix(), "sha256": mjcf_hash},
                                "contract": {"path": CONTRACT_OUT.relative_to(ROOT).as_posix(),
                                             "sha256": sha256(CONTRACT_OUT)},
                                "builder": {"path": Path(__file__).name, "sha256": sha256(Path(__file__))}},
                    "joint_limits": limit_receipt, "gas_force_law": gas_receipt,
                    "mesh_files": mesh_receipt, "mesh_file_count": len(mesh_receipt),
                    "mesh_bytes_unchanged": True, "MJCF_meshdir": "assets",
                    "USD_inline_geometry_no_asset_dependencies": True,
                    "USD_31_bodies_36_joints_structure_preserved": True,
                    "USD_nonlimit_joint_attrs_and_contact_filters_preserved": True,
                    "MJCF_31_bodies_structure_preserved_except_declared_changes": True,
                    "USD_and_contract_gas_law_preserved": True,
                    "legacy_MJCF_force_law_changed_to_match_native_USD_contract": True,
                    "original_sources_unchanged": True,
                    "mujoco_compile_verified": False, "physx_runtime_verified": False,
                    "simulation_started": False, "training_started": False,
                    "single_sided_MJCF_syntax": "limited=true with finite/inf endpoint; compiler angle=radian",
                    "pending_validation": ["parent MuJoCo actual compilation and numeric boundary checks",
                                           "target PhysX import/runtime", "physical maximum gas stroke measurement"],
                    "not_claimed": spec["not_claimed"]})


def main() -> int:
    owned_path(RECEIPT_OUT)
    check(not RECEIPT_OUT.exists(), "Existing BUILD_RECEIPT retained; this is a one-shot builder")
    receipt = {"schema": "mod4v2.p0.build_receipt.v1", "started_at": utc_now(),
               "status": "BUILD_STARTED", "writes_confined_to_owned_outputs": True,
               "no_IsaacSDK_GPU_MuJoCo_simulation_or_training_imports": True}
    result = 0
    try:
        build(receipt)
    except Exception as error:
        receipt.update({"status": "BUILD_FAILED_RETAINED", "error": str(error),
                        "traceback": traceback.format_exc(), "partial_outputs_retained": True})
        traceback.print_exc()
        result = 1
    finally:
        receipt["finished_at"] = utc_now()
        write_json_new(RECEIPT_OUT, receipt)
    print(json.dumps({"status": receipt["status"], "receipt": str(RECEIPT_OUT),
                      "outputs": receipt.get("outputs", {}),
                      "mesh_file_count": receipt.get("mesh_file_count")}, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    sys.exit(main())
