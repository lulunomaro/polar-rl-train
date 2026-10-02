"""Skill rewards for the MOD4 Isaac task, ported from the mjlab implementation.

Source of truth for the maths: train/rmvehicle/src/rmvehicle/mdp/skills.py and the
`if skills:` block of train/rmvehicle/src/rmvehicle/env_cfgs.py.  Three families:

* 小陀螺  gyro_track_wide            - wide triangular kernel on the yaw-rate error
* 过洞    tunnel_traversal           - crouch low and cross the 250 mm opening
* 飞坡    flight_progress / unwanted_airborne / landing_recovery

Everything here is plain torch over the Isaac Lab managers, so it stays engine-agnostic and
can be diffed against the mjlab version line by line.
"""
from __future__ import annotations

import os

import torch

from isaaclab.managers import SceneEntityCfg


# --- delivered RMUC2026 dog hole: MEASURED geometry (2026-09-12) ---------------------------
# floor/ceiling: incoming/rmuc2026_field_20260911/rmuc2026_training/reports/tunnel_clearance.json
# roofed span and opening: rays on the delivered collision mesh (see
# incoming/mod4_fixed_20260912/chassis_mod4/reports/tunnel_measured.json and
# docs/MOD4_FIXED_PLANT_INTEGRATION_20260912.md).
HOLE_FLOOR_Z = -0.155806
HOLE_CEILING_Z = 0.091402
HOLE_ROOF_X = (0.760, 1.100)          # depth 0.34 m, both routes (|x|)
HOLE_LANE_Y = (5.42, 6.355)           # opening width 0.935 m, both sides (|y|)
# CAD skin height above the root at the drivable crouch: 244.934 mm envelope at root 0.178 m
# (tools/crouch_window.py, 931 drivable poses scanned).  PhysX only resolves the 232 mm
# collision hull, i.e. 13 mm SHORTER -- scoring the collision geometry alone would teach a
# crossing that the real robot cannot make.
CAD_TOP_ABOVE_ROOT_M = 0.066934
CAD_TOP_OFFSET_ENV = "RM_CAD_TOP_OFFSET_M"


def _hole_inside(env):
    root = _robot(env).data.root_pos_w - env.scene.env_origins
    x, y, z = root[:, 0].abs(), root[:, 1].abs(), root[:, 2]
    # The (x, y) footprint of the dog hole is ALSO part of the road above it: a robot driving
    # over the tunnel at normal height sits ~0.35 m above the hole floor, i.e. above the ceiling,
    # and must not be scored or terminated by the hole's clearance.  Measured 2026-09-12: the
    # first version (footprint only) fired `tunnel_roof_hit` 27 times on the ramp_down routes,
    # which merely pass near the hole.  Require the root to be BELOW the ceiling too.
    under = (z > HOLE_FLOOR_Z - 0.05) & (z < HOLE_CEILING_Z + 0.12)
    return ((x >= HOLE_ROOF_X[0]) & (x <= HOLE_ROOF_X[1]) &
            (y >= HOLE_LANE_Y[0]) & (y <= HOLE_LANE_Y[1]) & under), z


def tunnel_clearance_cad(env, cad_top_offset_m: float = CAD_TOP_ABOVE_ROOT_M,
                         band_m: float = 0.006, penalty_gain: float = 2.0,
                         penetration_scale_m: float = 0.004) -> torch.Tensor:
    """过洞净空（按 CAD 皮肤算）: reward the envelope the REAL robot presents.

    1.0 with >= band_m of clearance under the delivered ceiling, 0 at the ceiling, and a linear
    penalty when the CAD skin would already be inside the roof.  Active only inside the
    delivered roofed span, so it never fires on the open highway.
    """
    inside, z = _hole_inside(env)
    off = float(os.environ.get(CAD_TOP_OFFSET_ENV, cad_top_offset_m))
    clearance = HOLE_CEILING_Z - (z + off)
    good = (clearance / max(1e-6, band_m)).clamp(0.0, 1.0)
    bad = (-clearance / max(1e-6, penetration_scale_m)).clamp(0.0, 1.0)
    return inside.float() * (good - penalty_gain * bad)


def tunnel_roof_hit_cad(env, cad_top_offset_m: float = CAD_TOP_ABOVE_ROOT_M,
                        penetration_m: float = 0.002) -> torch.Tensor:
    """Terminate when the CAD skin is already penetration_m inside the delivered roof."""
    inside, z = _hole_inside(env)
    off = float(os.environ.get(CAD_TOP_OFFSET_ENV, cad_top_offset_m))
    return inside & ((HOLE_CEILING_Z - (z + off)) < -abs(penetration_m))


# SCUT parity (audit item 8): "terrain command override + stable state machine".  The delivered
# 247 mm hole is a 2 mm-tall pose window, so the height command is scheduled BY TERRAIN
# POSITION instead of being one constant for the whole route: normal drive height on the
# approach, a pre-crouch before the mouth, the measured drivable crouch inside the roofed span,
# and a recovery height after the exit.  Values come from tools/crouch_window.py (2026-09-12).
TUNNEL_STAGE_HEIGHT = (0.24, 0.178, 0.178, 0.30)
TUNNEL_STAGE_NAMES = ("approach", "pre_crouch", "inside", "recover")
# Pre-crouch lead.  2026-09-12 measured BOTH failure modes: 0.55 m of lead let the robot arrive
# 66 mm too tall and jam at the mouth, while a 1.00 m lead made it crouch from the spawn -- and a
# crouched robot only makes 0.03-0.09 m/s (probe_crouch_drive.py), so it never reached the hole
# (eval of model_10550: 22 s window, underpass_seen 0/32).  The physics therefore demands a
# DYNAMIC crossing: drive in at speed, squat late, coast through on the guide rollers.  0.40 m
# leaves room to drop while still carrying momentum.
TUNNEL_PRECROUCH_LEAD_M = 0.40


def update_tunnel_state(env, env_ids=None) -> None:
    """Step event: write the staged height command for the tunnel routes (all other routes
    keep the constant their `ROUTE_HEIGHT_CMD` published).  `env_ids` is accepted because
    Isaac Lab's EventManager always passes it, even for mode='step'."""
    h = getattr(env, "_mod4_height_cmd", None)
    if h is None:
        h = torch.full((env.num_envs, 1), 0.24, device=env.device)
        env._mod4_height_cmd = h
    st = getattr(env, "_mod4_tunnel_state", None)
    if st is None or st.numel() != env.num_envs or st.device != env.device:
        st = torch.zeros(env.num_envs, dtype=torch.long, device=env.device)
        env._mod4_tunnel_state = st
    is_tunnel = getattr(env, "_mod4_is_tunnel", None)
    if is_tunnel is None:
        kinds = getattr(env, "_mod4_route_kinds", None)
        ids = getattr(env, "_mod4_route_ids", None)
        if kinds is None or ids is None:
            return
        table = torch.tensor([k == "tunnel_cross" for k in kinds], device=env.device)
        is_tunnel = table[ids.long()]
        env._mod4_is_tunnel = is_tunnel
    root = _robot(env).data.root_pos_w - env.scene.env_origins
    ax, ay = root[:, 0].abs(), root[:, 1].abs()
    lane = (ay >= HOLE_LANE_Y[0] - 0.40) & (ay <= HOLE_LANE_Y[1] + 0.40)
    state = torch.zeros_like(st)
    state = torch.where(is_tunnel & lane & (ax >= HOLE_ROOF_X[0] - TUNNEL_PRECROUCH_LEAD_M)
                        & (ax < HOLE_ROOF_X[0] - 0.05),
                        torch.ones_like(st), state)                       # pre-crouch
    state = torch.where(is_tunnel & lane & (ax >= HOLE_ROOF_X[0] - 0.05) & (ax <= HOLE_ROOF_X[1] + 0.10),
                        torch.full_like(st, 2), state)                    # inside the hole
    state = torch.where(is_tunnel & lane & (ax > HOLE_ROOF_X[1] + 0.10) & (ax <= HOLE_ROOF_X[1] + 0.90),
                        torch.full_like(st, 3), state)                    # exit / recover
    st.copy_(torch.where(is_tunnel, state, torch.zeros_like(st)))
    table = torch.tensor(TUNNEL_STAGE_HEIGHT, device=env.device, dtype=h.dtype)
    h[is_tunnel, 0] = table[st[is_tunnel]]


TUNNEL_TRACK_STD_M = 0.08          # LINEAR ramp half-width (not a Gaussian: a tight kernel has
#                                    no gradient 68 mm away, which is where the first run was)


