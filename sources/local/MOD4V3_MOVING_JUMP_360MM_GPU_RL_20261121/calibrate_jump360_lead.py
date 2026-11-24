"""Measure the wheel-at-apex press distance and replay it against fixed solids."""
from argparse import ArgumentParser
import json
from multiprocessing import Pool
from pathlib import Path

import torch

from eval_moving_jump_360mm import MeasuredPlant, NeuralControl, Trial, calibrated_lead, clearance_score, run_trial
from jump360_scene import HERE, HOLD_TICKS, json_save, model_from, sha

SPEEDS = (.6, 1., 1.4, 1.8, 2.)
HEIGHTS = (.22, .32, .42)
PLANT = None
POLICY = None
TEACHER = None


def initialize(checkpoint, teacher):
    global PLANT, POLICY, TEACHER
    torch.set_num_threads(1)
    PLANT = MeasuredPlant()
    POLICY = NeuralControl(model_from(checkpoint))
    TEACHER = {(row["speed"], row["height"]): row for row in teacher["trials"]
               if row["seed"] == 141 and row["dr"] == 0.}


def calibrate(case):
    speed, height = case
    floor, _, _, _ = run_trial(PLANT, POLICY, Trial(9, speed, height, 0.))
    uses_floor = floor["flight_peak_all_m"] >= .30 and floor["forward_running"]
    apex = floor if uses_floor else TEACHER[case]
    chosen = {}
    for kind in ("platform", "hurdle"):
        mid = calibrated_lead(apex, kind)
        candidates = []
        for offset in (0., -.04, .04, -.08, .08, -.12, .12, -.16, .16):
            lead = max(.12, mid+offset)
            result, _, _, _ = run_trial(PLANT, POLICY, Trial(9, speed, height, 0., kind, lead,
                                                             wall_at=floor["press_x_m"]+lead))
            candidates.append(result)
        selected = max(candidates, key=lambda row: clearance_score(row) + (
            row["wall_margin_m"] if row["wall_margin_m"] is not None else -.360,))
        # Keep the measured apex timing in bins where the warm policy cannot yet clear.
        lead = selected["lead"] if selected["obstacle_pass_physical"] else mid
        chosen[kind] = dict(lead_m=lead, center_at_apex_m=mid, selected=selected, sweep=candidates)
    return dict(speed=speed, height=height, apex_source="warm_policy" if uses_floor else "offline_demonstration",
                apex_after_press_s=apex["apex_after_press_s"], speed_at_press_m_s=apex["press_vx_m_s"],
                warm_flat=floor, **chosen)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--teacher", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=5)
    args = parser.parse_args()
    checkpoint = HERE/args.checkpoint
    teacher = json.loads((HERE/args.teacher).read_text(encoding="utf-8"))
    with Pool(args.workers, initializer=initialize, initargs=(checkpoint, teacher)) as pool:
        cases = pool.map(calibrate, [(v, h) for v in SPEEDS for h in HEIGHTS])
    matrices = {kind: [[cases[i*len(HEIGHTS)+j][kind]["lead_m"] for j in range(len(HEIGHTS))]
                       for i in range(len(SPEEDS))] for kind in ("platform", "hurdle")}
    json_save(args.out, dict(speeds=SPEEDS, heights=HEIGHTS, jitter_m=.08, key_hold_ticks=HOLD_TICKS,
                             checkpoint_sha256=sha(checkpoint), physics_hz=400, cases=cases, **matrices))
    for row in cases:
        print(row["speed"], row["height"], row["apex_source"], row["apex_after_press_s"],
              [(kind, round(row[kind]["lead_m"], 3), row[kind]["selected"]["obstacle_pass_physical"])
               for kind in matrices], flush=True)


if __name__ == "__main__":
    main()
