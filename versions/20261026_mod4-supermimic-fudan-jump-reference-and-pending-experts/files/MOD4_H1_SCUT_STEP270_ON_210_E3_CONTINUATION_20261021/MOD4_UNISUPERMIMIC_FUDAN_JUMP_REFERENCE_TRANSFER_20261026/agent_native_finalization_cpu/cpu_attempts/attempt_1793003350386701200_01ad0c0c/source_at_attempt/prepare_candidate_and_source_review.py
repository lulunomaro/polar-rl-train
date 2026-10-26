"""New local source-only preparation. Never executes any old once or worker."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent
T = HERE.parent.parent
H = T / 'MOD4_UNISUPERMIMIC_H1_STEP270_ON72_CONVERGENCE_20261026'
P = T / 'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82Q_20261026/payloads/e2'
snapshots = HERE / 'source_snapshots'
snapshots.mkdir()
reports = HERE / 'reports'
reports.mkdir()
files = [
    H / 'candidate_source_v5/h1_supermimic_bridge_v1.py',
    H / 'check_actual_saved_RSL_logger_checkpoint_API_and_inference_CPU_v5_unused_once.py',
    H / 'candidate_source_v5/supermimic_vendor_v2/learner.py',
    P / 'h1_unisupermimic_step270_worker_v1.py',
    P / 'h1_step270_fullstate_checkpoint_candidate_uninstalled.py',
    P / 'h1_production_control_prefix_trace_v1.py',
    P / 'job0/runtime/isaac/mod4/rescue_training.py',
    P / 'job0/runtime/isaac/mod4/train_H1_ground_prelaunch_fullstate_v2.py',
]
for name in ('chassis_pd_checkpoint.py', 'gas_damping_checkpoint.py',
             'spring_pressure_checkpoint.py', 'action_delay_checkpoint.py',
             'feedback_delay_checkpoint.py', 'sensor_resume_contract.py'):
    files.append(P / 'job0/runtime/isaac/mod4' / name)
index = []
for source in files:
    raw = source.read_bytes()
    target = snapshots / (('bridge_v5_' if source.name == 'h1_supermimic_bridge_v1.py' else '') + source.name)
    with target.open('xb') as stream:
        stream.write(raw)
    index.append(dict(path=str(source), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest(),
                      snapshot=str(target), source_only=True))
assert index[0]['SHA'] == 'c12656e931aaee8a8288bc0881555fb134ae4cf9f1201a85b3e760d1f9026289'

source_report = T / 'MOD4_MIXED_PRECISION_STEP_THROUGHPUT_AFTER67_20261025/reports/ACTUAL_RSL_RUNNER_LOGGER_SOURCE_AND_RESOURCE_72_ACTUAL.json'
rows = json.loads(source_report.read_text('utf8'))['sources']
saved_rsl = []
for row in rows:
    target = snapshots / ('captured_RSL_' + Path(row['path']).name)
    with target.open('x', encoding='utf8', newline='') as stream:
        stream.write(row['text'])
    saved_rsl.append(dict(original_path=row['path'], original_bytes=row['bytes'],
                          original_SHA=row['SHA'], snapshot=str(target),
                          snapshot_SHA=hashlib.sha256(target.read_bytes()).hexdigest()))
original = files[0].read_text('utf8')
tree = ast.parse(original)
run = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'run')
old_save = next(node for node in run.body if isinstance(node, ast.FunctionDef) and node.name == 'save')
failed = next(node for node in run.body if isinstance(node, ast.Assign)
              and ast.unparse(node) == 'failed = False')
lines = original.splitlines(keepends=True)
new_save = '''    publisher = NativeCheckpointPublisher(oldsave, learner, bridge, out, producer=dict(
        bridge_source_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        finalization_source_SHA=finalization_source_sha(),
        bootstrap_task_source_SHA=task['source_SHA'],
        native_not_production_H1_or_E2_source=True))

    def save(path, *args, **kwargs):
        return publisher(path, *args, **kwargs)
'''
tail = '''    return run_native_lifecycle(
        train=learner.train, stop_types=(OwnCompleteSavedStop,),
        persist_trace=trace.persist, save=save, out=out,
        iteration=lambda: learner.iteration,
        world_updates=lambda: bridge.wm_updates,
        policy_updates=lambda: bridge.pi_updates,
        events=trace.lifetime_goal_counter.snapshot)
'''
candidate = ''.join(lines[:old_save.lineno - 1]) + new_save + ''.join(lines[old_save.end_lineno:failed.lineno - 1]) + tail
candidate = candidate.replace('import torch\n',
    'import torch\nfrom native_finalization_v1 import NativeCheckpointPublisher, run_native_lifecycle, source_sha as finalization_source_sha\n', 1)
candidate_path = HERE / 'h1_supermimic_bridge_v1.py'
with candidate_path.open('x', encoding='utf8', newline='') as stream:
    stream.write(candidate)
diff = ''.join(difflib.unified_diff(original.splitlines(True), candidate.splitlines(True),
                                  fromfile='installed82Q_candidate_source_v5/h1_supermimic_bridge_v1.py',
                                  tofile='UNINSTALLED_native_finalization_v6/h1_supermimic_bridge_v1.py'))
with (HERE / 'native_finalization_v6_exact.diff').open('x', encoding='utf8') as stream:
    stream.write(diff)
review = dict(
    attempt_id='native-finalization-source-preparation-v1', epoch=time.time(),
    stage='local_source_CPU_preparation_only', candidate_uninstalled=True,
    source_index=index, saved_RSL_sources=saved_rsl,
    actual82Q=dict(world_updates=670, policy_updates=57, complete_preupdate69_reported=True,
                   FINAL_json_absent=True, final_file_stat_only_bytes=140498700,
                   final_producer_SHA='UNKNOWN', node_rc=0, original_error=True, final=None,
                   cause='UNPROVEN', evidence='Parent supplied closed metadata; no pilot content read'),
    prospective_source_gaps=[
        'trace.persist() before guarded save can prevent any terminal save/manifest',
        'oldsave exceptions including a scenario SavedStop can prevent native augmentation',
        'stat/hash/event-snapshot/manifest failure outside save try can leave FINAL absent',
        'a secondary trace/save/receipt error can replace a primary learning traceback',
    ],
    save_stop_constraint=(
        'Do not swallow oldsave SavedStop: upper D0-D7/task wrappers may not have run. '
        'This candidate retains the fresh stage and emits explicit failure receipts. '
        'No closure mutation, environment-variable suppression, guessed state reconstruction, '
        'or stale existing-file promotion is used.'),
    no_actual_cause_or_skill_convergence_claim=True,
    no_remote_GPU_environment_actor_forward_training_checkpoint_read_or_budget_action=True,
    local_tool_reader_errors_preserved=[
        dict(kind='overbroad_filename_listing', result='truncated; narrowed subsequent searches'),
        dict(kind='source_path_lookup', path='payloads/e2/job0/runtime/isaac/mod4/h1_step270_fullstate_checkpoint_candidate_uninstalled.py',
             result='not found; actual source is payloads/e2/h1_step270_fullstate_checkpoint_candidate_uninstalled.py'),
        dict(kind='source_path_lookup', path='payloads/e2/job0/runtime/isaac/mod4/sensor_checkpoint.py',
             result='not found; no execution; actual source sensor_resume_contract.py read'),
    ],
    Git_status='PENDING_ROOT_PHASE_ARCHIVE_NO_AGENT_GIT_WRITE',
)
with (reports / 'SOURCE_REVIEW_AND_PREPARATION_ACTUAL.json').open('x', encoding='utf8') as stream:
    json.dump(review, stream, indent=2)
print(json.dumps(dict(candidate=str(candidate_path), source_SHA=index[0]['SHA'], source_review_passed=True)))
