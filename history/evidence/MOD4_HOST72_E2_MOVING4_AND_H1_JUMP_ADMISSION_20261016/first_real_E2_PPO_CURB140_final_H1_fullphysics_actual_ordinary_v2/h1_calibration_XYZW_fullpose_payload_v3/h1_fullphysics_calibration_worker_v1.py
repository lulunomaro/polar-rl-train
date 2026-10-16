"""No-learning motor-action calibration; never an actor/PPO/teacher training trajectory."""
from pathlib import Path
import os,sys,json,time,runpy,hashlib,traceback
OWN=Path(__file__).resolve().parent;B=OWN;J=B/'job1';OUT=OWN/'output'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def main():
 OUT.mkdir();task=json.loads((J/'TASK.json').read_bytes());source=J/'source/E0_full_source.pt';assert H(source)==task['source_SHA']
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 env=json.loads((J/'original_run_manifest.json').read_bytes())['env'];os.environ.update({k:str(v) for k,v in env.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')});os.environ.update(RM_MOD4_USD=str(J/'assets/robot.usd'),RM_JUMP_SCRIPT_PROB='0',RM_MOD4_MAP='',RM_MOD4_TERRAIN='flat',OWN_E2_H1_KIND=task['kind'],RM_RESCUE_STOP_FILE=str(OUT/'STOP_AFTER_SAVE.json'))
 sys.path[:0]=[str(OWN),str(B/'lib'),str(J/'runtime/isaac/mod4')];entry=J/'runtime/isaac/mod4/train_E2_H1_fresh_v1.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','80','--seed','20260928','--steps_per_env','24','--learning_rate','.0001','--init_checkpoint',str(source),'--log_root',str(OUT/'logs'),'--run_name','H1_explicit_motor_calibration_not_PPO','--additional_iterations','1'];ns=runpy.run_path(str(entry),run_name='own_H1_nonlearning_config')
 import torch,numpy as np,warp as wp,rescue_training
 from spring_pressure_checkpoint import exact
 from h1_authored_full_collider_plane_reference_v1 import extract,evaluate
 def tensor(v):return v.torch if hasattr(v,'torch') else v if torch.is_tensor(v) else wp.to_torch(v)
 def calibration(runner,n,log_dir):
  env=runner.env.unwrapped;vec=runner.env;runner.logger.writer=None;s=torch.load(source,map_location='cpu',weights_only=False)
  for key,v in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(v,s[key])
  assert float(os.environ['RM_JUMP_SCRIPT_PROB'])==0
  term=env.command_manager.get_term('twist');term.set_manual_evaluation_mode();term.vel_command_b.zero_();env._mod4_mode_bit=torch.full((80,),4,device=env.device,dtype=torch.long)
  body_names=list(env.scene['robot'].body_names);sensor=env.scene.sensors['full_robot_contact'];contact_names=list(sensor.body_names);assert set(body_names)==set(contact_names) and len(contact_names)==31
  shapes=extract(env.sim.stage,'/World/envs/env_0/Robot',body_names);assert len(shapes)==34;wheelshape=[[i for i,s in enumerate(shapes) if s['body']==name] for name in ('left_wheel','right_wheel')];assert all(wheelshape)
  contactwheel=[contact_names.index(x) for x in ('left_wheel','right_wheel')];nonwheel=[i for i,n in enumerate(contact_names) if n not in ('left_wheel','right_wheel')]
  put(OUT/'ACTUAL_AUTHORED_ALL_COLLIDER_REFERENCE.json',dict(epoch=time.time(),shapes=shapes,body_names=body_names,actual_contact_view_body_names=contact_names,source_USD_SHA=H(J/'assets/robot.usd'),authored_geometry_not_cookedShapeLocal_directread=True,actual_physical_link_pose_and_allbody_contact_alignment_required=True))
  prefix=[];chunks=[];controls=[];control_chunks=[];tick=env._integrated_contact.tick;original=env.scene.update;maxforce=0.
  def persist():
   if prefix:
    q=OUT/('physics_'+str(len(chunks))+'.npz');np.savez_compressed(q,**{k:np.stack([z[k] for z in prefix]) for k in prefix[0]});chunks.append(dict(path=str(q),bytes=q.stat().st_size,SHA=H(q),rows=len(prefix)));prefix.clear()
   if controls:
    q=OUT/('controls_'+str(len(control_chunks))+'.npz');np.savez_compressed(q,**{k:np.stack([z[k] for z in controls]) for k in controls[0]});control_chunks.append(dict(path=str(q),bytes=q.stat().st_size,SHA=H(q),rows=len(controls)));controls.clear()
   put(OUT/'VALID_PREFIX_INDEX_ACTUAL.json',dict(epoch=time.time(),physics=chunks,controls=control_chunks,explicit_scripted_motor_calibration_not_actor_or_PPO=True,not_used_for_policy_gradient_or_training_replay=True))
  def physical(dt):
   nonlocal maxforce
   original(dt);robot=env.scene['robot'];root=tensor(robot.data.root_state_w);pos=tensor(robot.data.body_pos_w);quat=tensor(robot.data.body_quat_w);clear=evaluate(pos,quat,shapes);f=tensor(sensor.contact_view.get_net_contact_forces(dt=float(dt))).reshape(80,31,3);raw=env._integrated_contact.sensor.contact_view.get_net_contact_forces(dt=float(dt));raw=tensor(raw).reshape(80,2,3);difference=(f[:,contactwheel]-raw).abs().amax();maxforce=max(maxforce,float(difference));assert maxforce<=.1
   q=root[:,3:7];x,y,z,w=q.unbind(-1);roll=torch.atan2(2*(w*x+y*z),1-2*(x*x+y*y));pitch=torch.asin((2*(w*y-z*x)).clamp(-1,1));yaw=torch.atan2(2*(w*z+x*y),1-2*(y*y+z*z));wheelclear=torch.stack([clear[:,ids].amin(1) for ids in wheelshape],-1)
   prefix.append(dict(tick=np.asarray(env._integrated_contact.tick),root13=root.cpu().numpy().copy(),q30=tensor(robot.data.joint_pos).cpu().numpy().copy(),body_pos31_w=pos.cpu().numpy().copy(),body_quat31_xyzw=quat.cpu().numpy().copy(),all_shape_clearance=clear.cpu().numpy().copy(),wheel_clearance=wheelclear.cpu().numpy().copy(),all_body_contact_force=f.cpu().numpy().copy(),wheel_raw_force=raw.cpu().numpy().copy(),wheel_5ms_mean_force=env._integrated_contact.history[:,0].clone().cpu().numpy(),roll=roll.cpu().numpy(),pitch=pitch.cpu().numpy(),yaw=yaw.cpu().numpy(),episode=env._sensor_mild.episode.clone().cpu().numpy()))
  env.scene.update=physical;runner.alg.actor.eval();runner.alg.critic.eval();before=OUT/'source_model_fresh80_before.pt';runner.save(str(before));groups=torch.arange(80,device=env.device)%4
  try:
   with torch.inference_mode():
    for i in range(224):
     # These caller-defined calibration inputs never enter PPO or a sampled-action log_prob.
     act=torch.zeros((80,6),device=env.device);k=max(0,i-24)%83;amplitude=torch.where(groups==1,.3,torch.where(groups==2,.6,torch.where(groups==3,-.6,0.)))
     if i>=24 and k<40:act[:,:4]=amplitude[:,None]
     elif i>=24 and k<43:act[:,:4]=-amplitude[:,None]
     obs,reward,done,extra=vec.step(act);controls.append(dict(requested6=act.cpu().numpy(),done=done.cpu().numpy(),original_reward=reward.cpu().numpy(),policy35=obs['policy'].cpu().numpy()))
     if i%24==23:persist();assert not (Path(log_dir)/'STOP_AFTER_SAVE').exists()
  finally:persist();env.scene.update=original;runner.save(str(OUT/'source_model_fresh80_after.pt'))
  assert env._integrated_contact.tick-tick==896 and sum(x['rows'] for x in chunks)==896
  for key,v in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(v,s[key])
  put(OUT/'COMPLETE_ACTUAL.json',dict(epoch=time.time(),source_SHA=H(source),num_envs=80,controls=224,callbacks=896,all_shapes=len(shapes),contact_bodies=31,fullsensor_wheel_sensor_max_component_error_N=maxforce,physics=chunks,controls_raw=control_chunks,source9critic8STD17Adam_unchanged=True,optimizer_updates=0,fresh80_perenv_DR_not_full20k_restore=True,scripted_motor_calibration_only=True,not_actor_jump_performance_or_learning=True,no_training_replay_or_teacher_or_upward_force=True,actual_authored_reference_not_cookedShapeLocal=True,actual_callback_data_present_not_airborne_success_assumed=True))
 rescue_training.learn=calibration
 try:ns['main']()
 except BaseException:put(OUT/'ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry=True));raise
 finally:put(OUT/'APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()
if __name__=='__main__':
 try:main()
 except BaseException:
  OUT.mkdir(exist_ok=True);put(OUT/'ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_PPO_or_budget=True));raise
