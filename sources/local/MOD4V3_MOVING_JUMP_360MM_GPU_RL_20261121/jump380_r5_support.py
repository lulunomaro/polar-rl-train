"""Training support criterion and CPU replay of the archived R4 landings."""
from collections import deque
import math

SUPPORT_FORCE_N = 1.
SUPPORT_WINDOW_TICKS = 15
MIN_SUPPORT_TICKS = 11
PHYSICS_STEPS_PER_TICK = 8
END_TICK = 115


def compare_support(trace, end_of_flight, trial, measurement):
    """Apply both training predicates to the same native physics frames."""
    edge = measurement["wall_edge_m"]
    window = deque(maxlen=SUPPORT_WINDOW_TICKS)
    streak = 0
    ticks = []
    for start in range(0, len(trace) - PHYSICS_STEPS_PER_TICK + 1, PHYSICS_STEPS_PER_TICK):
        samples = trace[start:start + PHYSICS_STEPS_PER_TICK]
        last = samples[-1]
        peaks = [max(frame.wheel_top_force[wheel] for frame in samples) for wheel in range(2)]
        upright = math.cos(math.radians(last.pitch)) * math.cos(math.radians(last.roll))
        can_land = (start + PHYSICS_STEPS_PER_TICK > end_of_flight
                    and last.lagging_wheel_x > edge + .02
                    and last.vx > .35 * trial.speed and upright > .95)
        old = can_land and min(last.wheel_top_force) > SUPPORT_FORCE_N
        new = can_land and min(peaks) > SUPPORT_FORCE_N
        streak = streak + 1 if old else 0
        window.append(new)
        ticks.append(dict(tick=len(ticks) + 1, time_s=last.time - trace[0].time + .0025,
                          wheel_top_peak_n=peaks, last_substep_top_n=last.wheel_top_force,
                          old_valid=old, new_valid=new, old_consecutive_ticks=streak,
                          new_supported_ticks=sum(window),
                          old_stable=streak >= 18, new_stable=sum(window) >= MIN_SUPPORT_TICKS,
                          whole_car_beyond=last.min_x > edge))
    terminal = ticks[END_TICK - 1]
    clean_forward_finish = (not measurement["fall"] and measurement["forward_running"]
                            and measurement["wall_face_free"] and measurement["charge_scrape_n"] < 1.
                            and terminal["whole_car_beyond"])
    return dict(case=measurement, ticks=ticks, compare_terminal_tick=END_TICK,
                old_valid_count=sum(t["old_valid"] for t in ticks),
                new_valid_count=sum(t["new_valid"] for t in ticks),
                longest_old_streak=max(t["old_consecutive_ticks"] for t in ticks),
                first_new_stable_tick=next((t["tick"] for t in ticks if t["new_stable"]), None),
                old_terminal_success=clean_forward_finish and terminal["old_stable"],
                new_terminal_success=clean_forward_finish and terminal["new_stable"])


def main():
    import json

    import torch

    from eval_moving_jump_360mm import main_flight_bounds
    from jump360_r3_policy import R3Control, load_policy
    from jump360_scene import json_save, sha
    from jump380_r4_evaluate import trial_from
    from jump380_r4_replay import run_trial
    from jump380_r5_scene import PARENT, PARENT_SHA, PLATFORMS, RUN, Jump380Plant

    torch.set_num_threads(1)
    archive = PARENT.parents[1] / "showcase_008m/CPU_400HZ.json"
    parent_sha = sha(PARENT)
    if parent_sha != PARENT_SHA:
        raise ValueError("Archived R4 checkpoint SHA-256 mismatch")
    inputs = json.loads(archive.read_text(encoding="utf-8"))
    if inputs["sha256"] != parent_sha:
        raise ValueError("Landing records do not match the replay checkpoint")
    plant = Jump380Plant()
    policy = R3Control(load_policy(PARENT))
    results = []
    for case in inputs["trials"]:
        if case["kind"] not in PLATFORMS:
            continue
        trial = trial_from(case)
        measured, trace = run_trial(plant, policy, trial)
        _, stop = main_flight_bounds(trace)
        result = compare_support(trace, stop, trial, measured)
        print(trial.kind, {key: value for key, value in result.items() if key not in ("case", "ticks")},
              flush=True)
        results.append(result)
    json_save(RUN / "SUPPORT_REPLAY.json", dict(physics_hz=400, policy_hz=50,
                                               checkpoint_sha256=parent_sha, trials=results))


if __name__ == "__main__":
    main()
