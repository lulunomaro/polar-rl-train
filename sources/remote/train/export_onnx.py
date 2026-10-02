"""Export a trained RMVehicle policy to the wheelbipe deployment ONNX contract.

  input  "obs"     float32[1, 35]
  output "actions" float32[1, 6]

Usage: python export_onnx.py --checkpoint logs/rsl_rl/rm_flat_v1/<run>/model_2000.pt \
                             --out    deploy/rm_vehicle.onnx
"""
import argparse, hashlib, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from dataclasses import asdict
from pathlib import Path

import numpy as np
import torch

import rmvehicle  # registers the task
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import MjlabOnPolicyRunner, RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg

ap = argparse.ArgumentParser()
ap.add_argument("--task", default="RMVehicle-CC-Field-v0")
ap.add_argument("--checkpoint", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--num-envs", type=int, default=1)
ap.add_argument("--device", default="cuda:0",
                help="device for the mjlab env/runner; use 'cpu' to export while the GPU "
                     "is busy training (the ONNX graph itself is exported on CPU either way)")
ap.add_argument("--model", choices=("auto", "cc", "later"), default="auto",
                help="which plant contract to stamp (auto: from the task id)")
ap.add_argument("--contract-out", default="",
                help="where write_deploy_contract.py should write the matching JSON")
ap.add_argument(
    "--allow-regression-export", action="store_true",
    help="allow export from a non-closed-chain regression task; the result is NOT approved for hardware",
)
ap.add_argument(
    "--allow-envelope-mismatch", action="store_true",
    help="export even though the checkpoint was trained under a DIFFERENT motor envelope than the "
         "current deploy contract; the ONNX is then stamped hardware_deployable=0",
)
ap.add_argument("--smoke", action="store_true",
                help="pipeline-validation export: always stamp hardware_deployable=0")
ap.add_argument("--min-deploy-iter", type=int, default=1000,
                help="minimum checkpoint iteration for hardware_deployable=1")
args = ap.parse_args()

if "-CC-" not in args.task and not args.allow_regression_export:
    raise SystemExit(
        "REFUSING NON-DEPLOYABLE EXPORT: use RMVehicle-CC-Field-v0 for the real similar-linkage "
        "closed-chain robot. Pass --allow-regression-export only for an explicitly labelled sim-only artifact."
    )

# Validate provenance before creating an environment or writing ``--out``.  A
# rejected export must not leave a plausible-looking ONNX artifact behind.
from rmvehicle import robot_cfg as _RC
from rmvehicle import train_log as _TL
from rmvehicle.names import CC as _CCN, RM2025_LATER as _LATER

_model = args.model
if _model == "auto":
    _model = "later" if "RM2025-Later" in args.task else "cc"
_names = _LATER if _model == "later" else _CCN
_leg_hints = ("crank", "hip") if _model == "later" else ("front1",)
_C = _RC.contract(_names)
if not args.contract_out:
    args.contract_out = os.path.join(
        ROOT, "train", "deploy",
        "contract_rm2025_later.json" if _model == "later" else "contract.json")
if "-CC-" in args.task:
    if _C.get("plant_kind") != "similar_linkage_closed_chain":
        raise SystemExit("REFUSING EXPORT: deploy contract is not the closed-chain plant")
    if _C.get("policy_coordinate_space") != "actuator_output_joint":
        raise SystemExit("REFUSING EXPORT: policy is not in actuator output-joint coordinates")
    if _C.get("policy_controls_passive_knee"):
        raise SystemExit("REFUSING EXPORT: passive knee appears in the policy contract")

_train_env = _TL.read_actuator_envelope(args.checkpoint)
_env_mismatch = _TL.check_against_contract(_train_env, _C, leg_hints=_leg_hints)
for _m in _env_mismatch:
    print("ENVELOPE MISMATCH:", _m)
if _env_mismatch:
    print("training-time actuators:", _TL.describe(_train_env))
    if not args.allow_envelope_mismatch:
        raise SystemExit(
            "REFUSING EXPORT BEFORE WRITING OUTPUT: this checkpoint was trained under a different "
            "motor envelope. Re-train on the current plant, or pass --allow-envelope-mismatch "
            "to create an explicitly non-deployable diagnostic artifact."
        )
_deployable = "-CC-" in args.task and not _env_mismatch

env_cfg = load_env_cfg(args.task, play=True)
agent_cfg = load_rl_cfg(args.task)
env_cfg.scene.num_envs = args.num_envs
env_cfg.observations["actor"].enable_corruption = False
for name in ("push_robot",):
    env_cfg.events.pop(name, None)

env = ManagerBasedRlEnv(cfg=env_cfg, device=args.device)
env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
runner = MjlabOnPolicyRunner(env, asdict(agent_cfg), device=args.device)
# A checkpoint written on CUDA stores CUDA tensors; map_location lets the same artifact
# load on a CPU-only export host (or while the GPU is busy training).
runner.load(args.checkpoint, map_location=args.device)
print("loaded", args.checkpoint)

# A random / barely-trained checkpoint must never be stamped as deployable just because
# its actuator envelope matches.  This is what makes the smoke artifact safe to keep.
_checkpoint_iter = int(getattr(runner, "current_learning_iteration", 0) or 0)
_block_reason = ""
if args.smoke:
    _block_reason = "explicit --smoke export"
elif _checkpoint_iter < args.min_deploy_iter:
    _block_reason = ("checkpoint iteration %d < min-deploy-iter %d"
                     % (_checkpoint_iter, args.min_deploy_iter))
if _block_reason:
    _deployable = False
    print("NOT HARDWARE-DEPLOYABLE:", _block_reason)

out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)
runner.export_policy_to_onnx(path=str(out.parent), filename=out.name)
print("wrote", out)

