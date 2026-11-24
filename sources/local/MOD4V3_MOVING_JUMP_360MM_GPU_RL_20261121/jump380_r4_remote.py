"""Stage R4 and run it on host72 GPU 1, with CPU-only video jobs."""
from argparse import ArgumentParser
import json
from pathlib import PurePosixPath

from jump380_r4_scene import PARENT_SHA
from remote_jump360 import EXP, HERE, UUID, collect, connect, execute, launch, q
from remote_jump360_r3 import send

ROOT = PurePosixPath("evidence/jump380_r4")
PARENT = EXP/"evidence/jump360_r3/ppo/model_004m.pt"
TRAIN_INPUTS = ("jump380_r4_scene.py", "jump380_r4_gpu.py", "jump380_r4_contact.py", "jump380_r4_train.py")


def gpu(ssh):
    gpu_row = execute(ssh, f"nvidia-smi -i {q(UUID)} --query-gpu=index,uuid,memory.used,utilization.gpu "
                           "--format=csv,noheader")
    compute_rows = execute(ssh, f"nvidia-smi -i {q(UUID)} --query-compute-apps=pid,used_memory "
                                "--format=csv,noheader")
    print(json.dumps(dict(gpu=gpu_row.strip(), compute=compute_rows.strip())))


def main():
    parser = ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("stage")
    commands.add_parser("gpu")
    for command in ("probe", "train", "status", "collect", "video"):
        options = commands.add_parser(command)
        options.add_argument("job")
        if command == "train":
            options.add_argument("--probe", default="probe")
        elif command == "collect":
            options.add_argument("name", nargs="?")
        elif command == "video":
            options.add_argument("checkpoint")
            options.add_argument("results")
    args = parser.parse_args()
    with connect("host72") as ssh:
        if args.command == "stage":
            check = q(f"{PARENT_SHA}  {PARENT}")
            print(execute(ssh, f"printf '%s\\n' {check} | sha256sum -c"))
            send(ssh, [*(PurePosixPath(name) for name in TRAIN_INPUTS), ROOT/"calibration/TIMING.json"])
            return
        if args.command == "gpu":
            gpu(ssh)
            return
        if not args.job.replace("_", "").isalnum():
            parser.error("Use a single R4 job name")
        job = "jump380_r4/" + args.job
        if args.command in ("probe", "train"):
            options = ["--mode", args.command]
            if args.command == "train":
                options += ["--preflight", ROOT/args.probe]
            launch(ssh, job, "jump380_r4_train.py", True, False, options)
        elif args.command == "collect":
            collect(ssh, job, args.name)
        elif args.command == "video":
            send(ssh, [PurePosixPath(name) for name in (
                "jump380_r4_replay.py", "jump380_r4_evaluate.py", args.results)])
            with ssh.open_sftp() as sftp:
                sftp.stat(str(EXP/args.checkpoint))
            launch(ssh, job, "jump380_r4_evaluate.py", False, True, [
                "--checkpoint", args.checkpoint, "--render", "--from-results", args.results])
        else:
            directory = EXP/"evidence"/job
            with ssh.open_sftp() as sftp, sftp.open(str(directory/"LAUNCH.json")) as stream:
                pid = int(json.load(stream)["pid"])
            print(execute(ssh, f"tail -n 15 {q(directory/'worker.log')}"
                               f" && ps -p {pid} -o pid=,stat=,etime= || true"))


if __name__ == "__main__":
    main()
