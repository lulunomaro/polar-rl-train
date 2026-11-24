"""COMMANDER-AUTHORED Remote Staging, Guard & Collection Manager on host72 GPU 0 ONLY."""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import shlex
import shutil
import tarfile

from nav_common import DONOR, HERE, LOCAL, donor_imports, put, sha256

donor_imports()
from remote_e0 import DEPS, PITCH, PLANT, connect, execute, remote_python

ROOT = PurePosixPath("/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_LIDAR_NAV_3V3_REPAIR_20261122")
PY = "/home/lc01/Zonglin Li/zonglin2/run-python.sh"
UUID = "GPU-16828f91-2b45-b646-8dc0-9481138e2842"

CODE = (
    "unified_policies.py",
    "terrain_sensor_4d.py",
    "nav4d_isaac_env.py",
    "train_generalized_ppo.py",
    "train_nav4d_stair.py",
    "jump_unified_gpu.py",
    "train_jump_unified.py",
    "fsm_isaac_env.py",
    "fsm_geometry.py",
    "fsm_io.py",
    "fsm_reset_sensors.py",
    "manual_fsm_model.py",
)

GUARD = r'''
import json, os, signal, subprocess, sys, time
from pathlib import Path
root, job, seconds, script, probe, python = sys.argv[1:]
root = Path(root); out = root / job; seconds = int(seconds)
uuid = 'GPU-16828f91-2b45-b646-8dc0-9481138e2842'
def put(p, obj):
    t = p.with_suffix(p.suffix + '.partial'); t.write_text(json.dumps(obj, indent=2)); t.replace(p)
def inventory():
    return subprocess.check_output(['nvidia-smi', '-i', '0', '--query-gpu=index,uuid,memory.used,utilization.gpu', '--format=csv,noheader,nounits'], text=True).strip()
i, gpu, mem, util = [v.strip() for v in inventory().split(',')]
assert gpu == uuid and int(mem) < 150 and int(util) == 0, f'Assigned GPU0 is not idle: {inventory()}'
if seconds:
    p = json.loads((root / probe / 'PROBE.json').read_text())
    c = json.loads((root / probe / 'SAFE_CLOSED.json').read_text())
    e = json.loads((root / (probe + '_EXIT.json')).read_text())
    assert p['passed'] and p['steps'] == 600 and p['envs'] == 2048 and p['optimizer_steps'] == 0
    assert c['scene_closed'] and e['exit_code'] == 0 and e['own_gpu_process_released'] and not e['hard_kill']
with (root / (job + '.log')).open('xb', buffering=0) as log:
    args = [python, '-B', '-u', str(root / script), str(out), '--seconds', str(seconds)]
    if seconds:
        args += ['--probe', str(root / probe)]
    worker = subprocess.Popen(
        args, cwd=root, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True,
        env=dict(os.environ, CUDA_VISIBLE_DEVICES=uuid, PYTHONDONTWRITEBYTECODE='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                 XDG_CACHE_HOME=str(root / 'cache'), WARP_CACHE_PATH=str(root / 'cache/warp'), TMPDIR=str(root / 'cache/tmp'), MUJOCO_GL='disable')
    )
    put(root / (job + '_LAUNCH.json'), dict(pid=worker.pid, guard_pid=os.getpid(), gpu_uuid=uuid, budget_s=seconds, script=script, epoch=time.time()))
    start = time.time(); hard = None; kill = False
    while worker.poll() is None:
        if (out / 'TRAIN_START.json').exists():
            hard = json.loads((out / 'TRAIN_START.json').read_text())['hard_stop_epoch']
        if (hard is not None and time.time() >= hard) or (hard is None and time.time() - start > 1900):
            try:
                os.killpg(worker.pid, signal.SIGKILL); kill = True
            except ProcessLookupError:
                pass
        time.sleep(0.25)
    for _ in range(40):
        apps = subprocess.check_output(['nvidia-smi', '-i', '0', '--query-compute-apps=pid', '--format=csv,noheader,nounits'], text=True).split()
        if str(worker.pid) not in apps:
            break
        time.sleep(0.25)
    apps = subprocess.check_output(['nvidia-smi', '-i', '0', '--query-compute-apps=pid', '--format=csv,noheader,nounits'], text=True).split()
    released = str(worker.pid) not in apps
    put(root / (job + '_EXIT.json'), dict(exit_code=worker.returncode, hard_kill=kill, own_gpu_process_released=released, inventory=inventory(), epoch=time.time()))
'''


