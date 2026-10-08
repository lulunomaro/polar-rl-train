"""Review completed development-seed D5 retention; no new physics or learning."""
from pathlib import Path
import ast, hashlib, json, math, statistics, sys, time
D=Path(__file__).resolve().parent; R=D/'reports'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sys.path.insert(0,str(D.parent/'MOD4_S1A_MATCHED_EVALUATION_20261007/review_contracts'))
from scut_curriculum_gate_v4 import evidence
from world_progress_contract import target
original=D.parent/'MOD4_CLOSURE_EPISODE_CONTINUATION_20261008/review_block1_matched_scope.py'
tree=ast.parse(original.read_text(encoding='utf8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='facts'],type_ignores=[]),str(original),'exec'))
index=read(R/'STAGE_EVALUATOR_CURRENT_ACTUAL.json'); jobs={j['id']:j for j in index['jobs']}
oldroot=D.parent/'MOD4_D5_FULL_CONTRACT_20261008/reports'
oldindex={j['id']:j for j in read(oldroot/'D5_COMPLETED_SCOPE_FILES.json')['jobs']}
prefix='clk2500-closure-episode-d3-'
source='9f865a7a75ed62d8fa704cae4dbe320f310f15e79269fd10ed84aa5462515b98'
archives={'nominal':'d7bcaeb0f305a0abac4c3ce1549477e0843d5f8857764619c818ef97f6be409b',
          'white_v2':'fe8dc6bcb027215739a9edf7a8b5fa46240326b402e05ae0d0463db87044452c',
          'white_v3':'fe8dc6bcb027215739a9edf7a8b5fa46240326b402e05ae0d0463db87044452c'}
cases=[]; returns=[]
for seed in (20261002,20261003):
 for profile in ('nominal','white_v2','white_v3'):
  for kind in ('flat','spin','world'):
   reused=seed==20261002 and profile=='white_v3'
   suffix=('75-d5-b1-'+kind if reused else
           f'96-d5-retention-nominal-{seed}-{kind}' if profile=='nominal' else
           f'97-d5-retention-{seed}-{profile.replace("_v","")}-{kind}')
   job=prefix+suffix
   row=oldindex[job] if reused else jobs[job]
   folder=(oldroot/'windows'/job) if reused else (R/'stage_scope'/job)
   p,m,res=[read(folder/n) for n in ('probe.json','manifest.json','result.json')]
   assert res['phase']=='complete' and res['exit_code']==0 and not res['errors'] and not res['error_files'],job
   assert res['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==source
   assert res['checkpoint']['finite_tensors']==89
   assert res['runtime_archive_sha256']==m['artifacts']['runtime']['sha256']==archives[profile]
   assert res['seed']==m['seed']==p['seed']==seed and res['profile']==m['profile']==profile
   assert p['steps']==m['steps']==res['steps']==1500 and m['num_envs']==(80 if kind=='flat' else 88)
   assert m['no_learning'] and not m['canonical_write_authority'] and not res['new_learning']
   assert m['physics_dt_s']==.0025 and m['control_dt_s']==.01 and m['solver_position']==32 and m['solver_velocity']==4
   for name in ('probe.json','result.json'):
    proof=row['files'][name]; actual=hashlib.sha256((folder/name).read_bytes()).hexdigest()
    assert actual==proof['sha256']
    assert proof.get('bridge_return_bytes_exact',proof.get('automatic_bridge_return_bytes_exact')) is True
    returns.append(dict(job=job,file=name,SHA=actual,bridge_bytes_exact=True,reused=reused))
   params=p.get('initial_parameter_audit') or p['mild_initial_parameters']
   assert params['profile']==profile and params['actual_parameters_pass']
   final=p.get('final_parameter_audit') or p['mild_final_parameters']
   assert final['actual_parameters_pass'] and final['profile']==profile
   if profile=='nominal':
    assert params['registered_ranges']=={'mass':[1.,1.],'motor':[1.,1.],'friction':[.9,.9]}
    assert params['mass_inertia_factor_range']==[1.,1.] and params['nominal_environment_count']==m['num_envs']
    assert p['nominal_D0_private_RNG_unchanged'] and p['nominal_D0_parameter_reset_does_not_write_or_draw']
   assert p['D5_closed_loop_stiffness_engineering_pressure'] and p['D4_closed_loop_actual_physical_target_delay']
   pressure=p['spring_pressure_audit']; assert pressure['actual_PhysX_buffer_implicit_model_exact']
   assert pressure['preload_damping_force_limit_armature_unchanged'] and pressure['independent_episode_two_CUDA_RNG']
   assert p['spring_pressure_initial_episode_assignments']==p['spring_pressure_final_episode_assignments']
   action=p['physical_action_delay_audit']; assert action['callback_counts']=={'legs':6000,'wheels':6000}
   assert action['application_formula_max_error']==0
   assert p['physical_action_initial_episode_assignments']==p['physical_action_final_episode_assignments']
   f=facts(p,kind)
   cases.append(dict(job=job,seed=seed,profile=profile,kind=kind,source_SHA=source,runtime_SHA=archives[profile],
                     actual_model_task_data_passed=True,facts=f,process_wall_s=res['physics_process_wall_seconds'],
                     transfer_s=res['transfer_seconds'],exact_evidence_reused=reused))
assert len(cases)==18 and len(returns)==36
summary=[]
for seed in (20261002,20261003):
 for profile in archives:
  c={row['kind']:row['facts'] for row in cases if row['seed']==seed and row['profile']==profile}
  summary.append(dict(seed=seed,profile=profile,world={k:c['world'][k] for k in ('passed','count','max_abs_cross','along_range','directions')},
                      straight=c['flat']['straight'],pure4pi=[{k:v for k,v in row.items() if k!='values'} for row in c['spin']['pure4pi']],
                      closure_mm={k:v['closure_mm'] for k,v in c.items()}))
report=dict(epoch=time.time(),source_SHA=source,cases=cases,summary=summary,returned_files=returns,
            actual_model_task_data_passed_all18=True,conditions='2 development seeds x 3 D0 profiles x 3 skills; D1-D5 remain enabled',
            firstseed_white3_3cases_exactly_reused=True,new_cases=15,held_out_seed_claimed=False,
            clean_original_distribution_claimed=False,full_DR_or_hardware_graduation=False,
            cross_package_runtime_exact_claimed=False,cross_GPU_dynamic_bitexact=False,
            quality_flags_and_all_raw_preserved=True,new_GPU_PPO_or_budget_transactions=0)
(R/'D5_FULL_RETENTION_ACTUAL_REVIEW.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(dict(all18_actual_data_passed=True,summary=summary,exact_reused=3,new_completed=15),ensure_ascii=True))
