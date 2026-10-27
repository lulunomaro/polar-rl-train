from pathlib import Path
import sys,json,time,hashlib,importlib.util,traceback,shlex
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;R=S/'reports';N=T/'MOD4_H1_FLAT05_MASK_AWARE_MIXED72_RESOURCE_V91_20261027'
ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT91_FROZEN_WM_DIAG_20261028r1'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)

PRE=r'''from pathlib import Path
import json,shutil,hashlib
root=Path(v['root']);base=Path(v['old']);assert not root.exists() and root.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks'))
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['remaining_training_seconds']>86412.86069250107
if c['active_segment'] is not None:assert set(c['active_segment']['experts'])=={'w35'} and c['active_segment']['owner_parent_pid']==v['owner']['pid']
root.mkdir();(root/'code').mkdir();dest=root/'runtime';dest.mkdir();m=json.loads((base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
assert hashlib.sha256((base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==v['manifest_SHA']
count=0
for row in m['files']:
 rel=row['relative'];src=base/rel;d=dest/rel;assert d.resolve().is_relative_to(dest.resolve())
 if d.suffix.lower() in ('.pt','.pth','.npz'):continue
 assert not src.is_symlink() and src.is_file() and src.stat().st_size==row['bytes']
 d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,d);count+=1
shutil.copy2(base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
assert shutil.disk_usage(root).free>25*1024**3
print(json.dumps(dict(passed=True,readonly_runtime_files_copied=count,no_old_models_raw_copied=True,no_budget_or_training_state_write=True,active_W35_allowed=c['active_segment'] is not None)))'''

RUN=r'''from pathlib import Path
import os,json,subprocess,time,psutil,hashlib
root=Path(v['root']);script=root/'code/run_native91_frozen_flat_WM_N1_once.py';log=root/'EVAL_PROCESS.log';args=['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(script),'--binding',str(root/'EVAL_BINDING.json')]
e=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1')
p=subprocess.Popen(args,cwd=root,env=e,stdout=log.open('xb'),stderr=subprocess.STDOUT,close_fds=True)
loader='/home/lc01/Zonglin Li/zonglin2/compat/glibc240/ld-linux-x86-64.so.2';lib='/home/lc01/Zonglin Li/zonglin2/compat/glibc240:/home/lc01/Zonglin Li/zonglin2/envs/mod4/lib';py='/home/lc01/Zonglin Li/zonglin2/envs/mod4/bin/python'
expected=[loader,'--library-path',lib,py,'-B','-u','-B',str(script),'--binding',str(root/'EVAL_BINDING.json')];deadline=time.monotonic()+10;identity=None;previous=None
while True:
 assert p.poll() is None,'owned N1 helper exited before identity admission'
 q=psutil.Process(p.pid);row=dict(pid=p.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),root=q.cwd())
 if row['exe']==loader and row['argv']==expected and row['root']=='/home/lc01/Zonglin Li/zonglin2':
  if row==previous:identity=row;break
  previous=row
 assert time.monotonic()<deadline,dict(expected=expected,actual=row);time.sleep(.05)
rc=p.wait(timeout=300);done=root/'case/FROZEN_DIAGNOSTIC_FUNCTION_RETURNED_ACTUAL.json';errors=[dict(path=str(x),text=x.read_text(errors='replace')) for x in (root/'case').glob('*ERROR*.json')]
rows=[]
for f in root.rglob('*'):
 if f.is_file() and f.suffix.lower() in ('.json','.jsonl','.log'):
  a=f.stat()
  with f.open('rb') as q:SHA=hashlib.file_digest(q,'sha256').hexdigest()
  b=f.stat();assert (a.st_size,a.st_mtime_ns)==(b.st_size,b.st_mtime_ns)
  rows.append(dict(relative=f.relative_to(root).as_posix(),path=str(f),bytes=a.st_size,SHA=SHA))
value=dict(actual_finite_returned=True,actual_waited_exit=rc,owned_identity=identity,actual_case_returned=done.is_file(),case= json.loads(done.read_bytes()) if done.is_file() else None,errors=errors,files=rows,no_learning_or_account_writer=True,one_fixed_case_only=True)
print(json.dumps(value))'''

