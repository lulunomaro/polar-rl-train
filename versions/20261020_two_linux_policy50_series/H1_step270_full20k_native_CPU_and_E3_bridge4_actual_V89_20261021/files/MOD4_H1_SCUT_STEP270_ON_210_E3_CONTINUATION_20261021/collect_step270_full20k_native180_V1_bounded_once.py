from pathlib import Path
import hashlib,json,shutil,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';sys.path.insert(0,str(B.parent/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
 return h.hexdigest()
READ=r'''
from pathlib import Path
import hashlib,json,os,psutil,time
B=Path(v['parent']['root']);read=lambda p:json.loads(p.read_bytes()) if p.is_file() else None;assert read(B/'PARENT_IDENTITY.json')['creation']==v['parent']['creation'];until=time.monotonic()+600
def own():
 rows=[]
 for p in psutil.process_iter(['pid','cmdline','create_time','status']):
  try:
   if p.pid!=os.getpid() and p.info['status']!=psutil.STATUS_ZOMBIE and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []):rows.append(p.info)
  except psutil.Error:pass
 return rows
while (not (B/'PARENT_EXIT_ACTUAL.json').exists() or own()) and time.monotonic()<until:time.sleep(1)
live=own();ex=read(B/'PARENT_EXIT_ACTUAL.json');pending=not ex or bool(live);out=dict(epoch=time.time(),pending=pending,parent_complete=read(B/'PARENT_COMPLETE_ACTUAL.json'),parent_exit=ex,actual_own_live=live,texts=[],raw=[])
if not pending:
 assert ex['all_own_children_waited'] and ex['own_eval_lease_released']
 for p in B.rglob('*'):
  if not p.is_file():continue
  if p.suffix in ('.json','.log') and '/job0/' not in str(p):target=out['texts']
  elif p.suffix in ('.npz','.pt') and p.is_relative_to(B/'out'):target=out['raw']
  else:continue
  h=hashlib.sha256()
  with p.open('rb') as f:
   for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
  target.append(dict(path=str(p),relative=p.relative_to(B).as_posix(),bytes=p.stat().st_size,SHA=h.hexdigest()))
print(json.dumps(out))
'''
client=None
try:
 q=json.loads((R/'STEP270_FULL20K_NATIVE180_V1_DETACHED_ACTUAL_STARTED.json').read_bytes());put(R/'STEP270_FULL20K_NATIVE180_V1_COLLECTOR_STARTED.json',dict(epoch=time.time(),parent=q['parent'],max_wait600=True));client=d.t.connect();v=d.code(client,d.t.PY,READ,dict(parent=q['parent']),timeout=660)
 dest=B/'full20k_native180_V1_actual';dest.mkdir();sf=client.open_sftp();sf.get_channel().settimeout(90)
 try:
  for row in v['texts']+v['raw']:
   assert shutil.disk_usage('C:/').free>row['bytes']+8*1024**3
   p=dest/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();sf.get(row['path'],str(p));assert p.stat().st_size==row['bytes'] and sha(p)==row['SHA']
 finally:sf.close()
 v['actual_finite_transport_returned']=True;put(R/'STEP270_FULL20K_NATIVE180_V1_FINITE_RETURNED_ACTUAL.json',v);print(json.dumps(dict(pending=v['pending'],parent_complete=v['parent_complete'],raw_count=len(v['raw']),raw_bytes=sum(x['bytes'] for x in v['raw']))))
except BaseException:put(R/'STEP270_FULL20K_NATIVE180_V1_COLLECTOR_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True));raise
finally:
 if client:client.close()
