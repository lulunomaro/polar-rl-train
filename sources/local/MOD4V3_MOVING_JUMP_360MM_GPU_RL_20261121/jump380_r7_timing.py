"""Measure R7 run-up and derive press distances from native 400 Hz flat replays."""
from argparse import ArgumentParser
from multiprocessing import Pool
from pathlib import Path

import torch

from jump360_r3_policy import R3Control
from jump360_scene import json_save, sha
from jump380_r4_calibrate import SPEED_GRID, STANCE_GRID, geometry_window
from jump380_r6_policy import load_policy as load_r6
from jump380_r6_replay import Trial, run_trial
from jump380_r6_scene import HEIGHTS, KINDS, LENGTHS, Jump380Plant
from jump380_r7_policy import INITIAL, PARENT, RUN, load_policy

PLANT = MODEL = PARENT_MODEL = None


def initialize(checkpoint, cruise=False):
    global PLANT, MODEL, PARENT_MODEL
    torch.set_num_threads(1)
    PLANT = Jump380Plant()
    MODEL = load_policy(checkpoint)
    if cruise:
        PARENT_MODEL = load_r6(PARENT)


def cruise_sample(speed, height, actor):
    PLANT.setup(height)
    command = 0.
    velocity, measured_height = [], []
    for tick in range(250):
        command += ((speed if tick >= 30 else 0.) - command)/12.
        observation = PLANT.command(command, height, False)
        action = actor.drive_base(torch.from_numpy(observation)).numpy()
        PLANT.advance(action)
        if tick >= 175:
            velocity.append(float(PLANT.body_vx))
            measured_height.append(float(PLANT.d.qpos[2]))
        if PLANT.tilt_fault:
            break
    return dict(mean_vx_m_s=sum(velocity)/len(velocity) if velocity else None,
                mean_root_height_m=sum(measured_height)/len(measured_height) if measured_height else None,
                peak_tail_vx_m_s=max(velocity, default=None), frames=len(velocity)*8,
                fall=bool(PLANT.tilt_fault))


def measure_cruise(task):
    _, _, speed, height = task
    return dict(speed=speed, height=height,
                r6=cruise_sample(speed, height, PARENT_MODEL), r7=cruise_sample(speed, height, MODEL))


def lead_center(geometry, overhang, speed, training):
    low, high = geometry["landing_window_m"] if geometry else (None, None)
    approach = max(0., speed)
    safe = overhang + max(.38, .32 + .36*approach)
    if training:
        return max((low + .14) if low is not None else 0., .66 + .42*approach,
                   safe + .12 + .04 + .02*approach)
    if geometry and high >= low:
        return max(.18, (low + high)/2.)
    return max(safe, (low + .05) if low is not None else .66 + .42*approach)


def measure_jump(task):
    i, j, speed, height, training = task
    # The post-training timing seeds are separate from the acceptance grids.
    seed = (73800 if training else 74100) + 13*i + j
    flat, trace = run_trial(PLANT, R3Control(MODEL),
                            Trial(seed, speed, height, 0., press_tick=130+(i+3*j)%19, hold_ticks=40))
    # Flat replay has no wall, so recover the front extent from the press frame.
    front_x = trace[0].max_x if trace else flat["press_x_m"] + .29
    overhang = front_x - flat["press_x_m"]
    entries = {}
    for kind, obstacle_height, length in zip(KINDS[1:], HEIGHTS[1:], LENGTHS[1:]):
        geometry = geometry_window(flat, trace, obstacle_height, length if kind == "hurdle_380" else 0.)
        entries[kind] = dict(geometry=geometry, center_m=lead_center(
            geometry, overhang, flat["press_vx_m_s"], training))
    return dict(speed=speed, height=height, overhang_m=overhang, flat=flat, obstacles=entries)


def calibrate(checkpoint, workers, training=False):
    tasks = [(i, j, speed, height, training) for i, speed in enumerate(SPEED_GRID)
             for j, height in enumerate(STANCE_GRID)]
    with Pool(workers, initializer=initialize, initargs=(checkpoint,)) as pool:
        rows = list(pool.imap(measure_jump, tasks))
    n = len(STANCE_GRID)
    tables = {kind: [[rows[i*n+j]["obstacles"][kind]["center_m"] for j in range(n)]
                     for i in range(len(SPEED_GRID))] for kind in KINDS[1:]}
    return dict(checkpoint_sha256=sha(checkpoint), physics_hz=400, training=training,
                speeds=SPEED_GRID, heights=STANCE_GRID, cases=rows, **tables)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=INITIAL)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--mode", choices=("training", "acceptance", "cruise"), required=True)
    args = parser.parse_args()
    if args.mode == "cruise":
        tasks = [(i, j, speed, h) for i, speed in enumerate(SPEED_GRID)
                 for j, h in enumerate((.24, .28, .32, .36, .39, .42))]
        with Pool(args.workers, initializer=initialize, initargs=(args.checkpoint, True)) as pool:
            rows = list(pool.imap(measure_cruise, tasks))
        for key in ("r6", "r7"):
            average = sum(abs(row[key]["mean_vx_m_s"] - row["speed"]) for row in rows)/len(rows)
            print(key, "total command MAE", round(average, 4))
        out = dict(physics_hz=400, seconds_per_case=5., rows=rows,
                   checkpoint_sha256=sha(args.checkpoint), parent_sha256=sha(PARENT))
    else:
        out = calibrate(args.checkpoint, args.workers, training=args.mode == "training")
        print(args.mode, [(kind, round(min(map(min, out[kind])), 3),
                           round(max(map(max, out[kind])), 3)) for kind in KINDS[1:]], flush=True)
    json_save(args.out, out)


if __name__ == "__main__":
    main()
