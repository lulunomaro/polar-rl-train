"""Append post-stage saved receipt; no second experiment/tag or runtime action."""
from pathlib import Path
import json,subprocess,sys,time
D=Path(__file__).resolve().parent;W=D.parent;REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
cap.a.FOLDERS=(D,)
def main():
 receipt=json.loads((D/'reports/S5_FIRST_MATCHED35_STAGE_GIT_RECORDED_ACTUAL.json').read_bytes())
 assert receipt['actual_remote_main_tag_peeled_and_oldtags_verified'] and cap.g('rev-parse','HEAD')==receipt['commit'] and not cap.g('status','--porcelain')
 dest=REPO/'history/evidence'/D.name/'ordinary_first_matched35_stage_receipt_v1';assert not dest.exists()
 old=cap.a.gitio.refs();rows,files=cap.capture_streaming(dest)
 subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(v.encode()+b'\0' for v in files),check=True,capture_output=True)
 cap.g('commit','-m','Append first S5 matched35 stage receipt and complete evidence index')
 head=cap.g('rev-parse','HEAD');cap.g('push','origin','HEAD');cap.a.verify(rows,old,head)
 print(json.dumps(dict(epoch=time.time(),ordinary_commit=head,actual_remote_main_and_all_oldtags_verified=True,all_old_tag_objects_and_peeled_preserved=len(old),actual_tracked_SHA_verified=True,saved_sources=len(rows),new_trial_or_tag_created=False,large_originals_retained=True)))
if __name__=='__main__':main()
