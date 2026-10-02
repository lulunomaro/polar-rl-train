"""Entity configuration for the STEP-derived wheel-leg robot (both model variants)."""
from pathlib import Path

import mujoco

from mjlab.actuator import (
  BuiltinPositionActuatorCfg,
  BuiltinVelocityActuatorCfg,
  DcMotorActuatorCfg,
)
from mjlab.entity import EntityArticulationInfoCfg, EntityCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.utils.spec_config import CollisionCfg

from .names import (CC, LEG_EFFORT, LEG_SATURATION, LEG_VELOCITY, MOTORS,
                    MOTOR_PROFILE, OPEN, WHEEL_EFFORT_P, WHEEL_KNEE_VELOCITY,
                    WHEEL_SATURATION, WHEEL_VELOCITY, ModelNames)

_HERE = Path(__file__).parent
ASSETS = _HERE / "assets"
_WORKSPACE = Path(__file__).resolve().parents[4]

# mjt enum -> the string names mjlab.sim.MujocoCfg accepts.  Kept here (not in env_cfgs)
# so that ``plant_options`` is the single place that reads a plant's physics.
_INTEGRATOR_NAME = {
    int(mujoco.mjtIntegrator.mjINT_EULER): "euler",
    int(mujoco.mjtIntegrator.mjINT_IMPLICITFAST): "implicitfast",
}
_CONE_NAME = {
    int(mujoco.mjtCone.mjCONE_PYRAMIDAL): "pyramidal",
    int(mujoco.mjtCone.mjCONE_ELLIPTIC): "elliptic",
}
_SOLVER_NAME = {
    int(mujoco.mjtSolver.mjSOL_NEWTON): "newton",
    int(mujoco.mjtSolver.mjSOL_CG): "cg",
    int(mujoco.mjtSolver.mjSOL_PGS): "pgs",
}
_ENABLE_FLAG_NAME = {
    getattr(mujoco.mjtEnableBit, n).value: n.removeprefix("mjENBL_").lower()
    for n in dir(mujoco.mjtEnableBit)
    if n.startswith("mjENBL_")
}
_DISABLE_FLAG_NAME = {
    getattr(mujoco.mjtDisableBit, n).value: n.removeprefix("mjDSBL_").lower()
    for n in dir(mujoco.mjtDisableBit)
    if n.startswith("mjDSBL_")
}


# Directories that used to hold the runnable plant and are sealed off as of 2026-09-10.
# 0908/0910 lived under `incoming/rm2025_fixed`; the MOD4 delivery replaced both.  A plant
# that still resolves into that directory is a bug (or a stale config), not a choice, so
# fail loudly instead of silently training a retired mechanism.
_DEPRECATED_PLANT_DIRS = ("rm2025_fixed",)


def _resolve_path(names: ModelNames) -> Path:
  path = Path(names.xml_name)
  resolved = path if path.is_absolute() else ASSETS / path
  for part in resolved.parts:
    if part in _DEPRECATED_PLANT_DIRS:
      raise RuntimeError(
        "DEPRECATED PLANT: %s resolves inside '%s'. The 0908/0910 models are retired - "
        "see incoming/rm2025_fixed/DO_NOT_USE.md; the live plant is "
        "incoming/rm2025_mod4/robot_hifi.xml." % (resolved, part))
  return resolved


def wheel_effort_for(names: ModelNames) -> float:
  """Wheel torque cap actually used by BOTH training and the deployment plant."""
  return float(names.wheel_effort_override or WHEEL_EFFORT_P)


# Reflected rotor inertia the delivered 0910 MJCF carries on left/right_wheel_spin:
# 4e-6 * 15.8^2.  Used only to REPORT the contract when no override is set; the training
# model gets it straight from the source MJCF, and scripts/check_model_identity.py reads it
# back out of the compiled env model instead of trusting this constant.
WHEEL_ARMATURE_DELIVERED = 4e-6 * 15.8 * 15.8


