"""Root-authorized unique249 deployment and first120 frozen baseline.

No210, Linux RPC, oldtask/job, localGPU, installedSDK or canonical budget changes.
Unknown outcomes are inspected from actual receipts; this script is once-only.
"""
from pathlib import Path
import sys,os,json,time,base64,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
ROOT='D:/MOD4_async_eval/MOD4_DIRECT_FACTOR_20261013'
PY='D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe'
TASK='MOD4_DirectFactor_20261013_baseline120_v2'
CASE='native3060_bodypos_worldpos_baseline120_v2'
Z=D/'DIRECT3060_NATIVE_FROZEN_FACTOR_CPU_PREPARED_V2_20261013.zip'
ZH='5585cc8d119907fe452b2a0d3db17e33001ac41f4f71e366af4bd2871f5c149f'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
GUARD=r'''
from pathlib import Path
import os,json,time,msvcrt,psutil,subprocess
root=Path(ROOT);lock=Path('D:/MOD4_async_eval/worker.lock');rows=[]
for p in psutil.process_iter(['pid','create_time','name','cmdline','ppid']):
 try:
  a=p.info;s=' '.join(a.get('cmdline') or []).lower()
  if any(w in s for w in ['paired_direct3060','run_direct3060','eval_worker','mirror_target_tui.py','kit.exe']):rows.append(a)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
assert not rows, 'Another evaluation/Kit/oldworker process exists'
assert lock.exists()
with lock.open('rb') as f:
 f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
gpu=subprocess.run(['nvidia-smi','--query-gpu=index,name,memory.total,memory.free','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=20)
assert gpu.returncode==0,gpu.stderr
device=gpu.stdout.strip().splitlines();assert len(device)==1
index,name,total,free=[x.strip() for x in device[0].split(',')];assert int(index)==0 and int(free)>=4096
apps=subprocess.run(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],capture_output=True,text=True,timeout=20)
assert apps.returncode==0;active=[x.strip() for x in apps.stdout.splitlines() if x.strip() and 'No running processes' not in x]
desktop=[];unknown=[]
allowed_names={'textinputhost.exe','explorer.exe','shellexperiencehost.exe','searchhost.exe','phoneexperiencehost.exe','opencode.exe','msedgewebview2.exe','chatgpt.exe','codex-computer-use-swift.exe','startmenuexperiencehost.exe','dwm.exe','msedge.exe','wudfhost.exe'}
for line in active:
 try:
  pid=int(line.split(',')[0].strip());process=psutil.Process(pid);exe=process.exe();argv=process.cmdline();name=Path(exe).name.lower()
  if name not in allowed_names:unknown.append(dict(pid=pid,exe=exe))
  else:desktop.append(dict(pid=pid,creation=process.create_time(),exe=exe,role='actual Windows desktop/browser/Codex background process; retained untouched'))
 except (ValueError,psutil.NoSuchProcess,psutil.AccessDenied):unknown.append(dict(raw=line,unresolved=True))
assert not unknown, 'Another or unresolved non-desktop compute process owns GPU'
ram=psutil.virtual_memory();disk=psutil.disk_usage('D:/')
assert ram.available>=8*2**30 and disk.free>=4*2**30
outbound=[]
for c in psutil.net_connections(kind='tcp'):
 if c.raddr and c.raddr.ip in ['10.24.4.210','172.27.131.74']:outbound.append(dict(pid=c.pid,remote=list(c.raddr),status=c.status))
assert not outbound, 'Retired210 bridge still connected'
print(json.dumps(dict(epoch=time.time(),root=str(root),new_root_unused=not root.exists(),shared_OS_lock_free=True,
 GPU=dict(index=int(index),name=name,total_MiB=int(total),free_MiB=int(free),confirmed_WDDM_desktop_GPU_processes=desktop,unknown_or_evaluation_compute_processes=unknown),
 RAM_available=ram.available,durable_D_free=disk.free,thresholds=dict(RAM_available_min=8*2**30,durable_min=4*2**30,GPU_free_MiB_min=4096),
 oldworker_and_GPUchild_absence=True,target210_outbound=[],read_only=True)))
'''
def py(c,code,timeout=60):
 compile(code,'<authorized249 reviewed operation>','exec');enc=base64.b64encode(code.encode()).decode()
 command='"'+PY+'" -X utf8 -c "import base64;exec(base64.b64decode(\''+enc+'\'))"'
 _,o,e=c.exec_command(command,timeout=timeout);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 assert rc==0,(rc,err.decode('utf8','replace')[-6000:]);return json.loads(raw)
def ps(c,code,timeout=60):
 enc=base64.b64encode(code.encode('utf16le')).decode()
 _,o,e=c.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+enc,timeout=timeout)
 raw=o.read();err=e.read();rc=o.channel.recv_exit_status();assert rc==0,(rc,err.decode('utf8','replace')[-5000:])
 return json.loads(raw.decode('utf8-sig'))
