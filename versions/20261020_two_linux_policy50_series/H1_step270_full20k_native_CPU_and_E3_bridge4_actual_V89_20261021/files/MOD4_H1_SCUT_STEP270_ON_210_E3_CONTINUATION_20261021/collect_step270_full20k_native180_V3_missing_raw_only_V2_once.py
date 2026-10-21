from pathlib import Path
import hashlib,json,shutil,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';A=B/'full20k_native180_V3_actual';sys.path.insert(0,str(B.parent/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def H(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
 return h.hexdigest()
READ=r'''
from pathlib import Path
import hashlib,json,os,psutil,shutil,time
B=Path(v['root']);ex=json.loads((B/'PARENT_EXIT_ACTUAL.json').read_bytes());co=json.loads((B/'PARENT_COMPLETE_ACTUAL.json').read_bytes());assert ex['all_own_children_waited'] and ex['own_eval_lease_released'] and co['passed']
assert not any(p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
rows=[]
for p in (B/'out').rglob('*'):
 if not p.is_file() or p.suffix not in ('.pt','.npz'):continue
 rel=p.relative_to(B).as_posix();st=p.stat()
 if rel in v['existing']:
  assert st.st_size==v['existing'][rel];rows.append(dict(path=str(p),relative=rel,bytes=st.st_size,SHA=None,existing_complete_local_not_rehashed_or_downloaded=True));continue
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
 rows.append(dict(path=str(p),relative=rel,bytes=st.st_size,SHA=h.hexdigest(),existing_complete_local_not_rehashed_or_downloaded=False))
print(json.dumps(dict(epoch=time.time(),parent_complete=co,parent_exit=ex,raw=rows,all_own_out=True,source_disk_free=shutil.disk_usage(B).free)))
'''
c=None;copied=[]
try:
 assert (R/'STEP270_FULL20K_NATIVE180_V3_COLLECTOR_ORIGINAL_ERROR.json').is_file()
 ex=json.loads((A/'PARENT_EXIT_ACTUAL.json').read_bytes());co=json.loads((A/'PARENT_COMPLETE_ACTUAL.json').read_bytes());assert ex['all_own_children_waited'] and co['passed']
 existing={p.relative_to(A).as_posix():p.stat().st_size for p in (A/'out').rglob('*') if p.is_file() and p.suffix in ('.npz','.pt')}
 final=co['final'];known={x['relative']:x for x in final['artifacts']};missing=[x for x in final['artifacts'] if x['relative'] not in existing];assert shutil.disk_usage('C:/').free>sum(x['bytes'] for x in missing)+8*1024**3+16*1024**2
 put(R/'STEP270_FULL20K_NATIVE180_V3_MISSING_RAW_V2_STARTED.json',dict(epoch=time.time(),existing_complete_local=existing,estimated_missing_bytes=sum(x['bytes'] for x in missing),initial_collector_error_retained=True))
 q=json.loads((R/'STEP270_FULL20K_NATIVE180_V3_DETACHED_ACTUAL_STARTED.json').read_bytes());c=d.t.connect();v=d.code(c,d.t.PY,READ,dict(root=q['parent']['root'],existing=existing),timeout=180);put(R/'STEP270_FULL20K_NATIVE180_V3_MISSING_RAW_V2_FRESH_MANIFEST.json',v)
 sf=c.open_sftp();sf.get_channel().settimeout(90)
 try:
  for row in v['raw']:
   if row['existing_complete_local_not_rehashed_or_downloaded']:continue
   assert shutil.disk_usage('C:/').free>row['bytes']+8*1024**3
   p=A/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();sf.get(row['path'],str(p));assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'];copied.append(row)
 finally:sf.close()
 for row in v['raw']:
  if row['relative'] in known:row['SHA']=known[row['relative']]['SHA']
  row['local_path']=str(A/row['relative'])
 v.update(actual_finite_transport_returned=True,pending=False,texts_original_first_collector_retained=True,only_missing_raw_downloaded=True,newly_downloaded=copied,C_free_after=shutil.disk_usage('C:/').free)
 put(R/'STEP270_FULL20K_NATIVE180_V3_COMPLETE_RAW_AND_EXIT_RECOVERED_V2_ACTUAL.json',v);print(json.dumps(dict(passed_execution=co['passed'],raw_count=len(v['raw']),raw_bytes=sum(x['bytes'] for x in v['raw']),new_downloads=len(copied),all_old_complete_local_paths_not_redownloaded=True,C_free=v['C_free_after'])))
except BaseException:put(R/'STEP270_FULL20K_NATIVE180_V3_MISSING_RAW_V2_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),new_completed_prefix=copied,no_replay=True));raise
finally:
 if c:c.close()