def wheel_armature_for(names: ModelNames) -> float:
  """Wheel-joint armature actually present in the training model.

  0 in ``wheel_armature_override`` means "keep whatever the source MJCF declares".
  Since 2026-09-10 that is the delivered 9.9856e-4 kg*m^2, so the old placeholder is no
  longer applied; this helper keeps the reported contract honest either way.
  """
  return float(names.wheel_armature_override or WHEEL_ARMATURE_DELIVERED)


def _portable_path(path: Path) -> str:
  """Store plant paths relative to the workspace so contracts survive the OS move."""
  try:
    return str(path.resolve().relative_to(_WORKSPACE.resolve()))
  except ValueError:
    return str(path)


def plant_options(names: ModelNames) -> dict:
  """The ``<option>`` block of the *source* MJCF, in ``MujocoCfg`` vocabulary.

  ``MjSpec.attach()`` does NOT copy non-default ``<option>`` fields from an entity into
  the mjlab scene: it keeps the scene defaults and only prints a warning.  The previous
  later-model run therefore trained with the scene's ``timestep=0.002`` /
  ``iterations=100`` / ``tolerance=1e-8`` / pyramidal cone while claiming the delivered
  plant's 0.5 ms / 80 / 1e-10 / elliptic settings.  Reading the numbers from the same
  file the deployment ships and re-applying them through ``SimulationCfg.mujoco`` is the
  only way to keep training physics and the sim2sim plant from drifting apart.
  """
  m = mujoco.MjSpec.from_file(str(_resolve_path(names))).compile()
  return dict(
      timestep=float(m.opt.timestep),
      integrator=_INTEGRATOR_NAME[int(m.opt.integrator)],
      cone=_CONE_NAME[int(m.opt.cone)],
      solver=_SOLVER_NAME[int(m.opt.solver)],
      iterations=int(m.opt.iterations),
      ls_iterations=int(m.opt.ls_iterations),
      tolerance=float(m.opt.tolerance),
      ls_tolerance=float(m.opt.ls_tolerance),
      impratio=float(m.opt.impratio),
      gravity=tuple(float(x) for x in m.opt.gravity),
      enableflags=tuple(sorted(n for b, n in _ENABLE_FLAG_NAME.items()
                               if int(m.opt.enableflags) & b)),
      disableflags=tuple(sorted(n for b, n in _DISABLE_FLAG_NAME.items()
                                if int(m.opt.disableflags) & b)),
  )

# DM-J8009-2EC/DM3519 drives: legs position controlled, wheels velocity controlled,
# which is what both the reference stack and the wheelbipe deployment do on hardware.
LEG_KP, LEG_KD = 60.0, 2.0            # PARAMETERS.md section 3
# An EXPLICIT velocity servo is only numerically sound while kd*dt < M_dof.  The wheel DOF
# inertia is 1.62e-3 kg*m^2 (scripts/wheel_servo_stability.py) and both the training physics
# step and the deployed controller step are 2 ms, so the old kd=1.5 gave kd*dt/M = 1.855:
# every step overshoots and the wheel torque rings at the integration limit.  0.6 gives 0.74,
# which is monotone and settles in ~3 steps, and still holds 52 rad/s against a 0.2 N*m
# rolling load with only 0.3 rad/s of droop.  The deployment reads the same number out of
# train/deploy/contract.json, so the two can no longer disagree.
WHEEL_KD = 0.6
# ---- command-delay randomisation (sim2real) ------------------------------------------
# The trained policy runs at 50 Hz and the torque is zero-order-held, but on hardware the
# command reaches the DM drive one CAN frame later and the drive's own loop is 1 kHz, so the
# effective actuation delay is 0-4 ms and it is NOT the same on every joint.  mjlab's actuators
# already implement a per-env delay buffer; lags are counted in PHYSICS timesteps (dt=2 ms),
# so max_lag=2 spans 0..4 ms.  Fudan's open-source wheel-leg project randomises exactly this
# (delay_ms_range=[0,10] in its DR block), which is the independent confirmation I wanted.
import os as _d_os
DELAY_MIN_LAG = int(_d_os.environ.get("RM_DELAY_MIN_LAG", "0"))
DELAY_MAX_LAG = int(_d_os.environ.get("RM_DELAY_MAX_LAG", "2"))
DELAY_HOLD_PROB = float(_d_os.environ.get("RM_DELAY_HOLD_PROB", "0.75"))
DELAY_UPDATE_PERIOD = int(_d_os.environ.get("RM_DELAY_UPDATE_PERIOD", "10"))  # 20 ms
DELAY_KW = dict(delay_min_lag=DELAY_MIN_LAG, delay_max_lag=DELAY_MAX_LAG,
                delay_hold_prob=DELAY_HOLD_PROB, delay_update_period=DELAY_UPDATE_PERIOD,
                delay_per_env_phase=True)
