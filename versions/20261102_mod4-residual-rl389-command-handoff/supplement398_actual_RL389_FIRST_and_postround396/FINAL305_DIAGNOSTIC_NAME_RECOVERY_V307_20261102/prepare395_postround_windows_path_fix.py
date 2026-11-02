"""Independent unused395 fixes a Windows path comparison before any bind or launch."""
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
OQ = T / 'RESIDUAL_RL389_POSTROUND_V394_20261102'
OE = T / 'RESIDUAL_RL389_INDEPENDENT_EVAL_V394_20261102'
Q = T / 'RESIDUAL_RL389_POSTROUND_V395_20261102'
E = T / 'RESIDUAL_RL389_INDEPENDENT_EVAL_V395_20261102'
H = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

def put(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)

assert not (N / 'reports/BIND388_POSTROUND_ONCE_CONSUMED.json').exists()
oldindex = OQ / 'INDEX394_POSTROUND_FOR389_FROZEN.json'
for row in json.loads(oldindex.read_bytes())['files']:
    path = Path(row['path'])
    assert path.stat().st_size == row['bytes'] and H(path) == row['SHA']
put(P / 'reports/STATIC395_UNUSED394_WINDOWS_PATH_COMPARISON_REJECTION.json', dict(
    epoch=time.time(), passed=False, prior_index_SHA=H(oldindex),
    issue='CIM ExecutablePath uses backslashes while CONTROL has forward slashes; lower() alone compares unequal',
    prior394_frozen_preserved=True, prior394_not_bound_or_launched=True,
    repair='Independent395 normalizes slashes only for executable identity comparison',
    network=0, SDK=0, model_reads=0, training389_changed=False))

def rename(text):
    # Preserve every pinned SHA and GPU UUID while renaming only the version token.
    protected = {}
    pattern = r'GPU-[0-9a-f-]{36}|\b[0-9a-f]{64}\b'
    def hold(match):
        key = f'PINNEDVALUE{len(protected)}PLACEHOLDER'
        protected[key] = match.group(0)
        return key
    text = re.sub(pattern, hold, text)
    text = text.replace('394', '395')
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

path = Q / 'postround395_close_RL389_eval_once.py'
text = path.read_text('utf8')
old = "me['ExecutablePath'].lower()==CONTROL.lower()"
new = "me['ExecutablePath'].replace(chr(92),'/').lower()==CONTROL.replace(chr(92),'/').lower()"
assert text.count(old) == 1
text = text.replace(old, new)
path.write_text(text, encoding='utf8')

task_path = E / 'TASK395_PENDING_FINAL_IDENTITY.json'
prior = json.loads(task_path.read_bytes())
keys = ('kind','source_run','model_path','model_SHA','model_bytes','qualified240_package_root',
        'source_full_CPU_receipt_SHA','GPU_UUID','num_envs','seed','max_controls','worker_seconds',
        'physics_dt','policy_hz','feedback_hz','TGS','closure_m','mimic_rad','sdk_python',
        'worker_SHA','optimizer_steps','model_byte_reads','model_decodes','account_writes',
        'first_episode_only','human_request','actual_parent_private_EX_and_authority_admitted',
        'current_authority_binding','expected_Pi_updates','reference','evaluation_seed',
        'same_fixed_reference_course','heldout_terrain_layout','RL_residual','online_MPC')
task = {key: prior[key] for key in keys}
task.update(source_run='PENDING_RL389_FINAL',
            worker_SHA=H(E / 'source/evaluate395.py'),
            distinct_evaluation_purpose='Independent final RL389 actor+saved origin+fixed processed motor feedforward; no online MPC',
            feedforward_command_hz=50, source_saved_command_hz=100,
            control_resampling='Even source commands held at50Hz; not a100Hz closed-loop MPC reproduction',
            future_actual_depth_in_imagination=False)
task_path.write_text(json.dumps(task, indent=2), encoding='utf8')

for path in list(Q.rglob('*.py')) + list(E.rglob('*.py')):
    ast.parse(path.read_text('utf8'), filename=str(path))
assert 'import psutil' not in (Q / 'postround395_close_RL389_eval_once.py').read_text('utf8')
assert 'import psutil' not in (E / 'run395_eval_once.py').read_text('utf8')
assert 'C:\\Users\\lulu'.replace(chr(92),'/').lower() == 'C:/Users/lulu'.lower()
assert task['worker_SHA'] == H(E / 'source/evaluate395.py')
assert H(N / 'INDEX389_SOURCE_TASK_CALLERS_FROZEN.json') == '57fa0b19306db14a451fcbf1efe272beb8304f68c1c907bc6b3d13cd7aa9411c'
put(Q / 'INDEX395_POSTROUND_FOR389_FROZEN.json', dict(epoch=time.time(), files=[
    dict(path=str(path), bytes=path.stat().st_size, SHA=H(path))
    for root in (Q, E) for path in sorted(root.rglob('*'))
    if path.is_file() and '__pycache__' not in path.parts]))
put(P / 'reports/STATIC395_POSTROUND_RL389_WINDOWS_CIM_FIX.json', dict(
    epoch=time.time(), passed=True, root=str(Q), evalroot=str(E),
    indexSHA=H(Q / 'INDEX395_POSTROUND_FOR389_FROZEN.json'),
    training389_frozen_unchanged=True, prior390_394_unused_preserved=True,
    AST=True, Windows_path_comparison_fixture_passed=True,
    no_local_psutil_dependency=True, stale_MPC_task_metadata_removed=True,
    model_reads=0, network=0, physics=0))
print(json.dumps(dict(passed=True, root=str(Q), indexSHA=H(Q / 'INDEX395_POSTROUND_FOR389_FROZEN.json'))))
