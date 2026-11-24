"""Pure-policy independent MuJoCo acceptance and 1x replay."""
from __future__ import annotations

from argparse import ArgumentParser
import math
from multiprocessing import Pool
import os
from pathlib import Path
from statistics import mean
import sys

if '--render' in sys.argv and (mesa := os.environ.get('JUMP360_OSMESA')):
    import ctypes
    import ctypes.util

    platform_find_library = ctypes.util.find_library
    ctypes.util.find_library = lambda name: mesa if name == "OSMesa" else platform_find_library(name)
    ctypes.CDLL(mesa, mode=ctypes.RTLD_GLOBAL)

import numpy as np
import torch

from jump360_scene import (
    CLOSURE_LIMIT, DT, HERE, HOLD_TICKS, HURDLE_THICKNESS, PARENT, PLATFORM_LENGTH, WALL_HEIGHT, JumpPlant,
    StatefulMoEJumpActor, json_save, model_from, mujoco, sha,
)

SPEEDS = (.60, 1.00, 1.40, 1.80)
HEIGHTS = (.24, .32, .42)
REQUIRED_CLEARANCE = .385
CALIBRATION_OFFSETS = (0., -.04, .04, -.08, .08, -.12, .12, -.16, .16)
EVAL_PLANT = None
EVAL_POLICY = None


MeasuredPlant = JumpPlant


class Trial:
    def __init__(self, seed, speed, height, dr, kind="flat", lead=.85, press_tick=142, hold_ticks=HOLD_TICKS,
                 wall_at=None):
        self.seed = seed
        self.speed = speed
        self.height = height
        self.dr = dr
        self.kind = kind
        self.lead = lead
        self.press_tick = press_tick
        self.hold_ticks = hold_ticks
        self.wall_at = wall_at


def main_flight_bounds(frames):
    air = np.array([f.total_force < 1. and f.lowest > .006 for f in frames], dtype=bool)
    boundaries = np.flatnonzero(np.diff(np.r_[False, air, False]))
    for start, end in zip(boundaries[::2], boundaries[1::2]):
        if end-start >= 12 and not any(f.obstacle_force >= 1. for f in frames[:start]):
            return int(start), int(end)
    return 0, 0


def edge_margin(frames, edge, wall_height):
    for index, (previous, frame) in enumerate(zip(frames, frames[1:]), start=1):
        if previous.lagging_wheel_x <= edge < frame.lagging_wheel_x:
            fraction = (edge-previous.lagging_wheel_x)/(frame.lagging_wheel_x-previous.lagging_wheel_x)
            return previous.lowest + fraction*(frame.lowest-previous.lowest) - wall_height, index
    return None, None


