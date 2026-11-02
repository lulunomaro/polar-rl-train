"""Pure SOURCE builders matching unchanged parent generic-stager W35 interface.
No model/PT stat/open/hash/decode, SDK, GPU, C, budget, locks, GO or Ready writer.
create_derivation... writes ONLY the dedicated new posttrain SOURCE index.
Task/GO drafts are returned to OWNER_PLAN, never published by this module.
"""
from pathlib import Path
import ast, hashlib, json

KIND='MOD4V1_W35_RESUME32643_FULLD0D7_RM70_POSTTRAIN20_V4'
INSTALL_KIND='MOD4V1_W35_POSTTRAIN_INSTALL_ACTUAL_V1'
DERIVATION_KIND='MOD4V1_W35_POSTTRAIN_REVIEWABLE_SOURCE_ONLY_V1'
DERIVATION_FILE='MOD4V1_W35_POSTTRAIN_DERIVATION_INDEX.json'
WORKER='worker_mod4v1_w35_posttrain20_v2.py'
PROTOCOL='mod4v1_w35_posttrain_protocol_v2.py'
DESCRIPTOR='W35_POSTTRAIN_SOURCE_DESCRIPTOR_V2.json'
GPU_CERT_FILE='INPUT8D_GPU_FULLRESTORE_ACTUAL.json'
GPU_CERT_SHA='eb7818657e17c5ef649770f608aceb1231042160f30b9b329519151495037f34'
MODEL='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_RESUME89ACA_WAIT_V4_20261102_054158_1793569318385718000/production/model_final_complete.pt'
SHA='8d6a9ab5fae3fd2689c59bcfc1f1e776eb162b8eef671417df0fc88150285c54'
BYTES=17620037;ITER=32643;ADAM=654500;LR=1.0000000000000004e-05
USD='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
CONTRACT='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
CANONICAL='/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'
GENERATION='MOD4_SINGLE_WRITER72_20261026'
SOURCE_METADATA=dict(path=MODEL,SHA=SHA,bytes=BYTES,iteration=ITER,Adam17=ADAM,LR=LR,
    prior_window_PPO_updates=82,prior_cumulative_PPO_updates=162,metadata_only_not_opened=True)


def raw_text(path):
    p=Path(path)
    assert p.suffix in('.py','.json'), 'Builder reads only explicit source/metadata text'
    return p.read_bytes()


def file_sha(path):return hashlib.sha256(raw_text(path)).hexdigest()


def source_row(root,name):
    raw=raw_text(Path(root)/name)
    return dict(relative=name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())


def create_derivation_from_installed_source(dst):
    """Seal only NEW worker/protocol outputs, never old MOD4V1_DERIVATION_INDEX.

    This is source evidence, NOT actual new live model/SDK/budget admission.
    Called by unchanged stage_generic_nonpt_roles_v2.py BEFORE its install manifest.
    """
    dst=Path(dst)
    outputs=[source_row(dst,name) for name in(WORKER,PROTOCOL)]
    for row in outputs:ast.parse(raw_text(dst/row['relative']).decode('utf-8-sig'))
    certificate=raw_text(dst/GPU_CERT_FILE)
    assert hashlib.sha256(certificate).hexdigest()==GPU_CERT_SHA
    proof=json.loads(certificate)
    assert proof['source_SHA']==SHA and proof['iteration']==ITER and proof['Adam17']==ADAM and proof['actual_LR']==LR
    assert proof['source_cache']['source_bytes']==BYTES
    index=dict(kind=DERIVATION_KIND,source_version=2,status='SOURCE_ONLY_NOT_ACTUAL_TRAINING_ADMISSION',
        source_model_metadata=SOURCE_METADATA,source_GPU_fullrestore_proof_SHA=GPU_CERT_SHA,
        outputs=outputs,inputs=[source_row(dst,GPU_CERT_FILE)],
        original_integration_index='MOD4V1_DERIVATION_INDEX.json remains original immutable integration evidence; not rewritten',
        current_source_identity_is_new8d_not_old89aca=True,source_prior_window_PPO_updates=82,source_prior_cumulative_PPO_updates=162,
        seed=20260928,steps_per_env=24,num_envs=20000,max_additional_updates=20,
        original_rsl_saved_iteration='Read unchanged original runner/save value; completed PPO updates counted independently',
        source_read_purpose='Parent runtime string NEW_W35_FULL20K_POSTTRAIN20_<run_id>',
        source_read_plan=dict(physical_byte_opens=1,decodes=1,source_bytes=BYTES),
        original_owner_budget_lock_lifecycle_modified=False,
        source_only_not_created=['TASK.json','GO_PRODUCTION.json','ROOT_ADMISSION_ACTUAL.json','Ready/live restore receipt','canonical copy'])
    with (dst/DERIVATION_FILE).open('x',encoding='utf-8')as f:json.dump(index,f,indent=2,ensure_ascii=False)
    return index


