"""MOD4 chassis in Isaac Lab 6.x: deployment-shaped PPO task with SCUT-style randomization.

Design notes (2026-09-10):

* Asset: the MOD4 delivery USD (incoming/chassis_mod4_mjcf_usd_20260910/chassis_mod4/
  isaac/robot.usd).  Every number below is read from the delivered import_contract.json
  that ships next to that USD, so the training plant and the shipped asset cannot drift
  apart silently.
* Contract: 6-D action = [crank_L, hip_L, crank_R, hip_R, wheel_L, wheel_R] in the
  exported wheelbipe order, and the 35-D policy observation of
  train/deploy/contract_rm2025_later.json.  This is the SAME interface the mjlab trainer
  (train/rmvehicle/src/rmvehicle/env_cfgs.py) and the real robot use, so an Isaac-trained
  checkpoint goes through the existing ONNX export instead of a second interface.
* Motors: Isaac Lab DC motor model (stall torque / continuous torque / no-load speed):
  legs 53.3333 / 40.0 / 16.7552, wheels 28.1853 / 5.7759 / 55.3557.  That is exactly the
  plateau-then-voltage-falloff curve the deployment firmware enforces.
* Randomization: the SCUT list already implemented in the mjlab task - sensor delay,
  observation noise, per-episode encoder bias, action delay, motor authority scale and
  per-step noise, armature/joint friction, body mass and inertia, wheel friction, gas
  spring stiffness/damping, sustained push.  See docs/SCUT_ALIGNMENT_AND_DEPLOY_20260909.md.
* Safety gate: `closure_broken` terminates an environment whose closed-chain anchors
  separate by more than 2 mm, so a solver blow-up cannot silently poison a long run.

Engine facts established locally on 2026-09-10 (docs/ISAACLAB_MOD4_20260910.md): the
delivered RuntimeGuard assumed Isaac Lab 2.x quaternion order (w, x, y, z) while 3.0/6.x
use (x, y, z, w); after patching that, the 6000-step PhysX acceptance run passes with
0.51 mm maximum closure error.
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import torch

import isaaclab.sim as sim_utils
from isaaclab.actuators import DCMotor, DCMotorCfg, ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg, AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.envs.mdp import actions as mdp_actions
from isaaclab.envs.mdp import commands as mdp_commands
from isaaclab.envs.mdp import events as mdp_events
from isaaclab.envs.mdp import observations as mdp_obs
from isaaclab.envs.mdp import rewards as mdp_rewards
from isaaclab.envs.mdp import terminations as mdp_term
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.managers import CurriculumTermCfg as CurrTerm
from isaaclab.managers.action_manager import ActionTerm
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import ContactSensorCfg
from isaaclab.sim import SimulationCfg
# Isaac Lab 3.0 packages `configclass` as a submodule; `from isaaclab.utils import
# configclass` silently returns the MODULE once anything (e.g. isaaclab.assets) has imported
# it, which then explodes at the first @configclass with "'module' object is not callable".
# This is the form Isaac Lab's own code uses and it is import-order independent.
from isaaclab.utils.configclass import configclass
from isaaclab.utils.math import quat_apply
from isaaclab.utils.noise import UniformNoiseCfg as Unoise

# The RMUC2026 field builder lives one level up (isaac/rmuc2026_field.py) and is the same
# code the earlier Isaac work used; it reads cad/out_map/field_dims.json, which is also the
# source of the mjlab curriculum's terrain numbers.
_FIELD_DIR = Path(__file__).resolve().parents[1]
if str(_FIELD_DIR) not in sys.path:
    sys.path.insert(0, str(_FIELD_DIR))
import rmuc2026_field as _field  # noqa: E402
import skills_isaac as skills  # noqa: E402
import scut_flat_rescue as scut_rescue

# RM_MOD4_TERRAIN=field adds, per environment: the measured stairs, the 25 deg and 12.1 deg
# ramps, the launch ramp (飞坡) with its landing platform, the gap banks, the barricade and
# the user's 250 mm x 800 mm x 300 mm tunnel.  flat keeps the v1 single cuboid.
TERRAIN = os.environ.get("RM_MOD4_TERRAIN", "flat").strip().lower()
if TERRAIN not in ("flat", "field"):
    raise ValueError("RM_MOD4_TERRAIN must be 'flat' or 'field', got %r" % TERRAIN)
from isaaclab_physx.physics import PhysxCfg

ROOT = Path(__file__).resolve().parents[2]
# The asset may live in the repo's synced copy (incoming/rm2025_mod4/isaac, which is what
# the target machine has) or in the raw unzip directory used during local development.
# Pick whichever actually exists instead of hard-coding one of them.
_ASSET_CANDIDATES = (
    # 2026-09-12 model fix: real CAD hard stop reachable (knee/rocker/gas limits) + the eight
    # 30 mm guide rollers as analytic colliders.  Preferred as soon as it is synced; the old
    # packages stay as fallbacks so a machine without the fix still runs.
    ROOT / "incoming" / "mod4_fixed_20260912" / "chassis_mod4" / "isaac",
    ROOT / "incoming" / "rm2025_mod4" / "isaac",
    ROOT / "incoming" / "chassis_mod4_mjcf_usd_20260910" / "chassis_mod4" / "isaac",
)
_ENV_USD = os.environ.get("RM_MOD4_USD", "").strip()      # explicit override for A/B runs
MOD4_ISAAC = (Path(_ENV_USD).resolve().parent if _ENV_USD else
              next((p for p in _ASSET_CANDIDATES if (p / "robot.usd").is_file()),
                   _ASSET_CANDIDATES[0]))
MOD4 = MOD4_ISAAC.parent
USD_PATH = str(MOD4_ISAAC / "robot.usd")
CONTRACT = json.loads((MOD4_ISAAC / "import_contract.json").read_text(encoding="utf8"))
DELIVERY_CONTRACT = json.loads(
    (ROOT / "train" / "deploy" / "contract_rm2025_later.json").read_text(encoding="utf8"))

# --- joint groups ----------------------------------------------------------------
ACTUATED = list(CONTRACT["actuated_joint_names"])            # model / PhysX order
# Policy + export order (wheelbipe deployment contract, export_action_permutation
# [1, 0, 3, 2, 4, 5] of the raw order).  Keeping the policy in the exported order means
# the ONNX metadata needs no re-permutation.
LEG_ORDER = ["left_crank", "left_hip", "right_crank", "right_hip"]
WHEEL_ORDER = ["left_wheel_spin", "right_wheel_spin"]
ACTION_ORDER = LEG_ORDER + WHEEL_ORDER
GAS_JOINTS = list(CONTRACT["gas_springs"].keys())
PASSIVE_JOINTS = [n for n in CONTRACT["joints"]
                  if n not in ACTUATED + GAS_JOINTS]

LEG_KP = float(DELIVERY_CONTRACT["leg_kp"])                  # 60.0
LEG_KD = float(DELIVERY_CONTRACT["leg_kd"])                  # 2.0
WHEEL_KD = float(DELIVERY_CONTRACT["wheel_kd"])              # 0.6
LEG_ACTION_SCALE = float(DELIVERY_CONTRACT["leg_action_scale"])      # 0.5 rad
WHEEL_ACTION_SCALE = float(DELIVERY_CONTRACT["wheel_action_scale"])  # 10.0 rad/s
LEG_EFFORT = float(CONTRACT["leg_motor"]["peak_torque_nm"])          # 40.0
LEG_STALL = float(DELIVERY_CONTRACT["leg_voltage_line_intercept"])   # 53.3333
LEG_NO_LOAD = float(DELIVERY_CONTRACT["leg_no_load"])                # 16.7552 rad/s
WHEEL_EFFORT = float(DELIVERY_CONTRACT["wheel_effort"])             # 5.7759
WHEEL_STALL = float(DELIVERY_CONTRACT["wheel_voltage_line_intercept"])  # 28.1853
WHEEL_NO_LOAD = float(DELIVERY_CONTRACT["wheel_no_load"])           # 55.3557 rad/s
POLICY_HZ = float(DELIVERY_CONTRACT["policy_hz"])                   # 100 Hz
PHYSICS_DT = float(CONTRACT["physics_dt_s"])                        # 0.0005 s
DECIMATION = int(round((1.0 / POLICY_HZ) / PHYSICS_DT))             # 20

# --- SCUT randomization knobs (same names as the mjlab task) ----------------------
def _f(name: str, default: float) -> float:
    return float(os.environ.get(name, str(default)))


# P2 staging (audit item 8): RM_DR_OFF=1 has to be read BEFORE the knob block below.
# Gating only the EventCfg terms left the observation noise, the sensor-delay lines and the
# action-delay line alive, so the "nominal" stage still ran a noisy, latency-shifted task --
# and the delay-line reset was skipped with them (ghost samples from the previous episode).
DR_OFF = os.environ.get("RM_DR_OFF", "").strip() == "1"

EFFORT_LEG = (_f("RM_EFFORT_LEG_MIN", 0.75), _f("RM_EFFORT_LEG_MAX", 1.25))
EFFORT_WHEEL = (_f("RM_EFFORT_WHEEL_MIN", 0.90), _f("RM_EFFORT_WHEEL_MAX", 1.10))
EFFORT_NOISE = 0.0 if DR_OFF else _f("RM_EFFORT_NOISE", 0.03)
EFFORT_NOISE_WHEEL = 0.0 if DR_OFF else _f("RM_EFFORT_NOISE_WHEEL", 0.02)
ARMATURE_SCALE = (0.7, 1.6)
LEG_FRICTION_MAX = _f("RM_LEG_FRICTION_MAX", 0.10)
WHEEL_FRICTION_MAX = _f("RM_WHEEL_FRICTION_MAX", 0.02)
ENCODER_BIAS = _f("RM_ENCODER_BIAS", 0.015)
OBS_DELAY_MIN = 0 if DR_OFF else int(_f("RM_OBS_DELAY_MIN_LAG", 1))
OBS_DELAY_MAX = 0 if DR_OFF else int(_f("RM_OBS_DELAY_MAX_LAG", 2))
ACTION_DELAY_MIN = 0 if DR_OFF else int(_f("RM_ACTION_DELAY_MIN_LAG", 0))
ACTION_DELAY_MAX = 0 if DR_OFF else int(_f("RM_ACTION_DELAY_MAX_LAG", 2))
DELAY_HOLD_PROB = _f("RM_OBS_DELAY_HOLD_PROB", 0.75)
DELAY_PERIOD = int(_f("RM_OBS_DELAY_UPDATE_PERIOD", 10))
HEIGHT_RANGE = (_f("RM_HEIGHT_MIN", 0.18), _f("RM_HEIGHT_MAX", 0.34))
# Dense penalty for sitting below the commanded height on flat ground (2026-09-28).
# The Gaussian height reward alone let the policy drift down until the 0.10 m low_base
# cut-off: half the episodes ended by sinking with attitude intact.  This term makes
# every centimetre below the command cost something, every step.
W_HEIGHT_DEFICIT = _f("RM_W_HEIGHT_DEFICIT", -12.0)
# Symmetric linear height-tracking weight (2026-09-28): the Gaussian kernel is flat beyond
# ~6 cm, so a policy standing 9-12 cm off receives essentially no gradient.
W_HEIGHT_LINEAR = _f("RM_W_HEIGHT_LINEAR", -1.0)
# SCUT-style height kernels: one wide (sigma 0.02) + one tight (sigma 0.005).
HEIGHT_SIGMA = _f("RM_HEIGHT_SIGMA", 0.02)
HEIGHT_TIGHT_SIGMA = _f("RM_HEIGHT_TIGHT_SIGMA", 0.005)
W_HEIGHT_TIGHT = _f("RM_W_HEIGHT_TIGHT", 0.5)
# Flat-orientation weight (2026-09-28): measured tilt 9-11 deg against an 8 deg gate.
W_FLAT_ORIENT = _f("RM_W_FLAT_ORIENT", -1.5)
# ---- 2026-09-28 SCUT 对齐（证据与推导见 docs/MOD4_REWARD_FIX_SCUT_PARITY_20260928.md）----
# 平地策略收敛成"站着不动"（探针：指令 0.30/0.60/1.00 m/s -> 实际速度 0.00），原因有三：
#   1. 速度项只有 exp 宽核（std 0.7071），不动也能拿 1.38/2.0；
#   2. 角速度项权重 5.0 而 wz 指令恒为 0 -> 站着白拿 ~5.0；
#   3. 指令下限 0.0，等于允许"站着"这个答案。
# 华南虎自己的平地任务：exp 核之外再挂一个平方误差罚，且指令下限 0.30（从不命令站立）。
# 下面三个旋钮把结构补齐；默认值保持原行为，只有显式打开才变。
W_TRACK_ANG = _f("RM_W_TRACK_ANG", 5.0)              # SCUT 平地走路 run 用 1.0
W_RUN_VEL_ERROR = _f("RM_W_RUN_VEL_ERROR", 0.0)      # SCUT 平地走路 run 用 -1.0（稠密 (m/s)^2）
W_HEIGHT_L2 = _f("RM_W_HEIGHT_L2", 0.0)              # SCUT track_height_square = -1.0（双向）
HEIGHT_L2_CLAMP = _f("RM_HEIGHT_L2_CLAMP", 0.15)     # SCUT height_err_constraint = 0.15 m
# ---- 2026-09-28 华南虎门控 + 双轮接地高度项（出处：华南虎官方仓库 wheelbipe25_v3）----------
# 病灶：四件套之后策略学会"趴/蹦着把速度做满"（探针 model_1850：0.6/1.0 m/s 档车高只有
# 0.096/0.120 m，1.0 档双轮接地 23%，导轮接触 0% —— 低空蹦跳，不是滚）。
# 华南虎同一问题的两件工具：
#   1) vel_height_gate —— 高度没跟住时把速度/角速度奖励（含误差罚）整体乘 0~1 的门控；
#      原文注释 "避免 policy 为了追速度牺牲高度"（linear_band: ±5cm=1, ≥10cm=0）。
#   2) track_height_exp_both_wheels_contact（权重 0.3）—— 高度奖励只在双轮同时接地时发放。
VEL_HEIGHT_GATE_MODE = os.environ.get("RM_VEL_HEIGHT_GATE", "off").strip().lower()
VEL_HEIGHT_GATE_FULL = _f("RM_VEL_HEIGHT_GATE_FULL", 0.05)
VEL_HEIGHT_GATE_ZERO = _f("RM_VEL_HEIGHT_GATE_ZERO", 0.10)
VEL_HEIGHT_GATE_SIGMA = _f("RM_VEL_HEIGHT_GATE_SIGMA", HEIGHT_SIGMA)
W_HEIGHT_BOTH_WHEELS = _f("RM_W_HEIGHT_BOTH_WHEELS", 0.0)
# ---- 2026-09-29 全面对齐华南虎 wheelbipe25_v3 平地任务（出处：refs/wheeled-legged_RL-main）----
# 25_v3 平地奖励表（env_cfg.py rewards OrderedDict + env.py 公式，sigma 见 cfg）：
#   track_lin_vel_xy +1.0(σ0.25) / _tight +0.2(σ0.01) / _huge_gap -1.0(err²>0.5) / _square -1.0((0.25err)²)
#   track_ang_vel_z +0.5(σ0.25) / _square -1.0((0.25err)²)
#   track_height_exp +0.7(σ0.01) / _tight +0.3(σ0.001) / _both_wheels +0.3(σ0.1) / _square -1.0((5err)²)
#   lin_vel_z -0.5 / ang_vel_xy -0.05 / action_rate -0.01 / action_smoothness -0.05
#   joint_torque -1e-5 / wheel_power -1e-4 / flat_orientation_* -1.0 / no_fork -1.0 / no_fork_z -2.0
#   ** 没有 alive / 没有 termination 罚 / 没有 wheel_contact **
SCUT_LIN_W = _f("RM_SCUT_LIN_W", 1.0)
SCUT_LIN_SIGMA = _f("RM_SCUT_LIN_SIGMA", 0.25)
SCUT_LIN_TIGHT_W = _f("RM_SCUT_LIN_TIGHT_W", 0.2)
SCUT_LIN_TIGHT_SIGMA = _f("RM_SCUT_LIN_TIGHT_SIGMA", 0.01)
SCUT_LIN_GAP_W = _f("RM_SCUT_LIN_GAP_W", -1.0)
SCUT_LIN_GAP = _f("RM_SCUT_LIN_GAP", 0.5)
SCUT_LIN_SQ_W = _f("RM_SCUT_LIN_SQ_W", -1.0)
SCUT_LIN_SQ_SIGMA = _f("RM_SCUT_LIN_SQ_SIGMA", 0.25)
SCUT_ANG_W = _f("RM_SCUT_ANG_W", 0.5)
SCUT_ANG_SIGMA = _f("RM_SCUT_ANG_SIGMA", 0.25)
SCUT_ANG_SQ_W = _f("RM_SCUT_ANG_SQ_W", -1.0)
SCUT_ANG_SQ_SIGMA = _f("RM_SCUT_ANG_SQ_SIGMA", 0.25)
SCUT_H_W = _f("RM_SCUT_H_W", 0.7)
SCUT_H_SIGMA = _f("RM_SCUT_H_SIGMA", 0.01)
SCUT_H_TIGHT_W = _f("RM_SCUT_H_TIGHT_W", 0.3)
SCUT_H_TIGHT_SIGMA = _f("RM_SCUT_H_TIGHT_SIGMA", 0.001)
SCUT_H_SOFT_SIGMA = _f("RM_SCUT_H_SOFT_SIGMA", 0.1)
SCUT_H_SQ_W = _f("RM_SCUT_H_SQ_W", -1.0)
SCUT_H_SQ_SIGMA = _f("RM_SCUT_H_SQ_SIGMA", 5.0)
SCUT_ALIVE_W = _f("RM_SCUT_ALIVE_W", 0.0)          # 华南虎平地：没有 alive
SCUT_TERM_W = _f("RM_SCUT_TERM_W", 0.0)            # 华南虎平地：没有 termination 罚
SCUT_WHEEL_CONTACT_W = _f("RM_SCUT_WHEEL_CONTACT_W", 0.0)
SCUT_ORIENT_W = _f("RM_SCUT_ORIENT_W", -1.0)
SCUT_LINVELZ_W = _f("RM_SCUT_LINVELZ_W", -0.5)
SCUT_ACTION_RATE_W = _f("RM_SCUT_ACTION_RATE_W", -0.01)
SCUT_ACTION_ACC_W = _f("RM_SCUT_ACTION_ACC_W", -0.05)
SCUT_TORQUE_W = _f("RM_SCUT_TORQUE_W", -1.0e-5)
SCUT_POWER_W = _f("RM_SCUT_POWER_W", -1.0e-4)
SCUT_BASE_CONTACT_W = _f("RM_SCUT_BASE_CONTACT_W", -2.0)
RANDOM_START = os.environ.get("RM_RANDOM_START", "0").strip() not in ("", "0", "off")
RANDOM_START_LEG = _f("RM_RANDOM_START_LEG", 0.25)
RANDOM_START_WHEEL_VEL = _f("RM_RANDOM_START_WHEEL_VEL", 25.0)
CMD_VX = (_f("RM_CMD_VX_MIN", -1.5), _f("RM_CMD_VX_MAX", 2.8))
# 小陀螺 target is 2 rev/s = 12.57 rad/s; the window is opened further by the gyro_window
# curriculum below, starting at +/-2 rad/s.
CMD_WZ = (_f("RM_CMD_WZ_MIN", -13.0), _f("RM_CMD_WZ_MAX", 13.0))

WHEEL_BODIES = ["left_wheel", "right_wheel"]
LIMB_BODIES = [b for b in CONTRACT["bodies"]
               if b != "chassis" and b not in WHEEL_BODIES]


# --- DC motor with randomized torque authority -------------------------------------
class Mod4DCMotor(DCMotor):
    """DC motor whose torque authority can be randomized per environment.

    The mjlab task randomizes the same thing through `dr.effort_limits`; PhysX drive
    limits are shared by every environment, so the scale is applied to the computed
    effort instead.  `episode_scale` covers unit-to-unit spread, `step_scale` adds the
    per-step gain noise SCUT injects on top of it.
    """

    def __init__(self, cfg, *args, **kwargs):
        super().__init__(cfg, *args, **kwargs)
        # ActuatorBase keeps the environment count and device private.
        self.episode_scale = torch.ones(self._num_envs, 1, device=self._device)
        self.step_scale = torch.ones(self._num_envs, 1, device=self._device)

    def _ids(self, env_ids):
        # The event manager calls step/reset terms with env_ids=None for "all environments";
        # the original code assumed a tensor and would have raised on the very first call
        # (which never happened because "step" mode is not applied by stock Isaac Lab).
        if env_ids is None:
            return torch.arange(self._num_envs, device=self._device)
        if isinstance(env_ids, slice):
            return torch.arange(self._num_envs, device=self._device)[env_ids]
        return env_ids

    def resample_episode_scale(self, env_ids, low: float, high: float) -> None:
        ids = self._ids(env_ids)
        n = int(ids.numel())
        self.episode_scale[ids] = torch.empty(n, 1, device=self._device).uniform_(low, high)

    def resample_step_scale(self, env_ids, low: float, high: float) -> None:
        ids = self._ids(env_ids)
        n = int(ids.numel())
        self.step_scale[ids] = torch.empty(n, 1, device=self._device).uniform_(low, high)

    def _clip_effort(self, effort: torch.Tensor) -> torch.Tensor:
        scaled = super()._clip_effort(effort) * self.episode_scale * self.step_scale
        return scaled


@configclass
class Mod4DCMotorCfg(DCMotorCfg):
    class_type: type = Mod4DCMotor


# --- mass / inertia randomization ------------------------------------------------------
# Isaac Lab's stock randomize_rigid_body_mass/inertia events call the PhysX setters in a way
# that logs hundreds of "PxRigidBody::setMassSpaceInertiaTensor(): components must be
# non-negative" errors per run (measured 2026-09-10: 0 with the events disabled, 368-514
# with them enabled, for 32 environments).  The final state read back is valid, but the
# noise hides real problems and spams the GUI.  Doing it ourselves is quieter AND stricter:
# read the DEFAULT mass/inertia once, multiply by strictly positive factors, write both
# arrays in a single call.
_DR_DEFAULTS: dict = {}


def _dr_defaults(robot):
    key = id(robot)
    if key not in _DR_DEFAULTS:
        # Same source Isaac Lab's own randomizers use (CPU-side torch tensors).
        _DR_DEFAULTS[key] = (robot.data.body_mass.torch.clone(),
                             robot.data.body_inertia.torch.clone())
    return _DR_DEFAULTS[key]


# NOTE: the signature must be exactly (env, env_ids) - Isaac Lab's EventManager inspects it
# and treats extra parameters as mandatory args (a bare **kwargs made every run fail with
# "expects mandatory parameters: ['_kw']").
def randomize_mass_inertia(env, env_ids=None) -> None:
    """SCUT-style mass/inertia randomization for the MOD4 plant, in one validated pass."""
    robot = env.scene["robot"]
    ids = (torch.arange(env.num_envs, device=env.device) if env_ids is None
           else env_ids)
    default_mass, default_inertia = _dr_defaults(robot)
    masses = default_mass.to(env.device).clone()
    inertias = default_inertia.to(env.device).clone()
    names = list(robot.body_names)
    n = int(ids.numel())

    def u(lo: float, hi: float) -> torch.Tensor:
        return torch.empty(n, device=env.device).uniform_(lo, hi)

    c = names.index("chassis")
    masses[ids, c] = torch.clamp(masses[ids, c] + u(-1.0, 2.0), min=1e-3)
    inertias[ids, c] = inertias[ids, c] * u(0.8, 1.2).view(-1, 1)
    scales = {}
    for name in list(LIMB_BODIES) + list(WHEEL_BODIES):
        i = names.index(name)
        limb = name in LIMB_BODIES
        m_scale = u(0.9, 1.1)
        i_scale = u(0.7, 1.3) if limb else u(0.8, 1.2)
        masses[ids, i] = torch.clamp(masses[ids, i] * m_scale, min=1e-4)
        inertias[ids, i] = inertias[ids, i] * i_scale.view(-1, 1)
        scales[name] = (m_scale, i_scale)
    # Write through the articulation's own indexed setters - the same call Isaac Lab's
    # randomize_rigid_body_mass uses (events.py line ~544).  Values are (len(env_ids),
    # len(body_ids)) / (..., 9).
    body_ids = [names.index("chassis")] + [names.index(b) for b in LIMB_BODIES] + \
               [names.index(b) for b in WHEEL_BODIES]
    robot.set_masses_index(masses=masses[ids[:, None], body_ids], body_ids=body_ids, env_ids=ids)
    robot.set_inertias_index(inertias=inertias[ids[:, None], body_ids], body_ids=body_ids, env_ids=ids)


def mod4_robot_cfg(prim_path: str = "/World/envs/env_.*/Robot") -> ArticulationCfg:
    """ArticulationCfg built from the delivered USD + contract."""
    armature = {n: CONTRACT["joints"][n]["armature"] for n in CONTRACT["joints"]}
    damping = {n: CONTRACT["joints"][n]["damping_si"] for n in CONTRACT["joints"]}
    leg_armature = {n: armature[n] for n in LEG_ORDER}
    wheel_armature = {n: armature[n] for n in WHEEL_ORDER}
    leg_damping = {n: max(damping[n], LEG_KD) for n in LEG_ORDER}  # drive kd >= XML damping
    wheel_damping = {n: max(damping[n], WHEEL_KD) for n in WHEEL_ORDER}
    gas = CONTRACT["gas_springs"]
    return ArticulationCfg(
        prim_path=prim_path,
        spawn=sim_utils.UsdFileCfg(
            usd_path=USD_PATH,
            # Reference the source asset instead of copying it per environment: with the
            # default (copy_from_source=True) every env duplicates all 277 CAD meshes and
            # their materials, and 4096 envs blow PhysX's 64K material limit
            # ("PxPhysics::createMaterial: limit of 64K materials reached", measured
            # 2026-09-10).  A reference shares both across environments.
            copy_from_source=False,
            activate_contact_sensors=True,  # chassis_contact sensor + base-contact gate
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                disable_gravity=False, max_depenetration_velocity=1.0,
                linear_damping=0.0, angular_damping=0.0, enable_gyroscopic_forces=True),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=True,
                # P3: solver budget is a switch so the 32/8 vs 16/4 comparison can be run
                # without editing code (the audit asks for that A/B under load).
                solver_position_iteration_count=int(os.environ.get("RM_SOLVER_POS", "32")),
                solver_velocity_iteration_count=int(os.environ.get("RM_SOLVER_VEL", "8"))),
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            pos=(0.0, 0.0, CONTRACT["spawn_height_m"]),
            joint_pos={".*": 0.0}, joint_vel={".*": 0.0}),
        soft_joint_pos_limit_factor=1.0,
        actuators={
            "legs": Mod4DCMotorCfg(
                joint_names_expr=LEG_ORDER, effort_limit=LEG_EFFORT,
                velocity_limit=LEG_NO_LOAD, saturation_effort=LEG_STALL,
                stiffness=LEG_KP, damping=leg_damping, armature=leg_armature,
                friction=0.0),
            "wheels": Mod4DCMotorCfg(
                joint_names_expr=WHEEL_ORDER, effort_limit=WHEEL_EFFORT,
                velocity_limit=WHEEL_NO_LOAD, saturation_effort=WHEEL_STALL,
                stiffness=0.0, damping=wheel_damping, armature=wheel_armature,
                friction=0.0),
            "passive": ImplicitActuatorCfg(
                joint_names_expr=PASSIVE_JOINTS, effort_limit_sim=1.0e6,
                velocity_limit_sim=1000.0, stiffness=0.0,
                damping={n: damping[n] for n in PASSIVE_JOINTS},
                armature={n: armature[n] for n in PASSIVE_JOINTS}, friction=0.0),
            "gas_springs": ImplicitActuatorCfg(
                joint_names_expr=GAS_JOINTS, effort_limit_sim=2000.0,
                velocity_limit_sim=1000.0,
                stiffness={n: gas[n]["stiffness_n_m"] for n in GAS_JOINTS},
                damping={n: gas[n]["damping_n_s_m"] for n in GAS_JOINTS},
                armature=0.002, friction=0.0),
        },
    )


# --- observation terms (35-D policy contract) --------------------------------------
def height_cmd(env) -> torch.Tensor:
    """[B, 1] target chassis height, obs index 3 (term scale 5.0)."""
    buf = getattr(env, "_mod4_height_cmd", None)
    if buf is None:
        buf = torch.full((env.num_envs, 1), _f("RM_NOMINAL_HEIGHT", .25), device=env.device)
        env._mod4_height_cmd = buf
    return buf


def zero_slots(env, asset_cfg: SceneEntityCfg) -> torch.Tensor:
    """[B, 2] reserved wheel position slots, obs 14..15: the contract fixes them to 0."""
    return torch.zeros(env.num_envs, len(asset_cfg.joint_names), device=env.device)


# audit item 2 (2026-09-11): route KIND -> mode bit of the 7-slot observation block.  The
# adapter resolves it once per reset; everything downstream is pure tensor work.
ROUTE_KIND_BITS = {
    "run": 0, "step_up": 1, "step_down": 1, "ramp_up": 2, "ramp_down": 2,
    "rough_cross": 2, "slope_spin": 3, "fly_jump": 4, "jump_in_place": 4,
    "tunnel_cross": 5,
}


def mode_onehot(env) -> torch.Tensor:
    """[B, 7] obs 28..34 = [normal, stair, slope, recover, JUMP, height, state_time]."""
    v = torch.zeros(env.num_envs, 7, device=env.device)
    # audit item 2: the arena sets _mod4_route_ids, not _mod4_task_id -- check the routes
    # FIRST, otherwise every arena route was reported as 'normal'.
    # The bit itself is computed ONCE per reset by the adapter and simply scattered here: the
    # earlier list comprehension walked 1024 route ids per control step (a GPU->CPU sync plus
    # 1024 Python int() calls at 50 Hz) and the audit asked for a vectorised implementation.
    bit = getattr(env, "_mod4_mode_bit", None)
    if bit is not None and bit.numel() == env.num_envs:
        v.scatter_(1, bit.clamp(min=0).unsqueeze(1), (bit >= 0).float().unsqueeze(1))
        return v
    _kinds = getattr(env, "_mod4_route_kinds", None)
    _rids = getattr(env, "_mod4_route_ids", None)
    if _kinds is not None and _rids is not None:
        table = getattr(env, "_mod4_kind_bit_table", None)
        if table is None:
            table = torch.tensor([ROUTE_KIND_BITS.get(k, -1) for k in _kinds],
                                 device=env.device, dtype=torch.long)
            env._mod4_kind_bit_table = table
        bit = table[_rids.long()]
        v.scatter_(1, bit.clamp(min=0).unsqueeze(1), (bit >= 0).float().unsqueeze(1))
        return v
    task = getattr(env, "_mod4_task_id", None)
    if task is None:                       # before the first reset
        v[:, 0] = 1.0
        return v
    # 2026-09-11 audit P0-2: bits follow the env's STABLE task bucket (legacy field mode).
    v[:, 0] = (task == 0).float()          # normal
    v[:, 1] = ((task == 1) | (task == 6)).float()   # stair / island climb
    v[:, 2] = ((task == 2) | (task == 7)).float()   # slope / undulation
    v[:, 3] = 0.0                          # recover (unused)
    v[:, 4] = (task == 4).float()          # JUMP
    v[:, 5] = (task == 3).float()          # height target active (tunnel crouch)
    v[:, 6] = 0.0                          # state_time
    return v


class SensorDelay:
    """Per-environment correlated delay line (mjlab delay_min_lag..max_lag semantics).

    Each environment keeps a lag drawn from [min_lag, max_lag] control steps and holds it
    for `period` steps with probability `hold_prob`, so the actor sees a persistent bus
    latency instead of white noise.
    """

    def __init__(self, num_envs, width, device, min_lag=1, max_lag=2,
                 hold_prob=0.75, period=10):
        self.min_lag = int(min_lag)
        self.max_lag = max(int(max_lag), int(min_lag))
        self.hold_prob = float(hold_prob)
        self.period = max(1, int(period))
        self.buf = torch.zeros(self.max_lag + 1, num_envs, width, device=device)
        self.lag = torch.zeros(num_envs, dtype=torch.long, device=device)
        self.age = torch.zeros(num_envs, dtype=torch.long, device=device)
        self.resample(torch.arange(num_envs, device=device))

    def resample(self, env_ids) -> None:
        n = env_ids.numel()
        self.lag[env_ids] = torch.randint(self.min_lag, self.max_lag + 1, (n,),
                                         device=self.buf.device)
        self.age[env_ids] = 0

    def push(self, value: torch.Tensor) -> torch.Tensor:
        self.buf = torch.roll(self.buf, 1, dims=0)
        self.buf[0] = value
        self.age += 1
        due = self.age >= self.period
        if due.any():
            ids = due.nonzero(as_tuple=False).flatten()
            keep = torch.rand(ids.numel(), device=self.buf.device) < self.hold_prob
            change = ids[~keep]
            if change.numel():
                self.resample(change)
            self.age[ids] = 0
        idx = self.lag.clamp(max=self.buf.shape[0] - 1)
        return self.buf[idx, torch.arange(self.buf.shape[1], device=self.buf.device)]


def delayed(env, key: str, base: torch.Tensor) -> torch.Tensor:
    """Cache one delay line per observation term and return the delayed sample."""
    if OBS_DELAY_MAX <= 0:
        # audit item 8: RM_DR_OFF=1 pins the lag window to zero.  Bypass the queue entirely
        # instead of paying for a one-deep buffer that is an identity map.
        return base
    cache = getattr(env, "_mod4_sensor_delay", None)
    if cache is None:
        cache = {}
        env._mod4_sensor_delay = cache
    line = cache.get(key)
    if line is None:
        line = SensorDelay(env.num_envs, base.shape[1], env.device,
                           OBS_DELAY_MIN, OBS_DELAY_MAX, DELAY_HOLD_PROB, DELAY_PERIOD)
        cache[key] = line
    return line.push(base)


def base_ang_vel_delayed(env, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")):
    return delayed(env, "base_ang_vel", mdp_obs.base_ang_vel(env, asset_cfg=asset_cfg))


def projected_gravity_delayed(env, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")):
    return delayed(env, "projected_gravity",
                   mdp_obs.projected_gravity(env, asset_cfg=asset_cfg))


def joint_pos_delayed(env, asset_cfg: SceneEntityCfg, bias_key: str):
    """Biased encoder positions relative to the default pose, then delayed."""
    base = mdp_obs.joint_pos_rel(env, asset_cfg=asset_cfg)
    bias = getattr(env, bias_key, None)
    if bias is not None:
        base = base + bias
    return delayed(env, bias_key, base)


def joint_vel_delayed(env, asset_cfg: SceneEntityCfg, key: str):
    return delayed(env, key, mdp_obs.joint_vel_rel(env, asset_cfg=asset_cfg))


def height_track(env, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
                 sigma: float = 0.02) -> torch.Tensor:
    """Exponential height-tracking reward against the live height command.

    2026-09-28: aligned with SCUT (`exp(-err^2 / sigma)`, sigma 0.005/0.01/0.025) after
    measuring that our old `exp(-(err/0.06)^2)` was flat beyond ~6 cm -- the probe showed the
    policy wandering 6-12 cm off the command with almost no gradient to correct it.
    """
    robot = env.scene[asset_cfg.name]
    target = height_cmd(env)[:, 0]
    # audit item 6: height is measured from the LOCAL terrain, not from world z=0 -- on the
    # dog-hole floor (-0.156 m) or the central island an absolute height reward is meaningless.
    ground = getattr(env, "_mod4_ground_z", None)
    z = robot.data.root_pos_w[:, 2] if ground is None else robot.data.root_pos_w[:, 2] - ground
    value = torch.exp(-torch.square(z - target) / sigma)
    # audit item 7: hold the last grounded value while a jump route is in the air.  Without
    # this the term pays 0.000 for the whole flight (the command window is 0.18-0.34 m), which
    # is one of the three reasons standing still out-scored jumping.
    return skills.jump_freeze_height(env, value)


def flat_height_deficit(env) -> torch.Tensor:
    """Dense low-height cost on flat ground: clamp(command - root_height, 0, 0.25).

    Applied on every flat sample (standing and moving); returns zero on field/arena terrain
    where the height command is route-driven and the local ground height varies.
    """
    if TERRAIN != "flat":
        return torch.zeros(env.num_envs, device=env.device)
    deficit = (height_cmd(env)[:, 0] - root_height_above_ground(env)).clamp(0.0, 0.25)
    return deficit


def flat_height_error_l1(env) -> torch.Tensor:
    """Symmetric linear height error on flat ground: |command - root_height|, clamped 0.25 m.

    Unlike the Gaussian height reward this keeps a constant slope for large errors, and unlike
    the one-sided deficit it also charges the robot for standing too tall.
    """
    if TERRAIN != "flat":
        return torch.zeros(env.num_envs, device=env.device)
    return (height_cmd(env)[:, 0] - root_height_above_ground(env)).abs().clamp(0.0, 0.25)


def flat_height_error_l2(env) -> torch.Tensor:
    """Two-sided squared height error, normalised to 1.0 at +-HEIGHT_L2_CLAMP (SCUT parity).

    2026-09-28 probe on model_1750: with 0.6 / 1.0 m/s commands the chassis sat at 0.39 / 0.45 m
    against a 0.245 m command while pumping +-6.5 cm (height std) -- the one-sided deficit term
    cannot charge that at all, and the L1 term saturates at 0.25 m (worth only -0.25 with
    weight -1.0).  SCUT's `track_height_square` (-1.0) is the two-sided term that makes
    "pump the legs, fly the body" unprofitable; the clamp mirrors their height_err_constraint
    of 0.15 m so the penalty is bounded and does not swamp the reward near a fall.
    """
    if TERRAIN != "flat":
        return torch.zeros(env.num_envs, device=env.device)
    err = (height_cmd(env)[:, 0] - root_height_above_ground(env)).clamp(-HEIGHT_L2_CLAMP, HEIGHT_L2_CLAMP)
    return (err / HEIGHT_L2_CLAMP).square()


def vel_height_gate(env) -> torch.Tensor:
    """SCUT `vel_height_gate`: 1.0 while the commanded height is tracked, 0 when it is not.

    出处：华南虎官方仓库 `wheeled-legged_RL / wheelbipe25_v3/env.py`，源码注释
    "速度高度门控：高度没跟住时降低速度/角速度 tracking 奖励，避免 policy 为了追速度牺牲高度"。
    linear_band 模式与该仓库一致：|err| <= FULL 时为 1，线性衰减到 ZERO 处为 0；
    exp 模式为 exp(-err^2/sigma)。`RM_VEL_HEIGHT_GATE=off`（默认）时不改变任何行为。
    """
    mode = VEL_HEIGHT_GATE_MODE
    if mode in ("", "off", "0", "none"):
        return torch.ones(env.num_envs, device=env.device)
    err = (height_cmd(env)[:, 0] - root_height_above_ground(env)).abs()
    if mode == "exp":
        return torch.exp(-torch.square(err) / max(VEL_HEIGHT_GATE_SIGMA, 1.0e-6))
    band = VEL_HEIGHT_GATE_ZERO - VEL_HEIGHT_GATE_FULL
    if band <= 0.0:
        return (err <= VEL_HEIGHT_GATE_FULL).float()
    return ((VEL_HEIGHT_GATE_ZERO - err) / band).clamp(0.0, 1.0)


def track_lin_vel_gated(env, command_name: str = "twist",
                        std: float = 0.7071067811865476) -> torch.Tensor:
    return mdp_rewards.track_lin_vel_xy_exp(env, std=std, command_name=command_name) * vel_height_gate(env)


def track_ang_vel_gated(env, command_name: str = "twist",
                        std: float = 1.4142135623730951) -> torch.Tensor:
    return skills.track_ang_vel_route_scaled(env, command_name=command_name, std=std) * vel_height_gate(env)


def run_velocity_error_gated(env, command_name: str = "twist") -> torch.Tensor:
    return skills.run_velocity_error_l2(env, command_name=command_name) * vel_height_gate(env)


def height_track_both_wheels(env, sigma: float = HEIGHT_SIGMA,
                             sensor_cfg: SceneEntityCfg = SceneEntityCfg("wheel_contact"),
                             threshold: float = 1.0) -> torch.Tensor:
    """SCUT `track_height_exp_both_wheels_contact`: height credit only with both wheels loaded.

    出处：华南虎官方仓库 wheelbipe25_v3（`rew_track_height_exp_both_wheels_contact =
    rew_track_height_exp_soft * both_wheels_contact`，权重 0.3）。低空蹦跳时双轮同时接地比例
    很低（我们 model_1850 在 1.0 m/s 档只有 23%），这一项让"蹦"拿不到高度分。
    """
    value = height_track(env, sigma=sigma)
    # Frozen SCUT wheelbipe25_v3: max per-wheel force over 3 x 5 ms samples.
    # Keep the original instantaneous sensor unchanged for strict acceptance.
    capture = getattr(env, "_integrated_contact", None)
    f = capture.history if capture is not None else env.scene.sensors["wheel_contact_scut"].data.net_forces_w_history
    if hasattr(f, "torch"):
        f = f.torch
    both = (f.norm(dim=-1).amax(dim=1) > threshold).all(dim=1).float()
    return value * both


def _lin_vel_err_xy(env, command_name: str = "twist") -> torch.Tensor:
    cmd = env.command_manager.get_command(command_name)[:, :2]
    return cmd - env.scene["robot"].data.root_lin_vel_b[:, :2]


def track_lin_vel_huge_gap(env, command_name: str = "twist", gap: float = 0.5) -> torch.Tensor:
    """SCUT `track_lin_vel_xy_huge_gap`: err^2 超阈值就 0/1 硬罚（权重 -1.0），不打门控。"""
    return (_lin_vel_err_xy(env, command_name).square().sum(dim=1) > gap).float()


def track_lin_vel_square(env, command_name: str = "twist", sigma: float = 0.25) -> torch.Tensor:
    """SCUT `track_lin_vel_xy_square`: (sigma * err_x)^2，权重 -1.0。"""
    return (sigma * _lin_vel_err_xy(env, command_name)[:, 0]).square()


def track_ang_vel_square(env, command_name: str = "twist", sigma: float = 0.25) -> torch.Tensor:
    cmd = env.command_manager.get_command(command_name)
    err = cmd[:, 2] - env.scene["robot"].data.root_ang_vel_b[:, 2]
    return (sigma * err).square()


def track_lin_vel_square_gated(env, command_name: str = "twist", sigma: float = 0.25) -> torch.Tensor:
    return track_lin_vel_square(env, command_name=command_name, sigma=sigma) * vel_height_gate(env)


def track_ang_vel_square_gated(env, command_name: str = "twist", sigma: float = 0.25) -> torch.Tensor:
    return track_ang_vel_square(env, command_name=command_name, sigma=sigma) * vel_height_gate(env)


def height_square_scut(env, sigma: float = 5.0) -> torch.Tensor:
    """SCUT `track_height_square`: (sigma * Δh)^2（双向，未归一化），权重 -1.0。"""
    if TERRAIN != "flat":
        return torch.zeros(env.num_envs, device=env.device)
    err = height_cmd(env)[:, 0] - root_height_above_ground(env)
    return (sigma * err).square()


def randomize_leg_start(env, env_ids,
                        asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> None:
    """SCUT `use_leg_random_start`: 复位时把腿关节位姿随机化（防止锁死单一站姿）。"""
    if not RANDOM_START:
        return
    robot = env.scene[asset_cfg.name]
    ids, _ = robot.find_joints(LEG_ORDER, preserve_order=True)
    pos = robot.data.joint_pos[env_ids][:, ids].clone()
    pos = pos + torch.empty_like(pos).uniform_(-RANDOM_START_LEG, RANDOM_START_LEG)
    robot.write_joint_state_to_sim(pos, torch.zeros_like(pos), ids, env_ids)


def randomize_wheel_vel(env, env_ids,
                        asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> None:
    """SCUT `use_joint_vel_random_start` 的轮速部分：复位时给轮子一个随机初速度。"""
    if not RANDOM_START:
        return
    robot = env.scene[asset_cfg.name]
    ids, _ = robot.find_joints(WHEEL_ORDER, preserve_order=True)
    vel = torch.empty((len(env_ids), len(ids)), device=env.device).uniform_(
        -RANDOM_START_WHEEL_VEL, RANDOM_START_WHEEL_VEL)
    robot.write_joint_velocity_to_sim(vel, ids, env_ids)


# --- closed-chain runtime gate ------------------------------------------------------
def _closure_cache(env):
    cache = getattr(env, "_mod4_closures", None)
    if cache is None:
        robot = env.scene["robot"]
        names = list(robot.body_names)
        cache = []
        for name, spec in CONTRACT["closures"].items():
            cache.append((name, names.index(spec["body0"]), names.index(spec["body1"]),
                          torch.tensor(spec["anchor0_m"], device=env.device),
                          torch.tensor(spec["anchor1_m"], device=env.device)))
        env._mod4_closures = cache
    return cache


def closure_errors(env) -> dict:
    robot = env.scene["robot"]
    pos, quat = robot.data.body_pos_w, robot.data.body_quat_w
    out = {}
    for name, i, j, a0, a1 in _closure_cache(env):
        p0 = pos[:, i] + quat_apply(quat[:, i], a0.expand(env.num_envs, 3))
        p1 = pos[:, j] + quat_apply(quat[:, j], a1.expand(env.num_envs, 3))
        out[name] = (p0 - p1).norm(dim=-1)
    return out


def closure_broken(env, threshold: float = 0.002) -> torch.Tensor:
    """Terminate an environment whose loop-closure anchors separate beyond tolerance."""
    worst = torch.stack(list(closure_errors(env).values())).max(dim=0).values
    env._mod4_closure_now = worst          # read by log_plant_metrics (audit P0-5)
    env._mod4_max_closure = max(float(getattr(env, "_mod4_max_closure", 0.0)),
                                float(worst.max().item()))
    return (worst > threshold) & _past_spawn_grace(env)


def mimic_errors(env) -> dict:
    """Chain-parallelism check of the four sprocket drives (audit P0-5).

    NOT the contracted gearing relation.  ``gearing: -1`` is the PhysX joint-coordinate
    convention; using it as a reading relation flags a healthy robot with ~2|q| of error -- the
    exact false alarm two earlier reports chased.  What must hold is that each drive link stays
    parallel to the link it is chained to: the relative rotation between the two bodies has to
    equal the authored neutral relative rotation.  ``probe_mimic.py`` measures 1e-3 rad on the
    delivered USD (1e-7 once settled); this term watches it online.
    """
    robot = env.scene["robot"]
    cache = getattr(env, "_mod4_mimic_pairs", None)
    if cache is None:
        names = list(robot.body_names)
        bodies = CONTRACT["bodies"]
        pairs = (("left_drive_hip", "left_thigh"), ("left_drive_input", "left_input"),
                 ("right_drive_hip", "right_thigh"), ("right_drive_input", "right_input"))
        cache = []
        for a, b in pairs:
            if a not in names or b not in names:
                continue
            qa = torch.tensor(bodies[a]["neutral_quat_wxyz"], device=env.device)
            qb = torch.tensor(bodies[b]["neutral_quat_wxyz"], device=env.device)
            authored = 2.0 * torch.acos((qa * qb).sum().abs().clamp(max=1.0))
            cache.append((a, names.index(a), names.index(b), authored))
        env._mod4_mimic_pairs = cache
    q = robot.data.body_quat_w
    out = {}
    for a, i, j, authored in cache:
        dot = (q[:, i] * q[:, j]).sum(dim=-1).abs().clamp(max=1.0)
        out[a] = (2.0 * torch.acos(dot) - authored).abs()
    return out

def mimic_broken(env, threshold: float = 0.05) -> torch.Tensor:
    """Terminate + track a transmission mimic that drifts apart (audit P0-5)."""
    errs = torch.stack(list(mimic_errors(env).values()))     # [pairs, N]
    worst = errs.max(dim=0).values
    env._mod4_mimic_now = worst            # read by log_plant_metrics (audit P0-5)
    env._mod4_mimic_mean = errs.mean(dim=0)
    env._mod4_max_mimic = max(float(getattr(env, "_mod4_max_mimic", 0.0)),
                              float(worst.max().item()))
    return (worst > threshold) & _past_spawn_grace(env)


def _past_spawn_grace(env) -> torch.Tensor:
    """[N] False during the first RM_SPAWN_GRACE_STEPS control steps of an episode.

    A spawn impact is not a mechanism failure: the ramp_up spawns were putting the chassis into
    the ramp (2900-3400 N) and the 2 mm loop-closure guard then killed the episode within 1-2
    steps, which hid a training problem behind a physics artefact (measured 2026-09-11 21:55).
    """
    grace = int(os.environ.get("RM_SPAWN_GRACE_STEPS", "10"))
    if grace <= 0:
        return torch.ones(env.num_envs, dtype=torch.bool, device=env.device)
    # Isaac Lab keeps this per-env counter for us (manager_based_rl_env.py: +1 per step, 0 on
    # reset), so no extra bookkeeping event is needed.
    return env.episode_length_buf >= grace


def log_plant_metrics(env, env_ids) -> None:
    """EventTerm (mode='step'): publish the plant-health numbers to TensorBoard.

    audit P0-5 ("训练目前只监控闭链锚点，没有在线监控四个传动 mimic"): the two termination
    terms already compute the worst anchor separation and the worst mimic drift every control
    step, so this term only has to READ them -- no extra physics work.  Written every
    RM_METRIC_PERIOD steps to keep the GPU->CPU syncs negligible.
    """
    period = max(1, int(os.environ.get("RM_METRIC_PERIOD", "10")))
    n = int(getattr(env, "_mod4_metric_step", 0)) + 1
    env._mod4_metric_step = n
    if n % period:
        return
    log = env.extras.setdefault("log", {})
    clo = getattr(env, "_mod4_closure_now", None)
    mim = getattr(env, "_mod4_mimic_now", None)
    mim_mean = getattr(env, "_mod4_mimic_mean", None)
    if clo is not None:
        log["Metrics/plant/closure_err_max_m"] = float(clo.max().item())
    if mim is not None:
        log["Metrics/plant/mimic_err_max_rad"] = float(mim.max().item())
    if mim_mean is not None:
        log["Metrics/plant/mimic_err_mean_rad"] = float(mim_mean.mean().item())
    log["Metrics/plant/closure_err_session_max_m"] = float(getattr(env, "_mod4_max_closure", 0.0))
    log["Metrics/plant/mimic_err_session_max_rad"] = float(getattr(env, "_mod4_max_mimic", 0.0))
    # Goal §3: `Metrics/success_rate` is Isaac Lab's COMMAND-level metric (velocity error inside
    # a threshold), NOT a route completion.  Rename it so nobody reads it as the terrain score,
    # and publish the real per-route numbers next to it.
    if "Metrics/success_rate" in log:
        log["Metrics/velocity_tracking_success_rate"] = log.pop("Metrics/success_rate")
    rc = getattr(env, "_mod4_routes", None)
    if rc is not None:
        finished = rc.finished.float()
        log["Metrics/route_complete_rate"] = float(finished.mean().item())
        batch = getattr(env, "_mod4_route_progress", None) or {}
        succ = batch.get("success")
        if succ is not None:
            # running window: how often a route goal is reached per logging period
            prev = getattr(env, "_mod4_success_steps", 0.0)
            env._mod4_success_steps = prev + float(succ.float().sum().item())
            log["Metrics/route_success_steps"] = float(env._mod4_success_steps)
        log["Metrics/tunnel_underpass_rate"] = float(rc.underpass_visited.float().mean().item())
        spin_done = ((rc.spin_angle.abs() >= 2.0 * 3.141592653589793).float().mean().item())
        log["Metrics/spin_360_rate"] = float(spin_done)
        log["Metrics/route_air_launched_rate"] = float(rc.launched.float().mean().item())

# --- randomization events (SCUT list) ----------------------------------------------
def resample_height_command(env, env_ids, low: float = HEIGHT_RANGE[0],
                            high: float = HEIGHT_RANGE[1]) -> None:
    buf = height_cmd(env)
    buf[env_ids] = torch.empty(env_ids.numel(), 1, device=env.device).uniform_(low, high)


def sample_encoder_bias(env, env_ids, asset_cfg: SceneEntityCfg, key: str,
                        bias_range: float = ENCODER_BIAS) -> None:
    bias = getattr(env, key, None)
    if bias is None:
        bias = torch.zeros(env.num_envs, len(asset_cfg.joint_names), device=env.device)
        setattr(env, key, bias)
    bias[env_ids] = torch.empty(env_ids.numel(), bias.shape[1],
                                device=env.device).uniform_(-abs(bias_range), abs(bias_range))


def reset_delay_lines(env, env_ids) -> None:
    for line in getattr(env, "_mod4_sensor_delay", {}).values():
        line.resample(env_ids)
        # P0-3 (audit 2026-09-11): clearing the ring buffer stops the first steps of a new
        # episode from replaying the previous episode's frames ("ghost" sensor/action).
        line.buf[:, env_ids] = 0.0


def resample_effort_scale(env, env_ids, asset_cfg: SceneEntityCfg, group: str,
                          low: float, high: float) -> None:
    env.scene[asset_cfg.name].actuators[group].resample_episode_scale(env_ids, low, high)


def resample_effort_noise(env, env_ids, asset_cfg: SceneEntityCfg, group: str,
                          delta: float) -> None:
    env.scene[asset_cfg.name].actuators[group].resample_step_scale(
        env_ids, 1.0 - delta, 1.0 + delta)


# --- delayed action terms -----------------------------------------------------------
class _DelayMixin:
    """Per-environment 0..2 control-step action delay (mjlab action-delay DR)."""

    def _init_delay(self, min_lag: int, max_lag: int, hold_prob: float,
                    period: int) -> None:
        self._min_lag, self._max_lag = int(min_lag), max(int(max_lag), int(min_lag))
        self._hold_prob, self._period = float(hold_prob), max(1, int(period))
        self._lag = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
        self._age = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
        self._hist = torch.zeros(self._max_lag + 1, self.num_envs, self.action_dim,
                                 device=self.device)
        self._resample_lag(torch.arange(self.num_envs, device=self.device))

    def _resample_lag(self, env_ids) -> None:
        n = env_ids.numel()
        self._lag[env_ids] = torch.randint(self._min_lag, self._max_lag + 1, (n,),
                                           device=self.device)
        self._age[env_ids] = 0

    def reset(self, env_ids=None):
        super().reset(env_ids)
        if env_ids is None:
            env_ids = torch.arange(self.num_envs, device=self.device)
        self._resample_lag(env_ids)
        # P0-3 (audit 2026-09-11): drop the previous episode's actions from the delay
        # line, otherwise the first steps of a new episode replay them.
        self._hist[:, env_ids] = 0.0

    def process_actions(self, actions: torch.Tensor):
        if self._max_lag <= 0:
            # audit item 8: no action delay configured (RM_DR_OFF=1) -> bypass the queue.
            super().process_actions(actions)
            return
        self._hist = torch.roll(self._hist, 1, dims=0)
        self._hist[0] = actions
        self._age += 1
        due = self._age >= self._period
        if due.any():
            ids = due.nonzero(as_tuple=False).flatten()
            keep = torch.rand(ids.numel(), device=self.device) < self._hold_prob
            change = ids[~keep]
            if change.numel():
                self._resample_lag(change)
            self._age[ids] = 0
        idx = self._lag.clamp(max=self._hist.shape[0] - 1)
        delayed_actions = self._hist[idx, torch.arange(self.num_envs, device=self.device)]
        super().process_actions(delayed_actions)


class DelayedJointPositionAction(_DelayMixin, mdp_actions.JointPositionAction):
    """Leg joint-position targets with the CAD input-difference stop projected on.

    handoff §1.3: hip and crank are two independent motors, and the CAD stop constrains their
    DIFFERENCE (crank - hip >= -1.0843 rad in the training window, -1.0863 rad at the real
    block).  PhysX resolves the closed chain with COMPLIANT mimic constraints, so a target pair
    outside that window does not simply "press the stop" -- it yanks the linkage.  The fix
    package's TorqueInterface does this at torque level for the self-test; the training action
    path had no such guard at all (measured 2026-09-12).
    """

    def __init__(self, cfg, env):
        super().__init__(cfg, env)
        self._init_delay(ACTION_DELAY_MIN, ACTION_DELAY_MAX, DELAY_HOLD_PROB, DELAY_PERIOD)
        win = CONTRACT.get("training_window") or {}
        stop = CONTRACT.get("mechanical_stop") or {}
        default_min = float(stop.get("input_difference_rad", float("-inf")))
        self.diff_min = float(os.environ.get("RM_DIFF_MIN",
                                             win.get("input_difference_min_rad", default_min)))
        self.diff_max = float(os.environ.get("RM_DIFF_MAX", 0.85))

    def process_actions(self, actions):
        super().process_actions(actions)
        if self.diff_min > -1.0e8:
            # LEG_ORDER == ["left_crank", "left_hip", "right_crank", "right_hip"], i.e. the
            # CRANK comes first in the processed target vector (action slots 0 and 2 are cranks).
            pa = self.processed_actions
            torch.maximum(pa[:, 0], pa[:, 1] + self.diff_min, out=pa[:, 0])
            torch.maximum(pa[:, 2], pa[:, 3] + self.diff_min, out=pa[:, 2])
            torch.minimum(pa[:, 0], pa[:, 1] + self.diff_max, out=pa[:, 0])
            torch.minimum(pa[:, 2], pa[:, 3] + self.diff_max, out=pa[:, 2])


class DelayedJointVelocityAction(_DelayMixin, mdp_actions.JointVelocityAction):
    def __init__(self, cfg, env):
        super().__init__(cfg, env)
        self._init_delay(ACTION_DELAY_MIN, ACTION_DELAY_MAX, DELAY_HOLD_PROB, DELAY_PERIOD)


@configclass
class DelayedJointPositionActionCfg(mdp_actions.JointPositionActionCfg):
    class_type: type = DelayedJointPositionAction


@configclass
class DelayedJointVelocityActionCfg(mdp_actions.JointVelocityActionCfg):
    class_type: type = DelayedJointVelocityAction


# --- sustained push disturbance (SCUT: +-10 N / +-1 N*m for 0.1-0.3 s) --------------
def _push_state(env):
    state = getattr(env, "_mod4_push", None)
    if state is None:
        n = env.num_envs
        state = {
            "force": torch.zeros(n, 1, 3, device=env.device),
            "torque": torch.zeros(n, 1, 3, device=env.device),
            "timer": torch.zeros(n, device=env.device),
            "active": torch.zeros(n, dtype=torch.bool, device=env.device),
            "next": torch.zeros(n, device=env.device),
        }
        env._mod4_push = state
    return state


def reset_push_state(env, env_ids, cooldown_s=(5.0, 10.0)) -> None:
    state = _push_state(env)
    state["active"][env_ids] = False
    state["timer"][env_ids] = 0.0
    state["force"][env_ids] = 0.0
    state["torque"][env_ids] = 0.0
    state["next"][env_ids] = torch.empty(env_ids.numel(), device=env.device).uniform_(
        cooldown_s[0], cooldown_s[1])


def sustained_push(env, env_ids, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
                   force_range=(-10.0, 10.0), torque_range=(-1.0, 1.0),
                   duration_s=(0.10, 0.30), cooldown_s=(5.0, 10.0)) -> None:
    """Transient external wrench, then a self-clearing cooldown.

    mjlab implements the SCUT disturbance with `apply_body_impulse` (0.1-0.3 s of force,
    5-10 s of cooldown).  Isaac Lab only ships a constant `apply_external_force_torque`,
    so the timing lives here instead of being silently turned into a permanent push.
    """
    state = _push_state(env)
    dt = env.step_dt
    active = state["active"]
    state["timer"][active] -= dt
    stop = active & (state["timer"] <= 0.0)
    if stop.any():
        n = int(stop.sum())
        state["active"][stop] = False
        state["force"][stop] = 0.0
        state["torque"][stop] = 0.0
        state["next"][stop] = torch.empty(n, device=env.device).uniform_(
            cooldown_s[0], cooldown_s[1])
    idle = ~state["active"]
    state["next"][idle] -= dt
    start = idle & (state["next"] <= 0.0)
    if start.any():
        n = int(start.sum())
        state["active"][start] = True
        state["timer"][start] = torch.empty(n, device=env.device).uniform_(
            duration_s[0], duration_s[1])
        state["force"][start] = torch.empty(n, 1, 3, device=env.device).uniform_(
            force_range[0], force_range[1])
        state["torque"][start] = torch.empty(n, 1, 3, device=env.device).uniform_(
            torque_range[0], torque_range[1])
    robot = env.scene[asset_cfg.name]
    robot.set_external_force_and_torque(state["force"], state["torque"],
                                        body_ids=asset_cfg.body_ids)
    robot.write_data_to_sim()


# --- scene, MDP and environment configuration ---------------------------------------
# --- RMUC2026 full arena (delivered package, 2026-09-11) ------------------------------
# RM_MOD4_MAP=rmuc2026 swaps the 29-box procedural field for the delivered CAD arena
# (1024 copies on a 34x20 m grid, collision/visual split, 15 semantic routes).  The terrain has
# to be built AFTER num_envs is known, so the train entry point calls attach_rmuc2026_terrain().
RMUC2026_ISAAC = (ROOT / "incoming" / "rmuc2026_field_20260911" / "rmuc2026_training" / "isaac")
MAP_MODE = os.environ.get("RM_MOD4_MAP", "").strip().lower()
# P2 staging: RM_DR_OFF=1 strips the wide randomisation so a new map/skill can be
# confirmed learnable before robustness training (audit P2).
# DR_OFF itself is read up with the SCUT knobs (see the top of this file, audit item 8), so a
# single switch gates the constants AND the events.


def attach_rmuc2026_terrain(cfg) -> bool:
    """Swap cfg.scene.terrain for the delivered arena.  Returns True when it was applied."""
    if MAP_MODE != "rmuc2026":
        return False
    import sys as _sys
    if str(RMUC2026_ISAAC) not in _sys.path:
        _sys.path.insert(0, str(RMUC2026_ISAAC))
    from terrain_cfg import make_terrain_cfg           # provided by the package
    cfg.scene.terrain = make_terrain_cfg(cfg.scene.num_envs)
    cfg.scene.env_spacing = 34.0
    # audit item 3/4: the 4000 x 4000 m plate (top at z=0) filled the 0.156 m deep dog-hole
    # and the 29 legacy Field_* boxes sat on top of the CAD arena.  Park the plate far below
    # the arena; the package's out_of_arena() handles runaways.
    try:
        cfg.scene.ground.init_state.pos = (0.0, 0.0, -100.0)
    except AttributeError:
        pass                        # 34 x 20 m rectangular grid
    # The package's own acceptance (PASS_RUNTIME_MAP) needs PhysX scene queries; Isaac Lab 3.0
    # defaults this to False, which silently makes every omni.physx ray miss.
    cfg.sim.enable_scene_query_support = True
    return True


def rmuc2026_route_module():
    """Import the package's RouteCommands (15 semantic routes) with sys.path set up."""
    import sys as _sys
    if str(RMUC2026_ISAAC) not in _sys.path:
        _sys.path.insert(0, str(RMUC2026_ISAAC))
    from route_commands import RouteCommands
    return RouteCommands

