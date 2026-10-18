"""Source-exact full20k native only; actual public request and executable reward audit."""
from pathlib import Path
import os,sys,json,time,hashlib,traceback,runpy
B=Path(__file__).resolve().parent;J=B/'job0';OUT=J/'native'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 p=Path(p);tmp=p.with_suffix(p.suffix+'.partial');tmp.write_text(json.dumps(v,indent=2));tmp.replace(p)
def main():
 OUT.mkdir();task=json.loads((J/'TASK.json').read_bytes());src=J/'source/H1_fe778_closed71.pt';assert H(src)==task['source_SHA']
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 old=json.loads((J/'original_run_manifest.json').read_bytes())['env'];os.environ.update({k:str(v) for k,v in old.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')});os.environ.update(RM_MOD4_USD=str(J/'assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0',RM_RESCUE_STOP_FILE=str(OUT/'STOP_AFTER_SAVE.json'),OWN_E2_H1_KIND=task['kind'])
 sys.path[:0]=[str(B/'lib'),str(J/'runtime/isaac/mod4')];entry=J/'runtime/isaac/mod4/train_H1_ground_prelaunch_fullstate_v2.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed','20260928','--steps_per_env','24','--learning_rate','.0001','--init_checkpoint',str(src),'--log_root',str(OUT/'logs'),'--run_name','H1_full20k_public_request_reward_NATIVE_ONLY','--additional_iterations','1'];ns=runpy.run_path(str(entry),run_name='owned_H1_native_config')
 import torch,numpy as np,rescue_training
 from spring_pressure_checkpoint import exact
 from h1_fullstate_checkpoint_v1 import state
 from h1_takeoff_progress_phase_v2 import H1TakeoffProgressPhaseV2 as H1PublicRequestPhase
 from h1_reward_scope_v1 import isolated_actual_SDK_dt_probe
 from h1_takeoff_progress_environment_v2 import tensor
 def save(runner,path):
  tmp=path.with_suffix('.pt.partial');runner.save(str(tmp));v=torch.load(tmp,map_location='cpu',weights_only=False);v['owned_H1_admission_task']=task;v['native_only_no_PPO']=True;torch.save(v,tmp);tmp.replace(path);return dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))
 def native(runner,n,log_dir):
  env=runner.env.unwrapped;vec=runner.env;runner.logger.writer=None;s=torch.load(src,map_location='cpu',weights_only=False)
  for k,v in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(v,s[k]),k
  assert env.num_envs==20000 and int(env._sim_step_counter)==0;startup=list(Path(log_dir).glob('*STARTUP_VERIFIED.json'));assert len(startup)>=7 and (Path(log_dir)/'H1_PHASE_FULLSTATE_RESUME_STARTUP_VERIFIED.json').exists()
  assert tuple(env.cfg.sim.gravity)==(0.,0.,-9.81) and any(x['source_phase_version']==2 for x in env.h1_phase.source_migration_history);sdk=isolated_actual_SDK_dt_probe(env);before=save(runner,OUT/'own_source_full20k_startup0.pt');put(OUT/'SOURCE_FULL20K_TYPED_ZERO_CLOCK_REWARD_SDK_ACTUAL.json',dict(epoch=time.time(),source_SHA=H(src),sourceactor9_critic8_STD17Adam_exact=True,actual_zero_clock=True,startup_receipts=[dict(path=str(p),value=json.loads(p.read_bytes())) for p in startup],SDK_reward_dt=sdk,H1_phase_new_explicit_not_old_source_claim=True,source_V2_saved_phase_migration=env.h1_phase.source_migration_history,actual_gravity=tuple(env.cfg.sim.gravity),own0=before))
  from pxr import Usd,UsdGeom,UsdPhysics
  plane=[];root=env.sim.stage.GetPrimAtPath('/World/ground');cache=UsdGeom.XformCache()
  for prim in Usd.PrimRange(root):
   if prim.HasAPI(UsdPhysics.CollisionAPI) and UsdPhysics.CollisionAPI(prim).GetCollisionEnabledAttr().Get() and prim.GetTypeName()=='Plane':
    axis={'X':0,'Y':1,'Z':2}[str(UsdGeom.Plane(prim).GetAxisAttr().Get())];matrix=np.asarray(cache.GetLocalToWorldTransform(prim),dtype=np.float64).T;normal=np.linalg.inv(matrix[:3,:3]).T@np.eye(3)[axis];normal/=np.linalg.norm(normal);plane.append(dict(path=str(prim.GetPath()),axis=axis,world_origin=matrix[:3,3].tolist(),world_normal=normal.tolist(),actual_type='Plane',source_layer=prim.GetStage().GetRootLayer().identifier))
  assert len(plane)==1 and abs(plane[0]['world_normal'][2])>.999999 and abs(plane[0]['world_origin'][2])<=1e-6
  geometry=dict(shapes=env.h1_shapes,body_names=env.h1_body_names,contact_body_names=env.h1_contact_names,witness_ids=env.h1_witness_ids.cpu().tolist(),plane=plane,actual_SDK_quaternion='XYZW',authored_geometry_reference_not_cooked_ShapeLocal_or_manifold=True);put(OUT/'ACTUAL_ALL34_COLLIDER_PLANE_AND_31_CONTACT_REFERENCE.json',geometry)
  controls=[];physics=[];control_rows=[];physical_rows=[];runner.alg.actor.eval();runner.alg.critic.eval();obs=vec.get_observations();tick=env._integrated_contact.tick;begun=time.monotonic();env.h1_capture=True
  def persist():
   for values,index,prefix in ((control_rows,controls,'controls'),(physical_rows,physics,'physics')):
    if not values:continue
    p=OUT/(prefix+'_'+str(len(index))+'.npz');assert not p.exists();np.savez_compressed(p,**{k:np.stack([x[k] for x in values]) for k in values[0]});index.append(dict(path=str(p),bytes=p.stat().st_size,SHA=H(p),rows=len(values)));values.clear()
   put(OUT/'ALL_VALID_NATIVE_PREFIX_INDEX.json',dict(epoch=time.time(),controls=controls,physics=physics,all_valid_failed_prefixes_retained=True))
  try:
   with torch.inference_mode():
    for i in range(task['controls']):
     x=obs['policy'];assert x.shape==(20000,35) and obs['critic'].shape==(20000,38);expected_mode=torch.nn.functional.one_hot(env.h1_phase.public_mode(),7).to(x.dtype);assert torch.equal(x[:,28:35],expected_mode),'Published external mode must reach actor before action';age=env.h1_phase.age_control.clone();before_x=x.cpu().numpy().copy();critic=obs['critic'].cpu().numpy().copy();a=runner.alg.actor(obs,stochastic_output=False);raw=a.cpu().numpy().copy();env.h1_physical_rows=[];obs,reward,done,info=vec.step(a);f=env.h1_control_frame;assert len(env.h1_physical_rows)==4
     row={k:v.cpu().numpy().copy() for k,v in f.items()};row.update(policy35=before_x,critic38=critic,raw6=raw,public_age_control=age.cpu().numpy().copy(),command=env.command_manager.get_term('twist').command.cpu().numpy().copy(),done=done.cpu().numpy().copy(),total_reward=reward.cpu().numpy().copy(),physical_wheel_force=np.stack([v['wheel_raw'].cpu().numpy() for v in env.h1_physical_rows]));control_rows.append(row)
     for rowp in env.h1_physical_rows:physical_rows.append({k:v.cpu().numpy().copy() for k,v in rowp.items()})
     env.h1_physical_rows=[]
     if i==149:
      actual=state(env);p=OUT/'H1_PHASE_MID_NATIVE_SHADOW_CUDA_ROUNDTRIP.pt';torch.save(actual,p);loaded=torch.load(p,map_location='cpu',weights_only=False);shadow=H1PublicRequestPhase(env.num_envs,env.device);shadow.load_state_dict(loaded['phase']);assert exact(shadow.state_dict(),actual['phase']);shadows=shadow.state_dict();ids=torch.tensor([1,3,5],device=env.device);shadow.reset(ids)
      keep=torch.ones(env.num_envs,dtype=torch.bool,device=env.device);keep[ids]=False
      for k,v in shadows['tensors'].items():assert torch.equal(shadow.tensors()[k][keep],v[keep]) and not shadow.tensors()[k][ids].any()
      put(OUT/'MID_NATIVE_PHASE_SHADOW_ROUNDTRIP_SELECTED_RESET_ACTUAL.json',dict(epoch=time.time(),actual_mid_phase_CUDA_diskroundtrip_exact=True,selectedreset_shadow_only_other19997rows_exact=True,live_environment_not_modified=True,no_startup_restore_in_stepped_process=True))
     if i%6==5:
      persist();put(OUT/'CURRENT_ACTUAL.json',dict(epoch=time.time(),controls=i+1,callbacks=env.h1_callback_count,optimizer_updates=0,current_public_modes=torch.bincount(env.h1_phase.public_mode(),minlength=7).cpu().tolist()));assert not (Path(log_dir)/'STOP_AFTER_SAVE').exists() and not (OUT/'STOP_AFTER_SAVE.json').exists();assert time.monotonic()-begun<900
  finally:
   persist();env.h1_capture=False;save(runner,OUT/'own_native_valid_prefix_full20k.pt')
  assert env.h1_callback_count==task['callbacks'] and env._integrated_contact.tick-tick==task['callbacks']
  for k,v in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(v,s[k]),k
  after=save(runner,OUT/'own_H1_ground_prelaunch_v2_native180.pt');put(OUT/'NATIVE180_PRELAUNCH_V2_COMPLETE_ACTUAL.json',dict(epoch=time.time(),controls=task['controls'],callbacks=task['callbacks'],num_envs=env.num_envs,source_SHA=H(src),sourceactor9_critic8_STD17Adam_unchanged=True,optimizer_updates=0,controls_raw=controls,physics_raw=physics,saved=after,initial=before,actual_sdk_reward_probe=sdk,force_view_maxabs_N=env.h1_force_error,original_chassis_PD_parameter_hardware_audit=env.chassis_pd_audit(),original_action_delay_audit=env._physics_action_delay.audit(),actual_full20k_original_source_restore=True,actual_all34_shape_31contact_saved=True,witness8_bodyposes_only_not_allrow_bodypose_replay=True,native_not_jump_skill_or_PPO_pass=True));put(OUT/'FINAL.json',dict(epoch=time.time(),native_only=True,passed_worker_not_independent_CPU=True,saved=after))
 rescue_training.learn=native
 try:ns['main']()
 except BaseException:put(OUT/'ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),error=traceback.format_exc(),native_only=True));raise
 finally:put(OUT/'APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()
if __name__=='__main__':
 try:main()
 except BaseException:
  OUT.mkdir(exist_ok=True);put(OUT/'ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay_or_PPO=True));raise
