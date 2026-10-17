"""Read actual current writer/GPU locks and new native raw metadata only; no old raw hash."""
from pathlib import Path
import os,sys,time,json,getpass,traceback,importlib.util
B=Path(__file__).resolve().parent;R=B/'reports';from deploy_H1_closed24_target72_new_native_original_handoff_once import a,SOURCE,TARGET
G=B.parent/'MOD4_TWO72_CLOSED_SOURCES_HEALTHY_NEXT_BLOCK_20261017';sys.path.insert(0,str(G));sp=importlib.util.spec_from_file_location('original_canonical_read_only_actual',G/'collect_existing_v5_actual_terminal_original_handoff_bounded_missing_final_only_once.py');f=importlib.util.module_from_spec(sp);sp.loader.exec_module(f)
LOCKS=r'''
from pathlib import Path
import os,sys,time,json,psutil
B=Path(sys.argv[1]);source=sys.argv[2]=='owner';i=json.loads((B/('OWNER_IDENTITY.json' if source else 'NODE_IDENTITY.json')).read_bytes());pid=i['pid'];actual=None
try:
 p=psutil.Process(pid);actual=dict(pid=p.pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd());assert abs(actual['creation']-i['creation'])<.01 and actual['argv']==i['argv']
except psutil.NoSuchProcess:pass
paths=[Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock'),Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')] if source else [Path(json.loads((B/'OWN_GPU_PREVIOUS_ACTUAL_OUT_FCNTL_ACQUIRED.json').read_bytes())['path'])]
raw=Path('/proc/locks').read_text();rows=[]
for p in paths:
 st=p.stat();key=f'{os.major(st.st_dev):02x}:{os.minor(st.st_dev):02x}:{st.st_ino}';lines=[line for line in raw.splitlines() if len(line.split())>5 and line.split()[5].lower()==key.lower()];held=any(line.split()[1]=='FLOCK' and line.split()[4]==str(pid) for line in lines);rows.append(dict(path=str(p),inode=st.st_ino,device=st.st_dev,proc_locks_matching_lines=lines,actual_recorded_owner_holds_real_fcntl=held))
print(json.dumps(dict(epoch=time.time(),root=str(B),recorded_identity=i,current_exact_identity=actual,real_OS_locks=rows,not_file_exists_lock_inference=True)))
'''
RAW=r'''
from pathlib import Path
import sys,json,time,subprocess
B=Path(sys.argv[1]);p=B/'job0/native/NATIVE180_PRELAUNCH_V2_COMPLETE_ACTUAL.json';v=json.loads(p.read_bytes());rows=[]
for key in ('controls_raw','physics_raw'):
 for row in v[key]:
  q=Path(row['path']);assert q.resolve().is_relative_to((B/'job0/native').resolve());s=q.stat();assert s.st_size==row['bytes'];rows.append(dict(kind=key,actual_worker_original_path_size_SHA=row,actual_current_inode=s.st_ino,actual_current_size=s.st_size,actual_current_mtime_ns=s.st_mtime_ns,no_raw_rehash_or_download=True))
print(json.dumps(dict(epoch=time.time(),native_complete_metadata=dict(source_SHA=v['source_SHA'],controls=v['controls'],callbacks=v['callbacks'],initial=v['initial'],saved=v['saved'],optimizer_updates=v['optimizer_updates']),native_raw_indices=rows,all_new_native_raw_originals_present_size_exact=True,gpu=subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,utilization.gpu,memory.used,memory.total','--format=csv,noheader,nounits']).decode(),compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name,used_gpu_memory','--format=csv,noheader,nounits']).decode(),no_old_native_Task_PT_or_raw_hash=True)))
'''
def main():
 v=json.loads((R/'H1_TARGET72_MISSING_NATIVE_FIRST_COMPLETE_MERGED_BOUND_COLLECTION_V2_ACTUAL.json').read_bytes());assert v['actual_return_hands_all_transport_back'];pw=getpass.getpass('Host72 current H1 OSlock and new native index only (hidden): ');c=None;out={}
 try:c=a.t.connect();out['source_owner']=a.code(c,a.t.PY,LOCKS,SOURCE,'owner',timeout=60);out['original_account']=a.code(c,a.t.PY,f.ACCOUNT,timeout=60)
 finally:a.t.close(c);c=None
 try:c=a.connect72(pw);pw=None;out['target_node']=a.code(c,a.PY,LOCKS,TARGET,'node',timeout=60);out['new_native_raw_index']=a.code(c,a.PY,RAW,TARGET,timeout=60)
 finally:
  pw=None
  if c:c.close()
 out.update(epoch=time.time(),actual_return_hands_all_transport_back=True,no_runtime_GPU_or_account_mutation=True)
 with (R/'H1_TARGET72_CURRENT_ORIGINAL_CANONICAL_REAL_OSLOCK_NATIVE_RAW_INDEX_ACTUAL.json').open('x',encoding='utf8') as h:json.dump(out,h,indent=2)
 print(json.dumps(dict(epoch=out['epoch'],owner_locks=out['source_owner']['real_OS_locks'],node_lock=out['target_node']['real_OS_locks'],GPU=out['new_native_raw_index']['gpu'],compute=out['new_native_raw_index']['compute'],native_raw_entries=len(out['new_native_raw_index']['native_raw_indices']),actual_transport_returned=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_TARGET72_REAL_LOCK_RAW_INDEX_READ_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as h:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_runtime_GPU_or_account_mutation=True),h,indent=2)
  raise
