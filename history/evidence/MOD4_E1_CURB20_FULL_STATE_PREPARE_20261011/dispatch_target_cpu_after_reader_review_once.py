"""Independent continuation after stdlib Python preimport rejection, before launch."""
from stage_reviewed_fullstate_once import D,R,E,B,PY,NEW,connect_both,cleanup,save
import json,time,shlex,traceback
def main():
 error=json.loads((R/'REVIEWED_DISPATCH_ERROR.json').read_bytes());assert "No module named 'torch'" in error['error']
 save('TARGETCPU_DISPATCH_STARTED.json',dict(epoch=time.time(),trial_id='CURB-TARGETCPU-DISPATCH-INTERPRETER-REPAIR-01',original_preimport_error_retained=True,no_original_launch_or_ledger_action_had_run=True))
 n,w=connect_both()
 try:
  code=r'''from pathlib import Path
import sys,json,time,subprocess,torch
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_curb20_fullstate_reviewed_once as reviewed
own=reviewed.prior;own.verify();own.wait_existing()
assert not (D/'reports/E1_DISPATCH_STARTED.json').exists() and not (D/'reports/REVIEWED_DISPATCH_ACTUAL_RECEIPT.json').exists() and not (D/'fullstate_reviewed_parent.log').exists()
assert not torch.cuda.is_initialized()
argv=[own.s.q.base.PY,str(D/'supervise_curb20_fullstate_reviewed_once.py')]
with (D/'fullstate_reviewed_parent.log').open('x') as out:p=subprocess.Popen(argv,cwd=D,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
identity=own.identity(p.pid);assert identity and identity['cwd']==str(D) and identity['argv']==argv
v=dict(epoch=time.time(),owner=identity,argv=argv,root=str(D),source_count=len(own.read(D/'reports/SOURCE_FREEZE.json')['sha256']),new_CPU_validation_passed=True,
 actual_new_CUDA_PPO_admission_and_formal_pending=True,SDK_native_clock_not_replayed=True,new_budget_seconds=0,target_Torch_CPU_interpreter_verified=True,original_stdlib_import_error_retained=True)
(D/'reports/REVIEWED_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT',repr(NEW))
  compile(code,'<targetcpu-actual-dispatch>','exec');_,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:save('TARGETCPU_DISPATCH_REJECTION.json',dict(epoch=time.time(),stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace'),returncode=rc,do_not_replay_or_assume_no_process=True));raise RuntimeError('Inspect actual own processes before any continuation')
  v=json.loads(raw);save('REVIEWED_DISPATCH_ACTUAL_RECEIPT.json',v);save('TARGETCPU_DISPATCH_ACTUAL_RECEIPT.json',v);print(json.dumps(v))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('TARGETCPU_DISPATCH_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_dispatch=True));raise
