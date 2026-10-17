"""Describe source-defined recovery events before first failure; never credits reset teleports."""
from pathlib import Path
import json,time,hashlib,sys,os,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np
B=Path(__file__).resolve().parent;R=B/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 proof=json.loads((R/'E3_CLOSED85_1500_ALL_PHYSICAL_PUBLIC03_SOURCE_CPU_ACTUAL.json').read_bytes());assert proof['passed_complete_data_and_source_CPU'] and proof['steps']==1500
 def files(label):
  j=json.loads((R/('E3_CLOSED85_FULL1500_V3_MISSING_ONLY_COMPLETION_BOUND_V2_ACTUAL.json' if label=='FULL1500' else 'E3_CLOSED85_NATIVE120_V3_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json')).read_bytes())
  return lambda name:Path(next(row['local_path'] for row in j['files'] if row.get('local_path') and row['relative'].endswith('/'+name)))
 f=files('FULL1500');n=files('NATIVE120');p=json.loads(f('probe.json').read_bytes());np0=json.loads(n('probe.json').read_bytes());reset=json.loads(f('E3_FRESH104_EXPLICIT_LEGAL_FALL_RESET_ACTUAL.json').read_bytes())
 raw=f('retention_full_control_substep_actual.npz');assert H(raw)==p['native_readonly_witness']['raw']['sha256']
 with np.load(raw,allow_pickle=False) as z:a={k:z[k] for k in z.files}
 for same,original in [('E3_root13','root'),('E3_q30','q'),('E3_executed6','processed_action'),('E3_impulse','impulse'),('E3_history','contact_history'),('E3_closure','closure'),('E3_mimic','mimic')]:assert np.array_equal(a[same],a[original]),(same,original)
 recipe=np.arange(104)%13;assert np.array_equal(recipe,reset['recipe']) and all((recipe==r).sum()==8 for r in range(13));done=a['terminated']|a['truncated'];names=p['native_readonly_witness']['reason_names'];rows=[]
 for i in range(104):
  failed=np.flatnonzero(done[:,i]);last=int(failed[0]) if len(failed) else 1500;good=np.flatnonzero(a['E3_phase_credited'][:last,i]);mode0=np.flatnonzero((a['E3_phase_age'][:last,i]>300)&(a['E3_phase_request'][:last,i]==False))
  row=dict(env_id=i,recipe_id=int(recipe[i]),valid_controls_before_first_failure=last,valid_duration_s=.01*last,first_failure_control=last if last<1500 else None,first_failure_reasons=[name for k,name in enumerate(names) if last<1500 and a['reasons'][last,i,k]],original_source_stable50_credited_before_any_failure=bool(len(good)),source_first_credit_control=int(good[0]) if len(good) else None,actual_first_episode_credited_at_least50controls=bool(len(good)),normal_public_request_after_rescue_window_before_first_failure=bool(len(mode0)),survived_all15s_without_reset=last==1500,post_failure_or_reset_credits_used=False)
  rows.append(row)
 groups=[]
 for rid in range(13):
  rr=[r for r in rows if r['recipe_id']==rid];angle=0 if rid==12 else [-90,-60,-30,30,60,90][rid%6];groups.append(dict(recipe_id=rid,axis='normal' if rid==12 else ('roll' if rid<6 else 'pitch'),declared_degrees=angle,environments=8,original_stable50_credit_valid_prefix_count=sum(r['original_source_stable50_credited_before_any_failure'] for r in rr),whole15s_no_reset_count=sum(r['survived_all15s_without_reset'] for r in rr),normal_window_reached_in_valid_first_episode=sum(r['normal_public_request_after_rescue_window_before_first_failure'] for r in rr),valid_first_duration_min_median_max_s=[float(v) for v in np.percentile([r['valid_duration_s'] for r in rr],[0,50,100])]))
 initial=p['native_readonly_witness']['first_physics_initial'];nativeinitial=np0['native_readonly_witness']['first_physics_initial'];same={k:initial[k]==nativeinitial[k] for k in ('root','q30','physical_parameters')};q=json.loads(f('retention_plane_query_actual.json').read_bytes())['initial'];nq=json.loads(n('retention_plane_query_actual.json').read_bytes())['initial']
 for k in ('actual_USD_and_native_actor_metadata','source_reference'):same['Plane_'+k]=q[k]==nq[k]
 same['loaded_own_PhysX_file_fingerprints']=q['loaded_PhysX_binary_fingerprints']['files']==nq['loaded_PhysX_binary_fingerprints']['files']
 rescues=[r for r in rows if r['recipe_id']!=12];normal=[r for r in rows if r['recipe_id']==12]
 out=dict(epoch=time.time(),source_SHA=proof['source_SHA'],frozen_full1500_complete_data_CPU_passed=True,source_original_stable50_credit_before_any_failure=sum(r['original_source_stable50_credited_before_any_failure'] for r in rescues),fall_environment_count=96,fall_whole15s_without_any_reset=sum(r['survived_all15s_without_reset'] for r in rescues),normal_whole15s_without_any_reset=sum(r['survived_all15s_without_reset'] for r in normal),normal_environment_count=8,groups=groups,all_environment_valid_first_episode_rows=rows,actual_native_full_initial_comparison=same,matched_actual_initial_all_selected_fields_exact=all(same.values()),comparison_descriptive_not_new_statistical_or_causal_claim=True,original_source_reward_event_definition_upright10deg_root_speed003_ang_speed02_50controls=True,first_failure_prefix_excludes_failed_control_and_all_later_reset_samples=True,peak_progress_credit_not_counted_as_recovery_success=True,no_new_skill_gate_or_training_reward_or_threshold=True,no_graduation_or_new_paid_learning_permission_from_this_report=True,ordinary_total=proof['ordinary'],truncations_total=proof['truncations'],original_GPU_geometry_false_and_idealZ0_false_and_missing_EXIT_NATURAL_preserved=True,actual_raw=dict(path=str(raw),bytes=raw.stat().st_size,SHA=H(raw)))
 with (R/'E3_CLOSED85_FULL1500_ORIGINAL_FIRST_EPISODE_RECOVERY_AND_NORMAL_RETENTION_RESIDUAL_CPU_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps({k:v for k,v in out.items() if k not in ('groups','all_environment_valid_first_episode_rows')}),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('E3_FULL_FROZEN_FIRST_EPISODE_BEHAVIOR_CPU_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True),f,indent=2)
  raise
