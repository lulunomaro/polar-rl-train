from pathlib import Path
import sys,json,base64
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'EVALUATOR_CPU_TASK_STARTED.json').exists();sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect_eval()
try:
 code=r'''
from pathlib import Path
import json,subprocess,base64,time
D=Path('D:/MOD4_async_eval/closure_episode_clock2500_v15');assert not (D/'HANDOVER_STARTED.json').exists()
ps=r"""
$ErrorActionPreference='Stop'
$name='MOD4_AsyncFrozenEvaluation_closure2500_saved_handover_once'
if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'Bootstrap task already exists'}
$action=New-ScheduledTaskAction -Execute 'D:\claude2\fangzhen\.venv-isaaclab\Scripts\pythonw.exe' -Argument 'D:\MOD4_async_eval\closure_episode_clock2500_v15\handover_eval_idle.py' -WorkingDirectory 'D:\MOD4_async_eval\closure_episode_clock2500_v15'
$principal=New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $name -Action $action -Principal $principal -Settings $settings -Description 'One-shot CPU idle worker handover; no trigger/GPU/PPO/canonical write.'|Out-Null
Start-ScheduledTask -TaskName $name
$xml=Export-ScheduledTask -TaskName $name
[pscustomobject]@{name=$name;triggerCount=([xml]$xml).Task.Triggers.ChildNodes.Count;state=(Get-ScheduledTask -TaskName $name).State.ToString()}|ConvertTo-Json -Compress
"""
enc=base64.b64encode(ps.encode('utf-16le')).decode();p=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',enc],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000);assert p.returncode==0,p.stdout+p.stderr
v=dict(epoch=time.time(),task=json.loads(p.stdout),reason='Use desktop interactive demand task so SSH child lifetime does not govern the CPU-only handover',no_GPU_or_canonical_authority=True);assert v['task']['triggerCount']==0;print(json.dumps(v))
'''
 enc=base64.b64encode(code.encode()).decode();cmd='"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" -c "import base64;exec(base64.b64decode(\''+enc+'\'))"'
 _,o,e=c.exec_command(cmd,timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw);(R/'EVALUATOR_CPU_TASK_STARTED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
