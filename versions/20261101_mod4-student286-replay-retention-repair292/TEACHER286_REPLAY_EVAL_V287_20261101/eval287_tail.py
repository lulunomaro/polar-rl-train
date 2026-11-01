 from wheel_geometry220 import load_own_wheels
 import omni.usd
 stage=omni.usd.get_context().get_stage()
 rp=cfg.scene.robot.prim_path.replace('{ENV_REGEX_NS}','/World/envs/env_0').replace('env_.*','env_0')
 metadata,points=load_own_wheels(stage,rp)
 assert all(p is not None for p in points),metadata
 put('ACTUAL287_OWN_WHEEL_SUPPORT_GEOMETRY.json',dict(wheels=metadata,queries=2))
 raw=Path(TASK['model_path']).read_bytes()
 assert len(raw)==TASK['model_bytes'] and hashlib.sha256(raw).hexdigest()==TASK['model_SHA']
 ck=torch.load(io.BytesIO(raw),map_location=real.device,weights_only=False);del raw
 assert ck['kind']=='LQR_MPC_DEPTH_TEACHER_STUDENT286_COMPLETE' and ck['actual_new_Pi_updates']==2336
 weights={k.removeprefix('mlp.'):v for k,v in ck['student']['actor_state_dict'].items()if k.startswith('mlp.')}
 actor=torch.nn.Sequential(torch.nn.Linear(44,128),torch.nn.ELU(),torch.nn.Linear(128,64),torch.nn.ELU(),torch.nn.Linear(64,32),torch.nn.ELU(),torch.nn.Linear(32,6)).to(real.device)
 actor.load_state_dict(weights,strict=True);actor.eval()
 for parameter in actor.parameters():parameter.requires_grad_(False)
 del ck
 put('ACTUAL287_FINAL286_ACTOR_ONE_READ.json',dict(passed=True,SHA=TASK['model_SHA'],model_byte_reads=1,model_decodes=1,optimizer_constructs=0))
 cmd=real.command_manager.get_term('twist');ground_ids=torch.where(real._mixed209_flat)[0]
 ground_v=torch.tensor([0.,.3,-.3,0.,.3,-.3,0.,.3],device=real.device)
 old_update=cmd._update_command
 def cue():
  cmd.vel_command_b[ground_ids]=torch.stack((ground_v,torch.zeros_like(ground_v),torch.zeros_like(ground_v)),-1)
  sdk.task.height_cmd(real)[ground_ids,0]=.25
  for name in('is_standing_env','is_heading_env','is_pure_spin','is_moving_spin','is_transition_spin'):getattr(cmd,name)[ground_ids]=False
  cmd.signed_yaw[ground_ids]=0.;cmd.time_left[ground_ids]=20.
 def command_update():old_update();cue()
 cmd._update_command=command_update
 body_names=list(robot.body_names);wheel_ids=[body_names.index(n) for n in('left_wheel','right_wheel')]
 nonwheel=[i for i,n in enumerate(body_names)if n not in('left_wheel','right_wheel')]
 support=[torch.tensor(p,device=real.device)for p in points]
 origin=real.scene.env_origins.clone();target=real.target286.clone();ct,st=target[:,3].cos(),target[:,3].sin()
 def bounds():
  allpos=tensor(robot.data.body_pos_w);allq=tensor(robot.data.body_quat_w);lo=[];hi=[]
  for i,wid in enumerate(wheel_ids):
   q=allq[:,wid];x,y,z,w=q.unbind(-1)
   R=torch.stack((1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)),-1).reshape(80,3,3)
   v=torch.einsum('nij,pj->npi',R,support[i])+allpos[:,wid,None]-origin[:,None]
   delta=v[:,:,:2]-target[:,None,:2]
   local=torch.stack((ct[:,None]*delta[:,:,0]+st[:,None]*delta[:,:,1],-st[:,None]*delta[:,:,0]+ct[:,None]*delta[:,:,1],v[:,:,2]),-1)
   lo.append(local.amin(1));hi.append(local.amax(1))
  return torch.stack(lo,1),torch.stack(hi,1)
 def depth_features():
  camera.update(real.step_dt,force_recompute=True)
  image=tensor(camera.data.output['distance_to_image_plane']).detach().cpu().numpy().reshape(80,48,84)
  K=tensor(camera.data.intrinsic_matrices).detach().cpu().numpy();pos=tensor(camera.data.pos_w).detach().cpu().numpy()
  quat=tensor(camera.data.quat_w_ros).detach().cpu().numpy();root=tensor(robot.data.root_state_w).detach().cpu().numpy()
  feats=[]
  for j in range(80):
   x,y,z,w=root[j,3:7];yaw=np.arctan2(2*(w*z+x*y),1-2*(y*y+z*z));c,s=np.cos(yaw),np.sin(yaw)
   heading=np.array([[c,s,0.],[-s,c,0.],[0.,0.,1.]],dtype=np.float32)
   transform=np.eye(4,dtype=np.float32);transform[:3,:3]=heading@rotation(quat[j]);transform[:3,3]=heading@(pos[j]-[root[j,0],root[j,1],0.])
   feats.append(target_from_depth(image[j],K[j],transform,sensor_time=0.,control_time=0.,pixel_center_offset=.5)['features'])
  return torch.tensor(np.stack(feats),device=real.device)
 real.reset();cue();obs=vec.get_observations();active=torch.ones(80,dtype=torch.bool,device=real.device)
 flight=torch.zeros(80,dtype=torch.long,device=real.device);first_air=torch.zeros_like(flight);up=torch.zeros_like(active)
 cross=torch.zeros(80,2,dtype=torch.bool,device=real.device);land=torch.zeros_like(flight);stable=torch.zeros_like(flight);stable_peak=torch.zeros_like(flight)
 success=torch.zeros_like(active);cross_ever=torch.zeros_like(active);flight_ever=torch.zeros_like(active)
 counts=torch.zeros_like(flight);reward_sum=torch.zeros(80,device=real.device);vx_sum=torch.zeros_like(reward_sum);vx_mae=torch.zeros_like(reward_sum)
 overflow=torch.zeros(80,6,dtype=torch.long,device=real.device);depth_valid=torch.zeros_like(flight)
 low,high=bounds();previous=high[:,:,0].clone();tick0=int(real._integrated_contact.tick);fb0=int(real._feedback_100hz_tick)
 previous_air=torch.zeros_like(active);physics_counts=torch.zeros_like(flight);current_control=0;terminal_rows={};frames=[];captured={};phys_calls=0
 selected=[1,0,10,20];old_scene_update=real.scene.update
 def measure_physics(dt):
  global flight,first_air,up,cross,land,stable,stable_peak,success,cross_ever,flight_ever,previous,previous_air,phys_calls
  old_scene_update(dt)
  if abs(float(dt)-.0025)>1e-9:return
  phys_calls+=1;low,high=bounds();root=tensor(robot.data.root_state_w)
  f=tensor(real.contacts194.data.net_forces_w)[:,real.contact_order194];wf=f[:,wheel_ids];nw=torch.linalg.vector_norm(f[:,nonwheel],dim=-1).amax(-1)
  airborne=(torch.linalg.vector_norm(wf,dim=-1)<=1).all(-1)&(low[:,:,2]>.005).all(-1)&(nw<=1)&active
  first_air+=(airborne&~previous_air&active).long();first=first_air==1
  flight=torch.where(airborne,flight+1,torch.zeros_like(flight));up|=airborne&first&(root[:,9]>.05)
  crossing=(previous<0)&(high[:,:,0]>=0)&(low[:,:,2]>=.27)
  cross|=crossing&airborne[:,None]&first[:,None]
  crossed=cross.all(-1)&up&first;cross_ever|=crossed;flight_ever|=airborne
  inside=(low[:,:,0]>=0)&(high[:,:,0]<=3)&(low[:,:,1]>=-1)&(high[:,:,1]<=1)
  ontop=inside.all(-1)&(low[:,:,2]>=.269).all(-1)&(low[:,:,2]<=.28).all(-1)&(wf[:,:,2]>1).all(-1)&(nw<=1)&active
  land=torch.where(ontop&cross_ever&first,land+1,torch.zeros_like(land))
  x,y,z,w=root[:,3:7].unbind(-1)
  roll=torch.atan2(2*(w*x+y*z),1-2*(x*x+y*y));pitch=torch.asin((2*(w*y-z*x)).clamp(-1,1));yaw=torch.atan2(2*(w*z+x*y),1-2*(y*y+z*z))
  heading=torch.atan2(torch.sin(yaw-target[:,3]),torch.cos(yaw-target[:,3]))
  steady=ontop&(land>=12)&(root[:,9].abs()<=.03)&(torch.linalg.vector_norm(root[:,7:9],dim=-1)<=.03)&(roll.abs()<.174533)&(pitch.abs()<.174533)&(heading.abs()<.2)
  stable=torch.where(steady,stable+1,torch.zeros_like(stable));stable_peak=torch.maximum(stable_peak,stable);success|=(stable>=200)&(~real._mixed209_flat)&active
  physics_counts.add_(active.long());previous=high[:,:,0].clone();previous_air=airborne
 real.scene.update=measure_physics
 original_compute=real.termination_manager.compute
 def compute(*args,**kwargs):
  value=original_compute(*args,**kwargs);done=real.termination_manager.terminated|real.termination_manager.time_outs
  root=tensor(robot.data.root_state_w)
  captured.update(root=root.detach().clone(),pos=tensor(robot.data.body_pos_w).detach().clone(),quat=tensor(robot.data.body_quat_w).detach().clone(),
   closure=real._mod4_closure_now.detach().clone(),wheel_forces=tensor(real.contacts194.data.net_forces_w)[:,real.contact_order194][:,wheel_ids].detach().clone())
  for i in torch.where(done&active)[0].cpu().tolist():
   terminal_rows[str(i)]=dict(control=current_control,seconds=(int(counts[i])+1)*.02,flags={n:bool(real.termination_manager.get_term(n)[i])for n in real.termination_manager.active_terms},root13=root[i].cpu().tolist())
  return value
 real.termination_manager.compute=compute
 for current_control in range(1,TASK['max_controls']+1):
  assert time.time()<deadline
  d=depth_features();x=torch.cat((obs['policy'],d/d.new_tensor([4.,.4,2.,np.pi,2.,4.,1.,.2,1.])),-1)
  with torch.inference_mode():action=actor(x)
  assert torch.isfinite(action).all();before=active.clone();counts.add_(before.long());overflow.add_((action.abs()>6)&before[:,None]);depth_valid.add_((d[:,8]==1)&before)
  obs,reward,done,extra=vec.step(action)
  reward_sum.add_(torch.where(before,reward,0.));r=captured['root'];q=r[:,3:7];v=r[:,7:10]
  u=-q[:,:3];tv=2*torch.cross(u,v,dim=-1);bodyv=v+q[:,3,None]*tv+torch.cross(u,tv,dim=-1)
  vx_sum.add_(torch.where(before,bodyv[:,0],0.));expected=torch.full((80,),1.4,device=real.device);expected[ground_ids]=ground_v
  vx_mae.add_(torch.where(before,(bodyv[:,0]-expected).abs(),0.))
  frames.append(dict(pos=captured['pos'][selected].cpu().numpy(),quat=captured['quat'][selected].cpu().numpy(),root=r[selected].cpu().numpy(),
   force=captured['wheel_forces'][selected].cpu().numpy(),action=action[selected].cpu().numpy(),depth=d[selected].cpu().numpy()))
  active&=~done.bool()
  if current_control%50==0:put('PROGRESS287.json',dict(control=current_control,active_first_episodes=int(active.sum()),successes=int(success.sum())))
  if not active.any():break
 assert phys_calls==current_control*8 and int(real._integrated_contact.tick)-tick0==current_control*8 and int(real._feedback_100hz_tick)-fb0==current_control*2
 assert all(torch.equal(value,actor.state_dict()[key])for key,value in weights.items())
 results=[]
 for i in range(80):
  isflat=bool(real._mixed209_flat[i]);controls=int(counts[i]);term=terminal_rows.get(str(i))
  results.append(dict(env=i,kind='ground'if isflat else'heldout270',controls=controls,seconds=controls*.02,full_window=controls==400,
   command_vx=float(expected[i]),body_vx_mean=float(vx_sum[i]/max(1,controls)),body_vx_MAE=float(vx_mae[i]/max(1,controls)),target=target[i].cpu().tolist(),
   episode_terminal=term,first_air_events=int(first_air[i]),airborne_ever=bool(flight_ever[i]),first_flight_both_cross=bool(cross_ever[i]),
   longest_stable_seconds=float(stable_peak[i])*.0025,strict270_stable=bool(success[i]),depth_valid_controls=int(depth_valid[i]),action_overflow=overflow[i].cpu().tolist()))
 replay=[]
 for j,env_id in enumerate(selected):
  count=int(counts[env_id]);packet=dict(body_position_w=np.stack([f['pos'][j]for f in frames[:count]]),body_quat_xyzw=np.stack([f['quat'][j]for f in frames[:count]]),
   root13=np.stack([f['root'][j]for f in frames[:count]]),wheel_contact_xyz=np.stack([f['force'][j]for f in frames[:count]]),
   action6=np.stack([f['action'][j]for f in frames[:count]]),depth9=np.stack([f['depth'][j]for f in frames[:count]]))
  path=OUT/('REPLAY287_env'+str(env_id)+'.npz');np.savez_compressed(path,**packet)
  replay.append(dict(env=env_id,path=str(path),bytes=path.stat().st_size,SHA=hashlib.sha256(path.read_bytes()).hexdigest(),controls=count,
   seconds=count*.02,result=results[env_id],origin=origin[env_id].cpu().tolist(),body_names=body_names))
 jumps=[r for r in results if r['kind']=='heldout270'];ground=[r for r in results if r['kind']=='ground']
 summary=dict(passed=True,kind=TASK['kind'],model_SHA=TASK['model_SHA'],seed=9137,controls=current_control,physics_callbacks=phys_calls,
  feedback_samples=current_control*2,first_episodes=80,jump_cases=72,strict_successes=sum(r['strict270_stable']for r in jumps),crossed_cases=sum(r['first_flight_both_cross']for r in jumps),
  ground_complete=sum(r['full_window']for r in ground),ground_cases=ground,
  terminations={name:sum(bool((r['episode_terminal']or{}).get('flags',{}).get(name))for r in results)for name in real.termination_manager.active_terms},
  results=results,replay=replay,optimizer_steps=0,model_byte_reads=1,model_decodes=1,account_writes=0,
  support_measurement='400Hz full authored collision wheel bounds+net wheel load over top; no contact manifold normal identity',
  no_new_training=True,readiness='failure valid; success requires corresponding top manifold confirmation before graduation')
 put('RESULT287.json',summary);print(json.dumps({k:summary[k]for k in('passed','controls','strict_successes','crossed_cases','ground_complete','terminations')}),flush=True)
except BaseException:
 put('ORIGINAL287_ERROR.json',dict(error=traceback.format_exc(),no_auto_retry=True));raise
finally:
 if real is not None:
  try:real.close();put('ENV287_CLOSE_RETURNED.json',dict(closed=True))
  except BaseException:put('ENV287_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
 if ns is not None:put('APP287_CLOSE_REQUESTED.json',dict(close_call_next=True));ns['app'].close()