@configclass
class Mod4SceneCfg(InteractiveSceneCfg):
    """Ground, light and (with RM_MOD4_TERRAIN=field) the full RMUC2026 feature set."""

    robot: ArticulationCfg = mod4_robot_cfg()
    # A locally generated collider instead of Isaac Lab terrain "plane" assets: those are
    # fetched from the Nucleus server (or the packaged grid USD) and block/hang offline.
    ground = AssetBaseCfg(
        prim_path="/World/ground",
        spawn=sim_utils.CuboidCfg(
            # One static collider for every environment.  With RM_MOD4_TERRAIN=field the
            # environments are 13 m apart, so a 4096-env run spans ~832 m per side; the old
            # 200 m plate would have dropped most robots into the void.  4 km covers up to
            # ~30k envs at that spacing and costs nothing (it is a single static box).
            size=(4000.0, 4000.0, 0.1),
            collision_props=sim_utils.CollisionPropertiesCfg(),
            physics_material=sim_utils.RigidBodyMaterialCfg(
                static_friction=0.9, dynamic_friction=0.9, restitution=0.0),
        ),
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0.0, 0.0, -0.05)))
    light = AssetBaseCfg(prim_path="/World/light",
                         spawn=sim_utils.DomeLightCfg(intensity=2000.0))
    chassis_contact = ContactSensorCfg(
        prim_path="{ENV_REGEX_NS}/Robot/links/chassis", update_period=0.0,
        history_length=3, track_air_time=False, debug_vis=False)
    # Goal §2: the eight guide rollers are individually named collision prims under the chassis
    # (`guide_wheel_00..07`), so their ground load can be measured separately instead of being
    # lumped into `chassis_contact`.  Belly force = chassis_contact - guide_contact.
    guide_contact = ContactSensorCfg(
        # The eight rollers were reparented into their own fixed body (`guide_rollers`) by
        # tools/add_guide_roller_body.py so a ContactSensor can report them (goal §2).
        prim_path="{ENV_REGEX_NS}/Robot/links/guide_roller_.*", update_period=0.0,
        history_length=3, track_air_time=False, debug_vis=False)
    # Wheel contact is what tells the flight-jump rewards apart from "standing still": both
    # wheels off the ground is the only definition of airborne we use.
    wheel_contact = ContactSensorCfg(
        prim_path="{ENV_REGEX_NS}/Robot/links/(left|right)_wheel", update_period=0.0,
        history_length=3, track_air_time=False, debug_vis=False)
    wheel_contact_scut = ContactSensorCfg(
        prim_path="{ENV_REGEX_NS}/Robot/links/(left|right)_wheel", update_period=0.005,
        history_length=3, track_air_time=False, debug_vis=False)


    if TERRAIN == "field" and MAP_MODE != "rmuc2026":
        # audit item 3: in arena mode the 29 procedural Field_* boxes must NOT be spawned on
        # top of the delivered CAD arena.
        # Per-environment copies of the measured features.  Each returned AssetBaseCfg is
        # parented to {ENV_REGEX_NS}, so every environment gets its own field at its own
        # origin.  Assigning into the class namespace is how @configclass picks up scene
        # entries (the same way `ground` and `light` above are declared).
        _field_cfgs, _field_info = _field.rmuc2026_field_per_env(
            cap_h=float(os.environ.get("RM_TERRAIN_CAP_H", "0.20")))
        for _name, (_prim_name, _cfg) in _field_cfgs.items():
            locals()[_name] = _cfg
        # Keep the layout metadata as a MODULE global, and delete the temporaries: any name
        # left in the class namespace is treated as a scene asset by InteractiveScene, which
        # is exactly how `_field_cfgs` first blew up with "Unknown asset config type".
        globals()["FIELD_INFO"] = _field_info
        del _field_cfgs, _field_info, _name, _prim_name, _cfg
    else:
        globals()["FIELD_INFO"] = {}


