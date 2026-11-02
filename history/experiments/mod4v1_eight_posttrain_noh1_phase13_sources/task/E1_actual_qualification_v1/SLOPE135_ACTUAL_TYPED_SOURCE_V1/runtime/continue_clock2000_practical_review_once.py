"""S0P selected clock: real retention readback, full PPO, then approved A0."""
from pathlib import Path
import argparse,json,math,os,shutil,subprocess,time,traceback
import supervise_world_spin as w
from physics_clock import validate_clock
D=Path(__file__).resolve().parent;R=D/'reports';P=w.P;ctl=w.ctl;base=w.base;helpers=w.helpers
ER=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports')
C=Path('/home/egde/rl_candidates/MOD4_PHYSICS_CLOCK_REVIEW_20261007')
SOURCE=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/logs/2026-10-06_05-04-08_auto_0282_physical_dr_stage1_learning_cap12.5664_white_v3/model_23509.pt')
SHA='2f82374fe07a849dbbaeabbf8dd34b20d0df8da789f2ebc2be3e688a1b24498a'
w.STATE=R/'SELECTED_CLOCK_STATE.json'
def write(n,v):base.atomic_json(R/n,v)
def verify():
 a=w.read(ER/'PLAN_APPROVAL.json');assert a['approved'] and a['version']=='1.5' and {'S0P','S1A'}.issubset(a['allowed_stages'])
 assert base.sha(ER/'MOD4_MOE_MASTER_PLAN.md')==a['approved_plan_sha256']
 assert base.budget_state()['authorized_training_seconds']==828000 and base.sha(SOURCE)==SHA
 for n,h in w.read(R/'SOURCE_FREEZE.json')['sha256'].items():assert base.sha(D/n)==h,n
 for n,h in w.read(P/'reports/SPIN_SOURCE_FREEZE.json')['sha256'].items():
  p=Path(n);p=p if p.is_absolute() else P/p
  if base.sha(p)!=h:
   review=w.read(ER/'DISPLAY_SOURCE_REVIEW.json')
   assert n=='isaac/mod4/tui_spin_rate.py' and h==review['old_candidate_sha256'] and base.sha(p)==review['current_P_sha256']
   assert review['other_top_level_AST_exact'] and not review['trainer_probe_and_non_UI_frozen_source_imports_display']
 cfg=w.read(w.CODE/'env.json');assert cfg['RM_MILD_DR_PROFILE']=='white_v3' and cfg['RM_KEEP_STD']=='1'
 if 'RM_PHYSICS_DT_S' in cfg:validate_clock(float(cfg['RM_PHYSICS_DT_S']))
def status(stage=None,**kw):
 b=base.budget_state();v=dict(stage=stage,supervisor_pid=os.getpid(),active_code_root=str(D),plan_id='MOD4-MOE-PLAN-001',plan_version='1.5',plan_stage='S0P/S1A',
  active_expert='E0',architecture_variant='A0',canonical_budget=str(ctl.CANONICAL),budget_seconds=b['authorized_training_seconds'],authorized_training_seconds=b['authorized_training_seconds'],
  physics_dt_s=float(w.read(w.CODE/'env.json').get('RM_PHYSICS_DT_S','.0005')),policy_period_s=.01,profile='white_v3',scope='Validated clock performance and separate A0 expert branch; no new DR/task/reward/interface')
 v.update(kw);base.status(**v)
def freeze_run(run):
 out=run/'rolling_source_freeze.json'
 if out.exists():return
 f=w.read(R/'SOURCE_FREEZE.json')
 for n,h in f['sha256'].items():
  assert base.sha(D/n)==h;p=run/'clock_source_snapshot'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/n,p)
 base.atomic_json(out,dict(candidate_root=str(D),sha256=f['sha256'],plan_version='1.5',physics_clock=validate_clock(float(w.read(w.CODE/'env.json')['RM_PHYSICS_DT_S'])),
  original_import_contract_physics_dt_s=.0005,task_reward_DR_hardware_PPO_observation_reset_unchanged=True,physics_integration_timestep_changed=True))
