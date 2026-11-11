"""Capture actual R1 observation/target/nominal-PD vectors, with frozen actor only."""
from pathlib import Path
import os,sys,json,argparse,traceback,time
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--out',required=True);p.add_argument('--checkpoint',required=True);a=p.parse_args();plan=json.loads(Path(a.plan).read_text());out=Path(a.out);out.mkdir(exist_ok=False)
storage=out/'kit';(storage/'data').mkdir(parents=True);(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
os.environ.update(MOD4V1_E0_JOB_ROOT=str(out),MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),MOD4_SCUT_SOURCE_PATHS=plan['source_paths'],PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15',JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1')
sys.path[:0]=[plan['runtime'],plan['shared_package'],plan['package'],plan['support']]
from launcher_mod4v1_e0 import IsolatedAppLauncher208
app=IsolatedAppLauncher208(dict(headless=True,device='cuda:0',enable_cameras=False)).app;env=None
try:
 import torch,numpy as np,hashlib
 from mod4v3_ppo_v1.model import metadata,reset_bank
 from mod4v3_ppo_v1.scut_flat_env import configuration,tensor
 from mod4v3_ppo_v1.scut_rough_r1_env import ScutRoughR1Env
 from mod4v3_ppo_v1.sampling import Sampling
 torch.manual_seed(1211);n=20;dev='cuda:0';meta=metadata(plan['package']);bank=reset_bank(plan['package'],plan['reset_bank']);env=ScutRoughR1Env(configuration(meta,bank,n,1211,terrain_selection='rough_r1'),meta,bank);env.enforce_closure_reset=True;env.render_enabled=False;env.reset();env.sample=Sampling(env)
 state=torch.load(a.checkpoint,map_location=dev,weights_only=False)['actor_state_dict'];dims=[35,256,128,64,6];layers=[]
 for i in range(4):
  layers.append(torch.nn.Linear(dims[i],dims[i+1]))
  if i<3:layers.append(torch.nn.ELU())
 actor=torch.nn.Sequential(*layers).to(dev).eval();actor.load_state_dict({k[4:]:v for k,v in state.items() if k.startswith('mlp.')})
 commands=torch.tensor([[0,0,0],[.3,0,0],[2.,0,0],[-1.5,0,0],[0,0,14.137167]],device=dev).repeat(4,1);heights=torch.tensor([.28,.2,.4,.28,.28],device=dev).repeat(4)
 def command():env.command.copy_(commands);env.height.copy_(heights);env.command_timer.fill_(10000.);env.heading_env.zero_();env._ground_command_until.zero_();env.reward.command.copy_(commands);env.reward.height_cmd.copy_(heights)
 rows=[];nom=env.full_dr.nominal_env_mask
 for step in range(40):
  command();obs=env._encode()['policy'];d=env.view.data
  row=dict(command=commands.clone(),height=heights.clone(),q=tensor(env.robot.data.joint_pos)[:,env.active_ids].clone(),qd=tensor(env.robot.data.joint_vel)[:,env.active_ids].clone(),gyro=d.root_ang_vel_b.clone(),gravity=d.projected_gravity_b.clone(),previous_action=env.actions.clone(),observation=obs.clone())
  with torch.inference_mode():action=actor(obs).clamp(-6.,6.)
  row['action']=action.clone();env._pre_physics_step(action);row['target']=env.targets.clone()
  counter=env._sim_step_counter;env._sim_step_counter=1;env.zero_torque_remaining.zero_();env._apply_action();env._sim_step_counter=counter;row['torque']=env.applied_motor_torque.clone();row['nominal']=nom.clone()
  rows.append({k:v.detach().cpu().numpy() for k,v in row.items()});env.step(action)
 np.savez_compressed(out/'RUNTIME_VECTORS.npz',**{k:np.concatenate([x[k] for x in rows]) for k in rows[0]})
 c=env.reward.cfg;info=dict(samples=40*n,nominal_PD_samples=40*int(nom.sum()),actual_policy_order=[env.robot.joint_names[i] for i in env.active_ids],default_q=tensor(env.robot.data.default_joint_pos)[0,env.active_ids].tolist(),delta_bounds=env.delta_bounds,physics_dt=env.cfg.sim.dt,policy_dt=.02,feedback_dt=.01,ctrl_mode_obs_enabled=c.ctrl_mode_obs_enabled,observation_clip=c.obs_input_clip_cfg,observation_scale=c.obs_input_scale_cfg,checkpoint_sha256=hashlib.sha256(Path(a.checkpoint).read_bytes()).hexdigest(),source='Actual frozen R1 source, ScutRoughR1Env; clean encoder before physical DR delays. Target and nominal torque sampled from unmodified original implementation. No optimizer.')
 (out/'CAPTURE.json').write_text(json.dumps(info,indent=2)+'\n');print('RUNTIME_CAPTURE_READY',flush=True)
except BaseException:
 (out/'ERROR.txt').write_text(traceback.format_exc());traceback.print_exc();raise
finally:
 if env is not None:env.close()
 (out/'SAFE_CLOSED.json').write_text(json.dumps(dict(epoch=time.time(),closed=True)))
 app.close()