def build_source_templates(*,job_root,run_id,role_key,manifest_SHA):
    """Return (task_template,go_template) for OWNER_PLAN only.

    Draft owner PID=0, epoch=0, root admission SHA=0, no inherited fds or valid
    Ready hash. Parent task_and_go supplies actual PID/fd/canonical/admit/time/
    UUID/stop/Ready. This function never touches C or emits live JSON filenames.
    """
    job=Path(job_root)
    task=dict(kind=KIND,role='W35',run_id=run_id,role_key=role_key,num_envs=20000,seed=20260928,steps_per_env=24,
        source_SHA=SHA,source_bytes=BYTES,source_iteration=ITER,source_Adam_step=ADAM,source_LR=LR,
        source_prior_new_PPO_updates=162,source_prior_window_PPO_updates=82,source_prior_cumulative_PPO_updates=162,
        model_path=MODEL,source_GPU_fullrestore_proof_SHA=GPU_CERT_SHA,
        asset_USD_SHA=USD,asset_contract_SHA=CONTRACT,asset_dir=str(job/'runtime/assets'),
        closure_episode_m=.01,mimic_rad=.01,original_canonical_generation=GENERATION,canonical_path=CANONICAL,
        source_read_purpose='NEW_W35_FULL20K_POSTTRAIN20_'+run_id,
        source_read_plan=dict(physical_byte_opens=1,decodes=1,source_bytes=BYTES),
        worker_SHA=file_sha(job/WORKER),manifest_file='INSTALL_MOD4V1_POSTTRAIN_ACTUAL.json',manifest_SHA=manifest_SHA,
        ready_file='READY_W35_POSTTRAIN_ACTUAL.json',root_admission_file=str(job/'ROOT_ADMISSION_ACTUAL.json'),root_admission_SHA='0'*64,
        derivation_index_SHA=file_sha(job/DERIVATION_FILE),owner_parent_pid=0,inherited_lock_fds=[],GPU_UUID='DRAFT_NO_GPU',
        max_parent_seconds=3900,save_after_seconds=3600,exit_headroom_seconds=300,max_additional_updates=20,
        stop_file=str(job/'STOP_AFTER_SAVE.json'),go_file=str(job/'GO_PRODUCTION.json'))
    go=dict(run_id=run_id,role_key=role_key,role='W35',GPU_UUID='DRAFT_NO_GPU',one_original_writer=True,
        source_model_SHA=SHA,source_iteration=ITER,input_Adam=ADAM,source_LR=LR,source_qualification_kind=KIND,
        num_envs=20000,seed=20260928,steps_per_env=24,actor_obs=35,critic_obs=38,action_dim=6,
        physics_dt=.0025,TGS=[32,4],policy_hz=50,feedback_hz=100,asset_USD_SHA=USD,asset_contract_SHA=CONTRACT,
        manifest_SHA=manifest_SHA,root_admission_SHA='0'*64,source_CPU_SHA='0'*64,
        learning_started_epoch=0.,max_parent_seconds=3900,save_deadline=3600.,nominal_end_epoch=3900.,
        exit_headroom_seconds=300,max_additional_updates=20,original_owner_pid=0,stop_file=str(job/'STOP_AFTER_SAVE.json'))
    return task,go


PARENT_ENTRY_FIELDS=dict(role='W35',source_family='w35',source_SHA=SHA,source_model_metadata=SOURCE_METADATA,
    max_additional_updates=20,num_envs=20000,max_parent_seconds=3900,save_after_seconds=3600,exit_headroom_seconds=300,
    install_kind=INSTALL_KIND,manifest_file='INSTALL_MOD4V1_POSTTRAIN_ACTUAL.json',
    worker_argv=[WORKER,'--mode','train','--num-envs','20000','--run-id','{RUN}','--out','{JOB}/production'],
    final_file='production/FINAL.json',final_updates_key='actual_new_PPO_updates',stop_relative='STOP_AFTER_SAVE.json',
    source_contract_AST_MOCK_passed=False,source_contract_not_SDK_pass_claim=True,
    actual_evidence_paths_parent_must_supply=['actual_prior_full20k_proof_file','native0pt_evidence_file',
        'target_source_SDK_receipt_file','historical_geometry_evidence_file'],
    required_immutable_files=[dict(relative='original_run_manifest.json',SHA='0543b0c47c53e15da0d7d017693d2b69f7f6354ef088c3a1b8ed2b9cc56e2beb'),
        dict(relative='MOD4V1_DERIVATION_INDEX.json'),dict(relative='MOD4V1_ASSET_DIFF.json'),
        dict(relative='RM70_BINARY_INSTALL_ACTUAL.json'),dict(relative=GPU_CERT_FILE,SHA=GPU_CERT_SHA)])
