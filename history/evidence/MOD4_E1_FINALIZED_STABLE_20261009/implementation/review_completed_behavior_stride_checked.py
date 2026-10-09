"""Independent actual raw/parameter/route and inherited-skill review; no dispatch."""
from pathlib import Path
import json,sys,ast,time,hashlib,math,statistics
import numpy as np
D=Path(__file__).resolve().parent;R=D/'reports';B=D.parent;read=lambda p:json.loads(p.read_text(encoding='utf8'))
sys.path.insert(0,str(B/'MOD4_S1A_MATCHED_EVALUATION_20261007/review_contracts'))
from scut_curriculum_gate_v4 import evidence
from world_progress_contract import target
original=B/'MOD4_CLOSURE_EPISODE_CONTINUATION_20261008/review_block1_matched_scope.py'
tree=ast.parse(original.read_text(encoding='utf8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='facts'],type_ignores=[]),str(original),'exec'))
v=read(R/'E1_PLANNED_BEHAVIOR_CURRENT_ACTUAL.json');pub=read(R/'E1_PLANNED_BEHAVIOR_PUBLISHED.json');rows=v['rows']
assert all(r.get('result') and r['result']['phase']=='complete' for r in rows.values()),'Pending actual cases; do not write acceptance'
assert not v['evaluator_receipts']['ATTENTION']
terrain={};retention={}
for job,row in rows.items():
 m=row['manifest'];r=row['result'];p=row['probe'];kind=m['kind']
 assert r['exit_code']==0 and not r['errors'] and not r['error_files'] and r['new_learning'] is False
 assert r['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256'] and r['runtime_archive_sha256']==m['artifacts']['runtime']['sha256']
 assert r['steps']==m['steps']==p['steps']==1500 and m['physics_dt_s']==.0025 and m['solver_position']==32 and m['solver_velocity']==4
 if m['actual_behavior_scope'].startswith('gentle terrain'):
  assert p['protocol']=='approved_E1_gentle_route_behavior_v1' and p['not_user_paused93_94'] and not p['new_learning'] and p['optimizer_updates']==0
  assert r['checkpoint']['sha256']==p['checkpoint_sha256'] and p['seed']==m['seed']==20260928 and p['num_envs']==80
  assert p['reason_coverage_exact'] and not p['nonfinite'] and p['max_mimic_rad']<=.01 and p['independent_ground_max_error_m']<=1e-6 and p['height_reward_formula_max_error']<=1e-6
  assert p['actual_physical_callbacks']==6000 and p['actual_action_callbacks']==dict(legs=6000,wheels=6000) and p['physical_action_audit']['application_formula_max_error']==0
  assert p['initial']['parameters']['parameter_auditor']['actual_parameters_pass'] and p['final']['parameters']['parameter_auditor']['actual_parameters_pass']
  assert p['independent_control_mean_load_max_error_N']<=.1 and row['raw_SHA_exact']
  file=R/'actual_cases'/job/p['full_route_raw']['name'];assert hashlib.sha256(file.read_bytes()).hexdigest()==p['full_route_raw']['sha256']
  a=np.load(file);assert a['root'].shape==(1500,80,13) and a['q'].shape==(1500,80,30) and a['physical_wheel_force_N'].shape==(6000,80,2,3)
  assert all(np.isfinite(a[k]).all() for k in a.files)
  masks=a['reasons'];names=p['reason_names'];counts={n:int(masks[...,i].sum()) for i,n in enumerate(names)};assert counts==p['termination_counts']
  assert int(a['terminated'].sum())==p['actual_union_ordinary'] and int(a['truncated'].sum())==p['actual_union_truncation']
  assert all(counts.get(n,0)==0 for n in ('mimic',))
  assert np.array_equal(a['episode'][1:]-a['episode'][:-1],(a['terminated']|a['truncated'])[:-1].astype(np.int64))
  forces=a['physical_wheel_force_N'].reshape(1500,4,80,2,3)
  independent=np.maximum(forces[...,2],0).sum(1)*.0025
  err=float(abs(independent-a['impulse']).max())/.01;assert err<=.1 and abs(err-p['independent_control_mean_load_max_error_N'])<=1e-6
  quat=a['before_root'][:,:,3:7];heading=np.arctan2(2*(quat[:,:,3]*quat[:,:,2]+quat[:,:,0]*quat[:,:,1]),1-2*(quat[:,:,1]**2+quat[:,:,2]**2))
  delta=a['root'][:,:,:2]-a['before_root'][:,:,:2];along=delta[:,:,0]*np.cos(heading)+delta[:,:,1]*np.sin(heading)
  fail=np.where(a['terminated'],np.arange(1500)[:,None],1500).min(0)
  for group in p['groups']:
   ids=np.zeros(80,dtype=bool);ids[group['env_ids']]=True;valid=(np.arange(1500)[:,None]<fail[None,:])[:,ids];speed=along[:,ids]/.01
   per=np.where(valid,speed,0).sum(0)/valid.sum(0).clip(1)
   assert np.allclose(per,group['per_env_valid_prefix_along_m_s'],rtol=0,atol=1e-7)
   assert abs(float(along[:,ids].sum())-group['total_signed_along_m'])<=1e-4
   assert np.allclose(a['command'][:,ids,0],group['command_vx_m_s']) and (a['command'][:,ids,1:]==0).all()
  assert p['geometry']['all_faces_and_winding_retained'] and not p['geometry']['geometry_simplified']
  terrain['anchor' if '-anchor-' in job else 'candidate']=dict(job=job,probe=p,raw_sha256=p['full_route_raw']['sha256'],actual_raw_reviewed=True)
 else:
  assert m['seed']==20261002 and r['checkpoint']['finite_tensors']==96 and m['artifacts']['runtime']['sha256']=='8a964c1d0cfa291ea8faf72d978464daa8b2a8e90834554c435d528ffb222871'
  f=facts(p,kind)
  oldfolder=B/'MOD4_D7_FULL_CONTRACT_20261009/reports/stage_scope'/pub['reused_old_skill_baseline'][kind]['job_id'];baseline=read(oldfolder/'probe.json')
  assert hashlib.sha256((oldfolder/'probe.json').read_bytes()).hexdigest()==pub['reused_old_skill_baseline'][kind]['probe_sha256']
  for key in ('reset_root_before_physics','reset_joint_pos_before_physics','sensor_recipe','feedback_delay_recipe','physical_action_delay_recipe','spring_pressure_recipe','gas_damping_recipe','chassis_PD_recipe','physical_action_initial_episode_assignments','spring_pressure_initial_episode_assignments','gas_damping_initial_episode_assignments','chassis_PD_initial_episode_assignments'):
   assert p[key]==baseline[key],(kind,key)
  params=lambda x:x.get('initial_parameter_audit') or x.get('mild_initial_parameters')
  assert params(p)==params(baseline)
  for key in ('physical_action','spring_pressure','gas_damping','chassis_PD'):
   assert p[key+'_initial_episode_assignments']==p[key+'_final_episode_assignments']
  assert p['chassis_PD_audit']['parameter_auditor']['actual_parameters_pass']
  retention[kind]=dict(job=job,facts=f,baseline_facts=facts(baseline,kind),paired_initial_root_q_parameters_recipes_assignments_exact=True)
assert len(terrain)==2 and len(retention)==3
b=terrain['anchor']['probe'];n=terrain['candidate']['probe'];assert b['initial']==n['initial'] and b['geometry']==n['geometry'] and b['geometry_recipe']==n['geometry_recipe']
for key in ('sensor_recipe','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe'):
 # Recipe draw counters are identical only when reset counts agree; bounds/profile
 # are paired in actual initial assignments, while all later draws are retained.
 if key!='sensor_recipe':assert b[key]==n[key],key
summary=dict(terrain={k:dict(groups=x['probe']['groups'],termination_counts=x['probe']['termination_counts'],max_closure_mm=x['probe']['max_closure_m']*1000,raw_sha256=x['raw_sha256']) for k,x in terrain.items()},
 retention={k:dict(candidate={n:x['facts'].get(n) for n in ('straight','pure4pi','passed','count','max_abs_cross','along_range')},baseline={n:x['baseline_facts'].get(n) for n in ('straight','pure4pi','passed','count','max_abs_cross','along_range')}) for k,x in retention.items()})
report=dict(epoch=time.time(),source_sha256=pub['source']['sha256'],actual_five_cases_review_complete=True,task_model_data_scope_accepted=True,summary=summary,terrain=terrain,retention=retention,
 no_new_performance_graduation_percentage=True,old_strict_raw_and_ordinary_events_preserved=True,not_all_E1_or_RM_or_hardware_graduation=True,cross_GPU_dynamic_bitexact=False,
 no_GPU_or_canonical_write=True,new_budget_seconds=0)
(R/'E1_PLANNED_BEHAVIOR_STRIDE_CHECKED_REVIEW.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(summary))
