"""New native-only GPU admission. Does not replay the completed formal parent."""
from pathlib import Path
import json,os,shlex,time,hashlib
from read_linux_resume_boundary_actual import connect_linux_only
D=Path(__file__).resolve().parent
BASE='/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013'
OLD=BASE+'/original_Linux20k_d05_continuation_runtime_assets_complete_v3'
NEW=BASE+'/left_exploration20k_target_CPU_v1'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
names=('left_exploration_resume_contract_v1.py','left_exploration_worker_v1.py','left_exploration_native_parent_v1.py')
def main():
 assert not (D/'reports/LEFT_NATIVE0PPO_DISPATCH_ACTUAL.json').exists()
 for name in names:compile((D/name).read_text(),name,'exec')
 c=connect_linux_only()
 try:
  code=r'''
from pathlib import Path
import json,hashlib,fcntl,subprocess,shutil
R=Path(NEW);O=Path(OLD)
assert json.loads((O/'INDEPENDENT_POSTEXIT_TYPED_SCHEMA_ACTUAL.json').read_bytes())['independent_postexit_pass']
assert json.loads((O/'FINAL_FULL_TRAINING_TRACE_CPU_ACTUAL.json').read_bytes())['passed']
assert not (R/'LEFT_NATIVE_GPU_ADMISSION_MANIFEST.json').exists()
assert json.loads((R/'TARGET_FULLSTATE107_CPU_PASSED.json').read_bytes())['passed_target_CPU_only']
for q in [Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock'),Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]:
 with q.open('r+b') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True).strip()
print(json.dumps(dict(idle=True,target_CPU_passed=True,durable_free=shutil.disk_usage(R).free)))
'''
  def run(code,label,timeout=60):
   si,so,se=c.exec_command('python3 -',timeout=timeout);si.write('OLD='+repr(OLD)+'\nNEW='+repr(NEW)+'\nPY='+repr(PY)+'\n'+code);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status()
   p=D/'reports'/(label+'.json');p.write_text(json.dumps(dict(epoch=time.time(),code=rc,stdout=out.decode(),stderr=err.decode()),indent=2),encoding='utf8');assert rc==0,str(p);return json.loads(out)
  run(code,'LEFT_NATIVE0PPO_PREUPLOAD_BOUNDARY_ACTUAL')
  sf=c.open_sftp()
  for n in names:sf.put(str(D/n),NEW+'/'+n)
  sf.close()
  code=r'''
from pathlib import Path
import json,hashlib,subprocess,time
R=Path(NEW);O=Path(OLD);m=json.loads((O/'ORIGINAL_LINUX_CONTINUATION_MANIFEST.json').read_bytes())
rows=json.loads((R/'LEFT_EXPLORATION_SOURCE_FREEZE_PREPARED.json').read_bytes())['actual_source_files']
for n in NAMES:
 p=R/n;assert hashlib.sha256(p.read_bytes()).hexdigest()==HASHES[n];compile(p.read_text(),n,'exec');rows.append(dict(path=str(p),sha256=HASHES[n],bytes=p.stat().st_size))
source=O/'formal/learning_logs/2026-10-14_00-51-56_E1_WAVE50_original_Linux20k_continuation/model_32447.pt'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06'
v=dict(epoch=time.time(),approved_GPU_native0PPO=True,approved_PPO=False,source=dict(path=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),bytes=source.stat().st_size),sourcefreeze=rows,original_environment=m['original_environment'],num_envs=20000,seed=20260928,new_one_time_left_mean_std_axis=True,original_allstate_exact_before_explicit_left_initializer=True,CPU_candidate_SHA='8ff1a32789364351e70ab23a7d96accf6cfdcdc670d1d352a6bea998d4b50d42',original_geometry_clockDRhardware_parameters_unchanged=True,no_qualified50_or_future_PPO_claim=True)
p=R/'LEFT_NATIVE_GPU_ADMISSION_MANIFEST.json'
with p.open('x') as f:json.dump(v,f,indent=2)
argv=[PY,'-u',str(R/'left_exploration_native_parent_v1.py')]
p=subprocess.Popen(argv,cwd=R,stdout=(R/'left_native_parent_stdout.log').open('xb'),stderr=subprocess.STDOUT,start_new_session=True)
ticks=int((Path('/proc')/str(p.pid)/'stat').read_text().split(') ',1)[1].split()[19])
receipt=dict(epoch=time.time(),pid=p.pid,start_ticks=ticks,argv=argv,cwd=NEW,approved_only_native0PPO=True,PPO_started=False,source_SHA=v['source']['sha256'],new_GPU_once_only=True)
(R/'LEFT_NATIVE0PPO_DISPATCH_RECEIPT.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
'''
  prefix='NAMES='+repr(names)+'\nHASHES='+repr({n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in names})+'\n'
  v=run(prefix+code,'LEFT_NATIVE0PPO_DISPATCH_ACTUAL');print(json.dumps(v))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
