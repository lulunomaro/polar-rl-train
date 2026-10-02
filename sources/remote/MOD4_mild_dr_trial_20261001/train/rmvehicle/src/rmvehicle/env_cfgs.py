"""Flat-ground velocity + height tracking task for the STEP-derived wheel-leg robot.

Works for both model variants (see names.py).  The observation vector reproduces the
wheelbipe_ros2_sim2sim policy contract exactly (obs float32[1,35] -> action float32[1,6])
so the exported ONNX drops into that framework unchanged.
"""
from __future__ import annotations

import math
import os

from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.envs import mdp as envs_mdp
from mjlab.envs.mdp import dr
from mjlab.envs.mdp.actions import JointPositionActionCfg, JointVelocityActionCfg
from mjlab.managers.action_manager import ActionTermCfg
from mjlab.managers.command_manager import CommandTermCfg
from mjlab.managers.event_manager import EventTermCfg
from mjlab.managers.observation_manager import ObservationGroupCfg, ObservationTermCfg
from mjlab.managers.reward_manager import RewardTermCfg
from mjlab.managers.scene_entity_config import SceneEntityCfg
from mjlab.managers.curriculum_manager import CurriculumTermCfg
from mjlab.managers.termination_manager import TerminationTermCfg
from mjlab.scene import SceneCfg
from mjlab.sensor import ContactMatch, ContactSensorCfg
from mjlab.sim import MujocoCfg, SimulationCfg
from mjlab.tasks.velocity import mdp as velocity_mdp
from mjlab.tasks.velocity.mdp import UniformVelocityCommandCfg
from mjlab.terrains import TerrainEntityCfg
from mjlab.utils.noise import UniformNoiseCfg as Unoise
from mjlab.viewer import ViewerConfig

from . import mdp
from .field_cfg import field_terrain_entity, load_dims
from .mdp import observations as ob
from .names import CC, OPEN, RM2025_LATER, ModelNames
from .robot_cfg import (
  LEG_ACTION_SCALE,
  WHEEL_ACTION_SCALE,
  make_robot_cfg,
  plant_options,
)


# SCUT trains 5..25 ms of motor/IMU feedback delay; at our 100 Hz policy 1..2 control
# steps = 10..20 ms.  A zero-delay actor was optimistically assuming a perfect bus.
_OBS_DELAY_MIN = int(os.environ.get("RM_OBS_DELAY_MIN_LAG", "1"))
_OBS_DELAY_MAX = int(os.environ.get("RM_OBS_DELAY_MAX_LAG", "2"))
_OBS_DELAY_HOLD = float(os.environ.get("RM_OBS_DELAY_HOLD_PROB", "0.75"))
_OBS_DELAY_PERIOD = int(os.environ.get("RM_OBS_DELAY_UPDATE_PERIOD", "10"))


def _actor_terms(names: ModelNames, deploy_robust: bool = True) -> dict:
  """35-D contract, term by term, in index order.

  ``preserve_order=True`` is REQUIRED, not cosmetic: mjlab's default resolves a pattern
  tuple into *model* order.  Our closed-chain MJCF declares rear1 before front1, so the
  default silently produced obs[10:14] = [rear1_L, front1_L, rear1_R, front1_R] while the
  action vector and the wheelbipe deployment contract (PARAMETERS.md sec.3) are
  [front1_L, rear1_L, front1_R, rear1_R].  Training and deployment then fed the policy
  swapped joint pairs."""
  leg = SceneEntityCfg("robot", joint_names=tuple(names.leg_joints), preserve_order=True)
  wheel = SceneEntityCfg("robot", joint_names=tuple(names.wheel_joints), preserve_order=True)
  # SCUT's current V14 task delays IMU and motor feedback independently.  Keep
  # the deployed 35-D width unchanged, but train the actor with 0..1 policy-step
  # (0..20 ms at 50 Hz) correlated sensor latency.  The privileged critic gets
  # fresh, noise-free state and play/evaluation disables this block.
  sensor_delay = dict(
      delay_min_lag=_OBS_DELAY_MIN,
      delay_max_lag=_OBS_DELAY_MAX,
      delay_per_env=True,
      delay_hold_prob=_OBS_DELAY_HOLD,
      delay_update_period=_OBS_DELAY_PERIOD,
      delay_per_env_phase=True,
  ) if deploy_robust else {}
  return {
    # 0..2  commands (linear.x, reserved 0, angular.z)
    "commands": ObservationTermCfg(func=ob.twist_commands,
                                   params={"command_name": "twist"}),
    # 3     target height x 5
    "height_command": ObservationTermCfg(func=ob.height_command, scale=5.0),
    # 4..6  body rates x 0.5
    "base_ang_vel": ObservationTermCfg(func=envs_mdp.base_ang_vel, scale=0.5,
                                       noise=Unoise(n_min=-0.25, n_max=0.25)
                                       if deploy_robust else None, **sensor_delay),
    # 7..9  projected gravity
    "projected_gravity": ObservationTermCfg(func=velocity_mdp.projected_gravity,
                                            noise=Unoise(n_min=-0.05, n_max=0.05)
                                            if deploy_robust else None, **sensor_delay),
    # 10..13 leg joint positions, relative to the default pose
    "leg_pos": ObservationTermCfg(func=ob.leg_pos, params={"asset_cfg": leg},
                                  noise=Unoise(n_min=-0.01, n_max=0.01)
                                  if deploy_robust else None, **sensor_delay),
    # 14..15 reserved wheel position slots (contract: constant 0)
    "wheel_pos_slots": ObservationTermCfg(func=ob.wheel_pos_slots,
                                          params={"asset_cfg": wheel}),
    # 16..19 leg joint velocities x 0.1
    "leg_vel": ObservationTermCfg(func=ob.leg_vel, params={"asset_cfg": leg},
                                  scale=0.1, noise=Unoise(n_min=-0.5, n_max=0.5)
                                  if deploy_robust else None, **sensor_delay),
    # 20..21 wheel joint velocities x 0.1
    "wheel_vel": ObservationTermCfg(func=ob.wheel_vel, params={"asset_cfg": wheel},
                                    scale=0.1, noise=Unoise(n_min=-1.0, n_max=1.0)
                                    if deploy_robust else None, **sensor_delay),
    # 22..27 previous raw action
    "last_action": ObservationTermCfg(func=envs_mdp.last_action),
    # 28..34 normal-only mode block
    "mode_onehot": ObservationTermCfg(func=ob.mode_onehot),
  }


