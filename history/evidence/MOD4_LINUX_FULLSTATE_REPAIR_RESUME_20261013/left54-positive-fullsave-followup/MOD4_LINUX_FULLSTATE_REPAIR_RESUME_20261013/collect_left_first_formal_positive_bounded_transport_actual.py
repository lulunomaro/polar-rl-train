"""Readonly actual own saved PPO verification and exact artifact collection."""
from pathlib import Path
import json,os,time,hashlib
from read_linux_resume_boundary_actual import connect_linux_only
D=Path(__file__).resolve().parent
R='/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_exploration20k_first_formal_v1'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
CODE=r'''
from pathlib import Path
import json,time,hashlib,sys,torch,psutil
R=Path(ROOT);m=json.loads((R/'LEFT_FORMAL_ADMISSION_MANIFEST.json').read_bytes())
alllatest=list((R/'left_formal3600_v1/learning_logs').glob('*/latest_complete.json'))
if not alllatest:print(json.dumps(dict(epoch=time.time(),pending_own_complete_save=True)));sys.exit(0)
assert len(alllatest)==1
l=json.loads(alllatest[0].read_bytes());p=Path(l['checkpoint']);assert p.is_file()
sys.path[:0]=[str(R),str(R/'isaac/mod4')]
from wave50_lifetime_fullsave_cpu import fullsave
from left_exploration_resume_contract_v1 import KEY,same
info=fullsave(p,count=20000);c=torch.load(p,map_location='cpu',weights_only=False);s=torch.load(m['source']['path'],map_location='cpu',weights_only=False)
delta=[float(c['optimizer_state_dict']['state'][i]['step'])-float(s['optimizer_state_dict']['state'][i]['step']) for i in range(17)]
assert len(set(delta))==1 and delta[0]>0 and delta[0]%20==0
actor=sum(not torch.equal(v,s['actor_state_dict'][k]) for k,v in c['actor_state_dict'].items());assert actor==9
assert same(c[KEY],s[KEY]) and c['E1_terrain_state']['num_envs']==20000
dispatch=json.loads((R/'left_formal3600_v1/DISPATCH_RECEIPT.json').read_bytes())
proofs=[]
for q in p.parent.glob('*STARTUP*VERIFIED.json'):
 v=json.loads(q.read_bytes());assert v['pid']==dispatch['child']['pid'] and v['source_sha256']==m['source']['sha256']
 if 'passed' in v:assert v['passed'] is True
 for k,z in v.items():
  if k.endswith('_exact') or k.endswith('_verified') or k in ('actor_critic_std_exact','optimizer_loaded_original_path','global_CPU_CUDA_streams_restored','sensor_streams_restored','all_episode_counters_incremented_once'):assert z is True,(q.name,k)
 if q.name=='LEFT_EXPLORATION_RESUME_STARTUP_VERIFIED.json':assert v['explicit_one_time_left_mean_std_initialization'] is False and v['same_left_branch_restored_exact'] is True
 proofs.append(dict(path=str(q),sha256=hashlib.sha256(q.read_bytes()).hexdigest(),proof=v))
assert len(proofs)==13 and not torch.cuda.is_initialized()
raw=(R/'left_formal3600_v1/worker_stdout.log').read_bytes();assert all(x not in raw for x in (b'buffer overflow detected',b'Contacts have been dropped',b'PhysX scene is corrupted',b'CUDA error',b'Traceback (most recent call last)'))
h=json.loads((p.parent/'CLOCK_TRAINING_HEALTH.json').read_bytes());assert h['integrity_task_reset_events']==h['unknown_task_reset_events']==0 and not h['nonfinite_observed'] and h['stop_reason'] is None
assert h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact']
g=json.loads((R/'left_formal3600_v1/GUARDIAN_CURRENT.json').read_bytes())
print(json.dumps(dict(epoch=time.time(),passed=True,own_checkpoint=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),source=m['source'],actual_fullsave=info,saved_updates=int(delta[0]/20),saved_controls=int(delta[0]/20)*24,saved_envsteps=int(delta[0]/20)*480000,saved_callbacks=int(delta[0]/20)*96,actor_tensors_changed=actor,optimizer_step_delta=delta[0],thirteen_actual_startup=proofs,health_latest_separate_from_saved_controls=h,guardian_snapshot=g,original_worker_stdout_SHA=hashlib.sha256(raw).hexdigest(),own_dispatch=dispatch,formal_final_claimed=False,qualified50=False)))
'''
def main():
 c=connect_linux_only();sf=None
 try:
  si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+PY+' -',timeout=60);si.write('ROOT='+repr(R)+'\n'+CODE);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status()
  stamp=str(time.time_ns());q=D/'reports'/('LEFT_FIRST_FORMAL_SAVED_CPU_REMOTE_'+stamp+'.json');q.write_text(json.dumps(dict(code=rc,stdout=out.decode(),stderr=err.decode()),indent=2),encoding='utf8');assert rc==0,str(q);v=json.loads(out)
  if v.get('pending_own_complete_save'):print(json.dumps(v));return
  dest=D/('left_first_formal_ownsave_'+stamp);dest.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(60);names=[v['own_checkpoint']]+[x['path'] for x in v['thirteen_actual_startup']]+[R+'/LEFT_FORMAL_ADMISSION_MANIFEST.json',R+'/left_formal3600_v1/DISPATCH_RECEIPT.json']
  rows=[]
  expected={v['own_checkpoint']:v['sha256'],**{x['path']:x['sha256'] for x in v['thirteen_actual_startup']}}
  for i,name in enumerate(names):
   p=dest/(str(i)+'_'+name.rsplit('/',1)[1]);sf.get(name,str(p),max_concurrent_prefetch_requests=16);h=hashlib.sha256(p.read_bytes()).hexdigest()
   if name in expected:rh=expected[name]
   else:
    with sf.open(name,'rb') as f:rh=hashlib.file_digest(f,'sha256').hexdigest()
   assert h==rh and p.stat().st_size==sf.stat(name).st_size
   rows.append(dict(remote_path=name,local_path=str(p),bytes=p.stat().st_size,sha256=h))
  assert rows[0]['sha256']==v['sha256']
  q=D/'reports'/('LEFT_FIRST_FORMAL_POSITIVE_SAVED_ACTUAL_'+stamp+'.json');q.write_text(json.dumps(dict(epoch=time.time(),remote_CPU=v,two_host_byteSHA_exact=rows),indent=2),encoding='utf8')
  print(json.dumps(dict(report=str(q),own_SHA=v['sha256'],saved_updates=v['saved_updates'],saved_envsteps=v['saved_envsteps'],actor9=v['actor_tensors_changed'],Adamdelta=v['optimizer_step_delta'],formal_final=False)))
 finally:
  if sf:sf.close()
  c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
