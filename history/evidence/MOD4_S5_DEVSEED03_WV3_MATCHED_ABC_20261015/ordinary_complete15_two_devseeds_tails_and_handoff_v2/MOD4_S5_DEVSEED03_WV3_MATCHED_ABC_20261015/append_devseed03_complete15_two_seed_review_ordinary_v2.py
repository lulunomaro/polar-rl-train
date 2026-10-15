"""Append new stage receipt and saved monitor/results; never record or retag."""
from pathlib import Path
import importlib.util,json,subprocess,time
D=Path(__file__).resolve().parent;REPO=D.parent/'polar-rl-train'
p=D/'archive_devseed03_native_fixed15_stage_actual_once.py';s=importlib.util.spec_from_file_location('dev03_pure_capture_no_record',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 assert json.loads((D/'reports/DEVSEED03_COMPLETE15_ACTUAL_CIM_HANDOFF_CPU.json').read_bytes())['actual_owner_absent']
 assert json.loads((D/'reports/DEVSEED03_COMPLETE15_TWO_DEVSEED_THREEWAY_SCOPE_TAIL_COST_CPU_ACTUAL.json').read_bytes())['actual_second_development_seed_threeway_complete']
 assert m.cap.g('rev-parse','HEAD')=='5ea503154cb791259d3c9aadc4b1bc8447e3188f' and not m.cap.g('status','--porcelain')
 dest=REPO/'history/evidence'/D.name/'ordinary_complete15_two_devseeds_tails_and_handoff_v2';assert not dest.exists();old=m.cap.a.gitio.refs();rows,files=m.capture_saved_completed_and_metadata(dest)
 subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(x.encode()+b'\0' for x in files),capture_output=True,check=True)
 m.cap.g('commit','-m','Append complete S5 second development seed, gate world regression and actual transport handoff')
 head=m.cap.g('rev-parse','HEAD');m.cap.g('push','origin','HEAD');m.cap.a.verify(rows,old,head)
 print(json.dumps(dict(epoch=time.time(),ordinary_commit=head,actual_remote_main_and_all_oldtags_verified=True,all_old_tag_objects_and_peeled_preserved=len(old),actual_tracked_SHA_verified=True,saved_sources=len(rows),new_trial_or_tag_created=False,large_originals_retained=True,complete15_and_two_devseed_review_captured=True)))
if __name__=='__main__':main()
