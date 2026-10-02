import os

import torch

_ROUTE_FILTER = None          # cached list of allowed route indices (RM_ROUTE_KINDS)

# Per-route crouch command (mjlab audit P0-2: "each task needs an explicit command").  The
# height command IS the crouch channel of the 35-D contract; the stock task samples 0.18-0.34 m
# uniformly for every environment, which asks the robot to crouch on the highway and to stand
# tall inside the 250 mm dog hole.  Values follow the audit: tunnel 0.24-0.26 m, everything else
# at the top of the command range.
RUN_HEIGHT_CMD = float(os.environ.get("RM_RUN_HEIGHT_CMD", "0.34"))
if not 0.18 <= RUN_HEIGHT_CMD <= 0.34:
    raise ValueError("RM_RUN_HEIGHT_CMD must lie in [0.18, 0.34] m")
ROUTE_HEIGHT_CMD = {
    "run": RUN_HEIGHT_CMD, "step_up": 0.32, "step_down": 0.32, "ramp_up": 0.32, "ramp_down": 0.32,
    # `jump_in_place` used to ask for 0.24 m, i.e. a DEEP CROUCH to hold.  Measured 21:07: the
    # height reward (+1.0/step, maxed at exactly 0.24) then paid the policy to crouch and STAY
    # there, and the flight rewards were 0.0000-0.0003 -- 1.2M env-steps produced 4 attempts.
    # The crouch belongs to the jump itself (jump_crouch/jump_push shape it), so the command is
    # the neutral standing height and the crouch is no longer the reward optimum.
    "rough_cross": 0.32, "slope_spin": 0.32, "fly_jump": 0.32, "jump_in_place": 0.34,
    # audit 2026-09-11 20:10: the delivered dog hole measures 247.2 mm of clear height, so a
    # 250 mm command asks for a pose that cannot fit.  Direct COLLISION-envelope measurement
    # (probe_tunnel_fit_arena.py, root clamped inside the roofed corridor at x=0.92):
    #   0.18/0.20/0.21/0.22 m -> chassis-roof contact 0 N   (fits)
    #   0.23 m                 -> 519 N                    (grazes the roof)
    #   0.24 m                 -> 339 021 N                (deep penetration)
    # so the command sits 10 mm below the measured boundary.  The CAD skin is taller than the
    # collision geometry, which is why the real robot still needs the roof lowered -- see the
    # hardware note in the docs.
    # 22:30 follow-up: with a 0.21 m command the height reward kernel (std 0.06) still pays 0.78
    # at 0.24 m, where the envelope no longer fits (519 N against the roof) -- the tunnel stage
    # spent 45 min crouched and driving on the spot (route_progress 0.035, underpass never seen).
    # 2026-09-12 (crouch_window.py, 982 drivable poses): the commands above were calibrated on
    # the PhysX COLLISION hull (232 mm), which is 13 mm shorter than the CAD skin (245 mm).  The
    # real envelope only fits the delivered 247.2 mm hole for root z <= 0.180 m, and the driving
    # wheels only touch the floor for root z >= 0.178 m.  The command is therefore the deep end
    # of that 2 mm window: 0.178 m -> CAD envelope 244.9 mm, i.e. 2.3 mm of real clearance,
    # while `skills.tunnel_clearance_cad` scores exactly that envelope during training.
    # Start at the normal approach height.  update_tunnel_state() changes this to the verified
    # 0.178 m pose only after the robot enters the pre-crouch window.  Publishing 0.178 here
    # made the very first post-reset observation demand a hard crouch even when the spawn was
    # still in the open approach lane.
    "tunnel_cross": 0.24,
}

# audit item 7: the jump state machine scores both kinds of "leave the ground" route.
JUMP_LIKE_KINDS = ("jump_in_place", "fly_jump")

"""Route-driven spawn + commands for the delivered RMUC2026 arena (audit P1).

Thin adapter over the package's RouteCommands so mod4_task only needs events:
  route_spawn     (mode='reset') : place each env on its semantic route
  route_commands  (mode='step')  : write the route's velocity command every control step

Audit items 1/2/7/9 (2026-09-11): the route FILTER, the spawn point, the observation mode
bits, the jump bookkeeping and the evaluator's per-route labels all read the SAME id tensor,
so a stage can no longer spawn on one route, command a second and report a third.
"""


