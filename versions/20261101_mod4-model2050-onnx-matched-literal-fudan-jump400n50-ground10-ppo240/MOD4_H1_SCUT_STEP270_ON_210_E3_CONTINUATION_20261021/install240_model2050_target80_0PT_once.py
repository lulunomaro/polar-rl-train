"""ROOT new240 namespace, one selected model upload, actual model-free80 admission."""
from pathlib import Path,PurePosixPath
import ast,hashlib,importlib.util,json,os,subprocess,sys,time,traceback
T=Path(__file__).resolve().parent;W=T.parent;N=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101';R=N/'reports'
GPU='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def stage(sf,p,b):
 cur=''
 for bit in str(PurePosixPath(p).parent).split('/'):
  if not bit:continue
  cur+='/'+bit
  try:sf.mkdir(cur)
  except OSError:sf.stat(cur)
 with sf.file(p,'wx')as f:f.write(b);f.flush()
ADMIT=r'''from pathlib import Path
import fcntl,hashlib,json,os,psutil,shutil,subprocess,sys,time,traceback
B=Path(v['job']);G=v['GPU_UUID'];locks=[];p=None;rc=None;error=None;result=None
def put(n,x):
 with(B/n).open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
try:
 for path in (Path('/home/lc01/Zonglin Li/zonglin2/state')/('three_expert_v2_'+G+'.lock'),Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock')):
  f=path.open('rb+')
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BaseException:f.close();raise
  locks.append(f)
 line=subprocess.check_output(['nvidia-smi','-i',G,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();a=[x.strip()for x in line.split(',')]
 ram=psutil.virtual_memory().available;disk=shutil.disk_usage(B).free
 resource=dict(epoch=time.time(),GPU_line=line,RAM_available=ram,disk_free=disk,private_and_validation_EX_held=True,no_PID_query=True)
 put('ACTUAL240_ADMISSION80_RESOURCE_HELD.json',resource)
 assert a[0]==G and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669 and int(a[3])<=30 and ram>32*1024**3 and disk>25*1024**3
 env=dict(os.environ,CUDA_VISIBLE_DEVICES=G,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
 for k in ('PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(k,None)
 for k,leaf in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp'}.items():
  path=B/'private_admission'/leaf;path.mkdir(parents=True,exist_ok=True);env[k]=str(path)
 args=[sys.executable,'-u','-B',str(B/'run240_model2050_mixed_literal_worker.py'),'--mode','admission','--num-envs','80','--run-id','MODEL2050_TARGET240_0PT80','--out',str(B/'admission80')]
 with(B/'ADMISSION80_FULL_STDOUT_STDERR.log').open('xb')as log:
  p=subprocess.Popen(args,cwd=B,env=env,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,close_fds=True)
  q=psutil.Process(p.pid);identity=dict(pid=q.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),cwd=q.cwd())
  put('ACTUAL240_ADMISSION80_WORKER_IDENTITY_BEFORE_WAIT.json',identity)
  try:rc=p.wait(timeout=900)
  except subprocess.TimeoutExpired:
   put('ACTUAL240_ADMISSION80_ORIGINAL_TIMEOUT_NO_SIGNAL.json',dict(epoch=time.time(),error=traceback.format_exc(),signal_sent=False,original_wait_pending=True));raise
 put('ACTUAL240_ADMISSION80_ORIGINAL_WAIT.json',dict(epoch=time.time(),returncode=rc,original_waited=True,identity=identity))
 proof=B/'admission80/ACTUAL240_0PT_SOURCE_SDK_NATIVE8_ADMISSION.json';function=B/'admission80/FUNCTION_RETURNED.json'
 result=json.loads(proof.read_bytes()) if proof.is_file() else None
 assert rc==0 and result and result['passed'] and result['controls']==8 and result['physics_callbacks']==64 and result['num_envs']==80
 assert function.is_file() and json.loads(function.read_bytes())['passed']
 assert not list((B/'admission80').glob('*ERROR*.json')) and(B/'admission80/APP240_CLOSING.json').is_file()
 text=(B/'ADMISSION80_FULL_STDOUT_STDERR.log').read_text('utf8',errors='replace')
 assert not any('PxPhysics::createMaterial'in x and'64K'in x for x in text.splitlines())
except BaseException:
 error=traceback.format_exc();put('ACTUAL240_ADMISSION80_ORIGINAL_PARENT_ERROR.json',dict(epoch=time.time(),error=error,no_auto_retry_or_signal=True))
finally:
 if p is not None:rc=p.wait()
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
 put('ACTUAL240_ADMISSION80_ALL_WAITED_EX_RELEASED.json',dict(epoch=time.time(),all_own_children_waited=p is None or p.poll()is not None,returncode=rc,
  private_and_validation_EX_acquired=len(locks)==2,private_and_validation_EX_released=len(locks)==2,signals=0))
texts=[]
for path in [B/'ADMISSION80_FULL_STDOUT_STDERR.log']+list(B.glob('ACTUAL240_ADMISSION80*.json'))+list((B/'admission80').glob('*.json')):
 if path.is_file():
  raw=path.read_bytes();texts.append(dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8','replace')))
print(json.dumps(dict(epoch=time.time(),passed_execution=error is None,returncode=rc,parent_error=error,result=result,full_UTF8=texts,
 private_and_validation_EX_released=len(locks)==2,all_own_children_waited=p is None or p.poll()is not None,models_or_NN_or_PPO_or_account_writes=0)))
'''
def main():
 assert sys.version_info[:2]==(3,14)
 install=read(R/'INSTALL240_SOURCE_ASSET_MANIFEST.json');cpu=read(R/'ROOT240_SELECTED2050_FULLPPO_SOURCE_AND_ONNX_CPU_QUALIFIED_ACTUAL.json')
 assert cpu['passed'] and read(R/'ROOT240_NEW_SOURCE_TaskGO_CPU_RETURNED_ACTUAL.json')['passed']
 J=install['job_root'];O=install['owner_root'];assert J!=O
 pattern='install240_|transfer240_|read240_|start240_|run_ROOT240_|launch_e2_solo_|collect_e2_solo_|run_ROOT_latest32481_|run_ROOT238_|admit238_|read239_|run_actual'
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(q.stdout)if q.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];assert len(rows)==len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower()
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT240_ADMIT80_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),passed=True,PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows))
 put('ROOT240_ADMIT80_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),job_root=J,GPU_UUID=GPU,
  selected2050_local_upload_reads=1,selected2050_remote_admission_reads=0,source_models_CPU_or_GPU_decodes_this_entry=0,
  original_own_source_asset_copies_new_namespace=True,postcopy_source_assets_integrity_passes=1,native80_controls=8,max_parent_wait_seconds=1080,
  no_new_learning_GO_or_account_write=True,no_kill_or_signal=True))
 wrapper=module('root240_admit_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 source=module('root240_existing_remote_helpers',T/'E2_PLAN_MIMIC01_ADMISSION_KIND_ROOT_V4_20261101/remote_e2_solo_payloads.py')
 client=transport=previous=secret=None
 try:
  transport,previous=wrapper.install();sec=module('root240_admit_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover()
  client=d.connect72(secret);secret=None
  put('ROOT240_ADMIT80_FRESH72_CNONE_RESERVE_ACTUAL.json',d.code(client,d.PY72,source.AUTH,{},timeout=45))
  create=source.CREATE.replace("(J/'control_e2_solo').mkdir()","(J/'control240').mkdir()")
  put('ROOT240_NEW_SOURCE_TARGET_AND_OWNER_NAMESPACES_ACTUAL.json',d.code(client,d.PY72,create,dict(job=J,owner=O),timeout=30))
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   for row in install['files']:
    # These new target files have no checkpoints; assets are necessary SDK inputs.
    assert not row['relative'].endswith('.pt');sfpath=J+'/'+row['relative']
    if row['bytes']>1024*1024:
     stage(sf,sfpath,b'')
     with sf.file(sfpath,'wb')as remote,Path(row['local_path']).open('rb')as local:
      while chunk:=local.read(1024*1024):remote.write(chunk)
    else:stage(sf,sfpath,Path(row['local_path']).read_bytes())
   selected=Path(cpu['source_path'])
   with selected.open('rb')as f:b=f.read()
   assert len(b)==cpu['source_bytes'] and hashlib.sha256(b).hexdigest()==cpu['source_SHA']
   stage(sf,J+'/source_model/model_2050_selected.pt',b);del b
  finally:sf.close()
  verify=source.POSTCOPY_NO_MODEL
  put('ROOT240_NEW_NAMESPACE_SOURCE_ASSET_POSTCOPY_ACTUAL.json',d.code(client,d.PY72,verify,dict(job=J,files=install['files']),timeout=180))
  result=d.code(client,d.PY72,ADMIT,dict(job=J,GPU_UUID=GPU),timeout=1080)
  put('ROOT240_ACTUAL_TARGET80_NATIVE8_0PT_OR_ORIGINAL_ERROR_RETURNED.json',result)
  assert result['passed_execution'] and result['returncode']==0 and result['private_and_validation_EX_released'] and result['all_own_children_waited']
  print(json.dumps(dict(passed=True,controls=result['result']['controls'],physics_callbacks=result['result']['physics_callbacks'],num_envs=result['result']['num_envs'],selected2050_GPU_decodes=0,all_own_waited_EX_free=True)),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT240_ADMIT80_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT240_ADMIT80_ORIGINAL_CALLER_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_auto_retry=True));raise
