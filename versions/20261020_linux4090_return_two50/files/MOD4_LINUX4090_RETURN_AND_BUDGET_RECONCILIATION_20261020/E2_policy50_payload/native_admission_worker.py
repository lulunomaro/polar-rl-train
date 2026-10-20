"""New phase in a fresh process; H1 is explicitly native-only, no teacher or jump PPO."""
from pathlib import Path
import argparse,hashlib,json,os,runpy,sys,time,traceback,shutil
B=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def main():
 p=argparse.ArgumentParser();p.add_argument('--job',type=int,choices=(0,1),required=True);p.add_argument('--phase',choices=('native','precheck128','precheck20k','production'),required=True);args=p.parse_args();j=B/('job'+str(args.job));task=json.loads((j/'TASK.json').read_bytes());phase=args.phase;assert args.job==0 and phase in ('native','production');out=j/('clock_native50' if phase=='native' else phase);out.mkdir()
 source=j/'source/E2_closed_hour241.pt';assert H(source)==task['source_SHA'];assert task['policy_clock_migration_authorized'] and task['source_policy_hz'] in (50,100);N=128 if phase=='precheck128' else task['per_GPU_envs'];fresh=phase=='precheck128' or args.job==1
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 os.environ['MOD4_RESUME_QUEUE_CONTROL_US']=str(1000000//task['source_policy_hz'])
 m=json.loads((j/'original_run_manifest.json').read_bytes());os.environ.update({k:str(v) for k,v in m['env'].items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')});os.environ.update(RM_MOD4_USD=str(j/'assets/robot.usd'),RM_RESCUE_STOP_FILE=str(out/'STOP_AFTER_SAVE.json'),RM_JUMP_SCRIPT_PROB='0',OWN_E2_H1_KIND=task['kind'],RM_MOD4_MAP='',RM_MOD4_TERRAIN='flat')
 assert int(m['env'].get('RM_SPAWN_GRACE_STEPS','10'))==10
 os.environ['RM_SPAWN_GRACE_STEPS']='5'
 sys.path[:0]=[str(B/'lib'),str(j/'runtime/isaac/mod4')];entry=j/'runtime/isaac/mod4'/('train_E2_H1_fresh_v1.py' if fresh else 'train_E2_full_resume_v1.py');sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs',str(N),'--seed','20260928','--steps_per_env','24','--learning_rate','.0001','--save_interval','25','--init_checkpoint',str(source),'--log_root',str(out/'logs'),'--run_name',task['kind']+'_'+phase,'--additional_iterations','100000'];ns=runpy.run_path(str(entry),run_name='owned_new_phase_config')
 import torch,numpy as np,rescue_training
 from spring_pressure_checkpoint import exact
 class SavedStop(Exception):pass
 def learn(runner,n,log_dir):
  env=runner.env.unwrapped;vec=runner.env;runner.logger.writer=None;src=torch.load(source,map_location='cpu',weights_only=False)
  for key,v in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(v,src[key]),key
  assert int(env._sim_step_counter)==0 and float(os.environ['RM_JUMP_SCRIPT_PROB'])==0
  receipts=sorted(Path(log_dir).glob('*STARTUP_VERIFIED.json'));assert fresh or len(receipts)>=7
  term=env.command_manager.get_term('twist')
  if args.job==1:term.set_manual_evaluation_mode();term.vel_command_b.zero_();env._mod4_mode_bit=torch.full((N,),4,device=env.device,dtype=torch.long)
  oldsave=runner.save
  def save(path,updates):
   path=Path(path);tmp=path.with_suffix(path.suffix+'.partial');oldsave(str(tmp));v=torch.load(tmp,map_location='cpu',weights_only=False);v['owned_new_expert_task']=task;v['owned_phase']=phase;v['owned_phase_complete_updates']=updates;v['policy_clock']=dict(policy_hz=50,physics_dt_s=.0025,decimation=8,feedback_sampling_hz=100,source_policy_hz=task['source_policy_hz']);torch.save(v,tmp);tmp.replace(path);steps={int(x['step']) for x in v['optimizer_state_dict']['state'].values()};assert steps=={task['source_Adamstep']+updates*20};r=dict(epoch=time.time(),path=str(path),bytes=path.stat().st_size,SHA=H(path),phase=phase,updates=updates,Adam_step=next(iter(steps)),kind=task['kind']);put(out/'latest_complete.json',r);return r
  assert env.physics_dt==.0025 and env.step_dt==.02 and env.cfg.decimation==8
  env._physics_action_delay.queue.control_us=20000
  put(out/'POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json',dict(policy_hz=50,control_period_s=.02,physics_dt_s=.0025,decimation=8,feedback_sampling_hz=100,contact_bin_s=.005,action_transition_delay_us=[0,2500,5000],source_policy_hz=task['source_policy_hz'],source_SHA=task['source_SHA'],gamma=.9801,lam=.9025,rollout_decisions=24,rollout_simulated_seconds=.48))
  zero=save(out/'own_startup0.pt',0);put(out/'STARTUP_SOURCE_ACTUAL.json',dict(epoch=time.time(),source_SHA=H(source),model9_critic8_STD17Adam_literal_exact=True,zero_clock=True,full20k_original_D0_D7_restore=not fresh,fresh80_or128_perenv_not_full20k_restore=fresh,typed_receipts=[str(p) for p in receipts],zero=zero))
  if phase=='native':
   runner.alg.actor.eval();runner.alg.critic.eval();obs=vec.get_observations();tick=env._integrated_contact.tick;fbt=env._feedback_100hz_tick;checks=[]
   with torch.inference_mode():
    for i in range(24):
     before=env._integrated_contact.tick;fb=env._feedback_100hz_tick;action=runner.alg.actor(obs,stochastic_output=False);obs,reward,done,info=vec.step(action)
     assert env._integrated_contact.tick-before==8 and env._feedback_100hz_tick-fb==2
     assert obs['policy'].shape==(20000,35) and obs['critic'].shape==(20000,38) and torch.isfinite(obs['policy']).all() and torch.isfinite(reward).all()
     checks.append(dict(control=i+1,callbacks=env._integrated_contact.tick-before,feedback_10ms_samples=env._feedback_100hz_tick-fb))
     assert not (out/'STOP_AFTER_SAVE.json').exists()
   for k,v in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(v,src[k]),k
   assert env._integrated_contact.tick-tick==192 and env._feedback_100hz_tick-fbt==48
   last=save(out/'own_clock_native24.pt',0);put(out/'CLOCK_NATIVE24_COMPLETE.json',dict(epoch=time.time(),source_SHA=task['source_SHA'],controls=24,callbacks=192,actual_step_s=float(env.step_dt),physics_dt_s=float(env.physics_dt),maximum_target_error=env._physics_action_delay.formula_max_error,all_policy_steps_exactly_8_physics_callbacks=True,all_feedback_steps_exactly_2_10ms_samples=True,no_optimizer_update=True,checks=checks,not_skill_or_336_native_qualification=True));put(out/'FINAL.json',dict(epoch=time.time(),passed=True,final=last,clock_protocol_only=True));return
  original_step=vec.step
  def step50(action):
   before=env._integrated_contact.tick;fb=env._feedback_100hz_tick;out=original_step(action)
   assert env._integrated_contact.tick-before==8 and env._feedback_100hz_tick-fb==2
   return out
  vec.step=step50
  completed=0;oldlog=runner.logger.log
  go=json.loads((j/('GO_'+phase.upper()+'.json')).read_bytes());deadline=go['save_deadline']
  def log(*aa,**kk):
   nonlocal completed
   oldlog(*aa,**kk);completed+=1;stop=(shutil.disk_usage(B).free<8*1024**3) or (phase=='precheck128' and completed>=2) or (phase=='precheck20k' and completed>=4) or time.time()>=deadline or (out/'STOP_AFTER_SAVE.json').exists() or (Path(log_dir)/'STOP_AFTER_SAVE').exists()
   if completed==1 or completed%25==0 or stop:put(out/'PPO_POSITIVE_CURRENT.json',save(out/('model_update'+str(completed)+'.pt'),completed))
   if stop:raise SavedStop()
  runner.logger.log=log
  try:runner.learn(num_learning_iterations=n,init_at_random_ep_len=True)
  except SavedStop:pass
  row=json.loads((out/'latest_complete.json').read_bytes());assert row['updates']>0
  if phase=='precheck128':assert row['updates']==2
  if phase=='precheck20k':assert row['updates']==4
  put(out/'FINAL.json',dict(epoch=time.time(),passed=True,final=row,prechecks_discarded=phase!='production'))
 rescue_training.learn=learn
 try:ns['main']()
 except BaseException:put(out/'WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
 finally:put(out/'APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()
if __name__=='__main__':
 try:main()
 except BaseException:
  try:put(Path(__file__).resolve().parent/('WORKER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_automatic_retry=True))
  except BaseException:pass
  raise
