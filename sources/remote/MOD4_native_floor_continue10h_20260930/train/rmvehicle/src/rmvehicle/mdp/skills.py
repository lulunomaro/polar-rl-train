"""Run / jump / gyro-spin skill machinery for the closed-chain vehicle.

Everything here stays contract-compatible: the 35-D observation keeps its documented
layout, and the jump request is published in mode-block slot 4
(``[normal, stair, slope, recover, JUMP, height_target, state_time]``) -- exactly where
the deployment's DT7 ``cmd_state`` puts it.

Jump feasibility for THIS mechanism (20 kg, one leg per side):
  lifting the body by 0.06 m costs      m*g*h = 20*9.81*0.06  = 11.8 J
  the nitrogen spring releases          0.5*k*x^2 = 0.5*6000*0.058^2 = 10.1 J
  from its installed compression, and the two 30 N*m hip-axis motors add the rest
  through the similar linkage, which multiplies knee torque (SJTU note 1.2.1:
  "支持力和扭转力都平均分配到了两关节电机上").
"""
from __future__ import annotations

import os
import math

import torch

from mjlab.entity import Entity
from mjlab.sensor import ContactSensor

from .terrain_utils import terrain_mask

#: a jump request stays up for this long [s]
HOLD_S = (1.0, 1.6)
#: idle time between jump attempts [s]
GAP_S = (3.0, 6.0)
#: probability that the next attempt is actually a jump
# Duty cycle of the jump request: ~27% of the time.  Raising this further makes the
# policy hop continuously and stop tracking speed (measured: p=1.0/gap=0.8-1.8 gave
# jump_airborne 0.45 but episode length 452 and err_vx 0.84).
# probability that an idle->active transition becomes a jump request.
# On the RMUC2026 map a 0.4 duty means hopping on top of the stairs, which is the
# main cause of pitch-exursion falls, so it is tunable per run (RM_JUMP_P).
P_JUMP = float(os.environ.get("RM_JUMP_P", 0.4))
#: requested extra body rise [m].  Bounded by the measured capability of this
#: mechanism at the contract torque: scripts/jump_gains.py gives peak vz 1.10 m/s
#: at +-50.9 N*m -> v^2/2g = 6.2 cm of ballistic rise (0.82 m/s -> 3.4 cm at 30 N*m).
# requested extra body rise [m]; overridable so a run can ask for more than the
# plant can physically deliver.  With the datasheet DM8009 (40 N*m, 17 rad/s, torque-
# speed curve) the open-loop ceiling is ~0.23 m (docs/MOTOR_PARAMS.md E3), so v11 asks
# for 0.08-0.20 m instead of 0.04-0.09 m.
RISE_M = (float(os.environ.get("RM_RISE_MIN", 0.04)),
          float(os.environ.get("RM_RISE_MAX", 0.09)))
def _uniform(n, lo, hi, device):
    return torch.rand(n, 1, device=device) * (hi - lo) + lo


def _ensure(env):
    if not hasattr(env, "_rm_jump_flag"):
        d, B = env.device, env.num_envs
        env._rm_jump_flag = torch.zeros(B, 1, device=d)
        env._rm_jump_target = torch.zeros(B, 1, device=d)
        env._rm_jump_timer = _uniform(B, GAP_S[0], GAP_S[1], d)
        env._rm_jump_phase = torch.zeros(B, 1, device=d)
    return env


def update_jump_command(env, dt: float = 0.5, hold=HOLD_S, gap=GAP_S, p=P_JUMP,
                        target=RISE_M, **_) -> None:
    """Event term (mode="interval"): advance the per-env jump scheduler by ``dt``."""
    _ensure(env)
    d, B = env.device, env.num_envs
    ph, tm = env._rm_jump_phase, env._rm_jump_timer
    # the framework hands us the elapsed interval, which may be a per-env tensor
    step = dt.reshape(-1, 1) if torch.is_tensor(dt) else float(dt)
    tm = tm - step
    expired = tm <= 0
    was_idle = ph <= 0
    go = (expired & was_idle).squeeze(-1)          # idle phase just ended
    act = (expired & ~was_idle).squeeze(-1)        # active phase just ended
    draw = go & (torch.rand(B, device=d) < p)      # ... and this one is a jump
    new_ph = ph.clone()
    new_ph[act] = 0.0
    new_ph[draw] = 1.0
    env._rm_jump_phase = new_ph
    env._rm_jump_flag = new_ph
    dur = torch.where(new_ph > 0, _uniform(B, hold[0], hold[1], d),
                      _uniform(B, gap[0], gap[1], d))
    env._rm_jump_timer = torch.where(expired, dur, tm)
    tgt = _uniform(B, target[0], target[1], d)
    env._rm_jump_target = torch.where(draw.unsqueeze(-1), tgt,
                                      torch.where(act.unsqueeze(-1), torch.zeros_like(tgt),
                                                  env._rm_jump_target))


