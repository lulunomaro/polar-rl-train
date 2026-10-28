"""NEW bounded frozen E0 case. Original20k D1-D7 reset/restore, zero PPO steps.

No budget/transport/GO writer. Parent holds source210 private GPU lock and gives
the fresh SDK/resource and known-active-original72-owner readonly admission.
This short regression is not a graduation protocol or complete WM dataset.
"""
from pathlib import Path
import argparse,hashlib,json,os,runpy,sys,time,traceback
MODEL_SHA='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a'
GPU='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'
OUT=None
def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(n,v):
 with (OUT/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def read(p):return json.loads(Path(p).read_bytes())
def main():
 global OUT
 p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True);a=p.parse_args();job=a.job_root.resolve();task=read(job/'FROZEN_CASE_TASK.json')
 assert task['kind']=='MOD4_E0_ADAPTED40050_ORIGINAL_N20K_FROZEN_REGRESSION_V1' and task['source_SHA']==MODEL_SHA
 assert task['no_optimizer_steps'] is True and task['num_envs']==20000 and 1<=task['controls']<=120 and 60<=task['maximum_worker_seconds']<=480
 assert task['actual_source210_SDK_admission_passed'] and task['actual_private_GPU_EX_held_by_parent'] and task['canonical72_known_owner_readonly_passed']
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==GPU
 OUT=job/'frozen_regression';OUT.mkdir();started=time.time();deadline=started+task['maximum_worker_seconds']
 source=job/'source/E0_ADAPTED89D_FINAL82.pt';assert H(source)==MODEL_SHA and source.stat().st_size==14031973
 original=read(job/'original_run_manifest.json');assert H(job/'original_run_manifest.json')=='1dbde5972c65baf8842bc82024fe7ddfd6393d73a51137cc9880ed6310ff1af1'
 for key in list(os.environ):
  if key.startswith('RM_') or key in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[key]
 env={k:str(v) for k,v in original['env'].items() if k not in ('RM_RESCUE_STOP_FILE','RM_RESCUE_DEADLINE')}
 env.update(RM_MOD4_USD=str(job/'runtime/assets/robot.usd'),RM_RESCUE_STOP_FILE=str(OUT/'STOP.json'),RM_RESCUE_DEADLINE=str(deadline));os.environ.update(env);os.environ['MOD4_RESUME_QUEUE_CONTROL_US']='20000'
 mod=job/'runtime/isaac/mod4';sys.path[:0]=[str(job/'lib'),str(mod),str(job/'runtime')]
 entry=mod/'train_chassis_pd_resume_ppo.py'
 sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed','20260928','--steps_per_env','24','--learning_rate','.00038443359375000017','--save_interval','25','--init_checkpoint',str(source),'--log_root',str(OUT/'logs'),'--run_name','FROZEN_E0_ADAPTED40050_CASE_NO_PPO','--additional_iterations','1']
 ns=runpy.run_path(str(entry),run_name='frozen_E0_original_restore_config')
 import torch,numpy as np,rescue_training
 from spring_pressure_checkpoint import exact
 from spring_nominal_sdk_readback import tensor
 def work(runner,n,log_dir):
  runner.logger.writer=None;runner.alg.learning_rate=runner.alg.optimizer.param_groups[0]['lr'];real=runner.env.unwrapped;vec=runner.env
  assert real.num_envs==20000 and real.physics_dt==.0025 and real.step_dt==.02 and real.cfg.decimation==8 and real._sim_step_counter==0
  assert real._physics_action_delay.queue.control_us==20000 and real.spring_pressure_recipe()['nominal_stiffness_N_m']==2000
  steps={int(x['step']) for x in runner.alg.optimizer.state_dict()['state'].values()};assert steps=={641200}
  receipts=list(Path(log_dir).glob('*STARTUP_VERIFIED.json'));required={'SENSOR_RESUME_STARTUP_VERIFIED.json','DELAY_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json'};assert required<={x.name for x in receipts}
  for q in receipts:assert read(q).get('source_sha256',MODEL_SHA)==MODEL_SHA
  runner.alg.actor.eval();runner.alg.critic.eval()
  before={k:{name:value.detach().clone() for name,value in model.state_dict().items()} for k,model in [('actor',runner.alg.actor),('critic',runner.alg.critic)]};opt={k:{name:value.detach().clone() if torch.is_tensor(value) else value for name,value in row.items()} for k,row in runner.alg.optimizer.state_dict()['state'].items()}
  put('ACTUAL_ORIGINAL_N20K_CUDA_FULLRESTORE_BEFORE_MEAN_ACTION.json',dict(passed=True,source_SHA=MODEL_SHA,Adam_step=641200,num_envs=20000,original_D1_D7_reset_and_private_RNG_restore_retained=True,receipts=[dict(path=str(q),value=read(q)) for q in receipts],no_PPO_or_optimizer_or_norm_update=True))
  ids=torch.arange(32,device=real.device);frames=[];metrics=[];terminal=[None];oldterm=real.termination_manager.compute
  def term(*aa,**kk):
   result=oldterm(*aa,**kk);r=real.scene['robot'];terminal[0]=dict(root13=tensor(r.data.root_state_w)[ids].detach().clone(),q30=tensor(r.data.joint_pos)[ids].detach().clone(),executed6=real.action_manager.action[ids].detach().clone(),terminated=real.termination_manager.terminated[ids].clone(),truncated=real.termination_manager.time_outs[ids].clone())
   cmd=real.command_manager.get_term('twist').command;velocity=tensor(r.data.root_lin_vel_b)
   metrics.append(dict(control=len(metrics)+1,physics_tick=int(real._sim_step_counter),forward_command_abs_mean=float(cmd[:,0].abs().mean()),forward_abs_tracking_error_mean=float((cmd[:,0]-velocity[:,0]).abs().mean()),yaw_abs_tracking_error_mean=float((cmd[:,2]-tensor(r.data.root_ang_vel_b)[:,2]).abs().mean()),terminated_count=int(real.termination_manager.terminated.sum()),truncated_count=int(real.termination_manager.time_outs.sum()),root_height_mean=float(tensor(r.data.root_state_w)[:,2].mean())))
   return result
  real.termination_manager.compute=term;obs=vec.get_observations();completed=0
  with torch.inference_mode():
   for i in range(task['controls']):
    if time.time()>=deadline:break
    robot=real.scene['robot'];root=tensor(robot.data.root_state_w)[ids].clone();command=real.command_manager.get_term('twist').command[ids].clone();bodyv=tensor(robot.data.root_lin_vel_b)[ids].clone();tick=real._integrated_contact.tick;fb=real._feedback_100hz_tick
    action=runner.alg.actor(obs,stochastic_output=False);requested=action[ids].detach().clone();terminal[0]=None;obs,reward,done,info=vec.step(action)
    assert real._integrated_contact.tick-tick==8 and real._feedback_100hz_tick-fb==2 and terminal[0] is not None and torch.isfinite(reward).all() and torch.isfinite(obs['policy']).all() and torch.isfinite(obs['critic']).all()
    end=terminal[0];row=dict(before_root13=root,terminal_root13=end['root13'],terminal_q30=end['q30'],requested6=requested,executed6=end['executed6'],command3=command,before_body_velocity3=bodyv,terminated=end['terminated'],truncated=end['truncated'])
    frames.append({k:v.detach().cpu().numpy() for k,v in row.items()});completed+=1
  real.termination_manager.compute=oldterm
  assert completed>0 and all(exact(model.state_dict(),before[k]) for k,model in [('actor',runner.alg.actor),('critic',runner.alg.critic)]) and exact(runner.alg.optimizer.state_dict()['state'],opt)
  path=OUT/'selected32_actual_before_and_terminal_prefix.npz'
  with path.open('xb') as f:np.savez_compressed(f,**{k:np.stack([x[k] for x in frames]) for k in frames[0]})
  put('BOUNDED_FROZEN_E0_MEAN_REGRESSION_ACTUAL.json',dict(passed_execution=True,source_SHA=MODEL_SHA,source_adaptation_updates=82,controls=completed,simulated_seconds=completed*.02,requested_controls=task['controls'],wall_time_limited=completed<task['controls'],num_envs=20000,selected_trace_env_ids=list(range(32)),core_actor_critic_STD_optimizer_literal_unchanged=True,all17_Adam_steps=641200,no_optimizer_step_no_norm_update=True,deterministic_mean_policy=True,original_reset_D1_D7_and_seconds_clock_retained=True,trace=dict(path=str(path),bytes=path.stat().st_size,SHA=H(path),endpoint_before_autoreset=True),all_population_metrics=metrics,source_legacy_entry_mode_train_does_not_mean_optimizer_executed=True,skill_graduation=False,complete_typed_WM_dataset=False))
 rescue_training.learn=work
 try:ns['main']()
 finally:
  put('APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()
if __name__=='__main__':
 try:main()
 except BaseException:
  if OUT and OUT.exists():put('FROZEN_E0_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_source_promotion_or_optimizer_step=True))
  raise