def measure(frames, trial, press, edge, fall):
    start, end = main_flight_bounds(frames)
    flight = frames[start:end]
    apex = max(flight, key=lambda f: f.lowest, default=None)
    charge = frames[:start+1] if flight else frames[:min(240, len(frames))]
    recovery = frames[end:] if flight else []
    max_pitch = max((abs(f.pitch) for f in flight), default=0.)
    peak = apex.lowest if apex else 0.
    charge_min = min((f.vx for f in charge), default=press.vx)
    least_progress = min([0., *(f.x-press.x for f in charge)])
    scrape = max((f.scrape_force for f in charge), default=0.)
    face = max((f.face_force for f in frames), default=0.)
    impact = max((f.obstacle_force for f in frames), default=0.)
    tail = recovery[-120:]
    if trial.kind == "platform":
        supported = [f.min_x > edge and f.vx > .25*trial.speed and abs(f.pitch) < 18
                     and min(f.wheel_top_force) > 1. and f.tire_low > WALL_HEIGHT-.015
                     for f in recovery]
    elif trial.kind.startswith("hurdle"):
        supported = [f.min_x > edge+HURDLE_THICKNESS and f.vx > .25*trial.speed
                     and abs(f.pitch) < 18 and min(f.wheel_up_force) > 1. and f.tire_low < .020
                     for f in recovery]
    else:
        supported = [f.vx > .25*trial.speed and abs(f.pitch) < 18 and min(f.wheel_up_force) > 1.
                     and f.tire_low < .020 for f in recovery]
    support_samples = sum(supported)
    stable_running = bool(not fall and len(tail) == 120 and sum(supported[-120:]) >= 72
                          and mean(f.vx for f in tail) > .35*trial.speed)
    face_free = face <= 1.e-6 and (not trial.kind.startswith("hurdle") or impact <= 1.e-6)
    post_contact = max((f.scrape_force for f in recovery), default=0.)
    maximum_closure = max((f.closure for f in frames), default=0.)
    wall_height = .340 if trial.kind == "hurdle340" else WALL_HEIGHT
    margin, crossing = edge_margin(frames, edge, wall_height)
    result = vars(trial).copy()
    result.update(
        fall=bool(fall), press_vx_m_s=press.vx, press_actual_height_m=press.z,
        min_charge_vx_m_s=charge_min, charge_distance_m=(charge[-1].x-press.x if charge else 0.),
        min_charge_progress_m=least_progress, min_charge_height_m=min((f.z for f in charge), default=press.z),
        charge_scrape_n=scrape, flight_peak_all_m=peak,
        tire_peak_m=max((f.tire_low for f in flight), default=0.),
        guide_peak_m=max((f.guide_low for f in flight), default=0.),
        chassis_peak_m=max((f.chassis_low for f in flight), default=0.),
        tire_at_apex_m=apex.tire_low if apex else None, guide_at_apex_m=apex.guide_low if apex else None,
        chassis_at_apex_m=apex.chassis_low if apex else None,
        apex_after_press_s=(apex.time-press.time if apex else None),
        apex_x_after_press_m=(apex.x-press.x if apex else None),
        apex_front_after_press_m=(apex.max_x-press.x if apex else None),
        apex_rear_after_press_m=(apex.min_x-press.x if apex else None),
        apex_lagging_wheel_after_press_m=(apex.lagging_wheel_x-press.x if apex else None),
        flight_s=len(flight)*DT, flight_pitch_deg=max_pitch,
        forward_running=bool(press.vx > 0. and charge_min > 0. and least_progress > -1.e-6),
        flight_start_after_press_s=flight[0].time-press.time if flight else None,
        takeoff_vz_m_s=max((f.vz for f in frames[max(0, start-12):start+4]), default=0.),
        wall_face_force_n=face, obstacle_max_force_n=impact, wall_face_free=face_free,
        wall_margin_m=margin, wall_crossing_in_main_flight=bool(crossing is not None and start <= crossing < end),
        first_touch_after_press_s=frames[end].time-press.time if flight and end < len(frames) else None,
        supported_samples=support_samples, landed_running=stable_running,
        final_vx_m_s=mean(f.vx for f in tail) if tail else None, end_x=frames[-1].x if frames else press.x,
        wall_edge_m=edge if trial.kind != "flat" else None,
        end_clear_of_obstacle=bool(frames and frames[-1].min_x > edge + (HURDLE_THICKNESS if trial.kind.startswith("hurdle") else 0.)),
        max_closure_m=maximum_closure, max_mimic_residual_rad=max((f.mimic for f in frames), default=0.),
        landing_scrape_n=post_contact,
    )
    result["qualified"] = bool(
        peak >= REQUIRED_CLEARANCE and result["forward_running"] and scrape <= 1.e-6
        and max_pitch <= 12. and stable_running and face_free and maximum_closure < CLOSURE_LIMIT
    )
    return result


def run_trial(plant, policy, trial, video=None, collect_actions=False, park_until_press=False):
    rng = np.random.default_rng(trial.seed)
    y, yaw = rng.uniform(-.012, .012), rng.uniform(-.010, .010)
    plant.rng = np.random.default_rng(trial.seed + 94887)
    plant.setup(trial.height, trial.dr, (0., float(y), float(yaw)))
    policy.reset_history()
    frames, actions, observations = [], [], []
    edge = math.inf
    press = None
    if trial.kind != "flat" and not park_until_press:
        # The validation approach starts on the floor. Place the box at its fixed
        # location before traffic begins, using the floor calibration distance.
        duration = trial.press_tick * .02
        travel_estimate = trial.speed * max(0., duration-.85)
        edge = trial.wall_at if trial.wall_at is not None else travel_estimate + trial.lead
        plant.wall(trial.kind, edge)
    speed_cmd = 0.
    number = trial.press_tick + 130
    trigger = None
    for tick in range(number):
        if (trigger is None and tick >= 60 and
                (tick >= trial.press_tick if trial.kind == "flat" or park_until_press
                 else float(plant.d.qpos[0]) >= edge-trial.lead-1.e-9)):
            trigger = tick
            press = plant.frame()
            if trial.kind != "flat" and park_until_press:
                edge = press.x + trial.lead
                plant.wall(trial.kind, edge)
        target = trial.speed if tick >= 30 else 0.
        speed_cmd += (target - speed_cmd) / 12.
        key = trigger is not None and tick-trigger < trial.hold_ticks
        observation = plant.command(speed_cmd, trial.height, key)
        action = policy(plant, observation)
        if collect_actions:
            observations.append(observation)
            actions.append(action)
        plant.advance(action, frames.append if press is not None else None)
        if video is not None and tick % 2 == 1:
            video.frame(plant, key, speed_cmd, frames)
        if plant.tilt_fault or not np.isfinite(plant.d.qpos).all():
            break
        if trigger is not None and tick-trigger >= 125:
            break
    if press is None:
        press = plant.frame()
    result = measure(frames, trial, press, edge, plant.tilt_fault)
    result["triggered"] = trigger is not None
    result["trigger_tick"] = trigger
    result["press_x_m"] = press.x
    result["press_gap_from_leading_geom_m"] = edge-press.max_x if trial.kind!="flat" else None
    result["end_actual_height_from_support_m"] = float(plant.d.qpos[2]) - (
        WALL_HEIGHT if trial.kind == "platform" and result["end_clear_of_obstacle"] else 0.)
    result["obstacle_pass_physical"] = bool(trial.kind != "flat" and result["end_clear_of_obstacle"]
                                           and result["landed_running"] and result["wall_face_free"])
    return result, frames, np.asarray(observations), np.asarray(actions)


