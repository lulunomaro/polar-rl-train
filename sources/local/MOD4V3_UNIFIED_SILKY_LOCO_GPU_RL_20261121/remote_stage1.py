"""Launch and collect Stage-1 on the assigned host72 GPU 0."""
from datetime import datetime, timezone
from argparse import ArgumentParser
import csv
import json
from pathlib import Path
import shlex
import sys
import tarfile
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'MOD4V3_E0_FLAT_ROUGH_REPAIR_20261120'))
from remote_e0 import DEPS, PITCH, PLANT, PARENTS, collect, connect, execute, location, remote_python
from train_silky_loco import PPO_SECONDS, RESUME_CHECKPOINTS, TRAIN_SECONDS_BY_TAG, sha256, put

HOST = 'host72'
ROOT, PYTHON = location(HOST)
ROOT = ROOT.parent / HERE.name
E0 = HERE.parent/'MOD4V3_E0_FLAT_ROUGH_REPAIR_20261120'
STAIR = HERE.parent/'MOD4V3_RL_SINGLE200_FULLDR_5OF5_20261118'
CODE = ('train_silky_loco.py', 'silky_loco_env.py', 'unified_soft_moe.py', 'silky_geometry.py')

GUARD = r'''
import hashlib, json, math, os, signal, subprocess, sys, time
from pathlib import Path
from silky_geometry import POLICY_SUBSTEPS, SUPPORT_STEPS

root, job, gpu, budget, launcher = sys.argv[1:]
budget = int(budget)
root = Path(root)
output = root / job
rows = subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,memory.used,utilization.gpu',
                               '-i', '0', '--format=csv,noheader,nounits'], text=True)
_, uuid, used, utilization = next(row.split(', ') for row in rows.splitlines() if row.split(',')[0] == gpu)
if uuid != 'GPU-16828f91-2b45-b646-8dc0-9481138e2842':
    raise SystemExit('GPU UUID does not match the assigned RTX 4090')
apps = subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid',
                                '-i', '0', '--format=csv,noheader,nounits'], text=True)
if int(used) > 150 or int(utilization) != 0 or uuid in apps.splitlines():
    raise SystemExit(f'GPU {gpu} is busy')
if budget:
    probe_bytes = (root/'probe/PROBE.json').read_bytes()
    probe = json.loads(probe_bytes)
    closed = json.loads((root/'probe/SAFE_CLOSED.json').read_text())
    exit_status = json.loads((root/'probe_EXIT.json').read_text())
    flat_ticks = probe['best_support_physics_steps']['flat'][0]
    gradient_groups = ('history_encoder', 'router', 'expert_0', 'expert_1', 'expert_2', 'expert_3')
    gradients_ok = all(probe['gradient_groups'][key]['all_finite']
                       and math.isfinite(probe['gradient_groups'][key]['l2'])
                       and probe['gradient_groups'][key]['l2'] > 0 for key in gradient_groups)
    if not (probe['steps'] == 600 and probe['envs'] == 2048
            and probe['physics_samples'] == probe['steps']*POLICY_SUBSTEPS
            and probe['optimizer_steps'] == probe['ppo_updates'] == probe['active_dr'] == 0
            and probe['rays_finite'] and probe['mesh_finite'] and probe['gradients_finite'] and gradients_ok
            and probe['actor_unchanged'] and probe['router_simplex_max_error'] < 1.e-6
            and flat_ticks >= SUPPORT_STEPS and closed['scene_closed']
            and exit_status['exit_code'] == 0 and not exit_status['hard_kill']):
        raise SystemExit('Precheck did not pass')
    (root/'train_PRECHECK.json').write_text(json.dumps(dict(passed=True, probe_reported_pass=probe['passed'],
        probe_sha256=hashlib.sha256(probe_bytes).hexdigest(), flat_continuous_support_steps=flat_ticks,
        required_support_steps=SUPPORT_STEPS, gpu_uuid=uuid)))
log = root / f'{job}.log'
started = time.monotonic()
with log.open('xb', buffering=0) as stream:
    worker = subprocess.Popen([launcher, '-B', '-u', str(root/'train_silky_loco.py'), str(output),
                               '--seconds', str(budget)], cwd=root,
        env=dict(os.environ, CUDA_VISIBLE_DEVICES=uuid, PYTHONUNBUFFERED='1'),
        stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
    receipt = root/f'{job}_REMOTE_LAUNCH.json'
    receipt.write_text(json.dumps(dict(pid=worker.pid, guard_pid=os.getpid(), job=str(output),
                   gpu=int(gpu), gpu_uuid=uuid, log=str(log), budget_seconds=budget)))
    hard_epoch = None
    kill_sent = False
    while worker.poll() is None:
        start_path = output/'TRAIN_START.json'
        if budget and hard_epoch is None and start_path.exists():
            hard_epoch = json.loads(start_path.read_text())['hard_stop_epoch']
        if hard_epoch is not None and time.time() >= hard_epoch:
            try:
                os.killpg(worker.pid, signal.SIGKILL)
                kill_sent = True
            except ProcessLookupError:
                pass
        if hard_epoch is None and time.monotonic()-started > (900 if budget else 1800):
            try:
                os.killpg(worker.pid, signal.SIGKILL)
                kill_sent = True
            except ProcessLookupError:
                pass
        time.sleep(.20)
    (root/f'{job}_EXIT.json').write_text(json.dumps(dict(exit_code=worker.returncode,
                       hard_kill=kill_sent, epoch=time.time(), hard_stop_epoch=hard_epoch)))
'''


