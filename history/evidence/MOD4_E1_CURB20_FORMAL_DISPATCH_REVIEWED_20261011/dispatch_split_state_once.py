"""Unique dispatch after actual ManagerTermBase CPU proof and old failed exit."""
from stage_split_state_admission_once import D,R,E,B,PY,NEW,connect_both,cleanup,save
import json,time,shlex,traceback
def main():
 cpu=json.loads((R/'SPLIT_STATE_TARGET_CPU_PASSED.json').read_bytes());assert cpu['passed'] and cpu['source_count']==388
 save('SPLIT_STATE_DISPATCH_STARTED.json',dict(epoch=time.time(),trial_id='CURB-SPLIT-STATE-388-DISPATCH-01',new_CPU_zero_step_startup_contract_passed=True,SDK_native_small_not_repeated=True))
 n,w=connect_both()
 try:
  code=r'''from pathlib import Path
import sys,json,time,subprocess,torch
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_curb20_split_state_admission_once as own
own.verify();own.wait_existing()
assert own.read(D/'reports/CURB_SPLIT_FULLSTATE_CPU_PASSED.json')['passed']
assert not (D/'reports/E1_DISPATCH_STARTED.json').exists() and not (D/'reports/SPLIT_STATE_DISPATCH_ACTUAL_RECEIPT.json').exists() and not (D/'split_state_parent.log').exists()
assert not torch.cuda.is_initialized()
argv=[own.s.q.base.PY,str(D/'supervise_curb20_fresh_process_resume_once.py')]
with (D/'split_state_parent.log').open('x') as out:p=subprocess.Popen(argv,cwd=D,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
identity=own.identity(p.pid);assert identity and identity['cwd']==str(D) and identity['argv']==argv
v=dict(epoch=time.time(),owner=identity,argv=argv,root=str(D),source_count=len(own.read(D/'reports/SOURCE_FREEZE.json')['sha256']),CPU_passed=True,
actual_new_CUDA_PPO_admission_and_formal_pending=True,SDK_native_small_clock_not_replayed=True,new_budget_seconds=0,old380_prelearning_failure_retained=True)
(D/'reports/SPLIT_STATE_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT',repr(NEW))
  compile(code,'<environment-view-actual-dispatch>','exec');_,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:save('SPLIT_STATE_DISPATCH_REJECTION.json',dict(epoch=time.time(),stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace'),returncode=rc,do_not_replay_or_assume_no_process=True));raise RuntimeError('Read actual own processes before any continuation')
  v=json.loads(raw);save('SPLIT_STATE_DISPATCH_ACTUAL_RECEIPT.json',v);print(json.dumps(v))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('SPLIT_STATE_DISPATCH_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_dispatch=True));raise
