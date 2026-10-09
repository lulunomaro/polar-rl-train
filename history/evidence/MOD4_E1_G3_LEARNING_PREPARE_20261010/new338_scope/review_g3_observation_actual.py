"""Review complete123 actual candidate routes and inherited skills; no GPU or publication."""
from pathlib import Path
import sys,json,time,traceback,hashlib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';read=lambda p:json.loads(p.read_bytes())
sys.path.insert(0,str(W/'MOD4_E1_G1_ACTUAL_REVIEW_20261010'))
import review_actual_schema_checked as common
sys.path.insert(0,str(W/'MOD4_E1_G3_35MM_SCOPE_PREPARE_20261010'))
from review35mm126_actual import audit
def main():
 v=read(sorted(R.glob('CANDIDATE_127_COLLECTED_*.json'))[-1]);b=v['passed'];assert b and not b['discarded_preflight'] and len(b['unique_completed_segment'])==1
 h=b['health'];assert h['control_steps']==b['actual_updates']*24 and h['actual_physics_callbacks']==h['expected_physics_callbacks']==h['control_steps']*4
 assert h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact'] and not h['nonfinite_observed'] and h['stop_reason'] is None
 assert h['integrity_task_reset_events']==h['unknown_task_reset_events']==0
 rows={};retention={};terrain=None
 for jid,row in v['cases'].items():
  p,m,r=row['probe'],row['manifest'],row['result'];assert r['phase']=='complete' and not r['exit_code'] and not r['errors'] and not r['error_files'] and not r['new_learning']
  assert r['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==b['checkpoint']['sha256'] and r['checkpoint']['finite_tensors']==96
  assert r['runtime_archive_sha256']==m['artifacts']['runtime']['sha256'] and r['steps']==m['steps']==p['steps']==1500 and m['no_learning'] and not m['canonical_write_authority']
  assert m['physics_dt_s']==.0025 and m['control_dt_s']==.01 and m['solver_position']==32 and m['solver_velocity']==4
  if 'full_route_raw' in p:
   assert r['runtime_archive_sha256']=='ccf288b3f32c0d028d8e1cb555d64e98af5267be27fcf4157a3750b8bdfeeebc' and row['raw_SHA_exact']
   terrain=audit(p,R/'cases'/jid)
   anchor=read(W/'MOD4_E1_G3_35MM_SCOPE_PREPARE_20261010/reports/cases/clk2500-closure-episode-d3-126-e1-g3-35mm-source32058-manifest-reviewed-fullroute-flat/probe.json')
   for k in ('initial','geometry','geometry_recipe','route_scope','sensor_recipe','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names'):assert p[k]==anchor[k],k
  else:
   kind=m['kind'];assert p['seed']==m['seed']==20261002 and m['profile']=='white_v3' and r['runtime_archive_sha256']=='8a964c1d0cfa291ea8faf72d978464daa8b2a8e90834554c435d528ffb222871'
   baseline=read(common.BASE/('clk2500-closure-episode-d3-115-e1-retention32053-'+kind)/'probe.json')
   keys=('reset_root_before_physics','reset_joint_pos_before_physics','sensor_recipe','feedback_delay_recipe','physical_action_delay_recipe','spring_pressure_recipe','gas_damping_recipe','chassis_PD_recipe','physical_action_initial_episode_assignments','spring_pressure_initial_episode_assignments','gas_damping_initial_episode_assignments','chassis_PD_initial_episode_assignments')
   assert all(p[k]==baseline[k] for k in keys)
   params=lambda x:x.get('initial_parameter_audit') or x.get('mild_initial_parameters');assert params(p)==params(baseline)
   if 'probe_sha256' in baseline:assert p['probe_sha256']==baseline['probe_sha256']
   a=p['physical_action_delay_audit'];assert a['callback_counts']==dict(legs=6000,wheels=6000) and a['application_formula_max_error']==0
   assert p['spring_pressure_audit']['actual_PhysX_buffer_implicit_model_exact'] and p['gas_damping_audit']['actual_PhysX_buffer_implicit_model_exact'] and p['chassis_PD_audit']['parameter_auditor']['actual_parameters_pass']
   resets=common.reset_audit(p);age=p['sensor_actual_manager_audit']['actual_feedback_sample_apply']==baseline['sensor_actual_manager_audit']['actual_feedback_sample_apply']
   if not age:assert p.get('resets',0)>0
   retention[kind]=dict(candidate=common.facts(p,kind),baseline32053=common.facts(baseline,kind),initial30q_parameters_recipes_assignments_pair_exact=True,reset_audit=resets,feedback_age_pair_exact=age)
 compact=lambda x:{k:x[k] for k in ('straight','pure4pi','passed','count','max_abs_cross','along_range','closure_mm','original_flags') if k in x}
 summary=dict(terrain=terrain['groups'] if terrain else None,retention={kind:{role:compact(x[role]) for role in ('baseline32053','candidate')} for kind,x in retention.items()})
 report=dict(epoch=time.time(),trial_id='E1-G3-300S-CANDIDATE-ACTUAL-REVIEW-01',collection=str(sorted(R.glob('CANDIDATE_127_COLLECTED_*.json'))[-1]),own=b,terrain=terrain,retention=retention,summary=summary,pending=v['pending'],review_complete=terrain is not None and set(retention)=={'flat','spin','world'} and not v['pending'],reviewed_cases_have_matched_initial_conditions=True,original_flags_failures_and_residuals_preserved=True,no_RM70mm_or_all_E1_graduation=True,no_permanent_anti_forgetting_proof=True,requires_actual_retention_decision_before_more_PPO=True,no_GPU_PPO_queue_or_canonical_write=True,new_budget_seconds=0)
 out=R/('CANDIDATE_127_REVIEW_'+str(int(report['epoch']))+'.json');assert not out.exists();out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),summary=summary,pending=v['pending'],review_complete=report['review_complete']),ensure_ascii=True))
if __name__=='__main__':
 try:main()
 except Exception:
  out=R/('CANDIDATE_127_REVIEW_ERROR_'+str(int(time.time()))+'.json');assert not out.exists();out.write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G3-300S-CANDIDATE-CPU-READER-01',error=traceback.format_exc(),original_source_and_error_retained=True,no_production_change=True),indent=2),encoding='utf8');raise