# Optional measured wheel torque-speed curve (SCUT-style CSV).  Empty -> analytic envelope.
WHEEL_CURVE_PATH = _d_os.environ.get("RM_WHEEL_CURVE", "")
WHEEL_EFFORT = WHEEL_EFFORT_P
LEG_ACTION_SCALE = 0.5                # rad per unit action
# A counter-rotating spin at yaw rate wz needs wheel speed wz*half_track/wheel_r:
# half_track 0.270 m, wheel_r 0.073 m -> 3.70 rad/s of wheel per rad/s of yaw.
#   14 rad/s of 小陀螺  ->  51.8 rad/s per wheel      (DM3519+15.8 no-load is 55.36)
# The action unit therefore has to BE the wheel speed the motor can reach.  At the old scale
# of 10 a full-scale action was 2.7 rad/s of yaw and at 20 it was 5.4 -- which is precisely
# where v11 (5.35) and v12 (5.75) plateaued.  Not a learning failure: an action-unit ceiling.
# At 55 the range action +-1 covers the whole usable wheel-speed range (yaw 0.27 -> 14.9), so
# full 小陀螺 rate sits inside the linear part of the policy output.
import os as _os
WHEEL_ACTION_SCALE = float(_os.environ.get("RM_WHEEL_SCALE", "55.0"))

# back-compat aliases used by the open-chain (serial 2-DOF) regression config
HIP_KP, HIP_KD, HIP_EFFORT = LEG_KP, LEG_KD, 24.0
KNEE_KP, KNEE_KD, KNEE_EFFORT = LEG_KP, LEG_KD, 30.0
# Deliberately NOT re-aliasing LEG_EFFORT any more: this file used to end with
#   LEG_KP, LEG_KD, LEG_EFFORT = HIP_KP, HIP_KD, KNEE_EFFORT
# which silently redefined the datasheet value imported from names.py (40 N*m) as the OPEN
# model's 30 N*m knee torque.  Four different leg torque ceilings (54 / 50.9 / 40 / 30) were
# in play across the pipeline at once; this is the kind of shadowing that produced them.
HIP_PATTERNS = OPEN.leg_joints[0::2]
KNEE_PATTERNS = OPEN.leg_joints[1::2]
LEG_PATTERNS = (r"^(hip|knee)_(L|R)_joint$",)
WHEEL_PATTERNS = OPEN.wheel_joints


