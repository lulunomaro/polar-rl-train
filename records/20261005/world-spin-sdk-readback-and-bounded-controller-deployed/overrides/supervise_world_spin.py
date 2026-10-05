"""Authorized world-directional lesson; bounded exposure, same sole PPO budget.

New one-shot controller. Never resume an old entry or overwrite the spin final.
"""
import argparse,hashlib,json,math,os,shutil,subprocess,sys,time,traceback
from pathlib import Path
D=Path(__file__).resolve().parent;P=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002');CODE=D/'isaac/mod4';R=D/'reports'
sys.path.insert(0,str(P/'isaac/mod4'))
import supervise_autonomy as ctl
base,rate,helpers=ctl.base,ctl.rate,ctl.helpers
sys.path.insert(0,str(CODE));sys.path.insert(0,str(D))
from scut_curriculum_gate_v4 import assess,assess_flat,evidence,fullscale,VERSION
from world_progress_contract import target
read=ctl.read;STATE=R/'WORLD_SPIN_STATE.json';F=R/'SOURCE_FREEZE.json'
ctl.CODE=rate.CODE=ctl.spin.CODE=CODE
ctl.PROBES=tuple(ctl.PROBES)+('/contact_calibration_probe.py','/world_spin_probe.py','/world_fullscale_probe.py')
ctl.spin.PROBES=ctl.PROBES
def phase(name,**kw):
 s=read(STATE) if STATE.exists() else {};s.update(phase=name,updated_epoch=time.time(),**kw);base.atomic_json(STATE,s)
def runtime():
 cfg=read(CODE/'env.json');env={k:v for k,v in os.environ.items() if not k.startswith('RM_')}
 env.update({k:str(v) for k,v in cfg.items()});env.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1');return env
def verify():
 b=base.budget_state();assert b['authorized_training_seconds']==324000 and b['owner_root']==str(P)
 for n,h in read(P/'reports/SPIN_SOURCE_FREEZE.json')['sha256'].items():
  p=Path(n);p=p if p.is_absolute() else P/p;assert base.sha(p)==h,n
 for n,h in read(F)['sha256'].items():assert base.sha(D/n)==h,n
 cfg=read(CODE/'env.json')
 assert cfg['RM_SPIN_STAGE']=='world_directional_v1' and cfg['RM_MILD_DR_PROFILE']=='white_v2'
 assert cfg['RM_KEEP_STD']=='1' and cfg['RM_SPIN_ROLLING_PROFILE']=='v1'
 assert float(cfg['RM_SPIN_MAX_RAD_S'])==4*math.pi
 assert float(cfg['RM_SPIN_WORLD_PROGRESS_M_S']) in (.15,.3,.5)
def status(stage=None,**kw):
 cfg=read(CODE/'env.json');b=base.budget_state()
 values=dict(**({'stage':stage} if stage else {}),supervisor_pid=os.getpid(),active_code_root=str(D),
  canonical_budget=str(ctl.CANONICAL),authorized_training_seconds=b['authorized_training_seconds'],budget_seconds=b['authorized_training_seconds'],
  profile='white_v2',world_progress_goal_m_s=float(cfg['RM_SPIN_WORLD_PROGRESS_M_S']),moving_yaw_max_rad_s=2.,
  yaw_limit_rad_s=4*math.pi,spin_stage='world_directional_v1',spin_stage_finished=True,stand_fraction=.1,straight_fraction=.4,
  spin_fraction=.3,moving_spin_fraction=.2,autonomy_version='world_directional_spin_scut_v4_budget90_v1',
  scope='World-directed low-rate spin translation. Finite quality diagnostics only; actual task/model/data correctness and hardware envelope preserved.')
 values.update(kw);base.status(**values)
def freeze_run(run):
 out=run/'rolling_source_freeze.json'
 if out.exists():return
 dst=run/'world_source_snapshot'
 for n,h in read(F)['sha256'].items():
  assert base.sha(D/n)==h;q=dst/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/n,q)
 base.atomic_json(out,dict(candidate_root=str(D),sha256=read(F)['sha256'],acceptance_version=VERSION,
  lesson='world_directional_spin',world_goal_m_s=float(read(CODE/'env.json')['RM_SPIN_WORLD_PROGRESS_M_S']),reward_DR_hardware_physics_PPO_unchanged=True))
ctl.verify=verify;ctl.runtime=runtime;base.runtime_env=runtime;ctl.status=status;rate.freeze_run=freeze_run
def update_goal(v):
 ctl.idle();cfg=read(CODE/'env.json');cfg['RM_SPIN_WORLD_PROGRESS_M_S']=str(v);base.atomic_json(CODE/'env.json',cfg)
 f=read(F);f['sha256']['isaac/mod4/env.json']=base.sha(CODE/'env.json');base.atomic_json(F,f)
