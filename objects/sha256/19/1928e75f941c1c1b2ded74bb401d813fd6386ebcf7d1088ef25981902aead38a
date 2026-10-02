"""v2 item 4, path B: per-route difficulty levels driven by the measured success rate.

Why path B
----------
The user's spec was a *terrain* curriculum ("hole 350 -> 250 mm, step height, slope, jump
height").  That needs geometry we do not have a generator for: the 15 routes come from the
delivered package (`data/routes.json` + `assets/arena_collision.usdc`, a CAD-derived binary),
`build_layout.py` only *places references* to that prototype, and the CAD source
(`RMUC2026_V2.0.0.stp`) is not in the tree.  So path B varies the TASK (speed window, pre-crouch
lead, goal distance, episode budget) instead of the geometry, and path A (procedurally rebuilding
the 15 routes) stays a separate, larger job.

What the reference actually does (do NOT copy blindly)
-----------------------------------------------------
`refs/fudan_src/fudan_rl_wheel_leg-main` promotes on **distance walked** (`> terrain_length/4`
= 2.0 m from the tile origin), not on a success rate; its reward-based demotion guard is
numerically inert; and the "0.7 threshold" the user remembered belongs to a *different*
mechanism -- the command-range curriculum (`legged_robot.py:894-951`).  Two things are worth
copying from it and they are both here:
  * **windowed** statistics, never cumulative counters (their own audit found "100 000 attempts,
    0 reached" hidden behind cumulative sums);
  * a rate-based promote gate with a hysteresis band, plus a demote path.
What is deliberately different: the promotion signal is OUR per-route success flag, because for
ramps/steps "walked far" is not the same as "completed the route".

Two entry points
----------------
* `accumulate_route_stats(env)` -- call from a **step event** (every control step).  A curriculum
  term is only evaluated on environment reset, so counters incremented there would advance at the
  reset rate (~4 calls/iteration, a trap documented in `gyro_window_schedule`).
* `route_difficulty_schedule(env, env_ids=None)` -- the `CurriculumTerm` itself.  It derives the
  iteration from `env.common_step_counter`, closes a window every `RM_CURR_WINDOW_STEPS`, and
  promotes/demotes each route kind independently.

State it publishes on the env (consumers read these, with a fallback to the old constants):
    env._mod4_route_level       list[int]   current level per route kind
    env._mod4_route_speed_scale list[float] speed-window multiplier per route kind
    env._mod4_route_lead_m      list[float] pre-crouch lead per route kind (tunnel only)
"""

from __future__ import annotations

LENGTH_LIMITED_KINDS = ("tunnel_cross",)
import os

# Order must match route_isaac's route-kind table (the ids published by _publish_route_identity).
ROUTE_KINDS = ("run", "ramp_up", "ramp_down", "step_up", "step_down",
               "rough_cross", "slope_spin", "fly_jump", "jump_in_place", "tunnel_cross")
K = len(ROUTE_KINDS)


def _f(name, default):
    try:
        return float(os.environ.get(name, str(default)))
    except (TypeError, ValueError):
        return float(default)


def _state(env):
    st = getattr(env, "_mod4_route_curr", None)
    if st is None:
        # START AT THE TOP, not at the bottom.  The first version started every kind at level 0,
        # i.e. speed_scale 0.60 on every route -- including the ones that already pass.  Measured
        # 2026-09-13: slope_spin passes at 0.703 (bar 0.60) with a spin that has to cover 2*pi in
        # one episode; scaling its command to 0.60 would need 1.67x the time and could push it back
        # under the bar.  Starting at the maximum level makes enabling the curriculum a NO-OP for
        # everything that works today, and the demote path (rate < RM_CURR_DEMOTE) then eases only
        # the routes that actually fail -- which is the whole point of the v2 change set.
        _levels = max(1, int(_f("RM_CURR_LEVELS", 5)))
        _init = int(_f("RM_CURR_INIT_LEVEL", _levels - 1))
        _init = min(max(_init, 0), _levels - 1)
        st = {
            "attempts": [0.0] * K,      # running window
            "successes": [0.0] * K,
            "last_rate": [float("nan")] * K,
            "windows": 0,
            "level": [_init] * K,
        }
        env._mod4_route_curr = st
        env._mod4_route_level = st["level"]
        # Publish immediately so the consumers see the initial level from step 0 instead of only
        # after the first window closes.  With the default init level (maximum) the published
        # scale is 1.0, so this is numerically a no-op -- but it makes the initial state explicit
        # and testable, and it means RM_CURR_INIT_LEVEL=0 really does ease from the very first step.
        env._mod4_route_speed_scale = [_level_to_speed_scale(l) for l in st["level"]]
        env._mod4_route_lead_m = [_level_to_lead_m(l) for l in st["level"]]
    return st


