"""Independent 400 Hz CPU acceptance and real-time video for R4."""
from argparse import ArgumentParser
from dataclasses import fields
import json
import math
from multiprocessing import Pool
import os
from pathlib import Path
from statistics import mean

# The host72 software renderer uses the same pinned Mesa library as the R2/R3 videos.
if os.environ.get("MUJOCO_GL") == "osmesa" and (mesa := os.environ.get("JUMP360_OSMESA")):
    import ctypes
    import ctypes.util

    find_library = ctypes.util.find_library
    ctypes.util.find_library = lambda name: mesa if name == "OSMesa" else find_library(name)
    ctypes.CDLL(mesa, mode=ctypes.RTLD_GLOBAL)

import torch

from eval_moving_jump_360mm import Video
from jump360_r3_policy import R3Control, load_policy
from jump360_scene import HERE, json_save, sha
from jump380_r4_replay import Trial, run_trial
from jump380_r4_scene import KINDS, PLATFORMS, RUN, Jump380Plant, prepare_scene

SCENES = KINDS[:3]
SOURCES = ("jump380_r4_scene.py", "jump380_r4_replay.py", "jump380_r4_evaluate.py")
PROFILES = {
    "screen": (28100, (16, 34, 50), (-.08, 0., .08)),
    "acceptance": (31700, (12, 19, 25, 31, 37, 44, 50), (-.12, -.08, -.04, 0., .04, .08, .12)),
}
VIDEO_FILES = {
    "platform_380": ("PLATFORM_380MM_1X.mp4", "380 mm solid platform"),
    "platform_360": ("PLATFORM_360MM_1X.mp4", "360 mm solid platform"),
    "flat": ("MOVING_JUMP_FLAT_1X.mp4", "Flat moving jump"),
}
TRIAL_FIELDS = tuple(field.name for field in fields(Trial))
PLANT = POLICY = None


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def trial_from(row):
    return Trial(**{key: row[key] for key in TRIAL_FIELDS})


def initialize(checkpoint):
    global PLANT, POLICY
    torch.set_num_threads(1)
    PLANT = Jump380Plant()
    POLICY = R3Control(load_policy(checkpoint))


def replay(trial):
    row, _ = run_trial(PLANT, POLICY, trial)
    return row


def cases(timing, profile):
    start_seed, holds, offsets = PROFILES[profile]
    for i, speed in enumerate(timing["speeds"]):
        for j, height in enumerate(timing["heights"]):
            for rep, hold in enumerate(holds):
                seed = start_seed + 19 * (i * len(timing["heights"]) + j) + rep
                jitter = offsets[(rep + i + 2 * j) % len(offsets)]
                for dr in (0., 1.):
                    yield Trial(seed, speed, height, dr, hold_ticks=hold, press_tick=123 + seed % 26)
                    for kind in PLATFORMS:
                        center = timing[kind][i][j]
                        wall = center + (1.36 + .09 * (seed % 5)) * speed
                        yield Trial(seed, speed, height, dr, kind, center + jitter,
                                    hold_ticks=hold, wall_at=wall)


def statistics(rows):
    return dict(
        trials=len(rows), physical=sum(row["obstacle_pass_physical"] for row in rows),
        strict_direct=sum(row["strict_direct"] for row in rows),
        qualified=sum(row["qualified"] for row in rows),
        clearance_385=sum(row["flight_peak_all_m"] >= .385 for row in rows),
        falls=sum(row["fall"] for row in rows), running_recovery=sum(row["landed_running"] for row in rows),
        dual_wheel_top_beyond=sum(row["both_wheels_top_beyond_samples"] > 0 for row in rows),
        post_touch_with_key=sum(row["supported_while_held"] for row in rows),
        no_face_collision=sum(row["wall_face_free"] for row in rows),
        peak_mean_m=mean(row["flight_peak_all_m"] for row in rows) if rows else None,
        max_peak_m=max((row["flight_peak_all_m"] for row in rows), default=None),
        max_post_press_vx_m_s=max((row["peak_vx_after_press_m_s"] for row in rows
                                   if row["peak_vx_after_press_m_s"] is not None), default=None),
    )