def probe(ck,kind,profile='white_v2',seed=20261002,steps=1500,count=None):
 ctl.idle();verify();label=ctl.fresh_label('world_'+kind);out=ctl.REPORTS/(label+'.json')
 name={'world':'world_spin_probe.py','spin':'contact_calibration_probe.py','flat':'validate_speed.py','20k':'world_fullscale_probe.py'}[kind]
 argv=[str(CODE/name),'--headless','--checkpoint',str(ck),'--output',str(out),'--steps',str(steps),
  '--num_envs',str(count or (80 if kind=='flat' else 88))]
 if kind!='20k':argv+=['--seed',str(seed),'--dr-profile',profile]
 if kind=='flat':argv+=['--speed_limit','1.5','--ramp_suite']
 else:argv+=['--max-rate',str(4*math.pi)]
 if kind in ('world','spin'):argv+=['--contact-readback']
 p=base.spawn(argv,out.with_suffix('.log'));ctl.LIVE=p
 phase('frozen_'+kind,checkpoint=base.checkpoint(ck),goal_m_s=float(read(CODE/'env.json')['RM_SPIN_WORLD_PROGRESS_M_S']),child=helpers.identity(p.pid),output=str(out))
 status('frozen_world_'+kind,training_pid=None,evaluation_pid=p.pid,validation_pid=None,active_log=str(out.with_suffix('.log')),evaluation_path=str(out))
 result=base.wait_probe(p,out);ctl.LIVE=None
 verdict=fullscale(result) if kind=='20k' else assess_flat(result) if kind=='flat' else evidence(result,'spin',steps*.01)
 base.atomic_json(out.with_name(out.stem+'_decision.json'),dict(**verdict,world_target=target(result,float(read(CODE/'env.json')['RM_SPIN_WORLD_PROGRESS_M_S'])) if kind=='world' and steps>=1500 else None))
 status(evaluation_pid=None,validation_pid=None,latest_world_admission=verdict)
 assert verdict['pass_'],verdict
 return result,out
def regression(ck):
 f,fp=probe(ck,'flat');s,sp=probe(ck,'spin');w,wp=probe(ck,'world')
 return dict(flat=str(fp),spin=str(sp),world=str(wp),world_target=target(w,float(read(CODE/'env.json')['RM_SPIN_WORLD_PROGRESS_M_S'])))
def paired(ck):
 rows=[];worlds=[];goal=float(read(CODE/'env.json')['RM_SPIN_WORLD_PROGRESS_M_S'])
 for seed in (20261002,20261003):
  for kind in ('flat','spin','world'):
   rs=[probe(ck,kind,p,seed) for p in ('nominal','white_v2')]
   exact=all(rs[0][0][k]==rs[1][0][k] for k in ('reset_joint_pos_before_physics','reset_root_before_physics'))
   assert exact,'Paired complete initial root/q mismatch'
   if kind=='world':worlds += [target(r,goal) for r,_ in rs]
   rows.append(dict(seed=seed,kind=kind,initial_root_q_exact=exact,paths=[str(p) for _,p in rs]))
 out=ctl.REPORTS/(ctl.fresh_label('world_paired_acceptance')+'.json')
 base.atomic_json(out,dict(pass_=True,pairs=rows,checkpoint=base.checkpoint(ck),goal_m_s=goal,world_tracking=worlds,learning_admission_only=True,acceptance_version=VERSION))
 return worlds,str(out)
def hold(ck,reason):
 if base.trainers() or base.budget_state()['active_segment']:
  phase('attention_required_active_child_preserved',reason=reason);status('attention_required',error=reason);return
 ctl.S['chosen_checkpoint']=str(ck);ctl.S['active_training']=None;ctl.persist()
 phase('repair_hold',reason=reason,last_validated_source=base.checkpoint(ck),finite_quality_not_a_veto=True)
 status('repair_hold',training_pid=None,evaluation_pid=None,validation_pid=None,reason=reason,rollback_checkpoint=str(ck))
def guardian(owner,ticks):
 while True:
  ident=helpers.identity(owner)
  if (R/'WORLD_SPIN_FINISHED.json').exists():return
  b=base.budget_state();a=b.get('active_segment')
  if a:
   remaining=b['authorized_training_seconds']-b['charged_training_seconds']-max(0,time.time()-a['accounted_through_epoch'])
   proc=helpers.identity(a['pid'])
   if remaining<=0 and proc and proc['cwd']==str(P) and str(CODE/'train_mod4_ppo.py') in proc['argv']:
    run=rate.trainer_run(P/'logs',proc['pid']);stop=run/'STOP_AFTER_SAVE'
    if not stop.exists():stop.write_text('Canonical budget exhausted: complete full atomic save and stop.\n')
  if (not ident or str(ident['start_ticks'])!=str(ticks)) and not a:return
  time.sleep(15)
