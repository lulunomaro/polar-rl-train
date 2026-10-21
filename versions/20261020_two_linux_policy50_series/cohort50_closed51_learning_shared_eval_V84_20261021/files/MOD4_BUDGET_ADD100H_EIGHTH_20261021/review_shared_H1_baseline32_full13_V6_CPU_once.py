from pathlib import Path
import json,time,traceback,numpy as np,torch,sys
from frozen_actor_exact_cpu import FrozenActor
B=Path(__file__).resolve().parent;R=B/'reports';A=B/'shared_H1_baseline32_full13_V6_actual'
try:
 q=json.loads((R/'SHARED_H1_BASELINE32_FULL13_V6_EXISTING_FINITE_RETURNED_ACTUAL.json').read_bytes());co=q['parent_complete'];f=co['final'];assert not q['pending'] and q['actual_finite_transport_returned'] and co['passed'] and co['actual_child_waited'] and co['returncode']==0 and not co['errors'] and q['parent_exit']['all_own_children_waited'] and q['parent_exit']['own_eval_lease_released']
 c=np.load(A/'out/CONTROL_ACTUAL.npz',allow_pickle=False);p=np.load(A/'out/PHYSICAL_CALLBACK_ACTUAL.npz',allow_pickle=False);initial=np.load(A/'out/INITIAL_ACTUAL.npz',allow_pickle=False);cfg=json.loads((A/'out/ACTUAL_CONFIG.json').read_bytes());gpu=json.loads((A/'out/ACTUAL_SHARED_GPU_COMPUTE.json').read_bytes());assert cfg['source_SHA']==f['source_SHA'] and f['controls']==750 and f['callbacks']==6000 and f['feedback_samples']==1500 and f['actor9_STD_initial_final_literal_exact'] and f['zero_optimizer'];assert all('GPU-16828f91-2b45-b646-8dc0-9481138e2842' in x for x in gpu['own_compute_rows'])
 for data,count in ((c,750),(p,6000)):
  for k in data.files:
   value=data[k];assert value.shape[:2]==(count,13)
   if value.dtype.kind in 'fc':assert np.isfinite(value).all(),k
 obs=c['policy'];raw=c['raw_action'];done=c['done'].astype(bool);executed=c['executed6'];assert obs.shape==(750,13,35) and raw.shape==(750,13,6) and not obs[:,:,:3].any();assert np.array_equal(executed,np.clip(raw,-6,6));last=np.zeros((13,6),np.float32)
 for i in range(750):
  assert np.array_equal(obs[i,:,22:28],last),('previous_actual6',i)
  last=executed[i].copy();last[done[i]]=0
 mode=obs[:,:,28:35];assert np.isin(mode.argmax(-1),(0,3)).all() and np.array_equal(mode.sum(-1),np.ones((750,13),np.float32))
 ages=c['age_after'];prior=np.zeros(13,np.int64)
 for i in range(750):
  assert np.array_equal(ages[i],prior+2),('10ms_counter',i)
  prior=ages[i].copy();prior[done[i]]=0
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();src=B.parent/'MOD4_LINUX4090_RETURN_AND_BUDGET_RECONCILIATION_20261020/current_two50_closed_models/recovery/final_valid_update76.pt';actor=FrozenActor(src,f['source_SHA'],f['source_Adam']);CPU=np.stack([actor.mean(torch.from_numpy(x.copy())).numpy() for x in obs]);clip_error=float(abs(np.clip(CPU,-6,6)-executed).max());audit=json.loads((R/'SHARED_H1_BASELINE32_FULL13_V6_ORIGINAL_MEAN_SAVED_INPUT_GPU_AUDIT_ACTUAL.json').read_bytes());assert audit['source_SHA']==f['source_SHA'] and audit['source9_STD_unchanged'] and audit['zero_optimizer'] and audit['any_raw_exact'] and audit['any_clipped_exact'];assert next(x for x in audit['rows'] if x['precision']=='highest')['raw_bitwise_exact']
 old=B.parent/'MOD4_H1_TARGET72_CLOSED_FINAL_E3_FROZEN_REVIEW_20261017/e3_closed85_frozen_prepared_v1/payload';sys.path.insert(0,str(old));from hard_top1_frozen_expert_CPU_component_v1 import FrozenMean35
 original=FrozenMean35(actor.weights);assert torch.equal(original(torch.from_numpy(obs[0].copy())),actor.mean(torch.from_numpy(obs[0].copy()))) and actor.exact() and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 candidate_initial=np.load(B/'shared_H1_full13_V4_actual/out/INITIAL_ACTUAL.npz',allow_pickle=False);assert all(np.array_equal(initial[k],candidate_initial[k]) for k in ('root13','q30','recipe','mode'));cases=[];credited=c['credited_before_reset'].astype(bool)
 for env in range(13):
  failures=np.flatnonzero(done[:,env]);first_fail=int(failures[0]) if len(failures) else None;limit=first_fail+1 if first_fail is not None else 750;credits=np.flatnonzero(credited[:limit,env]);first_credit=int(credits[0]) if len(credits) else None
  cases.append(dict(recipe=env,public_request=env!=12,first_failure_control=None if first_fail is None else first_fail+1,first_failure_sim_seconds=None if first_fail is None else .02*(first_fail+1),source_stable_credit_in_first_episode=first_credit is not None,first_stable_credit_control=None if first_credit is None else first_credit+1,total_resets=int(done[:,env].sum()),closure_max_m=float(c['closure'][:,env].max()),mimic_max_rad=float(c['mimic'][:,env].max()),raw_saturation_fraction=float(np.mean(abs(raw[:,env])>6))))
 h=f['source_health'];assert h['actual_task_reset_events']==int(done.sum()) and h['integrity_task_reset_events']==h['unknown_task_reset_events']==0 and not h['nonfinite_observed']
 report=dict(epoch=time.time(),passed_diagnostic_execution_and_all_row_CPU=True,source_SHA=f['source_SHA'],source_Adam=f['source_Adam'],actual_GPU=gpu,case_count=13,request_case_count=12,physical_sim_seconds=15,controls=750,callbacks=6000,feedback_samples=1500,all_actor9_STD_frozen_no_optimizer=True,all_callback_control_finite=True,candidate_baseline_initial_state_bitwise_exact=True,previous_actual6_and_selected_reset_exact=True,public_mode_0_or3_exact=True,recovery_age_10ms_units_increment2_exact=True,mean_kernel_exact_original_CPU=True,original_same_GPU_saved_input_raw_action_bitwise_exact=True,original_mean_GPU_audit=audit,CPU_GPU_cross_device_difference_diagnostic_only=True,effective_clipped_action_CPU_GPU_max_abs_error=clip_error,first_episode_source_stable_recoveries=sum(x['source_stable_credit_in_first_episode'] for x in cases if x['public_request']),ordinary_failed_environments=sum(x['total_resets']>0 for x in cases),total_ordinary_resets=int(done.sum()),cases=cases,native13_no_baseline_behavior_improvement_claim=True,not_original104_graduation_or_jump_height=True,original_mimic01_closure2mm_source_selected_resets_retained=True,all_own_children_actual_out_and_eval_lease_free=True)
 with (R/'SHARED_H1_BASELINE32_FULL13_V6_ALL_ROWS_AND_FIRST_EPISODE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(passed=True,first_episode_recovered=report['first_episode_source_stable_recoveries'],request_cases=12,failed_envs=report['ordinary_failed_environments'],resets=report['total_ordinary_resets'],clip_error=clip_error,cases=cases)))
except BaseException:
 with (R/'SHARED_H1_BASELINE32_FULL13_V6_CPU_V3_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True),f,indent=2)
 raise
