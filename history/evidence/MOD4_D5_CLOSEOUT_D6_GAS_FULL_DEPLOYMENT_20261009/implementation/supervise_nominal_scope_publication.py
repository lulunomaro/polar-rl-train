"""CPU-only nominal SDK evidence reader and six-case publication. No training authority."""
from pathlib import Path
import json,time,hashlib,traceback,os
D=Path(__file__).resolve().parent;R=D/'reports';E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):
 p=R/n;t=Path(str(p)+'.partial');t.write_text(json.dumps(v,indent=2));t.replace(p)
def main():
 assert not (R/'PUBLISHED.json').exists();pub=read(R/'NOMINAL_SCOPE_PACKAGE_PUBLISHED.json');job=pub['job']['job_id'];folder=E/'eval_results'/job
 while not (folder/'result.json').exists():
  write('STATE.json',dict(epoch=time.time(),pid=os.getpid(),phase='waiting_nominal_interface_SDK',GPU_training_canonical_authority=False));time.sleep(15)
 result=read(folder/'result.json');assert result['phase']=='complete' and result['exit_code']==0 and not result['errors'],result
 p=read(folder/'probe.json');assert result['checkpoint']['sha256']==pub['job']['artifacts']['checkpoint']['sha256'] and result['runtime_archive_sha256']==pub['package']['sha256']
 assert p['nominal_D0_private_RNG_unchanged'] and p['nominal_D0_parameter_reset_does_not_write_or_draw']
 for name in ('mild_initial_parameters','mild_final_parameters'):
  a=p[name];assert a['profile']=='nominal' and a['actual_parameters_pass'] and a['mass_inertia_factor_range']==[1.,1.] and a['nominal_environment_count']==10
  assert all(s['min']==s['max']==1. for s in a['motor_strength'].values()) and all(abs(x-.9)<1e-6 for x in a['friction_range'])
 action=p['physical_action_delay_audit'];assert action['callback_counts']=={'legs':1200,'wheels':1200} and action['application_formula_max_error']<=1e-6
 assert p['spring_pressure_audit']['actual_PhysX_buffer_implicit_model_exact'] and p['spring_pressure_audit']['preload_damping_force_limit_armature_unchanged']
 proof=dict(epoch=time.time(),interface_scope_accepted=True,job_id=job,source_SHA=result['checkpoint']['sha256'],runtime_SHA=pub['package']['sha256'],probe_SHA=sha(folder/'probe.json'),result_SHA=sha(folder/'result.json'),actual_D0_mass_inertia_motor_mu_nominal=True,D0_private_RNG_no_draws=True,D1_D5_pressure_delay_noise_retained=True,each_action_group_callbacks=1200,original_flags_raw_retained=True,not_skill_graduation=True)
 write('NOMINAL_ACTUAL_SDK_REVIEW.json',proof);jobs=[]
 for seed in (20261002,20261003):
  for kind in ('flat','spin','world'):
   old='clk2500-closure-episode-d3-95-d5-retention-'+str(seed)+'-nominal-'+kind;template=read(E/'eval_queue'/(old+'.json'));new='clk2500-closure-episode-d3-96-d5-retention-nominal-'+str(seed)+'-'+kind;q=E/'eval_queue'/(new+'.json');assert not q.exists()
   row=dict(template,job_id=new,published_epoch=time.time(),artifacts=dict(template['artifacts'],runtime=pub['package']),role='Actual nominal D0 lifecycle accepted; D1-D5 retained; replacement of incompatible original nominal task, not replay of valid result')
   t=Path(str(q)+'.partial');t.write_text(json.dumps(row,indent=2));t.replace(q);jobs.append(row)
 write('PUBLISHED.json',dict(epoch=time.time(),pid=os.getpid(),SDK_proof=proof,jobs=jobs,old_failed_and_never_run_jobs_retained=True,no_GPU_PPO_canonical_or_training_launch_authority=True))
 write('STATE.json',dict(epoch=time.time(),pid=os.getpid(),phase='nominal_SDK_accepted_six_regression_jobs_published',GPU_training_canonical_authority=False))
if __name__=='__main__':
 try:main()
 except BaseException:
  write('ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),no_training_or_canonical_mutation=True));raise
