"""Run this isolated E0 study on one idle project GPU and collect verified artifacts."""
from argparse import ArgumentParser
from pathlib import Path, PurePosixPath
import hashlib
import io
import json
import os
import shlex
import sys
import tarfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
LOCAL = HERE.parent
ARCHIVE = Path(os.environ['LOCALAPPDATA']) / 'MOD4v3_Repair_Archive/e0_flat_rough_20261120'
sys.path.insert(0, str(LOCAL / 'MOD4V3_AUTONOMOUS_MOE_REPAIR_20261120'))
from remote_repair import connect, execute, location, remote_python

PITCH = LOCAL / 'MOD4V3_SCUT_PITCH_BRAKE_2H_20261116'
DEPS = LOCAL / 'MOD4V3_CONTINUOUS_STAIRS_200MM_2H_20261113/dependencies'
PLANT = REPO / 'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/plant/MOD4v3_HW300N60_R3'
PARENTS = {
    'old010': (LOCAL / 'MOD4V3_FIXED200_DAGGER_SEMANTIC_10M_20261116/weights/model_010m.pt',
               '37dbe1784bf80883586225ae0f1a6238c6258c51c1ceeb516627f6735aa2193a'),
    'c874': (REPO / 'deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt',
             'c874a1afa9adc33c3fa806d098fc135a76d3e9ecdf411d0ca4ab879696b18617'),
}
HOST = 'host72'
REMOTE, PYTHON = location(HOST)
REMOTE = REMOTE.parent / HERE.name


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def get_bundle(candidate, archive):
    plan = json.loads((PITCH/'PLAN.json').read_text(encoding='utf-8'))
    parent, sha = PARENTS[candidate]
    if digest(parent) != sha:
        raise ValueError(f'Checkpoint hash changed for {candidate}')
    assets = {'assets/'+name:data['sha256'] for name,data in plan['asset_identity']['actual_training_assets'].items()}
    assets['mjcf/scene.xml'] = plan['asset_identity']['local_mjcf_sha256']
    for path, expected in assets.items():
        if digest(PLANT / path) != expected:
            raise ValueError(f'Native asset hash changed for {path}')
    with tarfile.open(archive, 'w:gz', compresslevel=2) as bundle:
        def add(path, target):
            bundle.add(path, arcname=target, filter=lambda item: None if '__pycache__' in item.name or item.name.endswith('.pyc') else item)
        add(DEPS, 'dependencies')
        add(PITCH/'support', 'support')
        add(PLANT, 'plant')
        add(parent, 'parent.pt')
        add(HERE/'e0_env.py', 'support/mod4v3_ppo_v1/e0_env.py')
        add(HERE/'train_e0.py', 'train_e0.py')
        info = dict(required_asset_sha256=assets, parent=candidate, parent_sha256=sha,
                    code_sha256={name:digest(HERE/name) for name in ('e0_env.py','train_e0.py')})
        raw = json.dumps(info, indent=2).encode()
        member = tarfile.TarInfo('INPUTS.json')
        member.size = len(raw)
        bundle.addfile(member, io.BytesIO(raw))
    return info


RUN_SCRIPT = '''
import json, os, subprocess, sys
from pathlib import Path
root, job, gpu, parent_sha, deadline, launcher = sys.argv[1:]
root = Path(root)
gpu = int(gpu)
query = subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,memory.used','--format=csv,noheader,nounits'], text=True)
rows = [x.strip().split(', ') for x in query.strip().splitlines()]
index, uuid, memory = next(x for x in rows if int(x[0]) == gpu)
if int(memory) > 150:
    raise RuntimeError(f'GPU {gpu} is in use ({memory} MiB).')
if int(deadline):
    if not json.loads((root/'probe'/'PROBE.json').read_text())['passed']:
        raise RuntimeError('Native probe did not pass')
    assert (root/'probe'/'SAFE_CLOSED.json').is_file()
output = root / (job + '.log')
env = dict(os.environ, CUDA_VISIBLE_DEVICES=uuid, PYTHONUNBUFFERED='1')
cmd = [launcher, '-B', '-u', str(root/'train_e0.py'), str(root/job),
       '--parent', str(root/'parent.pt'), '--parent-sha256', parent_sha, '--seconds', deadline]
with output.open('xb', buffering=0) as log:
    worker = subprocess.Popen(cmd, cwd=root, env=env, stdin=subprocess.DEVNULL,
                              stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
print(json.dumps(dict(pid=worker.pid, job=str(root/job), gpu=gpu, gpu_uuid=uuid,
                      log=str(output), budget_seconds=int(deadline), parent_sha256=parent_sha)))
'''


def copy_checked(sftp, remote, local, expected):
    partial = local.with_suffix(local.suffix+'.partial')
    sftp.get(str(remote), str(partial))
    if expected is not None and digest(partial) != expected:
        raise ValueError(f'Downloaded artifact SHA mismatch for {local.name}')
    partial.replace(local)


