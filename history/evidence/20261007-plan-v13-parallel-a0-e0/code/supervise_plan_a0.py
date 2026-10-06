"""Unique45min A0/E0 branch;3060 frozen calibration continues independently."""
from pathlib import Path
import argparse,json,os,shutil,subprocess,time,traceback
import supervise_world_spin as w
from plan_stage_contract import validate,SOURCE_SHA
D,R,P,ctl,base,helpers=w.D,w.R,w.P,w.ctl,w.base,w.helpers
E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');ER=E/'reports'
ENTRY=Path(__file__).resolve();STATE=R/'A0_STATE.json';DONE=R/'A0_SAVED_REVIEW_READY.json'
VERSION='plan_v13_S1A_A0_E0_parallel_v1'
w.STATE=STATE
def phase(name,**kw):w.phase(name,plan_id='MOD4-MOE-PLAN-001',plan_version='1.3',stage='S1A',variant='A0',expert='E0',**kw)
def verify():
 a=w.read(ER/'PLAN_APPROVAL.json');assert a['approved'] and a['version']=='1.3'
 assert base.sha(ER/'MOD4_MOE_MASTER_PLAN.md')==a['approved_plan_sha256']
 b=base.budget_state();assert b['owner_root']==str(P) and b['authorized_training_seconds']==828000
 for n,h in w.read(P/'reports/SPIN_SOURCE_FREEZE.json')['sha256'].items():
  p=Path(n);p=p if p.is_absolute() else P/p;actual=base.sha(p)
  if actual!=h:
   review=w.read(ER/'DISPLAY_SOURCE_REVIEW.json')
   assert n=='isaac/mod4/tui_spin_rate.py' and h==review['old_candidate_sha256'] and actual==review['current_P_sha256']
   assert review['other_top_level_AST_exact'] and not review['trainer_probe_and_non_UI_frozen_source_imports_display']
 for n,h in w.read(w.F)['sha256'].items():assert base.sha(D/n)==h,n
 original=w.read(R/'REUSED_F_SOURCE_FREEZE.json')
 for n,h in original['sha256'].items():assert base.sha(D/n)==h,n
 assert w.read(w.CODE/'env.json')==w.read(R/'E0_BASE_ENV.json')
 assert w.read(R/'EXPERT_CPU_CONTRACT.json')['pass_']
 assert w.read(R/'REUSED_PREFLIGHT.json')['all_original_runtime_files_exact']
def status(stage=None,**kw):
 kw.pop('scope',None);b=base.budget_state()
 base.status(**({'stage':stage} if stage else {}),supervisor_pid=os.getpid(),active_code_root=str(D),
  plan_id='MOD4-MOE-PLAN-001',plan_version='1.3',plan_stage='S1A',architecture_variant='A0',active_expert='E0',
  profile='white_v3',stand_fraction=.1,straight_fraction=.4,spin_fraction=.3,moving_spin_fraction=.2,
  world_progress_goal_m_s=.5,moving_yaw_max_rad_s=2.,yaw_limit_rad_s=12.566370614359172,
  canonical_budget=str(ctl.CANONICAL),budget_seconds=b['authorized_training_seconds'],authorized_training_seconds=b['authorized_training_seconds'],
  scope='Independent E0 single-frame A0 branch on validated flat tasks, parallel3060 frozen calibration; no new DR/interface/terrain',**kw)
def freeze_run(run):
 out=run/'rolling_source_freeze.json'
 if out.exists():return
 f=w.read(w.F)
 for n,h in f['sha256'].items():
  assert base.sha(D/n)==h;q=run/'plan_a0_source_snapshot'/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/n,q)
 base.atomic_json(out,dict(candidate_root=str(D),sha256=f['sha256'],controller_version=VERSION,expert='E0',variant='A0',
  plan_sha256=w.read(ER/'PLAN_APPROVAL.json')['approved_plan_sha256'],original_F167_runtime_byte_exact=True,
  task_DR_reward_hardware_physics_PPO_observation_reset_unchanged=True))
