"""Unique approved S2 D1+D2 authority, staged probes then discard PPO and45min."""
from pathlib import Path
import sys,json,time,os,subprocess,traceback,argparse,math
D=Path(__file__).resolve().parent;R=D/'reports';CODE=D/'isaac/mod4'
N=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT1000_WORKER_REVIEW_20261007')
sys.path.insert(0,str(N));import continue_clock1000_worker_manifest_review_once as q
LIVE=None
def write(n,v):q.base.atomic_json(R/n,v)
def verify():
 q.verify();a=q.w.read(q.ER/'PLAN_APPROVAL.json');assert a['approved'] and 'S2' in a['allowed_stages']
 assert a['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
 for n,h in q.w.read(R/'SOURCE_FREEZE.json')['sha256'].items():assert q.base.sha(D/n)==h,n
 assert q.w.read(CODE/'env.json')==q.w.read(N/'isaac/mod4/env.json')
 assert q.w.read(R/'SENSOR_CPU_CONTRACT.json')['passed']
 assert q.w.read(q.ER/'S1A_ARCHITECTURE_SELECTION.json')['selected_architecture']=='A0'
def source():
 s=q.w.read(R/'S1A_ARCHITECTURE_SELECTION.json')['selected_source'];p=Path(s['path']);assert q.base.sha(p)==s['sha256'];return p
def left():
 b=q.base.budget_state();a=b['active_segment'];return b['remaining_training_seconds']-(max(0,time.time()-a['accounted_through_epoch']) if a else 0)
def env(profile='noise_bias_mild_v1'):
 e=q.w.runtime();e.update(PYTHONPATH=str(D)+os.pathsep+str(CODE),RM_SENSOR_PROFILE=profile,PYTHONUNBUFFERED='1');return e
def phase(p,**kw):
 x=dict(epoch=time.time(),phase=p,owner=q.helpers.identity(os.getpid()),**kw);write('E0_SENSOR_DR_STATE.json',x)
 q.base.status(stage=p,active_code_root=str(D),active_expert='E0',plan_stage='S2 D1+D2',architecture_variant='A0',physics_dt_s=.001,profile='white_v3',sensor_profile=kw.get('sensor_profile','noise_bias_mild_v1'))
def frozen(label,args,e):
 global LIVE
 verify();assert q.base.budget_state()['active_segment'] is None and not q.base.trainers();out=R/(label+'.json');log=D/(label+'.log');assert not out.exists() and not log.exists()
 before=q.ctl.CANONICAL.read_bytes();start=time.time()
 with log.open('x') as f:child=subprocess.Popen([q.base.PY,*args,'--headless','--output',str(out)],cwd=q.P,env=e,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 LIVE=child;phase('frozen_'+label,child=q.helpers.identity(child.pid),output=str(out),active_log=str(log),sensor_profile=e['RM_SENSOR_PROFILE'])
 child.wait(timeout=1800);LIVE=None
 assert child.returncode==0 and out.exists() and not Path(str(out)+'.error').exists() and not Path(str(out)+'.error.txt').exists() and 'Traceback (most recent call last)' not in log.read_text(errors='replace'),('Frozen worker failure',label)
 assert before==q.ctl.CANONICAL.read_bytes();raw=q.w.read(out);row=dict(epoch=time.time(),output=str(out),output_sha256=q.base.sha(out),pid=child.pid,exit_code=0,process_wall_seconds=time.time()-start,new_learning=False)
 write(label+'_COMPLETE.json',row);return raw,row
def sensor_fullsave(p):
 import torch
 ck=torch.load(p,map_location='cpu',weights_only=False);info=q.base.checkpoint(p)
 assert ck['actor_state_dict']['mlp.0.weight'].shape==(256,35) and ck['critic_state_dict']['mlp.0.weight'].shape==(256,38)
 assert ck['optimizer_state_dict']['state'] and ck['sensor_recipe']['profile']=='noise_bias_mild_v1'
 s=ck['sensor_DR_state'];assert s['version']==1 and set(s['noise_rng'])=={'base_ang_vel','projected_gravity','leg_pos','leg_vel','wheel_vel'} and len(s['cache'])==5
 assert ck['sensor_global_rng_state']['cuda'] and 'sensor_command_DR_rng_state' in ck and 'sensor_physical_DR_rng_state' in ck
 return info
def freeze_run(run):
 if (run/'rolling_source_freeze.json').exists():return
 import shutil
 f=q.w.read(R/'SOURCE_FREEZE.json')
 for n,h in f['sha256'].items():
  assert q.base.sha(D/n)==h;p=run/'sensor_source_snapshot'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/n,p)
 q.base.atomic_json(run/'rolling_source_freeze.json',dict(candidate_root=str(D),sha256=f['sha256'],plan_stage='S2 D1+D2',physics_dt_s=.001,actor_feedback_noise_bias_only=True,original189_runtime_files_exact=True))
def train(init,count,updates,duration,label,discard):
 global LIVE
 verify();assert q.base.budget_state()['active_segment'] is None and not q.base.trainers() and not q.w.read(q.ctl.STATE_PATH).get('active_training')
 assert left()>120;duration=min(duration,left());logs=D/('discard_logs' if discard else 'learning_logs');logs.mkdir(exist_ok=True);name=label+'_'+str(time.time_ns());log=D/(name+'.log');deadline=time.time()+duration
 e=env();e['RM_RESCUE_DEADLINE']=str(deadline)
 args=[q.base.PY,str(CODE/'train_sensor_ppo.py'),'--headless','--num_envs',str(count),'--steps_per_env','24','--max_iterations',str(updates),'--save_interval','1' if discard else '25','--learning_rate','.0001','--seed','20260928','--run_name',name,'--log_root',str(logs),'--init_checkpoint',str(init)]
 with log.open('x') as f:child=subprocess.Popen(args,cwd=q.P,env=e,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 LIVE=child;q.base.start_segment(child,'moe_S2_D1D2_'+name,log);q.ctl.S=q.w.read(q.ctl.STATE_PATH);q.ctl.S['active_training']=dict(pid=child.pid,source=q.base.checkpoint(init),phase=label,profile='white_v3',sensor_profile='noise_bias_mild_v1',log_root=str(logs),deadline=deadline);q.ctl.persist()
 phase('complete_sensor_PPO_preflight' if discard else 'bounded_E0_sensor_DR_learning',child=q.helpers.identity(child.pid),active_log=str(log),deadline_epoch=deadline,source=q.base.checkpoint(init))
 while child.poll() is None:
  q.base.account_segment()
  try:
   run=q.w.rate.trainer_run(logs,child.pid);receipt=q.w.read(run/'latest_complete.json');freeze_run(run)
   write('E0_SENSOR_CURRENT_SAVE.json',dict(epoch=time.time(),own_run=str(run),receipt=receipt))
  except (AssertionError,FileNotFoundError):pass
  time.sleep(1 if discard else 5)
 q.base.account_segment(finish=True);LIVE=None;q.ctl.S['active_training']=None;q.ctl.persist()
 assert child.returncode==0 and 'Traceback (most recent call last)' not in log.read_text(errors='replace'),('PPO worker failed; retain own saves',label)
 run=q.w.rate.trainer_run(logs,child.pid);receipt=q.w.read(run/'latest_complete.json');freeze_run(run);p=Path(receipt['checkpoint']);ck=sensor_fullsave(p);m=q.w.read(run/'run_manifest.json');health=q.w.read(run/'CLOCK_TRAINING_HEALTH.json')
 assert m['init_checkpoint_sha256']==q.base.sha(init) and m['source_map']==q.w.read(R/'SOURCE_FREEZE.json')['sha256']
 for n,h in m['src_sha256'].items():assert q.base.sha(run/'src_snapshot'/n)==h,n
 assert health['actual_task_reset_events']==0 and health['failed_environments']==0 and health['max_closure_error_m']<=.002 and health['max_mimic_error_rad']<=.01 and health['actual_physics_callbacks']==health['expected_physics_callbacks'],('Actual task/model/clock failure',health)
 if discard:assert health['control_steps']==24*updates
 row=dict(epoch=time.time(),checkpoint=ck,run=str(run),own_PID_bound_receipt=receipt,health=health,actual_environment_steps=health['control_steps']*count,discarded_preflight=discard,unique_completed_segment=[x for x in q.w.read(q.ctl.CANONICAL)['completed_segments'] if x['pid']==child.pid])
 assert len(row['unique_completed_segment'])==1;write(label+'_COMPLETE.json',row);return p,row
def guardian(pid,ticks):
 while True:
  p=q.helpers.identity(pid);a=q.base.budget_state()['active_segment'];lost=not p or p['state']=='Z' or p['start_ticks']!=ticks
  if a and (lost or left()<=0):
   actual=q.helpers.identity(a['pid'])
   if actual and str(CODE/'train_sensor_ppo.py') in actual['argv']:
    for logs in (D/'learning_logs',D/'discard_logs'):
     try:run=q.w.rate.trainer_run(logs,actual['pid']);break
     except AssertionError:continue
    else:run=None
    if run and not (run/'STOP_AFTER_SAVE').exists():(run/'STOP_AFTER_SAVE').write_text('Own full-save boundary: owner or budget protection\n')
  if not a and (lost or (R/'E0_SENSOR_STAGE1_REVIEW_READY.json').exists() or (R/'E0_SENSOR_ATTENTION.json').exists()):return
  time.sleep(15)
def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'E0_SENSOR_STARTED.json').exists();verify()
 q.helpers.acquire(q.P/'autonomy_controller.lock');q.helpers.acquire(q.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
 assert q.base.budget_state()['active_segment'] is None and not q.base.trainers() and not q.w.read(q.ctl.STATE_PATH).get('active_training')
 old=Path('/home/egde/rl_candidates/MOD4_S1A_FROZEN_SAVED_SCHEMA_REVIEW_20261007');x=q.w.read(old/'reports/FROZEN_PROTOCOL_REVIEW_LAUNCHED.json');assert not q.helpers.identity(x['owner']['pid']) and not q.helpers.identity(803760)
 assert q.w.read(old/'reports/FROZEN_MATCHED_REPLAY_READY.json')['canonical_bytes_exact']
 init=source();write('E0_SENSOR_STARTED.json',dict(epoch=time.time(),owner=q.helpers.identity(os.getpid()),selected_source=q.base.checkpoint(init),no_budget_change_at_install=True,old189_runtime_byte_exact=True))
 old=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_DR_STAGE1_20261007');proof=q.w.read(old/'reports/SENSOR_ACTUAL_SDK_PASSED.json')
 assert proof['off_on_fixed_clean_plant_root_q_parameters_bit_exact'] and proof['real_manager_formula_tick_selected_reset_cleancritic_verified']
 reused=[]
 for label,count,steps in (('sensor_sdk_off',10,300),('sensor_sdk_noise_bias_mild_v1',10,300),('sensor_native20k',20000,120)):
  row=q.w.read(old/'reports'/(label+'_COMPLETE.json'));p=Path(row['output']);assert q.base.sha(p)==row['output_sha256'] and row['exit_code']==0
  raw=q.w.read(p);assert raw['actual_task_failed_environments']==0 and not raw['nonfinite'] and raw['max_closure_error_m']<=.002 and raw['max_mimic_error_rad']<=.01 and raw['physical_callback_count']==steps*10
  assert raw['initial_parameters']['actual_parameters_pass'] and raw['final_parameters']['actual_parameters_pass'];reused.append(row)
 write('SENSOR_SDK_NATIVE20K_EXACT_REUSED.json',dict(epoch=time.time(),receipts=reused,SDK=proof,same199_runtime_files_exact=True,new_PPO=0,no_duplicate_probe=True))
 sys.path.insert(0,str(CODE));from scut_curriculum_gate_v4 import evidence
 from world_progress_contract import target
 baseline=[]
 for kind,count in (('flat',80),('spin',88),('world',88)):
  args=[str(CODE/('sensor_'+kind+'_probe.py')),'--checkpoint',str(init),'--steps','1500','--num_envs',str(count),'--seed','20261002','--dr-profile','white_v3']
  args+=['--speed_limit','1.5','--ramp_suite'] if kind=='flat' else ['--max-rate',str(4*math.pi),'--contact-readback']
  r,row=frozen('sensor_baseline_'+kind,args,env());v=evidence(r,'spin' if kind=='world' else kind);assert v['pass_'],v
  row['admission']=v
  if kind=='world':row['world_target']=target(r,.5)
  baseline.append(row)
 write('SENSOR_BASELINE_BEHAVIOR_PASSED.json',dict(epoch=time.time(),receipts=baseline,finite_quality_is_diagnostic=True,source=q.base.checkpoint(init),new_sensor_distribution=True))
 with (D/'guardian.log').open('x') as f:g=subprocess.Popen([q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(q.helpers.identity(os.getpid())['start_ticks'])],cwd=q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 write('E0_SENSOR_GUARDIAN_STARTED.json',q.helpers.identity(g.pid))
 pre=[]
 for count,updates in ((128,2),(20000,4)):
  _,row=train(init,count,updates,600,'sensor_discard_'+str(count),True);pre.append(row)
 write('SENSOR_COMPLETE_PPO_PREFLIGHT_PASSED.json',dict(epoch=time.time(),receipts=pre,weights_discarded=True,not_training_sources=True))
 p,row=train(init,20000,10000,2700,'sensor_formal45',False)
 write('E0_SENSOR_STAGE1_REVIEW_READY.json',dict(epoch=time.time(),formal=row,first45min_fullsave_not_graduation=True,behavior_of_new_saved_policy_pending=True,next='Exact immutable3060 feedback-scope package and retention review; then approved stable1-2h blocks or nextDR group',all_courses_finished=False))
 phase('E0_sensor_stage1_saved_review_ready',child=None,source=q.base.checkpoint(p))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--guardian',nargs=2);x=a.parse_args()
 try:
  if x.guardian:guardian(int(x.guardian[0]),int(x.guardian[1]))
  else:main()
 except BaseException:
  write('E0_SENSOR_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),active_segment=q.base.budget_state()['active_segment'],own_child_still_alive=bool(LIVE and LIVE.poll() is None),all_weights_retained=True,no_blind_resume=True));raise
