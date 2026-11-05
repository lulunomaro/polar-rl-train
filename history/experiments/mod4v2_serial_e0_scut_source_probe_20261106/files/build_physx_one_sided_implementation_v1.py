#!/usr/bin/env python3
"""Opt-in HW300N60 PhysX coordinate-representation candidate; SOURCE ONLY until run.

Use the existing pxr environment, without installing anything:
  C:/Users/lulu/Desktop/claude/mjcf/.venv/Scripts/python.exe -B THIS_FILE

Reads only the pinned HW300N60 mechanical package/spec. Creates the NEW directory
  mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60_PHYSX_REPR_V2/package
and retains any existing/partial output instead of replacing it. No SDK, MuJoCo,
GPU, training, PT/model, oldraw, JSONL, network, canonical or Git operations.

Observed old native getter: all ten one-sided passive hinges lost BOTH bounds;
the eight continuous active/follower axes and two double-finite sliders behaved
as expected. This is a finite-pair implementation candidate, NOT a native pass.
The parent must demonstrate all 20 joint limits with the actual native getter.

Proof scope: original neutral-signed source branch, canonical RELATIVE passive
coordinates, delta=[-1.0863195404360622, 0.49192233306644084]. The actual source
maps every passive q to [-pi, pi), contained in the CLOSED native [-pi, pi]
coordinate interval. Common hip/crank rotation leaves delta and passive q unchanged.
Added +/-pi endpoints are ONLY backend representation endpoints, never newly
measured hardware stops. Their pairs have span <2*pi; +/-2*pi API support is not
assumed. This is a set-inclusion proof, NOT a strict-interior-margin certificate
at -pi. No claim about other assembly branches, arbitrary passive winding or
3-D collision freedom.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import sys
import xml.etree.ElementTree as ET

IMPLEMENTATION = "HW300N60_PHYSX_REPR_V2"
SCHEMA = "mod4v2.native_coordinate_representation.v1"
SPEC_NAME = "MECHANICAL_LIMITS_SPEC_V2_HW300N60.json"
SPEC_SHA = "57d129d5116dd4d2655e9aae8ec57179d8041e368a97b238fd4d0c03804da005"
P0_DEFAULT = Path(__file__).resolve().parent.parent / "mod4v2_p0_mechanical_limits_20261105"
SIDES = ("left", "right")
PASSIVE = ("rocker_pin", "coupler_pin", "knee", "distal_pin", "gas_pin")
CONTINUOUS = ("hip", "crank", "drive_hip_spin", "drive_input_spin")
TAU = 2.0 * math.pi
REPRESENTATION_ENDPOINT = math.pi
DELTA = [-1.0863195404360622, 0.49192233306644084]
SOURCE_SHA = {
    "assets/robot.usd": "2237070ddc0a4e33f0c28e23fe5bb3db1f12bb619fddcdd89f9a74d5ac875f18",
    "assets/import_contract.json": "00199c26533a9adaca6a35a49d30e8b8b27182230772674bd936d8b527169f4e",
    "mjcf/scene.xml": "c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125",
    "kinematics_v2.py": "26ef50347dab961ed75fedff410659614e20dc1252946c4a42998a476110df64",
    "model_parameters.json": "35122ac4ee8e1558d8c9f00b39a993033e0456bf51767dcccbfb13d29b8882d4",
    "reports/model_manifest.json": "9b3650f2942f7290c11d7a500b27f7688610bda748503eb8da86cd4f2ca36578",
    "runtime_adapter_v2.py": "148cbfdfab17e9bad04c5974c196279200c645af31e2f0b70ea8aa474ee82d98",
    "runtime_requirements.json": "754811b25f44963e27f44dc260f0ae94750978369dc9df727509a724d800eb45",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def put_json(path, value):
    # These paths are exclusively owned by the freshly created output candidate.
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False,
                                    allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def source_coordinate_proof(source, params):
    """Algebraic enclosure from pinned executable expressions, NOT sampled extrema."""
    text = (source / "kinematics_v2.py").read_text(encoding="utf-8")
    for expression in (
        "TAU = 2.0 * math.pi",
        "return (value + math.pi) % TAU - math.pi",
        'for name in ("rocker_pin", "coupler_pin", "knee", "distal_pin", "gas_pin"):',
        "values[name] = (values[name] + math.pi) % TAU - math.pi",
        "delta = crank - hip",
        "values, local_pins = _local_configuration(delta, side)",
        "values.update(hip=hip, crank=crank, drive_hip_spin=hip, drive_input_spin=crank)",
    ):
        need(expression in text, "Reviewed source coordinate expression changed: " + expression)
    for side in SIDES:
        need(params["derived_continuous_delta_bounds_rad"][side] == DELTA,
             "Source continuous branch changed")
        need(params["continuous_branch_derivation"][side]["upper_active_constraints"] == ["gas_slide:upper"],
             "Source upper mechanical event changed")
    # C is the actual canonical source-branch image; H is the original hardware
    # domain and R=[-pi,pi]. C is a subset of R, hence C intersect H intersect R
    # equals C intersect H. This proves no canonical state is clipped, including
    # a possible q=-pi; it does NOT invent a strictly positive boundary margin.
    return {
        "method": "pinned_actual_kinematics_coordinate_range_theorem_not_pose_sampling",
        "kinematics_sha256": SOURCE_SHA["kinematics_v2.py"],
        "source_lines": {"angle_range": [36, 38], "relative_q": [68, 81],
                         "common_rotation": [227, 242]},
        "scope": "source neutral-signed assembly branch canonical relative coordinates only",
        "delta_by_side_rad": {side: list(DELTA) for side in SIDES},
        "passive_names_per_side": list(PASSIVE),
        "identity": "q=(raw_q+pi)%(2*pi)-pi => -pi<=q<pi; C subset R=[-pi,pi] => C intersect H intersect R = C intersect H",
        "canonical_enclosure_rad": [-math.pi, math.pi],
        "canonical_enclosure_upper_open": True,
        "native_limit_endpoints_inclusive": True,
        "passive_finite_pair_spans_strictly_below_2pi": True,
        "canonical_state_domain_unchanged": True,
        "strict_interior_margin_at_minus_pi_proven": False,
        "source_comment_not_used_as_numeric_extrema_certificate": True,
        "common_turn_identity": "(crank+alpha)-(hip+alpha)=delta; local solve has no hip input; final values.update changes only four active/follower coordinates",
        "continuous_active_or_follower_position_box_added": False,
        "new_measured_hardware_stop": False,
        "not_claimed": ["other assembly branches", "arbitrary passive-coordinate winding",
                        "3D collision-free common rotations", "native SDK acceptance"],
    }


# Inserted only into the NEW package adapter. It validates BOTH semantic layers;
# the original mechanical comparison loop remains in force against the native pair.
ADAPTER_HELPER = '''def _native_representation(contract, bounds):
    """Keep hardware one-sided semantics distinct from backend finite coordinates."""
    passive = ("rocker_pin", "coupler_pin", "knee", "distal_pin", "gas_pin")
    continuous = ("hip", "crank", "drive_hip_spin", "drive_input_spin")
    req = _requirements().get("native_implementation", {})
    impl = contract.get("native_impl_limits", {})
    if (req.get("schema") != "mod4v2.native_coordinate_representation.v1" or
            impl.get("schema") != req.get("schema") or
            req.get("implementation") != "HW300N60_PHYSX_REPR_V2" or
            impl.get("implementation") != req.get("implementation") or
            impl.get("representation_endpoint_rad") != math.pi or
            impl.get("added_endpoints_are_hardware_stops") is not False or
            impl.get("hardware_spec_sha256") != req.get("hardware_spec_sha256") or
            req.get("hardware_spec_sha256") != "57d129d5116dd4d2655e9aae8ec57179d8041e368a97b238fd4d0c03804da005"):
        raise ValueError("Missing or inconsistent HW300N60 native representation provenance")
    if contract["mechanical_limits_v2"]["per_side_joint_bounds_SI"] != bounds:
        raise ValueError("Hardware geometry bounds changed under native representation")
    expected_native, expected_one_sided = {}, {}
    for side in ("left", "right"):
        for key, hardware in bounds.items():
            name = side + "_" + key
            pair = list(hardware)
            roles = ["hardware" if value is not None else "unbounded" for value in pair]
            if key in passive:
                if sum(value is None for value in pair) != 1:
                    raise ValueError("Expected original single-sided hardware stop: " + name)
                expected_one_sided[name] = list(pair)
                for index, value in enumerate(pair):
                    if value is None:
                        pair[index] = -math.pi if index == 0 else math.pi
                        roles[index] = "native_coordinate_representation_only"
            elif key in continuous:
                if pair != [None, None]:
                    raise ValueError("Continuous active/follower gained a bound: " + name)
            elif key != "gas_slide" or None in pair:
                raise ValueError("Unexpected native representation joint: " + name)
            joint = contract["joints"][name]
            if (joint.get("hardware_limits_si") != hardware or
                    joint.get("native_impl_limits_si") != pair or
                    joint.get("limit_endpoint_roles") != roles or
                    joint.get("continuous") is not (key in continuous) or
                    joint.get("limited") is not any(value is not None for value in pair) or
                    joint.get("lower_limit_enabled") is not (pair[0] is not None) or
                    joint.get("upper_limit_enabled") is not (pair[1] is not None)):
                raise ValueError("Native/hardware endpoint declaration differs: " + name)
            expected_native[name] = pair
    if (impl.get("per_joint_limits_si") != expected_native or
            contract.get("hardware_one_sided_limits") != expected_one_sided):
        raise ValueError("Native pairs or original CAD one-sided endpoints changed")
    pins = req.get("bindings_sha256", {})
    required = {"assets/robot.usd", "assets/import_contract.json", "mjcf/scene.xml",
                "kinematics_v2.py", "model_parameters.json", "reports/model_manifest.json",
                "runtime_adapter_v2.py"}
    if set(pins) != required:
        raise ValueError("Incomplete new-package native representation bindings")
    for relative, expected_sha in pins.items():
        if hashlib.sha256((HERE / relative).read_bytes()).hexdigest() != expected_sha:
            raise ValueError("New native representation package binding changed: " + relative)
    if impl.get("coordinate_proof", {}).get("kinematics_sha256") != pins["kinematics_v2.py"]:
        raise ValueError("Native representation theorem is not bound to this geometry source")
    return expected_native


'''


def new_adapter(source_text):
    marker = "def _contract():\n"
    need(source_text.count(marker) == 1, "Adapter _contract ABI changed")
    text = source_text.replace(marker, ADAPTER_HELPER + marker, 1)
    old = "    bounds = _geometry().JOINT_BOUNDS\n"
    need(text.count(old) == 1, "Adapter hardware-bound read ABI changed")
    text = text.replace(old, old + "    native_expected = _native_representation(contract, bounds)\n", 1)
    old = '            actual = contract["joints"][side + "_" + name]["limits_si"]\n'
    need(text.count(old) == 1, "Adapter endpoint comparison ABI changed")
    return text.replace(old, old + '            expected = native_expected[side + "_" + name]\n', 1)


def xml_signature(element, changed):
    attrs = dict(element.attrib)
    if element.tag == "joint" and attrs.get("name") in changed:
        attrs.pop("range", None)
    return element.tag, tuple(sorted(attrs.items())), tuple(xml_signature(child, changed) for child in element)


def build(project):
    source = (project / "candidates/HW300N60/package").resolve()
    candidate = (project / "candidates" / IMPLEMENTATION).resolve()
    output = candidate / "package"
    need(candidate.parent == (project / "candidates").resolve() and candidate != source.parent,
         "Output must be the distinct new representation candidate")
    need(not candidate.exists(), "Existing/partial candidate retained; choose no overwrite or automatic replay")
    spec_path = project / SPEC_NAME
    need(sha(spec_path) == SPEC_SHA, "Original hardware spec changed")
    for relative, expected in SOURCE_SHA.items():
        need(sha(source / relative) == expected, "Pinned mechanical source changed: " + relative)
    spec = load(spec_path)
    params = load(source / "model_parameters.json")
    original = load(source / "assets/import_contract.json")
    hardware = spec["per_side_joint_bounds_SI"]
    need(hardware == params["per_side_joint_bounds_SI"] == original["mechanical_limits_v2"]["per_side_joint_bounds_SI"],
         "Source spec/geometry/contract hardware bounds differ")
    need(set(hardware) == set(PASSIVE + CONTINUOUS + ("gas_slide",)), "Unexpected mechanical joint set")
    need(spec["hardware_configuration"] == original["hardware_configuration"] == params["hardware_configuration"],
         "Hardware configuration binding changed")
    hw = spec["hardware_configuration"]
    need((hw["nominal_extension_force_N"], hw["stroke_m"], hw["compressed_eye_length_m"],
          hw["extended_eye_length_m"]) == (300.0, .06, .14, .2), "Wrong confirmed hardware master")
    proof = source_coordinate_proof(source, params)
    native, one_sided, roles = {}, {}, {}
    for side in SIDES:
        for key, pair in hardware.items():
            name = side + "_" + key
            need(original["joints"][name]["limits_si"] == pair, "Source joint differs from hardware: " + name)
            native[name] = list(pair)
            roles[name] = ["hardware" if value is not None else "unbounded" for value in pair]
            if key in PASSIVE:
                need(sum(value is None for value in pair) == 1, "Expected one-sided passive: " + name)
                one_sided[name] = list(pair)
                for index, value in enumerate(pair):
                    if value is None:
                        native[name][index] = -REPRESENTATION_ENDPOINT if index == 0 else REPRESENTATION_ENDPOINT
                        roles[name][index] = "native_coordinate_representation_only"
            else:
                need(pair == [None, None] if key in CONTINUOUS else all(v is not None for v in pair),
                     "Continuous or slider source bounds differ: " + name)
    need(len(native) == 20 and len(one_sided) == 10, "Incorrect native representation joint count")
    for name in one_sided:
        lower, upper = native[name]
        need(-math.pi <= lower < upper <= math.pi and upper - lower < TAU,
             "Passive native pair exceeds canonical representation/span: " + name)
    xml_text = (source / "mjcf/scene.xml").read_text(encoding="utf-8")
    xml_old = ET.fromstring(xml_text)
    need(xml_old.find("compiler").get("angle") == "radian" and
         xml_old.find("compiler").get("meshdir") == "assets", "Unexpected source MJCF units/mesh root")
    need(len(xml_old.findall("./worldbody//body")) == len(original["bodies"]) == 31, "Expected 31 bodies")
    need(len(original["closures"]) == 6 and len(original["mimics"]) == 4, "Closure or transmission count changed")
    meshes = []
    for mesh in xml_old.findall("./asset/mesh"):
        relative = Path(mesh.get("file"))
        need(not relative.is_absolute() and ".." not in relative.parts, "Mesh escaped packaged assets")
        meshes.append("mjcf/assets/" + relative.as_posix())
    need(len(meshes) == len(set(meshes)) == 277, "Expected unchanged 277 packaged meshes")
    replacements = set()

    def replace_joint(match):
        element = ET.fromstring(match.group(0))
        name = element.get("name")
        if name not in one_sided:
            return match.group(0)
        need(element.get("limited") == "true", "Source passive is not enabled: " + name)
        tokens = element.get("range", "").split()
        need(len(tokens) == 2, "Missing original MJCF endpoint pair: " + name)
        for index, hardware_value in enumerate(one_sided[name]):
            if hardware_value is None:
                need(math.isinf(float(tokens[index])), "Original MJCF open endpoint changed: " + name)
                tokens[index] = format(native[name][index], ".17g")
            else:
                need(float(tokens[index]) == hardware_value, "Original MJCF CAD endpoint changed: " + name)
        values = " ".join(tokens)  # Preserve the original CAD finite-end token exactly.
        result, count = re.subn(r'(\brange\s*=\s*)([\"\'])(.*?)\2',
                                lambda found: found.group(1) + found.group(2) + values + found.group(2),
                                match.group(0))
        need(count == 1 and name not in replacements, "Unexpected MJCF passive range: " + name)
        replacements.add(name)
        return result

    xml_new = re.sub(r"<joint\b[^>]*?/>", replace_joint, xml_text)
    need(replacements == set(one_sided), "MJCF representation edit set differs")
    need(xml_signature(xml_old, one_sided) == xml_signature(ET.fromstring(xml_new), one_sided),
         "MJCF changed outside ten passive ranges")
    # Import pxr ONLY during an explicit future build, never for source/AST review.
    from pxr import Sdf, Usd, UsdPhysics
    source_stage = Usd.Stage.Open(str(source / "assets/robot.usd"), Usd.Stage.LoadNone)
    need(bool(source_stage), "Source USD open failed")
    source_layer = source_stage.GetRootLayer()
    need(not source_layer.subLayerPaths, "Expected the independent HW300N60 USD")
    layer = Sdf.Layer.CreateAnonymous("hw300n60_physx_repr.usda")
    layer.TransferContent(source_layer)
    stage = Usd.Stage.Open(layer, Usd.Stage.LoadNone)
    before_endpoints = {}
    for name, pair in one_sided.items():
        joint = UsdPhysics.RevoluteJoint(stage.GetPrimAtPath("/Robot/joints/" + name))
        need(bool(joint), "Missing passive revolute joint: " + name)
        index = 0 if pair[0] is None else 1
        attr = joint.GetLowerLimitAttr() if index == 0 else joint.GetUpperLimitAttr()
        value = float(attr.Get())
        need(math.isinf(value) and (value < 0) == (index == 0), "Source endpoint is not the expected infinity")
        before_endpoints[name] = (index, value)
        need(attr.Set(-180.0 if index == 0 else 180.0), "USD representation endpoint authoring failed")
    candidate.mkdir(parents=False, exist_ok=False)
    for relative in list(SOURCE_SHA) + meshes:
        src, dst = source / relative, output / relative
        need(dst.resolve().is_relative_to(candidate), "Output escaped new candidate")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        need(sha(dst) == sha(src), "Copy changed mechanical source bytes: " + relative)
    (output / "mjcf/scene.xml").write_text(xml_new, encoding="utf-8", newline="\n")
    xml_sha = sha(output / "mjcf/scene.xml")
    root = stage.GetPrimAtPath("/Robot")
    original_root_custom = copy.deepcopy(root.GetCustomData())
    custom = copy.deepcopy(original_root_custom)
    custom["mod4"]["sourceSha256"] = xml_sha
    custom["mod4"]["nativeImplementationVersion"] = IMPLEMENTATION
    custom["mod4"]["nativeRuntimeVerified"] = False
    root.SetCustomData(custom)
    old_layer_custom = copy.deepcopy(layer.customLayerData)
    layer.customLayerData = dict(old_layer_custom, nativeImplementationVersion=IMPLEMENTATION,
                                 nativeRuntimeVerified=False)
    need(layer.Export(str(output / "assets/robot.usd")), "New candidate USD export failed")
    # Exact FULL layer comparison after restoring ONLY declared endpoint/metadata
    # edits: includes geometry arrays, mass/COM/inertia, all frames, closures,
    # mimics, drives (including gas targets), actuators, filters and attributes.
    reopened = Usd.Stage.Open(str(output / "assets/robot.usd"), Usd.Stage.LoadNone)
    need(bool(reopened), "New USD reopen failed")
    check_layer = Sdf.Layer.CreateAnonymous("unchanged_mechanics_check.usda")
    check_layer.TransferContent(reopened.GetRootLayer())
    check_stage = Usd.Stage.Open(check_layer, Usd.Stage.LoadNone)
    for name, (index, previous) in before_endpoints.items():
        joint = UsdPhysics.RevoluteJoint(check_stage.GetPrimAtPath("/Robot/joints/" + name))
        attr = joint.GetLowerLimitAttr() if index == 0 else joint.GetUpperLimitAttr()
        need(float(attr.Get()) == (-180.0 if index == 0 else 180.0), "New authored endpoint differs")
        attr.Set(previous)
    check_stage.GetPrimAtPath("/Robot").SetCustomData(original_root_custom)
    check_layer.customLayerData = old_layer_custom
    need(check_layer.ExportToString() == source_layer.ExportToString(),
         "Full USD content changed outside ten missing endpoints and declared provenance")
    adapter = new_adapter((source / "runtime_adapter_v2.py").read_text(encoding="utf-8"))
    (output / "runtime_adapter_v2.py").write_text(adapter, encoding="utf-8", newline="\n")
    usd_sha = sha(output / "assets/robot.usd")
    contract = copy.deepcopy(original)
    contract["hardware_one_sided_limits"] = one_sided
    contract["native_impl_limits"] = {
        "schema": SCHEMA, "implementation": IMPLEMENTATION, "backend": "PhysX",
        "hardware_spec_sha256": SPEC_SHA, "representation_endpoint_rad": REPRESENTATION_ENDPOINT,
        "added_endpoints_are_hardware_stops": False, "per_joint_limits_si": native,
        "units": "hinge radians / slider metres; USD hinge degrees",
        "coordinate_proof": proof, "source_package_sha256": copy.deepcopy(SOURCE_SHA),
        "status": "STATIC_CANDIDATE_PENDING_ACTUAL_NATIVE_GETTER",
        "native_getter_verified": False, "new_measured_hardware_limits": False,
    }
    for side in SIDES:
        for key, pair in hardware.items():
            name = side + "_" + key
            joint = contract["joints"][name]
            joint.update(limits_si=list(native[name]), hardware_limits_si=list(pair),
                         native_impl_limits_si=list(native[name]), limit_endpoint_roles=roles[name],
                         lower_limit_enabled=native[name][0] is not None,
                         upper_limit_enabled=native[name][1] is not None)
    contract["joint_limit_semantics"]["limits_si_basis"] = (
        "Actual native implementation pairs; original hardware bounds remain in hardware_limits_si, "
        "hardware_one_sided_limits and mechanical_limits_v2; added +/-pi are coordinate representation only")
    contract.update(native_implementation_version=IMPLEMENTATION, output_usd_sha256=usd_sha,
                    mjcf_sha256=xml_sha, source_mjcf_sha256=xml_sha, runtime_tested=False)
    contract["enhancement"].update(output_usd_sha256=usd_sha, native_implementation_version=IMPLEMENTATION,
                                    runtime_verified=False)
    # The protected contract physics must remain byte-value equivalent.
    for field in ("bodies", "closures", "mimics", "filters", "geometry", "actuated_joint_names",
                  "effort_limits_nm", "leg_motor", "wheel_motor", "roller_joints", "roller_parameters",
                  "gas_springs", "hardware_configuration", "mechanical_stop", "mechanical_limits_v2"):
        need(contract[field] == original[field], "Protected mechanical contract field changed: " + field)
    put_json(output / "assets/import_contract.json", contract)
    requirements = load(source / "runtime_requirements.json")
    requirements["inherited_HW300N60_local_validation_provenance"] = requirements.pop("local_validation", {})
    requirements["local_validation"] = {
        "source_coordinate_enclosure": "algebraic theorem bound to unchanged source SHA; not a native pass",
        "native_getter": "PENDING_PARENT_ACTUAL_GETTER_NEW_PURPOSE",
        "simulation_or_training_started_by_builder": False,
    }
    bindings = {relative: sha(output / relative) for relative in SOURCE_SHA if relative != "runtime_requirements.json"}
    requirements["native_implementation"] = {
        "schema": SCHEMA, "implementation": IMPLEMENTATION, "hardware_spec_sha256": SPEC_SHA,
        "bindings_sha256": bindings, "added_endpoints_are_hardware_stops": False,
    }
    requirements.update(target_physx_verified=False, runtime_validation_status="PENDING_ACTUAL_NATIVE_REPR_GETTER")
    put_json(output / "runtime_requirements.json", requirements)
    # All old inputs, all 277 output mesh bytes, and unchanged kinematics/parameters
    # are checked again; no original file has ever been opened for writing.
    need(sha(spec_path) == SPEC_SHA, "Original hardware spec changed during build")
    for relative, expected in SOURCE_SHA.items():
        need(sha(source / relative) == expected, "Original package changed during build: " + relative)
    for relative in meshes + ["kinematics_v2.py", "model_parameters.json", "reports/model_manifest.json"]:
        need(sha(output / relative) == sha(source / relative), "Protected output bytes changed: " + relative)
    return {"status": "BUILT_STATIC_CANDIDATE_NOT_NATIVE_ACCEPTED", "implementation": IMPLEMENTATION,
            "package": str(output), "builder_source_sha256": sha(__file__),
            "output_bindings_sha256": bindings, "runtime_requirements_sha256": sha(output / "runtime_requirements.json"),
            "missing_passive_endpoints_represented": 10, "continuous_active_follower_axes_unchanged": 8,
            "mesh_files_byte_preserved": 277, "original_hardware_spec_and_package_unchanged": True,
            "native_getter_verified": False, "simulation_started": False, "training_started": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=P0_DEFAULT,
                        help="Existing P0 mechanical project; output name is fixed and never overwrites")
    args = parser.parse_args()
    result = build(args.project.resolve())
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
