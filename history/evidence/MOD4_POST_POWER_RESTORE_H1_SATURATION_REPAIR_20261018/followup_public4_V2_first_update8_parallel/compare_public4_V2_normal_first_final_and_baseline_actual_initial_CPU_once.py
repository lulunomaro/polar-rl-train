"""Descriptive same-initial checks, not unique-cause or statistical proof."""
from pathlib import Path
import json,time
B=Path(__file__).resolve().parent;R=B/'reports';X=B.parent/'MOD4_H1_FROZEN_FE1709_REVIEW_20261018/reports'

def case(root,collection,cpu,factors):
 j=json.loads((root/collection).read_bytes());c=json.loads((root/cpu).read_bytes());f=json.loads((root/factors).read_bytes());assert c['passed_complete_data_and_source_CPU']
 def read(name):return json.loads(Path(next(r['local_path'] for r in j['files'] if r['relative'].endswith('/'+name))).read_bytes())
 return dict(cpu=c,factors=f,initial=read('probe.json')['native_readonly_witness']['first_physics_initial'],query_initial=read('retention_plane_query_actual.json')['initial'])

def main():
 a=case(X,'LINUX_GPU1_B326_FULL1500_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json','H1_B326_LINUX72_1500_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_ACTUAL.json','H1_B326_FULL1500_ORIGINAL_VALID_PREFIX_PHASE_FACTORS_CPU_ACTUAL.json')
 cases={
 'normal_only_first':case(R,'LINUX_GPU1_PUBLIC4N1_FULL1500_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json','H1_PUBLIC4N1_LINUX72_1500_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_ACTUAL.json','H1_PUBLIC4N1_FULL1500_ORIGINAL_VALID_PREFIX_PHASE_FACTORS_CPU_ACTUAL.json'),
 'public4_finite_final':case(R,'LINUX_GPU1_PUBLIC4FINAL_FULL1500_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json','H1_PUBLIC4FINAL_LINUX72_1500_ALL_PHYSICAL_PUBLIC04_SOURCE_FP64_REFERENCE_CPU_V3_ACTUAL.json','H1_PUBLIC4FINAL_FULL1500_ORIGINAL_VALID_PREFIX_PHASE_FACTORS_CPU_ACTUAL.json'),
 }
 out={}
 for name,b in cases.items():
  exact={k:a['initial'][k]==b['initial'][k] for k in ('root','q30','physical_parameters')}
  refs={k:a['query_initial'][k]==b['query_initial'][k] for k in ('actual_USD_and_native_actor_metadata','source_reference')}
  refs['loaded_own_PhysX_files']=a['query_initial']['loaded_PhysX_binary_fingerprints']['files']==b['query_initial']['loaded_PhysX_binary_fingerprints']['files']
  out[name]=dict(source_SHA=b['cpu']['source_SHA'],events=b['cpu']['first_episode_before_failed_control_events'],ordinary=b['cpu']['ordinary'],truncations=b['cpu']['truncations'],ready_before_first_public4=b['factors']['ready_at_last_normal_control_before_first_mode4'],actual_initial_fields_exact=exact,actual_source_and_loaded_binary_fields_exact=refs,same_selected_actual_initial=all(exact.values()) and all(refs.values()))
 result=dict(epoch=time.time(),baseline_source_SHA=a['cpu']['source_SHA'],baseline_ready_before_first_public4=a['factors']['ready_at_last_normal_control_before_first_mode4'],baseline_events=a['cpu']['first_episode_before_failed_control_events'],cases=out,normal_first_aux0_not_auxiliary_effectiveness=True,whole_training_paths_not_counterfactual_matched=True,descriptive_only_not_unique_cause_or_statistical_significance=True,original_gates_and_all_false_preserved=True,no_new_paid_window_permission=True)
 with (R/'PUBLIC4_V2_BASELINE_NORMAL_FIRST_COMPLETE_FINAL_MATCHED_INITIAL_COMPARISON_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
 print(json.dumps(result))

if __name__=='__main__':main()
