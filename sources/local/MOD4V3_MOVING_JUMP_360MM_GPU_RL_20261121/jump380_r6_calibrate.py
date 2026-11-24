"""Scan fixed walls after measuring the R6 initial actor's straight run-up."""
from argparse import ArgumentParser
from dataclasses import replace
from multiprocessing import Pool

import torch

from jump360_r3_policy import R3Control
from jump360_scene import json_save, sha
from jump380_r4_calibrate import SPEED_GRID, STANCE_GRID, geometry_window, score
from jump380_r6_policy import INITIAL, RUN, load_policy
from jump380_r6_replay import Trial, run_trial
from jump380_r6_scene import HEIGHTS, KINDS, LENGTHS, Jump380Plant, prepare_scene

OFFSETS = (-.12, -.06, 0., .06, .12)
PLANT = POLICY = None


def initialize():
    global PLANT, POLICY
    torch.set_num_threads(1)
    PLANT = Jump380Plant()
    POLICY = R3Control(load_policy(INITIAL))


def calibrate(task):
    i, j, speed, stance = task
    trial = Trial(63800 + 11*i + j, speed, stance, 0., press_tick=130 + (i + 3*j) % 19, hold_ticks=40)
    flat, trace = run_trial(PLANT, POLICY, trial)
    cells = {}
    for kind, height, length in zip(KINDS[1:], HEIGHTS[1:], LENGTHS[1:]):
        geom = geometry_window(flat, trace, height, length if kind == "hurdle_380" else 0.)
        if geom:
            first, last = geom["landing_window_m"]
            center = (first + last)/2. if last >= first else first + .015
        else:
            center = .25 + .21*speed
        center = max(.17, center)
        wall_at = flat["press_x_m"] + center
        scan = []
        for offset in OFFSETS:
            lead = max(.07, center + offset)
            result, _ = run_trial(PLANT, POLICY, replace(trial, kind=kind, wall_at=wall_at, lead=lead))
            scan.append(dict(offset_m=offset, **result))
        best = max(scan, key=lambda row: (row["course_qualified"], *score(row), -abs(row["offset_m"])))
        measured_window = best["obstacle_pass_physical"] or (
            best["course_qualified"] and best["positive_crossing_during_main_flight"] and best["wall_face_free"])
        cells[kind] = dict(lead_m=best["lead"] if measured_window else center, geometry_window=geom, scan=scan,
                           selected_from_scan=measured_window)
    return dict(speed=speed, height=stance, flat=flat, obstacles=cells)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=14)
    args = parser.parse_args()
    prepare_scene(False)
    tasks = [(i, j, speed, height) for i, speed in enumerate(SPEED_GRID) for j, height in enumerate(STANCE_GRID)]
    rows = []
    with Pool(args.workers, initializer=initialize) as pool:
        for row in pool.imap(calibrate, tasks):
            rows.append(row)
            print(row["speed"], row["height"], "run-up",
                  round(row["flat"]["approach_max_abs_y_m"], 4), round(row["flat"]["approach_max_abs_yaw_deg"], 2),
                  {name: round(cell["lead_m"], 3) for name, cell in row["obstacles"].items()}, flush=True)
    n = len(STANCE_GRID)
    table = {kind: [[rows[i*n+j]["obstacles"][kind]["lead_m"] for j in range(n)]
                    for i in range(len(SPEED_GRID))] for kind in KINDS[1:]}
    approaches = [trial for cell in rows for trial in (
        cell["flat"], *(row for obstacle in cell["obstacles"].values() for row in obstacle["scan"]))]
    json_save(RUN / "calibration/TIMING.json", dict(
        checkpoint_sha256=sha(INITIAL), physics_hz=400, speeds=SPEED_GRID, heights=STANCE_GRID,
        scan_offsets_m=OFFSETS, flat_approach_max_abs_y_m=max(r["flat"]["approach_max_abs_y_m"] for r in rows),
        flat_approach_max_abs_yaw_deg=max(r["flat"]["approach_max_abs_yaw_deg"] for r in rows),
        all_scan_approach_max_abs_y_m=max(r["approach_max_abs_y_m"] for r in approaches),
        all_scan_approach_max_abs_yaw_deg=max(r["approach_max_abs_yaw_deg"] for r in approaches),
        cases=rows, **table))


if __name__ == "__main__":
    main()
