"""Bounded read-only state; no retries, GPU/PPO/canonical writes."""
from pathlib import Path
import base64,json,time,sys
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';T=R+'/temporary_scope2048_memory20GB_left_repair_20261013'
def read(save=True):
 code="""from pathlib import Path;import psutil,json,time,msvcrt
t=Path('"""+T+"""');r=t.parent;out=dict(epoch=time.time(),scope=str(t),stages={})
for n in ('SEQUENCE_CURRENT_ACTUAL.json','SEQUENCE_ORIGINAL_ERROR.json','SEQUENCE_FINAL_ACTUAL.json','SEQUENCE_PARENT_OSLOCK_RELEASED_ACTUAL.json','OWN_REPAIRED_FULLRESTORE_SOURCE_ACTUAL.json','SEQUENCE_ONCE_CONSUMED.json'):
 p=t/n
 if p.exists():out[n]=json.loads(p.read_bytes())
for a in sorted((t/'attempts').iterdir()):
 row={};out['stages'][a.name]=row
 for base,names in [(a,['DISPATCH_RECEIPT.json','EXIT_RECEIPT.json','GUARDIAN_CURRENT.json']),(a/'output',['STARTED.json','INITIALIZED.json','PROBE_PROGRESS.json','PROBE_COMPLETE.json','ORIGINAL_ERROR.json','WINDOWS4090_FULLSTATE_STARTUP_VERIFIED.json','LEFT_HEAD_ACTUAL_INIT_VERIFIED.json','WINDOWS4090_LATEST_COMPLETE.json','FULLRESTORE_PHYSICAL_PROBE_PASSED.json','WINDOWS4090_PPO_PROGRESS.json','WINDOWS4090_PPO_FORMAL_FINAL_ACTUAL.json'])]:
  for n in names:
   p=base/n
   if p.exists():row[n]=json.loads(p.read_bytes())
 p=a/'worker_stdout.log'
 if p.exists():
  with p.open('rb') as f:f.seek(max(0,p.stat().st_size-6000));row['actual_log_tail']=f.read().decode('utf8','replace')
for key in ('SEQUENCE_CURRENT_ACTUAL.json','SEQUENCE_ONCE_CONSUMED.json'):
 if key in out:
  for name in ('parent','child'):
   x=out[key].get(name)
   if x:
    try:p=psutil.Process(x['pid']);out[key][name+'_actual_running']=p.create_time()==x['created'];out[key][name+'_actual_argv']=p.cmdline()
    except psutil.Error:out[key][name+'_actual_running']=False
lock=r/'WINDOWS4090_GPU_EXCLUSIVE.lock';held=None
if lock.exists():
 try:
  with lock.open('r+b') as f:f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
  held=False
 except OSError:held=True
out['actual_native_OSlock_held']=held;out['RAM_available_bytes']=psutil.virtual_memory().available
print(json.dumps(out))
"""
 b=base64.b64encode(code.encode()).decode();raw=powershell(connect(),"[Console]::OutputEncoding=[System.Text.Encoding]::UTF8;& '"+R+"/env/python.exe' -c \"import base64;exec(base64.b64decode('"+b+"'))\"",timeout=35);actual=json.loads(raw)
 if save:
  p=D/'reports'/('TEMP2048_ACTUAL_'+str(time.time_ns())+'.json');p.write_text(json.dumps(actual,indent=2),encoding='utf8')
 else:p=None
 current=actual.get('SEQUENCE_CURRENT_ACTUAL.json',{})
 print(json.dumps(dict(report=str(p) if p else None,phase=current.get('phase'),RSS_GB=current.get('RSS_bytes',0)/1e9,peak_RSS_GB=current.get('peak_RSS_bytes',0)/1e9,job_peak_commit_GB=current.get('job_peak_commit_bytes',0)/1e9,parent_running=current.get('parent_actual_running'),child_running=current.get('child_actual_running'),native_OSlock_held=actual.get('actual_native_OSlock_held'),sequence_error=bool(actual.get('SEQUENCE_ORIGINAL_ERROR.json')),stages={k:dict(error=v.get('ORIGINAL_ERROR.json',{}).get('error'),probe_controls=v.get('PROBE_PROGRESS.json',{}).get('controls'),PPO_updates=v.get('WINDOWS4090_PPO_PROGRESS.json',{}).get('actual_updates'),exit_passed=v.get('EXIT_RECEIPT.json',{}).get('passed')) for k,v in actual['stages'].items()})))
 return actual
if __name__=='__main__':read()
