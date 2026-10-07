"""Borrow only the verified idle evaluator task, run a bounded solver screen, restore it."""
from pathlib import Path
import json,subprocess,base64,time,os,msvcrt,traceback,hashlib
D=Path(__file__).resolve().parent;W=D.parent/'sensor_clock1000_v15'
PY='D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe';TASK='MOD4_AsyncFrozenEvaluation_v15_sensor'
def write(n,v):(D/n).write_text(json.dumps(v,indent=2),encoding='utf8')
def ps(code):
 enc=base64.b64encode(code.encode('utf-16le')).decode()
 r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',enc],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000)
 assert r.returncode==0,r.stderr
 return r.stdout
assert not(D/'SCREEN_STARTED.json').exists(),'Completed or active unique controller must not be rerun.'
st=json.loads((W/'WORKER_STARTED.json').read_text(encoding='utf8'));state=json.loads((W/'WORKER_STATE.json').read_text(encoding='utf8'))
assert time.time()-state['epoch']<90 and state['phase']=='polling'
assert all((W/'jobs'/j/'complete.json').is_file() for j in state['jobs'])
identity=json.loads(ps("$p=Get-CimInstance Win32_Process -Filter 'ProcessId="+str(st['pid'])+"';$c=@(Get-CimInstance Win32_Process -Filter 'ParentProcessId="+str(st['pid'])+"');$t=Get-ScheduledTask -TaskName '"+TASK+"';[pscustomobject]@{process=$p|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}};children=@($c|Select-Object ProcessId,CommandLine);task=$t.Actions|Select-Object Execute,Arguments}|ConvertTo-Json -Depth 5 -Compress"))
assert identity['process']['ProcessId']==st['pid'] and abs(identity['process']['creation_epoch']-st['epoch'])<2
assert 'sensor_clock1000_v15' in identity['process']['CommandLine'] and 'eval_worker_sensor.py' in identity['process']['CommandLine']
assert not identity['children'] and 'sensor_clock1000_v15' in identity['task']['Arguments'],identity
cases=[('fixed24',24,'replay',32,3000),('fixed32',32,'replay',32,3000),('explore16',16,'exploration',128,1500),('explore24',24,'exploration',128,1500),('explore32',32,'exploration',128,1500)]
write('SCREEN_STARTED.json',{'epoch':time.time(),'pid':os.getpid(),'idle_worker_identity':identity,'completed_jobs':state['jobs'],'cases':cases,'no_native_4090_operations':True,'PPO_updates':0,'canonical_write_authority':False})
parked=False;lock=None;completed=[]
try:
 ps("Stop-ScheduledTask -TaskName '"+TASK+"'");parked=True
 for _ in range(30):
  p=ps("@(Get-CimInstance Win32_Process -Filter 'ProcessId="+str(st['pid'])+"')|Select-Object ProcessId,CommandLine|ConvertTo-Json -Compress")
  if not p.strip():break
  time.sleep(.25)
 else:raise RuntimeError('The verified idle evaluator has not exited. No GPU probe was started.')
 lock=(D.parent/'worker.lock').open('a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
 env=dict(os.environ);env.update(PYTHONUTF8='1',PYTHONUNBUFFERED='1',ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES')
 for name,pos,mode,count,steps in cases:
  C=D/name;C.mkdir(exist_ok=True)
  args=[PY,'-X','utf8',str(C/'solver_repair_probe.py'),'--headless','--device','cuda:0','--output',str(C/'result.json'),'--steps',str(steps),'--num_envs',str(count),'--solver-pos',str(pos),'--mode',mode]
  if mode=='replay':args+=['--replay-file',str(D/'fixed_actions.npz')]
  with(C/'probe.log').open('wb') as f:
   child=subprocess.Popen(args,cwd=D/'source/runtime',env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=0x08000000)
   write('SCREEN_STATE.json',{'phase':'probing','epoch':time.time(),'case':name,'child_pid':child.pid,'argv':args,'completed':completed,'GPU_lock_acquired':True})
   (C/'STARTED.json').write_text(json.dumps({'pid':child.pid,'epoch':time.time(),'argv':args,'probe_sha256':hashlib.sha256((C/'solver_repair_probe.py').read_bytes()).hexdigest()},indent=2),encoding='utf8')
   try:rc=child.wait(timeout=1800)
   except subprocess.TimeoutExpired:
    # Only this isolated non-learning child; never a production trainer or another task.
    child.terminate();child.wait(timeout=30);rc=-99
  v={'epoch':time.time(),'exit_code':rc,'result_exists':(C/'result.json').is_file(),'error_exists':(C/'result.error.txt').is_file()}
  (C/'EXITED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
  if rc!=0 or not v['result_exists'] or v['error_exists']:raise RuntimeError('Isolated probe failed: '+name+' '+json.dumps(v))
  r=json.loads((C/'result.json').read_text(encoding='utf8'));completed.append({'name':name,'result':{k:r[k] for k in ('percentile_mm','max_closure_mm','over_2mm_fraction','longest_contiguous_over_2mm_seconds','nonfinite','wall_seconds')},'result_sha256':hashlib.sha256((C/'result.json').read_bytes()).hexdigest()})
 write('SCREEN_COMPLETE.json',{'phase':'screen_complete_review_required','epoch':time.time(),'completed':completed,'production_adoption':False,'PPO_updates':0})
 write('SCREEN_STATE.json',{'phase':'screen_complete_review_required','epoch':time.time(),'completed':completed,'child_pid':None})
except Exception:
 write('SCREEN_ATTENTION.json',{'epoch':time.time(),'error':traceback.format_exc(),'completed':completed});raise
finally:
 if lock:
  lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1);lock.close()
 if parked:
  ps("Start-ScheduledTask -TaskName '"+TASK+"'")
  write('WORKER_RESTART_REQUESTED.json',{'epoch':time.time(),'task':TASK,'source_unchanged':True})
