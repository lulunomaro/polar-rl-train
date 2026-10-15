"""Root's two new frozen single-policy cases; no automatic learning or retry."""
from pathlib import Path
import argparse,hashlib,json,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';Q=D/'payload';ROOT='D:/MOD4_async_eval/'+D.name
sys.path.insert(0,str(W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'))
import transport_249_bodyframe_current_terminal_role_v3 as t
t.ROOT=ROOT
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):
 p=R/n;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
def main():
 a=argparse.ArgumentParser();a.add_argument('--steps',type=int,choices=(120,1500),required=True);a.add_argument('--execute-root-new-single-case',action='store_true');args=a.parse_args();assert args.execute_root_new_single_case
 S=args.steps;case=f's5_single_w35_original35_{S}_v1';task=f'MOD4_S5_SingleW35_Original35_{S}_v1_20261015'
 prep=json.loads((R/'S5_SINGLE_W35_ORIGINAL35_PACKAGE_CPU_PREPARED_ACTUAL.json').read_bytes());assert prep['prepared_CPU_only'] and prep['CPU_RNG_unchanged_no_CUDA_or_optimizer']
 decision=json.loads((W/'MOD4_S4_FIRST_GATE_RETENTION_PAIR_20261015/reports/S4_FIRST_GATE_COMPLETE_RETENTION_LIMITED_PRACTICAL_CLOSEOUT_AND_S5_SCOPE_DECISION_CPU_V2.json').read_bytes());assert decision['actual_S4_first_prototype_learning_and_complete_35_flat_spin_world_review_closed'] and decision['no_new_PPO_or_second_gate_block_admitted']
 assert not (R/(case+'_INTENT_ACTUAL.json')).exists()
 if S==1500:
  p=R/'S5_SINGLE35_OWN_PHYSICAL_DATA_ADMITTED_s5_single_w35_original35_120_v1.json';v=json.loads(p.read_bytes());assert v['passed'] and v['controls']==120
  p=R/'s5_single_w35_original35_120_v1_S5_SINGLE_CONTROL_CPU_ADMITTED.json';v=json.loads(p.read_bytes());assert v['passed'] and v['controls']==120
  b=json.loads((R/'s5_single_w35_original35_120_v1_INDEPENDENT_BOUNDARY.json').read_bytes());assert b['actual_parent_absent'] and b['actual_child_absent'] and b['shared_OS_lock_free']
 c=None;sf=None
 try:
  c=t.connect();guard=t.py(c,t.guard_code());assert guard['shared_OS_lock_free'] and guard['new_root_unused']==(S==120)
  state=t.ps(c,"$t=Get-ScheduledTask -TaskName '"+task+"' -ErrorAction SilentlyContinue;[PSCustomObject]@{exists=($null-ne $t)}|ConvertTo-Json -Compress");assert not state['exists']
  save(case+'_INTENT_ACTUAL.json',dict(epoch=time.time(),case=case,steps=S,resource=guard,prepared_SHA=H(R/'S5_SINGLE_W35_ORIGINAL35_PACKAGE_CPU_PREPARED_ACTUAL.json'),scope_decision_SHA=H(W/'MOD4_S4_FIRST_GATE_RETENTION_PAIR_20261015/reports/S4_FIRST_GATE_COMPLETE_RETENTION_LIMITED_PRACTICAL_CLOSEOUT_AND_S5_SCOPE_DECISION_CPU_V2.json'),new_PPO=False,unknown_mutation_requires_readonly_not_retry=True))
  sf=c.open_sftp();sf.get_channel().settimeout(60)
  if S==120:
   z=Path(prep['package']['path']);assert H(z)==prep['package']['sha256'];sf.mkdir(ROOT)
   with sf.open(ROOT+'/'+z.name,'wx') as f:f.write(z.read_bytes());f.flush()
  ctx=dict(root=ROOT,case=case,steps=S,package=Path(prep['package']['path']).name,packageSHA=prep['package']['sha256'],packagebytes=prep['package']['bytes'],manifestSHA=prep['manifest']['sha256'],source=prep['source_single'])
  code=r'''
from pathlib import Path
import hashlib,json,zipfile,torch,sys,time,importlib.metadata as metadata
R=Path(C['root']);Q=R/'payload';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if C['steps']==120:
 z=R/C['package'];assert z.stat().st_size==C['packagebytes'] and H(z)==C['packageSHA'] and not Q.exists()
 Q.mkdir();(R/'attempts').mkdir();(R/'leases').mkdir()
 with zipfile.ZipFile(z) as a:
  for n in a.namelist():
   p=Q/n;assert p.resolve().is_relative_to(Q.resolve()) and not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(a.read(n))
assert H(Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json')==C['manifestSHA']
m=json.loads((Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json').read_bytes());assert m['source_single_policy']==C['source']
for row in m['file_rows']:assert (Q/row['relative']).stat().st_size==row['bytes'] and H(Q/row['relative'])==row['sha256'],row['relative']
sdk=json.loads((Q/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for n,v in sdk['versions'].items():
 if v is not None:assert metadata.version(n)==v
for row in sdk['files']:assert H(row['path'])==row['sha256']
assert H(C['source']['local_path'])==C['source']['sha256']
ck=torch.load(C['source']['local_path'],map_location='cpu',weights_only=False);ts=[]
def walk(v):
 if torch.is_tensor(v):assert v.device.type=='cpu' and (not v.is_floating_point() or torch.isfinite(v).all());ts.append(v)
 elif hasattr(v,'items'):
  for x in v.values():walk(x)
 elif isinstance(v,(tuple,list)):
  for x in v:walk(x)
walk(ck);assert sum(x.is_floating_point() for x in ts)==102 and len(ck['actor_state_dict'])==9 and ck['E1_terrain_state']['num_envs']==20000
assert ck['E1_terrain_state']['G3_profile_sha256']==H(Q/'runtime/isaac/mod4/g3_cad_profile.json')
sys.path.insert(0,str(Q));from s5_single_frozen35_v1 import Single35
rng=torch.get_rng_state().clone();actor=Single35(C['source']['local_path'],80,'cpu');assert actor.exact() and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
assert not (R/'attempts'/C['case']).exists() and not (R/'leases'/(C['case']+'.json')).exists() and not (R/(C['case']+'_START_INTENT.json')).exists()
if C['steps']==1500:
 ex=json.loads((R/'attempts/s5_single_w35_original35_120_v1/PARENT_EXIT_RECEIPT.json').read_bytes());d=json.loads((R/'attempts/s5_single_w35_original35_120_v1/output/COMPLETE_ACTUAL.json').read_bytes())
 assert ex['exit_code']==0 and not ex['original_error_present'] and ex['complete_data_contract_present'] and d['steps']==120 and d['callbacks']==480
print(json.dumps(dict(epoch=time.time(),targetCPU_actual=True,all_source_files=len(m['file_rows']),sourceSHA=H(C['source']['local_path']),whole_floating=102,single_actor9_STD_source_exact=True,SDK_and_original35_geometry_source_binding_exact=True,no_CUDA_or_PPO_or_budget=True,new_case_unused=True)))
'''
  cpu=t.py(c,'C='+repr(ctx)+'\n'+code,90);save(case+'_TARGET_CPU_ACTUAL.json',cpu)
  fresh=t.py(c,t.guard_code());assert fresh['shared_OS_lock_free']
  lease=dict(epoch=time.time(),case_id=case,target_host='10.24.4.249',namespace=D.name,GPU_lease_granted_by_root=True,actual_shared_slot_idle_verified=True,resource_boundary=fresh,checkpoint_path=prep['source_single']['local_path'],checkpoint_sha256=prep['source_single']['sha256'],worker_sha256=prep['worker_SHA'],factor_runtime_sha256=prep['runtime_SHA'],source_bundle_manifest_sha256=prep['manifest']['sha256'],single_policy_source=prep['source_single'],single_actor_adapter_SHA=H(Q/'s5_single_frozen35_v1.py'),case_parameters=dict(steps=S,num_envs=80,seed=20260928,body_sign=1,world_sign=1,feedback_current=False,headless=True,device='cuda:0'),scope='S5 missing single W35 policy A, original35 first cell against completed matched ruleB/gateC only after actual initial-state pair verification',no_PPO=True,no_new_canonical_transaction=True)
  save(case+'_OWN_PARAMETER_BOUND_LEASE_ACTUAL.json',lease)
  with sf.open(ROOT+'/leases/'+case+'.json','wx') as f:f.write(json.dumps(lease,indent=2).encode());f.flush()
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
""".replace('CASE',repr(case))
  script=D/('demand_'+case+'_once.py');assert not script.exists();compile(launcher,str(script),'exec');script.write_text(launcher,encoding='utf8');sf.put(str(script),ROOT+'/'+script.name)
  result=t.ps(c,"$ErrorActionPreference='Stop';$n='"+task+"';if(Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue){throw 'Task exists'};$a=New-ScheduledTaskAction -Execute '"+t.PY+"' -Argument '\""+ROOT+'/'+script.name+"\"' -WorkingDirectory '"+ROOT+"';$p=New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited;$s=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew;Register-ScheduledTask -TaskName $n -Action $a -Principal $p -Settings $s|Out-Null;Start-ScheduledTask -TaskName $n;$t=Get-ScheduledTask -TaskName $n;[PSCustomObject]@{task=$n;state=[string]$t.State;triggers=@($t.Triggers|Where-Object {$null-ne $_}).Count}|ConvertTo-Json -Compress")
  assert result['triggers']==0;save(case+'_UNIQUE_DISPATCH_ACTUAL.json',dict(epoch=time.time(),case=case,task=result,lease=lease,actual_result_pending=True,no_new_learning=True));print(json.dumps(dict(dispatched=True,case=case,task=result,no_PPO=True)))
 except BaseException:
  save(case+'_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_outcome_requires_actual_readonly_first=True,no_automatic_retry=True));raise
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':main()
