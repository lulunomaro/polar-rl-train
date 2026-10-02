"""Run an isolated MOD4 gain adaptation from the recorded v10 environment."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path('/home/egde/rl_candidates/MOD4_takeover_20260914')
CODE = ROOT / 'env_scaling_20260915/source/isaac/mod4'

parser = argparse.ArgumentParser()
parser.add_argument('--manifest', required=True)
parser.add_argument('--checkpoint', required=True)
parser.add_argument('--label', required=True)
parser.add_argument('--iterations', type=int, default=40)
parser.add_argument('--seed', type=int, default=202609173)
parser.add_argument('--clamp-leg-targets', action='store_true')
args = parser.parse_args()
if not re.fullmatch(r'flat_[A-Za-z0-9_]+', args.label) or args.iterations <= 0:
    raise ValueError('invalid stage label or iteration count')
checkpoint = Path(args.checkpoint).resolve(strict=True)
manifest_path = Path(args.manifest).resolve(strict=True)
manifest = json.loads(manifest_path.read_text())
recorded = manifest['env']
env = {k: v for k, v in os.environ.items() if not k.startswith('RM_')}
env.update({k: str(v) for k, v in recorded.items()
            if k.startswith('RM_') and v is not None})
old_gain = env.get('RM_LEG_KP')
if old_gain not in ('2500', '60'):
    raise ValueError('expected an audited v10/v11 gain baseline')
env.update(RM_LEG_KP='60', OMNI_KIT_ACCEPT_EULA='YES', PYTHONUNBUFFERED='1',
           CUDA_VISIBLE_DEVICES='0')
if args.clamp_leg_targets:
    env['RM_CLAMP_LEG_TARGETS'] = '1'
out = ROOT / 'repair_zero_success_20260916/flat_dr' / args.label
out.mkdir(parents=True, exist_ok=True)
audit = {
    'status': 'STARTING', 'initial_checkpoint': str(checkpoint),
    'initial_checkpoint_sha256': hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
    'baseline_manifest': str(manifest_path),
    'baseline_manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
    'environment_changes': {k: {'old': recorded.get(k), 'new': v}
                            for k, v in env.items() if k.startswith('RM_')
                            and str(recorded.get(k)) != v},
    'num_envs': 12000, 'steps_per_env': 48, 'additional_iterations': args.iterations,
    'seed': args.seed, 'learning_rate': 4e-5,
    'acceptance_note': 'Training completion is not stability acceptance. Nominal and mild DR require deterministic rollouts.',
}
status = out / 'stage_status.json'
if status.exists():
    raise FileExistsError(status)
status.write_text(json.dumps(audit, indent=2) + '\n')
command = [sys.executable, str(CODE / 'train_mod4_ppo.py'), '--headless',
           '--num_envs', '12000', '--additional_iterations', str(args.iterations),
           '--save_interval', '5', '--steps_per_env', '48', '--learning_rate', '0.00004',
           '--run_name', args.label, '--seed', str(args.seed), '--log_root', str(out / 'logs'),
           '--init_checkpoint', str(checkpoint), '--report', str(out / 'train_report.json')]
print('Audited continuation changes: ' + json.dumps(audit['environment_changes']), flush=True)
with (out / 'train.log').open('x') as log:
    result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT)
audit['returncode'] = result.returncode
iterations_seen = re.findall(r'Learning iteration\s+(\d+)/(\d+)', (out / 'train.log').read_text(errors='replace'))
audit['last_logged_iteration'] = int(iterations_seen[-1][0]) if iterations_seen else None
complete = (result.returncode == 0 and (out / 'train_report.json').is_file()
            and audit['last_logged_iteration'] == args.iterations - 1)
audit['status'] = 'TRAINING_FINISHED_UNEVALUATED' if complete else 'TRAINING_STOPPED_OR_FAILED'
models = list((out / 'logs').glob('*/model_*.pt'))
if models:
    latest = max(models, key=lambda p: p.stat().st_mtime_ns)
    audit['latest_checkpoint'] = str(latest)
    audit['latest_checkpoint_sha256'] = hashlib.sha256(latest.read_bytes()).hexdigest()
    (out / 'LATEST_CHECKPOINT.txt').write_text(str(latest) + '\n')
status.write_text(json.dumps(audit, indent=2) + '\n')
raise SystemExit(0 if complete else (result.returncode or 3))
