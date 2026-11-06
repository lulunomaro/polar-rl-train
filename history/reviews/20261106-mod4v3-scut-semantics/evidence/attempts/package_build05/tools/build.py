"""Reproducible MOD4v3 semantic delivery; immutable source packages are inputs."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

import mujoco
import numpy as np
from scipy.spatial.transform import Rotation
from pxr import Gf, Sdf, Usd, UsdGeom, UsdPhysics


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf8")


def ry(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def quaternion(matrix):
    return Rotation.from_matrix(matrix).as_quat()[[3, 0, 1, 2]]


def rotation(q):
    return Rotation.from_quat(np.asarray(q)[[1, 2, 3, 0]]).as_matrix()


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def numbers(v):
    return " ".join(f"{float(x):.16g}" for x in np.asarray(v).reshape(-1))


def vec(text, default=(0., 0., 0.)):
    return np.array([float(x) for x in text.split()]) if text else np.asarray(default)


def qgf(q):
    return Gf.Quatf(float(q[0]), Gf.Vec3f(*map(float, q[1:])))


def quat_array(q):
    return np.array([q.GetReal(), *q.GetImaginary()], dtype=float)


def finite(x):
    return float(x) if math.isfinite(float(x)) else None


def mappings():
    bodies = {"chassis": "base_link"}
    joints = {}
    short = {"input": "front1", "coupler": "front2", "rocker": "front3",
             "distal": "front4", "thigh": "rear1", "shin": "rear2",
             "wheel": "wheel", "gas_inner": "spring1", "gas_barrel": "spring2"}
    jshort = {"crank": "front1", "coupler_pin": "front2", "rocker_pin": "f3r1",
              "distal_pin": "front4", "hip": "rear1", "knee": "rear2",
              "wheel_spin": "wheel", "gas_pin": "spring1", "gas_slide": "spring2"}
    for side in ("left", "right"):
        bodies.update({f"{side}_{k}": f"{side}_{v}_link" for k, v in short.items()})
        joints.update({f"{side}_{k}": f"{side}_{v}_joint" for k, v in jshort.items()})
        for old, new in (("drive_hip", "rear1_drive"), ("drive_input", "front1_drive")):
            bodies[f"{side}_{old}"] = f"{side}_{new}_link"
            joints[f"{side}_{old}_spin"] = f"{side}_{new}_joint"
        joints[f"{side}_proximal_closure"] = f"{side}_front3_joint"
        joints[f"{side}_distal_closure"] = f"{side}_f4r2_joint"
        joints[f"{side}_gas_closure"] = f"{side}_s2r2_joint"
    guides = ["left_bottom2", "left_bottom3", "right_bottom2", "right_bottom3",
              "left_front", "left_rear", "right_front", "right_rear"]
    for i, name in enumerate(guides):
        bodies[f"guide_roller_{i:02d}"] = name + "_guide_link"
        joints[f"guide_roller_{i:02d}"] = name + "_guide_joint"
    return bodies, joints


def reference_data(repo):
    relative = "source/agent_world/agent_world/assets/usd_files/wheelbipeV14_2_1/wheelbipeV14_2.usd"
    asset = repo / relative
    stage = Usd.Stage.Open(str(asset))
    if not stage:
        raise ValueError("SCUT V14_2 USD did not load")
    cache = UsdGeom.XformCache()
    joints, bodies = {}, {}
    for prim in stage.Traverse():
        if prim.HasAPI(UsdPhysics.RigidBodyAPI):
            matrix = cache.GetLocalToWorldTransform(prim)
            bodies[prim.GetName()] = dict(path=str(prim.GetPath()),
                p=np.array(matrix.ExtractTranslation()),
                R=rotation(quat_array(matrix.ExtractRotationQuat())))
        if prim.IsA(UsdPhysics.Joint):
            joint = UsdPhysics.Joint(prim)
            row = dict(name=prim.GetName(), path=str(prim.GetPath()), type=prim.GetTypeName())
            for i in (0, 1):
                target = getattr(joint, f"GetBody{i}Rel")().GetTargets()[0]
                pos = getattr(joint, f"GetLocalPos{i}Attr")().Get()
                row[f"body{i}"] = target.name
                row[f"anchor{i}"] = np.array(cache.GetLocalToWorldTransform(stage.GetPrimAtPath(target)).Transform(pos))
                row[f"rot{i}"] = quat_array(getattr(joint, f"GetLocalRot{i}Attr")().Get())
            axis = prim.GetAttribute("physics:axis").Get()
            row["axis"] = axis
            row["limits"] = [prim.GetAttribute("physics:" + n + "Limit").Get() for n in ("lower", "upper")]
            joints[prim.GetName()] = row
    commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    paths = [asset, repo / "LICENSE",
        repo / "source/agent_world/agent_world/assets/wheelbipe_V14_2.py",
        repo / "source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/cfg_utils.py",
        repo / "source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env.py",
        repo / "source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py"]
    provenance = dict(repository="https://github.com/scutrobotlab/wheeled-legged_RL", commit=commit,
        files=[dict(path=p.relative_to(repo).as_posix(), sha256=sha(p), bytes=p.stat().st_size) for p in paths],
        used_usd=relative, used_usd_sha256=sha(asset),
        reference_MJCF_available=False,
        MJCF_inventory=[p.relative_to(repo).as_posix() for p in repo.rglob("*.xml") if ".git" not in p.parts],
        source_of_truth="SCUT V14_2 authored USD + matching source; no MJCF substituted from another robot")
    return stage, joints, bodies, provenance


def derive_frames(model, data, ref_joints, ref_bodies):
    """Align frames by homologous pin rays, not by matching joint name strings."""
    phases = {model.body(i).name: 0. for i in range(1, model.nbody)}
    shifts = {name: np.zeros(3) for name in phases}
    evidence = []
    for side in ("left", "right"):
        def pivot(short):
            return np.array(data.xanchor[model.joint(side + "_" + short).id])
        def site(short):
            return np.array(data.site_xpos[model.site(side + "_" + short).id])
        def ref(short):
            return ref_joints[side + "_" + short + "_joint"]["anchor0"]
        O, A, P = pivot("hip"), pivot("coupler_pin"), pivot("rocker_pin")
        B, C, D = site("proximal_a"), pivot("distal_pin"), site("distal_a")
        K, W = pivot("knee"), pivot("wheel_spin")
        S, T = pivot("gas_pin"), site("gas_end")
        rays = {
            "input": (A-O, ref("front2")-ref("front1"), "front1 root pivot -> front2 pivot"),
            "coupler": (B-A, ref("front3")-ref("front2"), "front2 pivot -> front3 pivot"),
            "rocker": (P-B, ref("f3r1")-ref("front3"), "front3 pivot -> rear1 closure pivot"),
            "distal": (D-C, ref("f4r2")-ref("front4"), "front4 pivot -> rear2 closure pivot"),
            "thigh": (K-O, ref("rear2")-ref("rear1"), "rear1 root pivot -> rear2 pivot"),
            "shin": (W-K, ref("wheel")-ref("rear2"), "rear2 pivot -> wheel axle"),
            "gas_inner": (T-S, ref("s2r2")-ref("spring1"), "gas pivot -> distal eye closure"),
        }
        slider_axis = np.array(model.jnt_axis[model.joint(side + "_gas_slide").id])
        ref_axis = rotation(ref_joints[side + "_spring2_joint"]["rot1"]) @ np.array([1., 0., 0.])
        rays["gas_barrel"] = (slider_axis, ref_axis, "prismatic positive axis in child frame")
        for short, (a, b, rule) in rays.items():
            angle_a, angle_b = math.atan2(-a[2], a[0]), math.atan2(-b[2], b[0])
            phase = wrap(angle_a-angle_b)
            name = side + "_" + short
            phases[name] = phase
            evidence.append(dict(body_v2=name, homology_rule=rule,
                mod4_ray_old_body_frame=a.tolist(), SCUT_ray_reference_frame=b.tolist(),
                new_body_rotation_y_rad=phase,
                direction_error_rad=abs(wrap(angle_a-phase-angle_b)),
                link_lengths_preserved=True))
        # Give the wheel the same zero-frame orientation as its rear2 carrier,
        # as in SCUT, so a neutral wheel coordinate remains zero despite the
        # anatomical lower-leg-frame change. Visual geometry is counter-rotated.
        phases[side + "_wheel"] = phases[side + "_shin"]
        phases[side + "_drive_hip"] = phases[side + "_thigh"]
        phases[side + "_drive_input"] = phases[side + "_input"]
        shifts[side + "_rocker"] = B - np.array(data.xpos[model.body(side + "_rocker").id])
    return phases, shifts, evidence


def rewrite_mjcf(source, out, phases, shifts, body_map, joint_map, model):
    root = ET.parse(source / "mjcf/scene.xml").getroot()
    root.set("model", "MOD4v3_HW300N60_SCUT_V14_semantics")
    for mesh in root.find("asset").findall("mesh"):
        file = Path(mesh.get("file"))
        src = source / "mjcf/assets" / file
        dst = out / "mjcf/assets" / file
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.copy2(src, dst)
    offsets = {}
    for body in root.findall(".//body"):
        old = body.get("name")
        parent_id = int(model.body_parentid[model.body(old).id])
        parent = model.body(parent_id).name if parent_id else None
        pc = phases.get(parent, 0.)
        dc = shifts.get(parent, np.zeros(3))
        phase, delta = phases[old], shifts[old]
        body.set("pos", numbers(ry(-pc) @ (vec(body.get("pos")) + delta - dc)))
        body.set("quat", numbers(quaternion(ry(phase-pc))))
        for element in list(body):
            if element.tag == "body":
                continue
            if element.tag in ("geom", "site", "inertial", "joint"):
                if "fromto" in element.attrib:
                    ft = vec(element.get("fromto")).reshape(2, 3)
                    element.set("fromto", numbers((ft-delta) @ ry(-phase).T).strip())
                else:
                    element.set("pos", numbers(ry(-phase) @ (vec(element.get("pos"))-delta)))
                if "quat" in element.attrib:
                    element.set("quat", numbers(quaternion(ry(-phase) @ rotation(vec(element.get("quat"))))))
                elif element.tag in ("geom", "site", "inertial") and "fromto" not in element.attrib:
                    element.set("quat", numbers(quaternion(ry(-phase))))
            if element.tag == "joint":
                name = element.get("name")
                axis = vec(element.get("axis"), (0, 0, 1))
                element.set("axis", numbers(ry(-phase) @ axis))
                offset = phase-pc if element.get("type", "hinge") == "hinge" else 0.
                offsets[name] = offset
                element.set("ref", f"{offset:.16g}")
                if element.get("type", "hinge") == "hinge" and element.get("range"):
                    element.set("range", numbers(vec(element.get("range"))+offset))
            if element.tag == "freejoint":
                element.set("name", "root_joint")
        body.set("name", body_map[old])
    # All names in selectors, closures, excludes, motor and sensor bindings move
    # together. Sites/visual IDs remain unchanged so their identities stay traceable.
    for element in root.iter():
        for key, value in list(element.attrib.items()):
            if key in ("body1", "body2", "body") and value in body_map:
                element.set(key, body_map[value])
            elif key in ("joint", "joint1", "joint2") and value in joint_map:
                element.set(key, joint_map[value])
            elif key == "name" and element.tag in ("joint", "connect") and value in joint_map:
                element.set(key, joint_map[value])
            elif element.tag == "motor" and key == "name":
                element.set(key, joint_map[value.removesuffix("_motor")] + "_motor")
    # Native actuator array order is the reference policy order, independent of
    # MuJoCo body traversal and PhysX articulation joint ordering.
    policy = ["left_front1_joint", "right_front1_joint", "left_rear1_joint",
              "right_rear1_joint", "left_wheel_joint", "right_wheel_joint"]
    actuator = root.find("actuator")
    children = {e.get("joint"): e for e in list(actuator)}
    actuator[:] = [children[n] for n in policy]
    # Explicit hip anchors coexist with SCUT's base-origin projected leg measure.
    base = root.find(".//body[@name='base_link']")
    for side in ("left", "right"):
        point = model.body_pos[model.body(side + "_thigh").id]
        ET.SubElement(base, "site", name=side + "_hip_anchor", pos=numbers(point), size=".002", group="3")
    path = out / "mjcf/scene.xml"
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(path, encoding="utf8", xml_declaration=True)
    return offsets, policy


def rewrite_usd(source, out, phases, shifts, body_map, joint_map, offsets, semantic_hash):
    src = Usd.Stage.Open(str(source / "assets/robot.usd"))
    path = out / "assets/robot.usd"
    path.parent.mkdir(parents=True, exist_ok=True)
    src.Flatten().Export(str(path))
    stage = Usd.Stage.Open(str(path))
    for old in body_map:
        prim = stage.GetPrimAtPath("/Robot/links/" + old)
        angle, delta = phases[old], shifts[old]
        body_matrix = UsdGeom.Xformable(prim).GetLocalTransformation()
        origin = np.array(body_matrix.ExtractTranslation())
        change = Gf.Matrix4d(1.)
        change.SetRotate(Gf.Rotation(Gf.Vec3d(0, 1, 0), math.degrees(angle)))
        change.SetTranslateOnly(Gf.Vec3d(*map(float, delta)))
        for child in prim.GetChildren():
            if child.IsA(UsdGeom.Xformable):
                xf = UsdGeom.Xformable(child)
                matrix = xf.GetLocalTransformation() * change.GetInverse()
                xf.ClearXformOpOrder()
                xf.AddTransformOp().Set(matrix)
        mass = UsdPhysics.MassAPI(prim)
        com = mass.GetCenterOfMassAttr().Get()
        mass.GetCenterOfMassAttr().Set(Gf.Vec3f(*map(float, ry(-angle) @ (np.array(com)-delta))))
        old_axes = quat_array(mass.GetPrincipalAxesAttr().Get())
        mass.GetPrincipalAxesAttr().Set(qgf(quaternion(ry(-angle) @ rotation(old_axes))))
        xf = UsdGeom.Xformable(prim)
        xf.ClearXformOpOrder()
        matrix = Gf.Matrix4d(1.)
        matrix.SetRotate(Gf.Rotation(Gf.Vec3d(0, 1, 0), math.degrees(angle)))
        matrix.SetTranslateOnly(Gf.Vec3d(*map(float, origin+delta)))
        xf.AddTransformOp().Set(matrix)
        prim.SetCustomDataByKey("mod4v3:legacyBody", old)
        prim.SetCustomDataByKey("mod4v3:frameRotationYRad", angle)
    for prim in stage.Traverse():
        if not prim.IsA(UsdPhysics.Joint):
            continue
        old = prim.GetName()
        joint = UsdPhysics.Joint(prim)
        for i in (0, 1):
            targets = getattr(joint, f"GetBody{i}Rel")().GetTargets()
            if not targets:
                continue
            owner = targets[0].name
            p = np.array(getattr(joint, f"GetLocalPos{i}Attr")().Get())
            getattr(joint, f"GetLocalPos{i}Attr")().Set(Gf.Vec3f(*map(float, ry(-phases[owner]) @ (p-shifts[owner]))))
            if prim.IsA(UsdPhysics.RevoluteJoint):
                # All original scalar hinges are the same signed +Y axle. Their
                # frame rotations now encode the SCUT anatomical reference zero.
                getattr(joint, f"GetLocalRot{i}Attr")().Set(qgf([1, 0, 0, 0]))
            else:
                q = quat_array(getattr(joint, f"GetLocalRot{i}Attr")().Get())
                getattr(joint, f"GetLocalRot{i}Attr")().Set(qgf(quaternion(ry(-phases[owner]) @ rotation(q))))
        if prim.IsA(UsdPhysics.RevoluteJoint):
            prim.GetAttribute("physics:axis").Set("Y")
            offset = math.degrees(offsets[old])
            for key in ("physics:lowerLimit", "physics:upperLimit",
                        "drive:angular:physics:targetPosition", "state:angular:physics:position"):
                attr = prim.GetAttribute(key)
                if attr and attr.HasAuthoredValueOpinion():
                    attr.Set(float(attr.Get())+offset)
        prim.SetCustomDataByKey("mod4v3:legacyJoint", old)
    # Namespace edits on a flattened standalone layer. Remap every relationship
    # and connection explicitly, including filters, materials and mimic targets.
    path_map = {}
    for old, new in body_map.items():
        path_map["/Robot/links/" + old] = "/Robot/links/" + new
    actual_joint_paths={p.GetName():str(p.GetPath()) for p in stage.Traverse() if p.IsA(UsdPhysics.Joint)}
    for old, new in joint_map.items():
        path_map[actual_joint_paths[old]] = "/Robot/joints/" + new
    edits = Sdf.BatchNamespaceEdit()
    for old, new in path_map.items():
        if stage.GetPrimAtPath(old):
            edits.Add(old, new)
    if not stage.GetRootLayer().Apply(edits):
        raise RuntimeError("USD namespace edit failed")
    def moved(p):
        for old, new in sorted(path_map.items(), key=lambda x: -len(x[0])):
            if p.HasPrefix(Sdf.Path(old)):
                return p.ReplacePrefix(Sdf.Path(old), Sdf.Path(new))
        return p
    for prim in stage.Traverse():
        for rel in prim.GetRelationships():
            targets = rel.GetTargets()
            if targets:
                rel.SetTargets([moved(p) for p in targets])
        for attr in prim.GetAttributes():
            connections = attr.GetConnections()
            if connections:
                attr.SetConnections([moved(p) for p in connections])
    root = stage.GetDefaultPrim()
    root.SetCustomDataByKey("mod4v3:version", "MOD4v3-HW300N60-SCUT-V14")
    root.SetCustomDataByKey("mod4v3:semanticSha256", semantic_hash)
    root.SetCustomDataByKey("mod4v3:coordinateInterface", "../semantics.py:Semantics")
    root.SetCustomDataByKey("mod4v3:front3IsDerivedScalarAcrossLoopCut", True)
    legacy_data=root.GetCustomDataByKey("mod4")
    if legacy_data:
        root.SetCustomDataByKey("mod4v3:inheritedV2Metadata",legacy_data)
        root.ClearCustomDataByKey("mod4")
    layer_data=dict(stage.GetRootLayer().customLayerData)
    layer_data["mod4_asset_version"]="MOD4v3-HW300N60-SCUT-V14"
    layer_data["mod4EnhancementVersion"]="MOD4v3-HW300N60-SCUT-V14"
    stage.GetRootLayer().customLayerData=layer_data
    stage.GetRootLayer().Save()
    return stage


def serial(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {k: serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return "-inf" if value < 0 else "inf"
    return value


def build(args):
    source, repo, out = args.source_package.resolve(), args.reference_repo.resolve(), args.output.resolve()
    if out.exists():
        raise FileExistsError("New delivery directory required; do not overwrite an existing build")
    out.mkdir(parents=True)
    model = mujoco.MjModel.from_xml_path(str(source / "mjcf/scene.xml"))
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    _, refs, ref_bodies, ref_provenance = reference_data(repo)
    body_map, joint_map = mappings()
    phases, shifts, rays = derive_frames(model, data, refs, ref_bodies)
    offsets, policy = rewrite_mjcf(source, out, phases, shifts, body_map, joint_map, model)
    native_order = [joint_map[model.joint(i).name] for i in range(model.njnt) if model.jnt_type[i] != mujoco.mjtJoint.mjJNT_FREE]
    native_from_v2 = {joint_map[n]: dict(source=n, offset_si=offsets[n]) for n in offsets}
    expressions = {}
    for n in native_order:
        if n.endswith("_f3r1_joint"):
            side = n.split("_")[0]
            expressions[side + "_front3_joint"] = {n: 1., side + "_rear1_joint": 1.,
                side + "_front1_joint": -1., side + "_front2_joint": -1.}
        else:
            expressions[n] = {n: 1.}
    all_body_rows = []
    inverse_body = {v: k for k, v in body_map.items()}
    for n, row in ref_bodies.items():
        old = inverse_body.get(n)
        all_body_rows.append(dict(scut=n, mod4v2=old, mod4v3=n if old else None,
            status="homologous_role_different_dimensions" if old else "absent_on_MOD4",
            reason=None if old else "MOD4 does not physically contain this gimbal/guide roller; no dummy body created"))
    inverse_joint = {v: k for k, v in joint_map.items()}
    all_joint_rows = []
    for n, row in refs.items():
        old = inverse_joint.get(n)
        status = "homologous_pivot" if old else "absent_on_MOD4"
        binding = "direct_native_coordinate"
        if n.endswith("_front3_joint"):
            status, binding = "homologous_pivot_different_tree_cut", "derived_scalar_from_native_hinges"
        elif n.endswith("_f3r1_joint"):
            status, binding = "homologous_pivot_different_tree_cut", "native_hinge_instead_of_reference_spherical_cut"
        elif n.endswith(("_f4r2_joint", "_s2r2_joint")):
            binding = "native_spherical_loop_closure"
        all_joint_rows.append(dict(scut=n, mod4v2=old, mod4v3=n if old else None,
            status=status, binding=binding if old else None, reference_type=row["type"],
            reference_parent=row["body0"], reference_child=row["body1"],
            semantic_expression=expressions.get(n),
            reason=None if old else "No physical MOD4 gimbal/roller counterpart; requests raise an error"))
    spec = dict(schema="mod4v3.scut_semantics.v1", asset_version="MOD4v3-HW300N60-SCUT-V14",
        reference=ref_provenance, reference_coverage=dict(bodies=all_body_rows, joints=all_joint_rows),
        source_to_v3=dict(bodies=body_map, joints=joint_map),
        body_frame_changes={n:dict(rotation_y_rad=phases[n], origin_shift_in_old_body_m=shifts[n].tolist()) for n in body_map},
        frame_derivation=rays,
        coordinates=dict(native_order=native_order, semantic_order=list(expressions),
            native_from_v2=native_from_v2, semantic_from_native=expressions,
            reference_zero="Homologous pin-ray orientations, not SCUT lengths or physical joint bounds",
            continuous_angles="Unwrapped/lifted; no modulo applied to stored active coordinates",
            raw_tree_exception="front3 scalar is rear1+f3r1-front1-front2; both files retain the MOD4 loop cut"),
        frames=dict(world="right-handed X-forward Y-left Z-up", scalar_units="SI radians/metres; native USD angle attributes degrees",
            root_quaternion_interface="wxyz; Newton xyzw converted at boundary",
            native_USD_rotation_axis="Y for hinges, with identity hinge local frames",
            wheel_order=["left_wheel_link", "right_wheel_link"]),
        measures=dict(scut_leg_length="sqrt(base_to_wheel_heading_x**2+base_to_wheel_world_z**2), y=0",
            scut_leg_angle="atan2(-base_to_wheel_heading_x,-base_to_wheel_world_z)",
            mod4_L0_3d="norm(wheel_center_b-actual_hip_anchor_b); separately named, not substituted into SCUT",
            mod4_theta="atan2(hip_to_wheel_body_x,-hip_to_wheel_body_z)", wheel_radius_m=.0625),
        control=dict(policy_action_order=policy, leg_target_units="absolute anatomical semantic radians, apply declared action scale in controller",
            policy_order_basis="explicit V14 ordered_leg_joint_names front1 L/R then rear1 L/R; resolve upstream runtime actuator order separately",
            raw_action_formula="q_leg_target=default_leg_pos+leg_action_scale*a_leg; wheel_target=wheel_scale*a_wheel",
            wheel_target_units="explicit velocity rad/s or torque Nm mode; no automatic assumption", actuator_order=policy, external_transmission_applied_once=True,
            physical_limits="MOD4 HW300N60 torque/speed, gas and CAD stops retained; not replaced with SCUT limits",
            dt_physics_s=.0025, dt_control_s=.02),
        contact_groups=dict(desired=["left_wheel_link", "right_wheel_link"],
            guides=[n for n in body_map.values() if n.endswith("_guide_link")],
            structural=[n for n in body_map.values() if not n.endswith(("_wheel_link", "_guide_link"))],
            body_index_space="resolve sensor names independently; no reuse of articulation indices",
            force_frame="world SI N", guide_mapping="functional location; missing SCUT rollers explicit; no new collision shapes"),
        reward_execution=dict(missing_nonzero_term="raise KeyError", termination_source="final terminated before reset",
            timeout_bootstrap="terminal observation, not auto-reset observation", dt_applied_exactly_once=.02,
            reward_weights_changed=False, old_learner_or_environment_hotpatched=False),
        physical_delta=dict(mass_or_geometry_changed=False, constraints_removed=False,
            spanning_tree_changed=False, numeric_coordinates_and_body_frames_changed=True,
            closure_threshold_m=.01, mimic_threshold_rad=.01))
    write_json(out / "semantics.json", spec)
    stage = rewrite_usd(source, out, phases, shifts, body_map, joint_map, offsets, sha(out/"semantics.json"))
    # Preserve only the compact geometric solver as a legacy-coordinate helper.
    legacy = out / "legacy"
    (legacy / "reports").mkdir(parents=True)
    for n in ("kinematics_v2.py", "model_parameters.json", "reports/model_manifest.json"):
        shutil.copy2(source / n, legacy / n)
    shutil.copy2(Path(__file__).with_name("semantics.py"), out / "semantics.py")
    shutil.copy2(repo / "LICENSE", out / "SCUT_LICENSE")
    params = json.loads((source / "model_parameters.json").read_bytes())
    params["schema"] = "mod4v3.HW300N60.model_parameters.v1"
    params["model"] = spec["asset_version"]
    params["parameter_coordinate_basis"] = "legacy_v2 for inherited numeric geometry; semantics.json defines all v3 reference offsets"
    params["semantics_file"] = "semantics.json"
    params["delivery_status"] = "SEMANTIC_PACKAGE_REQUIRES_REPORTED_VALIDATION"
    write_json(out / "model_parameters.json", params)
    source_files = [source / p for p in ("mjcf/scene.xml", "assets/robot.usd", "assets/import_contract.json", "model_parameters.json")]
    write_json(out/"PROVENANCE.json",dict(source_package=str(source),
        immutable_inputs=[dict(path=str(p), bytes=p.stat().st_size, sha256=sha(p)) for p in source_files],
        reference=ref_provenance, builder_sha256=sha(__file__)))
    v3m = mujoco.MjModel.from_xml_path(str(out/"mjcf/scene.xml"))
    compiled_joints = {}
    for i in range(v3m.njnt):
        if v3m.jnt_type[i] == mujoco.mjtJoint.mjJNT_FREE:
            continue
        n = v3m.joint(i).name
        b = int(v3m.jnt_bodyid[i]); p = int(v3m.body_parentid[b])
        compiled_joints[n] = dict(parent=v3m.body(p).name, child=v3m.body(b).name,
            type="slide" if v3m.jnt_type[i] == mujoco.mjtJoint.mjJNT_SLIDE else "hinge",
            axis_child=v3m.jnt_axis[i].tolist(), reference_si=float(v3m.qpos0[v3m.jnt_qposadr[i]]),
            limited=bool(v3m.jnt_limited[i]),
            limits_si=[finite(x) for x in v3m.jnt_range[i]] if v3m.jnt_limited[i] else [None,None])
    contract = dict(format_version="mod4v3.import_contract.v1", model_kind="faithful_closed_chain_MOD4",
        asset_version=spec["asset_version"], mjcf_path="../mjcf/scene.xml", semantics_path="../semantics.json",
        source_mjcf_sha256=sha(out/"mjcf/scene.xml"), output_usd_sha256=sha(out/"assets/robot.usd"),
        semantics_sha256=sha(out/"semantics.json"),
        body_names=[v3m.body(i).name for i in range(1,v3m.nbody)], joints=compiled_joints,
        native_articulation_joint_count=30, independent_controlled_dofs=6,
        native_MJCF_equalities=v3m.neq, physical_total_mass_kg=float(v3m.body_mass.sum()),
        actuated_joint_names=policy, native_USD_is_closed_loop_rig=True,
        raw_selector_exceptions=["left_front3_joint", "right_front3_joint"],
        required_coordinate_interface="semantics.Semantics",
        gimbal_present=False, reference_MJCF_available=False,
        SDK_GPU_dynamics_verified=False, reward_training_convergence_verified=False)
    write_json(out/"assets/import_contract.json",contract)
    initial={n:row['reference_si'] for n,row in compiled_joints.items()}
    runtime=dict(schema='mod4v3.runtime_config.v1',asset_version=spec['asset_version'],
        USD='assets/robot.usd',MJCF='mjcf/scene.xml',root_body='base_link',
        initial_joint_positions=initial,
        do_not_initialize_all_anatomical_angles_to_zero=True,
        policy_action_order=policy,leg_position_scale='required from selected task configuration',
        wheel_mode='required: velocity or torque',wheel_scale='required from selected task configuration',
        leg_PD=dict(kp_Nm_rad=60.,kd_Nm_s_rad=2.),
        actuator_hardware_source='legacy/model_parameters.json',
        leg_motor_peak_torque_Nm=40.,wheel_motor_peak_torque_Nm=5.775909774436091,
        gas_spring_owned_by_asset=True,do_not_add_second_SCUT_spring=True,
        no_pretrained_policy_compatibility_claim=True,
        SCUT_IK_cannot_copy_link_lengths=True,
        required_reward_view='semantics.ScutRobotView',
        control_dt_s=.02,physics_dt_s=.0025,closure_reset_m=.01,mimic_reset_rad=.01,
        raw_front3_native_articulation_scalar_available=False)
    write_json(out/'runtime_config.json',runtime)
    shutil.copy2(Path(__file__).with_name('kinematics.py'),out/'kinematics.py')
    from reference_inventory import inventory
    inventory(repo,out)
    toolsdir=out/'tools';toolsdir.mkdir()
    for name in ['build.py','validate.py','reference_inventory.py','probe_newton.py']:
        shutil.copy2(Path(__file__).with_name(name),toolsdir/name)
    readme = Path(__file__).with_name("README.md").read_text(encoding="utf8")
    (out/"README.md").write_text(readme,encoding="utf8")
    print(json.dumps(dict(output=str(out), model=contract["asset_version"],
        source_sha=sha(source/"mjcf/scene.xml"), mjcf_sha=sha(out/"mjcf/scene.xml"),
        usd_sha=sha(out/"assets/robot.usd"), native_coordinates=len(native_order),
        reference_bodies=len(ref_bodies), reference_joints=len(refs)),ensure_ascii=False))


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-package",type=Path,required=True)
    parser.add_argument("--reference-repo",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    build(parser.parse_args())
