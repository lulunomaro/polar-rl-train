"""Read-only evaluator state, own process identities and completed new-scope evidence."""
from pathlib import Path
import sys,json,base64
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect_eval();root='D:/MOD4_async_eval/history_clock1000_v15'
try:
 code=r'''
from pathlib import Path
import json,subprocess,base64,time
D=Path('D:/MOD4_async_eval/history_clock1000_v15')
def read(p):return json.loads(p.read_text(encoding='utf8')) if p.is_file() else None
started=read(D/'WORKER_STARTED.json');pid=started['pid']
ps="$p=Get-CimInstance Win32_Process -Filter 'ProcessId="+str(pid)+"';$c=@(Get-CimInstance Win32_Process -Filter 'ParentProcessId="+str(pid)+"');[pscustomobject]@{process=$p|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}};children=$c|Select-Object ProcessId,CommandLine;oldTask=(Get-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v12').State.ToString();newTask=(Get-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_clock1000').State.ToString()}|ConvertTo-Json -Depth 5 -Compress"
enc=base64.b64encode(ps.encode('utf-16le')).decode();p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',enc],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000);assert p.returncode==0,p.stderr
jobs=[]
for d in sorted((D/'jobs').glob('*')):
 jobs.append(dict(job_id=d.name,active=read(d/'ACTIVE.json'),complete=read(d/'complete.json'),result=read(d/'result.json'),manifest_present=(d/'manifest.json').exists(),probe_present=(d/'probe.json').exists(),
  last_log=(d/'probe.log').read_text(errors='replace').splitlines()[-4:] if (d/'probe.log').exists() else [],partial_bytes={x.name:x.stat().st_size for x in d.glob('*.partial')}))
gpu=subprocess.run(['nvidia-smi','--query-gpu=name,memory.used,memory.total,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,creationflags=0x08000000)
print(json.dumps(dict(epoch=time.time(),worker_started=started,worker_state=read(D/'WORKER_STATE.json'),attention=read(D/'WORKER_ATTENTION.json'),identity=json.loads(p.stdout),GPU=gpu.stdout.strip(),jobs=jobs)))
'''
 enc=base64.b64encode(code.encode()).decode()
 cmd='"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" -c "import base64;exec(base64.b64decode(\''+enc+'\'))"'
 _,o,e=c.exec_command(cmd,timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,err.decode(errors='replace')
 v=json.loads(raw);(R/'CLOCK1000_EVAL_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 with c.open_sftp() as s:
  for j in v['jobs']:
   if j['complete']:
    local=R/'clock1000_eval'/j['job_id'];local.mkdir(parents=True,exist_ok=True)
    for n in ['complete.json','result.json','probe.json','manifest.json']:s.get(root+'/jobs/'+j['job_id']+'/'+n,str(local/n))
 print(json.dumps(dict(epoch=v['epoch'],identity=v['identity'],GPU=v['GPU'],attention=v['attention'],jobs=[dict(job_id=j['job_id'],complete=bool(j['complete']),result=j['result'],active_pid=(j['active'] or {}).get('pid'),log_tail=[l[:200] for l in j['last_log']],partial_bytes=j['partial_bytes']) for j in v['jobs']])))
finally:c.close()