# The per-environment field metadata (tunnel entry/exit, launch take-off, gap banks, ...) for
# rewards, logs and the launch scripts.  Empty in flat mode.
FIELD_INFO = dict(globals().get("FIELD_INFO", {}) or {})


def _obs_noise(n_min: float, n_max: float):
    """Observation noise for one ObsTerm, or None when RM_DR_OFF=1 (audit item 8).

    The P2 nominal stage has to see CLEAN sensor data: gating only the events left the actor
    on noisy observations while the critic and every reward saw the clean state.
    """
    return None if DR_OFF else Unoise(n_min=n_min, n_max=n_max)


@configclass
class ObservationsCfg:
    """The 35-D deployment contract on the policy side, privileged state on the critic."""

    @configclass
    class PolicyCfg(ObsGroup):
        commands = ObsTerm(func=mdp_obs.generated_commands,
                           params={"command_name": "twist"})
        height_command = ObsTerm(func=height_cmd, scale=5.0)
        base_ang_vel = ObsTerm(func=base_ang_vel_delayed, scale=0.5,
                               noise=_obs_noise(-0.25, 0.25))
        projected_gravity = ObsTerm(func=projected_gravity_delayed,
                                    noise=_obs_noise(-0.05, 0.05))
        leg_pos = ObsTerm(
            func=joint_pos_delayed,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=LEG_ORDER,
                                                preserve_order=True),
                    "bias_key": "_mod4_leg_bias"},
            noise=_obs_noise(-0.01, 0.01))
        wheel_pos_slots = ObsTerm(
            func=zero_slots,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=WHEEL_ORDER,
                                                preserve_order=True)})
        leg_vel = ObsTerm(
            func=joint_vel_delayed,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=LEG_ORDER,
                                                preserve_order=True),
                    "key": "leg_vel"},
            scale=0.1, noise=_obs_noise(-0.5, 0.5))
        wheel_vel = ObsTerm(
            func=joint_vel_delayed,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=WHEEL_ORDER,
                                                preserve_order=True),
                    "key": "wheel_vel"},
            scale=0.1, noise=_obs_noise(-1.0, 1.0))
        last_action = ObsTerm(func=mdp_obs.last_action)
        mode_onehot = ObsTerm(func=mode_onehot)

        def __post_init__(self):
            self.enable_corruption = True
            self.concatenate_terms = True

    @configclass
    class CriticCfg(ObsGroup):
        commands = ObsTerm(func=mdp_obs.generated_commands,
                           params={"command_name": "twist"})
        height_command = ObsTerm(func=height_cmd, scale=5.0)
        base_ang_vel = ObsTerm(func=mdp_obs.base_ang_vel, scale=0.5)
        base_lin_vel = ObsTerm(func=mdp_obs.base_lin_vel, scale=0.5)
        projected_gravity = ObsTerm(func=mdp_obs.projected_gravity)
        leg_pos = ObsTerm(
            func=mdp_obs.joint_pos_rel,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=LEG_ORDER,
                                                preserve_order=True)})
        wheel_pos_slots = ObsTerm(
            func=zero_slots,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=WHEEL_ORDER,
                                                preserve_order=True)})
        leg_vel = ObsTerm(
            func=mdp_obs.joint_vel_rel,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=LEG_ORDER,
                                                preserve_order=True)},
            scale=0.1)
        wheel_vel = ObsTerm(
            func=mdp_obs.joint_vel_rel,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=WHEEL_ORDER,
                                                preserve_order=True)},
            scale=0.1)
        last_action = ObsTerm(func=mdp_obs.last_action)
        mode_onehot = ObsTerm(func=mode_onehot)

        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = True

    policy: PolicyCfg = PolicyCfg()
    critic: CriticCfg = CriticCfg()


