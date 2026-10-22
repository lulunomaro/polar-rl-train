from pathlib import Path
import json,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports';N=T/'H1_STEP270_E3_REWARD_PATH_PAIR_V18_20261022'
read=lambda p:json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 proof=read(N/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');assert proof['passed']
 p=N/'current_pair_closed_text/h1/job0/production';healths=list(p.glob('logs/*/CLOCK_TRAINING_HEALTH.json'));assert len(healths)==1;h=read(healths[0])
 assert h['control_steps']==proof['models']['h1']['updates']*24==2808
 assert h['actual_physics_callbacks']==h['expected_physics_callbacks']==2808*4
 assert not h['nonfinite_observed'] and h['termination_reason_coverage_exact'] and h['unknown_task_reset_events']==h['integrity_task_reset_events']==0 and h['stop_reason'] is None
 root=p/'control_prefix_raw';index=read(root/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json');history=read(root/'PREFIX_PAIR_RETENTION_HISTORY_ACTUAL.json')
 receipts={x.name:read(x) for x in root.glob('PREFIX_PAIR_RETENTION_RECEIPT_*.json')};intents={x.name:read(x) for x in root.glob('PREFIX_PAIR_RETENTION_INTENT_*.json')}
 count=len(index['index']);assert count==117 and index['controls']==2808 and len(index['retention_status'])==count
 kept=[x['index'] for x in index['retention_status'] if x['raw_retained'] and x['preupdate_retained']];assert kept==[0,115,116]
 assert not index['all_success_and_failed_control_prefixes_retained'] and not index['retention_failure_flag_preserves_all_currently_present_files']
 removed=[]
 for tx in history['transactions']:
  name=Path(tx['intent']).name;intent=intents[name];receipt=receipts[name.replace('INTENT','RECEIPT')]
  assert receipt==tx and receipt['all_selected_actual_removed']
  selected=[f for row in intent['selected'] for f in row['files']];assert selected==receipt['removed'];removed+=selected
 assert len(receipts)==len(intents)==len(history['transactions'])==114 and len(removed)==228
 assert len({x['path'] for x in removed})==228
 retain_bytes=sum(index['index'][i]['bytes']+index['index'][i]['preupdate_source']['bytes'] for i in kept)
 errors=[x.name for x in root.iterdir() if 'ERROR' in x.name or 'FAIL' in x.name];assert not errors
 terms=('Episode_Reward/h1_step270_path_progress','Episode_Reward/h1_step270_requested_forward','Episode_Reward/h1_scut_fudan_air_wheel_zero_torque')
 selected=[]
 with (p.parent/'production_WORKER.log').open(encoding='utf8',errors='replace') as f:
  for line in f:
   if any(k in line for k in terms):selected.append(line.rstrip())
 assert selected
 put('V108_FIRST_NEW_REWARD_COMPLETE117_HEALTH_RETENTION_AND_EPISODE_CPU_ACTUAL.json',dict(epoch=time.time(),passed_checkpoint_health_and_recording_scope=True,health=h,H1_current_episode_snapshot=proof['models']['h1']['H1_current_episode_snapshot'],retention=dict(producer_count=count,retained_indices=kept,retained_pair_producer_bytes=retain_bytes,original_all_success_and_failed_control_prefixes_retained=False,transactions=114,removed_files=228,all_intent_receipt_history_exact=True,errors=errors,text_only_not_new_directory_stat_or_raw_PT_read=True),actual_reward_log_last12=selected[-12:],no_storage_savedstop_file=not any(p.glob('*SAVED_STOP*')),not_skill_or_whole_window_event_totals=True,no_GPU_actor_optimizer_RNG_or_additional_PT_load=True))
 print(json.dumps(dict(passed=True,controls=2808,callbacks=11232,retained=kept,current_episode_landing=proof['models']['h1']['H1_current_episode_snapshot']['landing_count_sum'],not_skill_PASS=True)))
except BaseException:
 put('CLOSED18_TEXT_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
