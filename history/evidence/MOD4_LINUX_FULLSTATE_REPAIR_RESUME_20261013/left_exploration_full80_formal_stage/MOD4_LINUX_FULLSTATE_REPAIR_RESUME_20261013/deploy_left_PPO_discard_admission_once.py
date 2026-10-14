"""Actual native-own-source admission into one new four-update PPO discard."""
from pathlib import Path
import json,os,time,hashlib
from read_linux_resume_boundary_actual import connect_linux_only
D=Path(__file__).resolve().parent
ROOT='/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_exploration20k_target_CPU_v1'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def main():
 proof=D/'reports/LEFT_NATIVE_GPU_OWN0PPO_INDEPENDENT_CPU_PASSED.json';v=json.loads(proof.read_bytes());assert v['passed'] and v['no_PPO'] and v['ownactual_checkpoint']['sha256']=='1e776d3b9935119f7b6c0c321509b8acdcee1bf4cbb140c2abf2d6d3eb907022'
 assert not (D/'reports/LEFT_DISCARD4_PPO_DISPATCH_ACTUAL.json').exists()
 name='left_PPO_discard_admission_parent_v1.py';compile((D/name).read_text(),name,'exec')
 c=connect_linux_only();sf=None
 try:
  sf=c.open_sftp();sf.put(str(D/name),ROOT+'/'+name);sf.put(str(proof),ROOT+'/LEFT_NATIVE_INDEPENDENT_CPU_LOCAL_PROOF.json');sf.close();sf=None
  code=r'''
from pathlib import Path
import json,hashlib,sys,torch,fcntl,subprocess,time,psutil,shutil
R=Path(ROOT);m=json.loads((R/'LEFT_NATIVE_GPU_ADMISSION_MANIFEST.json').read_bytes())
own=json.loads((R/'LEFT_NATIVE_OWN_FULLSAVE0PPO_PASSED.json').read_bytes());assert own['passed'] and own['PPO_updates']==0
assert json.loads((R/'LEFT_NATIVE_INDEPENDENT_CPU_LOCAL_PROOF.json').read_bytes())['passed']
assert not (R/'LEFT_PPO_DISCARD_ADMISSION_MANIFEST.json').exists() and not (R/'LEFT_DISCARD4_PPO_DISPATCH_RECEIPT.json').exists()
ex=json.loads((R/'left_native0PPO_v1/EXIT_RECEIPT.json').read_bytes());assert ex['returncode']==0 and ex['child_actually_absent'] and ex['canonical_bytes_unchanged']
assert not Path('/proc',str(ex['child']['pid'])).exists()
source=Path(own['checkpoint']);assert hashlib.sha256(source.read_bytes()).hexdigest()==own['sha256']=='1e776d3b9935119f7b6c0c321509b8acdcee1bf4cbb140c2abf2d6d3eb907022'
sys.path[:0]=[str(R),str(R/'isaac/mod4')]
from wave50_lifetime_fullsave_cpu import fullsave
info=fullsave(source,count=20000);ck=torch.load(source,map_location='cpu',weights_only=False)
assert ck['LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION']['source_SHA']=='1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06'
assert float(ck['actor_state_dict']['distribution.std_param'][0])==1 and not torch.cuda.is_initialized()
for p in (Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock'),Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True).strip()
assert psutil.virtual_memory().available>=55000000000 and shutil.disk_usage(R).free>=30000000000
q=R/'left_PPO_discard_admission_parent_v1.py';assert hashlib.sha256(q.read_bytes()).hexdigest()==PARENTSHA;compile(q.read_text(),str(q),'exec')
new=dict(m);new['source']=dict(path=str(source),sha256=own['sha256'],bytes=source.stat().st_size);new['sourcefreeze']=list(m['sourcefreeze'])+[dict(path=str(q),bytes=q.stat().st_size,sha256=PARENTSHA)]
new.update(num_envs=20000,seed=20260928,approved_GPU_native0PPO=False,approved_PPO_discard4_only=True,approved_formal_PPO=False,full_native_own_source_GPU_and_CPU_actual_passed=True,source_CPU_actual_fullcontract=info,discard_trained_weights_not_source=True,original_parameters_unchanged_except_prior_approved_left_initialization=True)
with (R/'LEFT_PPO_DISCARD_ADMISSION_MANIFEST.json').open('x') as f:json.dump(new,f,indent=2)
argv=[PY,'-u',str(q)]
p=subprocess.Popen(argv,cwd=R,stdout=(R/'left_discard4_parent_stdout.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True)
ticks=int(Path('/proc',str(p.pid),'stat').read_text().split(') ',1)[1].split()[19])
row=dict(epoch=time.time(),pid=p.pid,start_ticks=ticks,argv=argv,cwd=ROOT,source_SHA=own['sha256'],new_unique_PPO_discard4_only=True,formal_NOT_dispatched=True,actual_PPO_positive_save_still_pending=True)
(R/'LEFT_DISCARD4_PPO_DISPATCH_RECEIPT.json').write_text(json.dumps(row,indent=2));print(json.dumps(row))
'''
  si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+PY+' -',timeout=65)
  # CPU parent starts with CUDA_VISIBLE_DEVICES restored for its child; it has not initialized CUDA.
  prefix='ROOT='+repr(ROOT)+'\nPY='+repr(PY)+'\nPARENTSHA='+repr(hashlib.sha256((D/name).read_bytes()).hexdigest())+'\n'
  code=code.replace("argv=[PY,'-u',str(q)]","import os\nos.environ.pop('CUDA_VISIBLE_DEVICES',None)\nargv=[PY,'-u',str(q)]")
  si.write(prefix+code);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status()
  p=D/'reports/LEFT_DISCARD4_PPO_DISPATCH_ACTUAL.json';p.write_text(json.dumps(dict(epoch=time.time(),code=rc,stdout=out.decode(),stderr=err.decode()),indent=2),encoding='utf8');assert rc==0,str(p);print(out.decode())
 finally:
  if sf:sf.close()
  c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
