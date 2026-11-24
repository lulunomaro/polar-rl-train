"""Stage and collect this experiment on Host72 GPU 1 only."""
from __future__ import annotations

from argparse import ArgumentParser
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shlex
import sys
import tarfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / "MOD4V3_AUTONOMOUS_MOE_REPAIR_20261120"))
from remote_repair import connect, execute, location

UUID = "GPU-c27eecbd-6838-7290-1cd2-37e34522213d"
base, PYTHON = location("host72")
REMOTE = base.parent / HERE.name
MIRROR = REMOTE / "workspace"
EXP = MIRROR / HERE.relative_to(REPO).as_posix()
OLD = HERE.parent / "MOD4V3_RL_HIGH_MOVING_JUMP_20261118"
DELIVERY = REPO / "deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112"
C874 = REPO / "deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt"
E0 = HERE.parent / "MOD4V3_E0_FLAT_ROUGH_REPAIR_20261120/weights/e0_c874_004m.pt"


def q(value):
    return shlex.quote(str(value))


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def local_json(name, obj):
    path = HERE / "evidence" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def send_bundle(ssh, initial):
    (HERE / "evidence").mkdir(exist_ok=True)
    bundle = HERE / "evidence" / ("inputs.tar.gz" if initial else "source_update.tar.gz")
    paths = [path for path in sorted(HERE.glob("*.py")) if path.name != Path(__file__).name]
    paths.append(HERE / "JUMP360_BRIEF.md")
    if initial:
        paths.extend([C874, E0, DELIVERY / "plant", DELIVERY / "runtime/core",
                      OLD / "moe_jump_model.py", OLD / "rl_jump_env.py", OLD / "weights/model_rl_best.pt"])
    def only_source(member):
        return None if any(p in ("__pycache__", ".git") for p in PurePosixPath(member.name).parts) else member
    with tarfile.open(bundle, "w:gz", compresslevel=2) as tar:
        for item in paths:
            tar.add(item, arcname=item.relative_to(REPO).as_posix(), filter=only_source)
    execute(ssh, f"mkdir -p {q(MIRROR)} {q(EXP / 'evidence')}")
    archive = REMOTE / bundle.name
    with ssh.open_sftp() as sftp:
        sftp.put(str(bundle), str(archive))
    hash_line = q(f"{digest(bundle)}  {archive}")
    print(execute(ssh, f"printf '%s\\n' {hash_line} | sha256sum -c && tar -xzf {q(archive)} -C {q(MIRROR)}", timeout=120))
    hashes = {path.relative_to(REPO).as_posix(): digest(path) for path in paths if path.is_file()}
    local_json("INPUTS.json" if initial else "SOURCE_UPDATE.json", hashes)


LAUNCH = '''
import json, os, subprocess, sys
from pathlib import Path
experiment, launcher, uuid, script, job, uses_gpu, software_render, *args = sys.argv[1:]
root = Path(experiment)
result = root / 'evidence' / job
result.mkdir()
if uses_gpu == '1':
    query = ['nvidia-smi', '-i', uuid, '--query-gpu=index,uuid,memory.used', '--format=csv,noheader,nounits']
    index, actual_uuid, used = subprocess.check_output(query, text=True).strip().split(', ')
    applications = subprocess.check_output(['nvidia-smi', '-i', uuid,
        '--query-compute-apps=pid,used_memory', '--format=csv,noheader'], text=True).strip()
    if (index, actual_uuid) != ('1', uuid) or applications or int(used) >= 256:
        raise RuntimeError(f'Expected available Host72 GPU 1, got {index} {actual_uuid} {used} {applications}')
job_env = dict(os.environ, CUDA_DEVICE_ORDER='PCI_BUS_ID', CUDA_VISIBLE_DEVICES=uuid if uses_gpu == '1' else '',
               PYTHONDONTWRITEBYTECODE='1', PYTHONUNBUFFERED='1', OMP_NUM_THREADS='1',
               OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', XDG_CACHE_HOME=str(root/'cache'),
               WARP_CACHE_PATH=str(root/'cache/warp'), MUJOCO_GL='disable')
runtime = Path(launcher).parent
libc = runtime/'compat/glibc240'
conda = runtime/'envs/mod4'
cache = root/'cache'
cache.mkdir(exist_ok=True)
job_env.pop('PYTHONHOME', None)
job_env.pop('PYTHONPATH', None)
job_env.pop('LD_LIBRARY_PATH', None)
job_env.update(PYTHONNOUSERSITE='1', CONDA_PREFIX=str(conda), CUDA_CACHE_PATH=str(cache/'cuda'),
               TORCH_HOME=str(cache/'torch'), TMPDIR='./cache')
if software_render == '1':
    if uses_gpu == '1':
        raise ValueError('Use CPU-only Mesa for video rendering')
    lib = root/'render_deps/usr/lib/x86_64-linux-gnu/libOSMesa.so.8'
    if not lib.is_file():
        raise FileNotFoundError(lib)
    job_env.update(MUJOCO_GL='osmesa',JUMP360_OSMESA=str(lib),
                   LD_PRELOAD='/lib/x86_64-linux-gnu/libffi.so.7', LP_NUM_THREADS='4')
command = [str(libc/'ld-linux-x86-64.so.2'), '--library-path', f'{libc}:{conda}/lib',
           str(conda/'bin/python'), '-B', '-u', str(root / script), '--out', str(result), *args]
with (result / 'worker.log').open('xb', buffering=0) as log:
    process = subprocess.Popen(command, env=job_env, cwd=root, stdin=subprocess.DEVNULL,
        stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
state = dict(pid=process.pid, job=str(result), gpu=uuid if uses_gpu == '1' else None, command=command[6:])
(result / 'LAUNCH.json').write_text(json.dumps(state, indent=2))
print(json.dumps(state))
'''