def reset_jump_command(env, env_ids=None) -> None:
    """Event term (mode="reset"): re-draw the schedule for the given envs."""
    _ensure(env)
    d = env.device
    n = env.num_envs if env_ids is None else (
        env_ids.numel() if hasattr(env_ids, "numel") else len(env_ids))
    ids = env_ids if env_ids is not None else slice(None)
    env._rm_jump_phase[ids] = 0.0
    env._rm_jump_flag[ids] = 0.0
    env._rm_jump_target[ids] = 0.0
    env._rm_jump_timer[ids] = _uniform(n, GAP_S[0], GAP_S[1], d)


def jump_flag(env) -> torch.Tensor:
    """[B,1] 1.0 while a jump is requested (observation slot 32)."""
    return _ensure(env)._rm_jump_flag


def jump_target(env) -> torch.Tensor:
    """[B,1] requested extra body rise [m], 0 when no jump is active."""
    return _ensure(env)._rm_jump_target


def _airborne(env, sensor_name: str) -> torch.Tensor:
    """[B] 1.0 when neither wheel touches the ground (per-env, not the batch mean)."""
    sensor: ContactSensor = env.scene[sensor_name]
    found = sensor.data.found
    touching = (found > 0).float().reshape(found.shape[0], -1).max(dim=1).values
    return 1.0 - touching


def body_rise(env) -> torch.Tensor:
  """[B] chassis height above the standing value [m]."""
  asset: Entity = env.scene["robot"]
  # Different delivered robots place the floating root at different locations.  The old
  # Hero model puts it on the wheel axle (z=0.075); the user's later no-gimbal model puts it
  # on the chassis (z=0.2989368).  Read the configured neutral state instead of baking either.
  return asset.data.root_link_pos_w[:, 2] - asset.data.default_root_state[:, 2]


def jump_tracking(env, std: float = 0.05) -> torch.Tensor:
    """Gaussian tracking of the requested rise while a jump is active."""
    err = (body_rise(env) - jump_target(env).squeeze(-1)) ** 2
    return torch.exp(-err / std ** 2) * jump_flag(env).squeeze(-1)


def jump_progress(env, cap: float = 1.2) -> torch.Tensor:
    """Monotone rise progress: clamp(rise / target, 0, cap) while a jump is requested.

    This is deliberately NOT a symmetric tracking error: a real jump needs a crouch
    first, and any reward that penalises being *below* the nominal height creates the
    local optimum "stand still".  Clamping at zero makes crouching free, so the only
    gradient left is "push harder".
    """
    tgt = jump_target(env).squeeze(-1).clamp(min=1e-3)
    prog = (body_rise(env) / tgt).clamp(0.0, cap)
    return prog * jump_flag(env).squeeze(-1)


def jump_airborne(env, sensor_name: str = "wheel_contact") -> torch.Tensor:
    """Bonus for actually leaving the ground during a requested jump."""
    return _airborne(env, sensor_name) * jump_flag(env).squeeze(-1)


def _root_vx(env) -> torch.Tensor:
    return env.scene["robot"].data.root_link_lin_vel_b[:, 0]


def _upright(env, max_tilt: float = 0.5) -> torch.Tensor:
    g = env.scene["robot"].data.projected_gravity_b
    return ((-g[:, 2]) > math.cos(max_tilt)).float()


def unwanted_airborne(env, sensor_name: str = "wheel_contact",
                      min_vx: float = 0.0) -> torch.Tensor:
    """Penalty for hopping in place when no jump was requested.

    A ramp launch at speed is NOT a mistake: with ``min_vx`` > 0 only slow, unrequested
    airborne phases are penalised, so 飞坡 (drive off a ramp and fly) is not trained away.
    """
    air = _airborne(env, sensor_name)
    if min_vx > 0.0:
        slow = (_root_vx(env).abs() < min_vx).float()
    else:
        slow = torch.ones_like(air)
    return air * (1.0 - jump_flag(env).squeeze(-1)) * slow


def flight_progress(env, sensor_name: str = "wheel_contact", min_vx: float = 0.8,
                    max_tilt: float = 0.6, v_cap: float = 3.0) -> torch.Tensor:
    """飞坡: reward forward progress while genuinely airborne and upright.

    Unlike ``jump_*`` this does not require a jump request: the ramp lip launches the robot,
    and the skill is to keep speed and attitude until the wheels come back down.
    """
    air = _airborne(env, sensor_name)
    vx = torch.clamp(_root_vx(env), min=min_vx, max=v_cap) - min_vx
    return air * _upright(env, max_tilt) * vx