def get_spec(names: ModelNames = CC) -> mujoco.MjSpec:
  """Load the MJCF.  Only the *policy-driven* actuators are removed and re-added through
  mjlab actuator configs; anything else in the file (there is none any more: the gas
  spring is now native joint stiffness/damping) is left alone."""
  # The closed-chain file carries exactly the six policy-driven motors (the gas spring
  # is native joint stiffness/damping now), so dropping all of them and re-adding them
  # through mjlab actuator configs is both simple and lossless.
  model_path = _resolve_path(names)
  spec = mujoco.MjSpec.from_file(str(model_path))
  for act in list(spec.actuators):
    spec.delete(act)
  if names.key == "rm2025_later_no_gimbal":
    # The delivered XML predates the confirmed DM8009 rotor-inertia correction and carries
    # 0.025 kg.m2.  Apply the contract value at runtime without rewriting the identity-pinned
    # source MJCF.
    active = {"left_hip", "left_crank", "right_hip", "right_crank"}
    for joint in spec.joints:
      if joint.name in active:
        joint.armature = 1.95e-4 * 9.0 * 9.0
      if names.wheel_armature_override and joint.name in {
          "left_wheel_spin", "right_wheel_spin"}:
        # Escape hatch only.  The 0908 XML carried armature=0 (so the wheel-armature DR was
        # a no-op and this had to inject a placeholder); the 0910 XML carries the reflected
        # rotor inertia itself, the override is left at 0 and the delivered value is used.
        joint.armature = names.wheel_armature_override
  return spec


def make_robot_cfg(names: ModelNames = CC) -> EntityCfg:
  legs = []
  delay_kw = dict(DELAY_KW)
  if names.physics_dt < 0.002 and "RM_DELAY_MAX_LAG" not in _d_os.environ:
    # SCUT trains 0..20 ms of command latency at 200 Hz (up to one control step of their
    # 50 Hz policy).  Our later plant runs at 100 Hz control, so 0..10 ms is the equivalent
    # one-control-step worst case; the old 0..4 ms only covered a CAN frame, not the drive.
    delay_kw["delay_max_lag"] = int(round(0.010 / names.physics_dt))
  if MOTOR_PROFILE == "dm8009":
    # DM-J8009-2EC 9:1 at 24 V: the current limit holds 40 N*m up to about
    # 4.19 rad/s; the voltage line (53.33 N*m intercept) then reaches zero at
    # 16.76 rad/s.  An explicit PD is also what the onboard DM drive runs.
    for pat, eff in zip(names.leg_actuators, names.leg_effort):
      legs.append(DcMotorActuatorCfg(
        target_names_expr=(pat,), stiffness=LEG_KP, damping=LEG_KD,
        effort_limit=eff, saturation_effort=LEG_SATURATION,
        velocity_limit=LEG_VELOCITY,
        **delay_kw))
    # DM3519 + 15.8 (0.90 relative gearbox efficiency, 0910 delivery) at 24 V: 5.7759 N*m
    # current plateau through 44.0119 rad/s, followed by the voltage-limited fall to zero
    # at 55.3557 rad/s.  DcMotorActuator represents that two-piece envelope when the
    # voltage-line intercept is 28.1853 N*m and effort_limit is the current plateau.
    if WHEEL_CURVE_PATH:
      from .actuators import CurveMotorActuatorCfg
      wheels = [CurveMotorActuatorCfg(
        target_names_expr=names.wheel_actuators, stiffness=0.0, damping=WHEEL_KD,
        effort_limit=wheel_effort_for(names), saturation_effort=WHEEL_SATURATION,
        velocity_limit=WHEEL_VELOCITY, curve_path=WHEEL_CURVE_PATH,
        gear_ratio=MOTORS["wheel_total_ratio"], gearbox_efficiency=1.0,
        output_stall_torque=WHEEL_SATURATION, **delay_kw)]
    else:
      wheels = [DcMotorActuatorCfg(
        target_names_expr=names.wheel_actuators, stiffness=0.0, damping=WHEEL_KD,
        effort_limit=wheel_effort_for(names), saturation_effort=WHEEL_SATURATION,
        velocity_limit=WHEEL_VELOCITY, **delay_kw)]
  else:
    for pat, eff in zip(names.leg_actuators, names.leg_effort):
      legs.append(BuiltinPositionActuatorCfg(
        target_names_expr=(pat,), stiffness=LEG_KP, damping=LEG_KD, effort_limit=eff))
    wheels = [BuiltinVelocityActuatorCfg(
      target_names_expr=names.wheel_actuators, damping=WHEEL_KD,
      effort_limit=wheel_effort_for(names))]
  wheel_geoms = tuple(names.wheel_geoms)
  # The chassis box must NOT touch the heightfield terrain: a 0.71 x 0.39 m box over a
  # 0.1 m grid spans more than MuJoCo's 50-contact-per-pair limit, which floods the log
  # with "height field collision overflow" and silently drops contacts.  Legs and wheels
  # are thin enough to stay inside the limit, so they keep colliding (the robot still
  # cannot crawl through a barricade), and falling is detected by bad_orientation.
  collision = CollisionCfg(
    geom_names_expr=tuple(names.collide_geoms), contype=0, conaffinity=1,
    condim={wheel_geoms[0]: 6, ".*": 1},
    priority={wheel_geoms[0]: 1},
    friction={wheel_geoms[0]: names.wheel_friction},
    # everything not listed above (the big base box and every visual MESH geom, whose
    # 0.68 x 0.39 x 0.61 m AABB spans far more than 50 heightfield cells) gets its
    # collision turned OFF, which is what stops MuJoCo's
    # "height field collision overflow" flood on rough terrain.
    disable_other_geoms=True,
  )
  return EntityCfg(
    init_state=EntityCfg.InitialStateCfg(
      # The model origin sits in the middle of the wheel axles, so on flat ground the
      # root height equals the wheel radius (73 mm).  qpos 0 for every joint is the CAD
      # pose, which closes both linkage loops exactly.
      pos=(0.0, 0.0, names.root_height),
      joint_pos={r".*": 0.0},
      joint_vel={".*": 0.0},
    ),
    collisions=(collision,),
    spec_fn=lambda n=names: get_spec(n),
    articulation=EntityArticulationInfoCfg(actuators=tuple(legs) + tuple(wheels),
                                           soft_joint_pos_limit_factor=0.95),
  )


