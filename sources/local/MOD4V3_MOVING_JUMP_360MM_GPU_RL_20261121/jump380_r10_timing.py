"""Measure the R10 cruise and press geometry using native 400 Hz MuJoCo."""

from argparse import ArgumentParser
from multiprocessing import Pool
from pathlib import Path

from jump360_scene import json_save, sha
from jump380_r6_scene import HEIGHTS, KINDS, LENGTHS
from jump380_r8_timing import JITTER_HIGH_M, JITTER_LOW_M, PRESS_GAP_M, lead_center
from jump380_r10_policy import (CALIBRATION_KEY, EXPERIMENT, PARENT, PARENT_SHA, RUN,
                               SPEED_GRID, STANCE_GRID, TRAIN_SPEED_GRID, load_policy)

TRAIN_TIMING = RUN / "calibration/TRAIN_TIMING.json"
CRUISE_FILE = RUN / "calibration" / CALIBRATION_KEY
PLANT = MODEL = None


def initialize(checkpoint):
    global PLANT, MODEL
    import torch
    from jump380_r6_scene import Jump380Plant

    torch.set_num_threads(1)
    PLANT = Jump380Plant()
    MODEL = load_policy(checkpoint)


def measure_cruise(task):
    from jump360_r3_policy import R3Control

    speed, height = task
    actor = R3Control(MODEL)
    PLANT.setup(height)
    command = 0.
    tail = []
    for tick in range(250):
        command += ((speed if tick >= 30 else 0.) - command)/12.
        obs = PLANT.command(command, height, False)
        PLANT.advance(actor(PLANT, obs))
        if tick >= 175:
            tail.append(float(PLANT.body_vx))
        if PLANT.tilt_fault:
            break
    return dict(speed=speed, height=height, fall=bool(PLANT.tilt_fault), tail_ticks=len(tail),
                mean_vx_m_s=sum(tail)/len(tail) if tail else None,
                min_tail_vx_m_s=min(tail, default=None), max_tail_vx_m_s=max(tail, default=None))


def measure_geometry(task):
    from jump360_r3_policy import R3Control
    from jump380_r4_calibrate import geometry_window
    from jump380_r6_replay import Trial, run_trial

    i, j, speed, height, training = task
    seed = (73800 if training else 74100) + 13*i + j
    flat, trace = run_trial(PLANT, R3Control(MODEL),
                            Trial(seed, speed, height, 0., press_tick=130+(i+3*j)%19, hold_ticks=40))
    overhang = trace[0].max_x - flat["press_x_m"] if trace else .29
    cells = {}
    for kind, obstacle_height, length in zip(KINDS[1:], HEIGHTS[1:], LENGTHS[1:]):
        width = length if kind == "hurdle_380" else 0.
        cells[kind] = dict(geometry=geometry_window(flat, trace, obstacle_height, width))
    return dict(speed=speed, height=height, overhang_m=overhang, flat=flat, obstacles=cells)


def calibrate(checkpoint, workers, training=False):
    checksum = sha(checkpoint)
    if training and checksum != PARENT_SHA:
        raise ValueError("R10 training timing requires the pinned R8 checkpoint")
    speeds = TRAIN_SPEED_GRID if training else SPEED_GRID
    tasks = [(i, j, speed, height, training) for i, speed in enumerate(speeds)
             for j, height in enumerate(STANCE_GRID)]
    with Pool(workers, initializer=initialize, initargs=(checkpoint,)) as pool:
        rows = list(pool.imap(measure_geometry, tasks))
    tables = {}
    for kind in KINDS[1:]:
        measured = [row for row in rows if row["obstacles"][kind]["geometry"] is not None]
        if not measured:
            raise ValueError(f"No measured {kind} clearance window on the R10 timing grid")
        for row in rows:
            cell = row["obstacles"][kind]
            reference = row
            if cell["geometry"] is None:
                # For a missing window, start the scan at the nearest measured stance and speed.
                reference = min(measured, key=lambda r: abs(r["speed"]-row["speed"])/.4
                                + abs(r["height"]-row["height"])/.09)
                cell["center_reference"] = {key: reference[key] for key in ("speed", "height")}
            cell["center_m"] = lead_center(reference["obstacles"][kind]["geometry"])
            cell["center_source"] = "measured" if reference is row else "nearest_measured_grid_cell"
        centers = [row["obstacles"][kind]["center_m"] for row in rows]
        stride = len(STANCE_GRID)
        tables[kind] = [centers[i:i+stride] for i in range(0, len(centers), stride)]
        print(kind, f"{len(measured)}/{len(rows)} measured, lead {min(centers):.3f}–{max(centers):.3f} m",
              flush=True)
    return dict(experiment=EXPERIMENT, checkpoint_sha256=checksum, physics_hz=400, training=training,
                speeds=speeds, heights=STANCE_GRID, cases=rows, training_press_floor_m=PRESS_GAP_M,
                training_jitter_m=[JITTER_LOW_M, JITTER_HIGH_M],
                lead_center_rule="midpoint if high >= low, otherwise low + 0.035 m", **tables)


def cruise(checkpoint, workers):
    tasks = [(speed, height) for speed in TRAIN_SPEED_GRID for height in STANCE_GRID]
    tasks += [(speed, .38) for speed in (2.4, 2.8, 3.)]
    with Pool(workers, initializer=initialize, initargs=(checkpoint,)) as pool:
        rows = list(pool.imap(measure_cruise, tasks))
    target = [row for row in rows if row["speed"] == 2.8 and row["height"] in STANCE_GRID]
    passed = all(not row["fall"] and row["tail_ticks"] == 75 and 2.75 <= row["mean_vx_m_s"] <= 2.85
                 for row in target)
    print("2.8 m/s steady cruise", [(row["height"], row["mean_vx_m_s"]) for row in target],
          "passed", passed, flush=True)
    return dict(experiment=EXPERIMENT, checkpoint_sha256=sha(checkpoint), physics_hz=400,
                seconds_per_case=5., high_speed_target_passed=passed, rows=rows)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=PARENT)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--mode", choices=("cruise", "training", "acceptance"), required=True)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    if args.mode == "cruise":
        result = cruise(args.checkpoint, args.workers)
        json_save(args.out or CRUISE_FILE, result)
    else:
        training = args.mode == "training"
        result = calibrate(args.checkpoint, args.workers, training)
        json_save(args.out or (TRAIN_TIMING if training else RUN/"TIMING.json"), result)
