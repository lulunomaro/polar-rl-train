"""Independent 400 Hz R9 acceptance on fixed 380 mm and 360 mm walls."""
from argparse import ArgumentParser
import math
from multiprocessing import Pool
from pathlib import Path

# Set up the existing software renderer before loading MuJoCo.
from jump380_r4_evaluate import VIDEO_FILES, aggregate, read_json, representative, trial_from
from jump380_r8_evaluate import FIXED_OFFSETS, WINDOW_OFFSETS, cases, evaluate_case, initialize
import torch

from eval_moving_jump_360mm import Video
from jump360_r3_policy import R3Control
from jump360_scene import HERE, json_save, sha
from jump380_r6_replay import run_trial
from jump380_r6_scene import HALF_WIDTH, YAW_LIMIT_DEG, Y_LIMIT, Jump380Plant, prepare_scene
from jump380_r7_policy import load_policy

def render(checkpoint, rows, out):
    torch.set_num_threads(1)
    plant = Jump380Plant(visual=True)
    policy = R3Control(load_policy(checkpoint))
    checksum = sha(checkpoint)
    videos = []
    for kind, (filename, title) in VIDEO_FILES.items():
        lower_speed_passes = [row for row in rows
                              if row["kind"] == kind and row["strict_direct"] and row["speed"] <= 1.8]
        full_dr_passes = [row for row in lower_speed_passes if row["dr"] == 1.]
        pick = representative(full_dr_passes or lower_speed_passes or rows, kind)
        trial = trial_from(pick)
        passed = pick["qualified" if kind == "flat" else "strict_direct"]
        label = "Strict pass" if passed else "Physical pass" if pick["obstacle_pass_physical"] else "Attempt"
        dr = "Full DR" if trial.dr else "Nominal"
        camera = Video(out / filename, f"MOD4v3 R9 {checksum[:8]} | {title} | {label} | {dr}")
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
            raise ValueError("R9 replay and CPU evaluation checkpoints differ")
        render(args.checkpoint, saved["trials"], args.out)
        return
    from jump380_r9_timing import calibrate

    timing_path = args.timing or args.out / "TIMING.json"
    if args.timing:
        timing = read_json(timing_path)
    else:
        timing = calibrate(args.checkpoint, args.workers)
        json_save(timing_path, timing)
    if timing["checkpoint_sha256"] != checksum or timing["training"] or timing["experiment"] != "jump380_r9":
        raise ValueError("Acceptance requires geometry measured on the evaluated R9 checkpoint")

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
        sources={name: sha(HERE / name) for name in ("jump380_r9_evaluate.py", "jump380_r8_evaluate.py", "jump380_r9_timing.py",
                    "jump380_r7_policy.py", "jump380_r6_scene.py", "jump380_r6_replay.py", "jump380_r4_replay.py")},
        fixed_offsets_m=FIXED_OFFSETS, window_offsets_m=WINDOW_OFFSETS,
        by_protocol=outcome, fixed_trials=fixed, best_window_trials=windows, flat_trials=floors,
        scan_trials=scanned, trials=floors + fixed + windows + scanned))


if __name__ == "__main__":
    main()
