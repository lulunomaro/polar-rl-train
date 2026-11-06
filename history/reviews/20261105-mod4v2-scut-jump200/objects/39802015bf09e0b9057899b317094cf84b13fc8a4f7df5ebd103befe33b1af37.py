"""Fetch the already pinned public SCUT checkpoint from its Git object."""
from pathlib import Path
import hashlib
import json
import subprocess
import datetime

ROOT = Path(__file__).resolve().parent
REF = Path('C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL')
REV = '1a26356d6f591734d4f6f666f5cead1a6925da67'
PREFIX = 'pretrained/26_infantry/rough_rotation_stair/2026-07-23_16-23-21/'
items = []
for rel, expected in [('model_1000.pt', 'a52bbf91101302a1427273af553f941fb425ba8b'), ('exported/policy.pt', '565edab1aa30d52a6b58e515ab7ad421313af248')]:
    path = ROOT / Path(rel).name
    if not path.exists():
        payload = subprocess.run(['git', 'cat-file', 'blob', f'{REV}:{PREFIX}{rel}'], cwd=REF, check=True, capture_output=True, timeout=120).stdout
        path.write_bytes(payload)
    payload = path.read_bytes()
    blob = hashlib.sha1(f'blob {len(payload)}\0'.encode() + payload).hexdigest()
    assert blob == expected, (rel, blob)
    items.append({'path': str(path), 'bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest(), 'git_blob': blob, 'source_path': PREFIX + rel})
delta = subprocess.run(['git', 'diff', '--stat', REV, 'HEAD', '--', 'source/agent_tasks/agent_tasks/direct/wheelbipe', 'source/agent_world/agent_world/assets'], cwd=REF, check=True, capture_output=True, text=True).stdout
assert not delta.strip(), delta
out = {'attempt': 'scut-original-teacher-native-20261106', 'time': datetime.datetime.now().astimezone().isoformat(), 'source_commit': REV, 'runtime_ref': str(REF), 'runtime_task_and_assets_diff': delta, 'artifacts': items}
(ROOT / 'SOURCE_BINDING.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(out, ensure_ascii=False))
