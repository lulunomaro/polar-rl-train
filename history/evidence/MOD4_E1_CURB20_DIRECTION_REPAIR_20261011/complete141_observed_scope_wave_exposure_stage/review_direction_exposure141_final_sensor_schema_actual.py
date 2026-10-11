"""Independent full CURB/contact + three signed skills, paired with132/115/129."""
from pathlib import Path
import sys
D=Path(__file__).resolve().parent;R=D/'reports'
from direction_io import *
sys.path.insert(0,str(D.parent/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011'))
from pathlib import Path
import sys,json,time,traceback
sys.path.insert(0,str(D.parent/'MOD4_E1_G1_ACTUAL_REVIEW_20261010'))
import review_actual_schema_checked as common
from review_curb132_actual import audit
read=lambda p:json.loads(p.read_bytes())

def final_sensor_receipt_pair(candidate,reference):
 a=candidate['sensor_recipe'];b=reference['sensor_recipe'];dynamic='max_abs_actual_bias_rad'
 assert set(a)==set(b) and all(a[k]==b[k] for k in a if k!=dynamic)
 assert a['episode_leg_encoder_bias_bound_rad']==b['episode_leg_encoder_bias_bound_rad']==.0075
 assert a['bias_finite'] and b['bias_finite'] and 0<=a[dynamic]<=.0075 and 0<=b[dynamic]<=.0075
 assert candidate['sensor_manager']['tick']==reference['sensor_manager']['tick']==1500
 return dict(static_sensor_configuration_and_noise_draw_counts_exact=True,final_observation_key=dynamic,
  candidate_final_bias_max=a[dynamic],reference_final_bias_max=b[dynamic],final_bias_observation_exact=a[dynamic]==b[dynamic],
  actual_bias_resampled_on_physical_episode_reset_as_original_source=True,not_an_initial_recipe_parameter=True,
  initial_sensor_bias_vectors_not_raw_captured_no_new_exact_claim=True,original_bias_bound_and_finite_checks_unchanged=True)
def main():
 collection=sorted(R.glob('CURB141_COLLECTED_[0-9]*.json'))[-1];v=read(collection);b=v['passed'];assert b and not b['discarded_preflight'] and len(b['unique_completed_segment'])==1
 ownCPU=read(sorted(R.glob('EXPOSURE_MATCHED_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'))[-1]);assert ownCPU['passed'] and ownCPU['own_checkpoint']['sha256']==b['checkpoint']['sha256'] and ownCPU['actual_source_count']==424
 h=b['health'];assert h['control_steps']==24*b['actual_updates'] and h['actual_physics_callbacks']==h['expected_physics_callbacks']==4*h['control_steps']
 assert h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact'] and not h['nonfinite_observed'] and h['stop_reason'] is None
 assert h['integrity_task_reset_events']==h['unknown_task_reset_events']==0
 terrain=None;retention={};source_root=D.parent/'MOD4_E1_G3_COMMAND_RETENTION_PREPARE_20261010/reports/cases'
 for jid,row in v['cases'].items():
  p,m,r=row['probe'],row['manifest'],row['result'];assert r['phase']=='complete' and not r['exit_code'] and not r['errors'] and not r['error_files'] and not r['new_learning']
  assert r['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==b['checkpoint']['sha256']
  if 'full_route_raw' in p:assert p['checkpoint_sha256']==b['checkpoint']['sha256']
  else:assert p['checkpoint'].replace('\\','/').lower()==('D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs/'+jid+'/checkpoint.bin').lower()
  assert r['checkpoint']['finite_tensors']==b['checkpoint']['finite_tensors']==ownCPU['actual_finite_tensor_count'] and r['runtime_archive_sha256']==m['artifacts']['runtime']['sha256']
  assert r['steps']==m['steps']==p['steps']==1500 and m['no_learning'] and not m['canonical_write_authority']
  if 'full_route_raw' in p:
   assert r['runtime_archive_sha256']=='b91238eddc550555a70f2a09e4cf8ff085d66fad1cb00bcb5736da6a71b04e7d' and row['raw_SHA_exact']
   terrain=audit(p,R/'cases'/jid)
   anchor=read(D.parent/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011/reports/cases/clk2500-closure-episode-d3-132-e1-curb20-source364-mirrored-fullroute-flat/probe.json')
   for k in ('initial','geometry','geometry_recipe','route_scope','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names'):assert p[k]==anchor[k],k
   selected140=read(R/'cases/clk2500-closure-episode-d3-140-e1-curb20-direction-repair-terrain-flat/probe.json')
   for k in ('initial','geometry','geometry_recipe','route_scope','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names'):assert p[k]==selected140[k],k
   terrain['sensor_receipt_source132']=final_sensor_receipt_pair(p,anchor)
   terrain['sensor_receipt_selected140']=final_sensor_receipt_pair(p,selected140)
   terrain['selected_source140_complete_review']=str(R/'CURB140_SCHEMA_REVIEW_1791718216726562600.json')
  else:
   kind=m['kind'];assert p['seed']==m['seed']==20261002 and m['profile']=='white_v3' and r['runtime_archive_sha256']=='8a964c1d0cfa291ea8faf72d978464daa8b2a8e90834554c435d528ffb222871'
   baseline=read(common.BASE/('clk2500-closure-episode-d3-115-e1-retention32053-'+kind)/'probe.json')
   source=read(source_root/('clk2500-closure-episode-d3-129-e1-g3-command-retention-retention-'+kind)/'probe.json')
   keys=('reset_root_before_physics','reset_joint_pos_before_physics','sensor_recipe','feedback_delay_recipe','physical_action_delay_recipe','spring_pressure_recipe','gas_damping_recipe','chassis_PD_recipe','physical_action_initial_episode_assignments','spring_pressure_initial_episode_assignments','gas_damping_initial_episode_assignments','chassis_PD_initial_episode_assignments')
   assert all(p[k]==baseline[k]==source[k] for k in keys)
   params=lambda x:x.get('initial_parameter_audit') or x.get('mild_initial_parameters');assert params(p)==params(baseline)==params(source)
   if 'probe_sha256' in baseline:assert p['probe_sha256']==baseline['probe_sha256']==source['probe_sha256']
   a=p['physical_action_delay_audit'];assert a['callback_counts']==dict(legs=6000,wheels=6000) and a['application_formula_max_error']==0
   assert p['spring_pressure_audit']['actual_PhysX_buffer_implicit_model_exact'] and p['gas_damping_audit']['actual_PhysX_buffer_implicit_model_exact'] and p['chassis_PD_audit']['parameter_auditor']['actual_parameters_pass']
   resets=common.reset_audit(p)
   age=p['sensor_actual_manager_audit']['actual_feedback_sample_apply']==baseline['sensor_actual_manager_audit']['actual_feedback_sample_apply']
   if not age:assert p.get('resets',0)>0
   retention[kind]=dict(candidate=common.facts(p,kind),source364=common.facts(source,kind),baseline32053=common.facts(baseline,kind),initial30q_parameters_recipes_assignments_pair_exact=True,reset_audit=resets,feedback_age_pair_exact=age)
   selected140=read(R/'cases'/('clk2500-closure-episode-d3-140-e1-curb20-direction-repair-retention-'+kind)/'probe.json')
   assert all(p[k]==selected140[k] for k in keys) and params(p)==params(selected140)
   retention[kind]['source423']=common.facts(selected140,kind)
 compact=lambda x:{k:x[k] for k in ('straight','pure4pi','passed','count','max_abs_cross','along_range','closure_mm','original_flags') if k in x}
 summary=dict(terrain=terrain['groups'] if terrain else None,retention={k:{role:compact(x[role]) for role in ('source364','source423','candidate','baseline32053')} for k,x in retention.items()})
 result=dict(epoch=time.time(),trial_id='CURB141-COMPLETE-INDEPENDENT-ACTUAL-REVIEW-01',collection=str(collection),own=b,terrain=terrain,retention=retention,summary=summary,pending=v['pending'],review_complete=terrain is not None and set(retention)=={'flat','spin','world'} and not v['pending'],all_valid_incomplete_prefixes_and_original_flags_preserved=True,standing_not_required_to_cross=True,no_gate_or_RM002_or_full_E1_graduation=True,no_permanent_anti_forgetting_proof=True,requires_complete_scope_decision_before_more_PPO=True,no_GPU_PPO_queue_or_budget_write=True)
 p=save('CURB141_SCHEMA_REVIEW_'+str(time.time_ns())+'.json',result);print(json.dumps(dict(report=str(p),summary=summary,pending=v['pending'],review_complete=result['review_complete']),ensure_ascii=True))
if __name__=='__main__':
 try:main()
 except BaseException:save('CURB141_SCHEMA_REVIEW_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),reader_only=True,original_source_results_not_relabelled=True));raise
