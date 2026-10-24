from pathlib import Path
import json,math,statistics,time,traceback
N=Path(__file__).resolve().parent;R=N/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def stats(values):
 values=sorted(float(x) for x in values);assert values and all(math.isfinite(x) for x in values)
 def q(p):
  x=(len(values)-1)*p;lo=int(x);return values[lo]*(1-(x-lo))+values[min(lo+1,len(values)-1)]*(x-lo)
 return dict(count=len(values),median=statistics.median(values),q25=q(.25),q75=q(.75),minimum=values[0],maximum=values[-1])
try:
 closed=json.loads((R/'BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());assert closed['collector_function_complete'] and closed['original_canonical_cost_settled'] and closed['owner_node_workers_all_actual_out']
 slots={}
 fields=['collection_s','original_logger_learning_s','actor_critic_act_wall_s','environment_step_wall_s','PPO_update_wall_s','cycle_wall_s','collection_env_steps_s','end_to_end_env_steps_s']
 for key in ['h1','recovery']:
  base=N/'benchmark_closed_text'/key/'job0/production';modes={};errors={str(p.relative_to(base)):json.loads(p.read_bytes()) for p in base.rglob('*ORIGINAL_ERROR*.json')}
  for mode in ['fp32','bf16','fp16']:
   path=base/mode/'MODE_COMPLETE_ACTUAL.json'
   if not path.exists():modes[mode]=dict(valid=False,reason='No actual mode completion receipt');continue
   result=json.loads(path.read_bytes());rows=[r for r in result['rows'] if not r['warmup']]
   valid=result['complete'] and result['actual_completed_updates']==6 and len(rows)==4 and all(r['all_source_model_optimizer_tensors_finite'] and r['actual17Adam_steps']==[r['expected_Adam_without_skipped_FP16_steps']] for r in result['rows'])
   phases=sorted({p for r in rows for p in r['sampling_phase_exclusive_CPU_wall_s']})
   measurements={f:stats([r[f] for r in rows]) for f in fields} if rows else {}
   phase_rows=[]
   for p in phases:
    wall=stats([r['sampling_phase_exclusive_CPU_wall_s'].get(p,0.) for r in rows]);pct=stats([100*r['sampling_phase_exclusive_CPU_wall_s'].get(p,0.)/r['collection_s'] for r in rows]);phase_rows.append(dict(phase=p,seconds=wall,percent_of_collection=pct,calls_per_update=sorted({r['sampling_phase_call_counts'].get(p,0) for r in rows})))
   phase_rows.sort(key=lambda r:r['seconds']['median'],reverse=True)
   modes[mode]=dict(valid=valid,complete=result['complete'],complete_updates=result['actual_completed_updates'],error=result.get('error'),comparison_same_source_same_reset_observations=result['comparison'],FP32_master_parameters=result['all_FP32_master_parameters'],measurements=measurements,sampling_phases_CPU_exclusive_wall=phase_rows,unattributed_or_async_tail=stats([r['collection_unattributed_or_async_tail_s'] for r in rows]) if rows else None,all_actual_17Adam_steps=[r['actual17Adam_steps'] for r in result['rows']],benchmark_only_not_source=True)
  gains={}
  if modes['fp32']['valid']:
   base=modes['fp32']['measurements']
   for mode in ['bf16','fp16']:
    if not modes[mode]['valid']:continue
    other=modes[mode]['measurements'];gains[mode]=dict(collection_step_speed_change_percent=100*(other['collection_env_steps_s']['median']/base['collection_env_steps_s']['median']-1),cycle_step_speed_change_percent=100*(other['end_to_end_env_steps_s']['median']/base['end_to_end_env_steps_s']['median']-1),PPO_update_speed_factor=base['PPO_update_wall_s']['median']/other['PPO_update_wall_s']['median'],inference_speed_factor=base['actor_critic_act_wall_s']['median']/other['actor_critic_act_wall_s']['median'],only_four_measured_updates_per_mode_IQR_reported_not_statistical_significance=True)
  slots[key]=dict(modes=modes,measured_changes_from_same_instrumented_FP32=gains,all_actual_errors_preserved=errors)
 result=dict(epoch=time.time(),passed_summary_CPU=True,both_slots_all_three_modes_valid=all(v['modes'][m]['valid'] for v in slots.values() for m in ['fp32','bf16','fp16']),slots=slots,actual_original_cost_sumonce=closed['original_actual_cost_sumonce'],remaining_at_actual_closure_snapshot=closed['original_remaining_closed_snapshot'],units='20k environments x24 decisions per update =480000 transitions per wall second, not single-env control Hz',scope='Sampling+update cycle timing from first act to logger entry; excludes logger/report-writing and any between-iteration save, includes original H1 trace/preupdate/NPZ/fullSHA/retention within collection. Mode setup and warmup excluded. CPU-wall phase attribution includes implicit GPU waits; not CUPTI-exclusive GPU kernel percentages.',fixed_mode_order_and_stochastic_trajectory_divergence_limit=True,no_claim_bitwise_equal_trajectories_or_long_run_training_quality=True,no_BF16_FP16_production_adoption_or_270mm_graduation=True,latestqualified_sources_remain_closed67=True,no_PT_raw_model_policy_GPU_or_host_query=True)
 put('ACTUAL_CLOSED_FP32_BF16_FP16_THROUGHPUT_AND_SAMPLING_PHASE_CPU_SUMMARY.json',result)
 print(json.dumps(dict(all_modes_valid=result['both_slots_all_three_modes_valid'],cost=result['actual_original_cost_sumonce'],slots={key:dict(gains=s['measured_changes_from_same_instrumented_FP32'],FP32_sampling_largest=s['modes']['fp32'].get('sampling_phases_CPU_exclusive_wall',[])[:5],valid_modes={k:v['valid'] for k,v in s['modes'].items()}) for key,s in slots.items()})))
except BaseException:
 put('PERFORMANCE_SUMMARY_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
