"""One approved CPU-only publisher: final healthy source -> immutable3060 jobs."""
from pathlib import Path
import json,hashlib,time,os,shutil,traceback
E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
S=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_DEPENDENCY_REVIEW_20261007')
D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
 t=p.with_suffix(p.suffix+'.partial');t.write_text(json.dumps(v,indent=2));os.replace(t,p)
def verify():
 a=json.loads((E/'reports/PLAN_APPROVAL.json').read_text());assert a['approved'] and 'S0E' in a['allowed_stages'] and 'S2' in a['allowed_stages']
 assert a['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
 assert sha(Path(__file__))==json.loads((R/'SOURCE_FREEZE.json').read_text())['sha256'][Path(__file__).name]
 return a
def main():
 import fcntl
 lock=(R/'publication.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert not (R/'STARTED.json').exists();verify();write(R/'STARTED.json',dict(pid=os.getpid(),epoch=time.time(),CPU_only=True,GPU_authority=False,canonical_write_authority=False))
 deadline=time.time()+14400
 while not (S/'reports/E0_SENSOR_STAGE1_REVIEW_READY.json').exists():
  if (S/'reports/E0_SENSOR_ATTENTION.json').exists():raise RuntimeError('Training authority requires review; no candidate automatically published')
  if time.time()>deadline:raise TimeoutError('No healthy final source before publication review bound')
  write(R/'STATE.json',dict(epoch=time.time(),phase='waiting_own_healthy_sensor_final_save',pid=os.getpid(),GPU_child=None))
  time.sleep(15)
 approval=verify();ready=json.loads((S/'reports/E0_SENSOR_STAGE1_REVIEW_READY.json').read_text());formal=ready['formal'];h=formal['health']
 assert h['actual_task_reset_events']==0 and h['failed_environments']==0 and h['max_closure_error_m']<=.002 and h['max_mimic_error_rad']<=.01 and h['actual_physics_callbacks']==h['expected_physics_callbacks']
 assert not formal['discarded_preflight'] and len(formal['unique_completed_segment'])==1
 source=formal['checkpoint'];p=Path(source['path']);assert p.is_relative_to(S/'learning_logs') and sha(p)==source['sha256']
 assert formal['own_PID_bound_receipt']['checkpoint']==str(p) and formal['own_PID_bound_receipt']['pid']==formal['unique_completed_segment'][0]['pid']
 run=Path(formal['run']);m=json.loads((run/'run_manifest.json').read_text());f=json.loads((S/'reports/SOURCE_FREEZE.json').read_text())
 assert m['source_map']==f['sha256'] and len(f['sha256'])==202
 for n,digest in f['sha256'].items():assert sha(S/n)==digest and sha(run/'sensor_source_snapshot'/n)==digest,n
 import torch;torch.set_num_threads(1)
 ck=torch.load(p,map_location='cpu',weights_only=False)
 assert ck['sensor_recipe']['profile']=='noise_bias_mild_v1' and ck['sensor_DR_state']['version']==1 and ck['optimizer_state_dict']['state']
 count=0
 def walk(v):
  nonlocal count
  if torch.is_tensor(v) and (v.is_floating_point() or v.is_complex()):assert torch.isfinite(v).all();count+=1
  elif isinstance(v,dict):
   for x in v.values():walk(x)
  elif isinstance(v,(list,tuple)):
   for x in v:walk(x)
 walk(ck);assert count>=68 and ck['actor_state_dict']['mlp.0.weight'].shape==(256,35)
 old=json.loads((E/'reports/SENSOR_COMPLETE_ASYNC_PACKAGE_AND_JOBS.json').read_text());runtime=old['package'];assert sha(Path(runtime['path']))==runtime['sha256']
 target=E/'artifacts'/('clock1000-s2sensor-final-'+source['sha256']+'.pt');assert not target.exists()
 shutil.copyfile(p,str(target)+'.partial');assert sha(Path(str(target)+'.partial'))==source['sha256'];os.replace(str(target)+'.partial',target)
 jobs=[]
 for kind in ('flat','spin','world'):
  job='clk1000-s2complete-10-candidate-'+kind;path=E/'eval_queue'/(job+'.json');assert not path.exists()
  row=dict(job_id=job,stage='S0E',immutable=True,plan_id=approval['plan_id'],plan_sha256=approval['approved_plan_sha256'],published_epoch=time.time(),kind=kind,
   profile='white_v3',sensor_profile='noise_bias_mild_v1',seed=20261002,num_envs=80 if kind=='flat' else 88,steps=1500,max_wall_seconds=1800,architecture_variant='A0',role='S2 actual45min candidate',physics_dt_s=.001,control_dt_s=.01,
   protocol='Frozen matched source23783 versus actual healthy S2 final candidate on3060 noise feedback scope; retain full signed cycles and old flags. Not final graduation.',
   artifacts=dict(runtime=runtime,checkpoint=dict(path=str(target),bytes=target.stat().st_size,sha256=source['sha256'])),no_learning=True,canonical_write_authority=False,GPU_concurrency=1,platform_scope_not_yet_accepted=True)
  write(path,row);jobs.append(row)
 proof=dict(epoch=time.time(),healthy_own_final_source=source,full_checkpoint_finite_tensors=count,actual_environment_steps=formal['actual_environment_steps'],formal_run=str(run),own_unique_completed_segment=formal['unique_completed_segment'],jobs=jobs,CPU_only=True,canonical_write_authority=False,training_launch_authority=False,existing_evaluator_unchanged=True)
 write(E/'reports/SENSOR_COMPLETE_ASYNC_CANDIDATE_PUBLISHED.json',proof);write(R/'PUBLISHED.json',proof)
 write(R/'STATE.json',dict(epoch=time.time(),phase='healthy_final_candidate_published',pid=os.getpid(),jobs=[x['job_id'] for x in jobs],no_PPO=True))
if __name__=='__main__':
 try:main()
 except BaseException:
  write(R/'ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_canonical_authority=True));raise
