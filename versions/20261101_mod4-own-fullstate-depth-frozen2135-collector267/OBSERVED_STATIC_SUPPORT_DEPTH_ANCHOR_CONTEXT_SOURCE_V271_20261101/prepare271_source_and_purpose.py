"""Pure source metadata prepare/freeze; no Torch, SDK or artifact load."""
from pathlib import Path
import argparse
import hashlib
import json
import time

N = Path(__file__).resolve().parent
T = N.parent
R = N / 'reports'
S255 = T / 'D435I_SUPERMIMIC_NATIVE_WM50_CONTEXT40_SOURCE_V255_20261101'
native = T / 'MOD4_H1_MATLAB_REFERENCE_IMAGINATION_TRACKING_RESOURCE_V165_20261030/payloads_v2/seed27/source'


def row(p):
    b = p.read_bytes()
    return dict(path=str(p), bytes=len(b), SHA=hashlib.sha256(b).hexdigest())


def write(path, value):
    with path.open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, allow_nan=False)


p = argparse.ArgumentParser()
p.add_argument('--freeze', action='store_true')
args = p.parse_args()
if not args.freeze:
    refs = [S255 / 'native_depth_world_model50_v255.py',
        native / 'supermimic_wheel_leg_v3/geometry.py',
        native / 'compact_episode_static31_v1.py',
        T / 'DEPTH_HORIZONTAL_SUPPORT_PIXEL_CENTER_V263_20261101/depth_stair263.py',
        T / 'OWN_MOD4_FULLSTATE_DEPTH_COLLECTOR_V267_20261101/source/evaluate267_front_depth_zero_PT_UNUSED_once.py',
        T / 'DEPTH_SUPERMIMIC_MEASURED224_WM50_SOURCE_FROM255_V268_20261101/native_measured_depth_world_model50_v268.py']
    write(N / 'SOURCE271_REFERENCE_AND_PACKET_ABI.json', dict(epoch=time.time(),
        kind='PURE_SOURCE_REFERENCE_NO_TARGET_QUALIFICATION', references=[row(f) for f in refs],
        packet_schema='CurrentDepthPacket271: one current packet only',
        projected_context='RAW static31 + RAW belief9, existing255 normalization once',
        required_new_actual_field='measured current target263.visible_floor_z_m discarded by267 depth_now',
        old267_T_heading_optical_is_not_T_world_heading=True,
        scope='same run/generation/source/sensor/env/episode; new observation required after reset',
        age='actual admission<=.20; H32 static belief<=.64+initial age, not a future camera',
        authoring_errors_preserved=[dict(kind='apply_patch_verification_failed',
            detail='One multi-file patch expected a backslash before a literal plus in HANDOFF; verification rejected all changes',
            correction='Read exact lines and reapplied correct source/HANDOFF patch before purpose freeze; no fixture had run')],
        actual_Pi_runtime_admitted=False, actual_data_model_reads=0,
        actual_root_execution='PENDING new current-packet collector/purpose; no old artifact read'))
    files = sorted(N.glob('*.py')) + list(N.glob('*.md')) + [N / 'SOURCE271_REFERENCE_AND_PACKET_ABI.json']
    write(R / 'FROZEN271_NEW_STATIC_SUPPORT_CONTEXT_SYNTHETIC_CPU_PURPOSE.json', dict(
        epoch=time.time(), purpose_ID='NEW271_CURRENT_OBSERVED_STATIC_SUPPORT_RAW40_FUTURE_SAFE_CONTEXT_CPU_ONCE',
        source_files=[row(f) for f in files], source255_directory=str(S255), native_source_directory=str(native),
        exact_counts=dict(runs=1, synthetic_envs=2, groups=5, rejection_cases=23,
            actual_controls=0, NN_models_constructed=0, optimizer_steps=0,
            real_model_raw_asset_reads=0, SDK_GPU_remote_Git=0, old_fixture_replays=0),
        purpose='current-frame anchor + static belief predicted-pose motion/yaw/autograd/age/raw40/scope refusal',
        no_actual_Pi_WM_skill_qualification=True))
    print(json.dumps(dict(purpose_frozen=True, files=len(files), references=len(refs))))
else:
    result = json.loads((R / 'ACTUAL271_NEW_STATIC_SUPPORT_CONTEXT_CPU_RETURNED.json').read_bytes())
    assert result['passed'], 'Preserve original false; do not freeze a ready index'
    files = sorted(f for f in N.rglob('*') if f.is_file())
    index = N / 'INDEX271_OBSERVED_STATIC_SUPPORT_CONTEXT_SOURCE_FROZEN.json'
    write(index, dict(epoch=time.time(), kind='FROZEN_SOURCE_SYNTHETIC_CPU_ONLY_OBSERVED_STATIC_SUPPORT_CONTEXT_V271',
        source_ready=True, synthetic_CPU_passed=True, groups=5, refusals=23,
        real_model_raw_asset_reads=0, SDK_GPU_SSH_remote_Git=0, actual_Pi_WM_updates=0,
        original255_263_268_and_270_unchanged=True,
        actual_future_safe_Pi_runtime_admitted=False,
        current267_floor_packet_compatible=False,
        PENDING='new current-packet collector retaining visible_floor_z/sensor-time WORLD heading pose; real H32 Pi integration/admission',
        Git_status='PENDING_ROOT_ORDINARY_PHASE_APPEND', files=[row(f) for f in files]))
    print(json.dumps(dict(passed=True, files=len(files), index=row(index), actual_Pi_WM_updates=0)))
