from pathlib import Path
import sys,json,base64
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect_eval()
try:
 code=r'''
from pathlib import Path
import json,time,subprocess,base64
D=Path('D:/MOD4_async_eval/closure_episode_clock2500_v15');read=lambda p:json.loads(p.read_text(encoding='utf8')) if p.exists() else None
v=dict(epoch=time.time(),reports={n:read(D/n) for n in ['HANDOVER_STARTED.json','HANDOVER_STATE.json','HANDOVER_COMPLETE.json','HANDOVER_ATTENTION.json','HANDOVER_PERMISSION_REVIEW_STARTED.json','HANDOVER_PERMISSION_REVIEW_ATTENTION.json','WORKER_STARTED.json','WORKER_STATE.json','WORKER_ATTENTION.json']});started=v['reports']['WORKER_STARTED.json']
v['current_attention']=v['reports']['WORKER_ATTENTION.json'] or v['reports']['HANDOVER_PERMISSION_REVIEW_ATTENTION.json'] or (v['reports']['HANDOVER_ATTENTION.json'] if not v['reports']['HANDOVER_COMPLETE.json'] else None)
if started:
 pid=started['pid'];ps="$p=Get-CimInstance Win32_Process -Filter 'ProcessId="+str(pid)+"';$c=@(Get-CimInstance Win32_Process -Filter 'ParentProcessId="+str(pid)+"');[pscustomobject]@{process=$p|Select-Object ProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}};children=$c|Select-Object ProcessId,CommandLine;taskState=(Get-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_closure2500').State.ToString()}|ConvertTo-Json -Depth 6 -Compress"
 enc=base64.b64encode(ps.encode('utf-16le')).decode();p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',enc],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000);assert p.returncode==0,p.stderr;v['identity']=json.loads(p.stdout)
print(json.dumps(v))
'''
 enc=base64.b64encode(code.encode()).decode();cmd='"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" -c "import base64;exec(base64.b64decode(\''+enc+'\'))"'
 _,o,e=c.exec_command(cmd,timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw);(R/'EVALUATOR_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
