"""CPU actual G1/retention review, accepting no pending case as passed."""
from pathlib import Path
import ast,hashlib,json,sys,time,traceback
import numpy as np
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
BASE=W/'MOD4_S3_E1_ROUTE_BEHAVIOR_CONTINUATION_20261009/reports/actual_cases'
sys.path.insert(0,str(W/'MOD4_S1A_MATCHED_EVALUATION_20261007/review_contracts'))
from scut_curriculum_gate_v4 import evidence
from world_progress_contract import target
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
old=W/'MOD4_CLOSURE_EPISODE_CONTINUATION_20261008/review_block1_matched_scope.py'
node=next(n for n in ast.parse(old.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='facts')
node.body=[n for n in node.body if not(isinstance(n,ast.Assert) and ast.unparse(n.test)=="e['pass_']")]
import math,statistics
exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),str(old),'exec'))
oldterrain=W/'MOD4_E1_RETENTION_REPAIR_20261009/review_completed_block2_reset_diagnostic.py'
nodes=[n for n in ast.parse(oldterrain.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name in ('recipe_manager','terrain')]
class ProtocolOnly(ast.NodeTransformer):
 def visit_Constant(self,n):
  if n.value=='approved_E1_gentle_route_behavior_v1':n.value='approved_E1_G1_derived10mm_route_behavior_v1'
  return n
nodes=[ProtocolOnly().visit(n) for n in nodes]
hashfile=sha
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),str(oldterrain),'exec'))
def reset_audit(p):
 def rows(a,b,path=''):
  if isinstance(a,dict):
   assert set(a)==set(b)
   for k in a:yield from rows(a[k],b[k],path+'/'+k)
  elif isinstance(a,list):assert len(a)==len(b);yield path,a,b
  else:assert a==b,(path,'non-row metadata differs')
 increments=None
 for name in ('physical_action','spring_pressure','gas_damping','chassis_PD'):
  parts=list(rows(p[name+'_initial_episode_assignments'],p[name+'_final_episode_assignments']))
  for key,a,b in parts:
   if key.endswith('/episode'):
    delta=[y-x for x,y in zip(a,b)];assert all(v>=0 and int(v)==v for v in delta)
    if increments is None:increments=delta
    else:assert increments==delta
  for key,a,b in parts:
   for i,(x,y) in enumerate(zip(a,b)):
    if increments[i]==0:assert x==y,(name,key,i)
    elif key.endswith('/delay_us'):assert y in (0,2500,5000)
 assert increments is not None
 assert sum(increments)==p['resets'] if 'resets' in p else sum(increments)==0
 return dict(changed_rows=[i for i,v in enumerate(increments) if v],episode_increments=increments,unreset_rows_exact=True,original_task_flags_retained=True)
