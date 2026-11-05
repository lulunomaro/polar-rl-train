#!/usr/bin/env python3
"""One-shot, opt-in MOD4v2-HW300N60 asset builder (standard library + pxr).

Default output: candidates/HW300N60, never the frozen pre-clarification package.
Usage: python -B build_mod4v2_hw300n60_assets.py [--spec FILE] [--output-dir DIR]
The output directory is the candidate root, containing package/ and receipt.
No Isaac/MuJoCo/GPU/training imports. Existing outputs are retained, not replaced.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import sys
import traceback
import xml.etree.ElementTree as ET
from pxr import Sdf, Usd, UsdPhysics

PROJECT = Path(__file__).resolve().parent
VERSION = "MOD4v2-HW300N60"
SIDES = ("left", "right")
CONTINUOUS = {"hip", "crank", "drive_hip_spin", "drive_input_spin"}
TARGET_ATTR = "drive:linear:physics:targetPosition"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write("\n")


def number(value, lower):
    return ("-inf" if lower else "inf") if value is None else format(value, ".17g")


def null_inf(value):
    return float(value) if math.isfinite(value) else None


def invariant(stage, edited):
    """Structural/body/joint signature, excluding only declared bound/target edits."""
    result = {"bodies": {}, "joints": {}, "shapes": [], "filtered_pairs": {}}
    for p in stage.Traverse():
        path = str(p.GetPath())
        if p.HasAPI(UsdPhysics.RigidBodyAPI):
            result["bodies"][path] = {a.GetName(): str(a.Get()) for a in p.GetAttributes()
                                      if a.HasAuthoredValueOpinion()}
        rel = p.GetRelationship("physics:filteredPairs")
        if rel:
            result["filtered_pairs"][path] = [str(t) for t in rel.GetTargets()]
        if p.IsA(UsdPhysics.Joint):
            attrs = {}
            for a in p.GetAttributes():
                if p.GetName() in edited and a.GetName() in {"physics:lowerLimit", "physics:upperLimit"}:
                    continue
                if p.GetName() in {"left_gas_slide", "right_gas_slide"} and a.GetName() == TARGET_ATTR:
                    continue
                if a.HasAuthoredValueOpinion():
                    attrs[a.GetName()] = str(a.Get())
            result["joints"][path] = {
                "type": p.GetTypeName(), "schemas": str(p.GetMetadata("apiSchemas")), "attrs": attrs,
                "relationships": {r.GetName(): [str(t) for t in r.GetTargets()] for r in p.GetRelationships()}}
        if p.GetTypeName() in {"Mesh", "Capsule", "Cube", "Cylinder", "Sphere"}:
            result["shapes"].append((path, p.GetTypeName(), p.HasAPI(UsdPhysics.CollisionAPI)))
    return result


def xml_invariant(element, edited):
    attrs = dict(element.attrib)
    if element.tag == "compiler":
        attrs.pop("meshdir", None)
    if element.tag == "joint" and attrs.get("name") in edited:
        attrs.pop("range", None)
        attrs.pop("limited", None)
        if attrs["name"].endswith("_gas_slide"):
            attrs.pop("springref", None)
    return element.tag, tuple(sorted(attrs.items())), tuple(xml_invariant(c, edited) for c in element)


def build(spec_path, candidate, receipt):
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    require(spec["schema"] == "mod4v2.p0.mechanical_limits.HW300N60.v1", "Wrong hardware spec schema")
    hw, law, bounds = spec["hardware_configuration"], spec["gas_law"], spec["per_side_joint_bounds_SI"]
    require(hw["hardware_spec_status"] == "CONFIRMED", "Hardware definition is not confirmed")
    require(hw["stroke_m"] == .06 and hw["extended_eye_length_m"] == .2, "Wrong confirmed stroke")
    require(hw["nominal_extension_force_N"] == 300, "Wrong nominal extension force")
    require(math.isclose(bounds["gas_slide"][1] - bounds["gas_slide"][0], .06, abs_tol=1e-15), "Slide stroke mismatch")
    source = spec["source"]
    usd_src, contract_src, xml_src = (Path(source[k]) for k in ("USD", "contract", "MJCF"))
    pinned = {str(p): sha(p) for p in (usd_src, contract_src, xml_src, spec_path)}
    require(pinned[str(usd_src)] == source["USD_SHA256"], "Pinned source USD hash mismatch")
    require(pinned[str(contract_src)] == source["contract_SHA256"], "Pinned source contract hash mismatch")
    # Freeze protection is observational: no file here is ever opened for writing.
    frozen = {str(p): sha(p) for p in (PROJECT / "build_mod4v2_assets.py", PROJECT / "BUILD_RECEIPT.json",
              PROJECT / "package/assets/robot.usd", PROJECT / "package/assets/import_contract.json",
              PROJECT / "package/mjcf/scene.xml") if p.is_file()}
    old = json.loads(contract_src.read_text(encoding="utf-8"))
    text_old = xml_src.read_text(encoding="utf-8")
    xml_old = ET.fromstring(text_old)
    require(xml_old.find("compiler").get("angle") == "radian", "Source angle must be radian")
    require(len(xml_old.findall("./worldbody//body")) == 31, "MJCF source must have 31 bodies")
    edited = {f"{side}_{key}" for side in SIDES for key in bounds}
    require(len(edited) == 20 and edited.issubset(old["joints"]), "Unexpected edited joint set")
    package = candidate / "package"
    out_usd, out_contract = package / "assets/robot.usd", package / "assets/import_contract.json"
    out_xml, out_mesh = package / "mjcf/scene.xml", package / "mjcf/assets"
    for p in (out_usd, out_contract, out_xml, out_mesh):
        require(p.resolve().is_relative_to(candidate), f"Output escaped candidate: {p}")
        require(not p.exists(), f"Existing output retained: {p}")
    meshroot = Path(xml_old.find("compiler").get("meshdir", ""))
    if not meshroot.is_absolute():
        meshroot = xml_src.parent / meshroot
    meshes = {}
    for element in xml_old.findall("./asset/mesh"):
        rel = Path(element.get("file"))
        require(not rel.is_absolute() and ".." not in rel.parts, f"Unexpected mesh reference: {rel}")
        src = (meshroot / rel).resolve()
        require(src.is_file(), f"Missing mesh: {src}")
        meshes[rel.as_posix()] = src
    receipt.update({"source_files_sha256": pinned, "frozen_preclarification_files_sha256": frozen,
                    "spec_sha256": pinned[str(spec_path)], "hardware_configuration": copy.deepcopy(hw),
                    "force_curve_status": "ENGINEERING_SURROGATE_K2000_D3_NOT_MEASURED"})

    source_stage = Usd.Stage.Open(str(usd_src), Usd.Stage.LoadNone)
    require(bool(source_stage), "Source USD open failed")
    baseline = invariant(source_stage, edited)
    require(len(baseline["bodies"]) == 31 and len(baseline["joints"]) == 36, "Unexpected USD counts")
    for p in source_stage.Traverse():
        for a in p.GetAttributes():
            if a.HasAuthoredValueOpinion() and a.GetTypeName() in (Sdf.ValueTypeNames.Asset, Sdf.ValueTypeNames.AssetArray):
                require(not a.Get(), f"Unpackaged external USD asset: {a.GetPath()}")
    flat = source_stage.Flatten()
    stage = Usd.Stage.Open(flat)
    limits, gas_changes = {}, {}
    for side in SIDES:
        for key, pair in bounds.items():
            name = f"{side}_{key}"
            p = stage.GetPrimAtPath(f"/Robot/joints/{name}")
            require(bool(p), f"Missing USD joint: {name}")
            angular = key != "gas_slide"
            joint = UsdPhysics.RevoluteJoint(p) if angular else UsdPhysics.PrismaticJoint(p)
            values = [(-math.inf if i == 0 else math.inf) if v is None else math.degrees(v) if angular else v
                      for i, v in enumerate(pair)]
            joint.GetLowerLimitAttr().Set(values[0])
            joint.GetUpperLimitAttr().Set(values[1])
            require(UsdPhysics.Joint(p).GetJointEnabledAttr().Get() is True, f"Disabled source joint: {name}")
            limits[name] = {"limits_si": pair, "USD_unit": "degree" if angular else "m",
                            "USD_after": [null_inf(joint.GetLowerLimitAttr().Get()), null_inf(joint.GetUpperLimitAttr().Get())],
                            "continuous": key in CONTINUOUS, "joint_enabled": True,
                            "joint_enabled_authored": UsdPhysics.Joint(p).GetJointEnabledAttr().HasAuthoredValueOpinion()}
            if key == "gas_slide":
                drive = UsdPhysics.DriveAPI(p, "linear")
                before = drive.GetTargetPositionAttr().Get()
                require(drive.GetStiffnessAttr().Get() == law["stiffness_N_m"], "Source gas k mismatch")
                require(drive.GetDampingAttr().Get() == law["damping_N_s_m"], "Source gas damping mismatch")
                drive.GetTargetPositionAttr().Set(law[f"{side}_target_position_m"])
                gas_changes[name] = {"source_USD_target_position_m": before,
                                      "v2_contract_target_position_m": law[f"{side}_target_position_m"],
                                      "v2_USD_target_position_m": drive.GetTargetPositionAttr().Get(),
                                      "USD_force_law_changed_from_legacy400N": True}

    replaced = set()
    def joint_tag(match):
        e = ET.fromstring(match.group(0)); name = e.get("name")
        if name not in edited:
            return match.group(0)
        side, key = name.split("_", 1); pair = bounds[key]
        if pair == [None, None]:
            e.set("limited", "false"); e.attrib.pop("range", None)
        else:
            e.set("limited", "true"); e.set("range", f"{number(pair[0], True)} {number(pair[1], False)}")
        if key == "gas_slide":
            require(float(e.get("stiffness")) == law["stiffness_N_m"] and float(e.get("damping")) == law["damping_N_s_m"],
                    f"Source MJCF gas k/d mismatch: {name}")
            old_ref = float(e.get("springref", "0")); target = law[f"{side}_target_position_m"]
            e.set("springref", format(target, ".17g"))
            gas_changes[name].update({"source_MJCF_springref_m": old_ref, "v2_MJCF_springref_m": target,
                                     "constant_force_delta_vs_source_MJCF_N": law["stiffness_N_m"] * (target-old_ref),
                                     "constant_force_delta_vs_source_contract_N": law["stiffness_N_m"] *
                                         (target-old["gas_springs"][name]["target_position_m"]),
                                     "legacy_MJCF_force_law_changed": True})
        replaced.add(name)
        return ET.tostring(e, encoding="unicode", short_empty_elements=True)
    text = re.sub(r"<joint\b[^>]*?/>", joint_tag, text_old)
    require(replaced == edited, "MJCF edited joint set mismatch")
    def compiler_tag(match):
        e = ET.fromstring(match.group(0)); e.set("meshdir", "assets")
        return ET.tostring(e, encoding="unicode", short_empty_elements=True)
    text, n = re.subn(r"<compiler\b[^>]*?/>", compiler_tag, text)
    require(n == 1, "Expected one MJCF compiler")
    xml_new = ET.fromstring(text)
    require(xml_invariant(xml_old, edited) == xml_invariant(xml_new, edited), "Unexpected MJCF structural change")
    out_xml.parent.mkdir(parents=True, exist_ok=True)
    with out_xml.open("x", encoding="utf-8", newline="\n") as f:
        f.write(text)
    mesh_receipt = []
    for rel, src in sorted(meshes.items()):
        dst = out_mesh / rel
        require(dst.resolve().is_relative_to(candidate), "Mesh destination escaped candidate")
        dst.parent.mkdir(parents=True, exist_ok=True)
        require(not dst.exists(), f"Existing mesh retained: {dst}")
        shutil.copyfile(src, dst)
        digest = sha(src); require(sha(dst) == digest, f"Mesh bytes changed: {rel}")
        mesh_receipt.append({"path": dst.relative_to(candidate).as_posix(), "sha256": digest, "bytes": dst.stat().st_size})
    xml_sha = sha(out_xml)
    # Stamp the actual current version, retaining source metadata as provenance.
    root = stage.GetPrimAtPath("/Robot")
    root_custom = copy.deepcopy(root.GetCustomData())
    inherited_root_custom = copy.deepcopy(root_custom)
    mod4 = root_custom.setdefault("mod4", {})
    mod4["inheritedV1SourceSha256"] = mod4.get("sourceSha256", "")
    mod4["sourceSha256"] = xml_sha
    mod4["assetVersion"] = VERSION
    mod4["hardwareConfiguration"] = copy.deepcopy(hw)
    mod4["gasLaw"] = copy.deepcopy(law)
    enhancement = mod4.setdefault("enhancement", {})
    enhancement.update({"version": VERSION, "gas400_wrapper_preserved": False,
                        "gas300_hw60_configuration": True, "gas400_force_law_preserved": False,
                        "source_root_sha256": source["USD_SHA256"],
                        "source_contract_sha256": source["contract_SHA256"], "runtime_verified": False})
    root.SetCustomData(root_custom)
    data = dict(flat.customLayerData)
    data.update({"mod4EnhancementVersion": VERSION, "mod4_asset_version": VERSION,
                 "sourceRootSHA256": source["USD_SHA256"], "specSHA256": pinned[str(spec_path)],
                 "hardware_spec_status": "CONFIRMED", "gas_nominal_extension_force_N": 300.0,
                 "gas_stroke_m": .06, "gas_extended_eye_m": .2,
                 "gas_force_curve_calibrated": False, "runtime_verified": False})
    flat.customLayerData = data
    out_usd.parent.mkdir(parents=True, exist_ok=True)
    require(flat.Export(str(out_usd)), "USD export failed")
    reopened = Usd.Stage.Open(str(out_usd), Usd.Stage.LoadNone)
    require(invariant(reopened, edited) == baseline, "USD invariants changed outside declared bounds/gas target")
    require(not reopened.GetRootLayer().subLayerPaths, "USD is not independent")
    endpoint_checks = {}
    for side in SIDES:
        name = f"{side}_gas_slide"; pair = bounds["gas_slide"]
        target = law[f"{side}_target_position_m"]
        drive = UsdPhysics.DriveAPI(reopened.GetPrimAtPath(f"/Robot/joints/{name}"), "linear")
        require(math.isclose(drive.GetTargetPositionAttr().Get(), target, rel_tol=0, abs_tol=1e-8), "USD target float mismatch")
        extension_force = law["stiffness_N_m"] * (target-pair[1])
        compressed_force = law["stiffness_N_m"] * (target-pair[0])
        require(math.isclose(extension_force, 300, abs_tol=1e-10), "Extension force is not 300N")
        require(math.isclose(compressed_force, 420, abs_tol=1e-10), "Compressed engineering force is not 420N")
        require(math.isclose(hw["neutral_eye_length_m"]+pair[0], .14, abs_tol=1e-15), "Compressed eye length mismatch")
        require(math.isclose(hw["neutral_eye_length_m"]+pair[1], .2, abs_tol=1e-15), "Extended eye length mismatch")
        endpoint_checks[name] = {"compressed_eye_m": .14, "extended_eye_m": .2, "stroke_m": .06,
                                 "zero_velocity_extension_force_N": extension_force,
                                 "zero_velocity_compressed_force_N": compressed_force,
                                 "force_curve_calibrated": False, "damping_calibrated": False}

    usd_sha = sha(out_usd)
    contract = copy.deepcopy(old)
    history_keys = ("format_version", "source_mjcf_sha256", "source_usd_sha256", "source_usd_path",
                    "derived_from", "enhancement", "training_window", "tendon_translation", "gas_springs", "mechanical_stop")
    contract.update({"format_version": 2, "version": VERSION, "asset_version": VERSION,
                     "source_mjcf_sha256": xml_sha, "mjcf_sha256": xml_sha,
                     "source_usd_sha256": source["USD_SHA256"], "source_usd_path": source["USD"],
                     "output_usd_sha256": usd_sha, "output_usd_path": "robot.usd",
                     "mjcf_path": "../mjcf/scene.xml", "runtime_tested": False,
                     "hardware_configuration": copy.deepcopy(hw),
                     "legacy_v1_metadata": {k: copy.deepcopy(old.get(k)) for k in history_keys},
                     "inherited_v1_root_custom_data": inherited_root_custom,
                     "inherited_from": {"version": "v1", "USD": source["USD"], "USD_SHA256": source["USD_SHA256"],
                                        "contract": source["contract"], "contract_SHA256": source["contract_SHA256"],
                                        "MJCF": source["MJCF"], "MJCF_SHA256": pinned[str(xml_src)]},
                     "joint_limit_semantics": {"units": "radian hinge / metre slide",
                         "null_lower_endpoint": "negative infinity", "null_upper_endpoint": "positive infinity",
                         "whole_limits_si_null": "No scalar position range; consult joint type",
                         "continuous": "No arbitrary absolute position bound; assembly/collision still applies"}})
    contract["legacy_operating_provenance"] = {
        "enforced_by_default": False,
        "per_joint_limits_si": {n: copy.deepcopy(j.get("limits_si")) for n, j in old["joints"].items()},
        "training_window": copy.deepcopy(old["training_window"]),
        "old400N_candidate_superseded": True}
    for side in SIDES:
        for key, pair in bounds.items():
            j = contract["joints"][f"{side}_{key}"]
            j.update({"limits_si": copy.deepcopy(pair), "continuous": key in CONTINUOUS,
                      "limited": any(v is not None for v in pair), "joint_enabled": True,
                      "joint_enabled_source": "USD schema fallback, unchanged",
                      "lower_limit_enabled": pair[0] is not None, "upper_limit_enabled": pair[1] is not None,
                      "limit_basis": "confirmed_140_to_200mm_hardware_stroke" if key == "gas_slide" else
                                     "continuous_active_or_mimic" if key in CONTINUOUS else "shared_CAD_stop_one_sided_equivalent"})
        spring = contract["gas_springs"][f"{side}_gas_slide"]
        spring.update({"target_position_m": law[f"{side}_target_position_m"],
                       "nominal_extension_force_n": 300.0, "stroke_m": .06,
                       "compressed_eye_length_m": .14, "extended_eye_length_m": .2,
                       "stiffness_status": law["stiffness_status"], "damping_status": law["damping_status"],
                       "force_curve_calibrated": False, "damping_calibrated": False,
                       "force_reference_convention": law["force_reference_convention"]})
    contract["mechanical_stop"]["passive_bounds"]["rocker_pin"]["min"] = bounds["rocker_pin"][0]
    contract["mechanical_stop"].update({"v2_numeric_consistency_basis": spec["stop_evidence"]["rocker_new_value_basis"],
        "gas_value_is_mechanism_lowfold_not_slider_hardware_lower": True,
        "user_stop_description": "Actual stop between shin and linkage; CAD equivalent group retained, no new mesh contact"})
    contract["training_window"].update({"enforced_by_default": False, "provenance_only": True})
    contract["mechanical_limits_v2"] = {"spec_schema": spec["schema"], "spec_sha256": pinned[str(spec_path)],
        "coordinate_convention": copy.deepcopy(spec["coordinate_convention"]),
        "per_side_joint_bounds_SI": copy.deepcopy(bounds), "stop_evidence": copy.deepcopy(spec["stop_evidence"]),
        "gas_extension_evidence": copy.deepcopy(spec["gas_extension_evidence"]), "gas_law": copy.deepcopy(law),
        "gas_force_law_changes": gas_changes, "gas_endpoint_static_checks": endpoint_checks,
        "training_soft_margin_enabled_by_default": False, "runtime_verified": False,
        "screenshot_required_to_pass": False, "not_claimed": copy.deepcopy(spec["not_claimed"])}
    contract["tendon_translation"] = "No tendons. HW300N60 uses confirmed gas stroke and CAD shared-stop one-sided equivalents; old operating boxes are provenance only."
    enhancement = contract["enhancement"]
    enhancement.update({"version": VERSION, "source_root_sha256": source["USD_SHA256"],
                        "source_contract_sha256": source["contract_SHA256"], "output_usd_sha256": usd_sha,
                        "gas400_wrapper_preserved": False, "gas400_force_law_preserved": False,
                        "gas300_hw60_configuration": True, "runtime_verified": False})
    enhancement["runtime_requirements"].update({"gas_nominal_force_n": 300,
                                               "gas_stiffness_status": law["stiffness_status"],
                                               "gas_damping_status": law["damping_status"]})
    for field in ("bodies", "closures", "mimics", "filters", "geometry", "actuated_joint_names", "effort_limits_nm",
                  "leg_motor", "wheel_motor", "roller_joints", "roller_parameters"):
        require(contract[field] == old[field], f"Contract invariant changed: {field}")
    write_json(out_contract, contract)
    require(all(sha(p) == v for p, v in pinned.items()), "A pinned source input changed during build")
    require(all(sha(p) == v for p, v in frozen.items()), "Frozen pre-clarification file changed during build")
    receipt.update({"status": "BUILT_STATIC_PENDING_MUJOCO_AND_PHYSX_VALIDATION",
        "outputs": {"USD": {"path": out_usd.relative_to(candidate).as_posix(), "sha256": usd_sha},
                    "MJCF": {"path": out_xml.relative_to(candidate).as_posix(), "sha256": xml_sha},
                    "contract": {"path": out_contract.relative_to(candidate).as_posix(), "sha256": sha(out_contract)},
                    "builder": {"path": str(Path(__file__).resolve()), "sha256": sha(__file__)}},
        "joint_limits": limits, "gas_force_law_changes": gas_changes, "gas_endpoint_static_checks": endpoint_checks,
        "mesh_files": mesh_receipt, "mesh_file_count": len(mesh_receipt), "mesh_bytes_unchanged": True,
        "MJCF_meshdir": "assets", "USD_inline_geometry_no_external_assets": True,
        "31_body_36_USD_joint_invariants_preserved": True,
        "USD_nonlimit_and_nongas_target_joint_attributes_and_filters_preserved": True,
        "MJCF_structure_unchanged_except_limits_springref_meshdir": True,
        "source_and_frozen_preclarification_files_unchanged": True,
        "new_hardware_stroke_confirmed_not_fitted_to_screenshot": True,
        "old_screenshot_inside_current_hardware_stroke": False,
        "mujoco_compile_verified": False, "physx_runtime_verified": False,
        "simulation_started": False, "training_started": False,
        "pending_validation": ["parent actual MuJoCo compilation and numeric checks", "target PhysX import/runtime",
                               "measured full spring force/damping curve"], "not_claimed": spec["not_claimed"]})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=PROJECT / "MECHANICAL_LIMITS_SPEC_V2_HW300N60.json")
    parser.add_argument("--output-dir", type=Path, default=PROJECT / "candidates/HW300N60")
    args = parser.parse_args()
    spec_path = args.spec.resolve()
    candidate = args.output_dir.resolve()
    require(candidate.parent == (PROJECT / "candidates").resolve(), "Output must be a direct child of project candidates/")
    require(candidate.name != "", "Empty candidate name")
    receipt_path = candidate / "BUILD_RECEIPT.json"
    require(not receipt_path.exists(), "Existing receipt retained; one-shot candidate build")
    receipt = {"schema": "mod4v2.HW300N60.build_receipt.v1", "version": VERSION,
               "started_at": now(), "status": "BUILD_STARTED", "spec_path": str(spec_path),
               "candidate_path": str(candidate), "writes_confined_to_candidate": True,
               "no_IsaacSDK_MuJoCo_GPU_simulation_or_training_imports": True}
    result = 0
    try:
        build(spec_path, candidate, receipt)
    except Exception as error:
        receipt.update({"status": "BUILD_FAILED_RETAINED", "error": str(error),
                        "traceback": traceback.format_exc(), "partial_outputs_retained": True})
        traceback.print_exc(); result = 1
    finally:
        receipt["finished_at"] = now()
        write_json(receipt_path, receipt)
    print(json.dumps({"status": receipt["status"], "version": VERSION, "receipt": str(receipt_path),
                      "outputs": receipt.get("outputs", {}), "mesh_file_count": receipt.get("mesh_file_count")},
                     indent=2, ensure_ascii=False))
    return result


if __name__ == "__main__":
    sys.exit(main())
