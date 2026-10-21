from pathlib import Path
import importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';N=B.parent/'MOD4_TWO_LINUX_POLICY50_COHORT_50_20261021';sys.path.insert(0,str(N));import deploy_two50_reconciled_original_writer_once as d
s=importlib.util.spec_from_file_location('memory',B/'run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(s);s.loader.exec_module(memory)
READ=r'''
from pathlib import Path
import hashlib,json,os,psutil,time
B=Path(v['root']);read=lambda p:json.loads(p.read_bytes()) if p.is_file() else None;until=time.monotonic()+65
def own():
 out=[]
 for p in psutil.process_iter(['pid','cmdline','create_time','status']):
  try:
   if p.pid!=os.getpid() and p.info['status']!=psutil.STATUS_ZOMBIE and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []):out.append(p.info)
  except psutil.Error:pass
 return out
while (not (B/'PARENT_EXIT_ACTUAL.json').exists() or own()) and time.monotonic()<until:time.sleep(1)
live=own();ex=read(B/'PARENT_EXIT_ACTUAL.json');co=read(B/'PARENT_COMPLETE_ACTUAL.json');pending=not ex or bool(live);out=dict(epoch=time.time(),root=str(B),pending=pending,own_actual_live=live,parent_exit=ex,parent_complete=co,parent_error=read(B/'PARENT_ORIGINAL_ERROR.json'),texts=[],raw=[],no_GPU_account_or_training_mutation=True)
if not pending:
 assert ex['all_own_children_waited'] and ex['own_eval_lease_released']
 for p in B.rglob('*'):
  if p.is_file() and (p.suffix in ('.json','.log')) and '/job0/' not in str(p):out['texts'].append(dict(path=str(p),relative=p.relative_to(B).as_posix(),bytes=p.stat().st_size))
 for p in (B/'out').glob('*.npz'):out['raw'].append(dict(path=str(p),relative=p.relative_to(B).as_posix(),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
print(json.dumps(out))
'''
try:
 started=json.loads((R/'SHARED_H1_FULL13_DETACHED_ACTUAL_STARTED.json').read_bytes());root=started['parent']['root']
 with (R/'SHARED_H1_FULL13_COLLECTOR_STARTED.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),bound_parent=started['parent'],no_replay=True),f)
 secret=memory.recover();c=d.connect72(secret);secret=None
 try:
  v=d.code(c,d.PY72,READ,dict(root=root),timeout=90);local=B/'shared_H1_full13_V4_actual';local.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(90)
  try:
   for row in v['texts']+v['raw']:
    p=local/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();sf.get(row['path'],str(p));assert p.stat().st_size==row['bytes']
    if row.get('SHA'):assert __import__('hashlib').sha256(p.read_bytes()).hexdigest()==row['SHA']
  finally:sf.close()
 finally:c.close()
 v['actual_finite_transport_returned']=True
 with (R/'SHARED_H1_FULL13_EXISTING_FINITE_RETURNED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(actual_returned=True,pending=v['pending'],parent_complete=v['parent_complete'])))
except BaseException:
 with (R/'SHARED_H1_FULL13_COLLECTOR_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_replay=True),f)
 raise
