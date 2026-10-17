"""Actual matched initial-state comparison only; no causal/statistical or new skill claim."""
from pathlib import Path
import json,time,sys,traceback
B=Path(__file__).resolve().parent;R=B/'reports'
def case(name):
 j=json.loads((R/name).read_bytes())
 def path(n):return Path(next(r['local_path'] for r in j['files'] if r['relative'].endswith('/'+n)))
 return json.loads(path('probe.json').read_bytes())['native_readonly_witness'],json.loads(path('retention_plane_query_actual.json').read_bytes())
def main():
 a,qa=case('LINUX_GPU1_MEANFIRST_FULL1500_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json');b,qb=case('LINUX_GPU1_PUBLIC4N1_FULL1500_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json');ia=a['first_physics_initial'];ib=b['first_physics_initial']
 exact={k:ia[k]==ib[k] for k in ('root','q30','physical_parameters')};assert all(exact.values())
 refs={k:qa['initial'][k]==qb['initial'][k] for k in ('actual_USD_and_native_actor_metadata','source_reference')};refs['loaded_own_PhysX_files']=qa['initial']['loaded_PhysX_binary_fingerprints']['files']==qb['initial']['loaded_PhysX_binary_fingerprints']['files'];assert all(refs.values())
 x=json.loads((R/'H1_MEANFIRST_LINUX72_1500_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_ACTUAL.json').read_bytes());y=json.loads((R/'H1_PUBLIC4N1_LINUX72_1500_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_ACTUAL.json').read_bytes());assert x['passed_complete_data_and_source_CPU'] and y['passed_complete_data_and_source_CPU']
 out=dict(epoch=time.time(),actual_initial_root_q30_DR_parameters_complete_RNG_queue_states_exact=exact,actual_Plane_native_actor_source_reference_loaded_own_PhysX_exact=refs,same_actual_initial_all_selected_fields_exact=True,source_old_global_aux_first=x,source_new_public4_normal_only_first=y,first24_normal_controls_aux0_not_post_auxiliary_effectiveness=True,source_order_not_statistical_significance_or_unique_cause=True,no_old_results_relabelled_or_raw_modified=True,original_thresholds_no_new_reward_or_paid_learning_permission=True)
 with (R/'H1_GLOBAL_FIRST_VS_PUBLIC4_NORMAL_FIRST_FULL1500_ACTUAL_INITIAL_COMPARISON_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(matched_actual_initial=True,old_b326_events=x['first_episode_before_failed_control_events'],new_mean_final_events=y['first_episode_before_failed_control_events'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_FULL_INITIAL_COMPARISON_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_threshold_change=True),f,indent=2)
  raise
