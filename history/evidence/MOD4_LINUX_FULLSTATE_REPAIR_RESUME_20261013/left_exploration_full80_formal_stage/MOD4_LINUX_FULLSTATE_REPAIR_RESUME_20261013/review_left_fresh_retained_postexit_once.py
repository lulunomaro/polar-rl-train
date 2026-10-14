"""Independent postexit retained-save review; original failed scope is immutable."""
from pathlib import Path
import json,os,time,hashlib
from read_linux_resume_boundary_actual import connect_linux_only
D=Path(__file__).resolve().parent
R='/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_exploration20k_target_CPU_v1'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
CODE=r'''
from pathlib import Path
import json,sys,time,hashlib,fcntl,torch,psutil
R=Path(ROOT);B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
before=sha(B);assert json.loads(B.read_bytes())['active_segment'] is None
m=json.loads((R/'LEFT_FRESH_GPU_ADMISSION_MANIFEST.json').read_bytes())
ex=json.loads((R/'left_fresh0PPO_v1/EXIT_RECEIPT.json').read_bytes());dispatch=json.loads((R/'left_fresh0PPO_v1/DISPATCH_RECEIPT.json').read_bytes())
assert ex['child_actually_absent'] and ex['canonical_bytes_unchanged'] and ex['PPO_updates']==0 and not ex['physics_capacity_error']
for who in ('parent','child'):
 row=dispatch[who]
 assert not psutil.pid_exists(row['pid']) or psutil.Process(row['pid']).create_time()!=row['created']
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert not (R/'LEFT_FRESH_OWN_FULLSAVE0PPO_PASSED.json').exists()
err=R/'LEFT_FRESH_ORIGINAL_ERROR.json';assert 'NATIVE_REPAIRED0PPO_COMPLETE' in err.read_text()
log=R/'left_fresh0PPO_v1/worker_stdout.log';raw=log.read_bytes()
assert b'UnboundLocalError' in raw and b'env.write_retention_trace(log_dir)' in raw
assert all(x not in raw for x in (b'buffer overflow detected',b'Contacts have been dropped',b'PhysX scene is corrupted',b'CUDA error'))
folders=list((R/'left_fresh0PPO_v1/learning_logs').glob('*/model_own_repaired0PPO.pt'));assert len(folders)==1
p=folders[0];folder=p.parent
sys.path[:0]=[str(R),str(R/'isaac/mod4')]
from wave50_lifetime_fullsave_cpu import fullsave
from left_exploration_resume_contract_v1 import same,KEY
info=fullsave(p,count=20000)
source=Path(m['source']['path']);assert sha(source)==m['source']['sha256']
ck=torch.load(p,map_location='cpu',weights_only=False);old=torch.load(source,map_location='cpu',weights_only=False)
for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict',KEY):assert same(ck[k],old[k]),k
assert ck['E1_terrain_state']['num_envs']==20000
markers=[]
for q in sorted(folder.glob('*STARTUP*VERIFIED.json')):
 v=json.loads(q.read_bytes());assert v['pid']==dispatch['child']['pid'] and v['source_sha256']==m['source']['sha256']
 if 'passed' in v:assert v['passed'] is True
 for k,z in v.items():
  if k.endswith('_exact') or k.endswith('_verified') or k in ('actor_critic_std_exact','optimizer_loaded_original_path','global_CPU_CUDA_streams_restored','sensor_streams_restored','all_episode_counters_incremented_once'):assert z is True,(q.name,k,z)
 if q.name=='LEFT_EXPLORATION_RESUME_STARTUP_VERIFIED.json':
  assert v['explicit_one_time_left_mean_std_initialization'] is False and v['same_left_branch_restored_exact'] is True
 markers.append(dict(path=str(q),sha256=sha(q),proof=v))
assert len(markers)==13
h=json.loads((folder/'CLOCK_TRAINING_HEALTH.json').read_bytes())
assert h['control_steps']==h['actual_physics_callbacks']==0 and h['stop_reason'] is None
assert h['ordinary_episode_reset_events']==h['integrity_task_reset_events']==h['unknown_task_reset_events']==0 and h['nonfinite_observed'] is False
assert not list(folder.glob('*.npz'))
assert sha(B)==before and not torch.cuda.is_initialized()
q=R/'LEFT_FRESH_RETAINED_INDEPENDENT_POSTEXIT_CPU_PASSED.json';assert not q.exists()
v=dict(epoch=time.time(),passed=True,checkpoint=str(p),sha256=sha(p),bytes=p.stat().st_size,source=m['source'],actual_fullsave=info,actor_critic_optimizer_branch_exact=True,thirteen_actual_CPUCUDA_markers=markers,health=h,PPO_updates=0,physical_controls=0,original_parent_passed=False,original_error_path=str(err),original_error_SHA=sha(err),original_stdout_SHA=sha(log),original_worker_after_save_UnboundLocalError_preserved=True,independent_retained_fullstate_admission_only=True,original_missing_completion_marker_preserved=True,exit=ex,actual_processes_absent_locks_free=True,budget_bytes_unchanged=True,qualified50=False)
with q.open('x') as f:json.dump(v,f,indent=2)
print(json.dumps(v))
'''
def main():
 dest=D/'left_fresh_retained_postexit_actual';assert not dest.exists()
 c=connect_linux_only();sf=None
 try:
  si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+PY+' -',timeout=60);si.write('ROOT='+repr(R)+'\n'+CODE);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status()
  report=D/'reports'/('LEFT_FRESH_RETAINED_POSTEXIT_REMOTE_CPU_'+str(time.time_ns())+'.json');report.write_text(json.dumps(dict(code=rc,stdout=out.decode(),stderr=err.decode()),indent=2),encoding='utf8');assert rc==0,str(report)
  v=json.loads(out);dest.mkdir();sf=c.open_sftp()
  folder=v['checkpoint'].rsplit('/',1)[0]
  names=[R+'/LEFT_FRESH_RETAINED_INDEPENDENT_POSTEXIT_CPU_PASSED.json',R+'/LEFT_FRESH_ORIGINAL_ERROR.json',R+'/left_fresh0PPO_v1/worker_stdout.log',R+'/left_fresh0PPO_v1/EXIT_RECEIPT.json',v['checkpoint']]
  names.extend(folder+'/'+n for n in sf.listdir(folder) if n.endswith('.json'))
  rows=[]
  for i,name in enumerate(names):
   p=dest/(str(i)+'_'+name.rsplit('/',1)[1]);sf.get(name,str(p));h=hashlib.sha256(p.read_bytes()).hexdigest()
   with sf.open(name,'rb') as f:rh=hashlib.file_digest(f,'sha256').hexdigest()
   assert h==rh and p.stat().st_size==sf.stat(name).st_size
   rows.append(dict(remote_path=name,local_path=str(p),bytes=p.stat().st_size,sha256=h))
  q=D/'reports/LEFT_FRESH_RETAINED_POSTEXIT_ACTUAL_COLLECTION.json';q.write_text(json.dumps(dict(epoch=time.time(),independent_review=v,two_host_byteSHA_exact=rows,no_GPU_or_PPO=True),indent=2),encoding='utf8')
  print(json.dumps(dict(report=str(q),independent_passed=v['passed'],original_parent_passed=False,checkpoint=v['checkpoint'],sha256=v['sha256'],controls=0,PPO_updates=0)))
 finally:
  if sf:sf.close()
  c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
