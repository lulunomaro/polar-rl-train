"""Independent 400 Hz R7 acceptance on fixed 380 mm and 360 mm walls."""
from argparse import ArgumentParser
from dataclasses import replace
import math
from multiprocessing import Pool
from pathlib import Path

# Set up the existing software renderer before loading MuJoCo.
from jump380_r4_evaluate import VIDEO_FILES, aggregate, read_json, representative, trial_from
import torch

from eval_moving_jump_360mm import Video
from jump360_r3_policy import R3Control
from jump360_scene import HERE, json_save, sha
from jump380_r6_replay import Trial, run_trial
from jump380_r6_scene import HALF_WIDTH, PLATFORMS, YAW_LIMIT_DEG, Y_LIMIT, Jump380Plant, prepare_scene
from jump380_r7_policy import load_policy

HOLDS = (12, 19, 25, 31, 37, 44, 50)
FIXED_OFFSETS = (-.12, -.08, -.04, 0., .04, .08, .12)
WINDOW_OFFSETS = (-.24, -.16, -.08, 0., .08, .16, .24)
PLANT = POLICY = None


def initialize(checkpoint):
    global PLANT, POLICY
    torch.set_num_threads(1)
    PLANT = Jump380Plant()
    POLICY = R3Control(load_policy(checkpoint))


def cases(timing, profile):
    for i, speed in enumerate(timing["speeds"]):
        for j, height in enumerate(timing["heights"]):
            reps = range(len(HOLDS)) if profile == "acceptance" else ((2*i + j) % len(HOLDS),)
            for rep in reps:
                anchor = 31700 if profile == "acceptance" else 54100
                seed = anchor + 19*(i*len(timing["heights"]) + j) + rep
                offset = FIXED_OFFSETS[(rep + i + 2*j) % len(FIXED_OFFSETS)]
                centers = tuple(timing[kind][i][j] for kind in PLATFORMS)
                for dr in (0., 1.):
                    flat = Trial(seed, speed, height, dr, press_tick=123 + seed % 26, hold_ticks=HOLDS[rep])
                    yield flat, centers, offset, (profile == "screen" or rep in (0, 3, 6))


def evaluate_case(task):
    from jump380_r4_calibrate import geometry_window, score
    from jump380_r7_timing import lead_center

    flat, centers, fixed_offset, scan_allowed = task
    floor, trace = run_trial(PLANT, POLICY, flat)
    nose_extension = (trace[0].max_x - floor["press_x_m"]) if trace else .30
    # Keep the wall fixed during each set, including when trying a different
    # operator press distance. The flat trace only sets an initial search range.
    minimum = nose_extension + .38
    fixed_rows, scans, best = [], [], []
    for kind, nominal, height in zip(PLATFORMS, centers, (.38, .36)):
        wall_at = max(1., floor["press_x_m"]) + max(nominal, minimum)
        lead = max(minimum, nominal + fixed_offset)
        base = replace(flat, kind=kind, wall_at=wall_at, lead=lead)
        fixed, _ = run_trial(PLANT, POLICY, base)
        fixed = dict(requested_fixed_offset_m=fixed_offset, effective_fixed_offset_m=lead - nominal, **fixed)
        fixed_rows.append(fixed)
        if not scan_allowed:
            continue
        geometry = geometry_window(floor, trace, height, 0.)
        center = lead_center(geometry, nose_extension, floor["press_vx_m_s"], training=False)
        # With a feasible flat window, include its interior even if it is narrow.
        distances = {round(max(minimum, center + offset), 3) for offset in WINDOW_OFFSETS}
        if geometry:
            low, high = geometry["landing_window_m"]
            if high >= low:
                distances.update(round(max(minimum, fraction*low+(1.-fraction)*high), 3)
                                 for fraction in (.15, .5, .85))
        rows = [fixed]
        for distance in sorted(distances):
            if abs(distance - lead) < .004:
                continue
            result, _ = run_trial(PLANT, POLICY, replace(base, lead=distance))
            rows.append(dict(searched_offset_m=distance - center, **result))
        scans.extend(rows)
        best.append(max(rows, key=score))
    return floor, fixed_rows, scans, best