def route_controller(env):
    """Lazily build the package's RouteCommands (15 routes) on this env."""
    rc = getattr(env, "_mod4_routes", None)
    if rc is None:
        import sys
        import mod4_task
        if str(mod4_task.RMUC2026_ISAAC) not in sys.path:
            sys.path.insert(0, str(mod4_task.RMUC2026_ISAAC))
        from route_commands import RouteCommands
        base_h = float(mod4_task.CONTRACT["spawn_height_m"])
        rc = RouteCommands(env.scene.env_origins, base_height_m=base_h)
        # Training-scope goal override (distance curriculum).  Measured 2026-09-12: at the
        # crouch the robot only makes 0.05-0.09 m/s (probe_crouch_drive.py), so the full 2 m
        # delivered route cannot be finished inside an episode no matter the reward.  With
        # RM_TUNNEL_GOAL_X the tunnel goal is pulled in for TRAINING only; evaluations keep the
        # delivered goal (they run without the variable), so the gate stays honest.
        goal_override = float(os.environ.get("RM_TUNNEL_GOAL_X", "0") or 0.0)
        if goal_override > 0.0:
            for i, route in enumerate(rc.routes):
                if route["kind"] == "tunnel_cross":
                    sign = 1.0 if rc.goals[i, 0] > rc.starts[i, 0] else -1.0
                    if abs(rc.goals[i, 0]) > goal_override:
                        rc.goals[i, 0] = sign * goal_override
        # audit P0-2 ("each task gets a sane speed range"): the delivered rough road samples
        # 0.3-2.0 m/s, and the measured washboard is +-35 mm over ~1.2 m (max slope ~10 deg) --
        # the terrain stage kept losing episodes to bad_orientation there.  RM_ROUGH_SPEED_MAX
        # caps that route's sampled speed so the traversing skill can be learned before speed.
        rough_cap = float(os.environ.get("RM_ROUGH_SPEED_MAX", "0") or 0.0)
        if rough_cap > 0.0:
            for i, route in enumerate(rc.routes):
                if route["kind"] == "rough_cross":
                    rc.speeds[i, 1] = min(float(rc.speeds[i, 1]), rough_cap)
        # Specialist bootstraps need deterministic, physically useful approach speeds.  These
        # knobs change only the route command sampler; the full-route acceptance evaluator can
        # leave them unset and retain the delivered speed ranges.
        for kind, prefix in (("run", "RM_RUN_SPEED"),
                             ("tunnel_cross", "RM_TUNNEL_SPEED"),
                             ("fly_jump", "RM_FLY_SPEED")):
            lo_s = os.environ.get(prefix + "_MIN", "").strip()
            hi_s = os.environ.get(prefix + "_MAX", "").strip()
            if not (lo_s or hi_s):
                continue
            for i, route in enumerate(rc.routes):
                if route["kind"] != kind:
                    continue
                lo = float(lo_s) if lo_s else float(rc.speeds[i, 0])
                hi = float(hi_s) if hi_s else float(rc.speeds[i, 1])
                if hi < lo:
                    raise ValueError("%s speed range is inverted: %.3f..%.3f" % (kind, lo, hi))
                rc.speeds[i, 0], rc.speeds[i, 1] = lo, hi
        env._mod4_routes = rc
        env._mod4_route_ready = False
    return rc


def route_filter(env, rc):
    """[K] long tensor of the route indices allowed by RM_ROUTE_KINDS (False = no filtering)."""
    global _ROUTE_FILTER
    if _ROUTE_FILTER is None:
        kinds = os.environ.get("RM_ROUTE_KINDS", "").strip()
        if kinds:
            keep = [i for i, r in enumerate(rc.routes) if r["kind"] in kinds.split(",")]
            assert keep, "RM_ROUTE_KINDS matched no route: %s" % kinds
            _ROUTE_FILTER = torch.tensor(keep, dtype=torch.long, device=env.device)
        else:
            _ROUTE_FILTER = False          # sentinel: no filtering
    return _ROUTE_FILTER


