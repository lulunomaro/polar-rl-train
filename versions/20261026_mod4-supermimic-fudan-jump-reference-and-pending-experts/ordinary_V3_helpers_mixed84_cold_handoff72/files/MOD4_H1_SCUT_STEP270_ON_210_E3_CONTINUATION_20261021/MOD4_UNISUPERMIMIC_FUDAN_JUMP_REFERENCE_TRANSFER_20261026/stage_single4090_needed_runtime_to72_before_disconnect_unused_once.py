from pathlib import Path
import hashlib,importlib.util,io,json,sys,tarfile,time,traceback
J=Path(__file__).resolve().parent;T=J.parent;W=T.parent;R=J/'reports';N=T/'H1_STEP270_MIXED_FUDAN_SUPERMIMIC_RESOURCE_V84_20261026';P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026'
ROOT='/home/lc01/Zonglin Li/zonglin2/staging/MOD4_SINGLE4090_DISCONNECT_HANDOFF_20261026'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('SINGLE4090_TO72_NEEDED_RUNTIME_HANDOFF_STARTED_ACTUAL.json',dict(epoch=time.time(),human_requested_temporary_single_host_disconnect=True,new84_deployer_not_executed=True,no_owner_GO_or_budget_migration=True))
 files=[];known={}
 for k in ('h1','e2','recovery'):
  base=N/'payloads'/k;m=json.loads((base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
  for row in m['files']:known[str(base/row['relative'])]=row['SHA']
 for p in sorted(N.rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts:files.append((p,'mixed84_source_only/'+p.relative_to(N).as_posix(),known.get(str(p))))
 proof=json.loads((P/'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled']
 for k,row in proof['models'].items():
  f=row['final'];p=Path(f['local_path']);assert p.stat().st_size==f['bytes'];files.append((p,'qualified83B/'+k+'/'+p.name,f['SHA']))
 for name in ('THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json','THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json','THREE_EXPERT_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json'):
  p=P/'reports'/name;files.append((p,'closed83B_receipts/'+name,None))
 rows=[];buffer=io.BytesIO()
 with tarfile.open(fileobj=buffer,mode='w:gz',compresslevel=1) as archive:
  for p,rel,digest in files:
   assert not p.is_symlink() and not rel.startswith('/') and '..' not in Path(rel).parts
   if digest is None:digest=hashlib.sha256(p.read_bytes()).hexdigest()
   rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=digest));archive.add(p,arcname=rel,recursive=False)
 bundle=buffer.getvalue();sha=hashlib.sha256(bundle).hexdigest()
 put('SINGLE4090_TO72_NEEDED_RUNTIME_SOURCE_MANIFEST_ACTUAL.json',dict(epoch=time.time(),files=rows,archive_bytes=len(bundle),archive_SHA=sha,archive_created_in_memory_no_local_weight_duplicate=True,normal_E2_latest_qualified83B_retained=True,no_canonical_ledger_copy=True))
 sp=importlib.util.spec_from_file_location('defs',T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83_20261026/relocate_minimal_closed81O_82Q_NPZ_for83_TLS_V5_unused_once.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);d=m.d
 ms=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');mem=importlib.util.module_from_spec(ms);ms.loader.exec_module(mem);secret=mem.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  ready=d.code(c,d.PY72,"from pathlib import Path;import shutil,json;B=Path(v['root']);assert not B.exists();assert shutil.disk_usage(B.parent.parent).free-v['size']>25*1024**3;B.mkdir(parents=True);print(json.dumps(dict(root=str(B),new_unused=True)))",dict(root=ROOT,size=len(bundle)),timeout=30)
  sf=c.open_sftp()
  try:sf.putfo(io.BytesIO(bundle),ROOT+'/NEEDED_RUNTIME_AND_QUALIFIED_SOURCES.tar.gz',file_size=len(bundle))
  finally:sf.close()
  source="from pathlib import Path;import hashlib,json,tarfile,time;B=Path(v['root']);p=B/'NEEDED_RUNTIME_AND_QUALIFIED_SOURCES.tar.gz';assert p.stat().st_size==v['bytes'];assert hashlib.sha256(p.read_bytes()).hexdigest()==v['SHA'];dest=B/'files';dest.mkdir()\nwith tarfile.open(p,'r:gz') as tf:\n members=tf.getmembers();assert all(x.isfile() and not Path(x.name).is_absolute() and '..' not in Path(x.name).parts for x in members);tf.extractall(dest,filter='data')\nfor row in v['files']:\n q=dest/row['relative'];assert q.resolve().is_relative_to(dest.resolve()) and q.stat().st_size==row['bytes'];assert hashlib.sha256(q.read_bytes()).hexdigest()==row['SHA']\nresult=dict(epoch=time.time(),passed=True,root=str(B),archive=dict(path=str(p),bytes=v['bytes'],SHA=v['SHA']),file_count=len(v['files']),all_transferred_file_bytes_and_fullSHA_verified=True,no_owner_node_Task_GO_model_load_or_budget_writer=True,canonical_not_copied_or_replaced=True);(B/'HANDOFF_COMPLETE_ACTUAL.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))"
  actual=d.code(c,d.PY72,source,dict(root=ROOT,bytes=len(bundle),SHA=sha,files=rows),timeout=180)
  put('SINGLE4090_TO72_NEEDED_RUNTIME_HANDOFF_RETURNED_ACTUAL.json',actual);print(json.dumps(actual))
 except BaseException:
  put('SINGLE4090_TO72_NEEDED_RUNTIME_HANDOFF_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_retry=True));raise
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':main()
