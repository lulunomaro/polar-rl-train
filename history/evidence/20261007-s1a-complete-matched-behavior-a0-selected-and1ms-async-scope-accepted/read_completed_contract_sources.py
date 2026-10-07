"""Read-only source/returned-result collection for the completed comparison."""
from pathlib import Path
import sys,json,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
c=connect()
try:
 with c.open_sftp() as s:
  root='/home/egde/rl_candidates/MOD4_S1A_FROZEN_SAVED_SCHEMA_REVIEW_20261007'
  dest=D/'review_contracts';dest.mkdir(exist_ok=True)
  for n in ['scut_curriculum_gate_v4.py','world_progress_contract.py','physics_clock.py']:
   try:s.get(root+'/isaac/mod4/'+n,str(dest/n))
   except FileNotFoundError:
    try:s.get(root+'/'+n,str(dest/n))
    except FileNotFoundError:pass
  rows=[]
  for d in sorted((R/'clock1000_eval').iterdir()):
   if not d.is_dir():continue
   p=d/'probe.json'
   with s.open('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/eval_results/'+d.name+'/probe.json','rb') as f:raw=f.read()
   assert raw==p.read_bytes(),d.name
   rows.append(dict(job_id=d.name,returned_probe_sha256=hashlib.sha256(raw).hexdigest(),exact_to_worker=True))
  out=dict(results=rows,all14_returned_exact=len(rows)==14,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.glob('*.py')},read_only=True)
  (R/'COMPLETED_RETURN_AND_CONTRACT_READBACK.json').write_text(json.dumps(out,indent=2))
  print(json.dumps(out))
finally:c.close()
