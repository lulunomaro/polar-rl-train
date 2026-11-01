"""Preserve the V1 pre-network interpreter failure; freeze independent V2 callers."""
from pathlib import Path
import ast, hashlib, json, sys, time
from compression import zstd
import paramiko

T = Path(__file__).resolve().parent
old = T / 'E2_QUALIFIED_FULLSTATE_SOLO_ROOT_CALLERS_V1_20261101'
new = T / 'E2_QUALIFIED_FULLSTATE_SOLO_ROOT_CALLERS_PY314_V2_20261101'
assert sys.version_info[:2] == (3, 14)
assert not new.exists()
old_index = old / 'INDEX_E2_SOLO_ROOT_CALLERS_FROZEN.json'
assert hashlib.sha256(old_index.read_bytes()).hexdigest() == '4ccfb1326b15f705f8f0aca1c88937384b940b018e55bf79f7f7a613477b4705'
old_manifest = json.loads(old_index.read_bytes())
new.mkdir(); (new / 'reports').mkdir()
def put(name, value):
    with (new / name).open('x', encoding='utf8', newline='\n') as f:
        json.dump(value, f, indent=2, allow_nan=False)
def H(data): return hashlib.sha256(data).hexdigest()
put('reports/ROOT235_PY314_REPAIR_PURPOSE_BEFORE_USE.json', dict(
    epoch=time.time(), kind='ROOT235_INDEPENDENT_CALLER_PY314_REPAIR',
    V1_original_error='ModuleNotFoundError: No module named compression',
    V1_failed_before_wrapper_install_auth_recovery_network=True,
    V1_model_SDK_network_GO_reads_writes=0,
    interpreter=sys.executable, version=sys.version,
    selected_existing_interpreter_imports=['compression.zstd', 'paramiko'],
    only_mutation='Require existing Python314 before control once marker; use independent V2 namespace',
    worker_reward_command_control_budget_physics_unchanged=True,
    old_fixture_model_raw_SDK_network_replays=0))
changes = []; parsed = 0
for row in old_manifest['files']:
    rel = row['relative']
    if not rel.endswith('.py') and rel != 'HANDOFF_THREE_ROOT_CALLERS.md':
        continue
    data = (old / rel).read_bytes()
    assert len(data) == row['bytes'] and H(data) == row['SHA']
    selected = data
    if rel in ('launch_e2_solo_install_FIRST_ROOT_ONLY_once.py',
               'collect_e2_solo_original_formal_cost_normal900_ROOT_ONLY_once.py'):
        text = data.decode('utf8')
        needle = 'def main():\n'
        normalized = text.replace('\r\n', '\n')
        assert normalized.count(needle) == 1
        normalized = normalized.replace(needle, needle + " assert sys.version_info[:2] == (3,14), 'Control transport requires existing Python314 compression.zstd'\n", 1)
        selected = normalized.encode('utf8')
        # The added early interpreter assertion is the sole executable AST change.
        before, after = ast.parse(text), ast.parse(normalized)
        a = next(n for n in after.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
        assert isinstance(a.body.pop(0), ast.Assert)
        assert ast.dump(before, include_attributes=False) == ast.dump(after, include_attributes=False)
    elif rel == 'HANDOFF_THREE_ROOT_CALLERS.md':
        s = data.decode('utf8')
        s = s.replace('C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe',
                      'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe', 2)
        s = ('ROOT V2 before-use correction: control launcher and normal collector use existing Python 3.14. '
             'V1 failed before network because its command selected the CPU Torch environment without compression.zstd. '
             'V1 source/false/once marker are immutable. NEW formal CPU still uses env_isaaclab.\n\n' + s)
        selected = s.encode('utf8')
    (new / rel).write_bytes(selected)
    if rel.endswith('.py'): ast.parse(selected); parsed += 1
    changes.append(dict(relative=rel, original_SHA=H(data), selected_SHA=H(selected), bytes_identical=selected == data))
original_cpu = old / 'reports/CPU_E2_SOLO_CALLERS_NEW_INTERFACE_ACTUAL.json'
assert json.loads(original_cpu.read_bytes())['passed']
put('reports/ROOT235_V1_SOURCE_AND_CPU_PROOF_REUSE.json', dict(
    original_frozen_index=str(old_index), original_frozen_index_SHA=H(old_index.read_bytes()),
    original_interface_CPU_ref=str(original_cpu), original_interface_CPU_SHA=H(original_cpu.read_bytes()),
    old_fixture_reexecutions=0, files=changes))
put('reports/CPU_E2_SOLO_CALLERS_NEW_INTERFACE_ACTUAL.json', dict(
    epoch=time.time(), kind='ROOT235_PY314_V2_INDEPENDENT_BEFORE_USE_SOURCE_CHECK', passed=True,
    new_source_AST=parsed, two_control_main_ASTs_identical_after_removing_early_interpreter_assert=True,
    existing_Python314_transport_imports_passed=True, original_V1_interface_proof_reused_by_SHA=True,
    worker_control_budget_reward_physics_changes=0,
    old_fixture_Torch_model_asset_raw_SDK_network_Git=0,
    actual_new_launcher='UNUSED_PENDING'))
files=[]
for p in sorted(new.rglob('*')):
    if p.is_file():
        b=p.read_bytes(); files.append(dict(relative=p.relative_to(new).as_posix(),path=str(p),bytes=len(b),SHA=H(b)))
put('INDEX_E2_SOLO_ROOT_CALLERS_FROZEN.json', dict(
    kind='ROOT235_E2_SOLO_ROOT_CALLERS_PY314_V2_FROZEN',frozen_epoch=time.time(),files=files,
    actual_network_model_SDK_GO=0, V1_false_and_frozen_source_unchanged=True))
idx = new / 'INDEX_E2_SOLO_ROOT_CALLERS_FROZEN.json'
print(json.dumps(dict(passed=True,root=str(new),index_SHA=H(idx.read_bytes()),files=len(files),source_AST=parsed)))
