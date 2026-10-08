"""Review actual immutable D6 inference, not checkpoint maturity or hardware tolerance."""
from pathlib import Path
import json,sys,ast,time,hashlib,math,statistics
D=Path(__file__).resolve().parent;R=D/'reports';read=lambda p:json.loads(p.read_text(encoding='utf8'))
sys.path.insert(0,str(D.parent/'MOD4_S1A_MATCHED_EVALUATION_20261007/review_contracts'))
from scut_curriculum_gate_v4 import evidence
from world_progress_contract import target
original=D.parent/'MOD4_CLOSURE_EPISODE_CONTINUATION_20261008/review_block1_matched_scope.py'
tree=ast.parse(original.read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='facts'],type_ignores=[]),str(original),'exec'))
index=read(R/'STAGE_EVALUATOR_CURRENT_ACTUAL.json');jobs={j['id']:j for j in index['jobs']};prefix='clk2500-closure-episode-d3-'
archive='0f51e024c9f5c2cc7448b814203e2f21c810618fb246138c7cdcab92a5dbb3c7'
out={}
for label in ['85-d6-gas-anchor']+[f'86-d6-gas-b{i}' for i in (1,2,3)]:
 cases={}
 for kind in ('flat','spin','world'):
  job=prefix+label+'-'+kind
  if job not in jobs:continue
  row=jobs[job];folder=R/'stage_scope'/job;p,m,res=[read(folder/n) for n in ('probe.json','manifest.json','result.json')]
  assert res['phase']=='complete' and res['exit_code']==0 and not res['errors'] and not res['error_files']
  assert res['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']
  if label=='85-d6-gas-anchor':assert res['checkpoint']['sha256']=='9f865a7a75ed62d8fa704cae4dbe320f310f15e79269fd10ed84aa5462515b98'
  assert res['runtime_archive_sha256']==m['artifacts']['runtime']['sha256']==archive
  assert p['steps']==m['steps']==res['steps']==1500 and p['seed']==m['seed']==20261002
  assert m['profile']=='white_v3' and m['num_envs']==(80 if kind=='flat' else 88)
  assert m['physics_dt_s']==.0025 and m['control_dt_s']==.01 and m['solver_position']==32 and m['solver_velocity']==4
  assert m['no_learning'] and not m['canonical_write_authority']
  for name,file in row['files'].items():assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==file['sha256'] and file['bridge_return_bytes_exact']
  assert p['D6_closed_loop_gas_damping_engineering_pressure'] and p['D5_closed_loop_stiffness_engineering_pressure'] and p['D4_closed_loop_actual_physical_target_delay']
  gas=p['gas_damping_audit'];assign=p['gas_damping_initial_episode_assignments'];recipe=p['gas_damping_recipe']
  assert recipe['profile']==gas['profile']==m['gas_damping_profile']=='gas_damping_independent_episode_090_110_v1'
  assert gas['actual_PhysX_buffer_implicit_model_exact'] and gas['only_two_gas_damping_columns_changed'] and gas['D5_stiffness_expected_state_exact']
  assert gas['motor_PD_passive_damping_friction_preload_force_cap_armature_unchanged'] and gas['independent_episode_two_RNG'] and gas['not_full_D6_joint_friction_coverage']
  assert assign==p['gas_damping_final_episode_assignments']
  assert len(assign['factor'])==m['num_envs'] and all(len(row)==2 for row in assign['factor'])
  assert all(.9-1e-6<=x<=1.1+1e-6 for row in assign['factor'] for x in row)
  assert all(abs(d-3*f)<1e-6 for dr,fr in zip(assign['actual_damping_Ns_m'],assign['factor']) for d,f in zip(dr,fr))
  pressure=p['spring_pressure_audit'];assert pressure['actual_PhysX_buffer_implicit_model_exact']
  assert p['spring_pressure_initial_episode_assignments']==p['spring_pressure_final_episode_assignments']
  action=p['physical_action_delay_audit'];assert action['callback_counts']=={'legs':6000,'wheels':6000} and action['application_formula_max_error']==0
  assert p['physical_action_initial_episode_assignments']==p['physical_action_final_episode_assignments']
  f=facts(p,kind)
  cases[kind]=dict(facts=f,gas_audit=gas,result=res,source_SHA=res['checkpoint']['sha256'],
   identity=dict(root=p['reset_root_before_physics'],q=p['reset_joint_pos_before_physics'],parameters=p.get('initial_parameter_audit') or p['mild_initial_parameters'],
   sensor_recipe=p['sensor_recipe'],feedback_recipe=p['feedback_delay_recipe'],action_recipe=p['physical_action_delay_recipe'],spring_recipe=p['spring_pressure_recipe'],gas_recipe=recipe,
   gas_assignment=assign,spring_assignment=p['spring_pressure_initial_episode_assignments'],action_assignment=p['physical_action_initial_episode_assignments'],feedback_age=p['sensor_actual_manager_audit']['actual_feedback_sample_apply']))
 if cases:out[label]=cases
base=out['85-d6-gas-anchor'];assert len(base)==3
pairs=[]
for label,cases in out.items():
 if label=='85-d6-gas-anchor':continue
 for kind,c in cases.items():assert c['identity']==base[kind]['identity'];pairs.append(dict(label=label,kind=kind,full_root_q_parameters_recipe_assignments_exact=True))
summary={label:{k:({n:c['facts'][n] for n in ('passed','count','max_abs_cross','along_range')} if k=='world' else c['facts'].get('straight') or c['facts'].get('pure4pi')) for k,c in cases.items()} for label,cases in out.items()}
report=dict(epoch=time.time(),scope='Same3060/firstseed20261002/white_v3/A0/D0-D6 gas subset/80flat-88spin-88world/1500control15s',baseline_functional_scope_accepted=True,cases=out,pairs=pairs,summary=summary,
 original_flags_and_raw_retained=True,cross_GPU_dynamic_bitexact=False,dualseed_allprofiles_graduation=False,hardware_force_calibration=False,not_full_D6_friction_coverage=True,
 learned_candidate_scope_pending=not any(label!='85-d6-gas-anchor' and len(c)==3 for label,c in out.items()),new_GPU_PPO_or_budget_transactions=0)
(R/'D6_ACTUAL_BASELINE_SCOPE_REVIEW.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(dict(summary=summary,baseline_functional_scope_accepted=True,learned_candidate_scope_pending=report['learned_candidate_scope_pending']),ensure_ascii=True))
