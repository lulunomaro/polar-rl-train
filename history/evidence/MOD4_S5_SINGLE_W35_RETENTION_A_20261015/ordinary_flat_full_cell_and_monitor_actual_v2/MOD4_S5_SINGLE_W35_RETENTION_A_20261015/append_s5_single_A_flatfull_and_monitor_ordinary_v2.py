"""Second ordinary evidence snapshot; existing trial/tag and running owner intact."""
from pathlib import Path
import importlib.util,json,subprocess,time
D=Path(__file__).resolve().parent;REPO=D.parent/'polar-rl-train'
p=D/'archive_s5_single_A_native_flat_and_finite_start_actual_once.py';s=importlib.util.spec_from_file_location('S5_A_capture_without_record_v2',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 assert json.loads((D/'reports/S5_SINGLE_A_FLAT_FULL_COMPLETE_MONITOR_TOML_UTF8_ACTUAL_VERIFIED.json').read_bytes())['passed']
 assert json.loads((D/'reports/S5_SINGLE_A_FLAT_FULL1500_ACTUAL_MATCHED_B_C_LIMITED_CELL_REVIEW.json').read_bytes())['passed_first_flat_single_A_B_C_matched_cell']
 assert m.cap.g('rev-parse','HEAD')=='fd140d6e3e2ab963a554fbd73f98b7a8d5220dce' and not m.cap.g('status','--porcelain')
 dest=REPO/'history/evidence'/D.name/'ordinary_flat_full_cell_and_monitor_actual_v2';assert not dest.exists()
 old=m.cap.a.gitio.refs();rows,files=m.capture_saved_completed_and_metadata(dest)
 subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(x.encode()+b'\0' for x in files),capture_output=True,check=True)
 m.cap.g('commit','-m','Append complete S5 flat three-way cell and actual finite-owner monitor')
 head=m.cap.g('rev-parse','HEAD');m.cap.g('push','origin','HEAD');m.cap.a.verify(rows,old,head)
 print(json.dumps(dict(epoch=time.time(),ordinary_commit=head,actual_remote_main_and_all_oldtags_verified=True,all_old_tag_objects_and_peeled_preserved=len(old),actual_tracked_SHA_verified=True,saved_sources=len(rows),new_trial_or_tag_created=False,large_originals_retained=True,later_finite_results_require_ordinary_supplement=True)))
if __name__=='__main__':main()
