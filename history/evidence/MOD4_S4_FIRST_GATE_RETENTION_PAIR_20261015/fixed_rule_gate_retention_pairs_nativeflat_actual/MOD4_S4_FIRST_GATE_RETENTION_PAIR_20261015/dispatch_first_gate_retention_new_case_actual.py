"""Root-only new unused retention case. Never replays an existing attempt."""
from pathlib import Path
import argparse, json, time, hashlib, sys, traceback
D=Path(__file__).resolve().parent; W=D.parent; R=D/'reports'; Q=D/'payload'
sys.path.insert(0,str(D))
import transport_s4_retention_pair_actual as t
ROOT=t.ROOT
SHARED='D:/MOD4_async_eval/MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload'
SOURCES={'pair_anchor':(ROOT+'/payload/source/E1_WAVE35_frozen_source.pt','b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd')}

H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,v):
 p=R/name; assert not p.exists(); p.write_text(json.dumps(v,indent=2),encoding='utf8')
def main():
 p=argparse.ArgumentParser();p.add_argument('--kind',choices=('flat','spin','world'),required=True);p.add_argument('--steps',type=int,choices=(120,1500),required=True);p.add_argument('--source',choices=SOURCES,required=True);p.add_argument('--native-proof');p.add_argument('--routing-proof');p.add_argument('--mode',choices=('rule_eval','gate_eval'),required=True);p.add_argument('--execute-root-dispatch',action='store_true');a=p.parse_args();assert a.execute_root_dispatch,'Explicit root execution flag required'
 case=f's4_retention_{a.mode}_{a.kind}_{a.steps}_v1';task='MOD4_S4_RetentionPair_20261015_'+case
 assert not (R/(case+'_DISPATCH_ACTUAL.json')).exists()
 if a.steps==1500:
  assert a.native_proof and a.routing_proof; proof=json.loads(Path(a.native_proof).read_bytes());v=proof['result'];assert v['kind']==a.kind and v['steps']==120 and v['data']['complete_data_contract'];routing=json.loads(Path(a.routing_proof).read_bytes());assert routing['passed'] and routing['steps']==120 and routing['kind']==a.kind and routing['all24_initial_final_source_exact']
 assert json.loads((R/'FIRST_GATE_RETENTION_PAIR_CPU_PREPARED_ACTUAL.json').read_bytes())['CPU_prepared_no_remote_or_GPU']
 assert json.loads((R/'FIRST_GATE_RETENTION_PAIR_UPLOAD_TARGET_CPU_ACTUAL.json').read_bytes())['actual_targetCPU']
 baseline,source_sha=SOURCES[a.source]
 names=['retention_worker_v8.py','retention_parent_v8.py','retention_native_witness_v8.py','retention_'+a.kind+'_native_v8.py','retention_plane_reference_v8.py','represented_native_plane_CPU_component_v2.py','retention_plane_metadata_v7.py','raycast_hit_serializer_v5.py','RETENTION_CPU_MANIFEST_V8.json'];hashes={n:H(Q/n) for n in names}
 c=t.connect();sf=None
 try:
  guard=t.py(c,t.guard_code());assert not guard['new_root_unused']
  state=t.ps(c,"$t=Get-ScheduledTask -TaskName '"+task+"' -ErrorAction SilentlyContinue;[PSCustomObject]@{exists=($null -ne $t)}|ConvertTo-Json -Compress");assert not state['exists']
  code="""from pathlib import Path
import json,hashlib,torch,importlib.metadata as metadata
R=Path(ROOT);P=R/'payload';S=Path(SHARED)
assert R.exists() and not (R/'attempts'/CASE).exists() and not (R/'leases'/(CASE+'.json')).exists()
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for n,h in HASHES.items():assert H(P/n)==h,n
m=json.loads((P/'RETENTION_CPU_MANIFEST_V8.json').read_bytes())
for row in m['package_files_v8']:assert H(P/row['relative'])==row['sha256'],row['relative']
assert H(m['V7_actual_native_binding']['path'])==m['V7_actual_native_binding']['sha256']
for row in m['shared_source_freeze']:assert H(S/row['relative'])==row['sha256'],row['relative']
sdk=json.loads((S/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for n,v in sdk['versions'].items():
 if v is not None:assert metadata.version(n)==v
for row in sdk['files']:assert H(row['path'])==row['sha256']
assert H(CHECKPOINT)==SOURCE_SHA
import sys
sys.path.insert(0,str(P))
from s4_shared_feedback_hardtop1_v1 import PairRouter
from s4_eval_trained_gate_source_v1 import load_trained_gate
pair=json.loads((P/'S4_PAIR_SOURCE_MANIFEST.json').read_bytes());gate=json.loads((P/'S4_TRAINED_GATE_SOURCE_MANIFEST.json').read_bytes())
router=PairRouter(pair['sources'],88,'cpu');gateproof=load_trained_gate(router,gate)
assert not torch.cuda.is_initialized()
print(json.dumps(dict(new_case_unused=True,source_sha256=SOURCE_SHA,targetCPU_source_and_SDK_exact=True,trained_gate_SHA=gate['sha256'],gateproof=gateproof,no_GPU=True)))
"""
  prefix='ROOT='+repr(ROOT)+'\nSHARED='+repr(SHARED)+'\nCASE='+repr(case)+'\nHASHES='+repr(hashes)+'\nCHECKPOINT='+repr(baseline)+'\nSOURCE_SHA='+repr(source_sha)+'\n'
  cpu=t.py(c,prefix+code);save(case+'_TARGET_CPU_ACTUAL.json',cpu)
  fresh=t.py(c,t.guard_code());lease=dict(epoch=time.time(),case_id=case,target_host='10.24.4.249',namespace=D.name,GPU_lease_granted_by_root=True,actual_shared_slot_idle_verified=True,resource_boundary=fresh,checkpoint_path=baseline,checkpoint_sha256=source_sha,worker_sha256=hashes['retention_worker_v8.py'],port_sources_sha256={n:hashes[n] for n in ('retention_native_witness_v8.py','retention_'+a.kind+'_native_v8.py','raycast_hit_serializer_v5.py')},shared_payload_target=SHARED,case_parameters=dict(router_mode=a.mode,kind=a.kind,steps=a.steps,num_envs={'flat':80,'spin':88,'world':88}[a.kind],seed=20261002,headless=True,device='cuda:0'),native_data_admission_report=a.native_proof,native_routing_admission_SHA=H(a.routing_proof) if a.routing_proof else None,source_trained_gate_SHA='02718c74024508c50ff559be2fa6351b7f63046afeb4ee3fd7c51ad6160ae1f3',checkpoint_argument_is_scene_anchor_not_single_actor=True,no_PPO=True)
  save(case+'_INTENT_ACTUAL.json',lease);sf=c.open_sftp();sf.get_channel().settimeout(60)
  with sf.open(ROOT+'/leases/'+case+'.json','wx') as f:f.write(json.dumps(lease,indent=2).encode());f.flush()
  launch="""from pathlib import Path
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
  script=D/('demand_'+case+'_once.py');assert not script.exists();compile(launch,str(script),'exec');script.write_text(launch,encoding='utf8');sf.put(str(script),ROOT+'/'+script.name)
  setup=t.ps(c,"$ErrorActionPreference='Stop';$name='"+task+"';if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'Task exists'};$a=New-ScheduledTaskAction -Execute '"+t.PY+"' -Argument '\""+ROOT+'/'+script.name+"\"' -WorkingDirectory '"+ROOT+"';$p=New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited;$s=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew;Register-ScheduledTask -TaskName $name -Action $a -Principal $p -Settings $s|Out-Null;Start-ScheduledTask -TaskName $name;$t=Get-ScheduledTask -TaskName $name;[PSCustomObject]@{task=$name;state=[string]$t.State;triggers=@($t.Triggers|Where-Object {$null -ne $_}).Count}|ConvertTo-Json -Compress")
  assert setup['triggers']==0;save(case+'_DISPATCH_ACTUAL.json',dict(epoch=time.time(),lease=lease,task=setup,actual_result_pending=True,no_old_case_replayed=True));print(json.dumps(dict(new_dispatch=True,case=case,task=setup)))
 except BaseException:
  save(case+'_ORIGINAL_DISPATCH_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_outcome_requires_readonly_recovery=True));raise
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':main()