def launch(ssh, job, script, uses_gpu, software_render, args):
    command = " ".join(q(item) for item in ["python3", "-c", LAUNCH, EXP, PYTHON, UUID,
                                             script, job, int(uses_gpu), int(software_render), *args])
    receipt = json.loads(execute(ssh, command))
    local_json(job + "_LAUNCH.json", receipt)
    print(receipt)


def collect(ssh, job, name=None):
    folder = EXP / "evidence" / job
    local = HERE / "evidence" / job
    local.mkdir(parents=True, exist_ok=True)

    def copy_directory(sftp, remote_dir, local_dir):
        local_dir.mkdir(exist_ok=True)
        for entry in sftp.listdir_attr(str(remote_dir)):
            if entry.filename.endswith(".partial"):
                continue
            if entry.st_mode & 0o170000 == 0o040000:
                copy_directory(sftp, remote_dir / entry.filename, local_dir / entry.filename)
            else:
                copy_file(sftp, remote_dir, local_dir, entry.filename)

    def copy_file(sftp, remote_dir, local_dir, filename):
        destination = local_dir / filename
        partial = destination.with_suffix(destination.suffix + ".partial")
        sftp.get(str(remote_dir / filename), str(partial))
        partial.replace(destination)

    with ssh.open_sftp() as sftp:
        if name:
            copy_file(sftp, folder, local, name)
        else:
            copy_directory(sftp, folder, local)


def main():
    parser = ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("stage")
    sub.add_parser("sync")
    sub.add_parser("gpu")
    transfer = sub.add_parser("upload")
    transfer.add_argument("file", type=Path)
    start = sub.add_parser("launch")
    start.add_argument("job")
    start.add_argument("script")
    start.add_argument("--gpu", action="store_true")
    start.add_argument("--software-render", action="store_true")
    status = sub.add_parser("status")
    status.add_argument("job")
    get = sub.add_parser("collect")
    get.add_argument("job")
    get.add_argument("name", nargs="?")
    args, remaining = parser.parse_known_args()
    if args.action != "launch" and remaining:
        parser.error(str(remaining))
    with connect("host72") as ssh:
        if args.action in ("stage", "sync"):
            send_bundle(ssh, args.action == "stage")
        if args.action == "upload":
            path = (HERE / args.file).resolve()
            remote = EXP / path.relative_to(HERE).as_posix()
            execute(ssh, f"mkdir -p {q(remote.parent)}")
            with ssh.open_sftp() as sftp:
                partial = str(remote)+".partial"
                sftp.put(str(path), partial)
                sftp.posix_rename(partial, str(remote))
            print(execute(ssh, f"printf '%s\\n' {q(f'{digest(path)}  {remote}')} | sha256sum -c"))
        if args.action == "launch":
            if not args.job.replace("_", "").isalnum() or Path(args.script).name != args.script:
                parser.error("Expected a job label and script basename")
            launch(ssh, args.job, args.script, args.gpu, args.software_render, remaining)
        if args.action == "collect":
            collect(ssh, args.job, args.name)
        if args.action == "status":
            job = EXP / "evidence" / args.job
            print(execute(ssh, f"ls -l {q(job)} && tail -n 14 {q(job/'worker.log')}"))
        if args.action == "gpu":
            print(execute(ssh, f"nvidia-smi -i {q(UUID)} --query-gpu=index,uuid,memory.used,utilization.gpu --format=csv,noheader"
                               f" && nvidia-smi -i {q(UUID)} --query-compute-apps=pid,used_memory --format=csv,noheader"))


if __name__ == "__main__":
    main()
