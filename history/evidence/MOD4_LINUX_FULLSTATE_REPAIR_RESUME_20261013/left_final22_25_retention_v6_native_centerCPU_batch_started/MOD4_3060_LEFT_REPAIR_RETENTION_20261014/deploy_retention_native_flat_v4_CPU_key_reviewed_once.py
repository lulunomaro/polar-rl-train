"""Root-only sequential249 transport and one fresh native case, no Linux connection."""
from pathlib import Path
import sys,json,time,hashlib,os,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';Q=D/'payload'
sys.path.insert(0,str(W/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014'));import transport_249_only as t
ROOT='D:/MOD4_async_eval/MOD4_3060_LEFT_REPAIR_RETENTION_20261014';t.ROOT=ROOT
SHARED='D:/MOD4_async_eval/MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload'
BASE='D:/MOD4_async_eval/MOD4_3060_FULL80_FROZEN_CURRENT_20261014/payload/source/model_32411_17b.pt'
CASE='retention_baseline1aa_flat_native120_v4';TASK='MOD4_RetentionPair_20261014_baseline1aa_flat_native120_v4'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,v):
 p=R/name;assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
def main():
 assert not (R/'NATIVE_FLAT_V4_UNIQUE_DISPATCH_ACTUAL.json').exists()
 z=D/'retention_scenequery_support_v4_CPU_COMPONENTS.zip';assert H(z)=='0cb0ef9685d1cdae27fe123b011a70b61e55e5592dcc96a4da3e2fb13cca8073'
 assert json.loads((R/'SCENE_QUERY_V4_SYNTHETIC_CPU_FIXTURE_PASSED.json').read_bytes())['passed_CPU_synthetic_only']
 prior=json.loads((R/'retention_baseline1aa_flat_native120_v3_INDEPENDENT_BOUNDARY.json').read_bytes());assert prior['actual_parent_absent'] and prior['actual_child_absent'] and prior['shared_OS_lock_free']
 c=t.connect();sf=None
 try:
  guard=t.py(c,t.guard_code());assert not guard['new_root_unused']
  task=t.ps(c,"$t=Get-ScheduledTask -TaskName '"+TASK+"' -ErrorAction SilentlyContinue;[PSCustomObject]@{exists=($null -ne $t)}|ConvertTo-Json -Compress");assert not task['exists']
  save('NATIVE_FLAT_V4_DEPLOY_INTENT.json',dict(epoch=time.time(),newroot=ROOT,case=CASE,guard=guard,only_native0PPO=True))
  t.py(c,"from pathlib import Path\nimport json\np=Path("+repr(ROOT)+");assert p.exists();assert not (p/'attempts'/"+repr(CASE)+").exists();assert not (p/'leases'/ ("+repr(CASE)+"+'.json')).exists();print(json.dumps(dict(existing_root_verified=str(p),new_case_unused=True)))")
  sf=c.open_sftp();sf.get_channel().settimeout(60);sf.put(str(z),ROOT+'/'+z.name)
  hashes={n:H(Q/n) for n in ('retention_worker_v4.py','retention_parent_v4.py','retention_native_witness_v4.py','retention_flat_native_v4.py','RETENTION_CPU_MANIFEST_V4.json')}
  code=r'''
from pathlib import Path
import json,hashlib,time,zipfile,torch,importlib.metadata as metadata
R=Path(ROOT);P=R/'payload';assert P.exists()
z=R/ZIP;assert hashlib.sha256(z.read_bytes()).hexdigest()==ZIP_SHA
with zipfile.ZipFile(z) as f:
 for n in f.namelist():assert (P/n).resolve().is_relative_to(P.resolve())
 for n in f.namelist():
  dst=P/n
  if n.endswith('/'):
   dst.mkdir(parents=True,exist_ok=True);continue
  b=f.read(n)
  if dst.exists():assert dst.read_bytes()==b,('Existing source would change',n)
  else:
   dst.parent.mkdir(parents=True,exist_ok=True)
   with dst.open('xb') as out:out.write(b)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for n,h in HASHES.items():assert H(P/n)==h
m=json.loads((P/'RETENTION_CPU_MANIFEST_V4.json').read_bytes());S=Path(SHARED)
for row in m['shared_source_freeze']:assert H(S/row['relative'])==row['sha256'],row['relative']
sdk=json.loads((S/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for n,v in sdk['versions'].items():
 if v is not None:assert metadata.version(n)==v
for row in sdk['files']:assert H(row['path'])==row['sha256']
assert H(BASE)=='1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06'
ck=torch.load(BASE,map_location='cpu',weights_only=False);assert ck['E1_terrain_state']['num_envs']==20000
assert not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),newtarget_CPU_passed=True,shared_source_files=len(m['shared_source_freeze']),SDK_actual_verified=True,baseline_source_SHA=H(BASE),no_GPU_or_PPO=True)))
'''
  prefix='ROOT='+repr(ROOT)+'\nSHARED='+repr(SHARED)+'\nBASE='+repr(BASE)+'\nZIP='+repr(z.name)+'\nZIP_SHA='+repr(H(z))+'\nHASHES='+repr(hashes)+'\n'
  cpu=t.py(c,prefix+code);save('NATIVE_FLAT_V4_TARGET_CPU_SOURCE_ACTUAL.json',cpu)
  fresh=t.py(c,t.guard_code());assert not fresh['new_root_unused']
  lease=dict(epoch=time.time(),case_id=CASE,target_host='10.24.4.249',namespace='MOD4_3060_LEFT_REPAIR_RETENTION_20261014',GPU_lease_granted_by_root=True,actual_shared_slot_idle_verified=True,resource_boundary=fresh,checkpoint_path=BASE,checkpoint_sha256=cpu['baseline_source_SHA'],worker_sha256=hashes['retention_worker_v4.py'],port_sources_sha256={n:hashes[n] for n in ('retention_native_witness_v4.py','retention_flat_native_v4.py')},shared_payload_target=SHARED,case_parameters=dict(kind='flat',steps=120,num_envs=80,seed=20261002,headless=True,device='cuda:0'),native_scope_only_no_full_behavior_claim=True,no_PPO=True)
  leasepath=ROOT+'/leases/'+CASE+'.json'
  with sf.open(leasepath,'wx') as f:f.write(json.dumps(lease,indent=2).encode());f.flush()
  launch="""from pathlib import Path
import sys,subprocess,json,time,os,psutil
R=Path(__file__).resolve().parent;case=CASE;assert not (R/(case+'_START_INTENT.json')).exists()
(R/(case+'_START_INTENT.json')).write_text(json.dumps(dict(epoch=time.time(),pid=os.getpid(),creation=psutil.Process().create_time(),no_PPO=True)))
argv=[sys.executable,str(R/'payload/retention_parent_v4.py'),'--lease',str(R/'leases'/ (case+'.json')),'--attempt',str(R/'attempts'/case)]
with (R/(case+'_PARENT_CONSOLE.log')).open('xb') as log:
 p=subprocess.Popen(argv,cwd=R/'payload',stdout=log,stderr=subprocess.STDOUT)
 (R/(case+'_PARENT_PID.json')).write_text(json.dumps(dict(pid=p.pid,creation=psutil.Process(p.pid).create_time(),argv=argv)))
 rc=p.wait()
(R/(case+'_LAUNCH_EXIT.json')).write_text(json.dumps(dict(epoch=time.time(),exit_code=rc,no_PPO=True)))
sys.exit(rc)
""".replace('CASE',repr(CASE))
  script=D/('demand_'+CASE+'_once.py');assert not script.exists();compile(launch,str(script),'exec');script.write_text(launch,encoding='utf8');sf.put(str(script),ROOT+'/'+script.name)
  setup=t.ps(c,"$ErrorActionPreference='Stop';$name='"+TASK+"';if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'Task exists'};$a=New-ScheduledTaskAction -Execute '"+t.PY+"' -Argument '\""+ROOT+'/'+script.name+"\"' -WorkingDirectory '"+ROOT+"';$p=New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited;$s=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew;Register-ScheduledTask -TaskName $name -Action $a -Principal $p -Settings $s|Out-Null;Start-ScheduledTask -TaskName $name;$t=Get-ScheduledTask -TaskName $name;[PSCustomObject]@{task=$name;state=[string]$t.State;triggers=@($t.Triggers|Where-Object {$null -ne $_}).Count}|ConvertTo-Json -Compress")
  assert setup['triggers']==0;save('NATIVE_FLAT_V4_UNIQUE_DISPATCH_ACTUAL.json',dict(epoch=time.time(),lease=lease,task=setup,original_scope_GPU_result_pending=True,no_oldcase_replayed=True));print(json.dumps(dict(unique_dispatch=True,task=setup,case=CASE,native120_pending=True)))
 except BaseException:
  save('NATIVE_FLAT_V4_ORIGINAL_DEPLOY_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),unknown_outcome_requires_readonly_recovery=True));raise
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':main()