def _base_env_cfg(play: bool = False, names: ModelNames = OPEN,
                  skills: bool = False) -> ManagerBasedRlEnvCfg:
  wheel_contact = ContactSensorCfg(
    name="wheel_contact",
    primary=ContactMatch(mode="body", pattern=names.wheel_bodies, entity="robot"),
    secondary=ContactMatch(mode="body", pattern="terrain"),
    fields=("found", "force"), reduce="maxforce", num_slots=1, history_length=4,
    track_air_time=True,
  )
  base_contact = ContactSensorCfg(
    name="base_contact",
    primary=ContactMatch(mode="body", pattern=names.base_bodies, entity="robot"),
    secondary=ContactMatch(mode="body", pattern="terrain"),
    fields=("found",), reduce="maxforce", num_slots=1,
  )

  leg = SceneEntityCfg("robot", joint_names=tuple(names.leg_joints), preserve_order=True)
  wheel = SceneEntityCfg("robot", joint_names=tuple(names.wheel_joints),
                    preserve_order=True)
  # Actuator DR must resolve actuator names, not joint names.  If actuator_names
  # is left unset, SceneEntityCfg defaults to slice(None) and a "leg" effort
  # event would silently randomize the wheels too (followed by the wheel event
  # randomizing every actuator a second time).
  leg_drive = SceneEntityCfg("robot", actuator_names=list(names.leg_actuators),
                             preserve_order=True)
  wheel_drive = SceneEntityCfg("robot", actuator_names=list(names.wheel_actuators),
                               preserve_order=True)
  actor_terms = _actor_terms(names, deploy_robust=not play)
  critic_terms = {
    **_actor_terms(names, deploy_robust=False),
    "base_lin_vel": ObservationTermCfg(func=envs_mdp.base_lin_vel, scale=0.5),
    "wheel_contact": ObservationTermCfg(
      func=mdp.wheel_contact_obs, params={"sensor_name": "wheel_contact"}),
  }
  observations = {
    "actor": ObservationGroupCfg(terms=actor_terms, concatenate_terms=True,
                                 enable_corruption=not play),
    "critic": ObservationGroupCfg(terms=critic_terms, concatenate_terms=True,
                                  enable_corruption=False),
  }

  actions: dict[str, ActionTermCfg] = {
    "leg_joint_pos": JointPositionActionCfg(
      entity_name="robot", actuator_names=tuple(names.leg_actuators),
      scale=LEG_ACTION_SCALE, offset=0.0, use_default_offset=True),
    "wheel_joint_vel": JointVelocityActionCfg(
      entity_name="robot", actuator_names=tuple(names.wheel_actuators),
      # Per-model trained value wins over the module default, so the acceptance harness /
      # ONNX export / any bare python session cannot silently use the wrong wheel unit.
      scale=names.wheel_action_scale_override or WHEEL_ACTION_SCALE,
      offset=0.0, use_default_offset=False),
  }

  # 跑 (run) up to 2.8 m/s = 38 rad/s of wheel, inside the DM3519+15.8
  # current-limited plateau (44.0 rad/s); and
  # 小陀螺 (gyro) up to +-6 rad/s of yaw = 1.6 m/s per wheel at the 0.27 m half track.
  # Command window.  The skills/field stage starts from a policy that only ever tracked
  # +-1.0 m/s on a plane; handing it a 2.8 m/s sprint command (or a 2 rad/s spin) on rough
  # ground produced 0.6 s episodes and a slightly negative per-step reward, i.e. "fall over
  # early" was again the better return.  The window is therefore env-overridable so the
  # terrain-adaptation phase can match what the policy can actually do; the full window is
  # opened once the terrain curriculum starts moving.
  vx = (float(os.environ.get("RM_VX_MIN", "-1.5" if skills else "-1.0")),
        float(os.environ.get("RM_VX_MAX", "2.8" if skills else "1.8")))
  # 小陀螺.  The kinematic ceiling is wheel_no_load*wheel_r/half_track =
  # 55.36*0.073/0.270 = 15.0 rad/s, and the SJTU design puts a 360-deg hip on the vehicle
  # precisely so the legs never interfere with a sustained spin.  +-6 under-used the
  # hardware by ~3x, so the command range now goes to +-14 rad/s (env-tunable).
  import os as _os
