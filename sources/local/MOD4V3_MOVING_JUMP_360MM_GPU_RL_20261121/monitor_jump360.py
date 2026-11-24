"""Collect bounded PPO products and run their independent screening replays."""
from __future__ import annotations

from argparse import ArgumentParser
import json
from pathlib import Path
import socket
import time

from remote_jump360 import EXP, HERE, UUID, collect, connect, digest, execute, launch, local_json, q


def load_file(sftp, path):
    with sftp.open(str(path), "r") as stream:
        return json.load(stream)


def inspect(job):
    experiment = EXP/"evidence"
    training = experiment/job
    screen_prefix = job+"_cpu_"
    with connect("host72") as ssh:
        with ssh.open_sftp() as sftp:
            names = sftp.listdir(str(training))
            jobs = set(sftp.listdir(str(experiment)))
            if "HARD_DEADLINE.txt" in names or "ERROR.txt" in names:
                collect(ssh, job)
                raise RuntimeError(f"Remote PPO failure. See evidence/{job}.")
            is_final = "FINAL.json" in names and "SAFE_CLOSED.json" in names
            if "LATEST.json" not in names:
                return False
            latest = load_file(sftp, training/"LATEST.json")
            progress = {key: latest[key] for key in ("elapsed_s","ppo_updates","adam_steps","stats",
                                                     "active_dr_reset_probability","actor_head_max_change",
                                                     "exploration_std")}
            checks = [name for name in names if name.startswith("model_") and name.endswith("m.pt.json")]
            if is_final:
                checks.append("FINAL.json")

            selections = {}
            for mark in sorted(checks):
                original = load_file(sftp, training/mark)
                code = Path(original["checkpoint"]).stem.split("_",1)[1].removesuffix("m")
                screen = screen_prefix+code
                evidence = experiment/screen
                if screen not in jobs:
                    launch(ssh,screen,"eval_moving_jump_360mm.py",False,False,[
                        "--quick", "--endpoints", "--sweep", "--seeds=101", "--dr=0,1", "--scenarios=flat,platform",
                        f"--checkpoint=evidence/{job}/{original['checkpoint']}",
                    ])
                    continue
                if "JUMP360_RESULT.json" not in sftp.listdir(str(evidence)):
                    continue
                result = load_file(sftp, evidence/"JUMP360_RESULT.json")
                if result["sha256"] != original["sha256"]:
                    raise ValueError(f"Replay SHA mismatch for {screen}")
                collect(ssh,screen,"JUMP360_RESULT.json")
                selections[screen] = dict(checkpoint=original["checkpoint"], sha256=result["sha256"],
                                          stats=result["summaries"])
            progress["screened"] = selections
            progress["training_final"] = is_final
            local_json(job+"_MONITOR.json",progress)
            print(round(progress["elapsed_s"]),progress["ppo_updates"],progress["adam_steps"],
                  "full DR",progress["stats"]["current_full_dr"],"screened",sorted(selections),flush=True)
            if is_final:
                for artifact in ("FINAL.json", "SAFE_CLOSED.json", "PPO_START.json", "model_final.pt"):
                    path = HERE/"evidence"/job/artifact
                    if not path.exists():
                        collect(ssh,job,artifact)
                final = json.loads((HERE/"evidence"/job/"FINAL.json").read_text())
                observed = digest(HERE/"evidence"/job/final["checkpoint"])
                if observed!=final["sha256"]:
                    raise ValueError("Final weight download SHA mismatch")
                values = execute(ssh, f"nvidia-smi -i {q(UUID)} --query-compute-apps=pid,used_memory --format=csv,noheader")
                local_json(job+"_GPU_RELEASE.json",dict(gpu=UUID,compute_processes=values.splitlines()))
                if screen_prefix+"final" in selections and len(selections) == len(checks):
                    collect(ssh,job)
                    return True
    return False


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--job", default="jump360_r2")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    end = time.monotonic()+2100.
    while time.monotonic() < end:
        try:
            if inspect(args.job) or args.once:
                return
        except (OSError, EOFError, socket.timeout) as exc:
            print(type(exc).__name__,str(exc),flush=True)
        time.sleep(35)
    raise TimeoutError("Timed out collecting the bounded training and checkpoint replays")


if __name__ == "__main__":
    main()
