from pathlib import Path
import hashlib,importlib.util,io,json,tarfile,time,traceback
J=Path(__file__).resolve().parent;T=J.parent;W=T.parent;R=J/'reports';B=J/'agent_next_E2_supermimic_cpu';ROOT='/home/lc01/Zonglin Li/zonglin2/staging/MOD4_SINGLE4090_DISCONNECT_HANDOFF_20261026/NEW_E2_SUPERMIMIC_SOURCE_CPU_ONLY'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('NEW_E2_SUPERMIMIC_SOURCE_ONLY72_MISSING_STARTED_ACTUAL.json',dict(epoch=time.time(),only_new_frozen_CPU_source_files=True,no_old_payload_or_weight_transfer=True))
 rows=[];buffer=io.BytesIO()
 with tarfile.open(fileobj=buffer,mode='w:gz',compresslevel=1) as archive:
  for p in sorted(B.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts:continue
   assert p.suffix.lower() in {'.py','.json','.txt','.md','.log','.diff','.jsonl','.csv'}
   rel=p.relative_to(B).as_posix();raw=p.read_bytes();rows.append(dict(relative=rel,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()));archive.add(p,arcname=rel,recursive=False)
 raw=buffer.getvalue();sha=hashlib.sha256(raw).hexdigest();put('NEW_E2_SUPERMIMIC_SOURCE_ONLY72_MISSING_MANIFEST_ACTUAL.json',dict(files=rows,archive_bytes=len(raw),archive_SHA=sha,not_installed_training_or_reference_demo=True))
 sp=importlib.util.spec_from_file_location('defs',T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83_20261026/relocate_minimal_closed81O_82Q_NPZ_for83_TLS_V5_unused_once.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);d=m.d
 ms=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');mem=importlib.util.module_from_spec(ms);ms.loader.exec_module(mem);secret=mem.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  d.code(c,d.PY72,"from pathlib import Path;import json;B=Path(v['root']);assert B.parent.is_dir() and not B.exists();B.mkdir();print(json.dumps(dict(created=True)))",dict(root=ROOT),timeout=30)
  sf=c.open_sftp()
  try:sf.putfo(io.BytesIO(raw),ROOT+'/E2_SOURCE_CPU_ONLY.tar.gz',file_size=len(raw))
  finally:sf.close()
  code="from pathlib import Path;import hashlib,json,tarfile,time;B=Path(v['root']);p=B/'E2_SOURCE_CPU_ONLY.tar.gz';assert p.stat().st_size==v['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==v['SHA'];out=B/'files';out.mkdir()\nwith tarfile.open(p,'r:gz') as tf:\n assert all(x.isfile() and not Path(x.name).is_absolute() and '..' not in Path(x.name).parts for x in tf.getmembers());tf.extractall(out,filter='data')\nfor r in v['files']:\n p=out/r['relative'];assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA']\na=dict(epoch=time.time(),passed=True,root=str(B),file_count=len(v['files']),all_new_file_fullSHA_verified=True,CPU_source_only_not_runtime_or_GO=True,no_old_weights_or_source_host_access=True);(B/'COMPLETE_ACTUAL.json').write_text(json.dumps(a,indent=2));print(json.dumps(a))"
  result=d.code(c,d.PY72,code,dict(root=ROOT,bytes=len(raw),SHA=sha,files=rows),timeout=60);put('NEW_E2_SUPERMIMIC_SOURCE_ONLY72_MISSING_RETURNED_ACTUAL.json',result);print(json.dumps(result))
 except BaseException:
  put('NEW_E2_SUPERMIMIC_SOURCE_ONLY72_MISSING_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_retry=True));raise
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':main()
