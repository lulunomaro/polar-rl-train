"""Post-stage receipt and later completed evidence; no repeated trial/tag."""
from pathlib import Path
import importlib.util,json,subprocess,time
D=Path(__file__).resolve().parent;REPO=D.parent/'polar-rl-train'
p=D/'archive_s5_single_A_native_flat_and_finite_start_actual_once.py'
s=importlib.util.spec_from_file_location('S5_A_actual_capture_helpers_only',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 receipt=json.loads((D/'reports/S5_SINGLE_A_NATIVE_AND_FINITE_STAGE_GIT_RECORDED_ACTUAL.json').read_bytes());assert receipt['actual_remote_main_tag_peeled_and_oldtags_verified']
 assert m.cap.g('rev-parse','HEAD')==receipt['commit'] and not m.cap.g('status','--porcelain')
 dest=REPO/'history/evidence'/D.name/'ordinary_native_stage_receipt_and_later_actual_v1';assert not dest.exists()
 old=m.cap.a.gitio.refs();rows,files=m.capture_saved_completed_and_metadata(dest)
 subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(x.encode()+b'\0' for x in files),capture_output=True,check=True)
 m.cap.g('commit','-m','Append actual S5 single-policy native stage receipt and bounded finite evidence')
 head=m.cap.g('rev-parse','HEAD');m.cap.g('push','origin','HEAD');m.cap.a.verify(rows,old,head)
 print(json.dumps(dict(epoch=time.time(),ordinary_commit=head,actual_remote_main_and_all_oldtags_verified=True,all_old_tag_objects_and_peeled_preserved=len(old),actual_tracked_SHA_verified=True,saved_sources=len(rows),new_trial_or_tag_created=False,large_originals_retained=True,later_finite_results_still_require_supplement=True)))
if __name__=='__main__':main()
