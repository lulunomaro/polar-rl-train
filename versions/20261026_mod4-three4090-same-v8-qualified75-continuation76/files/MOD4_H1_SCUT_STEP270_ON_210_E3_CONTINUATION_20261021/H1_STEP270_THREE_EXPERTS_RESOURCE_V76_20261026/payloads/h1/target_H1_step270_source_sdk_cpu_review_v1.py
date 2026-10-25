"""Installed source/SDK/RSL/whole checkpoint CPU check. Does not construct a scene."""
from pathlib import Path
import ast, hashlib, importlib.util, json, os, sys, time

os.environ['CUDA_VISIBLE_DEVICES'] = ''
import torch
torch.set_num_threads(2)
B = Path(sys.argv[1])
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
m = json.loads((B / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
for row in m['files']:
    p = B / row['relative']
    assert p.resolve().is_relative_to(B.resolve()) and not p.is_symlink()
    assert p.stat().st_size == row['bytes'] and H(p) == row['SHA'], row['relative']
    if p.suffix == '.py':
        ast.parse(p.read_text('utf8'))
src = B / 'job0/source' / m['source_filename']
assert H(src) == m['source_SHA']
s = torch.load(src, map_location='cpu', weights_only=False)
sys.path.insert(0, str(B))
from h1_step270_fullstate_checkpoint_candidate_uninstalled import validate_source
validate_source(s, 20000)
assert len(s['actor_state_dict']) == 9 and len(s['critic_state_dict']) == 8
assert len(s['optimizer_state_dict']['state']) == 17
assert {int(v['step']) for v in s['optimizer_state_dict']['state'].values()} == {m['source_Adamstep']}
rsl = Path(next(iter(importlib.util.find_spec('rsl_rl').submodule_search_locations)))
actual = []
for row in m['expected_actual_RSL_sources']:
    path = rsl / row['relative']
    assert path.stat().st_size == row['bytes'] and H(path) == row['SHA']
    actual.append(dict(path=str(path), SHA=H(path)))
sdk = Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations))) / 'utils/math.py'
assert H(sdk) == m['expected_actual_SDK_math_SHA']
assert not torch.cuda.is_initialized()
v = dict(epoch=time.time(), passed_CPU_only=True, key='h1',
         source_SHA=m['source_SHA'], all17Adam=m['source_Adamstep'],
         actor9_critic8_all6STD_and_D0_D7_finite_CPU=True,
         manifest_SHA=H(B / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),
         actual_RSL_sources=actual, actual_SDK_math=dict(path=str(sdk),SHA=H(sdk)),
         actual_optimizer_saved_LR=s['optimizer_state_dict']['param_groups'][0]['lr'],
         no_GPU_native_optimizer_or_GO=True)
(B / 'TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json').write_text(json.dumps(v,indent=2))
print(json.dumps(v))