def landing_recovery(env, sensor_name: str = "wheel_contact", window_s: float = 0.5,
                     max_tilt: float = 0.5) -> torch.Tensor:
    """飞坡 landing: after any airborne phase, pay for upright wheels-back-on-ground.

    The touchdown transition is latched for ``window_s`` so a policy cannot farm the bonus
    by bouncing: the reward is only paid while both wheels are in contact and the chassis is
    upright.  The per-step guard keeps the timer correct even if the reward is evaluated
    more than once for logging.
    """
    if not hasattr(env, "_rm_was_airborne"):
        env._rm_was_airborne = torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
        env._rm_landing_timer = torch.zeros(env.num_envs, device=env.device)
        env._rm_landing_step = -1
    air = _airborne(env, sensor_name) > 0.5
    if getattr(env, "_rm_landing_step", -1) != int(env.common_step_counter):
        touchdown = env._rm_was_airborne & ~air
        env._rm_landing_timer = torch.where(
            touchdown, torch.full_like(env._rm_landing_timer, float(window_s)),
            (env._rm_landing_timer - env.step_dt).clamp(min=0.0))
        env._rm_was_airborne = air
        env._rm_landing_step = int(env.common_step_counter)
    active = (env._rm_landing_timer > 0.0).float()
    return active * _upright(env, max_tilt) * (1.0 - air.float())


def tunnel_traversal(env, terrain_key: str = "tunnel", top_offset: float = 0.05968,
                     h_ref: float = 0.28, h_span: float = 0.08, vx_ref: float = 1.5,
                     tilt_max: float = 0.30, rate_sigma: float = 0.5) -> torch.Tensor:
  """过洞奖励：越低、越快、越稳、底盘越水平，奖励越高。

  Only the envs assigned to the tunnel terrain column score.  The four components are
  normalised to [0, 1] and combined as a weighted sum so a single bad axis does not zero
  the whole gradient:

  * ``low``    - chassis top below 0.28 m, maxed at 0.20 m (the user's measured lowest
                 state); weight 0.50
  * ``speed``  - forward speed, maxed at ``vx_ref``; weight 0.25
  * ``level``  - chassis tilt below ``tilt_max`` rad (17 deg); weight 0.125
  * ``stable`` - small roll/pitch rate; weight 0.125
  """
  mask = terrain_mask(env, terrain_key).float()
  if float(mask.sum()) == 0.0:
    return torch.zeros(env.num_envs, device=env.device)
  robot = env.scene["robot"]
  terrain = env.scene["terrain"]
  origins = getattr(terrain, "env_origins", None)
  ground_z = origins[:, 2] if origins is not None else 0.0
  top_h = robot.data.root_link_pos_w[:, 2] - ground_z + top_offset
  low = ((h_ref - top_h) / h_span).clamp(0.0, 1.0)
  speed = (_root_vx(env) / vx_ref).clamp(0.0, 1.0)
  g = robot.data.projected_gravity_b
  tilt = torch.acos((-g[:, 2]).clamp(-1.0, 1.0))
  level = (1.0 - tilt / tilt_max).clamp(0.0, 1.0)
  w = robot.data.root_link_ang_vel_b
  stable = torch.exp(-(w[:, 0] ** 2 + w[:, 1] ** 2) / (2.0 * rate_sigma ** 2))
  return mask * (0.50 * low + 0.25 * speed + 0.125 * level + 0.125 * stable)


def gyro_stance(env, spin_min: float = 3.0) -> torch.Tensor:
    """During 小陀螺 (|yaw command| > spin_min) keep both legs the same length.

    Stops the spin from degenerating into a one-legged wobble; the 360-degree hip is what
    makes sustained spinning possible at all, so this is the skill's stability term.
    """
    asset: Entity = env.scene["robot"]
    cmd = env.command_manager.get_command("twist")
    spin = (cmd[:, 2].abs() > spin_min).float()
    z = asset.data.body_link_pos_w
    names = list(asset.body_names)
    try:
        if "left_thigh" in names:
            hl, hr = names.index("left_thigh"), names.index("right_thigh")
        else:
            hl, hr = names.index("left_rear1"), names.index("right_rear1")
        wl, wr = names.index("left_wheel"), names.index("right_wheel")
    except ValueError:
        return torch.zeros(env.num_envs, device=z.device)
    diff = (z[:, hl, 2] - z[:, wl, 2]) - (z[:, hr, 2] - z[:, wr, 2])
    return spin * diff ** 2


def jump_gate(env, value: torch.Tensor) -> torch.Tensor:
    """Mask a per-env reward out while a jump is being requested.

    Without this the policy is punished for the things a jump necessarily disturbs
    (forward speed, yaw tracking, commanded leg height, a few degrees of pitch), and
    the safe optimum stays "never jump".
    """
    return value * (1.0 - jump_flag(env).squeeze(-1))


def gated_term(env, func, params=None, gate=None) -> torch.Tensor:
    """Run another reward term and zero it out while a jump is requested.

    `gate` defaults to :func:`jump_gate` (mask = 1 - jump_flag).  This is what keeps the
    gait rewards from taxing a take-off: without it the jump is never worth its risk.
    """
    out = func(env, **(params or {}))
    return jump_gate(env, out) if gate is None else gate(env, out)
