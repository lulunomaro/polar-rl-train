"""Sweep manual press timing at fixed wall positions from the R6/R7 replays."""

from argparse import ArgumentParser
from dataclasses import replace
from multiprocessing import Pool
from pathlib import Path

import jump380_r8_evaluate as evaluation
from jump360_scene import HERE, json_save, sha
from jump380_r4_evaluate import aggregate, read_json, trial_from
from jump380_r6_replay import run_trial


def sweep(example):
    trial = trial_from(example)
    floor, _ = run_trial(evaluation.PLANT, evaluation.POLICY,
                        replace(trial, kind="flat", press_tick=example["trigger_tick"]))
    # Shift the center with the measured R8 run-up at the reference key frame.
    # Every replay within a sweep holds the wall position and disturbance fixed.
    center = trial.wall_at - floor["press_x_m"]
    rows = {}
    for offset_cm in range(-24, 25, 2):
        lead = max(.32, center + .01*offset_cm)
        row, _ = run_trial(evaluation.PLANT, evaluation.POLICY, replace(trial, lead=lead))
        rows.setdefault(row["trigger_tick"], row)
    return list(rows.values())


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    references = []
    for round_name in ("jump380_r6", "jump380_r7"):
        examples = read_json(HERE / "evidence" / round_name / "VIDEO.json")
        references.extend(video["case"] for video in examples["videos"]
                          if video["case"]["strict_direct"])
    with Pool(args.workers, initializer=evaluation.initialize, initargs=(args.checkpoint,)) as pool:
        rows = [run for group in pool.imap(sweep, references) for run in group]
    report = dict(sha256=sha(args.checkpoint), physics_hz=400, policy_hz=50,
                  protocol="fixed wall replays at R6/R7 reference speeds, stances and seeds",
                  by_scene=aggregate(rows), trials=rows)
    json_save(args.out / "CPU_400HZ.json", report)
    print([(row["kind"], row["dr"], row["trials"], row["strict_direct"], row["physical"])
           for row in report["by_scene"]], flush=True)


if __name__ == "__main__":
    main()
