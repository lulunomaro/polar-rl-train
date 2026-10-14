"""Only the missing own full15s route after own native physically passed."""
from pathlib import Path
import sys,json,time,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';ROOT='D:/MOD4_async_eval/'+D.name;Q=D/'payload'
sys.path.insert(0,str(W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'));import transport_249_bodyframe_current_terminal_role_v3 as t
t.ROOT=ROOT;CASE='s4_rule_original35_query35_full1500_v2';TASK='MOD4_S4_Original35Query35_Full1500_v2_20261015';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):
 p=R/n;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
def main():
 proof=R/'S4_RULE35_OWN_PHYSICAL_DATA_ADMITTED_s4_rule_original35_query35_native120_v2.json';routing=R/'S4_RULE35_SHARED_ROUTING_ADMITTED_s4_rule_original35_query35_native120_v2.json'
 assert json.loads(proof.read_bytes())['passed'] and json.loads(routing.read_bytes())['passed']
 prep=json.loads((R/'S4_ORIGINAL35_TRANSITION_RULE_SOURCE_CPU_PREPARED_ACTUAL_V2.json').read_bytes());prior=json.loads((R/'S4_ORIGINAL35_OWN_NATIVE120_PARAMETER_BOUND_LEASE_ACTUAL.json').read_bytes());boundary=json.loads((R/'s4_rule_original35_query35_native120_v2_INDEPENDENT_BOUNDARY.json').read_bytes())
 assert boundary['actual_parent_absent'] and boundary['actual_child_absent'] and boundary['shared_OS_lock_free'] and not (R/'S4_RULE35_FULL1500_UNIQUE_DEPLOY_INTENT.json').exists()
 c=None;sf=None
 try:
  c=t.connect();guard=t.py(c,t.guard_code());assert not guard['new_root_unused'] and guard['shared_OS_lock_free']
  actual=t.py(c,'CONTEXT='+repr(dict(root=ROOT,case=CASE,manifestSHA=prep['manifest']['sha256'],sdkSHA=H(Q/'EXPECTED_INSTALLED_3060_BACKEND_V2.json')))+'\n'+r'''
from pathlib import Path
import json,hashlib
R=Path(CONTEXT['root']);Q=R/'payload';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not (R/'attempts'/CONTEXT['case']).exists() and not (R/'leases'/(CONTEXT['case']+'.json')).exists() and not (R/(CONTEXT['case']+'_START_INTENT.json')).exists()
assert H(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json')==CONTEXT['manifestSHA']
m=json.loads((Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json').read_bytes())
for row in m['file_rows']:assert H(Q/row['relative'])==row['sha256']
assert H(Q/'EXPECTED_INSTALLED_3060_BACKEND_V2.json')==CONTEXT['sdkSHA']
for row in json.loads((Q/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())['files']:assert H(row['path'])==row['sha256']
for row in m['source_pair']:assert H(row['local_path'])==row['sha256']
n=R/'attempts/s4_rule_original35_query35_native120_v2';x=json.loads((n/'PARENT_EXIT_RECEIPT.json').read_bytes());v=json.loads((n/'output/COMPLETE_ACTUAL.json').read_bytes())
assert x['exit_code']==0 and not x['original_error_present'] and x['complete_data_contract_present'] and v['steps']==120 and v['callbacks']==480
print(json.dumps(dict(own_native_actual_complete=True,all_active_source_pair_and_backend_SHA_unchanged=True,new_case_all_once_paths_unused=True,no_new_GPU_yet=True)))
''')
  task=t.ps(c,"$x=Get-ScheduledTask -TaskName '"+TASK+"' -ErrorAction SilentlyContinue;[PSCustomObject]@{exists=($null-ne $x)}|ConvertTo-Json -Compress");assert not task['exists']
  save('S4_RULE35_FULL1500_UNIQUE_DEPLOY_INTENT.json',dict(epoch=time.time(),case=CASE,actual=actual,guard=guard,own_native_physical_review_SHA=H(proof),own_native_routing_review_SHA=H(routing),no_new_GPU_yet=True,unknown_outcome_readonly_not_retry=True))
  lease=dict(prior);lease.update(epoch=time.time(),case_id=CASE,resource_boundary=guard,case_parameters=dict(steps=1500,num_envs=80,seed=20260928,body_sign=1,world_sign=1,feedback_current=False,headless=True,device='cuda:0'),scope='own frozen E0+W35 original35 route full1500/15s; no learned gate or PPO',own_native_physical_review_SHA=H(proof),own_native_routing_review_SHA=H(routing),old_failed_query50_scope_not_replayed=True)
  sf=c.open_sftp();sf.get_channel().settimeout(60)
  with sf.open(ROOT+'/leases/'+CASE+'.json','wx') as f:f.write(json.dumps(lease,indent=2).encode());f.flush()
  save('S4_RULE35_FULL1500_PARAMETER_BOUND_OWN_NATIVE_LEASE_ACTUAL.json',lease)
  launcher="""from pathlib import Path
import subprocess,sys,json,os,time,psutil
R=Path(__file__).resolve().parent;case=CASE;assert not (R/(case+'_START_INTENT.json')).exists()
(R/(case+'_START_INTENT.json')).write_text(json.dumps(dict(epoch=time.time(),pid=os.getpid(),creation=psutil.Process().create_time(),no_PPO=True)))
argv=[sys.executable,str(R/'payload/run_full80_parameter_bound_parent_v2.py'),'--lease',str(R/'leases'/(case+'.json')),'--attempt',str(R/'attempts'/case)]
with (R/(case+'_PARENT_CONSOLE.log')).open('xb') as log:
 p=subprocess.Popen(argv,cwd=R/'payload',stdout=log,stderr=subprocess.STDOUT)
 (R/(case+'_PARENT_PID.json')).write_text(json.dumps(dict(pid=p.pid,creation=psutil.Process(p.pid).create_time(),argv=argv)))
 rc=p.wait()
(R/(case+'_LAUNCH_EXIT.json')).write_text(json.dumps(dict(epoch=time.time(),exit_code=rc,no_PPO=True)))
sys.exit(rc)
""".replace('CASE',repr(CASE))
  script=D/('demand_'+CASE+'_once.py');assert not script.exists();compile(launcher,str(script),'exec');script.write_text(launcher,encoding='utf8');sf.put(str(script),ROOT+'/'+script.name)
  task=t.ps(c,"$ErrorActionPreference='Stop';$n='"+TASK+"';if(Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue){throw 'Task exists'};$a=New-ScheduledTaskAction -Execute '"+t.PY+"' -Argument '\""+ROOT+'/'+script.name+"\"' -WorkingDirectory '"+ROOT+"';$p=New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited;$s=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew;Register-ScheduledTask -TaskName $n -Action $a -Principal $p -Settings $s|Out-Null;Start-ScheduledTask -TaskName $n;$t=Get-ScheduledTask -TaskName $n;[PSCustomObject]@{task=$n;state=[string]$t.State;triggers=@($t.Triggers|Where-Object {$null-ne $_}).Count}|ConvertTo-Json -Compress")
  assert task['triggers']==0;save('S4_RULE35_FULL1500_UNIQUE_TASK_DISPATCH_ACTUAL.json',dict(epoch=time.time(),case=CASE,task=task,fullroute_actual_pending=True,gate_training_not_admitted=True));print(json.dumps(dict(dispatched=True,task=task,case=CASE,no_PPO=True)))
 except BaseException:
  save('S4_RULE35_FULL1500_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_blind_retry=True));raise
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':main()
