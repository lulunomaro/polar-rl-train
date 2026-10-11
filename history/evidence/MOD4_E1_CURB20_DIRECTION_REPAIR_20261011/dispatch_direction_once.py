from direction_io import *
import traceback
def main():
 root=json.loads((R/'DIRECTION_ACTIVE_ROOT.json').read_bytes())['root'];n,w=io.connect_both()
 try:
  v=run(n,'''from pathlib import Path
import sys,json,time,torch,subprocess,fcntl
D=Path(ROOT);C=D/'isaac/mod4';sys.path.insert(0,str(D));sys.path.insert(0,str(C));torch.set_num_threads(1)
import supervise_curb20_direction_once as own
own.verify();own.wait_existing();assert not torch.cuda.is_initialized()
assert not (D/'controller.log').exists() and not (D/'reports/E1_DISPATCH_STARTED.json').exists()
args=[own.s.q.base.PY,str(D/'supervise_curb20_direction_once.py')]
with (D/'controller.log').open('x') as f:p=subprocess.Popen(args,cwd=own.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
v=dict(epoch=time.time(),root=str(D),owner=own.identity(p.pid),argv=args,CPU_passed=True,source_count=len(own.read(D/'reports/SOURCE_FREEZE.json')['sha256']),only_CURB_command_direction_axis=True,formal_requires_new_scope_PASSED=True,no_budget_extension=True)
(D/'reports/DIRECTION_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT',repr(root)))
  save('DIRECTION_DISPATCH_ACTUAL_RECEIPT.json',v);print(json.dumps(v))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('DIRECTION_DISPATCH_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_once_replay=True));raise
