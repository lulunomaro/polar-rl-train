"""Frozen mean24-controls admission, original normal-H1 D1-D7 path, no PPO."""
from pathlib import Path
import argparse,hashlib,json,os,runpy,sys,time,traceback
SOURCE='71db5543b14919eb11d2a8606f9ffe1acf0814260d7d89aa823565a49a7b21c4'
# Future original parent assigns physical GPU; no historical GPU/resource pin.
def H(p):
  with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
  p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True);p.add_argument('--task',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();B=a.job_root.resolve();J=B/'job0';O=a.out.resolve();O.mkdir()
  def put(n,v):
   with (O/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
  stat=Path('/proc/self/stat').read_text();v=stat[stat.rfind(')')+2:].split();boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '));put('GPU_OWN_WORKER_IDENTITY.json',dict(pid=os.getpid(),creation=boot+int(v[19])/os.sysconf('SC_CLK_TCK'),exe=os.readlink('/proc/self/exe'),argv=[os.fsdecode(x) for x in Path('/proc/self/cmdline').read_bytes().split(bytes([0])) if x],cwd=os.readlink('/proc/self/cwd')))
  sys.path[:0]=[str(B/'lib'),str(J/'runtime/isaac/mod4'),str(B)]
  from h1_mod4v1_source_contract_v1 import validate_future_task_metadata
  from h1_pinned_source_v1 import PinnedSourceH1,selected_source,cached_load
  from mod4v1_fresh_dr_guard import bind_before_task_import,verify_task_module,configure_new_task,FreshDRNominalGuard
  task=json.loads(a.task.read_text(encoding='utf8'));validate_future_task_metadata(task);source=Path(task['selected_source_path'])
  for k in list(os.environ):
   if k.startswith('RM_') or k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
  original=json.loads((J/'original_run_manifest.json').read_bytes())['env'];os.environ.update({k:str(v) for k,v in original.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')});os.environ.update(RM_MOD4_USD=str(Path(task['asset_dir'])/'robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0',RM_KEEP_STD='1',RM_RESCUE_STOP_FILE=str(O/'UNUSED_STOP.json'),OWN_E2_H1_KIND='H1_NORMAL_TYPED71DB_MOD4V1_WHOLE20K_NATIVE24_NOUPDATE_V1');os.environ.update(RM_PHYSICS_DT_S='0.0025',RM_SOLVER_POS='32',RM_SOLVER_VEL='4');identity=bind_before_task_import(task['asset_dir'])
  sys.path[:0]=[str(B/'lib'),str(J/'runtime/isaac/mod4'),str(B)];entry=J/'runtime/isaac/mod4/train_H1_ground_prelaunch_fullstate_v2.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed','20260928','--steps_per_env','24','--learning_rate','.00038443359375000017','--save_interval','25','--init_checkpoint',str(source),'--log_root',str(O/'logs'),'--run_name','NORMAL_H1_FROZEN_NATIVE24_NO_PPO','--additional_iterations','1']
  ns=None;created=[None]
  try:
   ns=runpy.run_path(str(entry),run_name='normal_H1_original_restoration_configuration_only')
   import mod4_task;verify_task_module(mod4_task,identity)
   import h1_scut_fudan_jump_reward_v1 as scut
   import h1_step270_sdk_runtime_candidate as terrain
   oldconfigure=scut.configure;scut.configure=lambda cfg:terrain.configure_rewards(cfg,oldconfigure)
   factory=ns['build_env'];original_cfg=ns['Mod4EnvCfg']
   def cfg():
    c=original_cfg();c.scene.num_envs=20000;c.seed=20260928;c.sim.device='cuda:0';assert float(c.terminations.closure.params['threshold'])==.002 and float(c.terminations.mimic.params['threshold'])>=.01;c.terminations.mimic.params={**c.terminations.mimic.params,'threshold':.01};configure_new_task(c,identity);assert c.sim.dt==.0025 and c.decimation==8 and c.sim.physics.solver_type==1;assert c.scene.robot.spawn.articulation_props.solver_position_iteration_count==32 and c.scene.robot.spawn.articulation_props.solver_velocity_iteration_count==4;return c
   factory.__globals__.update(Mod4Env=terrain.H1Step270Env,Mod4EnvCfg=cfg)
   def build():
    env=factory();created[0]=env;assert env.num_envs==20000 and env.physics_dt==.0025 and env.step_dt==.02 and env.cfg.decimation==8 and env._physics_action_delay.queue.control_us==20000;from mild_dr import tensor;env._mod4v1_nominal_guard=FreshDRNominalGuard(env,identity,torch_module=__import__('torch'),tensor_converter=tensor);return env
   ns['main'].__globals__['build_env']=build
   import h1_fullstate_checkpoint_v1 as checkpoint_API
   from h1_step270_fullstate_checkpoint_candidate_uninstalled import resume_step270_new_episode,install_step270_save_contract
   def guarded_original_resume(runner,env,path,log_dir):
    with env._mod4v1_nominal_guard.around_original_fullstate_restore():
     return resume_step270_new_episode(runner,env,path,log_dir)
   checkpoint_API.resume_h1_new_episode=guarded_original_resume;checkpoint_API.install_h1_save_contract=install_step270_save_contract
   import torch,rescue_training
   from spring_pressure_checkpoint import exact
   from h1_reward_scope_v1 import isolated_actual_SDK_dt_probe
   def work(runner,n,log_dir):
    runner.logger.writer=None;real=runner.env.unwrapped;ck=cached_load(source,map_location='cpu',weights_only=False,purpose='H1.actual_native24.work.source_identity');assert 'H1_step270_task_state' in ck and ck['iter']==41448
    assert runner.current_learning_iteration==41448 and runner.alg.learning_rate==runner.alg.optimizer.param_groups[0]['lr']==.00038443359375000017
    assert runner.alg.__class__.__module__=='owned_h1_public4_mean_overflow_ppo_v2'
    for k,x in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(x,ck[k]),k
    assert {int(x['step']) for x in runner.alg.optimizer.state_dict()['state'].values()}=={832460} and int(real._sim_step_counter)==0 and not real.h1_phase.age_control.any()
    assert real.spring_pressure_recipe()['nominal_stiffness_N_m']==2000 and real.action_delay_recipe()['control_period_us']==20000
    required={'SENSOR_RESUME_STARTUP_VERIFIED.json','DELAY_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','STEP270_FULLSTATE_RESUME_STARTUP_VERIFIED.json'}
    actual={p.name:p for p in Path(log_dir).glob('*STARTUP_VERIFIED.json')};assert required<=set(actual)
    receipts=[dict(path=str(actual[name]),value=json.loads(actual[name].read_bytes())) for name in sorted(required)]
    probe=isolated_actual_SDK_dt_probe(real);assert probe['dt']==.02
    put('MOD4V1_NORMAL_H1_FULLRESTORE_BEFORE_MEAN_ACTION.json',dict(passed=True,source_SHA=SOURCE,new_asset_nominal_guard=real._mod4v1_nominal_guard.receipt(),asset_USD_SHA=identity.usd_sha256,asset_contract_SHA=identity.contract_sha256,Adam832460=True,constructor_and_optimizer_LR=.00038443359375000017,full_D1_D7_H1_restore_receipts=receipts,actual_reward_manager_dt_probe=probe,original270_goal=True,no_optimization=True))
    runner.alg.actor.eval();runner.alg.critic.eval();before={k:{name:value.detach().clone() for name,value in model.state_dict().items()} for k,model in [('actor',runner.alg.actor),('critic',runner.alg.critic)]};opt={k:{name:value.detach().clone() if torch.is_tensor(value) else value for name,value in row.items()} for k,row in runner.alg.optimizer.state_dict()['state'].items()};groups=runner.alg.optimizer.state_dict()['param_groups']
    obs=runner.env.get_observations();real._mod4v1_nominal_guard.check_observations(obs);rows=[];start_tick=int(real._sim_step_counter);start_feedback=int(real._feedback_100hz_tick);start_callbacks=int(real.h1_callback_count)
    with torch.inference_mode():
     for i in range(24):
      t=int(real._sim_step_counter);f=int(real._feedback_100hz_tick);ct=int(real.h1_callback_count);contact=int(real._integrated_contact.tick);age=real.h1_phase.age_control.clone();action=runner.alg.actor(obs,stochastic_output=False);assert action.shape==(20000,6) and torch.isfinite(action).all();obs,reward,done,info=runner.env.step(action)
      assert int(real._sim_step_counter)-t==8 and int(real.h1_callback_count)-ct==8 and int(real._integrated_contact.tick)-contact==8 and int(real._feedback_100hz_tick)-f==2
      assert obs['policy'].shape==(20000,35) and obs['critic'].shape==(20000,38) and torch.isfinite(obs['policy']).all() and torch.isfinite(obs['critic']).all() and torch.isfinite(reward).all()
      reset=done.bool();expected=torch.where(reset,torch.zeros_like(age),age+2);assert torch.equal(real.h1_phase.age_control,expected)
      rows.append(dict(control=i+1,physics_tick=int(real._sim_step_counter),feedback_100Hz_tick=int(real._feedback_100hz_tick),H1_callback_count=int(real.h1_callback_count),selected_episode_resets=int(reset.sum()),public_age100Hz_plus2_or_selected_reset0=True))
    assert int(real._sim_step_counter)-start_tick==192 and int(real._feedback_100hz_tick)-start_feedback==48 and int(real.h1_callback_count)-start_callbacks==192
    assert all(exact(model.state_dict(),before[k]) for k,model in [('actor',runner.alg.actor),('critic',runner.alg.critic)]) and exact(runner.alg.optimizer.state_dict()['state'],opt) and runner.alg.optimizer.state_dict()['param_groups']==groups
    put('MOD4V1_NORMAL_H1_NATIVE24_192PHYSICS_48FEEDBACK_NOUPDATE.json',dict(passed=True,source_SHA=SOURCE,new_asset_nominal_guard=real._mod4v1_nominal_guard.receipt(),source_cache_purpose=cache.receipt(),asset_USD_SHA=identity.usd_sha256,asset_contract_SHA=identity.contract_sha256,num_envs=20000,controls=24,physics_callbacks=192,feedback100Hz_samples=48,policy_hz=50,physics_dt_s=.0025,public_phase_tick_hz=100,original270_goal_landing12_recovery200_callbacks_unchanged=True,source_17Adam_step=832460,LR=.00038443359375000017,mean_policy_only=True,all_actor_critic_STD_norm_optimizer_literal_unchanged=True,no_PPO_or_normalization_update=True,per_control=rows,skill_graduation=False,not_complete_WM_dataset=True))
   cache=PinnedSourceH1(torch,source,SOURCE,16879851)
   with selected_source(cache):
    rescue_training.learn=work;ns['main']()
  except BaseException:
   put('NORMAL_H1_NATIVE24_ORIGINAL_EXCEPTION_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_optimizer_or_GO=True));raise
  finally:
   put('APP_CLOSING.json',dict(epoch=time.time()))
   if ns is not None:ns['app'].close()
if __name__=='__main__':main()
