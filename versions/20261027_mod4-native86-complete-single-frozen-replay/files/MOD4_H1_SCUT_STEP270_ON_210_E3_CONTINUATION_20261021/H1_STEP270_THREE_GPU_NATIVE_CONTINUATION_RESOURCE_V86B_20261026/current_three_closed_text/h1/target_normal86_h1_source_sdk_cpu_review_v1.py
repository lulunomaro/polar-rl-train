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
from h1_step270_fullstate_checkpoint_candidate_uninstalled import validate_new_phase, RETAINED_GROUPS
assert all(k in s for k in RETAINED_GROUPS) and 'H1_step270_task_state' in s
phase=s['H1_step270_task_state'];assert phase['version']==270
validate_new_phase(phase['phase'],20000)
assert s['H1_step270_runtime_contract']['original_D0_D7_STD_optimizer_save_chain_retained']
def finite(x):
    if torch.is_tensor(x):assert not x.is_floating_point() or torch.isfinite(x).all()
    elif isinstance(x,dict):
        for value in x.values():finite(value)
    elif isinstance(x,(list,tuple)):
        for value in x:finite(value)
finite(s)
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
from step270_reward_installed_CPU_v1 import check as reward_check
v['new_reward_integration_CPU']=reward_check(B,sdk.parent.parent/'managers/reward_manager.py',reference_path=B/'reference_sources/V5_h1_step270_path_reward_v1.py')
from step270_boundary_installed_CPU_v1 import check as boundary_check
v['boundary_repair_integration_CPU']=boundary_check(B)
v['reward_runtime_SHA']=H(B/'h1_step270_sdk_runtime_candidate.py')
v['reward_module_SHA']=H(B/'h1_step270_path_reward_v1.py')
from sampling_acceleration_installed_CPU_v2 import check as sampling_acceleration_check
v['sampling_acceleration_CPU']=sampling_acceleration_check(B,'h1')
(B / 'TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json').write_text(json.dumps(v,indent=2))
print(json.dumps(v))


# Reuse original one-load source object only after every original installed check.
from normal86_source_guard_v1 import complete_installed_CPU
normal86_complete_CPU = complete_installed_CPU(B, m, s, v)
print(json.dumps(normal86_complete_CPU))