class NeuralControl:
    def __init__(self, core):
        self.actor = StatefulMoEJumpActor(core)

    def reset_history(self):
        self.actor.reset_history()

    def __call__(self, plant, observation):
        return self.actor(torch.from_numpy(observation[None]))[0].numpy()


def calibrated_lead(result, kind):
    apex = result["apex_lagging_wheel_after_press_m"]
    if apex is None:
        apex = .40 * result["press_vx_m_s"]
    return max(.12, apex-(0. if kind == "platform" else HURDLE_THICKNESS*.5))


def swept_leads(record, trace, kind):
    start, end = main_flight_bounds(trace)
    wall_height = .340 if kind == "hurdle340" else WALL_HEIGHT
    origin = record["press_x_m"]
    center = calibrated_lead(record, kind)
    distances = [center+offset for offset in CALIBRATION_OFFSETS]
    high = [frame for frame in trace[start:end] if frame.lowest > wall_height]
    if high:
        nose_at_rise = high[0].max_x-origin
        end_x = high[-1].lagging_wheel_x if kind == "platform" else high[-1].min_x-HURDLE_THICKNESS
        wheel_at_descent = end_x-origin
        midpoint = .5*(nose_at_rise+wheel_at_descent)
        distances.extend([nose_at_rise, wheel_at_descent, midpoint, midpoint-.04, midpoint+.04])
    # Different geometry estimates can land on the same timing bin.
    return tuple(dict.fromkeys(round(max(.12, distance), 3) for distance in distances))


def clearance_score(row):
    return (row["qualified"], row["obstacle_pass_physical"], not row["fall"], row["wall_face_free"],
            -min(row["obstacle_max_force_n"],row["wall_face_force_n"]) if row["kind"] == "platform"
            else -row["obstacle_max_force_n"], row["forward_running"], row["flight_peak_all_m"])


def replay_example(results, name):
    rows = [row for row in results if row["dr"] == 0. and row["kind"] == name]
    return max(rows, default={}, key=lambda row: (
        row["qualified"], row["obstacle_pass_physical"], row["forward_running"],
        row["min_charge_vx_m_s"] >= .5*row["speed"],
        row.get("wall_crossing_in_main_flight", False),
        row.get("wall_margin_m") or 0., row["flight_peak_all_m"],
    ))


def init_acceptance(checkpoint):
    global EVAL_PLANT, EVAL_POLICY
    torch.set_num_threads(1)
    EVAL_PLANT = MeasuredPlant()
    EVAL_POLICY = NeuralControl(model_from(checkpoint))


