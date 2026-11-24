"""Measure the parent flight window and replay fixed 360/380 mm obstacles."""
from argparse import ArgumentParser
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import torch

from eval_moving_jump_360mm import main_flight_bounds
from jump360_r3_policy import R3Control, load_policy
from jump360_scene import json_save, sha
from jump380_r4_replay import Trial, run_trial
from jump380_r4_scene import HEIGHTS, KINDS, LENGTHS, PARENT, PARENT_SHA, RUN, Jump380Plant

SPEED_GRID = (.8, 1., 1.2, 1.4, 1.6, 1.8, 2.)
STANCE_GRID = (.24, .32, .42)
TRAIN_CASE_SEED = 935
HOLD = 38
PLANT = POLICY = None


def initialize(checkpoint):
    global PLANT, POLICY
    torch.set_num_threads(1)
    PLANT = Jump380Plant()
    POLICY = R3Control(load_policy(checkpoint))


def geometry_window(row, trace, height, width):
    start, stop = main_flight_bounds(trace)
    rise = [i for i in range(start, stop) if trace[i].lowest > height]
    if not rise:
        return None
    start_high, end_high = rise[0], rise[-1]
    low_front = "low_front_380" if height == .380 else "low_front_360"
    nose = max((getattr(f, low_front) for f in trace[:start_high]
                if getattr(f, low_front) is not None), default=row["press_x_m"])
    last = trace[end_high]
    origin = row["press_x_m"]
    return dict(
        start_high_s=trace[start_high].time - trace[0].time + .0025,
        end_high_s=last.time - trace[0].time + .0025,
        leading_below_height_x_m=nose - origin,
        trailing_tire_x_at_end_m=last.trailing_tire_x - origin,
        lagging_tire_x_at_end_m=last.lagging_wheel_x - origin,
        whole_car_rear_x_at_end_m=last.min_x - origin,
        landing_window_m=[nose - origin, last.lagging_wheel_x - origin - .02 - width],
    )


def score(row):
    return (row["strict_direct"], row["obstacle_pass_physical"],
            row["positive_crossing_during_main_flight"], row["both_wheels_top_beyond_samples"],
            row["wall_face_free"], row["wall_margin_m"] if row["wall_margin_m"] is not None else -9.,
            row["flight_peak_all_m"])


def calibrate(case):
    speed, stance = case
    flat, trace = run_trial(PLANT, POLICY, Trial(TRAIN_CASE_SEED, speed, stance, 0., hold_ticks=HOLD))
    cells = {}
    for kind, height, length in zip(KINDS[1:], HEIGHTS[1:], LENGTHS[1:]):
        width = length if kind == "hurdle_380" else 0.
        geometry = geometry_window(flat, trace, height, width)
        if geometry:
            low, high = geometry["landing_window_m"]
            center = (low + high) / 2. if high >= low else low + .015
        else:
            center = .24 + speed * .21
        center = max(.18, center)
        sweep = []
        for offset in (-.10, -.05, 0., .05, .10):
            lead = max(.10, center + offset)
            trial = Trial(TRAIN_CASE_SEED, speed, stance, 0., kind, lead, hold_ticks=HOLD,
                          wall_at=flat["press_x_m"] + center)
            result, _ = run_trial(PLANT, POLICY, trial)
            sweep.append(result)
        best = max(sweep, key=score)
        proven = [row["lead"] for row in sweep if row["obstacle_pass_physical"]]
        # A physically measured pass takes precedence over the geometric estimate.
        # Keep geometric timing when none of the attempted wall replays landed.
        selected = best["lead"] if proven else center
        cells[kind] = dict(window=geometry, lead_center_m=selected, pass_leads_m=proven, trials=sweep)
    print(f"{speed:.2f}/{stance:.2f} {flat['flight_peak_all_m']:.3f} m "
          + " ".join(f"{kind}={value['lead_center_m']:.3f} ({len(value['pass_leads_m'])} pass)"
                     for kind, value in cells.items()), flush=True)
    return dict(speed=speed, height=stance, flat=flat, obstacles=cells)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=PARENT)
    parser.add_argument("--out", type=Path, default=RUN / "calibration")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    checksum = sha(args.checkpoint)
    if args.checkpoint == PARENT and checksum != PARENT_SHA:
        raise ValueError("R3 four-minute checkpoint checksum mismatch")
    tasks = [(speed, height) for speed in SPEED_GRID for height in STANCE_GRID]
    with Pool(args.workers, initializer=initialize, initargs=(args.checkpoint,)) as pool:
        results = list(pool.imap(calibrate, tasks))
    tables = {kind: np.array([row["obstacles"][kind]["lead_center_m"] for row in results])
              .reshape(len(SPEED_GRID), len(STANCE_GRID)).tolist() for kind in KINDS[1:]}
    json_save(args.out / "TIMING.json", dict(
        checkpoint_sha256=checksum, physics_hz=400, speeds=SPEED_GRID, heights=STANCE_GRID,
        fixed_walls=True, measured_hold_ticks=HOLD, cases=results, **tables))


if __name__ == "__main__":
    main()