@configclass
class ActionsCfg:
    """6-D policy action: four leg position targets, then two wheel velocity targets."""

    legs = DelayedJointPositionActionCfg(
        asset_name="robot", joint_names=LEG_ORDER, scale=LEG_ACTION_SCALE,
        use_default_offset=True, preserve_order=True)
    wheels = DelayedJointVelocityActionCfg(
        asset_name="robot", joint_names=WHEEL_ORDER, scale=WHEEL_ACTION_SCALE,
        use_default_offset=False, offset=0.0, preserve_order=True)


@configclass
class CommandsCfg:
    """速度指令：对齐华南虎平地任务（航向指令 50%、重采样 1–8 s、10% 站立环境）。"""

    twist = mdp_commands.UniformVelocityCommandCfg(
        asset_name="robot",
        resampling_time_range=(1.0, 8.0),
        heading_command=bool(int(os.environ.get("RM_HEADING_CMD", "1"))),
        heading_control_stiffness=float(os.environ.get("RM_HEADING_STIFFNESS", "1.0")),
        rel_standing_envs=float(os.environ.get("RM_REL_STANDING", "0.1")),
        rel_heading_envs=float(os.environ.get("RM_REL_HEADING", "0.5")),
        debug_vis=False,
        ranges=mdp_commands.UniformVelocityCommandCfg.Ranges(
            lin_vel_x=(_f("RM_CMD_VX_MIN", -1.2), _f("RM_CMD_VX_MAX", 1.2)),
            lin_vel_y=(0.0, 0.0),
            ang_vel_z=(0.0, 0.0),
            heading=(0.0, 0.0),
        ),
    )