# Speed / heading tracking widths.  Overridable so a training experiment can narrow them
# without touching the defaults: with the historical sqrt(0.5) = 0.707 m/s the linear
# tracking reward is already flat above ~2 m/s of error (exp(-8) = 3e-4), so the optimum is
# to ignore a 2.8 m/s command and coast - which is exactly what v16 does (measured envelope
# in scripts/speed_envelope.py: cmd 1.0 -> 96 %, 1.8 -> 80 %, 2.8 -> 6 %).
  _LV_STD = float(_os.environ.get("RM_LV_STD", "0.7071067811865476"))
  _AV_STD = float(_os.environ.get("RM_AV_STD", "1.4142135623730951"))
  _wzmax = float(_os.environ.get("RM_WZ_MAX", "14.0"))
  # Start the yaw window at the rate the previous policy demonstrably HELD, then let
  # mdp.gyro_command_range widen it.  Jumping straight to +-14 (what v13 did) put most of the
  # new command space in the tail of the tracking Gaussian and error_vel_yaw rose 0.15 -> 7.0.
  _wz0 = _wzmax if play else float(_os.environ.get("RM_WZ0", "4.0"))
  _wzwin = _wz0 if skills else 1.0
  wz = (-_wzwin, _wzwin) if skills else (-1.0, 1.0)
  commands: dict[str, CommandTermCfg] = {
    "twist": UniformVelocityCommandCfg(
      entity_name="robot", resampling_time_range=(6.0, 12.0),
      rel_standing_envs=0.10 if skills else 0.15,
      rel_heading_envs=0.0, heading_command=False,
      ranges=UniformVelocityCommandCfg.Ranges(
        lin_vel_x=vx, lin_vel_y=(0.0, 0.0), ang_vel_z=wz)),
  }

  hparams = {"body_names": (names.thigh_bodies[0], names.wheel_bodies[0],
                            names.thigh_bodies[1], names.wheel_bodies[1])}
  rewards = {
    "track_lin_vel": RewardTermCfg(func=velocity_mdp.track_linear_velocity, weight=2.0,
                                   params={"command_name": "twist", "std": _LV_STD}),
    # Wider std + higher weight: with std=sqrt(0.5) the Gaussian collapses once the yaw
    # error exceeds ~1 rad/s, so a +-14 rad/s command was actively unrewardable.  sqrt(2.0)
    # keeps a real gradient out to the rates the chassis can actually hold.
    "track_ang_vel": RewardTermCfg(func=velocity_mdp.track_angular_velocity, weight=2.5,
                                   params={"command_name": "twist", "std": _AV_STD}),
    "height_tracking": RewardTermCfg(func=mdp.height_tracking, weight=1.0,
                                     params={"std": 0.06, "command_name": "height",
                                             **hparams}),
    "wheel_contact": RewardTermCfg(func=mdp.wheel_contact_fraction, weight=0.8,
                                   params={"sensor_name": "wheel_contact"}),
    "alive": RewardTermCfg(func=envs_mdp.is_alive, weight=1.0),
    "flat_orientation": RewardTermCfg(func=envs_mdp.flat_orientation_l2, weight=-1.0),
    "lin_vel_z": RewardTermCfg(func=mdp.lin_vel_z_l2, weight=-0.6),
    "ang_vel_xy": RewardTermCfg(func=mdp.ang_vel_xy_l2, weight=-0.05),
    "leg_symmetry": RewardTermCfg(
      func=mdp.leg_symmetry, weight=-0.2,
      params={"leg_joints": tuple(names.leg_joints)}),
    # Plant-dependent smoothness penalty.  The value -2.5e-6 was tuned on the CC plant
    # whose drop-test sum(qacc^2) is ~9e4.  The delivered later plant carries ~6e6 even
    # in a zero-control drop (stiff gas spring + 10 closed-chain equalities, peak
    # constraint force ~1.6e4 N), so the same weight made joint_acc 99% of the episode
    # reward in rm2025_later_cc_v1.  Keep the default for backward compatibility; a new
    # experiment can set RM_JOINT_ACC_W (e.g. -1e-8) without touching the old run.
    "joint_acc": RewardTermCfg(
      func=envs_mdp.joint_acc_l2,
      weight=float(_os.environ.get("RM_JOINT_ACC_W", "-2.5e-6"))),
    "joint_torques": RewardTermCfg(func=envs_mdp.joint_torques_l2, weight=-1.5e-5),
    "joint_power": RewardTermCfg(func=mdp.joint_power, weight=-2.0e-4),
    "action_rate": RewardTermCfg(func=envs_mdp.action_rate_l2, weight=-0.05),
    # SCUT penalises wheel action rate AND the second difference (action smoothness)
    # separately.  mjlab already ships the second-difference term; a small weight here
    # keeps the wheels from chattering without slowing the leg response.
    "action_acc": RewardTermCfg(func=envs_mdp.action_acc_l2, weight=-0.02),
    # Direct counterweight to the entropy bonus.  Split by group: after the wheel unit
    # changed 55 -> 10 rad/s, a wheel action at 1.5 m/s is ~2.4 (vs ~0.44 before), so a
    # single shared weight would either overtax the wheels or under-constrain the legs.
    #
    # 2026-09-10 - weight 0.5 -> 0.1.  At -0.5 this ONE term (-0.2638 per step at
    # iteration 200 of rm2025_later_flat_verify_v1) outweighed every positive reward
    # combined (+0.0991), so the per-step net was -0.208 and the return improved the
    # earlier the robot fell over: "die fast" was the optimal policy and bad_orientation
    # grew monotonically from 3.25 to 210.9.  At -0.1 the same policy state nets +0.003
    # and a healthy one is comfortably positive, which makes surviving the dominant
    # strategy again.  See docs/DIAG_FLAT_V1_20260910.md.
    "action_l2_leg": RewardTermCfg(func=mdp.action_l2, params={"action_slice": (0, 4)},
                                   weight=float(_os.environ.get("RM_ACTION_L2_W", "-0.1"))),
    "action_l2_wheel": RewardTermCfg(func=mdp.action_l2, params={"action_slice": (4, 6)},
                                     weight=float(_os.environ.get("RM_ACTION_L2_WHEEL", "-0.02"))),
    "dof_pos_limits": RewardTermCfg(func=envs_mdp.joint_pos_limits, weight=-5.0),
    # One-shot penalty on a NON-timeout termination (bad_orientation / base_contact /
    # nan_detection - `termination_manager.terminated` excludes time-outs, which live in
    # its separate `time_outs` buffer).  A 20 s episode at a healthy net of ~+0.13/step is
    # worth ~+260, so without this the terminal states were "free": the policy could cash
    # in an early fall instead of paying the remaining tracking cost.  Deliberately
    # comparable to the reward still on the table, not to the whole episode.
    "termination": RewardTermCfg(
      func=envs_mdp.is_terminated,
      weight=float(_os.environ.get("RM_TERM_PENALTY", "-20.0"))),
  }
  if skills:
    rewards.update({
      # 跳: aim for the requested rise, actually get airborne, and do not hop unasked
      # dense + monotone (see jump_progress): the crouch must be free, the push rewarded
      # The jump has to be worth more than the risk of falling, and the gait rewards must
      # not tax the take-off (see mdp.jump_gate).
      "jump_progress": RewardTermCfg(func=mdp.jump_progress, weight=6.0,
                                     params={"cap": 1.2}),
      "jump_tracking": RewardTermCfg(func=mdp.jump_tracking, weight=1.5,
                                     params={"std": 0.05}),
      "jump_airborne": RewardTermCfg(func=mdp.jump_airborne, weight=3.0,
                                     params={"sensor_name": "wheel_contact"}),
      "unwanted_airborne": RewardTermCfg(func=mdp.unwanted_airborne, weight=-0.3,
                                         params={"sensor_name": "wheel_contact",
                                                 "min_vx": 0.8}),
      # 飞坡: reward forward progress while genuinely airborne (no jump request needed).
      # The old unwanted_airborne term punished this exact behaviour, which is why ramp
      # launches were trained away.  Airborne at speed is now a skill, not a mistake.
      "flight_progress": RewardTermCfg(
        func=mdp.flight_progress, weight=2.0,
        params={"sensor_name": "wheel_contact", "min_vx": 0.8}),
      # Landing recovery: after a flight, pay for getting both wheels back down upright.
      "landing_recovery": RewardTermCfg(
        func=mdp.landing_recovery, weight=1.5,
        params={"sensor_name": "wheel_contact", "window_s": 0.5}),
      # 过洞: 越低、越快、越稳、底盘越水平，奖励越高 (user's measured 250x800x300 mm hole).
      "tunnel_traversal": RewardTermCfg(
        func=mdp.tunnel_traversal, weight=5.0,
        params={"terrain_key": "tunnel", "h_ref": 0.28, "h_span": 0.08,
                "vx_ref": 1.5, "tilt_max": 0.30}),
      # 小陀螺: both legs stay the same length while spinning fast
      "gyro_stance": RewardTermCfg(func=mdp.gyro_stance, weight=-8.0,
                                   params={"spin_min": 3.0}),
      # Wide-band 小陀螺 tracking (triangular kernel).  The narrow Gaussian has NO gradient
      # once the commanded rate is far beyond what the policy can hold, which is exactly why
      # v14 plateaued at 5.53 rad/s = 0.88 rev/s while the command window said 13.2.  The
      # user's target is 2 rev/s = 12.57 rad/s.  (Fudan's open-source wheel-leg project uses
      # the same trick: a second, 10x wider yaw-tracking kernel.)
      "gyro_track_wide": RewardTermCfg(
        func=mdp.gyro_track_wide,
        weight=float(_os.environ.get("RM_GYRO_WIDE_W", "1.5")),
        params={"command_name": "twist",
                "band_floor": float(_os.environ.get("RM_GYRO_BAND", "6.0")),
                "max_tilt": float(_os.environ.get("RM_GYRO_TILT", "0.35"))}),
      # running costs more wheel slip / reaction, keep the chassis calm
      "lin_vel_z": RewardTermCfg(func=mdp.lin_vel_z_l2, weight=-1.0),
    })

  terminations = {
    "time_out": TerminationTermCfg(func=velocity_mdp.time_out, time_out=True),
    "bad_orientation": TerminationTermCfg(func=velocity_mdp.bad_orientation,
                                          params={"limit_angle": 0.75}),
    "base_contact": TerminationTermCfg(func=velocity_mdp.illegal_contact,
                                       params={"sensor_name": "base_contact"}),
    "nan_detection": TerminationTermCfg(func=velocity_mdp.nan_detection),
  }

  events = {
    "reset_scene": EventTermCfg(func=velocity_mdp.reset_scene_to_default, mode="reset"),
    "reset_height": EventTermCfg(func=mdp.randomize_height_command, mode="reset",
                                 params={"range": (0.18, 0.34) if not play else (0.22, 0.22)}),
    "reset_base": EventTermCfg(
      func=velocity_mdp.reset_root_state_uniform, mode="reset",
      params={"pose_range": {"x": (-0.1, 0.1), "y": (-0.1, 0.1), "yaw": (-0.3, 0.3)},
              "velocity_range": {"x": (-0.2, 0.2), "y": (-0.2, 0.2), "z": (-0.1, 0.1),
                                 "roll": (-0.3, 0.3), "pitch": (-0.3, 0.3),
                                 "yaw": (-0.3, 0.3)},
              "asset_cfg": SceneEntityCfg("robot")}),
    "push_robot": EventTermCfg(
      func=velocity_mdp.push_by_setting_velocity, mode="interval",
      interval_range_s=(6.0, 12.0),
      params={"velocity_range": {"x": (-0.4, 0.4), "y": (-0.3, 0.3),
                                 "pitch": (-0.4, 0.4)},
              "asset_cfg": SceneEntityCfg("robot")}),
    # SCUT additionally injects a sustained external wrench every 5-10 s (force +-10 N,
    # torque +-1 N*m).  mjlab's apply_body_impulse is the transient, self-clearing version:
    # it applies the wrench for 0.1-0.3 s and then zeroes it, so it does not silently
    # persist across episodes like a raw xfrc_applied write would.
    "push_impulse": EventTermCfg(
      func=envs_mdp.apply_body_impulse, mode="step",
      params={"asset_cfg": SceneEntityCfg("robot", body_names=tuple(names.base_bodies)),
              "force_range": (-10.0, 10.0), "torque_range": (-1.0, 1.0),
              "duration_s": (0.10, 0.30), "cooldown_s": (5.0, 10.0),
              "body_point_offset": (0.0, 0.0, 0.10)}),
    "wheel_friction": EventTermCfg(
      func=dr.geom_friction, mode="reset",
      params={"asset_cfg": SceneEntityCfg("robot", geom_names=tuple(names.wheel_geoms)),
              "operation": "scale", "ranges": (0.7, 1.3), "distribution": "uniform"}),
    # The wheel contact is what decides whether a fast 小陀螺 is achievable at all: the
    # torsional term resists the contact patch pivoting about the contact normal, which is
    # precisely the motion of an in-place spin, and the rolling term resists the wheels
    # themselves.  Both are the least known numbers on this machine (the plant carries
    # 1.2 / 0.02 / 0.002, the reference file uses 0.01 / 0.001), so randomise them per env.
    # mjlab only applies axes 1/2 when condim >= 4, and the wheels are condim=6.
    "wheel_torsion_friction": EventTermCfg(
      func=dr.geom_friction, mode="reset",
      params={"asset_cfg": SceneEntityCfg("robot", geom_names=tuple(names.wheel_geoms)),
              "operation": "scale", "ranges": (0.2, 2.0), "axes": [1],
              "distribution": "uniform"}),
    "wheel_rolling_friction": EventTermCfg(
      func=dr.geom_friction, mode="reset",
      params={"asset_cfg": SceneEntityCfg("robot", geom_names=tuple(names.wheel_geoms)),
              "operation": "scale", "ranges": (0.2, 2.5), "axes": [2],
              "distribution": "uniform"}),
    # Payload / build-mass uncertainty, randomised through the pseudo-inertia matrix so that
    # mass and inertia move together.  The old dr.body_mass("add", -3..+5 kg) changed only
    # the mass; that was harmless while the (buggy) chassis inertia was 1/14 of the true one,
    # but with the corrected plant a +5 kg battery/gimbal load also adds ~0.2 kg*m^2, and a
    # policy trained on 22 kg with 17 kg of inertia is not the policy we want to hand the
    # hardware.  alpha is a log-density scale: mass and inertia both go as e^(2 alpha), so
    # e^(2a) in [13.96/16.96, 21.96/16.96] = [0.823, 1.295] is alpha in [-0.097, +0.129].
    "base_mass": EventTermCfg(
      func=dr.pseudo_inertia, mode="reset",
      params={"asset_cfg": SceneEntityCfg("robot", body_names=tuple(names.base_bodies)),
              "alpha_range": (-0.097, 0.129), "distribution": "uniform"}),
    "base_com": EventTermCfg(
      func=dr.body_com_offset, mode="reset",
      params={"asset_cfg": SceneEntityCfg("robot", body_names=tuple(names.base_bodies)),
              "operation": "add",
              "ranges": {0: (-0.03, 0.03), 1: (-0.03, 0.03), 2: (-0.03, 0.03)}}),
    # NOTE (2026-09-10, MOD4): there used to be a "leg_stiffness" event that scaled
    # jnt_stiffness.  Every actuated leg joint in the delivered plant carries stiffness 0
    # (the legs are torque controlled; the only spring is the gas slide), so scaling it did
    # nothing at all - a silent no-op, the same failure mode as the old wheel-armature
    # override that scaled a zero.  The gas spring has its own randomization below; the
    # dead event is removed rather than left in place pretending to add robustness.
    "leg_damping": EventTermCfg(
      func=dr.joint_damping, mode="reset",
      params={"asset_cfg": leg, "operation": "scale", "ranges": (0.8, 1.25),
              "distribution": "uniform"}),
    # Current limits vary with battery voltage, thermal state and drive
    # calibration.  This mirrors SCUT V14's per-episode output-strength DR, widened from
    # 0.8-1.1 to their 0.75-1.25 once MOD4's masses and gearbox were pinned.
    "leg_effort_scale": EventTermCfg(
      func=dr.effort_limits, mode="reset",
      params={"asset_cfg": leg_drive, "operation": "scale",
              "effort_limit_range": (float(_os.environ.get("RM_EFFORT_LEG_MIN", "0.75")),
                                     float(_os.environ.get("RM_EFFORT_LEG_MAX", "1.25"))),
              "distribution": "uniform"}),
    "wheel_effort_scale": EventTermCfg(
      func=dr.effort_limits, mode="reset",
      params={"asset_cfg": wheel_drive, "operation": "scale",
              "effort_limit_range": (float(_os.environ.get("RM_EFFORT_WHEEL_MIN", "0.9")),
                                     float(_os.environ.get("RM_EFFORT_WHEEL_MAX", "1.1"))),
              "distribution": "uniform"}),
    # SCUT V14 additionally injects per-step drive-gain noise (`leg_effort_noise` /
    # `wheel_effort_noise` in their config) on top of the per-episode scaling.  Without it
    # the policy only ever sees one constant torque authority per episode.  These run in
    # "step" mode, so every control step re-draws the force range around the episode value.
    # Defaults are deliberately small (+-3% legs, +-2% wheels); RM_EFFORT_NOISE=0 disables.
    "leg_effort_noise": EventTermCfg(
      func=dr.effort_limits, mode="step",
      params={"asset_cfg": leg_drive, "operation": "scale",
              "effort_limit_range": (
                  1.0 - float(_os.environ.get("RM_EFFORT_NOISE", "0.03")),
                  1.0 + float(_os.environ.get("RM_EFFORT_NOISE", "0.03"))),
              "distribution": "uniform"}),
    "wheel_effort_noise": EventTermCfg(
      func=dr.effort_limits, mode="step",
      params={"asset_cfg": wheel_drive, "operation": "scale",
              "effort_limit_range": (
                  1.0 - float(_os.environ.get("RM_EFFORT_NOISE_WHEEL", "0.02")),
                  1.0 + float(_os.environ.get("RM_EFFORT_NOISE_WHEEL", "0.02"))),
              "distribution": "uniform"}),
    # A fixed offset for an entire episode is the failure mode of a slightly
    # mis-zeroed absolute encoder; white observation noise does not cover it.
    "leg_encoder_bias": EventTermCfg(
      func=dr.encoder_bias, mode="reset",
      params={"asset_cfg": leg, "bias_range": (-0.015, 0.015)}),
    # --- deployment-transfer randomization -------------------------------------------
    # The trained policy runs against mujoco-warp on the GPU at a 50 Hz torque ZOH, while
    # the wheelbipe deployment injects tau = kp*(q*-q) - kd*qdot as an EXPLICIT
    # qfrc_applied from a 500 Hz loop on the CPU solver.  Both sides are explicit (mjlab's
    # motor actuator is biastype=NONE), but the update instant, the rotor reflected
    # inertia and the hub frictionloss are not identical.  Randomizing them here is what
    # makes the policy tolerant of that mismatch instead of over-fitting to one timing.
    "leg_armature": EventTermCfg(
      func=dr.joint_armature, mode="reset",
      params={"asset_cfg": leg, "operation": "scale", "ranges": (0.7, 1.6),
              "distribution": "uniform"}),
    # MOD4 ships dof_frictionloss = 0 on every joint, so the old "scale" randomization was
    # multiplying zero and the gearbox/joint friction was never modelled at all.  SCUT
    # randomizes friction by ADDING an absolute amount per joint (static/dynamic/viscous
    # +0.25..1.0 / +0.25..1.0 / +0.025..0.1 in their units); the MuJoCo equivalent is an
    # absolute dof_frictionloss.  Ranges are in N*m at the joint.
    "leg_frictionloss": EventTermCfg(
      func=dr.joint_friction, mode="reset",
      params={"asset_cfg": leg, "operation": "abs",
              "ranges": (0.0, float(_os.environ.get("RM_LEG_FRICTION_MAX", "0.10"))),
              "distribution": "uniform"}),
    "wheel_armature": EventTermCfg(
      func=dr.joint_armature, mode="reset",
      params={"asset_cfg": wheel, "operation": "scale", "ranges": (0.7, 1.6),
              "distribution": "uniform"}),
    "wheel_frictionloss": EventTermCfg(
      func=dr.joint_friction, mode="reset",
      params={"asset_cfg": wheel, "operation": "abs",
              "ranges": (0.0, float(_os.environ.get("RM_WHEEL_FRICTION_MAX", "0.02"))),
              "distribution": "uniform"}),
  }

  if names.gas_spring_joints and names.limb_bodies:
    limb_bodies = SceneEntityCfg(
      "robot", body_names=tuple(names.limb_bodies))
    wheel_bodies = SceneEntityCfg(
      "robot", body_names=tuple(names.wheel_bodies))
    spring = SceneEntityCfg(
      "robot", joint_names=tuple(names.gas_spring_joints),
      preserve_order=True)
    # The gas spring is the energy store for steps/jumps.  SCUT randomizes its
    # force and damping; keeping ours fixed made the policy rely on one exact
    # pre-load.  These ranges cover pressure, temperature and seal variation.
    events.update({
      # CAD material assignment and fasteners easily shift individual link and
      # wheel mass by ten percent.  Scale mass and inertia together so every
      # randomized body remains physically valid (SCUT V14 uses the same 0.9-1.1
      # envelope, but pseudo-inertia avoids impossible mass/inertia pairs).
      "limb_pseudo_inertia": EventTermCfg(
        func=dr.pseudo_inertia, mode="reset",
        params={"asset_cfg": limb_bodies,
                "alpha_range": (-0.0526802578, 0.0476550899),
                "distribution": "uniform"}),
      "wheel_pseudo_inertia": EventTermCfg(
        func=dr.pseudo_inertia, mode="reset",
        params={"asset_cfg": wheel_bodies,
                "alpha_range": (-0.0526802578, 0.0476550899),
                "distribution": "uniform"}),
      "gas_spring_stiffness": EventTermCfg(
        func=dr.joint_stiffness, mode="reset",
        params={"asset_cfg": spring, "operation": "scale",
                "ranges": (0.85, 1.15), "distribution": "uniform"}),
      "gas_spring_damping": EventTermCfg(
        func=dr.joint_damping, mode="reset",
        params={"asset_cfg": spring, "operation": "scale",
                "ranges": (0.7, 1.3), "distribution": "uniform"}),
      "gas_spring_friction": EventTermCfg(
        func=dr.joint_friction, mode="reset",
        # MOD4 ships dof_frictionloss = 0 on the gas slide as well, so the old scale range
        # was another multiply-by-zero.  Abs, in N (prismatic joint): gas-spring seal
        # friction is one of the numbers the delivery says needs hardware calibration.
        params={"asset_cfg": spring, "operation": "abs",
                "ranges": (0.0, float(_os.environ.get("RM_GAS_FRICTION_MAX", "5.0"))),
                "distribution": "uniform"}),
    })

  if skills:
    # A take-off necessarily disturbs speed / heading / commanded height / attitude, so
    # those terms are masked out while the jump flag is on (mdp.gated_term).
    for _g in ("track_lin_vel", "track_ang_vel", "height_tracking", "flat_orientation"):
        _t = rewards[_g]
        rewards[_g] = RewardTermCfg(
          func=mdp.gated_term, weight=_t.weight,
          params={"func": _t.func, "params": dict(_t.params or {})})
    # the framework injects the elapsed interval as `dt`, so do not pass it ourselves
    events["jump_schedule"] = EventTermCfg(
      func=mdp.update_jump_command, mode="interval", interval_range_s=(0.5, 0.5))
    events["jump_reset"] = EventTermCfg(func=mdp.reset_jump_command, mode="reset")
    # a wider stance range: low for the gyro, high for clearing obstacles
    events["reset_height"].params["range"] = (0.16, 0.32)

  curriculums: dict[str, CurriculumTermCfg] = {}
  if skills and _os.environ.get("RM_SKILL_SPLIT", "0") == "1":
    # v15 evidence: with vx and wz drawn independently at full range, an env is asked to sprint
    # at 2.8 m/s while spinning at 14 rad/s.  It cannot, so it never traverses its terrain patch
    # and the terrain curriculum demotes it (terrain_levels/mean fell 0.275 -> 0.055 while every
    # skill reward was improving).  Splitting the batch by skill ends the fight.
    curriculums["skill_split"] = CurriculumTermCfg(
      func=mdp.skill_command_split,
      params=dict(command_name="twist",
                  fraction=float(_os.environ.get("RM_SKILL_GYRO_FRAC", "0.25")),
                  wz_loco=float(_os.environ.get("RM_SKILL_WZ_LOCO", "2.0")),
                  wz_max=_wzmax, vx_loco=vx))
  if skills:
    # 小陀螺: open the yaw window only as fast as the robot keeps the rate it was given.
    curriculums["gyro_window"] = CurriculumTermCfg(
      func=mdp.gyro_command_range,
      params=dict(command_name="twist", target=_wzmax, start=_wz0,
                  step=float(_os.environ.get("RM_WZ_STEP", "0.4")),
                  every=int(_os.environ.get("RM_WZ_EVERY", "60")),
                  hi=0.55, lo=0.18, tol=0.25, hard_frac=0.75, min_envs=32, floor=2.0))

  # Physics identity: for the delivered later no-gimbal plant, re-apply the source
  # MJCF's own <option> block.  MjSpec.attach() silently keeps the scene defaults
  # (0.002 s / 100 / 1e-8 / pyramidal, no multiccd) otherwise, which is a different
  # robot from the one that ships.  The earlier CC regression keeps its historic
  # solver settings so its existing checkpoints remain a valid rollback.
  if names.key == "rm2025_later_no_gimbal":
    _o = plant_options(names)
    mujoco_cfg = MujocoCfg(
      timestep=_o["timestep"], integrator=_o["integrator"], cone=_o["cone"],
      solver=_o["solver"], iterations=_o["iterations"],
      ls_iterations=_o["ls_iterations"], tolerance=_o["tolerance"],
      ls_tolerance=_o["ls_tolerance"], impratio=_o["impratio"],
      gravity=_o["gravity"], enableflags=_o["enableflags"],
      disableflags=_o["disableflags"])
    # nconmax/njmax are per-world ALLOCATION hints, not physics semantics.  The MJCF's
    # 512/4096 values make mujoco-warp allocate ~12.9 GB of EPA scratch at 8192 worlds and
    # OOM the 4090.  Keep the same capacity the working CC production run uses; the new
    # gap/narrow/wave terrains can need more, so both are tunable per run.
    sim_nconmax = int(os.environ.get("RM_NCONMAX", "64"))
    sim_njmax = int(os.environ.get("RM_NJMAX", "900"))
  else:
    mujoco_cfg = MujocoCfg(timestep=names.physics_dt, iterations=10,
                           ls_iterations=10, impratio=50, cone="elliptic")
    sim_nconmax, sim_njmax = 64, 900

  return ManagerBasedRlEnvCfg(
    scene=SceneCfg(num_envs=2048, env_spacing=2.5, extent=1.0,
                   terrain=TerrainEntityCfg(terrain_type="plane"),
                   sensors=(wheel_contact, base_contact)),
    observations=observations, actions=actions, commands=commands,
    events=events, rewards=rewards, terminations=terminations,
    curriculum=curriculums, metrics={},
    sim=SimulationCfg(nconmax=sim_nconmax, njmax=sim_njmax, mujoco=mujoco_cfg),
    decimation=names.decimation,
    episode_length_s=20.0,
    viewer=ViewerConfig(origin_type=ViewerConfig.OriginType.ASSET_BODY,
                        entity_name="robot", body_name=names.base_bodies[0],
                        distance=2.4, elevation=-14.0, azimuth=95.0),
  )


