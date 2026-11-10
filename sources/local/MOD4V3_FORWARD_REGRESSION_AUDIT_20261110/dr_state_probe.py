"""Four-environment DR state readback. No policy, optimizer, or physics rollout."""
from pathlib import Path
import argparse,json,os,sys,traceback,time,inspect
p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--out',required=True);a=p.parse_args()
plan=json.loads(Path(a.plan).read_text());out=Path(a.out);out.mkdir(exist_ok=False)
storage=out/'kit_isolation';(storage/'data').mkdir(parents=True);(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
os.environ.update(MOD4V1_E0_JOB_ROOT=str(out),MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),MOD4_SCUT_SOURCE_PATHS=plan['source_paths'],
 JOINT_FRICTION_SCALE='0.5',SPRING_DAMPING_FRACTION='0.25',EXTERNAL_DR_FRACTION='0.25',OBS_NOISE_FRACTION='0.25',
 PHYSICAL_ACTION_DELAY_MIN_MS='0',PHYSICAL_ACTION_DELAY_MAX_MS='5',PHYSICAL_SENSOR_DELAY_MIN_MS='0',PHYSICAL_SENSOR_DELAY_MAX_MS='5')
sys.path[:0]=[plan['runtime'],plan['shared_package'],plan['package'],plan['support']]
from launcher_mod4v1_e0 import IsolatedAppLauncher208
app=IsolatedAppLauncher208(dict(headless=True,device='cuda:0',enable_cameras=False)).app
env=None
try:
 import torch
 from mod4v3_ppo_v1.model import metadata,reset_bank
 from mod4v3_ppo_v1.scut_flat_env import configuration,tensor
 from mod4v3_ppo_v1.scut_flat_physical_delay_env import ScutFlatPhysicalDelayEnv
 torch.manual_seed(66);torch.cuda.manual_seed_all(66)
 meta=metadata(plan['package']);bank=reset_bank(plan['package'],plan['reset_bank'])
 env=ScutFlatPhysicalDelayEnv(configuration(meta,bank,4,66),meta,bank);env.render_enabled=False
 env.reset();dr=env.full_dr;ids=torch.arange(4,device=env.device,dtype=torch.long)
 initial=tensor(env.robot.root_view.get_coms()).clone().to(env.device)[:,dr.base_id,:3]
 com=[]
 for count in range(1,33):
  dr(env,ids)
  current=tensor(env.robot.root_view.get_coms()).clone().to(env.device)[:,dr.base_id,:3]
  delta=current-initial
  com.append(dict(additional_dr_calls=count,base_com=current.cpu().tolist(),delta_from_initial_m=delta.cpu().tolist(),max_abs_coordinate_change_m=float(delta.abs().max())))
 names=[n for n in dir(env.robot.root_view) if 'friction' in n.lower()]
 readbacks={}
 for name in names:
  if not name.startswith('get_'):continue
  try:
   value=getattr(env.robot.root_view,name)();value=tensor(value).cpu()
   readbacks[name]=dict(shape=list(value.shape),values=value.tolist())
  except Exception as e:readbacks[name]=dict(error=type(e).__name__+': '+str(e))
 def values(attr,group):
  value=getattr(env.robot.data,attr,None)
  return None if value is None else tensor(value).cpu()[:,group].tolist()
 friction={group:{attr:values(attr,index) for attr in ['joint_friction_coeff','joint_dynamic_friction_coeff','joint_viscous_friction_coeff']} for group,index in [('leg',dr.leg_active_joint_ids),('wheel',dr.wheel_joint_ids),('passive',dr.passive_joint_ids)]}
 (out/'ENGINE_FRICTION_API.txt').write_text(inspect.getsource(type(env.robot).write_joint_friction_coefficient_to_sim))
 env._external_timer.fill_(-1.);env._external_hold.zero_();wrench=[]
 for step in range(25):
  env._update_external_wrench()
  wrench.append(dict(control_call=step,hold=env._external_hold.cpu().tolist(),force=env._external_force.cpu().tolist(),torque=env._external_torque.cpu().tolist(),timer=env._external_timer.cpu().tolist()))
 result=dict(no_training=True,no_policy_loaded=True,physics_steps=0,num_envs=4,dr_calls=32,com_initial_m=initial.cpu().tolist(),com_history=com,friction_cached=friction,root_friction_methods=names,root_friction_readback=readbacks,joint_names=list(env.robot.joint_names),external_wrench_history=wrench,control_dt_s=env._control_dt)
 (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
except BaseException:
 (out/'ERROR.json').write_text(json.dumps(dict(traceback=traceback.format_exc()),ensure_ascii=False,indent=2));raise
finally:
 if env is not None:env.close()
 (out/'SAFE_CLOSED.json').write_text(json.dumps(dict(epoch=time.time())));app.close()
