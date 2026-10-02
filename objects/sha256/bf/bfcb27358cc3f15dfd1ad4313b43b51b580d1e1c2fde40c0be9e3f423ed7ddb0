"""Guard the sim2real / sim2sim contract against silent drift.  Exits non-zero on ANY
mismatch, and treats a missing value as a mismatch -- the previous version printed
"contract OK" while reading None out of a regex that never matched the file layout.

The same physical quantity is written down in five places:
  1. the plant MJCF forcerange            -> torque ceilings
  2. rmvehicle.robot_cfg (env-tunable)    -> what TRAINING actually used
  3. train/deploy/contract.json           -> what the exporter claims
  4. the exported ONNX metadata           -> what ships inside the policy file
  5. the deployed controller YAML         -> what the ROS2 controller multiplies by
Only (2) is authoritative; (3) is generated from it, and (1)/(4)/(5) must agree with it.
This matters most for the wheel action scale: a policy trained at 55 and deployed at 10 runs
at 1/5.5 speed and looks like a failed 小陀螺 rather than a config bug, which is precisely how
this project lost a day.
"""
import argparse, json, os, re, sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parents[1])


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def plant_limits(xml):
    s = read(xml)
    def one(pat):
        m = re.search(pat, s)
        if not m:
            return None
        return max(abs(float(v)) for v in m.group(1).split())
    return dict(leg=one(r'name="left_front1_ctrl"[^>]*forcerange="([-0-9. ]+)"'),
                wheel=one(r'name="left_wheel_ctrl"[^>]*forcerange="([-0-9. ]+)"'))


def yaml_params(path):
    """The runtime controller YAML (flow-style lists under ros__parameters)."""
    import yaml
    doc = yaml.safe_load(read(path))
    for _, controllers in doc.items():
        for name, body in (controllers or {}).items():
            p = (body or {}).get("ros__parameters")
            if isinstance(p, dict) and "joint_action_scale" in p:
                return p
    return None


