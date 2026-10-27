"""Missing-only small E0 manifest, pinned known source path; no models or GPU."""
from pathlib import Path
import json,time,sys,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;R=S/'reports'
def put(n,x):
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
CODE='''from pathlib import Path
import json,hashlib
p=Path('/home/egde/rl_candidates/MOD4_D7_FULL_CONTRACT_20261009/learning_logs/2026-10-09_09-45-49_d7_stable_block1_1791510179560330441/run_manifest.json')
assert p.is_file(),'exact original E0 run_manifest missing; no guessed fallback'
a=p.stat();assert a.st_size<2000000
b=p.read_bytes();c=p.stat();assert (a.st_size,a.st_mtime_ns,a.st_ino)==(c.st_size,c.st_mtime_ns,c.st_ino)
j=json.loads(b)
print(json.dumps(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),original_UTF8_text=b.decode('utf8'),before_after_stat_unchanged=True,no_model_GPU_or_account_read=True)))
'''
def main():
 put('E0_EXACT_ORIGINAL_RUN_MANIFEST_READ_CONSUMED_ACTUAL.json',dict(epoch=time.time(),purpose='Missing original E0 reward/runtime source provenance for authorized PPO50 gas400 adaptation'))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 c=None
 try:
  c=route.connect();r=d.code(c,route.PY,CODE,{},timeout=60)
  p=S/'E0_ACTUAL_ORIGINAL_RUN_MANIFEST_UTF8.json'
  with p.open('x',encoding='utf8',newline='') as f:f.write(r.pop('original_UTF8_text'))
  import hashlib
  assert hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA']
  r.update(actual_finite_returned=True,local_exact_path=str(p))
  put('E0_EXACT_ORIGINAL_RUN_MANIFEST_FOR_PPO_ADAPTATION_RETURNED_ACTUAL.json',r)
  print(json.dumps(r))
 finally:
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('E0_EXACT_RUN_MANIFEST_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_guessed_fallback_or_repeat=True));raise
