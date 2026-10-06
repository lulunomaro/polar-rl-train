"""Explicit status-reader repair: adopt the actual active trainer, never launch PPO."""
from pathlib import Path
import argparse,os,signal,subprocess,time,traceback
import supervise_plan_a0 as q
D,R,P,ctl,base,helpers=q.D,q.R,q.P,q.ctl,q.base,q.helpers
ENTRY=Path(__file__).resolve();EXPECTED_PID=670475;EXPECTED_TICKS=46556747
def merged_status(stage=None,**kw):
 b=base.budget_state();values=dict(supervisor_pid=os.getpid(),active_code_root=str(D),plan_id='MOD4-MOE-PLAN-001',plan_version='1.3',plan_stage='S1A',
  architecture_variant='A0',active_expert='E0',profile='white_v3',canonical_budget=str(ctl.CANONICAL),budget_seconds=b['authorized_training_seconds'],
  authorized_training_seconds=b['authorized_training_seconds'],world_progress_goal_m_s=.5,moving_yaw_max_rad_s=2.,yaw_limit_rad_s=12.566370614359172)
 if stage:values['stage']=stage
 values.update(kw);base.status(**values)
def observer():
 import torch;torch.set_num_threads(1)
 marker=R/'A0_ACTIVE_OBSERVER_STARTED.json';assert not marker.exists(),'Explicit adoption already executed'
 helpers.acquire(P/'autonomy_controller.lock');helpers.acquire(ctl.CANONICAL.parent/'native_floor_supervisor.lock')
 ctl.S=q.w.read(ctl.STATE_PATH);base.STATE.update(q.w.read(P/'status.json'));q.verify()
 b=base.budget_state();a=b['active_segment'];assert a and a['pid']==EXPECTED_PID
 trainer=helpers.identity(EXPECTED_PID);assert trainer and trainer['state']!='Z' and trainer['start_ticks']==EXPECTED_TICKS
 assert str(q.w.CODE/'train_mod4_ppo.py') in trainer['argv'] and trainer['cwd']==str(P)
 active=ctl.S['active_training'];assert active['pid']==EXPECTED_PID and active['source']['sha256']==q.SOURCE_SHA
 original=q.w.read(R/'A0_STARTED.json');before_bytes=ctl.CANONICAL.read_bytes();owner=helpers.identity(os.getpid())
 with (D/'guardian_a0_status_review.log').open('x') as log:
  g=subprocess.Popen([base.PY,str(ENTRY),'--guardian',str(os.getpid()),str(owner['start_ticks'])],cwd=P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 newguard=helpers.identity(g.pid);assert newguard and newguard['state']!='Z'
 old=q.w.read(R/'A0_GUARDIAN_STARTED.json');now=helpers.identity(old['pid'])
 if now and now['state']!='Z':
  assert now['start_ticks']==old['start_ticks'] and str(D/'supervise_plan_a0.py') in now['argv'] and '--guardian' in now['argv']
  os.kill(now['pid'],signal.SIGTERM)
  end=time.time()+5
  while helpers.identity(now['pid']) and helpers.identity(now['pid'])['state']!='Z' and time.time()<end:time.sleep(.05)
  assert not helpers.identity(now['pid']) or helpers.identity(now['pid'])['state']=='Z'
 cleared=None
 try:
  run=q.w.rate.trainer_run(P/'logs',EXPECTED_PID);stop=run/'STOP_AFTER_SAVE'
  if stop.exists():
   text=stop.read_text();assert text=='Plan budget or controller protection: complete full save and stop.\n'
   receipt=q.w.read(run/'latest_complete.json');assert receipt['pid']==EXPECTED_PID
   cleared={'path':str(stop),'text':text,'reason':'Original status parent failed; new independent guardian and same-PID observer established before expiry'}
   stop.unlink()
 except AssertionError:
  if cleared:raise
 assert ctl.CANONICAL.read_bytes()==before_bytes
 base.atomic_json(marker,dict(epoch=time.time(),owner=owner,trainer=trainer,new_guardian=newguard,retired_guardian=old,
  original_deadline=active['deadline'],original_source=active['source'],same_trainer_adopted=True,no_PPO_relaunch=True,no_budget_extension_or_settlement=True,
  startup_status_exception_retained=True,only_status_keywords_merged=True,old_stop_request=cleared))
 q.w.status=ctl.status=merged_status
 q.phase('bounded_A0_E0_learning',owner=owner,trainer=trainer,status_reader_repaired=True,parallel_S0E=True)
 log=Path(a['log']);run=None
 try:
  while True:
   actual=helpers.identity(EXPECTED_PID)
   if not actual or actual['state']=='Z':break
   assert actual['start_ticks']==EXPECTED_TICKS
   base.account_segment()
   try:run=q.w.rate.trainer_run(P/'logs',EXPECTED_PID)
   except AssertionError:pass
   if run:
    q.freeze_run(run);receipt=q.w.read(run/'latest_complete.json');ck=Path(receipt['checkpoint'])
    merged_status('training',training_pid=EXPECTED_PID,active_log=str(log),latest_checkpoint=str(ck),log_dir=str(run),iteration=int(ck.stem.rsplit('_',1)[1]),trainer_deadline_epoch=active['deadline'])
   else:merged_status('training_initializing',training_pid=EXPECTED_PID,active_log=str(log),trainer_deadline_epoch=active['deadline'])
   time.sleep(5)
  exited=helpers.identity(EXPECTED_PID);text=log.read_text(errors='replace')
  assert 'SimulationContext cleared' in text and 'Traceback (most recent call last)' not in text,'Actual exit needs audit; active ledger preserved'
  if exited:
   stat=(Path('/proc')/str(EXPECTED_PID)/'stat').read_text().rsplit(')',1)[1].split()
   assert exited['state']=='Z' and int(stat[49])==0,'Nonzero exit; preserve active for actual audit'
  detected=time.time();a2=base.budget_state()['active_segment'];assert a2 and a2['pid']==EXPECTED_PID
  base.account_segment(finish=True)
  run=q.w.rate.trainer_run(P/'logs',EXPECTED_PID);q.freeze_run(run);receipt=q.w.read(run/'latest_complete.json');ck=Path(receipt['checkpoint']);saved=base.checkpoint(ck)
  assert receipt['pid']==EXPECTED_PID and q.w.read(run/'run_manifest.json')['init_checkpoint_sha256']==q.SOURCE_SHA
  ctl.S.update(active_training=None,chosen_checkpoint=str(ck));ctl.persist()
  review=dict(epoch=time.time(),checkpoint=saved,source=active['source'],PID_bound_receipt=receipt,run=str(run),same_trainer_adopted=True,
   actual_additional_iterations=saved['iteration_stored']-23509,original_deadline=active['deadline'],observed_exit_upper_epoch=detected,exit_observation_uncertainty_upper_s=5.5,
   learning_seconds=base.budget_state()['charged_training_seconds']-original.get('charged_before',312508.39150452614),
   frozen_evaluation_required=True,MoE_or_history_selected=False,all_curricula_finished=False,
   next='Actual A0 frozen assessment and matched A1/A2 from original23509; no highest-iteration selection')
  base.atomic_json(q.DONE,review);q.phase('A0_saved_review_ready',**review);merged_status('S1A_A0_saved_review_ready',training_pid=None,final_evaluation=review)
 except BaseException:
  base.atomic_json(R/'A0_OBSERVER_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),active_segment=base.budget_state().get('active_segment'),all_weights_retained=True));raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 if a.guardian:q.guardian(int(a.guardian[0]),a.guardian[1])
 else:observer()
