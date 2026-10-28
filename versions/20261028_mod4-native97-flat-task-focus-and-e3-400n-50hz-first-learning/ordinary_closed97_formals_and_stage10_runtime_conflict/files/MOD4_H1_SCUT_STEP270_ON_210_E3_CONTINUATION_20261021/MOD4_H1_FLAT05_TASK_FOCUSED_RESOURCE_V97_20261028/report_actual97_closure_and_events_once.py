from pathlib import Path
import json,re,time
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
C=L/'TWO97_correct_normal900_dual_native_PPO_collector_source_v1'
v=read(C/'reports/TWO97_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
h=read(L/'TWO97_NEW_H1_NATIVE_FORMAL_INITIAL_CPU_SOURCE_V1/reports/NATIVE97_NEW_FORMAL_INITIAL_WHOLE_CPU_QUALIFIED_ACTUAL.json')
e3=read(L/'TWO97_NEW_E3_PPO_FORMAL_INITIAL_CPU_SOURCE_V1/reports/E3_97_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V1.json')
assert h['passed'] and e3['passed'] and v['canonical_None'] and v['all_two_original_owner_nodes_workers_out']
events=v['published']['h1']['original_producer']['original_H1_events'];flat=events['flat_real_physics_events'];original=events['original270_completed_control_events'];count=h['progress']['counters']
assert count['completed_fresh_controls']==original['complete_control_rows']==3500
assert original['environment_control_transitions']==3500*4096 and original['diagnostic_valid'] and original['invalid_rows']==0
assert flat['callbacks']==14000 and flat['last_physics_tick']==14000 and flat['tick_errors']==0
texts=v['all_original_texts_full_case_safe'];focus=[r for r in texts if re.search(r'NATIVE_TASK_FOCUS_SAMPLE_COUNTS_\d+_ACTUAL.json$',r['relative'])]
ids=sorted(int(re.search(r'COUNTS_(\d+)',r['relative'])[1]) for r in focus)
assert ids==list(range(1,count['new_policy_updates']+1))
last_focus=read(max(focus,key=lambda r:int(re.search(r'COUNTS_(\d+)',r['relative'])[1]))['local_path'])
assert last_focus['calls']==count['new_policy_updates']==1310 and last_focus['returned_starts']==1310*1024
assert last_focus['selected_focus']+last_focus['fallback_uniform']==last_focus['requested_focus']
curve=next(r for r in texts if r['relative']=='h1_slot/h1/job0/production/ACTUAL_H1_CONVERGENCE_CURVE.jsonl')
rows=0;previous=-1;last=None
with Path(curve['local_path']).open(encoding='utf8') as f:
 for line in f:
  last=json.loads(line);assert last['completed_control_rows']>=previous;previous=last['completed_control_rows'];rows+=1
assert last['native_iteration']==count['native_iteration'] and last['completed_control_rows']==3499
proof=dict(epoch=time.time(),formal_h1=v['published']['h1'],formal_e3=v['published']['e3'],native_progress=count,E3_new_PPO_updates=e3['new_updates'],E3_Adam=e3['Adam_step'],original_events=events,formal_complete_rows=3500,formal_environment_transitions=3500*4096,formal_flat_physics_callbacks=14000,flat_invalid_env_callbacks=flat['lifetime']['invalid_env_callbacks'],flat_invalid_callbacks_not_reconstructed_or_declared_valid=True,no_observed_flat5cm_takeoff_height_landing_recovery=all(flat['lifetime'][k]==0 for k in ('takeoffs','height_met','landings','recoveries')),no_observed_270_success=True,curve=dict(source=curve,rows=rows,last_complete_control_rows=last['completed_control_rows'],last_elapsed_s=last['GO_elapsed_s'],last_policy=last['policy_last'],last_wm=last['wm_last'],last_flat_lifetime=last['flat_real_physics_events']['lifetime'],formal_includes_one_more_complete_control=True),task_focus=dict(last_original=last_focus,all_call_receipts_present=True,actual_selected_focus_fraction=last_focus['selected_focus']/last_focus['returned_starts'],attempted_starts_not_unique_envs_or_airborne_transitions=True),original_fees=v['original_fee_by_slot'],original_fee_sum=v['original_fee_seconds'],closed_remaining_snapshot=v['closing_remaining_snapshot'],original_two_models_initial_CPU_qualified=True,no_additional_model_weight_read_hash_actor_WM_forward_GPU_remote_or_account_write=True,not_skill_graduation=True)
put('CLOSED97_TWO_QUALIFIED_FORMALS_AND_REAL_EVENT_SCOPE_ACTUAL.json',proof)
stage10=read(L/'NEW_HOST_STAGE10_READONLY_TERMINAL_FULL_LOG_SOURCE_V1/reports/STAGE10_READONLY_TERMINAL_FULL_LOGS_RETURNED_ACTUAL.json')
assert stage10['terminal_observed'] and stage10['all_original_recorded_out'] and stage10['installer_passed'] is False
put('CURRENT_CLOSED97_RESULTS_AND_NEXT_FROZEN_MOTION_DIAGNOSTIC_WORK_ORDER_ACTUAL.json',dict(epoch=time.time(),state='CLOSED97_TWO_FORMALS_QUALIFIED_NO_OBSERVED_H1_TAKEOFF',event_report=str(R/'CLOSED97_TWO_QUALIFIED_FORMALS_AND_REAL_EVENT_SCOPE_ACTUAL.json'),latest_native_method=v['published']['h1'],latest_normal_E3_adapted=e3['model'],next_root='Prepare one NEW typed97 fixed-seed20260928 fresh N1 frozen-policy motion and paired WM diagnostic, original done or maximum500 controls/2000 callbacks/5s; no learner.collect/optimizer/normalizer updates; exact97 source objective/mask/terminal/focus contracts and400 plant. No identical blind training window.',next_child='Use already delegated minimum frozen E0 source210 regression; other expert actual transition collection after typed admission. Child owns oldexperts/new86; root H1 only.',stage10=dict(collected=True,terminal_failed=True,all_original_out=True,primary_dependency_conflict='isaacsim-core6.0.1.0 requires torch==2.11.0 versus pinned torch2.10.0+cu128',Nvidia_DNS_retry_also_retained=True,no_install_SDK_GPU_model_GO_proof=True,next='Coherent runtime metadata proposal in unused namespace, no old launcher rerun or dependency ignoring.'),Git=dict(unique97_consumed=True,actual_main_before_supplement='83223781238bcc5c3a77db968e595d64a6ad75a0',ordinary_pending=['all97closure/fullUTF8/source and readers','two initialCPU reviews','real event scope and workorder','Stage10 new reader/local preparer error/full failure logs','frozen E3 reviewer source','next H1 diagnostic source after freeze','child source after freeze']),no_continuous_Goal_or_duplicate_monitor=True))
print(json.dumps(dict(passed_scope=True,native=count,E3_new_PPO=e3['new_updates'],flat_lifetime=flat['lifetime'],task_focus_fraction=proof['task_focus']['actual_selected_focus_fraction'],original_fee_sum=v['original_fee_seconds'])))