# ------------------------------------------------------------------ metadata
import onnx
from mjlab.entity import Entity

robot: Entity = env.unwrapped.scene["robot"]
names = list(robot.joint_names)
model = onnx.load(str(out))


def add(key, value):
    e = onnx.StringStringEntryProto()
    e.key, e.value = key, value if isinstance(value, str) else ",".join(
        repr(float(x)) for x in np.atleast_1d(value).ravel())
    model.metadata_props.append(e)


add("policy_contract", "obs float32[1,35] -> actions float32[1,6] @ %d Hz"
    % _C["policy_hz"])
add("joint_names", ",".join(names))
add("policy_joint_order", ",".join(names))
add("observation_names", ",".join(env.unwrapped.observation_manager.active_terms["actor"]))
add("default_joint_pos", robot.data.default_joint_pos[0].cpu().numpy())
# The policy CARRIES its own contract.  These used to be literals here (60/2/0.5/10.0), i.e.
# a fourth copy of the numbers that could disagree with the training config that produced the
# weights -- and it did, which is why a policy trained at wheel scale 55 can no longer be
# deployed against a YAML that still says 10 without the robot running at 1/5.5 speed.
_contract_digest = hashlib.sha256(
    json.dumps(_C, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
).hexdigest()
add("contract_schema_version", str(_C["schema_version"]))
add("base_contract_sha256", _contract_digest)
add("plant_kind", _C["plant_kind"])
add("policy_coordinate_space", _C["policy_coordinate_space"])
add("policy_controls_passive_knee", "0")
add("leg_drive_roles", json.dumps(_C["leg_drive_roles"], sort_keys=True))
add("leg_motor_model", _C["leg_motor_model"])
add("wheel_motor_model", _C["wheel_motor_model"])
add("leg_internal_reduction", [_C["leg_internal_reduction"]])
add("leg_external_chain_ratio", [_C["leg_external_chain_ratio"]])
add("wheel_total_reduction", [_C["wheel_total_reduction"]])
add("joint_stiffness", [_C["leg_kp"]] * 4 + [0.0, 0.0, 0.0, 0.0])
add("joint_damping", [_C["leg_kd"]] * 4 + [_C["wheel_kd"]] * 2 + [0.0, 0.0])
add("joint_action_scale", [_C["leg_action_scale"]] * 4 + [_C["wheel_action_scale"]] * 2
    + [0.0, 0.0])
add("joint_output_max", [_C["leg_effort"]] * 4 + [_C["wheel_effort"]] * 2)
add("wheel_no_load_rad_s", [_C["wheel_no_load"]])
add("leg_no_load_rad_s", [_C["leg_no_load"]])
add("wheel_current_plateau_nm", [_C["wheel_effort"]])
add("wheel_voltage_line_intercept_nm", [_C["wheel_voltage_line_intercept"]])
add("wheel_knee_speed_rad_s", [_C["wheel_knee_speed"]])
add("leg_voltage_line_intercept_nm", [_C["leg_voltage_line_intercept"]])
add("leg_effort_max", [_C["leg_effort"]] * 4)
add("wheel_torque_speed_curve", "1" if _C["wheel_torque_speed_curve"] else "0")
_wz = float(os.environ.get("RM_WZ_MAX", "14.0"))
add("yaw_command_limit_rad_s", [_wz])
add("wheel_rad_s_per_yaw_rad_s", [_C["half_track"] / _C["wheel_radius"]])
add("yaw_rate_at_unit_action", [_C["wheel_action_scale"] * _C["wheel_radius"]
                               / _C["half_track"]])
import mujoco as _mj
_m = env.unwrapped.sim.mj_model
_base = _names.base_bodies[0]
_bid = _mj.mj_name2id(_m, _mj.mjtObj.mjOBJ_BODY, "robot/" + _base)
if _bid < 0:
    _bid = _mj.mj_name2id(_m, _mj.mjtObj.mjOBJ_BODY, _base)
add("plant_inertia", "base_mass=%.4f base_com_z=%.4f Izz=%.4f" % (
    float(_m.body_mass[_bid]), float(_m.body_ipos[_bid][2]),
    float(_m.body_inertia[_bid][2])))
add("checkpoint", os.path.abspath(args.checkpoint))
add("checkpoint_iteration", str(_checkpoint_iter))
add("hardware_deployable", "1" if _deployable else "0")
if _block_reason:
    add("deploy_block_reason", _block_reason)
add("train_envelope_matches_contract", "0" if _env_mismatch else "1")
if _env_mismatch:
    add("train_envelope_mismatch", " | ".join(_env_mismatch))
add("train_env_yaml", _TL.params_path(args.checkpoint) or "absent")
# ------------------------------------------------------ action slot order (2026-09-06)
# mjlab resolves the ACTION term in MODEL DEFINITION order (BaseActionCfg.preserve_order
# defaults to False, envs/mdp/actions/actions.py:35) but the OBSERVATION term in the contract
# order (SceneEntityCfg(preserve_order=True)).  For this plant the MJCF defines left_rear1
# before left_front1, so the raw action is [rear1_L, front1_L, rear1_R, front1_R, wL, wR]
# while obs[10:14] is [front1_L, rear1_L, ...].  Every consumer of this ONNX has ONE joints
# list (wheelbipe_ros2_sim2sim state_rl.cpp, sim_mujoco/onnx_play.py, the real bridge), so the
# exported vector is permuted here into the contract order.  Before this the two hip motors
# were swapped in deployment: v14/v15/v16 spun at 2 rev/s inside mjlab and toppled inside
# 0.8 s in native MuJoCo / ROS2 / sim2real.
from rmvehicle import action_order as _AO
_perm, _contract = _AO.permutation(names, _names.leg_joints, _names.wheel_joints)
if _perm != list(range(len(_perm))):
    _AO.permute_onnx(model, _perm)
    print('ACTION ORDER permuted raw->contract:', _perm, _contract)
else:
    print('ACTION ORDER already contract order:', _contract)
add("action_order", ",".join(_contract))
# ---- learned yaw-bias calibration (rmvehicle/yaw_trim.py) -------------------------
# The policies settle at ~0.17 rad/s of unintended yaw at a zero command; on the RMUC2026
# map that is what destroys the straight-line speed.  Solved from the network itself and
# baked into an Add node on obs[2], so ROS2, the CPU parity harness and the real bridge all
# inherit it.  Set RM_YAW_TRIM=off to export the raw policy instead.
_trim = 0.0
if __import__("os").environ.get("RM_YAW_TRIM", "auto") != "off":
    try:
        import onnxruntime  # noqa: F401
    except ModuleNotFoundError:
        # The training venv does not ship onnxruntime.  The raw policy is still a valid
        # artifact; bake the trim later with scripts/bake_yaw_trim.py on any host that has it.
        print("WARN onnxruntime missing: skipping yaw-trim bake. Run "
              "scripts/bake_yaw_trim.py --onnx <this.onnx> --contract <contract.json>.")
    else:
        from rmvehicle import yaw_trim as _YT
        # The trim solver converts a wheel differential into a yaw rate, so it must use
        # THIS plant's wheel scale/radius/half-track.  It used to hardcode the CC numbers.
        _trim, _y0 = _YT.solve_trim(
            _YT.session_from_model(model), geom=_YT.geometry_from_contract(_C))
        if abs(_trim) > 1e-4:
            _YT.bake(model, _trim)
        add("yaw_equilibrium_rad_s", "%.4f" % _y0)
        add("yaw_command_trim_rad_s", "%.4f" % _trim)
        print("YAW TRIM: untrimmed equilibrium %+0.4f rad/s -> baked %+0.4f rad/s"
              % (_y0, _trim))
add("action_order_permutation", ",".join(str(x) for x in _perm))

onnx.save(model, str(out))
print("onnx metadata contract: scale leg %.3f wheel %.3f, kd wheel %.3f, yaw limit %.1f"
      % (_C["leg_action_scale"], _C["wheel_action_scale"], _C["wheel_kd"], _wz))

# and the matching JSON that the ROS2 parameter generator reads
import subprocess
subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "write_deploy_contract.py"),
                "--checkpoint", os.path.abspath(args.out),
                "--wz-max", str(_wz), "--model", _model,
                "--out", args.contract_out], check=True)

