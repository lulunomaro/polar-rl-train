"""Frozen stair motion replay: physical-substep forces, actions and kinematics, no optimizer."""
from pathlib import Path
import sys,json,hashlib,time,importlib.util,types,shutil,traceback,os
import numpy as np,torch,mujoco
T=Path(__file__).resolve().parent;R=T.parents[2];D=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112';E=T/'evidence'
CKPT=R/'sources/local/MOD4V3_FLAT_SPEED_REPAIR_20261112/weights/selected_flat_speed_candidate.pt'
EXPECTED='979e355a563b3057d7509e9e5ef33e7a364906bd80bd16789ad80df654efa64d'
assert hashlib.sha256(CKPT.read_bytes()).hexdigest()==EXPECTED
spec=importlib.util.spec_from_file_location('motion_stair_source',D/'viewer/showcase.py');show=importlib.util.module_from_spec(spec);spec.loader.exec_module(show)
show.CKPT=CKPT;show.EXPECTED=EXPECTED;torch.set_num_threads(1)
import play_mod4v3 as plant
CASE_SPECS=[('raised365_fast',.365,2.2),('raised400_fast',.4,2.2),('raised365_slow',.365,1.),('low280_fast',.28,2.2)]

def run(case,height,speed):
 out=E/case;out.mkdir(exist_ok=False)
 B=out/'scene_assets';(B/'tiles').mkdir(parents=True);shutil.copy2(D/'viewer/tiles/r00_c00.npz',B/'tiles/r00_c00.npz');show.B=B
 s=show.Replay(direction='up');s.args.vx=speed;e=s.env;m=e.m;d=e.d
 assert int(m.opt.integrator)==int(mujoco.mjtIntegrator.mjINT_IMPLICITFAST)
 shutil.copy2(Path(s.args.xml),out/'scene.xml')
 wheel_names=['left_wheel_link','right_wheel_link'];wb=[m.body(n).id for n in wheel_names]
 terrain={i for i in range(m.ngeom) if m.geom(i).name=='ground' or m.geom(i).name.startswith('step_')}
 ids=np.asarray(e.spec.act_idx);qa=e.qadr_all[ids];va=e.dadr_all[ids]
 leg_joints=[[e.joint_ids['left_front1_joint'],e.joint_ids['left_rear1_joint']],[e.joint_ids['right_front1_joint'],e.joint_ids['right_rear1_joint']]]
 record={k:[] for k in ['time','qpos','qvel','action_env','ctrl_env','actuator_force_env','joint_torque_env','joint_power_env','root_pose','root_vel_world','root_noseup_deg','com_world','wheel_pos_world','wheel_vel_world','leg_length','leg_angle_deg','wheel_offset_body','wheel_force_world','wheel_normal_force','wheel_riser_force','wheel_tread_force','all_terrain_force_world','base_contact_force','other_contact_force','height_command','velocity_command','closure']}
 policy={'time':[],'observation':[],'action_ppo':[]}
 handle=s.actor.register_forward_hook(lambda mod,inp,output:(policy['time'].append(float(d.time)),policy['observation'].append(inp[0].detach().cpu().numpy().reshape(-1)),policy['action_ppo'].append(output.detach().cpu().numpy().reshape(-1))) and None)
 contacts=(out/'contacts.jsonl').open('w',encoding='utf8')
 policy_rows=[];first_success=None;started=time.time();stop='duration';max_closure=0.
 def physics(env,act):
  nonlocal max_closure
  act=act.clamp(-env.action_clip,env.action_clip)
  for j in range(env.decim):
   if j%4==0 or j%1==0:
    tau=env._torque(act).detach().numpy().reshape(-1)
    if j%4==0:d.ctrl[env.act_ids[:4]]=tau[:4]
    d.ctrl[env.act_ids[4:]]=tau[4:]
   # implicitfast forward fields after mj_step belong to this cached pre-integration state.
   t=float(d.time);q=d.qpos.copy();v=d.qvel.copy();control=d.ctrl[env.act_ids].copy()
   mujoco.mj_step(m,d)
   if not np.isfinite(d.qpos).all() or not np.isfinite(d.qvel).all():raise show.SafetyStop('nonfinite')
   cl=max(float(np.linalg.norm(d.site_xpos[a]-d.site_xpos[b])) for a,b in s.pairs);s.closure=cl;max_closure=max(max_closure,cl)
   if cl>.002:raise show.SafetyStop('closure>2mm')
   Rb=d.xmat[env.base_id].reshape(3,3);bp=d.xpos[env.base_id].copy();wp=d.xpos[wb].copy();wv=[];length=[];angle=[];offset=[]
   for side,bid in enumerate(wb):
    vel=np.zeros(6);mujoco.mj_objectVelocity(m,d,mujoco.mjtObj.mjOBJ_BODY,bid,vel,0);wv.append(vel[3:].copy())
    anchor=d.xanchor[leg_joints[side]].mean(0);vec=Rb.T@(wp[side]-anchor);length.append(float(np.linalg.norm(vec)));angle.append(float(np.degrees(np.arctan2(vec[0],-vec[2]))));offset.append(Rb.T@(wp[side]-bp))
   wf=np.zeros((2,3));wn=np.zeros(2);wr=np.zeros(2);wt=np.zeros(2);total=np.zeros(3);base=np.zeros(3);other=np.zeros(3);cc=[]
   for ci in range(d.ncon):
    c=d.contact[ci];g1,g2=int(c.geom1),int(c.geom2)
    if (g1 in terrain)==(g2 in terrain):continue
    terrain_first=g1 in terrain;tg=g1 if terrain_first else g2;rg=g2 if terrain_first else g1;body=int(m.geom_bodyid[rg])
    cf=np.zeros(6);mujoco.mj_contactForce(m,d,ci,cf)
    if cf[0]<=1e-8:continue
    frame=np.asarray(c.frame).reshape(3,3);force=frame.T@cf[:3]*(1 if terrain_first else -1);normal=frame[0]*(1 if terrain_first else -1)
    total+=force
    if body in wb:
     side=wb.index(body);wf[side]+=force;wn[side]+=cf[0]
     if abs(normal[0])>.7 and abs(normal[2])<.35:wr[side]+=cf[0]
     if normal[2]>.7:wt[side]+=cf[0]
    elif body==env.base_id:base+=force
    else:other+=force
    cc.append(dict(terrain=m.geom(tg).name,robot_geom=m.geom(rg).name,body=m.body(body).name,position=c.pos.tolist(),normal_on_robot=normal.tolist(),force_on_robot=force.tolist(),normal_force=float(cf[0]),distance=float(c.dist)))
   if cc:contacts.write(json.dumps(dict(t=t,contacts=cc),separators=(',',':'))+'\n')
   jt=d.qfrc_actuator[va].copy();rv={
    'time':t,'qpos':q,'qvel':v,'action_env':act.detach().numpy().reshape(-1).copy(),'ctrl_env':control,'actuator_force_env':d.actuator_force[env.act_ids].copy(),'joint_torque_env':jt,'joint_power_env':jt*v[va],
    'root_pose':q[:7],'root_vel_world':v[:3],'root_noseup_deg':np.degrees(np.arctan2(Rb[2,0],np.hypot(Rb[0,0],Rb[1,0]))),'com_world':d.subtree_com[env.base_id].copy(),
    'wheel_pos_world':wp,'wheel_vel_world':wv,'leg_length':length,'leg_angle_deg':angle,'wheel_offset_body':offset,'wheel_force_world':wf,'wheel_normal_force':wn,'wheel_riser_force':wr,'wheel_tread_force':wt,
    'all_terrain_force_world':total,'base_contact_force':base,'other_contact_force':other,'height_command':s.height,'velocity_command':s.cmd_vx,'closure':cl}
   for key,val in rv.items():record[key].append(val)
  env.a_prev=act.detach().to(env.device);return env.state()
 e.step=types.MethodType(physics,e)
 try:
  for k in range(600):
   s.set_height(.28+(height-.28)*min(k/100.,1.));s.step({'w'} if k>=150 else set())
   x,y=map(float,d.qpos[:2]);ground=s.ground(x,y)
   row=dict(t=k*.02,x=x,y=y,ground=ground,relative_height=float(s.z),vx=float(e.vx),command_height=s.height,closure=s.closure,resets=s.reset_count-1,reason=s.reason)
   policy_rows.append(row)
   success=bool(s.reset_count==1 and s.cos_tilt>.766 and s.z>.18 and x>-.9 and ground>.30)
   if success and first_success is None:first_success=k*.02
   if first_success is not None and k*.02-first_success>=.36:stop='success_plus_0.36s';break
   if s.reset_count>1:stop='original_reset';break
 finally:
  handle.remove();contacts.close();s.close()
 arrays={k:np.asarray(v) for k,v in record.items()};arrays.update({f'policy_{k}':np.asarray(v) for k,v in policy.items()});np.savez_compressed(out/'trajectory.npz',**arrays)
 summary=dict(case=case,height=height,speed=speed,model=str(CKPT),model_sha256=EXPECTED,success=first_success is not None,first_success_time=first_success,stop=stop,resets=s.reset_count-1,reset_reason=s.reason,max_closure_m=max_closure,physical_samples=len(record['time']),policy_samples=len(policy['time']),wall_seconds=time.time()-started,scene=str(Path(s.args.xml)),scene_sha256=hashlib.sha256(Path(s.args.xml).read_bytes()).hexdigest(),mass_kg=float(m.body_subtreemass[e.base_id]),integrator=int(m.opt.integrator),actuator_names=[e.spec.joint_names[i] for i in ids],actuator_dof_adr=va.tolist(),joint_names=e.spec.joint_names,qpos_adr=e.qadr_all.tolist(),qvel_adr=e.dadr_all.tolist(),wheel_body_names=wheel_names,hip_reference='Midpoint of left/right front1 and rear1 actuated joint anchors; effective leg length is wheel-center distance to this reference, not individual rod length',timing='All substep state/kinematics/contact/force rows are aligned to pre-integration t; post-mj_step derived fields from implicitfast belong to cached pre-step q/v. Original control update/state-return calls unchanged.',physics_dt=.0025,leg_feedback_dt=.01,wheel_feedback_dt=.0025,policy_dt=.02,nominal_only=True,training=False)
 (out/'RESULT.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8');(out/'policy_trace.json').write_text(json.dumps(policy_rows,indent=2)+'\n',encoding='utf8')
 print(json.dumps(summary),flush=True)
 return summary

if __name__=='__main__':
 try:
  results=[run(*case) for case in CASE_SPECS]
  (E/'REPLAY_COMPLETE.json').write_text(json.dumps(dict(cases=results,python=sys.version,torch=torch.__version__,mujoco=mujoco.__version__,numpy=np.__version__,no_optimizer=True),indent=2)+'\n',encoding='utf8')
 except Exception:
  (E/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf8');raise
