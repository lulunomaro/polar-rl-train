"""Text/source-only closed-window handoff. No model, raw, GPU or remote reads."""
from pathlib import Path
import json, hashlib, time, tomllib
N=Path(__file__).resolve().parent;R=N/'reports';T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,x):
 with (R/name).open('x',encoding='utf8') as f:json.dump(x,f,indent=2,ensure_ascii=False)
def main():
 c=read(R/'NATIVE88C_CASE_SAFE_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_V2_ACTUAL.json')
 v=read(R/'NATIVE88C_READER_REPAIRED_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
 assert c['all_active_node_collection_passed'] and v['passed'] and not v['errors']
 prepared=read(R/'NATIVE88_TWO_PAYLOADS_SOURCE_PREPARED_ACTUAL.json')
 summaries={}
 for key in ('h1','recovery'):
  f=c['native_H1_method_fullstate'][key][0];p=N/'current_native88_closed_text'/key/'job0/production'
  rows=[json.loads(line) for line in (p/'ACTUAL_H1_CONVERGENCE_CURVE.jsonl').read_text('utf8').splitlines() if line.strip()]
  assert all(r['events']['diagnostic_valid'] for r in rows)
  previous=0;increments=[]
  for row in rows:
   count=row['events']['events']['takeoff_count']
   if count>previous:increments.append(dict(right_control_inclusive=row['completed_control_rows'],GO_elapsed_s=row['GO_elapsed_s'],delta=count-previous))
   assert count>=previous;previous=count
  final_events=f['original_H1_events'];window=f['native88_migration_window'];phase=read(p/'NATIVE_POLICY_PHASE_SAMPLE_COVERAGE_ACTUAL.json')
  last=rows[-1];source=Path(prepared['payloads'][key])/'source/supermimic_wheel_leg_v3/learner.py'
  manifest=read(Path(prepared['payloads'][key])/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
  pin=next(r for r in manifest['files'] if r['relative']=='source/supermimic_wheel_leg_v3/learner.py')
  assert H(source)==pin['SHA']
  learner=source.read_text('utf8')
  assert 'imagined_reward = (reward_sum / self.cfg.horizon / self.mdp.max_step_reward).mean()' in learner
  assert 'imagined_reward,\n            grad_norm.detach(),' in learner
  summaries[key]=dict(final_path=f['local_path'],final_bytes=f['bytes'],final_SHA=f['SHA'],updates=f['updates'],world_updates=f['world_updates'],policy_updates=f['policy_updates'],new_window=window['counters'],true_completed_control_events=final_events,
    true_complete_control_coverage=final_events['complete_control_rows']==window['counters']['completed_fresh_controls'],curve_rows=len(rows),last_curve_GO_elapsed_s=last['GO_elapsed_s'],last_takeoff_increment_observed=increments[-1] if increments else None,
    first_newPi=window['first_new_policy_update'],phase=phase,latest_policy_last=last['policy_last'],latest_normalized_imagined_reward=last['policy_last'][2],learner_source_SHA=pin['SHA'],imagined_reward_is_not_real_skill_success=True,
    phase_counts_are_attempted_starts_not_completed_optimizer_updates_or_unique_envs=True,events_cover_completed_rows_not_all_physics_callbacks_or_frozen_success_rate=True)
 cost=v['original_fees']
 out=dict(schema='mod4.closed88C.actual_two_native_completed_window_and_reader_recovery.v1',epoch=time.time(),run_id=c['run_id'],passed_model_cost_allout=True,step_skill_success_observed=False,models=summaries,original_fees=cost,
  original_collector_failed_local_casefold_capture_not_training=True,case_safe_missing_only_transfer_V2_passed=True,original_reader_NameError_H_before_NEW_FINAL_loads=True,reader_dependency_fix_only_H_and_read=True,
  original_reader_shared_witness_loads=1,original_reader_NEW_FINAL_loads=0,new_purpose_shared_witness_necessary_reread=1,new_purpose_NEW_FINAL_initial_loads=2,no_R5_native_model_reread=True,
  training_and_hardware_or_reward_not_changed_for_collection_or_reader_repair=True,old_false_reports_unchanged=True,
  evidence_interpretation=['No completed-row crossing/landing/stable recovery in either current window. This is not a frozen evaluation or permanent impossibility proof.',
   'Jump-phase attempted starts are present. Initial phase starvation alone does not explain this result.',
   'Normalized imagined rewards near .93-.95 coexist with zero real step events. Different state/sample scopes prevent treating this alone as a proven WM-error cause.',
   'Most takeoffs occurred before first NEW Pi; a few later increments stop early in the window. This does not establish causal policy regression.'],
  next_concrete_work='Admit a new typed gas400/own-wheel V2 native88C frozen single attempt with the qualified h1 FINAL, real terminations/contact/height/gap/tilt/action history; compare real motion and imagined objective before another training window.',
  next_source_helper=dict(path=str(L/'native88C_frozen_single_attempt_source_preparation_v1'),status='SOURCE_ONLY_HELPER_IN_PROGRESS_OR_FROZEN_SEPARATELY_CHECK_INDEX',not_installed_or_executed=True,pending_ordinary_capture_after_freeze=True),
  no_new_training_payload_controller_Task_GO_fee_or_replay_this_heartbeat=True,goal_remains_unachieved=True,hourly_only_no_continuous_Goal=True,unknown16828_preserved=True)
 put('CURRENT_CLOSED88C_ACTUAL_RESULTS_READER_REPAIR_AND_NEXT_DIAGNOSTIC_WORK_ORDER.json',out)
 old=tomllib.loads(Path(r'C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
 with (R/'PREVIOUS_ACTUAL88C_FIRST_PI_AND_PRE_CLOSE_MONITOR_HISTORICAL.txt').open('x',encoding='utf8') as f:f.write(old['prompt'])
 description='''Closed88C: two formal nativeH1 models on the two authorized free4090s completed, original sole72 costs settled and allout verified. Original gas400/reset/own-wheel V2 admission remains actual. No actual step success: h1 7944 completedcontrols x4096=32538624 transitions takeoff203; recovery3235x4096=13250560 takeoff678; both leadingcross/landing/stable-recovery0. Native progress h1 6469/64690/6341 (NEW31520WM/3088Pi), recovery2677/26770/2549 (NEW12680WM/1204Pi). Actual normalduration independent costs3606.0225822925568+3610.161264896393=7216.18384718895, closing562175.5721518993 snapshot. No refund/recharge/budget change/secondwriter.

Original collector221 had a Windows casefold path collision between upper/lowercase STARTED reports; its false/partial preserved. New missing-only222 keeps canonical production paths, distinct case-preserved diagnostics, verifies/reuses old copied bytes and transfers only missing text plus each NEW formal FINAL once. Both actual source terminal/knownidentity/locks/cost/formal metadata/stat/twohostSHA passed. Source FINALs256227465bytes each, h1a9bf6dca376e9d570ef0a6e2c15604f38656c4ebfedaa829a34830ee57c73aaf and recovery0885f3cfc4413c7a65b4f50448df6cbcdb7427152b4f3a95e47185ecd5e2b2a0. Native is a method source, never normalH1/E2/PPO promotion.

Original initialCPU reader failed before both NEW FINAL loads because pure-source PinnedSource omitted H/read helpers. It already loaded sharednormal86 witness once then exited; oldfalse/intent/consumedmarker preserved. One sequential helper froze only those2pure functions, original all function/class AST and guards exact,9tiny sourceCPU tests and unresolved-global audit passed. New separate purpose/output namespace first preflights actual source/CPU metadata, then loads each NEW FINAL initially once plus ONE necessary extra sharednormal86 witness read for literal frozen comparison after prior process cache was lost. This necessary reread is explicit; no false claim of0oldwitness reads. Allnewmodels/norms/WM/Pi/Critic/3opts finite and strict, frozenRSLactor9critic8STD6/17Adam832460 exact, actual400backend/preload/firstreset/source/objective/recipe/task/clock/save checks passed; no actual actor/WM forward, GPU, scene, raw or account action. No oldR5 native reread. Collector and CPU reader failures are collection/reader issues, not training failures. All original source/errors/false retained.

Complete curves include jump-phase attempted starts but no crossing/landing/recovery; normalized imagined rewards~.948/.932 do not imply actual motion success. This motivates real-vs-imagined diagnostic, does not prove a unique cause or causal regression. No blindly identical new training window. Latest qualified method sources now the complete88C formal models; next typed single fresh frozen gas400 nativeC attempt is source preparation only, no new test run/GO. At mostONE sequential helper source-only; any active next helper explicitly pending ordinary capture after freeze and excluded from this immutable capture. Root remains sole finiteSSH. User hourly replacement persists, no continuous Goal exists/recreated. Unknown16828 retained; solefinite72authority/old210retirement/physical/success/caps unchanged. All1461existingtagobjects/peels protected, ordinary supplement to consumed88trial, no record/tag. Binarymetadata only actualpathbytes/existingproducerSHA, no model/raw/USD/GPU/host read forGit. PostGit verification conversation only.
'''
 with (R/'CLOSED88C_ORDINARY_ARCHIVE_DESCRIPTION_SOURCE.txt').open('x',encoding='utf8') as f:f.write(description)
 print(json.dumps(dict(passed=True,models={k:dict(controls=x['true_completed_control_events']['complete_control_rows'],events=x['true_completed_control_events']['events'],cross=x['true_completed_control_events']['both_leading_edges_cross_event_count']) for k,x in summaries.items()},fees=cost),ensure_ascii=False))
if __name__=='__main__':main()