def render(checkpoint, rows, out):
    torch.set_num_threads(1)
    plant = Jump380Plant(visual=True)
    policy = R3Control(load_policy(checkpoint))
    checksum = sha(checkpoint)
    videos = []
    for kind, (filename, title) in VIDEO_FILES.items():
        pick = representative(rows, kind)
        trial = trial_from(pick)
        passed = pick["qualified" if kind == "flat" else "strict_direct"]
        label = "Strict pass" if passed else "Physical pass" if pick["obstacle_pass_physical"] else "Attempt"
        dr = "Full DR" if trial.dr else "Nominal"
        camera = Video(out / filename, f"MOD4v3 R7 {checksum[:8]} | {title} | {label} | {dr}")
        try:
            actual, _ = run_trial(plant, policy, trial, camera)
        finally:
            camera.close()
        for field in ("qualified", "strict_direct", "obstacle_pass_physical", "course_qualified",
                      "key_observed_ticks"):
            if actual[field] != pick[field]:
                raise RuntimeError(f"Rendered {kind} differs on {field}")
        if not math.isclose(actual["flight_peak_all_m"], pick["flight_peak_all_m"],
                            rel_tol=.01, abs_tol=.002) or camera.count == 0:
            raise RuntimeError(f"Rendered {kind} differs on clearance")
        videos.append(dict(kind=kind, file=filename, sha256=sha(out / filename),
                           frames=camera.count, fps=25, playback_speed=1., case=actual))
    json_save(out / "VIDEO.json", dict(checkpoint_sha256=checksum, videos=videos))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timing", type=Path)
    parser.add_argument("--profile", choices=("screen", "acceptance"), default="acceptance")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--render-from", type=Path)
    args = parser.parse_args()
    checksum = sha(args.checkpoint)
    if args.render_from:
        saved = read_json(args.render_from)
        if saved["sha256"] != checksum:
            raise ValueError("R7 replay and CPU evaluation checkpoints differ")
        render(args.checkpoint, saved["trials"], args.out)
        return
    from jump380_r7_timing import calibrate

    timing_path = args.timing or args.out / "TIMING.json"
    if args.timing:
        timing = read_json(timing_path)
    else:
        timing = calibrate(args.checkpoint, args.workers)
        json_save(timing_path, timing)
    if timing["checkpoint_sha256"] != checksum or timing["training"]:
        raise ValueError("Acceptance requires geometry measured on the evaluated R7 checkpoint")

    attempts = list(cases(timing, args.profile))
    floors, fixed, scanned, windows = [], [], [], []
    with Pool(args.workers, initializer=initialize, initargs=(args.checkpoint,)) as pool:
        for index, (floor, exact, scan, best) in enumerate(pool.imap(evaluate_case, attempts, chunksize=2), 1):
            floors.append(floor)
            fixed.extend(exact)
            scanned.extend(scan)
            windows.extend(best)
            if index % 21 == 0 or index == len(attempts):
                print(f"cpu {checksum[:8]} {index}/{len(attempts)} "
                      f"fixed {sum(r['strict_direct'] for r in fixed)} "
                      f"window {sum(r['strict_direct'] for r in windows)}", flush=True)

    outcome = dict(fixed_offset=aggregate(floors + fixed), best_window=aggregate(windows))
    for name, group in outcome.items():
        print(name, [(row["kind"], int(row["dr"]), row["trials"], row["strict_direct"],
                      row["physical"], row["qualified"], row["clearance_385"]) for row in group], flush=True)
    json_save(args.out / "CPU_400HZ.json", dict(
        physics_hz=400, policy_hz=50, checkpoint=str(args.checkpoint), sha256=checksum,
        profile=args.profile, timing_sha256=sha(timing_path), scene_sha256=sha(prepare_scene(False)),
        platform_width_m=2.*HALF_WIDTH, max_allowed_abs_y_m=Y_LIMIT, max_allowed_abs_yaw_deg=YAW_LIMIT_DEG,
        sources={name: sha(HERE / name) for name in ("jump380_r7_evaluate.py", "jump380_r7_timing.py",
                    "jump380_r7_policy.py", "jump380_r6_scene.py", "jump380_r6_replay.py", "jump380_r4_replay.py")},
        fixed_offsets_m=FIXED_OFFSETS, window_offsets_m=WINDOW_OFFSETS,
        by_protocol=outcome, fixed_trials=fixed, best_window_trials=windows, flat_trials=floors,
        scan_trials=scanned, trials=floors + fixed + windows + scanned))


if __name__ == "__main__":
    main()
