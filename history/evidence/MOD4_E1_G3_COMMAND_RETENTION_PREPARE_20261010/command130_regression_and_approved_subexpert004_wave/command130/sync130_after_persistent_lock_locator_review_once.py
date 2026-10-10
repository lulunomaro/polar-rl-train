"""Continue only the unexecuted metadata CAS after a prewrite lock-file guard rejection."""
from pathlib import Path
import ast,hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,indent=2).encode());return p
def main():
 assert (R/'COMMAND130_COMPLETE_FINALIZE_ERROR.json').exists() and not (R/'COMMAND130_COMPLETE_METADATA_SYNCED.json').exists()
 save('COMMAND130_LOCK_GUARD_REPAIR_STARTED.json',dict(epoch=time.time(),trial_id='E1-G3-130-METADATA-PERSISTENT-LOCK-READER-REPAIR-01',original_failed_before_current_or_handoff_write=True,lock_files_persist_when_OS_lock_is_free=True,event_key_corrected_from_actual365_source=True,no_Git_training_or_budget_mutation=True))
 tree=ast.parse((D/'finalize_command130_coverage_decision_once.py').read_text(encoding='utf8'))
 assignment=next(x for x in ast.walk(tree) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='code' for t in x.targets))
 node=assignment.value
 while isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):node=node.func.value
 code=ast.literal_eval(node)
 assert "assert all(not p.exists() for p in locks)" in code
 code=code.replace('import hashlib,json,time,os','import hashlib,json,time,os,fcntl')
 code=code.replace('assert all(not p.exists() for p in locks)',"\nfor lock in locks:\n with lock.open('r') as handle:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(handle,fcntl.LOCK_UN)")
 code=code.replace("v['E1_G3_command_retention_365_execution_event']","v['E1_G3_command_retention_365_matched_execution_event']")
 code=code.replace('Path(REPORTS)','Path('+repr(E+'/reports')+')')
 compile(code,'<independent130-lock-and-event-reader-reviewed-CAS>','exec')
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 files={'E1_G3_COMMAND_RETENTION_130_COMPLETE_ACTUAL_REVIEW.json':sorted(R.glob('CANDIDATE_130_REVIEW_[0-9]*.json'))[-1],'E1_G3_COMMAND_RETENTION_130_SELECTED_SOURCE_MATCHED_REVIEW.json':sorted(R.glob('CANDIDATE_130_SELECTED_SOURCE_REVIEW_[0-9]*.json'))[-1],'E1_G3_COMMAND_RETENTION_130_COMPLETE_RETENTION_DECISION.json':R/'COMMAND130_COMPLETE_RETENTION_DECISION.json','E1_G3_COMMAND_RETENTION_130_SAMPLING_DIAGNOSIS.json':sorted(R.glob('COMMAND130_RETENTION_DIAGNOSIS_[0-9]*.json'))[-1],'E1_G3_COMMAND_RETENTION_130_COMPLETE_REPORT.md':R/'COMMAND130_COMPLETE_REPORT.md','NEXT_E1_G3_COMMAND_COVERAGE_REPAIR_WORK_ORDER_V3.json':R/'NEXT_E1_G3_COMMAND_COVERAGE_REPAIR_WORK_ORDER_V3.json','E1_G3_NEXT_FLAT_PURE_COVERAGE_CPU_COMPONENT_REVIEW.json':R/'NEXT_COMMAND_COVERAGE_CPU_REVIEW.json'}
 try:
  with c.open_sftp() as f:
   for n,p in files.items():assert f.open(E+'/reports/'+n).read()==p.read_bytes(),n
  _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
  v=json.loads(raw);v.update(original_guard_failure_preserved=True,only_previously_unexecuted_CAS_completed=True,persistent_lock_files_not_deleted_or_rewritten=True,files=[dict(name=n,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for n,p in files.items()]);p=save('COMMAND130_COMPLETE_METADATA_SYNCED.json',v)
  with c.open_sftp() as f:
   raw=p.read_bytes()
   with f.open(E+'/reports/E1_G3_COMMAND_RETENTION_130_COMPLETE_METADATA_SYNCED.json','wbx') as out:out.write(raw)
   assert f.open(E+'/reports/E1_G3_COMMAND_RETENTION_130_COMPLETE_METADATA_SYNCED.json').read()==raw
  print(json.dumps(dict(complete130_synced=True,original_prewrite_guard_refusal_preserved=True,persistent_OS_locks_checked_free=True,new_budget_seconds=0)))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:save('COMMAND130_LOCK_GUARD_REPAIR_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_completed_transactions=True));raise
