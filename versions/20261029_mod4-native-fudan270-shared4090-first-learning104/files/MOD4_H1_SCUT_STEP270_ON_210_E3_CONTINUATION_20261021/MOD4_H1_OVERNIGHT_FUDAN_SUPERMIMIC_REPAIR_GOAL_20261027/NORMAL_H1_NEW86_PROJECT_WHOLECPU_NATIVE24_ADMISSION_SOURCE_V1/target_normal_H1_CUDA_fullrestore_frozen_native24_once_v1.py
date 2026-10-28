"""Frozen mean24-controls admission, original normal-H1 D1-D7 path, no PPO."""
from pathlib import Path
import argparse,hashlib,json,os,runpy,sys,time,traceback
SOURCE='71db5543b14919eb11d2a8606f9ffe1acf0814260d7d89aa823565a49a7b21c4'
GPU='GPU-90a66ae2-f536-7033-79c0-487536ae36d3'
def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True);a=p.parse_args();B=a.job_root.resolve();J=B/'job0';O=B/'native24_admission';O.mkdir()
 def put(n,v):
  with (O/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
 stat=Path('/proc/self/stat').read_text();v=stat[stat.rfind(')')+2:].split();boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '));put('GPU_OWN_WORKER_IDENTITY.json',dict(pid=os.getpid(),creation=boot+int(v[19])/os.sysconf('SC_CLK_TCK'),exe=os.readlink('/proc/self/exe'),argv=[os.fsdecode(x) for x in Path('/proc/self/cmdline').read_bytes().split(bytes([0])) if x],cwd=os.readlink('/proc/self/cwd')))
 task=json.loads((B/'NATIVE24_ADMISSION_TASK.json').read_bytes());assert task['kind']=='normal_H1_PPO86B40050_frozen_native24_admission_v1' and task['source_SHA']==SOURCE and task['no_optimizer_or_normalizer_update'] and task['private_EX_held_by_parent'] and task['CPU_actual_waited_returncode0']
 assert os.environ['CUDA_VISIBLE_DEVICES']==GPU and H(B/'NORMAL_H1_TARGET_INITIAL_WHOLE_SOURCE_SDK_CPU_ACTUAL.json')==task['actual_CPU_report_SHA'];cpu=json.loads((B/'NORMAL_H1_TARGET_INITIAL_WHOLE_SOURCE_SDK_CPU_ACTUAL.json').read_bytes());assert cpu['passed'] and cpu['source_SHA']==SOURCE
 waited=B/'NORMAL_H1_TARGET_CPU_ORIGINAL_WAIT_PROOF.json';assert H(waited)==task['actual_CPU_waited_proof_SHA'];proof=json.loads(waited.read_bytes());assert proof['actual_waited'] and proof['returncode']==0 and proof['report_SHA']==task['actual_CPU_report_SHA'] and proof['passed']
 source=J/'source/NORMAL_H1_86B138_N20K_PPO50_GAS400_NOT_GPU_ADMITTED.pt';assert H(source)==SOURCE
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 original=json.loads((J/'original_run_manifest.json').read_bytes())['env'];os.environ.update({k:str(v) for k,v in original.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')});os.environ.update(RM_MOD4_USD=str(J/'assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0',RM_KEEP_STD='1',RM_RESCUE_STOP_FILE=str(O/'UNUSED_STOP.json'),OWN_E2_H1_KIND='normal_H1_PPO86B40050_frozen_native24_admission_v1')
 sys.path[:0]=[str(B/'lib'),str(J/'runtime/isaac/mod4'),str(B)];entry=J/'runtime/isaac/mod4/train_H1_ground_prelaunch_fullstate_v2.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed','20260928','--steps_per_env','24','--learning_rate','.00038443359375000017','--save_interval','25','--init_checkpoint',str(source),'--log_root',str(O/'logs'),'--run_name','NORMAL_H1_FROZEN_NATIVE24_NO_PPO','--additional_iterations','1']
 ns=None;created=[None]
 try:
  ns=runpy.run_path(str(entry),run_name='normal_H1_original_restoration_configuration_only')
  import h1_scut_fudan_jump_reward_v1 as scut
  import h1_step270_sdk_runtime_candidate as terrain
  oldconfigure=scut.configure;scut.configure=lambda cfg:terrain.configure_rewards(cfg,oldconfigure)
  factory=ns['build_env'];original_cfg=ns['Mod4EnvCfg']
  def cfg():
   c=original_cfg();c.scene.num_envs=20000;c.seed=20260928;c.sim.device='cuda:0';assert float(c.terminations.closure.params['threshold'])==.002 and float(c.terminations.mimic.params['threshold'])>=.01;c.terminations.mimic.params={**c.terminations.mimic.params,'threshold':.01};return c
  factory.__globals__.update(Mod4Env=terrain.H1Step270Env,Mod4EnvCfg=cfg)
  def build():
   env=factory();created[0]=env;assert env.num_envs==20000 and env.physics_dt==.0025 and env.step_dt==.02 and env.cfg.decimation==8 and env._physics_action_delay.queue.control_us==20000;return env
  ns['main'].__globals__['build_env']=build
  import h1_fullstate_checkpoint_v1 as checkpoint_API
  from h1_step270_fullstate_checkpoint_candidate_uninstalled import resume_step270_new_episode,install_step270_save_contract
  checkpoint_API.resume_h1_new_episode=resume_step270_new_episode;checkpoint_API.install_h1_save_contract=install_step270_save_contract
  import torch,rescue_training
  from spring_pressure_checkpoint import exact
  from h1_reward_scope_v1 import isolated_actual_SDK_dt_probe
  def work(runner,n,log_dir):
   runner.logger.writer=None;real=runner.env.unwrapped;ck=torch.load(source,map_location='cpu',weights_only=False)
   assert runner.current_learning_iteration==41448 and runner.alg.learning_rate==runner.alg.optimizer.param_groups[0]['lr']==.00038443359375000017
   assert runner.alg.__class__.__module__=='owned_h1_public4_mean_overflow_ppo_v2'
   for k,x in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(x,ck[k]),k
   assert {int(x['step']) for x in runner.alg.optimizer.state_dict()['state'].values()}=={832460} and int(real._sim_step_counter)==0 and not real.h1_phase.age_control.any()
   assert real.spring_pressure_recipe()['nominal_stiffness_N_m']==2000 and real.action_delay_recipe()['control_period_us']==20000
   required={'SENSOR_RESUME_STARTUP_VERIFIED.json','DELAY_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','STEP270_FULLSTATE_RESUME_STARTUP_VERIFIED.json'}
   actual={p.name:p for p in Path(log_dir).glob('*STARTUP_VERIFIED.json')};assert required<=set(actual)
   receipts=[dict(path=str(actual[name]),value=json.loads(actual[name].read_bytes())) for name in sorted(required)]
   probe=isolated_actual_SDK_dt_probe(real);assert probe['dt']==.02
   put('ACTUAL_NORMAL_H1_CUDA_FULLRESTORE_BEFORE_MEAN_ACTION.json',dict(passed=True,source_SHA=SOURCE,Adam832460=True,constructor_and_optimizer_LR=.00038443359375000017,full_D1_D7_H1_restore_receipts=receipts,actual_reward_manager_dt_probe=probe,original270_goal=True,no_optimization=True))
   runner.alg.actor.eval();runner.alg.critic.eval();before={k:{name:value.detach().clone() for name,value in model.state_dict().items()} for k,model in [('actor',runner.alg.actor),('critic',runner.alg.critic)]};opt={k:{name:value.detach().clone() if torch.is_tensor(value) else value for name,value in row.items()} for k,row in runner.alg.optimizer.state_dict()['state'].items()};groups=runner.alg.optimizer.state_dict()['param_groups']
   obs=runner.env.get_observations();rows=[];start_tick=int(real._sim_step_counter);start_feedback=int(real._feedback_100hz_tick);start_callbacks=int(real.h1_callback_count)
   with torch.inference_mode():
    for i in range(24):
     t=int(real._sim_step_counter);f=int(real._feedback_100hz_tick);ct=int(real.h1_callback_count);contact=int(real._integrated_contact.tick);age=real.h1_phase.age_control.clone();action=runner.alg.actor(obs,stochastic_output=False);assert action.shape==(20000,6) and torch.isfinite(action).all();obs,reward,done,info=runner.env.step(action)
     assert int(real._sim_step_counter)-t==8 and int(real.h1_callback_count)-ct==8 and int(real._integrated_contact.tick)-contact==8 and int(real._feedback_100hz_tick)-f==2
     assert obs['policy'].shape==(20000,35) and obs['critic'].shape==(20000,38) and torch.isfinite(obs['policy']).all() and torch.isfinite(obs['critic']).all() and torch.isfinite(reward).all()
     reset=done.bool();expected=torch.where(reset,torch.zeros_like(age),age+2);assert torch.equal(real.h1_phase.age_control,expected)
     rows.append(dict(control=i+1,physics_tick=int(real._sim_step_counter),feedback_100Hz_tick=int(real._feedback_100hz_tick),H1_callback_count=int(real.h1_callback_count),selected_episode_resets=int(reset.sum()),public_age100Hz_plus2_or_selected_reset0=True))
   assert int(real._sim_step_counter)-start_tick==192 and int(real._feedback_100hz_tick)-start_feedback==48 and int(real.h1_callback_count)-start_callbacks==192
   assert all(exact(model.state_dict(),before[k]) for k,model in [('actor',runner.alg.actor),('critic',runner.alg.critic)]) and exact(runner.alg.optimizer.state_dict()['state'],opt) and runner.alg.optimizer.state_dict()['param_groups']==groups
   put('ACTUAL_NORMAL_H1_CUDA_NATIVE24_192PHYSICS_48FEEDBACK_ADMISSION.json',dict(passed=True,source_SHA=SOURCE,num_envs=20000,controls=24,physics_callbacks=192,feedback100Hz_samples=48,policy_hz=50,physics_dt_s=.0025,public_phase_tick_hz=100,original270_goal_landing12_recovery200_callbacks_unchanged=True,source_17Adam_step=832460,LR=.00038443359375000017,mean_policy_only=True,all_actor_critic_STD_norm_optimizer_literal_unchanged=True,no_PPO_or_normalization_update=True,per_control=rows,skill_graduation=False,not_complete_WM_dataset=True))
  rescue_training.learn=work;ns['main']()
 except BaseException:
  put('NORMAL_H1_NATIVE24_ORIGINAL_EXCEPTION_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_optimizer_or_GO=True));raise
 finally:
  put('APP_CLOSING.json',dict(epoch=time.time()))
  if ns is not None:ns['app'].close()
if __name__=='__main__':main()
