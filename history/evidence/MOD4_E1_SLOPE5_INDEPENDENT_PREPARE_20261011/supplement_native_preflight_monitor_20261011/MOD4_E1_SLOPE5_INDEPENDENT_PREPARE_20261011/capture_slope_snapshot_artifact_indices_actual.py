from slope_io import *
NEW='/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_SNAPSHOT_REVIEWED_20261011'
n,w=connect_both()
try:
 row=linux_json(n,r'''from pathlib import Path
import json,hashlib,time
roots=[Path(ROOT),Path('/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_INDEPENDENT_20261011')];rows=[]
for root in roots:
 for scope in ('discard_logs','learning_logs','fresh_process_resume'):
  for p in sorted((root/scope).rglob('*')):
   if not p.is_file() or p.suffix.lower() not in ('.pt','.npz','.npy','.usd') and p.stat().st_size<1800000:continue
   size=p.stat().st_size;sha=hashlib.sha256(p.read_bytes()).hexdigest();assert p.stat().st_size==size
   rows.append(dict(path=str(p),bytes=size,sha256=sha,actual_original_retained=True,large_original_index_only=True))
print(json.dumps(dict(epoch=time.time(),rows=rows,no_PPO_or_budget_write=True)))
'''.replace('ROOT',repr(NEW)))
 p=save('SNAPSHOT_FULL_ARTIFACT_INDICES_'+str(time.time_ns())+'.json',row);print(json.dumps(dict(report=str(p),indices=len(row['rows']))))
finally:cleanup(n,w)
