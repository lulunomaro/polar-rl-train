"""Remeasure fixed-wall jump timing with the archived R4 eight-minute actor."""
from argparse import ArgumentParser
from dataclasses import replace
import json
from multiprocessing import Pool
from pathlib import Path

import torch

from jump360_r3_policy import R3Control, load_policy
from jump360_scene import json_save, sha
from jump380_r4_calibrate import SPEED_GRID, STANCE_GRID, geometry_window, score
from jump380_r4_replay import Trial, run_trial
from jump380_r5_scene import HEIGHTS, KINDS, LENGTHS, PARENT, PARENT_SHA, RUN, Jump380Plant, prepare_scene

SCAN_OFFSETS = (-.18, -.12, -.06, 0., .06, .12, .18)
PLANT = POLICY = None


def initialize(checkpoint):
    global PLANT, POLICY
    torch.set_num_threads(1)
    PLANT = Jump380Plant()
    POLICY = R3Control(load_policy(checkpoint))


def scan_case(task):
    attempt, prior = task
    flat, flight = run_trial(PLANT, POLICY, attempt)
    cells = {}
    for kind, height, length in zip(KINDS[1:], HEIGHTS[1:], LENGTHS[1:]):
        geom = geometry_window(flat, flight, height, length if kind == "hurdle_380" else 0.)
        center = prior.get(kind)
        if center is None:
            if geom:
                first, last = geom["landing_window_m"]
                center = max(.18, (first + last) / 2. if last >= first else first + .015)
            else:
                center = .24 + attempt.speed * .21
        wall = flat["press_x_m"] + center
        scan = []
        for delta in SCAN_OFFSETS:
            lead = max(.07, center + delta)
            row, _ = run_trial(PLANT, POLICY, replace(attempt, kind=kind, lead=lead, wall_at=wall))
            scan.append(dict(offset_m=delta, **row))
        best = max(scan, key=lambda row: (*score(row), -abs(row["offset_m"])))
        improvement = best["obstacle_pass_physical"] or (
            best["positive_crossing_during_main_flight"] and best["wall_face_free"]
            and best["both_wheels_top_beyond_samples"] > 0)
        # Give an archived physically demonstrated center priority over weaker new crossings.
        center_proven = prior.get(kind + "_proven", False)
        select = best["obstacle_pass_physical"] or (improvement and not center_proven)
        cells[kind] = dict(prior_m=center, selected_m=best["lead"] if select else center,
                           source="fixed_wall_scan" if select else "parent_prior",
                           archive_has_physical_pass=center_proven, flight_window=geom, trials=scan)
    return dict(speed=attempt.speed, height=attempt.height, flat=flat, obstacles=cells)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=RUN / "calibration")
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    checksum = sha(PARENT)
    if checksum != PARENT_SHA:
        raise ValueError("R4 eight-minute checkpoint checksum mismatch")
    archive = PARENT.parents[1] / "calibration/TIMING_008M.json"
    scans = PARENT.parents[1] / "windows_008m/CPU_400HZ.json"
    prior = json.loads(archive.read_text(encoding="utf-8"))
    archived_trials = json.loads(scans.read_text(encoding="utf-8"))
    if prior["checkpoint_sha256"] != checksum or archived_trials["sha256"] != checksum:
        raise ValueError("Archived timing did not use the R5 parent")
    passed = {(row["kind"], row["speed"], row["height"]) for row in archived_trials["trials"]
              if row["obstacle_pass_physical"]}
    prepare_scene(False)
    tasks = []
    for i, speed in enumerate(SPEED_GRID):
        for j, height in enumerate(STANCE_GRID):
            trial = Trial(935 + 7*i + j, speed, height, 0., press_tick=124 + (i + 3*j) % 16, hold_ticks=38)
            cell = {kind: prior[kind][i][j] for kind in KINDS[1:3]}
            cell.update({kind + "_proven": (kind, speed, height) in passed for kind in cell})
            tasks.append((trial, cell))
    rows = []
    with Pool(args.workers, initializer=initialize, initargs=(PARENT,)) as pool:
        for row in pool.imap(scan_case, tasks, chunksize=1):
            rows.append(row)
            print(row["speed"], row["height"],
                  {kind: round(cell["selected_m"], 3) for kind, cell in row["obstacles"].items()},
                  flush=True)
    cols = len(STANCE_GRID)
    tables = {kind: [[rows[i*cols+j]["obstacles"][kind]["selected_m"] for j in range(cols)]
                     for i in range(len(SPEED_GRID))] for kind in KINDS[1:]}
    json_save(args.out / "TIMING.json", dict(
        checkpoint_sha256=checksum, physics_hz=400, speeds=SPEED_GRID, heights=STANCE_GRID,
        fixed_wall_offsets_m=SCAN_OFFSETS, archived_timing_sha256=sha(archive),
        archived_scan_sha256=sha(scans), cases=rows, **tables))


if __name__ == "__main__":
    main()
