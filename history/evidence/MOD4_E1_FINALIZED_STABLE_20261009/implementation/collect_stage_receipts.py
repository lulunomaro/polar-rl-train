from pathlib import Path
import sys,json,time
D=Path(__file__).resolve().parent;R=D/'reports';B=D.parent
sys.path.insert(0,str(B/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/'+D.name
try:
 with c.open_sftp() as f:
  for n in ('SOURCE_FREEZE.json','E1_REVIEWED_STABLE_DEPLOYED.json','PREDECESSOR_CPU_TRANSFER_REJECTION.json','PREDECESSOR_CPU_DEPENDENCY_REJECTION.json','E1_INSTALL_BOUNDARY.json','E1_DISPATCH_STARTED.json','E1_GUARDIAN_STARTED.json','E1_COMPLETE_PPO_PREFLIGHT_PASSED.json','E1_STATE.json','E1_ATTENTION.json','E1_PLANNED_BEHAVIOR_SCOPE_ACCEPTED.json'):
   try:raw=f.open(root+'/reports/'+n).read()
   except FileNotFoundError:continue
   (R/n).write_bytes(raw)
 print(json.dumps(dict(epoch=time.time(),receipts_collected=True,no_mutation=True)))
finally:c.close()