def make_bundle(path, choice, landing_pool, warmstart_dir, resume=None):
    if choice == 'selected':
        manifest = json.loads((E0/'SELECTED_E0.json').read_text(encoding='utf-8'))
        parent, expected = E0/manifest['e0_checkpoint'], manifest['e0_sha256']
    else:
        parent, expected = PARENTS['c874']
    if sha256(parent) != expected:
        raise ValueError('Checkpoint hash mismatch')
    plan = json.loads((PITCH/'PLAN.json').read_text(encoding='utf-8'))['asset_identity']
    inputs = {f'plant/assets/{k}': v['sha256'] for k, v in plan['actual_training_assets'].items()}
    inputs['plant/mjcf/scene.xml'] = plan['local_mjcf_sha256']
    for key, digest in inputs.items():
        if sha256(PLANT/Path(key).relative_to('plant')) != digest:
            raise ValueError(f'Plant hash mismatch for {key}')
    inputs['parent.pt'] = expected
    for name in CODE:
        inputs[name] = sha256(HERE/name)
    warmstart_source = warmstart_dir/'WARMSTART_SOURCE.json'
    inputs['WARMSTART_SOURCE.json'] = sha256(warmstart_source)
    if resume is not None:
        checkpoint, resume_sha = resume
        if choice != 'selected' or sha256(checkpoint) != resume_sha:
            raise ValueError('Resume requires the pinned final checkpoint and SELECTED_E0')
        inputs['resume.pt'] = resume_sha
        policy_inputs = [(checkpoint, 'resume.pt')]
    else:
        warmstart = json.loads(warmstart_source.read_text())
        teacher = STAIR/'weights/model_rl_stair_best.pt'
        data = warmstart_dir/'WARMSTART_DATA.npz'
        inputs['stair_teacher.pt'] = sha256(teacher)
        inputs['WARMSTART_DATA.npz'] = sha256(data)
        if (inputs['stair_teacher.pt'] != warmstart['teacher_sha256']
                or inputs['WARMSTART_DATA.npz'] != warmstart['data_sha256']):
            raise ValueError('Warm-start source hash mismatch')
        policy_inputs = [(teacher, 'stair_teacher.pt'), (data, 'WARMSTART_DATA.npz')]
    if landing_pool is not None:
        inputs['JUMP_LANDING_POOL.json'] = sha256(landing_pool)
    manifest_path = path.parent/'INPUTS.json'
    put(manifest_path, inputs)
    with tarfile.open(path, 'w:gz', compresslevel=2) as bundle:
        for src, dst in ((DEPS, 'dependencies'), (PITCH/'support', 'support'), (PLANT, 'plant'),
                         (parent, 'parent.pt'), (manifest_path, 'INPUTS.json'),
                         (E0/'e0_env.py', 'support/mod4v3_ppo_v1/e0_env.py'),
                         (warmstart_source, 'WARMSTART_SOURCE.json'), *policy_inputs,
                         *((HERE/name, name) for name in CODE)):
            bundle.add(src, arcname=dst, filter=lambda item: (
                None if '__pycache__' in item.name or item.name.endswith('.pyc') else item))
        if landing_pool is not None:
            bundle.add(landing_pool, arcname='JUMP_LANDING_POOL.json')


def inventory():
    try:
        with connect(HOST) as session:
            rows = execute(session, 'nvidia-smi -i 0 --query-gpu=index,uuid,name,memory.total,memory.used,utilization.gpu --format=csv,noheader,nounits')
            processes = execute(session, 'nvidia-smi -i 0 --query-compute-apps=gpu_uuid,pid,used_gpu_memory --format=csv,noheader,nounits')
        apps = [{'uuid': gpu, 'pid': pid, 'memory_mib': used}
                for gpu, pid, used in csv.reader(processes.splitlines(), skipinitialspace=True)]
        gpus = [dict(index=int(index), uuid=gpu, name=name, memory_total_mib=int(total),
                     memory_used_mib=int(used), utilization_pct=int(util),
                     idle=int(used) <= 150 and int(util) == 0 and not any(a['uuid'] == gpu for a in apps))
                for index, gpu, name, total, used, util in csv.reader(rows.splitlines(), skipinitialspace=True)]
        return dict(connected=True, gpus=gpus, compute_processes=apps)
    except Exception as exc:
        return dict(connected=False, error=f'{type(exc).__name__}: {exc}', gpus=None)


