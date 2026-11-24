"""Run R5 on the pinned host72 GPU and render replays with CPU Mesa."""
from argparse import ArgumentParser
import json
from pathlib import PurePosixPath

from jump380_r4_remote import gpu
from jump380_r5_scene import PARENT_SHA
from remote_jump360 import EXP, collect, connect, execute, launch, q
from remote_jump360_r3 import send

ROOT = PurePosixPath("evidence/jump380_r5")
PARENT = EXP / "evidence/jump380_r4/ppo/model_008m.pt"
TRAIN_INPUTS = tuple(PurePosixPath(f"jump380_r5_{module}.py")
                     for module in ("scene", "support", "gpu", "train"))


def main():
    parser = ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("stage")
    commands.add_parser("timing")
    commands.add_parser("gpu")
    for command in ("probe", "train", "status", "collect", "video"):
        job = commands.add_parser(command)
        job.add_argument("job", default="probe" if command == "probe" else "ppo", nargs="?")
        if command == "train":
            job.add_argument("--probe", default="probe")
        elif command == "collect":
            job.add_argument("name", nargs="?")
        elif command == "video":
            job.add_argument("--checkpoint", required=True)
            job.add_argument("--results", required=True)
    args = parser.parse_args()
    with connect("host72") as ssh:
        if args.command == "stage":
            print(execute(ssh, f"printf '%s\\n' {q(f'{PARENT_SHA}  {PARENT}')} | sha256sum -c"))
            send(ssh, TRAIN_INPUTS)
            return
        if args.command == "timing":
            send(ssh, (ROOT / "calibration/TIMING.json",))
            return
        if args.command == "gpu":
            gpu(ssh)
            return
        if not args.job.replace("_", "").isalnum():
            parser.error("Use a single R5 job name")
        job = "jump380_r5/" + args.job
        if args.command in ("probe", "train"):
            options = ["--mode", args.command]
            if args.command == "train":
                if not args.probe.replace("_", "").isalnum():
                    parser.error("Use a single R5 preflight job name")
                options += ["--preflight", ROOT/args.probe]
            launch(ssh, job, "jump380_r5_train.py", True, False, options)
        elif args.command == "collect":
            collect(ssh, job, args.name)
        elif args.command == "video":
            results, checkpoint = PurePosixPath(args.results), PurePosixPath(args.checkpoint)
            if ROOT not in results.parents or ROOT not in checkpoint.parents:
                parser.error("R5 rendering requires an R5 checkpoint and CPU results")
            send(ssh, (PurePosixPath("jump380_r5_evaluate.py"), results))
            with ssh.open_sftp() as sftp:
                sftp.stat(str(EXP/checkpoint))
            launch(ssh, job, "jump380_r5_evaluate.py", False, True,
                   ["--checkpoint", checkpoint, "--render-from", results])
        else:
            directory = EXP / "evidence" / job
            with ssh.open_sftp() as sftp, sftp.open(str(directory / "LAUNCH.json")) as stream:
                pid = int(json.load(stream)["pid"])
            print(execute(ssh, f"tail -n 8 {q(directory/'worker.log')}"
                               f" && ps -p {pid} -o pid=,stat=,etime= || true"))


if __name__ == "__main__":
    main()
