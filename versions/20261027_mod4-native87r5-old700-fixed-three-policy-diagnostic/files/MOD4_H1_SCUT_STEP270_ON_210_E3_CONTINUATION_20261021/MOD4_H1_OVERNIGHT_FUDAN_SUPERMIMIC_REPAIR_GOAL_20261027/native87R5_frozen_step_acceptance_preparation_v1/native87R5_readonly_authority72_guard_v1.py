"""UNUSED root finite-parent guard for source210 eval; no ledger writes/copy.

Keep stdin open while owned eval children run. Root must wait all children, send
release_after_all_eval_children_waited, then require identical canonical exit SHA.
"""
from pathlib import Path
import hashlib,json,os,select,sys,time
from native87R5_frozen_acceptance_contract_v1 import CANONICAL,require
def main():
 import fcntl,psutil
 C=Path(CANONICAL);locks=[];initial=None
 try:
  for name in ('native_floor_supervisor.lock','autonomy_controller.lock'):
   f=(C.parent/name).open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
  raw=C.read_bytes();c=json.loads(raw);initial=hashlib.sha256(raw).hexdigest()
  require(c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['remaining_training_seconds']>86412.86069250107 and c['budget_mode']=='finite_original_limits_restored_after_single4090_return' and c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[],'sole72 original finite closed state required')
  p=psutil.Process(os.getpid());expires=time.time()+1800
  print(json.dumps(dict(kind='native87R5_readonly72_eval_guard',canonical=CANONICAL,canonical_SHA=initial,canonical_active_segment=None,original_two_locks_held=True,read_only=True,
   original_owner_locks=[dict(path=str(C.parent/name),actual_fcntl_free=True) for name in ('native_floor_supervisor.lock','autonomy_controller.lock')],
   pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),expires_epoch=expires,no_account_write_or_copy=True)),flush=True)
  while time.time()<expires:
   require(hashlib.sha256(C.read_bytes()).hexdigest()==initial,'canonical bytes changed under readonly eval guard')
   if select.select([sys.stdin],[],[],1.)[0]:
    line=sys.stdin.readline();require(line.strip()=='release_after_all_eval_children_waited','root waited release required; EOF is not successful completion');break
  else:raise RuntimeError('readonly source210 authority guard expired; eval must stop')
  require(hashlib.sha256(C.read_bytes()).hexdigest()==initial,'canonical bytes changed at exit')
  print(json.dumps(dict(passed=True,canonical_bytes_unchanged=True,canonical_SHA=initial,root_waited_release_received=True,no_account_write_or_copy=True)),flush=True)
 finally:
  for f in reversed(locks):f.close()
if __name__=='__main__':main()
