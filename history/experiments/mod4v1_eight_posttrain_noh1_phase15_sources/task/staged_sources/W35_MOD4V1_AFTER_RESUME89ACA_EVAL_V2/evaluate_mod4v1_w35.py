"""ROOT-only32s max no-PPO skill facts using frozen219/214 physical runtime.

One selected NEW formal byte/hash/decode;213-style sameUID/pre-reset observer.
No old raw, NPZ or model reader beyond original physical constructor/own saves.
"""
from pathlib import Path
import argparse,hashlib,json,os,runpy,sys,time,traceback
from postadapt_eval_contract import SHA as MODEL,BYTES,ITER,ADAM,LR,UPDATES,validate_task
OUT=None


def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (OUT/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
 global OUT
 p=argparse.ArgumentParser();p.add_argument('--task',type=Path,required=True);a=p.parse_args();job=a.task.resolve().parent
 task=read(a.task);validate_task(task,admitted=True)
 assert task['model_SHA']==MODEL and task['model_bytes']==BYTES and task['model_iteration']==ITER
 assert task['Adam17']==ADAM and task['model_new_PPO_updates']==UPDATES and task['num_envs']==20000
 assert task['controls_max']==1600 and task['no_new_learning_or_GO'] and task['actual_current_authority_private_shared_resources_admitted']
 assert task['worker_seconds']==3600 and task['parent_seconds']==3780 and task['actual_saved_LR'] is None
 assert task['telemetry_producer']['format']=='mod4.227.lossless_fieldset_positional_jsonl.v1'
 for key,name in [('observer_SHA','rm70_intervals227.py'),('writer_SHA','positional_rows227.py'),('decoder_SHA','decode227_positional.py')]:assert H(job/name)==task['telemetry_producer'][key]
 assert os.environ['CUDA_VISIBLE_DEVICES']==task['GPU_UUID'] and H(__file__)==task['worker_SHA']
 ROOT=Path(task['producer_job_root']);runtime=Path(task['runtime_job'])/'runtime';mod=runtime/'isaac/mod4'
 assert Path(task['model_path']).parent==ROOT/'production' and Path(task['model_path']).name=='model_final_complete.pt'
 assert H(Path(task['runtime_job'])/'original_run_manifest.json')=='0543b0c47c53e15da0d7d017693d2b69f7f6354ef088c3a1b8ed2b9cc56e2beb'
 OUT=job/'actual_latest32';OUT.mkdir(exist_ok=False);deadline=time.time()+3600;ns=book=cache=None;guard_uninstall=None
 original=read(Path(task['runtime_job'])/'original_run_manifest.json')['env']
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 os.environ.update({k:str(v) for k,v in original.items() if k not in ('RM_RESCUE_STOP_FILE','RM_RESCUE_DEADLINE')})
 os.environ.update(RM_MOD4_USD=str(runtime/'assets/robot.usd'),RM_RESCUE_STOP_FILE=str(OUT/'STOP.json'),RM_RESCUE_DEADLINE=str(deadline),
  MOD4_RESUME_QUEUE_CONTROL_US='20000',MOD4_RM70_ORIGINAL_ASSET_ROOT=str(Path(task['runtime_job'])/'original_field'),
  MOD4_RM70_ASSET_RECEIPT=str(Path(task['runtime_job'])/'RM70_BINARY_INSTALL_ACTUAL.json'),MOD4_RM70_NEW_LAYOUT_ROOT=str(OUT/'new_original_CAD_layout'),
  MOD4_NEW208_JOB_ROOT=task['runtime_job'],MOD4V1_ASSET_DIR=str(runtime/'assets'))
 storage=Path(task['runtime_job'])/'kit_isolation';storage.mkdir(exist_ok=False);(storage/'data').mkdir();(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
 os.environ['MOD4_W35_OWN_KIT_STORAGE_ROOT']=str(storage)
 sys.path[:0]=[str(job),str(mod),str(runtime)]
 import torch
 from source_cache208_v3 import PinnedSource208,selected_source
 from rm70_intervals227 import RM70Intervals227
 from positional_rows227 import configure227_producer
 configure227_producer(dict(task['telemetry_producer'],source_model_SHA=MODEL))
 cache=PinnedSource208(torch,task['model_path'],MODEL,BYTES)
 assert cache.state['iter']==ITER and cache.state['actual_new_PPO_updates']==UPDATES
 assert cache.state['typed_W35_RM70_task']['source_SHA']=='89aca6ce52f8e83719de14dd53cb423a182f14e4f370614887605b2131d5bf0f' and cache.state['typed_W35_RM70_task']['kind']=='MOD4V1_W35_RESUME32561_FULLD0D7_RM70_V3'
 entry=mod/'train_mod4v1_w35.py';assert H(entry)==task['original_entry_SHA']
 sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed','20260928','--steps_per_env','24',
  '--learning_rate',str(float(cache.state['optimizer_state_dict']['param_groups'][0]['lr'])),'--save_interval','25','--init_checkpoint',task['model_path'],
  '--log_root',str(OUT/'logs'),'--run_name','POSTADAPT_MOD4V1_RM70_NO_PPO','--additional_iterations','1']
 with selected_source(cache):
  try:
   ns=runpy.run_path(str(entry),run_name='postadapt_mod4v1_config_no_old_main')
   import rescue_training
   from command208_v3 import RM70Command208
   from spring_pressure_checkpoint208_v3 import exact
   from retention_flat_runtime import tensor
   book=RM70Intervals227(torch,20000,'cuda:0',OUT,MODEL);book.install(RM70Command208)
   def work(runner,n,log_dir):
    runner.logger.writer=None;real=runner.env.unwrapped;vec=runner.env;robot=real.scene['robot'];cmd=real.command_manager.get_term('twist')
    runner.alg.actor.eval();runner.alg.critic.eval();runner.alg.learning_rate=runner.alg.optimizer.param_groups[0]['lr']
    assert real.num_envs==20000 and real.physics_dt==.0025 and real.step_dt==.02 and real.cfg.decimation==8 and real._sim_step_counter==0
    assert real._physics_action_delay.queue.control_us==20000 and real.spring_pressure_recipe()['nominal_stiffness_N_m']==2000
    assert real.cfg.terminations.closure.params['threshold']==.01 and real.cfg.terminations.mimic.params['threshold']==.01
    guard=real._mod4v1_fresh_dr_guard.receipt();assert guard['new_constructor_nominal_caches_preserved'] and guard['fresh_D0_mass_inertia_based_on_new_asset'] and guard['original_fresh_reset_calls']==1 and guard['usd_sha256']==task['asset_USD_SHA'] and guard['contract_sha256']==task['asset_contract_SHA']
    assert runner.current_learning_iteration==ITER and runner.alg.learning_rate==float(cache.state['optimizer_state_dict']['param_groups'][0]['lr'])
    assert {int(v['step']) for v in runner.alg.optimizer.state_dict()['state'].values()}=={ADAM}
    assert len(runner.alg.optimizer.state_dict()['state'])==17
    for key,current in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(current,cache.state[key]),key
    terrain=read(Path(log_dir)/'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json')
    assert terrain['source_sha256']==MODEL and terrain['original_terrain_restored_exact'] and terrain['one_new_physical_episode']
    assert not cmd.manual_evaluation_mode and list(cmd.cfg.resampling_time_range)==[12.,16.] and cmd.cfg.rel_standing_envs==.2
    assert tuple(cmd.cfg.ranges.lin_vel_x)==(-.3,.3) and tuple(cmd.cfg.ranges.lin_vel_y)==(0.,0.) and tuple(cmd.cfg.ranges.ang_vel_z)==(0.,0.)
    assert real.scene.terrain.retention_assignment_sha=='9f05b0cae71752f36ba95465ed6723f96321c1fd2262bb1e2d0f363c8266397b'
    origin=book.arm(real,cmd)
    def forbidden(*args,**kwargs):raise RuntimeError('NEW227 is evaluation only;optimizer/update forbidden')
    old_update=runner.alg.update;old_step=runner.alg.optimizer.step;runner.alg.update=forbidden;runner.alg.optimizer.step=forbidden
    oldterm=real.termination_manager.compute;oldreward=real.reward_manager.compute;rewards_dt=[]
    def term(*aa,**kk):
     value=oldterm(*aa,**kk);book.terminal(real._e1_pre_reset_frame,real.termination_manager);return value
    def reward(*aa,**kk):
     dt=kk.get('dt',aa[0] if aa else None);assert dt==.02;rewards_dt.append(dt);return oldreward(*aa,**kk)
    real.termination_manager.compute=term;real.reward_manager.compute=reward
    obs=vec.get_observations();real._mod4v1_fresh_dr_guard.check_observations(obs);put('MOD4V1_FULLRESTORE_GUARD_ACTUAL.json',real._mod4v1_fresh_dr_guard.receipt());tick=int(real._integrated_contact.tick);fb=int(real._feedback_100hz_tick);queues=dict(real._physics_action_delay.calls);completed=0
    put('FULLRESTORE227_BEFORE_CONTROL.json',dict(passed=True,source_SHA=MODEL,iteration=ITER,Adam17=ADAM,actual_LR=runner.alg.learning_rate,
     actor_critic_STD_optimizer_verified=True,original_D0_D7_then_one_new_episode=True,initial_origin=origin,
     source_cache=cache.receipt(),original_rough_command_and_reward_unchanged=True,new_mod4v1_fullrestore_guard=guard,actual_mimic_radians=.01,actual_closure_m=.01))
    try:
     with torch.inference_mode():
      for i in range(1600):
       if time.time()>=deadline:break
       book.begin(i,tensor(robot.data.root_pos_w)[:,:2].clone(),tensor(robot.data.heading_w).clone())
       action=runner.alg.actor(obs,stochastic_output=False);obs,reward_value,done,extra=vec.step(action);completed+=1
       assert obs['policy'].shape==(20000,35) and obs['critic'].shape==(20000,38) and torch.isfinite(obs['policy']).all() and torch.isfinite(obs['critic']).all() and torch.isfinite(reward_value).all()
       if (Path(log_dir)/'STOP_AFTER_SAVE').exists():raise RuntimeError('Original runtime health stop,not bypassed')
       if completed==24:
        assert int(real._integrated_contact.tick)-tick==192 and int(real._feedback_100hz_tick)-fb==48 and rewards_dt==[.02]*24
        put('NATIVE24_227_PART_OF_SAME_CASE.json',dict(passed=True,controls=24,physics=192,feedback=48,optimizer_steps=0,actual_mimic_radians=.01,actual_closure_m=.01))
     assert completed>0 and int(real._integrated_contact.tick)-tick==8*completed and int(real._feedback_100hz_tick)-fb==2*completed
     assert rewards_dt==[.02]*completed
     assert {k:real._physics_action_delay.calls[k]-queues[k] for k in ('legs','wheels')}=={'legs':8*completed,'wheels':8*completed}
     for key,current in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(current,cache.state[key]),key
     facts=book.finish();book.finished=True
     put('ACTUAL227_CLOSED_RM70_SKILL_FACTS.json',dict(passed_execution=True,source_SHA=MODEL,controls=completed,
      physics=8*completed,feedback=2*completed,seconds=.02*completed,requested_max_controls=1600,
      bounded_window_complete=completed==1600,source_cache=cache.receipt(),facts=facts,
      original_conditions='MOD4v1 2c/bae +400N50D0-D7/CAD70 peak-valley/user closure10mm/mimic.01/original sampler and reward',
      core_and_17Adam_unchanged=True,optimizer_steps=0,account_writes=0,new_learning_GO=False,
      explicit_mimic_guard_tightening_from_legacy05=True,user_authorized_closure10mm=True,previous_closure_m=.002,actual_mimic_radians=.01,actual_closure_m=.01,full_expert_skill='UNKNOWN',full_SuperMimic_conversion=False,
      original_runtime_retention_outputs='Original own startup roundtrip .pt and new retention prefixes remain original producer artifacts;not consumed old raw or full WM dataset'))
    finally:
     real.termination_manager.compute=oldterm;real.reward_manager.compute=oldreward;runner.alg.update=old_update;runner.alg.optimizer.step=old_step
   rescue_training.learn=work;ns['main']();put('ENV227_CLOSE_RETURNED.json',dict(epoch=time.time(),closed=True))
  except BaseException:
   put('ORIGINAL227_EVAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
  finally:
   if book is not None:
    if not getattr(book,'finished',False):
     try:put('PARTIAL227_SKILL_FACTS_ON_ERROR.json',book.finish())
     except BaseException:put('PARTIAL227_OBSERVER_ERROR.json',dict(error=traceback.format_exc()))
    book.uninstall()
   put('SOURCE227_FINAL_READ_COUNTS.json',cache.receipt())
   if guard_uninstall is not None:guard_uninstall()
   if ns is not None:
    put('APP227_CLOSING.json',dict(epoch=time.time(),source='Appclose may exit interpreter;use originalwaitRC0,not postclose marker'))
    ns['app'].close()


if __name__=='__main__':main()