w.verify=ctl.verify=verify;w.status=ctl.status=status;w.rate.freeze_run=freeze_run
def guardian(owner,ticks):
 while True:
  p=helpers.identity(owner);b=base.budget_state();a=b['active_segment']
  lost=not p or p['state']=='Z' or p['start_ticks']!=ticks
  if a:
   child=helpers.identity(a['pid']);remaining=b['authorized_training_seconds']-b['charged_training_seconds']-max(0,time.time()-a['accounted_through_epoch'])
   if child and str(w.CODE/'train_mod4_ppo.py') in child['argv'] and (lost or remaining<=0):
    root=Path(ctl.S.get('active_training',{}).get('log_root',P/'logs'))
    for folder in [root,P/'logs',P/'autonomy_preflight_logs']:
     try:run=w.rate.trainer_run(folder,child['pid']);break
     except AssertionError:continue
    else:run=None
    if run and not (run/'STOP_AFTER_SAVE').exists():(run/'STOP_AFTER_SAVE').write_text('Owner/budget protection: complete save and stop.\n')
  if not a and (lost or (R/'SELECTED_CLOCK_REVIEW_READY.json').exists()):return
  time.sleep(15)
def controller():
 import torch;torch.set_num_threads(1)
 assert not (R/'SELECTED_CLOCK_WAIT_STARTED.json').exists(),'Unique entry already executed'
 write('SELECTED_CLOCK_WAIT_STARTED.json',dict(epoch=time.time(),owner=helpers.identity(os.getpid()),scope='CPU wait; no GPU or ledger authority'))
 assert base.budget_state()['active_segment'] is None and not base.trainers()
 helpers.acquire(P/'autonomy_controller.lock');helpers.acquire(ctl.CANONICAL.parent/'native_floor_supervisor.lock')
 ctl.S=w.read(ctl.STATE_PATH);base.STATE.update(w.read(P/'status.json'));ctl.idle();verify()
 previous=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT2000_IMPORT_REVIEW_20261007')
 assert (previous/'reports/SELECTED_CLOCK_REVIEW_READY.json').exists()
 dt=.002;clock=validate_clock(dt);verify();info=base.checkpoint(SOURCE)
 for n,h in w.read(previous/'reports/SOURCE_FREEZE.json')['sha256'].items():assert base.sha(D/n)==h,n
 for name in ('CROSSBIN_SDK_PASSED.json','NATIVE20K_PASSED.json'):
  v=w.read(previous/'reports'/name);assert base.sha(Path(v['output']))==v['sha256'] and v['physical_task_passed']
  write(name,v)
 selected=w.read(R/'NATIVE20K_PASSED.json')
 ctl.S.update(profile='white_v3',chosen_checkpoint=str(SOURCE));ctl.persist()
 write('SELECTED_CLOCK_STARTED.json',dict(epoch=time.time(),selected=selected,clock=clock,source=info,complete_initial_root_q_exact=True,no_production_adoption_yet=True))
 with (D/'guardian.log').open('x') as log:
  g=subprocess.Popen([base.PY,str(Path(__file__)), '--guardian',str(os.getpid()),str(helpers.identity(os.getpid())['start_ticks'])],cwd=P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 write('SELECTED_CLOCK_GUARDIAN_STARTED.json',helpers.identity(g.pid))
 facts=w.read(previous/'reports/SELECTED_CLOCK_BEHAVIOR_REVIEW.json')
 assert facts['task_model_data_all_pass'] and facts['initial_root_q_exact'] and facts['clock']==clock
 paths=facts['paths'];reports={}
 for kind,path in paths.items():
  r=w.read(Path(path));assert r['checkpoint']==str(SOURCE) and r['seed']==20261002 and r['steps']==1500
  v=w.assess_flat(r) if kind=='flat' else w.evidence(r,'spin',15.);assert v['pass_'];reports[kind]=r
 assert facts['world']['pass_'] and all(x['all_in_original_signed_02'] for x in facts['pure4pi'])
 assert not facts['strict_sufficient_evidence']
 decision=w.read(R/'PRACTICAL_ADMISSION.json');assert decision['accepted_for_bounded_adaptation'] and decision['source_sha256']==SHA
 write('SELECTED_CLOCK_BEHAVIOR_REVIEW.json',facts)
 if dt!=.0005:
  ctl.training(SOURCE,'clock128_discard',count=128,iterations=2,duration=600)
  ctl.training(SOURCE,'clock20k_discard',count=20000,iterations=4,duration=600)
  receipts=[]
  for p in sorted((P/'reports').glob('*clock*discard*_receipt.json')):
   v=w.read(p);ck=Path(v['discarded_weights']['path']);m=w.read(ck.parent/'run_manifest.json')
   if m['env'].get('RM_PHYSICS_DT_S')==str(dt) and m['init_checkpoint_sha256']==SHA and m['src_sha256']['train_mod4_ppo.py']==base.sha(w.CODE/'train_mod4_ppo.py'):
    health=w.read(ck.parent/'CLOCK_TRAINING_HEALTH.json')
    assert health['actual_task_reset_events']==0 and health['failed_environments']==0 and health['actual_physics_callbacks']==health['expected_physics_callbacks'],'Actual complete PPO physical failure'
    assert base.checkpoint(ck)['finite_tensors']==68 and int(base.checkpoint(ck)['iteration_stored'])>=23509+(1 if m['num_envs']==128 else 3) and health['control_steps']==(48 if m['num_envs']==128 else 96)
    receipts.append(dict(receipt_path=str(p),receipt_sha256=base.sha(p),physical_health=health,complete_PPO_receipt=v))
  assert len(receipts)==2,'Unique128/20k exact complete physical evidence required'
  write('SELECTED_CLOCK_PPO_PREFLIGHT_PASSED.json',dict(epoch=time.time(),new_dt=dt,source=info,weights_discarded=True,exact_physical_health=receipts,all_loading_PPO_save_exit_charged_same_canonical=True))
 else:write('SELECTED_CLOCK_PPO_PREFLIGHT_REUSED.json',dict(epoch=time.time(),unchanged_original_physics=True,original_F_full128_and20k_PPO_reused=True))
 write('SELECTED_CLOCK_ADOPTION.json',dict(epoch=time.time(),clock=clock,source=info,behavior_evidence=paths,complete_PPO_passed=True,practical_admission=decision,original_asset_not_overwritten=True,expert='E0',variant='A0',comparison_restarts_from_original23509=True))
 w.phase('bounded_A0_E0_selected_clock_learning',clock=clock,source=info,owner=helpers.identity(os.getpid()),duration_s=min(2700,ctl.remaining()))
 before=base.budget_state()['charged_training_seconds'];last=ctl.training(SOURCE,'moe_S1A_A0_selected_clock_learning',duration=min(2700,ctl.remaining()))
 saved=base.checkpoint(last);freeze_run(last.parent)
 review=dict(epoch=time.time(),checkpoint=saved,clock=clock,run=str(last.parent),PID_bound_receipt=w.read(last.parent/'latest_complete.json'),actual_learning_seconds=base.budget_state()['charged_training_seconds']-before,
  next='MatchedA1/A2 at same final clock and original23509; frozen3060 package must carry explicit newclock',all_curricula_finished=False)
 write('SELECTED_CLOCK_REVIEW_READY.json',review);w.phase('A0_selected_clock_saved_review_ready',**review);status('A0_selected_clock_saved_review_ready',training_pid=None,evaluation_pid=None)
 health=w.read(last.parent/'CLOCK_TRAINING_HEALTH.json')
 write('FORMAL_CLOCK_HEALTH_REVIEW.json',dict(epoch=time.time(),actual_health=health,adoption_retained=health['actual_task_reset_events']==0,all_weights_preserved=True))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:controller()
 except BaseException:
  write('SELECTED_CLOCK_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),active_segment=base.budget_state()['active_segment'],all_weights_preserved=True));raise