def set_arena_friction(env, env_ids=None, static: float = 0.9, dynamic: float = 0.9,
                       prim_root: str = "/World/RMUC2026") -> None:
    """EventTerm (mode='startup'): give the delivered arena the same tyre friction as the field.

    2026-09-11 traction probe on the arena: wheels commanded to 16 rad/s spun at 16-17 rad/s while
    the chassis advanced 0.02 m/s -- the delivered collision material is far slipperier than the
    0.9/0.9 the robot was trained on, so it could neither drive nor balance (1-9 step episodes).
    """
    try:
        from pxr import UsdPhysics
    except Exception:
        return
    stage = env.sim.stage
    n = 0
    # 2026-09-11 material probe: the arena ships NO material prims at all, so every floor
    # collider falls back to /physicsScene/defaultMaterial (PhysX friction 0.5) while the
    # wheels carry 0.9 -- the contact therefore averages to ~0.7 and the robot is slipperier
    # than the field it was trained on (which used a 0.9 ground material).  Raise the scene
    # default instead of guessing at per-prim bindings that do not exist.
    for mat_path in ("/physicsScene/defaultMaterial",):
        prim = stage.GetPrimAtPath(mat_path)
        if prim and prim.IsValid() and prim.HasAPI(UsdPhysics.MaterialAPI):
            api = UsdPhysics.MaterialAPI(prim)
            api.GetStaticFrictionAttr().Set(float(static))
            api.GetDynamicFrictionAttr().Set(float(dynamic))
            n += 1
            print("[arena] %s friction -> %.2f/%.2f" % (mat_path, static, dynamic), flush=True)
    for prim in stage.Traverse():
        path = prim.GetPath().pathString
        if not path.startswith(prim_root):
            continue
        if not prim.HasAPI(UsdPhysics.MaterialAPI):
            continue
        api = UsdPhysics.MaterialAPI(prim)
        api.GetStaticFrictionAttr().Set(float(static))
        api.GetDynamicFrictionAttr().Set(float(dynamic))
        n += 1
    env._mod4_arena_materials = n
    print("[arena] friction set on %d material prims (%.2f/%.2f)" % (n, static, dynamic), flush=True)


