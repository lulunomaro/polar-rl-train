"""Unique388 combines actual completed save/restore proofs, then only300s formal."""
from pathlib import Path
import argparse,json,os,subprocess,time,traceback
import supervise_curb20_fresh_process_resume_once as previous
prior=previous.prior;D=Path(__file__).resolve().parent;R=D/'reports';CODE=D/'isaac/mod4';s=previous.s
read=previous.read;write=previous.write;identity=previous.identity;train=previous.train;fullsave=previous.fullsave;verify=previous.verify;phase=previous.phase
from curb20_completed_state_admission_cpu import admit
OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_FRESH_PROCESS_REVIEWED_20261011')
def wait_existing():
 previous.wait_existing();st=read(OLD/'reports/E1_STATE.json');att=read(OLD/'reports/E1_ATTENTION.json');assert not att['own_child_still_alive'] and att['active_segment'] is None
 for loc in [st['owner'],st['child'],read(OLD/'reports/E1_GUARDIAN_STARTED.json')]:
  a=identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
 assert s.q.base.budget_state()['active_segment'] is None
def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'E1_DISPATCH_STARTED.json').exists();verify();wait_existing();init=prior.source();proof=admit(D,fullsave)
 assert read(R/'CURB_SPLIT_FULLSTATE_CPU_PASSED.json')['passed'] and proof['passed']
 s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');wait_existing()
 write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),expert='E1_CURB',actual_split_fullstate_admission_passed=True,only_formal300s=True,no_GPU_preflight_repeated=True,new_budget_seconds=0))
 with (D/'guardian.log').open('x') as out:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 write('E1_GUARDIAN_STARTED.json',identity(g.pid))
 write('E1_COMPLETE_PPO_PREFLIGHT_PASSED.json',dict(epoch=time.time(),small=read(R/'REUSED_SMALL128.json'),big=read(R/'FRESH_PROCESS_BIG_CORE_VERIFIED.json'),weights_discarded=True,independent_actual_fullrestore_and_fullsave_admission=proof,all_old_failures_preserved=True,SDK_native_small_big_freshrestore_no_replay=True))
 saved,row=train(init,20000,10000,min(300,s.left()),'e1_CURB20_independent_observation',False)
 assert s.q.base.sha(init)==prior.SOURCE_SHA and saved.is_relative_to(D/'learning_logs')
 write('E1_CURB_OWNERSHIP_FINAL_VERIFIED.json',dict(epoch=time.time(),checkpoint=row['checkpoint'],source_SHA_preserved=True,E0_Wave_not_optimizer_or_save_targets=True))
 prior.publish(saved);write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(saved),expert='E1_CURB',all_courses_finished=False,requires_actual133_fourcase_review=True,automatic_more_PPO_disallowed=True));phase('E1_CURB20_independent_saved_review_ready',child=None)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:previous.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
