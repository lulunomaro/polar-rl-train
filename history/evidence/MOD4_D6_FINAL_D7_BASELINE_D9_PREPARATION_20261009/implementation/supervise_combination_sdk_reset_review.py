"""CPU-only publication after actual nominal SDK and explicit paired D7 source review."""
from pathlib import Path
import json,time,hashlib,traceback,os,shutil,re
D=Path(__file__).resolve().parent;R=D/'reports';E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');T=Path('/home/egde/rl_candidates/MOD4_D7_FULL_CONTRACT_20261009')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):
 p=R/n;t=p.with_suffix(p.suffix+'.partial');t.write_text(json.dumps(v,indent=2));t.replace(p)
def waiting(phase):write('REVIEW_STATE.json',dict(epoch=time.time(),pid=os.getpid(),phase=phase,GPU_PPO_canonical_training_launch_authority=False))
def main():
 assert not (R/'PUBLISHED.json').exists()
 pub=read(R/'D9_NOMINAL_INTERFACE_PUBLISHED.json');folder=E/'eval_results'/pub['job']['job_id']
 while not (folder/'result.json').exists():waiting('waiting_actual_nominal_D0_D1_D7_interface');time.sleep(15)
 result=read(folder/'result.json');p=read(folder/'probe.json')
 assert result['phase']=='complete' and result['exit_code']==0 and not result['errors'] and not result['error_files']
 assert result['checkpoint']['sha256']==pub['job']['artifacts']['checkpoint']['sha256'] and result['runtime_archive_sha256']==pub['package']['sha256']
 assert p['steps']==300 and p['nominal_D0_private_RNG_unchanged'] and p['nominal_D0_parameter_reset_does_not_write_or_draw']
 for name in ('mild_initial_parameters','mild_final_parameters'):
  a=p[name];assert a['profile']=='nominal' and a['actual_parameters_pass'] and a['mass_inertia_factor_range']==[1.,1.] and a['nominal_environment_count']==10
  assert all(s['min']==s['max']==1. for s in a['motor_strength'].values()) and all(abs(x-.9)<1e-6 for x in a['friction_range'])
 action=p['physical_action_delay_audit'];assert action['callback_counts']=={'legs':1200,'wheels':1200} and action['application_formula_max_error']==0
 assert p['spring_pressure_audit']['actual_PhysX_buffer_implicit_model_exact'] and p['gas_damping_audit']['actual_PhysX_buffer_implicit_model_exact']
 cp=p['chassis_PD_audit'];assert cp['COM']['actual_PhysX_local_pose_and_buffer_exact'] and cp['COM']['other_body_physical_rotations_preserved'] and cp['PD']['motor_implicit_drive_stiffness_and_damping_zero'] and cp['parameter_auditor']['actual_parameters_pass']
 initial=p['chassis_PD_initial_episode_assignments'];final=p['chassis_PD_final_episode_assignments']
 selected_reset=p['sensor_platform_sdk']['selected_reset'];assert selected_reset['ids']==[1,4,7] and selected_reset['other_bias_episode_exact'] and selected_reset['global_tick_unchanged']
 assert p['sensor_platform_sdk']['diagnostic_reset_only_for_10env'] and p['resets']==0 and p['physics_pass'] and not p['nonfinite']
 for group in ('COM','PD'):
  assert final[group]['episode']==[v+(i in (1,4,7)) for i,v in enumerate(initial[group]['episode'])]
 for i in range(10):
  if i not in (1,4,7):
   assert initial['COM']['delta_m'][i]==final['COM']['delta_m'][i]
   for key in ('factors','actual_coefficients'):
    assert all(v[i]==final['PD'][key][name][i] for name,v in initial['PD'][key].items())
 assert all(abs(v)<=.005+1e-8 for row in final['COM']['delta_m'] for v in row)
 assert all(.95-1e-6<=v<=1.05+1e-6 for xs in final['PD']['factors'].values() for row in xs for v in row)
 assert all(x['actor35'] and x['critic38_clean'] and x['command_lastaction_mode_wheel_slots_exact'] and x['formula_max_error']==0 and x['same_tick_draws_unchanged'] for x in p['sensor_platform_sdk']['rows'])
 proof=dict(epoch=time.time(),interface_scope_accepted=True,job_id=pub['job']['job_id'],source_SHA=result['checkpoint']['sha256'],runtime_SHA=pub['package']['sha256'],probe_SHA=sha(folder/'probe.json'),result_SHA=sha(folder/'result.json'),actual_nominal_D0_no_private_RNG_draw=True,D1_D7_retained=True,callbacks_each_action_group=1200,not_skill_graduation=True)
 write('D9_NOMINAL_ACTUAL_SDK_REVIEW.json',proof)
 selector=R/'SELECTED_D7_BEHAVIOR_SOURCE.json'
 while not selector.exists():waiting('nominal_interface_accepted_waiting_explicit_actual_D7_paired_source_review');time.sleep(15)
 selected=read(selector);assert selected['behavior_review_complete'] and selected['source_count']==277 and selected['snapshot_count']==44 and selected['finite_tensors']==94
 src=Path(selected['source']['path']);h=selected['source']['sha256'];assert sha(src)==h
 passed=[read(p) for p in (T/'reports').glob('d7_stable_block*_PASSED.json')];own=[x for x in passed if x['checkpoint']['sha256']==h];assert len(own)==1
 own=own[0];assert own['own_PID_bound_receipt']['pid']==selected['own_PID_bound_receipt']['pid'] and len(own['unique_completed_segment'])==1
 base=read(T/'reports/D7_FROZEN_BEHAVIOR_PACKAGES.json');assert all(sha(Path(x['path']))==x['sha256'] for x in base.values())
 reused=[]
 for kind in ('flat','spin','world'):
  jid=selected['paired_cases'][kind]['job_id'];m=read(E/'eval_queue'/(jid+'.json'));res=read(E/'eval_results'/jid/'result.json')
  assert m['seed']==20261002 and m['profile']=='white_v3' and m['kind']==kind and m['steps']==1500 and m['num_envs']==(80 if kind=='flat' else 88)
  assert res['phase']=='complete' and not res['errors'] and res['exit_code']==0 and res['checkpoint']['sha256']==h and res['runtime_archive_sha256']==base[kind]['sha256']
  reused.append(jid)
 artifact=E/'artifacts'/('d9-selected-d7-'+h[:16]+'.pt')
 if artifact.exists():assert sha(artifact)==h
 else:
  tmp=artifact.with_suffix('.pt.partial');shutil.copyfile(src,tmp);assert sha(tmp)==h;tmp.replace(artifact)
 checkpoint=dict(path=str(artifact),sha256=h,bytes=artifact.stat().st_size);jobs=[]
 for seed in (20261002,20261003):
  for profile,slug in (('nominal','nominal'),('white_v2','white2'),('white_v3','white3')):
   if seed==20261002 and profile=='white_v3':continue
   for kind in ('flat','spin','world'):
    template=read(E/'eval_queue'/('clk2500-closure-episode-d3-98-d7-com-pd-anchor-'+kind+'.json'))
    jid='clk2500-closure-episode-d3-101-d9-retention-'+str(seed)+'-'+slug+'-'+kind;assert re.fullmatch('[A-Za-z0-9-]+',jid)
    q=E/'eval_queue'/(jid+'.json');assert not q.exists()
    runtime=pub['package'] if profile=='nominal' else base[kind]
    assert sha(Path(runtime['path']))==runtime['sha256']
    row=dict(template,job_id=jid,published_epoch=time.time(),seed=seed,profile=profile,artifacts=dict(template['artifacts'],checkpoint=checkpoint,runtime=runtime),role='D9 approved D0-D7 development retention; actual fully paired D7 source; not clean or heldout; no learning')
    assert row['no_learning'] and not row['canonical_write_authority']
    t=q.with_suffix('.json.partial');t.write_text(json.dumps(row,indent=2));t.replace(q);jobs.append(row)
 assert len(jobs)==15 and len(reused)==3
 write('PUBLISHED.json',dict(epoch=time.time(),pid=os.getpid(),source=selected,nominal_SDK=proof,three_exact_cases_reused=reused,fifteen_new_cases=jobs,total_development_conditions=18,not_clean_or_heldout=True,no_GPU_PPO_canonical_training_launch_authority=True))
 waiting('D9_eighteen_condition_development_retention_published')
if __name__=='__main__':
 try:main()
 except BaseException:
  write('REVIEW_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),no_training_or_canonical_mutation=True));raise