def _level_to_speed_scale(level: int) -> float:
    """Easier level = narrower speed window.  level 0 starts at the low end."""
    lo = _f("RM_CURR_SPEED_SCALE_MIN", 0.6)
    hi = _f("RM_CURR_SPEED_SCALE_MAX", 1.0)
    levels = max(1, int(_f("RM_CURR_LEVELS", 5)))
    frac = min(max(level, 0), levels - 1) / float(levels - 1)
    return lo + (hi - lo) * frac


def _level_to_lead_m(level: int) -> float:
    """Tunnel pre-crouch lead: harder level = shorter lead (squat later, keep momentum)."""
    lo = _f("RM_CURR_LEAD_MIN_M", 0.18)
    hi = _f("RM_CURR_LEAD_MAX_M", 0.40)
    levels = max(1, int(_f("RM_CURR_LEVELS", 5)))
    frac = min(max(level, 0), levels - 1) / float(levels - 1)
    return hi + (lo - hi) * frac


def _publish(env, st):
    env._mod4_route_level = st["level"]
    env._mod4_route_speed_scale = [_level_to_speed_scale(l) for l in st["level"]]
    env._mod4_route_lead_m = [_level_to_lead_m(l) for l in st["level"]]
    # v2 fix (2026-09-13, §36.2): do NOT publish a CUDA tensor and do NOT scale the per-step
    # command.  Bisection showed the failure lands exactly on the FIRST WINDOW CLOSE
    # (12 iterations x 24 steps = 288 ~= RM_CURR_WINDOW_STEPS 300) and that every CUDA operation
    # performed inside an event/CurrTerm -- allocation or sync -- breaks the PhysX contact view.
    # So the scaling is applied HOST-SIDE to the route controller's speed table instead (see
    # _apply_speeds_to_routes below), exactly like the proven RM_ROUGH_SPEED_MAX path.
    env._mod4_route_speed_scale_t = None


def accumulate_route_stats(env, env_ids=None):
    """Called AFTER termination/reward, BEFORE reset: count completed episodes by kind."""
    import torch
    from repair_contracts import episode_counts
    rc = getattr(env, "_mod4_routes", None)
    if rc is None:
        raise RuntimeError("route curriculum needs route controller")
    attempts, successes = episode_counts(
        rc.ids, [r["kind"] for r in rc.routes], list(ROUTE_KINDS),
        env.reset_buf, rc.finished, env.reset_terminated)
    # ``episode_counts`` may return integer attempts and floating-point successes.
    # Accumulate both in float32 so PyTorch never rejects an in-place add at the
    # first completed episode (the former zeros_like(attempts) made successes Long).
    attempts = attempts.to(dtype=torch.float32)
    successes = successes.to(dtype=torch.float32)
    # Always retain exact terminal-event totals for the live monitor.  Route success is a
    # one-control-step pulse, so a 20 s polling thread cannot observe it reliably.  These
    # device counters are updated before reset and synchronized only when the monitor writes.
    live = getattr(env, "_mod4_live_route_stats", None)
    if live is None:
        live = env._mod4_live_route_stats = {
            "attempts": torch.zeros(len(ROUTE_KINDS), dtype=torch.float32,
                                    device=attempts.device),
            "successes": torch.zeros(len(ROUTE_KINDS), dtype=torch.float32,
                                     device=attempts.device),
        }
    live["attempts"] += attempts
    live["successes"] += successes
    if os.environ.get("RM_ROUTE_CURRICULUM", "0").strip() != "1":
        return
    st = _state(env)
    for key, value in (("attempts", attempts), ("successes", successes)):
        prior = st[key]
        if not isinstance(prior, torch.Tensor):
            prior = torch.as_tensor(prior, dtype=value.dtype, device=value.device)
        st[key] = prior + value