def onnx_meta(path):
    import onnx
    m = onnx.load(path)
    return {p.key: p.value for p in m.metadata_props}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plant", default=os.path.join(ROOT, "robot/out_cc/rm_vehicle_cc.xml"))
    ap.add_argument("--yaml", default=os.path.join(ROOT, "sim2sim_cc/rm_vehicle/config/rm_vehicle.yaml"))
    ap.add_argument("--contract", default=os.path.join(ROOT, "train/deploy/contract.json"))
    ap.add_argument("--onnx", default=os.path.join(ROOT, "train/deploy"),
                    help="directory whose top level holds the policy about to be deployed "
                         "(train/deploy/legacy/ is deliberately excluded)")
    ap.add_argument("--policy", default="", help="explicit ONNX to treat as the deployment")
    a = ap.parse_args()
    fails = []
    warns = []
    dep = a.onnx

    if not os.path.exists(a.contract):
        fails.append("MISSING %s -- run scripts/write_deploy_contract.py with the same "
                     "environment you trained with" % a.contract)
        c = {}
    else:
        c = json.loads(read(a.contract))
    print("contract.json:", c.get("motor_profile"), "wheel_scale", c.get("wheel_action_scale"),
          "wheel_kd", c.get("wheel_kd"), "checkpoint", c.get("checkpoint"))

    # ---- 1: authoritative training config, re-read from source (not from the JSON) -----
    sys.path.insert(0, os.path.join(ROOT, "train/rmvehicle/src"))
    from rmvehicle import robot_cfg as RC
    truth = RC.contract()
    for k, v in truth.items():
        if k not in c:
            fails.append("contract.json is missing authoritative field %r -- rerun "
                         "write_deploy_contract.py" % k)
        elif c[k] != v:
            fails.append("contract.json is STALE for %r: %r but training config says %r "
                         "-- rerun write_deploy_contract.py" % (k, c[k], v))

    # ---- 2: plant MJCF torque ceilings -------------------------------------------------
    tl = plant_limits(a.plant)
    print("plant MJCF forcerange: leg=%s wheel=%s" % (tl["leg"], tl["wheel"]))
    for key, label in (("leg", "leg_effort"), ("wheel", "wheel_effort")):
        if tl[key] is None:
            fails.append("could not read the %s forcerange out of %s" % (key, a.plant))
        elif abs(tl[key] - truth[label]) > 1e-6:
            fails.append("%s torque: plant %.3f vs training config %.3f"
                         % (key, tl[key], truth[label]))

    # ---- 3: the deployed controller YAML, checked against the policy it points at --------
    # The YAML is allowed to be BEHIND the latest training run (that just means we have not
    # deployed it yet), but it must never disagree with the ONNX it actually loads.  The
    # policy carries its own contract, so this is a closed check.
    # The reference for everything below is the ONNX that is about to be shipped: the newest
    # non-legacy policy in train/deploy (or --policy).  train/deploy/legacy holds every
    # historic checkpoint, and those legitimately carry the scale they were trained with, so
    # they must not be compared against today's training config.
    staged = []
    if os.path.isdir(dep):
        if a.policy:
            staged = [a.policy]
        else:
            staged = sorted((f for f in os.listdir(dep) if f.endswith(".onnx")),
                            key=lambda f: os.path.getmtime(os.path.join(dep, f)),
                            reverse=True)
    if not staged:
        warns.append("nothing staged for deployment in %s (everything is under legacy/) -- "
                     "export the checkpoint you want to ship, then re-run this check" % dep)
    pol_path = os.path.join(dep, staged[0]) if staged else None
    pol_meta = onnx_meta(pol_path) if pol_path else {}
    pol_scale = ([float(x) for x in pol_meta["joint_action_scale"].split(",")][:6]
                 if "joint_action_scale" in pol_meta else None)
    pol_kd = ([float(x) for x in pol_meta["joint_damping"].split(",")][:6]
              if "joint_damping" in pol_meta else None)
    pol_wz = float(pol_meta.get("yaw_command_limit_rad_s", "0") or 0)
    print("staged policy           :", os.path.basename(pol_path) if pol_path else "(none)",
          "scale", pol_scale, "kd", pol_kd, "yaw limit", pol_wz)
    if pol_path:
        for key, expected in (
            ("hardware_deployable", "1"),
            ("plant_kind", "similar_linkage_closed_chain"),
            ("policy_coordinate_space", "actuator_output_joint"),
            ("policy_controls_passive_knee", "0"),
            # A policy may only claim hardware_deployable=1 if it was TRAINED under this exact
            # motor envelope.  train/export_onnx.py reads the actuator limits back out of the
            # run's params/env.yaml and stamps this flag, so a 5.5 N.m / 63.4 rad/s wheel policy
            # can no longer be re-labelled as a DM3519+15.8 one by exporting it from newer source.
            ("train_envelope_matches_contract", "1"),
            ("base_contract_sha256", c.get("base_contract_sha256", "")),
        ):
            if pol_meta.get(key) != expected:
                fails.append("%s metadata %s=%r, expected %r"
                             % (os.path.basename(pol_path), key, pol_meta.get(key), expected))
    if pol_scale:
        want = [truth["leg_action_scale"]] * 4 + [truth["wheel_action_scale"]] * 2
        if any(abs(g - e) > 1e-6 for g, e in zip(pol_scale, want)):
            fails.append("%s was exported for action scale %s but the CURRENT training config "
                         "says %s -- re-export it with the environment it was trained under"
                         % (os.path.basename(pol_path), pol_scale, want))
        if pol_kd and abs(pol_kd[4] - truth["wheel_kd"]) > 1e-6:
            fails.append("%s expects wheel damping %s, the training config says %s"
                         % (os.path.basename(pol_path), pol_kd[4:6], truth["wheel_kd"]))
    if os.path.exists(a.yaml):
        p = yaml_params(a.yaml)
        if p is None:
            fails.append("%s has no template_ros2_controller.ros__parameters block" % a.yaml)
        else:
            sc = [float(x) for x in p["joint_action_scale"]]
            ymax = [float(x) for x in p["joint_output_max"]]
            ymin = [float(x) for x in p.get("joint_output_min", p["joint_output_max"])]
            kd = [float(x) for x in p["joint_damping"]]
            print("yaml joint_action_scale:", sc)
            print("yaml joint_output_max  :", ymax)
            print("yaml joint_damping     :", kd)
            print("yaml motion_angular_z  :", p.get("motion_angular_z_min"),
                  p.get("motion_angular_z_max"))
            want_t = [truth["leg_effort"]] * 4 + [truth["wheel_effort"]] * 2 + [50.0, 50.0]
            for i, (got, exp) in enumerate(zip(ymax, want_t)):
                if abs(got - exp) > 1e-6:
                    fails.append("joint_output_max[%d] = %s vs plant/contract %s" % (i, got, exp))
            if any(h != -lo for h, lo in zip(ymax, ymin)):
                fails.append("yaml output limits are not symmetric")
            if tl.get("leg") and abs(ymax[0] - tl["leg"]) > 1e-6:
                fails.append("yaml leg torque %s vs plant forcerange %s" % (ymax[0], tl["leg"]))
            if tl.get("wheel") and abs(ymax[4] - tl["wheel"]) > 1e-6:
                fails.append("yaml wheel torque %s vs plant forcerange %s" % (ymax[4], tl["wheel"]))
            # deployment YAML vs the policy it will actually load
            if pol_scale and any(abs(g - e) > 1e-6 for g, e in zip(sc, pol_scale)):
                fails.append("DEPLOYMENT IS SELF-INCONSISTENT: %s carries action scale %s but "
                             "the YAML feeds it %s -> the robot moves at the wrong speed and "
                             "it reads as a bad policy, not a bad config"
                             % (os.path.basename(pol_path), pol_scale, sc))
            elif not pol_scale:
                warns.append("the staged policy carries no joint_action_scale metadata, so the "
                             "YAML could not be cross-checked against it")
            if pol_kd and any(abs(g - e) > 1e-6 for g, e in zip(kd[4:6], pol_kd[4:6])):
                fails.append("wheel damping: YAML %s vs staged policy %s" % (kd[4:6], pol_kd[4:6]))
            if pol_wz:
                az = (float(p["motion_angular_z_min"]), float(p["motion_angular_z_max"]))
                if az[1] < pol_wz - 1e-6:
                    fails.append("the policy is trained to command %.1f rad/s of yaw but "
                                 "motion_angular_z_max is only %.1f -- the command path clamps "
                                 "the 小陀螺 away" % (pol_wz, az[1]))
    else:
        fails.append("deployment YAML not present yet: %s" % a.yaml)

    # ---- 4: the ONNX files themselves ---------------------------------------------------
    # (dep was already bound above section 3)
    if os.path.isdir(dep):
        policy_paths = ([a.policy] if a.policy else
                        [os.path.join(dep, f) for f in sorted(os.listdir(dep))
                         if f.endswith(".onnx")])
        for path in policy_paths:
            onx = os.path.basename(path)
            meta = onnx_meta(path)
            import onnxruntime as ort
            s = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
            i = list(s.get_inputs()[0].shape)[-1]
            o = list(s.get_outputs()[0].shape)[-1]
            if i != truth["obs_width"] or o != truth["action_width"]:
                fails.append("%s contract width obs=%s act=%s (expected %d/%d)"
                             % (onx, i, o, truth["obs_width"], truth["action_width"]))
            ms = meta.get("joint_action_scale", "")
            print("%-26s obs=%s act=%s meta_scale=%r" % (onx, i, o, ms[:60]))
            if not ms:
                fails.append("%s carries no joint_action_scale metadata" % onx)
            else:
                got = [float(x) for x in ms.split(",")]
                want = [truth["leg_action_scale"]] * 4 + [truth["wheel_action_scale"]] * 2
                # the metadata may be written per-ACTION (6) or per-CONTRACT-JOINT (8, the
                # ros2_control order, with zeros on the two passive gas-spring sliders);
                # both are correct, anything else is drift.
                if len(got) not in (6, 8) or any(abs(g - w) > 1e-6 for g, w in zip(got, want)):
                    fails.append("%s was EXPORTED with scale %s; the current training config "
                                 "says %s. Either export again or deploy the matching "
                                 "contract (RM_WHEEL_SCALE is per-checkpoint!)"
                                 % (onx, got, want))
            if meta.get("hardware_deployable") != "1":
                fails.append("%s is not explicitly marked hardware_deployable=1" % onx)
            if meta.get("train_envelope_matches_contract") is not None and \
                    meta.get("train_envelope_matches_contract") != "1":
                fails.append("%s was TRAINED under a different motor envelope: %s"
                             % (onx, meta.get("train_envelope_mismatch", "(no detail)")))
    print()
    for w in warns:
        print("   ~", w)
    if fails:
        print("CONTRACT DRIFT DETECTED (%d):" % len(fails))
        for f in fails:
            print("   !", f)
        return 1
    print("contract OK for the staged policy and the deployment YAML%s"
          % ("" if not warns else "  (%d warning%s)" % (len(warns), "s" if len(warns) > 1 else "")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
