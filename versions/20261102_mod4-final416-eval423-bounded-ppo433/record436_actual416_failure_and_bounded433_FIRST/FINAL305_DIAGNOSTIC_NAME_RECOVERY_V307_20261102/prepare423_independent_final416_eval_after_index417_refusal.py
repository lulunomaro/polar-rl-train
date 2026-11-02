"""Independent423 repairs local self-index417 failure; preserves all frozen417 evidence."""
from pathlib import Path
import ast
import hashlib
import json
import time

P = Path(__file__).resolve().parent
T = P.parent
R = P / 'reports'
N = T / 'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V416_20261102'
OLD = T / 'RL416_FINAL_INDEPENDENT_EVAL_V417_20261102'
NEW = T / 'RL416_FINAL_INDEX_REPAIRED_EVAL_V423_20261102'
read = lambda path: json.loads(path.read_bytes())
H = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

def put(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)

assert not NEW.exists()
cpu_path = N / 'reports/ROOT416_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'
cpu = read(cpu_path)
assert cpu['passed'] and cpu['Pi'] == 160 and cpu['finite_tensors'] == 747
assert cpu['SHA'] == '8365d243006ef5ed6818d01298003107808f918347ad929f4ea936544f96e01a'
closed = read(N / 'reports/ROOT416_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
assert closed['owner_closed']['canonical_None'] and closed['owner_closed']['shared_locks_free']
assert closed['roles']['jump_72']['qualified_formal']
assert not (OLD / 'reports/ROOT417_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
index = OLD / 'INDEX417_SOURCE_TASK_CALLERS_FROZEN.json'
bad = []
for row in read(index)['files']:
    path = Path(row['path'])
    actual_sha = H(path)
    if path.stat().st_size != row['bytes'] or actual_sha != row['SHA']:
        bad.append(dict(path=str(path), frozen_bytes=row['bytes'], frozenSHA=row['SHA'],
            actual_bytes=path.stat().st_size, actualSHA=actual_sha))
assert len(bad) == 1 and Path(bad[0]['path']) == index and bad[0]['frozen_bytes'] == 0
NEW.mkdir()
(NEW / 'source').mkdir()
(NEW / 'reports').mkdir()
copied = []
for path in sorted((OLD / 'source').rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts or path.name == 'evaluate417.py':
        continue
    dest = NEW / 'source' / path.relative_to(OLD / 'source')
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(path.read_bytes())
    assert H(dest) == H(path)
    copied.append(dict(path=str(dest), source=str(path), bytes=dest.stat().st_size, SHA=H(dest)))
for name in ('feedforward389.json', 'reference389.npz'):
    dest = NEW / name
    dest.write_bytes((OLD / name).read_bytes())
    assert H(dest) == H(OLD / name)
    copied.append(dict(path=str(dest), source=str(OLD / name), bytes=dest.stat().st_size, SHA=H(dest)))

def named423(source):
    for token in ('contract', 'evaluate', 'target', 'TASK', 'INDEX', 'PACKAGE', 'ROOT', 'PARENT',
        'ACTUAL', 'RESULT', 'PROGRESS', 'ENV', 'APP', 'ORIGINAL', 'REPLAY', 'VIEW', 'VISIBLE_REPLAY', 'PhysX'):
        source = source.replace(token + '417', token + '423')
    source = source.replace('FROZEN416_ACTUAL_RESIDUAL_PPO_EVAL417', 'FROZEN416_ACTUAL_RESIDUAL_PPO_EVAL423')
    return source

def py(path, value):
    ast.parse(value)
    path.write_bytes(value.encode('utf8'))

worker = named423((OLD / 'source/evaluate417.py').read_text('utf8'))
worker = worker.replace('Frozen RL389 actor + fixed command baseline', 'Frozen actualPPO416 actor + fixed command baseline')
assert "ck['kind']=='ACTUAL_RESIDUAL_PPO416_COMPLETE'" in worker
py(NEW / 'source/evaluate423.py', worker)
parent = named423((OLD / 'target417_parent.py').read_text('utf8'))
assert 'from contract423 import' in parent and "P/'source/evaluate423.py'" in parent
py(NEW / 'target423_parent.py', parent)
py(NEW / 'contract423.py', named423((OLD / 'contract417.py').read_text('utf8')))
caller = named423((OLD / 'run417_eval_once.py').read_text('utf8'))
caller = caller.replace('run417_eval', 'run423_eval')
caller = caller.replace('Own locked final286 evaluation; new purpose, no learning or account mutation.',
    'Independent final416 evaluation after local417 self-index refusal; no learning or account mutation.')
caller = caller.replace("assert len(own)==1 and own[0]['ExecutablePath'].lower()==sys.executable.lower()",
    "assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].replace(chr(92),'/').lower()==sys.executable.replace(chr(92),'/').lower()")
assert 'H(N/\'INDEX423_SOURCE_TASK_CALLERS_FROZEN.json\')' in caller
py(NEW / 'run423_eval_once.py', caller)
view = named423((OLD / 'view417_actual_RL_replay.py').read_text('utf8'))
view = view.replace('Visible replay of actual frozen final389', 'Visible replay of actual frozen final416')
view = view.replace('417N /50Hz', '400N /50Hz')
py(NEW / 'view423_actual_RL_replay.py', view)
render = named423((OLD / 'render417_recorded_frames.py').read_text('utf8'))
render = render.replace('view417_actual_RL_replay', 'view423_actual_RL_replay')
render = render.replace('Native renderer of already recorded417', 'Native renderer of already recorded423')
render = render.replace('RECORDED417_NATIVE_FRAMES', 'RECORDED423_NATIVE_FRAMES')
render = render.replace('learned residual RL389', 'learned actual residual PPO416')
py(NEW / 'render423_recorded_frames.py', render)
task = read(OLD / 'TASK417_FROZEN.json')
assert task['model_SHA'] == cpu['SHA'] and task['model_bytes'] == cpu['bytes']
assert task['source_full_CPU_receipt_SHA'] == H(cpu_path)
task.update(kind='FROZEN416_ACTUAL_RESIDUAL_PPO_EVAL423', worker_SHA=H(NEW / 'source/evaluate423.py'),
    human_request='Independent actualPPO416 eval after local417self-index refusal; samefinal/samephysicalprotocol',
    distinct_evaluation_purpose='Firstactualindependent416skill evaluation;417never reachednetworkSDKmodelphysics',
    original417_selfindex_refusal_preserved=True)
put(NEW / 'TASK423_FROZEN.json', task)
import importlib.util
spec = importlib.util.spec_from_file_location('contract423', NEW / 'contract423.py')
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)
contract.validate_task(task)
assert H(NEW / 'feedforward389.json') == task['fixed_feedforward']['SHA']
assert H(NEW / 'reference389.npz') == task['reference']['SHA']
index423 = NEW / 'INDEX423_SOURCE_TASK_CALLERS_FROZEN.json'
# Materialize the complete file list before creating the index: no self reference.
frozen = [dict(path=str(path), bytes=path.stat().st_size, SHA=H(path))
    for path in sorted(NEW.rglob('*')) if path.is_file() and '__pycache__' not in path.parts]
assert all(Path(row['path']) != index423 for row in frozen)
put(index423, dict(epoch=time.time(), files=frozen, self_excluded=True))
for row in read(index423)['files']:
    path = Path(row['path'])
    assert path.stat().st_size == row['bytes'] and H(path) == row['SHA']
for path in NEW.rglob('*.py'):
    ast.parse(path.read_bytes())
put(R / 'STATIC423_FINAL416_SELF_INDEX417_REFUSAL_REPAIR.json', dict(epoch=time.time(), passed=True,
    old417_index=str(index), old417_indexSHA=H(index), old417_mismatches=bad,
    old417_network_SDK_model_physics=0, old417_normal_and_CPU_consumed_no_replay=True,
    final416_cpu=cpu, new_root=str(NEW), new_index=str(index423), new_indexSHA=H(index423),
    exact_copied_source_and_data=copied, source_eval_behavior_preserved_except_namespace=True,
    fixed_seed9137_same270_80firstepisodes400controls=True, modelreads=0, SDK=0, physics=0, network=0))
print(json.dumps(dict(passed=True, root=str(NEW), indexSHA=H(index423), files=len(frozen),
    selfindex_excluded=True, SDK=0, physics=0, modelreads=0)))
