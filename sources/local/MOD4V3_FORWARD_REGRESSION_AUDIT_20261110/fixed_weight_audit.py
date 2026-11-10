"""Fixed-weight PhysX diagnosis. No PPO runner, backward, or optimizer step."""
from pathlib import Path
import argparse,json,os,sys,traceback,time,hashlib
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--out',required=True);a=p.parse_args()
plan=json.loads(Path(a.plan).read_text());out=Path(a.out);out.mkdir(exist_ok=False)
storage=out/'kit_isolation';(storage/'data').mkdir(parents=True);(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
os.environ.update(MOD4V1_E0_JOB_ROOT=str(out),MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),MOD4_SCUT_SOURCE_PATHS=plan['source_paths'],
 PHYSICAL_ACTION_DELAY_MIN_MS='0',PHYSICAL_ACTION_DELAY_MAX_MS='5',PHYSICAL_SENSOR_DELAY_MIN_MS='0',PHYSICAL_SENSOR_DELAY_MAX_MS='5',
 JOINT_FRICTION_SCALE='0.5',SPRING_DAMPING_FRACTION='0.25',EXTERNAL_DR_FRACTION='0.25',OBS_NOISE_FRACTION='0.25')
sys.path[:0]=[plan['runtime'],plan['shared_package'],plan['package'],plan['support']]
from launcher_mod4v1_e0 import IsolatedAppLauncher208
app=IsolatedAppLauncher208(dict(headless=True,device='cuda:0',enable_cameras=False)).app
env=None
try:
 import torch,warp as wp,numpy as np
 from isaaclab.utils.math import quat_from_euler_xyz
 from mod4v3_ppo_v1.model import metadata,reset_bank
 from mod4v3_ppo_v1.scut_flat_env import configuration,tensor
 from mod4v3_ppo_v1.scut_flat_physical_delay_env import ScutFlatPhysicalDelayEnv
 from mod4v3_ppo_v1.scut_mild_dr import MildDRv3
 from mod4v3_ppo_v1.sampling import Sampling
 variants=['nominal0','nominal5','all0','all5','all5_no_obs_noise','all5_no_wrench','all5_nominal_com','all5_nominal_gain','all5_no_joint_friction','all5_no_torque_noise','mild5','parent_legacy_obs20']
 tasks=[('forward2.2',2.2,0.),('backward2.2',-2.2,0.),('backward1.5',-1.5,0.),('yaw14.137',0.,4.5*np.pi)]
 models=plan['audit_models'];seeds=10
 cells=[(model,variant,task,i) for model in models for variant in variants for task in range(len(tasks)) for i in range(seeds)]
 n=len(cells);device='cuda:0';torch.manual_seed(66);torch.cuda.manual_seed_all(66)
 meta=metadata(plan['package']);bank=reset_bank(plan['package'],plan['reset_bank'])
 env=ScutFlatPhysicalDelayEnv(configuration(meta,bank,n,66),meta,bank);env.render_enabled=False
 dr=env.full_dr;ids=torch.arange(n,device=device,dtype=torch.long)
 nominal_com=tensor(env.robot.root_view.get_coms()).clone().to(device)
 env.reset();env.sample=Sampling(env)
 # Mirror one sampled DR group to every condition/model for each task/seed.
 base_ids=torch.arange(len(tasks)*seeds,device=device).repeat(len(models)*len(variants))
 def mirrored(value):return value[base_ids].clone()
 masses=mirrored(tensor(env.robot.root_view.get_masses()).to(device));inertias=mirrored(tensor(env.robot.root_view.get_inertias()).to(device))
 com=mirrored(tensor(env.robot.root_view.get_coms()).to(device))
 leg=mirrored(dr.leg_gain_scale);wheel=mirrored(dr.wheel_gain_scale)
 spring=mirrored(dr.spring_damping_scale);torque_noise=mirrored(dr.torque_noise_scale)
 static=mirrored(tensor(env.robot.data.joint_friction_coeff).to(device))
 dynamic=mirrored(tensor(env.robot.data.joint_dynamic_friction_coeff).to(device))
 viscous=mirrored(tensor(env.robot.data.joint_viscous_friction_coeff).to(device))
 materials=mirrored(tensor(env.robot.root_view.get_material_properties()).to(device)).cpu()
 variant_masks={v:torch.tensor([cell[1]==v for cell in cells],device=device) for v in variants}
 model_masks={m:torch.tensor([cell[0]==m for cell in cells],device=device) for m in models}
 nominal=variant_masks['nominal0']|variant_masks['nominal5']
 mild=variant_masks['mild5'];nogain=nominal|variant_masks['all5_nominal_gain'];nocom=nominal|mild|variant_masks['all5_nominal_com']
 nofriction=nominal|mild|variant_masks['all5_no_joint_friction'];notorque=nominal|mild|variant_masks['all5_no_torque_noise']
 com[nocom]=nominal_com[nocom];leg[nogain]=1.;wheel[nogain]=1.;spring[nominal|mild]=1.;torque_noise[notorque]=0.
 masses[nominal]=dr.mass[nominal];inertias[nominal]=dr.inertia[nominal]
 materials[nominal.cpu()]=dr.materials[nominal.cpu()]
 # Mild material: fixed original body surfaces, only the wheel coefficient varied.
 materials[mild.cpu()]=dr.materials[mild.cpu()]
 mild_ids=mild.nonzero().flatten();mu=mirrored(dr.mu.to(device))[mild_ids]
 materials[mild_ids.cpu()[:,None],dr.wheel_shapes]=torch.stack((mu,mu,torch.zeros_like(mu)),-1).cpu()[:,None,:]
 static[nofriction]=dr.static_friction_default[nofriction];dynamic[nofriction]=(dr.dynamic_friction_default if dr.dynamic_friction_default is not None else dr.static_friction_default)[nofriction];viscous[nofriction]=(dr.viscous_friction_default if dr.viscous_friction_default is not None else torch.zeros_like(static))[nofriction]
 env.robot.set_masses_index(masses=masses,env_ids=ids);env.robot.set_inertias_index(inertias=inertias,env_ids=ids)
 env.robot.set_coms_index(coms=wp.from_torch(com[:,[dr.base_id],:].contiguous(),dtype=wp.transformf),body_ids=[dr.base_id],env_ids=ids,full_data=False)
 env.robot.root_view.set_material_properties(wp.from_torch(materials.contiguous(),dtype=wp.float32),wp.from_torch(ids.to('cpu',torch.int32),dtype=wp.int32))
 env.robot.write_joint_friction_coefficient_to_sim(joint_friction_coeff=static,joint_dynamic_friction_coeff=dynamic,joint_viscous_friction_coeff=viscous,joint_ids=dr.joint_ids,env_ids=ids)
 dr.leg_gain_scale.copy_(leg);dr.wheel_gain_scale.copy_(wheel);dr.spring_damping_scale.copy_(spring);dr.torque_noise_scale.copy_(torque_noise)
 # Every task/seed starts at the same bank pose across condition/model cells.
 g=torch.Generator(device=device).manual_seed(9001);small=len(tasks)*seeds
 pick=torch.randint(len(env._bank_h),(small,),device=device,generator=g)[base_ids]
 q=env._bank_q[pick][:,env._bank_ids].clone();root=tensor(env.robot.data.default_root_state).clone();root[:,:3]+=env.scene.env_origins;root[:,2]=env.scene.env_origins[:,2]+env._bank_h[pick]
 def perturb(low,hi):return torch.empty(small,device=device).uniform_(low,hi,generator=g)[base_ids]
 root[:,3:7]=quat_from_euler_xyz(perturb(-.01,.01),perturb(-.01,.01),perturb(-.05,.05));root[:,7:]=0.;root[:,7]=perturb(-.01,.01);root[:,12]=perturb(-.01,.01)
 env.robot.write_root_state_to_sim(root,env_ids=ids);env.robot.write_joint_state_to_sim(q,torch.zeros_like(q),env_ids=ids)
 env.actions.zero_();env.torque.zero_();env.zero_torque_remaining.zero_();env.reward.reset(ids);env.episode_length_buf.zero_()
 commands=torch.tensor([[tasks[c[2]][1],0.,tasks[c[2]][2]] for c in cells],device=device);heights=torch.full((n,),.28,device=device)
 def command():
  env.command.copy_(commands);env.height.copy_(heights);env.command_timer.fill_(10000.);env.heading_env.zero_();env.standing_env.zero_()
  env.reward.command.copy_(commands);env.reward.height_cmd.copy_(heights)
 command();env._execution_pending.fill_(True);env._sensor_pending.fill_(True);env._sensor_last_tick=-1
 env._action_delay_ticks.fill_(2);env._sensor_delay_ticks.fill_(2)
 no_delay=variant_masks['nominal0']|variant_masks['all0']|variant_masks['parent_legacy_obs20'];env._action_delay_ticks[no_delay]=0;env._sensor_delay_ticks[no_delay]=0
 no_wrench=nominal|mild|variant_masks['all5_no_wrench'];env._external_timer.fill_(5.5);env._external_hold.zero_()
 wrench_gen=torch.Generator(device=device).manual_seed(19001)
 paired_force=torch.empty((small,3),device=device).uniform_(-2.5,2.5,generator=wrench_gen)[base_ids]
 paired_torque=torch.empty((small,3),device=device).uniform_(-.25,.25,generator=wrench_gen)[base_ids]
 paired_noise=torch.empty((small,6),device=device)
 def paired_wrench():
  env._external_timer-=env._control_dt
  event=env._external_timer<=0
  env._external_force[event]=paired_force[event];env._external_torque[event]=paired_torque[event]
  env._external_hold[event]=10;env._external_timer[event]=10000.
  env._external_force[no_wrench]=0.;env._external_torque[no_wrench]=0.;env._external_hold[no_wrench]=0
  env.robot.set_external_force_and_torque(env._external_force[:,None],env._external_torque[:,None],env_ids=ids,body_ids=[dr.base_id])
 env._update_external_wrench=paired_wrench

 env.scene.write_data_to_sim();env.scene.update(dt=0.)
 def network(state):
  dims=[state['mlp.0.weight'].shape[1]]+[state[f'mlp.{i}.weight'].shape[0] for i in (0,2,4,6)]
  layers=[]
  for j in range(4):
   layers.append(torch.nn.Linear(dims[j],dims[j+1]));
   if j<3:layers.append(torch.nn.ELU())
  net=torch.nn.Sequential(*layers).to(device);net.load_state_dict({k[4:]:v for k,v in state.items() if k.startswith('mlp.')});net.eval();return net
 actors={};critics={};std={};input_hash={}
 for name,path in models.items():
  data=torch.load(path,map_location=device,weights_only=False);actors[name]=network(data['actor_state_dict']);critics[name]=network(data['critic_state_dict']);std[name]=data['actor_state_dict']['distribution.std_param'];input_hash[name]=hashlib.sha256(Path(path).read_bytes()).hexdigest()
 no_noise=nominal|mild|variant_masks['all5_no_obs_noise']
 legacy=variant_masks['parent_legacy_obs20'];previous=None
 def policy_observation(raw):
  global previous
  pol=raw['policy'].clone();clean=env._encode()['policy'];sensor=torch.cat([env._gather(env._sensor_history,env._sensor_delay_ticks[:,i],lo,hi) for i,(lo,hi) in enumerate([(0,3),(3,6),(6,12),(12,18)])],-1)
  clean[:,4:22]=sensor;pol[no_noise]=clean[no_noise]
  prev=pol.clone() if previous is None else previous
  current=pol.clone();pol[legacy]=prev[legacy];previous=current
  return pol
 stats={};counts=0;resets=torch.zeros(n,device=device,dtype=torch.long);weighted={};rawterms={};cross={name:[] for name in actors}
 def accumulate(key,v):
  if key not in stats:stats[key]=torch.zeros_like(v)
  stats[key]+=v
 with torch.inference_mode():
  obs=env._get_observations();pol=policy_observation(obs)
  for step in range(320):
   actions=torch.empty((n,6),device=device)
   for name,mask in model_masks.items():actions[mask]=actors[name](pol[mask]).clamp(-6,6)
   env._external_timer[no_wrench]=10000.;env._external_force[no_wrench]=0.;env._external_torque[no_wrench]=0.;env._external_hold[no_wrench]=0
   obs,reward,term,timeout,_=env.step(actions);resets+=term.long();command();pol=policy_observation(obs)
   if step>=200:
    counts+=1;d=env.view.data;v=d.root_lin_vel_b[:,0];wz=d.root_ang_vel_b[:,2];qd=d.joint_vel[:,env.reward._actuate_idx]
    from mod4v1_scut.math_ops import euler_xyz_from_quat
    pitch=euler_xyz_from_quat(d.root_quat_w)[1]
    accumulate('vx',v);accumulate('wz',wz);accumulate('pitch',pitch);accumulate('height',env._height_observation());accumulate('reward',reward)
    accumulate('wheel_speed',qd[:,4:]);accumulate('wheel_target',env.targets[:,4:]);accumulate('actions',actions);accumulate('torque',env.torque)
    accumulate('wheel_slip',.0625*qd[:,4:]-v[:,None]);accumulate('external_force',env._external_force);accumulate('external_hold',(env._external_hold>0).float())
    applied=d.applied_torque[:,env.reward._actuate_idx];accumulate('reward_torque',applied)
    peak=env.torque.new_tensor([40.]*4+[5.775909774436091]*2);accumulate('torque_plateau_fraction',(env.torque.abs()>=peak*.99).float())
    for name,val in env.reward._last_reward_terms.items():
     if name not in weighted:weighted[name]=torch.zeros_like(val)
     weighted[name]+=val
    for name,val in env.reward.raw_terms.items():
     if name in env.reward.cfg.rewards and env.reward.cfg.rewards[name]!=0:
      if name not in rawterms:rawterms[name]=torch.zeros_like(val,dtype=torch.float32)
      rawterms[name]+=val.float()
    # Read-only policy comparisons on identical observation inputs; no gradient step.
    parent=next(iter(actors));mu0=actors[parent](pol)
    for name in actors:
     mu=actors[name](pol);kl=(torch.log(std[name]/std[parent])+(std[parent]**2+(mu0-mu)**2)/(2*std[name]**2)-.5).sum(-1)
     if name not in cross or not isinstance(cross[name],dict):cross[name]={'kl':torch.zeros_like(kl),'delta':torch.zeros_like(mu)}
     cross[name]['kl']+=kl;cross[name]['delta']+=mu-mu0
    if step in (200,224):
     np.savez_compressed(out/f'observations_{step}.npz',policy=pol.cpu().numpy(),critic=obs['critic'].cpu().numpy(),actions=actions.cpu().numpy())
   if step%40==0:(out/'PROGRESS.json').write_text(json.dumps({'step':step,'seconds':time.time()}))
  torch.save(dict(stats=stats,weighted=weighted,rawterms=rawterms,cross=cross,resets=resets,counts=counts,cells=cells),out/'aggregate.pt')
  rows=[]
  for model in models:
   for variant in variants:
    for ti,task in enumerate(tasks):
     chosen=[i for i,c in enumerate(cells) if c[0]==model and c[1]==variant and c[2]==ti];idx=torch.tensor(chosen,device=device)
     row=dict(model=model,variant=variant,task=task[0],command=[task[1],task[2]],n=len(chosen),resets=int(resets[idx].sum()),metrics={key:(value[idx]/counts).mean(0).tolist() for key,value in stats.items()},reward_terms={key:float(value[idx].mean()/counts) for key,value in weighted.items()},raw_reward_terms={key:float(value[idx].mean()/counts) for key,value in rawterms.items()},policy_comparison={key:dict(kl=float(value['kl'][idx].mean()/counts),mean_delta=(value['delta'][idx].mean(0)/counts).tolist()) for key,value in cross.items()})
     row['per_env_vx']=(stats['vx'][idx]/counts).tolist();rows.append(row)
  result=dict(purpose='Fixed weights only; no optimizer, backward or training updates',input_sha=input_hash,num_envs=n,physics='PhysX',steps=320,tail=120,rows=rows,
    friction_readback=dict(leg_static_mean=float(static[:,dr.leg_active_joint_ids].mean()),wheel_static_mean=float(static[:,dr.wheel_joint_ids].mean()),passive_static_mean=float(static[:,dr.passive_joint_ids].mean())),
    com_offset_max_m=float((com[:,:,:3]-nominal_com[:,:,:3]).abs().max()))
  (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
except BaseException:
 (out/'ERROR.json').write_text(json.dumps(dict(traceback=traceback.format_exc()),ensure_ascii=False,indent=2));raise
finally:
 if env is not None:env.close()
 (out/'SAFE_CLOSED.json').write_text(json.dumps(dict(epoch=time.time())))
 app.close()
