"""Retain the actual MuJoCo input/one-shot integration attempt, including failures."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

T = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--checkpoint', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=False)
(a.output / 'source.py').write_bytes((T / 'mujoco_player.py').read_bytes())
command = [sys.executable, '-X', 'utf8', '-B', str(T / 'mujoco_player.py'),
           '--checkpoint', str(a.checkpoint), '--smoke', '--output', str(a.output / 'actual')]
result = subprocess.run(command, capture_output=True, text=True, encoding='utf8', timeout=90)
(a.output / 'console.log').write_text(result.stdout + result.stderr, encoding='utf8')
receipt = dict(epoch=time.time(), command=command, returncode=result.returncode,
               checkpoint=str(a.checkpoint.resolve()),
               checkpoint_sha256=hashlib.sha256(a.checkpoint.read_bytes()).hexdigest(),
               interface_and_one_shot_passed=result.returncode == 0,
               note='Integration check, not an independent skill success-rate evaluation')
(a.output / 'CHECK.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf8')
print(json.dumps(receipt, indent=2))
if result.returncode:
    print(result.stdout[-3000:] + result.stderr[-6000:])
    raise SystemExit(result.returncode)
