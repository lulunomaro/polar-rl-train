from slope_io import *
import traceback
NEW='/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_SNAPSHOT_REVIEWED_20261011'
def main():
 assert (R/'SNAPSHOT_FULL_RECEIPTS_STAGED_VERIFIED.json').exists()
 save('SNAPSHOT_DISPATCH_STARTED.json',dict(epoch=time.time(),new_unique_root_only=True,old402_not_restarted=True))
 n,w=connect_both()
 try:
  boundary(n)
  code=r'''from pathlib import Path
import sys,json,torch,ast,time,subprocess
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_slope5_snapshot_reviewed_once as own
assert own.read(D/'reports/SLOPE_SNAPSHOT_TARGET_CPU_PASSED.json')['passed']
own.verify();own.wait_existing();assert not torch.cuda.is_initialized() and not (D/'reports/E1_DISPATCH_STARTED.json').exists()
entry=D/'supervise_slope5_snapshot_reviewed_once.py';ast.parse(entry.read_text());assert 'else:main()' in entry.read_text()
args=[own.s.q.base.PY,str(entry)];log=D/'controller.log';assert not log.exists()
with log.open('x') as f:p=subprocess.Popen(args,cwd=own.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
receipt=dict(epoch=time.time(),owner=own.identity(p.pid),argv=args,import_module_matches_unique_main=entry.stem,source_count=len(own.read(D/'reports/SOURCE_FREEZE.json')['sha256']),snapshot_only_worker_repair=True,SDK_native_small_exact_reused=True,formal_after_new_big_and_fresh_PASSED_only=True,no_budget_extension=True)
(D/'reports/SLOPE_SNAPSHOT_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
'''.replace('ROOT',repr(NEW))
  _,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:save('SNAPSHOT_DISPATCH_REJECTED.json',dict(returncode=rc,stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace')));raise RuntimeError('Unique snapshot repair dispatch rejected')
  row=json.loads(raw);save('SNAPSHOT_DISPATCH_ACTUAL_RECEIPT.json',row);print(json.dumps(row))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('SNAPSHOT_DISPATCH_ERROR.json',dict(error=traceback.format_exc(),no_oldonce_replay=True));raise
