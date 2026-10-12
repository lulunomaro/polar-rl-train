"""Only collect the already-started oneoff task; never repeat registration or launch."""
from scut_wave_detached_io import *

def main():
    w=connect()
    try:
        v=execute(w,r'''from pathlib import Path
import json,time,subprocess,base64,hashlib
D=Path(ROOT_TOKEN);TASK=TASK_TOKEN
assert (D/'REFERENCE_COORDINATOR_STARTED.json').exists() and (D/'TARGET_CPU_ADMITTED.json').exists() and not (D/'DETACHED_DISPATCH_ACTUAL_RECEIPT.json').exists()
started=json.loads((D/'REFERENCE_COORDINATOR_STARTED.json').read_bytes());pid=started['pid']
ps="$t=Get-ScheduledTask -TaskName '"+TASK+"';$i=Get-ScheduledTaskInfo -TaskName '"+TASK+"';$p=Get-CimInstance Win32_Process -Filter 'ProcessId="+str(pid)+"';[pscustomobject]@{name=$t.TaskName;state=$t.State.ToString();triggers=@($t.Triggers|Where-Object {$_ -ne $null}).Count;action=$t.Actions|Select-Object Execute,Arguments,WorkingDirectory;principal=$t.Principal|Select-Object UserId,LogonType,RunLevel;last_result=$i.LastTaskResult;process=$p|Select-Object ProcessId,ParentProcessId,Name,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}}}|ConvertTo-Json -Depth 6 -Compress"
r=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-EncodedCommand',base64.b64encode(ps.encode('utf-16le')).decode()],capture_output=True,text=True,encoding='utf8',errors='replace',creationflags=0x08000000);assert r.returncode==0;r=json.loads(r.stdout)
assert r['triggers']==0 and 'reference_coordinator_detached_reviewed_once.py' in r['action']['Arguments'] and r['process']['ProcessId']==pid and abs(r['process']['creation_epoch']-started['epoch'])<2
v=dict(epoch=time.time(),passed=True,oneoff_task=r,coordinator_started=started,probe_scope_root=str(D),coordinator_SHA=hashlib.sha256((D/'reference_coordinator_detached_reviewed_once.py').read_bytes()).hexdigest(),actual_TaskService_dispatch=True,no_periodic_or_boot_trigger=True,prior_Triggers_null_array_count_reader_assertion_preserved=True,receipt_only_no_task_registration_start_or_GPU_replay=True,actual_probe_phase_requires_future_receipts=True)
(D/'DETACHED_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(REMOTE)).replace('TASK_TOKEN',repr(TASK)))
        save('DETACHED_REFERENCE_DISPATCH_ACTUAL_RECEIPT.json',v);print(json.dumps(dict(passed=True,task_state=v['oneoff_task']['state'],triggers=0,actualPID=v['oneoff_task']['process'],no_relaunch=True)))
    finally:w.close()

if __name__=='__main__':
    try:main()
    except BaseException:save('DETACHED_DISPATCH_RECEIPT_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_receipt_only_no_GPU_or_task_replay=True));raise