def _ids_for(env, rc, env_ids):
    """Route id per env id: stable bucket, restricted to the filter when one is configured."""
    table = route_filter(env, rc)
    # Goal §3: a balanced sampler must not let the two 100%-pass downhill routes dominate.
    # RM_ROUTE_WEIGHTS="run:2,ramp_up:3,ramp_down:1" builds a weighted id sequence ONCE; every env
    # keeps a stable slot in it (the same env keeps the same route across resets).  With no
    # filter the weights apply to the full 15-route table, which is what the mixed stage needs.
    weighted = getattr(env, "_mod4_weight_table", None)
    if weighted is None:
        spec = os.environ.get("RM_ROUTE_WEIGHTS", "").strip()
        seq = []
        if spec:
            kinds = [r["kind"] for r in rc.routes]
            weights = {}
            for item in spec.split(","):
                if ":" in item:
                    k, w = item.split(":")
                    weights[k.strip()] = max(0, int(float(w)))
            allowed = (set(int(v) for v in table.tolist()) if table is not False
                       else set(range(len(rc.routes))))
            for i, kind in enumerate(kinds):
                if i in allowed:
                    seq += [i] * weights.get(kind, 0)
        weighted = (torch.tensor(seq, dtype=torch.long, device=env.device) if seq else table)
        env._mod4_weight_table = weighted
    if weighted is False:
        return torch.remainder(env_ids, len(rc.routes))
    return weighted[torch.remainder(env_ids, weighted.numel())]


def _buffer(env, name, dtype, fill):
    buf = getattr(env, name, None)
    if buf is None or buf.numel() != env.num_envs or buf.dtype != dtype:
        buf = torch.full((env.num_envs,), fill, dtype=dtype, device=env.device)
        setattr(env, name, buf)
    return buf


def _stand_hold_update(stand, finished_before, timer, grounded, tilt_deg,
                       lin_speed, ang_speed, dt, hold_s, tilt_max,
                       speed_max, ang_max):
    """Pure tensor state transition for the continuous standing-success gate."""
    stable = stand & grounded & (tilt_deg <= tilt_max) & (lin_speed <= speed_max) & \
        (ang_speed <= ang_max)
    next_timer = torch.where(stable, timer + dt, torch.zeros_like(timer))
    reached = stand & (next_timer >= hold_s)
    success = reached & ~finished_before
    finished = torch.where(stand, finished_before | reached, finished_before)
    return next_timer, success, finished


def _run_brake_scale(distance, goal_radius: float, brake_distance: float):
    """Brake toward the goal centre, crossing the acceptance sphere at finite speed.

    Zero speed at the sphere boundary made a perfect velocity tracker approach the
    strict distance < radius gate asymptotically. Keep the original brake-zone start,
    but place zero speed at the centre, inside the region that counts as arrival.
    """
    return (distance / max(1.0e-3, float(goal_radius) + float(brake_distance))).clamp(0.0, 1.0)


def _publish_route_identity(env, rc, env_ids, ids) -> None:
    """One identity per environment: route id -> kind -> observation mode bit -> jump flag."""
    import mod4_task

    kinds = [r["kind"] for r in rc.routes]
    env._mod4_route_kinds = kinds
    table = getattr(env, "_mod4_kind_bit_table", None)
    if table is None or table.numel() != len(kinds):
        table = torch.tensor([mod4_task.ROUTE_KIND_BITS.get(k, -1) for k in kinds],
                             dtype=torch.long, device=env.device)
        env._mod4_kind_bit_table = table
        env._mod4_jump_route = torch.tensor([k in JUMP_LIKE_KINDS for k in kinds],
                                            dtype=torch.bool, device=env.device)
        env._mod4_fly_route = torch.tensor([k == "fly_jump" for k in kinds],
                                           dtype=torch.bool, device=env.device)
        env._mod4_route_height = torch.tensor([ROUTE_HEIGHT_CMD.get(k, 0.24) for k in kinds],
                                              dtype=torch.float32, device=env.device)
    _buffer(env, "_mod4_route_ids", torch.long, 0)[env_ids] = ids
    _buffer(env, "_mod4_mode_bit", torch.long, 0)[env_ids] = table[ids]
    _buffer(env, "_mod4_is_jump", torch.bool, False)[env_ids] = env._mod4_jump_route[ids]
    # Keep fly-ramp launch gating separate from an in-place jump.  The old code only published
    # the combined jump mask, so enabling RM_JUMP_LAUNCH_READY accidentally required the
    # in-place jump route to visit the fly-ramp launch platform -- an impossible condition.
    _buffer(env, "_mod4_is_fly", torch.bool, False)[env_ids] = env._mod4_fly_route[ids]
    _buffer(env, "_mod4_jump_target", torch.float32, 0.0)[env_ids] = rc.jump_target[env_ids]
    # mjlab audit P0-2: the height command follows the route, not a uniform 0.18-0.34 sample.
    _publish_height_cmd(env, env_ids, ids)


