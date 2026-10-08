"""Read real D5 closedloop cases and retain original world/legacy facts."""
from pathlib import Path
import json,hashlib,time,ast,sys,math,statistics
D=Path(__file__).resolve().parent;R=D/'reports';read=lambda p:json.loads(p.read_text(encoding='utf8'))
sys.path.insert(0,str(D.parent/'MOD4_S1A_MATCHED_EVALUATION_20261007/review_contracts'))
from scut_curriculum_gate_v4 import evidence
from world_progress_contract import target
original=D.parent/'MOD4_CLOSURE_EPISODE_CONTINUATION_20261008/review_block1_matched_scope.py'
tree=ast.parse(original.read_text(encoding='utf8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='facts'],type_ignores=[]),str(original),'exec'))
index=read(R/'D5_COMPLETED_SCOPE_FILES.json');jobs={r['id']:r for r in index['jobs']};prefix='clk2500-closure-episode-d3-'
archive='fe8dc6bcb027215739a9edf7a8b5fa46240326b402e05ae0d0463db87044452c'
actual=read(R/'D5_CURRENT_ACTUAL.json');source=actual['state']['source']['sha256'];out={}
for label in ['70-d5-anchor']+[f'75-d5-b{i}' for i in (1,2,3)]:
 cases={}
 for kind in ('flat','spin','world'):
  job=prefix+label+'-'+kind
  if job not in jobs:continue
  folder=R/'windows'/job;p,m,res=[read(folder/n) for n in ('probe.json','manifest.json','result.json')]
  assert res['exit_code']==0 and not res['errors'] and not res['error_files']
  assert res['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']
  if label=='70-d5-anchor':assert res['checkpoint']['sha256']==source
  assert res['runtime_archive_sha256']==m['artifacts']['runtime']['sha256']==archive
  assert p['steps']==m['steps']==res['steps']==1500 and p['seed']==m['seed']==20261002
  assert m['profile']=='white_v3' and m['num_envs']==(80 if kind=='flat' else 88)
  assert m['physics_dt_s']==.0025 and m['solver_position']==32 and m['solver_velocity']==4
  assert m['no_learning'] and not m['canonical_write_authority']
  for n,row in jobs[job]['files'].items():
   assert hashlib.sha256((folder/n).read_bytes()).hexdigest()==row['sha256']
   if n in ('probe.json','result.json'):assert row['automatic_bridge_return_bytes_exact']
  assert p['D5_closed_loop_stiffness_engineering_pressure'] and p['D4_closed_loop_actual_physical_target_delay']
  pressure=p['spring_pressure_audit'];recipe=p['spring_pressure_recipe'];assign=p['spring_pressure_initial_episode_assignments']
  assert recipe['profile']==pressure['profile']=='gas_stiffness_independent_episode_090_110_v1'
  assert pressure['actual_PhysX_buffer_implicit_model_exact'] and pressure['preload_damping_force_limit_armature_unchanged']
  assert not pressure['hardware_force_stroke_calibration'] and not pressure['actual_drive_or_constraint_force_measured']
  assert assign==p['spring_pressure_final_episode_assignments']
  assert all(.9<=x<=1.1 for row in assign['factor'] for x in row)
  assert len(assign['factor'])==m['num_envs'] and all(len(row)==2 for row in assign['factor'])
  assert all(abs(k-3500*f)<.001 for kr,fr in zip(assign['actual_stiffness_N_m'],assign['factor']) for k,f in zip(kr,fr))
  action=p['physical_action_delay_audit'];assert action['callback_counts']=={'legs':6000,'wheels':6000} and action['application_formula_max_error']==0
  assert p['physical_action_initial_episode_assignments']==p['physical_action_final_episode_assignments']
  f=facts(p,kind);assert f['v4']['pass_'],f['v4']
  cases[kind]=dict(facts=f,pressure_audit=pressure,result=res,source_SHA=res['checkpoint']['sha256'],
   identity=dict(root=p['reset_root_before_physics'],q=p['reset_joint_pos_before_physics'],parameters=p.get('initial_parameter_audit') or p['mild_initial_parameters'],
   sensor_recipe=p['sensor_recipe'],feedback_recipe=p['feedback_delay_recipe'],action_recipe=p['physical_action_delay_recipe'],spring_recipe=recipe,
   spring_assignment=assign,action_assignment=p['physical_action_initial_episode_assignments'],feedback_age=p['sensor_actual_manager_audit']['actual_feedback_sample_apply']))
 if cases:out[label]=cases
base=out.get('70-d5-anchor',{});assert len(base)==3,'Actual D5 baseline all three must finish'
pairs=[]
for label,cases in out.items():
 if label=='70-d5-anchor':continue
 for kind,c in cases.items():assert c['identity']==base[kind]['identity'];pairs.append(dict(label=label,kind=kind,initial_conditions_parameter_recipes_assignments_exact=True))
v=dict(epoch=time.time(),scope='Same3060/seed20261002/white_v3/A0/D0-D5/flat80-spin88-world88 each15s,actual spring and action delay closedloop',
 baseline_scope_accepted=True,cases=out,pairs=pairs,bridge_files=index,hardware_force_stroke_calibration=False,
 dualseed_allprofile_graduation=False,all_raw_and_old_flags_retained=True,D5_learned_candidates_pending=not any(k!='70-d5-anchor' and len(c)==3 for k,c in out.items()))
(R/'D5_ACTUAL_BASELINE_SCOPE_REVIEW.json').write_text(json.dumps(v,indent=2),encoding='utf8')
print(json.dumps({label:{k:({n:c['facts'][n] for n in ('passed','count','max_abs_cross','along_range')} if k=='world' else c['facts'].get('straight') or c['facts'].get('pure4pi')) for k,c in cases.items()} for label,cases in out.items()}))
