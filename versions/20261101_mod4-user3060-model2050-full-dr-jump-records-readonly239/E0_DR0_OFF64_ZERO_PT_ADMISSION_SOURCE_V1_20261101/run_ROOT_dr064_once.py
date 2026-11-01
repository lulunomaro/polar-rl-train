"""ROOT-only existing Py314 serial0PT64 admission;unselected until ROOT evidence decision."""
from pathlib import Path,PurePosixPath
import argparse,ast,hashlib,importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
C=T/'E0_ALL_RANDOMIZATION_OFF_DR0_SOURCE_CONTRACT_V1_20261101'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def mod(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
AUTH='''from pathlib import Path
import hashlib,json,psutil,time
ns={};exec(v['authority_source'],ns)
ns.update(Path=Path,hashlib=hashlib,json=json,psutil=psutil,time=time,read=lambda p:json.loads(Path(p).read_bytes()))
exec(v['audit_function'],ns);a=ns['audit_current'](v['binding']);assert a['scope']['active_GPU_UUID']!=v['GPU_UUID'];print(json.dumps(a))'''
SETUP='''from pathlib import Path
import json,shutil
B=Path(v['job']);base=Path(v['base_runtime']);assert B.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve()) and not B.exists()
assert (base/'isaac/mod4/mod4_task.py').is_file() and (base/'assets/robot.usd').is_file() and not B.resolve().is_relative_to(base.resolve())
B.mkdir(parents=True);dst=B/'runtime'
def ignore(p,names):
 return [x for x in names if x in ('logs','learning_logs','kit_isolation','private_train','__pycache__','.git','.cache') or Path(x).suffix in ('.pt','.pth','.onnx','.jsonl')]
shutil.copytree(base,dst,ignore=ignore)
print(json.dumps(dict(passed=True,new_root=str(B),new_runtime=str(dst),source_runtime=str(base),physical_source_asset_copy_purpose='Necessary independent0PT64 nominal constructor;model/log/trajectory suffixes excluded',source_model_reads=0,source_model_copies=0,account_writes=0)))'''
CASE='''from pathlib import Path
import fcntl,hashlib,json,os,psutil,shutil,subprocess,sys,time,traceback
B=Path(v['job']);sys.path.insert(0,str(B))
from audit235_dr064 import audit_current
for r in v['components']:
 p=B/r['relative'];b=p.read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['SHA']
for r in v['off_modules']:
 src=B/'off_sources'/Path(r['relative']).name;dst=B/'runtime/isaac/mod4'/src.name
 b=src.read_bytes();assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['SHA'];shutil.copyfile(src,dst)
locks=[];child=None;error=None;wait=None;result=None
try:
 for path in [Path('/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_'+v['GPU_UUID']+'.lock'),Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock')]:
  f=path.open('rb+')
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BaseException:f.close();raise
  locks.append(f)
 auth=audit_current(v['binding']);assert auth['scope']['active_GPU_UUID']!=v['GPU_UUID']
 line=subprocess.check_output(['nvidia-smi','-i',v['GPU_UUID'],'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();a=[x.strip() for x in line.split(',')]
 ram=psutil.virtual_memory().available;disk=shutil.disk_usage(B).free
 assert a[0]==v['GPU_UUID'] and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669 and int(a[3])<=30 and ram>32*1024**3 and disk>25*1024**3
 admission=dict(epoch=time.time(),passed=True,authority=auth,GPU_line=line,RAM_available=ram,disk_free=disk,private_and_validation_EX=True,nonempty_compute_UUID_allowed=True,account_writes=0)
 with (B/'ACTUAL_DR064_AUTHORITY_RESOURCE.json').open('x') as f:json.dump(admission,f,indent=2)
 task=dict(kind='DR0_OFF64_ZERO_PT_ORIGINAL_PHYSICAL_ADMISSION_V1',purpose_id=v['purpose_id'],num_envs=64,controls=8,seed=v['seed'],new_runtime_root=str(B/'runtime'),off_modules=v['off_modules'],original_env=v['original_env'],actual_parent_private_validation_EX_held=True,NN_model_reads=0,PPO_updates=0,core_INDEX_SHA=v['core_INDEX_SHA'])
 with (B/'TASK_DR064_ACTUAL.json').open('x') as f:json.dump(task,f,indent=2)
 env=dict(os.environ,CUDA_VISIBLE_DEVICES=v['GPU_UUID'],PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
 for k in ('PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(k,None)
 for k,leaf in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp'}.items():
  p=B/'private'/leaf;p.mkdir(parents=True,exist_ok=True);env[k]=str(p)
 with (B/'ACTUAL_DR064_STDOUT_STDERR.log').open('xb') as log:
  child=subprocess.Popen([v['python'],'-B','-u',str(B/'probe_dr0_64_worker_ROOT_ONLY.py'),'--task',str(B/'TASK_DR064_ACTUAL.json')],cwd=B,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,close_fds=True)
  p=psutil.Process(child.pid);identity=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),cwd=p.cwd())
  with (B/'DR064_IDENTITY_BEFORE_WAIT.json').open('x') as f:json.dump(identity,f,indent=2)
  rc=child.wait(timeout=360);wait=dict(epoch=time.time(),returncode=rc,original_waited=True,identity=identity)
 result=json.loads((B/'ACTUAL_DR064_RESULT.json').read_bytes());errors=[str(x) for x in B.glob('*ERROR*.json')]
 text=(B/'ACTUAL_DR064_STDOUT_STDERR.log').read_text(encoding='utf8',errors='replace');material=[x for x in text.splitlines() if 'PxPhysics::createMaterial' in x and '64K' in x]
 assert rc==0 and result['passed'] and not errors and not material and (B/'DR064_APPCLOSING_BEFORE_CLOSE.json').is_file()
except BaseException:
 error=traceback.format_exc()
 with (B/'ACTUAL_DR064_PARENT_ERROR.json').open('x') as f:json.dump(dict(epoch=time.time(),error=error,no_automatic_retry=True),f,indent=2)
finally:
 if child is not None:
  rc=child.wait()
  if wait is None:wait=dict(epoch=time.time(),returncode=rc,original_waited=True,after_original_parent_error=True)
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
 released=dict(epoch=time.time(),all_own_children_waited=child is None or child.poll() is not None,private_validation_EX_acquired=len(locks)==2,all_owned_EX_released=True,wait=wait)
 with (B/'DR064_ALL_WAITED_EX_RELEASED.json').open('x') as f:json.dump(released,f,indent=2)
texts=[]
for p in sorted(B.iterdir()):
 if p.is_file() and p.suffix in ('.json','.log'):
  b=p.read_bytes();texts.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8','replace')))
print(json.dumps(dict(epoch=time.time(),passed_execution=error is None and bool(result and result['passed']),result=result,original_error=error,original_wait=wait,release=released,full_UTF8=texts,model_reads=0,model_copies=0,account_writes=0,GUI=False)))'''

def main():
 assert sys.version_info[:2]==(3,14),'Existing Py314 compression.zstd control transport required'
 p=argparse.ArgumentParser()
 for k in ('authority-binding','auth-provider','original-manifest'):p.add_argument('--'+k,type=Path,required=True)
 for k in ('root-lease-label','purpose-id','remote-job-root','base-runtime-root','GPU-UUID','additional-control-pattern','source-index-SHA'):p.add_argument('--'+k,required=True)
 a=p.parse_args();assert a.root_lease_label.startswith('ROOT_DR064_EXCLUSIVE_') and a.purpose_id.startswith('ROOT_DR064_') and a.additional_control_pattern
 idx=N/'INDEX_DR064_SOURCE_FROZEN.json';assert H(idx)==a.source_index_SHA
 for r in read(idx)['files']:assert Path(r['path']).suffix in ('.py','.json','.md') and H(r['path'])==r['SHA']
 assert H(C/'INDEX_DR0_OFF_SOURCE_CORE_FROZEN.json')=='71d34a674382769f04f36a1ee6fc2018ba7e5215d14fbc7553471b11cf94f029'
 assert read(R/'CPU_DR064_NEW_SOURCE_INTERFACE_ACTUAL.json')['passed']
 components=read(R/'DR064_SOURCE_COMPONENTS.json')['files'];off=read(C/'reports/INSTALL_DR0_OFF_MODULES.json')['files'];binding=read(a.authority_binding);original=read(a.original_manifest)['env']
 pattern='run_ROOT_dr064_|run_ROOT_latest32481_|launch_e2_solo_|collect_e2_solo_|review_e2_solo_|'+a.additional_control_pattern
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern.replace("'","''")+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(q.stdout) if q.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];other=[x for x in rows if x['ProcessId']!=os.getpid()]
 assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower() and not other
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT_DR064_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),rows=rows,PID=os.getpid(),passed=True))
 put('ROOT_DR064_ONCE_BEFORE_NETWORK.json',dict(epoch=time.time(),purpose_id=a.purpose_id,model_byte_decode=[0,0],NN_constructors=0,PPO_updates=0,account_writes=0,source_asset_runtime_copy_to_NEW_namespace=True,original_reset_bank_constructor_read_declared=True))
 wrapper=mod('dr064_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 text=(N/'audit235_dr064.py').read_text(encoding='utf8');fn=next(x for x in ast.parse(text).body if isinstance(x,ast.FunctionDef) and x.name=='audit_current')
 auth=dict(authority_source=(N/'authority235_dr064.py').read_text(encoding='utf8'),audit_function=ast.get_source_segment(text,fn),binding=binding,GPU_UUID=a.GPU_UUID)
 client=transport=previous=secret=None
 try:
  transport,previous=wrapper.install();secret=mod('dr064_auth',a.auth_provider).recover();client=d.connect72(secret)
  put('ROOT_DR064_FRESH72_EXACT235_OR_CLOSED_CNONE_CLOSE72.json',d.code(client,d.PY72,AUTH,auth,timeout=45));client.close();client=None
  client=d.connect72(secret);secret=None
  put('ROOT_DR064_INDEPENDENT_RUNTIME_SOURCE_SETUP.json',d.code(client,d.PY72,SETUP,dict(job=a.remote_job_root,base_runtime=a.base_runtime_root),timeout=120))
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   for r in components:
    with sf.file(a.remote_job_root+'/'+r['relative'],'wx') as f:f.write(Path(r['path']).read_bytes());f.flush()
   sf.mkdir(a.remote_job_root+'/off_sources')
   for r in off:
    with sf.file(a.remote_job_root+'/off_sources/'+Path(r['relative']).name,'wx') as f:f.write(Path(r['local_path']).read_bytes());f.flush()
  finally:sf.close()
  actual=d.code(client,d.PY72,CASE,dict(job=a.remote_job_root,components=components,off_modules=off,binding=binding,GPU_UUID=a.GPU_UUID,
   original_env=original,python=d.PY72,seed=20260928,purpose_id=a.purpose_id,core_INDEX_SHA='71d34a674382769f04f36a1ee6fc2018ba7e5215d14fbc7553471b11cf94f029'),timeout=480)
  put('ROOT_DR064_ORIGINAL_CASE_OR_ERROR_RETURNED.json',actual);print(json.dumps(dict(passed_execution=actual['passed_execution'],result=actual.get('result'),error=actual.get('original_error'))),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT_DR064_ALL_SSH_CLOSED_SESSION_RESTORED.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE',physical_child_EX_status='Use original wait/release receipts;UNKNOWN on transport exception',no_signal=True))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT_DR064_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_retry=True));raise
