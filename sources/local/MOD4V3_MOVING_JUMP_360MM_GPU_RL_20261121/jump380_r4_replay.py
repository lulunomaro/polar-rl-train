"""Fixed-wall, 400 Hz CPU replays of the deployed neural policy."""
from dataclasses import dataclass
import math
from statistics import mean

import numpy as np

from eval_moving_jump_360mm import edge_margin, main_flight_bounds
from jump360_scene import CLOSURE_LIMIT, DT
from jump380_r4_scene import HEIGHTS, KINDS, LENGTHS, PLATFORMS


@dataclass(frozen=True)
class Trial:
    seed: int
    speed: float
    height: float
    dr: float
    kind: str = "flat"
    lead: float = .55
    press_tick: int = 137
    hold_ticks: int = 38
    wall_at: float | None = None


def run_trial(plant, policy, trial, video=None):
    rng = np.random.default_rng(trial.seed)
    y, yaw = rng.uniform(-.012, .012), rng.uniform(-.010, .010)
    plant.rng = np.random.default_rng(trial.seed + 94887)
    plant.setup(trial.height, trial.dr, (0., float(y), float(yaw)))
    policy.reset_history()
    trace = []
    edge = math.inf
    obstacle = trial.kind != "flat"
    if obstacle:
        edge = trial.wall_at if trial.wall_at is not None else trial.speed * 1.6 + trial.lead
        plant.wall(trial.kind, edge)
    command = 0.
    press = played_ticks = None
    key_ticks = 0
    for tick in range(400):
        x = float(plant.d.qpos[0])
        if press is None and tick >= 59:
            at_press = x >= edge - trial.lead - 1.e-9 if obstacle else tick >= trial.press_tick
            if at_press:
                press, played_ticks = plant.frame(), tick
        command += ((trial.speed if tick >= 30 else 0.) - command) / 12.
        key = press is not None and tick - played_ticks < trial.hold_ticks
        observation = plant.command(command, trial.height, key)
        key_ticks += bool(observation[30])
        action = policy(plant, observation)
        plant.advance(action, trace.append if press is not None else None)
        if video is not None and tick % 2 == 1:
            video.frame(plant, key, command, trace)
        if plant.tilt_fault or not np.isfinite(plant.d.qpos).all():
            break
        if played_ticks is not None and tick - played_ticks >= 124:
            break
        if press is None and tick >= 299:
            break
    if press is None:
        press = plant.frame()
    return measure(plant, trial, trace, press, played_ticks, key_ticks, edge), trace


