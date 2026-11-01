"""Pure source metadata. No tensor imports, SDK or artifact access."""
from pathlib import Path
import argparse
import hashlib
import json
import time

N = Path(__file__).resolve().parent
T = N.parent
R = N / 'reports'
S255 = T / 'D435I_SUPERMIMIC_NATIVE_WM50_CONTEXT40_SOURCE_V255_20261101'
S268 = T / 'DEPTH_SUPERMIMIC_MEASURED224_WM50_SOURCE_FROM255_V268_20261101'
S271 = T / 'OBSERVED_STATIC_SUPPORT_DEPTH_ANCHOR_CONTEXT_SOURCE_V271V2_20261101'
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
if not args.freeze:
    refs = [S255 / 'native_depth_world_model50_v255.py', S268 / 'native_measured_depth_world_model50_v268.py',
        S268 / 'measured_state224_v268.py', S268 / 'INDEX268_MEASURED224_WM50_SOURCE_FROZEN.json',
        S271 / 'observed_support_context271.py', S271 / 'INDEX271V2_OBSERVED_STATIC_SUPPORT_CONTEXT_SOURCE_FROZEN.json',
        native / 'supermimic_wheel_leg_v3/augmented_wheel_leg_world_model_v1.py',
        native / 'supermimic_wheel_leg_v3/geometry.py', native / 'supermimic_wheel_leg_v3/replay.py',
        native / 'supermimic_wheel_leg_v3/networks.py', native / 'supermimic_wheel_leg_v3/contract.py',
        native / 'flat91_mask_aware_goal_conditioning_v1.py', native / 'matlab144_goal_conditioning_v1.py',
        native / 'compact_episode_static31_v1.py']
    write(N / 'SOURCE273_PINNED_BINDINGS_AND_ABI.json', dict(epoch=time.time(),
        kind='SOURCE_ONLY_WM_WARM_FIRST_CURRENT_ANCHOR_NOT_Pi_RUNTIME', references=[row(p) for p in refs],
        imports=[str(S268), str(S271), str(S255), str(native)],
        packet='exact CurrentDepthPacket271; False floor NaN; actual run/env/time scope preserved',
        no_future_depth='per-step context from first admitted WORLD corners + predicted native state only',
        actor_critic_STD_17Adam='external frozen qualified fullstate contract, no optimizer references here',
        WM_optimizer_count=1, complete_three_optimizer_conversion=False,
        actual272_packet_admitted_by_this_child=False, real_model_data_SDK_GPU_remote_reads=0))
    files = sorted(f for f in N.rglob('*') if f.is_file())
    write(R / 'FROZEN273V2_NEW_FIRST_ANCHOR_H32_SYNTHETIC_CPU_PURPOSE.json', dict(epoch=time.time(),
        purpose_ID='NEW273V2_SYNTAX_REPAIRED_SUPPORTED_START_TRUE_SCOPE_NO_FUTURE_DEPTH_H32_NATIVE_WM_CPU_ONCE',
        source_files=[row(f) for f in files],
        import_directories=[str(S268), str(S271), str(S255), str(native)], native_source_directory=str(native),
        exact_counts=dict(runs=1, synthetic_envs=3, rows=33, pairs=99, groups=4, refusals=4,
            synthetic_WM_optimizer_updates=1, actual_Pi_WM_updates=0, real_model_raw_asset_reads=0,
            SDK_GPU_remote_Git_GO=0, old268_271_fixtures=0),
        new_scope='supported-start packet replay + vectorized true repeated scope + first-anchor-only H32 forward/loss',
        previous_fixture_replays=False))
    print(json.dumps(dict(purpose_frozen=True, files=len(files), references=len(refs))))
else:
    report = json.loads((R / 'ACTUAL273V2_NEW_FIRST_ANCHOR_H32_CPU_RETURNED.json').read_bytes())
    assert report['passed'], 'Preserve false; source cannot be frozen READY'
    V1 = T / 'DEPTH_WM224_FUTURE_SAFE_H32_WARM_SOURCE_V273_20261101'
    files = sorted(f for f in V1.rglob('*') if f.is_file()) + sorted(f for f in N.rglob('*') if f.is_file())
    index = N / 'INDEX273V2_FUTURE_SAFE_WM224_H32_WARM_SOURCE_FROZEN.json'
    write(index, dict(epoch=time.time(), kind='FROZEN_SOURCE_SYNTHETIC_CPU_ONLY_WM224_FIRST_ANCHOR_H32_V273',
        source_ready=True, synthetic_CPU_passed=True, groups=4, refusals=4, synthetic_pairs=99,
        synthetic_WM_updates=1, actual_Pi_WM_updates=0, actual_models_raw_assets_SDK_GPU_SSH_remote_Git_GO=0,
        original268_271_unchanged=True, original_fixtures_replayed=0,
        actual_current_packet_runtime_and_Pi_admission='PENDING_ROOT', complete_three_optimizer_conversion=False,
        future_depth_in_H32_forward=False, actor_critic_STD_full17Adam='frozen external teacher contract only',
        files=[row(f) for f in files], Git_status='PENDING_ROOT_ORDINARY_OR_ACTUAL_WM_PHASE_APPEND'))
    print(json.dumps(dict(passed=True, index=row(index), files=len(files), actual_Pi_WM_updates=0)))