def _env_cfg(play: bool, names: ModelNames, skills: bool = False) -> ManagerBasedRlEnvCfg:
  cfg = _base_env_cfg(play=play, names=names, skills=skills)
  cfg.scene.entities = {"robot": make_robot_cfg(names)}
  if play:
    cfg.episode_length_s = int(1e9)
    cfg.events.pop("push_robot", None)
    cfg.events.pop("push_impulse", None)
    cfg.observations["actor"].enable_corruption = False
  return cfg


def flat_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """The earlier serial-chain model (kept for regression)."""
  return _env_cfg(play, OPEN)


def flat_cc_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """The validated similar-linkage closed chain, flat speed/height task."""
  return _env_cfg(play, CC)


def skills_cc_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Closed chain + the three skills the robot has to actually do:
  跑 (run to 2.8 m/s), 跳 (jump on request, 5-11 cm rise), 小陀螺 (sustained +-6 rad/s
  gyro spin, which is what the 360-degree hip exists for)."""
  return _env_cfg(play, CC, skills=True)


def flat_rm2025_later_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """User's later no-gimbal closed-chain model on flat ground."""
  return _env_cfg(play, RM2025_LATER)


def skills_rm2025_later_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """User's later no-gimbal closed-chain model with run/jump/gyro commands."""
  return _env_cfg(play, RM2025_LATER, skills=True)


