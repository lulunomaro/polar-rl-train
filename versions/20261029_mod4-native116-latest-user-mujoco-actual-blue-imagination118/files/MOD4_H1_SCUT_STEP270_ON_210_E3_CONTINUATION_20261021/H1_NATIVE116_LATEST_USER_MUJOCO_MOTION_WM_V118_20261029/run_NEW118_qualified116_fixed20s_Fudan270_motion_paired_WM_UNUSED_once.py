from pathlib import Path
import sys,json,time,hashlib,importlib.util,traceback,shlex
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;R=S/'reports';N=T/'MOD4_H1_FUDAN270_DIRECT_COMMAND_RESOURCE_V116_20261029'
ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_NATIVE116_FUDAN270_FROZEN_MOTION_WM_DIAG_20261029v112'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)

PRE=r'''from pathlib import Path
import json,shutil,hashlib,os
root=Path(v['root']);base=Path(v['old']);assert not root.exists() and root.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks'))
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['remaining_training_seconds']>86412.86069250107
assert c['active_segment'] is None, 'NEW118 only after actual111 closed/no new learning owner'
root.mkdir();(root/'code').mkdir();dest=root/'runtime';dest.mkdir();m=json.loads((base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
assert hashlib.sha256((base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==v['manifest_SHA']
count=0
for row in m['files']:
 rel=row['relative'];src=base/rel;d=dest/rel;assert d.resolve().is_relative_to(dest.resolve())
 if d.suffix.lower() in ('.pt','.pth'):continue
 if d.suffix.lower()=='.npz':
  d.parent.mkdir(parents=True,exist_ok=True);os.link(src,d);assert os.path.samestat(src.stat(),d.stat());continue
 assert not src.is_symlink() and src.is_file() and src.stat().st_size==row['bytes']
 d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,d);count+=1
shutil.copy2(base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
assert shutil.disk_usage(root).free>25*1024**3
print(json.dumps(dict(passed=True,readonly_runtime_files_copied=count,no_old_models_raw_copied=True,no_budget_or_training_state_write=True,canonical_None=c['active_segment'] is None)))'''

RUN=r'''from pathlib import Path
import os,json,subprocess,time,psutil,hashlib
root=Path(v['root']);script=root/'code/run_native118_frozen_flat_WM_N1_once.py';log=root/'EVAL_PROCESS.log';args=['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(script),'--binding',str(root/'EVAL_BINDING.json')]
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
rc=p.wait(timeout=780);done=root/'case/FROZEN_DIAGNOSTIC_FUNCTION_RETURNED_ACTUAL.json';errors=[dict(path=str(x),text=x.read_text(errors='replace')) for x in (root/'case').glob('*ERROR*.json')]
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
 put('FROZEN118_NEW_PURPOSE_ENTERED_ACTUAL.json',dict(epoch=time.time(),one_seed=20260928,no_retry=True,source='qualified116 formal',frozen_Pi_and_WM_new_purpose_load=True,no_learner_optimizer_or_learning_GO=True))
 L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
 cpu=L/'TWO116_DIRECT_COMMAND_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1/reports/NATIVE116_seed27_NEW_FORMAL_INITIAL_WHOLE_CPU_QUALIFIED_ACTUAL.json';qual=json.loads(cpu.read_bytes());assert qual['passed']
 closed=json.loads((L/'TWO116_DIRECT_COMMAND_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1/reports/TWO116_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_V2_ACTUAL.json').read_bytes());assert closed['canonical_None'] and closed['original_private_shared_writer_locks_free'] and closed['all_two_original_owner_nodes_workers_out']
 prep=dict(payload_manifest_SHA=H(N/'payloads/seed27/THREE_SLOT_COMPLETE_MANIFEST_V1.json'));old='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_DIRECT_COMMAND_2610v116/seed27'
 q=dict(eval_root=ROOT,source_job_root=ROOT+'/runtime',qualified_training_job_root=old,source_model=qual['model'],fixed_seed=20260928,max_controls=2000,max_callbacks=8000,qualification_SHA=H(cpu),runtime_manifest_SHA=prep['payload_manifest_SHA'],resource_policy=dict(schema='mod4.user_allowed_light_compute.20261029.v1',free_MiB_strictly_above=15669,utilization_percent_max=30,compute_UUID_rows_allowed=True,other_processes_untouched=True),eval_code_SHAs={p.name:H(p) for p in (S/'code').glob('*.py')})
 (S/'EVAL_BINDING.json').write_text(json.dumps(q,indent=2),encoding='utf8')
 helper=T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py';sp=importlib.util.spec_from_file_location('known_zstd_memory_transport_for_new105_frozen_diag',helper);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);transport,previous=m.install()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('frozen105_secret_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec);secret=sec.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  put('FROZEN118_NEW_RUNTIME_COPY_AND_ACTIVE_AUTHORITY_ADMITTED_ACTUAL.json',d.code(c,d.PY72,PRE,dict(root=ROOT,old=old,manifest_SHA=prep['payload_manifest_SHA']),timeout=90))
  sf=c.open_sftp();sf.get_channel().settimeout(90)
  try:
   for p in (S/'code').glob('*.py'):sf.put(str(p),ROOT+'/code/'+p.name)
   sf.put(str(S/'EVAL_BINDING.json'),ROOT+'/EVAL_BINDING.json');sf.put(str(cpu),ROOT+'/source_qualified116_CPU.json')
  finally:sf.close()
  result=d.code(c,d.PY72,RUN,dict(root=ROOT),timeout=810);put('FROZEN118_SINGLE_CASE_AND_WM_DIAGNOSTIC_RETURNED_ACTUAL.json',result)
  target=S/'actual_case_text';target.mkdir();rows=[]
  sf=c.open_sftp();sf.get_channel().settimeout(90)
  try:
   for row in result['files']:
    name=hashlib.sha256(row['relative'].encode()).hexdigest()[:20]+'_'+Path(row['relative']).name;p=target/name;sf.get(row['path'],str(p));assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'];rows.append(dict(**row,local_path=str(p)))
  finally:sf.close()
  put('FROZEN118_CASE_FULL_TEXT_AND_NEW_RAW_TRANSFER_ACTUAL.json',dict(passed=True,rows=rows,new_case_only_no_old_raw=True))
  assert result['actual_case_returned'] and not result['errors'] and result['case']['passed'],result['errors']
  print(json.dumps(dict(actual_frozen_case_passed=True,controls=result['case']['result']['controls'],original270=result['case']['result']['original270_terminal_physics_events'],no_skill_graduation_or_learning=True)))
 finally:
  secret=None
  if c:c.close()
  transport.SESSION=previous

if __name__=='__main__':
 try:main()
 except BaseException:put('FROZEN118_NEW_PURPOSE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_retry_or_account_mutation=True));raise
