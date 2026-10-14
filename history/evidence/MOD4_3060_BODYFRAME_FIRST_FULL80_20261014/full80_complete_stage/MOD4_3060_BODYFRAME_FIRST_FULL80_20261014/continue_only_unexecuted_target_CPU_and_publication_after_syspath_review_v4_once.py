"""Root-authorized fresh249 source/namespace/task/frozen1500 dispatch once."""
from pathlib import Path
import json,time,hashlib,traceback,os
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014'))
import transport_249_bodyframe_current_terminal_role_v3 as t
t.ROOT='D:/MOD4_async_eval/MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'
P=Path(__file__).resolve().parent;R=P/'reports';Q=P/'payload'
ROOT=t.ROOT;PY=t.PY
CASE='native3060_bodyframe_first_final_full80_frozen1500_v1'
TASK='MOD4_BodyframeFirstFinalFull80_20261014_Frozen1500_v1'
SHA='f5166509d297814e3c3fe4f457ae064d9b02a8bd62702914759dc430f20d2139'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prep=json.loads((R/'FULL80_NATIVE_CPU_PORT_PREPARED_ACTUAL.json').read_bytes());pack=prep['package']
Z=Path(pack['path']);assert H(Z)==pack['sha256']
CPU=prep
intent=R/'REFERENCE17B_FROZEN1500_DEPLOY_INTENT.json';assert intent.exists()

def save(name,value):
    p=R/name;assert not p.exists()
    with p.open('xb') as f:f.write(json.dumps(value,ensure_ascii=False,indent=2).encode());f.flush();os.fsync(f.fileno())
    return p


