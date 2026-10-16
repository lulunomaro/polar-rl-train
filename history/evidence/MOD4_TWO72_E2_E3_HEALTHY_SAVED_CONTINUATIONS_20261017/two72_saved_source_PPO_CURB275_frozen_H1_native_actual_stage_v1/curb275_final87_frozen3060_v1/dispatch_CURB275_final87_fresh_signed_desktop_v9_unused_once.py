"""Source/resource-bound new native or full case on3060, never replay an old scope."""
from pathlib import Path
import argparse,hashlib,json,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parents[1];R=D/'reports';Q=D/'eval_payload_v2';ROOT='D:/MOD4_async_eval/MOD4_TWO72_E2_E3_HEALTHY_SAVED_CONTINUATIONS_20261017/curb275_final87_frozen3060_v1'
sys.path.insert(0,str(W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'));import transport_249_fresh_signed_desktop_exact_0112_v8 as t
t.ROOT=ROOT
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,x):
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
def main():
 p=argparse.ArgumentParser();p.add_argument('--steps',type=int,choices=(120,1500),required=True);p.add_argument('--execute-own-unused-case',action='store_true');a=p.parse_args();assert a.execute_own_unused_case;steps=a.steps;case=f'curb275_final87_{steps}_v2';task=f'MOD4_CURB275_FINAL87_3060_{steps}_v2_20261017';prep=json.loads((R/'CURB275_FINAL87_FROZEN3060_CPU_PACKAGE_PREPARED_ACTUAL.json').read_bytes());assert prep['passed_CPU_only'];assert not (R/(case+'_PARENTFIX_DISPATCH_INTENT.json')).exists()
 if steps==1500:
  v=json.loads((R/'CURB275_FINAL87_NATIVE120_COMPLETE_PHYSICAL_SOURCE_CPU_ADMITTED.json').read_bytes());assert v['passed'] and v['controls']==120 and v['parent_child_actual_absent_lock_free']
 c=sf=None
 try:
  c=t.connect();g=t.py(c,t.guard_code());assert g['shared_OS_lock_free'] and g['new_root_unused']==(steps==120)
  unused=t.ps(c,"$t=Get-ScheduledTask -TaskName '"+task+"' -ErrorAction SilentlyContinue;[PSCustomObject]@{exists=($null-ne $t)}|ConvertTo-Json -Compress");assert not unused['exists'];save(case+'_PARENTFIX_DISPATCH_INTENT.json',dict(epoch=time.time(),case=case,resource=g,source=prep['source'],no_PPO=True,unknown_outcome_readonly_first_no_replay=True))
  sf=c.open_sftp();sf.get_channel().settimeout(90)
  if steps==120:
   parent_guard=t.py(c,"from pathlib import Path;import json;B=Path("+repr(ROOT)+");P=B.parent;A=Path('D:/MOD4_async_eval');assert P.resolve().is_relative_to(A.resolve()) and P.parent.resolve()==A.resolve() and not P.is_symlink() and not B.exists();P.mkdir(exist_ok=True);assert P.is_dir() and not P.is_symlink();print(json.dumps(dict(parent=str(P),resolved=str(P.resolve()),own_parent_ready=True,no_delete_or_GPU=True)))");save(case+'_PARENT_ROOT_GUARD_ACTUAL.json',parent_guard)
   sf.mkdir(ROOT);copied=t.py(c,"from pathlib import Path;import shutil,json;A=Path("+repr('D:/MOD4_async_eval/MOD4_THREE4090_CURB_DIRECTION_AND_E3_RECOVERY_20261016/curb_v7final147_frozen35_3060_v1')+");B=Path("+repr(ROOT)+");assert A.is_relative_to(Path('D:/MOD4_async_eval')) and not (B/'payload').exists();shutil.copytree(A/'payload',B/'payload');print(json.dumps(dict(existing_exact_payload_copied=True,no_GPU=True)))");save(case+'_EXISTING_SOURCE_REUSE_ACTUAL.json',copied)
   for name in ('s5_single_frozen35_v1.py','paired_full80_parameter_bound_v2.py','REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json','source/CURB275_first_final87.pt','full80_runtime_native_v1.py','runtime/isaac/mod4/curb35_profile.json','runtime/isaac/mod4/curb35_geometry.py'):sf.put(str(Q/name),ROOT+'/payload/'+name)
  C=dict(root=ROOT,steps=steps,case=case,package=Path(prep['package']['path']).name,packageSHA=prep['package']['sha256'],packagebytes=prep['package']['bytes'],manifestSHA=prep['manifest_SHA'],source=prep['source'])
  code=r'''
from pathlib import Path
import hashlib,json,zipfile,sys,torch,importlib.metadata as metadata
R=Path(C['root']);Q=R/'payload';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if C['steps']==120:
 assert Q.is_dir();(R/'attempts').mkdir();(R/'leases').mkdir()
assert H(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json')==C['manifestSHA'];m=json.loads((Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json').read_bytes());assert m['source_single_policy']==C['source']
for r in m['file_rows']:assert (Q/r['relative']).stat().st_size==r['bytes'] and H(Q/r['relative'])==r['sha256'],r['relative']
sdk=json.loads((Q/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for k,v in sdk['versions'].items():
 if v is not None:assert metadata.version(k)==v
for r in sdk['files']:assert H(r['path'])==r['sha256']
source=Path(C['source']['local_path']);assert H(source)==C['source']['sha256'];ck=torch.load(source,map_location='cpu',weights_only=False);ts=[]
def walk(x):
 if torch.is_tensor(x):assert not x.is_floating_point() or torch.isfinite(x).all();ts.append(x)
 elif isinstance(x,dict):
  for v in x.values():walk(v)
 elif isinstance(x,(tuple,list)):
  for v in x:walk(v)
walk(ck);assert len(ts)==181 and sum(x.is_floating_point() for x in ts)==102 and ck['E1_terrain_state']['num_envs']==20000
assert ck['E1_terrain_state']['CURB_height_m']==.0275 and ck['E1_terrain_state']['CURB_strip_width_m']==.150 and ck['E1_terrain_state']['CURB_profile_sha256']==H(Q/'runtime/isaac/mod4/curb35_profile.json')
sys.path.insert(0,str(Q));from s5_single_frozen35_v1 import Single35
rng=torch.get_rng_state().clone();actor=Single35(source,80,'cpu');assert actor.exact() and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
assert not (R/'attempts'/C['case']).exists() and not (R/'leases'/(C['case']+'.json')).exists()
print(json.dumps(dict(targetCPU_actual=True,sourceSHA=H(source),finite_tensors=len(ts),floating=102,source9_STD_exact=True,all_source_files=len(m['file_rows']),SDK_source_binding_exact=True,no_CUDA_or_PPO=True)))
'''
  cpu=t.py(c,'C='+repr(C)+'\n'+code,120);save(case+'_TARGET_CPU_ACTUAL.json',cpu);fresh=t.py(c,t.guard_code());assert fresh['shared_OS_lock_free']
  lease=dict(epoch=time.time(),case_id=case,target_host='10.24.4.249',namespace=D.name,GPU_lease_granted_by_root=True,actual_shared_slot_idle_verified=True,resource_boundary=fresh,checkpoint_path=prep['source']['local_path'],checkpoint_sha256=prep['source']['sha256'],worker_sha256=prep['worker_SHA'],factor_runtime_sha256=prep['runtime_SHA'],source_bundle_manifest_sha256=prep['manifest_SHA'],case_parameters=dict(steps=steps,num_envs=80,seed=20260928,body_sign=1,world_sign=1,feedback_current=False,headless=True,device='cuda:0'),frozen_no_PPO=True,not_training_full20k_DR_resume=True)
  save(case+'_LEASE_ACTUAL.json',lease)
  with sf.open(ROOT+'/leases/'+case+'.json','wx') as f:f.write(json.dumps(lease,indent=2).encode());f.flush()
  launcher='''from pathlib import Path
import subprocess,sys,json,time,os,psutil
R=Path(__file__).resolve().parent;case=CASE;assert not (R/(case+'_START_INTENT.json')).exists()
(R/(case+'_START_INTENT.json')).write_text(json.dumps(dict(epoch=time.time(),pid=os.getpid(),creation=psutil.Process().create_time(),no_PPO=True)))
argv=[sys.executable,str(R/'payload/run_full80_parameter_bound_parent_v2.py'),'--lease',str(R/'leases'/(case+'.json')),'--attempt',str(R/'attempts'/case)]
with (R/(case+'_PARENT_CONSOLE.log')).open('xb') as log:
 p=subprocess.Popen(argv,cwd=R/'payload',stdout=log,stderr=subprocess.STDOUT);(R/(case+'_PARENT_PID.json')).write_text(json.dumps(dict(pid=p.pid,creation=psutil.Process(p.pid).create_time(),argv=argv)));rc=p.wait()
(R/(case+'_LAUNCH_EXIT.json')).write_text(json.dumps(dict(epoch=time.time(),exit_code=rc,no_PPO=True)));sys.exit(rc)
'''.replace('CASE',repr(case));script=D/('demand_'+case+'_once.py');assert not script.exists();compile(launcher,str(script),'exec');script.write_text(launcher,encoding='utf8');sf.put(str(script),ROOT+'/'+script.name)
  taskv=t.ps(c,"$ErrorActionPreference='Stop';$n='"+task+"';if(Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue){throw 'Task exists'};$a=New-ScheduledTaskAction -Execute '"+t.PY+"' -Argument '\""+ROOT+'/'+script.name+"\"' -WorkingDirectory '"+ROOT+"';$p=New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited;$s=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew;Register-ScheduledTask -TaskName $n -Action $a -Principal $p -Settings $s|Out-Null;Start-ScheduledTask -TaskName $n;$t=Get-ScheduledTask -TaskName $n;[PSCustomObject]@{task=$n;state=[string]$t.State;triggers=@($t.Triggers|Where-Object {$null-ne $_}).Count}|ConvertTo-Json -Compress")
  assert taskv['triggers']==0;save(case+'_DISPATCH_ACTUAL.json',dict(epoch=time.time(),case=case,task=taskv,lease=lease,actual_result_pending=True));print(json.dumps(dict(dispatched=True,case=case,task=taskv)),flush=True)
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:
  save('CURB275_FINAL87_DISPATCH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_outcome_readonly_first=True));raise
