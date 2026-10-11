from direction_io import *
import traceback
from prepare_direction140_decision_and_exposure_continuation_once import ROOT

def main():
 assert json.loads((R/'COMPLETE140_AND_EXPOSURE_CPU_METADATA_SYNCED.json').read_bytes())['metadata_synced']
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import sys,json,time,torch,subprocess
D=Path(NEW_ROOT_TOKEN);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_curb20_direction_exposure_matched_once as own
own.prior.verify();own.boundary();assert own.read(D/'reports/MATCHED_REUSE_CPU_PASSED.json')['passed']
assert not (D/'reports/E1_DISPATCH_STARTED.json').exists() and not (D/'reports/MATCHED_DISPATCH_ACTUAL_RECEIPT.json').exists()
assert not torch.cuda.is_initialized()
args=[own.prior.s.q.base.PY,str(D/'supervise_curb20_direction_exposure_matched_once.py')]
with (D/'controller.log').open('x') as f:p=subprocess.Popen(args,cwd=own.prior.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
v=dict(epoch=time.time(),root=str(D),owner=own.prior.identity(p.pid),argv=args,source_count=424,target_seconds=900,source=own.read(D/'reports/MATCHED_SOURCE_SELECTED.json'),scope='same_CURB20_entry_direction_training_exposure_only',old_all_admission_scope_exact_SHA_reused=True,no_preflight_replay_or_budget_extension=True)
(D/'reports/MATCHED_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('NEW_ROOT_TOKEN',repr(ROOT)))
  save('EXPOSURE_MATCHED_DISPATCH_ACTUAL_RECEIPT.json',v);print(json.dumps(dict(root=v['root'],owner=v['owner'],source_count=424,target_seconds=900,no_preflight_replay=True)))
 finally:io.cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('EXPOSURE_MATCHED_DISPATCH_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),old_main_not_replayed=True));raise
