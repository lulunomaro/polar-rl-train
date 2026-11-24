"""Independent 400 Hz fixed-wall acceptance and real-time R10 replays."""

from argparse import ArgumentParser
from dataclasses import replace
import math
from multiprocessing import Pool
from pathlib import Path
import sys

# Initialize the existing CPU Mesa renderer before importing MuJoCo.
from jump380_r4_evaluate import aggregate, read_json, trial_from
import numpy as np
import torch

from eval_moving_jump_360mm import Video
from jump360_r3_policy import R3Control
from jump360_scene import HERE, json_save, sha
from jump380_r6_replay import Trial, run_trial
from jump380_r6_scene import HALF_WIDTH, PLATFORMS, YAW_LIMIT_DEG, Y_LIMIT, Jump380Plant, prepare_scene
import jump380_r8_evaluate as sweep
from jump380_r10_policy import EXPERIMENT, RUN, SPEED_GRID, STANCE_GRID, load_policy
from jump380_r10_timing import PRESS_GAP_M, calibrate, lead_center

CPU_INPUTS = RUN/"cpu_inputs"
if CPU_INPUTS.is_dir():
    sys.path.append(str(CPU_INPUTS))

VIDEOS = (
    ("platform_380", (2.8,), "PLATFORM_380MM_2P8MS_1X.mp4", "380 mm solid platform"),
    ("platform_380", (1.4, 1.5, 1.6), "PLATFORM_380MM_MID_1X.mp4", "380 mm solid platform"),
    ("platform_360", (2.8,), "PLATFORM_360MM_2P8MS_1X.mp4", "360 mm solid platform"),
    ("flat", (2.8,), "MOVING_JUMP_FLAT_2P8MS_1X.mp4", "Flat moving jump"),
)


def initialize(checkpoint):
    torch.set_num_threads(1)
    sweep.PLANT = Jump380Plant()
    sweep.POLICY = R3Control(load_policy(checkpoint))


def demo_cases(timing):
    # Extra Full-DR replays for the requested video speeds and the R8 .38 m stance.
    for i, speed in enumerate((1.4, 1.5, 1.6, 2.8, 3.)):
        heights = STANCE_GRID if speed == 3. else (.24, .28, .32, .36, .38, .42)
        for j, height in enumerate(heights):
            centers = tuple(float(np.interp(speed, SPEED_GRID, [np.interp(height, STANCE_GRID, line)
                            for line in timing[kind]])) for kind in PLATFORMS)
            holds = (19, 40) if speed == 3. else (12, 19, 31, 40, 50)
            for rep, hold in enumerate(holds):
                seed = 81910 + 103*i + 13*j + rep
                offset = sweep.FIXED_OFFSETS[(i+2*j+rep)%len(sweep.FIXED_OFFSETS)]
                yield Trial(seed, speed, height, 1., press_tick=132 + seed%17, hold_ticks=hold), centers, offset, True


def target_cases():
    for i, speed in enumerate((2.8, 1.4, 1.5, 1.6)):
        for j, height in enumerate((.24, .28, .32, .36, .38, .42)):
            holds = (12, 19, 25, 31, 36, 40, 44, 50) if speed == 2.8 else (12, 25, 38, 50)
            for rep, hold in enumerate(holds):
                seed = 86230 + 173*i + 23*j + rep
                yield Trial(seed, speed, height, 1., press_tick=126 + seed%24, hold_ticks=hold)


def high_speed_cases():
    for j, height in enumerate((.24, .28, .32, .36, .38, .42)):
        for rep in range(24):
            seed = 88100 + 67*j + rep
            yield Trial(seed, 2.8, height, 1., press_tick=126 + seed%24,
                        hold_ticks=(12, 19, 25, 31, 37, 44, 50)[rep%7])


def evaluate_target(trial, match_speed=False):
    from jump380_r4_calibrate import geometry_window

    flat, trace = run_trial(sweep.PLANT, sweep.POLICY, trial)
    scans, best = [], []
    if not flat["forward_running"] or not trace or (match_speed and abs(flat["press_vx_m_s"] - 2.8) > .085):
        return flat, [], scans, best
    nose_extension = trace[0].max_x - flat["press_x_m"]
    for kind, height in zip(PLATFORMS, (.38, .36)):
        geometry = geometry_window(flat, trace, height, 0.)
        if geometry is None:
            continue
        center = lead_center(geometry)
        wall = flat["press_x_m"] + center
        base = replace(trial, kind=kind, wall_at=wall)
        tick_distance = .020*max(.20, flat["press_vx_m_s"])
        by_trigger = {}
        for offset in (.002, -tick_distance, tick_distance, -2.*tick_distance, 2.*tick_distance):
            distance = max(nose_extension + PRESS_GAP_M, center + offset)
            row, _ = run_trial(sweep.PLANT, sweep.POLICY, replace(base, lead=distance))
            by_trigger.setdefault(row["trigger_tick"], row)
            if row["strict_direct"] and (trial.speed != 2.8 or
                    abs(row["press_vx_m_s"] - trial.speed) <= .05 and row["flight_pitch_deg"] <= 8.):
                break
        rows = list(by_trigger.values())
        scans.extend(rows)
        best.append(max(rows, key=replay_rank))
    return flat, [], scans, best


def evaluate_high_speed(trial):
    return evaluate_target(trial, match_speed=True)


def strict(row):
    return row["qualified"] if row["kind"] == "flat" else row["strict_direct"]


