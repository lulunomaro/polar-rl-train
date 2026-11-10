"""Read back independent startup mass DR and execute frozen-policy physics."""
from pathlib import Path
import argparse,hashlib,json,os,sys,time,traceback
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--out',required=True);a=p.parse_args()
plan=json.loads(Path(a.plan).read_text());out=Path(a.out);out.mkdir(exist_ok=False)
storage=out/'kit_isolation';(storage/'data').mkdir(parents=True);(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
os.environ.update(MOD4V1_E0_JOB_ROOT=str(out),MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),MOD4_SCUT_SOURCE_PATHS=plan['source_paths'],JOINT_FRICTION_SCALE='0.5',SPRING_DAMPING_FRACTION='0.25',EXTERNAL_DR_FRACTION='0.25',OBS_NOISE_FRACTION='0.25',PHYSICAL_DELAY_QUANTUM_MS='5',PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15')
sys.path[:0]=[plan['runtime'],plan['shared_package'],plan['package'],plan['support']]
from launcher_mod4v1_e0 import IsolatedAppLauncher208
app=IsolatedAppLauncher208(dict(headless=True,device='cuda:0',enable_cameras=False)).app;env=None
try:
 import torch
 from mod4v3_ppo_v1.model import metadata,reset_bank
 from mod4v3_ppo_v1.scut_flat_env import configuration,tensor
 from mod4v3_ppo_v1.scut_flat_body_mass_env import ScutFlatBodyMassEnv
 from mod4v3_ppo_v1.physical_delay_checks import _ground_start
 from mod4v3_ppo_v1.sampling import Sampling
 torch.manual_seed(66);torch.cuda.manual_seed_all(66)
 meta=metadata(plan['package']);bank=reset_bank(plan['package'],plan['reset_bank'])
 env=ScutFlatBodyMassEnv(configuration(meta,bank,64,66),meta,bank);env.render_enabled=False
 dr=env.full_dr;scale=dr.body_mass_scale.clone();expected_mass=dr.mass*scale;expected_inertia=dr.inertia*scale[...,None]
 def readback():
  return tensor(env.robot.root_view.get_masses()).to(env.device).clone(),tensor(env.robot.root_view.get_inertias()).to(env.device).clone()
 initial_mass,initial_inertia=readback();mass_error=float((initial_mass-expected_mass).abs().max());inertia_error=float((initial_inertia-expected_inertia).abs().max())
 assert mass_error<1e-5 and inertia_error<1e-6,(mass_error,inertia_error)
 ids=torch.arange(env.num_envs,device=env.device)
 for _ in range(8):dr(env,ids)
 reset_mass,reset_inertia=readback();reset_mass_change=float((reset_mass-initial_mass).abs().max());reset_inertia_change=float((reset_inertia-initial_inertia).abs().max())
 (out/'RESET_READBACK.json').write_text(json.dumps(dict(mass_max_change=reset_mass_change,inertia_max_change=reset_inertia_change,initial_mass=initial_mass.cpu().tolist(),reset_mass=reset_mass.cpu().tolist(),initial_inertia=initial_inertia.cpu().tolist(),reset_inertia=reset_inertia.cpu().tolist(),expected_mass=expected_mass.cpu().tolist(),body_names=list(env.robot.body_names)),indent=2))
 assert reset_mass_change<1e-6 and reset_inertia_change<1e-7,(reset_mass_change,reset_inertia_change)
 checks={}
 for group,indices in dr.mass_groups.items():
  lo,hi=dr.mass_ranges[group];values=scale[:,indices];assert bool(((values>=lo)&(values<=hi)).all())
  checks[group]=dict(body_names=[env.robot.body_names[i] for i in indices],min=float(values.min()),max=float(values.max()))
 chosen=[i for ids_group in dr.mass_groups.values() for i in ids_group];unselected=[i for i in range(len(dr.mass_body_names)) if i not in chosen]
 assert bool((scale[:,unselected]==1).all())
 left=env.robot.body_names.index('left_front1_link');right=env.robot.body_names.index('right_front1_link')
 pair_abs_difference=(scale[:,left]-scale[:,right]).abs();assert float(pair_abs_difference.max())>.01
 with torch.inference_mode():_ground_start(env,6600)
 env.sample=Sampling(env)
 digest=hashlib.sha256(Path(plan['parent']).read_bytes()).hexdigest();assert digest==plan['parent_sha256']
 ck=torch.load(plan['parent'],map_location=env.device,weights_only=False);state=ck['actor_state_dict'];dims=[state['mlp.0.weight'].shape[1]]+[state[f'mlp.{i}.weight'].shape[0] for i in (0,2,4,6)];layers=[]
 for i in range(4):
  layers.append(torch.nn.Linear(dims[i],dims[i+1]))
  if i<3:layers.append(torch.nn.ELU())
 actor=torch.nn.Sequential(*layers).to(env.device);actor.load_state_dict({k[4:]:v for k,v in state.items() if k.startswith('mlp.')});actor.eval()
 def command():
  env.command.zero_();env.command[:,0]=2.2;env.height.fill_(.28);env.heading_env.zero_();env.standing_env.zero_();env.command_timer.fill_(10000.);env.reward.command.copy_(env.command);env.reward.height_cmd.copy_(env.height)
 command();max_closure=0.;resets=0;finite=True
 with torch.inference_mode():
  obs=env._get_observations()
  for step in range(80):
   actions=actor(obs['policy']).clamp(-6,6);obs,reward,term,timeout,_=env.step(actions);command();resets+=int((term|timeout).sum());max_closure=max(max_closure,float(env.closure_error.max()))
   finite=finite and bool(torch.isfinite(reward).all()) and all(bool(torch.isfinite(v).all()) for v in obs.values())
   assert obs['policy'].shape==(64,35) and obs['critic'].shape==(64,78)
 assert finite and env.done_totals['numerical']==0
 result=dict(passed=True,parent_sha256=digest,num_envs=64,steps=80,body_mass_groups=checks,mass_write_read_max_error_kg=mass_error,inertia_write_read_max_error=inertia_error,after8reset_mass_max_change_kg=reset_mass_change,after8reset_inertia_max_change=reset_inertia_change,unselected_body_scale_one=True,left_right_front1_mass_scale_difference_max=float(pair_abs_difference.max()),mass_scale=scale.cpu().tolist(),body_names=env.robot.body_names,actual_mass_kg=initial_mass.cpu().tolist(),critic_mass_ratio=dr.factor.cpu().tolist(),finite=finite,done_totals=env.done_totals,max_closure_m=max_closure,actor_dim=35,critic_dim=78,no_optimizer_constructed=True,active_dr=dr.summary())
 (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
except BaseException:
 (out/'ERROR.json').write_text(json.dumps(dict(traceback=traceback.format_exc()),ensure_ascii=False,indent=2));raise
finally:
 if env is not None:env.close()
 (out/'SAFE_CLOSED.json').write_text(json.dumps(dict(epoch=time.time(),result=(out/'RESULT.json').exists(),error=(out/'ERROR.json').exists())))
 app.close()
