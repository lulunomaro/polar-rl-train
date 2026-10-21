from pathlib import Path
import json,sys,time,traceback,hashlib
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
READ=r'''
from pathlib import Path
import hashlib,json,os,psutil,time
B=Path('/mnt/mod4_linux_durable_20261013/H1step270_native32_2110v4');co=json.loads((B/'PARENT_COMPLETE_ACTUAL.json').read_bytes());ex=json.loads((B/'PARENT_EXIT_ACTUAL.json').read_bytes());assert co['passed'] and co['actual_child_waited'] and co['returncode']==0 and not co['errors'] and ex['all_own_children_waited'] and ex['own_eval_lease_released'];assert not any(p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']));known={x['path']:x for x in co['final']['artifacts']};raw=[]
for p in (B/'out').glob('*.npz'):
 x=known.get(str(p));raw.append(dict(path=str(p),relative=p.relative_to(B).as_posix(),bytes=p.stat().st_size,SHA=x['SHA'] if x else hashlib.sha256(p.read_bytes()).hexdigest()))
sdk=Path('/home/egde/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab');source=[]
for p in (sdk/'cloner').rglob('*.py'):
 text=p.read_text()
 if 'def grid_transforms(' in text:source.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),text=text))
assert source
print(json.dumps(dict(epoch=time.time(),pending=False,parent_complete=co,parent_exit=ex,raw=raw,SDK_grid_source=source,no_new_GPU_or_account_write=True)))
'''
try:
 (R/'STEP270_NATIVE_V4_MISSING_RAW_COLLECTOR_STARTED.json').open('x',encoding='utf8').write(json.dumps(dict(epoch=time.time()),indent=2));c=d.t.connect()
 try:
  v=d.code(c,d.t.PY,READ,{},timeout=45);sf=c.open_sftp()
  try:
   for row in v['raw']:
    p=B/'native32_v4_actual'/row['relative'];assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);sf.get(row['path'],str(p));assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
  finally:sf.close()
 finally:c.close()
 for row in v['SDK_grid_source']:
  p=B/'sdk210_source_snapshot_unmodified'/('cloner_'+Path(row['path']).name);p.open('x',encoding='utf8').write(row.pop('text'));assert hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA'];row['local_path']=str(p)
 v['actual_finite_transport_returned']=True;(R/'STEP270_NATIVE_V4_FULL_RAW_FINITE_RETURNED_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(v,indent=2));print(json.dumps(dict(passed_complete_execution=True,raw_files=len(v['raw']),raw_bytes=sum(x['bytes'] for x in v['raw']),SDK_grid_source_read=True)))
except BaseException:
 (R/'STEP270_NATIVE_V4_MISSING_RAW_COLLECTOR_ORIGINAL_ERROR.json').open('x',encoding='utf8').write(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True),indent=2));raise
