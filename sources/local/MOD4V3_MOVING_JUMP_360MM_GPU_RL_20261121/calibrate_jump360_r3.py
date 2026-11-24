"""Measure R2's 400 Hz clearance window and validate it with a fixed solid wall."""
from argparse import ArgumentParser
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import torch

from eval_moving_jump_360mm import NeuralControl, Trial, main_flight_bounds, run_trial
from jump360_scene import HERE, HOLD_TICKS, HURDLE_THICKNESS, WALL_HEIGHT, JumpPlant, geom_extent, json_save, model_from, sha

PARENT_R2 = HERE / "evidence/jump360_r2/model_final.pt"
R2_SHA = "78519d2b8c2f8f5c6c1e804069d55e331c19cb07a62229a61d6cca7ada687187"
SPEEDS = (.60, .80, 1.00, 1.20, 1.40, 1.60, 1.80, 2.00)
HEIGHTS = (.22, .32, .42)
PLANT = POLICY = None


class TimingPlant(JumpPlant):
    def frame(self):
        frame = super().frame()
        matrix = self.d.geom_xmat[self.measured_gids].reshape(-1, 3, 3)
        centers = self.d.geom_xpos[self.measured_gids]
        radius_x = geom_extent(self.sizes, matrix[:, 0], 10)
        bottom = centers[:, 2] - geom_extent(self.sizes, matrix[:, 2], 10)
        front = centers[:, 0] + radius_x
        low = bottom <= WALL_HEIGHT
        frame.tire_front = float(front[:2].max())
        frame.tire_rear = float((centers[:2, 0] - radius_x[:2]).min())
        frame.low_front = float(front[low].max()) if low.any() else None
        return frame


def initialize(checkpoint):
    torch.set_num_threads(1)
    global PLANT, POLICY
    PLANT = TimingPlant()
    POLICY = NeuralControl(model_from(checkpoint))


def geometry_window(row, trace):
    start, stop = main_flight_bounds(trace)
    origin = row["press_x_m"]
    high = [i for i in range(start, stop) if trace[i].tire_low > WALL_HEIGHT]
    if not high:
        return dict(whole_car_window_m=None)
    rise, descent = high[0], high[-1]
    apex = max(trace[start:stop], key=lambda frame: frame.lowest)
    nose = max((frame.low_front for frame in trace[:rise + 1] if frame.low_front is not None), default=origin)
    rear = max(frame.min_x for frame in trace[rise:descent + 1])
    return dict(
        front_tire_rise_x_m=trace[rise].tire_front - origin,
        front_tire_rise_after_press_s=trace[rise].time-trace[0].time+.0025,
        rear_tire_descent_x_m=trace[descent].tire_rear - origin,
        rear_tire_descent_after_press_s=trace[descent].time-trace[0].time+.0025,
        lagging_tire_center_descent_x_m=trace[descent].lagging_wheel_x - origin,
        whole_car_window_m=(nose-origin, rear-origin),
        apex_front_m=apex.max_x-origin,
        apex_rear_m=apex.min_x-origin,
    )


def replay_score(row):
    return (
        row["qualified"] and row["wall_crossing_in_main_flight"],
        row["obstacle_pass_physical"] and row["wall_crossing_in_main_flight"],
        row["wall_face_free"] and row["wall_crossing_in_main_flight"],
        row["wall_face_free"] and not row["fall"],
        row["supported_samples"],
        -row["wall_face_force_n"],
        row["wall_margin_m"] if row["wall_margin_m"] is not None else -1.,
    )


def compact(row):
    fields = (
        "seed", "speed", "height", "dr", "kind", "hold_ticks", "lead", "wall_at", "press_x_m", "press_vx_m_s",
        "press_gap_from_leading_geom_m", "triggered", "trigger_tick", "qualified", "obstacle_pass_physical",
        "fall", "wall_face_force_n", "wall_margin_m", "wall_crossing_in_main_flight", "supported_samples",
        "flight_peak_all_m", "flight_pitch_deg", "landed_running", "forward_running", "final_vx_m_s",
        "min_charge_vx_m_s", "first_touch_after_press_s", "flight_start_after_press_s",
        "apex_lagging_wheel_after_press_m", "apex_after_press_s",
    )
    return {key: row[key] for key in fields}


