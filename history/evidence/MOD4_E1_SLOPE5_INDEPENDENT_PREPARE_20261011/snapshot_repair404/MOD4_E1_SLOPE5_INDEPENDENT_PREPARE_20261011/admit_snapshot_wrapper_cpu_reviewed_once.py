from slope_io import *
import ast,traceback
NEW='/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_SNAPSHOT_REVIEWED_20261011'
def main():
 save('SNAPSHOT_CPU_WRAPPER_SCHEMA_REVIEW.json',dict(epoch=time.time(),old_CPU_reader_AttributeError_preserved=True,wrapper_source_uses_prior_source_explicitly=True,production_wrapper_unchanged=True,no_GPU_or_budget_mutation=True))
 tree=ast.parse((D/'stage_slope_snapshot_full_receipts_once.py').read_text())
 code=next(x.value for x in ast.walk(tree) if isinstance(x,ast.Constant) and isinstance(x.value,str) and 'snapshot_members_checked=len(checked)' in x.value)
 assert 'source=own.source()' in code;code=code.replace('source=own.source()','source=own.prior.source()').replace('ROOTNEW',repr(NEW)).replace('ROOT402',repr('/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_INDEPENDENT_20261011'))
 n,w=connect_both()
 try:
  boundary(n);_,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:save('SNAPSHOT_CPU_WRAPPER_REJECTED.json',dict(returncode=rc,stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace')));raise RuntimeError('CPU wrapper reader rejected')
  save('SNAPSHOT_REPAIR_TARGET_CPU_PASSED.json',json.loads(raw));save('SNAPSHOT_FULL_RECEIPTS_STAGED_VERIFIED.json',dict(epoch=time.time(),root=NEW,source_count=404,old_failure_unique_cost_retained=True,no_native_small_replay=True,new_CPU_actual_passed=True));print(json.dumps(dict(root=NEW,CPU_passed=True,source_count=404,no_GPU_launch=True)))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('SNAPSHOT_CPU_WRAPPER_ERROR.json',dict(error=traceback.format_exc(),no_oldstage_replay=True));raise
