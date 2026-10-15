"""Second ordinary evidence snapshot; existing trial/tag and running owner intact."""
from pathlib import Path
import importlib.util,json,subprocess,time
D=Path(__file__).resolve().parent;REPO=D.parent/'polar-rl-train'
p=D/'archive_s5_single_A_native_flat_and_finite_start_actual_once.py';s=importlib.util.spec_from_file_location('S5_A_capture_without_record_v2',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
 assert json.loads((D/'reports/S5_SINGLE_A_FIXED_SIX_COMPLETE_ACTUAL_CIM_HANDOFF_CPU.json').read_bytes())['actual_owner_absent']
 assert json.loads((D/'reports/S5_FOUR_DOMAIN_THREEWAY_COMPLETE_LIMITED_SCOPE_TAIL_COST_AND_NEXT_DEVSEED_CPU_ACTUAL.json').read_bytes())['actual_four_domain_single_rule_gate_cellset_complete']
 assert m.cap.g('rev-parse','HEAD')=='4d44392af8cf58538e968af3df867c714fabdb0c' and not m.cap.g('status','--porcelain')
 dest=REPO/'history/evidence'/D.name/'ordinary_complete_six_four_domain_review_actual_v3';assert not dest.exists()
 old=m.cap.a.gitio.refs();rows,files=m.capture_saved_completed_and_metadata(dest)
 subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b''.join(x.encode()+b'\0' for x in files),capture_output=True,check=True)
 m.cap.g('commit','-m','Append completed S5 A retention six, full four-domain tails and actual owner handoff')
 head=m.cap.g('rev-parse','HEAD');m.cap.g('push','origin','HEAD');m.cap.a.verify(rows,old,head)
 print(json.dumps(dict(epoch=time.time(),ordinary_commit=head,actual_remote_main_and_all_oldtags_verified=True,all_old_tag_objects_and_peeled_preserved=len(old),actual_tracked_SHA_verified=True,saved_sources=len(rows),new_trial_or_tag_created=False,large_originals_retained=True,complete_six_and_four_domain_review_captured=True)))
if __name__=='__main__':main()
