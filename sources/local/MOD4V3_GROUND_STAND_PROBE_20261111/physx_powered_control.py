"""Frozen policy ground-start test in its original PhysX runtime. No optimizer."""
from pathlib import Path
import argparse,hashlib,json,os,sys,time,traceback
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--poses',required=True);p.add_argument('--out',required=True);p.add_argument('--checkpoint',required=True);a=p.parse_args()
plan=json.loads(Path(a.plan).read_text());poses=json.loads(Path(a.poses).read_text());out=Path(a.out);out.mkdir(exist_ok=False)
storage=out/'kit_isolation';(storage/'data').mkdir(parents=True);(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
os.environ.update(MOD4V1_E0_JOB_ROOT=str(out),MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),MOD4_SCUT_SOURCE_PATHS=plan['source_paths'],PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15',JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1')
sys.path[:0]=[plan['runtime'],plan['shared_package'],plan['package'],plan['support']]
from launcher_mod4v1_e0 import IsolatedAppLauncher208
app=IsolatedAppLauncher208(dict(headless=True,device='cuda:0',enable_cameras=False)).app;env=None
try:
 import torch,numpy as np
 from mod4v3_ppo_v1.model import metadata,reset_bank
 from mod4v3_ppo_v1.scut_flat_env import configuration,tensor
 from mod4v3_ppo_v1.scut_flat_mixed_dr_env import ScutFlatMixedRemainingDREnv
 from mod4v3_ppo_v1.sampling import Sampling
 torch.manual_seed(1111);torch.cuda.manual_seed_all(1111)
 digest=hashlib.sha256(Path(a.checkpoint).read_bytes()).hexdigest();assert digest==poses['checkpoint_sha256']
 state=torch.load(a.checkpoint,map_location='cuda:0',weights_only=False)['actor_state_dict'];dims=[state['mlp.0.weight'].shape[1]]+[state[f'mlp.{i}.weight'].shape[0] for i in (0,2,4,6)];layers=[]
 for i in range(4):
  layers.append(torch.nn.Linear(dims[i],dims[i+1]))
  if i<3:layers.append(torch.nn.ELU())
 actor=torch.nn.Sequential(*layers).to('cuda:0');actor.load_state_dict({k[4:]:v for k,v in state.items() if k.startswith('mlp.')});actor.eval();assert dims[0]==35 and dims[-1]==6
 cases=poses['cases'][-1:];repeats=5;n=len(cases)*repeats;dev='cuda:0';ids=torch.arange(n,device=dev)
 meta=metadata(plan['package']);bank=reset_bank(plan['package'],plan['reset_bank']);cfg=configuration(meta,bank,n,1111);env=ScutFlatMixedRemainingDREnv(cfg,meta,bank);env.render_enabled=False;env.enforce_closure_reset=True;env.reset();env.sample=Sampling(env)
 names=list(env.robot.joint_names);sensor_names=list(env.scene['contacts'].body_names);base_sensor=sensor_names.index('base_link');wheel_sensors=[sensor_names.index(x) for x in ('left_wheel_link','right_wheel_link')];support_sensors=[i for i,x in enumerate(sensor_names) if x=='base_link' or 'guide' in x]
 nominal=env.full_dr.nominal_env_mask.clone();assert int(nominal.sum())==len(cases)
 q=tensor(env.robot.data.default_joint_pos).clone();root=tensor(env.robot.data.default_root_state).clone()
 for i,case in enumerate(cases):
  lo=i*repeats;hi=lo+repeats
  for j,name in enumerate(names):q[lo:hi,j]=case['joint_positions'][name]
  root[lo:hi,:3]=root.new_tensor(case['root_position'])+env.scene.env_origins[lo:hi];root[lo:hi,3:7]=root.new_tensor(case['root_quaternion_xyzw']);root[lo:hi,7:]=0.
 env.robot.write_root_state_to_sim(root,env_ids=ids);env.robot.write_joint_state_to_sim(q,torch.zeros_like(q),env_ids=ids)
 env._ground_command_until.zero_();env.actions.zero_();env.torque.zero_();env._execution_pending.fill_(True);env._sensor_pending.fill_(True);env._sensor_last_tick=-1
 def command():
  env.command.zero_();env.height.fill_(.28);env.command_timer.fill_(10000.);env.heading_env.zero_();env.standing_env.zero_();env.reward.command.zero_();env.reward.height_cmd.fill_(.28);env._ground_command_until.zero_()
 command();env.scene.write_data_to_sim();env.scene.update(dt=0.)
 alive=torch.ones(n,device=dev,dtype=torch.bool);first_hard=[None]*n;native_first=[None]*n;peak_closure=torch.zeros(n,device=dev);peak_joint=torch.zeros(n,device=dev);phase='settle';step_index=0;snapshot=None;traces=[];last_trace=None
 orig_done=env._get_dones
 def observation():
  f=tensor(env.scene['contacts'].data.net_forces_w);mag=torch.linalg.vector_norm(f,dim=-1)
  return dict(root=tensor(env.robot.data.root_state_w).clone(),q=tensor(env.robot.data.joint_pos).clone(),qd=tensor(env.robot.data.joint_vel).clone(),chassis_force=mag[:,base_sensor].clone(),support_force=mag[:,support_sensors].amax(-1).clone(),wheel_force=mag[:,wheel_sensors].clone(),closure=env.closure_error.clone())
 def test_done():
  global snapshot
  term,timeout=orig_done();hard=env.numeric|env.closure_reset|env.mimic_reset|env.fall_reset|env.catastrophic_closure_reset
  snapshot=observation();peak_closure.copy_(torch.maximum(peak_closure,snapshot['closure']));peak_joint.copy_(torch.maximum(peak_joint,snapshot['qd'].abs().amax(-1)))
  for i in (hard&alive).nonzero().flatten().tolist():
   first_hard[i]=dict(phase=phase,time_s=step_index*.02,numerical=bool(env.numeric[i]),closure=bool(env.closure_reset[i]),mimic=bool(env.mimic_reset[i]),fall=bool(env.fall_reset[i]),closure_m=float(env.closure_error[i]));alive[i]=False
  if phase=='policy':
   for i in term.nonzero().flatten().tolist():
    if native_first[i] is None:native_first[i]=dict(time_s=step_index*.02,hard=bool(hard[i]),root_height_m=float(snapshot['root'][i,2]-env.scene.env_origins[i,2]),chassis_force_N=float(snapshot['chassis_force'][i]),support_force_N=float(snapshot['support_force'][i]))
  # Standalone recovery task permits initial body contact/tilt. Native task done is
  # recorded above. Numerical/2mm closure/mimic guards remain active and censor a
  # sample permanently; auto-reset states can never count as a successful rise.
  return hard,torch.zeros_like(timeout)
 env._get_dones=test_done
 env.zero_torque_remaining.zero_()
 for step_index in range(100):
  command();env.zero_torque_remaining.zero_()
  with torch.inference_mode():control_action=actor(env._get_observations()['policy']).clamp(-6.,6.)
  env.step(control_action)
 settled=observation();settled_np={k:v.detach().cpu().numpy() for k,v in settled.items()};np.savez_compressed(out/'SETTLED_STATES.npz',**settled_np)
 valid_ground=(settled['support_force']>1.)&(settled['root'][:,2]-env.scene.env_origins[:,2]<.225)&alive
 valid_ground[torch.arange(n,device=dev)//5==len(cases)-1]=alive[torch.arange(n,device=dev)//5==len(cases)-1]
 env.reward.reset(ids);env.episode_length_buf.zero_();env.zero_torque_remaining.zero_();env.actions.zero_();env.torque.zero_();env._execution_pending.fill_(True);env._sensor_pending.fill_(True);env._sensor_last_tick=-1;command()
 phase='policy';obs=env._get_observations();start=time.monotonic();hold=torch.zeros(n,device=dev,dtype=torch.long);max_hold=hold.clone();first_success=torch.full((n,),float('nan'),device=dev);success=torch.zeros(n,device=dev,dtype=torch.bool)
 # Save t=0, then every20ms; raw native joint order and xyzw quaternions.
 def save_trace(t,s):
  global last_trace
  row={k:v.detach().cpu().numpy().copy() for k,v in s.items()};row['time_s']=float(t);row['alive']=alive.cpu().numpy().copy()
  if last_trace is not None:
   dead=~row['alive']
   for k in ('root','q','qd','chassis_force','support_force','wheel_force','closure'):row[k][dead]=last_trace[k][dead]
  traces.append(row);last_trace=row
 save_trace(0.,settled)
 for step_index in range(1,501):
  command()
  with torch.inference_mode():action=actor(obs['policy']).clamp(-6.,6.)
  obs,reward,term,timeout,info=env.step(action);s=snapshot
  # Projected gravity is already quaternion-order corrected by the runtime.
  tilt_cos=None
  # Use physical root orientation from raw xyzw quaternion for a direct check.
  quat=s['root'][:,3:7];cos=1.-2.*(quat[:,0].square()+quat[:,1].square());height=s['root'][:,2]-env.scene.env_origins[:,2]
  upright=(height>=.23)&(height<=.33)&(cos>=np.cos(np.deg2rad(20.)))&(s['support_force']<1.)&(s['wheel_force'].amin(-1)>1.)&alive&valid_ground
  hold=torch.where(upright,hold+1,0);max_hold=torch.maximum(max_hold,hold);new=(hold>=50)&~success;first_success[new]=step_index*.02-1.;success|=new;save_trace(step_index*.02,s)
 np.savez_compressed(out/'TRAJECTORIES.npz',**{k:np.stack([r[k] for r in traces]) for k in traces[0]})
 rows=[]
 for i in range(n):
  case=cases[i//5];rows.append(dict(env=i,case=case['id'],kind=case['kind'],variant='nominal' if bool(nominal[i]) else 'fullDR',replicate=i%5,valid_ground_start=bool(valid_ground[i]),settled_root_height_m=float(settled['root'][i,2]-env.scene.env_origins[i,2]),settled_chassis_force_N=float(settled['chassis_force'][i]),settled_support_force_N=float(settled['support_force'][i]),settled_max_joint_speed_rad_s=float(settled['qd'][i].abs().max()),success=bool(success[i]),first_stable_interval_start_s=float(first_success[i]) if bool(success[i]) else None,max_stable_duration_s=float(max_hold[i])*.02,first_hard_failure=first_hard[i],native_task_first_termination=native_first[i],peak_closure_m=float(peak_closure[i]),peak_joint_speed_rad_s=float(peak_joint[i]),final_root_height_m=float(traces[-1]['root'][i,2]-float(env.scene.env_origins[i,2])),final_tilt_deg=float(np.rad2deg(np.arccos(np.clip(1.-2.*sum(traces[-1]['root'][i,3:5]**2),-1.,1.))))))
 result=dict(checkpoint=a.checkpoint,checkpoint_sha256=digest,num_envs=n,num_cases=len(cases),settle_seconds=2.,policy_seconds=10.,command=dict(vx=0,vy=0,wz=0,height=.28),physics=dict(dt=float(env.cfg.sim.dt),decimation=int(env.cfg.decimation),closure_guard_m=.002),success_definition='At least1 continuous second at height .23-.33m, tilt<=20deg, both driven wheels contact>1N and chassis/guide support<1N; no safety reset. Eight sample poses, not a universal capability test.',termination_handling='Native task terminations recorded; standalone recovery permits contact/tilt while standing up. Original numerical/2mm closure/mimic guards still terminate and censor the individual sample. No post-reset success is counted.',joint_names=names,sensor_body_names=sensor_names,nominal_mask=nominal.cpu().tolist(),full_DR_summary=env.full_dr.summary(),origins=env.scene.env_origins.cpu().tolist(),elapsed_policy_wall_s=time.monotonic()-start,rows=rows)
 (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('GROUND_STAND_RESULT',json.dumps(rows,ensure_ascii=False),flush=True)
except BaseException:
 (out/'ERROR.txt').write_text(traceback.format_exc());traceback.print_exc();raise
finally:
 if env is not None:env.close()
 (out/'SAFE_CLOSED.json').write_text(json.dumps(dict(epoch=time.time(),closed=True)))
 app.close()