def field_cc_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """The skills task, but on the RMUC2026 7v7 field: ramps, stairs, barricades and bumps
  whose dimensions come from the map STEP file (cad/out_map/field_dims.json), with a
  difficulty curriculum so the robot is walked up to the hardest feature in the map.

  Spawning uses terrain flat patches, and `terrain_levels_vel` promotes/demotes each env
  between rows by how well it actually tracked its velocity command.
  """
  dims = load_dims()
  cfg = _env_cfg(play, CC, skills=True)
  cfg.scene.terrain = field_terrain_entity(
    num_rows=int(os.environ.get("RM_TERRAIN_ROWS", "8")), size_m=8.0,
    env_spacing=10.0, dims=dims)
  cfg.scene.env_spacing = 10.0
  cfg.events["reset_base"] = EventTermCfg(
    func=velocity_mdp.reset_root_state_from_flat_patches, mode="reset",
    params={"patch_name": "spawn",
            "pose_range": {"x": (-0.25, 0.25), "y": (-0.25, 0.25), "yaw": (-0.5, 0.5)},
            "velocity_range": {"x": (-0.2, 0.2), "y": (-0.2, 0.2), "z": (-0.1, 0.1),
                               "roll": (-0.2, 0.2), "pitch": (-0.2, 0.2),
                               "yaw": (-0.2, 0.2)},
            "asset_cfg": SceneEntityCfg("robot")})
  cfg.curriculum["terrain_levels"] = CurriculumTermCfg(
    func=velocity_mdp.terrain_levels_vel,
    params={"command_name": "twist", "asset_cfg": SceneEntityCfg("robot")})
  cfg.terminations["out_of_terrain"] = TerminationTermCfg(
    func=velocity_mdp.out_of_terrain_bounds,
    params={"asset_cfg": SceneEntityCfg("robot")})
  # on a slope the chassis must stay level relative to gravity, not to the ground
  cfg.rewards["flat_orientation"].weight = -1.5
  return cfg


