"""Ordinary supplement of the existing stage; no new trial, budget or GPU action."""
from pathlib import Path
import json,sys,subprocess,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;RET=W/'MOD4_3060_BODYFRAME_FIRST_RETENTION_20261014';REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'));import append_large_install_evidence_import_reviewed_git as cap
def main():
 dest=REPO/'history/evidence'/D.name/'positive21_monitor_readers_ordinary_supplement';assert not dest.exists() and not cap.g('status','--porcelain')
 old=cap.a.gitio.refs();cap.a.FOLDERS=(RET,D);rows,files=cap.capture_streaming(dest)
 subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(p.encode()+b'\0' for p in files),check=True,capture_output=True)
 cap.g('commit','-m','Append second BODY20k positive21 fullsave, retained skill comparisons, readers and hourly monitor actual receipts')
 cap.g('push','origin','HEAD');head=cap.g('rev-parse','HEAD');cap.a.verify(rows,old,head)
 print(json.dumps(dict(commit=head,actual_remote_main_and_tracked_SHA_verified=True,all_oldtags_preserved=len(old),sources=len(rows),ordinary_supplement_no_newtrial=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=D/'reports'/('SECOND_BODY_SUPPLEMENT_GIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(error=traceback.format_exc(),continue_existing_objects_only_no_record_tag_commit_replay=True),indent=2),encoding='utf8');raise
