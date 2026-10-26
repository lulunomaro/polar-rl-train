"""Bounded new86B text only; no PT/raw/actor/plant imports or network."""
from pathlib import Path
import hashlib,importlib.util,json,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
READER=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026/agent_closed85_native_curve_analysis_cpu/native_curve_text_reader_v1.py'
READER_SHA='138ff24522e214993ca8fc2a08570716879408130118b022964f9d3eb15bd0e0'
BASELINE=dict(native_iteration=68,world_updates=680,policy_updates=58)

def first_new(rows,key,baseline):
 previous=None
 for row in rows:
  if not row['update_counters_valid']:continue
  value=row[key]
  if value<baseline:raise ValueError('Cumulative native counter below qualified source: '+key)
  if value>baseline:
   return dict(status='first_new_update_curve_interval_censored',source_baseline=baseline,
    lower_GO_elapsed_s=None if previous is None else previous['GO_elapsed_s'],upper_GO_elapsed_s=row['GO_elapsed_s'],
    lower_completed_controls=None if previous is None else previous['completed_control_rows'],upper_completed_controls=row['completed_control_rows'],
    cumulative_count=value,new_window_count=value-baseline,exact_optimizer_time_unknown=True)
  previous=row
 return dict(status='no_new_update_in_valid_curve_rows' if previous is not None else 'unknown_no_valid_rows',source_baseline=baseline)

def main():
 raw=READER.read_bytes();assert hashlib.sha256(raw).hexdigest()==READER_SHA
 spec=importlib.util.spec_from_file_location('pinned_original_text_curve_reader86b',READER);reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
 collector_path=R/'THREE_GPU86B_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json'
 collector=json.loads(collector_path.read_bytes());assert collector['actual_finite_transport_returned']
 detached=json.loads((R/'THREE_GPU86B_ACTUAL_OWNER_NODES_DETACHED.json').read_bytes());assert collector['run_id']==detached['run_id']
 inputs=reader.collector_inputs(collector);go=collector['authority72']['cohort']['go']['e2']
 assert inputs['go']==go and go['source_native_iteration']==68 and go['window_start_world_updates']==680 and go['window_start_policy_updates']==58
 curve=inputs.pop('curve',None);analysis=reader.analyze_curve(curve,**inputs)
 if analysis.get('first_positive'):
  for key in ('world_updates','policy_updates'):analysis['first_positive'].pop(key,None)
 analysis['first_new_native_updates']={key:first_new(analysis['rows'],key,BASELINE[key]) for key in ('world_updates','policy_updates')}
 analysis['native_source_and_window_baseline']=BASELINE
 summary=analysis.get('curve_summary')
 if summary:analysis['new_window_last_curve_progress']={k:summary[k]-v for k,v in BASELINE.items()}
 analysis.update(epoch=time.time(),scope='actual86B completed-control text and cumulative source85-to86B native counters',
  source_model_read=False,loss_or_new_update_not_step_success=True,
  no_frozen_evaluation_or_matched_causal_speed_ratio=True,
  formal_native_FINAL_and_fullfinite_qualification_is_separate_CPU_report=True)
 with (R/'CLOSED86B_NATIVE_NEW_WINDOW_EVENTS_PHASE_AND_TIME_TEXT_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(analysis,f,ensure_ascii=False,indent=2,allow_nan=False)
 print(json.dumps(dict(status=analysis['status'],curve_rows=analysis.get('parsed_curve_rows'),event_coverage=analysis.get('final_counter_coverage',{}).get('status'),new_updates=analysis['first_new_native_updates'],not_skill_graduation=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('CLOSED86B_TEXT_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_model_read_or_same_once_retry=True),f,indent=2)
  raise
