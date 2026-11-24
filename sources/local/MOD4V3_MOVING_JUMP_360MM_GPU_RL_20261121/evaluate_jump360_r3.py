"""Run deterministic, paired 400 Hz CPU replays for the R3 candidate decision."""
from argparse import ArgumentParser
import json
from multiprocessing import Pool
from pathlib import Path
from statistics import mean

import torch

from calibrate_jump360_r3 import HEIGHTS, SPEEDS
from eval_moving_jump_360mm import Trial, Video, main_flight_bounds, run_trial, summaries
from jump360_r3_policy import R3ActorCritic, R3Control, load_policy
from jump360_scene import HERE, JumpPlant, json_save, sha

ATTEMPTS = ((10, 311, 0.), (15, 337, -.04), (20, 359, .04), (30, 383, -.08),
            (40, 401, .08), (46, 421, 0.), (50, 443, -.04))
TRIAL_KEYS = tuple(vars(Trial(0, .6, .22, 0.)))
PLANT = POLICY = None
MODE_LOGITS = []


class ApproachContactAudit:
    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        self.approach_face_force = 0.

    def advance(self, action, callback=None):
        if callback is None and self.wall_scene != "flat" and self.wall_edge-self.d.qpos[0]<.65:
            def measure_before_press(frame):
                self.approach_face_force = max(self.approach_face_force, frame.face_force)
            callback = measure_before_press
        super().advance(action, callback)


class ReplayPlant(ApproachContactAudit, JumpPlant):
    pass


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def initialize(checkpoint, plant_type=ReplayPlant):
    global PLANT, POLICY
    torch.set_num_threads(1)
    PLANT = plant_type()
    model = load_policy(checkpoint)
    if isinstance(model, R3ActorCritic):
        model.actor_body.mode_head.register_forward_hook(
            lambda module, inputs, output: MODE_LOGITS.append(float(output.item())))
    POLICY = R3Control(model)


