"""Capture missing exact quantized stage text receipts; no weight reread or cleanup replay."""
from pathlib import Path
import base64,hashlib,importlib.util,json,os,sys,time,traceback
Q=Path(__file__).resolve().parent;T=Q.parent;W=T.parent;R=Q/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''
from pathlib import Path
import base64,hashlib,json,time
B=Path('/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025');R=B/'receipts';rows=[]
paths=[p for p in R.iterdir() if p.is_file() and p.name.startswith(('SINGLE4090_Q8_','Q8_WINDOWS_MEMORY_RELAY_'))]
paths.append(B/'FULL13_DOWNLOAD_CANCELLED_BY_HUMAN_20261025.json')
for p in sorted(paths):
 assert not p.is_symlink() and p.suffix in ('.json','.log') and p.stat().st_size<2000000
 raw=p.read_bytes();rows.append(dict(path=str(p),relative=p.relative_to(B).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),base64=base64.b64encode(raw).decode()))
print(json.dumps(dict(epoch=time.time(),text_rows=rows,no_model_weight_raw_GPU_budget_read_or_write=True,no_cleanup_or_download_reexecuted=True)))
'''
try:
 put('MISSING_ONLY_Q8_PRODUCER_TEXT_CAPTURE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None
 try:value=d.code(c,d.PY72,CODE,{},timeout=45)
 finally:c.close()
 dest=Q/'actual72_all_quantized_producer_texts';dest.mkdir()
 for row in value['text_rows']:
  raw=base64.b64decode(row.pop('base64'));assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA'];p=dest/row['relative'];p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb') as f:f.write(raw)
  row['local_path']=str(p)
 put('MISSING_ONLY_Q8_PRODUCER_TEXT_CAPTURE_RETURNED_ACTUAL.json',value);print(json.dumps(dict(captured_texts=len(value['text_rows']),no_weight_rehash_or_cleanup_replay=True)))
except BaseException:
 put('MISSING_ONLY_Q8_TEXT_CAPTURE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
