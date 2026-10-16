"""E3 legal fallen pose/contact admission; default PD, no recovery or PPO."""
from pathlib import Path
import os,sys,json,time,runpy,hashlib,traceback
B=Path(__file__).resolve().parent;J=B/'job1';OUT=B/'output'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def main():
 OUT.mkdir();task=json.loads((J/'TASK.json').read_bytes());source=J/'source/E0_full_source.pt';assert H(source)==task['source_SHA']
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 old=json.loads((J/'original_run_manifest.json').read_bytes())['env'];os.environ.update({k:str(v) for k,v in old.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')});os.environ.update(RM_MOD4_USD=str(J/'assets/robot.usd'),RM_JUMP_SCRIPT_PROB='0',RM_MOD4_MAP='',RM_MOD4_TERRAIN='flat',OWN_E2_H1_KIND='E3_LEGAL_FALLEN_RESET_ADMISSION',RM_RESCUE_STOP_FILE=str(OUT/'STOP_AFTER_SAVE.json'))
 sys.path[:0]=[str(B),str(B/'lib'),str(J/'runtime/isaac/mod4')];entry=J/'runtime/isaac/mod4/train_E2_H1_fresh_v1.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','80','--seed','20260928','--steps_per_env','24','--learning_rate','.0001','--init_checkpoint',str(source),'--log_root',str(OUT/'logs'),'--run_name','E3_legal_pose_contact_not_PPO','--additional_iterations','1'];ns=runpy.run_path(str(entry),run_name='own_E3_pose_contact_config')
 import torch,numpy as np,warp as wp,rescue_training
 from spring_pressure_checkpoint import exact
 from h1_authored_full_collider_plane_reference_v1 import extract,evaluate
 def tensor(v):return v.torch if hasattr(v,'torch') else v if torch.is_tensor(v) else wp.to_torch(v)
 def mul(a,b):return torch.cat((a[...,-1:]*b[...,:3]+b[...,-1:]*a[...,:3]+torch.cross(a[...,:3],b[...,:3],dim=-1),a[...,-1:]*b[...,-1:]-(a[...,:3]*b[...,:3]).sum(-1,keepdim=True)),-1)
 def admission(runner,n,log_dir):
  env=runner.env.unwrapped;vec=runner.env;runner.logger.writer=None;robot=env.scene['robot'];s=torch.load(source,map_location='cpu',weights_only=False)
  for key,v in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(v,s[key])
  term=env.command_manager.get_term('twist');term.set_manual_evaluation_mode();term.vel_command_b.zero_();env._mod4_mode_bit=torch.zeros((80,),device=env.device,dtype=torch.long)
  body_names=list(robot.body_names);sensor=env.scene.sensors['full_robot_contact'];contact_names=list(sensor.body_names);assert set(body_names)==set(contact_names) and len(body_names)==31
  shapes=extract(env.sim.stage,'/World/envs/env_0/Robot',body_names);assert len(shapes)==34;wheel=[contact_names.index(x) for x in ('left_wheel','right_wheel')];assert callable(robot.write_root_pose_to_sim) and callable(robot.write_root_velocity_to_sim)
  put(OUT/'ACTUAL_AUTHORED_COLLIDER_REFERENCE.json',dict(epoch=time.time(),shapes=shapes,body_names=body_names,contact_body_names=contact_names,source_USD_SHA=H(J/'assets/robot.usd'),quaternion_convention='XYZW',not_cookedShapeLocal_or_hardware_calibration=True))
  rows=[];chunks=[];poses=[];stage='before';maxforce=0.;original=env.scene.update
  def persist():
   if rows:
    p=OUT/('physics_'+str(len(chunks))+'.npz');np.savez_compressed(p,**{k:np.stack([x[k] for x in rows]) for k in rows[0]});chunks.append(dict(path=str(p),bytes=p.stat().st_size,SHA=H(p),rows=len(rows)));rows.clear()
   put(OUT/'VALID_PREFIX_INDEX_ACTUAL.json',dict(epoch=time.time(),physics=chunks,pose_controls=poses,no_PPO_or_teacher_trajectory=True))
  def physical(dt):
   nonlocal maxforce
   original(dt);root=tensor(robot.data.root_state_w);pos=tensor(robot.data.body_pos_w);quat=tensor(robot.data.body_quat_w);clear=evaluate(pos,quat,shapes);force=tensor(sensor.contact_view.get_net_contact_forces(dt=float(dt))).reshape(80,31,3);wf=tensor(env._integrated_contact.sensor.contact_view.get_net_contact_forces(dt=float(dt))).reshape(80,2,3);maxforce=max(maxforce,float((force[:,wheel]-wf).abs().max()));assert maxforce<=.1
   assert all(torch.isfinite(x).all() for x in (root,pos,quat,clear,force,wf))
   rows.append(dict(tick=np.asarray(env._integrated_contact.tick),phase=np.asarray(stage),root13=root.cpu().numpy().copy(),q30=tensor(robot.data.joint_pos).cpu().numpy().copy(),body_pos31_w=pos.cpu().numpy().copy(),body_quat31_xyzw=quat.cpu().numpy().copy(),all_shape_clearance=clear.cpu().numpy().copy(),all_body_contact_force=force.cpu().numpy().copy(),wheel_raw_force=wf.cpu().numpy().copy(),episode=env._sensor_mild.episode.clone().cpu().numpy()))
  env.scene.update=physical;runner.alg.actor.eval();runner.alg.critic.eval();runner.save(str(OUT/'source_fresh80_before.pt'))
  try:
   with torch.inference_mode():
    for axis in (0,1):
     for degrees in (-90,-60,-30,30,60,90):
      stage='legal_original_reset';vec.reset();term.vel_command_b.zero_();env._mod4_mode_bit.zero_();root=tensor(robot.data.root_state_w).clone();pos=tensor(robot.data.body_pos_w).clone();quat=tensor(robot.data.body_quat_w).clone();q30=tensor(robot.data.joint_pos).clone();angle=degrees*torch.pi/180;delta=torch.zeros((80,4),device=env.device);delta[:,axis]=float(np.sin(angle/2));delta[:,3]=float(np.cos(angle/2));rel=pos-root[:,None,:3];a=delta[:,None,:3].expand_as(rel);rot=rel+2*torch.cross(a,torch.cross(a,rel,dim=-1)+delta[:,None,3:4]*rel,dim=-1);newpos=root[:,None,:3]+rot;newquat=mul(delta[:,None,:].expand_as(quat),quat);shift=.0001-evaluate(newpos,newquat,shapes).amin(-1);pose=torch.cat((root[:,:3],mul(delta,root[:,3:7])),-1);pose[:,2]+=shift
      # Supported public root setters; original legal joint reset is preserved.
      robot.write_root_pose_to_sim(pose);robot.write_root_velocity_to_sim(torch.zeros((80,6),device=env.device));rb=tensor(robot.data.root_state_w).clone();position_error=float((rb[:,:3]-pose[:,:3]).abs().max());quat_error=float(torch.minimum((rb[:,3:7]-pose[:,3:7]).abs().amax(-1),(rb[:,3:7]+pose[:,3:7]).abs().amax(-1)).max());assert position_error<=1e-6 and quat_error<=1e-6 and torch.equal(q30,tensor(robot.data.joint_pos))
      stage='fallen_control';starttick=env._integrated_contact.tick;obs,reward,done,extra=vec.step(torch.zeros((80,6),device=env.device));callbacks=env._integrated_contact.tick-starttick;assert callbacks==4;poses.append(dict(axis=axis,degrees=degrees,root_pose_readback_position_maxabs=position_error,root_pose_readback_quaternion_sign_equivalent_maxabs=quat_error,joints_unchanged_before_step=True,authored_initial_margin_m=.0001,actual_control_callbacks=callbacks,ordinary_done_count=int(done.sum()),default_PD_not_zero_torque=True));persist()
  finally:persist();env.scene.update=original;runner.save(str(OUT/'source_fresh80_after.pt'))
  for key,v in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(v,s[key])
  assert len(poses)==12;put(OUT/'COMPLETE_ACTUAL.json',dict(epoch=time.time(),source_SHA=H(source),num_envs=80,pose_groups=12,control_callbacks=sum(x['actual_control_callbacks'] for x in poses),all_callback_rows_including_reset=sum(x['rows'] for x in chunks),fullsensor_wheel_max_component_error_N=maxforce,physics=chunks,poses=poses,actor9critic8STD17Adam_unchanged=True,optimizer_updates=0,original_termination_reward_and_hardware_not_changed=True,no_recovery_or_selfrescue_success_or_full20k_restore_or_PPO_claim=True,contact_reset_admission_only=True))
 rescue_training.learn=admission
 try:ns['main']()
 except BaseException:put(OUT/'ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
 finally:put(OUT/'APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()
if __name__=='__main__':
 try:main()
 except BaseException:
  OUT.mkdir(exist_ok=True);put(OUT/'ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_or_PPO=True));raise
