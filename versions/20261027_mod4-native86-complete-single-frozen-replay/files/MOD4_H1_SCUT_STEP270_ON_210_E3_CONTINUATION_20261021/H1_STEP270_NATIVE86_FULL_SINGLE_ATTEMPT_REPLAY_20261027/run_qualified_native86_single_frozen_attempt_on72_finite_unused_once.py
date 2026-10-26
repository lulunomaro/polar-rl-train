from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;R=S/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
PREP="""from pathlib import Path
import json,shutil,psutil,time
q=v['q'];root=Path(q['remote_root']);owned=Path('/home/lc01/Zonglin Li/zonglin2/tasks')
assert root.resolve().is_relative_to(owned.resolve()) and not root.exists()
c=json.loads(Path(q['canonical']).read_bytes());assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'
assert psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
assert json.loads((Path(q['source_root'])/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited']
assert json.loads((Path(q['old_owner_root'])/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled']
root.mkdir();print(json.dumps(dict(epoch=time.time(),new_unused_root=str(root),source86_closed_native=True,canonical_None=True,no_budget_write=True)))
"""
RUN="""from pathlib import Path
import os,psutil,subprocess,time,json,hashlib
q=v['q'];root=Path(q['remote_root'])
for name,digest in v['files'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest
env=dict(os.environ);env['CUDA_VISIBLE_DEVICES']=q['GPU_UUID'];env['CUDA_DEVICE_ORDER']='PCI_BUS_ID'
started=time.time()
with (root/'OWN_STDOUT.log').open('xb') as out,(root/'OWN_STDERR.log').open('xb') as err:
 child=subprocess.Popen([v['py'],'-u','-B',str(root/'native86_frozen_single_sdk_entry_v1.py')],cwd=str(root),env=env,stdout=out,stderr=err,start_new_session=True,close_fds=True)
 try:
  p=psutil.Process(child.pid);identity=dict(pid=p.pid,creation=p.create_time(),argv=p.cmdline(),exe=p.exe())
 except psutil.NoSuchProcess:identity=dict(pid=child.pid,original_exit_before_identity=True)
 (root/'OWN_FROZEN_REPLAY_CHILD_STARTED.json').write_text(json.dumps(dict(epoch=started,identity=identity,one_attempt=True,no_learning=True)),encoding='utf8')
 rc=child.wait(timeout=600)
assert not any(any(a.startswith(str(root)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']) if p.pid!=os.getpid())
files=[]
for p in root.rglob('*'):
 if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix in ('.py','.json','.jsonl','.log') and 'home' not in p.relative_to(root).parts and 'tmp' not in p.relative_to(root).parts:
  raw=p.read_bytes();files.append(dict(path=str(p),relative=p.relative_to(root).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
result=dict(epoch=time.time(),returncode=rc,child_identity=identity,all_own_child_processes_actual_out=True,remote_root=str(root),files=files,evaluation_wall_seconds=time.time()-started,no_training_or_budget_write=True)
for name,key in [('FROZEN_REPLAY_FUNCTION_RETURNED_ACTUAL.json','result'),('FROZEN_NATIVE_REPLAY_ORIGINAL_ERROR.json','original_error'),('ACTUAL_SINGLE_N1_SDK_AND_REFERENCE_ADMISSION.json','actual_SDK_admission')]:
 if (root/name).is_file():result[key]=json.loads((root/name).read_bytes())
print(json.dumps(result))
"""
def main():
 q=json.loads((S/'BINDING.json').read_bytes());assert q['one_frozen_native_policy_attempt_only'] and q['no_budget_write']
 files={n:H(S/n) for n in ('BINDING.json','driver.py','native86_frozen_single_sdk_entry_v1.py')}
 assert files['driver.py']==q['driver_SHA'] and files['native86_frozen_single_sdk_entry_v1.py']==q['entry_SHA']
 put('FROZEN_NATIVE86_SINGLE_REPLAY_FINITE_STARTED_ACTUAL.json',dict(epoch=time.time(),source=q['model'],no_learning=True,one_attempt=True,source_admission_not_yet_actual_N1=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('replay72_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(sp);sp.loader.exec_module(memory)
 secret=memory.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  pre=d.code(c,d.PY72,PREP,dict(q=q),timeout=45);put('NATIVE86_REPLAY_NEW_ROOT_PREFLIGHT_ACTUAL.json',pre)
  sf=c.open_sftp();sf.get_channel().settimeout(90)
  try:
   for name in files:sf.put(str(S/name),q['remote_root']+'/'+name)
  finally:sf.close()
  receipt=d.code(c,d.PY72,RUN,dict(q=q,files=files,py=d.PY72),timeout=650)
  put('FROZEN_NATIVE86_SINGLE_REPLAY_ORIGINAL_REMOTE_RECEIPT_ACTUAL.json',receipt)
  sf=c.open_sftp();sf.get_channel().settimeout(90);local=[]
  try:
   for row in receipt['files']:
    rel=Path(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts
    p=S/'actual_72'/rel;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();sf.get(row['path'],str(p))
    assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'];local.append(dict(row,local_path=str(p),twohost_SHA_verified=True))
  finally:sf.close()
  result=dict(epoch=time.time(),actual_finite_returned=True,source=q['model'],returncode=receipt['returncode'],
   actual_original_SDK_admission=receipt.get('actual_SDK_admission'),actual_result=receipt.get('result'),original_error=receipt.get('original_error'),
   all_own_children_actual_out=receipt['all_own_child_processes_actual_out'],files=local,evaluation_wall_seconds=receipt['evaluation_wall_seconds'],no_training_or_budget_write=True)
  put('FROZEN_NATIVE86_SINGLE_COMPLETE_ATTEMPT_RETURNED_ACTUAL.json',result)
  print(json.dumps(dict(actual_finite_returned=True,returncode=result['returncode'],SDK_admitted=bool(result['actual_original_SDK_admission']),status=(result['actual_result'] or {}).get('result'),original_error=result['original_error'])))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('FROZEN_NATIVE86_REPLAY_FINITE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_same_root_or_once_retry=True,no_training_or_budget_write=True));raise