def field_rm2025_later_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Deployable RMUC2026 task using the user's later no-gimbal closed-chain MJCF."""
  dims = load_dims()
  cfg = _env_cfg(play, RM2025_LATER, skills=True)
  cfg.scene.terrain = field_terrain_entity(
    num_rows=int(os.environ.get("RM_TERRAIN_ROWS", "8")), size_m=8.0,
    env_spacing=10.0, dims=dims)
  cfg.scene.env_spacing = 10.0
  cfg.events["reset_base"] = EventTermCfg(
    func=velocity_mdp.reset_root_state_from_flat_patches, mode="reset",
    params={"patch_name": "spawn",
            "pose_range": {"x": (-0.25, 0.25), "y": (-0.25, 0.25),
                           "yaw": (-0.5, 0.5)},
            "velocity_range": {"x": (-0.2, 0.2), "y": (-0.2, 0.2),
                               "z": (-0.1, 0.1), "roll": (-0.2, 0.2),
                               "pitch": (-0.2, 0.2), "yaw": (-0.2, 0.2)},
            "asset_cfg": SceneEntityCfg("robot")})
  cfg.curriculum["terrain_levels"] = CurriculumTermCfg(
    func=velocity_mdp.terrain_levels_vel,
    params={"command_name": "twist", "asset_cfg": SceneEntityCfg("robot")})
  cfg.curriculum["tunnel_height"] = CurriculumTermCfg(
    func=mdp.tunnel_height_command,
    params={"height": 0.20, "terrain_key": "tunnel"})
  cfg.terminations["out_of_terrain"] = TerminationTermCfg(
    func=velocity_mdp.out_of_terrain_bounds,
    params={"asset_cfg": SceneEntityCfg("robot")})
  cfg.rewards["flat_orientation"].weight = -1.5
  return cfg