def measure(plant, trial, trace, press, pressed, key_ticks, edge):
    obstacle_id = KINDS.index(trial.kind)
    platform = trial.kind in PLATFORMS
    wall_height = HEIGHTS[obstacle_id]
    end_edge = edge if platform else edge + LENGTHS[obstacle_id]
    begin, end = main_flight_bounds(trace)
    flight, recovery = trace[begin:end], trace[end:] if end else []
    charge = trace[:begin + 1] if flight else trace[:240]
    apex = max(flight, key=lambda f: f.lowest, default=None)
    tail = recovery[-120:]
    top = [f for f in recovery if min(f.wheel_top_force) > 1.]
    proper_contact = lambda f: (
        min(f.wheel_top_force) > 1. and f.tire_low > wall_height - .015
        if platform else min(f.wheel_up_force) > 1. and f.tire_low < .020)
    supported = [
        proper_contact(f) and (not obstacle_id or f.min_x > end_edge)
        and f.vx > .25 * trial.speed and abs(f.pitch) < 18. and abs(f.roll) < 18.
        for f in recovery
    ]
    longest = consecutive = 0
    for sample in supported:
        consecutive = consecutive + 1 if sample else 0
        longest = max(longest, consecutive)
    fall = bool(plant.tilt_fault or not np.isfinite(plant.d.qpos).all())
    tail_vx = mean(f.vx for f in tail) if len(tail) == 120 else None
    stable = bool(not fall and tail_vx is not None and sum(supported[-120:]) >= 72
                  and tail_vx > .35 * trial.speed)
    peak = apex.lowest if apex else 0.
    pitch = max((abs(f.pitch) for f in flight), default=0.)
    minimum_vx = min((f.vx for f in charge), default=press.vx)
    charge_retreat = min((f.x - press.x for f in charge), default=0.)
    forward = bool(pressed is not None and press.vx > 0. and minimum_vx > 0. and charge_retreat >= -1.e-6)
    scrape = max((f.scrape_force for f in charge), default=0.)
    face = max([plant.approach_face, *(f.face_force for f in trace)])
    impact = max([plant.approach_obstacle, *(f.obstacle_force for f in trace)])
    closure = max((f.closure for f in trace), default=0.)
    face_free = face <= 1.e-6 and (trial.kind != "hurdle_380" or impact <= 1.e-6)
    margin, crossing = edge_margin(trace, edge, wall_height) if obstacle_id else (None, None)
    air_cross = bool(crossing is not None and begin <= crossing < end and margin >= 0.)
    all_car_beyond = bool(obstacle_id and trace and trace[-1].min_x > end_edge)
    physical = bool(obstacle_id and forward and all_car_beyond and stable and face_free)
    qualified = bool(peak >= .385 and pitch <= 12. and forward and stable and face_free
                     and scrape <= 1.e-6 and closure < CLOSURE_LIMIT)
    first = trace[end] if recovery else None
    return dict(
        **vars(trial), wall_height_m=wall_height, wall_edge_m=edge if obstacle_id else None,
        triggered=pressed is not None, trigger_tick=pressed, press_x_m=press.x,
        actual_lead_m=edge - press.x if obstacle_id else None, press_vx_m_s=press.vx,
        front_gap_on_press_m=edge - press.max_x if obstacle_id else None,
        press_height_m=press.z, min_charge_vx_m_s=minimum_vx, min_charge_progress_m=charge_retreat,
        charge_scrape_n=scrape, forward_running=forward, flight_peak_all_m=peak,
        tire_peak_m=max((f.tire_low for f in flight), default=0.),
        guide_peak_m=max((f.guide_low for f in flight), default=0.),
        chassis_peak_m=max((f.chassis_low for f in flight), default=0.),
        flight_pitch_deg=pitch, flight_s=len(flight) * DT,
        takeoff_after_press_s=flight[0].time - press.time if flight else None,
        apex_after_press_s=apex.time - press.time if apex else None,
        first_touch_after_press_s=first.time - press.time if first else None,
        first_top_support_after_press_s=top[0].time - press.time if top else None,
        first_top_support_lagging_wheel_margin_m=top[0].lagging_wheel_x - edge if top else None,
        supported_while_held=bool(any(f.time - press.time <= key_ticks * .020 for f in top)),
        peak_abs_vz_first_120ms_m_s=max((abs(f.vz) for f in recovery[:48]), default=None),
        rebound_vz_first_120ms_m_s=max((max(0., f.vz) for f in recovery[:48]), default=None),
        peak_pitch_first_120ms_deg=max((abs(f.pitch) for f in recovery[:48]), default=None),
        peak_vx_after_press_m_s=max((f.vx for f in trace), default=None),
        end_vx_m_s=tail_vx,
        recovery_mae_m_s=mean(abs(f.vx - trial.speed) for f in tail) if tail else None,
        wall_face_force_n=face, wall_face_free=face_free, obstacle_max_force_n=impact,
        wall_margin_m=margin, positive_crossing_during_main_flight=air_cross,
        both_wheels_top_samples=len(top), both_wheels_top_beyond_samples=sum(
            f.lagging_wheel_x > edge + .02 for f in top),
        final_300ms_support_samples=sum(supported[-120:]), longest_both_wheels_running_s=longest * DT,
        max_closure_m=closure, end_clear_of_obstacle=all_car_beyond, fall=fall, landed_running=stable,
        key_observed_ticks=key_ticks, obstacle_pass_physical=physical, qualified=qualified,
        strict_direct=bool(physical and qualified and air_cross),
    )
