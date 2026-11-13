"""Frozen R1 policy test at the user's exact MOD4v3 gas-200 rear-ground pose."""
from pathlib import Path
import csv
import hashlib
import json
import math
import sys
import time

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parent
ASSET = Path(r"F:\RMPOLAR-RL\mod4v3_scut_semantics_20261106\review_r3\corrected")
POSE_FILE = Path(r"F:\RMPOLAR-RL\mod4v3_limit_fold_pose_20261113\POSE_RESULT.json")
sys.path.insert(0, str(ROOT / "bundle/runtime"))
from control import Controller, build_observation, decode_targets, limit_torque

CONTRACT = json.loads((ROOT / "bundle/config/deployment_contract.json").read_text(encoding="utf-8"))
POSES = json.loads(POSE_FILE.read_text(encoding="utf-8"))
ORDER = CONTRACT["output"]["order"]
SECONDS = 12.0
CLOSURE_GUARD = 0.01
MIMIC_GUARD = 0.01
COMMAND = [0.0, 0.0, 0.0, 0.28]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_actor():
    ctrl = Controller()
    rows = json.loads((ROOT / "bundle/examples/golden_vectors.json").read_text(encoding="utf-8"))["vectors"]
    errors = []
    for row in rows:
        obs = build_observation(row["command"], row["joint_position_rad"],
                                row["joint_velocity_rad_s"], row["gyro_b_rad_s"],
                                row["gravity_b"], row["previous_action"])
        action = ctrl.session.run(["action"], {"observation": obs[None]})[0][0]
        target = decode_targets(action, row["joint_position_rad"])
        error = {"observation": float(np.max(np.abs(obs - row["observation"]))),
                 "action": float(np.max(np.abs(action - row["action"]))),
                 "target": float(np.max(np.abs(target - row["target"])))}
        errors.append(error)
    result = {"vectors": len(rows), "max_abs_errors": {
        key: max(row[key] for row in errors) for key in errors[0]}, "errors": errors}
    (ROOT / "GOLDEN_PARITY.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    assert result["max_abs_errors"]["observation"] < 2e-5, result
    assert result["max_abs_errors"]["action"] < 2e-5, result
    assert result["max_abs_errors"]["target"] < 2e-5, result
    return result


def errors(m, d):
    closure, mimic = [], []
    for i in range(m.neq):
        a, b = int(m.eq_obj1id[i]), int(m.eq_obj2id[i])
        if m.eq_type[i] == mujoco.mjtEq.mjEQ_CONNECT:
            assert m.eq_objtype[i] == mujoco.mjtObj.mjOBJ_SITE
            closure.append(float(np.linalg.norm(d.site_xpos[a] - d.site_xpos[b])))
        elif m.eq_type[i] == mujoco.mjtEq.mjEQ_JOINT:
            ia, ib = m.jnt_qposadr[a], m.jnt_qposadr[b]
            x = d.qpos[ib] - m.qpos0[ib]
            expected = sum(m.eq_data[i, j] * x**j for j in range(5))
            mimic.append(float(abs(d.qpos[ia] - m.qpos0[ia] - expected)))
    return max(closure), max(mimic)


def initialize(m, d, kind):
    mujoco.mj_resetData(m, d)
    if kind == "nominal":
        bank = json.loads((ROOT / "bundle/plant/reset_bank.json").read_text(encoding="utf-8"))
        pose = next(p for p in bank["poses"] if 0.24 <= p["root_height_m"] <= 0.272)
        mapping = json.loads((ASSET / "semantics.json").read_text(encoding="utf-8"))["coordinates"]["native_from_v2"]
        d.qpos[:3] = [0, 0, pose["root_height_m"]]
        d.qpos[3:7] = [1, 0, 0, 0]
        for name, row in mapping.items():
            d.qpos[m.jnt_qposadr[m.joint(name).id]] = pose["joint_pos"].get(row["source"], 0.0) + row["offset_si"]
    else:
        d.qpos[:] = POSES["stages"]["04_gas200_rear_ground"]["qpos"]
    d.qvel[:] = 0
    d.ctrl[:] = 0
    d.xfrc_applied[:] = 0
    mujoco.mj_forward(m, d)
    assert errors(m, d)[0] < 1e-8


def run_case(name, initial, powered):
    m = mujoco.MjModel.from_xml_path(str(ASSET / "mjcf/scene.xml"))
    d = mujoco.MjData(m)
    assert m.nq == 37 and abs(m.opt.timestep - 0.0025) < 1e-12
    initialize(m, d, initial)
    ctrl = Controller()
    qidx = [m.jnt_qposadr[m.joint(n).id] for n in ORDER]
    vidx = [m.jnt_dofadr[m.joint(n).id] for n in ORDER]
    actuators = [m.actuator(n + "_motor").id for n in ORDER]
    base = m.body("base_link").id
    ground = m.geom("ground").id
    tires = [m.geom(side + "_tire").id for side in ("left", "right")]
    samples, positions, velocities = [], [], []
    actions, targets, torques = [], [], []
    action = np.zeros(6)
    target = np.zeros(6)
    applied = np.zeros(6)
    worst_closure, worst_mimic = errors(m, d)
    fault = None

    def sample():
        R = d.xmat[base].reshape(3, 3)
        spatial = np.zeros(6)
        mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_BODY, base, spatial, 1)
        wheel_touch = [False, False]
        other_ground = set()
        for contact in d.contact:
            if contact.dist > 0.001:
                continue
            pair = [contact.geom1, contact.geom2]
            if ground not in pair:
                continue
            other = pair[1] if pair[0] == ground else pair[0]
            if other in tires:
                wheel_touch[tires.index(other)] = True
            else:
                other_ground.add(m.geom(other).name)
        cl, mi = errors(m, d)
        tilt = math.degrees(math.acos(float(np.clip(R[2, 2], -1, 1))))
        speed = float(np.linalg.norm(spatial[3:5]))
        standing = (d.qpos[2] >= 0.23 and tilt <= 10.0 and all(wheel_touch)
                    and not other_ground and speed <= 0.35 and np.linalg.norm(spatial[:3]) <= 0.5)
        samples.append(dict(time_s=float(d.time), x_m=float(d.qpos[0]), y_m=float(d.qpos[1]),
                            root_z_m=float(d.qpos[2]), tilt_deg=tilt, horizontal_speed_m_s=speed,
                            vx_body_m_s=float(spatial[3]), angular_speed_rad_s=float(np.linalg.norm(spatial[:3])),
                            left_tire_contact=wheel_touch[0], right_tire_contact=wheel_touch[1],
                            other_ground_contacts=";".join(sorted(other_ground)),
                            closure_m=cl, mimic_rad=mi, standing=bool(standing)))
        positions.append(d.qpos.copy())
        velocities.append(d.qvel.copy())
        actions.append(action.copy())
        targets.append(target.copy())
        torques.append(applied.copy())

    sample()
    started = time.monotonic()
    physics_steps = 0
    for step in range(round(SECONDS / 0.02)):
        if powered:
            R = d.xmat[base].reshape(3, 3)
            spatial = np.zeros(6)
            mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_BODY, base, spatial, 1)
            reply = ctrl.policy_tick(dict(command=COMMAND, joint_position_rad=d.qpos[qidx],
                                          joint_velocity_rad_s=d.qvel[vidx], gyro_b_rad_s=spatial[:3],
                                          gravity_b=R.T @ np.array([0.0, 0.0, -1.0])))
            action = np.asarray(reply["action"])
            target = np.asarray(reply["target"])
        for sub in range(8):
            if powered:
                if sub % 4 == 0:
                    held = ctrl.PD_tick(d.qpos[qidx], d.qvel[vidx])
                applied = limit_torque(held, d.qvel[vidx])
            else:
                applied = np.zeros(6)
            d.ctrl[actuators] = applied
            mujoco.mj_step(m, d)
            physics_steps += 1
            mujoco.mj_forward(m, d)
            cl, mi = errors(m, d)
            worst_closure = max(worst_closure, cl)
            worst_mimic = max(worst_mimic, mi)
            if not (np.isfinite(d.qpos).all() and np.isfinite(d.qvel).all() and np.isfinite(d.qacc).all()):
                fault = dict(time_s=float(d.time), reason="nonfinite")
            elif cl > CLOSURE_GUARD or mi > MIMIC_GUARD:
                fault = dict(time_s=float(d.time), reason="closure10mm" if cl > CLOSURE_GUARD else "mimic0p01rad",
                             closure_m=cl, mimic_rad=mi)
            if fault:
                break
        sample()
        if fault:
            break
    arrays = dict(time=np.array([r["time_s"] for r in samples]), qpos=np.asarray(positions), qvel=np.asarray(velocities),
                  action=np.asarray(actions), target=np.asarray(targets), torque=np.asarray(torques),
                  standing=np.asarray([r["standing"] for r in samples]))
    np.savez_compressed(ROOT / (name + ".npz"), **arrays)
    with (ROOT / (name + ".csv")).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(samples[0]))
        writer.writeheader()
        writer.writerows(samples)
    stable_count = 0
    first_stable_start = None
    longest = 0
    for i, row in enumerate(samples):
        stable_count = stable_count + 1 if row["standing"] else 0
        longest = max(longest, stable_count)
        if stable_count >= 101 and first_stable_start is None:
            first_stable_start = samples[i - 100]["time_s"]
    tail = [r for r in samples if r["time_s"] >= max(0, samples[-1]["time_s"] - 2.0)]
    tail_standing = len(tail) >= 100 and all(r["standing"] for r in tail)
    result = dict(case=name, initial_kind=initial, policy_enabled=powered, command=COMMAND,
                  physics_steps=physics_steps, simulated_s=float(d.time), wall_s=time.monotonic() - started,
                  fault=fault, initial=samples[0], final=samples[-1], root_z_max_m=max(r["root_z_m"] for r in samples),
                  tilt_max_deg=max(r["tilt_deg"] for r in samples), displacement_xy_m=np.linalg.norm(d.qpos[:2]).item(),
                  first_two_second_stand_start_s=first_stable_start, longest_standing_s=max(0, longest - 1) * 0.02,
                  final_two_seconds_standing=tail_standing, tail_standing_fraction=sum(r["standing"] for r in tail) / len(tail),
                  closure_max_m=worst_closure, mimic_max_rad=worst_mimic,
                  tail_root_z_mean_m=float(np.mean([r["root_z_m"] for r in tail])),
                  tail_tilt_mean_deg=float(np.mean([r["tilt_deg"] for r in tail])),
                  tail_speed_mean_m_s=float(np.mean([r["horizontal_speed_m_s"] for r in tail])),
                  status="numerical_stop" if fault else "standing_at_end" if tail_standing else
                         "stood_then_lost" if first_stable_start is not None else "no_stable_stand")
    (ROOT / (name + ".json")).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result


