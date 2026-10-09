"""Approved S3/E1 interface only: actual gentle-grid ground, complete D0-D7, no PPO."""
import argparse,json,os,time,hashlib
from pathlib import Path
p=argparse.ArgumentParser()
for k in ('checkpoint','output'):p.add_argument('--'+k,required=True)
p.add_argument('--steps',type=int,default=300);p.add_argument('--num_envs',type=int,default=10)
p.add_argument('--seed',type=int,default=20261002);p.add_argument('--dr-profile',default='white_v3')
p.add_argument('--speed_limit',type=float,default=1.5);p.add_argument('--ramp_suite',action='store_true')
for k,v in json.loads(Path(__file__).with_name('env.json').read_text(encoding='utf8')).items():os.environ[k]=str(v)
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(p);args=p.parse_args();os.environ['RM_MILD_DR_PROFILE']=args.dr_profile
app=AppLauncher(args).app
import numpy as np,torch
import mod4_task as task
from e1_terrain_runtime import configure_intro,E1ChassisTerrainEnv,refresh_ground,query
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
from frozen_history_policy import build_frozen_policy

@torch.inference_mode()
def main():
 assert args.num_envs==10 and args.steps==300 and args.dr_profile=='white_v3'
 torch.manual_seed(args.seed);cfg=task.Mod4EnvCfg();cfg.seed=args.seed;cfg.scene.num_envs=args.num_envs;recipe=configure_intro(cfg)
 env=E1ChassisTerrainEnv(cfg=cfg);r=env.scene['robot'];env.reset();env.sim.forward();env.scene.update(env.physics_dt)
 qerr=float((r.data.joint_pos-env._rough_probe_expected_q).abs().max());assert qerr<1e-5
 assert torch.unique(r.data.root_pos_w[:,:2],dim=0).shape[0]==env.num_envs
 reset=dict(env._rough_probe_reset_receipt);partition=env.scene.terrain.exact_partition_receipt
 assert partition['pass_'] and partition['all_faces_and_winding_retained'] and not partition['geometry_simplified']
 ids=torch.tensor([1,4,7],device=env.device);other=torch.tensor([0,2,3,5,6,8,9],device=env.device)
 root=r.data.root_state_w.clone();q=r.data.joint_pos.clone();tick=int(env._sim_step_counter)
 oldCOM=env._chassis_com.component.state_dict();oldPD=env._explicit_pd.component.state_dict()
 oldbias=env._sensor_mild.bias.clone();oldepisode=env._sensor_mild.episode.clone()
 env._reset_idx(ids);env.sim.forward();env.scene.update(env.physics_dt)
 assert int(env._sim_step_counter)==tick and torch.equal(q[other],r.data.joint_pos[other]) and torch.equal(root[other],r.data.root_state_w[other])
 assert torch.equal(oldbias[other],env._sensor_mild.bias[other]) and torch.equal(oldepisode[other],env._sensor_mild.episode[other])
 assert bool((env._sensor_mild.episode[ids]==oldepisode[ids]+1).all())
 def untouched(a,b):
  if isinstance(a,dict):
   for k in a:untouched(a[k],b[k])
  elif torch.is_tensor(a) and a.ndim and a.shape[0]==env.num_envs:assert torch.equal(a[other],b[other])
 untouched(oldCOM,env._chassis_com.component.state_dict());untouched(oldPD,env._explicit_pd.component.state_dict())
 assert float((r.data.joint_pos-env._rough_probe_expected_q).abs().max())<1e-5
 vec=RslRlVecEnvWrapper(env,clip_actions=6.);vec,policy,observer=build_frozen_policy(vec,args.checkpoint,env.device)
 initial={'root':r.data.root_state_w.cpu().tolist(),'q':r.data.joint_pos.cpu().tolist(),'parameters':env.chassis_pd_audit(),'reset':reset}
 c=env._integrated_contact;tick0=c.tick;calls=dict(env._physics_action_delay.calls);ground0=getattr(env,'_rough_query_updates',0)
 frames=[];counts={n:0 for n in env.termination_manager.active_terms};peak=0.;mimic=0.;grounderror=0.;rewarderror=0.;start=time.time()
 for step in range(args.steps):
  action=policy(vec.get_observations());obs,reward,done,_=vec.step(action)
  frame=env._e1_pre_reset_frame
  assert all(bool(torch.isfinite(x).all()) for x in (action,reward,frame['root'],frame['q'],frame['ground'],frame['normal']))
  assert env._rough_termination_query_tick==env._rough_reward_query_tick==int(env._sim_step_counter)
  grounderror=max(grounderror,frame['independent_ground_error']);rewarderror=max(rewarderror,env._e1_height_formula_error)
  cmd=env.command_manager.get_command('twist');assert float(cmd[:,1:].abs().max())<1e-6 and float(cmd[:,0].abs().max())<=.300001
  for n in counts:counts[n]+=int(env.termination_manager.get_term(n).sum())
  peak=max(peak,float(frame['closure'].max()));mimic=max(mimic,float(frame['mimic'].max()))
  if step%25==0:frames.append({'control':step,'root':frame['root'].cpu().tolist(),'q':frame['q'].cpu().tolist(),'ground':frame['ground'].cpu().tolist(),'normal':frame['normal'].cpu().tolist(),'commands':cmd.cpu().tolist()})
 expected=args.steps*4;actual=c.tick-tick0;groups={k:env._physics_action_delay.calls[k]-n for k,n in calls.items()}
 assert actual==expected and all(n==expected for n in groups.values()) and grounderror<1e-5 and rewarderror<1e-6
 assert env._rough_query_updates-ground0==args.steps
 aa=env._physics_action_delay.audit();assert aa['application_formula_max_error']==0
 pa=env.chassis_pd_audit();assert pa['parameter_auditor']['actual_parameters_pass']
 sensor=env.sensor_sdk_audit();assert sensor['actor35'] and sensor['critic38_clean'] and sensor['formula_max_error']<=2e-6
 geometry=query(env).geometry;streamed=hashlib.sha256()
 for first in range(0,len(geometry.faces),100000):streamed.update(np.asarray(geometry.vertices,dtype='<f4')[geometry.faces[first:first+100000]].tobytes())
 assert streamed.hexdigest()==partition['triangle_world_f32_order_sha256']
 result={'scope':'Approved S3/E1 gentle40x40-grid actual interface; not canceled synthetic93/94 evaluation, not skill admission or learning.','SDK_interface_contract_pass':True,'new_learning':False,'no_PPO_or_optimizer_updates':True,'checkpoint_sha256':vec.checkpoint_sha256,'seed':args.seed,'num_envs':env.num_envs,'steps':args.steps,'recipe':recipe,'initial':initial,'final_parameters':pa,'selected_reset':{'ids':[1,4,7],'other_root_q_sensor_COM_PD_rows_exact':True,'selected_sensor_episode_incremented_once':True,'global_physical_clock_unchanged':True,'full30q_readback_error':qerr},'actual_contact_callbacks':actual,'actual_action_group_callbacks':groups,'action_audit':aa,'sensor_audit':sensor,'sensor_recipe':env._sensor_mild.receipt(),'feedback_recipe':env.feedback_delay_recipe(),'action_recipe':env.action_delay_recipe(),'spring_recipe':env.spring_pressure_recipe(),'gas_recipe':env.gas_damping_recipe(),'chassis_PD_recipe':env.chassis_pd_recipe(),'initial_complete_ground_query_updates':args.steps,'actual_ground_fresh_readback_max_error_m':grounderror,'height_reward_formula_max_error':rewarderror,'nonfinite':False,'ordinary_task_events':counts,'max_closure_m':peak,'max_mimic_rad':mimic,'actual_mesh':geometry.receipt(),'exact_collision_partition':partition,'contact_capture_metadata':env._contact_capture_metadata,'phase_readbacks':frames,'collection_wall_seconds':time.time()-start,'ground_truth_not_actor_input':True,'worldZ_contact_impulse_not_surface_normal_force':True,'not_PhysX_exactresume':True,'fullPPO_checkpoint_restore_still_required':True,'RM_future_entry_lip_or_fullterrain_spin_not_installed':True}
 Path(args.output).write_text(json.dumps(result,indent=2),encoding='utf8');env.close()
try:main()
except BaseException:
 import traceback
 Path(args.output).with_suffix('.error.txt').write_text(traceback.format_exc(),encoding='utf8');raise
finally:app.close()