def get_robot_cfg(names: ModelNames = OPEN) -> EntityCfg:
  return make_robot_cfg(names)


def leg_asset_cfg(names: ModelNames = CC) -> SceneEntityCfg:
  return SceneEntityCfg("robot", joint_names=tuple(names.leg_joints))


def wheel_asset_cfg(names: ModelNames = CC) -> SceneEntityCfg:
  return SceneEntityCfg("robot", joint_names=tuple(names.wheel_joints))

def _leg_drive_role(joint_name: str) -> str:
  """Map a resolved leg-drive joint to its mechanical role.

  The earlier CC plant calls the crank drive ``front1``; the later delivered plant calls
  it ``crank``.  Both must be documented as the crank drive so the deployment bridge can
  never rename it to a passive knee.
  """
  return "crank_drive" if ("crank" in joint_name or "front1" in joint_name) else "thigh_drive"


def _resolved_action_order(names: ModelNames):
  """(raw mjlab action order, exported contract order, permutation) for this plant."""
  from . import action_order as AO
  m = mujoco.MjModel.from_xml_path(str(_resolve_path(names)))
  model_joints = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i)
                  for i in range(m.njnt)]
  perm, contract_order = AO.permutation(model_joints, names.leg_joints,
                                        names.wheel_joints)
  natural = ([n for n in model_joints if n in set(contract_order[:4])]
             + [n for n in model_joints if n in set(contract_order[4:])])
  return natural, contract_order, perm


