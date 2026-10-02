"""Read current state, then launch one frozen alternate-seed evaluation only."""
from pathlib import Path
import importlib.util
import json
import os
import time

ROOT = Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930')
OUT = Path('/home/egde/rl_candidates/MOD4_AUTO_PROGRESS_NEXT_AI_20261001')
spec = importlib.util.spec_from_file_location('native_supervisor', ROOT/'isaac/mod4/supervise_native_floor.py')
sup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sup)

evaluators = []
for path in Path('/proc').glob('[0-9]*/cmdline'):
    try:
        argv = path.read_bytes().split(b'\0')
        if any(a.endswith(b'/validate_speed.py') for a in argv):
            evaluators.append(int(path.parent.name))
    except OSError:
        pass
receipt = OUT/'confirmation_launch.json'
if receipt.exists():
    print(receipt.read_text())
    raise SystemExit(0)
if evaluators:
    print(json.dumps({'deferred': 'existing evaluator', 'pids': evaluators}))
    raise SystemExit(0)
ck = sup.latest(ROOT/'logs')
info = sup.checkpoint(ck)
output = OUT/f'nominal_confirmation_model{info["iteration_stored"]}_seed20261001.json'
process = sup.spawn(['isaac/mod4/validate_speed.py', '--headless', '--checkpoint', str(ck),
    '--speed_limit', '1.5', '--ramp_suite', '--seed', '20261001', '--num_envs', '80',
    '--steps', '1500', '--output', str(output)], output.with_suffix('.log'))
data = {'pid': process.pid, 'started_epoch': time.time(), 'checkpoint': info,
        'seed': 20261001, 'output': str(output), 'production_modified': False,
        'scope': 'frozen nominal multi-seed confirmation; not a graduation claim'}
sup.atomic_json(receipt, data)
print(json.dumps(data))