def replay(task):
    name, values = task
    trial = Trial(**values)
    MODE_LOGITS.clear()
    row, trace, observations, _ = run_trial(PLANT, POLICY, trial, collect_actions=True)
    _, landing_idx = main_flight_bounds(trace)
    post = trace[landing_idx:] if landing_idx else []
    row["suite"] = name
    row["observed_high_ticks"] = int((observations[:, 30]>.5).sum()) if len(observations) else 0
    row["observed_key_release"] = bool(len(observations) and observations[-1, 30]==0. and row["triggered"])
    row["peak_vx_after_press_m_s"] = max((frame.vx for frame in trace), default=None)
    row["peak_vx_after_touch_m_s"] = max((frame.vx for frame in post), default=None)
    row["recovery_mae_m_s"] = mean(abs(frame.vx-trial.speed) for frame in post[-120:]) if len(post)>=120 else None
    if trial.kind=="platform":
        top = [frame for frame in post if min(frame.wheel_top_force)>1.]
        edge = row["wall_edge_m"]
        row["both_wheels_on_top_samples"] = len(top)
        row["both_wheels_on_top_and_car_beyond_samples"] = sum(frame.min_x>edge for frame in top)
        row["both_wheels_on_top_beyond_and_forward_samples"] = sum(frame.min_x>edge and frame.vx>.25*trial.speed
                                                                  for frame in top)
    row["supported_while_held"] = bool(landing_idx and any(
        min(frame.wheel_top_force if trial.kind=="platform" else frame.wheel_up_force)>1.
        for frame in trace[landing_idx:trial.hold_ticks*8]))
    if MODE_LOGITS and row["first_touch_after_press_s"] is not None:
        contact_tick = row["trigger_tick"] + int(-(-landing_idx//8))
        held_end = row["trigger_tick"]+trial.hold_ticks
        ground_with_key = MODE_LOGITS[contact_tick:held_end]
        row["on_ground_while_held_ticks"] = len(ground_with_key)
        row["drive_preferred_on_ground_while_held_ticks"] = sum(logit<0. for logit in ground_with_key)
        settle = next((index for index in range(contact_tick, len(MODE_LOGITS)-3)
                       if max(MODE_LOGITS[index:index+4])<0.), None)
        row["drive_switch_s_after_contact"] = (settle-contact_tick)*.02 if settle is not None else None
    row["strict_direct"] = bool(row["qualified"] and row["obstacle_pass_physical"]
                                and row["wall_crossing_in_main_flight"] and row["wall_margin_m"]>=0.)
    row["approach_face_force_n"] = PLANT.approach_face_force
    row["strict_direct_no_approach_hit"] = row["strict_direct"] and PLANT.approach_face_force <= 1.e-6
    return row


def original_cases(screen):
    result = read_json(HERE/"JUMP360_RESULT.json")
    for row in result["trials"]:
        if row["dr"]!=0. or row["kind"]=="platform" or (screen and row["seed"]!=101):
            continue
        yield "r2_regression", {key: row[key] for key in TRIAL_KEYS}


def matched_cases(measured_path, effective_path, screen):
    measured = read_json(measured_path)
    effective = read_json(effective_path)
    for offset, calibration in enumerate(measured["cases"]):
        i, j = divmod(offset, len(HEIGHTS))
        speed, height = calibration["speed"], calibration["height"]
        assert (speed, height) == (SPEEDS[i], HEIGHTS[j])
        for hold, seed, jitter in ATTEMPTS:
            if screen and hold not in (15, 46, 50):
                continue
            for dr in (0., 1.):
                yield "paired", vars(Trial(seed, speed, height, dr, hold_ticks=hold))
                for kind in ("platform", "hurdle"):
                    if kind=="hurdle" and (hold not in (15, 46, 50) or speed<1.4 or screen):
                        continue
                    center = effective[kind][i][j]
                    edge = calibration["floor"]["press_x_m"]+center
                    yield "paired", vars(Trial(seed, speed, height, dr, kind, max(.16, center+jitter),
                                               press_tick=272, hold_ticks=hold, wall_at=edge))


def representative_cases():
    cases = read_json(HERE/"evidence/r2_geometry_final/HOLD_TICKS.json")
    for row in cases:
        if row["kind"]=="platform":
            yield "r2_2ms_example", {key: row[key] for key in TRIAL_KEYS}
    case = next(row for row in cases if row["kind"]=="platform")
    for hold in (10, 15, 20, 30, 40):
        yield "r2_2ms_example", dict({key: case[key] for key in TRIAL_KEYS}, hold_ticks=hold)


def repeat_holds(results, checkpoint_sha):
    recorded = {}
    for path in results:
        data = read_json(path)
        if data["sha256"]!=checkpoint_sha:
            raise ValueError("Hold-duration input checkpoint mismatch")
        for row in data["trials"]:
            if row["kind"]=="platform" and row["strict_direct"]:
                trip = {key: row[key] for key in TRIAL_KEYS if key!="hold_ticks"}
                recorded[tuple(trip.values())] = trip
    for trip in recorded.values():
        for hold in (10, 15, 20, 30, 40, 42, 46, 50):
            yield "validated_platform_vary_hold", dict(trip, hold_ticks=hold)


def platform_from_hurdles(path, checkpoint_sha):
    data = read_json(path)
    if data["sha256"]!=checkpoint_sha:
        raise ValueError("Hurdle replay input checkpoint mismatch")
    for row in data["trials"]:
        if row["kind"]=="hurdle" and row["qualified"]:
            yield "hurdle_press_replayed_on_platform", dict({key: row[key] for key in TRIAL_KEYS}, kind="platform")


def aggregate(rows):
    by_scene = {name: summaries([row for row in rows if row["suite"]==name])
                for name in sorted({row["suite"] for row in rows})}
    walls = []
    for dr in (0., 1.):
        for speed in SPEEDS:
            group = [row for row in rows if row["suite"]=="paired" and row["kind"]=="platform"
                     and row["speed"]==speed and row["dr"]==dr]
            walls.append(dict(dr=dr, speed_m_s=speed, trials=len(group),
                              strict=sum(row["qualified"] for row in group), direct=sum(row["strict_direct"] for row in group),
                              physical=sum(row["obstacle_pass_physical"] for row in group),
                              hold_50_landed=sum(row["hold_ticks"]==50 and row["landed_running"] for row in group)))
    speed_2 = []
    for dr in (0., 1.):
        group = [row for row in rows if row["suite"]=="paired" and row["kind"]=="flat"
                 and row["speed"]==2. and row["dr"]==dr]
        if not group:
            continue
        recovered = [row for row in group if row["landed_running"]]
        speed_2.append(dict(dr=dr, trials=len(group), recovery_trials=len(recovered),
                            press_vx_mean=mean(row["press_vx_m_s"] for row in group),
                            press_vx_max=max(row["press_vx_m_s"] for row in group),
                            peak_vx_max=max((row["peak_vx_after_press_m_s"] or 0.) for row in group),
                            recovery_vx_mean=mean(row["final_vx_m_s"] for row in recovered) if recovered else None,
                            recovery_mae=mean(row["recovery_mae_m_s"] for row in recovered) if recovered else None))
    return dict(suites=by_scene, platform_by_speed=walls, speed_2_flat=speed_2)


def render_evidence(model, rows, out):
    plant = JumpPlant(visual=True)
    player = R3Control(model)
    videos = []
    names = {"flat": ("MOVING_JUMP_FLAT", "Flat moving jump"),
             "platform": ("PLATFORM_360MM", "360 mm solid platform"),
             "hurdle": ("HURDLE_360MM", "360 mm solid hurdle")}
    for kind, (stem, title) in names.items():
        options = [row for row in rows if row["kind"]==kind and row["qualified"]]
        if not options:
            continue
        best = max(options, key=lambda row: (
            row["strict_direct"], row["hold_ticks"]==50, row["speed"]<=1.8,
            row["wall_margin_m"] or 0., row["flight_peak_all_m"]))
        trial = Trial(**{key: best[key] for key in TRIAL_KEYS})
        name = stem+"_1X.mp4"
        caption = f"MOD4v3 R3 | {title} | {'Full DR' if trial.dr else 'Nominal'} | {trial.hold_ticks} ticks"
        video = Video(out/name, caption)
        try:
            rerun, _, _, _ = run_trial(plant, player, trial, video)
        finally:
            video.close()
        videos.append(dict(file=name, frames=video.count, fps=25, playback_speed=1.,
                           measured_peak_m=rerun["flight_peak_all_m"], case=rerun))
    json_save(out/"VIDEO.json", videos)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--measured", type=Path, default=Path("evidence/jump360_r3/calibration/TIMING_R2_MEASURED.json"))
    parser.add_argument("--effective", type=Path, default=Path("evidence/jump360_r3/probe/TRAINING_TIMING.json"))
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--screen", action="store_true")
    parser.add_argument("--render", action="store_true")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--from-results", type=Path)
    source.add_argument("--repeat-holds", type=Path, nargs="+")
    source.add_argument("--platform-from-hurdles", type=Path)
    args = parser.parse_args()
    checkpoint = HERE/args.checkpoint
    args.out.mkdir(parents=True, exist_ok=True)
    if args.from_results:
        payload = read_json(HERE/args.from_results)
        if sha(checkpoint)!=payload["sha256"]:
            raise ValueError("Video input checkpoint mismatch")
    else:
        if args.repeat_holds:
            cases = list(repeat_holds([HERE/path for path in args.repeat_holds], sha(checkpoint)))
        elif args.platform_from_hurdles:
            cases = list(platform_from_hurdles(HERE/args.platform_from_hurdles, sha(checkpoint)))
        else:
            cases = [*matched_cases(HERE/args.measured, HERE/args.effective, args.screen),
                     *representative_cases(), *original_cases(args.screen)]
        with Pool(args.workers, initializer=initialize, initargs=(checkpoint,)) as pool:
            rows = list(pool.imap(replay, cases, chunksize=4))
        payload = dict(physics_hz=400, checkpoint=str(args.checkpoint), sha256=sha(checkpoint),
                       screen=args.screen, **aggregate(rows), trials=rows)
        json_save(args.out/"CPU_400HZ.json", payload)
        print(json.dumps({key: payload[key] for key in ("sha256", "suites", "platform_by_speed", "speed_2_flat")}))
    if args.render:
        torch.set_num_threads(1)
        render_evidence(load_policy(checkpoint), payload["trials"], args.out)


if __name__ == "__main__":
    main()