def collect(ssh, job: str):
    folder = HERE / "evidence" / job
    folder.mkdir(parents=True, exist_ok=True)
    with ssh.open_sftp() as sftp:
        for remote, dest in [(ROOT / (job + suffix), folder / ("worker" + suffix)) for suffix in (".log", "_LAUNCH.json", "_EXIT.json")]:
            try:
                sftp.get(str(remote), str(dest))
            except FileNotFoundError:
                pass
        try:
            files = sftp.listdir(str(ROOT / job))
        except FileNotFoundError:
            files = []
        for name in files:
            if name.endswith((".json", ".pt", ".txt", ".npz")):
                tmp = folder / (name + ".download")
                sftp.get(str(ROOT / job / name), str(tmp))
                tmp.replace(folder / name)
    path = folder / "LATEST.json"
    if path.exists():
        print(path.read_text(encoding="utf-8"), flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=("stage", "probe", "train", "collect", "status", "stop", "inventory"))
    p.add_argument("--job", default="stair_probe_r1")
    p.add_argument("--probe", default="stair_probe_r1")
    p.add_argument("--seconds", type=int, default=1350)
    p.add_argument("--script", default="train_nav4d_stair.py")
    a = p.parse_args()
    if not a.job.replace("_", "").isalnum():
        p.error("Single alphanumeric job name required")

    if not (HERE / "RM27_SURVEY.npz").is_file():
        shutil.copy2(DONOR / "RM27_SURVEY.npz", HERE / "RM27_SURVEY.npz")

    with connect("host72") as ssh:
        if a.action == "inventory":
            print(execute(ssh, "nvidia-smi --query-gpu=index,uuid,name,memory.used,utilization.gpu --format=csv,noheader,nounits"))
            return
        if a.action == "stage":
            folder = HERE / "evidence/staging"
            folder.mkdir(parents=True, exist_ok=True)
            files = [(HERE / name, name) for name in CODE]
            files += [
                (HERE / "RM27_SURVEY.npz", "RM27_SURVEY.npz"),
                (DONOR / "E0_CALIBRATION.json", "E0_CALIBRATION.json"),
                (LOCAL / "MOD4V3_E0_FLAT_ROUGH_REPAIR_20261120/weights/e0_c874_004m.pt", "weights/e0.pt"),
                (HERE.parents[2] / "deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt", "weights/e0_base.pt"),
                (DONOR / "weights/E_stair_stage2_gate_final_fsm_r10c_model_015m.pt", "weights/stair_donor.pt"),
                (LOCAL / "MOD4V3_MOVING_JUMP_360MM_GPU_RL_20261121/evidence/jump380_r10/ppo/model_009m.pt", "weights/jump_r10_donor.pt"),
            ]
            put(folder / "INPUTS.json", {name: sha256(src) for src, name in files})
            bundle = folder / "inputs_v2.tar.gz"
            with tarfile.open(bundle, "w:gz", compresslevel=2) as tar:
                for src, dst in [
                    (DEPS, "dependencies"),
                    (PITCH / "support", "support"),
                    (PLANT, "plant"),
                    (LOCAL / "MOD4V3_E0_FLAT_ROUGH_REPAIR_20261120/e0_env.py", "support/mod4v3_ppo_v1/e0_env.py"),
                    (folder / "INPUTS.json", "INPUTS.json"),
                    *files,
                ]:
                    tar.add(src, arcname=dst, filter=lambda item: None if "__pycache__" in item.name or item.name.endswith(".pyc") else item)
            execute(ssh, shlex.join(["mkdir", "-p", str(ROOT / "cache/tmp")]))
            with ssh.open_sftp() as sftp:
                sftp.put(str(bundle), str(ROOT / "inputs_v2.tar.gz"))
                with sftp.open(str(ROOT / "guard_nav.py"), "w") as f:
                    f.write(GUARD)
            execute(ssh, f"cd {shlex.quote(str(ROOT))} && tar -xzf inputs_v2.tar.gz", timeout=180)
            script = """from pathlib import Path
import shutil, sys
r = Path(sys.argv[1])
donor = r.parent / 'MOD4V3_MOVING_JUMP_360MM_GPU_RL_20261121/workspace/sources/local/MOD4V3_MOVING_JUMP_360MM_GPU_RL_20261121'
s = r / 'jump_support'; s.mkdir(exist_ok=True)
for p in donor.glob('*.py'):
    shutil.copyfile(p, s / p.name)
path = s / 'jump360_scene.py'
text = path.read_text()
text = text.replace('HERE = Path(__file__).resolve().parent', 'HERE = Path(' + repr(str(donor)) + ')')
path.write_text(text)
print('staged_ok jump_source_count=', len(list(s.glob('*.py'))))
"""
            print(remote_python(ssh, PY, script, [ROOT]))
            return

        if a.action in ("probe", "train"):
            budget = 0 if a.action == "probe" else a.seconds
            assert 0 <= budget <= 1800
            script = """import subprocess, sys, json
from pathlib import Path
root, job, seconds, script, probe, python = sys.argv[1:]; r = Path(root)
with (r / (job + '_guard.log')).open('xb', buffering=0) as f:
    p = subprocess.Popen([sys.executable, str(r / 'guard_nav.py'), root, job, seconds, script, probe, python], stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
print(json.dumps(dict(guard_pid=p.pid, job=job, script=script, budget_seconds=int(seconds))))
"""
            receipt = remote_python(ssh, PY, script, [ROOT, a.job, budget, a.script, a.probe, PY])
            print(receipt)
            put(HERE / "evidence" / a.job / "DISPATCH.json", json.loads(receipt))
            return

        if a.action == "stop":
            execute(ssh, shlex.join(["touch", str(ROOT / a.job / "REQUEST_STOP")]))
            return

        collect(ssh, a.job)
        if a.action == "status":
            print(execute(ssh, f"tail -n 12 {shlex.quote(str(ROOT / (a.job + '.log')))}"))


if __name__ == "__main__":
    main()
