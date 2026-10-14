"""Append post-stage actual complete Wave, regressions, readers and app receipts."""
from pathlib import Path
import sys, subprocess, time, json, traceback
D=Path(__file__).resolve().parent;W=D.parent;REPO=W/'polar-rl-train'
E=W/'MOD4_3060_BODYFRAME_PHASE_FINAL_FULL80_20261015';RET=W/'MOD4_3060_BODYFRAME_PHASE_FINAL_RETENTION_20261015'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'));import append_large_install_evidence_import_reviewed_git as cap
def main():
 assert not cap.g('status','--porcelain')
 direct=json.loads((E/'reports/PHASE_FINAL_DIRECT_F516_ORIGINAL_FULL80_PREFIX_ACTUAL_REVIEW.json').read_bytes());assert direct['passed'] and direct['new_forward']==22 and direct['new_reverse']==26
 dest=REPO/'history/evidence'/D.name/'post_stage_wave22_26_regression_monitor_ordinary';assert not dest.exists()
 old=cap.a.gitio.refs();cap.a.FOLDERS=(D,E,RET);rows,files=cap.capture_streaming(dest)
 subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in files),check=True,capture_output=True)
 cap.g('commit','-m','Append own phase-final Wave22-26 regression, protected f516 priority, finite retention dispatch and actual monitor reader receipts')
 cap.g('push','origin','HEAD');head=cap.g('rev-parse','HEAD');cap.a.verify(rows,old,head)
 print(json.dumps(dict(commit=head,actual_remote_main_tracked_verified=True,all_oldtag_objects_peeled_preserved=len(old),sources=len(rows),new_Wave_regression_and_original_reader_rejection_preserved=True,finite_retention_future_results_not_claimed=True,large_originals_retained_path_size_SHA=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (D/'reports'/('PHASE_FINAL_ORDINARY_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),continue_existing_objects_only_no_commit_or_capture_replay=True),indent=2),encoding='utf8');raise