def imitation(row, observations, actions):
    if row["first_touch_after_press_s"] is None or not row["triggered"]:
        return None
    start = row["trigger_tick"]
    contact = start + int(np.ceil(row["first_touch_after_press_s"]/.02))
    # The actor target is the actual R2 action for the approach and original jump.
    # The gate label ends at first physical support.
    return observations, actions, np.arange(len(observations))-start, contact-start


def calibrate(case):
    speed, height = case
    base, trace, obs, acts = run_trial(PLANT, POLICY, Trial(9, speed, height, 0.), collect_actions=True)
    demos = [imitation(base, obs, acts)]
    # Extra flat trajectories vary the proprioception used during gate initialization.
    for seed, dr in ((155, 0.), (179, 1.), (201, 1.)):
        row, _, obs, acts = run_trial(PLANT, POLICY, Trial(seed, speed, height, dr), collect_actions=True)
        if not row["fall"] and row["flight_peak_all_m"] >= .385:
            demos.append(imitation(row, obs, acts))
    geom = geometry_window(base, trace)
    apex = base["apex_lagging_wheel_after_press_m"]
    if apex is None:
        apex = .35*speed
    out = dict(speed=speed, height=height, geometry=geom, floor=compact(base))
    for kind in ("platform", "hurdle"):
        width = 0. if kind == "platform" else HURDLE_THICKNESS
        centers = [apex-width/2]
        window = geom["whole_car_window_m"]
        if window:
            earliest, latest = window[0], window[1]-width
            centers.extend([earliest, (earliest+latest)*.5, latest])
        candidates = {round(max(.015, x + delta), 3) for x in centers
                      for delta in (0., -.04, .04, -.08, .08)}
        candidates.update((round(max(.015, apex-.14), 3), round(apex+.14, 3)))
        rows = []
        for lead in sorted(candidates):
            trial = Trial(9, speed, height, 0., kind, lead, hold_ticks=HOLD_TICKS,
                          wall_at=base["press_x_m"]+lead)
            row, _, _, _ = run_trial(PLANT, POLICY, trial)
            rows.append(row)
        selected = max(rows, key=replay_score)
        center = selected["lead"]
        if not selected["wall_crossing_in_main_flight"] and not selected["obstacle_pass_physical"]:
            center = max(.015, (.5*(window[0]+window[1]-width) if window else apex-width/2))
        good = [r["lead"] for r in rows if r["obstacle_pass_physical"] and r["wall_crossing_in_main_flight"]]
        out[kind] = dict(lead_m=center, pass_window_m=[min(good), max(good)] if good else None,
                         selected=compact(selected), sweep=[compact(r) for r in rows])
        if selected["obstacle_pass_physical"]:
            trial = Trial(**{key: selected[key] for key in vars(Trial(0, 0., 0., 0.))})
            row, _, obs, acts = run_trial(PLANT, POLICY, trial, collect_actions=True)
            demos.append(imitation(row, obs, acts))
    print(f"{speed:.2f} {height:.2f} apex {apex:+.3f} geometry {geom['whole_car_window_m']} "
          f"platform {out['platform']['lead_m']:.3f} {out['platform']['pass_window_m']} "
          f"hurdle {out['hurdle']['pass_window_m']}", flush=True)
    return out, [dataset for dataset in demos if dataset is not None]


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    if sha(PARENT_R2) != R2_SHA:
        raise ValueError("R2 checkpoint hash mismatch")
    args.out.mkdir(parents=True, exist_ok=True)
    with Pool(args.workers, initializer=initialize, initargs=(PARENT_R2,)) as pool:
        measured = pool.map(calibrate, [(v, h) for v in SPEEDS for h in HEIGHTS])
    cases = [row for row, _ in measured]
    matrices = {kind: [[cases[i*len(HEIGHTS)+j][kind]["lead_m"] for j in range(len(HEIGHTS))]
                       for i in range(len(SPEEDS))] for kind in ("platform", "hurdle")}
    json_save(args.out/"TIMING_R2_MEASURED.json",
              dict(speeds=SPEEDS, heights=HEIGHTS, key_hold_ticks=HOLD_TICKS, checkpoint_sha256=R2_SHA,
                   reference="fixed wall edge minus root x at the key press", physics_hz=400, cases=cases, **matrices))
    samples = [sample for _, demos in measured for sample in demos]
    np.savez_compressed(args.out/"R2_GATE_INIT.npz", **{
        f"{name}_{i}": array for i, sample in enumerate(samples)
        for name, array in zip(("obs", "act", "relative", "contact"), sample, strict=True)
    })


if __name__ == "__main__":
    main()

