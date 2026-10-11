from slope_io import *
import traceback
def main():
 assert json.loads((R/'SCOPE_METADATA_SYNCED.json').read_bytes())['metadata_synced']
 save('DISPATCH_STARTED.json',dict(epoch=time.time(),unique_new_scope_only=True,no_replay=True))
 n,w=connect_both()
 try:
  boundary(n)
  code=r'''from pathlib import Path
import sys,json,torch,ast,time,subprocess
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_slope5_independent_scope_once as own
own.verify();own.wait_existing();assert not torch.cuda.is_initialized() and not (D/'reports/E1_DISPATCH_STARTED.json').exists()
entry=D/'supervise_slope5_independent_scope_once.py';tree=ast.parse(entry.read_text());assert "else:main()" in entry.read_text()
args=[own.s.q.base.PY,str(entry)];log=D/'controller.log';assert not log.exists()
with log.open('x') as f:p=subprocess.Popen(args,cwd=own.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
receipt=dict(epoch=time.time(),owner=own.identity(p.pid),argv=args,import_module_matches_unique_main=entry.stem,source_count=len(own.read(D/'reports/SOURCE_FREEZE.json')['sha256']),new_scope_not_old_once=True,formal_after_all_actual_gates_only=True,no_budget_extension=True)
(D/'reports/SLOPE_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
'''.replace('ROOT',repr(NEW))
  _,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:save('DISPATCH_REJECTED.json',dict(returncode=rc,stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace'),no_blind_retry=True));raise RuntimeError('Unique new SLOPE dispatch rejected')
  receipt=json.loads(raw);save('DISPATCH_ACTUAL_RECEIPT.json',receipt);print(json.dumps(receipt))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('DISPATCH_ERROR.json',dict(error=traceback.format_exc(),no_main_or_oldonce_replay=True));raise
