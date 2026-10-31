"""ROOT one finite original-CAD scene admission, no robot/checkpoint/GO/ledger."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,posixpath,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';R.mkdir(exist_ok=True)
S=T/'W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031'
REMOTE='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_RM70_SCENE_20261101v211/source_admission'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m

REMOTE_CODE="""from pathlib import Path
import json,hashlib,fcntl,os,psutil,shutil,subprocess,time,traceback
B=Path(v['job']);owned=Path('/home/lc01/Zonglin Li/zonglin2');gpu=v['GPU_UUID']
def put(name,x):
 with (B/name).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
assert B.resolve().is_relative_to((owned/'tasks').resolve())
for r in v['files']:
 p=B/r['relative'];assert p.stat().st_size==r['bytes']
 with p.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
 assert sha==r['SHA']
receipt=dict(actual_postcopy_fullSHA_verified=True,files=[dict(relative=r['asset_relative'],bytes=r['bytes'],SHA=r['SHA']) for r in v['files'] if 'asset_relative' in r])
put('RM70_BINARY_INSTALL_ACTUAL.json',receipt)
task=dict(kind='NEW208_ORIGINAL_CAD_SCENE_ZERO_PT',num_envs=8,max_physics_steps=8,max_wall_seconds=180,model_opens=0,raw_JSONL_opens=0,neural_optimizer_updates=0,
 root_actual_exclusive_control_and_GPU_admission=True,GPU_UUID=gpu,worker_SHA=v['worker_SHA'])
