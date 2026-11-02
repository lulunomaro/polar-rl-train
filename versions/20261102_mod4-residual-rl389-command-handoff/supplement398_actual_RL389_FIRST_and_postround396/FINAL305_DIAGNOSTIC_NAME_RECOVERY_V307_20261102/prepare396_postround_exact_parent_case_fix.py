"""Independent unused396 fixes case normalization in the sole-own-parent check."""
from pathlib import Path
import ast
import hashlib
import json
import re
import shutil
import time

P = Path(__file__).resolve().parent
T = P.parent
N = T / 'MPC_COMMAND_RESIDUAL_RL_V389_20261102'
OQ = T / 'RESIDUAL_RL389_POSTROUND_V395_20261102'
OE = T / 'RESIDUAL_RL389_INDEPENDENT_EVAL_V395_20261102'
Q = T / 'RESIDUAL_RL389_POSTROUND_V396_20261102'
E = T / 'RESIDUAL_RL389_INDEPENDENT_EVAL_V396_20261102'
H = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

def put(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)

assert not (N / 'reports/BIND388_POSTROUND_ONCE_CONSUMED.json').exists()
for row in json.loads((OQ / 'INDEX395_POSTROUND_FOR389_FROZEN.json').read_bytes())['files']:
    path = Path(row['path'])
    assert path.stat().st_size == row['bytes'] and H(path) == row['SHA']
put(P / 'reports/STATIC396_UNUSED395_PARENT_CASE_REJECTION.json', dict(
    epoch=time.time(), passed=False,
    issue='Parent command line is lowercased but expected RL389 script token was mixed-case',
    prior395_frozen_preserved=True, prior395_not_bound_or_launched=True,
    repair='Independent396 lowercases both sides; exact PID/create/exe/direct-parent requirements retained',
    network=0, SDK=0, model_reads=0, training389_changed=False))

def rename(text):
    protected = {}
    def hold(match):
        key = f'PINNEDVALUE{len(protected)}PLACEHOLDER'
        protected[key] = match.group(0)
        return key
    text = re.sub(r'GPU-[0-9a-f-]{36}|\b[0-9a-f]{64}\b', hold, text)
    text = text.replace('395', '396')
    for key, value in protected.items():
        text = text.replace(key, value)
    return text

for original, destination in ((OQ, Q), (OE, E)):
    assert not destination.exists()
    destination.mkdir()
    (destination / 'reports').mkdir()
    for source in sorted(original.rglob('*')):
        if not source.is_file() or '__pycache__' in source.parts:
            continue
        if source.name.startswith('INDEX') or source.parent.name == 'reports':
            continue
        dest = destination / rename(str(source.relative_to(original)))
        dest.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix in ('.py', '.json'):
            dest.write_text(rename(source.read_text('utf8')), encoding='utf8')
        else:
            shutil.copyfile(source, dest)

path = E / 'run396_eval_once.py'
text = path.read_text('utf8')
old = "'/postround396_close_RL389_eval_once.py' in actual['CommandLine']"
new = "'/postround396_close_RL389_eval_once.py'.lower() in actual['CommandLine']"
assert text.count(old) == 1
text = text.replace(old, new)
path.write_text(text, encoding='utf8')
task_path = E / 'TASK396_PENDING_FINAL_IDENTITY.json'
task = json.loads(task_path.read_bytes())
task['worker_SHA'] = H(E / 'source/evaluate396.py')
task_path.write_text(json.dumps(task, indent=2), encoding='utf8')

runner = ast.parse(text)
expected_node = next(node for node in ast.walk(runner)
                     if isinstance(node, ast.Assert) and "CommandLine" in ast.unparse(node.test)
                     and 'postround396' in ast.unparse(node.test))
fixture = dict(actual={'CommandLine': 'C:\\Python314\\python.exe -B C:\\task\\postround396_close_RL389_eval_once.py'})
assert eval(compile(ast.Expression(expected_node.test), '<parent-case-fixture>', 'eval'), fixture)
for path in list(Q.rglob('*.py')) + list(E.rglob('*.py')):
    ast.parse(path.read_text('utf8'), filename=str(path))
assert task['GPU_UUID'] == 'GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
assert task['worker_SHA'] == H(E / 'source/evaluate396.py')
assert H(N / 'INDEX389_SOURCE_TASK_CALLERS_FROZEN.json') == '57fa0b19306db14a451fcbf1efe272beb8304f68c1c907bc6b3d13cd7aa9411c'
put(Q / 'INDEX396_POSTROUND_FOR389_FROZEN.json', dict(epoch=time.time(), files=[
    dict(path=str(path), bytes=path.stat().st_size, SHA=H(path))
    for root in (Q, E) for path in sorted(root.rglob('*'))
    if path.is_file() and '__pycache__' not in path.parts]))
put(P / 'reports/STATIC396_POSTROUND_RL389_EXACT_PARENT_FIX.json', dict(
    epoch=time.time(), passed=True, root=str(Q), evalroot=str(E),
    indexSHA=H(Q / 'INDEX396_POSTROUND_FOR389_FROZEN.json'),
    training389_frozen_unchanged=True, prior390_394_395_unused_preserved=True,
    AST=True, actual_assertion_case_fixture_passed=True,
    exact_PID_create_exe_directparent_retained=True,
    model_reads=0, network=0, physics=0))
print(json.dumps(dict(passed=True, root=str(Q), indexSHA=H(Q / 'INDEX396_POSTROUND_FOR389_FROZEN.json'))))
