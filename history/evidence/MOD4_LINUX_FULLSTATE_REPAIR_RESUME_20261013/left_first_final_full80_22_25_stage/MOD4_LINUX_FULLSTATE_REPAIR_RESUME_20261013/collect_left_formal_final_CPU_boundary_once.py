"""Readonly own final and sole settlement, bounded artifact transport, no GPU."""
from pathlib import Path
import json,time,os,hashlib
from read_linux_resume_boundary_actual import connect_linux_only
D=Path(__file__).resolve().parent
R='/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_exploration20k_first_formal_v1'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
CODE=r'''
from pathlib import Path
import json,hashlib,sys,torch,time,psutil,fcntl
R=Path(ROOT);a=R/'left_formal3600_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
v=json.loads((R/'LEFT_FORMAL_SAVED_REVIEW_READY.json').read_bytes());m=json.loads((R/'LEFT_FORMAL_ADMISSION_MANIFEST.json').read_bytes())
assert v['actual_first_formal_window'] and not v['discarded_preflight'] and not (R/'LEFT_FORMAL_PARENT_ERROR.json').exists()
ex=json.loads((a/'EXIT_RECEIPT.json').read_bytes());dispatch=json.loads((a/'DISPATCH_RECEIPT.json').read_bytes())
assert ex['returncode']==0 and ex['child_actually_absent'] and ex['canonical_cost_charged_once'] and not ex['physics_capacity_error']
for row in (dispatch['parent'],dispatch['child']):assert not psutil.pid_exists(row['pid']) or psutil.Process(row['pid']).create_time()!=row['created']
assert (R/'GUARDIAN_EXIT.json').exists()
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');budget_before=sha(B);b=json.loads(B.read_bytes())
assert b['active_segment'] is None and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
segments=[s for s in b['completed_segments'] if s['kind']==ex['canonical_unique_segment']];assert len(segments)==1
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
for row in m['sourcefreeze']:assert sha(row['path'])==row['sha256'],row['path']
p=Path(v['own_checkpoint']);assert sha(p)==v['checkpoint_sha256']
sys.path[:0]=[str(R),str(R/'isaac/mod4')]
from wave50_lifetime_fullsave_cpu import fullsave
from left_exploration_resume_contract_v1 import same,KEY
from e1_terrain_training_health import learning_health_pass
info=fullsave(p,count=20000);c=torch.load(p,map_location='cpu',weights_only=False);s=torch.load(m['source']['path'],map_location='cpu',weights_only=False)
assert same(c[KEY],s[KEY])
delta=[float(c['optimizer_state_dict']['state'][i]['step'])-float(s['optimizer_state_dict']['state'][i]['step']) for i in range(17)]
assert len(set(delta))==1 and delta[0]==v['actual_saved_updates']*20>0
assert sum(not torch.equal(x,s['actor_state_dict'][k]) for k,x in c['actor_state_dict'].items())==9
markers=[]
for q in p.parent.glob('*STARTUP*VERIFIED.json'):
 z=json.loads(q.read_bytes());assert z['pid']==dispatch['child']['pid'] and z['source_sha256']==m['source']['sha256']
 if 'passed' in z:assert z['passed'] is True
 for k,t in z.items():
  if k.endswith('_exact') or k.endswith('_verified') or k in ('actor_critic_std_exact','optimizer_loaded_original_path','global_CPU_CUDA_streams_restored','sensor_streams_restored','all_episode_counters_incremented_once'):assert t is True,(q.name,k)
 if q.name=='LEFT_EXPLORATION_RESUME_STARTUP_VERIFIED.json':assert z['explicit_one_time_left_mean_std_initialization'] is False and z['same_left_branch_restored_exact'] is True
 markers.append(dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q)))
assert len(markers)==13
h=json.loads((p.parent/'CLOCK_TRAINING_HEALTH.json').read_bytes());assert learning_health_pass(h) and h['stop_reason'] is None and h['control_steps']==v['actual_saved_updates']*24 and h['actual_physics_callbacks']==h['control_steps']*4
raw=(a/'worker_stdout.log').read_bytes();assert all(x not in raw for x in (b'Traceback (most recent call last)',b'buffer overflow detected',b'Contacts have been dropped',b'PhysX scene is corrupted',b'CUDA error'))
assert not torch.cuda.is_initialized() and sha(B)==budget_before
files=[p,R/'LEFT_FORMAL_SAVED_REVIEW_READY.json',a/'EXIT_RECEIPT.json',a/'DISPATCH_RECEIPT.json',R/'GUARDIAN_EXIT.json',p.parent/'CLOCK_TRAINING_HEALTH.json',p.parent/'RETENTION_COMMAND_ACTUAL.json',a/'worker_stdout.log']
rows=[dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q)) for q in files]
print(json.dumps(dict(epoch=time.time(),passed=True,own_checkpoint=rows[0],actual_fullsave=info,saved_updates=v['actual_saved_updates'],envsteps=v['envsteps'],callbacks=v['callbacks'],actor9_changed=True,optimizer_step_delta=delta[0],thirteen_strict_marker_indices=markers,health=h,source=m['source'],sourcefreeze_count=len(m['sourcefreeze']),sourcefreeze_all_bytes_actual_verified=True,exit=ex,unique_canonical_segment=segments[0],actual_parent_child_guardian_exit_twofcntlFree_idle=True,no_budget_mutation=True,complete_files=rows,qualified50=False)))
'''
def main():
 q=D/'reports/LEFT_FORMAL_FINAL_ACTUAL_COLLECTION.json';assert not q.exists()
 c=connect_linux_only();sf=None
 try:
  si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+PY+' -',timeout=75);si.write('ROOT='+repr(R)+'\n'+CODE);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status()
  receipt=D/'reports'/('LEFT_FORMAL_FINAL_REMOTE_CPU_'+str(time.time_ns())+'.json');receipt.write_text(json.dumps(dict(code=rc,stdout=out.decode(),stderr=err.decode()),indent=2),encoding='utf8');assert rc==0,str(receipt);v=json.loads(out)
  dest=D/'left_formal_final_actual';assert not dest.exists();dest.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(60);rows=[]
  for i,row in enumerate(v['complete_files']):
   p=dest/(str(i)+'_'+row['path'].rsplit('/',1)[1]);sf.get(row['path'],str(p),max_concurrent_prefetch_requests=16)
   assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
   rows.append(dict(**row,local_path=str(p),two_host_byteSHA_exact=True))
  q.write_text(json.dumps(dict(epoch=time.time(),passed=True,actual_remote_review=v,collected_files=rows),indent=2),encoding='utf8')
  print(json.dumps(dict(report=str(q),checkpoint=v['own_checkpoint'],updates=v['saved_updates'],envsteps=v['envsteps'],ordinary=v['health']['ordinary_episode_reset_events'],parent_cost=v['exit']['parent_load_learn_save_exit_seconds'],actual_exit_idle=True)))
 finally:
  if sf:sf.close()
  c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
