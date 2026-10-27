"""One finite snapshot of known own JSON/identities only; no PT or budget read/write."""
from pathlib import Path
import json,hashlib,time
from E0_single72_protocol_v1 import JOB
def snapshot():
 job=Path(JOB);parent=job.parent;owner=parent/'owner';node=parent/'node_e0';out=job/'adaptation'
 paths=[owner/'OWNER_IDENTITY.json',owner/'OWNER_CURRENT.json',owner/'COHORT_FINAL.json',owner/'OWNER_EXIT_ACTUAL.json',
  node/'NODE_IDENTITY.json',node/'NODE_CURRENT.json',node/'NODE_TERMINAL_ACTUAL.json',node/'NODE_EXIT_ACTUAL.json',
  job/'production_STARTED_ACTUAL.json',job/'production_WAITED_EXIT_ACTUAL.json',job/'GO_PRODUCTION.json',
  out/'SOURCE_FULLRESTORE_ZERO_VERIFIED.json',out/'CLOCK_GAS400_NATIVE24_ACTUAL.json',out/'PPO_POSITIVE_CURRENT.json',
  out/'latest_complete.json',out/'FINAL.json',out/'APP_CLOSED.json',out/'WORKER_ORIGINAL_ERROR.json',out/'WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json']
 result={};identities=[]
 for path in paths:
  if not path.exists():result[str(path)]=dict(exists=False);continue
  before=path.stat();raw=path.read_bytes();after=path.stat();stable=(before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
  value=json.loads(raw) if stable else None
  result[str(path)]=dict(exists=True,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),stable=stable,value=value)
  if path.name in ('OWNER_IDENTITY.json','NODE_IDENTITY.json','production_STARTED_ACTUAL.json') and value:identities.append(value)
 own=[]
 import psutil
 for identity in identities:
  try:
   process=psutil.Process(identity['pid']);creation=process.create_time()
   if creation!=identity['creation']:own.append(dict(pid=identity['pid'],original_creation=identity['creation'],PID_recycled_no_argv_or_exe_read=True));continue
   own.append(dict(pid=identity['pid'],creation=creation,exe=process.exe(),argv=process.cmdline(),root=process.cwd(),exact_recorded_own_creation_matched=True))
  except psutil.NoSuchProcess:own.append(dict(pid=identity['pid'],original_creation=identity['creation'],actual_own_process_out=True))
 return dict(epoch=time.time(),known_own_JSON=result,known_own_processes=own,no_PT_GPU_or_budget_IO=True,
  no_unknown_PID_or_process_enumeration=True,WM_transition_data_collection_executed=False,
  cost_is_settled_only_by_original_owner_and_actual_C72_not_inferred_from_worker_exit=True)
if __name__=='__main__':print(json.dumps(snapshot()))
