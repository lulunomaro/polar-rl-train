"""Root-authorized fresh249 source/namespace/task/frozen1500 dispatch once."""
from pathlib import Path
import json,time,hashlib,traceback,os
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014'))
import transport_249_only as t
t.ROOT='D:/MOD4_async_eval/MOD4_3060_FULL80_CURRENT_LINUX_FINAL_20261014'
P=Path(__file__).resolve().parent;R=P/'reports';Q=P/'payload'
ROOT=t.ROOT;PY=t.PY
CASE='native3060_Linux20k_final_full80_native120_v1'
TASK='MOD4_Linux20kFinalFull80_20261014_Native120_v1'
SHA='1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prep=json.loads((R/'FULL80_NATIVE_CPU_PORT_PREPARED_ACTUAL.json').read_bytes());pack=prep['package']
Z=Path(pack['path']);assert H(Z)==pack['sha256']
CPU=prep
intent=R/'REFERENCE17B_FROZEN1500_DEPLOY_INTENT.json';assert not intent.exists()

def save(name,value):
    p=R/name;assert not p.exists()
    with p.open('xb') as f:f.write(json.dumps(value,ensure_ascii=False,indent=2).encode());f.flush();os.fsync(f.fileno())
    return p

c=None;sf=None
try:
 c=t.connect()
 unknown=t.py(c,"from pathlib import Path\nimport json\np=Path("+repr(ROOT)+");print(json.dumps(dict(root_present=p.exists(),attempt_present=(p/'attempts'/"+repr(CASE)+").exists(),lease_present=(p/'ROOT_GPU_LEASE.json').exists(),start_intent=(p/'TASK_START_INTENT.json').exists())))")
 task=t.ps(c,"$x=Get-ScheduledTask -TaskName '"+TASK+"' -ErrorAction SilentlyContinue;[PSCustomObject]@{present=($null -ne $x);state=if($x){[string]$x.State}else{$null}}|ConvertTo-Json -Compress")
 assert not any(unknown.values()) and not task['present'], 'Actualunknown outcome requires read-only recovery, never dispatch again'
 guard=t.py(c,t.guard_code());assert guard['new_root_unused']
 save(intent.name,dict(epoch=time.time(),root=ROOT,case=CASE,task=TASK,guard=guard,package=pack,
                       no_GPU_or_task_started_yet=True,unknown_outcome_requires_actualread=True))
 t.py(c,"from pathlib import Path\nimport json\np=Path("+repr(ROOT)+");assert not p.exists();p.mkdir();print(json.dumps(dict(created=str(p))))")
 sf=c.open_sftp();remote=ROOT+'/FULL80_NATIVE_SOURCE_V1.zip';sf.put(str(Z),remote)
 uploaded=t.py(c,"from pathlib import Path\nimport json,hashlib\np=Path("+repr(remote)+");print(json.dumps(dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())))")
 assert uploaded['bytes']==pack['bytes'] and uploaded['sha256']==pack['sha256'];save('REFERENCE17B_ACTUAL_PACKAGE_UPLOAD_SHA.json',uploaded)
 unpack=r'''
from pathlib import Path
import zipfile,json,hashlib,importlib.metadata as metadata,time,torch
root=Path(ROOT);p=root/'payload';assert not p.exists();p.mkdir()
with zipfile.ZipFile(root/'FULL80_NATIVE_SOURCE_V1.zip') as z:
 for name in z.namelist():assert (p/name).resolve().is_relative_to(p.resolve())
 z.extractall(p)
H=lambda q:hashlib.sha256(Path(q).read_bytes()).hexdigest()
m=p/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json';assert H(m)==MANIFESTSHA
manifest=json.loads(m.read_bytes())
for r in manifest['file_rows']:
 q=p/r['relative'];assert q.stat().st_size==r['bytes'] and H(q)==r['sha256']
sdk=json.loads((p/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for name,version in sdk['versions'].items():
 if version is not None:assert metadata.version(name)==version
for r in sdk['files']:assert H(r['path'])==r['sha256']
ck=p/'source/model_32411_17b.pt';assert H(ck)==SOURCESHA
source=torch.load(ck,map_location='cpu',weights_only=False)
def finite(v):
 if isinstance(v,torch.Tensor):
  assert v.device.type=='cpu'
  if v.is_floating_point():assert torch.isfinite(v).all();return 1
  return 0
 if isinstance(v,dict):return sum(finite(x) for x in v.values())
 if isinstance(v,(list,tuple)):return sum(finite(x) for x in v)
 return 0
assert finite(source)==107 and source['E1_terrain_state']['num_envs']==20000 and len(source['actor_state_dict'])==9
assert not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),sourcefreeze_manifest_SHA=H(m),files=len(manifest['file_rows']),installed_SDK_files=len(sdk['files']),actual_checkpoint_SHA=H(ck),source_floating107=True,source_saved_envs20000=True,no_CUDA_or_trainingDR_resume=True)))
'''
 unpack=unpack.replace('ROOT',repr(ROOT)).replace('MANIFESTSHA',repr(CPU['manifest']['sha256'])).replace('SOURCESHA',repr(SHA))
 admitted=t.py(c,unpack);save('REFERENCE17B_EXTRACTED_SOURCE_CPU_ADMITTED_ACTUAL.json',admitted)
 fresh=t.py(c,t.guard_code());assert not fresh['new_root_unused']
 lease=dict(epoch=time.time(),case_id=CASE,target_host='10.24.4.249',namespace='MOD4_3060_FULL80_CURRENT_LINUX_FINAL_20261014',
            GPU_lease_granted_by_root=True,actual_shared_slot_idle_verified=True,resource_boundary=fresh,
            checkpoint_path=ROOT+'/payload/source/model_32411_17b.pt',checkpoint_sha256=SHA,
            worker_sha256=CPU['worker']['sha256'],factor_runtime_sha256=CPU['runtime']['sha256'],
            source_bundle_manifest_sha256=CPU['manifest']['sha256'],
            case_parameters=dict(steps=120,num_envs=80,seed=20260928,body_sign=1,world_sign=1,feedback_current=False,headless=True,device='cuda:0'),
            frozen_original_white3_fixture=True,no_PPO=True,no_training20000_DR_restore=True,
            native120_only_not_full15s_or_qualification=True)
 blob=json.dumps(lease,ensure_ascii=False,indent=2).encode();leasepath=ROOT+'/ROOT_GPU_LEASE.json'
 with sf.open(leasepath,'wx') as f:f.write(blob);f.flush()
 launcher="""from pathlib import Path
import sys,subprocess,json,time,os,hashlib,psutil
ROOT=Path(__file__).resolve().parent;payload=ROOT/'payload';lease=ROOT/'ROOT_GPU_LEASE.json';attempt=ROOT/'attempts/CASE'
assert not attempt.exists() and not (ROOT/'DEMAND_LAUNCH_ENTERED.json').exists()
row=dict(epoch=time.time(),pid=os.getpid(),creation=psutil.Process().create_time(),argv=sys.argv,lease_SHA=hashlib.sha256(lease.read_bytes()).hexdigest(),no_PPO=True)
with (ROOT/'DEMAND_LAUNCH_ENTERED.json').open('xb') as f:f.write(json.dumps(row,indent=2).encode());f.flush();os.fsync(f.fileno())
argv=[sys.executable,str(payload/'run_full80_native_parent_v1.py'),'--lease',str(lease),'--attempt',str(attempt)]
with (ROOT/'DEMAND_PARENT_CONSOLE.log').open('xb') as log:
 p=subprocess.Popen(argv,cwd=str(payload),stdout=log,stderr=subprocess.STDOUT)
 (ROOT/'DEMAND_PARENT_LAUNCH_PID.json').write_text(json.dumps(dict(epoch=time.time(),launcher_pid=os.getpid(),parent_pid=p.pid,parent_creation=psutil.Process(p.pid).create_time(),argv=argv,no_PPO=True),indent=2))
 rc=p.wait()
(ROOT/'DEMAND_LAUNCH_EXIT.json').write_text(json.dumps(dict(epoch=time.time(),exit_code=rc,parent_pid=p.pid,no_PPO=True)))
sys.exit(rc)
""".replace('CASE',CASE)
 script=P/'demand_full80_native120_parent_launcher_unique_once.py';assert not script.exists();compile(launcher,str(script),'exec');script.write_text(launcher,encoding='utf8')
 sf.put(str(script),ROOT+'/'+script.name)
 setup=t.ps(c,"$ErrorActionPreference='Stop';$name='"+TASK+"';if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'Task exists'};$action=New-ScheduledTaskAction -Execute '"+PY+"' -Argument '\""+ROOT+'/'+script.name+"\"' -WorkingDirectory '"+ROOT+"';$principal=New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited;$settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew;Register-ScheduledTask -TaskName $name -Action $action -Principal $principal -Settings $settings|Out-Null;$x=Get-ScheduledTask -TaskName $name;[PSCustomObject]@{task=$name;state=[string]$x.State;triggers=@($x.Triggers | Where-Object {$null -ne $_}).Count;action=$x.Actions.Execute;arguments=$x.Actions.Arguments}|ConvertTo-Json -Compress")
 assert setup['triggers']==0;save('REFERENCE17B_DEMAND_TASK_REGISTERED_ACTUAL.json',setup)
 started=t.ps(c,"$ErrorActionPreference='Stop';$p='"+ROOT+"/TASK_START_INTENT.json';if(Test-Path -LiteralPath $p){throw 'Start consumed'};[IO.File]::WriteAllText($p,'{\"single_start_requested\":true}');Start-ScheduledTask -TaskName '"+TASK+"';$x=Get-ScheduledTask -TaskName '"+TASK+"';[PSCustomObject]@{task=$x.TaskName;state=[string]$x.State;triggers=@($x.Triggers | Where-Object {$null -ne $_}).Count;unique_start=$true}|ConvertTo-Json -Compress")
 save('REFERENCE17B_DEMAND_TASK_STARTED_ACTUAL.json',dict(epoch=time.time(),task=started,lease=lease,lease_SHA=hashlib.sha256(blob).hexdigest(),launcher_SHA=H(script),no_oldcase_replayed=True))
 print(json.dumps(dict(unique_dispatch=True,case=CASE,task=started,root=ROOT,actual_GPU_result_pending=True)),flush=True)
except Exception:
 save('REFERENCE17B_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_outcome_requires_actualread=True,no_blind_restart=True))
 raise
finally:
 if sf:sf.close()
 t.close(c)
