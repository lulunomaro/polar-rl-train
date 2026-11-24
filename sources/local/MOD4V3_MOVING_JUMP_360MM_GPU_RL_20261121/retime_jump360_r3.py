"""Calibrate a synthetic operator on one seed and replay held-out 360 mm platform trials."""
from argparse import ArgumentParser
from multiprocessing import Pool
from pathlib import Path

from calibrate_jump360_r3 import HEIGHTS, SPEEDS, TimingPlant, compact, geometry_window
from eval_moving_jump_360mm import Trial, run_trial
from evaluate_jump360_r3 import ATTEMPTS, aggregate, read_json, replay
import evaluate_jump360_r3 as evaluation
from jump360_scene import HERE, HOLD_TICKS, json_save, sha

CALIBRATION_SEED = 557


class TimingReplayPlant(evaluation.ApproachContactAudit, TimingPlant):
    pass


def initialize(checkpoint):
    evaluation.initialize(checkpoint, TimingReplayPlant)


def score(row):
    return (
        row["qualified"] and row["wall_crossing_in_main_flight"],
        row["qualified"],
        row["obstacle_pass_physical"] and row["wall_crossing_in_main_flight"],
        row["obstacle_pass_physical"],
        row["wall_face_free"] and row["wall_crossing_in_main_flight"],
        row["supported_samples"],
        row["triggered"] and row["wall_face_free"] and not row["fall"],
        row["triggered"] and row["forward_running"],
        -row["wall_face_force_n"],
    )


def calibrate(task):
    speed, height, prior = task
    plant, policy = evaluation.PLANT, evaluation.POLICY
    floor, frames, _, _ = run_trial(plant, policy, Trial(CALIBRATION_SEED, speed, height, 0.))
    geometry = geometry_window(floor, frames)
    centers = [prior]
    overlap = geometry["whole_car_window_m"]
    if overlap is not None:
        centers.extend((overlap[0]+.04, overlap[1], (overlap[0]+overlap[1])*.5))
    apex = floor["apex_lagging_wheel_after_press_m"]
    if apex is not None:
        centers.append(apex)
    candidates = sorted({round(max(.22, base+offset), 3) for base in centers
                         for offset in (-.08, -.04, 0., .04, .08)})
    rows = []
    for lead in candidates:
        row = replay(("timing_calibration", vars(Trial(
            CALIBRATION_SEED, speed, height, 0., "platform", lead, press_tick=272,
            wall_at=floor["press_x_m"]+lead))))
        rows.append(row)
    best = max(rows, key=score)
    center = best["lead"]
    edge = best["wall_at"]
    original = replay(("old_085", vars(Trial(
        CALIBRATION_SEED, speed, height, 0., "platform", .85, press_tick=272, wall_at=edge))))
    tests = []
    for hold, seed, offset in ATTEMPTS:
        for dr in (0., 1.):
            tests.append(replay(("paired", vars(Trial(seed, speed, height, dr, "platform",
                                                    max(.16, center+offset), press_tick=272,
                                                    hold_ticks=hold, wall_at=edge)))))
    for hold in (10, 20, 30, 40, 46, 50):
        trial = Trial(611, speed, height, 0., "platform", center, press_tick=272, hold_ticks=hold, wall_at=edge)
        tests.append(replay(("same_press_vary_hold", vars(trial))))
    if speed==2. and height==.42:
        for hold in (42, 46, 50):
            trial = Trial(107, speed, height, 0., "platform", center, press_tick=272, hold_ticks=hold, wall_at=edge)
            tests.append(replay(("r2_2ms_example_retimed", vars(trial))))
    valid_leads = [row["lead"] for row in rows if row["obstacle_pass_physical"]]
    record = dict(speed=speed, height=height, prior_m=prior, geometry=geometry, floor=compact(floor),
                  center_m=center, wall_at=edge, calibration_best=best, old_085=original,
                  physical_leads_m=valid_leads, calibration_rows=rows)
    print(speed, height, round(center, 3), best["obstacle_pass_physical"],
          sum(row["strict_direct"] for row in tests), flush=True)
    return record, tests


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--effective", type=Path, default=Path("evidence/jump360_r3/probe/TRAINING_TIMING.json"))
    parser.add_argument("--workers", type=int, default=10)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    checkpoint = HERE/args.checkpoint
    prior = read_json(HERE/args.effective)["platform"]
    tasks = [(speed, height, prior[i][j]) for i, speed in enumerate(SPEEDS) for j, height in enumerate(HEIGHTS)]
    with Pool(args.workers, initializer=initialize, initargs=(checkpoint,)) as pool:
        output = pool.map(calibrate, tasks)
    rows = [row for _, results in output for row in results]
    json_save(args.out/"RETIME_400HZ.json", dict(
        physics_hz=400, calibration_seed=CALIBRATION_SEED, holdouts=ATTEMPTS, key_hold_ticks=HOLD_TICKS,
        paired_timing="same holdout speeds, stance heights, key durations, DR seeds and timing offsets",
        checkpoint=str(args.checkpoint), sha256=sha(checkpoint), cases=[item for item, _ in output],
        trials=rows, **aggregate(rows)))


if __name__ == "__main__":
    main()

