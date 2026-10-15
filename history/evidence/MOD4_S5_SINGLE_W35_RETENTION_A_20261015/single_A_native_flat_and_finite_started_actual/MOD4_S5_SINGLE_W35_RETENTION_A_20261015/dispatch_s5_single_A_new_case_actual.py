"""Own new single-policy case only; actual source/native/resource lease bound."""
from pathlib import Path
import argparse,hashlib,json,sys,time,traceback
D=Path(__file__).resolve().parent;Q=D/'payload';R=D/'reports'
import transport_s5_single_retention_A_actual as t
ROOT=t.ROOT;SHARED='D:/MOD4_async_eval/MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):
 p=R/n;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
def main():
 p=argparse.ArgumentParser();p.add_argument('--kind',required=True,choices=('flat','spin','world'));p.add_argument('--steps',required=True,type=int,choices=(120,1500));p.add_argument('--native-proof');p.add_argument('--source-proof');p.add_argument('--execute-root-new-single-case',action='store_true');a=p.parse_args();assert a.execute_root_new_single_case
 case=f's5_single_W35_{a.kind}_{a.steps}_v1';task='MOD4_S5_SingleW35RetentionA_20261015_'+case
 assert not (R/(case+'_INTENT_ACTUAL.json')).exists() and json.loads((R/'S5_SINGLE_A_UPLOAD_TARGET_CPU_ACTUAL.json').read_bytes())['actual_targetCPU']
 if a.steps==1500:
  assert a.native_proof and a.source_proof;x=json.loads(Path(a.native_proof).read_bytes())['result'];s=json.loads(Path(a.source_proof).read_bytes())
  assert x['kind']==a.kind and x['steps']==120 and x['data']['complete_data_contract'] and s['passed'] and s['controls']==120 and s['source9_STD_initial_final_exact']
 prep=json.loads((R/'S5_SINGLE_RETENTION_A_CPU_PREPARED_ACTUAL.json').read_bytes());source=prep['source_single'];c=sf=None
 try:
  c=t.connect();guard=t.py(c,t.guard_code());assert not guard['new_root_unused'] and guard['shared_OS_lock_free']
  state=t.ps(c,"$x=Get-ScheduledTask -TaskName '"+task+"' -ErrorAction SilentlyContinue;[PSCustomObject]@{exists=($null-ne $x)}|ConvertTo-Json -Compress");assert not state['exists']
  code=r'''
from pathlib import Path
import hashlib,json,sys,torch,importlib.metadata as metadata
R=Path(C['root']);Q=R/'payload';S=Path(C['shared']);H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert H(Q/'RETENTION_CPU_MANIFEST_V8.json')==C['manifestSHA'];m=json.loads((Q/'RETENTION_CPU_MANIFEST_V8.json').read_bytes())
for row in m['package_files_v8']:assert H(Q/row['relative'])==row['sha256']
for row in m['shared_source_freeze']:assert H(S/row['relative'])==row['sha256']
assert H(m['V7_actual_native_binding']['path'])==m['V7_actual_native_binding']['sha256'] and H(m['v5_sdk_primary_stub']['actual_installed_stub_path'])==m['v5_sdk_primary_stub']['actual_sha256']
sdk=json.loads((S/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for n,v in sdk['versions'].items():
 if v is not None:assert metadata.version(n)==v
for row in sdk['files']:assert H(row['path'])==row['sha256']
source=m['source_single'];assert source==C['source'] and H(source['local_path'])==source['sha256']
sys.path.insert(0,str(Q));from s5_single_frozen35_v1 import Single35
rng=torch.get_rng_state().clone();single=Single35(source['local_path'],C['n'],'cpu');assert single.exact() and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
assert not (R/'attempts'/C['case']).exists() and not (R/'leases'/(C['case']+'.json')).exists() and not (R/(C['case']+'_START_INTENT.json')).exists()
print(json.dumps(dict(new_case_unused=True,targetCPU_actual_source9_STD_and_SDK_exact=True,sourceSHA=source['sha256'],no_GPU=True)))
'''
  ctx=dict(root=ROOT,shared=SHARED,manifestSHA=prep['manifest_SHA'],source=source,n=80 if a.kind=='flat' else 88,case=case)
  actual=t.py(c,'C='+repr(ctx)+'\n'+code,90);save(case+'_TARGET_CPU_ACTUAL.json',actual)
  fresh=t.py(c,t.guard_code());assert fresh['shared_OS_lock_free']
  lease=dict(epoch=time.time(),case_id=case,target_host='10.24.4.249',namespace=D.name,GPU_lease_granted_by_root=True,actual_shared_slot_idle_verified=True,resource_boundary=fresh,checkpoint_path=source['local_path'],checkpoint_sha256=source['sha256'],worker_sha256=prep['worker_SHA'],port_sources_sha256={n:H(Q/n) for n in ('retention_native_witness_v8.py','retention_'+a.kind+'_native_v8.py','raycast_hit_serializer_v5.py')},shared_payload_target=SHARED,case_parameters=dict(kind=a.kind,steps=a.steps,num_envs=ctx['n'],seed=20261002,headless=True,device='cuda:0'),own_native_physical_CPU_proof_SHA=H(a.native_proof) if a.native_proof else None,own_native_source_CPU_proof_SHA=H(a.source_proof) if a.source_proof else None,single_W35_actor9_only_no_gate_or_second_expert=True,no_PPO=True,no_new_canonical_transaction=True)
  save(case+'_INTENT_ACTUAL.json',lease);sf=c.open_sftp();sf.get_channel().settimeout(60)
  with sf.open(ROOT+'/leases/'+case+'.json','wx') as f:f.write(json.dumps(lease,indent=2).encode());f.flush()
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
""".replace('CASE',repr(case))
  script=D/('demand_'+case+'_once.py');assert not script.exists();compile(launcher,str(script),'exec');script.write_text(launcher,encoding='utf8');sf.put(str(script),ROOT+'/'+script.name)
  taskresult=t.ps(c,"$ErrorActionPreference='Stop';$n='"+task+"';if(Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue){throw 'Task exists'};$a=New-ScheduledTaskAction -Execute '"+t.PY+"' -Argument '\""+ROOT+'/'+script.name+"\"' -WorkingDirectory '"+ROOT+"';$p=New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited;$s=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew;Register-ScheduledTask -TaskName $n -Action $a -Principal $p -Settings $s|Out-Null;Start-ScheduledTask -TaskName $n;$t=Get-ScheduledTask -TaskName $n;[PSCustomObject]@{task=$n;state=[string]$t.State;triggers=@($t.Triggers|Where-Object {$null-ne $_}).Count}|ConvertTo-Json -Compress")
  assert taskresult['triggers']==0;save(case+'_DISPATCH_ACTUAL.json',dict(epoch=time.time(),case=case,lease=lease,task=taskresult,actual_result_pending=True,no_old_case_replayed=True));print(json.dumps(dict(dispatched=True,case=case,task=taskresult,no_PPO=True)))
 except BaseException:
  save(case+'_DISPATCH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_outcome_readonly_first_no_retry=True));raise
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':main()