def main():
 v=read(sorted(R.glob('COLLECTED_*.json'))[-1]);b=v['passed'];h=b['health'];assert not b['discarded_preflight']
 assert h['control_steps']==b['actual_updates']*24 and h['actual_physics_callbacks']==h['expected_physics_callbacks']==h['control_steps']*4
 assert h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact'] and not h['nonfinite_observed'] and h['stop_reason'] is None
 assert h['integrity_task_reset_events']==h['unknown_task_reset_events']==0 and len(b['unique_completed_segment'])==1
 terrainrows={};retention={}
 for jid,row in v['cases'].items():
  m,p,r=row['manifest'],row['probe'],row['result'];folder=R/'cases'/jid
  assert r['phase']=='complete' and r['exit_code']==0 and not r['errors'] and not r['error_files'] and not r['new_learning']
  assert r['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256'] and r['checkpoint']['finite_tensors']==96
  assert r['runtime_archive_sha256']==m['artifacts']['runtime']['sha256'] and r['steps']==m['steps']==p['steps']==1500
  assert m['no_learning'] and not m['canonical_write_authority'] and m['physics_dt_s']==.0025 and m['control_dt_s']==.01 and m['solver_position']==32 and m['solver_velocity']==4
  if 'full_route_raw' in p:
   assert r['runtime_archive_sha256']=='ca8a647affeb6ed5c17b5e73b7362141878f9be5dd76db9a9d7b0e6ebad49279'
   role='anchor32053' if '117-' in jid else 'candidate32098'
   terrainrows[role]=dict(job_id=jid,review=terrain(p,folder),probe=p)
  else:
   kind=m['kind'];assert p['seed']==m['seed']==20261002 and m['profile']=='white_v3' and r['runtime_archive_sha256']=='8a964c1d0cfa291ea8faf72d978464daa8b2a8e90834554c435d528ffb222871'
   assert r['checkpoint']['sha256']==b['checkpoint']['sha256']
   baseline=read(BASE/('clk2500-closure-episode-d3-115-e1-retention32053-'+kind)/'probe.json')
   keys=('reset_root_before_physics','reset_joint_pos_before_physics','sensor_recipe','feedback_delay_recipe','physical_action_delay_recipe','spring_pressure_recipe','gas_damping_recipe','chassis_PD_recipe','physical_action_initial_episode_assignments','spring_pressure_initial_episode_assignments','gas_damping_initial_episode_assignments','chassis_PD_initial_episode_assignments')
   assert all(p[k]==baseline[k] for k in keys)
   params=lambda x:x.get('initial_parameter_audit') or x.get('mild_initial_parameters');assert params(p)==params(baseline)
   if 'probe_sha256' in baseline:assert p['probe_sha256']==baseline['probe_sha256']
   audit=p['physical_action_delay_audit'];assert audit['callback_counts']==dict(legs=6000,wheels=6000) and audit['application_formula_max_error']==0
   assert p['spring_pressure_audit']['actual_PhysX_buffer_implicit_model_exact'] and p['gas_damping_audit']['actual_PhysX_buffer_implicit_model_exact'] and p['chassis_PD_audit']['parameter_auditor']['actual_parameters_pass']
   resets=reset_audit(p);age=p['sensor_actual_manager_audit']['actual_feedback_sample_apply']==baseline['sensor_actual_manager_audit']['actual_feedback_sample_apply']
   if not age:assert p.get('resets',0)>0
   retention[kind]=dict(candidate=facts(p,kind),rollback32053=facts(baseline,kind),paired_initial_root30q_parameters_recipes_assignments_exact=True,reset_audit=resets,final_feedback_age_pair_exact=age)
 paired=False
 if set(terrainrows)=={'anchor32053','candidate32098'}:
  a,p=terrainrows['anchor32053']['probe'],terrainrows['candidate32098']['probe']
  for k in ('initial','geometry','geometry_recipe','sensor_recipe','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe'):assert a[k]==p[k],k
  paired=True
 for x in terrainrows.values():x.pop('probe')
 compact=lambda x:{k:x[k] for k in ('straight','pure4pi','passed','count','max_abs_cross','along_range','closure_mm','original_flags') if k in x}
 summary=dict(retention={k:{role:compact(x[role]) for role in ('rollback32053','candidate')} for k,x in retention.items()},terrain={k:{'groups':[{a:c for a,c in g.items() if not a.startswith('per_env') and a!='env_ids'} for g in x['review']['groups']],'ordinary':x['review']['ordinary'],'truncations':x['review']['unique_truncations']} for k,x in terrainrows.items()})
 report=dict(epoch=time.time(),trial_id='E1-G1-ACTUAL-REVIEW-20261010',collection_path=str(sorted(R.glob('COLLECTED_*.json'))[-1]),own=b,terrain=terrainrows,terrain_pair_exact=paired,retention=retention,summary=summary,pending=v['pending'],review_complete=paired and set(retention)=={'flat','spin','world'},original_task_flags_and_residuals_preserved=True,no_RM_or_E1_graduation_claim=True,full_wave_traversal_not_yet_proved=True,new_budget_seconds=0,no_GPU_PPO_queue_or_canonical_write=True,reused_CPU_contract_sources={str(old):sha(old),str(oldterrain):sha(oldterrain)},reader_only_protocol_changed=True)
 path=R/('REVIEW_'+str(int(report['epoch']))+'.json');assert not path.exists();path.write_text(json.dumps(report,indent=2),encoding='utf8')
 print(json.dumps(dict(report=str(path),summary=summary,pending=v['pending'],review_complete=report['review_complete']),ensure_ascii=True))
if __name__=='__main__':
 try:main()
 except Exception:
  path=R/('REVIEW_ERROR_'+str(int(time.time()))+'.json');path.write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G1-CPU-REVIEW-02-OPTIONAL-RESET-FIELD',error=traceback.format_exc(),reader_only_no_production_change=True),indent=2),encoding='utf8');raise
