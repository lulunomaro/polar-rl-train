"""One corrected literal/main dispatch, after actual old388 exit and both locks."""
from stage_formal_dispatch_reviewed_once import D,R,E,B,PY,NEW,connect_both,cleanup,save
import json,time,shlex,traceback
ENTRY='supervise_curb20_formal_dispatch_reviewed_once.py'
def main():
 cpu=json.loads((R/'FORMAL_DISPATCH_TARGET_CPU_PASSED.json').read_bytes());assert cpu['passed'] and cpu['source_count']==389 and cpu['corrected_dispatch_literal_must_match_entry']==ENTRY
 save('FORMAL_REVIEWED_DISPATCH_STARTED.json',dict(epoch=time.time(),trial_id='CURB389-CORRECT-ENTRY-FORMAL-DISPATCH-01',requested_entry=ENTRY,no_old_controller_main_replay=True))
 n,w=connect_both()
 try:
  code=r'''from pathlib import Path
import sys,json,time,hashlib,subprocess,fcntl,torch
D=Path(ROOT);B=Path(BUDGET);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_curb20_formal_dispatch_reviewed_once as reviewed
own=reviewed.own;own.verify();own.wait_existing();assert own.read(D/'reports/CURB_SPLIT_FULLSTATE_CPU_PASSED.json')['passed']
assert own.s.q.base.budget_state()['active_segment'] is None and not own.read(own.s.q.ctl.STATE_PATH).get('active_training')
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
entry=D/ENTRY;assert entry==Path(reviewed.__file__) and entry.name=='supervise_curb20_formal_dispatch_reviewed_once.py'
assert hashlib.sha256(entry.read_bytes()).hexdigest()==own.read(D/'reports/SOURCE_FREEZE.json')['sha256'][entry.name]
assert not (D/'reports/E1_DISPATCH_STARTED.json').exists() and not (D/'reports/FORMAL_REVIEWED_DISPATCH_ACTUAL_RECEIPT.json').exists() and not (D/'formal_reviewed_parent.log').exists() and not torch.cuda.is_initialized()
argv=[own.s.q.base.PY,str(entry)]
with (D/'formal_reviewed_parent.log').open('x') as out:p=subprocess.Popen(argv,cwd=D,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
identity=own.identity(p.pid);assert identity and identity['cwd']==str(D) and identity['argv']==argv
v=dict(epoch=time.time(),owner=identity,argv=argv,root=str(D),source_count=389,correct_main_import_and_Popen_entry_same_exact=True,old388_actual_exit_two_OS_locks_free=True,whole_split_actual_admission_passed=True,only_formal300s=True,no_new_GPU_preflight=True,new_budget_seconds=0)
(D/'reports/FORMAL_REVIEWED_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT',repr(NEW)).replace('BUDGET',repr(B)).replace('ENTRY',repr(ENTRY))
  compile(code,'<correct-main-actual-dispatch>','exec');_,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:save('FORMAL_REVIEWED_DISPATCH_REJECTION.json',dict(epoch=time.time(),returncode=rc,stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace'),no_blind_dispatch_replay=True));raise RuntimeError('Review actual before any next dispatch')
  v=json.loads(raw);save('FORMAL_REVIEWED_DISPATCH_ACTUAL_RECEIPT.json',v);print(json.dumps(v))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('FORMAL_REVIEWED_DISPATCH_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_dispatch=True));raise
