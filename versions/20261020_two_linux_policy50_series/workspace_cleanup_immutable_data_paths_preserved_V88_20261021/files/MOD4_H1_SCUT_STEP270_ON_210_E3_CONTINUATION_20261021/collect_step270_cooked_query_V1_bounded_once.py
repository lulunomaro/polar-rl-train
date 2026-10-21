from pathlib import Path
import json,sys,time,traceback,hashlib
B=Path(__file__).resolve().parent;R=B/'reports';sys.path.insert(0,str(B.parent/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
READ=r'''
from pathlib import Path
import hashlib,json,os,psutil,time
B=Path(v['parent']['root']);read=lambda p:json.loads(p.read_bytes()) if p.is_file() else None;assert read(B/'PARENT_IDENTITY.json')['creation']==v['parent']['creation'];until=time.monotonic()+65
def own():
 rows=[]
 for p in psutil.process_iter(['pid','cmdline','create_time','status']):
  try:
   if p.pid!=os.getpid() and p.info['status']!=psutil.STATUS_ZOMBIE and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []):rows.append(p.info)
  except psutil.Error:pass
 return rows
while (not (B/'PARENT_EXIT_ACTUAL.json').exists() or own()) and time.monotonic()<until:time.sleep(1)
live=own();ex=read(B/'PARENT_EXIT_ACTUAL.json');pending=not ex or bool(live);out=dict(epoch=time.time(),pending=pending,parent_complete=read(B/'PARENT_COMPLETE_ACTUAL.json'),parent_exit=ex,actual_own_live=live,texts=[],actual_result=read(B/'out/ACTUAL_COOKED_VS_AUTHORED_STEP270_QUERY_RESULT.json'))
if not pending:
 assert ex['all_own_children_waited'] and ex['own_eval_lease_released']
 for p in B.rglob('*'):
  if p.is_file() and p.suffix in ('.json','.log') and '/job0/' not in str(p):out['texts'].append(dict(path=str(p),relative=p.relative_to(B).as_posix(),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
print(json.dumps(out))
'''
try:
 q=json.loads((R/'STEP270_COOKED_QUERY_V1_DETACHED_ACTUAL_STARTED.json').read_bytes());(R/'STEP270_COOKED_QUERY_V1_COLLECTOR_STARTED.json').open('x',encoding='utf8').write(json.dumps(dict(epoch=time.time()),indent=2));c=d.t.connect()
 try:
  v=d.code(c,d.t.PY,READ,dict(parent=q['parent']),timeout=90);sf=c.open_sftp();dest=B/'cooked_query_V1_actual';dest.mkdir()
  try:
   for row in v['texts']:
    p=dest/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();sf.get(row['path'],str(p));assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
  finally:sf.close()
 finally:c.close()
 v['actual_finite_transport_returned']=True;(R/'STEP270_COOKED_QUERY_V1_FINITE_RETURNED_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(v,indent=2));print(json.dumps(dict(pending=v['pending'],parent_complete=v['parent_complete'],result_summary={k:x for k,x in (v['actual_result'] or {}).items() if k not in ('all_rows','front_rows')})))
except BaseException:
 (R/'STEP270_COOKED_QUERY_V1_COLLECTOR_ORIGINAL_ERROR.json').open('x',encoding='utf8').write(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True),indent=2));raise
