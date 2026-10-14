"""One independent bounded formal from admitted whole20k fresh retained save."""
from pathlib import Path
import json,hashlib,time,os
from read_linux_resume_boundary_actual import connect_linux_only
D=Path(__file__).resolve().parent;W=D.parent
N='/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_exploration20k_target_CPU_v1'
R='/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_exploration20k_first_formal_v1'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
FILES={n:D/n for n in ('left_exploration_worker_v3.py','left_first_formal_retained_parent_v2.py')}
FILES.update({n:D/'reports'/n for n in ('LEFT_FRESH_RETAINED_LOCAL_CPU_PASSED.json','LEFT_NATIVE_GPU_OWN0PPO_INDEPENDENT_CPU_PASSED.json','LEFT_FORMAL_RETAINED_CONSUMERS_CPU_PREPARED.json')})
FILES['FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json']=W/'MOD4_3060_FULL80_FROZEN_CURRENT_20261014/reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json'
FILES['FULL80_FULL1500_INDEPENDENT_CPU_DATA_ACTUAL_REVIEW.json']=W/'MOD4_3060_FULL80_FROZEN_CURRENT_20261014/reports/FULL80_FULL1500_INDEPENDENT_CPU_DATA_ACTUAL_REVIEW.json'
PREP=r'''
from pathlib import Path
import json,hashlib,shutil,fcntl,subprocess,psutil,os
R=Path(ROOT);N=Path(OLD);assert not R.exists()
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');d=json.loads(B.read_bytes())
assert d['active_segment'] is None and d['authorized_training_seconds']==1188000 and len(d['budget_extensions'])==7
assert 36000+sum(x['additional_training_seconds'] for x in d['budget_extensions'])==1188000 and d['remaining_training_seconds']>68400
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True).strip()
assert psutil.virtual_memory().available>=55000000000 and shutil.disk_usage(N).free>=30000000000
m=json.loads((N/'LEFT_NATIVE_GPU_ADMISSION_MANIFEST.json').read_bytes())
fresh=json.loads((N/'LEFT_FRESH_RETAINED_INDEPENDENT_POSTEXIT_CPU_PASSED.json').read_bytes());assert fresh['passed'] and fresh['original_parent_passed'] is False and fresh['PPO_updates']==0
discard=json.loads((N/'LEFT_DISCARD4_PPO_PASSED.json').read_bytes());assert discard['actual_saved_updates']==4 and discard['optimizer_step_delta']==80 and discard['discarded_preflight']
R.mkdir();rows=[]
for x in m['sourcefreeze']:
 p=Path(x['path']);assert p.is_relative_to(N) and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
 q=R/p.relative_to(N);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert hashlib.sha256(q.read_bytes()).hexdigest()==x['sha256']
 rows.append(dict(path=str(q),origin=str(p),bytes=q.stat().st_size,sha256=x['sha256']))
for name in ('LEFT_FRESH_RETAINED_INDEPENDENT_POSTEXIT_CPU_PASSED.json','LEFT_DISCARD4_PPO_PASSED.json','LEFT_NATIVE_OWN_FULLSAVE0PPO_PASSED.json'):
 shutil.copy2(N/name,R/name)
(R/'ACTUAL_BASE_SOURCEFREEZE.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(dict(prepared_new_root=ROOT,original_files_byteexact=len(rows),GPU_dispatched=False)))
'''
LAUNCH=r'''
from pathlib import Path
import json,hashlib,time,sys,torch,os,subprocess,ast
R=Path(ROOT);N=Path(OLD)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for n,h in HASHES.items():assert sha(R/n)==h
local=json.loads((R/'LEFT_FRESH_RETAINED_LOCAL_CPU_PASSED.json').read_bytes());assert local['passed'] and local['original_parent_passed'] is False
native=json.loads((R/'LEFT_NATIVE_GPU_OWN0PPO_INDEPENDENT_CPU_PASSED.json').read_bytes());assert native['passed']
f=json.loads((R/'LEFT_FRESH_RETAINED_INDEPENDENT_POSTEXIT_CPU_PASSED.json').read_bytes());assert f['passed'] and f['sha256']==local['own_source']['sha256']=='06a1ea73a943a7bd6fbb3626077f55b9ac06521f814f956cfb1d546074bbf5c2'
full80=json.loads((R/'FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json').read_bytes());assert full80['passed'] and full80['qualified50'] is False
assert json.loads((R/'FULL80_FULL1500_INDEPENDENT_CPU_DATA_ACTUAL_REVIEW.json').read_bytes())['passed']
sys.path[:0]=[str(R),str(R/'isaac/mod4')]
from wave50_lifetime_fullsave_cpu import fullsave
info=fullsave(f['checkpoint'],count=20000);assert sha(f['checkpoint'])==f['sha256']
assert not torch.cuda.is_initialized()
rows=json.loads((R/'ACTUAL_BASE_SOURCEFREEZE.json').read_bytes())
for n,h in HASHES.items():
 p=R/n
 if n.endswith('.py'):compile(p.read_text(),str(p),'exec')
 rows.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h))
for n in ('LEFT_FRESH_RETAINED_INDEPENDENT_POSTEXIT_CPU_PASSED.json','LEFT_DISCARD4_PPO_PASSED.json','LEFT_NATIVE_OWN_FULLSAVE0PPO_PASSED.json'):
 p=R/n;rows.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
old=json.loads((N/'LEFT_NATIVE_GPU_ADMISSION_MANIFEST.json').read_bytes())
m=dict(epoch=time.time(),num_envs=20000,seed=20260928,new_axis_first_formal_seconds=3600,source=dict(path=f['checkpoint'],sha256=f['sha256'],bytes=f['bytes']),sourcefreeze=rows,original_environment=old['original_environment'],actual_native0PPO_independent_CPU_passed=True,actual_discard4_PPO_passed=True,actual_fresh0PPO_passed=True,fresh_original_parent_passed=False,fresh_independent_retained_save_passed=True,actual_original80_full1500_data_reviewed=True,source_is_fresh_own0PPO_not_discardtrained=True,whole20k_target_CPU=info,original_full80_other_three_skills_pending=True,qualified50=False)
q=R/'LEFT_FORMAL_ADMISSION_MANIFEST.json';assert not q.exists()
with q.open('x') as z:json.dump(m,z,indent=2);z.flush();os.fsync(z.fileno())
os.environ.pop('CUDA_VISIBLE_DEVICES',None)
os.environ.pop('MOD4_LEFT_ADMISSION_MODE',None)
argv=[PY,'-u',str(R/'left_first_formal_retained_parent_v2.py')]
p=subprocess.Popen(argv,cwd=R,stdout=(R/'left_formal_parent_stdout.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True)
row=dict(epoch=time.time(),pid=p.pid,start_ticks=int(Path('/proc',str(p.pid),'stat').read_text().split(') ',1)[1].split()[19]),argv=argv,cwd=ROOT,source=m['source'],manifest_SHA=sha(q),actual_sourcefreeze_count=len(rows),first_bounded_formal_seconds=3600,actual_startup_PPO_proof_pending=True,qualified50=False)
(R/'LEFT_FORMAL_DISPATCH_ACTUAL.json').write_text(json.dumps(row,indent=2));print(json.dumps(row))
'''
def run(c,code,label):
 si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+PY+' -',timeout=75);si.write('ROOT='+repr(R)+'\nOLD='+repr(N)+'\nPY='+repr(PY)+'\nHASHES='+repr({n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in FILES.items()})+'\n'+code);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status()
 p=D/'reports'/(label+'_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(code=rc,stdout=out.decode(),stderr=err.decode()),indent=2),encoding='utf8');assert rc==0,str(p);return json.loads(out)
def main():
 assert not (D/'reports/LEFT_FIRST_FORMAL_DISPATCH_ACTUAL.json').exists()
 for n,p in FILES.items():assert p.is_file()
 c=connect_linux_only();sf=None
 try:
  run(c,PREP,'LEFT_FORMAL_NEWROOT_TARGET_CPU_PREPARED')
  sf=c.open_sftp()
  for n,p in FILES.items():sf.put(str(p),R+'/'+n)
  sf.close();sf=None
  v=run(c,LAUNCH,'LEFT_FORMAL_TARGET_CPU_UNIQUE_DISPATCH')
  (D/'reports/LEFT_FIRST_FORMAL_DISPATCH_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
 finally:
  if sf:sf.close()
  c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
