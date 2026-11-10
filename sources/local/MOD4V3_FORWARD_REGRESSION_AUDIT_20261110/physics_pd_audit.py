"""Fixed-weight PD frequency diagnosis; no weight/optimizer updates."""
from pathlib import Path
import argparse,json,os,sys,time,traceback
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--out',required=True);a=p.parse_args()
plan=json.loads(Path(a.plan).read_text());out=Path(a.out);out.mkdir(exist_ok=False)
storage=out/'kit_isolation';(storage/'data').mkdir(parents=True);(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
os.environ.update(MOD4V1_E0_JOB_ROOT=str(out),MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),MOD4_SCUT_SOURCE_PATHS=plan['source_paths'],PHYSICAL_ACTION_DELAY_MIN_MS='0',PHYSICAL_ACTION_DELAY_MAX_MS='5',PHYSICAL_SENSOR_DELAY_MIN_MS='0',PHYSICAL_SENSOR_DELAY_MAX_MS='5')
sys.path[:0]=[plan['runtime'],plan['shared_package'],plan['package'],plan['support']]
from launcher_mod4v1_e0 import IsolatedAppLauncher208
app=IsolatedAppLauncher208(dict(headless=True,device='cuda:0',enable_cameras=False)).app;env=None
try:
 import torch,warp as wp,numpy as np
 from mod4v3_ppo_v1.model import metadata,reset_bank
 from mod4v3_ppo_v1.scut_flat_env import configuration,tensor
 from mod4v3_ppo_v1.scut_flat_physical_delay_env import ScutFlatPhysicalDelayEnv
 from mod4v3_ppo_v1.physical_delay_checks import _ground_start
 from mod4v3_ppo_v1.sampling import Sampling
 from mod4v1_scut.math_ops import euler_xyz_from_quat
 models=plan['audit_models'];variants=['PD100_delay0','PD100_delay5','PD200_delay5','PD400_delay5'];tasks=[2.2,-2.2];seeds=10
 cells=[(model,var,task,seed) for model in models for var in variants for task in tasks for seed in range(seeds)]
 n=len(cells);device='cuda:0';ids=torch.arange(n,device=device);torch.manual_seed(66);torch.cuda.manual_seed_all(66)
 meta=metadata(plan['package']);bank=reset_bank(plan['package'],plan['reset_bank']);env=ScutFlatPhysicalDelayEnv(configuration(meta,bank,n,66),meta,bank);env.render_enabled=False
 dr=env.full_dr;nominal_com=tensor(env.robot.root_view.get_coms()).clone().to(device);_ground_start(env,8001);env.sample=Sampling(env)
 # Explicit nominal properties only; no production model or control is edited.
 env.robot.set_masses_index(masses=dr.mass,env_ids=ids);env.robot.set_inertias_index(inertias=dr.inertia,env_ids=ids)
 env.robot.set_coms_index(coms=wp.from_torch(nominal_com[:,[dr.base_id],:].contiguous(),dtype=wp.transformf),body_ids=[dr.base_id],env_ids=ids,full_data=False)
 env.robot.root_view.set_material_properties(wp.from_torch(dr.materials.contiguous(),dtype=wp.float32),wp.from_torch(ids.to('cpu',torch.int32),dtype=wp.int32))
 env.robot.write_joint_friction_coefficient_to_sim(joint_friction_coeff=dr.static_friction_default,joint_dynamic_friction_coeff=dr.static_friction_default,joint_viscous_friction_coeff=torch.zeros_like(dr.static_friction_default),joint_ids=dr.joint_ids,env_ids=ids)
 dr.leg_gain_scale.fill_(1);dr.wheel_gain_scale.fill_(1);dr.spring_damping_scale.fill_(1);dr.torque_noise_scale.zero_();dr.obs_noise_fraction=0.;env.full_dr_torque_noise_enabled=False
 env._external_timer.fill_(10000);env._external_hold.zero_();env._external_force.zero_();env._external_torque.zero_()
 # Match each direction/seed state across model/frequency groups.
 base_ids=torch.arange(20,device=device).repeat(len(models)*len(variants))
 root=tensor(env.robot.data.root_state_w).clone();q=tensor(env.robot.data.joint_pos).clone();vel=tensor(env.robot.data.joint_vel).clone()
 root[:,:3]-=env.scene.env_origins;root=root[base_ids];root[:,:3]+=env.scene.env_origins;q=q[base_ids];vel=vel[base_ids]
 env.robot.write_root_state_to_sim(root,env_ids=ids);env.robot.write_joint_state_to_sim(q,vel,env_ids=ids)
 commands=torch.tensor([[c[2],0.,0.] for c in cells],device=device);env.heading_env.zero_();env.standing_env.zero_();env.command.copy_(commands);env.height.fill_(.28);env.command_timer.fill_(10000.);env.reward.command.copy_(commands);env.reward.height_cmd.copy_(env.height)
 env._action_delay_ticks.fill_(2);env._sensor_delay_ticks.fill_(2)
 zero=torch.tensor([c[1]=='PD100_delay0' for c in cells],device=device);env._action_delay_ticks[zero]=0;env._sensor_delay_ticks[zero]=0
 env._execution_pending.fill_(True);env._sensor_pending.fill_(True);env._sensor_last_tick=-1;env.scene.write_data_to_sim();env.scene.update(dt=0.)
 div=torch.tensor([2 if c[1]=='PD200_delay5' else 1 if c[1]=='PD400_delay5' else 4 for c in cells],device=device)
 traces=[];capture=[i for i,c in enumerate(cells) if c[3]==0];trace_ids=torch.tensor(capture,device=device)
 original_apply=env._apply_action
 def apply():
  original_apply();tick=int(env._sim_step_counter)-1;changed=(div!=4)&(tick%div==0)
  if bool(changed.any()):
   q=tensor(env.robot.data.joint_pos)[:,env.active_ids];v=tensor(env.robot.data.joint_vel)[:,env.active_ids]
   raw=torch.cat((60*(env.targets[:,:4]-q[:,:4])-2*v[:,:4],.6*(env.targets[:,4:]-v[:,4:])),dim=-1)
   stall=raw.new_tensor([53.333333333333336]*4+[28.18525375641699]*2);no_load=raw.new_tensor([16.755160819145562]*4+[55.35573187814664]*2);peak=raw.new_tensor([40.]*4+[5.775909774436091]*2)
   upper=(stall*(1-v/no_load)).clamp_min(0).minimum(peak);lower=(-stall*(1+v/no_load)).clamp_max(0).maximum(-peak)
   env.torque[changed]=raw.minimum(upper).maximum(lower)[changed];env.robot.set_joint_effort_target(env.torque,joint_ids=env.active_ids)
  if tick>=8*220:
   traces.append(torch.cat((tensor(env.robot.data.joint_vel)[trace_ids][:,env.active_ids[4:]],env.targets[trace_ids,4:],env.torque[trace_ids,4:],env.view.data.root_lin_vel_b[trace_ids,:1]),-1).clone())
 env._apply_action=apply
 def network(state):
  layers=[]
  for i in [0,2,4,6]:
   v=state[f'mlp.{i}.weight'];layers.append(torch.nn.Linear(v.shape[1],v.shape[0]))
   if i<6:layers.append(torch.nn.ELU())
  net=torch.nn.Sequential(*layers).to(device);net.load_state_dict({k[4:]:v for k,v in state.items() if k.startswith('mlp.')});net.eval();return net
 nets={m:network(torch.load(path,map_location=device,weights_only=False)['actor_state_dict']) for m,path in models.items()};masks={m:torch.tensor([c[0]==m for c in cells],device=device) for m in models}
 sums={};counts=0;resets=torch.zeros(n,device=device,dtype=torch.long);positions=[]
 with torch.inference_mode():
  obs=env._get_observations()
  for step in range(300):
   actions=torch.empty((n,6),device=device)
   for m,mask in masks.items():actions[mask]=nets[m](obs['policy'][mask]).clamp(-6,6)
   obs,reward,term,timeout,_=env.step(actions);resets+=term.long()
   if step>=180:
    counts+=1;d=env.view.data
    values=dict(vx=d.root_lin_vel_b[:,0],vx_world=d.root_lin_vel_w[:,0],pitch=euler_xyz_from_quat(d.root_quat_w)[1],wheel_vel=d.joint_vel[:,env.reward._actuate_idx[4:]],wheel_target=env.targets[:,4:],torque=env.torque[:,4:],wheel_body_vx=d.body_lin_vel_w[:,env.reward._wheel_link_idx,0],reward=reward)
    for k,v in values.items():
     if k not in sums:sums[k]=torch.zeros_like(v)
     sums[k]+=v
    positions.append(d.root_pos_w[:,0].clone())
  rows=[]
  for m in models:
   for var in variants:
    for vx in tasks:
     sel=torch.tensor([i for i,c in enumerate(cells) if c[0]==m and c[1]==var and c[2]==vx],device=device)
     fd=(positions[-1][sel]-positions[0][sel])/(.02*(counts-1))
     rows.append(dict(model=m,variant=var,cmd=vx,resets=int(resets[sel].sum()),metrics={k:(v[sel]/counts).mean(0).tolist() for k,v in sums.items()},position_fd_vx=float(fd.mean())))
  np.savez_compressed(out/'physics_trace.npz',values=torch.stack(traces).cpu().numpy(),cells=np.array([cells[i] for i in capture],dtype=str),dt=.0025)
  (out/'RESULT.json').write_text(json.dumps(dict(rows=rows,no_training=True,columns=['omegaL','omegaR','targetL','targetR','tauL','tauR','vx']),ensure_ascii=False,indent=2))
except BaseException:
 (out/'ERROR.json').write_text(json.dumps(dict(traceback=traceback.format_exc()),ensure_ascii=False,indent=2));raise
finally:
 if env is not None:env.close()
 (out/'SAFE_CLOSED.json').write_text(json.dumps(dict(epoch=time.time())));app.close()
