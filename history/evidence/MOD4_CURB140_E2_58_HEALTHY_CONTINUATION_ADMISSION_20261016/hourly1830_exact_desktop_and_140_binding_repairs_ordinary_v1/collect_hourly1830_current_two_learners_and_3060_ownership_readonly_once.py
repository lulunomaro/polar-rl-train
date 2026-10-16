"""One bounded read per host, no runtime/task/lock/ledger mutation."""
from pathlib import Path
import sys,os,json,time,getpass,traceback,importlib.util
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';sys.path.insert(0,str(D));from deploy_two_exact_source_continuation_native_cohort_once import code,connect72,t,S,T,PY
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
READ=r'''
from pathlib import Path
import sys,time,json,psutil
B=Path(sys.argv[1]);kind=sys.argv[2];paths=[B/x for x in ('OWNER_CURRENT.json','OWNER_ORIGINAL_ERROR.json','OWNER_EXIT_ACTUAL.json','COHORT_FINAL.json','NODE_CURRENT.json','NODE_ORIGINAL_ERROR.json','NODE_TERMINAL_ACTUAL.json','NODE_EXIT_ACTUAL.json')];out=B/'job0'/('production_only' if kind=='curb' else 'production');paths+=[out/x for x in ('FINAL.json','latest_complete.json')];files=[]
for p in paths:
 if p.exists():files.append(dict(path=str(p),value=json.loads(p.read_bytes())))
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(str(B)+'/' in x for x in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
v=dict(epoch=time.time(),files=files,actual_own_processes=procs,no_runtime_mutation=True)
if kind=='curb':
 C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());v['canonical']={k:c[k] for k in ('active_segment','authorized_training_seconds','charged_training_seconds','remaining_training_seconds')};v['own_closed_segments']=[x for x in c['completed_segments'] if str(x.get('kind','')).startswith('Linux_TWO_DISTINCT_CURB35_E2_HEALTHY_CONTINUATIONS_')]
print(json.dumps(v))
'''
GPU249=r'''
from pathlib import Path
import os,json,time,psutil,subprocess,msvcrt
g=subprocess.run(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],capture_output=True,text=True,timeout=20);rows=[]
for line in g.stdout.splitlines():
 try:
  pid=int(line.split(',')[0]);p=psutil.Process(pid);rows.append(dict(pid=pid,creation=p.create_time(),name=p.name(),exe=p.exe(),argv=p.cmdline(),root=p.cwd()))
 except (ValueError,psutil.Error) as e:rows.append(dict(raw=line,unresolved=repr(e)))
lock=Path('D:/MOD4_async_eval/worker.lock');held=None
if lock.exists():
 with lock.open('rb') as f:
  try:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
  except OSError:held=True
  else:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1);held=False
root=Path('D:/MOD4_async_eval/MOD4_CURB140_E2_58_HEALTHY_CONTINUATION_ADMISSION_20261016/curb140_frozen35_3060_v1');print(json.dumps(dict(epoch=time.time(),GPU_processes=rows,shared_worker_lock_actual_held=held,new_eval_root_exists=root.exists(),GPU_snapshot=subprocess.check_output(['nvidia-smi','--query-gpu=index,name,memory.used,memory.free','--format=csv,noheader,nounits']).decode(),no_process_or_Task_or_GPU_change=True)))
'''
def main():
 put('HOURLY1830_SEQUENTIAL_READONLY_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),only_actual_alive_exclusive_210_72_249_transport_owner=True,no_GPU_or_learning_or_budget_write=True));pw=getpass.getpass('Host72 hourly ownscope read-only password (hidden): ');c=None;v={}
 try:
  c=t.connect();v['source']=code(c,t.PY,READ,S,'curb')
 except BaseException:v['source_original_error']=traceback.format_exc()
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;v['target']=code(c,PY,READ,T,'e2')
 except BaseException:v['target_original_error']=traceback.format_exc()
 finally:
  pw=None
  if c:c.close();c=None
 spec=importlib.util.spec_from_file_location('actual249_role_transport',W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014/transport_249_bodyframe_current_terminal_role_v3.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 try:
  c=m.connect();v['eval249']=m.py(c,GPU249);m.ROOT='D:/MOD4_async_eval/'+D.name+'/curb140_frozen35_3060_v1'
  try:v['eval249_strict_guard']=m.py(c,m.guard_code())
  except BaseException:v['eval249_original_guard_rejection']=traceback.format_exc()
 except BaseException:v['eval249_connect_original_error']=traceback.format_exc()
 finally:m.close(c)
 v['epoch']=time.time();v['local_lookup_miss_this_hour']='eval_payload_v2/run_new_CURB35_native_full_finite_v3_once.py absent; no runtime command based on absent source';put('HOURLY1830_TWO_CONTINUATIONS_3060_OWNERSHIP_READONLY_ACTUAL.json',v);print(json.dumps(dict(epoch=v['epoch'],source_own_processes=v.get('source',{}).get('actual_own_processes'),target_own_processes=v.get('target',{}).get('actual_own_processes'),source_closed=v.get('source',{}).get('own_closed_segments'),GPU249=v.get('eval249'),guard_passed='eval249_strict_guard' in v,errors=[x for x in v if 'error' in x or 'rejection' in x])),flush=True)
if __name__=='__main__':main()