w.verify=ctl.verify=verify;w.status=ctl.status=status;w.rate.freeze_run=freeze_run
def guardian(owner,ticks):
 while True:
  p=helpers.identity(owner);b=base.budget_state();a=b.get('active_segment')
  if a:
   trainer=helpers.identity(a['pid']);own=trainer and trainer['cwd']==str(P) and str(w.CODE/'train_mod4_ppo.py') in trainer['argv']
   remaining=b['authorized_training_seconds']-b['charged_training_seconds']-max(0,time.time()-a['accounted_through_epoch'])
   owner_lost=not p or p['state']=='Z' or str(p['start_ticks'])!=str(ticks)
   if own and (remaining<=0 or owner_lost):
    try:
     run=w.rate.trainer_run(P/'logs',trainer['pid']);stop=run/'STOP_AFTER_SAVE'
     if not stop.exists():stop.write_text('Plan budget or controller protection: complete full save and stop.\n')
     if owner_lost:base.atomic_json(R/'A0_OWNER_LOST_ATTENTION.json',dict(epoch=time.time(),trainer=trainer,active_segment=a,canonical_not_cleared=True))
    except AssertionError:pass
  if not a and (DONE.exists() or not p or p['state']=='Z' or str(p['start_ticks'])!=str(ticks)):return
  time.sleep(15)
def controller():
 import torch;torch.set_num_threads(1)
 assert not (R/'A0_STARTED.json').exists() and not STATE.exists(),'Unique entry executed; inspect receipt'
 helpers.acquire(P/'autonomy_controller.lock');helpers.acquire(ctl.CANONICAL.parent/'native_floor_supervisor.lock')
 ctl.S=w.read(ctl.STATE_PATH);base.STATE.update(w.read(P/'status.json'));ctl.idle();verify()
 for pid in [608553,608593,608594,624645]:
  p=helpers.identity(pid);assert not p or p['state']=='Z','Old authority still active'
 hand=w.read(R/'A0_SOURCE_CONTRACT.json');source=Path(hand['source']['path']);info=base.checkpoint(source)
 assert info==hand['source'] and info['sha256']==SOURCE_SHA
 validate(w.read(ER/'PLAN_APPROVAL.json'),base.sha(ER/'MOD4_MOE_MASTER_PLAN.md'),base.budget_state(),info,w.read(R/'EXPERT_CPU_CONTRACT.json'))
 assert not ctl.S.get('active_training')
 ctl.S.update(profile='white_v3',chosen_checkpoint=str(source));ctl.persist()
 owner=helpers.identity(os.getpid());start_budget=base.budget_state();before=start_budget['charged_training_seconds']
 base.atomic_json(R/'A0_STARTED.json',dict(epoch=time.time(),owner=owner,source=info,plan_version='1.3',plan_sha256=w.read(ER/'PLAN_APPROVAL.json')['approved_plan_sha256'],
  first_block_seconds=2700,S1A_total_learning_cap_seconds=21600,S0E_calibration_blocks_this_baseline=False,old_entries_not_resumed=True))
 with (D/'guardian_a0.log').open('x') as log:
  g=subprocess.Popen([base.PY,str(ENTRY),'--guardian',str(os.getpid()),str(owner['start_ticks'])],cwd=P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 base.atomic_json(R/'A0_GUARDIAN_STARTED.json',helpers.identity(g.pid))
 try:
  phase('bounded_A0_E0_learning',owner=owner,source=info,duration_s=min(2700,ctl.remaining()),parallel_S0E=True)
  last=ctl.training(source,'moe_plan_S1A_A0_E0_learning',duration=min(2700,ctl.remaining()))
  saved=base.checkpoint(last);run=last.parent;freeze_run(run);actual_budget=base.budget_state()
  assert actual_budget['active_segment'] is None and not ctl.S.get('active_training')
  review=dict(epoch=time.time(),checkpoint=saved,source=info,run=str(run),PID_bound_receipt=w.read(run/'latest_complete.json'),
   learning_seconds=actual_budget['charged_training_seconds']-before,actual_additional_iterations=saved['iteration_stored']-info['iteration_stored'],
   same_seed=20260928,count=20000,steps_per_env=24,full_optimizer_std_resume=True,source_anchors_unchanged=base.sha(source)==SOURCE_SHA,
   frozen_evaluation_required=True,S0E_formal_platform_review_still_required=True,MoE_or_history_selected=False,all_curricula_finished=False,
   next='Publish exact A0 frozen tasks on calibrated3060; implement matchedA1/A2 from original23509, not from this trainedA0',actual_budget=actual_budget)
  base.atomic_json(DONE,review);phase('A0_saved_review_ready',**review);status('S1A_A0_saved_review_ready',training_pid=None,evaluation_pid=None,final_evaluation=review)
 except BaseException:
  base.atomic_json(R/'A0_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),active_segment=base.budget_state().get('active_segment'),all_weights_retained=True))
  phase('attention_required',reason=traceback.format_exc());raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 if a.guardian:guardian(int(a.guardian[0]),a.guardian[1])
 else:controller()
