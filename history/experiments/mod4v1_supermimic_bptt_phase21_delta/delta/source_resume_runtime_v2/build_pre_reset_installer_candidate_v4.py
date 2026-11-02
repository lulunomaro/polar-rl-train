"""One-shot source addition: stable pre-reset installer hook, v2/v3 unchanged."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in HERE.glob('*.py') if path.name.endswith(('_v2.py', '_v3.py'))}
worker_old = 'worker_supermimic_bptt_actor_variant_candidate_v3.py'
worker_new = 'worker_supermimic_bptt_pre_reset_candidate_v4.py'
worker = (HERE / worker_old).read_text(encoding='utf-8')

def swap(text, old, new, count=1):
    assert text.count(old) == count, (old, text.count(old), count)
    return text.replace(old, new)

worker = swap(worker, 'from resume_runtime_contracts_v3 import (', 'from resume_runtime_install_hook_v4 import (install_optional_pose_cache_runtime_adapter,')
worker = swap(worker, 'bridge_adapter=None;actor_snapshot=None', 'bridge_adapter=None;actor_snapshot=None;pose_cache_handle=None;pose_cache_adapter=None;pose_cache_events=[]')
worker = swap(worker, 'guard.assert_new_nominals_unchanged();reset=env.reset();', '''guard.assert_new_nominals_unchanged()
  def record_pose_cache_event(event):
   pose_cache_events.append(dict(event));put(out/'POSE_CACHE_RUNTIME_ADAPTER_EVENTS_V3.json',dict(events=pose_cache_events,no_extra_observation_getters=True))
  pose_cache_handle,pose_cache_adapter=install_optional_pose_cache_runtime_adapter(env,task,J,callback=record_pose_cache_event);put(out/'POSE_CACHE_RUNTIME_ADAPTER_INSTALL_V3.json',pose_cache_adapter)
  reset=env.reset();''')
worker = swap(worker, 'command_binding=command_binding,bridge_adapter=bridge_adapter', 'command_binding=command_binding,bridge_adapter=bridge_adapter,pose_cache_adapter=pose_cache_adapter', count=2)
outputs = {worker_new: (worker_old, worker)}
for old in ('supermimic_original_owner_actor_variant_candidate_v3.py', 'supermimic_original_owner_shared_actor_variant_candidate_v3.py'):
    text = (HERE / old).read_text(encoding='utf-8')
    text = swap(text, 'from resume_runtime_contracts_v3 import ', 'from resume_runtime_install_hook_v4 import ')
    text = swap(text, worker_old, worker_new)
    outputs[old.replace('actor_variant_candidate_v3', 'pre_reset_candidate_v4')] = (old, text)

rows, patches = [], []
for name, (old, text) in outputs.items():
    ast.parse(text);compile(text, name, 'exec')
    assert not (HERE / name).exists()
    with (HERE / name).open('x', encoding='utf-8', newline='\n') as stream: stream.write(text)
    rows.append(dict(path=str(HERE / name), bytes=(HERE / name).stat().st_size, SHA=hashlib.sha256((HERE / name).read_bytes()).hexdigest()))
    patches.extend(difflib.unified_diff((HERE / old).read_text(encoding='utf-8').splitlines(True), text.splitlines(True), fromfile=str(HERE / old), tofile=str(HERE / name)))
assert before == {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in before}
with (HERE / 'PRE_RESET_INSTALLER_DIFF_V4.patch').open('x', encoding='utf-8') as stream: stream.write(''.join(patches))
receipt = dict(kind='SOURCE_ONLY_PARENT_STABLE_PRE_RESET_INSTALLER_HOOK_V4', outputs=rows,
               earlier_v2_v3_source_SHA_unchanged=before, SDK_imports=0, Torch_imports=0,
               actual_adapter_installed=0, native_runs=0, original_bridge_quaternion_guard_modified=False)
with (HERE / 'BUILD_PRE_RESET_INSTALLER_RECEIPT_V4.json').open('x', encoding='utf-8') as stream: json.dump(receipt, stream, indent=2)
print(json.dumps(receipt, indent=2))
