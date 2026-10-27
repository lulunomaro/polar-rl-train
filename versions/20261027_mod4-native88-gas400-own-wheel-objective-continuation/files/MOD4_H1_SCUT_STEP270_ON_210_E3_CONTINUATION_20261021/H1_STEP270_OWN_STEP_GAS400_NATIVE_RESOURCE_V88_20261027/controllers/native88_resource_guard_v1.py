"""Own recorded PID/create only; original private/shared resource locks, no peer scan."""
from pathlib import Path
import os,json,hashlib,fcntl,subprocess,psutil,shutil,time
from native88_protocol_v1 import SOURCES,require
def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def recorded_own_out(rows,backend,*,process=psutil.Process,no_such=psutil.NoSuchProcess):
 require(isinstance(rows,list) and rows,'known source process receipt required');observed=[]
 for row in rows:
  require(set(row)=={'role','execution_backend','pid','creation'} and row['execution_backend'] in ('source210','target72') and type(row['pid']) is int and row['pid']>0 and type(row['creation']) in (int,float) and row['creation']>0,'typed original own PID/create')
  if row['execution_backend']!=backend:continue
  try:
   p=process(row['pid']);creation=p.create_time()
  except no_such:observed.append(dict(role=row['role'],original_owned_process_out=True));continue
  require(creation!=row['creation'],'original owned process still present: '+row['role'])
  observed.append(dict(role=row['role'],original_owned_process_out_PID_recycled=True,no_foreign_identity_query=True))
 return observed
def acquire(spec,B):
 B=Path(B).resolve();key=spec['key'];require(key in SOURCES and spec['GPU_UUID']==SOURCES[key]['GPU_UUID'] and spec['execution_backend']==SOURCES[key]['execution_backend'],'only two own H1 cards')
 owned=Path('/mnt/mod4_linux_durable_20261013' if spec['execution_backend']=='source210' else '/home/lc01/Zonglin Li/zonglin2')
 require(B.is_relative_to(owned.resolve()),'new runtime path containment')
 if spec['execution_backend']=='source210':require(owned.is_mount(),'actual expanded original durable volume required')
 source=Path(spec['previous_runtime_root']).resolve();require(source.is_relative_to(owned.resolve()) and source!=B,'previous source own root')
 e=json.loads((source/'NODE_EXIT_ACTUAL.json').read_bytes());terminal=json.loads((source/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row']
 require(e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and terminal['terminal_all_own_children_waited'] and terminal['returncode']==0 and not terminal['original_error'] and not terminal['errors'] and terminal['final']['passed'],'original R5 source/allout')
 require(terminal['final']['final']['SHA']==spec['source_SHA'],'previous native final source SHA')
 contract=json.loads((B/'NATIVE88_SOURCE_CONTRACT_ACTUAL.json').read_bytes())
 rowpath=B/contract['known_own_processes_relative'];require(rowpath.resolve().is_relative_to(B) and H(rowpath)==contract['known_own_processes_SHA'],'actual own process proof pin')
 actual=recorded_own_out(json.loads(rowpath.read_bytes())['rows'],spec['execution_backend'])
 require(spec['private_lock']==contract['previous_R5_private_lock'],'exact original own private GPU lock')
 lockpath=Path(spec['private_lock']);lock=lockpath.open('rb+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 try:
  if spec['execution_backend']=='target72':
   with (owned/'state/finite_environment_validation.lock').open('rb+') as shared:
    fcntl.flock(shared,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(shared,fcntl.LOCK_UN)
  applications=subprocess.check_output(['nvidia-smi','-i',spec['GPU_UUID'],'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
  require(spec['GPU_UUID'] not in applications,'selected GPU occupied; leave user processes untouched')
  line=subprocess.check_output(['nvidia-smi','-i',spec['GPU_UUID'],'--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).strip()
  values=line.split(',');require(values[0].strip()==spec['GPU_UUID'] and int(values[1])>15669,'original native empty GPU floor')
  ram=psutil.virtual_memory().available;disk=shutil.disk_usage(B).free
  require(ram>32*1024**3 and disk>25*1024**3,'native4096 RAM32/postcopydisk25 floor')
  value=dict(epoch=time.time(),private_lock=str(lockpath),actual_private_GPU_fcntl_acquired=True,previous_root=str(source),actual_recorded_own_out=actual,GPU_line=line,RAM_available=ram,durable_free=disk,unknown16828_identity_not_queried=True,no_process_enumeration_or_foreign_argv_or_exe=True,no_account_write=True,shared_validation_brief_only=True)
  with (B/'OWN_GPU_PREVIOUS_ACTUAL_OUT_FCNTL_ACQUIRED.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
  return lock
 except BaseException:
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close();raise