lock=(owned/'state'/('three_expert_v2_'+gpu+'.lock')).open('rb+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
p=None;rc=None;error=None;resource=None
try:
 with (owned/'state/finite_environment_validation.lock').open('rb+') as shared:fcntl.flock(shared,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(shared,fcntl.LOCK_UN)
 line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();a=[x.strip() for x in line.split(',')]
 ram=psutil.virtual_memory().available;disk=shutil.disk_usage(B).free
 assert a[0]==gpu and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669 and int(a[3])<=30 and ram>32*1024**3 and disk>25*1024**3
 resource=dict(epoch=time.time(),GPU_line=line,RAM_available=ram,disk_free=disk,private_EX=True);put('RESOURCE211_ACTUAL.json',resource);put('SCENE0PT208_TASK.json',task)
 env=dict(os.environ,CUDA_VISIBLE_DEVICES=gpu,PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
 for k in ('PYTHONHOME','PYTHONPATH','LD_PRELOAD','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):env.pop(k,None)
 for k,name in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','XDG_RUNTIME_DIR':'state/runtime','CUDA_CACHE_PATH':'cache/cuda','WARP_CACHE_PATH':'cache/warp','TORCH_HOME':'cache/torch'}.items():
  target=B/'private'/name;target.mkdir(parents=True,exist_ok=True);env[k]=str(target)
 argv=[str(owned/'run-python.sh'),'-u','-B',str(B/'scene0pt211.py'),'--job-root',str(B)]
 with (B/'SCENE211_FULL_STDOUT_STDERR.log').open('xb') as out:p=subprocess.Popen(argv,cwd=B,env=env,stdout=out,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,pass_fds=(lock.fileno(),),start_new_session=True,close_fds=True)
 q=psutil.Process(p.pid);identity=dict(pid=q.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),cwd=q.cwd());put('SCENE211_WORKER_ORIGINAL_IDENTITY_BEFORE_WAIT.json',identity)
 rc=p.wait(timeout=300);put('SCENE211_ORIGINAL_WAITED_EXIT.json',dict(returncode=rc,actual_waited=True,identity=identity))
except BaseException:
 error=traceback.format_exc();put('SCENE211_PARENT_ORIGINAL_ERROR.json',dict(error=error,no_automatic_retry=True))
finally:
 waited=p is None or p.poll() is not None
 if waited:fcntl.flock(lock,fcntl.LOCK_UN)
 lock.close();put('SCENE211_PRIVATE_EX_EXIT_SCOPE.json',dict(all_own_children_waited=waited,private_EX_released=waited,if_timeout_inheritedFD_retains_original_lock=True))
result=B/'scene0pt208/SCENE0PT208_ACTUAL.json';value=json.loads(result.read_bytes()) if result.is_file() else None
texts=[]
for folder in (B,B/'scene0pt208'):
 for path in sorted(folder.iterdir()) if folder.is_dir() else []:
  if path.is_file() and path.suffix in ('.json','.log'):
   raw=path.read_bytes();texts.append(dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8','replace')))
print(json.dumps(dict(epoch=time.time(),passed=bool(rc==0 and waited and not error and value and value.get('passed_scene_and_route_ground_query')),result=value,
 returncode=rc,all_own_children_waited=waited,private_EX_released=waited,parent_error=error,resource=resource,full_UTF8=texts,model_reads=0,account_writes=0)))
"""

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root-lease-label',required=True);args=parser.parse_args();assert args.root_lease_label.startswith('ROOT211_EXCLUSIVE_SCENE_')
 index=S/'INDEX208_FROZEN.json';assert H(index)=='e4f5df8fbee2cf1c232e65dbf2068f0f72556aa075b47104ca1c49195bda920a'
 rows=[]
 for name in ('field208.py','course_math208.py','launcher208.py'):
  p=S/'source'/name;rows.append(dict(relative=name,local=str(p),bytes=p.stat().st_size,SHA=H(p)))
 original=(S/'source/scene0pt208.py').read_text('utf8')
 actual=original.replace("sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=.0025, device='cuda:0'))", "from isaaclab_physx.physics import PhysxCfg\n        sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=.0025, device='cuda:0', physics=PhysxCfg(solver_type=1, enable_external_forces_every_iteration=True)))")
 assert actual!=original
 p=N/'scene0pt211.py'
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(actual)
 rows.append(dict(relative=p.name,local=str(p),bytes=p.stat().st_size,SHA=H(p)))
 for relative,sha,size in [('assets/arena_collision.usdc','9f05b0cae71752f36ba95465ed6723f96321c1fd2262bb1e2d0f363c8266397b',635933),('data/arena_collision.npz','f79dae96a377992da9901979429db4a2e1af050399091f721d75a576f5b3e954',528810)]:
  p=W/'rmuc2026_training'/relative;assert p.stat().st_size==size
  rows.append(dict(relative='original_field/'+relative,asset_relative=relative,local=str(p),bytes=size,SHA=sha,local_binary_hashes=0))
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'install211_scene_source_zeroPT_once|launch210_|install209_|launch209_|collect197_|install208_|launch208_' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);cim=json.loads(p.stdout) if p.stdout.strip() else [];cim=cim if isinstance(cim,list) else [cim]
 own=[x for x in cim if x['ProcessId']==os.getpid()];others=[x for x in cim if x['ProcessId']!=os.getpid()]
 put('ROOT211_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=cim,others=others))
 assert len(own)==1 and own[0]['ExecutablePath'].lower()==sys.executable.lower() and own[0]['CreationDate'] and not others
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT211_SCENE_PURPOSE_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),root_lease_label=args.root_lease_label,source_index_SHA=H(index),files=rows,
  SDK_worker='one new8staticarena8step scene, no robot/no PT',original_collision_NPZ_max_constructor_loads=1,binary_asset_postcopy_hash_passes=1,
  no_old_data_reads_or_account_write=True,max_parent_wait_seconds=300,max_local_remote_seconds=600,
  source_delta='explicit installed SDK TGS solver_type1 only; no rigid articulation so32/4 joint solver iteration counts not applicable in this scene-only phase'))
 wrapper=module('scene211_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=None;transport=None;previous=None;secret=None
 try:
  transport,previous=wrapper.install();sec=module('scene211_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=d.connect72(secret);secret=None
  auth="""from pathlib import Path
import json,time,hashlib
P=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=P.read_bytes();c=json.loads(raw)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['active_segment'] is None and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
print(json.dumps(dict(passed=True,epoch=time.time(),CNone=True,SHA=hashlib.sha256(raw).hexdigest(),no_C_write=True)))"""
  put('ROOT211_FRESH72_CNONE_BEFORE_SCENE.json',d.code(client,d.PY72,auth,{},timeout=45))
  create="""from pathlib import Path
import json
B=Path(v['root']);assert B.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve());B.mkdir(parents=True,exist_ok=False)
print(json.dumps(dict(passed=True,new_root=str(B))))"""
  put('ROOT211_NEW_NAMESPACE_CREATED.json',d.code(client,d.PY72,create,dict(root=REMOTE),timeout=30))
  sf=client.open_sftp();sf.get_channel().settimeout(90)
  try:
   made=set()
   for row in rows:
    cur=REMOTE
    for bit in row['relative'].split('/')[:-1]:
     cur+='/'+bit
     if cur not in made:
      try:sf.mkdir(cur)
      except OSError:sf.stat(cur)
      made.add(cur)
    sf.put(row['local'],REMOTE+'/'+row['relative'])
  finally:sf.close()
  result=d.code(client,d.PY72,REMOTE_CODE,dict(job=REMOTE,files=rows,GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',worker_SHA=H(N/'scene0pt211.py')),timeout=420)
  put('ROOT211_ORIGINAL_CAD_SCENE_ZERO_PT_RETURNED_ACTUAL.json',result)
  print(json.dumps(dict(passed=result['passed'],returncode=result['returncode'],all_waited=result['all_own_children_waited'],private_EX_released=result['private_EX_released'],error=result['parent_error'],result=result['result'])),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT211_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT211_LOCAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_replay=True));raise
