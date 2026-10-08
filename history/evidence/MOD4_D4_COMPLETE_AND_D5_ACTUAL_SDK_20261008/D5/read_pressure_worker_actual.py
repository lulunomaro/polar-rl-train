from pathlib import Path
import sys,json,base64,time
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect_eval();root='D:/MOD4_async_eval/closure_episode_clock2500_v15'
try:
    code=r"$rows=@(Get-CimInstance Win32_Process|Where-Object {$_.CommandLine -like '*closure_episode_clock2500_v15*' -and $_.Name -like 'python*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}});[pscustomobject]@{rows=$rows;oldtask=(Get-ScheduledTask -TaskName 'MOD4_AsyncFrozenEvaluation_v15_closure2500').State.ToString()}|ConvertTo-Json -Compress -Depth 6"
    encoded=base64.b64encode(code.encode('utf-16le')).decode()
    _,o,e=c.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+encoded,timeout=20)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw);v['epoch']=time.time()
    with c.open_sftp() as f:
        for n in ('PRESSURE_DEPENDENCY_WORKER_STARTED.json','PRESSURE_DEPENDENCY_WORKER_STATE.json','PRESSURE_DEPENDENCY_WORKER_ATTENTION.json','PRESSURE_DEPENDENCY_WORKER_ADMITTED.json',
                  'SPRING_AUDIT_WORKER_STARTED.json','SPRING_AUDIT_WORKER_STATE.json','SPRING_AUDIT_WORKER_ATTENTION.json','SPRING_AUDIT_WORKER_ADMITTED.json'):
            try:v[n]=json.loads(f.open(root+'/'+n).read())
            except FileNotFoundError:v[n]=None
    (R/'PRESSURE_WORKER_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