def _publish_height_cmd(env, env_ids, ids) -> None:
    """Write the route's crouch command into the observation buffer (mjlab audit P0-2)."""
    buf = getattr(env, "_mod4_height_cmd", None)
    if buf is None or buf.numel() != env.num_envs:
        # height_cmd() lazily creates this buffer with a constant 0.24 default; create it here
        # instead so the first observation already carries the route's command.
        buf = torch.full((env.num_envs, 1), 0.24, device=env.device)
        env._mod4_height_cmd = buf
    table = getattr(env, "_mod4_route_height", None)
    if table is not None:
        buf[env_ids] = table[ids].to(buf.dtype).unsqueeze(1)


def _jump_window(env):
    """(lo, hi) of the jump-height curriculum window; created on first use (audit item 7)."""
    rng = getattr(env, "_mod4_jump_range", None)
    if rng is None:
        rng = [float(os.environ.get("RM_JUMP_LO", "0.04")),
               float(os.environ.get("RM_JUMP_HI", "0.09"))]
        env._mod4_jump_range = rng
    return float(rng[0]), float(rng[1])


def _reset_jump(env, env_ids) -> None:
    """Optional hook: skills_isaac owns the jump phase machine (audit item 7)."""
    try:
        import skills_isaac
        skills_isaac.reset_jump_state(env, env_ids)
    except Exception as exc:
        print("[arena] jump state reset failed: %r" % (exc,), flush=True)


