"""Source-only final V3 parent ABI handoff; never execute worker or tests."""
from pathlib import Path
import hashlib,json,time

HERE=Path(__file__).resolve().parent; P=HERE.parent; T=P.parent
OV=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'


def row(path):
    raw=path.read_bytes();return dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())


def main():
    worker=row(HERE/'worker_full208_v3.py')
    oldproof=OV/'W35_fixed92_NEW_FINAL_whole_CPU_reviewer_v1/W35_FIXED92_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V2.json'
    proof=row(oldproof)  # small saved CPU report only, never selected PT
    shared=['course_math208.py','field208.py','launcher208.py']
    metadata=dict(schema='mod4.208.full_PPO_production_source_parent_ABI.v3',epoch=time.time(),
        status='SOURCE_FROZEN_ROOT_TASKGO_JOIN_PENDING_NO_CHILD_REMOTE_EXECUTION',
        worker=worker,CLI='--mode train --num-envs 20000 --run-id RUN --out JOB/production',
        root_private_shared_solewriter_and_budget_unchanged=True,
        node_source_reference=str(T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/control/mixed210_fullstate_slot_node.py'),
        necessary_root_protocol_change='W35 role must use its own explicit new RM70 kind/field receipts; never call it literal_original_fudan_JUMP or satisfy old JUMP19-text readiness by false flags',
        task_file='TASK.json',go_file='GO_PRODUCTION.json',
        task_minimum=dict(kind='MOD4_W35_FULL_RM70_208_V3',run_id='actual same original-owner run',
            role_key='actual W35 original-owner role key',num_envs=20000,
            source_SHA='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f',
            source_bytes=17619013,source_iteration=32336,source_Adam_step=648360,
            source_LR=.00011390625000000003,
            original_canonical_generation='MOD4_SINGLE_WRITER72_20261026',
            worker_SHA=worker['SHA'],GPU_UUID='root planned c27 actual selected UUID',
            actual_private_EX_held_by_parent='actual original node lock true',
            actual_scene0PT211_passed='actual211 receipt true',actual_robot0PT212_passed='actual212 receipt true',
            original_saved_W35_fullstate_CPU_proof_reused=True,
            new_RM70_geometry_course_and_xyzw_source_reviewed=True,
            source_read_purpose=dict(physical_byte_opens=1,decodes=1,source_bytes=17619013)),
        go_required=dict(run_id='same original owner run',role_key='same original W35 role key',
            source_model_SHA='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f',
            source_iteration=32336,input_Adam=648360,one_original_writer=True,num_envs=20000,
            actor_obs=35,critic_obs=38,action_dim=6,physics_dt=.0025,TGS=[32,4],policy_hz=50,feedback_hz=100,
            max_parent_seconds=3900,save_deadline='learning_started_epoch+3600',nominal_end_epoch='learning_started_epoch+3900'),
        source_model_installed_relative='source/W35_ADAPTED92_FINAL78.pt',
        original_run_manifest_installed='original_run_manifest.json',
        original_manifest_SHA='0543b0c47c53e15da0d7d017693d2b69f7f6354ef088c3a1b8ed2b9cc56e2beb',
        field_install_and_receipt='Original two CAD files under original_field;RM70_BINARY_INSTALL_ACTUAL.json real postcopy SHA/bytes receipt',
        base_install_manifest=str(P/'reports/INSTALL208_SOURCE_INPUTS.json'),
        source_install_rule='All selected runtime .py from adapter_v3 plus shared original source files installed to runtime/isaac/mod4;derivation/seal utilities are archive-only',
        shared_frozen_sources=[row(P/'source'/name) for name in shared],
        preserved_v1_v2_before_use_errors=['wrong assumed WXYZ codec (fixed V3 actualxyzw)',
            'empty computeUUID gate (removed;freshlight+privateEX only)',
            'duplicate selectedPT hash/decode (explicit source cache V3)',
            'old--jobroot/adaptation ABI withoutFIRST (replaced original parent production CLI/schema)'],
        source_cache_scope=dict(exact_path_only=True,physical_reads=1,CPU_decodes=1,
            shared_clone_cache_for_original_DR_and_actor_load=True,
            runner_torch_load_route='temporary exact selected-path only during runner.load',
            global_Path_open_or_builtin_open_modification=False,
            cached_H_explicit_for_selected_source=True,
            old_source_weights_and_labels_unchanged=True,
            own_new_artifact_reads='Original sensor saver plus existing D2-D7 save/roundtrip wrappers and final fullsave validation;explicit cached_load tracks own loads; no caching/redirection of other paths'),
        startup_resource='fresh actual selected4090 free>15669MiB/util<=30/RAM>32GiB/disk>25GiB+original parent privateEX; nonempty computeUUID allowed',
        old_fullstate_CPU_proof=dict(**proof,scope='saved whole CPU report only;root already checked pass/fullmodel finite/35/38/6/17Adam648360/32336/LR/D1-D7factor+RNG structure;no PT reopen'),
        actual0PT_reports=[str(T/'W35_RM70_ORIGINAL_CAD_SCENE_ADMISSION_V211_20261101/reports/ROOT211_ORIGINAL_CAD_SCENE_ZERO_PT_RETURNED_ACTUAL.json'),
            str(T/'W35_RM70_OWN_MOD4_ROBOT_ADMISSION_V212_20261101/reports/ROOT212_ORIGINAL_RM70_OWN_ROBOT80_ZERO_PT_RETURNED_ACTUAL.json')],
        actual212_scope='80freshenv8controls/64physics/16feedback/64legs+wheels queue/.02Reward calls;no model/NN/optimizer;rootZ transient not skill',
        required_production_receipts=dict(FIRST_ACTUAL_NEW_PPO_UPDATE=dict(passed=True,
            actual_new_PPO_updates=1,new_environment_transitions=480000,source_SHA='ad504fec...df3f',
            initial_Adam_step=648360,new_Adam_step=648380,
            first_complete='actual path/bytes/SHA/saved_iteration32337/Adam_min=max648380'),
            FINAL='passed/actual_new_PPO_updates>0/final same full schema',
            latest_complete='actual saved complete metadata',LATEST_PROGRESS='actual update and480000*updates transitions',
            STOP_AFTER_SAVE='complete fullstate save after actual update boundary then return',
            original_SDK_close_and_worker_wait='root original node must wait/close/release/terminal account'),
        mandatory_saved_new_fields=['typed_W35_RM70_task','actual_new_PPO_updates',
            'iter=32336+actual_new_PPO_updates','original17Adam+STD+LR+allD0-D7fullstate',
            'explicitly_NEW_RM70_course/assignment/query/reset andxyzw'],
        actual_native24_before_PPO='full20k actor/critic/STD/optimizer and D0-D7 restored;24controls192physics48feedback;no optimizer until confirmed',
        no_old_G3_assignment_copied_into_new_terrain=True,
        remaining='root TaskGo+source metadata JOIN,one source stream-copy if needed,original unified cohort scheduling and actual worker run;no new WM/skill conversion dependency',
        child_new_local_tests=0,child_model_NPZ_USD_raw_SDK_GPU_SSH_calls=0,
        Git_status='ALL_REPORTS_AND_OLD_ERRORS_PENDING_ROOT_UNIQUE208_ARCHIVE',
        reader_note='One additional nonexistent sensor_checkpoint.py lookup returned ENOENT;actual base sensor saver is sensor_a0_runtime.py;no robot failure/no execution')
    with (HERE/'FULL_PRODUCTION208_V3_HANDOFF.json').open('x',encoding='utf8') as f:json.dump(metadata,f,indent=2)
    files=[row(path) for path in sorted(HERE.iterdir()) if path.is_file()]
    index=HERE/'INDEX208_FULL_PRODUCTION_V3.json'
    with index.open('x',encoding='utf8') as f:json.dump(dict(schema='mod4.208.full_production_index.v3',epoch=time.time(),
        files=files,shared_frozen_sources=metadata['shared_frozen_sources'],
        before_use_V1_V2_errors_retained=True,local_execution_and_tests=False,
        old_cpu_once_not_rerun=True,selected_worker=worker,
        original_frozen_index=str(P/'INDEX208_FROZEN.json'),
        Git_pending_root=True),f,indent=2)
    print(json.dumps(dict(index=row(index),worker=worker,fullstate_CPU_report=proof)))


if __name__=='__main__':main()