def tunnel_height_track(env, std: float = TUNNEL_TRACK_STD_M) -> torch.Tensor:
    """Tight height tracking while the robot is under or within the pre-crouch lead of the hole.

    The global height term (std 0.06, weight 1.0) pays 0.42 even 56 mm off command, which is
    exactly how the first fixed-plant run ended up jammed at the mouth 66 mm too tall
    (probe_tunnel_traj.py, 2026-09-12).  This term only scores the tunnel's own
    approach/inside zones, so it sharpens the crouch where the hole demands it without
    changing behaviour anywhere else on the map.
    """
    st = getattr(env, "_mod4_tunnel_state", None)
    if st is None:
        return torch.zeros(env.num_envs, device=env.device)
    robot = _robot(env)
    ground = getattr(env, "_mod4_ground_z", None)
    z = robot.data.root_pos_w[:, 2]
    if ground is not None:
        z = z - ground.to(env.device)
    h = getattr(env, "_mod4_height_cmd", None)
    if h is None:
        return torch.zeros(env.num_envs, device=env.device)
    zone = ((st == 1) | (st == 2)).float()
    err = (z - h[:, 0]).abs()
    # Linear ramp: full credit on command, zero at `std` metres off, and a usable gradient the
    # whole way.  The first version used exp(-(err/std)^2) with std=0.02 -> 1e-4 credit when the
    # robot was 66 mm too tall, i.e. no learning signal exactly where it was needed.
    return zone * (1.0 - (err / max(1e-6, std))).clamp(0.0, 1.0)


def _robot(env):
    return env.scene["robot"]