def route_spawn(env, env_ids=None) -> None:
    """EventTerm (mode='reset'): put each env on its route (subset given by RM_ROUTE_KINDS).

    The filter runs FIRST and the very same ids go to the spawn, the controller, the mode bits
    and the evaluator's labels.  Filtering only the spawn (the first implementation) left
    RouteCommands.update() commanding the unfiltered routes -- audit item 1.
    """
    robot = env.scene["robot"]
    dev = env.device
    if env_ids is None:
        env_ids = torch.arange(env.num_envs, device=dev)
    env_ids = torch.as_tensor(env_ids, device=dev, dtype=torch.long).flatten()
    rc = route_controller(env)
    ids = _ids_for(env, rc, env_ids)
    rc.ids[env_ids] = ids
    state = rc.reset(env_ids, route_ids=ids)
    # Flat-locomotion training must keep a real zero-command standing population.  Sampling
    # only moving `run` routes lets PPO trade away quiet stand behaviour while improving route
    # progress, which is unacceptable for a RoboMaster chassis that repeatedly waits, aims and
    # starts again on the field.  Resample the role per episode so every physical/randomized
    # instance experiences both behaviours instead of permanently reserving easy stand envs.
    stand = _buffer(env, "_mod4_run_stand", torch.bool, False)
    stand_time = _buffer(env, "_mod4_stand_time", torch.float32, 0.0)
    stand[env_ids] = False
    stand_time[env_ids] = 0.0
    stand_fraction = max(0.0, min(1.0, float(os.environ.get("RM_RUN_STAND_FRACTION", "0"))))
    if stand_fraction > 0.0:
        is_run = torch.tensor([r["kind"] == "run" for r in rc.routes],
                              device=dev, dtype=torch.bool)[ids]
        sample = torch.rand(env_ids.numel(), device=dev, generator=rc.generator)
        stand[env_ids] = is_run & (sample < stand_fraction)
    # RouteCommands.reset() samples slope-spin at only 2..4 rad/s.  The curriculum used to
    # report a growing gyro window without ever changing this command, so high-speed spin was
    # never trained.  Apply the live curriculum magnitude while preserving the sampled sign.
    spin_table = torch.tensor([r["kind"] == "slope_spin" for r in rc.routes], device=dev)
    spin_env = spin_table[ids]
    if bool(spin_env.any()):
        spin_ids = env_ids[spin_env]
        spin_mag = float(getattr(
            env, "_mod4_gyro_window", float(os.environ.get("RM_GYRO_START", "2.0"))))
        spin_sign = torch.sign(rc.spin_speed[spin_ids])
        spin_sign = torch.where(spin_sign == 0, torch.ones_like(spin_sign), spin_sign)
        rc.spin_speed[spin_ids] = spin_sign * spin_mag
    # Distance curriculum for the dog hole (mjlab used the same idea on the field map): the
    # delivered `tunnel` route spawns 0.46 m before the mouth, and the crouched robot only
    # manages ~0.06 m/s, so a full route inside one 20 s episode is tight.  RM_TUNNEL_LEAD_M
    # moves the tunnel spawns toward their goal (0 = the delivered spawn, unchanged) so a stage
    # can start close and push the start line back as the skill appears.
    # Spawn shortening and the pre-crouch trigger are distinct controls.
    lead = float(os.environ.get("RM_TUNNEL_SPAWN_LEAD_M", "0") or 0.0)
    local = rc.starts[ids].clone()
    if lead > 0.0:
        is_tunnel = torch.tensor([r["kind"] == "tunnel_cross" for r in rc.routes],
                                 device=dev)[ids]
        goal = rc.goals[ids]
        d = goal[:, :2] - local[:, :2]
        d = d / d.norm(dim=-1, keepdim=True).clamp(min=1e-6)
        # An upright reset must remain fully in front of the roof.  The old 0.35 m bootstrap
        # put the root at x=0.65 m; spawn_footprint_floor then saw the roof under the chassis,
        # lifted the robot onto the highway, and every tunnel episode overturned after 0.29 s.
        # spawn_footprint_floor samples +/-0.30 m, so keep its forward ray 20 mm before the
        # measured x=0.760 roof edge.
        safe_u = float(os.environ.get("RM_TUNNEL_SPAWN_SAFE_U", "0.44"))
        start_u = (local[:, 0] * torch.sign(goal[:, 0] - rc.starts[ids, 0])).abs()
        safe_lead = torch.clamp(torch.full_like(start_u, lead),
                                max=torch.clamp(torch.full_like(start_u, safe_u) - start_u,
                                                min=0.0))
        shift = d * safe_lead.unsqueeze(-1)
        local[:, :2] = local[:, :2] + torch.where(is_tunnel.unsqueeze(-1), shift,
                                                  torch.zeros_like(shift))
        state[:, :2] = env.scene.env_origins[env_ids, :2] + local[:, :2]
    # Bootstrap fly-jump near the launch region.  The original start is 2.2 m before the
    # reward latch, and the specialist policy consistently stopped 0.7 m short.  This knob
    # shortens only training; acceptance leaves it at zero and keeps the full CAD route.
    fly_lead = float(os.environ.get("RM_FLY_SPAWN_LEAD_M", "0") or 0.0)
    if fly_lead > 0.0:
        is_fly = torch.tensor([r["kind"] == "fly_jump" for r in rc.routes],
                              device=dev)[ids]
        goal = rc.goals[ids]
        d = goal[:, :2] - local[:, :2]
        d = d / d.norm(dim=-1, keepdim=True).clamp(min=1e-6)
        shift = d * fly_lead
        local[:, :2] = local[:, :2] + torch.where(is_fly.unsqueeze(-1), shift,
                                                  torch.zeros_like(shift))
        state[:, :2] = env.scene.env_origins[env_ids, :2] + local[:, :2]
    # Measured 2026-09-11 21:55 (probe_terrain_spawn.py): both `ramp_up` spawns put the chassis
    # INTO the ramp geometry -- 2830 N / 3421 N chassis contact on the very first step, which
    # tripped the 2 mm closed-chain guard and ended the episode in 1-2 control steps (the terrain
    # stage showed closure 0.25 / base_contact 0.257).  A larger clearance alone was not enough
    # (the `trapezoid` route still overlapped at 145 746 N), because the route table records ONE
    # ground sample per spawn while the chassis is half a metre long.  Put the robot on the
    # HIGHEST surface under its footprint, then add a small settle clearance.
    clearance = float(os.environ.get("RM_SPAWN_CLEARANCE_M", "0.02"))
    try:
        import mod4_task
        floor = mod4_task.spawn_footprint_floor(env, env_ids, local)
        state[:, 2] = floor + float(rc.base_height) + clearance
    except Exception as exc:
        print("[arena] footprint spawn failed: %r" % (exc,), flush=True)
        state[:, 2] = state[:, 2] + clearance
    # Spawn-distance curricula move the state after RouteCommands.reset() initialized
    # last_dist from the delivered start.  Without recomputing it, the first policy step got a
    # free 0.35/1.80 m progress spike (hundreds of reward units) that had no action cause.
    rc.last_dist[env_ids] = torch.linalg.vector_norm(rc.goals[ids, :2] - local[:, :2], dim=-1)
    # RouteCommands.reset() does not know about the footprint-floor correction above.
    # Capture the actual local root height so jump completion and episode diagnostics share
    # the same absolute reference and cannot count driving onto higher terrain as a jump.
    if hasattr(rc, "jump_start_z"):
        spawn_root_z = state[:, 2] - env.scene.env_origins[env_ids, 2]
        rc.jump_start_z[env_ids] = spawn_root_z
        rc.peak_z[env_ids] = spawn_root_z
    # audit item 7: the package samples jump_target = 0.08..0.35 m, which is above what this
    # plant can reach.  Draw from our own window; jump_target_schedule() opens it once hops
    # start landing inside the window.
    lo, hi = _jump_window(env)
    rc.jump_target[env_ids] = lo + (hi - lo) * torch.rand(env_ids.numel(), device=dev)
    # The package hands back quat as (w, x, y, z); Isaac Lab wants (x, y, z, w).  Passing it
    # through unchanged spawned every robot at 90-180 deg of tilt -- the "1.02-step episodes"
    # the first arena run showed.  Reorder instead of trusting the two conventions to match.
    pose_xyzw = torch.cat([state[:, :3], state[:, [4, 5, 6, 3]]], dim=-1)
    robot.write_root_pose_to_sim(pose_xyzw, env_ids=env_ids)
    robot.write_root_velocity_to_sim(state[:, 7:13], env_ids=env_ids)
    if not getattr(env, "_mod4_arena_friction_done", False):
        # 2026-09-11 traction probe: the delivered arena's collision material is far
        # slipperier than the 0.9/0.9 the robot trained on -- wheels spun at 16 rad/s while
        # the chassis advanced 0.02 m/s.  Match the field's tyre friction once per process.
        try:
            import mod4_task
            mod4_task.set_arena_friction(env)
        except Exception as exc:
            print("[arena] friction patch failed: %r" % (exc,), flush=True)
        env._mod4_arena_friction_done = True
    _gf = os.environ.get("RM_GUIDE_FRICTION", "")
    if _gf:
        _apply_guide_friction(env)
    _publish_route_identity(env, rc, env_ids, ids)
    _reset_jump(env, env_ids)
    env._mod4_route_ready = True


