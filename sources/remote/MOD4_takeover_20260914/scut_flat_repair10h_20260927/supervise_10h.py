"""Run one fixed MOD4 flat-ground PPO contract for ten wall-clock hours.

Every restart resumes the latest saved actor, critic, optimizer, iteration and
exploration state.  A restart is only for a process failure or a completed
segment; it never changes the plant, rewards or command distribution.
"""
from __future__ import annotations

import glob
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


STAGE = Path(__file__).resolve().parent
ROOT = STAGE / "run/scut_flat_walk_run_repair10h_20260927"
STATUS = ROOT / "status.json"
SOURCE = Path("/home/egde/rl_candidates/MOD4_takeover_20260914/scut_flat_mod4_20260926/run/scut_flat_walk_run_8h_20260927/segment_000/logs/2026-09-27_01-52-14_scut_flat_mod4/model_1390.pt")
DURATION_S = 10 * 3600
PYTHON = "/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python"


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def save(data):
    data["updated_utc"] = stamp()
    STATUS.write_text(json.dumps(data, indent=2) + "\n")


def latest():
    paths = glob.glob(str(ROOT / "segment_*/logs/*/model_*.pt"))
    return max(paths, key=lambda p: os.stat(p).st_mtime) if paths else None


def stop_group(proc):
    if proc.poll() is not None:
        return
    os.killpg(proc.pid, signal.SIGINT)
    try:
        proc.wait(timeout=120)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    if STATUS.exists():
        raise SystemExit(f"existing run status; refusing duplicate: {STATUS}")
    if not SOURCE.is_file():
        raise SystemExit(f"checkpoint missing: {SOURCE}")
    start = time.monotonic()
    deadline = start + DURATION_S
    data = {
        "state": "starting", "started_utc": stamp(),
        "deadline_utc": (datetime.now(timezone.utc) + timedelta(seconds=DURATION_S)).isoformat(timespec="seconds"),
        "source_checkpoint": str(SOURCE), "scene": "SCUT V14 Flat plane adapted to MOD4",
        "ppo": "SCUT V14 Flat 256/128/64 ELU, 5 epochs, 4 minibatches, adaptive KL",
        "envs": 12000, "steps_per_env": 48, "solver_position": 16,
        "solver_velocity": 4, "gas_force_n": 500, "gas_frame": "reference",
        "stage_root": str(STAGE), "segments": [],
    }
    save(data)
    checkpoint = SOURCE
    failures = 0
    segment = 0
    while time.monotonic() < deadline:
        tag = f"scut_flat_walk_run_repair10h_20260927/segment_{segment:03d}"
        cmd = [PYTHON, "-u", str(STAGE / "launch.py"), "train",
               "--tag", tag, "--envs", "12000", "--iterations", "5000",
               "--warmstart", "--resume-exact", "--checkpoint", str(checkpoint)]
        log_path = ROOT / f"segment_{segment:03d}_launcher.log"
        record = {"segment": segment, "checkpoint": str(checkpoint),
                  "command": cmd, "started_utc": stamp(), "log": str(log_path)}
        data["segments"].append(record)
        with log_path.open("w") as log:
            proc = subprocess.Popen(cmd, cwd=STAGE, stdout=log,
                                    stderr=subprocess.STDOUT, start_new_session=True)
            record["pid"] = proc.pid
            data["state"] = "training"
            save(data)
            while proc.poll() is None and time.monotonic() < deadline:
                time.sleep(min(30, max(1, deadline - time.monotonic())))
                recent = latest()
                data["latest_checkpoint"] = recent or str(checkpoint)
                data["elapsed_s"] = round(time.monotonic() - start, 1)
                save(data)
            timed_out = time.monotonic() >= deadline
            if timed_out:
                stop_group(proc)
            returncode = proc.wait()
        record["ended_utc"] = stamp()
        record["exit_code"] = returncode
        record["deadline_stop"] = timed_out
        recent = latest()
        data["latest_checkpoint"] = recent or str(checkpoint)
        save(data)
        if timed_out:
            data["state"] = "time_budget_complete"
            break
        if recent is None or (str(recent) == str(checkpoint) and returncode != 0):
            failures += 1
            if failures >= 3:
                data["state"] = "failed_needs_review"
                data["error"] = "Three consecutive failures without a newer checkpoint"
                break
            time.sleep(30)
        else:
            checkpoint = Path(recent)
            failures = 0
        segment += 1
    data["finished_utc"] = stamp()
    data["elapsed_s"] = round(time.monotonic() - start, 1)
    data["latest_checkpoint"] = latest() or str(checkpoint)
    save(data)


if __name__ == "__main__":
    main()