CONTINUE_INTENT=R/'ONLY_UNEXECUTED_TARGET_CPU_AND_TASK_PUBLICATION_AFTER_MISSING_SYSPATH_INTENT.json'
assert not CONTINUE_INTENT.exists()
c=None;sf=None
try:
 c=t.connect()
 status=t.ps(c,"$x=Get-ScheduledTask -TaskName '"+TASK+"' -ErrorAction SilentlyContinue;[PSCustomObject]@{present=($null -ne $x)}|ConvertTo-Json -Compress")
 assert not status['present']
 save(CONTINUE_INTENT.name,dict(epoch=time.time(),original_error='source extraction passed then missing sys.path for new CPU body validator; noGPUlease/Task/start',no_reupload_or_reextract=True))
 unpack="from pathlib import Path\nimport json,hashlib,importlib.metadata as metadata,time,torch,sys\nroot=Path(ROOT);p=root/'payload';assert p.is_dir() and not (root/'ROOT_GPU_LEASE.json').exists() and not (root/'TASK_START_INTENT.json').exists()\nsys.path.insert(0,str(p))\nH=lambda q:hashlib.sha256(Path(q).read_bytes()).hexdigest()\nm=p/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json';assert H(m)==MANIFESTSHA\nmanifest=json.loads(m.read_bytes())\nfor r in manifest['file_rows']:\n q=p/r['relative'];assert q.stat().st_size==r['bytes'] and H(q)==r['sha256']\nsdk=json.loads((p/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())\nfor name,version in sdk['versions'].items():\n if version is not None:assert metadata.version(name)==version\nfor r in sdk['files']:assert H(r['path'])==r['sha256']\nck=p/'source/model_32635_left_repair.pt';assert H(ck)==SOURCESHA\nsource=torch.load(ck,map_location='cpu',weights_only=False)\ndef finite(v):\n if isinstance(v,torch.Tensor):\n  assert v.device.type=='cpu'\n  if v.is_floating_point():assert torch.isfinite(v).all();return 1\n  return 0\n if isinstance(v,dict):return sum(finite(x) for x in v.values())\n if isinstance(v,(list,tuple)):return sum(finite(x) for x in v)\n return 0\nfrom bodyframe_owned_CPU_state_validation_v1 import KEY,validate\nvalidate(source[KEY]);assert source['E1_WAVE50_BODYFRAME_OWN_GPU_SOURCE']['actual_GPU_fullrestore'] is True\ncore={k:v for k,v in source.items() if k not in (KEY,'E1_WAVE50_BODYFRAME_OWN_GPU_SOURCE')}\nassert finite(core)==107 and source['E1_terrain_state']['num_envs']==20000 and len(source['actor_state_dict'])==9\nassert source['LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION']['profile']=='left_initial_joint_margin014_std1_v1'\nassert not torch.cuda.is_initialized()\nprint(json.dumps(dict(epoch=time.time(),sourcefreeze_manifest_SHA=H(m),files=len(manifest['file_rows']),installed_SDK_files=len(sdk['files']),actual_checkpoint_SHA=H(ck),source_core_floating107=True,new_owned_body_state_validated=True,extra_body_tensors_not_counted_as_legacy_core=True,source_saved_envs20000=True,no_CUDA_or_trainingDR_resume=True)))\n"
 unpack=unpack.replace('ROOT',repr(ROOT)).replace('MANIFESTSHA',repr(CPU['manifest']['sha256'])).replace('SOURCESHA',repr(SHA))
 admitted=t.py(c,unpack);save('REFERENCE17B_EXTRACTED_SOURCE_CPU_ADMITTED_ACTUAL.json',admitted)
 sf=c.open_sftp()
 fresh=t.py(c,t.guard_code());assert not fresh['new_root_unused']
 lease=dict(epoch=time.time(),case_id=CASE,target_host='10.24.4.249',namespace='MOD4_3060_BODYFRAME_FIRST_FULL80_20261014',
            GPU_lease_granted_by_root=True,actual_shared_slot_idle_verified=True,resource_boundary=fresh,
            checkpoint_path=ROOT+'/payload/source/model_32635_left_repair.pt',checkpoint_sha256=SHA,
            worker_sha256=CPU['worker']['sha256'],factor_runtime_sha256=CPU['runtime']['sha256'],
            source_bundle_manifest_sha256=CPU['manifest']['sha256'],
            case_parameters=dict(steps=1500,num_envs=80,seed=20260928,body_sign=1,world_sign=1,feedback_current=False,headless=True,device='cuda:0'),
            frozen_original_white3_fixture=True,no_PPO=True,no_training20000_DR_restore=True,
            full_original1500_protocol_qualification_requires_complete_review=True)
 blob=json.dumps(lease,ensure_ascii=False,indent=2).encode();leasepath=ROOT+'/ROOT_GPU_LEASE.json'
 with sf.open(leasepath,'wx') as f:f.write(blob);f.flush()
 launcher="""from pathlib import Path
import sys,subprocess,json,time,os,hashlib,psutil
ROOT=Path(__file__).resolve().parent;payload=ROOT/'payload';lease=ROOT/'ROOT_GPU_LEASE.json';attempt=ROOT/'attempts/CASE'
assert not attempt.exists() and not (ROOT/'DEMAND_LAUNCH_ENTERED.json').exists()
row=dict(epoch=time.time(),pid=os.getpid(),creation=psutil.Process().create_time(),argv=sys.argv,lease_SHA=hashlib.sha256(lease.read_bytes()).hexdigest(),no_PPO=True)
with (ROOT/'DEMAND_LAUNCH_ENTERED.json').open('xb') as f:f.write(json.dumps(row,indent=2).encode());f.flush();os.fsync(f.fileno())
argv=[sys.executable,str(payload/'run_full80_parameter_bound_parent_v2.py'),'--lease',str(lease),'--attempt',str(attempt)]
with (ROOT/'DEMAND_PARENT_CONSOLE.log').open('xb') as log:
 p=subprocess.Popen(argv,cwd=str(payload),stdout=log,stderr=subprocess.STDOUT)
 (ROOT/'DEMAND_PARENT_LAUNCH_PID.json').write_text(json.dumps(dict(epoch=time.time(),launcher_pid=os.getpid(),parent_pid=p.pid,parent_creation=psutil.Process(p.pid).create_time(),argv=argv,no_PPO=True),indent=2))
 rc=p.wait()
(ROOT/'DEMAND_LAUNCH_EXIT.json').write_text(json.dumps(dict(epoch=time.time(),exit_code=rc,parent_pid=p.pid,no_PPO=True)))
sys.exit(rc)
""".replace('CASE',CASE)
 script=P/'demand_full80_frozen1500_parent_launcher_unique_once.py';assert not script.exists();compile(launcher,str(script),'exec');script.write_text(launcher,encoding='utf8')
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