def _apply_guide_friction(env) -> None:
    """Idempotent, retried version of the guide-roller friction fix (goal 2).

    Measured 2026-09-12 18:31 (docs/probe_inertia_fric002.log): the original one-shot ran before
    the robot prims existed, matched 0 materials and marked itself done, so RM_GUIDE_FRICTION had
    no effect at all.  This runs again from the per-step route event until the roller materials
    are really there, and only then stops.
    """
    if getattr(env, "_mod4_guide_friction_done", False):
        return
    gf = os.environ.get("RM_GUIDE_FRICTION", "")
    if not gf:
        return
    tries = getattr(env, "_mod4_guide_tries", 0)
    env._mod4_guide_tries = tries + 1
    if tries % 25 != 0:                      # throttled: the robot may not exist for 1-2 steps
        return
    try:
        import mod4_task
        mod4_task.set_guide_roller_friction(env, friction=float(gf))
        if getattr(env, "_mod4_guide_materials", 0) <= 0:
            return                           # prims not in the stage yet -- keep retrying
        _tm = os.environ.get("RM_TIRE_ADD_MM", "")
        if _tm:
            mod4_task.set_tyre_deflection(env, add_m=float(_tm) / 1000.0)
    except Exception as exc:
        print("[guide] roller friction patch failed: %r" % (exc,), flush=True)
        return
    print("[guide] guide-roller friction applied after %d step-event tries" % (tries + 1,),
          flush=True)
    env._mod4_guide_friction_done = True