def evaluate_case(speed, height, seeds, scenarios, dr_scales, hold_ticks, sweep, jitter):
    plant, policy = EVAL_PLANT, EVAL_POLICY
    results, timing = [], []
    calibration, trace, _, _ = run_trial(plant, policy, Trial(9, speed, height, 0., hold_ticks=hold_ticks))
    deadlines = {}
    for name in (scenario for scenario in scenarios if scenario != "flat"):
        lead = calibrated_lead(calibration, name)
        if sweep:
            # Tune the synthetic operator's press position on seed 9 only.
            rows = []
            for proposed in swept_leads(calibration, trace, name):
                trial = Trial(9, speed, height, 0., name, proposed, hold_ticks=hold_ticks,
                              wall_at=calibration["press_x_m"]+proposed)
                row, _, _, _ = run_trial(plant, policy, trial)
                rows.append(row)
            selected = max(rows, key=clearance_score)
            lead = selected["lead"]
            timing.append(dict(speed=speed, height=height, scene=name, selected_lead_m=lead, cases=rows))
        deadlines[name] = lead
    for dr in dr_scales:
        for index, seed in enumerate(seeds):
            for name in scenarios:
                offset = jitter*(0., -.5, .5, -1., 1.)[index % 5] if name != "flat" else 0.
                lead = deadlines.get(name, .85)
                position = calibration["press_x_m"]+lead if name != "flat" else None
                trial = Trial(seed, speed, height, dr, name, max(.12, lead+offset),
                              hold_ticks=hold_ticks, wall_at=position)
                result, _, _, _ = run_trial(plant, policy, trial)
                results.append(result)
    return results, timing


def suite(checkpoint, seeds, *, scenarios, dr_scales, workers, hold_ticks=HOLD_TICKS, quick=False,
          sweep=False, endpoints=False, jitter=.08):
    speeds, heights = (SPEEDS, HEIGHTS) if not quick else ((.60, 1.40, 1.80), (.24, .32, .42))
    cases = [(v, h) for v in speeds for h in heights]
    if endpoints:
        cases.extend(((.60, .22), (2.00, .22), (2.00, .32), (2.00, .42)))
    jobs = [(v, h, seeds, scenarios, dr_scales, hold_ticks, sweep, jitter) for v, h in cases]
    if workers == 1:
        init_acceptance(checkpoint)
        output = [evaluate_case(*job) for job in jobs]
    else:
        with Pool(workers, initializer=init_acceptance, initargs=(checkpoint,)) as pool:
            output = pool.starmap(evaluate_case, jobs)
    return [row for results, _ in output for row in results], [row for _, timing in output for row in timing]


def summaries(results):
    output = []
    for dr, scenario in sorted({(r["dr"], r["kind"]) for r in results}):
        rows = [r for r in results if (r["dr"], r["kind"]) == (dr, scenario)]
        output.append(dict(
            dr=dr, scenario=scenario, trials=len(rows), survived=sum(not r["fall"] for r in rows),
            qualified=sum(r["qualified"] for r in rows),
            obstacle_pass=sum(r["obstacle_pass_physical"] for r in rows),
            landed_running=sum(r["landed_running"] for r in rows),
            threshold_clearance=sum(r["flight_peak_all_m"] >= REQUIRED_CLEARANCE for r in rows),
            continued_forward=sum(r["forward_running"] for r in rows),
            zero_scrape=sum(r["charge_scrape_n"] <= 1.e-6 for r in rows),
            peak_mean_m=mean(r["flight_peak_all_m"] for r in rows),
            peak_max_m=max(r["flight_peak_all_m"] for r in rows),
            max_air_pitch_deg=max(r["flight_pitch_deg"] for r in rows),
            min_charge_vx_m_s=min(r["min_charge_vx_m_s"] for r in rows),
        ))
    return output


class Video:
    def __init__(self, output, title):
        import imageio.v2 as imageio
        self.output = output
        output.parent.mkdir(parents=True, exist_ok=True)
        self.write = imageio.get_writer(str(output), fps=25, codec="libx264", macro_block_size=None,
                                        output_params=["-preset","fast"])
        self.title = title
        self.renderer = None
        self.camera = mujoco.MjvCamera()
        self.camera.distance = 2.5
        self.camera.elevation = -10
        self.camera.azimuth = 93
        self.opt = mujoco.MjvOption()
        self.opt.geomgroup[3] = 0
        self.count = 0

    def frame(self, plant, key, command, trace):
        from PIL import Image, ImageDraw, ImageFont
        if self.renderer is None:
            plant.m.vis.quality.offsamples = 0
            headlight = plant.m.vis.headlight
            headlight.ambient[:] = .52
            headlight.diffuse[:] = .76
            headlight.specular[:] = .20
            self.renderer = mujoco.Renderer(plant.m, height=432, width=768)
            self.font = ImageFont.load_default(size=19)
        self.camera.lookat[:] = [plant.d.qpos[0]+.27, 0., .32]
        self.renderer.update_scene(plant.d, self.camera, scene_option=self.opt)
        self.renderer.scene.flags[mujoco.mjtRndFlag.mjRND_SHADOW] = False
        frame = Image.fromarray(self.renderer.render())
        draw = ImageDraw.Draw(frame)
        draw.rectangle((0, 0, 768, 60), fill=(14, 20, 27))
        draw.text((17, 7), self.title, fill="#eef5fc", font=self.font)
        speed = plant.body_vx
        bit = int(key)
        start, end = main_flight_bounds(trace)
        peak = max((f.lowest for f in trace[start:end]), default=0.)
        draw.text((17, 33), f"t {plant.d.time:.2f} s    cmd {command:.2f} m/s    vx {speed:.2f} m/s    Space {bit}    airborne peak {max(peak,0.)*100:.1f} cm",
                  fill="#a8d8f6", font=self.font)
        self.write.append_data(np.asarray(frame))
        self.count += 1
        if self.count % 25 == 0:
            print("video", self.output.name, self.count, flush=True)

    def close(self):
        self.write.close()
        if self.renderer is not None:
            self.renderer.close()


