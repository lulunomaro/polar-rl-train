"""CPU-only389 preparation while preserving own accidental388 restore-only task."""
from stage_split_state_admission_once import D,R,E,B,PY,connect_both,cleanup,linux_json,H,save,put
from pathlib import Path
import json,time,shlex,traceback
OLD='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_SPLIT_STATE_ADMITTED_20261011'
NEW='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_FORMAL_DISPATCH_REVIEWED_20261011'
def main():
 receipt=json.loads((R/'SPLIT_STATE_DISPATCH_ACTUAL_RECEIPT.json').read_bytes());assert receipt['argv'][1].endswith('supervise_curb20_fresh_process_resume_once.py')
 save('FORMAL_DISPATCH_LITERAL_ERROR_REVIEW.json',dict(epoch=time.time(),trial_id='CURB388-DISPATCH-COPIED-OLD-MAIN-LITERAL-01',original_dispatch_receipt=receipt,actual_imported_validation_module='supervise_curb20_split_state_admission_once',actual_Popen_script='supervise_curb20_fresh_process_resume_once.py',restore_only_max_iterations0_not_formal=True,extra_restore_replay_is_invalid_attempt_retained=True,no_PPO_or_canonical_delta_observed=True,no_kill_hotpatch_or_second_GPU_launch=True,corrected_unique389_wrapper_will_wait_actual_old388_exit_and_two_locks=True))
 save('FORMAL_DISPATCH_STAGE_STARTED.json',dict(epoch=time.time(),CPU_only_no_new_GPU_authority_claim=True,new_dispatch_literal_and_main_reviewed=True))
 n,w=connect_both()
 try:
  v=linux_json(n,r'''from pathlib import Path
import json,time,hashlib,shutil
old=Path(OLD);new=Path(NEW);B=Path(BUDGET);budget=B.read_bytes();j=lambda p:json.loads(p.read_bytes());assert not new.exists()
l=j(B);assert l['active_segment'] is None and l['authorized_training_seconds']==828000
st=j(old/'reports/E1_STATE.json');assert st['phase']=='CURB_fresh_process_full_resume_admission'
f=j(old/'reports/SOURCE_FREEZE.json');assert len(f['sha256'])==388;new.mkdir();(new/'reports').mkdir()
for name,h in f['sha256'].items():
 p=old/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==h;q=new/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for name in ('SOURCE_SELECTED.json','CURB132_COMPLETE_ACTUAL_REVIEW.json','CURB_REUSED_NATIVE.json','CURB_FOUR_CASE_TEMPLATES.json','CURB_TARGET_FULLSTATE_CPU_PASSED.json','CURB_ENVIRONMENT_VIEW_CPU_PASSED.json','CURB_FRESH_PROCESS_CPU_PASSED.json','REUSED_SMALL128.json','FRESH_PROCESS_BIG_CORE_VERIFIED.json'):
 shutil.copy2(old/'reports'/name,new/'reports'/name)
assert B.read_bytes()==budget
print(json.dumps(dict(epoch=time.time(),source_freeze=f,all388_bytes_preserved=True,original388_actual_phase=st['phase'],no_GPU_boundary_or_formal_start_claimed=True,CPU_only_preparation=True,canonical_SHA=hashlib.sha256(budget).hexdigest())))
'''.replace('Path(OLD)','Path('+repr(OLD)+')').replace('Path(NEW)','Path('+repr(NEW)+')').replace('BUDGET',repr(B)))
  save('FORMAL_DISPATCH_388_COPIED.json',v)
  with n.open_sftp() as f:
   freeze=v['source_freeze'];hashes=dict(freeze['sha256']);p=D/'formal_dispatch_payload/supervise_curb20_formal_dispatch_reviewed_once.py';raw=p.read_bytes();compile(raw,str(p),'exec');name=p.name;assert name not in hashes
   put(f,NEW+'/'+name,raw);hashes[name]=H(raw);assert len(hashes)==389
   freeze=dict(freeze,candidate_root=NEW,sha256=hashes,all388_source_bytes_preserved=True,correct_dispatch_main_wrapper=True)
   put(f,NEW+'/reports/SOURCE_FREEZE.json',json.dumps(freeze,indent=2).encode());save('FORMAL_DISPATCH_SOURCE_FREEZE.json',freeze)
  code=r'''from pathlib import Path
import sys,json,time,ast,torch
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_curb20_formal_dispatch_reviewed_once as reviewed
own=reviewed.own;own.verify();proof=own.admit(D,own.fullsave)
entry=D/'supervise_curb20_formal_dispatch_reviewed_once.py';tree=ast.parse(entry.read_text());assert 'else:own.main()' in entry.read_text() and 'supervise_curb20_split_state_admission_once as own' in entry.read_text()
proof.update(epoch=time.time(),source_count=389,passed=True,corrected_dispatch_literal_must_match_entry=entry.name,corrected_main_calls_only_new_split_admission_formal300=True,old388_must_naturally_exit_before_GPU_authority=True)
assert not torch.cuda.is_initialized();(D/'reports/CURB_SPLIT_FULLSTATE_CPU_PASSED.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
'''.replace('ROOT',repr(NEW))
  _,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:save('FORMAL_DISPATCH_CPU_REJECTED.json',dict(epoch=time.time(),returncode=rc,stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace'),no_GPU_or_budget_action=True));raise RuntimeError('Formal dispatch CPU rejected')
  cpu=json.loads(raw);save('FORMAL_DISPATCH_TARGET_CPU_PASSED.json',cpu);print(json.dumps(dict(root=NEW,source_count=389,CPU_passed=True,no_GPU_launch=True,correct_main_entry_reviewed=True)))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('FORMAL_DISPATCH_STAGE_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_blind_stage_replay=True));raise
