from pathlib import Path
import json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';W35=T/'W35_RM70_QUALIFIED_CONTINUATION_AND_LOSSLESS_EVAL_SOURCE_V227_20261101';D=W35/'D_BEFORE_USE_CWD_REPAIR_SOURCE';DR=D/'reports'
def read(p):return json.loads(p.read_bytes())
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
closing=read(DR/'ROOT227D_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json');cpu=read(DR/'ROOT227D_NEW_W35_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json');role=cpu['roles']['w35_72']
assert closing['passed_collection']and closing['owner_closed']['canonical_None']and cpu['passed']and role['save_at_or_after_requested_deadline']and not cpu['CUDA_initialized']
fee=closing['owner_closed']['original_one_owner_segment']['charged_expert_seconds'];assert fee==3645.0908699035645
case=read(R/'CURRENT_ACTUAL232_E2_READER_AND_WORLD_SKILL_WORK_ORDER.json');facts=read(R/'ROOT233_ACTUAL_ORIGINAL_FAILURE_COMPONENTS_SINGLE_PASS_RETURNED.json');assert facts['passed']and facts['derived_F32_bounds_vs_original_flag_disagreements']==0
clarification=dict(epoch=time.time(),kind='ACTUAL232_PHYSICS_COMPLETE_PARENT_POST_APP_COUNTER_FALSE_PRESERVED',original_parent_passed_execution=False,original_parent_error=case['original_parent']['error'],actual_bounded_worker_completed_1200controls_24s=True,worker_original_wait0=case['original_parent']['original_wait'],all_own_waitout_private_shared_released=True,
 original_post_Appclose_SOURCE213_SELECTED_PT_READ_COUNTS_artifact='ABSENT',final_physical_source_read_counter='UNKNOWN;guarded cache/admitted maximum1,do not fabricate a returned producer count',
 cause_scope='APP_CLOSING and complete boundedcase/unchanged state reports exist;workerRC0. SDK fast shutdown is a plausible explanation for a missing post-close file,notproved. Originalparentfalse andtraceback retained,notrerun for counters.',
 CPU_metadata_V3_passed=True,native24_and_full_core68_fingerprint_restore_passed=True,source_input_Adam859300_LR_unchanged=True,no_new_optimizer_or_training=True,
 physical_E2_skill='FAILED_ORIGINAL_CONDITIONS_IN_MANY_COMPLETE_SPANS;notgraduated',raw_read233='Separatefrozennecessarypurpose actualoneopen/hash/parse+integrity,0model/GPU/download;CONSUMED')
put(R/'ROOT232_PHYSICAL_COMPLETION_AND_PARENT_COUNTER_FALSE_SCOPE_CLARIFICATION.json',clarification)
summary=dict(epoch=time.time(),kind='CLOSED227D_QUALIFIED_AND_ACTUAL232233_E2_WORLD_DIAGNOSTIC_COMPLETE_NOT_GRADUATED',
 W35_closed=dict(run_id=closing['run_id'],passed_original_normal=True,passed_NEW_formal_initial_CPU=True,qualified_formal=role,new_environment_transitions=role['new_PPO_updates']*20000*24,new_PPO_updates=77,saved_iteration=32481,Adam17=651260,allfinite_tensors=181,source_parent_SHA='343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd',
  original_raw_fee_SUMONCE=fee,closing_balance_snapshot_NOT_LIVE=409122.9400341511,original_cap3900_save3600_exit300=True,actual_hour_deadline_met=True,normal_and_CPU_and_one_formal_transfer_and_hashes='RETURNED0_CONSUMED do notrerun',owner_node_worker_waitout_private_sharedfree_freshCNone=True,all_original_FUDAN_or_LQR_main_claims=False,
  learning_kind='OriginalW35PPO/fullRM70 actual70mmpeak-to-trough/400N50D0-D7,fixedSI35/38. Not fullRM70skill orSMqualification',old227D_active_binding='HISTORICAL',full_RM70_skill='PENDING_NEW_LATEST_MODEL_FULL32S_CASE',new_qualified_SHA=role['SHA']),
 E2_actual232=dict(source_SHA='b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1',source_iteration=42822,Adam17=859300,actual_LR=.00022500000000000002,model_core_and_optimizer_unchanged=True,metadataV3_and_CUDA_DR_and_native24='PASS',
  actual_controls=1200,actual_seconds=24.,num_envs=20000,warmup=100,steady=1100,worker_wait0=True,all_original_control_clocks_queues_preserved=True,parent_passed_execution=False,parent_readerscope=clarification,full_E2_skill=False),
 E2_actual233=facts,
 decision='Normalization/restore/interface-clock proof passed,butE2 world-moving skill notqualified. Along-speed failure dominates(46147 of53140completeevents,40060along-only);cross9099/yaw8413overlap. Originalreference-to-.5errorMAE.00812 vsactual-to-reference.10469. This localizesobservedtrackingdeficit,notunique cause or population rate. Keepalloriginalbounds/reward/physics;nextauthorizedE2 originalPPO source preparation mayproceed afterexplicit Task/source/fullstate/readback/freshresources/solewriter;notblindlyclaimalloldexpertsorSMconverted.',
 action_chain_source='Sameauthorizedchildstaticreview:processprojectscrank,not hip;CADhiplimitsnotobservedsoftwaretargetclip;current inheritedSDK/cfg.clip UNKNOWN. Original225candidate/frozena92 untouched,no source-only fixclaim.',
 current_own_H1_learning=False,no_new_learning_GO_or_budget_writer=True,all_ROOT_SSH_closed_SESSION_restored_globalserial_FREE=True,
 future_remote='Fresh72 CNone ortrulynewexactowner/run/GO. Closed227D/219 bindingshistorical;never assumeactive orpermanentlyfree GPU.',
 pending=dict(E2_next_PPO_source='AuthorizedchildLOCALonly,inprogress/excluded untilownINDEX;noactuallearning',W35_full32s_latest2d0='Needsdistinctnewtypedpurpose;old227B fixed343e cannot silently pointto latest2d0',E3='NOT_GRADUATED',full_SuperMimic=False,E0='225copy/230wheelair9runs butheading/landingunresolved;no newE0trainingselected',true270=False),
 Git=dict(actual227_phase='CONSUMED',HEAD_before232='074c889507da8108ce965a4754b25a063f237e07',tagobject227='700e8b4e02e36776fddc7e2dcd7a373d26ba7f71',protected_old_tag_count=1508,new_actual232_phase='mod4-e2-metadata-reader-order-repair-and-world-skill232',any_existing232_tag_CONSUMED=True,227_closing='Ordinarysupplement capturedinside genuine232phase,no227retag'))
put(R/'CURRENT_CLOSED227D_AND_ACTUAL232233_E2_FAILURE_COMPONENTS_WORK_ORDER.json',summary)
put(W35/'reports/CURRENT_CLOSED227D_QUALIFIED_FULL_RM7077_AND_ACTUAL232233_E2_WORK_ORDER.json',summary)
print(json.dumps(dict(passed=True,W35new77=role['SHA'],E2complete24s=True,E2along_failure_events=facts['counts']['along_fail'],current_own_H1_learning=False)))
