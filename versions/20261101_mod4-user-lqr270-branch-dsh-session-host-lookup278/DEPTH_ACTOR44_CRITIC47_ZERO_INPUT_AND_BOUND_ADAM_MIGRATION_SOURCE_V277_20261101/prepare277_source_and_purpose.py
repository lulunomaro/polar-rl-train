"""Pure source metadata preparation/freeze, no tensor or model imports."""
from pathlib import Path
import argparse
import hashlib
import json
import time

N = Path(__file__).resolve().parent
T = N.parent
R = N / 'reports'


def row(path):
    b = path.read_bytes()
    return dict(path=str(path), bytes=len(b), SHA=hashlib.sha256(b).hexdigest())


def write(path, value):
    with path.open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, allow_nan=False)


p = argparse.ArgumentParser()
p.add_argument('--freeze', action='store_true')
args = p.parse_args()
if not args.freeze:
    refs = [T / 'OWN_DEPTH_WM_ONLY_ONLINE_WARM_V276_20261101/normal276/review276_NEW_WM_formal_initial_whole_CPU_UNUSED_once.py',
        T / 'OWN_DEPTH_WM_ONLY_ONLINE_WARM_V276V3_20261101/source/worker276_online_WM_only.py',
        T / 'OWN_DEPTH_WM_ONLY_WARM_PROTOCOL_SOURCE_V275_20261101/wm_only_task275.py',
        T / 'OWN_DEPTH_WM_ONLY_WARM_PROTOCOL_SOURCE_V275_20261101/INDEX275_WM_ONLY_WARM_PROTOCOL_SOURCE_FROZEN.json']
    write(N / 'SOURCE277_SCHEMA_REFERENCES_AND_PENDING_IDENTITIES.json', dict(epoch=time.time(),
        kind='SOURCE_ONLY_WEIGHT_SCHEMA_NO_ACTUAL_PARAMETER_ID_MAPPING', references=[row(f) for f in refs],
        known='actor9/critic8 mlp0/2/4/6, STD6,35/38 prefixes, original ELU',
        actual_source_optimizer_IDs='UNKNOWN_PENDING_ROOT_ACTUAL_IDENTITY_WITNESS',
        actual_target_optimizer_IDs='UNKNOWN_PENDING_ROOT_ACTUAL_IDENTITY_WITNESS',
        source_discovery_error_preserved=dict(kind='source_path_not_found',
            path='MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/run240_model2050_literal40050_worker.py',
            scope='Read-only source lookup only; no fixture/model/actual case executed; actual276 CPU-reader schema used'),
        running276V3_not_touched=True, source17_states_triplicated=False,
        WM_optimizer='not an input; inherited separately after actual qualified warm close/admission',
        actual_migration_Pi_gradient_Task_GO='PENDING', real_model_raw_asset_SDK_GPU_network_Git_reads=0))
    files = sorted(f for f in N.rglob('*') if f.is_file())
    write(R / 'FROZEN277_NEW_ZERO_INPUT_BOUND_ADAM_SYNTHETIC_CPU_PURPOSE.json', dict(epoch=time.time(),
        purpose_ID='NEW277_ZERO9_ACTOR44_CRITIC47_BOUND_ID_ADAM_SPLIT_SYNTHETIC_TENSOR_CPU_ONCE',
        source_files=[row(f) for f in files], exact_counts=dict(runs=1, groups=4, refusals=12,
            synthetic_observation_rows=17, source_parameter_slots=17, Pi_output_slots=9, critic_output_slots=8,
            optimizer_instances=0, optimizer_steps=0, actual_models_raw_assets_SDK_GPU_remote_Git_GO=0,
            old_fixture_replays=0), actual_migration_or_Pi_admission=False))
    print(json.dumps(dict(purpose_frozen=True, source_files=len(files), references=len(refs))))
else:
    report = json.loads((R / 'ACTUAL277_NEW_ZERO_INPUT_BOUND_ADAM_CPU_RETURNED.json').read_bytes())
    assert report['passed'], 'Preserve original false; no ready index'
    files = sorted(f for f in N.rglob('*') if f.is_file())
    index = N / 'INDEX277_ZERO_INPUT_BOUND_ADAM_MIGRATION_SOURCE_FROZEN.json'
    write(index, dict(epoch=time.time(), kind='FROZEN_SOURCE_SYNTHETIC_CPU_ONLY_ACTOR44_CRITIC47_BOUND_ADAM_V277',
        source_ready=True, synthetic_CPU_passed=True, groups=4, refusals=12,
        actual_model_raw_assets_SDK_GPU_network_Git_GO=0, actual_optimizer_instances_or_steps=0,
        actual_migration=False, actual_Pi_gradient_admission=False, complete_three_optimizer_conversion=False,
        current276V3_touched=False, actual_source_target_IDs='PENDING_ROOT_IDENTITY_WITNESSES',
        files=[row(f) for f in files], Git_status='PENDING_ROOT_ORDINARY_APPEND'))
    print(json.dumps(dict(passed=True, index=row(index), files=len(files), actual_migration=False)))
