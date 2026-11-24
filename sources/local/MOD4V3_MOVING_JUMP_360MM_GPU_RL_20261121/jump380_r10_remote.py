"""Stage R10 on Host72 GPU 1 and dispatch independent CPU replays."""

from argparse import ArgumentParser
import json
from pathlib import PurePosixPath

from jump380_r4_remote import gpu
from jump380_r10_policy import PARENT, PARENT_SHA
from remote_jump360 import EXP, HERE, collect, connect, execute, launch, q
from remote_jump360_r3 import send

ROOT = PurePosixPath("evidence/jump380_r10")
SOURCES = tuple(PurePosixPath(f"jump380_r10_{part}.py") for part in ("policy", "timing", "gpu", "train"))


def main():
    parser = ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("stage", "gpu", "stage_cpu"):
        commands.add_parser(name)
    for name in ("probe", "train", "status", "collect", "evaluate", "video"):
        job = commands.add_parser(name)
        job.add_argument("job")
        if name == "train":
            job.add_argument("--probe", default="probe")
        elif name == "collect":
            job.add_argument("file", nargs="?")
        elif name in ("evaluate", "video"):
            job.add_argument("--checkpoint", required=True)
            if name == "evaluate":
                job.add_argument("--profile", choices=("screen", "acceptance", "demo", "target", "high"),
                                 default="acceptance")
                job.add_argument("--workers", type=int, default=12)
            else:
                job.add_argument("--results", required=True)
    args = parser.parse_args()

    with connect("host72") as ssh:
        if args.command == "gpu":
            gpu(ssh)
            return
        if args.command == "stage":
            parent = EXP/PARENT.relative_to(HERE).as_posix()
            check = q(f"{PARENT_SHA}  {parent}")
            print(execute(ssh, f"printf '%s\\n' {check} | sha256sum -c"))
            send(ssh, (*SOURCES, ROOT/"calibration/TRAIN_TIMING.json", ROOT/"calibration/CRUISE.json"))
            return
        if args.command == "stage_cpu":
            send(ssh, (PurePosixPath("jump380_r10_evaluate.py"), ROOT/"cpu_inputs/jump380_r4_calibrate.py"))
            return
        if not args.job.replace("_", "").isalnum():
            parser.error("Use a single R10 job name")
        job = f"jump380_r10/{args.job}"
        if args.command in ("probe", "train"):
            options = ["--mode", args.command]
            if args.command == "train":
                if not args.probe.replace("_", "").isalnum():
                    parser.error("Use a single R10 probe job name")
                options += ["--preflight", ROOT/args.probe]
            launch(ssh, job, "jump380_r10_train.py", True, False, options)
        elif args.command == "collect":
            collect(ssh, job, args.file)
        elif args.command in ("evaluate", "video"):
            checkpoint = PurePosixPath(args.checkpoint)
            if ROOT not in checkpoint.parents and checkpoint.as_posix() != PARENT.relative_to(HERE).as_posix():
                parser.error("Use the pinned parent or an R10 checkpoint")
            options = ["--checkpoint", checkpoint]
            if args.command == "video":
                results = [PurePosixPath(path) for path in args.results.split(",")]
                if any(ROOT not in path.parents for path in results):
                    parser.error("R10 video rendering requires R10 CPU results")
                options += ["--render-from", *results]
            else:
                options += ["--profile", args.profile, "--workers", args.workers]
            launch(ssh, job, "jump380_r10_evaluate.py", False, args.command == "video", options)
        else:
            directory = EXP/"evidence"/job
            with ssh.open_sftp() as sftp, sftp.open(str(directory/"LAUNCH.json")) as stream:
                pid = int(json.load(stream)["pid"])
            print(execute(ssh, f"tail -n 10 {q(directory/'worker.log')} "
                               f"&& ps -p {pid} -o pid=,stat=,etime= || true"))


if __name__ == "__main__":
    main()
