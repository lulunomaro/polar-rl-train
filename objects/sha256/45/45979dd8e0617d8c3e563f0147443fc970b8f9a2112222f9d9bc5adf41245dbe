"""One-time guarded handoff to the stronger flat posture reward experiment."""
from __future__ import annotations

import glob
import hashlib
import json
import os
import signal
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/home/egde/rl_candidates/MOD4_takeover_20260914')
OLD = ROOT / 'scut_v14_spring_mod4_20260928'
NEW = ROOT / 'scut_v14_strong_posture_20260928'
OLD_STATUS = OLD / 'run/scut_v14_linear_spring_continue_20260928/status.json'
NEW_STATUS = NEW / 'run/scut_v14_strong_posture_20260928/status.json'
PYTHON = '/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'


def matches(pid: int, needle: str) -> bool:
    try:
        return needle in Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0', b' ').decode()
    except FileNotFoundError:
        return False


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def main() -> None:
    if NEW_STATUS.exists():
        raise SystemExit(f'refusing duplicate: {NEW_STATUS}')
    status = json.loads(OLD_STATUS.read_text())
    if status.get('state') != 'training':
        raise SystemExit(f'old state is {status.get("state")!r}')
    dry = NEW / 'run/dryrun_posture_20260928/report.json'
    if not dry.exists():
        raise SystemExit('posture dryrun has not completed')
    report = json.loads(dry.read_text())
    if (report['dry_run']['max_closure_error_m'] > .002 or
            report['dry_run']['mean_episode_len_steps'] < 50 or
            not (-100 < report['dry_run']['mean_reward'] < 100)):
        raise SystemExit('posture dryrun failed')
    supervisor = 995345
    launcher = int(status['segments'][-1]['pid'])
    if not matches(supervisor, 'supervise_scut_v14_spring.py'):
        raise SystemExit('old supervisor identity mismatch')
    if not matches(launcher, str(OLD / 'launch.py')):
        raise SystemExit('old launcher identity mismatch')
    if os.getpgid(launcher) != launcher:
        raise SystemExit('old launcher is not process-group leader')
    print('stopping old supervisor and launcher', supervisor, launcher, flush=True)
    os.kill(supervisor, signal.SIGTERM)
    os.killpg(launcher, signal.SIGINT)
    for _ in range(120):
        if not matches(launcher, str(OLD / 'launch.py')):
            break
        time.sleep(1)
    if matches(launcher, str(OLD / 'launch.py')):
        os.killpg(launcher, signal.SIGTERM)
        for _ in range(20):
            if not matches(launcher, str(OLD / 'launch.py')):
                break
            time.sleep(1)
    if matches(launcher, str(OLD / 'launch.py')):
        raise SystemExit('old launcher did not stop; refusing second trainer')
    paths = sorted(glob.glob(str(OLD / 'run/scut_v14_linear_spring_continue_20260928/segment_*/logs/*/model_*.pt')),
                   key=os.path.getmtime, reverse=True)
    checkpoint = None
    for path in paths:
        check = subprocess.run([PYTHON, '-c',
                                'import torch,sys; x=torch.load(sys.argv[1],map_location="cpu",weights_only=False); '
                                'assert "actor_state_dict" in x and "critic_state_dict" in x and "optimizer_state_dict" in x and "iter" in x',
                                path], capture_output=True, text=True, timeout=30)
        if check.returncode == 0:
            checkpoint = Path(path)
            break
    if checkpoint is None:
        raise SystemExit('no complete model+optimizer checkpoint found')
    digest = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    status['state'] = 'transferred_to_strong_posture'
    status['handoff_utc'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
    status['handoff_checkpoint'] = str(checkpoint)
    status['handoff_checkpoint_sha256'] = digest
    status['new_stage'] = str(NEW)
    OLD_STATUS.write_text(json.dumps(status, indent=2) + '\n')
    log = NEW / 'supervisor.log'
    command = [PYTHON, '-u', str(NEW / 'supervise_scut_v14_spring.py'),
               '--checkpoint', str(checkpoint), '--deadline-utc', status['deadline_utc']]
    with log.open('w') as output:
        proc = subprocess.Popen(command, cwd=NEW, stdin=subprocess.DEVNULL,
                                stdout=output, stderr=subprocess.STDOUT,
                                start_new_session=True)
    for _ in range(40):
        if NEW_STATUS.exists():
            new_status = json.loads(NEW_STATUS.read_text())
            if new_status.get('state') == 'training':
                print(json.dumps({'state': 'training', 'supervisor_pid': proc.pid,
                                  'checkpoint': str(checkpoint), 'sha256': digest,
                                  'deadline': status['deadline_utc']}, indent=2), flush=True)
                return
        if proc.poll() is not None:
            raise SystemExit(f'new supervisor exited {proc.returncode}: {log.read_text()[-2000:]}')
        time.sleep(1)
    raise SystemExit(f'new supervisor did not start within 40 s; inspect {log}')


if __name__ == '__main__':
    main()