def finish(ck,reason,paired_tracking=None):
 ctl.idle();f,fp=probe(ck,'flat');s,sp=probe(ck,'spin');w,wp=probe(ck,'world');n,np=probe(ck,'world','nominal')
 goal=float(read(CODE/'env.json')['RM_SPIN_WORLD_PROGRESS_M_S']);tracking=[target(w,goal),target(n,goal)]
 confirmed=bool(goal==.5 and paired_tracking and all(x['pass_'] for x in paired_tracking+tracking))
 result=dict(checkpoint=base.checkpoint(ck),goal_m_s=goal,world_progress_05_confirmed=confirmed,tracking=tracking,
  report_paths=[str(fp),str(sp),str(wp),str(np)],actual_budget=base.budget_state(),outcome=reason,
  spin_final_preserved=str(P/'reports/AUTONOMY_FINISHED.json'),real_robot_certified=False)
 base.atomic_json(R/'WORLD_SPIN_FINISHED.json',result);base.atomic_json(P/'reports/WORLD_SPIN_FINISHED.json',result)
 phase('world_stage_finished',**result);status('finished',training_pid=None,evaluation_pid=None,validation_pid=None,outcome=reason,final_evaluation=result)
def controller():
 assert not STATE.exists(),'World entry already started: inspect existing state, never rerun'
 import torch;torch.set_num_threads(1)
 ctl.S=read(ctl.STATE_PATH);base.STATE.update(read(P/'status.json'))
 ctl.idle();verify();helpers.acquire(P/'autonomy_controller.lock');helpers.acquire(ctl.CANONICAL.parent/'native_floor_supervisor.lock')
 sdk=read(R/'SDK_READBACK_PASSED.json');assert sdk['pass_'] and sdk['ledger_bytes_exact']
 assert helpers.identity(read(R/'SDK_VERIFICATION_LAUNCHED.json')['pid']) is None
 spin_final=read(P/'reports/AUTONOMY_FINISHED.json');assert spin_final['target_2rev_s_confirmed']
 source=Path(spin_final['checkpoint']['path']);assert base.checkpoint(source)==spin_final['checkpoint']
 ck=source;last=source;phase('world_lesson_preflight',source=base.checkpoint(source),owner=helpers.identity(os.getpid()),goal_m_s=.15,route=[.15,.3,.5],learning_admission_version=VERSION)
 with (D/'guardian_world_spin.log').open('x') as log:
  g=subprocess.Popen([base.PY,str(D/'supervise_world_spin.py'),'--guardian',str(os.getpid()),str(helpers.identity(os.getpid())['start_ticks'])],cwd=P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 base.atomic_json(R/'WORLD_GUARDIAN_STARTED.json',helpers.identity(g.pid))
 preflight_PPO_done=False
 try:
  for goal in (.15,.3,.5):
   update_goal(goal)
   # Fresh independent source/goal checks. The initial .15 short pair is reused
   # explicitly from the completed SDK receipt, not executed a second time.
   if goal!=.15:probe(ck,'world',steps=300,count=22)
   probe(ck,'20k',steps=120,count=20000)
   baseline=regression(ck)
   phase('world_baseline_measured',checkpoint=base.checkpoint(ck),goal_m_s=goal,baseline=baseline)
   if baseline['world_target']['pass_']:
    worlds,path=paired(ck)
    if all(x['pass_'] for x in worlds):
     last=ck;phase('existing_world_capability_verified_without_PPO',goal_m_s=goal,checkpoint=base.checkpoint(ck),paired_path=path)
     if goal==.5:finish(ck,'Measured .5 world progress already available; no unnecessary PPO',worlds);return
     continue
   if not preflight_PPO_done:
    ctl.training(ck,'world_128_discard',count=128,iterations=2,duration=600)
    ctl.training(ck,'world_20k_discard',count=20000,iterations=4,duration=600)
    preflight_PPO_done=True
   exposure=0;duration=2700
   while ctl.remaining()>120:
    charged_before=base.budget_state()['charged_training_seconds'];phase('bounded_world_learning',goal_m_s=goal,source=base.checkpoint(ck),duration_s=min(duration,ctl.remaining()),effective_exposure_s=exposure)
    ck=ctl.training(ck,'world_directional_learning',duration=min(duration,ctl.remaining()))
    exposure+=base.budget_state()['charged_training_seconds']-charged_before;regression(ck)
    worlds,path=paired(ck);last=ck
    phase('world_paired_learning_accepted',goal_m_s=goal,checkpoint=base.checkpoint(ck),effective_exposure_s=exposure,paired_path=path,target_confirmed=all(x['pass_'] for x in worlds),learning_admission_only=True)
    if goal!=.5:break
    if all(x['pass_'] for x in worlds):finish(ck,'Measured .5 world-directed progress confirmed with retained spin/flat and two-seed final reports',worlds);return
    duration=min(7200,ctl.remaining())
   if ctl.remaining()<=120:finish(ck,'Remaining effective budget insufficient for another safe PPO block; unspent remainder retained and target not assumed');return
 except BaseException:
  hold(last,traceback.format_exc());raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 if a.guardian:guardian(int(a.guardian[0]),a.guardian[1])
 else:controller()
