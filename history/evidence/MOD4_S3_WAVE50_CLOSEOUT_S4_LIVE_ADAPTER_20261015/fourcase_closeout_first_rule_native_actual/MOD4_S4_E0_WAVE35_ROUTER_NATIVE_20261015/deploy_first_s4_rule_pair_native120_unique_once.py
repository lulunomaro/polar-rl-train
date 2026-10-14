"""Fresh source-bound native flat120 only; no learned gate, PPO or ledger write."""
from pathlib import Path
import json,sys,time,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';Q=D/'payload_v2'
sys.path.insert(0,str(W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'));import transport_249_bodyframe_current_terminal_role_v3 as t
ROOT='D:/MOD4_async_eval/'+D.name;t.ROOT=ROOT
SHARED='D:/MOD4_async_eval/MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload'
CASE='s4_rule_pair_flat80_native120_v1';TASK='MOD4_S4_RulePairFlat80_Native120_v1_20261015'
def h(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,v):
 p=R/name;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8');return p
def main():
 prep=json.loads((R/'FIRST_S4_NATIVE_RULE_PAIR_CPU_PREPARED_ACTUAL_V2.json').read_bytes());assert prep['prepared_CPU_only'] and prep['case']==CASE
 actual=json.loads((W/'MOD4_S3_WAVE50_CLOSEOUT_S4_LIVE_ADAPTER_20261015/reports/FOURCASE_FINITE_ACTUAL_HANDOFF_AND_ORIGINAL_COST_READONLY.json').read_bytes());assert actual['local_root_and_child_actual_CIM_absent']
 assert not (R/'FIRST_S4_NATIVE_UNIQUE_DEPLOY_INTENT.json').exists();z=Path(prep['package']['path']);assert h(z)==prep['package']['sha256']
 c=None;sf=None
 try:
  c=t.connect();guard=t.py(c,t.guard_code());assert guard['new_root_unused'] and guard['shared_OS_lock_free']
  task=t.ps(c,"$x=Get-ScheduledTask -TaskName '"+TASK+"' -ErrorAction SilentlyContinue;[PSCustomObject]@{exists=($null -ne $x)}|ConvertTo-Json -Compress");assert not task['exists']
  save('FIRST_S4_NATIVE_UNIQUE_DEPLOY_INTENT.json',dict(epoch=time.time(),prep=prep,guard=guard,no_GPU_started_yet=True,unknown_outcome_requires_readonly_recovery=True))
  sf=c.open_sftp();sf.get_channel().settimeout(60);sf.mkdir(ROOT);remote=ROOT+'/'+z.name
  with sf.open(remote,'wx') as f:f.write(z.read_bytes());f.flush()
  code=r'''
from pathlib import Path
import json,hashlib,zipfile,sys,torch,time,importlib.metadata as metadata
R=Path(CONTEXT['root']);Q=R/'payload';S=Path(CONTEXT['shared']);z=R/CONTEXT['zip'];H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert H(z)==CONTEXT['zipsha'] and z.stat().st_size==CONTEXT['zipbytes'] and not Q.exists();Q.mkdir();(R/'attempts').mkdir();(R/'leases').mkdir()
with zipfile.ZipFile(z) as archive:
 for n in archive.namelist():
  p=Q/n;assert p.resolve().is_relative_to(Q.resolve()) and not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(archive.read(n))
m=json.loads((Q/'RETENTION_CPU_MANIFEST_V8.json').read_bytes());assert H(Q/'RETENTION_CPU_MANIFEST_V8.json')==CONTEXT['manifestsha']
for row in m['package_files_v8']:assert H(Q/row['relative'])==row['sha256']
for row in m['shared_source_freeze']:assert H(S/row['relative'])==row['sha256']
sdk=json.loads((S/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for n,v in sdk['versions'].items():
 if v is not None:assert metadata.version(n)==v
for row in sdk['files']:assert H(row['path'])==row['sha256']
assert H(m['V7_actual_native_binding']['path'])==m['V7_actual_native_binding']['sha256']
pair=json.loads((Q/'S4_PAIR_SOURCE_MANIFEST.json').read_bytes());assert H(Q/'S4_PAIR_SOURCE_MANIFEST.json')==CONTEXT['pairsha'] and pair['mode']=='rule_eval' and pair['no_gate_learning']
counts=[]
for row,count in zip(pair['sources'],(94,102)):
 assert H(row['local_path'])==row['sha256'] and Path(row['local_path']).stat().st_size==row['bytes'];c=torch.load(row['local_path'],map_location='cpu',weights_only=False);a=[]
 def walk(v):
  if torch.is_tensor(v):
   assert v.device.type=='cpu' and (not v.is_floating_point() or torch.isfinite(v).all());a.append(v)
  elif isinstance(v,dict):
   for x in v.values():walk(x)
  elif isinstance(v,(list,tuple)):
   for x in v:walk(x)
 walk(c);assert sum(v.is_floating_point() for v in a)==count and len(c['actor_state_dict'])==9;counts.append(dict(expert=row['expert'],floating=count))
assert not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),twohost_uploaded_package_SHA=H(z),source_pair_CPU_verified=counts,manifest_SHA=H(Q/'RETENTION_CPU_MANIFEST_V8.json'),pair_manifest_SHA=H(Q/'S4_PAIR_SOURCE_MANIFEST.json'),shared_backend_stub_binding_original_SHA_exact=True,no_CUDA_or_gate_training=True)))
'''
  ctx=dict(root=ROOT,shared=SHARED,zip=z.name,zipsha=prep['package']['sha256'],zipbytes=prep['package']['bytes'],manifestsha=prep['manifest_SHA'],pairsha=prep['pair_manifest_SHA'])
  cpu=t.py(c,'CONTEXT='+repr(ctx)+'\n'+code,90);save('FIRST_S4_NATIVE_SOURCE_UPLOAD_AND_TARGET_CPU_ACTUAL.json',cpu)
  fresh=t.py(c,t.guard_code());assert not fresh['new_root_unused'] and fresh['shared_OS_lock_free']
  m=json.loads((Q/'RETENTION_CPU_MANIFEST_V8.json').read_bytes());pair=json.loads((Q/'S4_PAIR_SOURCE_MANIFEST.json').read_bytes());names=('retention_native_witness_v8.py','retention_flat_native_v8.py','raycast_hit_serializer_v5.py')
  lease=dict(epoch=time.time(),case_id=CASE,target_host='10.24.4.249',namespace=D.name,GPU_lease_granted_by_root=True,actual_shared_slot_idle_verified=True,resource_boundary=fresh,checkpoint_path=pair['sources'][1]['local_path'],checkpoint_sha256=pair['sources'][1]['sha256'],worker_sha256=prep['worker_SHA'],port_sources_sha256={n:h(Q/n) for n in names},shared_payload_target=SHARED,case_parameters=dict(kind='flat',steps=120,num_envs=80,seed=20261002,headless=True,device='cuda:0'),source_pair_manifest_SHA=prep['pair_manifest_SHA'],CPU_runtime_probability_proof_SHA=h(W/'MOD4_S3_WAVE50_CLOSEOUT_S4_LIVE_ADAPTER_20261015/reports/S4_SHARED_TICK_ROUTER_JOINT_PROBABILITY_AND_CPU_FULLSAVE_ACTUAL.json'),scope='first stateless frozen two-expert rule routing on original flat120 only; not35 transition or learned gate',no_PPO=True,no_new_canonical_transaction=True)
  save('FIRST_S4_NATIVE_OWN_PARAMETER_BOUND_LEASE_ACTUAL.json',lease)
  with sf.open(ROOT+'/leases/'+CASE+'.json','wx') as f:f.write(json.dumps(lease,indent=2).encode());f.flush()
  launcher="""from pathlib import Path
import sys,subprocess,json,time,os,psutil
R=Path(__file__).resolve().parent;case=CASE;assert not (R/(case+'_START_INTENT.json')).exists()
(R/(case+'_START_INTENT.json')).write_text(json.dumps(dict(epoch=time.time(),pid=os.getpid(),creation=psutil.Process().create_time(),no_PPO=True)))
argv=[sys.executable,str(R/'payload/retention_parent_v8.py'),'--lease',str(R/'leases'/(case+'.json')),'--attempt',str(R/'attempts'/case)]
with (R/(case+'_PARENT_CONSOLE.log')).open('xb') as log:
 p=subprocess.Popen(argv,cwd=R/'payload',stdout=log,stderr=subprocess.STDOUT)
 (R/(case+'_PARENT_PID.json')).write_text(json.dumps(dict(pid=p.pid,creation=psutil.Process(p.pid).create_time(),argv=argv)))
 rc=p.wait()
(R/(case+'_LAUNCH_EXIT.json')).write_text(json.dumps(dict(epoch=time.time(),exit_code=rc,no_PPO=True)))
sys.exit(rc)
""".replace('CASE',repr(CASE))
  script=D/('demand_'+CASE+'_once.py');assert not script.exists();compile(launcher,str(script),'exec');script.write_text(launcher,encoding='utf8');sf.put(str(script),ROOT+'/'+script.name)
  setup=t.ps(c,"$ErrorActionPreference='Stop';$name='"+TASK+"';if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'Task exists'};$a=New-ScheduledTaskAction -Execute '"+t.PY+"' -Argument '\""+ROOT+'/'+script.name+"\"' -WorkingDirectory '"+ROOT+"';$p=New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited;$s=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew;Register-ScheduledTask -TaskName $name -Action $a -Principal $p -Settings $s|Out-Null;Start-ScheduledTask -TaskName $name;$t=Get-ScheduledTask -TaskName $name;[PSCustomObject]@{task=$name;state=[string]$t.State;triggers=@($t.Triggers|Where-Object {$null -ne $_}).Count}|ConvertTo-Json -Compress")
  assert setup['triggers']==0;save('FIRST_S4_NATIVE_UNIQUE_TASK_DISPATCH_ACTUAL.json',dict(epoch=time.time(),task=setup,case=CASE,source_pair=pair['sources'],scope_native120_only=True,new_gate_not_trained=True,only_actor_pair_frozen_GPU_eval=True,no_PPO_budgetwrite_or_oldGPUreplay=True));print(json.dumps(dict(dispatched=True,task=setup,case=CASE,new_native_result_pending=True,no_PPO=True)))
 except BaseException:
  save('FIRST_S4_NATIVE_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_outcome_requires_actual_readonly_recovery=True,no_retry=True));raise
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':main()
