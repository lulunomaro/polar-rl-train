"""One new reviewed controller, prechecked exactCPU/boundary, no old entry replay."""
from stage_reviewed_fullstate_once import D,R,E,B,PY,NEW,connect_both,cleanup,linux_json,H,save,put
from pathlib import Path
import json,time,traceback
def main():
 save('REVIEWED_DISPATCH_STARTED.json',dict(epoch=time.time(),trial_id='CURB-FULLSTATE-REVIEWED-LEARNING-DISPATCH-01',once=True,new_budget_seconds=0))
 n,w=connect_both()
 try:
  code=r'''from pathlib import Path
import sys,json,time,subprocess,torch
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_curb20_fullstate_reviewed_once as reviewed
own=reviewed.prior;own.verify();own.wait_existing()
assert not (D/'reports/E1_DISPATCH_STARTED.json').exists() and not (D/'fullstate_reviewed_parent.log').exists()
argv=[own.s.q.base.PY,str(D/'supervise_curb20_fullstate_reviewed_once.py')]
with (D/'fullstate_reviewed_parent.log').open('x') as out:p=subprocess.Popen(argv,cwd=D,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
identity=own.identity(p.pid);assert identity and identity['cwd']==str(D) and identity['argv']==argv
v=dict(epoch=time.time(),owner=identity,argv=argv,root=str(D),source_count=len(own.read(D/'reports/SOURCE_FREEZE.json')['sha256']),new_CPU_validation_passed=True,
 actual_new_CUDA_PPO_admission_and_formal_pending=True,SDK_native_clock_not_replayed=True,new_budget_seconds=0)
(D/'reports/REVIEWED_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT',repr(NEW))
  v=linux_json(n,code);save('REVIEWED_DISPATCH_ACTUAL_RECEIPT.json',v);print(json.dumps(v))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('REVIEWED_DISPATCH_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_dispatch_or_old_main=True,actual_state_required=True));raise
