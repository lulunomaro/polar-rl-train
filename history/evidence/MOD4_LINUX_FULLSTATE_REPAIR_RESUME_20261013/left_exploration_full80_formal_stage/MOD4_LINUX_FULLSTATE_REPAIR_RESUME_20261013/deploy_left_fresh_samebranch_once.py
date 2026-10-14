"""One new zero-control zero-PPO fresh process from the native own source, after discard exit."""
from pathlib import Path
import json,os,time,hashlib
from read_linux_resume_boundary_actual import connect_linux_only
D=Path(__file__).resolve().parent
ROOT='/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_exploration20k_target_CPU_v1'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
names=('left_exploration_worker_v2.py','left_fresh_samebranch_parent_dict_reviewed_v2.py')
def main():
 assert not (D/'reports/LEFT_FRESH0PPO_DISPATCH_ACTUAL.json').exists()
 for n in names:compile((D/n).read_text(),n,'exec')
 c=connect_linux_only();sf=None
 try:
  sf=c.open_sftp()
  for n in names:sf.put(str(D/n),ROOT+'/'+n)
  sf.close();sf=None
  code=r'''
from pathlib import Path
import json,hashlib,sys,torch,fcntl,subprocess,time,psutil,shutil,os
R=Path(ROOT);m=json.loads((R/'LEFT_NATIVE_GPU_ADMISSION_MANIFEST.json').read_bytes());own=json.loads((R/'LEFT_NATIVE_OWN_FULLSAVE0PPO_PASSED.json').read_bytes())
assert own['passed'] and own['PPO_updates']==0
discard=json.loads((R/'LEFT_DISCARD4_PPO_PASSED.json').read_bytes());assert discard['discarded_preflight'] and discard['actual_saved_updates']==4 and discard['optimizer_step_delta']==80 and discard['not_own_formal_source']
ex=json.loads((R/'left_discard4PPO_v1/EXIT_RECEIPT.json').read_bytes());assert ex['returncode']==0 and ex['child_actually_absent'] and ex['canonical_cost_charged_once'] and not ex['physics_capacity_error']
assert not Path('/proc',str(ex['child']['pid'])).exists()
assert not (R/'LEFT_FRESH_GPU_ADMISSION_MANIFEST.json').exists()
source=Path(own['checkpoint']);assert hashlib.sha256(source.read_bytes()).hexdigest()==own['sha256']=='1e776d3b9935119f7b6c0c321509b8acdcee1bf4cbb140c2abf2d6d3eb907022'
assert str(source)!=discard['own_checkpoint']
sys.path[:0]=[str(R),str(R/'isaac/mod4')]
from wave50_lifetime_fullsave_cpu import fullsave
info=fullsave(source,count=20000);assert not torch.cuda.is_initialized()
for p in (Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock'),Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True).strip()
assert psutil.virtual_memory().available>=55000000000 and shutil.disk_usage(R).free>=30000000000
rows=list(m['sourcefreeze'])
for n,h in HASHES.items():
 q=R/n;assert hashlib.sha256(q.read_bytes()).hexdigest()==h;compile(q.read_text(),str(q),'exec');rows.append(dict(path=str(q),sha256=h,bytes=q.stat().st_size))
new=dict(m);new.update(source=dict(path=str(source),sha256=own['sha256'],bytes=source.stat().st_size),sourcefreeze=rows,approved_GPU_native0PPO=False,approved_GPU_fresh0PPO=True,approved_PPO=False,num_envs=20000,seed=20260928,own_native_source_CPU_contract=info,actual_preflight4Passed_but_weights_discarded=True,actual_zero_controls_zero_PPO_fresh_branch=True,initializer_repeat_forbidden=True)
with (R/'LEFT_FRESH_GPU_ADMISSION_MANIFEST.json').open('x') as f:json.dump(new,f,indent=2)
os.environ.pop('CUDA_VISIBLE_DEVICES',None)
argv=[PY,'-u',str(R/'left_fresh_samebranch_parent_dict_reviewed_v2.py')]
p=subprocess.Popen(argv,cwd=R,stdout=(R/'left_fresh_parent_stdout.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True)
ticks=int(Path('/proc',str(p.pid),'stat').read_text().split(') ',1)[1].split()[19])
row=dict(epoch=time.time(),pid=p.pid,start_ticks=ticks,argv=argv,cwd=ROOT,source_SHA=own['sha256'],source_is_own_native0PPO_not_discardtrained=True,source_envs=20000,only_fresh_zero_control_zero_PPO=True,formal_NOT_dispatched=True,actual13_restore_pass_still_pending=True)
(R/'LEFT_FRESH0PPO_DISPATCH_RECEIPT.json').write_text(json.dumps(row,indent=2));print(json.dumps(row))
'''
  prefix='ROOT='+repr(ROOT)+'\nPY='+repr(PY)+'\nHASHES='+repr({n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in names})+'\n'
  si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+PY+' -',timeout=65);si.write(prefix+code);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status()
  p=D/'reports/LEFT_FRESH0PPO_DISPATCH_ACTUAL.json';p.write_text(json.dumps(dict(epoch=time.time(),code=rc,stdout=out.decode(),stderr=err.decode()),indent=2),encoding='utf8');assert rc==0,str(p);print(out.decode())
 finally:
  if sf:sf.close()
  c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