def collect(session, remote, local, receipt):
    job = PurePosixPath(receipt['job'])
    finish_at = time.monotonic() + 900 + receipt['budget_seconds']
    local.mkdir(exist_ok=True)
    with session.open_sftp() as sftp:
        checked = set()
        last = 0.
        while time.monotonic() < finish_at:
            try:
                names = sftp.listdir(str(job))
            except FileNotFoundError:
                names = []
            for name in sorted(names):
                if name.endswith('.json') or name == 'ERROR.txt':
                    copy_checked(sftp, job/name, local/name, None)
            for marker in [n for n in names if (n.startswith('model_') and n.endswith('.pt.json')) or n == 'FINAL.json']:
                data = json.loads((local/marker).read_text(encoding='utf-8'))
                name = data['checkpoint']
                if name not in checked:
                    copy_checked(sftp, job/name, local/name, data['sha256'])
                    checked.add(name)
                    print('CHECKPOINT', name, data['sha256'], data['ppo_updates'], data['optimizer_steps'], flush=True)
            if time.monotonic() - last >= 30.:
                for name in ('LATEST.json', 'FIRST_UPDATE.json', 'PROBE.json'):
                    path = local/name
                    if path.is_file():
                        print(name, path.read_text(encoding='utf-8')[:1800], flush=True)
                        break
                last = time.monotonic()
            if 'SAFE_CLOSED.json' in names or 'ERROR.txt' in names:
                copy_checked(sftp, PurePosixPath(receipt['log']), local/'worker.log', None)
                if 'ERROR.txt' in names:
                    raise RuntimeError((local/'ERROR.txt').read_text(encoding='utf-8'))
                if not ('PROBE.json' in names or 'FINAL.json' in names):
                    raise RuntimeError(f'Worker closed without results. See {local}/worker.log')
                return
            check_live = remote_python(session, PYTHON, 'import pathlib,sys;print(pathlib.Path("/proc",sys.argv[1],"cmdline").is_file())', [receipt['pid']]).strip()
            if check_live == 'False':
                copy_checked(sftp, PurePosixPath(receipt['log']), local/'worker.log', None)
                raise RuntimeError(f'Worker exited before completion. See {local}/worker.log')
            time.sleep(8.)
    raise TimeoutError(f'Collector deadline elapsed for {job}')


def main():
    parser = ArgumentParser()
    parser.add_argument('action', choices=('probe', 'train', 'collect'))
    parser.add_argument('tag')
    parser.add_argument('--parent', choices=PARENTS, default='old010')
    parser.add_argument('--gpu', type=int, default=0)
    parser.add_argument('--seconds', type=int, default=360, choices=(360,600))
    args = parser.parse_args()
    if not args.tag.replace('_', '').isalnum():
        parser.error('tag must be alphanumeric with optional underscores')
    local_root = ARCHIVE / args.tag
    remote_root = REMOTE / args.tag
    local_root.mkdir(parents=True, exist_ok=True)
    name = 'probe' if args.action == 'probe' else 'train'
    local = local_root / name
    receipt_path = local_root / f'{name}_LAUNCH.json'
    with connect(HOST) as session:
        if args.action == 'collect':
            receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
            collect(session, remote_root, local, receipt)
            return
        if args.action == 'probe':
            bundle = local_root / 'inputs.tar.gz'
            info = get_bundle(args.parent, bundle)
            manifest = local_root / 'INPUTS.json'
            manifest.write_text(json.dumps(info, indent=2)+'\n', encoding='utf-8')
            root = shlex.quote(str(remote_root))
            execute(session, f'mkdir -p {shlex.quote(str(REMOTE))} && mkdir {root}')
            with session.open_sftp() as sftp:
                sftp.put(str(bundle), str(remote_root/'inputs.tar.gz'), confirm=True)
            execute(session, f'cd {root} && echo {shlex.quote(digest(bundle)+"  inputs.tar.gz")} | sha256sum -c && tar -xzf inputs.tar.gz', timeout=120)
        else:
            info = json.loads((local_root/'INPUTS.json').read_text(encoding='utf-8'))
            for name_ in ('e0_env.py','train_e0.py'):
                if info['code_sha256'][name_] != digest(HERE/name_):
                    raise RuntimeError('Source changed since verified probe. Use a new tag.')
        receipt = json.loads(remote_python(session, PYTHON, RUN_SCRIPT, [remote_root, name, args.gpu,
                             info['parent_sha256'], 0 if name == 'probe' else args.seconds, PYTHON]))
        receipt_path.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
        print(receipt, flush=True)
        collect(session, remote_root, local, receipt)


if __name__ == '__main__':
    main()
