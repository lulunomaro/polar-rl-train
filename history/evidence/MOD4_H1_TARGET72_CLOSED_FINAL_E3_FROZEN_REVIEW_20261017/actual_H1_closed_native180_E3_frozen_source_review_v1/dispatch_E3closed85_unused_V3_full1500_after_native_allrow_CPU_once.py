"""Fresh isolated3060 native120 only, after exact resource/source/SDK CPU admission; no PPO."""
from pathlib import Path
import json,sys,time,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';E=D/'e3_closed85_frozen_prepared_v2';Q=E/'payload';N=W/'MOD4_TWO72_E2_E3_HEALTHY_SAVED_CONTINUATIONS_20261017'
sys.path[:0]=[str(D),str(W/'MOD4_TWO72_CLOSED_SOURCES_HEALTHY_NEXT_BLOCK_20261017'),str(N/'curb275_final87_frozen3060_v1'),str(W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014')]
import transport_249_E3_current_exact_desktop_2145_v1 as t
ROOT='D:/MOD4_async_eval/MOD4_H1_TARGET72_CLOSED_FINAL_E3_FROZEN_REVIEW_20261017/E3_CLOSED85_FROZEN_V3';t.ROOT=ROOT
CASE='e3closed85_public03_full1500_v3';TASK='MOD4_E3_CLOSED85_PUBLIC03_FULL1500_V3_20261017';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):
 with (R/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2)
def main():
 proof=json.loads((R/'E3_FROZEN_V2_QUERY104_PREFIX_AND_DR_PHASE_READBACK_COVERAGE_CPU_ACTUAL.json').read_bytes());assert proof['passed_pre_dispatch_actual_query104_prefix_and_source_coverage_CPU']
 native=json.loads((R/'E3_CLOSED85_120_ALL_PHYSICAL_PUBLIC03_SOURCE_CPU_ACTUAL.json').read_bytes());assert native['passed_complete_data_and_source_CPU'] and native['steps']==120 and native['callbacks']==480 and native['actual_parent_child_launcherout_and_MSVCRTfree']
 prep=json.loads((R/'E3_CLOSED85_NATIVE120_V2_EXACT_DEPLOY_BINDINGS_CPU_PREPARED.json').read_bytes());assert prep['passed_complete_payload_CPU_only'];assert not (R/'E3_CLOSED85_FULL1500_V3_DISPATCH_INTENT_ACTUAL.json').exists();c=sf=None
 try:
  c=t.connect();resource=t.py(c,t.guard_code(),90);assert resource['shared_OS_lock_free'] and not resource['new_root_unused']
  unused=t.ps(c,"$n='"+TASK+"';$t=Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue;[PSCustomObject]@{exists=($null-ne $t)}|ConvertTo-Json -Compress");assert not unused['exists']
  save('E3_CLOSED85_FULL1500_V3_DISPATCH_INTENT_ACTUAL.json',dict(epoch=time.time(),resource=resource,source=prep['source'],steps=1500,callbacks6000_pending=True,no_PPO=True,unknown_outcome_requires_readonly_no_replay=True))
  C=dict(root=ROOT,package=Path(prep['package']['path']).name,packageSHA=prep['package']['SHA'],packagebytes=prep['package']['bytes'],manifestSHA=prep['manifest']['SHA'],sourceSHA=prep['source']['SHA'],case=CASE)
  create=dict(own_source85_native120_physical_CPU_actually_passed=True,sealed_V2_payload_reused_for_new_unused_full_case_only=True)
  save('E3_CLOSED85_FULL1500_V3_OWN_ROOT_ACTUAL.json',create);sf=c.open_sftp();sf.get_channel().settimeout(120);assert H(prep['package']['path'])==C['packageSHA']
  code=r'''
from pathlib import Path
import ast,hashlib,json,zipfile,sys,torch,importlib.metadata as metadata
R=Path(C['root']);B=R/C['package'];Q=R/'payload';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert Q.is_dir() and B.stat().st_size==C['packagebytes'] and H(B)==C['packageSHA']
m=Q/'E3_CLOSED85_FROZEN_COMPLETE_MANIFEST_V2.json';assert H(m)==C['manifestSHA'];manifest=json.loads(m.read_bytes());assert manifest['source']['SHA']==C['sourceSHA']
for row in manifest['files']:
 p=Q/row['relative'];assert p.resolve().is_relative_to(Q.resolve()) and p.stat().st_size==row['bytes'] and H(p)==row['SHA'],row['relative']
 if p.suffix=='.py':ast.parse(p.read_text('utf8'))
sdk=json.loads((Q/'frozen_shared/EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for name,version in sdk['versions'].items():
 if version is not None:assert metadata.version(name)==version
for row in sdk['files']:assert H(row['path'])==row['sha256']
sys.path.insert(0,str(Q));from recovery_closed85_source_guard_v1 import validate_E3_source
source=Q/manifest['source_relative'];assert H(source)==C['sourceSHA'];checkpoint=torch.load(source,map_location='cpu',weights_only=False);proof=validate_E3_source(checkpoint);counts=[0,0]
def walk(x):
 if torch.is_tensor(x):counts[0]+=1;counts[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
 elif isinstance(x,dict):
  for v in x.values():walk(v)
 elif isinstance(x,(tuple,list)):
  for v in x:walk(v)
walk(checkpoint);assert counts==[173,96];before=torch.get_rng_state().clone()
from recovery_closed85_single35_public03_perenv_CPU_v2 import Single35
actor=Single35(source,104,'cpu');assert actor.exact() and torch.equal(before,torch.get_rng_state()) and not torch.cuda.is_initialized()
assert (R/'attempts').is_dir() and (R/'leases').is_dir() and not (R/'attempts'/C['case']).exists() and not (R/'leases'/(C['case']+'.json')).exists()
print(json.dumps(dict(epoch=__import__('time').time(),target_CPU_passed=True,source_CPU=proof,source_SHA=H(source),all_tensors=counts,all_manifest_files_verified=len(manifest['files']),installed_SDK_source_and_DLL_bindings_exact=True,source9_STD_exact_and_CPU_RNG_unchanged=True,no_CUDA_PPO_or_Task_yet=True)))
'''
  cpu=t.py(c,'C='+repr(C)+'\n'+code,180);save('E3_CLOSED85_FULL1500_V3_TARGET_SOURCE_SDK_CPU_ACTUAL.json',cpu)
  resource=t.py(c,t.guard_code(),90);assert resource['shared_OS_lock_free'] and not resource['new_root_unused']
  lease=dict(epoch=time.time(),case_id=CASE,target_host='10.24.4.249',namespace='E3_CLOSED85_PUBLIC03_FROZEN_V2_20261017',GPU_lease_granted_by_root=True,actual_shared_slot_idle_verified=True,resource_boundary=resource,checkpoint_path=ROOT+'/payload/'+json.loads((Q/'E3_CLOSED85_FROZEN_COMPLETE_MANIFEST_V2.json').read_bytes())['source_relative'],checkpoint_sha256=prep['source']['SHA'],worker_sha256=prep['worker']['SHA'],parent_sha256=prep['parent']['SHA'],source_manifest_sha256=prep['manifest']['SHA'],shared_payload_target=ROOT+'/payload/frozen_shared',case_parameters=dict(router_mode='single_eval',kind='recovery',steps=1500,num_envs=104,seed=20260928,headless=True,device='cuda:0'),frozen0PPO0canonical=True,actual_same_source_native120_independent_CPU_passed=True,native120_actual_exit_childrenout_lockfree=True,native_actual_CPU_report_SHA=H(R/'E3_CLOSED85_120_ALL_PHYSICAL_PUBLIC03_SOURCE_CPU_ACTUAL.json'),full1500_result_pending_not_skill_pass=True)
  assert lease['checkpoint_path']==ROOT+'/payload/source/E3_closed85.pt'
  binding=t.py(c,"from pathlib import Path;import hashlib,json;P=Path("+repr(lease['checkpoint_path'])+");assert hashlib.sha256(P.read_bytes()).hexdigest()=="+repr(lease['checkpoint_sha256'])+";print(json.dumps(dict(checkpoint_actual_path=str(P),source_SHA="+repr(lease['checkpoint_sha256'])+",before_lease_Task_GPU=True)))")
  save('E3_CLOSED85_FULL1500_V3_EXACT_PRETASK_CHECKPOINT_BINDING_ACTUAL.json',binding)
  save('E3_CLOSED85_FULL1500_V3_ROOT_LEASE_ACTUAL.json',lease)
  with sf.open(ROOT+'/leases/'+CASE+'.json','wx') as f:f.write(json.dumps(lease,indent=2).encode('utf8'));f.flush()
  launcher='''from pathlib import Path
import subprocess,sys,json,time,os,psutil,hashlib
R=Path(__file__).resolve().parent;case=CASE;assert not (R/(case+'_START_INTENT.json')).exists()
lease=R/'leases'/(case+'.json');v=json.loads(lease.read_bytes());p=R/'payload/e3_frozen_parent_v2.py';assert hashlib.sha256(p.read_bytes()).hexdigest()==v['parent_sha256']
(R/(case+'_START_INTENT.json')).write_text(json.dumps(dict(epoch=time.time(),pid=os.getpid(),creation=psutil.Process().create_time(),no_PPO=True)))
argv=[sys.executable,str(p),'--lease',str(lease),'--attempt',str(R/'attempts'/case)]
with (R/(case+'_PARENT_CONSOLE.log')).open('xb') as log:
 child=subprocess.Popen(argv,cwd=R/'payload',stdout=log,stderr=subprocess.STDOUT);(R/(case+'_PARENT_PID.json')).write_text(json.dumps(dict(pid=child.pid,creation=psutil.Process(child.pid).create_time(),argv=argv)));rc=child.wait()
(R/(case+'_LAUNCH_EXIT.json')).write_text(json.dumps(dict(epoch=time.time(),exit_code=rc,no_PPO=True)));sys.exit(rc)
'''.replace('CASE',repr(CASE));p=D/'demand_E3closed85_full1500_V3_unused_once.py';assert not p.exists();compile(launcher,str(p),'exec');p.write_text(launcher,encoding='utf8',newline='\n');sf.put(str(p),ROOT+'/'+p.name)
  script=ROOT+'/'+p.name
  task=t.ps(c,"$ErrorActionPreference='Stop';$n='"+TASK+"';if(Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue){throw 'Task exists'};$a=New-ScheduledTaskAction -Execute '"+t.PY+"' -Argument '\""+script+"\"' -WorkingDirectory '"+ROOT+"';$p=New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited;$s=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew;Register-ScheduledTask -TaskName $n -Action $a -Principal $p -Settings $s|Out-Null;Start-ScheduledTask -TaskName $n;$t=Get-ScheduledTask -TaskName $n;[PSCustomObject]@{task=$n;state=[string]$t.State;triggers=@($t.Triggers|Where-Object {$null-ne $_}).Count}|ConvertTo-Json -Compress")
  assert task['triggers']==0;save('E3_CLOSED85_FULL1500_V3_TASK_DISPATCHED_PENDING_ACTUAL.json',dict(epoch=time.time(),task=task,root=ROOT,case=CASE,no_PPO=True,lease=lease,not_native_or_skill_pass=True));print(json.dumps(dict(full1500_dispatched=True,task=task,root=ROOT,no_PPO=True)),flush=True)
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:
  save('E3_CLOSED85_FULL1500_V3_DISPATCH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_outcome_readonly_first_no_replay=True));raise
