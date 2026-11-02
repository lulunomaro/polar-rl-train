"""NEW v2 only: correct synthetic constructor init expectation; no Torch import."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
source = HERE / 'test_resume_legacy_torch_cpu_v1.py'
raw = source.read_bytes()
assert hashlib.sha256(raw).hexdigest() == '08c89b3603eb7b32b4eb430a9cde112035ca187695272ee992742ceb147079d7'
old = raw.decode('utf-8')
new = old
edits = [
    ('"""SYNTHETIC CPU Torch software validation; never native MOD4/physics training.',
     '"""V2: real vendor constructor initializes the fresh synthetic state exactly once.\n\nSYNTHETIC CPU Torch software validation; never native MOD4/physics training.'),
    ("        restored, fresh_env, restored_teacher, restored_snapshot = make_learner(view, directory / 'RESTORED_LEARNER_LOGS')\n",
     "        restored, fresh_env, restored_teacher, restored_snapshot = make_learner(view, directory / 'RESTORED_LEARNER_LOGS')\n        initializations_before_load = fresh_env.fresh_initializations\n        assert initializations_before_load == 1 and fresh_env.calls == 0\n"),
    ('        assert fresh_env.calls == fresh_env.fresh_initializations == 0\n        # Fresh environment state is first initialized by original collect; no old physical state import.\n',
     '        initializations_after_load = fresh_env.fresh_initializations\n        assert fresh_env.calls == 0 and initializations_after_load == initializations_before_load == 1\n        # Original vendor constructor _critic_input_dim -> _state_info already initialized once; loader adds none.\n'),
    ('        assert fresh_env.calls == fresh_env.fresh_initializations == 1\n',
     '        initializations_after_continue = fresh_env.fresh_initializations\n        assert fresh_env.calls == 1 and initializations_after_continue == initializations_before_load == 1\n'),
]
# The final receipt line is a separate exact literal below.
for before, after in edits:
    assert new.count(before) == 1, before
    new = new.replace(before, after)
before = '            only_one_fresh_initialization_before_continued_collection=True,\n'
after = ('            only_one_fresh_initialization_before_continued_collection=True,\n'
         '            synthetic_initialization_counts=dict(before_full_load=initializations_before_load,\n'
         '                after_full_load=initializations_after_load, after_continued_collect=initializations_after_continue),\n')
assert new.count(before) == 1
new = new.replace(before, after)
new = new.replace('SYNTHETIC_CPU_ACTUAL_LEGACY_A0_A1_AND_FULL_RESET_RESUME_NOT_NATIVE_V1', 'SYNTHETIC_CPU_ACTUAL_LEGACY_A0_A1_AND_FULL_RESET_RESUME_NOT_NATIVE_V2')
new = new.replace('SYNTHETIC_CPU_LEGACY_RESUME_SOFTWARE_TEST_ERROR_V1', 'SYNTHETIC_CPU_LEGACY_RESUME_SOFTWARE_TEST_ERROR_V2')
new = new.replace('SYNTHETIC_TORCH_RESUME_RECEIPT_V1.json', 'SYNTHETIC_TORCH_RESUME_RECEIPT_V2.json')
old_tree, new_tree = ast.parse(old), ast.parse(new)
dump = lambda n: ast.dump(n, include_attributes=False)
old_functions = {n.name: n for n in ast.walk(old_tree) if isinstance(n, ast.FunctionDef)}
new_functions = {n.name: n for n in ast.walk(new_tree) if isinstance(n, ast.FunctionDef)}
protected = [name for name in old_functions if name not in ('run', 'one_variant', 'main')]
assert all(dump(old_functions[name]) == dump(new_functions[name]) for name in protected)
assert not any(isinstance(n, ast.Import) and any(x.name == 'torch' for x in n.names) for n in new_tree.body)
path = HERE / 'test_resume_legacy_torch_cpu_v2.py'
compile(new, str(path), 'exec')
with path.open('x', encoding='utf-8', newline='') as stream: stream.write(new)
patch = ''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile=str(source), tofile=str(path)))
with (HERE / 'CONSTRUCTOR_INITIALIZATION_DIFF_V2.patch').open('x', encoding='utf-8', newline='') as stream: stream.write(patch)
receipt = dict(kind='SOURCE_ONLY_CONSTRUCTOR_EXPECTATION_CORRECTION_V2',
    original=dict(path=str(source), SHA256=hashlib.sha256(raw).hexdigest(), unchanged=True),
    candidate=dict(path=str(path), bytes=path.stat().st_size, SHA256=hashlib.sha256(path.read_bytes()).hexdigest()),
    exact_source_cause='supermimic_vendor_v2/learner.py:234-242 calls _state_info:225-232 during constructor -> one init_state',
    native_core_worker_contracts_modified=False, Torch_imported=False,
    correction='snapshot constructor init=1 before load; loader/continued collection add zero',
    AST_compile=True, all_other_functions_AST_identical=protected,
    old_CPU_failure_preserved='reports/LEGACY_A0_A1_FULL_RESUME_CPU_V1.json', actual_CPU_V2_result='PENDING_PARENT')
with (HERE / 'BUILD_CONSTRUCTOR_EXPECTATION_V2.json').open('x', encoding='utf-8') as stream: json.dump(receipt, stream, indent=2)
print(json.dumps(receipt, indent=2))
