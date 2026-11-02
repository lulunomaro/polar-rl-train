"""Pure local JSON/source provenance. No PT/stat/hash, Torch, SSH, GPU, SDK or budget.
Only explicitly listed existing .json/.py/.md text files are opened. No source is
imported/executed. Output is metadata reports ONLY; no new runtime/Ready/GO.
"""
from pathlib import Path
import hashlib,json
C=Path(r'C:\Users\lulu\Desktop\claude\mjcf')
R=C/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021'
N=R/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
T=Path(r'F:\RMPOLAR-RL\mod4v1_experts_fulldr_rm70_20261101');OUT=Path(__file__).resolve().parent
HRT=N/'NORMAL_H1_PPO86B_400N50_NEW86_RUNTIME_SOURCE_V1'
HAD=N/'NORMAL_H1_NEW86_PROJECT_WHOLECPU_NATIVE24_ADMISSION_SOURCE_V2_LIGHT_POLICY'
S=C/'MOD4_E1_SLOPE5_INDEPENDENT_PREPARE_20261011'
D=C/'MOD4_E1_CURB20_DIRECTION_REPAIR_20261011'
A=C/'MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016'
P=C/'MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016'
refs={};read_errors=[]

def text(p,expected=None):
    p=Path(p)
    if p.suffix.lower() not in ('.json','.py','.md') or p.name.upper().startswith('TRAINING_BUDGET'):
        raise ValueError('Metadata-only input guard: '+str(p))
    raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
    row=dict(path=str(p),bytes=len(raw),SHA=sha,kind='existing_text_or_saved_JSON_only')
    if expected is not None:row.update(expected_SHA=expected,expected_SHA_matches=sha==expected)
    refs[str(p)]=row
    if expected is not None and sha!=expected:read_errors.append(dict(path=str(p),kind='TEXT_SHA_MISMATCH',expected=expected,actual=sha))
    return raw.decode('utf-8-sig'),row

def load(p,expected=None):
    value,ref=text(p,expected);return json.loads(value),ref

def put(name,value):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False)

def manifest_text_rows(manifest,base,key='files',selected=None):
    result=[]
    for row in manifest[key]:
        rel=row.get('relative',row.get('path'))
        if selected is not None and rel not in selected:continue
        if Path(rel).suffix.lower() not in ('.py','.json','.md'):continue
        if Path(rel).name.upper().startswith('TRAINING_BUDGET'):continue
        local=Path(row.get('local_path',str(base/rel)))
        try:
            _,verified=text(local,row.get('SHA',row.get('sha256')))
            result.append(dict(relative=rel,source_row=row,current_text_ref=verified))
        except (FileNotFoundError,UnicodeError) as e:
            result.append(dict(relative=rel,source_row=row,current_text_status='UNKNOWN_LOCAL_TEXT_UNAVAILABLE',error=str(e)))
    return result

UN='UNKNOWN_NOT_PROVEN_FROM_SAVED_METADATA'
common=dict(current_task_PT_opens=0,PT_stat_or_rehash=0,Torch_imports=0,SSH_or_SDK_or_GPU_calls=0,canonical_budget_access=0,new_runtime_or_Ready_GO_created=False,skills='Current catalog Office/ACL only; no matching RL skill. Host read/glob/grep/local JSON CLI used.',scope='Saved JSON and code provenance only. Historical actual receipts are references, not new runs.')