def yaw_rate(env, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot")) -> torch.Tensor:
    return _robot(env).data.root_ang_vel_b[:, 2]


def tilt_deg(env) -> torch.Tensor:
    g = _robot(env).data.projected_gravity_b
    return torch.rad2deg(torch.acos((-g[:, 2]).clamp(-1.0, 1.0)))


def gyro_track_wide(env, command_name: str = "twist", band: float = 8.0,
                    max_tilt_deg: float = 30.0) -> torch.Tensor:
    """小陀螺: |wz| tracking with a WIDE kernel.

    The narrow Gaussian (std 0.25 rad/s, see track_ang_vel) has no gradient once the
    commanded rate is far beyond what the robot can hold - which is exactly the plateau
    mjlab hit at 5.5 rad/s against a 13 rad/s command.  The triangular kernel keeps a
    slope all the way to ``band``.
    """
    cmd = env.command_manager.get_command(command_name)[:, 2]
    err = (yaw_rate(env) - cmd).abs()
    core = (1.0 - err / band).clamp(min=0.0)
    return core * (tilt_deg(env) < max_tilt_deg).float()


def tunnel_traversal(env, entry: float, exit: float, lane_y: float, hole_h: float,
                     lane_half_width: float = 0.45, rearm_m: float = 0.9,
                     low_margin: float = 0.06, vx_ref: float = 1.0,
                     tilt_ref_deg: float = 20.0) -> torch.Tensor:
    """过洞: crouch below the beam and cross the 250 mm opening.

    The user's spec for this term is graded, not flat: 越低奖励越高、前进越快越高、越稳越
    水平越高.  The previous implementation paid a flat +1 for simply being in the tunnel,
    so a limp crawl and a fast level dash scored the same and the gradient inside the
    opening was zero.  Value in [0.25, 1] while the lane/height/crossing gate holds:

        0.25 floor        - keep the discovery signal (enter the tunnel at all)
        0.5 * low_score   - depth below the beam over ``low_margin`` metres
        0.25 * speed_score- forward speed over ``vx_ref`` m/s
        0.25 * level_score- 1 - tilt / ``tilt_ref_deg``

    ``lane_half_width`` keeps it from farming the reward by driving past the wall on the
    flat; ``just_out`` keeps paying (a little) for the first 60 cm after the exit.
    """
    # LOCAL coordinates: the tunnel coordinates come from FIELD_INFO, which is per-env
    # geometry relative to each environment's origin.  Comparing world x against them made
    # the term identically zero for every environment except the one sitting at the world
    # origin - the exact "registered, logged, never fires" failure this probe exists for.
    root = _robot(env).data.root_pos_w - env.scene.env_origins
    x, y, z = root[:, 0], root[:, 1], root[:, 2]
    in_lane = (y - lane_y).abs() < lane_half_width
    low = z <= (hole_h + 0.02)
    inside = (x >= entry) & (x <= exit)
    just_out = (x > exit) & (x <= exit + 0.6) & (z <= hole_h + 0.05)
    active = in_lane & low & (inside | just_out)
    # Graded quality: lower under the beam, faster forward, more level = more reward.
    low_score = ((hole_h + 0.02 - z) / max(1e-6, low_margin)).clamp(0.0, 1.0)
    vx = _robot(env).data.root_lin_vel_b[:, 0].clamp(min=0.0)
    speed_score = (vx / max(1e-6, vx_ref)).clamp(0.0, 1.0)
    level_score = (1.0 - tilt_deg(env) / max(1e-6, tilt_ref_deg)).clamp(0.0, 1.0)
    quality = 0.5 * low_score + 0.25 * speed_score + 0.25 * level_score
    return active.float() * (0.25 + 0.75 * quality)


def _airborne(env, sensor_cfg: SceneEntityCfg) -> torch.Tensor:
    sensor = env.scene.sensors[sensor_cfg.name]
    # This Isaac Lab version exposes the contact force, not a boolean "found" flag:
    # net_forces_w is [num_envs, num_bodies, 3]; the strongest wheel is what decides.
    forces = sensor.data.net_forces_w
    if hasattr(forces, "torch"):
        forces = forces.torch
    mag = forces.norm(dim=-1).max(dim=1).values
    return (mag < 1.0).float()


def _air_state(env) -> torch.Tensor:
    if not hasattr(env, "_mod4_air_prev"):
        env._mod4_air_prev = torch.zeros(env.num_envs, device=env.device)
        env._mod4_just_landed = torch.zeros(env.num_envs, device=env.device)
    return env._mod4_air_prev


def update_air_state(env, env_ids, sensor_cfg: SceneEntityCfg = SceneEntityCfg("wheel_contact")) -> None:
    """EventTerm (mode='step'): keeps the airborne/just-landed flags used by the rewards."""
    prev = _air_state(env)
    now = _airborne(env, sensor_cfg)
    env._mod4_just_landed = (prev > 0.5) & (now < 0.5)
    env._mod4_air_prev = now


def reset_history(env, env_ids) -> None:
    """EventTerm (mode='reset'): drop every across-episode buffer this task keeps.

    The 2026-09-11 audits (both the mjlab one and the arena one) found the same class of bug in
    three places: the action second difference (`_mod4_prev_action*`) and the landing flags
    (`_mod4_air_prev`, `_mod4_just_landed`) survived a reset, so the first one or two control
    steps of a new episode were scored against the PREVIOUS episode's action and contact
    history -- a "ghost" spike that shows up exactly as the start-of-episode falls.

    The observation delay lines and the action delay line are cleared by their own terms
    (`mod4_task.reset_delay_lines`, `_DelayMixin.reset`); this covers the rest.

    `env_ids` is positional-mandatory for the same reason as update_jump_state: the
    EventManager rejects a two-argument term whose second argument has a default.
    """
    if env_ids is None:
        env_ids = torch.arange(env.num_envs, device=env.device)
    ids = torch.as_tensor(env_ids, device=env.device, dtype=torch.long).flatten()
    if ids.numel() == 0:
        return
    for key in ("_mod4_prev_action", "_mod4_prev_action2", "_mod4_air_prev"):
        buf = getattr(env, key, None)
        if buf is not None:
            buf[ids] = 0.0
    landed = getattr(env, "_mod4_just_landed", None)
    if landed is not None:
        landed[ids] = False
    if getattr(env, "_mod4_jump", None) is not None:
        reset_jump_state(env, ids)


def flight_progress(env, sensor_cfg: SceneEntityCfg, min_vx: float = 0.8) -> torch.Tensor:
    """飞坡: forward progress while genuinely airborne."""
    vx = _robot(env).data.root_lin_vel_b[:, 0]
    air = _airborne(env, sensor_cfg)
    return air * (vx > min_vx).float() * vx.clamp(min=0.0)


def unwanted_airborne(env, sensor_cfg: SceneEntityCfg, min_vx: float = 0.8) -> torch.Tensor:
    """Do not hop in place: airborne with little forward speed is a mistake, not a jump."""
    vx = _robot(env).data.root_lin_vel_b[:, 0]
    air = _airborne(env, sensor_cfg)
    return air * (vx <= min_vx).float()


def landing_recovery(env, max_tilt_deg: float = 30.0) -> torch.Tensor:
    """Reward the step on which an airborne robot touches down still upright."""
    if not hasattr(env, "_mod4_just_landed"):
        _air_state(env)
    return env._mod4_just_landed.float() * (tilt_deg(env) < max_tilt_deg).float()


def filtered_contact_force(env, sensor_cfg: SceneEntityCfg) -> torch.Tensor:
    """Strongest contact force between the sensor bodies and the FILTERED partners only.

    The raw chassis contact sensor aggregates every contact of that body - including the
    legs brushing the chassis - and reported 99% of episodes as "chassis on the ground".
    With ``filter_prim_paths_expr`` set to the floor and the field pieces, the partner
    forces live in ``force_matrix_w`` ([num_envs, num_bodies, num_filters, 3]); that is what
    this reads.
    """
    sensor = env.scene.sensors[sensor_cfg.name]
    m = sensor.data.force_matrix_w
    if m is None:
        return torch.zeros(env.num_envs, device=env.device)
    if hasattr(m, "torch"):
        m = m.torch
    if m.dim() == 4:
        return m.norm(dim=-1).amax(dim=(1, 2))
    return m.norm(dim=-1).amax(dim=1)


def chassis_belly_down(env, sensor_cfg: SceneEntityCfg, threshold: float = 50.0,
                       max_height: float = 0.22, low_pose_h: float = 0.20,
                       low_pose_factor: float = 5.0) -> torch.Tensor:
    """True when the chassis is really on the floor/terrain, not just brushed by a leg.

    The unfiltered chassis contact sensor reports every contact of that body, including the
    legs brushing the chassis - which terminated 99% of episodes.  PhysX's filtered contact
    view crashes on this Isaac build (`contact_view.filter_count` is None), so the
    discrimination is geometric instead: a belly landing is a hard contact AND a low root.
    While walking, the root sits around 0.34 m even when the legs graze the chassis.
    """
    sensor = env.scene.sensors[sensor_cfg.name]
    f = sensor.data.net_forces_w
    if hasattr(f, "torch"):
        f = f.torch
    mag = f.norm(dim=-1).amax(dim=1)
    root_z = _robot(env).data.root_pos_w[:, 2]
    # audit item 6: measure from the LOCAL terrain.  An absolute z gate says "belly down"
    # for a robot standing correctly in the 0.156 m deep dog-hole and misses a real belly
    # landing on the central island.
    ground = getattr(env, "_mod4_ground_z", None)
    z = root_z if ground is None else root_z - ground
    # audit item 3 (2026-09-12): the eight guide rollers belong to the chassis body, so at the
    # dog-hole crouch (root ~0.178 m) their legitimate ground load (~88 N measured) tripped the
    # 50 N belly rule.  While the pose command IS the deep crouch the threshold is raised, so
    # only a real belly slam (>250 N by default) still terminates.
    thr = torch.full_like(mag, float(threshold))
    h = getattr(env, "_mod4_height_cmd", None)
    if h is not None:
        thr = torch.where(h[:, 0] <= float(low_pose_h), thr * float(low_pose_factor), thr)
    return (mag > thr) & (z < max_height)


def chassis_on_ground(env, sensor_cfg: SceneEntityCfg, threshold: float = 50.0,
                      max_height: float = 0.22) -> torch.Tensor:
    """TerminationTerm: the chassis has landed on the ground/terrain."""
    return chassis_belly_down(env, sensor_cfg, threshold, max_height)


def chassis_ground_penalty(env, sensor_cfg: SceneEntityCfg, threshold: float = 50.0,
                           max_height: float = 0.22) -> torch.Tensor:
    """RewardTerm: penalise real ground/terrain contact with the chassis."""
    return chassis_belly_down(env, sensor_cfg, threshold, max_height).float()


def gyro_window_schedule(env, env_ids=None) -> dict:
    """CurriculumTerm: open the yaw command window by +0.5 rad/s every N *iterations*.

    Approximation of SCUT's adaptive gyro window: theirs widens only while the policy holds
    the rate it was given (hold_ratio > 0.25).  This schedule always widens, which is the
    simpler half of the same idea; if the tracking metric in TensorBoard
    (Metrics/twist/error_vel_yaw) does not improve, the window is the first thing to make
    adaptive.

    Call-rate warning (2026-09-11): the term is only re-evaluated when environments reset, so
    a plain call counter advances with the reset pattern (measured ~4 calls/iteration in the
    1024-env field run) -- the window then ran 2 -> 13 rad/s in ~200 iterations instead of the
    intended ~880, i.e. it hard-commanded the final gyro rate, the same failure the retired
    mjlab run showed.  The window is now a function of ``env.common_step_counter`` (one tick
    per control step, 24 per PPO iteration): ``window = start + step * floor(iter / every)``
    with ``iter = common_step_counter / RM_GYRO_STEPS_PER_ITER``.
    """
    import os

    target = float(os.environ.get("RM_GYRO_TARGET", "13.0"))
    start = float(os.environ.get("RM_GYRO_START", "2.0"))
    step = float(os.environ.get("RM_GYRO_STEP", "0.5"))
    every = int(os.environ.get("RM_GYRO_EVERY", "40"))
    steps_per_iter = int(os.environ.get("RM_GYRO_STEPS_PER_ITER", "24"))
    # Drive the schedule off the environment's own control-step counter.  Curriculum terms are
    # only re-evaluated when environments reset, so a call counter advances at a rate that
    # depends on the reset pattern (measured: ~4 calls/iteration, not the 24 an "control steps"
    # reading would suggest) -- that is exactly how the old schedule finished the whole 2->13
    # ramp in ~200 iterations instead of ~880.  ``common_step_counter`` increments once per
    # control step for the whole env, so iterations == counter / steps_per_iter.
    counter = int(getattr(env, "common_step_counter", 0) or 0)
    if not hasattr(env, "_mod4_gyro_calls"):
        env._mod4_gyro_calls = 0
    env._mod4_gyro_calls += 1
    iters = (counter / float(steps_per_iter)) if counter > 0 else (env._mod4_gyro_calls / float(steps_per_iter))
    # SCUT widens the window only while the policy HOLDS the rate it was given
    # (Curriculum/gyro_window/hold_ratio in their config).  We previously ramped on a pure
    # schedule, and the 2026-09-11 sweep shows why that is not enough: the window reached
    # +-13 rad/s while the robot actually held < 1 rad/s.  Compute the hold ratio over the
    # window's own steps and only promote once 25% of environments hold 75% of the window.
    current = float(getattr(env, "_mod4_gyro_window", start))
    term_cmd = env.command_manager.get_term("twist")
    wz = _robot(env).data.root_ang_vel_b[:, 2]
    cmd_wz = term_cmd.command[:, 2]
    # 14:45: the window parked at 6.5 rad/s while the policy held ~1.2, because ANY command
    # above 0.5 counted as evidence -- the low half of the uniform window is trivially "held".
    # Only the DEMANDING commands count now (|cmd| > 75% of the window), so the window stops
    # where the policy can hold the TOP rate and the tracking kernels still have gradient there
    # (band 2.0 and std 1.414 both go numerically to zero once the error exceeds ~4 rad/s).
    active = cmd_wz.abs() > 0.75 * current
    need = min(max(0.25 * current, 0.25), 1.5)
    holding = ((wz - cmd_wz).abs() < need) & active
    ratio = float(holding.sum()) / max(1.0, float(active.sum()))
    env._mod4_gyro_hold = ratio
    level = int(iters // max(1, every))
    scheduled = min(float(target), float(start) + float(step) * level)
    if ratio > 0.25:
        env._mod4_gyro_window = max(current, min(scheduled, current + float(step)))
    else:
        env._mod4_gyro_window = current
    term = env.command_manager.get_term("twist")
    w = env._mod4_gyro_window
    term.cfg.ranges.ang_vel_z = (-w, w)
    return {"gyro_window/limit_rad_s": env._mod4_gyro_window}


def gas_spring_preload(env, env_ids, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
                       joint_names=(), targets=()) -> None:
    """EventTerm (mode='step'): restore the delivered gas-spring preload.

    The delivered MJCF writes the gas slides as preloaded springs
    (``stiffness="3500" springref="0.2206"``) and import_contract.json carries the same number
    as ``target_position_m``.  Isaac's implicit drive pushes towards the joint's *default*
    position instead, which is 0 here, so the stiffness alone gave no preload at all: with the
    stock build the root sagged 0.34 -> 0.20 m within half a second and the gas slide sat at
    -0.018 m (``probe_gas_preload.py``, spring=0 vs spring=1).  Writing the contract target
    every control step reproduces the MJCF force k * (springref - q), which is what keeps the
    leg extended -- and what makes "crouch below the 250 mm beam" an actual skill instead of a
    pose the robot is already in.
    """
    robot = env.scene[asset_cfg.name]
    ctrl = getattr(env, "_mod4_gas_ctrl", None)
    if ctrl is None or ctrl[1].shape[-1] != len(joint_names):
        ids = [robot.joint_names.index(n) for n in joint_names]
        tgt = torch.tensor([float(v) for v in targets], device=env.device, dtype=torch.float32)
        ctrl = (ids, tgt)
        env._mod4_gas_ctrl = ctrl
    ids, tgt = ctrl
    robot.set_joint_position_target(tgt.unsqueeze(0).repeat(env.num_envs, 1), joint_ids=ids)


def reset_skill_lanes(env, env_ids, tunnel_spawn, launch_spawn, tunnel_entry=None,
                       island_entry=None, undulation_entry=None,
                       spawn_start_m: float = 0.35, spawn_ramp_m_per_iter: float = 0.0008,
                       steps_per_iter: int = 24, fraction: float = 0.5):
    """EventTerm (mode='reset'): put part of the batch on the skill lanes.

    Without this the tunnel and launch-ramp rewards almost never fire: the default spawn is
    the centre lane, and nothing forces an environment to drive into the tunnel lane.
    Envs are split round-robin: tunnel lane, launch lane, centre lane.
    """
    robot = _robot(env)
    if env_ids is None:
        env_ids = torch.arange(env.num_envs, device=env.device)
    # P0-1 (audit 2026-09-11): bucket by STABLE env id, not by position in the reset list.
    # With partial resets the old scheme moved an env between tunnel / launch / centre at
    # random, so the per-task commands below would describe the wrong terrain.
    N_TASKS = 8          # 0 normal, 1 stair, 2 slope, 3 tunnel, 4 jump, 5 gyro, 6 island, 7 undulation
    task_buf = getattr(env, "_mod4_task_id", None)
    if task_buf is None or task_buf.numel() != env.num_envs:
        task_buf = torch.zeros(env.num_envs, dtype=torch.long, device=env.device)
        env._mod4_task_id = task_buf
    # P2 stage switch: RM_SKILL_TASKS="0" trains only normal driving, "0,1,2" adds stairs and
    # slopes, "0,1,2,3" adds the tunnel, "0,1,2,3,4,5" is the full mix.  Staging is what the
    # audit asks for (confirm each skill in a dedicated environment before mixing).
    import os as _os
    stage = _os.environ.get("RM_SKILL_TASKS", "")
    if stage:
        allowed = torch.tensor([int(v) for v in stage.split(",") if v.strip() != ""],
                               dtype=torch.long, device=env.device)
        task_buf[env_ids.long()] = allowed[torch.remainder(env_ids.long(), allowed.numel())]
    else:
        task_buf[env_ids.long()] = torch.remainder(env_ids.long(), N_TASKS)
    slot = task_buf[env_ids]
    default = robot.data.default_root_state[env_ids].clone()
    origins = env.scene.env_origins[env_ids]
    pose = default.clone()
    pose[:, 0:3] = default[:, 0:3] + origins
    tun = torch.tensor(tunnel_spawn, device=env.device).unsqueeze(0)
    # 过洞距离课程 (2026-09-11): with the delivered spawn 3 m before the opening the reward
    # never fires -- the warm-started policy advanced 0.43 m in 12 s of lane time (eval of
    # model_600), while the crouch+cross behaviour needs the opening inside the episode.  Start
    # 0.7 m in front of it and walk the spawn back to the contract position as training runs;
    # this is the mjlab terrain-level idea applied to the one feature that needs it.
    # Acceptance runs must use the CONTRACT spawn (3 m before the opening); set
    # RM_TUNNEL_SPAWN_DIST to override the distance curriculum, e.g. RM_TUNNEL_SPAWN_DIST=3.0.
    import os as _os
    forced = _os.environ.get("RM_TUNNEL_SPAWN_DIST", "")
    if forced:
        dist_forced = float(forced)
        tun = torch.tensor([float(tunnel_entry) - dist_forced, tunnel_spawn[1], tunnel_spawn[2]],
                           device=env.device).unsqueeze(0)
    if tunnel_entry is not None and not forced:
        iters = float(getattr(env, "common_step_counter", 0)) / float(steps_per_iter)
        full = abs(float(tunnel_entry) - float(tunnel_spawn[0]))
        # 2026-09-11 06:12: at 0.005 m/iter the spawn outran the policy -- the crouch term went
        # to 0.0000 by iteration 1448 because the lane robots never reached the last 1.5 m.  A
        # slow ramp (0.0008 m/iter) keeps the opening inside their reach so the crouch/cross
        # pair actually gets practised; distance can be pushed back in a later run.
        dist = min(full, 0.80, float(spawn_start_m) + float(spawn_ramp_m_per_iter) * iters)
        tun = torch.tensor([float(tunnel_entry) - dist, tunnel_spawn[1], tunnel_spawn[2]],
                           device=env.device).unsqueeze(0)
    lau = torch.tensor(launch_spawn, device=env.device).unsqueeze(0)
    # P1: the island and undulation features sit further down the centre lane, so those buckets
    # spawn just in front of them instead of 7-11 m away.
    for slot_id, entry_x in ((6, island_entry), (7, undulation_entry)):
        if entry_x is None:
            continue
        m = slot == slot_id
        if bool(m.any()):
            pose[m, 0] = origins[m, 0] + float(entry_x) - 1.5
            pose[m, 1] = origins[m, 1]
            pose[m, 2] = default[m, 2] + origins[m, 2]
    pose[slot == 3, 0:3] = (default[slot == 3, 0:3] + origins[slot == 3]
                            + tun - torch.tensor([0.0, 0.0, 0.0], device=env.device))
    pose[slot == 4, 0:3] = default[slot == 4, 0:3] + origins[slot == 4] + lau
    robot.write_root_pose_to_sim(pose[:, 0:7], env_ids=env_ids)
    robot.write_root_velocity_to_sim(pose[:, 7:13], env_ids=env_ids)


# --- SCUT / rmvehicle reward terms ported 2026-09-11 ---------------------------------
# Source: third_party/rc_mjlab src/robot/mdp/rewards.py and train/rmvehicle/src/rmvehicle/
# env_cfgs.py.  The mjlab team documented (env_cfgs.py, 2026-09-10) that WITHOUT these the
# per-step return of an untrained policy goes negative, "die fast" becomes the optimal
# policy and bad_orientation grows monotonically -- exactly the signature our Isaac runs
# showed on 2026-09-11 (episode length 64 -> 43 -> 23, bad_orientation 99%).

def action_l2(env, action_slice=None) -> torch.Tensor:
    """L2 of (a slice of) the last action: counterweight to the entropy bonus."""
    act = env.action_manager.action
    if action_slice is not None:
        act = act[:, action_slice[0]:action_slice[1]]
    return torch.sum(act * act, dim=1)


def action_acc_l2(env) -> torch.Tensor:
    """L2 of the action second difference -- SCUT penalises wheel chatter this way."""
    act = env.action_manager.action
    prev = getattr(env, "_mod4_prev_action", None)
    prev2 = getattr(env, "_mod4_prev_action2", None)
    if prev is None:
        env._mod4_prev_action = act.clone()
        env._mod4_prev_action2 = act.clone()
        return torch.zeros(env.num_envs, device=env.device)
    acc = act - 2.0 * prev + prev2
    env._mod4_prev_action2 = prev.clone()
    env._mod4_prev_action = act.clone()
    return torch.sum(acc * acc, dim=1)


def wheel_contact_fraction(env, sensor_cfg: SceneEntityCfg, threshold: float = 1.0) -> torch.Tensor:
    """Fraction of wheels touching the ground -- the positive "stand on the wheels" signal."""
    sensor = env.scene.sensors[sensor_cfg.name]
    forces = sensor.data.net_forces_w
    if hasattr(forces, "torch"):
        forces = forces.torch
    mag = forces.norm(dim=-1)
    return (mag > threshold).float().mean(dim=1)


def leg_symmetry(env, leg_joint_names) -> torch.Tensor:
    """|q_left - q_right| summed over the hip/crank pairs (SCUT penalises asymmetry)."""
    robot = _robot(env)
    ids = [robot.joint_names.index(n) for n in leg_joint_names]
    q = robot.data.joint_pos[:, ids]
    half = q.shape[1] // 2
    return torch.sum(torch.abs(q[:, :half] - q[:, half:]), dim=1)


def joint_power(env) -> torch.Tensor:
    """sum |tau * dq| -- mechanical power the motors are dumping into the plant."""
    robot = _robot(env)
    return torch.sum(torch.abs(robot.data.applied_torque * robot.data.joint_vel), dim=1)


def is_terminated(env) -> torch.Tensor:
    """One-shot flag on a NON-timeout termination (envs that just reset)."""
    return env.termination_manager.terminated.float()


def joint_torques_l2_motors(env, joint_names) -> torch.Tensor:
    """sum(tau^2) over the MOTOR joints only.

    Isaac's stock ``joint_torques_l2`` sums ``applied_torque`` over EVERY joint.  In this plant
    the gas slides are driven by implicit actuators whose "torque" is really a FORCE of ~720 N,
    so tau^2 is ~5e5 per gas slide and 99.99% of the penalty -- measured 1.1e6 of 1.1e6 on
    2026-09-11, i.e. -21.9 per step at weight -2e-5, versus ~+0.05 per step of positive reward.
    Paying 20 points per step for merely existing makes "end the episode" the optimal policy:
    the exact "die fast" signature the runs showed.  Restricting the sum to the leg and wheel
    motors puts it back at mjlab's scale (~-0.012/step here, ~-0.0032/step in their iter-21 log).
    """
    robot = _robot(env)
    ids = [robot.joint_names.index(n) for n in joint_names]
    t = robot.data.applied_torque[:, ids]
    return torch.sum(t * t, dim=1)


def joint_power_motors(env, joint_names) -> torch.Tensor:
    """sum |tau * dq| over the motor joints only (same gas-slide inflation as above)."""
    robot = _robot(env)
    ids = [robot.joint_names.index(n) for n in joint_names]
    return torch.sum(torch.abs(robot.data.applied_torque[:, ids] * robot.data.joint_vel[:, ids]), dim=1)


def skill_commands(env, env_ids=None) -> None:
    """EventTerm (mode='step'): drive the per-task command + height target (audit P0-2).

    2026-09-11 audit: the 35-D observation ends in [normal, stair, slope, recover, JUMP,
    height, state_time], but ``mode_onehot`` was hard-coded to normal=1 for every environment
    and every task received the same random twist command -- the policy could not tell whether
    it was being asked to crouch through the tunnel, take the ramp or spin.  Tasks are bucketed
    by stable env id (see reset_skill_lanes) and this term writes the matching command every
    control step:
        1 stair / 2 slope : 0.8 m/s forward, no yaw
        3 tunnel          : 1.2 m/s forward, no yaw, height target 0.25 m (crouch)
        4 jump            : 2.0 m/s run-up, no yaw
        5 gyro            : vx = 0, |wz| = current gyro window (alternating sign)
        0 normal          : left to the command manager's random sampling
    """
    import os

    task = getattr(env, "_mod4_task_id", None)
    if task is None:
        return
    term = env.command_manager.get_term("twist")
    cmd = term.command
    dev = env.device
    fwd = torch.zeros(env.num_envs, device=dev)
    fwd[task == 1] = 0.8
    fwd[task == 2] = 0.8
    fwd[task == 3] = 1.2
    fwd[task == 4] = 2.0
    fwd[task == 6] = 0.9     # island: approach the two-level climb
    fwd[task == 7] = 1.0     # undulation: keep rolling over the bumps
    drive = (task >= 1) & (task <= 7)
    cmd[drive, 0] = fwd[drive]
    cmd[drive, 1] = 0.0
    cmd[drive, 2] = 0.0
    gyro = task == 5
    if bool(gyro.any()):
        win = float(getattr(env, "_mod4_gyro_window", 2.0))
        sign = torch.where(torch.remainder(torch.arange(env.num_envs, device=dev), 2) == 0,
                           torch.ones(env.num_envs, device=dev),
                           -torch.ones(env.num_envs, device=dev))
        cmd[gyro, 0] = 0.0
        cmd[gyro, 1] = 0.0
        cmd[gyro, 2] = sign[gyro] * win
    h = getattr(env, "_mod4_height_cmd", None)
    if h is None:                     # same buffer mod4_task.height_cmd uses for obs[3]
        h = torch.full((env.num_envs, 1), 0.24, device=dev)
        env._mod4_height_cmd = h
    h[task == 3] = float(os.environ.get("RM_TUNNEL_CMD_HEIGHT", "0.25"))
    # The command manager resamples random twists inside env.step(), which runs AFTER this
    # step event -- without pinning its timer the per-task command was overwritten the moment
    # an env resampled (probe showed a slope env holding vx=+2.05 instead of 0.80).
    if hasattr(term, "time_left"):
        term.time_left[drive | gyro] = 1.0e9
    # A standing env (rel_standing_envs) has its command forced to zero by the command
    # manager every step, which zeroed the gyro bucket's spin command.
    if hasattr(term, "is_standing_env"):
        term.is_standing_env[drive | gyro] = False

def tunnel_approach(env, entry: float, lane_y: float, lane_half_width: float = 0.45,
                    vx_ref: float = 1.0) -> torch.Tensor:
    """过洞逼近: dense forward-progress signal inside the tunnel lane.

    Measured 2026-09-11 (eval of model_700, tunnel-lane envs spawned 0.7 m before the opening):
    the robot advanced 0.29 m in 12 s (0.025 m/s) and never reached x = 2.30, so
    ``tunnel_traversal`` could not fire however well it was written.  The lane environments get
    random twist commands -- many of them standing or spinning, with the yaw term weighted 2.5
    against 2.0 for linear -- so nothing pulls them toward the opening.  This term pays forward
    speed only while the robot is in the lane, in front of the opening and moving toward it, so
    the approach itself becomes worth points; once the opening is reached the crouch/cross term
    takes over.
    """
    root = _robot(env).data.root_pos_w - env.scene.env_origins
    x, y = root[:, 0], root[:, 1]
    in_lane = (y - lane_y).abs() < lane_half_width
    before = x < entry
    vx = _robot(env).data.root_lin_vel_b[:, 0].clamp(min=0.0)
    return (in_lane & before).float() * (vx / max(1e-6, vx_ref)).clamp(max=1.0)


def tunnel_crouch(env, entry: float, lane_y: float, lane_half_width: float = 0.45,
                  approach_m: float = 1.5, stand_z: float = 0.33,
                  crouch_z: float = 0.23, min_vx: float = 0.25,
                  target_z: float = 0.26, band: float = 0.03,
                  max_tilt_deg: float = 25.0) -> torch.Tensor:
    """过洞蹲姿: pay for getting low in the last metres before the opening.

    With the approach term alive (0.018 and rising) the lane robots drive at the beam but never
    cross it: ``tunnel_traversal`` needs the root below 0.27 m *while inside the opening*, so
    the crouch has to happen first, and nothing rewarded crouching before 2026-09-11.  This is
    the missing half of the gradient -- score 0 at standing height (0.33 m), 1 at the crouch the
    robot demonstrably reaches (0.23 m, probe_crouch.py: hip -2 / crank +2 -> 0.236 m).
    """
    root = _robot(env).data.root_pos_w - env.scene.env_origins
    x, y, z = root[:, 0], root[:, 1], root[:, 2]
    vx = _robot(env).data.root_lin_vel_b[:, 0]
    in_lane = (y - lane_y).abs() < lane_half_width
    near = (x >= entry - approach_m) & (x < entry)
    # 2026-09-11 07:50: probe_tunnel_pass.py showed that at the deep crouch (root ~0.20 m) the
    # chassis drags and the wheels lose traction -- a constant "deep crouch + drive" command
    # moves the robot 0.00 m.  The useful window is a SHALLOW crouch: low enough to clear the
    # 250 mm beam (z <= 0.27) but still rolling.  So pay for the z = 0.26 m band instead of
    # "as low as possible".
    low = (1.0 - (z - target_z).abs() / max(1e-6, band)).clamp(0.0, 1.0)
    # 2026-09-11 07:10: crouch-only credit taught the robot to STOP and squat in front of the
    # opening (eval of model_1900: max lane x = 1.93 m, opening at 2.30 m, crouch reward 0.35
    # while the crossing stayed 0).  Grading the term by forward speed makes "crouch while
    # driving at the opening" the thing that pays, which is the behaviour the crossing needs.
    moving = (vx / max(1e-6, min_vx)).clamp(0.0, 1.0)
    # 2026-09-11 09:50: probe_tunnel_pass.py with the crouch pose actually SET on the joints
    # (--crouch-rad 1.0) covers 0.35 m in 0.25 s and then stalls at x = 1.95 m with 13-21 deg of
    # pitch -- and the field has nothing between x = 1.60 and the opening at x = 2.30 (checked
    # against the feature AABBs).  So the blocker is the crouch+drive GAIT, not a wall: reward
    # staying level as well as low and moving.
    upright = (1.0 - tilt_deg(env) / max(1e-6, max_tilt_deg)).clamp(0.0, 1.0)
    return (in_lane & near).float() * low * moving * upright


# --- route-driven rewards (delivered RMUC2026 arena, audit P1/P2) ---------------------
# audit item 4 (mjlab "指标不能证明技能成功"): the package returns progress in METRES closed
# since the previous control step, while every other Isaac reward is a per-step value summed
# 100x per second.  At weight 2.0 a 1 m/s drive was therefore worth 0.02 per step against
# ~1.0 per step for merely staying alive, and the measured "run" policy did exactly that:
# progress_sum = -2.271 m over 16 envs x 400 steps, entered = 0, completed = 0.  Scaling the
# progress to a per-SECOND rate puts 1 m/s at 2.0 per step, i.e. driving finally out-scores
# standing.  RM_ROUTE_PROGRESS_SCALE=1 restores the package's raw units for A/B tests.
ROUTE_PROGRESS_SCALE = float(os.environ.get("RM_ROUTE_PROGRESS_SCALE", "100"))
TUNNEL_PROGRESS_MULT = float(os.environ.get("RM_TUNNEL_PROGRESS_MULT", "3"))


def route_progress(env) -> torch.Tensor:
    """Dense progress toward this environment's route goal (package RouteCommands).

    Measured 2026-09-12: on the tunnel route the policy settled into a full-length, high-reward
    episode that barely moved (route_progress 0.037 against alive 0.82 + wheel_contact 0.63 +
    track_lin_vel 1.57).  Since the crouched robot is genuinely slow, the crossing has to be
    worth more than surviving: tunnel routes get `RM_TUNNEL_PROGRESS_MULT` (default 3x).
    """
    d = getattr(env, "_mod4_route_progress", None)
    if not d or "progress_reward" not in d:
        return torch.zeros(env.num_envs, device=env.device)
    scale = torch.full((env.num_envs,), ROUTE_PROGRESS_SCALE, device=env.device)
    is_tunnel = getattr(env, "_mod4_is_tunnel", None)
    if is_tunnel is not None:
        scale = torch.where(is_tunnel.to(env.device),
                            scale * TUNNEL_PROGRESS_MULT, scale)
    return d["progress_reward"] * scale


def tunnel_stall(env, min_vx: float = 0.08, gain: float = 0.5) -> torch.Tensor:
    """Penalty for standing still inside the tunnel's crouch zones (2026-09-12).

    The deep crouch unloads the drive wheels onto the guide rollers, so the robot CAN only creep
    (~0.06 m/s measured); without this term "hold the crouch and time out" is a stable optimum.
    """
    st = getattr(env, "_mod4_tunnel_state", None)
    if st is None:
        return torch.zeros(env.num_envs, device=env.device)
    vx = _robot(env).data.root_lin_vel_b[:, 0].abs()
    zone = ((st == 1) | (st == 2)).float()
    return -gain * zone * (1.0 - (vx / max(1e-6, min_vx)).clamp(0.0, 1.0))


# SCUT parity, last piece (audit item 8: "分阶段落地控制").  Measured 2026-09-12 on the fly
# route: take-off and flight are learned (launched 32/32, air_after_launch 32/32) but the
# episodes end in `base_contact` -- the robot reaches the ground with its legs still extended
# and slams the chassis.  The height command is therefore dropped to an absorb value for a
# short window after touchdown, then released back to the neutral height.
LANDING_ABSORB_HEIGHT = 0.26
LANDING_ABSORB_S = 0.25


def update_landing_state(env, env_ids=None) -> None:
    """Step event: command a short absorb pose after each touchdown (jump-like routes only)."""
    st = getattr(env, "_mod4_jump", None)
    if st is None:
        return
    on_route = st.get("on_route")
    if on_route is None:
        return
    h = getattr(env, "_mod4_height_cmd", None)
    if h is None:
        h = torch.full((env.num_envs, 1), 0.24, device=env.device)
        env._mod4_height_cmd = h
    timer = getattr(env, "_mod4_land_timer", None)
    if timer is None or timer.numel() != env.num_envs:
        timer = torch.zeros(env.num_envs, device=env.device)
        env._mod4_land_timer = timer
    just_landed = getattr(env, "_mod4_just_landed", None)
    if just_landed is not None:
        timer = torch.where(just_landed.bool() & on_route.to(env.device),
                            torch.full_like(timer, LANDING_ABSORB_S), timer)
    dt = float(env.step_dt)
    active = (timer > 0.0) & on_route.to(env.device)
    timer = (timer - dt).clamp(min=0.0)
    env._mod4_land_timer = timer
    if bool(active.any()):
        keep = torch.where(active, torch.full_like(h[:, 0], float(LANDING_ABSORB_HEIGHT)),
                           h[:, 0])
        h[:, 0] = keep


# audit item 4 (mjlab "指标不能证明技能成功"): measured on the run stage 2026-09-11 20:52 --
# `Episode_Reward/track_ang_vel` 4.30 vs `route_progress` 0.288, i.e. 60% of the positive reward
# came from holding a yaw command that is ~0 on a straight route, while driving was 4%.  The
# team's own reference config uses track_ang_vel 2.5 / track_lin_vel 2.0, so the weight is now
# route-aware: full value on the 小陀螺 route (the one place it IS the task), halved elsewhere.
ANG_SCALE_OTHER = float(os.environ.get("RM_ANG_SCALE_OTHER", "0.5"))


def track_ang_vel_route_scaled(env, command_name: str = "twist",
                               std: float = 1.4142135623730951) -> torch.Tensor:
    """track_ang_vel_z_exp with a route-aware weight (spin route keeps the full kernel)."""
    term = env.command_manager.get_term(command_name)
    cmd = term.command
    err = cmd[:, 2] - _robot(env).data.root_ang_vel_b[:, 2]
    value = torch.exp(-torch.square(err) / std ** 2)
    bit = getattr(env, "_mod4_mode_bit", None)
    if bit is None:                       # legacy field task: unchanged
        return value
    spin = (bit == 3).float()             # ROUTE_KIND_BITS["slope_spin"]
    return value * (spin + (1.0 - spin) * ANG_SCALE_OTHER)


def route_success(env) -> torch.Tensor:
    """One-shot bonus on the step the route goal is reached (route-specific gate).

    Audit 2026-09-12: the reward manager multiplies every term by the control dt (0.01 s), so a
    weight of 20 paid only **0.2** on the success step while simply surviving a 30 s tunnel
    episode accumulates ~30.  A finished route was worth 1/150 of standing still, which is why
    every stage preferred to survive.  Dividing by dt restores the intended one-shot magnitude
    (20 * (1/dt) * dt = 20).
    """
    d = getattr(env, "_mod4_route_progress", None)
    if not d or "success" not in d:
        return torch.zeros(env.num_envs, device=env.device)
    return d["success"].float() / max(1e-6, float(env.step_dt))


# --- jump shaping (audit item 7) -------------------------------------------------------
# The delivered RouteCommands samples jump_target = 0.08..0.35 m and pays the height gate
# ONCE, on success, with progress forced to exactly zero on jump routes.  Three other terms
# pay the robot for staying on the ground instead: wheel_contact (+0.8), the height track
# against a 0.18-0.34 m command (a 0.45 m apex scores 0.000) and lin_vel_z_l2 (-0.6 on the
# very vertical speed a take-off needs).  A standing policy therefore out-scores every
# attempt, which is why route_progress stayed 0.0000 on the jump routes for a whole run.
# The terms below pay the crouch, the push-off, the height actually gained, the flight time
# and a clean landing, and the three standing incentives are lifted while a jump route is in
# flight.  The window starts at 0.04-0.09 m (audit item 7) instead of the package's 0.08-0.35.

JUMP_KIND = "jump_in_place"
JUMP_CLIMB_SCALE = 0.01      # reward 1.0 per 1 cm of newly gained apex height
JUMP_LOAD_S = 0.6            # crouch credit only inside this window after a landing
JUMP_CROUCH_REF = 0.02       # crouch credit starts this far BELOW the standing height
JUMP_CROUCH_DEPTH = 0.10     # ... and the depth that earns the full credit
# Push-off credit is a RAMP, not a plain scale: below RM_JUMP_PUSH_VZ_MIN nothing is paid, and
# RM_JUMP_PUSH_VZ is where the credit saturates.  Measured 21:24: with a plain scale the policy
# learned to extend the legs SLOWLY (root rising while the wheels stay on the floor) and farm
# 0.65/step of push reward forever -- 113 "attempts" per window but only 6 reaching the target.
# Only a fast release can actually launch the robot, so only a fast release is paid.
JUMP_PUSH_VZ_MIN = float(os.environ.get("RM_JUMP_PUSH_VZ_MIN", "0.35"))
JUMP_PUSH_VZ = float(os.environ.get("RM_JUMP_PUSH_VZ", "0.80"))  # saturation speed (m/s)
JUMP_LAND_TILT_DEG = 30.0    # a landing beyond this tilt is a crash, not a landing
JUMP_LAND_SIGMA = 1.2        # impact-speed scale (m/s) of the landing-quality kernel
# audit 2026-09-11 20:10 ("假跳跃刷奖励"): the state machine used the RAW contact force, so one
# frame of contact chatter was a take-off and the next frame a landing.  Measured: ~100 000
# "attempts" and 0 reaching the 0.04 m gate.  Take-off now needs JUMP_AIR_FRAMES consecutive
# airborne steps AND upward velocity; landing needs JUMP_CONTACT_FRAMES of stable contact; an
# attempt only counts once it cleared JUMP_MIN_RISE.
JUMP_AIR_FRAMES = int(os.environ.get("RM_JUMP_AIR_FRAMES", "4"))
JUMP_CONTACT_FRAMES = int(os.environ.get("RM_JUMP_CONTACT_FRAMES", "3"))
JUMP_MIN_VZ = float(os.environ.get("RM_JUMP_MIN_VZ", "0.15"))
JUMP_MIN_RISE = float(os.environ.get("RM_JUMP_MIN_RISE", "0.02"))
JUMP_WINDOW_STEPS = int(os.environ.get("RM_JUMP_WINDOW_STEPS", "2400"))   # ~100 iterations


def _jump_state(env):
    """Per-environment jump bookkeeping, created on first use."""
    st = getattr(env, "_mod4_jump", None)
    if st is not None:
        return st
    n, dev = env.num_envs, env.device
    zero = lambda: torch.zeros(n, device=dev)
    st = {
        "on_route": torch.zeros(n, dtype=torch.bool, device=dev),
        # `active` is written every step by update_jump_state; seed it here so a reward-only
        # evaluation (probe_success_reward.py) cannot KeyError before the first step.
        "active": zero(),
        "phase": torch.zeros(n, dtype=torch.long, device=dev),   # 0 grounded, 1 airborne
        "h": zero(), "peak": zero(), "vz": zero(), "air": zero(),
        "airborne": zero(),
        "h_ref": zero(), "risen": zero(),
        "climb": zero(), "crouch": zero(), "push": zero(),
        "land": zero(), "hard": zero(), "impact": zero(),
        "height_hold": zero(), "lin_mask": zero(), "air_t": zero(),
        "attempt_t": torch.zeros(n, device=dev),      # 0 = the load window is open
        "n_attempts": zero(), "n_success": zero(),
        "air_cnt": zero(), "ground_cnt": zero(),
        "peak_vz": zero(),
        "attempts_win": zero(), "reached_win": zero(), "air_win": zero(), "steps_win": zero(),
        "attempts_last": zero(), "reached_last": zero(), "steps_last": zero(), "air_last": zero(),
    }
    env._mod4_jump = st
    return st


def reset_jump_state(env, env_ids=None) -> None:
    """Drop the previous attempt's bookkeeping (called from the route spawn event)."""
    st = _jump_state(env)
    if env_ids is None:
        env_ids = torch.arange(env.num_envs, device=env.device)
    ids = torch.as_tensor(env_ids, device=env.device, dtype=torch.long).flatten()
    if ids.numel() == 0:
        return
    for key in ("h", "peak", "vz", "air", "airborne", "climb", "crouch", "push", "land", "hard",
                "impact", "height_hold", "lin_mask", "air_t", "h_ref", "risen"):
        st[key][ids] = 0.0
    for key in ("air_cnt", "ground_cnt", "peak_vz"):
        st[key][ids] = 0.0
    st["phase"][ids] = 0
    # The load window opens on spawn as well as on touchdown: a fresh episode that starts with
    # a crouch-and-release must earn credit exactly like the second hop of an episode.
    st["attempt_t"][ids] = 0.0


def update_jump_state(env, env_ids,
                      sensor_cfg: SceneEntityCfg = SceneEntityCfg("wheel_contact")) -> None:
    """EventTerm (mode='step'): the jump phase machine and the dense values the rewards read.

    Isaac Lab applies mode='step' events BEFORE the reward manager, so every value written
    here belongs to the control step that is about to be scored.

    `env_ids` is positional-mandatory on purpose: EventManager rejects a step term whose first
    two arguments are not (env, env_ids) -- the same reason update_air_state takes it.
    """
    st = _jump_state(env)
    robot = _robot(env)
    dev, n = env.device, env.num_envs
    zero = torch.zeros(n, device=dev)
    on_route = getattr(env, "_mod4_is_jump", None)
    if on_route is None or on_route.numel() != n:
        on_route = torch.zeros(n, dtype=torch.bool, device=dev)
    on_route = on_route.to(dev).bool()
    st["on_route"] = on_route
    ground = getattr(env, "_mod4_ground_z", None)
    z = robot.data.root_pos_w[:, 2]
    h = z if ground is None else z - ground.to(dev)
    vz = robot.data.root_lin_vel_w[:, 2]
    forces = env.scene.sensors[sensor_cfg.name].data.net_forces_w
    if hasattr(forces, "torch"):
        forces = forces.torch
    grounded = forces.norm(dim=-1).max(dim=1).values > 1.0
    dt = float(env.step_dt)
    # --- debounced contact bookkeeping (audit 2026-09-11 20:10) --------------------------
    air_raw = on_route & (~grounded)
    air_cnt = torch.where(air_raw, st["air_cnt"] + 1.0, zero)
    ground_cnt = torch.where(on_route & grounded, st["ground_cnt"] + 1.0, zero)
    air = on_route & (air_cnt >= JUMP_AIR_FRAMES)          # debounced: chatter is not flight
    was_air = st["phase"] == 1
    liftoff = air & (~was_air)
    touchdown = on_route & (ground_cnt >= JUMP_CONTACT_FRAMES) & was_air
    # height gained since the previous control step (dense: one value per step, no gate)
    gain = (h - st["peak"]).clamp(min=0.0)
    climb = torch.where(air, (gain / JUMP_CLIMB_SCALE).clamp(0.0, 1.0), zero)
    peak = torch.where(air_raw, torch.maximum(st["peak"], h), st["peak"])
    peak = torch.where(liftoff, h, peak)
    # load phase: crouch low, then push off inside JUMP_LOAD_S of touching down
    attempt_t = torch.where(touchdown, zero,
                            torch.where(on_route & grounded, st["attempt_t"] + dt,
                                        st["attempt_t"]))
    loading = on_route & grounded & (attempt_t < JUMP_LOAD_S)
    # The crouch is measured against THIS attempt's standing height, not against an absolute
    # 0.28 m: the arena spawns at different ground offsets, and an absolute reference silently
    # paid zero on every route where the robot stands lower (measured 2026-09-11: jump_crouch
    # stayed 0.0000 for a whole rollout while the root height never reached the threshold).
    crouch = loading.float() * (((st["h_ref"] - JUMP_CROUCH_REF) - h)
                                / JUMP_CROUCH_DEPTH).clamp(0.0, 1.0)
    # The push-off is the behaviour the policy never discovers: measured 21:10, jump_push was
    # 0.0079 and jump_climb 0.0000 -- the robot simply never extends upward.  A crouch-release
    # is a COORDINATED sustained action pattern that sigma=0.28 per joint essentially never
    # samples, so the reward has to point at it directly: the push term pays upward root speed
    # inside the load window (so a post-window bounce cannot farm it), and its weight is 10.
    push = (loading).float() * ((vz - JUMP_PUSH_VZ_MIN)
                                / max(1e-6, JUMP_PUSH_VZ - JUMP_PUSH_VZ_MIN)).clamp(0.0, 1.0)
    # landing quality: upright, low impact
    impact = torch.where(touchdown, vz.abs(), zero)
    upright = tilt_deg(env) < JUMP_LAND_TILT_DEG
    land = (touchdown & upright).float() * torch.exp(-torch.square(impact / JUMP_LAND_SIGMA))
    hard = (touchdown & (~upright)).float()
    # The package measures a jump as the rise above the SPAWN root height, not above the floor:
    # track the highest grounded height of the attempt as the reference (audit item 7).
    h_ref = torch.where(on_route & grounded, torch.maximum(st["h_ref"], h), st["h_ref"])
    risen = (peak - h_ref).clamp(min=0.0)
    target = getattr(env, "_mod4_jump_target", None)
    reached = (touchdown & (risen >= target.to(dev))) if target is not None else \
        torch.zeros(n, dtype=torch.bool, device=dev)
    # 2026-09-11 20:00, measured: with an ungated air reward the policy farmed it by bouncing
    # at 1 cm -- jump_air 0.26, jump_land 0.35, reach_ratio 0.0000, peak_rise 0.0094 m.
    # Air time, climb and landing quality are therefore paid in proportion to how much of the
    # REQUESTED height the attempt actually cleared: a 1 cm bounce against a 5 cm target is
    # worth 20%, a full hop 100%.  A hard gate would have killed the gradient for the first
    # half of the rise; scaling keeps it monotone.
    # 2026-09-11 21:40 measurement: with frac = risen/target the policy farmed the flight stack
    # by hopping 1-2 cm forever (attempts 1900 -> 4118 per window, reach_ratio 0.113 -> 0.079,
    # episodes 134 steps of hop-and-fall).  Two design fixes:
    #   * the sampled target was NEVER an input to the policy (it is not in the 35-D contract),
    #     so the run now uses a FIXED target (RM_JUMP_LO=RM_JUMP_HI) -- a deterministic task;
    #   * the flight rewards ramp from HALF the target to the target (0 below half), so a hop
    #     that cannot clear half of what was asked pays nothing while a real hop still does.
    half = (0.5 * target.to(dev)).clamp(min=1e-6) if target is not None else zero
    frac = (((risen - half) / half).clamp(0.0, 1.0) if target is not None else zero)
    climb = climb * frac
    land = land * frac
    # an attempt only counts once it cleared a real rise with upward velocity
    real = (risen >= JUMP_MIN_RISE) & (st["peak_vz"] > JUMP_MIN_VZ)
    landed_real = touchdown & real
    reached_land = landed_real & (risen >= target.to(dev)) if target is not None else \
        torch.zeros(n, dtype=torch.bool, device=dev)
    st["h"], st["peak"], st["vz"] = h, peak, vz
    st["h_ref"], st["risen"] = h_ref, risen
    # TWO air flags on purpose:
    #   airborne = debounced "off the ground" (1/0) -> masks, height-reward freeze
    #   air      = airborne * height-progress fraction -> the REWARD value
    # They were the same variable until 2026-09-11 21:00, and because `frac` is ~0 for a small
    # hop the freeze test (`air > 0.5`) silently stopped protecting those hops: a small hop lost
    # the whole height reward and paid almost nothing back, so the policy learned to STOP
    # hopping (measured: jump_air 0.0001, jump_climb 0.0000, 5 attempts per 1.2M env-steps).
    st["airborne"] = air.float()
    st["air"], st["climb"], st["crouch"], st["push"] = air.float() * frac, climb, crouch, push
    st["land"], st["hard"], st["impact"] = land, hard, impact
    st["air_cnt"], st["ground_cnt"] = air_cnt, ground_cnt
    st["peak_vz"] = torch.where(liftoff, vz.clamp(min=0.0),
                                torch.maximum(st["peak_vz"], torch.where(air_raw, vz, zero)))
    st["peak_vz"] = torch.where(touchdown, zero, st["peak_vz"])
    st["attempt_t"] = attempt_t
    st["air_t"] = torch.where(air, st["air_t"] + dt, zero)
    st["phase"] = torch.where(liftoff, torch.ones_like(st["phase"]),
                              torch.where(touchdown, torch.zeros_like(st["phase"]), st["phase"]))
    st["lin_mask"] = (air | (on_route & grounded & (vz > 0.05))).float()
    # One mask for every "the robot is mid-attempt" exemption (stability / action penalties):
    # loading, pushing and flying are all part of the same manoeuvre.
    st["active"] = (air | loading).float()
    st["n_attempts"] = st["n_attempts"] + liftoff.float()
    st["n_success"] = st["n_success"] + reached.float()
    # windowed INTEGER metrics (audit: cumulative counters hide "100 000 attempts, 0 reached")
    st["attempts_win"] = st["attempts_win"] + landed_real.float()
    st["reached_win"] = st["reached_win"] + reached_land.float()
    st["air_win"] = st["air_win"] + air.float()
    st["steps_win"] = st["steps_win"] + 1.0
    _win = int(getattr(env, "_mod4_jump_win_step", 0)) + 1
    if _win >= JUMP_WINDOW_STEPS:
        # Keep the FINISHED window's numbers: the curriculum term runs right after this event,
        # so zeroing them here made `window_done` unreachable and the height ceiling could
        # never be promoted (measured 2026-09-11 20:28: reach_ratio and window_done frozen at
        # 0.25 / 0.0 for 20 minutes while the window kept rolling underneath).
        st["attempts_last"] = st["attempts_win"].clone()
        st["reached_last"] = st["reached_win"].clone()
        st["steps_last"] = st["steps_win"].clone()
        st["air_last"] = st["air_win"].clone()
        for _k in ("attempts_win", "reached_win", "air_win", "steps_win"):
            st[_k].zero_()
        _win = 0
    env._mod4_jump_win_step = _win
    env._mod4_jump_phase = st["phase"]


def _jump_val(env, key) -> torch.Tensor:
    st = getattr(env, "_mod4_jump", None)
    if st is None:
        return torch.zeros(env.num_envs, device=env.device)
    return st[key]


def jump_crouch(env) -> torch.Tensor:
    """Dense: how deep and how promptly this jump route loaded its legs."""
    return _jump_val(env, "crouch")


def jump_push(env) -> torch.Tensor:
    """Dense: upward root speed while the wheels are still in contact (the extension)."""
    return _jump_val(env, "push")


def jump_climb(env) -> torch.Tensor:
    """Dense: new apex height gained this control step (1.0 per JUMP_CLIMB_SCALE metre)."""
    return _jump_val(env, "climb")


def jump_air(env) -> torch.Tensor:
    """Dense: 1.0 for every control step a jump route spends off the ground."""
    return _jump_val(env, "air")


def jump_land(env) -> torch.Tensor:
    """One-shot: landing quality of a jump route (upright + impact-speed kernel)."""
    return _jump_val(env, "land")


def jump_hard_land(env) -> torch.Tensor:
    """One-shot: 1.0 when a jump route touched down out of shape."""
    return _jump_val(env, "hard")


def jump_freeze_height(env, value: torch.Tensor) -> torch.Tensor:
    """Hold the height reward while a jump route is airborne.

    The height reward targets a 0.18-0.34 m root height, so a 0.45 m apex scores 0.000 for
    the whole flight -- the third term that made standing cheaper than jumping.
    """
    st = getattr(env, "_mod4_jump", None)
    if st is None:
        return value
    # use the UNWEIGHTED airborne flag: the reward value `st["air"]` is scaled by the height
    # fraction and is ~0 for a small hop, which used to disable this freeze exactly when it
    # was needed (see the comment in update_jump_state).
    out = torch.where(st["airborne"] > 0.5, st["height_hold"], value)
    st["height_hold"] = out.detach()
    return out


def lin_vel_z_l2_jump_exempt(env) -> torch.Tensor:
    """lin_vel_z_l2 with the penalty lifted during a jump push / flight (audit item 7)."""
    value = torch.square(_robot(env).data.root_lin_vel_b[:, 2])
    return value * (1.0 - _jump_active(env))


def _jump_active(env) -> torch.Tensor:
    """[N] 1.0 while a jump route is loading, pushing off or flying (0.0 everywhere else)."""
    st = getattr(env, "_mod4_jump", None)
    if st is None:
        return torch.zeros(env.num_envs, device=env.device)
    active = st.get("active")
    if active is None:
        return torch.zeros(env.num_envs, device=env.device)
    return active.clamp(0.0, 1.0)


def ang_vel_xy_jump_exempt(env) -> torch.Tensor:
    """ang_vel_xy_l2 with the roll/pitch RATE penalty lifted mid-attempt.

    Measured 2026-09-11: a scripted crouch-and-release paid -11.6 of ang_vel_xy (weight -0.05,
    squared) against +5.1 of jump_climb and +2.7 of jump_push -- the single largest reason the
    scripted hop scored below standing still.  The attitude itself is still scored by
    flat_orientation (and by jump_hard_land on touchdown); only the rate is exempt.
    """
    w = _robot(env).data.root_ang_vel_b
    value = torch.sum(torch.square(w[:, :2]), dim=1)
    return value * (1.0 - _jump_active(env))


def flat_orientation_jump_exempt(env) -> torch.Tensor:
    """flat_orientation_l2, halved while a jump attempt is in progress."""
    g = _robot(env).data.projected_gravity_b
    value = torch.sum(torch.square(g[:, :2]), dim=1)
    return value * (1.0 - 0.5 * _jump_active(env))


def action_rate_jump_exempt(env) -> torch.Tensor:
    """action_rate_l2, exempt mid-attempt: the release IS a step change in the leg command."""
    prev = getattr(env.action_manager, "prev_action", None)
    if prev is None:
        return torch.zeros(env.num_envs, device=env.device)
    value = torch.sum(torch.square(env.action_manager.action - prev), dim=1)
    return value * (1.0 - _jump_active(env))


def action_l2_jump_exempt(env, action_slice=None) -> torch.Tensor:
    """action_l2, exempt mid-attempt: holding a deep crouch is not wasted effort."""
    return action_l2(env, action_slice) * (1.0 - _jump_active(env))


def wheel_contact_fraction_jump_exempt(env, sensor_cfg: SceneEntityCfg,
                                       threshold: float = 1.0) -> torch.Tensor:
    """wheel_contact_fraction that does not charge a jump route for leaving the ground."""
    value = wheel_contact_fraction(env, sensor_cfg, threshold)
    st = getattr(env, "_mod4_jump", None)
    if st is None:
        return value
    air = st["airborne"].clamp(0.0, 1.0)
    return value * (1.0 - air) + air


def jump_target_schedule(env, env_ids=None) -> dict:
    """CurriculumTerm: widen the jump-height window only while hops actually clear it.

    The package samples 0.08..0.35 m, which the audit flagged as above this plant's reach.
    Stage 1 starts at 0.04-0.09 m and opens by one step every RM_JUMP_EVERY iterations, and
    only while >= RM_JUMP_HOLD of the attempted hops landed inside the window.
    """
    import os as _os

    lo = float(_os.environ.get("RM_JUMP_LO", "0.04"))
    hi0 = float(_os.environ.get("RM_JUMP_HI", "0.09"))
    hi_max = float(_os.environ.get("RM_JUMP_HI_MAX", "0.24"))
    step = float(_os.environ.get("RM_JUMP_HI_STEP", "0.01"))
    every = max(1, int(_os.environ.get("RM_JUMP_EVERY", "20")))
    hold = float(_os.environ.get("RM_JUMP_HOLD", "0.5"))
    steps_per_iter = max(1.0, float(_os.environ.get("RM_GYRO_STEPS_PER_ITER", "24")))
    rng = getattr(env, "_mod4_jump_range", None)
    if rng is None:
        rng = [lo, hi0]
        env._mod4_jump_range = rng
    st = getattr(env, "_mod4_jump", None)
    # audit 2026-09-11 20:10: cumulative counters hid "100 000 attempts, 0 reached".  The
    # promotion gate now reads a WINDOW of JUMP_WINDOW_STEPS control steps, so the number the
    # curriculum acts on is always a rate over the last ~100 iterations.
    # read the LAST COMPLETE window (stable for ~100 iterations) plus the running one, so the
    # promotion decision is never taken on a window that was just reset.
    attempts = (float(st["attempts_last"].sum()) + float(st["attempts_win"].sum())
                if st is not None else 0.0)
    reached = (float(st["reached_last"].sum()) + float(st["reached_win"].sum())
               if st is not None else 0.0)
    air_steps = (float(st["air_last"].sum()) + float(st["air_win"].sum())
                 if st is not None else 0.0)
    steps = (float(st["steps_last"].sum()) + float(st["steps_win"].sum())
             if st is not None else 0.0)
    window_done = st is not None and float(st["steps_last"].sum()) >= 0.5 * JUMP_WINDOW_STEPS * env.num_envs
    ratio = (reached / attempts) if attempts > 0 else 0.0
    counter = int(getattr(env, "common_step_counter", 0) or 0)
    level = int((counter / steps_per_iter) // every)
    scheduled = min(hi_max, hi0 + step * max(0, level))
    if window_done and attempts >= 20 and ratio >= hold:
        rng[1] = min(scheduled, rng[1] + step)
    return {"jump/target_lo_m": round(rng[0], 4), "jump/target_hi_m": round(rng[1], 4),
            "jump/attempts": attempts, "jump/reached": reached,
            "jump/reach_ratio": round(ratio, 4),
            "jump/air_frac": round(air_steps / max(1.0, steps), 4),
            "jump/window_steps": round(steps / max(1.0, float(env.num_envs)), 1) if st is not None else 0.0,
            "jump/window_done": int(bool(window_done))}
