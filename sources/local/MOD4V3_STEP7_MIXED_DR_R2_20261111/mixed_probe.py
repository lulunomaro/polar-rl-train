"""Read native full-range DR/reset state and run a frozen parent actor; no optimizer."""
from pathlib import Path
import argparse,os,json,sys,time,traceback,hashlib
p=argparse.ArgumentParser();p.add_argument("--plan",required=True);p.add_argument("--out",required=True);p.add_argument("--num-envs",type=int,default=64);p.add_argument("--steps",type=int,default=320);a=p.parse_args()
plan=json.loads(Path(a.plan).read_text());out=Path(a.out);out.mkdir(exist_ok=False)
storage=out/"kit_isolation";(storage/"data").mkdir(parents=True);(storage/"DerivedDataCache").mkdir();(storage/"data/user.config.json").write_text("{}")
os.environ.update(MOD4V1_E0_JOB_ROOT=str(out),MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),MOD4_SCUT_SOURCE_PATHS=plan["source_paths"],OMNI_KIT_ACCEPT_EULA="YES",ISAACSIM_ACCEPT_EULA="Y")
sys.path[:0]=[plan["runtime"],plan["shared_package"],plan["package"],plan["support"]]
from launcher_mod4v1_e0 import IsolatedAppLauncher208
app=IsolatedAppLauncher208(dict(headless=True,device="cuda:0",enable_cameras=False)).app;env=None
def put(name,d): (out/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
try:
 import torch
 from mod4v3_ppo_v1.model import metadata,reset_bank
 from mod4v3_ppo_v1.scut_flat_env import configuration,tensor
 from mod4v3_ppo_v1.scut_flat_mixed_dr_env import ScutFlatMixedRemainingDREnv as ScutFlatRemainingDREnv
 from mod4v3_ppo_v1.sampling import Sampling
 meta=metadata(plan["package"]);bank=reset_bank(plan["package"],plan["reset_bank"])
 env=ScutFlatRemainingDREnv(configuration(meta,bank,a.num_envs,66),meta,bank);env.render_enabled=False
 env.reset();env.sample=Sampling(env);env.sample.parity();dev=env.device;dr=env.full_dr;ids=torch.arange(env.num_envs,device=dev)
 read=lambda name:tensor(getattr(env.robot.root_view,name)()).clone().to(dev)
 com=read("get_coms");fr=read("get_dof_friction_properties");mass=read("get_masses");damp=read("get_dof_dampings")
 assert (com[:,dr.base_id,:3]-dr.com_nominal[:,dr.base_id,:3]-dr.startup_com_delta).abs().max()<1e-6
 assert (damp[:,env.gas_ids]-3*dr.spring_damping_scale).abs().max()<1e-6
 assert torch.all((dr.kp_scale>=.75)&(dr.kp_scale<=1.25));assert torch.all((dr.kd_scale>=.75)&(dr.kd_scale<=1.25))
 count=dr.gain_count.clone();kp=dr.kp_scale.clone();kd=dr.kd_scale.clone();spring=dr.spring_damping_scale.clone()
 tick=env._sim_step_counter
 env._sim_step_counter=719*env.cfg.decimation
 dr(env,ids);assert torch.equal(count,dr.gain_count);assert torch.equal(kp,dr.kp_scale) and torch.equal(kd,dr.kd_scale)
 env._sim_step_counter=720*env.cfg.decimation
 dr(env,ids[::2]);assert torch.all(dr.gain_count[::2]==count[::2]+1);assert torch.equal(dr.gain_count[1::2],count[1::2])
 env._sim_step_counter=tick
 for _ in range(4):env._reset_idx(ids)
 com2=read("get_coms");fr2=read("get_dof_friction_properties");mass2=read("get_masses")
 assert (com-com2).abs().max()<1e-6;assert (fr-fr2).abs().max()==0;assert (mass-mass2).abs().max()==0
 init=dict(com_readback_error=float((com[:,dr.base_id,:3]-dr.com_nominal[:,dr.base_id,:3]-dr.startup_com_delta).abs().max()),com_reset_change=float((com-com2).abs().max()),friction_reset_change=float((fr-fr2).abs().max()),mass_reset_change=float((mass-mass2).abs().max()),kp_range=[float(dr.kp_scale.min()),float(dr.kp_scale.max())],kd_range=[float(dr.kd_scale.min()),float(dr.kd_scale.max())],native_spring_damping_range=[float(damp[:,env.gas_ids].min()),float(damp[:,env.gas_ids].max())],cooldown719=True,cooldown720=True,reset_mode_counts=env.reset_count_by_mode.tolist(),initial_active_vel_max=float(tensor(env.robot.data.joint_vel)[:,env.active_ids].abs().max()),reset_length_range=[float(env.reset_length_samples.min()),float(env.reset_length_samples.max())],reset_angle_range=[float(env.reset_angle_samples.min()),float(env.reset_angle_samples.max())],native_friction=fr.cpu().tolist(),joint_names=list(env.robot.joint_names),active_dr=dr.summary())
 nominal=dr.nominal_env_mask
 assert int(nominal.sum())==a.num_envs//5
 assert torch.all(dr.body_mass_scale[nominal]==1.) and torch.all(dr.startup_com_delta[nominal]==0.)
 assert torch.all(dr.effort_scale[nominal]==1.) and torch.all(dr.kp_scale[nominal]==1.) and torch.all(dr.kd_scale[nominal]==1.)
 assert torch.all(env._action_delay_ticks[nominal]==0) and torch.all(env._sensor_delay_ticks[nominal]==0)
 obs=env._get_observations();clean=env._encode()["policy"]
 assert torch.equal(obs["policy"][nominal],clean[nominal])
 assert torch.equal(read("get_material_properties")[nominal],dr.materials.to(dev)[nominal])
 assert torch.equal(read("get_masses")[nominal],dr.mass[nominal])
 init["nominal_subset"]={"count":int(nominal.sum()),"fullDR_count":int((~nominal).sum()),"mass_material_com_gain_effort_delay_noise_readback":True,"same_reset_distribution":True}
 put("RESET_READBACK.json",init)
 assert hashlib.sha256(Path(plan["parent"]).read_bytes()).hexdigest()==plan["parent_sha256"]
 data=torch.load(plan["parent"],map_location=dev,weights_only=False);state=data["actor_state_dict"]
 dims=[state["mlp.0.weight"].shape[1]]+[state[f"mlp.{i}.weight"].shape[0] for i in [0,2,4,6]];layers=[]
 for i in range(4):
  layers.append(torch.nn.Linear(dims[i],dims[i+1]));
  if i<3:layers.append(torch.nn.ELU())
 actor=torch.nn.Sequential(*layers).to(dev);actor.load_state_dict({k[4:]:v for k,v in state.items() if k.startswith("mlp.")});actor.eval()
 obs=env._get_observations();peak=0.;closure=0.;env._external_timer.fill_(.04);env.velocity_push_time_left.fill_(.06);env.velocity_push_time_left[dr.nominal_env_mask]=1e9
 with torch.inference_mode():
  for step in range(a.steps):
   act=actor(obs["policy"]).clamp(-6,6)
   obs,reward,term,timeout,_=env.step(act)
   assert torch.isfinite(obs["policy"]).all() and torch.isfinite(obs["critic"]).all() and torch.isfinite(reward).all()
   assert obs["policy"].shape[-1]==35 and obs["critic"].shape[-1]==78
   peak=max(peak,float(tensor(env.robot.data.joint_vel)[:,env.active_ids].abs().max()));closure=max(closure,float(env.closure_error.max()))
   if step%32==0:put("PROGRESS.json",dict(step=step,done_totals=env.done_totals,peak_joint_vel=peak,max_closure_m=closure))
 assert torch.all(env.velocity_push_count[nominal]==0) and torch.all(env._external_force[nominal]==0)
 result=dict(passed=True,parent_sha256=plan["parent_sha256"],num_envs=a.num_envs,steps=a.steps,no_optimizer=True,readback=init,peak_joint_vel=peak,max_closure_m=closure,done_totals=env.done_totals,push_events=int(env.velocity_push_count.sum()),external_fraction=dr.external_fraction,obs_noise_fraction=dr.obs_noise_fraction)
 assert env.done_totals["numerical"]==0,"nonzero numerical resets in frozen probe"
 put("RESULT.json",result);print(json.dumps(result,ensure_ascii=False))
except BaseException:
 put("ERROR.json",dict(traceback=traceback.format_exc()));raise
finally:
 if env is not None:env.close()
 put("SAFE_CLOSED.json",dict(epoch=time.time(),scene_closed=True));app.close()