# normal-H1 original producer -> typed40050 -> actual target admission.
orig,oref=load(R/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/reports/THREE_GPU86B_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
typed,tref=load(N/'NORMAL_H1_PPO86B_400N50_NEW86_SOURCE_PREPARATION_V1/reports/NORMAL_H1_TYPED40050_ORIGINAL_FULLSTATE_CPU_ACTUAL_V1.json')
hm,hmref=load(HAD/'NORMAL_H1_ADMISSION_COMPLETE_INPUT_MANIFEST_V1.json','97cdcde4a891359a5f1209fdad1614bf87629e0c3d3a40ce9018dc1fe9e2426b')
actual,aref=load(HAD/'reports/NEW86_NORMAL_H1_WHOLECPU_CUDA_NATIVE24_ORIGINAL_RETURNED_ACTUAL.json')
derive,dref=load(HRT/'NORMAL_H1_WORKER_EXACT_SOURCE_DERIVATION_NOT_EXECUTED.json')
_,href=text(HRT/'HANDOFF.md');_,ahref=text(HAD/'HANDOFF.md')
hnames={'h1_step270_sdk_runtime_candidate.py','h1_step270_fullstate_checkpoint_candidate_uninstalled.py','h1_step270_path_reward_v1.py','normal_H1_PPO40050_finite_worker_v1.py','normal_H1_PPO40050_declared_source_guard_v1.py','target_normal_H1_whole_source_SDK_CPU_once_v1.py','target_normal_H1_CUDA_fullrestore_frozen_native24_once_v1.py'}
mods=['train_H1_ground_prelaunch_fullstate_v2.py','h1_takeoff_progress_environment_v2.py','h1_fullstate_checkpoint_v1.py','sensor_resume_contract.py','feedback_delay_checkpoint.py','action_delay_checkpoint.py','spring_pressure_checkpoint.py','gas_damping_checkpoint.py','chassis_pd_checkpoint.py','physics_clock.py','feedback_delay_runtime.py']
hnames.update('job0/runtime/isaac/mod4/'+name for name in mods)
hrows=manifest_text_rows(hm,HAD,selected=hnames)
phases=[]
for p in actual['actual_phase_waits']:
    v=p.get('report_value',{});take=['passed','kind','source_SHA','original_source_SHA','num_envs','controls','physics_callbacks','feedback100Hz_samples','policy_hz','physics_dt_s','public_phase_tick_hz','original270_goal_landing12_recovery200_callbacks_unchanged','source_17Adam_step','LR','mean_policy_only','all_actor_critic_STD_norm_optimizer_literal_unchanged','no_PPO_or_normalization_update','actor35_critic38_STD6_all17Adam832460_LR_preserved','D1_D7_private_state_and_H1_phase_CPU_structure','queue_original_CUDA16byte_RNG_untouched','actual_CUDA_RNG_restore_passed']
    phases.append(dict(phase=p['phase'],actual_waited=p['actual_waited'],returncode=p['returncode'],passed=p['passed'],actual_worker_identity=p.get('actual_worker_identity'),report_path=p['report_path'],saved_report_SHA=p['report_SHA'],saved_value_subset={k:v[k] for k in take if k in v}))
h1=dict(kind='H1_NORMAL_PPO86B_PROVENANCE_JOIN_V1',alias='H1_normal_PPO86B_NOT_native_H1_or_current_student',current_scope=common,
 original_producer=dict(metadata=oref,model=orig['models']['h1']['final'],stored_iteration=typed['source']['original_stored_RSL_iteration'],Adam17=typed['source']['original_Adam_step'],saved_LR=typed['source']['original_optimizer_LR'],raw_STD6_from_saved_proof=orig['models']['h1']['raw_actor_distribution_std_param6'],original_policy_hz=100,original_feedback_hz=100,physics_dt_s=.0025,decimation=4,TGS=[32,4],gas_nominal_k_N_m=3500,gas_force_nominal_N_each=700,clock_evidence=dref,role_separate_from_native=True),
 typed40050=dict(metadata=tref,model=typed['new_source'],four_recipe_fields_only=typed['source']['four_recipe_fields_only'],whole20k_other_state_literal_preserved=typed['all_other_source_fields_literal_preserved'],original_history_and_queues_not_rescaled=True,policy_hz=50,feedback_hz=100,public_phase_tick_hz=100,physics_dt_s=.0025,decimation=8,TGS=[32,4],gas_k_N_m=2000,gas_N_each=400,gas_damping=3,hardware_force_curve_calibrated=False),
 later_actual_target=dict(evidence=aref,passed_actual_wholeCPU_CUDA_fullrestore_native24_only=actual['passed_actual_wholeCPU_CUDA_fullrestore_native24_only'],job_root='/data/robemo/polar-rl-train/validation_runs/NORMAL_H1_PPO86B40050_WHOLECPU_NATIVE24_20261029v2',phases=phases,source_hash_unchanged='71db5543b14919eb11d2a8606f9ffe1acf0814260d7d89aa823565a49a7b21c4',new_PPO_producer=UN,qualification='Legacy400N50 targetCPU+CUDA20k fullrestore/native24 actual; not newMOD4v1 and not skill graduation',source_only_PENDING_handoff_superseded_only_for_this_target_scope=True),
 runtime_join=dict(manifest=hmref,input_rows=len(hm['files']),base451_manifest_SHA=hm['base_frozen_451_manifest_SHA'],worker_derivation=dref,selected_text_rows=hrows,phase_runtime='H1Step270Env/Step270Phase actual source, not generic nativeH1',phase_age_increment_per_policy=2,public_request_seconds=[1.,1.8],landing_physics_callbacks=12,recovery_physics_callbacks=200,source_clock_overlay=hm['source_only_clock_overlay'],all_original20k_states_restored_then_ONE_new_actual_episode=True,historical_helper_policy100_provenance_not_active50Hz_clock=True),
 migration_layers=dict(original_to40050='Saved typedCPU and later actual target20k/native24 proven',old400_asset={'USD_SHA':'bce9a7740fd9a2e2252d34a09c1fef7dab70e2a65f9d0ee2e422cec5f12c60e4','contract_SHA':'517cd6a4cc469455af08da75dc4b7f7cb596b375bafb4c3e566c7df5bc51df49'},new_MOD4v1_2c_bae='PENDING_NOT_PROVEN',new_nominal_D0_or_new_asset_fullrestore='PENDING_NOT_PROVEN'),
 unresolved=["No later actual normal-H1 PPO saved producer was proved in this bounded exact71db local report/source search. Do not infer global latest.","Need explicit current legacy variant selection and new2c/bae source/SDK/independent skill evidence in a separately approved task.","No new qualification inferred from 24 steps; source/native-H1/currentstudent remain distinct."],evidence_hierarchy='Saved actual returned process receipts override earlier source-only PENDING claims for the same legacy target, not for new2c/bae.')
put('H1_NORMAL_PPO86B_SOURCE_JOIN_v1.json',h1)

# independent E1 source packages. NO file access to referenced PT or raw geometry.
train,trainref=load(A/'train_payload/TRAIN_PACKAGE_MANIFEST.json')
task0,task0ref=load(A/'train_payload/job0/TASK.json');task1,task1ref=load(A/'train_payload/job1/TASK.json')
closed,closedref=load(A/'reports/FIRST_CURB_SLOPE_FINAL_MODELS_AND_EXACT_DISTINCT_INTERVAL_COST_CPU_ACTUAL.json')
work,workref=load(A/'reports/NEXT_CURB113_FROZEN_CLOSED_THREE_BLOCKS_FINAL_NEW_STEP_HOP_REVIEW_NO_AUTO_PPO_ACTUAL_WORK_ORDER.json')
core={'expert_independent_worker_v1.py','independent_expert_axis_v1.py'}
base_names=['train_independent_owned_axis_v1.py','independent_expert_axis_v1.py','retention_learning_env.py','curb20_entry_v3_runtime.py','curb20_entry_full_checkpoint.py','slope5_full_checkpoint.py','e1_terrain_checkpoint.py','retention_checkpoint.py','sensor_resume_contract.py','feedback_delay_checkpoint.py','action_delay_checkpoint.py','spring_pressure_checkpoint.py','gas_damping_checkpoint.py','chassis_pd_checkpoint.py','physics_clock.py','mod4_task.py']
core.update('job'+str(job)+'/runtime/isaac/mod4/'+name for job in (0,1) for name in base_names)
core.update('job'+str(job)+'/TASK.json' for job in (0,1))
trainrows=manifest_text_rows(train,A/'train_payload',key='rows',selected=core)
oldclock=dict(policy_hz=100,physics_dt_s=.0025,decimation=4,TGS=[32,4],feedback_hz=100,control_queue_us=10000,clock_status='Original100Hz source/current saved100Hz health, NOT50Hz migration')
oldDR=dict(D0='white_v3 original mass/inertia0.9-1.1, sixmotor0.9-1.1,wheelmu0.7-1',D1='noise_bias_mild_v1 original noise/bias/private streams',feedback='control0/10ms original queues',action='physical_target0/2500/5000us original4leg2wheel streams',D5=dict(nominal_k_N_m=3500,factors=[.9,1.1],gas_nominal_force_N_each=700),D6=dict(nominal_gas_damping=3,factors=[.9,1.1],not_all_joint_friction=True),D7=dict(chassis_COM_xyz_m=[-.005,.005],PD_factor=[.95,1.05]),full20k_history_and_queue_rule='Preserve all original state; no slicing/reconstruction was performed here')
interface=dict(actor_obs=35,critic_obs=38,actions=6,actor_tensors=9,critic_tensors=8,learned_STD6=True,fixed_SI=True)
scoped_migrations=dict(original_to50Hz_400N='UNKNOWN_PENDING_NO_ACTUAL_EVIDENCE_JOINED',new_MOD4v1_2c_bae='PENDING_NOT_PROVEN',two_changes_are_separate_layers=True,no_recipe_or_actor_changed=True)

curb_dec,curbref=load(D/'reports/CURB141_COMPLETE_OBSERVED_SCOPE_DECISION.json')
curb133,c133ref=load(C/'MOD4_E1_CURB20_133_COMPLETE_REVIEW_20261011/reports/CURB133_COMPLETE_SCOPE_DECISION.json')
curb133cpu,c133cpuref=load(C/'MOD4_E1_CURB20_133_COMPLETE_REVIEW_20261011/central_actual/1791664998916919500/E1_CURB20_FORMAL_REVIEWED_OWN_FINAL_CPU_VERIFIED.json')
curb113=next(x for x in closed['closed_models'] if x['kind']=='CURB20')
shared,sharedref=load(P/'final878_actual/source210/rank0/FINAL_SINGLE_PPO.json')
sharedcpu,sharedcpuref=load(P/'reports/FINAL878_THREE_COMPLETE_MODELS_LOCAL_CPU_AND_ACTUAL_CLOSURE_VERIFIED.json')
sharedliteral,literalref=load(P/'reports/FINAL878_LITERAL_TENSOR_BYTES_AND_OPTIMIZER_TREE_THREE_RANK_CPU_SUPPLEMENT.json')
sharedmanifest,spref=load(P/'payload/PAYLOAD_MANIFEST.json')
shared_names={'distributed_rank_worker_v1.py','plant/TASK_ASSIGNMENT.json','plant/runtime/isaac/mod4/train_host72_backend_admission_v1.py','plant/runtime/isaac/mod4/curb20_entry_v3_runtime.py','plant/runtime/isaac/mod4/curb20_entry_full_checkpoint.py','plant/runtime/isaac/mod4/retention_learning_env.py','plant/runtime/isaac/mod4/physics_clock.py'}
sharedrows=manifest_text_rows(sharedmanifest,P/'payload',selected=shared_names)
shared_eval,sevalref=load(A/'reports/CURB878_FULL1500_ORIGINAL_ROUTE_ALL_PREFIX_CPU_ACTUAL.json')
siblings=[]
for rank in (1,2):
    v,vr=load(P/('final878_actual/target72/rank'+str(rank)+'/FINAL_SINGLE_PPO.json'));siblings.append(dict(actual=v['final'],evidence=vr,not_an_independent_expert=True))
param_groups=sharedliteral['rows'][0]['three_parameter_optimizer_trees']['optimizer_state_dict']['param_groups']
curb=dict(kind='E1_CURB20_SEPARATE_FROZEN_VARIANTS_PROVENANCE_V1',alias='E1_CURB20',current_scope=common,interface=interface,original_clock=oldclock,original_DR=oldDR,migration_layers=scoped_migrations,
 variants=[
 dict(alias='CURB133_REVIEW_ONLY_NOT_SELECTED',model=curb133cpu['checkpoint'],selection_evidence=c133ref,selection_level='Explicit frozen review evidence ONLY; regression, not qualified CURB',qualified_selected=curb133['selected_as_qualified_CURB'],frozen=curb133['candidate_frozen_as_review_evidence_only'],producer=dict(pid=curb133cpu['own_PID'],updates=curb133cpu['actual_updates'],metadata=c133cpuref),saved_LR=UN,Adam17_step=UN),
 dict(alias='CURB141_20mm_mirrored_qualified_scope',model=curb_dec['checkpoint'],model_bytes=UN,selection_evidence=curbref,selection_level='Explicit freeze for observed20mm mirrored scope; NOT wholeRM/MoE/permanent-retention graduation',scope=curb_dec['accepted_scope'],frozen=curb_dec['freeze_this_checkpoint_for_accepted_scope_no_more_CURB20_PPO'],saved_LR=UN,Adam17_step=UN,producer_metadata_path=curb_dec['own_fullsave_CPU_PID_unique_closeout'],source_entry='train_curb20_entry_resume_ppo.py plus direction/exposure overlay; full snapshot/source-map is embedded in ownCPU report',full_source_count=424),
 dict(alias='CURB_shared878_protected_reference_one_actor',model=shared['final'],stored_iteration=UN,saved_LR=param_groups[0]['lr'],STD6_tree_evidence=literalref,selection_evidence=workref,selection_level='Explicit protected878 reference, old20mm originalroute27/27; not chosen by maximumupdate',producer_metadata=sharedref,source_manifest=spref,relevant_text_rows=sharedrows,source_ancestor_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',sibling_rank_fullstate_variants=siblings,shared_actor_critic_Adam_allrank_exact=True,independent_actor_count=1,allrank_878_not_three_experts=True,saved_CPU_evidence=sharedcpuref,observed_eval=dict(evidence=sevalref,controls=1500,physics=6000,ascending=27,descending=27,ordinary=0,scope='Original CURB20 mirrored150mm strip; not wholecourse skills')),
 dict(alias='CURB_independent113_frozen_later_branch',model=curb113,stored_iteration=UN,saved_LR=UN,selection_evidence=workref,selection_level='Explicit freeze after26/27 ascent vs protected87827/27; new source NOT presumed better/latest',producer_metadata=closedref,source_ancestor_SHA=task0['source_SHA'],task=task0ref,scope='Reset-bound normal20mm/150mm CURB command-coverage branch, not a higherstep',fullstate_additions=['independent_expert_scope_state','independent_expert_task_contract'],evidence_of_postfreeze_new_CURB20_producer=UN)
 ],
 runtime_packages=dict(shared878=dict(local_root=str(P/'payload'),remote_root='/mnt/mod4_linux_durable_20261013/MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016',manifest=spref,physical_original_entry='train_host72_backend_admission_v1.py -> RetentionLearningEnv/curb20_entry_v3_runtime'),independent113=dict(local_root=str(A/'train_payload'),manifest=trainref,producer_worker='expert_independent_worker_v1.py',task=task0ref,relevant_text_rows=[x for x in trainrows if not x['relative'].startswith('job1/')])),
 complete_state_chain=['RSL actor/critic/STD/17Adam load','curb20_entry_full_checkpoint / E1 terrain and retention command-state restore','original chassis_pd_checkpoint -> gas_damping_checkpoint -> spring_pressure_checkpoint -> action_delay_checkpoint -> feedback_delay_checkpoint -> sensor_resume_contract','ONE original fresh physical episode; then explicit independent-axis binding when applicable'],
 unknowns=['Current human-selected CURB20 migration source among separately frozen variants is UNKNOWN; no maxiter/rank substitution.', 'Exact saved LR/iteration/Adam step omitted by saved metadata remain UNKNOWN where marked; no PT opened to fill them.', '50Hz/400N migration and new2c/bae migration for these variants have not been proved by this join.'])
put('E1_CURB20_SOURCE_JOIN_v1.json',curb)

slopecpu,scref=load(S/'reports/SNAPSHOT_OWN_FORMAL_CPU_1791686991841256500.json')
slope135,s135ref=load(S/'reports/SLOPE135_COMPLETE_SCOPE_DECISION.json')
slope138,s138ref=load(S/'reports/SLOPE138_COMPLETE_SCOPE_DECISION.json')
slopefinal,sfref=load(S/'reports/SNAPSHOT_FORMAL_FINAL_ACTUAL_REVIEW.json')
scopy,scopyref=load(C/'MOD4_HOST72_E1_CURB_SLOPE_TRAINING_ASSIGNMENT_20261016/reports/OWN_TWO_SOURCE_FULL_CPU_TENSOR_OPTIMIZER_FINITE_ACTUAL.json')
slope50=next(x for x in closed['closed_models'] if x['kind']=='SLOPE5')
_,oldentryref=text(S/'snapshot_reviewed_payload/isaac/mod4/train_slope5_snapshot_reviewed_resume_ppo.py',slopecpu['manifest']['source_map']['isaac/mod4/train_slope5_snapshot_reviewed_resume_ppo.py'])
slope=dict(kind='E1_SLOPE5_SEPARATE_FROZEN_VARIANTS_PROVENANCE_V1',alias='E1_SLOPE5',current_scope=common,interface=interface,original_clock=oldclock,original_DR=oldDR,migration_layers=scoped_migrations,
 variants=[
 dict(alias='SLOPE135_24b_original5degree_frozen_scope',model=slope135['selected_checkpoint'],model_bytes=slope138['source_checkpoint']['bytes'],Adam17_step=scopy['rows'][1]['Adam_steps'][0],saved_LR=UN,producer=dict(actual_pid=slopecpu['own_PID_receipt']['pid'],updates=slopefinal['formal_PASSED']['actual_updates'],CPU_snapshot=scref,actual_closeout=sfref),selection_level='Explicit frozen5degree2m mirrored scope27/27 up+down; no wholeSLOPE/MoE graduation',selection_evidence=s135ref,frozen=slope135['freeze_5degree_scope_candidate'],source_ancestor_SHA=slopefinal['formal_PASSED']['source_sha256'],later_same_weight_observed_8_10degree_only=dict(evidence=s138ref,same_checkpoint_SHA=slope138['source_checkpoint']['sha256'],angles=slope138['accepted_observed_frozen_slope_angles_deg'],not_new_8or10degree_PPO=True),runtime=dict(local_root=str(S/'snapshot_reviewed_payload'),entry=oldentryref,rolling_source_count=slopecpu['source_count'],snapshot_count=slopecpu['actual_snapshot_count'],source_map=slopecpu['manifest']['source_map'],fullstate_helper='slope5_full_checkpoint.resume_e1_new_episode/install_e1_save_contract',terrain_identity=slopecpu['manifest']['E1_terrain_identity'])),
 dict(alias='SLOPE_independent50_frozen_later_branch',model=slope50,stored_iteration=UN,saved_LR=UN,selection_evidence=workref,selection_level='Later closed50 update SLOPE5 model explicitly frozen; no automatic substitution for old24b accepted5/8/10degree reference',producer_metadata=closedref,source_ancestor_SHA=task1['source_SHA'],task=task1ref,fullstate_additions=['independent_expert_scope_state','independent_expert_task_contract'],scope='Original full2m5degree ramp and bothflat supports; not8/10degree training',postfreeze_producer=UN)
 ],
 runtime_packages=dict(original24b=dict(local_root=str(S/'snapshot_reviewed_payload'),saved_full_metadata=scref,selected_entry=oldentryref),independent50=dict(local_root=str(A/'train_payload'),manifest=trainref,producer_worker='expert_independent_worker_v1.py',entry='job1/runtime/isaac/mod4/train_independent_owned_axis_v1.py -> RetentionLearningEnv/configure_slope',relevant_text_rows=[x for x in trainrows if not x['relative'].startswith('job0/')])),
 complete_state_chain=['RSL actor/critic/learnedSTD/17Adam original load','slope5_full_checkpoint -> E1 terrain/current-command/retained-flat/privateRNG identity migration','chassisPD/gasDamping/springPressure/actionDelay/feedbackDelay/sensor original chain','ONE new physical episode; independent-axis whole-route scope retained when applicable'],
 unknowns=['Current human-selected SLOPE5 migration variant is UNKNOWN; separately preserve old24b and lateraab50.', 'Saved exact LR/stored iteration of50 are not present in the selected metadata; no arithmetic or PT-read guess.', 'No proof here of later source400N50 or new2c/bae adaptation; remain separate pending layers.', 'Shared878 rank1/2 are CURB onePPO fullstate shards, not SLOPE actors.'])
put('E1_SLOPE5_SOURCE_JOIN_v1.json',slope)

put('TEXT_SOURCE_AND_REPORT_SHA_INDEX_v1.json',dict(kind='LEGACY_JOIN_EXACT_TEXT_INPUT_SHA_INDEX',current_scope=common,input_files=list(refs.values()),current_text_errors=read_errors,no_binary_models_or_banks_opened=True,all_models_SHAs_are_saved_report_claims_not_new_PT_hashes=True))
put('LEGACY_JOIN_SUMMARY_v1.json',dict(kind='LEGACY_FROZEN_LINEAGES_METADATA_JOIN_SUMMARY',reports=['H1_NORMAL_PPO86B_SOURCE_JOIN_v1.json','E1_CURB20_SOURCE_JOIN_v1.json','E1_SLOPE5_SOURCE_JOIN_v1.json','TEXT_SOURCE_AND_REPORT_SHA_INDEX_v1.json','METADATA_READER_ERRORS_v1.json'],current_scope=common,all_historical_experts_resolved_or_adapted=False,normalH1_legacy40050_target_admission_actual=True,new_MOD4v1_for_these_legacy_lineages='PENDING_NOT_PROVEN',frozen_variants_kept_separate=True,no_current_canonical_or_latest_selection_inferred=True,archive='Parent append-only phase archival pending; no child Git commit/push.'))
print(json.dumps(dict(status='LEGACY_SOURCE_METADATA_JOINS_WRITTEN_NOT_ADAPTATION',directory=str(OUT),text_inputs=len(refs),text_SHA_errors=len(read_errors),PT_opens=0,SSH_SDK_GPU_budget=0),indent=2))
