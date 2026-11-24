"""Stage and monitor the isolated R3 experiment on host72."""
from argparse import ArgumentParser
import json
from pathlib import PurePosixPath

from remote_jump360 import EXP, HERE, UUID, collect, connect, digest, execute, launch, q

ROOT = PurePosixPath("evidence/jump360_r3")
CALIBRATION = ROOT/"calibration/TIMING_R2_MEASURED.json"
INITIAL = ROOT/"initial/model_init.pt"


def send(ssh, paths):
    remote_paths = []
    for path in paths:
        local = HERE/path
        remote = EXP/path
        remote_paths.append((local, remote))
    execute(ssh, "mkdir -p " + " ".join(q(p) for p in sorted({remote.parent for _, remote in remote_paths})))
    with ssh.open_sftp() as sftp:
        for local, remote in remote_paths:
            temporary = str(remote)+".partial"
            sftp.put(str(local), temporary)
            sftp.posix_rename(temporary, str(remote))
    checks = " ".join(q(f"{digest(local)}  {remote}") for local, remote in remote_paths)
    print(execute(ssh, f"printf '%s\\n' {checks} | sha256sum -c"))


def main():
    parser = ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("stage")
    commands.add_parser("gpu")
    for command in ("probe", "train", "status", "collect"):
        options = commands.add_parser(command)
        options.add_argument("job")
        if command == "train":
            options.add_argument("--probe", default="probe")
        if command == "collect":
            options.add_argument("name", nargs="?")
    upload = commands.add_parser("upload")
    upload.add_argument("file", nargs="+")
    video = commands.add_parser("video")
    video.add_argument("job")
    video.add_argument("checkpoint")
    video.add_argument("results")
    args = parser.parse_args()
    with connect("host72") as ssh:
        if args.command == "stage":
            paths = [CALIBRATION, INITIAL, *(PurePosixPath(name) for name in (
                "calibrate_jump360_r3.py", "jump360_r3_gpu.py", "jump360_r3_policy.py", "train_jump360_r3.py"))]
            manifest_paths = [*paths, PurePosixPath("evidence/jump360_r2/model_final.pt")]
            send(ssh, paths)
            checks = " ".join(q(f"{digest(HERE/path)}  {EXP/path}") for path in manifest_paths)
            execute(ssh, f"printf '%s\\n' {checks} | sha256sum -c")
        elif args.command == "upload":
            send(ssh, [PurePosixPath(name) for name in args.file])
        elif args.command == "gpu":
            print(execute(ssh, f"nvidia-smi -i {q(UUID)} --query-gpu=index,uuid,memory.used,utilization.gpu --format=csv,noheader"
                               f" && nvidia-smi -i {q(UUID)} --query-compute-apps=pid,used_memory --format=csv,noheader"))
        else:
            if not args.job.replace("_", "").isalnum():
                parser.error("Use a single R3 job name")
            job = "jump360_r3/"+args.job
            if args.command in ("probe", "train"):
                options = ["--mode", args.command, "--timing", CALIBRATION, "--initial", INITIAL]
                if args.command == "train":
                    options.extend(["--preflight", ROOT/args.probe])
                launch(ssh, job, "train_jump360_r3.py", True, False, options)
            elif args.command == "video":
                paths = [PurePosixPath("evaluate_jump360_r3.py"), PurePosixPath(args.results)]
                send(ssh, paths)
                launch(ssh, job, "evaluate_jump360_r3.py", False, True, [
                    "--checkpoint", args.checkpoint, "--from-results", args.results, "--render"])
            elif args.command == "collect":
                collect(ssh, job, args.name)
            else:
                directory = EXP/"evidence"/job
                worker = execute(ssh, f"cat {q(directory/'LAUNCH.json')}")
                pid = int(json.loads(worker)["pid"])
                cmd = (f"ls -1 {q(directory)} && ps -p {pid} -o pid=,stat=,etime= "
                       f"; tail -n 8 {q(directory/'worker.log')}")
                print(execute(ssh, cmd))


if __name__ == "__main__":
    main()

