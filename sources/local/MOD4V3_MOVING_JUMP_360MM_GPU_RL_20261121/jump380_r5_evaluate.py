"""Measure fixed-wall timing tolerance and available press windows at 400 Hz."""
from argparse import ArgumentParser
from dataclasses import replace
import math
from multiprocessing import Pool
from pathlib import Path

# R4 evaluation initializes the pinned software renderer before importing MuJoCo.
from jump380_r4_evaluate import VIDEO_FILES, aggregate, read_json, representative, trial_from
import torch

from eval_moving_jump_360mm import Video
from jump360_r3_policy import R3Control, load_policy
from jump360_scene import HERE, json_save, sha
from jump380_r4_calibrate import geometry_window, score
from jump380_r4_replay import Trial, run_trial
from jump380_r5_scene import PARENT, PLATFORMS, RUN, Jump380Plant, prepare_scene

HOLDS = (12, 19, 25, 31, 37, 44, 50)
FIXED_OFFSETS = (-.12, -.08, -.04, 0., .04, .08, .12)
WINDOW_OFFSETS = (-.18, -.12, -.06, 0., .06, .12, .18)
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
                for dr in (0., 1.):
                    flat = Trial(seed, speed, height, dr, press_tick=123 + seed % 26, hold_ticks=HOLDS[rep])
                    obstacles = []
                    for kind in PLATFORMS:
                        center = timing[kind][i][j]
                        wall = center + (1.36 + .09*(seed % 5))*speed
                        obstacles.append((replace(flat, kind=kind, lead=center + offset, wall_at=wall),
                                          center, offset))
                    # Three of the seven holds also receive a fixed-wall press sweep.
                    yield flat, obstacles, profile == "screen" or rep in (0, 3, 6)


def evaluate_case(task):
    flat, obstacles, window = task
    floor, trace = run_trial(PLANT, POLICY, flat)
    exact, scans, best = [], [], []
    for obstacle, prior, fixed_offset in obstacles:
        fixed, _ = run_trial(PLANT, POLICY, obstacle)
        exact.append(dict(fixed_offset_m=fixed_offset, **fixed))
        if not window:
            continue
        geometry = geometry_window(floor, trace, fixed["wall_height_m"], 0.)
        if geometry:
            first, last = geometry["landing_window_m"]
            center = (first + last)/2. if last >= first else first + .015
        else:
            center = prior
        center = max(.13, min(max(center, prior - .18), prior + .18))
        rows = [dict(fixed_offset_m=fixed_offset, **fixed)]
        for offset in WINDOW_OFFSETS:
            lead = max(.07, round(center + offset, 3))
            if abs(lead - obstacle.lead) < 1.e-6:
                continue
            result, _ = run_trial(PLANT, POLICY, replace(obstacle, lead=lead))
            rows.append(dict(searched_offset_m=offset, **result))
        scans.extend(rows)
        best.append(max(rows, key=score))
    return floor, exact, scans, best


def render(checkpoint, rows, out):
    torch.set_num_threads(1)
    plant = Jump380Plant(visual=True)
    policy = R3Control(load_policy(checkpoint))
    checksum = sha(checkpoint)
    videos = []
    for kind, (filename, title) in VIDEO_FILES.items():
        pick = representative(rows, kind)
        trial = trial_from(pick)
        if not pick["qualified" if kind == "flat" else "strict_direct"]:
            raise ValueError(f"Missing a strict {kind} replay for the selected checkpoint")
        dr = "Full DR" if trial.dr else "Nominal"
        camera = Video(out / filename, f"MOD4v3 R5 {checksum[:8]} | {title} | {dr}")
        try:
            observed, _ = run_trial(plant, policy, trial, camera)
        finally:
            camera.close()
        if (not observed["qualified" if kind == "flat" else "strict_direct"]
                or not math.isclose(observed["flight_peak_all_m"], pick["flight_peak_all_m"],
                                    rel_tol=.01, abs_tol=.002)
                or observed["key_observed_ticks"] != trial.hold_ticks or camera.count == 0):
            raise RuntimeError(f"Rendered replay differs from the verified {kind} case")
        videos.append(dict(kind=kind, file=filename, sha256=sha(out / filename),
                           frames=camera.count, fps=25, playback_speed=1., case=observed))
    json_save(out / "VIDEO.json", dict(checkpoint_sha256=checksum, videos=videos))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timing", type=Path, default=RUN / "calibration/TIMING.json")
    parser.add_argument("--profile", choices=("screen", "acceptance"), default="acceptance")
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--render-from", type=Path)
    args = parser.parse_args()
    checksum = sha(args.checkpoint)
    if args.render_from:
        saved = read_json(args.render_from)
        if saved["sha256"] != checksum:
            raise ValueError("Replay weights and CPU evaluation checksums differ")
        render(args.checkpoint, saved["trials"], args.out)
        return

    prepare_scene(False)
    attempts = list(cases(read_json(args.timing), args.profile))
    floor_rows, fixed_rows, scan_rows, best_rows = [], [], [], []
    with Pool(args.workers, initializer=initialize, initargs=(args.checkpoint,)) as pool:
        for index, (floor, fixed, scans, best) in enumerate(pool.imap(evaluate_case, attempts, chunksize=2), 1):
            floor_rows.append(floor)
            fixed_rows.extend(fixed)
            scan_rows.extend(scans)
            best_rows.extend(best)
            if index % 21 == 0 or index == len(attempts):
                print(f"cpu {checksum[:8]} {index}/{len(attempts)} "
                      f"fixed {sum(r['strict_direct'] for r in fixed_rows)} "
                      f"window {sum(r['strict_direct'] for r in best_rows)}", flush=True)

    # Replay the archive's exact hand-controlled cases as a matched regression.
    initialize(args.checkpoint)
    archive = read_json(PARENT.parents[1] / "showcase_008m/CPU_400HZ.json")
    showcase = [run_trial(PLANT, POLICY, trial_from(row))[0] for row in archive["trials"]]
    results = dict(fixed_offset=aggregate(floor_rows + fixed_rows), best_window=aggregate(best_rows))
    for protocol, aggregates in results.items():
        for row in aggregates:
            print(protocol, {key: row[key] for key in ("kind", "dr", "trials", "strict_direct",
                                                       "physical", "qualified", "clearance_385")}, flush=True)
    json_save(args.out / "CPU_400HZ.json", dict(
        physics_hz=400, policy_hz=50, checkpoint=str(args.checkpoint), sha256=checksum,
        profile=args.profile, timing_sha256=sha(args.timing), scene_sha256=sha(prepare_scene(False)),
        sources={name: sha(HERE / name) for name in (
            "jump380_r5_evaluate.py", "jump380_r4_evaluate.py", "jump380_r4_replay.py",
            "jump380_r5_scene.py", "jump360_r3_policy.py")},
        fixed_offsets_m=FIXED_OFFSETS, window_offsets_m=WINDOW_OFFSETS,
        by_protocol=results, fixed_trials=fixed_rows, best_window_trials=best_rows,
        flat_trials=floor_rows, scan_trials=scan_rows, archived_showcase=showcase,
        trials=floor_rows + fixed_rows + best_rows + showcase))


if __name__ == "__main__":
    main()
