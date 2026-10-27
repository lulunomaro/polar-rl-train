"""Missing original CPU error/log only; no model/GPU/retry or other host."""
from pathlib import Path
import sys,json,time,hashlib,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
REMOTE=r'''from pathlib import Path
import json,psutil,hashlib
B=Path(v['root']);assert B==Path('/mnt/mod4_linux_durable_20261013/H1step270_own_step_gas400_native_2610v88/h1')
assert not any((B/x).exists() for x in ('NODE_IDENTITY.json','job0/GO_PRODUCTION.json','NODE_CURRENT.json'))
started=json.loads((B/'job0/native88_SOURCE_CPU_STARTED_ACTUAL.json').read_bytes());waited=json.loads((B/'job0/native88_SOURCE_CPU_WAITED_EXIT_ACTUAL.json').read_bytes());assert waited['pid']==started['pid'] and waited['actual_waited'] and waited['returncode']!=0
try:
 p=psutil.Process(started['pid']);assert p.create_time()!=started['creation'];out=True
except psutil.NoSuchProcess:out=True
names=['job0/native88_SOURCE_CPU.log','job0/native88_SOURCE_CPU_STARTED_ACTUAL.json','job0/native88_SOURCE_CPU_WAITED_EXIT_ACTUAL.json','job0/NATIVE88_SOURCE_CPU_STARTED_ACTUAL.json']
names.extend(p.relative_to(B).as_posix() for p in sorted((B/'job0').glob('NATIVE88_SOURCE_CPU_ORIGINAL_ERROR_*.json')))
texts={}
for rel in names:
 p=B/rel
 if not p.exists():continue
 assert p.is_file() and not p.is_symlink() and p.stat().st_size<=300000
 raw=p.read_bytes();texts[rel]=dict(bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8'))
print(json.dumps(dict(actual_own_CPU_waited_out=out,original_CPU_returncode=waited['returncode'],no_NODE_GO_or_owner=True,model_read_intent_present=(B/'job0/NATIVE88_SOURCE_CPU_MODEL_READ_INTENT_ACTUAL.json').exists(),native_initial_model_load_returned=(B/'job0/NATIVE88_NATIVE_SOURCE_INITIAL_LOAD_RETURNED_ACTUAL.json').exists(),normal_witness_initial_model_load_returned=(B/'job0/NATIVE88_NORMAL_WITNESS_INITIAL_LOAD_RETURNED_ACTUAL.json').exists(),texts=texts,no_new_model_or_GPU_or_account_read=True)))'''
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 put('NATIVE88_MISSING_CPU_ERROR_ENTRY_CONSUMED_ACTUAL.json',dict(epoch=time.time(),no_old_once_retry=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 c=route.connect()
 try:v=d.code(c,route.PY,REMOTE,dict(root='/mnt/mod4_linux_durable_20261013/H1step270_own_step_gas400_native_2610v88/h1'),timeout=60)
 finally:c.close()
 put('NATIVE88_H1_PREGO_CPU_ORIGINAL_ERROR_MISSING_ONLY_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_returned=True,**v))
 for rel,r in v['texts'].items():
  p=N/'original_failed_preGO_CPU_text'/rel;p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb') as f:f.write(r['text'].encode())
 print(json.dumps(dict(actual_finite_returned=True,no_NODE_GO=True,error_texts=len(v['texts']),model_read_intent_present=v['model_read_intent_present'])))
if __name__=='__main__':
 try:main()
 except BaseException:put('MISSING_CPU_ERROR_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(original_error=traceback.format_exc()));raise
