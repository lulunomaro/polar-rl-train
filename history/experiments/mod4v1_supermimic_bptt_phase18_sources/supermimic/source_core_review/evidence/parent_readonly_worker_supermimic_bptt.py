"""New original-owner admitted SuperMimic/context-reward BPTT training worker.
New algorithm, original plant/reward/DR. No old PPO learn/main or optimizer resume.
"""
from pathlib import Path
import argparse,os,sys,json,time,hashlib,runpy,traceback,shutil
KIND='MOD4V1_SUPERMIMIC_BPTT_TASK_V1'

def put(path,value):
 path=Path(path);tmp=path.with_suffix(path.suffix+'.partial');tmp.write_text(json.dumps(value,indent=2,allow_nan=False),encoding='utf-8');os.replace(tmp,path)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class WindowSavedStop(Exception):pass

def main():
 q=argparse.ArgumentParser();q.add_argument('--job-root',required=True,type=Path);a=q.parse_args();J=a.job_root.resolve();task=json.loads((J/'TASK.json').read_bytes());go=json.loads((J/'GO_PRODUCTION.json').read_bytes());ad=json.loads((J/'ROOT_ADMISSION_ACTUAL.json').read_bytes());out=J/'production';assert not out.exists();assert task['kind']==go['kind']==KIND and task['role']!='H1'and task['role']==go['role']==ad['role'];assert task['run_id']==go['run_id']==ad['run_id'];assert H(J/'ROOT_ADMISSION_ACTUAL.json')==task['root_admission_SHA'];assert ad['actual_original_authority_EX_private_GPU_EX_finite_SH']and ad['original_canonical_owner_admitted'];assert task['owner_parent_pid']==os.getppid()and os.environ['CUDA_VISIBLE_DEVICES']==task['GPU_UUID']
 for fd in task['inherited_lock_fds']:os.fstat(fd)
 assert len(task['inherited_lock_fds'])==4 and time.time()<go['save_deadline'];assert task['num_envs']in(512,1024,2048)and task['target_bptt_steps']>=3000;manifest=json.loads((J/'INSTALL_MANIFEST.json').read_bytes());assert H(J/'INSTALL_MANIFEST.json')==task['manifest_SHA']
 for f in manifest['files']:
  p=J/f['relative'];assert p.resolve().is_relative_to(J)and p.suffix.lower()not in('.pt','.pth','.ckpt');assert p.stat().st_size==f['bytes']and H(p)==f['SHA']
 out.mkdir();ns=env=teacher=bridge=learner=guard=None;error=None;latest=None;stop=False;role=task['role'];start=time.time();saved_count=0
 put(out/'TASK_AND_ORIGINAL_RESOURCE_BOUND_BEFORE_SDK_MODEL.json',dict(epoch=start,role=role,kind=KIND,canonical_binding=ad['canonical_binding'],fd_existence_verified=True,source_PT_reads=0,SDK_constructed=False,child_canonical_reads_writes=0))
 try:
  family=task['family'];mod=J/'runtime/isaac/mod4'
  for name in list(os.environ):
   if name.startswith(('RM_','MOD4V1_','MOD4_RESUME_'))or name in('PYTHONPATH','OWN_E2_H1_KIND','RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[name]
  if family=='e1':meta=json.loads((J/'E1_CANONICAL_SOURCE_METADATA.json').read_bytes());original=meta['original_env'];entry=mod/meta['entry']
  else:original=json.loads((J/'original_run_manifest.json').read_bytes())['env'];entry=mod/('train_mod4v1_'+role.lower()+'.py')
  os.environ.update({k:str(v)for k,v in original.items()if k not in('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')});assets=J/('new_assets'if family=='e1'else'runtime/assets');storage=J/'kit_isolation';storage.mkdir();(storage/'data').mkdir();(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
  os.environ.update(RM_MOD4_USD=str(assets/'robot.usd'),RM_KEEP_STD='1',RM_PHYSICS_DT_S='.0025',RM_SOLVER_POS='32',RM_SOLVER_VEL='4',MOD4_RESUME_QUEUE_CONTROL_US='20000',RM_RESCUE_DEADLINE=str(go['save_deadline']),RM_RESCUE_STOP_FILE=str(J/'STOP_AFTER_SAVE.json'),PYTHONDONTWRITEBYTECODE='1')
  if family=='e1':os.environ.update(MOD4V1_E1_ACTUAL_JOB_ROOT=str(J),MOD4V1_E1_KIT_STORAGE_ROOT=str(storage))
  elif role=='W35':os.environ.update(MOD4V1_ASSET_DIR=str(assets),MOD4_RM70_ORIGINAL_ASSET_ROOT=str(J/'original_field'),MOD4_RM70_ASSET_RECEIPT=str(J/'RM70_BINARY_INSTALL_ACTUAL.json'),MOD4_RM70_NEW_LAYOUT_ROOT=str(out/'new_CAD_layout'),MOD4_NEW208_JOB_ROOT=str(J),MOD4_W35_OWN_KIT_STORAGE_ROOT=str(storage))
  else:
   os.environ.update({f'MOD4V1_{role}_ASSET_DIR':str(assets),f'MOD4V1_{role}_JOB_ROOT':str(J),f'MOD4V1_{role}_KIT_STORAGE_ROOT':str(storage)})
   if role in('E2','E3'):os.environ.update(OWN_E2_H1_KIND='E2_WORLD_MOVING_SIGNED4'if role=='E2'else'E3_PUBLIC_RECOVERY',RM_SPAWN_GRACE_STEPS='5',RM_JUMP_SCRIPT_PROB='0',RM_MOD4_MAP='',RM_MOD4_TERRAIN='flat')
  sys.path[:0]=[str(J/'worker_sources'),str(J/'worker_sources/sm_deps'),str(J/'lib'),str(mod),str(J/'runtime'),str(J/'producer/lib'),str(J)];sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs',str(task['num_envs']),'--seed',str(task['seed']),'--steps_per_env','24','--additional_iterations','1']
  if family=='e1':
   from mod4v1_fresh_dr_guard import bind_before_task_import
   identity=bind_before_task_import(assets)
  ns=runpy.run_path(str(entry),run_name='new_supermimic_original_constructor_not_PPO_main')
  import torch
  from mod4v1_fresh_dr_guard import FreshDRNominalGuard,configure_new_task,verify_task_module
  from mild_dr import tensor
  if family=='e1':
   import mod4_task
   verify_task_module(mod4_task,identity);factory=ns['build_env'];oldcfg=ns['Mod4EnvCfg']
   def cfg():
    c=oldcfg();c.terminations.closure.params['threshold']=.01;c.terminations.mimic.params['threshold']=.01;configure_new_task(c,identity);return c
   factory.__globals__['Mod4EnvCfg']=cfg;env=factory()
  else:env=ns['build_env']();identity=ns['MOD4V1_IDENTITY'if role=='W35'else role+'_IDENTITY']
  assert env.num_envs==task['num_envs']and env.physics_dt==.0025 and env.step_dt==.02 and env.cfg.decimation==8;assert env.cfg.terminations.closure.params['threshold']==.01 and env.cfg.terminations.mimic.params['threshold']==.01;assert identity.usd_sha256==task['asset_SHA']and identity.contract_sha256==task['contract_SHA'];assert env.cfg.sim.physics.solver_type==1
  assert env.cfg.scene.robot.spawn.articulation_props.solver_position_iteration_count==32 and env.cfg.scene.robot.spawn.articulation_props.solver_velocity_iteration_count==4;assert env._mild_dr.profile=='white_v3'and env._sensor_mild.profile=='noise_bias_mild_v1';assert env._feedback_delay_mild.enabled and env._physics_action_delay.queue.enabled;assert env._spring_pressure.component.enabled and env._gas_damping.component.enabled and env._chassis_com.component.enabled and env._explicit_pd.component.enabled
  if role=='E3':env.e3_reset_enabled=True
  guard=FreshDRNominalGuard(env,identity,torch_module=torch,tensor_converter=tensor);guard.assert_new_nominals_unchanged();reset=env.reset();obs=reset[0]if isinstance(reset,tuple)else reset;guard.check_observations(obs);audit=guard.verify_live_parameters();assert audit['actual_parameters_pass'];assert env._physics_action_delay.queue.control_us==20000 and env.spring_pressure_recipe()['nominal_stiffness_N_m']==2000
  from native_supermimic_bridge import PinnedTeacher,NativeTaskBridge,TeacherResidualPolicy
  from supermimic_vendor_v2.learner import SuperMimicConfig
  from ctx_reward_learner import ContextRewardLearner
  teacher=PinnedTeacher(task);actor=teacher.build_actor(env.device);bridge=NativeTaskBridge(env,task,out,tensor,teacher,initial_obs=obs);bridge.init_state()
  class Learner(ContextRewardLearner):
   def _make_policy(self):return TeacherResidualPolicy(super()._make_policy(),actor,bridge.mdp.actor_context_offset,scale=.05)
   def _checkpoint(self,include_optimizers):
    value=super()._checkpoint(include_optimizers);value.update(bootstrap_teacher=teacher.receipt(),role=role,original_task_protocol=task['original_protocol'],new_algorithm_not_PPO_resume=True,asset_SHA=task['asset_SHA'],contract_SHA=task['contract_SHA']);return value
   def save(self,path=None,include_optimizers=True):
    nonlocal latest,saved_count
    teacher.assert_frozen();saved_count+=1;dest=out/'checkpoints'/('model_BPTT'+str(self.counts.pi_bptt_optimizer_steps).zfill(6)+'_I'+str(self.iteration).zfill(6)+'_S'+str(saved_count).zfill(4)+'_complete.pt');dest=super().save(dest,include_optimizers=True);raw=dest.read_bytes();latest=dict(epoch=time.time(),path=str(dest),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),iteration=self.iteration,counts=vars(self.counts),full_new_model_critic_aux_optimizers_replay_RNG_hist_saved=True,environment_resume='Explicit new original fresh episode; no bitwise PhysX warmstart claim',teacher_source=teacher.receipt(),teacher_unchanged=True,last_bptt_receipt=self.last_bptt_receipt,skill_pass_rate='PENDING_FROZEN_ORIGINAL_SCOPE');put(out/'latest_complete.json',latest);put(out/('COMPLETE_CHECKPOINT_RECEIPT_'+str(saved_count).zfill(4)+'.json'),latest);return dest
  cfg=SuperMimicConfig(iterations=100000,buffer_steps=128,utd=.4,horizon=16,goal_frames=1,hist=10,z_dim=32,wm_hidden=(512,512,512),policy_hidden=(512,256,128),critic_hidden=(256,128),wm_window=8,wm_batches=4,wm_batch=512,pi_batch=512,lr=1e-4,action_noise=.08,warmup_steps=64,wm_only_iters=100,critic_epochs=2,critic_minibatches=2,ckpt_every=500,log_every=10,log_backend='none',amp='none',compile=False,seed=task['seed']);learner=Learner(bridge,cfg,out/'learner',device=env.device,backend='Original_MOD4v1_'+role+'_freshDR_SuperMimic_WM_BPTT',policy_dt_s=.02);bridge.learner=learner;last_report=[-1]
  def before_action():
   if time.time()>=go['save_deadline']or(J/'STOP_AFTER_SAVE.json').exists()or shutil.disk_usage(out).free<8*1024**3:raise WindowSavedStop()
   if learner.iteration!=last_report[0]and learner.iteration%10==0:
    teacher.assert_frozen();put(out/'PROGRESS.json',dict(epoch=time.time(),role=role,iteration=learner.iteration,counts=vars(learner.counts),last_bptt_receipt=learner.last_bptt_receipt,auxiliary=learner.last_aux,**bridge.metrics()));last_report[0]=learner.iteration
  bridge.before_action=before_action
  put(out/'STARTUP_ACTUAL_NATIVE_SUPERMIMIC.json',dict(epoch=time.time(),role=role,num_envs=env.num_envs,physics_dt=env.physics_dt,policy_dt=env.step_dt,feedback_Hz=100,teacher=teacher.receipt(),new_SuperMimic_optimizer_not_PPO_optimizer=True,physics_native_not_differentiable=True,actual_nominal_parameter_audit=audit,fresh_full_D0_D7=True,one_explicit_fresh_reset=True,no_saved20k_history_slicing=True,no_N80_capacity_preset=True,quaternion_gravity_max_error=bridge.quaternion_gravity_max_error,context_layout=bridge.observed_context_layout,context_dim=bridge.mdp.context_dim,obs_dim=bridge.mdp.obs_dim,target_actual_BPTT_policy_steps=task['target_bptt_steps'],WM_warmup_iters=100,goal_final_success_per_expert=.90,intermediate_floor=.80,not_training_loss_or_no_fall_success_claim=True))
  try:learner.train(target_bptt_steps=task['target_bptt_steps'])
  except WindowSavedStop:stop=True
  finally:learner.save()
  guard.assert_new_nominals_unchanged();after=guard.verify_live_parameters();assert after['actual_parameters_pass'];teacher.assert_frozen();put(out/'FINAL.json',dict(epoch=time.time(),role=role,passed_execution=True,actual_BPTT_policy_steps=learner.counts.pi_bptt_optimizer_steps,counts=vars(learner.counts),target_reached=learner.counts.pi_bptt_optimizer_steps>=task['target_bptt_steps'],parent_finite_saved_stop=stop,checkpoint=latest,teacher=teacher.receipt(),original_parameter_audit_after=after,skill_graduated=False,goal_success_90_percent='PENDING_INDEPENDENT_ACCEPTANCE',**bridge.metrics()))
 except BaseException:
  error=traceback.format_exc();put(out/'WORKER_ERROR.json',dict(epoch=time.time(),role=role,error=error,counts=None if learner is None else vars(learner.counts),source_cache=None if teacher is None else teacher.receipt(),no_unchanged_automatic_retry=True));raise
 finally:
  if bridge is not None:bridge.close()
  if env is not None:
   put(out/'APP_CLOSING.json',dict(epoch=time.time(),calling_original_env_close=True));env.close();put(out/'ENV_CLOSED.json',dict(epoch=time.time(),closed=True))
  if ns is not None:ns['app'].close();put(out/'APP_CLOSED.json',dict(epoch=time.time(),closed=True))
if __name__=='__main__':main()