def ground_height(env) -> torch.Tensor:
    """[N] height of the terrain directly under each robot (audit item 6).

    The delivered arena is NOT flat: the dog-hole floor sits 0.156 m *below* z=0 and the central
    island is above it, so every absolute-height check (height reward, chassis-contact
    termination, low-base termination) silently changed meaning per route.  A downward ray per
    wheel against the package's shared collision mesh gives the local floor.

    audit 2026-09-11 20:10 (dog-hole defect): the ray used to start 1.0 m ABOVE the root.  The
    delivered dog hole is only ~0.25 m tall, so as soon as the robot drove in, the ray hit the
    ROOF first and reported the roof as the floor -- the robot's height above "ground" went
    negative, and the height reward, `low_base` and `base_contact` all fired on garbage.  From
    just above the wheel contact patches the ray is always below any roof the robot fits under.
    """
    # Flat collider top is world z=0. Never query the unspawned RMUC CAD mesh.
    if TERRAIN == "flat":
        env._mod4_ground_z = torch.zeros(env.num_envs, device=env.device)
        return env._mod4_ground_z
    q = getattr(env, "_mod4_ground_raycast", None)
    if q is None:
        q = ground_raycast(env)
    robot = env.scene["robot"]
    # Start AT the root, not 1 m above it and not at the wheel frames:
    #   * 1 m above -> inside the dog hole the first hit is the ROOF (measured 2026-09-11
    #     20:10: the retired ray reported +0.2651 m for a floor at -0.1558 m, so the robot's
    #     height above "ground" went negative);
    #   * at the wheel frames -> those link origins sit ~0.33 m BELOW the root (measured:
    #     root 0.036 m, wheels -0.288/-0.299 m), i.e. under the floor, and the ray hit the
    #     slab's underside at -0.300 m instead of its top.
    # The root itself is always above the floor it stands on and below any roof it can drive
    # under (the 247 mm dog hole leaves the crouched root ~0.19-0.23 m above its floor), so a
    # single downward ray from the root sees the right surface in both places.
    pos = robot.data.root_pos_w
    starts = pos.unsqueeze(1).contiguous()
    dirs = torch.zeros_like(starts)
    dirs[:, :, 2] = -1.0
    out = q.cast(starts, dirs, max_distance=3.0)
    hit = out["hit"].squeeze(1)
    z = torch.where(hit, pos[:, 2] - out["distance"].squeeze(1), env._mod4_ground_z)
    env._mod4_ground_z = z
    return z


def ground_raycast(env):
    """Lazily build the package's SharedTerrainRaycast for this env (shared by all probes)."""
    q = getattr(env, "_mod4_ground_raycast", None)
    if q is None:
        import sys
        if str(RMUC2026_ISAAC) not in sys.path:
            sys.path.insert(0, str(RMUC2026_ISAAC))
        from shared_raycast import SharedTerrainRaycast
        q = SharedTerrainRaycast(env.scene.env_origins)
        env._mod4_ground_raycast = q
        if getattr(env, "_mod4_ground_z", None) is None:
            env._mod4_ground_z = torch.zeros(env.num_envs, device=env.device)
    return q


def spawn_footprint_floor(env, env_ids, starts_xy) -> torch.Tensor:
    """Highest surface under the robot's spawn footprint (audit 2026-09-11 22:05).

    The route table records ONE ground height per spawn point, sampled by a single ray at the
    root.  On the `trapezoid` ramp that ray reads -0.107 m while the chassis -- half a metre
    long -- overlaps the ramp above it: measured 145 746 N of chassis contact on the first step
    and 38% of the terrain episodes ending with `base_contact`.  Sampling the floor along the
    footprint (front/centre/rear) and taking the HIGHEST hit puts the robot on top of whatever
    it actually stands on.
    """
    q = ground_raycast(env)
    origins = env.scene.env_origins[env_ids]
    n = len(starts_xy)
    half = float(os.environ.get("RM_SPAWN_FOOTPRINT_M", "0.30"))
    offs = torch.tensor([-half, 0.0, half], device=env.device)
    yaw = torch.zeros(n, device=env.device)
    dirs = torch.stack([torch.cos(yaw), torch.sin(yaw), torch.zeros_like(yaw)], dim=-1)
    base = torch.cat([origins[:, :2] + starts_xy[:, :2], starts_xy[:, 2:3]], dim=-1)
    starts = base.unsqueeze(1) + dirs.unsqueeze(1) * offs.view(1, 3, 1)
    starts = starts.clone()
    starts[:, :, 2] = starts[:, :, 2] + 1.0          # cast from above; spawns are in open terrain
    down = torch.zeros_like(starts)
    down[:, :, 2] = -1.0
    # `env_ids` MUST be forwarded: the raycast object is built from ALL env origins, and without
    # the ids it validates len(starts) against the full batch and raises "Mismatch between
    # environment IDs and ray batches" -- which silently demoted every PARTIAL reset back to the
    # single-sample route table (measured 2026-09-11 22:40: the trapezoid route kept slamming).
    out = q.cast(starts, down, max_distance=4.0, env_ids=env_ids)
    z = starts[:, :, 2] - out["distance"]
    z = torch.where(out["hit"], z, base[:, 2].unsqueeze(1))
    return z.max(dim=1).values


def update_ground_height(env, env_ids=None) -> None:
    """EventTerm (mode='step'): refresh the per-env local ground height."""
    ground_height(env)


def root_height_above_ground(env) -> torch.Tensor:
    """[N] root height measured from the local terrain, not from world z=0."""
    robot = env.scene["robot"]
    return robot.data.root_pos_w[:, 2] - getattr(env, "_mod4_ground_z",
                                                 torch.zeros(env.num_envs, device=env.device))


def low_base_relative(env, minimum_height: float = 0.10) -> torch.Tensor:
    """DoneTerm: fallen through / collapsed *relative to the local floor* (audit item 5/6)."""
    return root_height_above_ground(env) < minimum_height