def write_inventory():
    result = {'host72_gpu0': inventory()}
    result['observed_at_utc'] = datetime.now(timezone.utc).isoformat()
    result['idle_rule'] = '0% utilization, at most 150 MiB allocated, no compute process'
    put(HERE/'GPU0_INVENTORY_REFRESH.json', result)
    print(json.dumps(result, indent=2))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('inventory', 'probe', 'train', 'collect'), nargs='?', default='inventory')
    parser.add_argument('--tag', default='softmoe_r2')
    parser.add_argument('--gpu', type=int, choices=(0,), default=0)
    parser.add_argument('--parent', choices=('selected', 'c874'), default='selected')
    parser.add_argument('--job', choices=('probe', 'train'), default='probe')
    parser.add_argument('--landing-pool', type=Path)
    parser.add_argument('--warmstart', type=Path, default=HERE/'evidence/softmoe_r2_warmstart')
    args = parser.parse_args()
    if args.landing_pool is not None and args.action != 'probe':
        parser.error('--landing-pool is packaged by the probe and reused on train')
    if args.action == 'inventory':
        return write_inventory()
    if not args.tag.replace('_', '').isalnum():
        parser.error('Tag must contain letters, digits or underscores')
    job = args.job if args.action == 'collect' else args.action
    directory = HERE/'evidence'/args.tag
    directory.mkdir(parents=True, exist_ok=True)
    remote = ROOT/args.tag
    quoted = shlex.quote(str(remote))
    with connect(HOST) as session:
        if args.action == 'probe':
            bundle = directory/'inputs.tar.gz'
            resume = None
            if args.tag in RESUME_CHECKPOINTS:
                parent_tag, parent_sha = RESUME_CHECKPOINTS[args.tag]
                resume = (HERE/'evidence'/parent_tag/'train/model_final.pt', parent_sha)
            landing_pool = args.landing_pool
            if resume is not None and landing_pool is None:
                landing_pool = HERE/'JUMP_LANDING_POOL.json'
            make_bundle(bundle, args.parent, landing_pool, args.warmstart, resume)
            execute(session, f'mkdir -p {shlex.quote(str(ROOT))} && mkdir {quoted}')
            with session.open_sftp() as sftp:
                sftp.put(str(bundle), str(remote/bundle.name))
                with sftp.open(str(remote/'guard.py'), 'w') as f:
                    f.write(GUARD)
            execute(session, f'cd {quoted} && echo {shlex.quote(sha256(bundle)+"  "+bundle.name)}'
                             f' | sha256sum -c && tar -xzf {bundle.name}', timeout=120)
        if args.action == 'train':
            if not (HERE/'BASELINE_AUDIT.json').is_file():
                raise RuntimeError('Baseline audit is pending')
            audited = json.loads((directory/'INPUTS.json').read_text())
            for name in CODE:
                if sha256(HERE/name) != audited[name]:
                    raise RuntimeError('Source changed after precheck')
        receipt_path = directory/f'{job}_LAUNCH.json'
        if args.action != 'collect':
            if receipt_path.exists():
                raise RuntimeError('Job already launched')
            if args.action == 'train':
                with session.open_sftp() as sftp, sftp.open(str(remote/'guard.py'), 'w') as f:
                    f.write(GUARD)
            launch = ('import os,subprocess,sys; from pathlib import Path; '
                      'path=Path(sys.argv[1]); log=(path/(sys.argv[2]+"_guard.log")).open("xb",buffering=0); '
                      'p=subprocess.Popen([sys.executable,str(path/"guard.py"),*sys.argv[1:]],'
                      'cwd=path,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True);'
                      'print(p.pid)')
            budget = TRAIN_SECONDS_BY_TAG.get(args.tag, PPO_SECONDS) if job == 'train' else 0
            print('Guard PID', remote_python(session, PYTHON, launch,
                                            [remote, job, args.gpu, budget, PYTHON]), flush=True)
            read = ('import sys,time; from pathlib import Path; p=Path(sys.argv[1]); '
                    'exec("for i in range(60):\\n if p.exists():\\n  print(p.read_text());break\\n time.sleep(.25)")')
            raw = remote_python(session, PYTHON, read, [remote/f'{job}_REMOTE_LAUNCH.json'])
            if not raw.strip():
                raise RuntimeError(execute(session, f'cat {quoted}/{job}_guard.log'))
            put(receipt_path, json.loads(raw))
        receipt = json.loads(receipt_path.read_text())
        print(receipt, flush=True)
        status = None
        try:
            collect(session, remote, directory/job, receipt)
        finally:
            with session.open_sftp() as sftp:
                exit_name = f'{job}_EXIT.json'
                quit_by = time.monotonic()+20.
                while time.monotonic() < quit_by:
                    try:
                        with sftp.open(str(remote/exit_name), 'r') as handle:
                            status = json.load(handle)
                        put(directory/exit_name, status)
                        break
                    except (FileNotFoundError, json.JSONDecodeError):
                        time.sleep(.25)
                for name in (f'{job}_guard.log', f'{job}_PRECHECK.json'):
                    try:
                        sftp.get(str(remote/name), str(directory/name))
                    except FileNotFoundError:
                        pass
        if status is None or status['exit_code'] != 0 or status['hard_kill']:
            raise RuntimeError(f'{job} did not exit cleanly')


if __name__ == '__main__':
    main()
