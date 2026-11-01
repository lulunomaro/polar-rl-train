"""Unique isolated fresh-process restore admission, then only300s formal."""
from pathlib import Path
import argparse,json,os,subprocess,time,traceback
import supervise_curb20_environment_view_once as previous
prior=previous.prior;D=Path(__file__).resolve().parent;R=D/'reports';CODE=D/'isaac/mod4';s=previous.s
read=previous.read;write=previous.write;identity=previous.identity;train=previous.train;fullsave=previous.fullsave;runtime=previous.runtime;verify=previous.verify;phase=previous.phase
OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENVIRONMENT_VIEW_20261011')
def wait_existing():
 previous.wait_existing();st=read(OLD/'reports/E1_STATE.json');att=read(OLD/'reports/E1_ATTENTION.json');assert not att['own_child_still_alive'] and att['active_segment'] is None
 for loc in [st['owner'],st['child'],read(OLD/'reports/E1_GUARDIAN_STARTED.json')]:
  a=identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
 assert not previous.trainers() and s.q.base.budget_state()['active_segment'] is None
def guardian(owner,ticks):
 previous.guardian(owner,ticks)
def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'E1_DISPATCH_STARTED.json').exists();verify();wait_existing();init=prior.source()
 assert read(R/'CURB_FRESH_PROCESS_CPU_PASSED.json')['passed']
 s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');wait_existing()
 write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),expert='E1_CURB',only_new_fresh_process_full_resume_probe_then300s=True,SDK_native_small_big_PPO_exact_reused=True,no_new_budget=True))
 with (D/'guardian.log').open('x') as out:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 write('E1_GUARDIAN_STARTED.json',identity(g.pid))
 big=read(R/'FRESH_PROCESS_BIG_CORE_VERIFIED.json');e=runtime();e['RM_CURB_FRESH_RESUME_ONLY']='1';e['RM_CURB_PREFLIGHT_SELF_RESUME']='0'
 args=[s.q.base.PY,str(CODE/'probe_curb20_fresh_process_full_resume.py'),'--headless','--num_envs','20000','--max_iterations','0','--steps_per_env','24','--seed','20260928','--learning_rate','.0001','--init_checkpoint',big['checkpoint']['path'],'--log_root',str(D/'fresh_process_resume'),'--run_name','curb_fresh_full_resume_no_learning']
 with (D/'fresh_process_resume.log').open('x') as out:p=subprocess.Popen(args,cwd=s.q.P,env=e,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 s.LIVE=p;phase('CURB_fresh_process_full_resume_admission',child=identity(p.pid),source=big['checkpoint'],no_PPO=True,active_log=str(D/'fresh_process_resume.log'))
 while p.poll() is None:time.sleep(1)
 s.LIVE=None;assert p.returncode==0 and 'Traceback (most recent call last)' not in (D/'fresh_process_resume.log').read_text()
 proof=read(D/'fresh_process_resume/FRESH_PROCESS_SAME_CURB_FULL_RESUME_PASSED.json');assert proof['passed'] and proof['pid']==p.pid and proof['actual_control_steps']==proof['actual_additional_PPO_updates']==0
 cp=proof['own_complete_new_episode_save'];assert s.q.base.sha(Path(cp['path']))==cp['sha256'];fullsave(Path(cp['path']))
 write('CURB_FRESH_PROCESS_SAME_SCOPE_PASSED.json',proof)
 write('E1_COMPLETE_PPO_PREFLIGHT_PASSED.json',dict(epoch=time.time(),small=read(R/'REUSED_SMALL128.json'),big=big,weights_discarded=True,old384_postlearn_sameenv_failure_retained=True,new_fresh_process_sameCURB_full_resume_passed=proof,SDK_native_small_big_PPO_not_repeated=True))
 saved,row=train(init,20000,10000,min(300,s.left()),'e1_CURB20_independent_observation',False)
 assert s.q.base.sha(init)==prior.SOURCE_SHA and saved.is_relative_to(D/'learning_logs')
 write('E1_CURB_OWNERSHIP_FINAL_VERIFIED.json',dict(epoch=time.time(),checkpoint=row['checkpoint'],source_SHA_preserved=True,E0_Wave_not_optimizer_or_save_targets=True))
 prior.publish(saved);write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(saved),expert='E1_CURB',all_courses_finished=False,requires_actual133_fourcase_review=True,automatic_more_PPO_disallowed=True));phase('E1_CURB20_independent_saved_review_ready',child=None)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