@configclass
class EventCfg:
    """SCUT randomization list, term for term (see the module docstring)."""

    reset_scene = EventTerm(func=mdp_events.reset_scene_to_default, mode="reset")
    # 2026-09-29 华南虎 `use_leg_random_start` / `use_joint_vel_random_start`：
    # 复位时随机腿姿与轮速，防止策略锁死在单一姿态（站着/趴着）。
    randomize_leg_start = None  # replaced by full constraint-consistent reset below
    randomize_wheel_vel = None  # basic locomotion stage: zero initial wheel velocity
    # audit item 8: the delay-line reset has to run in BOTH stages.  It used to sit inside the
    # `if not DR_OFF` block, so the nominal stage kept replaying the previous episode's samples
    # (a "ghost observation" on the first steps after every reset).
    reset_delay_lines = EventTerm(func=reset_delay_lines, mode="reset")
    # audit item 5 (mjlab) / item 7 (arena): the action second difference and the landing flags
    # are per-episode state too -- without this the first steps of a new episode are scored
    # against the previous episode's action and contact history.
    reset_history = EventTerm(func=skills.reset_history, mode="reset")
    # audit P0-5: the closure anchors and the four transmission mimics are checked by the
    # termination terms every step -- publish their magnitudes so a slow drift is visible
    # BEFORE it crosses the termination threshold.
    plant_metrics = EventTerm(func=log_plant_metrics, mode="step")
    if not DR_OFF:                      # P2: no height / delay / push randomisation
        reset_height_command = EventTerm(func=resample_height_command, mode="reset")
        reset_push_state = EventTerm(func=reset_push_state, mode="reset")
    reset_base = EventTerm(
        func=mdp_events.reset_root_state_uniform, mode="reset",
        params={"pose_range": {"x": (-0.1, 0.1), "y": (-0.1, 0.1),
                               "yaw": (-0.3, 0.3)},
                "velocity_range": {"x": (-0.2, 0.2), "y": (-0.2, 0.2),
                                   "z": (-0.1, 0.1), "roll": (-0.3, 0.3),
                                   "pitch": (-0.3, 0.3), "yaw": (-0.3, 0.3)},
                "asset_cfg": SceneEntityCfg("robot")})
    if not DR_OFF:                      # P2: no actuator / friction / mass / CoM / effort randomisation
        leg_encoder_bias = EventTerm(
            func=sample_encoder_bias, mode="reset",
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=LEG_ORDER,
                                                preserve_order=True),
                    "key": "_mod4_leg_bias"})
        wheel_encoder_bias = EventTerm(
            func=sample_encoder_bias, mode="reset",
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=WHEEL_ORDER,
                                                preserve_order=True),
                    "key": "_mod4_wheel_bias"})
        push_velocity = EventTerm(
            func=mdp_events.push_by_setting_velocity, mode="interval",
            interval_range_s=(6.0, 12.0),
            params={"velocity_range": {"x": (-0.4, 0.4), "y": (-0.3, 0.3),
                                       "pitch": (-0.4, 0.4)},
                    "asset_cfg": SceneEntityCfg("robot")})
        push_wrench = EventTerm(
            func=sustained_push, mode="step",
            params={"asset_cfg": SceneEntityCfg("robot", body_names=["chassis"]),
                    "force_range": (-10.0, 10.0), "torque_range": (-1.0, 1.0),
                    "duration_s": (0.10, 0.30), "cooldown_s": (5.0, 10.0)})
        actuator_gains = EventTerm(
            func=mdp_events.randomize_actuator_gains, mode="reset",
            params={"asset_cfg": SceneEntityCfg("robot",
                                                joint_names=LEG_ORDER + WHEEL_ORDER),
                    "stiffness_distribution_params": (0.9, 1.1),
                    "damping_distribution_params": (0.8, 1.2),
                    "operation": "scale", "distribution": "uniform"})
        leg_joint_params = EventTerm(
            func=mdp_events.randomize_joint_parameters, mode="reset",
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=LEG_ORDER),
                    "armature_distribution_params": ARMATURE_SCALE,
                    "operation": "scale", "distribution": "uniform"})
        wheel_joint_params = EventTerm(
            func=mdp_events.randomize_joint_parameters, mode="reset",
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=WHEEL_ORDER),
                    "armature_distribution_params": ARMATURE_SCALE,
                    "operation": "scale", "distribution": "uniform"})
        # The delivered MJCF ships frictionloss = 0 everywhere, so a "scale" operation would
        # keep multiplying zero and the gearbox/joint friction would never be modelled.  SCUT
        # adds an absolute amount per joint, which is the "abs" operation here.
        leg_frictionloss = EventTerm(
            func=mdp_events.randomize_joint_parameters, mode="reset",
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=LEG_ORDER),
                    "friction_distribution_params": (0.0, LEG_FRICTION_MAX),
                    "operation": "abs", "distribution": "uniform"})
        wheel_frictionloss = EventTerm(
            func=mdp_events.randomize_joint_parameters, mode="reset",
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=WHEEL_ORDER),
                    "friction_distribution_params": (0.0, WHEEL_FRICTION_MAX),
                    "operation": "abs", "distribution": "uniform"})
        # Gas spring stiffness/damping live on the actuator, so they use the actuator-gain
        # event (joint-parameter events only cover limits, armature and friction).
        gas_spring_params = EventTerm(
            func=mdp_events.randomize_actuator_gains, mode="reset",
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=GAS_JOINTS),
                    "stiffness_distribution_params": (0.8, 1.2),
                    "damping_distribution_params": (0.7, 1.3),
                    "operation": "scale", "distribution": "uniform"})
        # P0-4 (audit 2026-09-11): the chassis mass used to be randomized TWICE -- once by this
        # event and again inside randomize_mass_inertia, which also re-captured the already-perturbed
        # mass as its "default".  The comprehensive event below is the single entry point now.
        # One event replaces Isaac Lab's six mass/inertia events: chassis mass -1..+2 kg with
        # inertia x0.8..1.2, limbs mass x0.9..1.1 with inertia x0.7..1.3, wheels mass x0.9..1.1
        # with inertia x0.8..1.2 (SCUT's envelope).  All factors are strictly positive, so no
        # PhysX setter ever sees a non-positive tensor.
        mass_inertia = EventTerm(func=randomize_mass_inertia, mode="reset")
        # Centre-of-mass offset.  This is the ONLY knob that moves the CoM: the mass and inertia
        # randomizations above scale symmetrically about the existing centre, so an off-centre
        # battery, gimbal or ammo load is invisible to them.  SCUT's envelope (their agent.yaml
        # com_range) is x +-0.04 m, y +-0.02 m, z +-0.02 m; on this 14.2 kg chassis a 3 cm
        # offset needs ~0.98 m/s^2 of sustained acceleration (~8% of the wheel authority) to
        # hold station, which is exactly the margin we do not want to lose on a slope.
        base_com = EventTerm(
            func=mdp_events.randomize_rigid_body_com, mode="reset",
            params={"asset_cfg": SceneEntityCfg("robot", body_names=["chassis"]),
                    "com_range": {"x": (-0.04, 0.04), "y": (-0.02, 0.02),
                                  "z": (-0.02, 0.02)}})
        wheel_friction = EventTerm(
            func=mdp_events.randomize_rigid_body_material, mode="reset",
            params={"asset_cfg": SceneEntityCfg("robot", body_names=WHEEL_BODIES),
                    "static_friction_range": (0.7, 1.3),
                    "dynamic_friction_range": (0.7, 1.3),
                    "restitution_range": (0.0, 0.0), "num_buckets": 64,
                    "make_consistent": True})
        leg_effort_scale = EventTerm(
            func=resample_effort_scale, mode="reset",
            params={"asset_cfg": SceneEntityCfg("robot"), "group": "legs",
                    "low": EFFORT_LEG[0], "high": EFFORT_LEG[1]})
        wheel_effort_scale = EventTerm(
            func=resample_effort_scale, mode="reset",
            params={"asset_cfg": SceneEntityCfg("robot"), "group": "wheels",
                    "low": EFFORT_WHEEL[0], "high": EFFORT_WHEEL[1]})
        leg_effort_noise = EventTerm(
            func=resample_effort_noise, mode="step",
            params={"asset_cfg": SceneEntityCfg("robot"), "group": "legs",
                    "delta": EFFORT_NOISE})
        wheel_effort_noise = EventTerm(
            func=resample_effort_noise, mode="step",
            params={"asset_cfg": SceneEntityCfg("robot"), "group": "wheels",
                    "delta": EFFORT_NOISE_WHEEL})
        # Airborne bookkeeping for the flight/landing rewards (step mode: every control step).
    # P0-2: per-task command + mode bits every control step (audit 2026-09-11).
    ground_track = EventTerm(func=update_ground_height, mode="step")
    skill_cmds = EventTerm(func=skills.skill_commands, mode="step")
    if MAP_MODE == "rmuc2026":
        # Route-driven arena: spawn on the semantic route and let the package write the
        # velocity command (replaces the lane-offset spawn and the per-task commands).
        from route_isaac import route_commands as _rc, route_spawn as _rs  # noqa: E402
        route_spawn_term = EventTerm(func=_rs, mode="reset")
        route_cmd_term = EventTerm(func=_rc, mode="step")
        # audit item 7: the jump phase machine has to run BEFORE the reward manager, which is
        # exactly what a mode='step' event gives us.
        jump_state = EventTerm(func=skills.update_jump_state, mode="step",
                               params={"sensor_cfg": SceneEntityCfg("wheel_contact")})
        # audit item 8 (SCUT parity, last piece): after touchdown the height command drops to a
        # short absorb pose -- the fly stage reaches the ground with the legs extended and was
        # ending episodes in base_contact (measured 2026-09-12: launched 32/32,
        # air_after_launch 32/32, complete_rate 0.0, fail/base_contact 21).
        landing_state = EventTerm(func=skills.update_landing_state, mode="step")
        # audit item 8 (SCUT parity): terrain-position-driven height command for the tunnel --
        # approach -> pre-crouch -> the measured drivable crouch -> recover.  A single constant
        # cannot describe a hole whose whole fitting window is 2 mm tall.
        tunnel_state = EventTerm(func=skills.update_tunnel_state, mode="step")
        del _rc, _rs          # keep the helper names out of the configclass namespace
    air_state = EventTerm(func=skills.update_air_state, mode="step",
                          params={"sensor_cfg": SceneEntityCfg("wheel_contact")})
    # The delivered MJCF gas springs are PRELOADED (springref / target_position_m = 0.2206 m).
    # Isaac's implicit drive targets the joint default (0), so without this the legs carry no
    # preload: root sags 0.34 -> 0.20 m in half a second and the "crouch under the beam"
    # reward stops discriminating (see probe_gas_preload.py A/B and docs/...REACHABILITY...).
    gas_spring_preload = EventTerm(
        func=skills.gas_spring_preload, mode="step",
        params={"joint_names": GAS_JOINTS,
                "targets": [float(CONTRACT["gas_springs"][n]["target_position_m"])
                            for n in GAS_JOINTS]})
    if TERRAIN == "field" and FIELD_INFO and MAP_MODE != "rmuc2026":
        # Put every third environment on the tunnel lane and every third on the launch lane;
        # the rest keep the default centre spawn.  Runs after the stock resets.
        skill_lanes = EventTerm(
            func=skills.reset_skill_lanes, mode="reset",
            params={"tunnel_spawn": FIELD_INFO["tunnel_spawn"],
                    "launch_spawn": FIELD_INFO["launch_spawn"],
                    "tunnel_entry": FIELD_INFO["tunnel_entry"],
                    "island_entry": FIELD_INFO.get("island_entry"),
                    "undulation_entry": FIELD_INFO.get("undulation_entry")})


    consistent_start = EventTerm(func=scut_rescue.consistent_reset, mode="reset")