def route_commands(env, env_ids=None) -> None:
    """EventTerm (mode='step'): route velocity command + progress/success bookkeeping."""
    _apply_guide_friction(env)      # 2026-09-12: retried here, the prims exist by now
    if not getattr(env, "_mod4_route_ready", False):
        return
    rc = route_controller(env)
    robot = env.scene["robot"]
    f = env.scene.sensors["wheel_contact"].data.net_forces_w
    if hasattr(f, "torch"):
        f = f.torch
    grounded = f.norm(dim=-1).max(dim=1).values > 1.0
    g = robot.data.projected_gravity_b
    tilt = torch.rad2deg(torch.acos((-g[:, 2]).clamp(-1.0, 1.0)))
    quat = robot.data.root_quat_w                      # (x, y, z, w)
    yaw = torch.atan2(2.0 * (quat[:, 3] * quat[:, 2] + quat[:, 0] * quat[:, 1]),
                      1.0 - 2.0 * (quat[:, 1] ** 2 + quat[:, 2] ** 2))
    stand = getattr(env, "_mod4_run_stand", None)
    if stand is None:
        stand = torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
    # Remember the latch before RouteCommands.update(): stand success is defined by a
    # continuous stability hold, never by accidentally drifting to the run-route waypoint.
    finished_before_all = rc.finished.clone()
    stand_finished_before = finished_before_all & stand
    out = rc.update(robot.data.root_pos_w, yaw, robot.data.root_ang_vel_b[:, 2],
                    grounded, (tilt < 60.0), env.step_dt)
    # RouteCommands.update() returns a dict: {"command": [N,3], "progress_reward": ...,
    # "success": ..., ...}.
    cmd = out["command"] if isinstance(out, dict) else out
    progress = {k: v for k, v in out.items() if k != "command"} if isinstance(out, dict) else {}
    # A finite route with an immediate terminal bonus otherwise rewards an overspeeding policy
    # for reaching the 0.35 m goal sphere early.  v6 completed 99.77% of nominal run episodes
    # while moving at 2.12 m/s against 0.3--1.2 m/s commands.  When explicitly enabled, taper
    # the flat-run command through a braking zone and accept completion only after the chassis
    # is slow, upright and settled on a driven wheel.  Other routes and legacy runs are byte-for-
    # byte unchanged because the switch defaults off.
    if os.environ.get("RM_RUN_BRAKE_GATE", "0").strip() == "1":
        run_table = torch.tensor([r["kind"] == "run" for r in rc.routes], device=env.device)
        moving_run = run_table[rc.ids] & ~stand
        # Keep this branch host-static.  Synchronizing moving_run.any() every control step
        # previously destabilized the replicated PhysX contact view at large env counts.
        if moving_run is not None:
            local_pos = robot.data.root_pos_w - env.scene.env_origins
            delta = rc.goals[rc.ids, :2] - local_pos[:, :2]
            distance = torch.linalg.vector_norm(delta, dim=1)
            heading = torch.atan2(delta[:, 1], delta[:, 0])
            heading_error = torch.atan2(torch.sin(heading - yaw), torch.cos(heading - yaw))
            goal_radius = float(os.environ.get("RM_RUN_GOAL_RADIUS_M", "0.35"))
            brake_distance = max(1.0e-3, float(os.environ.get("RM_RUN_BRAKE_DIST_M", "0.90")))
            brake_scale = _run_brake_scale(distance, goal_radius, brake_distance)
            target_speed = rc.speed * brake_scale
            cmd[:, 0] = torch.where(
                moving_run, target_speed * torch.clamp(torch.cos(heading_error), 0.0, 1.0),
                cmd[:, 0])
            cmd[:, 2] = torch.where(
                moving_run, torch.clamp(2.0 * heading_error, -2.0, 2.0), cmd[:, 2])

            lin_speed = torch.linalg.vector_norm(robot.data.root_lin_vel_b[:, :2], dim=1)
            ang_xy = torch.linalg.vector_norm(robot.data.root_ang_vel_b[:, :2], dim=1)
            stop_speed = float(os.environ.get("RM_RUN_STOP_SPEED_M_S", "0.30"))
            stop_tilt = float(os.environ.get("RM_RUN_STOP_TILT_DEG", "8.0"))
            stop_ang = float(os.environ.get("RM_RUN_STOP_ANG_XY_RAD_S", "1.50"))
            newly_finished = rc.finished & ~finished_before_all
            accepted = moving_run & newly_finished & grounded & (lin_speed <= stop_speed) & \
                (tilt <= stop_tilt) & (ang_xy <= stop_ang)
            rc.finished[:] = torch.where(
                moving_run, finished_before_all | accepted, rc.finished)
            if "success" in progress:
                progress["success"][:] = torch.where(
                    moving_run, accepted & ~finished_before_all, progress["success"])
            if "completed" in progress:
                progress["completed"][:] = torch.where(
                    moving_run, rc.finished, progress["completed"])
            # RouteCommands zeroed a rejected command when it first entered the goal sphere.
            # Restore the tapered command until the physical stop gate is honestly met.
            cmd[:] = torch.where(rc.finished.unsqueeze(1), torch.zeros_like(cmd), cmd)
    # A standing episode is successful only after remaining quiet and upright continuously.
    # These are physical-state gates, not reward proxies, so route_complete can terminate it as
    # an honest success and the reported completion rate is not diluted by deliberate stands.
    if float(os.environ.get("RM_RUN_STAND_FRACTION", "0")) > 0.0:
        hold_s = max(float(env.step_dt), float(os.environ.get("RM_STAND_HOLD_S", "3.0")))
        tilt_max = float(os.environ.get("RM_STAND_TILT_DEG", "8.0"))
        speed_max = float(os.environ.get("RM_STAND_SPEED_M_S", "0.12"))
        ang_max = float(os.environ.get("RM_STAND_ANG_VEL_RAD_S", "0.45"))
        lin_xy = torch.linalg.vector_norm(robot.data.root_lin_vel_b[:, :2], dim=1)
        ang_xyz = torch.linalg.vector_norm(robot.data.root_ang_vel_b, dim=1)
        timer = getattr(env, "_mod4_stand_time", None)
        if timer is None:
            timer = torch.zeros(env.num_envs, device=env.device)
            env._mod4_stand_time = timer
        next_timer, stand_success, stand_finished = _stand_hold_update(
            stand, stand_finished_before, timer, grounded, tilt, lin_xy, ang_xyz,
            float(env.step_dt), hold_s, tilt_max, speed_max, ang_max)
        timer.copy_(next_timer)
        rc.finished[:] = torch.where(stand, stand_finished, rc.finished)
        cmd[:] = torch.where(stand.unsqueeze(1), torch.zeros_like(cmd), cmd)
        if "progress_reward" in progress:
            progress["progress_reward"][:] = torch.where(
                stand, torch.zeros_like(progress["progress_reward"]), progress["progress_reward"])
        if "success" in progress:
            progress["success"][:] = torch.where(stand, stand_success, progress["success"])
        if "completed" in progress:
            progress["completed"][:] = torch.where(stand, rc.finished, progress["completed"])
    term = env.command_manager.get_term("twist")
    # v2 fix (2026-09-13, §36.2): deliberately NO per-step command scaling here.  Every form of it
    # (torch.tensor(list) per step, then clone) either allocated or launched a CUDA kernel inside a
    # step event and broke the PhysX contact view once the curriculum was enabled.  The curriculum
    # now scales the route controller's SPEED TABLE on the host instead -- see
    # mod4_curriculum._apply_speeds_to_routes.  This function is back to its original form.
    # v2 fix (2026-09-13): write the scaled vx STRAIGHT into the destination with `out=`.
    # Every earlier form allocated or launched a kernel per control step (torch.tensor(list),
    # torch.cat, then cmd.clone()) and each one kept the CUDA device-side assert alive while the
    # curriculum was enabled.  `torch.mul(..., out=dest)` does neither.
    term.command[:, 0] = cmd[:, 0]
    term.command[:, 1] = cmd[:, 1]
    term.command[:, 2] = cmd[:, 2]
    if hasattr(term, "time_left"):
        term.time_left[:] = 1.0e9
    if hasattr(term, "is_standing_env"):
        term.is_standing_env[:] = stand
    # v2 item 4: narrow/widen the FORWARD speed command with the route's difficulty level.
    # Reads the table the curriculum publishes; absent -> exact old behaviour.
    # ONLY channel 0 (vx) is scaled.  The first version multiplied all three channels, which
    # also scaled the yaw command: a spin route at level 0 would have had to cover 2*pi in
    # 1.67x the time, i.e. the curriculum could have broken the one subject that passes
    # (measured 2026-09-13: slope_spin 0.703 against a 0.60 bar).  The curriculum is a
    # SPEED curriculum for translation routes; the spin keeps its own difficulty settings.
    env._mod4_route_progress = progress


