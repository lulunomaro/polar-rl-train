"""Continue only registration/start not executed after local codec rejection."""
from pathlib import Path
import sys,os,json,time,base64,hashlib,traceback,importlib.util
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
spec=importlib.util.spec_from_file_location('prepared_original_deploy',D/'deploy_direct3060_baseline120_WDDM_guard_reviewed_once.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def ps(c,code,timeout=60):
 enc=base64.b64encode(code.encode('utf-16-le')).decode()
 _,o,e=c.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+enc,timeout=timeout)
 raw=o.read();err=e.read();rc=o.channel.recv_exit_status();assert rc==0,(rc,err.decode('utf8','replace')[-5000:])
 return json.loads(raw.decode('utf-8-sig'))
def save(name,v):
 p=R/name;assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def main():
 assert (R/'DIRECT3060_BASELINE120_EXTRACTED_SOURCE_TARGET_CPU_ACTUAL.json').exists()
 assert not (R/'DIRECT3060_BASELINE120_TASK_UNEXECUTED_CONTINUE_INTENT.json').exists()
 sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
 secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret;os.environ['MOD4_EVAL_SSH_PASSWORD']=secret
 sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
 c=connect_eval()
 try:
  actual=m.py(c,"from pathlib import Path\nimport json,hashlib\nr=Path("+repr(m.ROOT)+");p=r/'payload';assert not (r/'TASK_START_INTENT.json').exists() and not (r/'DEMAND_LAUNCH_ENTERED.json').exists(); assert hashlib.sha256((p/'SOURCE_BUNDLE_V2_MANIFEST.json').read_bytes()).hexdigest()=='e707752857aa7798cc54e1466b0ff7bf89d7691b23854e23fe88ae0c78a8c6ff'; l=json.loads((r/'BASELINE120_ROOT_GPU_LEASE.json').read_bytes());assert l['case_id']=="+repr(m.CASE)+";print(json.dumps(dict(root=str(r),lease=l,task_start_and_launcher_absent=True,launcher_SHA=hashlib.sha256((r/'demand_baseline120_parent_launcher_once.py').read_bytes()).hexdigest())))")
  assert actual['launcher_SHA']==hashlib.sha256((D/'demand_baseline120_parent_launcher_once.py').read_bytes()).hexdigest()
  guard=m.py(c,m.GUARD.replace('ROOT',repr(m.ROOT)));assert not guard['new_root_unused']
  taskcheck=ps(c,"$t=Get-ScheduledTask -TaskName '"+m.TASK+"' -ErrorAction SilentlyContinue; [PSCustomObject]@{task_present=($null -ne $t)}|ConvertTo-Json -Compress")
  assert taskcheck['task_present'] is False
  save('DIRECT3060_BASELINE120_TASK_UNEXECUTED_BOUNDARY_ACTUAL.json',dict(epoch=time.time(),actual=actual,guard=guard,taskcheck=taskcheck,
    original_local_codec_error_retained=True,no_upload_extract_lease_write_replayed=True))
  save('DIRECT3060_BASELINE120_TASK_UNEXECUTED_CONTINUE_INTENT.json',dict(epoch=time.time(),root=m.ROOT,only_registration_and_unique_start=True))
  setup=ps(c,"$ErrorActionPreference='Stop'; $name='"+m.TASK+"'; if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'Task already exists'}; $action=New-ScheduledTaskAction -Execute '"+m.PY+"' -Argument '\""+m.ROOT+"/demand_baseline120_parent_launcher_once.py\"' -WorkingDirectory '"+m.ROOT+"'; $user=[System.Security.Principal.WindowsIdentity]::GetCurrent().Name; $principal=New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited; $settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew; Register-ScheduledTask -TaskName $name -Action $action -Principal $principal -Settings $settings | Out-Null; $t=Get-ScheduledTask -TaskName $name; [PSCustomObject]@{name=$t.TaskName;state=[string]$t.State;triggers=@($t.Triggers | Where-Object { $null -ne $_ }).Count;user=$user;action=$t.Actions.Execute;arguments=$t.Actions.Arguments}|ConvertTo-Json -Compress")
  assert setup['triggers']==0;save('DIRECT3060_BASELINE120_DEMAND_TASK_REGISTERED_ACTUAL.json',setup)
  start=ps(c,"$ErrorActionPreference='Stop'; $name='"+m.TASK+"'; $p='"+m.ROOT+"/TASK_START_INTENT.json'; if(Test-Path -LiteralPath $p){throw 'Start intent consumed'}; [IO.File]::WriteAllText($p,'{\"single_start_requested\":true}'); Start-ScheduledTask -TaskName $name; $t=Get-ScheduledTask -TaskName $name; [PSCustomObject]@{name=$name;state=[string]$t.State;triggers=@($t.Triggers | Where-Object { $null -ne $_ }).Count;single_start_requested=$true}|ConvertTo-Json -Compress")
  save('DIRECT3060_BASELINE120_DEMAND_TASK_STARTED_ACTUAL.json',dict(epoch=time.time(),task=start,lease=actual['lease'],single_start=True,
    original_codec_rejection_before_any_task_or_GPU_retained=True,no_upload_or_oldonce_replay=True))
  print(json.dumps(dict(task=start,root=m.ROOT,GPU_result_pending=True)),flush=True)
 except Exception as e:
  q=R/('DIRECT3060_TASK_CONTINUE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');q.write_text(json.dumps(dict(epoch=time.time(),error=repr(e),traceback=traceback.format_exc(),unknown_outcome_requires_actualread_not_start_replay=True),ensure_ascii=False,indent=2),encoding='utf8');raise
 finally:c.close();os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
if __name__=='__main__':main()
