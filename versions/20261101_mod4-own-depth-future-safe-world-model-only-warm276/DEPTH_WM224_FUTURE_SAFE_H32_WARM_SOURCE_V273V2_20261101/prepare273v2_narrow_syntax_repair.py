"""Preserve the original AST false, repair one closing parenthesis in NEW bytes."""
from pathlib import Path
import hashlib
import json
import time

N = Path(__file__).resolve().parent
V1 = N.parent / 'DEPTH_WM224_FUTURE_SAFE_H32_WARM_SOURCE_V273_20261101'


def row(path):
    b = path.read_bytes()
    return dict(path=str(path), bytes=len(b), SHA=hashlib.sha256(b).hexdigest())


def write(path, value):
    with path.open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, allow_nan=False)


error_path = V1 / 'reports/ACTUAL273_NEW_FIRST_ANCHOR_H32_CPU_RETURNED.json'
error = json.loads(error_path.read_bytes())
assert error['passed'] is False and error['groups'] == [] and 'SyntaxError' in error['error']
old_index = V1 / 'INDEX273_V1_ORIGINAL_AST_REJECTION_FROZEN.json'
write(old_index, dict(epoch=time.time(), kind='ORIGINAL273_AST_REJECTED_BEFORE_TORCH_OR_FUNCTIONAL_CASE',
    passed=False, functional_groups_executed=0, Torch_imports=0, WM_models_constructed=0,
    optimizer_updates=0, actual_models_raw_SDK_GPU_remote=0,
    error='One missing closing parenthesis in _anchor_values packet-field loop',
    files=[row(p) for p in sorted(V1.rglob('*')) if p.is_file()]))
source = (V1 / 'future_safe_wm_warm273.py').read_text(encoding='utf8')
old = "('sensor_pose_native13', (n, 13)), ('environment_origins_world', (n, 3)), ('T_world_heading', (n, 4, 4)):"
new = "('sensor_pose_native13', (n, 13)), ('environment_origins_world', (n, 3)), ('T_world_heading', (n, 4, 4))):"
assert source.count(old) == 1
with (N / 'future_safe_wm_warm273.py').open('x', encoding='utf8') as f:
    f.write(source.replace(old, new))
test = (V1 / 'test273_new_first_anchor_H32_CPU_once.py').read_text(encoding='utf8')
for a, b in (('FROZEN273_NEW', 'FROZEN273V2_NEW'), ('CONSUMED273_NEW', 'CONSUMED273V2_NEW'),
             ('ACTUAL273_NEW', 'ACTUAL273V2_NEW')):
    test = test.replace(a, b)
with (N / 'test273v2_new_first_anchor_H32_CPU_once.py').open('x', encoding='utf8') as f:
    f.write(test)
prep = (V1 / 'prepare273_source_and_purpose.py').read_text(encoding='utf8')
for a, b in (('FROZEN273_NEW', 'FROZEN273V2_NEW'), ('ACTUAL273_NEW', 'ACTUAL273V2_NEW'),
             ('INDEX273_FUTURE', 'INDEX273V2_FUTURE'),
             ('NEW273_SUPPORTED_START', 'NEW273V2_SYNTAX_REPAIRED_SUPPORTED_START')):
    prep = prep.replace(a, b)
needle = "    files = sorted(f for f in N.rglob('*') if f.is_file())"
assert prep.count(needle) == 2
cut = prep.rfind(needle)
prep = prep[:cut] + "    V1 = T / 'DEPTH_WM224_FUTURE_SAFE_H32_WARM_SOURCE_V273_20261101'\n    files = sorted(f for f in V1.rglob('*') if f.is_file()) + sorted(f for f in N.rglob('*') if f.is_file())" + prep[cut+len(needle):]
with (N / 'prepare273v2_source_and_purpose.py').open('x', encoding='utf8') as f:
    f.write(prep)
with (N / 'HANDOFF273_ORIGINAL_ABI_SOURCE_REFERENCE.md').open('xb') as f:
    f.write((V1 / 'HANDOFF273_FIRST_ANCHOR_ONLY_WM_WARM_SOURCE.md').read_bytes())
write(N / 'SOURCE273V2_ORIGINAL_AST_FALSE_AND_ONE_CHARACTER_REPAIR.json', dict(
    epoch=time.time(), original_error=row(error_path), original_rejected_index=row(old_index),
    original_module=row(V1 / 'future_safe_wm_warm273.py'), selected_module=row(N / 'future_safe_wm_warm273.py'),
    original_AST_run_passed=False, original_functional_groups=0, original_WM_constructions=0,
    source_repair='one closing parenthesis only; no task/reward/physics/layout/loss semantics changed',
    test_change='new namespace purpose/consumed/report bindings only; original functional body was not reached',
    old_once_replayed=False, actual_models_raw_assets_SDK_GPU_remote_Git=0))
print(json.dumps(dict(preserved_original_false=True, new_source_prepared=True, Torch_or_model_reads=0)))