def aggregate(rows):
    speed_grid = sorted({row["speed"] for row in rows})
    height_grid = sorted({row["height"] for row in rows})
    holds = sorted({row["hold_ticks"] for row in rows})
    by_kind_dr = []
    for kind in SCENES:
        for dr in (0., 1.):
            group = [row for row in rows if row["kind"] == kind and row["dr"] == dr]
            if not group:
                continue
            by_kind_dr.append(dict(
                kind=kind, dr=dr, **statistics(group),
                by_speed=[dict(speed=speed, **statistics([row for row in group if row["speed"] == speed]))
                          for speed in speed_grid],
                by_height=[dict(height=height, **statistics([row for row in group if row["height"] == height]))
                           for height in height_grid],
                by_hold=[dict(hold_ticks=hold, **statistics([row for row in group if row["hold_ticks"] == hold]))
                         for hold in holds],
            ))
    return by_kind_dr


def representative(rows, kind):
    same_scene = [row for row in rows if row["kind"] == kind]
    if not same_scene:
        raise ValueError(f"No evaluated {kind} replay")
    return max(same_scene, key=lambda row: (
        row["qualified"] if kind == "flat" else row["strict_direct"],
        row["obstacle_pass_physical"] if kind != "flat" else row["landed_running"],
        row["wall_face_free"], row["supported_while_held"], row["both_wheels_top_beyond_samples"] > 0,
        -abs((row["end_vx_m_s"] or 0.) - row["speed"]),
        row["wall_margin_m"] if row["wall_margin_m"] is not None else -9.,
        row["flight_peak_all_m"], not row["dr"],
    ))


def render(checkpoint, rows, out):
    torch.set_num_threads(1)
    plant = Jump380Plant(visual=True)
    policy = R3Control(load_policy(checkpoint))
    videos = []
    checkpoint_id = sha(checkpoint)[:8]
    for kind, (filename, title) in VIDEO_FILES.items():
        pick = representative(rows, kind)
        trial = trial_from(pick)
        label = "Strict pass" if (pick["qualified"] if kind == "flat" else pick["strict_direct"]) else (
            "Physical pass" if pick["obstacle_pass_physical"] else "Failed replay")
        camera = Video(out / filename, f"MOD4v3 {checkpoint_id} | {title} | {label} | {'Full DR' if trial.dr else 'Nominal'}")
        try:
            rerun, _ = run_trial(plant, policy, trial, camera)
        finally:
            camera.close()
        for key in ("strict_direct", "qualified", "obstacle_pass_physical"):
            if rerun[key] != pick[key]:
                raise RuntimeError(f"Rendered replay disagrees on {kind} {key}")
        if not math.isclose(rerun["flight_peak_all_m"], pick["flight_peak_all_m"], rel_tol=.01, abs_tol=.002):
            raise RuntimeError(f"Rendered replay clearance differs on {kind}")
        if camera.count == 0:
            raise RuntimeError(f"Empty rendered video for {kind}")
        videos.append(dict(kind=kind, file=filename, frames=camera.count, fps=25, playback_speed=1., case=rerun))
    json_save(out/"VIDEO.json", dict(checkpoint_sha256=sha(checkpoint), videos=videos))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timing", type=Path, default=RUN/"calibration/TIMING.json")
    parser.add_argument("--profile", choices=PROFILES, default="acceptance")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--from-results", type=Path)
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    checksum = sha(args.checkpoint)
    if args.from_results:
        recorded = read_json(args.from_results)
        if recorded["sha256"] != checksum:
            raise ValueError("Video weights and CPU evaluation checksums differ")
        rows = recorded["trials"]
    else:
        timing = read_json(args.timing)
        prepare_scene(False)
        attempts = list(cases(timing, args.profile))
        with Pool(args.workers, initializer=initialize, initargs=(args.checkpoint,)) as pool:
            rows = list(pool.imap(replay, attempts, chunksize=4))
        outcome = aggregate(rows)
        json_save(args.out/"CPU_400HZ.json", dict(
            physics_hz=400, policy_hz=50, actor_inputs=[35, 420], action_dim=6,
            checkpoint=str(args.checkpoint), sha256=checksum, profile=args.profile, timing_sha256=sha(args.timing),
            scene_sha256=sha(prepare_scene(False)), sources={name: sha(HERE/name) for name in SOURCES},
            by_kind_dr=outcome, trials=rows))
        for row in outcome:
            print({key: row[key] for key in ("kind", "dr", "trials", "strict_direct", "physical",
                                             "qualified", "clearance_385")}, flush=True)
    if args.render:
        render(args.checkpoint, rows, args.out)


if __name__ == "__main__":
    main()
