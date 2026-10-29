"""Read only the known117 Task, own terminal publication and current local snapshot.
V4 registered/started the Task before its PowerShell output-boolean expression failed.
Never starts/restarts a Task and never enumerates unknown process identities.
"""
from pathlib import Path
import base64,json,runpy,time
HERE=Path(__file__).resolve().parent
ns=runpy.run_path(str(HERE/'collect_serial_and_publish_dashboard_v4.py'),run_name='definitions_only')['ns']
R=HERE/'reports/selected_v4';marker=R/'READONLY_REMOTE117_RECOVERY_CONSUMED.json';assert not marker.exists()
marker.write_text(json.dumps(dict(epoch=time.time(),no_task_start_or_mutation=True)),encoding='utf8')
_,secret,_=ns['credentials']();c=ns['connect249'](secret)
try:
    source=r'''import ctypes,json,time
from pathlib import Path
import psutil
p=Path('D:/MOD4_async_eval/MOD4_PLAN_AND_FOUR4090_TERMINAL_20261029v117')
started=p/'TERMINAL_ACTUAL_STARTED.json';receipt=json.loads(started.read_bytes()) if started.exists() else None
out=dict(epoch=time.time(),started=receipt,snapshot=json.loads((p/'monitor_snapshot.json').read_bytes()),own_process=None)
if receipt:
 try:
  proc=psutil.Process(receipt['pid'])
  if proc.create_time()==receipt['creation']:
   u=ctypes.WinDLL('user32');u.IsWindowVisible.argtypes=[ctypes.c_void_p]
   out['own_process']=dict(pid=proc.pid,creation=proc.create_time(),exe=proc.exe(),argv=proc.cmdline(),cwd=proc.cwd(),running=proc.is_running(),known_window_visible=bool(u.IsWindowVisible(receipt['own_console_handle'])))
  else:out['own_process']=dict(original_PID_recycled=True)
 except psutil.NoSuchProcess:out['own_process']=dict(original_out=True)
print(json.dumps(out,ensure_ascii=False))
'''
    enc=base64.b64encode(source.encode()).decode()
    _,o,e=c.exec_command('"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" -B -X utf8 -c "import base64;exec(base64.b64decode(\''+enc+'\'))"',timeout=45)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,err.decode('utf8','replace')[-1800:]
    result=json.loads(raw)
    task=ns['ps249'](c,"$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue';$x=Get-ScheduledTask -TaskName '"+ns['TASK']+"';$i=$x|Get-ScheduledTaskInfo;[PSCustomObject]@{name=$x.TaskName;state=[string]$x.State;lastResult=$i.LastTaskResult;principal=$x.Principal.UserId;logonType=[string]$x.Principal.LogonType;runLevel=[string]$x.Principal.RunLevel;triggers=@($x.Triggers|Where-Object{$null -ne $_}).Count}|ConvertTo-Json -Compress")
    result['actual_task']=task;result['no_task_restart']=True
    ns['put']('REMOTE3060_ACTUAL_TERMINAL_AND_TASK_READONLY_RECOVERED.json',result)
    print(json.dumps(dict(started=bool(result['started']),own_process=result['own_process'],actual_task=task,hosts=[dict(label=h['label'],passed=h['passed'],error=h.get('error')) for h in result['snapshot']['hosts']]),ensure_ascii=False))
finally:c.close();secret=None