def main():
 put('FROZEN91_NEW_PURPOSE_ENTERED_ACTUAL.json',dict(epoch=time.time(),one_seed=20260928,no_retry=True,source='qualified91 formal',frozen_Pi_and_WM_new_purpose_load=True,no_learner_optimizer_or_learning_GO=True))
 cpu=N/'reports/NATIVE91_FORMAL_NATIVE_FULLSTATE_INITIAL_CPU_AND_COST_ACTUAL.json';qual=json.loads(cpu.read_bytes());assert qual['passed']
 closed=json.loads((N/'reports/NATIVE91_COMPLETE_FINAL_OR_PARTIAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());assert closed['canonical_None'] and closed['original_owner_private_shared_locks_free']
 launched=json.loads((T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_fixed92_single72_owner_source_v2/reports/W35_FIXED92_OWNER_NODE_LAUNCHED_ACTUAL.json').read_bytes())
 prep=json.loads((N/'reports/NATIVE91_SOURCE_PREPARED_ACTUAL.json').read_bytes());old='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_MASK_AWARE_2610v91/h1'
 q=dict(eval_root=ROOT,source_job_root=ROOT+'/runtime',qualified_training_job_root=old,source_model=qual['model'],fixed_seed=20260928,max_controls=500,max_callbacks=2000,qualification_SHA=H(cpu),allowed_active_W35_owner=launched['owner'],runtime_manifest_SHA=prep['manifest_SHA'],eval_code_SHAs={p.name:H(p) for p in (S/'code').glob('*.py')})
 (S/'EVAL_BINDING.json').write_text(json.dumps(q,indent=2),encoding='utf8')
 helper=T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v253.py';sp=importlib.util.spec_from_file_location('known_zstd_memory_transport_for_new91_frozen_diag',helper);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);transport,previous=m.install()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('frozen91_secret_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec);secret=sec.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  put('FROZEN91_NEW_RUNTIME_COPY_AND_ACTIVE_AUTHORITY_ADMITTED_ACTUAL.json',d.code(c,d.PY72,PRE,dict(root=ROOT,old=old,owner=launched['owner'],manifest_SHA=prep['manifest_SHA']),timeout=90))
  sf=c.open_sftp();sf.get_channel().settimeout(90)
  try:
   for p in (S/'code').glob('*.py'):sf.put(str(p),ROOT+'/code/'+p.name)
   sf.put(str(S/'EVAL_BINDING.json'),ROOT+'/EVAL_BINDING.json');sf.put(str(cpu),ROOT+'/source_qualified91_CPU.json')
  finally:sf.close()
  result=d.code(c,d.PY72,RUN,dict(root=ROOT),timeout=330);put('FROZEN91_SINGLE_CASE_AND_WM_DIAGNOSTIC_RETURNED_ACTUAL.json',result)
  target=S/'actual_case_text';target.mkdir();rows=[]
  sf=c.open_sftp();sf.get_channel().settimeout(90)
  try:
   for row in result['files']:
    name=hashlib.sha256(row['relative'].encode()).hexdigest()[:20]+'_'+Path(row['relative']).name;p=target/name;sf.get(row['path'],str(p));assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'];rows.append(dict(**row,local_path=str(p)))
  finally:sf.close()
  put('FROZEN91_CASE_FULL_TEXT_AND_NEW_RAW_TRANSFER_ACTUAL.json',dict(passed=True,rows=rows,new_case_only_no_old_raw=True))
  assert result['actual_case_returned'] and not result['errors'] and result['case']['passed'],result['errors']
  print(json.dumps(dict(actual_frozen_case_passed=True,controls=result['case']['result']['controls'],flat=result['case']['result']['flat_real_physics_events']['lifetime'],no_skill_graduation_or_learning=True)))
 finally:
  secret=None
  if c:c.close()
  transport.SESSION=previous

if __name__=='__main__':
 try:main()
 except BaseException:put('FROZEN91_NEW_PURPOSE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_retry_or_account_mutation=True));raise
