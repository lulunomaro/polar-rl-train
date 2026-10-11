from pathlib import Path
import sys,json,time,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(D));from stage_entry_fullstate_and_cpu_once import NEW,save
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import repair_io as io

def main():
 assert json.loads((R/'ENTRY_TARGET_FULLSTATE_CPU_PASSED.json').read_bytes())['passed']
 assert not (R/'ENTRY_FULLSTATE_DISPATCH_ACTUAL_RECEIPT.json').exists()
 n,w=io.connect_both()
 try:
  code=r'''from pathlib import Path
import json,time,sys,subprocess,ast
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'))
import supervise_curb20_entry_fullstate_once as own
own.verify();own.wait_existing();assert own.D==D and own.R==D/'reports'
entry=D/'supervise_curb20_entry_fullstate_once.py';ast.parse(entry.read_text())
assert not (D/'controller.log').exists() and not (D/'reports/E1_DISPATCH_STARTED.json').exists()
args=[own.s.q.base.PY,str(entry)]
with (D/'controller.log').open('x') as f:p=subprocess.Popen(args,cwd=own.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
row=dict(epoch=time.time(),root=str(D),source_count=len(own.read(D/'reports/SOURCE_FREEZE.json')['sha256']),owner=own.identity(p.pid),argv=args,correct_import_and_main_entry_exact=True,first_new_scope_origin_bound_SDK10=True,valid_native20k_reused_not_replayed=True,source_sha256=own.SOURCE_SHA,PPO_small_big_fresh_and_formal_require_new_actual_PASSED=True,no_new_budget_extension=True)
(D/'reports/ENTRY_FULLSTATE_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(row,indent=2));print(json.dumps(row))
'''.replace('ROOT',repr(NEW))
  _,o,e=n.exec_command(io.PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:save('ENTRY_FULLSTATE_DISPATCH_REJECTED.json',dict(epoch=time.time(),exit_code=rc,stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace')));raise RuntimeError('New dispatch rejected; inspect own process before any further action')
  row=json.loads(raw);save('ENTRY_FULLSTATE_DISPATCH_ACTUAL_RECEIPT.json',row)
  print(json.dumps(dict(owner=row['owner'],source_count=row['source_count'],root=row['root'],first_scope='origin_bound_SDK10',formal_pending=True)))
 finally:io.cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY_FULLSTATE_DISPATCH_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_main_or_once_replay=True));raise
