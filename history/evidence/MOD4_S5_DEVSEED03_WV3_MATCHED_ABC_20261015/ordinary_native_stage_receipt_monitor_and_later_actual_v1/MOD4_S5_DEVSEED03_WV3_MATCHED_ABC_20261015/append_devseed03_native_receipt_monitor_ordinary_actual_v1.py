"""Append new stage receipt and saved monitor/results; never record or retag."""
from pathlib import Path
import importlib.util,json,subprocess,time
D=Path(__file__).resolve().parent;REPO=D.parent/'polar-rl-train'
p=D/'archive_devseed03_native_fixed15_stage_actual_once.py';s=importlib.util.spec_from_file_location('dev03_pure_capture_no_record',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 assert json.loads((D/'reports/DEVSEED03_STAGE_REMOTE_MONITOR_TOML_UTF8_ACTUAL_VERIFIED_V2.json').read_bytes())['passed']
 assert json.loads((D/'reports/DEVSEED03_NATIVE_AND_FIXED15_STAGE_GIT_RECORDED_ACTUAL.json').read_bytes())['actual_remote_main_tag_peeled_and_alloldtags_verified']
 assert m.cap.g('rev-parse','HEAD')=='099fab836c6eaf88c56de75a3387c7e1f2ae1407' and not m.cap.g('status','--porcelain')
 dest=REPO/'history/evidence'/D.name/'ordinary_native_stage_receipt_monitor_and_later_actual_v1';assert not dest.exists();old=m.cap.a.gitio.refs();rows,files=m.capture_saved_completed_and_metadata(dest)
 subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(x.encode()+b'\0' for x in files),capture_output=True,check=True)
 m.cap.g('commit','-m','Append S5 second-development-seed native receipt and exact hourly monitor')
 head=m.cap.g('rev-parse','HEAD');m.cap.g('push','origin','HEAD');m.cap.a.verify(rows,old,head)
 print(json.dumps(dict(epoch=time.time(),ordinary_commit=head,actual_remote_main_and_all_oldtags_verified=True,all_old_tag_objects_and_peeled_preserved=len(old),actual_tracked_SHA_verified=True,saved_sources=len(rows),new_trial_or_tag_created=False,large_originals_retained=True,later_finite_results_require_ordinary_supplement=True)))
if __name__=='__main__':main()
