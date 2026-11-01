"""Prepare/freeze metadata only. No Task/GO/control execution or tensor import."""
from pathlib import Path
import argparse
import hashlib
import json
import time

N = Path(__file__).resolve().parent
T = N.parent
R = N / 'reports'
C = T / 'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/control240'
W = T / 'DEPTH_WM224_FUTURE_SAFE_H32_WARM_SOURCE_V273V2_20261101'
P = T / 'FUDAN_TERRAIN80_CURRENT_DEPTH_PACKET_V272_20261101/source'


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
    refs = [C / 'model2050_task240.py', C / 'model2050_240_finite_owner_authority72.py',
        C / 'model2050_240_fullstate_slot_node.py', C / 'three_slot_common_v1.py',
        C / 'forwarded_original_owner_control_v1.py', W / 'future_safe_wm_warm273.py',
        W / 'INDEX273V2_FUTURE_SAFE_WM224_H32_WARM_SOURCE_FROZEN.json', P / 'terrain_only272.py']
    write(N / 'SOURCE275_PINNED_TEMPLATES_AND_SCOPE.json', dict(epoch=time.time(),
        kind='SOURCE_ONLY_TYPED_METADATA_NO_OWNER_OR_GO', references=[row(f) for f in refs],
        transport='existing jump_72 label/whitelist/HMAC unchanged',
        learning_scope='one_new_WM_Adam_only, frozen teacher2135/42940',
        source_CPU_SHA_scope='SHA(json.dumps(entire closed_source_CPU.value,indent=2)); not teacher CPU report SHA',
        resource_admission_scope='Ready: fresh ROOT released resource/private/shared probe receipt SHA; FIRST: separate actual node-held resource JSON SHA; neither is workerSHA',
        actual274V3_pass='ROOT reported actual CUDA no-step H32/B1024/512cube; no artifact/model read by child',
        controls='ROOT276 integrates separately; original accounting/HMAC/twofcntl/rawfee functions unchanged'))
    files = sorted(f for f in N.rglob('*') if f.is_file())
    write(R / 'FROZEN275_NEW_WM_ONLY_METADATA_INTERFACE_CPU_PURPOSE.json', dict(epoch=time.time(),
        purpose_ID='NEW275_WM_ONLY_FROZEN_TEACHER_TASK_READY_VALUE_GO_FIRST_FINAL_JSON_AST_CPU_ONCE',
        source_files=[row(f) for f in files], selected273V2_INDEX_SHA='05925ecccf95c58b0e1203207e4b1e5d6ec81c5a9eb16f2c67bae4dbcbcde3cf',
        actual240_owner_source=str(C / 'model2050_240_finite_owner_authority72.py'),
        actual240_common_source=str(C / 'three_slot_common_v1.py'),
        exact_counts=dict(runs=1, groups=4, refusal_cases=12, model_raw_assets_Torch_SDK_GPU_SSH_GO_account_Git=0,
            actual_Pi_WM_updates=0, old_fixture_runs=0), actual_Task_Ready_GO_admitted=False))
    print(json.dumps(dict(purpose_frozen=True, files=len(files), references=len(refs))))
else:
    result = json.loads((R / 'ACTUAL275_NEW_WM_ONLY_METADATA_INTERFACE_CPU_RETURNED.json').read_bytes())
    assert result['passed'], 'Keep original false; no ready index'
    files = sorted(f for f in N.rglob('*') if f.is_file())
    index = N / 'INDEX275_WM_ONLY_WARM_PROTOCOL_SOURCE_FROZEN.json'
    write(index, dict(epoch=time.time(), kind='FROZEN_SOURCE_ONLY_WM_ONLY_TEACHER2135_TYPED_PROTOCOL_V275',
        source_ready=True, pure_JSON_AST_CPU_passed=True, groups=4, refusals=12,
        actual_Pi_WM_updates=0, actual_models_raw_assets_Torch_SDK_GPU_SSH_GO_account_Git=0,
        original240_273_source_unchanged=True, transport_role_label='jump_72', learning_scope='one_new_WM_Adam_only',
        actual_Task_Ready_GO_admitted=False, controls_worker_install_and_execution='ROOT276_PENDING',
        files=[row(f) for f in files], Git_status='PENDING_ROOT_ORDINARY_OR_ACTUAL_PHASE_APPEND'))
    print(json.dumps(dict(passed=True, index=row(index), files=len(files), actual_Pi_WM_updates=0)))
