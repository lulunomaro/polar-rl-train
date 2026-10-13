"""Two separately authorized frozen leases, each once-only after actual boundary."""
from pathlib import Path
import sys,os,json,time,base64,hashlib,argparse,importlib.util,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
spec=importlib.util.spec_from_file_location('existing_guard',D/'deploy_direct3060_baseline120_WDDM_guard_reviewed_once.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
ROOT=g.ROOT;PY=g.PY
CASES={'baseline':('native3060_bodypos_worldpos_baseline1500_v2','MOD4_DirectFactor_20261013_baseline1500_v2',False),
       'D3':('native3060_bodypos_worldpos_D3current1500_v2','MOD4_DirectFactor_20261013_D3current1500_v2',True)}
def ps(c,code):
 enc=base64.b64encode(code.encode('utf-16-le')).decode();_,o,e=c.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+enc,timeout=60)
 raw=o.read();err=e.read();rc=o.channel.recv_exit_status();assert rc==0,err.decode('utf8','replace');return json.loads(raw.decode('utf-8-sig'))
def save(name,v):
 p=R/name;assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8');return p
def main():
 p=argparse.ArgumentParser();p.add_argument('--factor',choices=CASES,required=True);a=p.parse_args();case,task,factor=CASES[a.factor]
 # Both leases are granted, but second requires actual full firstcase review.
 reference=R/('DIRECT3060_BASELINE120_COMPLETE_INDEPENDENT_CPU_ACTUAL_REVIEW.json' if not factor else 'DIRECT3060_BASELINE1500_COMPLETE_INDEPENDENT_CPU_ACTUAL_REVIEW.json')
 ref=json.loads(reference.read_bytes());assert ref['passed'] is True
 assert not (R/(case+'_DISPATCH_INTENT.json')).exists()
 sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
 secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret;os.environ['MOD4_EVAL_SSH_PASSWORD']=secret
 sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
 c=connect_eval();sf=None
 try:
  # Inspect unknown outcomes before any new file creation/start.
  check=g.py(c,"from pathlib import Path\nimport json\nr=Path("+repr(ROOT)+");case="+repr(case)+";print(json.dumps(dict(attempt_present=(r/'attempts'/case).exists(),lease_present=(r/(case+'_ROOT_GPU_LEASE.json')).exists(),launch_present=(r/(case+'_DEMAND_LAUNCH_ENTERED.json')).exists(),start_intent_present=(r/(case+'_TASK_START_INTENT.json')).exists())))")
  taskcheck=ps(c,"$t=Get-ScheduledTask -TaskName '"+task+"' -ErrorAction SilentlyContinue;[PSCustomObject]@{present=($null -ne $t);state=if($t){[string]$t.State}else{$null}}|ConvertTo-Json -Compress")
  if any(check.values()) or taskcheck['present']:
   q=save(case+'_EXISTING_OUTCOME_READONLY.json',dict(epoch=time.time(),check=check,task=taskcheck,no_launch_replayed=True));print(json.dumps({'existing_actual':str(q),'launch_replayed':False}),flush=True);return
  guard=g.py(c,g.GUARD.replace('ROOT',repr(ROOT)));assert not guard['new_root_unused']
  target=g.py(c,"from pathlib import Path\nimport json,hashlib\np=Path("+repr(ROOT+ '/payload')+");m=p/'SOURCE_BUNDLE_V2_MANIFEST.json';assert hashlib.sha256(m.read_bytes()).hexdigest()=='e707752857aa7798cc54e1466b0ff7bf89d7691b23854e23fe88ae0c78a8c6ff';j=json.loads(m.read_bytes());\nfor row in j['file_rows']:assert hashlib.sha256((p/row['relative']).read_bytes()).hexdigest()==row['sha256']\nprint(json.dumps(dict(sourcefreeze_SHA=hashlib.sha256(m.read_bytes()).hexdigest(),targetfiles_actual_SHA_passed=True)))")
  save(case+'_DISPATCH_INTENT.json',dict(epoch=time.time(),case=case,root=ROOT,root_new_lease_authorized=True,reference_review=str(reference),reference_SHA=hashlib.sha256(reference.read_bytes()).hexdigest(),boundary=guard,target=target))
  lease=dict(epoch=time.time(),case_id=case,target_host='10.24.4.249',namespace='MOD4_3060_DIRECT_FACTOR_20261013',GPU_lease_granted_by_root=True,
   actual_shared_slot_idle_verified=True,resource_boundary=guard,reference_review_SHA=hashlib.sha256(reference.read_bytes()).hexdigest(),
   checkpoint_path=ROOT+'/payload/source/model_32396_91d.pt',checkpoint_sha256='91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4',
   worker_sha256='8fc3fac11f2c309158117512bb3b41fdd34640916f8332fdf3252b5b27f2de05',factor_runtime_sha256='6c2499a95e20f91b7787a1b41e183a343aa46afbc77d6dd86454c1f57847a542',
   source_bundle_manifest_sha256='e707752857aa7798cc54e1466b0ff7bf89d7691b23854e23fe88ae0c78a8c6ff',
   case_parameters=dict(steps=1500,num_envs=8,seed=20260928,body_sign=1,world_sign=1,feedback_current=factor,headless=True,device='cuda:0'),
   frozen_original_white3_fixture=True,no_PPO=True,not_80env_production_qualification=True)
  leasepath=ROOT+'/'+case+'_ROOT_GPU_LEASE.json';sf=c.open_sftp();blob=json.dumps(lease,ensure_ascii=False,indent=2).encode()
  with sf.open(leasepath,'wx') as f:f.write(blob);f.flush()
  launcher=(D/'demand_baseline120_parent_launcher_once.py').read_text(encoding='utf8')
  launcher=launcher.replace('BASELINE120_ROOT_GPU_LEASE.json',case+'_ROOT_GPU_LEASE.json').replace('native3060_bodypos_worldpos_baseline120_v2',case)
  launcher=launcher.replace('DEMAND_LAUNCH_ENTERED.json',case+'_DEMAND_LAUNCH_ENTERED.json').replace('DEMAND_PARENT_CONSOLE.log',case+'_DEMAND_PARENT_CONSOLE.log').replace('DEMAND_PARENT_LAUNCH_PID.json',case+'_DEMAND_PARENT_LAUNCH_PID.json').replace('DEMAND_LAUNCH_EXIT.json',case+'_DEMAND_LAUNCH_EXIT.json')
  script=D/(case+'_demand_parent_launcher_once.py');assert not script.exists();compile(launcher,str(script),'exec');script.write_text(launcher,encoding='utf8');remote=ROOT+'/'+script.name;sf.put(str(script),remote)
  setup=ps(c,"$ErrorActionPreference='Stop';$name='"+task+"';if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'Task exists'};$action=New-ScheduledTaskAction -Execute '"+PY+"' -Argument '\""+remote+"\"' -WorkingDirectory '"+ROOT+"';$principal=New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited;$settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew;Register-ScheduledTask -TaskName $name -Action $action -Principal $principal -Settings $settings|Out-Null;$t=Get-ScheduledTask -TaskName $name;[PSCustomObject]@{task=$name;state=[string]$t.State;triggers=@($t.Triggers | Where-Object {$null -ne $_}).Count;action=$t.Actions.Execute;arguments=$t.Actions.Arguments}|ConvertTo-Json -Compress")
  assert setup['triggers']==0;save(case+'_TASK_REGISTERED_ACTUAL.json',setup)
  started=ps(c,"$ErrorActionPreference='Stop';$p='"+ROOT+'/'+case+"_TASK_START_INTENT.json';if(Test-Path -LiteralPath $p){throw 'Start consumed'};[IO.File]::WriteAllText($p,'{\"single_start_requested\":true}');Start-ScheduledTask -TaskName '"+task+"';$t=Get-ScheduledTask -TaskName '"+task+"';[PSCustomObject]@{task=$t.TaskName;state=[string]$t.State;triggers=@($t.Triggers | Where-Object {$null -ne $_}).Count;unique_start=$true}|ConvertTo-Json -Compress")
  save(case+'_TASK_STARTED_ACTUAL.json',dict(epoch=time.time(),task=started,lease=lease,lease_SHA=hashlib.sha256(blob).hexdigest(),launcher_SHA=hashlib.sha256(script.read_bytes()).hexdigest(),no_oldcase_or_main_replayed=True))
  print(json.dumps(dict(case=case,task=started,results_pending=True)),flush=True)
 except Exception as e:
  q=R/(case+'_DISPATCH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');q.write_text(json.dumps(dict(epoch=time.time(),error=repr(e),traceback=traceback.format_exc(),unknown_outcome_requires_actualread=True),ensure_ascii=False,indent=2),encoding='utf8');raise
 finally:
  if sf:sf.close()
  c.close();os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
if __name__=='__main__':main()
