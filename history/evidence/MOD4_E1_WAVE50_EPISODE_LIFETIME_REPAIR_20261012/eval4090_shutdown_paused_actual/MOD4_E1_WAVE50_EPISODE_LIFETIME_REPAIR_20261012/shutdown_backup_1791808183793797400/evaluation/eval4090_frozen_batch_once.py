from pathlib import Path
import json,time,hashlib,subprocess,os,fcntl,torch,traceback,shutil
D=Path(__file__).resolve().parent;R=D/'reports';PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def h(p):
 a=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):a.update(b)
 return a.hexdigest()
def write(p,v):
 b=json.dumps(v,indent=2).encode();tmp=p.with_name(p.name+'.partial');tmp.write_bytes(b);os.replace(tmp,p)
def process(pid):
 try:
  p=Path('/proc')/str(pid);s=(p/'stat').read_text().rsplit(')',1)[1].split();return dict(pid=pid,start_ticks=int(s[19]),state=s[0],argv=[x.decode(errors='replace') for x in (p/'cmdline').read_bytes().split(bytes([0])) if x])
 except FileNotFoundError:return None
def resource():
 gpu=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,memory.used,memory.total','--format=csv,noheader,nounits']).decode().strip();v=list(map(int,gpu.replace(' ','').split(',')));return dict(epoch=time.time(),GPU_free_mib=v[0],GPU_used_mib=v[1],GPU_total_mib=v[2],durable_free_bytes=shutil.disk_usage(D).free,available_RAM=next(int(l.split()[1])*1024 for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))