@configclass
class RewardsCfg:
    # ================= 2026-09-29 华南虎平地配方（逐条对齐，出处见模块常量注释） =========
    # 速度跟踪：exp(σ0.25) + tight(σ0.01) + huge_gap 硬罚 + square 罚；exp/soft/square 走门控
    track_lin_vel = RewTerm(func=scut_rescue.linear_exp, weight=SCUT_LIN_W,
                            params={"command_name": "twist", "std": SCUT_LIN_SIGMA})
    track_lin_vel_tight = RewTerm(func=scut_rescue.linear_exp, weight=SCUT_LIN_TIGHT_W,
                                  params={"command_name": "twist", "std": SCUT_LIN_TIGHT_SIGMA})
    track_lin_vel_huge_gap = RewTerm(func=scut_rescue.linear_gap, weight=SCUT_LIN_GAP_W,
                                     params={"command_name": "twist", "gap": SCUT_LIN_GAP})
    track_lin_vel_square = RewTerm(func=scut_rescue.linear_square, weight=SCUT_LIN_SQ_W,
                                   params={"command_name": "twist", "sigma": SCUT_LIN_SQ_SIGMA})
    run_velocity_error = RewTerm(func=run_velocity_error_gated, weight=W_RUN_VEL_ERROR)
    # 角速度跟踪：exp(σ0.25, w0.5) + square 罚（航向指令由 command 项生成）
    track_ang_vel = RewTerm(func=scut_rescue.yaw_exp, weight=SCUT_ANG_W,
                            params={"command_name": "twist", "std": SCUT_ANG_SIGMA})
    track_ang_vel_square = RewTerm(func=track_ang_vel_square_gated, weight=SCUT_ANG_SQ_W,
                                   params={"command_name": "twist", "sigma": SCUT_ANG_SQ_SIGMA})
    # 高度：exp(σ0.01,w0.7) + tight(σ0.001,w0.3) + both_wheels(σ0.1,w0.3) + square((5Δh)²,w−1)
    height = RewTerm(func=height_track, weight=SCUT_H_W, params={"sigma": SCUT_H_SIGMA})
    height_tight = RewTerm(func=height_track, weight=SCUT_H_TIGHT_W,
                           params={"sigma": SCUT_H_TIGHT_SIGMA})
    height_both_wheels = RewTerm(func=height_track_both_wheels, weight=W_HEIGHT_BOTH_WHEELS,
                                 params={"sigma": SCUT_H_SOFT_SIGMA})
    height_square = RewTerm(func=height_square_scut, weight=SCUT_H_SQ_W,
                            params={"sigma": SCUT_H_SQ_SIGMA})
    # 平滑/约束（取华南虎平地表的数值）
    lin_vel_z = RewTerm(func=skills.lin_vel_z_l2_jump_exempt, weight=SCUT_LINVELZ_W)
    ang_vel_xy = RewTerm(func=skills.ang_vel_xy_jump_exempt, weight=-0.05)
    flat_orientation = None
    flat_orientation_y = RewTerm(func=scut_rescue.orientation, weight=-1., params={"mode":"pitch"})
    flat_orientation_y_v = RewTerm(func=scut_rescue.orientation, weight=-1., params={"mode":"pitch_velocity"})
    flat_orientation_x_v = RewTerm(func=scut_rescue.orientation, weight=-1., params={"mode":"roll_velocity"})
    no_fork = RewTerm(func=scut_rescue.no_fork, weight=-1., params={"axis":0})
    no_fork_z = RewTerm(func=scut_rescue.no_fork, weight=-2., params={"axis":2})
    wheel_motor_z_axis_align_exp = RewTerm(func=scut_rescue.leg_gravity_alignment, weight=.1, params={"sigma":.01})
    wheel_motor_z_axis_align_exp_tight = RewTerm(func=scut_rescue.leg_gravity_alignment, weight=.1, params={"sigma":.001})
    action_rate = RewTerm(func=skills.action_rate_jump_exempt, weight=SCUT_ACTION_RATE_W)
    action_acc = RewTerm(func=skills.action_acc_l2, weight=SCUT_ACTION_ACC_W)
    torques = RewTerm(func=skills.joint_torques_l2_motors, weight=SCUT_TORQUE_W,
                      params={"joint_names": LEG_ORDER + WHEEL_ORDER})
    joint_power = RewTerm(func=scut_rescue.wheel_power, weight=SCUT_POWER_W)
    dof_pos_limits = RewTerm(func=mdp_rewards.joint_pos_limits, weight=0.0)
    # 我们没有华南虎的 no_fork 几何，用既有的腿对称项顶上（同为 −0.2 量级）
    leg_symmetry = RewTerm(func=skills.leg_symmetry, weight=0.0,
                           params={"leg_joint_names": LEG_ORDER})
    # 华南虎平地：无 alive、无 termination 罚、无 wheel_contact；贴地算 undesired_contact(−2)
    alive = RewTerm(func=mdp_rewards.is_alive, weight=SCUT_ALIVE_W)
    termination = RewTerm(func=skills.is_terminated, weight=SCUT_TERM_W)
    wheel_contact = RewTerm(func=skills.wheel_contact_fraction_jump_exempt, weight=SCUT_WHEEL_CONTACT_W,
                            params={"sensor_cfg": SceneEntityCfg("wheel_contact")})
    base_contact = RewTerm(func=skills.chassis_ground_penalty, weight=SCUT_BASE_CONTACT_W,
                           params={"sensor_cfg": SceneEntityCfg("chassis_contact"), "threshold": 50.0})
    # 旧的"防下沉"三件套对齐后关闭（华南虎改用 height_square 双向罚）
    height_deficit = RewTerm(func=flat_height_deficit, weight=W_HEIGHT_DEFICIT)
    height_error_l1 = RewTerm(func=flat_height_error_l1, weight=W_HEIGHT_LINEAR)

    # --- skills: 小陀螺 / 过洞 / 飞坡 --------------------------------------------------
    # Ported from train/rmvehicle/src/rmvehicle/mdp/skills.py; see skills_isaac.py.  Only
    # registered in field mode, because the tunnel and the launch ramp have to exist first.
    if MAP_MODE == "rmuc2026":
        # Route rewards come straight from the delivered package: dense progress toward the
        # route goal plus a one-shot success bonus (route-specific gate: spin angle, jump
        # height + air time, underpass visit, ...).
        route_progress = RewTerm(func=skills.route_progress, weight=2.0)
        route_success = RewTerm(func=skills.route_success, weight=20.0)
        # Sim2real-safe crouch (2026-09-12): PhysX resolves the 232 mm collision hull, the CAD
        # skin is 245 mm -- score the CAD envelope against the DELIVERED ceiling so the policy
        # cannot learn a crossing that only works because the simulator's collider is shorter.
        tunnel_clearance = RewTerm(func=skills.tunnel_clearance_cad, weight=1.5)
        # ... and a tight (2 cm) height-tracking term inside/approaching the hole: the global
        # term's 6 cm kernel let the first fixed-plant run enter 66 mm too tall and jam at the
        # mouth (probe_tunnel_traj.py).
        tunnel_height = RewTerm(func=skills.tunnel_height_track, weight=1.5)
        # ... and a small penalty for standing still inside the crouch zones, so "hold the
        # crouch and time out" stops being an optimum (measured 2026-09-12).
        tunnel_stall = RewTerm(func=skills.tunnel_stall, weight=1.0)
        # --- audit item 7: dense jump shaping (jump_in_place routes only) ------------------
        # crouch -> extension -> height actually gained -> flight -> clean landing.  The
        # package forces progress to zero on jump routes, so without these terms the only
        # signal was the one-shot success bonus, which no random policy ever reaches.
        # 21:07 measurement: with (0.5, 1.5, 3.0, 0.9, 2.0) a discovered hop was worth ~+1.8
        # in the logged units against a standing total of ~2.2 -- too small to beat the return
        # noise, and the policy stayed in the crouch-hold optimum.  The whole jump stack is now
        # ~2.5x, so ONE clean hop is worth about as much as a whole episode of standing.
        jump_crouch = RewTerm(func=skills.jump_crouch, weight=0.8)
        jump_push = RewTerm(func=skills.jump_push, weight=10.0)
        jump_climb = RewTerm(func=skills.jump_climb, weight=8.0)
        jump_air = RewTerm(func=skills.jump_air, weight=1.5)
        jump_land = RewTerm(func=skills.jump_land, weight=3.0)
        jump_hard_land = RewTerm(func=skills.jump_hard_land, weight=-3.0)
    if TERRAIN == "field" and FIELD_INFO and MAP_MODE != "rmuc2026":
        gyro_track_wide = RewTerm(
            func=skills.gyro_track_wide, weight=3.0,
            params={"command_name": "twist", "band": 2.0, "max_tilt_deg": 30.0})
        tunnel_crouch = RewTerm(
            func=skills.tunnel_crouch, weight=0.5,
            params={"entry": FIELD_INFO["tunnel_entry"],
                    "lane_y": FIELD_INFO["tunnel_spawn"][1]})
        tunnel_approach = RewTerm(
            func=skills.tunnel_approach, weight=1.5,
            params={"entry": FIELD_INFO["tunnel_entry"],
                    "lane_y": FIELD_INFO["tunnel_spawn"][1]})
        tunnel_traversal = RewTerm(
            func=skills.tunnel_traversal, weight=5.0,
            params={"entry": FIELD_INFO["tunnel_entry"], "exit": FIELD_INFO["tunnel_exit"],
                    "lane_y": FIELD_INFO["tunnel_spawn"][1],
                    "hole_h": FIELD_INFO["tunnel_hole_m"][0]})
        flight_progress = RewTerm(
            func=skills.flight_progress, weight=2.0,
            params={"sensor_cfg": SceneEntityCfg("wheel_contact"), "min_vx": 0.8})
        unwanted_airborne = RewTerm(
            func=skills.unwanted_airborne, weight=-0.3,
            params={"sensor_cfg": SceneEntityCfg("wheel_contact"), "min_vx": 0.8})
        landing_recovery = RewTerm(
            func=skills.landing_recovery, weight=1.5,
            params={"max_tilt_deg": 30.0})


@configclass
class TerminationsCfg:
    time_out = DoneTerm(func=mdp_term.time_out, time_out=True)
    bad_orientation = DoneTerm(func=mdp_term.bad_orientation,
                               params={"limit_angle": 0.75})
    base_contact = DoneTerm(func=skills.chassis_on_ground,
                            # 50 N against the FLOOR/FIELD only (see skills_isaac.
                            # chassis_on_ground): the stock term used the unfiltered net
                            # force, so legs brushing the chassis terminated 99% of
                            # episodes and no skill could ever be learned.
                            params={"threshold": 50.0,
                                    "sensor_cfg": SceneEntityCfg("chassis_contact")})
    closure = DoneTerm(func=closure_broken, params={"threshold": 0.002})
    # P0-5: the four transmission mimics were only checked offline; a drift here means the
    # simulator is solving a different mechanism than the one being deployed.
    mimic = DoneTerm(func=mimic_broken, params={"threshold": 0.05})
    # audit item 5/6: relative to the LOCAL floor -- the dog-hole floor is 0.156 m below the
    # highway, so an absolute 0.10 m gate terminated a robot standing correctly inside it.
    # 2026-09-28: low_base used to END the episode below 0.10 m.  Combined with the new dense
    # height-deficit penalty that made "sink until the episode ends" the cheapest way to stop
    # paying it (measured: low_base 56% -> 78%, episodes 1400 -> 650).  The penalty must be
    # inescapable, so the term is disabled here (threshold unreachable) and the robot keeps
    # paying the deficit until it stands back up or the episode times out.
    low_base = DoneTerm(func=low_base_relative, params={"minimum_height": -1.0})
    if MAP_MODE == "rmuc2026":
        # The delivered hole is 247.2 mm; if the CAD skin would be 2 mm inside the roof the
        # real robot has already crashed, so the episode ends (same geometry as the reward).
        tunnel_roof_hit = DoneTerm(func=skills.tunnel_roof_hit_cad,
                                   params={"penetration_m": 0.002})


@configclass
class CurriculumCfg:
    """Curricula for the MOD4 task.

    The yaw-command window is a curriculum in BOTH terrains.  mjlab's working flat run ramps
    it too (their RM_WZ_MAX is 14 rad/s but the window starts at the rate the previous policy
    demonstrably HELD, and their config warns the tracking reward is already flat above ~2 m/s
    of error).  Our flat task used to command +-13 rad/s from iteration 0, so
    ``track_ang_vel = exp(-(13/0.25)^2) = 0`` for every env that cannot spin at 13 rad/s --
    the only feedback left was the penalty sum, and "die fast" won (observed 2026-09-11:
    episode length 40 -> 18 while std crept 0.30 -> 0.34).
    """

    # 小陀螺: open the yaw command window by +0.5 rad/s every 40 ITERATIONS, from +/-2 rad/s
    # up to the +/-13 the contract allows (see skills_isaac.gyro_window_schedule).
    gyro_window = CurrTerm(func=skills.gyro_window_schedule,
                           params={})
    if MAP_MODE == "rmuc2026":
        # audit item 7: the jump-height window opens only while hops actually clear it, and it
        # starts at 0.04-0.09 m because the package's 0.08-0.35 m is above this plant's reach.
        jump_target = CurrTerm(func=skills.jump_target_schedule, params={})


@configclass
class Mod4EnvCfg(ManagerBasedRLEnvCfg):
    """100 Hz policy over 2 kHz physics, the same rates as the deployment contract."""

    # The field spans roughly x in [-1, 7] and y in [-4, +5] m per environment, so the grid
    # spacing has to grow with it or neighbouring fields would overlap.
    scene: Mod4SceneCfg = Mod4SceneCfg(
        num_envs=256, env_spacing=(13.0 if TERRAIN == "field" else 2.5))
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    commands: CommandsCfg = CommandsCfg()
    events: EventCfg = EventCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    curriculum: CurriculumCfg = CurriculumCfg()

    def __post_init__(self):
        # Explicit straight-speed phase: prevent reset curriculum overriding zero yaw.
        if os.environ.get("RM_GYRO_CURRICULUM", "1") == "0":
            self.curriculum.gyro_window = None
        self.decimation = DECIMATION
        # RM_EPISODE_S: the dog-hole route is short but the crouched robot is slow (~0.06 m/s
        # measured 2026-09-12), so a stage may need a longer budget than the 20 s default.
        self.episode_length_s = float(os.environ.get("RM_EPISODE_S", 20.0))
        self.sim.dt = PHYSICS_DT
        self.sim.render_interval = self.decimation
        # The SCUT push injects external wrenches; this applies them every solver
        # iteration, which is the setting PhysX asks for when that warning appears.
        self.sim.physics = PhysxCfg(solver_type=1,
                                    enable_external_forces_every_iteration=True)


def contract_report() -> dict:
    """Numbers the acceptance run prints so a drift is visible without reading code."""
    return {
        "asset": USD_PATH,
        "policy_action_order": ACTION_ORDER,
        "policy_hz": POLICY_HZ, "physics_dt": PHYSICS_DT, "decimation": DECIMATION,
        "leg_kp": LEG_KP, "leg_kd": LEG_KD, "wheel_kd": WHEEL_KD,
        "leg_action_scale": LEG_ACTION_SCALE, "wheel_action_scale": WHEEL_ACTION_SCALE,
        "leg_effort": LEG_EFFORT, "leg_stall": LEG_STALL, "leg_no_load": LEG_NO_LOAD,
        "wheel_effort": WHEEL_EFFORT, "wheel_stall": WHEEL_STALL,
        "wheel_no_load": WHEEL_NO_LOAD,
        "effort_scale": {"legs": EFFORT_LEG, "wheels": EFFORT_WHEEL,
                         "step_noise": (EFFORT_NOISE, EFFORT_NOISE_WHEEL)},
        "obs_delay_lag": (OBS_DELAY_MIN, OBS_DELAY_MAX),
        "action_delay_lag": (ACTION_DELAY_MIN, ACTION_DELAY_MAX),
        "height_range": HEIGHT_RANGE, "cmd_vx": CMD_VX, "cmd_wz": CMD_WZ,
        # audit items 7/8/9: the switches that change the TASK, not just the plant.
        "map": MAP_MODE or "legacy",
        "dr_off": DR_OFF,
        "route_kinds": os.environ.get("RM_ROUTE_KINDS", "").strip() or "all",
        "jump_window_m": [float(os.environ.get("RM_JUMP_LO", "0.04")),
                          float(os.environ.get("RM_JUMP_HI", "0.09"))],
    }
