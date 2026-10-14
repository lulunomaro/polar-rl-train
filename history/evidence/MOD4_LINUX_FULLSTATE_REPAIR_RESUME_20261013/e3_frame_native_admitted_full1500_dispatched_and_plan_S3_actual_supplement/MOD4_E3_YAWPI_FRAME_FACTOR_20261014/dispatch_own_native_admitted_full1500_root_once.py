"""Root-only one new full1500, requiring this factor's actual native admission."""
from pathlib import Path
import sys,json,time,hashlib,traceback,os
P=Path(__file__).resolve().parent;W=P.parent;R=P/'reports'
sys.path.insert(0,str(W/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014'))
import transport_249_only as t
t.ROOT='D:/MOD4_async_eval/MOD4_E3_YAWPI_FRAME_FACTOR_20261014'
ROOT=t.ROOT;CASE='e3_yawpi_same_world_full1500_v2';TASK='MOD4_E3_YawPi_SameWorld_Full1500_v2_20261014'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,v):
 p=R/name;assert not p.exists()
 with p.open('xb') as f:f.write(json.dumps(v,ensure_ascii=False,indent=2).encode());f.flush();os.fsync(f.fileno())

def main():
 assert not (R/'YAWPI_FULL1500_ROOT_START_INTENT.json').exists(),'Only read actual unknown outcome; no retry'
 proof=R/'YAWPI_OWN_NATIVE120_ACTUAL_CPU_ADMITTED_V3.json';n=json.loads(proof.read_bytes())
 assert n['passed_actual_data_and_factor_admission'] is True and n['controls']==120 and n['callbacks']==480
 assert n['q30_XY_physicalparams_staticrecipes_captured_RNG_and_queue_exact_to_baseline'] and n['physical_birth_safe_Z_and_complete25200point_footprint_original_tolerances_passed']
 c=sf=None
 try:
  c=t.connect();fresh=t.py(c,t.guard_code());assert not fresh['new_root_unused']
  task=t.ps(c,"$x=Get-ScheduledTask -TaskName '"+TASK+"' -ErrorAction SilentlyContinue;[PSCustomObject]@{present=($null -ne $x)}|ConvertTo-Json -Compress");assert not task['present']
  code="""from pathlib import Path
import json,hashlib
root=Path(ROOT);a=root/'attempts/e3_yawpi_same_world_native120_v2';o=a/'output'
end=json.loads((a/'PARENT_EXIT_RECEIPT.json').read_bytes());complete=json.loads((o/'COMPLETE_ACTUAL.json').read_bytes())
assert end['exit_code']==0 and end['no_PPO'] and not end['original_error_present'] and end['complete_data_contract_present']
assert complete['steps']==120 and complete['callbacks']==480 and complete['passed_data_contract'] and not (o/'ORIGINAL_ERROR.json').exists()
assert not (root/'attempts/CASE').exists() and not (root/'ROOT_GPU_LEASE_FULL1500.json').exists() and not (root/'FULL1500_TASK_START_INTENT.json').exists()
lease=json.loads((root/'ROOT_GPU_LEASE_NATIVE120.json').read_bytes())
for row in lease['new_factor_components']:assert hashlib.sha256((root/'payload'/row['relative']).read_bytes()).hexdigest()==row['sha256']
print(json.dumps(dict(parent_exit=end,complete=complete,lease=lease,new_full_case_unused=True)))
""".replace('ROOT',repr(ROOT)).replace('CASE',CASE)
  a=t.py(c,code);lease=a['lease'];assert lease['checkpoint_sha256']==n['source_SHA']
  for row in lease['new_factor_components']:assert n['active_component_SHA'][row['relative']]==row['sha256']
  save('YAWPI_FULL1500_ROOT_START_INTENT.json',dict(epoch=time.time(),guard=fresh,native_admission=dict(path=str(proof),bytes=proof.stat().st_size,sha256=H(proof)),native_actual=a,new_case=CASE,task=TASK,no_PPO=True))
  lease=dict(lease);lease.update(epoch=time.time(),case_id=CASE,resource_boundary=fresh,own_new_native120_actual_admission=dict(path=ROOT+'/OWN_NATIVE120_INDEPENDENT_CPU_ADMITTED_V3.json',bytes=proof.stat().st_size,sha256=H(proof)),native120_only_before_full1500_requirement_actually_satisfied=True)
  lease['case_parameters']=dict(lease['case_parameters'],steps=1500)
  sf=c.open_sftp();sf.put(str(proof),ROOT+'/OWN_NATIVE120_INDEPENDENT_CPU_ADMITTED_V3.json')
  blob=json.dumps(lease,ensure_ascii=False,indent=2).encode();leasepath=ROOT+'/ROOT_GPU_LEASE_FULL1500.json'
  with sf.open(leasepath,'wx') as f:f.write(blob);f.flush()
  original=P/'launch_yawpi_new_native120_once.py';text=original.read_text(encoding='utf8')
  assert text.count('e3_yawpi_same_world_native120_v2')==1
  text=text.replace('NATIVE120','FULL1500').replace('e3_yawpi_same_world_native120_v2',CASE)
  local=P/'launch_yawpi_new_full1500_once.py';assert not local.exists();compile(text,str(local),'exec');local.write_bytes(text.encode());sf.put(str(local),ROOT+'/'+local.name)
  setup=t.ps(c,"$ErrorActionPreference='Stop';$name='"+TASK+"';if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'Task exists'};$action=New-ScheduledTaskAction -Execute '"+t.PY+"' -Argument '\""+ROOT+'/'+local.name+"\"' -WorkingDirectory '"+ROOT+"';$principal=New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited;$settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew;Register-ScheduledTask -TaskName $name -Action $action -Principal $principal -Settings $settings|Out-Null;$x=Get-ScheduledTask -TaskName $name;[PSCustomObject]@{task=$name;state=[string]$x.State;triggers=@($x.Triggers|Where-Object {$null -ne $_}).Count}|ConvertTo-Json -Compress")
  assert setup['triggers']==0;save('YAWPI_FULL1500_TASK_REGISTERED_ACTUAL.json',setup)
  start=t.ps(c,"$ErrorActionPreference='Stop';$p='"+ROOT+"/FULL1500_TASK_START_INTENT.json';if(Test-Path -LiteralPath $p){throw 'Start consumed'};[IO.File]::WriteAllText($p,'{\"single_start_requested\":true}');Start-ScheduledTask -TaskName '"+TASK+"';$x=Get-ScheduledTask -TaskName '"+TASK+"';[PSCustomObject]@{task=$x.TaskName;state=[string]$x.State;triggers=@($x.Triggers|Where-Object {$null -ne $_}).Count}|ConvertTo-Json -Compress")
  save('YAWPI_FULL1500_UNIQUE_DISPATCH_ACTUAL.json',dict(epoch=time.time(),task=start,lease=lease,lease_SHA=hashlib.sha256(blob).hexdigest(),launcher_SHA=H(local),no_oldcase_or_native_replayed=True,own_complete_native_CPU_admitted=True,full1500_result_pending=True,no_PPO=True))
  print(json.dumps(dict(unique_full1500_dispatched=True,task=start,root=ROOT,no_PPO=True)),flush=True)
 except BaseException:
  save('YAWPI_FULL1500_ROOT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_outcome_readonly_no_retry=True));raise
 finally:
  if sf:sf.close()
  t.close(c)

if __name__=='__main__':main()
