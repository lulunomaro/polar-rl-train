"""Execute the actual reward path with frozen parent weights; no PPO updates."""
from pathlib import Path
import argparse,hashlib,json,os,sys,time,traceback
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--out',required=True);a=p.parse_args()
plan=json.loads(Path(a.plan).read_text());out=Path(a.out);out.mkdir(exist_ok=False)
storage=out/'kit_isolation';(storage/'data').mkdir(parents=True);(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
os.environ.update(MOD4V1_E0_JOB_ROOT=str(out),MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),MOD4_SCUT_SOURCE_PATHS=plan['source_paths'],JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1',PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15')
sys.path[:0]=[plan['runtime'],plan['shared_package'],plan['package'],plan['support']]
from launcher_mod4v1_e0 import IsolatedAppLauncher208
app=IsolatedAppLauncher208(dict(headless=True,device='cuda:0',enable_cameras=False)).app;env=None
try:
 import torch,numpy as np
 from mod4v3_ppo_v1.model import metadata,reset_bank
 from mod4v3_ppo_v1.scut_flat_env import configuration,tensor
 from mod4v3_ppo_v1.scut_flat_forward_square_env import ScutFlatForwardSquareEnv,configuration_forward_square
 from mod4v3_ppo_v1.scut_flat_mixed_dr_env import ScutFlatMixedRemainingDREnv
 from mod4v3_ppo_v1.physical_delay_checks import _ground_start
 from mod4v3_ppo_v1.sampling import Sampling
 from mod4v1_scut.math_ops import euler_xyz_from_quat
 torch.manual_seed(66);torch.cuda.manual_seed_all(66)
 old=configuration_forward_square();old.rewards['track_lin_vel_xy_square']=-.5;new=configuration_forward_square()
 def serial(x):
  if hasattr(x,'__dict__'):return {k:serial(v) for k,v in vars(x).items()}
  if isinstance(x,dict):return {str(k):serial(v) for k,v in x.items()}
  if isinstance(x,(list,tuple)):return [serial(v) for v in x]
  if isinstance(x,(str,int,float,bool)) or x is None:return x
  return str(x)
 oldcfg=serial(old);newcfg=serial(new);cfgdiff={k:{'before':oldcfg.get(k),'after':newcfg.get(k)} for k in set(oldcfg)|set(newcfg) if oldcfg.get(k)!=newcfg.get(k)}
 assert set(cfgdiff)=={'rewards'},cfgdiff
 assert {k for k in old.rewards if old.rewards[k]!=new.rewards[k]}=={'track_lin_vel_xy_square'}
 assert old.rewards['track_lin_vel_xy_square']==-.5 and old.lin_vel_xy_square_sigma==1.
 assert new.rewards['track_lin_vel_xy_square']==-1. and new.lin_vel_xy_square_sigma==1.
 meta=metadata(plan['package']);bank=reset_bank(plan['package'],plan['reset_bank'])
 env=ScutFlatMixedRemainingDREnv(configuration(meta,bank,4,66),meta,bank);env.render_enabled=False
 with torch.inference_mode():_ground_start(env,6600)
 env._ground_command_until.zero_()
 env.sample=Sampling(env);parity=env.sample.parity();commands=torch.tensor([[2.2,0.,0.],[2.,0.,0.],[-1.5,0.,0.],[0.,0.,0.]],device=env.device)
 def command():
  env.command.copy_(commands);env.height.fill_(.28);env.command_timer.fill_(10000.);env.heading_env.zero_();env.standing_env.zero_();env.reward.command.copy_(commands);env.reward.height_cmd.copy_(env.height)
 command();digest=hashlib.sha256(Path(plan['parent']).read_bytes()).hexdigest();assert digest==plan['parent_sha256']
 ck=torch.load(plan['parent'],map_location=env.device,weights_only=False);s=ck['actor_state_dict'];dims=[s['mlp.0.weight'].shape[1]]+[s[f'mlp.{i}.weight'].shape[0] for i in (0,2,4,6)];layers=[]
 for i in range(4):
  layers.append(torch.nn.Linear(dims[i],dims[i+1]));
  if i<3:layers.append(torch.nn.ELU())
 actor=torch.nn.Sequential(*layers).to(env.device);actor.load_state_dict({k[4:]:v for k,v in s.items() if k.startswith('mlp.')});actor.eval()
 records=[];resets=0;max_raw_error=0.;max_weighted_error=0.;max_sum_error=0.;max_closure=0.
 with torch.inference_mode():
  obs=env._get_observations()
  for step in range(24):
   actions=actor(obs['policy']).clamp(-6,6);obs,total,term,timeout,_=env.step(actions)
   r=env.reward;d=env.view.data;pitch=euler_xyz_from_quat(d.root_quat_w)[1]
   error=commands[:,0]-d.root_lin_vel_b[:,0]*torch.cos(pitch)
   actualraw=r.raw_terms['track_lin_vel_xy_square'];expectedraw=error.square();actual=r._last_reward_terms['track_lin_vel_xy_square'];expected=-1.*expectedraw*.02
   max_raw_error=max(max_raw_error,float((actualraw-expectedraw).abs().max()));max_weighted_error=max(max_weighted_error,float((actual-expected).abs().max()))
   summed=torch.stack(list(r._last_reward_terms.values()),-1).sum(-1);max_sum_error=max(max_sum_error,float((summed-total).abs().max()))
   assert bool(torch.isfinite(total).all()) and obs['policy'].shape==(4,35) and obs['critic'].shape==(4,78)
   resets+=int((term|timeout).sum());max_closure=max(max_closure,float(env.closure_error.max()))
   if step in (0,1,8,16,23):records.append(dict(step=step,error_mps=error.tolist(),square_raw=actualraw.tolist(),square_reward_per_step=actual.tolist(),baseline_square_same_state=(-.5*error.square()*.02).tolist(),total_reward=total.tolist(),numerical=int(env.numeric.sum())))
   command()
 assert resets==0 and max_raw_error<1e-5 and max_weighted_error<1e-6 and max_sum_error<1e-6
 errors=[-2.2,-1.2,-.6,-.15,0.,.15,.6,1.2,2.2]
 curve=[dict(error_mps=e,old_rate=-.5*e*e,new_rate=-1.*e*e,new_step=-1.*e*e*.02,old_rate_d_reward_d_v=e,new_rate_d_reward_d_v=2.*e) for e in errors]
 result=dict(parent_sha256=digest,parent_iteration=ck.get('iter'),profile='flat_remaining_mixed_dr',num_envs=4,steps=24,no_optimizer_constructed=True,config_diff=cfgdiff,old_effective_coefficient=-.5,new_effective_coefficient=-1.,formula='-1.0 * (command_vx - root_lin_vel_b_x*cos(pitch))**2 * .02',max_raw_error=max_raw_error,max_weighted_error=max_weighted_error,max_reward_sum_error=max_sum_error,reset_events=resets,max_closure_m=max_closure,parity=parity,records=records,curve=curve,policy_input=35,critic_input=78,interpretation='Reward implementation only. Frozen weights cannot demonstrate learning or speed recovery.')
 (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
except BaseException:
 (out/'ERROR.json').write_text(json.dumps(dict(traceback=traceback.format_exc()),ensure_ascii=False,indent=2));raise
finally:
 if env is not None:env.close()
 (out/'SAFE_CLOSED.json').write_text(json.dumps(dict(epoch=time.time(),result=(out/'RESULT.json').exists(),error=(out/'ERROR.json').exists())))
 app.close()
