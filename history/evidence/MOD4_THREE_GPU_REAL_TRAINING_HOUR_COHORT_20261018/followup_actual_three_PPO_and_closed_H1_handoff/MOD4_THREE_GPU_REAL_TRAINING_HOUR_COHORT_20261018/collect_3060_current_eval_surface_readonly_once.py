"""Prepare the auxiliary evaluator with one read-only current-state capture; no task/native or GPU launch."""
from pathlib import Path
import sys,os,time,json,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';sys.path.insert(0,str(W/'MOD4_H1_TARGET72_CLOSED_FINAL_E3_FROZEN_REVIEW_20261017'));import transport_249_E3_current_exact_desktop_2145_v1 as t
CODE=r'''
from pathlib import Path
import sys,os,json,time,subprocess,psutil,shutil,hashlib,importlib.util
sys.dont_write_bytecode=True
def run(*argv):
 try:
  p=subprocess.run(argv,capture_output=True,text=True,timeout=20);return dict(returncode=p.returncode,stdout=p.stdout.strip(),stderr=p.stderr.strip())
 except BaseException as e:return dict(error=repr(e))
root=Path('D:/MOD4_async_eval');own=[]
for p in psutil.process_iter(['pid','create_time','name','cmdline','cwd']):
 try:
  if p.pid!=os.getpid() and any(('MOD4' in str(x) and 'D:' in str(x)) for x in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
files=[]
for name in ('rsl_rl','isaaclab'):
 try:
  spec=importlib.util.find_spec(name);paths=list(spec.submodule_search_locations) if spec and spec.submodule_search_locations else [];rels=['runners/on_policy_runner.py','algorithms/ppo.py'] if name=='rsl_rl' else ['utils/math.py']
  for base in paths:
   for rel in rels:
    p=Path(base)/rel
    if p.is_file():files.append(dict(module=name,path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
 except BaseException as e:files.append(dict(module=name,error=repr(e)))
print(json.dumps(dict(epoch=time.time(),boot_epoch=psutil.boot_time(),host='10.24.4.249',current_user_sessions=run('query','user'),GPU=run('nvidia-smi','--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'),compute=run('nvidia-smi','--query-compute-apps=gpu_uuid,pid,process_name,used_memory','--format=csv,noheader,nounits'),current_owned_MOD4_processes=own,existing_owned_eval_root=root.exists(),D_free=shutil.disk_usage('D:/').free if Path('D:/').exists() else None,actual_installed_sources=files,no_desktop_creation_signature_or_MSVCRT_GPU_lease_claim=True,no_GPU_Task_or_training_or_budget_or_UI_change=True)))
'''
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
if __name__=='__main__':
 c=None
 try:
  put('CURRENT3060_EVAL_SURFACE_READER_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_alive_only_exclusive_all_transport=True,no_old_2145_PID_assumed_current=True));c=t.connect();v=t.py(c,CODE,90);put('CURRENT3060_EVAL_SURFACE_READONLY_ACTUAL.json',v);print(json.dumps(dict(authenticated_readonly=True,GPU=v['GPU'],compute=v['compute'],owned_processes=len(v['current_owned_MOD4_processes']),D_free=v['D_free'],sources=len(v['actual_installed_sources']),not_current_GPU_admission_or_Task=True)),flush=True)
 except BaseException:put('CURRENT3060_EVAL_SURFACE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_Task_or_training_interruption=True));raise
 finally:
  if c:c.close()