def save(name,value):
 p=R/name;assert not p.exists()
 with p.open('wb') as f:f.write(json.dumps(value,ensure_ascii=False,indent=2).encode());f.flush();os.fsync(f.fileno())
 return p
def main():
 assert H(Z)==ZH and Z.stat().st_size==39_611_767
 assert not (R/'DIRECT3060_BASELINE120_DEPLOY_INTENT.json').exists()
 sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'))
 from reuse_authorized_session_transport import recover
 secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret;os.environ['MOD4_EVAL_SSH_PASSWORD']=secret
 sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'))
 from eval_remote_io import connect_eval
 c=connect_eval();sf=None
 try:
  guard=py(c,GUARD.replace('ROOT',repr(ROOT)));assert guard['new_root_unused']
  save('DIRECT3060_BASELINE120_RESOURCE_BOUNDARY_ADMITTED_ACTUAL.json',guard)
  save('DIRECT3060_BASELINE120_DEPLOY_INTENT.json',dict(epoch=time.time(),root=ROOT,task=TASK,case_id=CASE,package_SHA=ZH,
   root_authorized_unique_deploy_baseline120=True,no_replay_after_unknown_outcome=True))
  created=py(c,'from pathlib import Path\nimport json\np=Path('+repr(ROOT)+');assert not p.exists();p.mkdir();print(json.dumps(dict(new_root=str(p),created=True)))')
  sf=c.open_sftp();remote=ROOT+'/SOURCE_PACKAGE_5585cc8d.zip';sf.put(str(Z),remote)
  uploaded=py(c,'from pathlib import Path\nimport json,hashlib\np=Path('+repr(remote)+');print(json.dumps(dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())))')
  assert uploaded['bytes']==Z.stat().st_size and uploaded['sha256']==ZH
  save('DIRECT3060_BASELINE120_ACTUAL_PACKAGE_UPLOAD_SHA.json',uploaded)
  unpack=r'''
from pathlib import Path
import zipfile,json,hashlib,importlib.metadata as metadata
root=Path(ROOT);p=root/'payload';assert not p.exists();p.mkdir()
with zipfile.ZipFile(root/'SOURCE_PACKAGE_5585cc8d.zip') as z:
 for name in z.namelist():
  target=(p/name).resolve();assert target.is_relative_to(p.resolve())
 z.extractall(p)
H=lambda q:hashlib.sha256(Path(q).read_bytes()).hexdigest()
m=p/'SOURCE_BUNDLE_V2_MANIFEST.json';assert H(m)=='e707752857aa7798cc54e1466b0ff7bf89d7691b23854e23fe88ae0c78a8c6ff'
manifest=json.loads(m.read_bytes())
for r in manifest['file_rows']:
 q=p/r['relative'];assert q.stat().st_size==r['bytes'] and H(q)==r['sha256']
sdk=json.loads((p/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for name,version in sdk['versions'].items():
 if version is not None:assert metadata.version(name)==version
for r in sdk['files']:assert H(r['path'])==r['sha256']
print(json.dumps(dict(epoch=__import__('time').time(),root=str(root),payload=str(p),manifest_SHA=H(m),files=len(manifest['file_rows']),SDK_API_files=len(sdk['files']),
 actual_sourcefreeze_and_installed_backend_verified=True,checkpoint_SHA=H(p/'source/model_32396_91d.pt'),no_GPU=True)))
'''
  unpacked=py(c,unpack.replace('ROOT',repr(ROOT)));save('DIRECT3060_BASELINE120_EXTRACTED_SOURCE_TARGET_CPU_ACTUAL.json',unpacked)
  fresh=py(c,GUARD.replace('ROOT',repr(ROOT)));assert not fresh['new_root_unused']
  lease=dict(epoch=time.time(),case_id=CASE,target_host='10.24.4.249',namespace='MOD4_3060_DIRECT_FACTOR_20261013',GPU_lease_granted_by_root=True,
   actual_shared_slot_idle_verified=True,resource_boundary=fresh,
   checkpoint_path=ROOT+'/payload/source/model_32396_91d.pt',checkpoint_sha256='91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4',
   worker_sha256='8fc3fac11f2c309158117512bb3b41fdd34640916f8332fdf3252b5b27f2de05',factor_runtime_sha256='6c2499a95e20f91b7787a1b41e183a343aa46afbc77d6dd86454c1f57847a542',
   source_bundle_manifest_sha256='e707752857aa7798cc54e1466b0ff7bf89d7691b23854e23fe88ae0c78a8c6ff',
   case_parameters=dict(steps=120,num_envs=8,seed=20260928,body_sign=1,world_sign=1,feedback_current=False,headless=True,device='cuda:0'),
   frozen_white3_fixture_only=True,no_training_fullDR_resume=True,no_PPO=True,not_full15s_route_qualification=True)
  lease_bytes=json.dumps(lease,ensure_ascii=False,indent=2).encode();lease_path=ROOT+'/BASELINE120_ROOT_GPU_LEASE.json'
  with sf.open(lease_path,'wx') as f:f.write(lease_bytes);f.flush()
  launcher=r'''from pathlib import Path
import sys,subprocess,json,time,os,hashlib,psutil
ROOT=Path(__file__).resolve().parent;payload=ROOT/'payload';lease=ROOT/'BASELINE120_ROOT_GPU_LEASE.json';attempt=ROOT/'attempts/native3060_bodypos_worldpos_baseline120_v2'
assert not attempt.exists() and not (ROOT/'DEMAND_LAUNCH_ENTERED.json').exists()
row=dict(epoch=time.time(),pid=os.getpid(),creation=psutil.Process().create_time(),argv=sys.argv,lease_SHA=hashlib.sha256(lease.read_bytes()).hexdigest(),no_PPO=True)
with (ROOT/'DEMAND_LAUNCH_ENTERED.json').open('xb') as f:f.write(json.dumps(row,indent=2).encode());f.flush();os.fsync(f.fileno())
argv=[sys.executable,str(payload/'run_direct3060_factor_parent_v2.py'),'--lease',str(lease),'--attempt',str(attempt)]
with (ROOT/'DEMAND_PARENT_CONSOLE.log').open('xb') as log:
 p=subprocess.Popen(argv,cwd=str(payload),stdout=log,stderr=subprocess.STDOUT)
 (ROOT/'DEMAND_PARENT_LAUNCH_PID.json').write_text(json.dumps(dict(epoch=time.time(),launcher_pid=os.getpid(),parent_pid=p.pid,parent_creation=psutil.Process(p.pid).create_time(),argv=argv,no_PPO=True),indent=2))
 rc=p.wait()
(ROOT/'DEMAND_LAUNCH_EXIT.json').write_text(json.dumps(dict(epoch=time.time(),exit_code=rc,parent_pid=p.pid,no_PPO=True)))
sys.exit(rc)
'''
  local_launcher=D/'demand_baseline120_parent_launcher_once.py';assert not local_launcher.exists();local_launcher.write_text(launcher,encoding='utf8');compile(launcher,str(local_launcher),'exec')
  sf.put(str(local_launcher),ROOT+'/demand_baseline120_parent_launcher_once.py')
  setup=ps(c,"$ErrorActionPreference='Stop'; $name="+repr(TASK)+"; if(Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue){throw 'Task already exists'}; $action=New-ScheduledTaskAction -Execute '"+PY+"' -Argument '\""+ROOT+"/demand_baseline120_parent_launcher_once.py\"' -WorkingDirectory '"+ROOT+"'; $user=[System.Security.Principal.WindowsIdentity]::GetCurrent().Name; $principal=New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited; $settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew; Register-ScheduledTask -TaskName $name -Action $action -Principal $principal -Settings $settings | Out-Null; $t=Get-ScheduledTask -TaskName $name; [PSCustomObject]@{name=$t.TaskName;state=[string]$t.State;triggers=@($t.Triggers).Count;user=$user;action=$t.Actions.Execute;arguments=$t.Actions.Arguments}|ConvertTo-Json -Compress")
  assert setup['triggers']==0;save('DIRECT3060_BASELINE120_DEMAND_TASK_REGISTERED_ACTUAL.json',setup)
  start=ps(c,"$ErrorActionPreference='Stop'; $name='"+TASK+"'; $p='"+ROOT+"/TASK_START_INTENT.json'; if(Test-Path -LiteralPath $p){throw 'Start intent consumed'}; [IO.File]::WriteAllText($p,'{\"single_start_requested\":true}'); Start-ScheduledTask -TaskName $name; $t=Get-ScheduledTask -TaskName $name; [PSCustomObject]@{name=$name;state=[string]$t.State;triggers=@($t.Triggers).Count;single_start_requested=$true}|ConvertTo-Json -Compress")
  save('DIRECT3060_BASELINE120_DEMAND_TASK_STARTED_ACTUAL.json',dict(epoch=time.time(),task=start,lease=lease,lease_SHA=hashlib.sha256(lease_bytes).hexdigest(),launcher_SHA=H(local_launcher),unique_start=True))
  print(json.dumps(dict(deployed=True,task=start,root=ROOT,case=CASE,GPU_result_pending=True)),flush=True)
 except Exception as e:
  q=R/('DIRECT3060_BASELINE120_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');q.write_text(json.dumps(dict(epoch=time.time(),error=repr(e),traceback=traceback.format_exc(),no_blind_upload_or_start_retry=True),ensure_ascii=False,indent=2),encoding='utf8');raise
 finally:
  if sf:sf.close()
  c.close();os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
if __name__=='__main__':main()
