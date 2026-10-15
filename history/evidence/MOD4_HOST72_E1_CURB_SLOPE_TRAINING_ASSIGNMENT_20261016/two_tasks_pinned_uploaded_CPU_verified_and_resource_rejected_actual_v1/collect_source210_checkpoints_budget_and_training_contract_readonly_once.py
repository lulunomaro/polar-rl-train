"""Fresh bounded source inspection for the human-assigned host72 jobs; no GPU or writes."""
from pathlib import Path
import hashlib,json,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True);W=D.parent
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'))
import transport_bodyframe_root_owned as t
CODE=r'''
from pathlib import Path
import json,hashlib,time,fcntl,subprocess,os
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
before=H(B);b=json.loads(B.read_bytes());assert b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
locks=[]
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 try:
  with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
  locks.append(dict(path=str(p),free=True))
 except BlockingIOError:locks.append(dict(path=str(p),free=False))
paths=list((E/'artifacts').glob('*3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e*'))
curb=[p for p in paths if p.is_file() and p.suffix=='.pt'];assert len(curb)==1, [str(p) for p in paths]
slope=E/'artifacts/e1-slope-own-24b18846fcff1e0b8da7fd478314fca9cd2ed2b97461ca34f65ef5b7c7ff2411.pt'
assert H(curb[0])=='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
assert H(slope)=='24b18846fcff1e0b8da7fd478314fca9cd2ed2b97461ca34f65ef5b7c7ff2411'
import torch
rows=[]
for task,p in (('CURB20_original_warmstart_not_failed133_or139',curb[0]),('SLOPE5_own_complete_source',slope)):
 ck=torch.load(p,map_location='cpu',weights_only=False);tensors=[]
 def walk(x,key=''):
  if torch.is_tensor(x):
   assert x.device.type=='cpu' and (not x.is_floating_point() or torch.isfinite(x).all());tensors.append(dict(key=key,shape=list(x.shape),dtype=str(x.dtype),floating=x.is_floating_point()))
  elif hasattr(x,'items'):
   for k,v in x.items():walk(v,key+'/'+str(k))
  elif isinstance(x,(list,tuple)):
   for i,v in enumerate(x):walk(v,key+'/'+str(i))
 walk(ck)
 rows.append(dict(task=task,path=str(p),bytes=p.stat().st_size,sha256=H(p),iter=ck['iter'],keys=list(ck),tensors=tensors,
  actor=[dict(key=k,shape=list(v.shape),dtype=str(v.dtype)) for k,v in ck['actor_state_dict'].items()],
  terrain_metadata={k:v for k,v in ck['E1_terrain_state'].items() if not torch.is_tensor(v) and isinstance(v,(str,int,float,bool,type(None)))},
  recipe_fields={k:ck[k] for k in ('sensor_recipe','feedback_delay_recipe','physical_action_delay_recipe','spring_pressure_recipe','gas_damping_recipe','chassis_PD_recipe')},
  optimizer_states=len(ck['optimizer_state_dict']['state']),optimizer_param_groups=[{k:v for k,v in x.items() if k!='params'} for x in ck['optimizer_state_dict']['param_groups']]))
 assert not torch.cuda.is_initialized()
snapshots=[]
for root in ('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENTRY_SEED_REVIEWED_20261011','/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_SNAPSHOT_REVIEWED_20261011'):
 for p in sorted((Path(root)/'learning_logs').glob('*/run_manifest.json')):
  x=json.loads(p.read_bytes());snapshots.append(dict(path=str(p),bytes=p.stat().st_size,sha256=H(p),metadata={k:v for k,v in x.items() if k not in ('env','source_map','src_sha256')},source_map=x.get('source_map'),src_sha256=x.get('src_sha256'),
    RM_environment={k:v for k,v in x.get('env',{}).items() if k.startswith('RM_') and not any(y in k.lower() for y in ('password','secret','token','key'))}))
nv=subprocess.run(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name','--format=csv,noheader'],capture_output=True,text=True)
assert H(B)==before
v=dict(epoch=time.time(),source_host='10.24.4.210',canonical=dict(path=str(B),sha256=before,authorized=b['authorized_training_seconds'],charged=b['charged_training_seconds'],remaining=b['remaining_training_seconds'],active=b['active_segment'],completed_segments=len(b['completed_segments']),extensions=len(b['budget_extensions'])),
 actual_two_fcntl=locks,checkpoints=rows,original_snapshots=snapshots,actual_nvidia_compute_snapshot=dict(returncode=nv.returncode,stdout=nv.stdout,stderr=nv.stderr),
 no_source_write_GPU_PPO_budget_change_or_new_process_signal=True)
print(json.dumps(v))
'''
def main():
 assert not (R/'SOURCE210_CHECKPOINTS_CANONICAL_AND_ORIGINAL_CONTRACT_ACTUAL.json').exists()
 c=None
 try:
  c=t.connect();si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 '+shlex.quote(t.PY)+' -B -',timeout=120)
  si.write(CODE);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status()
  with (R/'SOURCE210_CONTRACT_TRANSPORT_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),rc=rc,stdout=out.decode(errors='replace'),stderr=err.decode(errors='replace')),f,indent=2)
  assert rc==0,err.decode(errors='replace')
  v=json.loads(out)
  with (R/'SOURCE210_CHECKPOINTS_CANONICAL_AND_ORIGINAL_CONTRACT_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
  print(json.dumps(dict(canonical=v['canonical'],locks=v['actual_two_fcntl'],sources=[{k:x[k] for k in ('task','path','bytes','sha256','optimizer_states')} for x in v['checkpoints']],snapshots=len(v['original_snapshots']),no_CUDA_or_budget_write=True)),flush=True)
 finally:t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('SOURCE210_CONTRACT_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_mutation_or_blind_retry=True),f,indent=2)
  raise
