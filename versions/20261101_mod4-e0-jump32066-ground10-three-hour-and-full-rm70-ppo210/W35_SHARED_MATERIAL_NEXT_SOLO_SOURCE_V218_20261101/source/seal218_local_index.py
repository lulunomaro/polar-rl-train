"""Seal final LOCAL218 source/report index; no test/SDK/model/remote/Git call."""
from pathlib import Path
import hashlib
import json
import time

B = Path(__file__).resolve().parent.parent
T = B.parent


def ref(path):
    path = Path(path)
    assert path.suffix in ('.py', '.json', '.md', '.txt')
    raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest())


def put(name, value):
    with (B / 'reports' / name).open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, allow_nan=False)


def main():
    cpu = json.loads((B / 'reports/CPU218_ACTUAL.json').read_bytes())
    assert cpu['passed'] and cpu['group_count'] == 3 and cpu['rejected_cases'] == 17
    put('CONTROL218_ORIGINAL_TEMPLATE_INSERTIONS.json', dict(
        status='UNEXECUTED_ROOT_DERIVATION_INTERFACE_NOT_A_SECOND_OWNER',
        original_solo_owner=ref(T / 'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/control/mixed210_finite_owner_authority72.py'),
        original_common=ref(T / 'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/control/three_slot_common_v1.py'),
        original_W35_capable_node=ref(T / 'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/control_v2/parallel210_fullstate_slot_node.py'),
        new_protocol=ref(B / 'source/solo218_protocol.py'),
        insertion_points=['solo-owner protocol import and exact single role set w35_72;task label only',
            'common.valid_ready protocol import',
            'W35-capable node Ready filename ADMISSION218_READY.json;spec.worker_script worker_full218.py'],
        never_modify=['original authority/HMAC authentication','original two-fcntl budget writer/charge/reserve',
            'canonical generation/path/total/newgrant/copy/refund','private/shared lock/startup light',
            'STOP_AFTER_SAVE/complete save/App close/child wait/terminal ACK'],
        source_CPU_SHA_scope='Original owner Ready VALUE hash only;historical model CPU SHA separate;no manifest circularity',
        one_hour=dict(roles=['w35_72'], num_envs=20000, max_parent_seconds=3900,
                      save_after_seconds=3600, exit_headroom_seconds=300),
        execute_by_child=False))
    put('READER218_ERRORS_AND_PENDING_RECORDING.json', dict(
        phase='LOCAL218 source-only preparation',
        errors=[dict(id='SOURCE_READER218_CONTINUED_CONTEXT_OUTPUT_CLIP',
            result='Earlier inherited broad source read exceeded available output context;no usable output;followed by narrow source reads',
            no_robot_or_model_execution=True),
          dict(id='SOURCE_READER218_GUESSED_208_DIRECTORY_ENOENT',
            result='Earlier guessed MATERIAL_LIMIT...V208 name was wrong;actual EXPERT_NORMALIZATION_SOURCE_V208 path used;original missing-path result not relabelled',
            no_robot_or_model_execution=True),
          dict(id='SOURCE_READER218_EXEC_JS_DESTRUCTURING_ERROR',
            result='TypeError: .for is not iterable;independent source-reader calls completed but JS output handling failed;corrected reader consumed only source files',
            no_robot_or_model_execution=True),
          dict(id='SOURCE_READER218_BINDING_RG_OUTPUT_CLIPPED',
            result='Combined214 source binding output was truncated at output budget;re-read only usd214 narrow source,not any binary or prior fixture',
            no_robot_or_model_execution=True)],
        preserved_old_failure_paths=[str(T / 'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/reports/ROOT210_W35_72_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json'),
          str(T / 'W35_USER_AUTHORIZED_EXACT_PROCESS_TERMINATION_V216_20261101/reports/ROOT216_ORIGINAL_POST_SIGNAL_EXIT_AND_NODE_RECEIPTS_ACTUAL.json')],
        old_failure_and_saved_model_raw_bytes_unchanged=True,
        active_partial_or_new_produced_PT_in_formal_index=False,
        Git='ALL_NEW218_FILES_PENDING_ROOT_UNIFIED_RECORD_EXPERIMENT_ARCHIVE;child made no Git calls'))
    put('NEXT218_UNEXECUTED_ENTRY_AND_RECEIPT_CONTRACT.json', dict(
        status='SOURCE_CPU_PASS_ACTUAL217_PASS_E0_ACTIVE_NOT_READY_NO_GO',
        entry=ref(B / 'source/worker_full218.py'), delegated214worker=ref(T / 'W35_FULL_RM70_MATERIAL_LIMIT_REPAIR_SOURCE_V214_20261101/source/worker_full214.py'),
        CLI='ACTUAL_SDK_PYTHON -u -B JOB/worker_full218.py --mode train --num-envs 20000 --run-id RUN --out JOB/production',
        install_map=str(B / 'reports/INSTALL218_FROZEN_SOURCE_BINDINGS.json'),
        actual217=str(B / 'reports/ACTUAL217_SELECTED_READBACK_AND_SOURCE_SCOPE.json'),
        first_required=dict(passed=True, actual_new_PPO_updates=1, new_environment_transitions=480000,
            source_SHA='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f',
            initial_Adam_step=648360, new_Adam_step=648380,
            first_complete='actual path/bytes/SHA/saved_iteration32337/17Adam_min=max648380'),
        native_before_PPO=dict(controls=24, physics=192, feedback=48, optimizer_updates=0),
        final_required='passed/actual_new_PPO_updates>0/full complete path bytes SHA iter32336+updates/17Adam648360+20*updates;originalD0-D7+typednewcourse+STD+LR',
        remaining_before_root_GO=['Original210 E0 complete save/App close/allownwaited/node+owner closed/cost settled',
            'Matching NEW E0 formal whole CPU PASS (closure evidence only)',
            'fresh actual canonicalCNone/exact LOCAL CIM/global serial SSH/resource/privateEX admission',
            'stage closed evidence selectors/Task/manifest/Ready in fresh new job,original owner metadata JOIN,sole W35 role schedule'],
        already_qualified_without_replay=['oldW35 full CPU saved proof','208 source geometry/xyzw','211 scene0PT','212 robot80 native8','214 source CPU','217 actual20k material ownrestore/native8'],
        child_model_raw_NPZ_USD_SDK_GPU_SSH_Git_calls=0, completed_RM70_skill=False,
        complete_SuperMimic_conversion=False))
    rows=[]
    for path in sorted(B.rglob('*')):
        if path.is_file():
            assert path.suffix in ('.py','.json','.md','.txt') and not path.name.endswith(('.partial','.active'))
            row=ref(path);row['relative']=str(path.relative_to(B)).replace('\\','/')
            row['synthetic_CPU_fixture_only']='SYNTHETIC_METADATA_ONLY_FIXTURE218' in row['relative']
            rows.append(row)
    index=dict(schema='mod4.218.frozen_local_source_and_metadata_index.v1', frozen_epoch=time.time(),
        status='SOURCE_CPU_PASS_217_ACTUAL_PASS_E0_ACTIVE_NEXT_SOLO_NOT_GO', files=rows,
        file_count=len(rows), new_CPU_purpose=cpu['purpose_id'], new_CPU_groups=3,
        new_CPU_rejections=17, child_model_raw_NPZ_USD_SDK_GPU_SSH_Git_calls=0,
        old_false_source_and_errors_preserved=True, no_active_partial_or_weight_in_this_index=True,
        source_model=dict(SHA='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f',
            bytes=17619013, iteration=32336, Adam17=648360, LR=.00011390625000000003),
        reference_indexes=[dict(path=str(T / 'W35_FULL_RM70_MATERIAL_LIMIT_REPAIR_SOURCE_V214_20261101/INDEX214_FROZEN.json'),
            bytes=15222,SHA='8a27849574f33e5d7e0c619526ddfead25ac57c54bede975315082e2a25ce171'),
          dict(path=str(T / 'W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031/adapter_v3/INDEX208_FULL_PRODUCTION_V3.json'),
            bytes=10479,SHA='5142c78e9955e1c46672c8b6c6f3d06ad9a7c578f0f48e9bcb3c19cc61edce25')],
        index_does_not_claim_Git_synced=True, Git_status='PENDING_ROOT_UNIFIED_ARCHIVE',
        training_or_skill_or_full_SuperMimic_complete=False)
    path=B/'INDEX218_FROZEN.json'
    with path.open('x',encoding='utf8') as f:json.dump(index,f,indent=2,allow_nan=False)
    print(json.dumps(dict(INDEX=ref(path), files=len(rows), source_CPU_passed=True,
                         actual_training_ready=False, child_forbidden_calls=0)))


if __name__=='__main__':
    main()
