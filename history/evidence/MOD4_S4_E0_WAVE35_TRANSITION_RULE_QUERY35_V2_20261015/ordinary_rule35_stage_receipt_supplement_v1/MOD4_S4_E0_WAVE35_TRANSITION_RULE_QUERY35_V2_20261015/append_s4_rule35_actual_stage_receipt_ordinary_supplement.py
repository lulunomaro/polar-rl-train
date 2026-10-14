"""Ordinary evidence supplement only; the real stage objects already exist."""
from pathlib import Path
import sys,json,time,subprocess
D=Path(__file__).resolve().parent;W=D.parent;REPO=W/'polar-rl-train'
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
import append_large_install_evidence_import_reviewed_git as cap
cap.a.FOLDERS=(D,)
def main():
 receipt=json.loads((D/'reports/S4_RULE35_FULLROUTE_AND_OBJECTIVE_STAGE_GIT_RECORDED_ACTUAL.json').read_bytes())
 assert receipt['actual_remote_main_tag_peeled_verified'] and not cap.g('status','--porcelain')
 dest=REPO/'history/evidence'/D.name/'ordinary_rule35_stage_receipt_supplement_v1';assert not dest.exists()
 old=cap.a.gitio.refs();rows,files=cap.capture_streaming(dest)
 subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(s.encode()+b'\0' for s in files),capture_output=True,check=True)
 cap.g('commit','-m','Append S4 original35 rule fullroute and query repair stage verification receipt')
 cap.g('push','origin','HEAD')
 head=cap.g('rev-parse','HEAD');cap.a.verify(rows,old,head)
 print(json.dumps(dict(epoch=time.time(),ordinary_supplement_commit=head,actual_remote_main_verified=True,all_old_tag_objects_peeled_preserved=len(old),source_stage_tag=receipt['tag'],source_stage_peeled_commit=receipt['commit'],source_stage_tagobject=receipt['tagobject'],actual_tracked_SHA_verified=True,saved_sources=len(rows),no_record_tag_training_budget_or_GPU_replay=True,final_verification_tool_output_only_no_infinite_receipt_loop=True)))
if __name__=='__main__':main()