def main():
 torch.set_num_threads(1);lock=(D/'evaluation_only.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert not (R/'BATCH_STARTED.json').exists();request=json.loads((R/'HUMAN_REQUEST_AND_BATCH_ADMISSION.json').read_bytes());jobs=request['jobs'];assert len(jobs)==4
 write(R/'BATCH_STARTED.json',dict(epoch=time.time(),owner=process(os.getpid()),source_SHA=request['source_SHA'],human_4090_eval_and_parallel_authorized=True,evaluation_concurrency=1,training_launch_or_canonical_write_authority=False))
 for index,job in enumerate(jobs):
  folder=D/'jobs'/job['job_id'];folder.mkdir();write(folder/'manifest.json',job);runtime=Path(job['adapted_runtime']);source=Path(job['artifacts']['checkpoint']['path']);assert h(source)==request['source_SHA']
  original=json.loads((runtime/'SOURCE_MANIFEST.json').read_bytes());adapter=json.loads((runtime/'PATH_ADAPTER.json').read_bytes())
  for name,sha in original['files'].items():assert h(runtime/name)==(adapter['adapted_env_sha256'] if name=='runtime/isaac/mod4/env.json' else sha)
  ck=torch.load(source,map_location='cpu',weights_only=False);count=0
  def walk(v):
   nonlocal count
   if isinstance(v,torch.Tensor) and (v.is_floating_point() or v.is_complex()):assert torch.isfinite(v).all();count+=1
   elif isinstance(v,dict):
    for x in v.values():walk(x)
   elif isinstance(v,(list,tuple)):
    for x in v:walk(x)
  walk(ck);assert count==request['actual_own_finite_tensors']==107 and ck['E1_WAVE50_episode_lifetime_profile']=='WAVE50_birth_episode_timeout40s_nonWave20s_v1';del ck
  need=job['historical_observed_peak_GPU_mib']+512
  while True:
   res=resource()
   if res['GPU_free_mib']>=need and res['available_RAM']>=8*1024**3 and res['durable_free_bytes']>request['remaining_eval_double_output_guard_bytes']+2*1024**3:break
   write(R/'EVAL_RESOURCE_PENDING.json',dict(epoch=time.time(),job_id=job['job_id'],required_GPU_mib=need,actual=res,no_training_stop_hotpatch_or_GPU_launch=True));time.sleep(15)
  write(R/'EVAL_CURRENT.json',dict(epoch=time.time(),phase='launching',job_id=job['job_id'],resource=res,parallel_training_allowed=True))
  probe={'flat':'frozen_history_flat.py','spin':'frozen_history_spin.py','world':'frozen_history_world.py'}[job['kind']];out=folder/'probe.json';log=folder/'probe.log'
  args=[PY,str(runtime/'runtime/isaac/mod4'/probe),'--headless','--device','cuda:0','--checkpoint',str(source),'--output',str(out),'--steps',str(job['steps']),'--num_envs',str(job['num_envs']),'--seed',str(job['seed']),'--dr-profile',job['profile']]
  args+=['--speed_limit','1.5','--ramp_suite'] if job['kind']=='flat' else ['--max-rate','12.566370614359172','--contact-readback']
  env={k:v for k,v in os.environ.items() if not k.startswith('RM_')};env.update(PYTHONPATH=str(runtime/'runtime')+os.pathsep+str(runtime/'runtime/isaac/mod4'),ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
  start=time.time();baseline=res['GPU_used_mib'];peak=baseline
  with log.open('xb') as f:p=subprocess.Popen(args,cwd=runtime/'runtime',env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  write(folder/'ACTIVE.json',dict(epoch=time.time(),child=process(p.pid),argv=args,checkpoint_SHA=request['source_SHA'],no_PPO=True,resource_admission=res))
  while p.poll() is None:
   res=resource();peak=max(peak,res['GPU_used_mib']);write(R/'EVAL_CURRENT.json',dict(epoch=time.time(),phase='evaluating',job_id=job['job_id'],child=process(p.pid),resource=res,observed_total_GPU_peak_mib=peak))
   if time.time()-start>job['max_wall_seconds']:
    write(R/'EVAL_ATTENTION.json',dict(epoch=time.time(),job_id=job['job_id'],reason='Own evaluation exceeded originalwalllimit; no kill authority, child retained',child=process(p.pid)));return
   time.sleep(2)
  raw=out.read_bytes() if out.exists() else None;text=log.read_text(errors='replace');errors=[l for l in text.splitlines() if any(s in l.lower() for s in ('traceback (most recent call last)','cuda out of memory','gpu collision stack overflow','physx error','nan tensor'))];error_files=[q.name for q in folder.glob('*.error.txt')]
  result=dict(job_id=job['job_id'],plan_sha256=job['plan_sha256'],host='4090-Linux-10.24.4.210',phase='complete' if p.returncode==0 and raw and not errors and not error_files else 'retained_failed',exit_code=p.returncode,checkpoint=dict(iteration_stored=request['source_iteration'],finite_tensors=107,sha256=request['source_SHA']),runtime_archive_sha256=job['artifacts']['runtime']['sha256'],probe_kind=job['kind'],num_envs=job['num_envs'],steps=job['steps'],seed=job['seed'],profile=job['profile'],transfer_seconds=0,physics_process_wall_seconds=time.time()-start,physics_dt_s=.0025,architecture_variant='A0',observed_GPU_memory_mib=peak,memory_sampling_period_s=2.,observed_peak_not_continuous_peak=True,errors=errors,error_files=error_files,result_present=raw is not None,formal_cross_host_equivalence_confirmed=False,new_learning=False,backend_changed_from3060_to4090_disclosed=True)
  write(folder/'result.json',result);write(folder/'PHYSICS_COMPLETE.json',result);write(folder/'complete.json',result);assert h(source)==request['source_SHA']
  if result['phase']!='complete':write(R/'EVAL_ATTENTION.json',dict(epoch=time.time(),job_id=job['job_id'],result=result,raw_error_retained=True,no_retry_oldjob_or_training_intervention=True));return
  if index==0:write(R/'TERRAIN_COMPLETE.json',dict(epoch=time.time(),job_id=job['job_id'],result=result,retention_remaining_can_run_with_training_when_resources_admitted=True))
 write(R/'BATCH_COMPLETE.json',dict(epoch=time.time(),source_SHA=request['source_SHA'],jobs=[j['job_id'] for j in jobs],all4_actualcomplete_errorfree=True,no_GPU_budget_or_training_write=True))
if __name__=='__main__':
 try:main()
 except BaseException:write(R/'EVAL_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),no_PPO_or_training_write=True));raise
