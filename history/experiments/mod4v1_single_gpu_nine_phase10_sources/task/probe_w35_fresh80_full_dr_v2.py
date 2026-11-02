"""Fresh80 RM70/D0-D7 target integration using new MOD4v1 trainer build_env.
No checkpoint/model file, actor/critic/optimizer creation or policy learning.
"""
from pathlib import Path
import argparse,os,sys,json,runpy,time,traceback

def main():
 p=argparse.ArgumentParser();p.add_argument('--task',required=True,type=Path);a=p.parse_args();out=a.task.parent;task=json.loads(a.task.read_bytes());job=Path(task['runtime_job'])
 def put(n,v):
  with (out/n).open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
 assert os.environ['CUDA_VISIBLE_DEVICES']==task['GPU_UUID']
 original=json.loads((job/'original_run_manifest.json').read_bytes())['env']
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 os.environ.update({k:str(v) for k,v in original.items() if k not in ('RM_RESCUE_STOP_FILE','RM_RESCUE_DEADLINE')})
 os.environ.update(RM_MOD4_USD=str(job/'runtime/assets/robot.usd'),MOD4V1_ASSET_DIR=str(job/'runtime/assets'),MOD4_RESUME_QUEUE_CONTROL_US='20000',MOD4_RM70_ORIGINAL_ASSET_ROOT=str(job/'original_field'),MOD4_RM70_ASSET_RECEIPT=str(job/'RM70_BINARY_INSTALL_ACTUAL.json'),MOD4_RM70_NEW_LAYOUT_ROOT=str(out/'new_CAD_layout'),MOD4_NEW208_JOB_ROOT=str(job))
 storage=job/'kit_isolation';storage.mkdir();(storage/'data').mkdir();(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}');os.environ['MOD4_W35_OWN_KIT_STORAGE_ROOT']=str(storage)
 mod=job/'runtime/isaac/mod4';sys.path[:0]=[str(mod),str(job/'runtime')]
 entry=mod/'train_mod4v1_w35.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','80','--seed','20260928','--dry_run','24']
 ns=None;env=None
 try:
  ns=runpy.run_path(str(entry),run_name='new_mod4v1_fresh80_no_model')
  import torch
  from mild_dr import tensor
  from mod4v1_fresh_dr_guard import FreshDRNominalGuard
  from actual_DR_memory_getter272 import RuntimeOrderBinding,ActualDRMemoryGetter
  env=ns['build_env']();robot=env.scene['robot'];identity=ns['MOD4V1_IDENTITY'];guard=FreshDRNominalGuard(env,identity,torch_module=torch,tensor_converter=tensor)
  guard.assert_new_nominals_unchanged();env.reset();guard.assert_new_nominals_unchanged()
  audit=env._mild_dr.audit();assert audit['actual_parameters_pass']
  def selected_names(key):
   ids=robot.actuators[key].joint_indices
   if isinstance(ids,slice):ids=list(range(len(robot.joint_names)))[ids]
   elif hasattr(ids,'tolist'):ids=ids.tolist()
   return tuple(robot.joint_names[i] for i in ids)
  binding=RuntimeOrderBinding(tuple(robot.body_names),tuple(robot.joint_names),selected_names('legs'),selected_names('wheels'),selected_names('gas_springs'),int(env._mild_dr.materials.shape[1]))
  getter=ActualDRMemoryGetter(env,binding);getter.capture_initial()
  obs=env.observation_manager.compute();guard.check_observations(obs)
  assert env.num_envs==80 and env.physics_dt==.0025 and env.step_dt==.02 and env.cfg.decimation==8
  assert env.cfg.terminations.closure.params['threshold']==.01 and env.cfg.terminations.mimic.params['threshold']==.01
  initial_tick=int(env._integrated_contact.tick);initial_fb=int(env._feedback_100hz_tick);initial_calls=dict(env._physics_action_delay.calls)
  def small_tensor(x):
   x=x.detach();return {'shape':list(x.shape),'dtype':str(x.dtype),'finite':bool(torch.isfinite(x).all()),'min':float(x.min()),'max':float(x.max()),'first8':x.reshape(-1)[:8].cpu().tolist()}
  initial_memory={k:small_tensor(v) for k,v in getter.cache.items()};counts={k:small_tensor(v) for k,v in getter.counts.items()}
  put('FRESH80_FULLDR_BEFORE_CONTROL.json',{'passed':True,'scope':'fresh80 noPT; not20k source fullrestore or skill proof','asset_SHA':identity.usd_sha256,'contract_SHA':identity.contract_sha256,'audit':audit,'observations':{k:list(v.shape) for k,v in obs.items()},'actual_component_memory_not_independent_PhysX_qualification':initial_memory,'reset_counts':counts,'interface':[35,38,6],'mimic_rad':.01,'closure_m':.01,'model_opens':0,'actor_calls':0,'optimizer_updates':0})
  zeros=torch.zeros((80,6),device=env.device);finite=True
  for _ in range(24):
   obs,reward,terminated,truncated,extra=env.step(zeros);finite=finite and all(bool(torch.isfinite(v).all()) for v in (obs['policy'],obs['critic'],reward))
  assert finite and int(env._integrated_contact.tick)-initial_tick==192 and int(env._feedback_100hz_tick)-initial_fb==48
  assert {k:env._physics_action_delay.calls[k]-initial_calls[k] for k in ('legs','wheels')}=={'legs':192,'wheels':192}
  put('FRESH80_FULLDR_NATIVE24_COMPLETE.json',{'passed':True,'asset_SHA':identity.usd_sha256,'contract_SHA':identity.contract_sha256,'num_envs':80,'controls':24,'physics_callbacks':192,'feedback_samples':48,'finite_policy_critic_reward':True,'model_opens':0,'actor_calls':0,'optimizer_updates':0,'canonical_writes':0,'D6_scope':'original gas damping, not full joint friction','full20k_saved_state_restore':False,'expert_adaptation_or_skill_pass':False})
 except BaseException:
  put('FRESH80_ORIGINAL_ERROR.json',{'error':traceback.format_exc(),'model_opens':0,'optimizer_updates':0});raise
 finally:
  if env is not None:env.close();put('ENV_CLOSE_RETURNED.json',{'closed':True})
  if ns is not None:put('APP_CLOSING.json',{'calling_original_App_close':True});ns['app'].close()
if __name__=='__main__':main()
