"""Metadata-only prepare/freeze for a narrow new completion purpose."""
from pathlib import Path
import argparse
import hashlib
import json
import time

N = Path(__file__).resolve().parent
T = N.parent
R = N / 'reports'
V1 = T / 'OBSERVED_STATIC_SUPPORT_DEPTH_ANCHOR_CONTEXT_SOURCE_V271_20261101'
S255 = T / 'D435I_SUPERMIMIC_NATIVE_WM50_CONTEXT40_SOURCE_V255_20261101'
native = T / 'MOD4_H1_MATLAB_REFERENCE_IMAGINATION_TRACKING_RESOURCE_V165_20261030/payloads_v2/seed27/source'


def row(path):
    b = path.read_bytes()
    return dict(path=str(path), bytes=len(b), SHA=hashlib.sha256(b).hexdigest())


def write(path, value):
    with path.open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, allow_nan=False)


p = argparse.ArgumentParser()
p.add_argument('--freeze', action='store_true')
args = p.parse_args()
old_result = V1 / 'reports/ACTUAL271_NEW_STATIC_SUPPORT_CONTEXT_CPU_RETURNED.json'
old = json.loads(old_result.read_bytes())
assert old['passed'] is False and len(old['groups']) == 4 and all(g['passed'] for g in old['groups'])
assert 'FrozenInstanceError' in old['error']
if not args.freeze:
    old_index = V1 / 'INDEX271_V1_SYNTHETIC_MUTATION_READER_REJECTED_FROZEN.json'
    write(old_index, dict(epoch=time.time(), kind='FROZEN_V1_ORIGINAL_SYNTHETIC_FALSE',
        passed=False, completed_groups=4, refusals_completed=23,
        failure='Last fixture used augmented assignment on frozen dataclass field',
        source_runtime_bug_claimed=False, rerun=False,
        files=[row(f) for f in sorted(V1.rglob('*')) if f.is_file()]))
    for src, dst in ((V1 / 'observed_support_context271.py', N / 'observed_support_context271.py'),
        (V1 / 'HANDOFF271_OBSERVED_STATIC_SUPPORT_SOURCE_ONLY.md', N / 'HANDOFF271_V1_SOURCE_SEMANTICS_REFERENCE.md')):
        with dst.open('xb') as f:
            f.write(src.read_bytes())
    write(N / 'SOURCE271V2_ORIGINAL_FALSE_AND_EXACT_MODULE_JOIN.json', dict(
        epoch=time.time(), original_false=row(old_result), original_rejected_index=row(old_index),
        original_module=row(V1 / 'observed_support_context271.py'), selected_module=row(N / 'observed_support_context271.py'),
        module_byte_identical=True, original_four_groups=old['groups'],
        module_or_runtime_logic_changed=False, actual_models_raw_SDK_GPU_remote_reads=0,
        new_purpose='only complete unexecuted clone isolation/max belief age/RNG; no prior motion/gradient/refusal replay'))
    files = sorted(f for f in N.rglob('*') if f.is_file())
    write(R / 'FROZEN271V2_ONLY_UNFINISHED_CLONE_AGE_CPU_PURPOSE.json', dict(
        epoch=time.time(), purpose_ID='NEW271V2_FROZEN_DATACLASS_BUFFER_READER_ONLY_UNFINISHED_COMPLETION_CPU_ONCE',
        source_files=[row(f) for f in files], source255_directory=str(S255), native_source_directory=str(native),
        exact_counts=dict(runs=1, synthetic_envs=2, new_groups=1, previous_four_groups=0,
            previous_refusals=0, NN_models_constructed=0, optimizer_steps=0, real_controls=0,
            actual_models_raw_assets_SDK_GPU_remote_Git=0),
        original271_false_preserved=True, full_Pi_runtime_qualified=False))
    print(json.dumps(dict(new_completion_purpose_frozen=True, files=len(files), original_false_preserved=True)))
else:
    result_path = R / 'ACTUAL271V2_UNFINISHED_CLONE_AGE_CPU_RETURNED.json'
    result = json.loads(result_path.read_bytes())
    assert result['passed'] and result['previous_four_groups_replayed'] == 0
    assert row(V1 / 'observed_support_context271.py')['SHA'] == row(N / 'observed_support_context271.py')['SHA']
    # Explicit final selection contains ALL V1 false/source/purpose files and
    # ALL V2 new-purpose/completion files; ROOT need not choose by a glob.
    files = sorted(f for f in V1.rglob('*') if f.is_file()) + sorted(f for f in N.rglob('*') if f.is_file())
    index = N / 'INDEX271V2_OBSERVED_STATIC_SUPPORT_CONTEXT_SOURCE_FROZEN.json'
    write(index, dict(epoch=time.time(), kind='FROZEN_SOURCE_WITH_ORIGINAL_FALSE_AND_NARROW_SYNTHETIC_COMPLETION_V271V2',
        source_ready=True, original271_run_passed=False, original_four_groups_passed=True,
        independent_unfinished_completion_passed=True, same_module_aggregate_groups=5,
        original_refusals=23, old_fixture_or_once_replays=0,
        actual_models_raw_assets_SDK_GPU_SSH_remote_Git=0, actual_Pi_WM_updates=0,
        actual_future_safe_Pi_runtime_admitted=False, actual267_packet_missing_visible_floor=True,
        pending='new current-packet collector/actual scope/pose/depth admission and full H32 Pi runtime',
        original271_rejected_index=row(V1 / 'INDEX271_V1_SYNTHETIC_MUTATION_READER_REJECTED_FROZEN.json'),
        original_false=row(old_result), new_completion=row(result_path),
        Git_status='PENDING_ROOT_ORDINARY267_PHASE_APPEND', files=[row(f) for f in files]))
    print(json.dumps(dict(passed_source_completion=True, index=row(index), files=len(files),
        original271_run_passed=False, actual_Pi_WM_updates=0)))
