"""Prepare the first actual final433 evaluation; preserve434 local refusal and all once receipts."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import time

P = Path(__file__).resolve().parent
T = P.parent
R = P / 'reports'
N = T / 'RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V433_20261102'
OLD = T / 'RL433_FINAL_INDEPENDENT_EVAL_V434_20261102'
NEW = T / 'RL433_FIRST_ACTUAL_INDEPENDENT_EVAL_V437_20261102'
H = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_bytes())


def put(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)


def py(path, source):
    ast.parse(source)
    path.write_bytes(source.encode('utf8'))


assert not NEW.exists()
cpu_path = N / 'reports/ROOT433_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'
cpu = read(cpu_path)
assert cpu['passed'] and cpu['finite_tensors'] == 795 and cpu['Pi'] == cpu['critic'] == 161
assert cpu['SHA'] == 'db6944ceca539106bb392a881185f1e85917efa5a9325bbeec72863f8240e04f'
assert cpu['bytes'] == 34402073 and cpu['totalWM'] == 30731
closed = read(N / 'reports/ROOT433_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
assert closed['owner_closed']['canonical_None'] and closed['owner_closed']['shared_locks_free']
role = closed['roles']['jump_72']
assert role['qualified_formal'] and role['formal']['SHA'] == cpu['SHA']
assert role['original_node_exit']['all_own_children_waited']
refusals = list((OLD / 'reports').glob('ROOT434_ORIGINAL_ERROR_*.json'))
assert len(refusals) == 1 and 'assert not other' in read(refusals[0])['error']
assert not (OLD / 'reports/ROOT434_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
assert not (OLD / 'reports/ROOT434_EVALUATION_FULL_RETURNED.json').exists()
for row in read(OLD / 'INDEX434_SOURCE_TASK_CALLERS_FROZEN.json')['files']:
    path = Path(row['path'])
    assert path.stat().st_size == row['bytes'] and H(path) == row['SHA']

NEW.mkdir()
(NEW / 'source').mkdir()
(NEW / 'reports').mkdir()
copied = []
for path in sorted((OLD / 'source').rglob('*.py')):
    if path.name == 'evaluate434.py':
        continue
    dest = NEW / 'source' / path.relative_to(OLD / 'source')
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = path.read_bytes()
    dest.write_bytes(data)
    copied.append(dict(path=str(dest), source=str(path), bytes=len(data), SHA=hashlib.sha256(data).hexdigest()))
for name in ('feedforward389.json', 'reference389.npz'):
    path = OLD / name
    data = path.read_bytes()
    (NEW / name).write_bytes(data)
    copied.append(dict(path=str(NEW / name), source=str(path), bytes=len(data), SHA=hashlib.sha256(data).hexdigest()))


def namespace(source, reverse=False):
    old, new = ('437', '434') if reverse else ('434', '437')
    for token in ('contract', 'evaluate', 'target', 'TASK', 'INDEX', 'PACKAGE', 'ROOT', 'PARENT',
                  'ACTUAL', 'RESULT', 'PROGRESS', 'ENV', 'APP', 'ORIGINAL', 'REPLAY', 'VIEW',
                  'VISIBLE_REPLAY', 'RECORDED', 'PhysX', 'FROZEN433_ACTUAL_RESIDUAL_PPO_EVAL'):
        source = source.replace(token + old, token + new)
    return source


original_worker = (OLD / 'source/evaluate434.py').read_text('utf8')
worker = namespace(original_worker)
# A reversible namespace edit leaves the actor, physical actions and acceptance AST identical.
assert ast.dump(ast.parse(namespace(worker, reverse=True))) == ast.dump(ast.parse(original_worker))
py(NEW / 'source/evaluate437.py', worker)
parent = namespace((OLD / 'target434_parent.py').read_text('utf8'))
assert 'from contract437 import' in parent and "P/'source/evaluate437.py'" in parent
py(NEW / 'target437_parent.py', parent)
py(NEW / 'contract437.py', namespace((OLD / 'contract434.py').read_text('utf8')))
caller = namespace((OLD / 'run434_eval_once.py').read_text('utf8')).replace('run434_eval', 'run437_eval')
caller = caller.replace('Independent final416 evaluation after local417 self-index refusal;',
                        'First actual final433 evaluation after434 local controller refusal;')
caller = caller.replace("patterns='MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021|RMPOLAR|",
                        "patterns='MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021|RMPOLAR|watch|E1collect|collect_actual|collect_generic|collect_nine|single_gpu|PAIR|")
caller = caller.replace("    assert not other, 'Independent417directcaller requires no other knowncontroller'\n\n    put('ROOT437_FRESH_EXACT_LOCAL_CIM.json',dict(epoch=time.time(),rows=rows))",
                        "    put('ROOT437_FRESH_EXACT_LOCAL_CIM.json',dict(epoch=time.time(),rows=rows,serialFREE=not other))\n    assert not other, 'Independent437 requires all other known controllers released'")
caller = caller.replace('MOD4_MPC_TARGET_COMPARISON417_', 'MOD4_RL433_FIRST_ACTUAL_EVAL437_')
assert 'MOD4_MPC_TARGET_COMPARISON' not in caller and 'serialFREE=not other' in caller
py(NEW / 'run437_eval_once.py', caller)
view = namespace((OLD / 'view434_actual_RL_replay.py').read_text('utf8'))
view = view.replace('frozen final416', 'frozen final433').replace('actual417 replay', 'actual437 replay')
view = view.replace("policy_updates='fromfinal416receipt'", "policy_updates=161")
py(NEW / 'view437_actual_RL_replay.py', view)
render = namespace((OLD / 'render434_recorded_frames.py').read_text('utf8'))
render = render.replace('view434_actual_RL_replay', 'view437_actual_RL_replay')
render = render.replace('already recorded434', 'already recorded437').replace('already recorded417 PhysXbodyposes', 'already recorded437 PhysX bodyposes')
py(NEW / 'render437_recorded_frames.py', render)

task = read(OLD / 'TASK434_FROZEN.json')
assert task['model_SHA'] == cpu['SHA'] and task['model_bytes'] == cpu['bytes']
assert task['model_path'] == role['formal']['path'] and task['source_full_CPU_receipt_SHA'] == H(cpu_path)
task.update(kind='FROZEN433_ACTUAL_RESIDUAL_PPO_EVAL437', worker_SHA=H(NEW / 'source/evaluate437.py'),
            human_request='First actual RL433 final evaluation after434 local busy refusal; no online MPC',
            distinct_evaluation_purpose='First actual final433 skill evaluation,80 firstepisodes seed9137 same270 newDR',
            original434_localbusy_refusal_preserved=True)
put(NEW / 'TASK437_FROZEN.json', task)
spec = importlib.util.spec_from_file_location('contract437', NEW / 'contract437.py')
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)
contract.validate_task(task)
assert H(NEW / 'feedforward389.json') == task['fixed_feedforward']['SHA']
assert H(NEW / 'reference389.npz') == task['reference']['SHA']
index = NEW / 'INDEX437_SOURCE_TASK_CALLERS_FROZEN.json'
frozen = [dict(path=str(path), bytes=path.stat().st_size, SHA=H(path))
          for path in sorted(NEW.rglob('*')) if path.is_file() and '__pycache__' not in path.parts]
assert all(Path(row['path']) != index for row in frozen)
put(index, dict(epoch=time.time(), files=frozen, self_excluded=True))
for row in frozen:
    path = Path(row['path'])
    assert path.stat().st_size == row['bytes'] and H(path) == row['SHA']
put(R / 'STATIC437_FINAL433_FIRST_EVAL_AFTER434_LOCALBUSY.json', dict(
    epoch=time.time(), passed=True, old434refusal=str(refusals[0]), old434refusalSHA=H(refusals[0]),
    old434_network_SDK_model_physics=0, old433normal_and_CPU_consumed_no_replay=True,
    final433_cpu=cpu, new_root=str(NEW), new_index=str(index), new_indexSHA=H(index),
    exact_copied_source_and_data=copied, worker_AST_identical_under_reversible_namespace=True,
    same_protocol_80firstepisodes_seed9137_400controls8s_edge8_270=True,
    inherited434_telemetry_labels_may_say_MPC_but_actor_path_has_no_MPC=True,
    current_roottranslation_in_reference_is_not_online_MPC=True,
    new_eval_unused=True, modelreads=0, SDK=0, physics=0, network=0))
print(json.dumps(dict(passed=True, root=str(NEW), indexSHA=H(index), files=len(frozen),
                     unused=True, modelreads=0, SDK=0, physics=0, network=0)), flush=True)
