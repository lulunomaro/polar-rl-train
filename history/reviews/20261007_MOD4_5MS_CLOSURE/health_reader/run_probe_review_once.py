"""Borrow this task's idle evaluator slot, then restore the unchanged demand worker."""
from pathlib import Path
import json,subprocess,base64,time,os,msvcrt,traceback,hashlib
D=Path(__file__).resolve().parent;W=D.parent.parent/'sensor_clock1000_v15'
PY='D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe'
TASK='MOD4_AsyncFrozenEvaluation_v15_sensor'
def write(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf8')
def ps(code):
 enc=base64.b64encode(code.encode('utf-16le')).decode()
 r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',enc],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000)
 assert r.returncode==0,r.stderr
 return r.stdout
assert not (D/'BORROW_STARTED.json').exists(),'This diagnostic coordinator was already executed; inspect its receipt.'
st=json.loads((W/'WORKER_STARTED.json').read_text(encoding='utf8'));state=json.loads((W/'WORKER_STATE.json').read_text(encoding='utf8'))
assert time.time()-state['epoch']<90 and state['phase']=='polling'
assert all((W/'jobs'/j/'complete.json').is_file() for j in state['jobs'])
identity=json.loads(ps("$p=Get-CimInstance Win32_Process -Filter 'ProcessId="+str(st['pid'])+"';$c=@(Get-CimInstance Win32_Process -Filter 'ParentProcessId="+str(st['pid'])+"');$t=Get-ScheduledTask -TaskName '"+TASK+"';[pscustomobject]@{process=$p|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}};children=@($c|Select-Object ProcessId,CommandLine);task=$t.Actions|Select-Object Execute,Arguments}|ConvertTo-Json -Depth 5 -Compress"))
assert identity['process']['ProcessId']==st['pid'] and abs(identity['process']['creation_epoch']-st['epoch'])<2
assert 'sensor_clock1000_v15' in identity['process']['CommandLine'] and 'eval_worker_sensor.py' in identity['process']['CommandLine']
assert not identity['children'],identity
assert 'sensor_clock1000_v15' in identity['task']['Arguments'],identity
write(D/'BORROW_STARTED.json',{'epoch':time.time(),'pid':os.getpid(),'idle_worker_identity':identity,'completed_jobs':state['jobs'],'no_4090_operations':True,'new_learning':False})
parked=False;lock=None
try:
 ps("Stop-ScheduledTask -TaskName '"+TASK+"'");parked=True
 # The scheduled task owns both the venv launcher and its actual Python process.
 for _ in range(20):
  p=ps("@(Get-CimInstance Win32_Process -Filter 'ProcessId="+str(st['pid'])+"') | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress")
  if not p.strip():break
  time.sleep(.25)
 else:raise RuntimeError('Idle worker did not exit; GPU diagnostic was not launched.')
 lock=(D.parent.parent/'worker.lock').open('a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
 env=dict(os.environ);env.update(PYTHONUTF8='1',PYTHONUNBUFFERED='1',ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES')
 args=[PY,'-X','utf8',str(D/'mod4_closure_probe.py'),'--headless','--device','cuda:0','--output',str(D/'closure_mod4_30s.json'),'--steps','100','--num_envs','32']
 with (D/'closure_mod4_30s.log').open('wb') as f:
  child=subprocess.Popen(args,cwd=D.parent/'source/runtime',env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=0x08000000)
  write(D/'PROBE_STARTED.json',{'pid':child.pid,'epoch':time.time(),'argv':args,'gpu_lock_acquired':True,'probe_sha256':hashlib.sha256((D/'mod4_closure_probe.py').read_bytes()).hexdigest()})
  try:rc=child.wait(timeout=1500)
  except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=30);rc=-99
 write(D/'PROBE_EXITED.json',{'epoch':time.time(),'exit_code':rc,'result_exists':(D/'closure_mod4_30s.json').is_file(),'error_exists':(D/'closure_mod4_30s.error.txt').is_file()})
except Exception:
 write(D/'BORROW_ATTENTION.json',{'epoch':time.time(),'error':traceback.format_exc()})
 raise
finally:
 if lock:
  lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1);lock.close()
 if parked:
  ps("Start-ScheduledTask -TaskName '"+TASK+"'")
  write(D/'WORKER_RESTART_REQUESTED.json',{'epoch':time.time(),'task':TASK,'original_worker_source_unchanged':True})
