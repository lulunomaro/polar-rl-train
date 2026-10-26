"""Authorized Fudan->SuperMimic reference phase; isolated72 CPU only, no MOD4 rollout or GPU learner."""
from pathlib import Path
import base64,hashlib,importlib.util,json,os,sys,time,traceback,urllib.request
J=Path(__file__).resolve().parent;T=J.parent;W=T.parent;R=J/'reports';read=lambda p:json.loads(Path(p).read_bytes())
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
INIT=r'''
from pathlib import Path
import fcntl,json,os,psutil,shutil,time
B=Path(v['root']);owned=Path('/home/lc01/Zonglin Li/zonglin2/research');assert B.parent==owned and not B.exists() and owned.is_dir() and shutil.disk_usage(owned).free>25*1024**3 and psutil.virtual_memory().available>8*1024**3
roots=[Path(x) for x in v['closed_roots']]
for old in roots:
 e=json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes());t=json.loads((old/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and t['terminal_all_own_children_waited'] and not t['original_error']
assert not any(p.pid!=os.getpid() and any(any(a.startswith(str(root)+'/') for root in roots) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
for p in v['private_locks']:
 with Path(p).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
B.mkdir();print(json.dumps(dict(epoch=time.time(),new_owned_root=str(B),old83B_two_target_nodes_children_actual_out=True,original_private_locks_free=True,free=shutil.disk_usage(owned).free,CPU_only_no_GPU_query_or_budget_write=True)))
'''
VERIFY_SETUP_RUN=r'''
from pathlib import Path
import hashlib,importlib.metadata,json,os,psutil,subprocess,sys,time
B=Path(v['root']);assert B.parent==Path('/home/lc01/Zonglin Li/zonglin2/research');files=[]
for row in v['files']:
 p=B/'vendor/fudan_rl_wheel_leg'/row['path'];raw=p.read_bytes();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA'] and hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['Git_blob_SHA1'];files.append(dict(row,remote_path=str(p),remote_full_SHA_verified=True))
def put(name,value):
 with (B/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
put('PINNED_ASSETS_TWOEND_FULL_SHA_ACTUAL.json',dict(epoch=time.time(),files=files,all_pinned_Git_blob_SHA1_and_twoend_SHA256=True,no_GPU_model_or_MOD4_policy=True))
env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1');venv=B/'.venv_reference_cpu';create=subprocess.run([sys.executable,'-m','venv',str(venv)],capture_output=True,text=True,timeout=60,env=env);put('ISOLATED_VENV_CREATE_ACTUAL.json',dict(returncode=create.returncode,stdout=create.stdout,stderr=create.stderr,base_python=sys.executable));assert create.returncode==0
py=venv/'bin/python';cmd=[str(py),'-m','pip','--disable-pip-version-check','install','--no-input','--index-url','https://pypi.org/simple','numpy==1.26.4','mujoco==3.2.7','onnxruntime==1.20.1'];install=subprocess.run(cmd,capture_output=True,text=True,timeout=300,env=env);put('ISOLATED_CPU_DEPENDENCIES_INSTALL_ACTUAL.json',dict(returncode=install.returncode,stdout=install.stdout,stderr=install.stderr,public_index_only=True,no_original_training_environment_change=True));assert install.returncode==0
driver=B/'fudan_original_jump_headless_CPU_reference_v1.py';assert hashlib.sha256(driver.read_bytes()).hexdigest()==v['driver_SHA'];stdout=B/'FOREIGN_REFERENCE_CPU_STDOUT.log';stderr=B/'FOREIGN_REFERENCE_CPU_STDERR.log'
with stdout.open('xb') as out,stderr.open('xb') as err:
 p=subprocess.Popen([str(py),'-u','-B',str(driver)],cwd=B,env=env,stdout=out,stderr=err);identity=dict(pid=p.pid,creation=psutil.Process(p.pid).create_time(),argv=psutil.Process(p.pid).cmdline(),root=str(B));put('FOREIGN_REFERENCE_CPU_STARTED_ACTUAL.json',identity);returncode=p.wait(timeout=650)
try:alive=psutil.Process(identity['pid']).create_time()==identity['creation']
except psutil.NoSuchProcess:alive=False
assert not alive;put('FOREIGN_REFERENCE_CPU_EXIT_ACTUAL.json',dict(epoch=time.time(),returncode=returncode,identity=identity,own_actual_child_waited=True,not_MOD4_training_or_native_FINAL=True))
texts=[];artifacts=[]
for p in B.rglob('*'):
 if not p.is_file() or '.venv_reference_cpu' in p.parts or 'vendor' in p.parts:continue
 if p.suffix in ('.json','.log','.py','.txt'):texts.append(dict(path=str(p),relative=p.relative_to(B).as_posix(),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
 elif p.suffix=='.npz':artifacts.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),original_reference_CPU_only=True))
print(json.dumps(dict(epoch=time.time(),root=str(B),all_assets_twoend_verified=True,reference_returncode=returncode,own_reference_child_actual_out=True,texts=texts,small_artifacts=artifacts,no_GPU_MOD4_policy_worldmodel_optimizer_or_budget_action=True)))
'''
def main():
 plan=read(R/'PINNED_FOREIGN_REFERENCE_ASSET_DOWNLOAD_PLAN_SOURCE_ONLY_ACTUAL.json');N=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026';proof=read(N/'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');q=read(N/'reports/THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json');assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled'] and proof['remaining_actual_snapshot']>86412.86069250107
 put('PINNED_FUDAN_CPU_REFERENCE_FINITE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,new_human_all_unfinished_experts_SuperMimic_authority=True,original83B_closing=proof['remaining_actual_snapshot'],planned_files=plan['files'],CPU_only_no_native_training_GO=True))
 sp=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(sp);sp.loader.exec_module(memory);secret=memory.recover();c=None;transferred=[]
 try:
  c=d.connect72(secret);secret=None;remote=plan['remote_root'];put('FUDAN_CPU_REFERENCE_72_FRESH_OWNED_ROOT_AND_ORIGINAL83B_OUT_ACTUAL.json',d.code(c,d.PY72,INIT,dict(root=remote,closed_roots=[q['roots'][x] for x in ('e2','recovery')],private_locks=[q['specs'][x]['private_lock'] for x in ('e2','recovery')]),timeout=60))
  sf=c.open_sftp();sf.get_channel().settimeout(60)
  try:
   sf.put(str(J/'fudan_original_jump_headless_CPU_reference_v1.py'),remote+'/fudan_original_jump_headless_CPU_reference_v1.py')
   for row in plan['files']:
    url='https://api.github.com/repos/yly-true/fudan_rl_wheel_leg/git/blobs/'+row['Git_blob_SHA1'];request=urllib.request.Request(url,headers={'User-Agent':'MOD4-pinned-reference-research','Accept':'application/vnd.github+json'});started=time.time()
    with urllib.request.urlopen(request,timeout=45) as response:blob=json.loads(response.read())
    raw=base64.b64decode(blob['content']);assert blob['sha']==row['Git_blob_SHA1'] and len(raw)==row['bytes'] and hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['Git_blob_SHA1'];digest=hashlib.sha256(raw).hexdigest();target=remote+'/vendor/fudan_rl_wheel_leg/'+row['path'];parts=target.split('/');current='/'
    for part in parts[1:-1]:
     current=current.rstrip('/')+'/'+part
     try:sf.stat(current)
     except FileNotFoundError:
      assert current.startswith(remote+'/');sf.mkdir(current)
    with sf.open(target+'.partial','wx') as out:out.write(raw);out.flush()
    sf.rename(target+'.partial',target);raw=None;transferred.append(dict(row,SHA=digest,path=row['path'],remote_path=target,elapsed_download_and_transfer_s=time.time()-started));put('PINNED_PUBLIC_ASSET_'+str(len(transferred)).zfill(2)+'_TRANSFERRED_ACTUAL.json',transferred[-1])
  finally:sf.close()
  result=d.code(c,d.PY72,VERIFY_SETUP_RUN,dict(root=remote,files=transferred,driver_SHA=hashlib.sha256((J/'fudan_original_jump_headless_CPU_reference_v1.py').read_bytes()).hexdigest()),timeout=1150);put('FUDAN_ORIGINAL_JUMP_CPU_REFERENCE_REMOTE_RESULT_ACTUAL.json',result)
  sf=c.open_sftp();local=J/'actual_72_reference_text';local.mkdir()
  try:
   for row in result['texts']:
    path=local/row['relative'];path.parent.mkdir(parents=True,exist_ok=True);sf.get(row['path'],str(path));assert path.stat().st_size==row['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest()==row['SHA']
  finally:sf.close()
  put('FUDAN_ORIGINAL_JUMP_CPU_REFERENCE_FINITE_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_returned=True,own_reference_child_actual_out=result['own_reference_child_actual_out'],reference_returncode=result['reference_returncode'],texts_collected=len(result['texts']),small_artifacts_producer=result['small_artifacts'],assets=transferred,CPU_foreign_reference_not_our_skill_or_native_training=True,no_native_or_our_model_promotion=True))
  print(json.dumps(dict(returned=True,reference_returncode=result['reference_returncode'],assets=len(transferred),small_reference_artifacts=len(result['small_artifacts']),no_GPU_training=True)))
 except BaseException:
  put('FUDAN_REFERENCE_CPU_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),transferred=transferred,no_same_once_rerun=True,own_remote_reference_out_only_if_exit_receipt=True));raise
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':main()
