"""Search measured, fixed-wall press positions for a replayable platform example."""
from argparse import ArgumentParser
from dataclasses import replace
from multiprocessing import Pool
from pathlib import Path

from jump360_scene import HERE, json_save, sha
from jump380_r4_calibrate import SPEED_GRID, STANCE_GRID, geometry_window
from jump380_r4_evaluate import aggregate, initialize, read_json, representative
import jump380_r4_evaluate as engine
from jump380_r4_replay import Trial, run_trial
from jump380_r4_scene import PLATFORMS, RUN, prepare_scene

OFFSETS = (0., -.04, .04, -.08, .08, -.12, .12)


def search(case):
    speed, stance, dr, hold, seed = case
    attempt = Trial(seed, speed, stance, dr, press_tick=124 + seed % 29, hold_ticks=hold)
    flat, trace = run_trial(engine.PLANT, engine.POLICY, attempt)
    rows, windows = [flat], {}
    for kind, wall_height in zip(PLATFORMS, (.380, .360)):
        geometry = geometry_window(flat, trace, wall_height, 0.)
        windows[kind] = geometry
        if geometry is None:
            continue
        first, last = geometry["landing_window_m"]
        center = (first + last) / 2. if last >= first else first + .01
        center = max(.13, center)
        # Fix each box at reset. Moving its starting location lets the operator
        # press at the measured gait state without moving a live obstacle.
        for offset in OFFSETS:
            lead = max(.07, round(center + offset, 3))
            trial = replace(attempt, kind=kind, lead=lead, wall_at=flat["press_x_m"] + lead)
            replay, _ = run_trial(engine.PLANT, engine.POLICY, trial)
            replay["searched_offset_m"] = offset
            rows.append(replay)
    return rows, windows


def exact_walls(checkpoint, out, source):
    data = read_json(source)
    rows = []
    torch_model = engine.load_policy(checkpoint)
    engine.torch.set_num_threads(1)
    plant = engine.Jump380Plant()
    policy = engine.R3Control(torch_model)
    for kind in PLATFORMS:
        best = representative(data["trials"], kind)
        if not best["obstacle_pass_physical"]:
            continue
        trial = engine.trial_from(best)
        for hold in (12, 20, 30, 40, 50, trial.hold_ticks):
            for delta in OFFSETS:
                variant = replace(trial, lead=trial.lead + delta, hold_ticks=hold)
                row, _ = run_trial(plant, policy, variant)
                row["resampled_offset_m"] = delta
                rows.append(row)
    json_save(out/"FIXED_WALL_WINDOW.json", dict(checkpoint=str(checkpoint), sha256=sha(checkpoint),
                                               profile="resampled_representative", trials=rows))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--resample", type=Path)
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    if args.resample:
        exact_walls(args.checkpoint, args.out, args.resample)
        return
    prepare_scene(False)
    cases = [(speed, stance, dr, hold, 44200 + 39*i + 11*j + 2*k + int(dr))
             for i, speed in enumerate(SPEED_GRID)
             for j, stance in enumerate(STANCE_GRID)
             for k, hold in enumerate((20, 34, 50))
             for dr in (0., 1.)]
    rows, geometry = [], []
    with Pool(args.workers, initializer=initialize, initargs=(args.checkpoint,)) as pool:
        for case, (trials, windows) in zip(cases, pool.imap(search, cases, chunksize=2)):
            rows.extend(trials)
            geometry.append(dict(case=case, windows=windows))
    outcome = aggregate(rows)
    json_save(args.out/"CPU_400HZ.json", dict(
        physics_hz=400, checkpoint=str(args.checkpoint), sha256=sha(args.checkpoint),
        profile="timing_search", geometry=geometry, by_kind_dr=outcome, trials=rows))
    for result in outcome:
        print({key: result[key] for key in ("kind", "dr", "trials", "qualified", "physical", "strict_direct")},
              flush=True)


if __name__ == "__main__":
    main()