def render(model, results, out):
    plant = MeasuredPlant(visual=True)
    player = NeuralControl(model)
    videos = []
    for name in ("flat", "platform", "hurdle"):
        best = replay_example(results, name)
        if not best:
            continue
        trial = Trial(**{key: best.get(key, default) for key, default in vars(Trial(0,1,.3,0)).items()})
        path = out / {"flat":"MOVING_JUMP_FLAT_1X.mp4", "platform":"PLATFORM_360MM_1X.mp4",
                      "hurdle":"HURDLE_360MM_1X.mp4"}[name]
        title = {"flat":"MOD4v3 | Flat moving jump", "platform":"MOD4v3 | 360 mm solid platform",
                 "hurdle":"MOD4v3 | 360 mm solid hurdle"}[name]
        video = Video(path, title)
        try:
            result, frames, _, _ = run_trial(plant, player, trial, video)
        finally:
            video.close()
        videos.append(dict(file=path.name, frames=video.count, fps=25, playback_speed=1.,
                           measured_peak_m=result["flight_peak_all_m"], case=result))
    json_save(out/"VIDEO.json", videos)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, default=PARENT)
    parser.add_argument("--scenarios", default="flat,platform,hurdle")
    parser.add_argument("--seeds", default="101,107,113,127,139")
    parser.add_argument("--dr", default="0,1")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--sweep", action="store_true")
    parser.add_argument("--endpoints", action="store_true")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--from-results", type=Path)
    parser.add_argument("--hold-ticks", type=int, default=HOLD_TICKS)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--jitter", type=float, default=.08)
    args = parser.parse_args()
    args.checkpoint = HERE / args.checkpoint
    if args.from_results is not None:
        args.from_results = HERE / args.from_results
    args.out.mkdir(exist_ok=True, parents=True)
    torch.set_num_threads(1)
    if args.from_results:
        import json
        source = json.loads(args.from_results.read_text(encoding="utf-8"))
        if source["sha256"] != sha(args.checkpoint):
            raise ValueError("Report and video use different weights")
        rows, timing = source["trials"], source.get("timing_calibration",[])
    else:
        rows, timing = suite(args.checkpoint, tuple(map(int, args.seeds.split(","))), scenarios=args.scenarios.split(","),
                            dr_scales=tuple(map(float, args.dr.split(","))), hold_ticks=args.hold_ticks,
                            quick=args.quick, sweep=args.sweep, endpoints=args.endpoints, workers=args.workers,
                            jitter=args.jitter)
    output = dict(checkpoint=str(args.checkpoint), sha256=sha(args.checkpoint), physics_hz=400, policy_hz=50,
                  wall_height_m=WALL_HEIGHT, platform_length_m=PLATFORM_LENGTH, hurdle_thickness_m=HURDLE_THICKNESS,
                  actor_inputs=[35, 420], actor_outputs=6, key_obs_index=30, sensors="joint, IMU, command, last action",
                  clearance_geometries={"main_wheels":2,"guides":8,"base_collision_boxes":8},
                  held_key_ticks=args.hold_ticks, heldout_timing_jitter_m=args.jitter,
                  summaries=summaries(rows), trials=rows, timing_calibration=timing)
    json_save(args.out/"JUMP360_RESULT.json", output)
    for stats in output["summaries"]:
        print(stats, flush=True)
    if args.render:
        render(model_from(args.checkpoint), rows, args.out)


if __name__ == "__main__":
    main()