def route_difficulty_schedule(env, env_ids=None) -> dict:
    """CurriculumTerm: promote a route kind when its windowed success rate clears the gate."""
    if os.environ.get("RM_ROUTE_CURRICULUM", "0").strip() != "1":
        return {}
    st = _state(env)
    steps_per_iter = max(1.0, _f("RM_GYRO_STEPS_PER_ITER", 24.0))
    window = max(1, int(_f("RM_CURR_WINDOW_STEPS", 4000)))
    counter = int(getattr(env, "common_step_counter", 0) or 0)
    # Only act when a whole window has elapsed; the counter (not the call count) is the clock,
    # so the reset pattern cannot change the schedule.
    done = counter // window
    if done <= st["windows"]:
        out = {"Curriculum/route_curriculum/level_%s" % k: float(v)
               for k, v in zip(ROUTE_KINDS, st["level"])}
        return out
    st["windows"] = done

    up = _f("RM_CURR_PROMOTE", 0.7)         # the user's "success rate > 0.7"
    down = _f("RM_CURR_DEMOTE", 0.3)        # hysteresis: only drop below this
    min_att = _f("RM_CURR_MIN_ATTEMPTS", 40.0)
    levels = max(1, int(_f("RM_CURR_LEVELS", 5)))
    out = {}
    # ONE sync per WINDOW (not per step): convert the vectorised device counters back to python
    # scalars here, then reset them.  This is the only GPU->CPU transfer in the whole module.
    import torch as _torch
    if isinstance(st["attempts"], _torch.Tensor):
        att_list = st["attempts"].detach().to("cpu").tolist()
        suc_list = st["successes"].detach().to("cpu").tolist()
        st["attempts"] = [0.0] * K
        st["successes"] = [0.0] * K
    else:
        att_list, suc_list = list(st["attempts"]), list(st["successes"])
    for k in range(K):
        att, suc = att_list[k], suc_list[k]
        rate = (suc / att) if att > 0 else float("nan")
        st["last_rate"][k] = rate
        if att >= min_att:
            if rate > up:
                st["level"][k] = min(st["level"][k] + 1, levels - 1)
            elif rate < down:
                st["level"][k] = max(st["level"][k] - 1, 0)
        st["attempts"][k] = 0.0
        st["successes"][k] = 0.0
        name = ROUTE_KINDS[k]
        out["Curriculum/route_curriculum/level_%s" % name] = float(st["level"][k])
        if att > 0:
            out["Curriculum/route_curriculum/rate_%s" % name] = float(rate)
            out["Curriculum/route_curriculum/attempts_%s" % name] = float(att)
    _publish(env, st)
    # §36.2: apply the new levels to the route controller's speed table (host-side, once per
    # window).  No per-step work is done anywhere in the curriculum path.
    _apply_speeds_to_routes(env)
    out["Curriculum/route_curriculum/windows"] = float(st["windows"])
    return out


def _apply_speeds_to_routes(env) -> None:
    """Scale the route controller's SPEED TABLE from the current levels (host-side, once).

    This is the §36.2 fix.  The original design scaled the per-step command inside a step event,
    which put CUDA work (tensor build / clone) between PhysX kernels and killed the run at the
    first window close.  `route_isaac.route_controller()` already supports exactly this kind of
    static speed cap for the rough route (`RM_ROUGH_SPEED_MAX` does
    `rc.speeds[i, 1] = min(...)` at construction), so the curriculum now does the same thing for
    every kind whenever a level changes -- same mechanism, same cost class, no per-step work.
    """
    if os.environ.get("RM_ROUTE_CURRICULUM", "0").strip() != "1":
        return
    try:
        from route_isaac import route_controller
        rc = route_controller(env)
    except Exception:
        return
    st = getattr(env, "_mod4_route_curr", None)
    if st is None:
        return
    scale = [_level_to_speed_scale(l) for l in st["level"]]
    # audit 46: for a LENGTH/TIME-limited route, lowering the speed makes completion strictly
    # harder (2.0 m at 0.05 m/s needs 40 s).  Never scale such a kind below 1.0 -- its level
    # may still move the other dimensions, but the speed must not push the goal further away.
    # Measured: tunnel_cross demoted 4->3->2 while route_success stayed 0.0.
    for _k in LENGTH_LIMITED_KINDS:
        _i = ROUTE_KINDS.index(_k) if _k in ROUTE_KINDS else None
        if _i is not None and scale[_i] < 1.0:
            scale[_i] = 1.0
    base = getattr(env, "_mod4_route_speed_base", None)
    if base is None:
        # remember the delivered upper bound once, so repeated level changes do not compound
        try:
            base = rc.speeds[:, 1].detach().clone()
        except Exception:
            base = [float(rc.speeds[i, 1]) for i in range(len(rc.routes))]
        env._mod4_route_speed_base = base
    for i, route in enumerate(rc.routes):
        k = ROUTE_KINDS.index(route["kind"]) if route["kind"] in ROUTE_KINDS else None
        if k is None:
            continue
        try:
            rc.speeds[i, 1] = base[i] * scale[k]
        except Exception:
            return


def route_param(env, kind: str, what: str, fallback):
    """Consumer helper: read a per-kind difficulty parameter, falling back to the old constant.

    `what` is "speed_scale" or "lead_m".  When the curriculum is off (or the kind is unknown)
    this returns `fallback`, so the patched consumers behave exactly as before.
    """
    if os.environ.get("RM_ROUTE_CURRICULUM", "0").strip() != "1":
        return fallback
    try:
        k = ROUTE_KINDS.index(kind)
        table = getattr(env, "_mod4_route_%s" % what, None)
        if table is None:
            return fallback
        return float(table[k])
    except (ValueError, IndexError, TypeError):
        return fallback