if __name__ == "__main__":
    assert sha(ASSET / "mjcf/scene.xml") == CONTRACT["plant"]["mjcf_sha256"]
    parity = verify_actor()
    results = [run_case("01_nominal_policy", "nominal", True),
               run_case("02_gas200_policy", "gas200", True),
               run_case("03_gas200_zero_torque", "gas200", False)]
    final = dict(selected_model=CONTRACT["selected_model"], iteration=CONTRACT["iteration"],
                 checkpoint_sha256=CONTRACT["checkpoint_sha256"], policy_sha256=sha(ROOT / "bundle/model/policy.onnx"),
                 mjcf_sha256=sha(ASSET / "mjcf/scene.xml"), initial_pose_source=str(POSE_FILE),
                 initial_pose_sha256=sha(POSE_FILE), mujoco=mujoco.__version__, parity=parity,
                 protocol=dict(seconds_per_case=SECONDS, policy_hz=50, PD_hz=100, physics_hz=400,
                               closure_guard_m=CLOSURE_GUARD, mimic_guard_rad=MIMIC_GUARD,
                               control_cache_refresh="mj_forward after each real physics step",
                               standing_criterion="root z>=0.23m; tilt<=10deg; both tires touch; no other floor contacts; horizontal speed<=0.35m/s; angular speed<=0.5rad/s; continuous 2s",
                               deterministic=True, domain_randomization=False, sensor_noise=False,
                               software_delay=False, resets_during_episode=0, scripted_rise=False,
                               external_assistance=False, nominal_parameters=True),
                 training_updates=0, hardware_commands=0, results=results)
    (ROOT / "RESULT.json").write_text(json.dumps(final, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