def bucket_by_route(kinds, ids, done_route, prog_route, failed, extra_sum=None, extra_max=None):
    """Per-route-kind acceptance buckets -- pure python, no torch, no Isaac (audit item 9).

    ``kinds`` is the package's route-kind list, ``ids`` the per-env route index published by
    ``_publish_route_identity``.  The trainer, this helper and the evaluator all read that one
    id tensor, which is what stops a per-route report from labelling a tunnel route "run"
    (audit item 1: the ids used to be filtered for the spawn but not for the controller).

    ``extra_sum`` / ``extra_max`` carry the per-terrain detail the audit asked for (attempts,
    entries, landings, air time, spin angle, and the count of each termination term per kind).
    """
    names = [kinds[int(i)] for i in ids]
    out = {}
    for kind in sorted(set(names)):
        m = [i for i, v in enumerate(names) if v == kind]
        done = sum(1 for i in m if bool(done_route[i]))
        rec = {
            "envs": len(m),
            "completed": done,
            "complete_rate": round(done / max(1, len(m)), 3),
            "progress_sum": round(sum(float(prog_route[i]) for i in m), 3),
            "failed": sum(1 for i in m if bool(failed[i])),
        }
        for key, arr in (extra_sum or {}).items():
            rec[key] = round(sum(float(arr[i]) for i in m), 4)
        for key, arr in (extra_max or {}).items():
            rec[key] = round(max(float(arr[i]) for i in m), 4)
        out[kind] = rec
    return out
