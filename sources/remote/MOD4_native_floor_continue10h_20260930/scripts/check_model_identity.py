"""Hard gate: the mjlab TRAINING plant must be the delivered deployment MJCF.

The failure this exists to catch (2026-09-09): ``MjSpec.attach()`` does not propagate an
entity's non-default ``<option>`` block into the mjlab scene.  The later no-gimbal run
therefore trained at the scene defaults (0.002 s, 100 iterations, 1e-8, pyramidal) while
the report and the deployment plant said 0.0005 s / 80 / 1e-10 / elliptic.  Every number
below is read back out of the *compiled environment model*, never out of the config that
was supposed to set it.

Run on the training host (CUDA is required to build the env):

  PYTHONPATH=train/rmvehicle/src:third_party/rc_mjlab/mjlab/src \
    python scripts/check_model_identity.py --task RM2025-Later-CC-Flat-v0
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import mujoco
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "train" / "rmvehicle" / "src"))

import rmvehicle  # noqa: E402,F401  registers the tasks
from mjlab.envs import ManagerBasedRlEnv  # noqa: E402
from mjlab.tasks.registry import load_env_cfg  # noqa: E402
from rmvehicle import robot_cfg as RC  # noqa: E402
from rmvehicle.names import CC, RM2025_LATER, WHEEL_SATURATION  # noqa: E402

MODELS = {"later": RM2025_LATER, "cc": CC}
FAIL: list[str] = []


def ok(cond: bool, msg: str) -> None:
  print(("   OK   " if cond else "   FAIL ") + msg)
  if not cond:
    FAIL.append(msg)


def joint_names(m: mujoco.MjModel) -> list[str]:
  return [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(m.njnt)]


def body_names(m: mujoco.MjModel) -> list[str]:
  return [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, i) for i in range(m.nbody)]


def norm(name: str | None) -> str | None:
  """mjlab prefixes attached entities: ``robot/left_hip`` -> ``left_hip``."""
  return None if name is None else name.split("/")[-1]


def actuated_joints(m: mujoco.MjModel) -> list[str]:
  out = []
  for i in range(m.nu):
    jid = int(m.actuator_trnid[i, 0])
    out.append(norm(mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, jid)))
  return out


def opt_dict(m: mujoco.MjModel) -> dict:
  return dict(
      timestep=round(float(m.opt.timestep), 12),
      integrator=int(m.opt.integrator), cone=int(m.opt.cone),
      solver=int(m.opt.solver), iterations=int(m.opt.iterations),
      ls_iterations=int(m.opt.ls_iterations),
      tolerance=float(m.opt.tolerance),
      ls_tolerance=float(m.opt.ls_tolerance),
      impratio=float(m.opt.impratio),
      gravity=tuple(round(float(x), 9) for x in m.opt.gravity),
      enableflags=int(m.opt.enableflags),
      disableflags=int(m.opt.disableflags))


def sha256_of(path: Path) -> str:
  import hashlib
  h = hashlib.sha256()
  with open(path, "rb") as fh:
    for chunk in iter(lambda: fh.read(1 << 20), b""):
      h.update(chunk)
  return h.hexdigest()


def load_provenance(plant_path: Path) -> dict | None:
  """Delivered-model provenance pin sitting next to the plant, if the checkout has one.

  Added 2026-09-10 with the 0910 swap: it pins the plant XML hash AND the derived motor
  constants, so neither a silently-restored old file nor a stale `names.py` constant can
  pass this gate.
  """
  p = plant_path.parent / "PLANT_PROVENANCE.json"
  if not p.exists():
    print("   NOTE   no PLANT_PROVENANCE.json next to %s: hash/constant pin skipped"
          % plant_path.name)
    return None
  return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
  ap = argparse.ArgumentParser()
  ap.add_argument("--task", default="RM2025-Later-CC-Flat-v0")
  ap.add_argument("--model", choices=sorted(MODELS), default="later")
  ap.add_argument("--num-envs", type=int, default=4)
  ap.add_argument("--device", default="cuda:0")
  ap.add_argument("--rollout-steps", type=int, default=0,
                  help="apply zero actions for N control steps and report survival")
  ap.add_argument("--nominal-start", action="store_true",
                  help="remove reset pose/velocity randomization before the rollout")
  ap.add_argument("--json-out", default="")
  a = ap.parse_args()

  names = MODELS[a.model]
  src = mujoco.MjModel.from_xml_path(str(RC._resolve_path(names)))
  print("source plant :", RC._portable_path(RC._resolve_path(names)))
  print("task         :", a.task)

  cfg = load_env_cfg(a.task, play=False)
  cfg.scene.num_envs = a.num_envs
  cfg.auto_reset = True
  if a.nominal_start:
    cfg.events.pop("push_robot", None)
    rb = cfg.events.get("reset_base")
    if rb is not None:
      rb.params["pose_range"] = {"x": (0.0, 0.0), "y": (0.0, 0.0), "yaw": (0.0, 0.0)}
      rb.params["velocity_range"] = {k: (0.0, 0.0) for k in
                                     ("x", "y", "z", "roll", "pitch", "yaw")}
  env = ManagerBasedRlEnv(cfg=cfg, device=a.device)
  m = env.sim.mj_model

  print("\n[1] plant identity")
  so, eo = opt_dict(src), opt_dict(m)
  for k in so:
    ok(so[k] == eo[k], "option %-12s training=%r source=%r" % (k, eo[k], so[k]))
  # Provenance pin: the SHA256 of the source file itself, so a silently restored older
  # plant cannot pass the numeric checks below just because they were re-tuned to match.
  prov = load_provenance(RC._resolve_path(names))
  if prov:
    ok(sha256_of(RC._resolve_path(names)) == prov["xml_sha256"],
       "source plant sha256 == provenance pin (version %s)" % prov.get("version"))
  ok(m.nq == src.nq and m.nv == src.nv and m.neq == src.neq,
     "nq/nv/neq training=(%d,%d,%d) source=(%d,%d,%d)"
     % (m.nq, m.nv, m.neq, src.nq, src.nv, src.neq))
  ok(m.nu == src.nu, "actuator count training=%d source=%d" % (m.nu, src.nu))
  ok(sorted(actuated_joints(m)) == sorted(actuated_joints(src)),
     "actuated joint set matches: %s" % actuated_joints(m))
  sj = {norm(n) for n in joint_names(src)} - {None}
  ej = {norm(n) for n in joint_names(m)} - {None}
  ok(sj <= ej, "every source joint exists in the scene: missing=%s" % sorted(sj - ej))
  sb = {norm(n) for n in body_names(src)} - {None}
  eb = {norm(n) for n in body_names(m)} - {None}
  ok(sb <= eb, "every source body exists in the scene: missing=%s" % sorted(sb - eb))
  ok(int(m.neq) == int(src.neq) and int(m.neq) > 0,
     "closed-chain equalities survived: neq=%d" % m.neq)

  # Active-joint armature correction (DM8009 rotor inertia reflected 9:1).
  arm = {norm(joint_names(m)[j]): float(m.dof_armature[int(m.jnt_dofadr[j])])
         for j in range(m.njnt)}
  arm_src = {norm(joint_names(src)[j]): float(src.dof_armature[int(src.jnt_dofadr[j])])
             for j in range(src.njnt)}
  if a.model == "later":
    want = 1.95e-4 * 81.0
    got = [arm.get(n) for n in ("left_hip", "left_crank", "right_hip", "right_crank")]
    ok(all(g is not None and abs(g - want) < 1e-12 for g in got),
       "active leg armature == %.6g: %s" % (want, got))
    got_w = [arm.get(n) for n in ("left_wheel_spin", "right_wheel_spin")]
    # 2026-09-10: the 0910 delivery carries the reflected rotor inertia itself
    # (4e-6 * 15.8^2 = 9.9856e-4), so the gate now compares the compiled training model
    # against the SOURCE xml instead of a python constant that can go stale.
    want_w = names.wheel_armature_override or arm_src.get("left_wheel_spin")
    ok(all(g is not None and abs(g - want_w) < 1e-12 for g in got_w),
       "wheel armature == %.10g (source MJCF / override): %s" % (want_w, got_w))
    # ...and the SOURCE itself must be self-consistent about the two wheels.
    ok(arm_src.get("left_wheel_spin") == arm_src.get("right_wheel_spin"),
       "source wheel armature left == right: %s / %s"
       % (arm_src.get("left_wheel_spin"), arm_src.get("right_wheel_spin")))
    # Wheel torque envelope: the cap training enforces must equal the cap the DELIVERED
    # deployment plant enforces, read out of the source MJCF's own actuator block.  This
    # is the check that catches a plant swap that keeps the old +-6 N*m training cap.
    src_cap = {}
    for i in range(src.nu):
      jid = int(src.actuator_trnid[i, 0])
      jn = norm(mujoco.mj_id2name(src, mujoco.mjtObj.mjOBJ_JOINT, jid))
      if jn in ("left_wheel_spin", "right_wheel_spin"):
        src_cap[jn] = (float(src.actuator_ctrlrange[i][1]),
                       float(src.actuator_forcerange[i][1]))
    train_effort = RC.wheel_effort_for(names)
    ok(len(src_cap) == 2 and all(
        abs(train_effort - v[0]) < 1e-9 and abs(v[0] - v[1]) < 1e-9
        for v in src_cap.values()),
       "training wheel cap %.10g == delivered ctrlrange/forcerange %s"
       % (train_effort, src_cap))
    if prov:
      w = prov.get("wheel", {})
      ok(abs(train_effort - w.get("peak_torque_nm", -1.0)) < 1e-9,
         "training wheel cap %.10g == provenance peak %.10g"
         % (train_effort, w.get("peak_torque_nm", float("nan"))))
      ok(abs(WHEEL_SATURATION - w.get("envelope_intercept_nm", -1.0)) < 1e-9,
         "wheel voltage-line intercept %.10g == provenance %.10g"
         % (WHEEL_SATURATION, w.get("envelope_intercept_nm", float("nan"))))
      ok(all(g is not None and abs(g - w.get("armature_kg_m2", -1.0)) < 1e-12
             for g in got_w),
         "wheel armature == provenance %.8g" % w.get("armature_kg_m2", float("nan")))
  if prov:
    gs = prov.get("gas_spring", {})
    gas = {}
    for j in range(src.njnt):
      n = norm(joint_names(src)[j])
      if n and n.endswith("_gas_slide"):
        gas[n] = float(src.jnt_stiffness[j])
    ok(len(gas) == 2 and all(
        abs(v - gs.get("stiffness_n_m", -1.0)) < 1e-9 for v in gas.values()),
       "source gas-spring stiffness == provenance %.6g: %s"
       % (gs.get("stiffness_n_m", float("nan")), gas))

  print("\n[2] policy contract")
  obs_dim = env.observation_manager.group_obs_dim["actor"]
  act_dim = env.action_manager.total_action_dim
  c = RC.contract(names)
  ok(int(np.sum(obs_dim)) == 35, "actor obs width == 35 (got %s)" % (obs_dim,))
  ok(act_dim == 6, "action width == 6 (got %d)" % act_dim)
  ok(c["obs_width"] == 35 and c["action_width"] == 6, "contract widths agree")
  ok(abs(env.physics_dt - c["physics_dt"]) < 1e-12,
     "physics_dt %.6g == contract %.6g" % (env.physics_dt, c["physics_dt"]))
  ok(abs(1.0 / env.step_dt - c["policy_hz"]) < 1e-6,
     "policy rate %.3f Hz == contract %s Hz" % (1.0 / env.step_dt, c["policy_hz"]))
  ok(abs(float(m.opt.timestep) - c["physics_dt"]) < 1e-12,
     "compiled timestep == contract physics_dt")
  ok(c["export_action_permutation"] == [1, 0, 3, 2, 4, 5] or a.model == "cc",
     "export action permutation %s" % c["export_action_permutation"])
  ok(all("knee" not in n for n in c["action_slot_order_exported"]),
     "no passive knee in the exported action order: %s" % c["action_slot_order_exported"])
  print("   contract  :", json.dumps({k: c[k] for k in (
      "model_key", "policy_hz", "physics_dt", "wheel_radius", "half_track",
      "action_slot_order_raw", "action_slot_order_exported",
      "export_action_permutation", "leg_drive_roles")}, ensure_ascii=False))

  result = dict(task=a.task, model=a.model, options=eo, obs_dim=list(obs_dim),
                action_dim=act_dim, contract=c)

  if a.rollout_steps > 0:
    print("\n[3] zero-action stand rollout (%d control steps = %.2f s)"
          % (a.rollout_steps, a.rollout_steps * env.step_dt))
    env.reset()
    robot = env.scene["robot"]
    zero = torch.zeros(env.num_envs, act_dim, device=env.device)
    term_count = torch.zeros(env.num_envs, device=env.device)
    heights, tilts = [], []
    for step in range(a.rollout_steps):
      env.step(zero)
      term_count += env.reset_terminated.float()
      g = robot.data.projected_gravity_b
      alive = ~env.reset_terminated
      if alive.any():
        heights.append(float(robot.data.root_link_pos_w[alive, 2].mean()))
        tilts.append(float(torch.acos((-g[alive, 2]).clamp(-1.0, 1.0)).mean()))
    h = np.asarray(heights)
    t = np.asarray(tilts)
    print("   mean root height over rollout: %.4f m (min %.4f)"
          % (h.mean() if h.size else float("nan"), h.min() if h.size else float("nan")))
    print("   mean tilt: %.4f rad (max %.4f)" % (t.mean() if t.size else float("nan"),
                                                 t.max() if t.size else float("nan")))
    print("   terminations/env: %s" % term_count.cpu().numpy().tolist())
    survived = bool((term_count == 0).all())
    if a.nominal_start:
      ok(survived, "zero-action policy survives %d steps from the nominal pose"
         % a.rollout_steps)
    else:
      print("   NOTE   zero-action does not balance a two-wheel base (expected); "
            "this is a plant sanity check, not a policy gate")
    result["rollout"] = dict(steps=a.rollout_steps,
                             mean_height=float(h.mean()) if h.size else None,
                             min_height=float(h.min()) if h.size else None,
                             mean_tilt=float(t.mean()) if t.size else None,
                             max_tilt=float(t.max()) if t.size else None,
                             terminations=term_count.cpu().numpy().tolist())

  print("\nRESULT:", "IDENTITY GATE PASS" if not FAIL else "%d CHECK(S) FAILED" % len(FAIL))
  for f in FAIL:
    print("   - " + f)
  if a.json_out:
    Path(a.json_out).write_text(json.dumps(result, indent=1, ensure_ascii=False),
                                encoding="utf-8")
    print("wrote", a.json_out)
  return 1 if FAIL else 0


if __name__ == "__main__":
  raise SystemExit(main())
