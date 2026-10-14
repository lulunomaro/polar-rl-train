"""One actual new original35 pair-router native case; no gate/PPO/ledger writes."""
from pathlib import Path
import sys,json,time,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';Q=D/'payload_v2';ROOT='D:/MOD4_async_eval/'+D.name
sys.path.insert(0,str(W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'))
import transport_249_bodyframe_current_terminal_role_v3 as t
t.ROOT=ROOT;CASE='s4_rule_original35_transition_native120_v1';TASK='MOD4_S4_Original35Rule_Native120_v1_20261015';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):
 p=R/n;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
def main():
 prep=json.loads((R/'S4_ORIGINAL35_TRANSITION_RULE_SOURCE_CPU_PREPARED_ACTUAL_V2.json').read_bytes());assert prep['own_V2_identity_metadata_explicit'] and prep['no_SSH_GPU_PPO_or_budgetwrite']
 previous=json.loads((W/'MOD4_S4_E0_WAVE35_ROUTER_NATIVE_20261015/reports/FIRST_S4_OWN_NATIVE120_WHOLE_PHYSICAL_AND_ROUTER_CPU_ADMITTED.json').read_bytes());assert previous['passed'] and previous['boundary']['actual_child_absent'] and previous['boundary']['shared_OS_lock_free']
 assert not (R/'S4_ORIGINAL35_NATIVE_UNIQUE_DEPLOY_INTENT.json').exists();z=Path(prep['package']['path']);assert H(z)==prep['package']['sha256']
 c=None;sf=None
 try:
  c=t.connect();guard=t.py(c,t.guard_code());assert guard['new_root_unused'] and guard['shared_OS_lock_free']
  task=t.ps(c,"$t=Get-ScheduledTask -TaskName '"+TASK+"' -ErrorAction SilentlyContinue;[PSCustomObject]@{exists=($null-ne $t)}|ConvertTo-Json -Compress");assert not task['exists']
  save('S4_ORIGINAL35_NATIVE_UNIQUE_DEPLOY_INTENT.json',dict(epoch=time.time(),case=CASE,guard=guard,prep=prep,no_GPU_started=True,unknown_mutation_requires_actual_readonly_recovery=True))
  sf=c.open_sftp();sf.get_channel().settimeout(60);sf.mkdir(ROOT)
  with sf.open(ROOT+'/'+z.name,'wx') as f:f.write(z.read_bytes());f.flush()
  code=r'''
from pathlib import Path
import json,zipfile,hashlib,torch,importlib.metadata as metadata,time
R=Path(CONTEXT['root']);Q=R/'payload';z=R/CONTEXT['zip'];H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not Q.exists() and H(z)==CONTEXT['zipSHA'] and z.stat().st_size==CONTEXT['zipbytes'];Q.mkdir();(R/'attempts').mkdir();(R/'leases').mkdir()
with zipfile.ZipFile(z) as archive:
 for n in archive.namelist():
  p=Q/n;assert p.resolve().is_relative_to(Q.resolve()) and not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(archive.read(n))
m=json.loads((Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json').read_bytes());assert H(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json')==CONTEXT['manifestSHA'] and m['source_SHA']==CONTEXT['anchor']
for row in m['file_rows']:assert (Q/row['relative']).stat().st_size==row['bytes'] and H(Q/row['relative'])==row['sha256']
sdk=json.loads((Q/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for n,v in sdk['versions'].items():
 if v is not None:assert metadata.version(n)==v
for row in sdk['files']:assert H(row['path'])==row['sha256']
pair=json.loads((Q/'S4_PAIR_SOURCE_MANIFEST.json').read_bytes());assert pair['sources']==m['source_pair'] and pair['mode']=='rule_eval' and pair['no_gate_learning']
counts=[]
for row,count in zip(pair['sources'],(94,102)):
 assert H(row['local_path'])==row['sha256'] and Path(row['local_path']).stat().st_size==row['bytes'];source=torch.load(row['local_path'],map_location='cpu',weights_only=False);tensors=[]
 def walk(v):
  if torch.is_tensor(v):assert v.device.type=='cpu' and (not v.is_floating_point() or torch.isfinite(v).all());tensors.append(v)
  elif isinstance(v,dict):
   for x in v.values():walk(x)
  elif isinstance(v,(tuple,list)):
   for x in v:walk(x)
 walk(source);assert sum(x.is_floating_point() for x in tensors)==count and len(source['actor_state_dict'])==9
 counts.append(dict(expert=row['expert'],floating=count,sha256=H(row['local_path'])))
 if row['expert']=='E1_WAVE35':assert source['E1_terrain_state']['profile']=='mod4_G3_CAD_derived_35mm_v1' and source['E1_terrain_state']['G3_profile_sha256']==H(Q/'runtime/isaac/mod4/g3_cad_profile.json')
assert not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),uploaded_packageSHA=H(z),manifestSHA=H(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'),all_source_files=len(m['file_rows']),source_pair_CPU=counts,SDK_source_binding_original_exact=True,original_G3_profile_source_exact=True,no_CUDA_PPO_or_budgetwrite=True)))
'''
  anchor=prep['source_pair'][1]['sha256'];ctx=dict(root=ROOT,zip=z.name,zipSHA=prep['package']['sha256'],zipbytes=prep['package']['bytes'],manifestSHA=prep['manifest']['sha256'],anchor=anchor)
  cpu=t.py(c,'CONTEXT='+repr(ctx)+'\n'+code,90);save('S4_ORIGINAL35_PACKAGE_TARGET_CPU_ACTUAL.json',cpu)
  fresh=t.py(c,t.guard_code());assert not fresh['new_root_unused'] and fresh['shared_OS_lock_free']
  lease=dict(epoch=time.time(),case_id=CASE,target_host='10.24.4.249',namespace=D.name,GPU_lease_granted_by_root=True,actual_shared_slot_idle_verified=True,resource_boundary=fresh,checkpoint_path=ROOT+'/payload/source/E1_WAVE35_frozen_source.pt',checkpoint_sha256=anchor,worker_sha256=prep['worker']['sha256'],factor_runtime_sha256=prep['runtime']['sha256'],source_bundle_manifest_sha256=prep['manifest']['sha256'],source_pair=prep['source_pair'],source_pair_manifest_SHA=H(Q/'S4_PAIR_SOURCE_MANIFEST.json'),case_parameters=dict(steps=120,num_envs=80,seed=20260928,body_sign=1,world_sign=1,feedback_current=False,headless=True,device='cuda:0'),scope='own original35 tenwaves flat-support route pair native120; not full15s, training fullstate or gate admission',no_PPO=True,no_new_canonical_transaction=True)
  save('S4_ORIGINAL35_OWN_NATIVE120_PARAMETER_BOUND_LEASE_ACTUAL.json',lease)
  with sf.open(ROOT+'/leases/'+CASE+'.json','wx') as f:f.write(json.dumps(lease,indent=2).encode());f.flush()
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
  result=t.ps(c,"$ErrorActionPreference='Stop';$n='"+TASK+"';if(Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue){throw 'Task exists'};$a=New-ScheduledTaskAction -Execute '"+t.PY+"' -Argument '\""+ROOT+'/'+script.name+"\"' -WorkingDirectory '"+ROOT+"';$p=New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited;$s=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew;Register-ScheduledTask -TaskName $n -Action $a -Principal $p -Settings $s|Out-Null;Start-ScheduledTask -TaskName $n;$t=Get-ScheduledTask -TaskName $n;[PSCustomObject]@{task=$n;state=[string]$t.State;triggers=@($t.Triggers|Where-Object {$null-ne $_}).Count}|ConvertTo-Json -Compress")
  assert result['triggers']==0;save('S4_ORIGINAL35_NATIVE_UNIQUE_TASK_DISPATCH_ACTUAL.json',dict(epoch=time.time(),task=result,case=CASE,lease=lease,native_actual_result_pending=True,gate_training_not_admitted=True));print(json.dumps(dict(dispatched=True,task=result,case=CASE,no_PPO=True)))
 except BaseException:
  save('S4_ORIGINAL35_NATIVE_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_blind_retry=True,unknown_outcome_actual_readonly_first=True));raise
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':main()
