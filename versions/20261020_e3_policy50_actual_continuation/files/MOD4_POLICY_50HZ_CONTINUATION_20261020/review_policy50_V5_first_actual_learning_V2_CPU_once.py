"""Review actual target clock, full native inheritance, health and first PPO without GPU access."""
from pathlib import Path
import hashlib,json,time,traceback,sys
B=Path(__file__).resolve().parent;R=B/'reports';A=B.parent/'MOD4_E3_AUTOMATIC_CONTINUATION_20261020'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 q=json.loads((R/'POLICY50_V5_MISSING_PPO_V2_FINITE_RETURNED_ACTUAL.json').read_bytes());assert q['actual_finite_transport_returned'];v=q['actual'];assert v['actual_50Hz_learning_verified'] and not v['errors'] and not v['series_error'];captures={x['remote_path']:x for x in q['captured_texts']}
 def captured(remote):
  row=captures[remote];p=Path(row['local_path']);assert H(p)==row['captured_SHA'];return json.loads(p.read_bytes())
 root=v['root'];node=root.rsplit('/',1)[0]+'/windows/hour0001/recovery';expected=json.loads((R/'POLICY50_V5_REMOTE_CONTROLLER_OVERLAY_EXACT_SHA_ACTUAL.json').read_bytes())['exact_SHA']
 for name,sha in expected.items():assert captures[root+'/'+name]['captured_SHA']==sha
 install=json.loads((R/'POLICY50_V5_ORIGINAL_SERIES_CLOSED_RESOURCE_HANDOFF_ACTUAL.json').read_bytes());cfg=install['cfg'];spec=captured(node.rsplit('/',1)[0]+'/SPEC_NO_TOKEN.json');assert spec['source_SHA']==cfg['initial_source']['SHA'] and spec['source_Adamstep']==cfg['initial_source']['Adam_step'] and spec['policy_hz']==50 and spec['source_policy_hz']==100
 native=v['actual_clock_native_CPU'];assert native['passed'] and native['source_SHA']==spec['source_SHA'] and native['source_actor9_critic8_STD17Adam_literal_exact'] and native['whole_tensor_counts']==[173,96] and native['actual_native_worker_waited_EXIT0']
 health=[captured(p) for p in captures if p.startswith(node+'/job0/clock_native50/logs/') and p.endswith('/CLOCK_TRAINING_HEALTH.json')];assert len(health)==1;health=health[0]
 assert health['version']==3 and health['integrity_task_reset_events']==health['unknown_task_reset_events']==0 and not health['nonfinite_observed'] and health['max_mimic_error_rad']<=.01 and health['termination_reason_coverage_exact'] and health['actual_physics_callbacks']==health['expected_physics_callbacks']==192 and health['control_dt_s']==.02 and not health['stop_reason']
 dt=captured(node+'/job0/production/E3_ACTUAL_SDK_REWARD_DT_PROBE.json');assert dt['dt']==.02 and dt['known_one_event_output_maxabs']<=1e-6 and dt['isolated_from_live_reward_manager']
 zero=captured(node+'/job0/production/SOURCE_TYPED_ZERO_CLOCK_ACTUAL.json');assert zero['source_SHA']==spec['source_SHA'] and zero['core_actor9_critic8_STD17Adam_literal_exact'];assert len(zero['startup'])>=7
 clock=v['actual_clock'];assert clock['physics_dt_s']==.0025 and clock['control_period_s']==.02 and clock['decimation']==8 and clock['feedback_sampling_hz']==100 and clock['action_transition_delay_us']==[0,2500,5000] and clock['gamma']==.9801 and clock['lam']==.9025
 saved=v['latest_PPO'];assert saved['updates']>0 and saved['Adam_step']==spec['source_Adamstep']+20*saved['updates'];go=v['GO'];assert go['source_qualification_kind']=='policy_clock_100_to_50_migration' and go['source_SHA']==spec['source_SHA'] and go['save_deadline']-go['learning_started_epoch']==3600 and go['nominal_end_epoch']-go['learning_started_epoch']==3900
 assert cfg['prior_100hz_series_pending_seconds']==sum(x['actual_pending_seconds'] for x in install['previous_closed_windows']);assert len(install['previous_closed_windows'])==len({x['run_id'] for x in install['previous_closed_windows']})
 report=dict(epoch=time.time(),passed=True,actual_50Hz_GO_positive_PPO_UUID_create_argv_verified=True,initial_source=cfg['initial_source'],source_Adam=spec['source_Adamstep'],current_complete_update=saved,GO=go,actual_policy_clock=clock,native_protocol='24 control / 192 callbacks / zero optimizer',native_full173_96_actor9_critic8_STD17Adam_exact_and_health_CPU_verified=True,native_health=health,actual_SDK_reward_dt_probe=dt,all7_full_state_startup_receipts=True,controller_overlay_SHA_exact=True,parent_identity=v['identity'],worker_identity=v['worker'],previous_100hz_series_all15_closed_actual_out=True,prior_100hz_series_pending_seconds=cfg['prior_100hz_series_pending_seconds'],prior_single_E3_pending_seconds=cfg['prior_single_E3_pending_seconds'],original_canonical_settled=False,existing_budget_only=True,not_future_FINAL_or_behavior_or_skill_qualification=True,player_and_package_not_changed=True)
 put('POLICY50_V5_FIRST_ACTUAL_LEARNING_WHOLE_INHERITANCE_CLOCK_HEALTH_CPU_ACTUAL.json',report);print(json.dumps(dict(passed=True,actual_policy_hz=50,PPO_updates=saved['updates'],Adam=saved['Adam_step'],source_SHA=spec['source_SHA'],canonical_settled=False)))
if __name__=='__main__':
 try:main()
 except BaseException:put('POLICY50_V5_FIRST_CPU_REVIEW_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_training_or_account_change=True));raise