# ---------------------------------------------------------------- probe + parity
obs, _ = env.reset()
o = obs["policy" if "policy" in obs else "actor"]
o = o.detach().cpu().numpy().astype(np.float32)

# Same observation, same policy: the ONNX graph may contain (a) the action-order
# permutation applied to the final layer and (b) the baked yaw trim Add on obs[2].
# Undo both on the PyTorch side before comparing, otherwise a correct export looks wrong.
_o_t = o.copy()
if abs(_trim) > 1e-4:
    _o_t[:, 2] += _trim
with torch.no_grad():
    _obs_t = torch.as_tensor(_o_t, device=args.device, dtype=torch.float32)
    # rsl-rl 5.x policies take the observation GROUP dict, not a bare tensor.
    _policy_fn = runner.get_inference_policy(device=args.device)
    try:
        a_torch = _policy_fn({"actor": _obs_t})
    except (IndexError, KeyError):
        a_torch = _policy_fn({"policy": _obs_t})
    a_torch = a_torch.detach().cpu().numpy().astype(np.float32)
a_torch = a_torch[:, _perm]

# onnxruntime is a deployment dependency, not a training one.  The training venv does not
# ship it, so the runtime half of the parity check may run on any host that has it
# (scripts/check_onnx_later.py reads action_torch from the probe npz).
a_onnx = None
try:
    import onnxruntime as ort
