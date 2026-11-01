from pathlib import Path
import hashlib,json,psutil,time
from authority235_dr064 import CANONICAL,validate_authority
def read(p):return json.loads(Path(p).read_bytes())
def audit_current(binding):
 raw=Path(CANONICAL).read_bytes();c=json.loads(raw);o=binding['owner'];O=Path(o['root'])
 identity=read(O/'OWNER_IDENTITY.json');current=read(O/'OWNER_CURRENT.json');fact=dict(running=False)
 try:
  q=psutil.Process(o['pid'])
  if q.create_time()==o['creation'] and q.status()!=psutil.STATUS_ZOMBIE:
   fact=dict(running=True,pid=q.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),cwd=q.cwd())
 except psutil.NoSuchProcess:pass
 closed=None
 if c['active_segment'] is None:closed=dict(cohort_final=read(O/'COHORT_FINAL.json'),owner_exit=read(O/'OWNER_EXIT_ACTUAL.json'))
 mode=validate_authority(c,binding,identity,current,fact,closed)
 return dict(epoch=time.time(),passed=True,scope=mode,canonical_SHA=hashlib.sha256(raw).hexdigest(),actual_canonical_active=c['active_segment'],
  actual_owner_identity=identity,actual_owner_current_GO=current['go'],exact_original_process_fact=fact,original_closed_proof=closed,account_writes=0)