def replay_rank(row):
    speed_error = abs(row["press_vx_m_s"] - row["speed"])
    return (strict(row), row["obstacle_pass_physical"], row["forward_running"], row["landed_running"],
            speed_error <= .05, speed_error <= .10, row["flight_pitch_deg"] <= 8.,
            -row["flight_pitch_deg"],
            -abs((row["end_vx_m_s"] or 0.) - row["speed"]),
            row["wall_margin_m"] if row["wall_margin_m"] is not None else row["flight_peak_all_m"])


def render(checkpoint, rows, out):
    torch.set_num_threads(1)
    plant = Jump380Plant(visual=True)
    policy = R3Control(load_policy(checkpoint))
    checksum = sha(checkpoint)
    videos = []
    for kind, speeds, filename, title in VIDEOS:
        matches = [row for row in rows if row["kind"] == kind and row["speed"] in speeds and row["dr"] == 1.]
        if not matches:
            raise ValueError(f"No Full-DR replay available for {filename}")
        pick = max(matches, key=replay_rank)
        trial = trial_from(pick)
        label = "Strict pass" if strict(pick) else "Physical pass" if pick["obstacle_pass_physical"] else "Attempt"
        camera = Video(out/filename, f"MOD4v3 R10 {checksum[:8]} | {title} | cmd {trial.speed:.1f} m/s | Full DR | {label}")
        try:
            actual, _ = run_trial(plant, policy, trial, camera)
        finally:
            camera.close()
        for field in ("qualified", "strict_direct", "obstacle_pass_physical", "course_qualified",
                      "key_observed_ticks", "final_300ms_support_samples"):
            if actual[field] != pick[field]:
                raise RuntimeError(f"Rendered {filename} differs on {field}")
        if not math.isclose(actual["flight_peak_all_m"], pick["flight_peak_all_m"],
                            rel_tol=.01, abs_tol=.002) or camera.count == 0:
            raise RuntimeError(f"Rendered {filename} differs on clearance")
        videos.append(dict(kind=kind, file=filename, sha256=sha(out/filename), frames=camera.count,
                           fps=25, playback_speed=1., case=actual))
    json_save(out/"VIDEO.json", dict(checkpoint_sha256=checksum, videos=videos))


def evaluate(args):
    timing_path = args.timing or args.out/"TIMING.json"
    checksum = sha(args.checkpoint)
    if args.timing:
        timing = read_json(timing_path)
    else:
        timing = calibrate(args.checkpoint, args.workers)
        json_save(timing_path, timing)
    if timing["checkpoint_sha256"] != checksum or timing["training"] or timing["experiment"] != EXPERIMENT:
        raise ValueError("R10 acceptance requires the evaluated checkpoint's own 400 Hz jump geometry")

    worker = sweep.evaluate_case
    if args.profile == "high":
        attempts = list(high_speed_cases())
        worker = evaluate_high_speed
    elif args.profile == "target":
        attempts = list(target_cases())
        worker = evaluate_target
    else:
        attempts = list(demo_cases(timing) if args.profile == "demo" else sweep.cases(timing, args.profile))
    floors, fixed, scans, windows = [], [], [], []
    with Pool(args.workers, initializer=initialize, initargs=(args.checkpoint,)) as pool:
        for index, (flat, exact, scan, best) in enumerate(pool.imap(worker, attempts), 1):
            floors.append(flat)
            fixed.extend(exact)
            scans.extend(scan)
            windows.extend(best)
            if index % 15 == 0 or index == len(attempts):
                print(f"{args.profile} {checksum[:8]} {index}/{len(attempts)} "
                      f"fixed {sum(row['strict_direct'] for row in fixed)} "
                      f"window {sum(row['strict_direct'] for row in windows)}", flush=True)
    outcome = dict(fixed_offset=aggregate(floors + fixed), best_window=aggregate(windows))
    for protocol, groups in outcome.items():
        print(protocol, [(row["kind"], row["dr"], row["trials"], row["strict_direct"], row["physical"],
                          row["qualified"], row["clearance_385"]) for row in groups], flush=True)
    json_save(args.out/"CPU_400HZ.json", dict(
        physics_hz=400, policy_hz=50, checkpoint=str(args.checkpoint), sha256=checksum,
        profile=args.profile, timing_sha256=sha(timing_path), scene_sha256=sha(prepare_scene(False)),
        platform_width_m=2.*HALF_WIDTH, max_allowed_abs_y_m=Y_LIMIT, max_allowed_abs_yaw_deg=YAW_LIMIT_DEG,
        sources={name: sha(HERE/name) for name in ("jump380_r10_evaluate.py", "jump380_r10_policy.py",
                 "jump380_r10_timing.py", "jump380_r8_evaluate.py", "jump380_r6_replay.py", "jump380_r4_replay.py")},
        fixed_offsets_m=sweep.FIXED_OFFSETS, window_offsets_m=sweep.WINDOW_OFFSETS,
        by_protocol=outcome, fixed_trials=fixed, best_window_trials=windows, flat_trials=floors,
        scan_trials=scans, trials=floors + fixed + windows + scans))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timing", type=Path)
    parser.add_argument("--profile", choices=("screen", "acceptance", "demo", "target", "high"), default="acceptance")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--render-from", type=Path, nargs="+")
    args = parser.parse_args()
    if args.render_from:
        checksum = sha(args.checkpoint)
        rows = []
        for path in args.render_from:
            report = read_json(path)
            if report["sha256"] != checksum:
                raise ValueError("R10 replay and CPU acceptance checkpoints differ")
            rows.extend(report["trials"])
        render(args.checkpoint, rows, args.out)
    else:
        evaluate(args)


if __name__ == "__main__":
    main()