except ModuleNotFoundError:
    print("WARN onnxruntime not installed here; runtime parity deferred to "
          "scripts/check_onnx_later.py (probe carries action_torch).")
else:
    sess = ort.InferenceSession(str(out), providers=["CPUExecutionProvider"])
    print("onnx inputs :", [(i.name, i.shape, i.type) for i in sess.get_inputs()])
    print("onnx outputs:", [(o.name, o.shape, o.type) for o in sess.get_outputs()])
    a_onnx = sess.run(None, {"obs": o})[0]
    print("obs shape", o.shape, "action shape", a_onnx.shape)
    print("action sample:", np.round(a_onnx[0], 4))
    _parity = float(np.max(np.abs(a_torch - a_onnx)))
    print("PARITY torch-vs-onnx max_abs_err: %.3e" % _parity)
    if not np.all(np.isfinite(a_onnx)) or _parity > 1e-4:
        raise SystemExit("ONNX/PYTORCH PARITY FAILED: max_abs_err %.3e" % _parity)
    add("export_parity_max_abs_err", "%.3e" % _parity)

payload = dict(obs=o, action_torch=a_torch)
if a_onnx is not None:
    payload["action"] = a_onnx
np.savez(str(out.with_suffix(".obs_probe.npz")), **payload)
add("export_device", args.device)
onnx.save(model, str(out))
env.close()
print("OK: contract verified" + (" (runtime parity deferred)" if a_onnx is None else ""))