def contract(names: ModelNames = CC) -> dict:
    '''Everything the sim2sim / sim2real deployment has to agree with, in one place.

    Written to train/deploy/contract.json by scripts/write_deploy_contract.py and consumed by
    sim2sim/wsl/make_params.py.  These numbers used to live in four files at once (robot_cfg,
    env_cfgs, the controller YAML, the ONNX metadata) and drifted apart silently, which cost
    this project several full debugging cycles.

    ``names`` selects the plant.  It defaults to the earlier CC model only so the historic
    regression call sites keep working; the deployable later no-gimbal plant must be written
    with ``contract(RM2025_LATER)`` and stamped with its own model_key.
    '''
    raw_order, export_order, perm = _resolved_action_order(names)
    leg_names = export_order[:4]
    roles = {n: "%s_%s" % ("left" if n.startswith("left") else "right",
                           _leg_drive_role(n)) for n in leg_names}
    policy_hz = int(round(1.0 / (names.physics_dt * names.decimation)))
    wheel_effort = wheel_effort_for(names)
    # Two-piece DM3519+15.8 envelope: current-limited plateau, then the voltage line.
    wheel_knee = WHEEL_VELOCITY * (1.0 - wheel_effort / WHEEL_SATURATION)
    return dict(
        schema_version=2,
        plant_kind="similar_linkage_closed_chain",
        model_key=names.key,
        model_xml=_portable_path(_resolve_path(names)),
        policy_coordinate_space="actuator_output_joint",
        policy_controls_passive_knee=False,
        motor_profile=MOTOR_PROFILE,
        leg_joints=list(names.leg_joints), wheel_joints=list(names.wheel_joints),
        leg_actuators=list(names.leg_actuators), wheel_actuators=list(names.wheel_actuators),
        leg_action_scale=LEG_ACTION_SCALE,
        wheel_action_scale=names.wheel_action_scale_override or WHEEL_ACTION_SCALE,
        leg_kp=LEG_KP, leg_kd=LEG_KD, wheel_kd=WHEEL_KD,
        leg_effort=LEG_EFFORT, wheel_effort=wheel_effort,
        leg_voltage_line_intercept=LEG_SATURATION,
        wheel_voltage_line_intercept=WHEEL_SATURATION,
        leg_no_load=LEG_VELOCITY, wheel_no_load=WHEEL_VELOCITY,
        wheel_knee_speed=wheel_knee,
        leg_motor_model=MOTORS["leg_model"],
        wheel_motor_model=MOTORS["wheel_model"],
        leg_internal_reduction=MOTORS["leg_internal_ratio"],
        leg_external_chain_ratio=MOTORS["leg_external_ratio"],
        wheel_total_reduction=MOTORS["wheel_total_ratio"],
        wheel_radius=names.wheel_radius, half_track=names.half_track,
        root_height=names.root_height, decimation=names.decimation,
        wheel_armature=wheel_armature_for(names),
        wheel_torque_curve_source=WHEEL_CURVE_PATH or "analytic_two_piece",
        obs_width=35, action_width=6, policy_hz=policy_hz,
        physics_dt=names.physics_dt,
        wheel_torque_speed_curve=True,
        # The second hip-axis motor drives the crank through the chain.  It is
        # never renamed to, observed as, or commanded as a passive knee joint.
        leg_drive_roles=roles,
        hardware_wire_contract={
            "state_and_command_coordinate": "model_output_radians",
            "effort_coordinate": "model_output_newton_meters",
            "normalization_owner": "embedded_firmware",
            "calibration_required_before_real_enable": True,
            "calibration_template": "train/deploy/hardware_calibration.template.json",
        },
        # ---- action slot order (the bug that made every deployment fall over 2026-09-06)
        # mjlab resolves the ACTION term in MODEL DEFINITION order (BaseActionCfg.
        # preserve_order defaults to False) but the OBSERVATION term in the contract order
        # (SceneEntityCfg(preserve_order=True)), so the raw 6-D action is
        # [rear1_L, front1_L, rear1_R, front1_R, wheel_L, wheel_R] while obs[10:14] is
        # [front1_L, rear1_L, front1_R, rear1_R].  train/export_onnx.py permutes the exported
        # network so the ONNX always speaks the contract order, which is what
        # wheelbipe_ros2_sim2sim, sim_mujoco/onnx_play.py and the real bridge assume.
        # scripts/check_action_order.py gates all three against the plant model.
        action_slot_order_raw=raw_order,
        action_slot_order_exported=export_order,
        export_action_permutation=perm,
    )

