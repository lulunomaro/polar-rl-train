"""User-authorized isolated TGS solver repair screening; no PPO or production authority."""
from pathlib import Path
import argparse,json,os,sys,time,hashlib,traceback
D=Path(__file__).resolve().parent;B=D.parent;CODE=B/'source/runtime/isaac/mod4'
for k,v in json.loads((CODE/'env.json').read_text()).items():os.environ[k]=str(v)
os.environ.update(RM_PHYSICS_DT_S='.0025',RM_MOD4_USD=str(B/'source/assets/robot.usd'),ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES')
sys.path.insert(0,str(B/'source/runtime'));sys.path.insert(0,str(CODE))
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--steps',type=int,default=3000);p.add_argument('--num_envs',type=int,default=32);p.add_argument('--solver-pos',type=int,required=True);p.add_argument('--mode',choices=['replay','exploration'],required=True);p.add_argument('--replay-file');p.add_argument('--action-seed',type=int,default=20261007)
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(p);args=p.parse_args();assert args.solver_pos in (16,24,32);os.environ.update(RM_SOLVER_POS=str(args.solver_pos),RM_SOLVER_VEL='4');app=AppLauncher(args).app
import torch,numpy as np
from pxr import Usd,UsdPhysics,UsdGeom,PhysxSchema
from sensor_a0_runtime import SensorMod4Env
import mod4_task as task
from frozen_history_policy import load_frozen_actor
from nominal_parameter_audit import parameter_audit
from tensordict import TensorDict
out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,v):(out.parent/n).write_text(json.dumps(v,indent=2,default=str),encoding='utf8')
def tv(x):
 if hasattr(x,'torch'):return x.torch
 import warp as wp
 if isinstance(x,wp.array):return wp.to_torch(x)
 return x
try:
 torch.manual_seed(20261002)
 cfg=task.Mod4EnvCfg();cfg.seed=20261002;cfg.scene.num_envs=args.num_envs
 assert cfg.sim.dt==.0025 and cfg.decimation==4
 cfg.scene.wheel_contact_scut.filter_prim_paths_expr=['/World/ground/geometry/mesh'];cfg.scene.wheel_contact_scut.max_contact_data_count_per_prim=64
 original_closure=cfg.terminations.closure.func;assert original_closure is task.closure_broken
 shadow=[]
 def record_only_closure(env,threshold=.002):
  would_reset=original_closure(env,threshold)
  shadow.append({'control':int(env.common_step_counter),'envs':would_reset.nonzero().flatten().cpu().tolist()})
  return torch.zeros_like(would_reset)
 # Explicit diagnostic-only censoring exception; all physical loop constraints stay enabled.
 cfg.terminations.closure.func=record_only_closure
 env=SensorMod4Env(cfg=cfg);robot=env.scene['robot'];n=env.num_envs
 actor,variant,digest=load_frozen_actor(B/'checkpoint.bin',n,env.device)
 assert variant=='A0' and digest=='6457195e25682c8059e2a9be7c7fb4531299216874ab8100014a9cf75f7f8b7b'
 env.reset();initial_params=parameter_audit(env)
 saved=torch.load(B/'checkpoint.bin',map_location='cpu',weights_only=False)
 std=saved['actor_state_dict']['distribution.std_param'].to(env.device)
 assert std.shape==(6,) and torch.isfinite(std).all() and (std>0).all()
 action_rng=torch.Generator(device=env.device);action_rng.manual_seed(args.action_seed)
 replay=None
 if args.mode=='replay':
  assert args.replay_file
  replay=np.load(args.replay_file,allow_pickle=False)['actions']
  assert replay.shape==(args.steps,n,6) and np.isfinite(replay).all()
 write('SAMPLING_CONTRACT.json',{'mode':args.mode,'saved_std':std.cpu().tolist(),'action_seed':args.action_seed,'global_rng_untouched_by_action_sampling':True,'replay_file_sha256':sha(args.replay_file) if replay is not None else None,'distribution':'mean + saved scalar std * independent standard normal, same original Gaussian family; no PPO updates'})
 initial_root=tv(robot.data.root_state_w).cpu().tolist();initial_q=tv(robot.data.joint_pos).cpu().tolist()
 stage=env.sim.stage;assert UsdGeom.GetStageMetersPerUnit(stage)==1.
 loops=[];solvers=[];enabled=[]
 for ei in range(n):
  for prim in Usd.PrimRange(stage.GetPrimAtPath('/World/envs/env_'+str(ei)+'/Robot')):
   if prim.HasAPI(PhysxSchema.PhysxArticulationAPI):
    api=PhysxSchema.PhysxArticulationAPI(prim);solvers.append({'env':ei,'position':api.GetSolverPositionIterationCountAttr().Get(),'velocity':api.GetSolverVelocityIterationCountAttr().Get()})
   if prim.IsA(UsdPhysics.Joint):
    j=UsdPhysics.Joint(prim)
    if j.GetExcludeFromArticulationAttr().Get() and j.GetJointEnabledAttr().Get():
     enabled.append(str(prim.GetPath()))
     if ei==0:loops.append({'name':prim.GetName(),'body0':j.GetBody0Rel().GetTargets()[0].name,'body1':j.GetBody1Rel().GetTargets()[0].name,'pos0':list(j.GetLocalPos0Attr().Get()),'pos1':list(j.GetLocalPos1Attr().Get())})
 assert len(loops)==6 and len(enabled)==n*6 and len(solvers)==n
 assert all(s['position']==args.solver_pos and s['velocity']==4 for s in solvers);assert cfg.sim.physics.solver_type==1
 for l in loops:
  c=task.CONTRACT['closures'][l['name']]
  assert l['body0']==c['body0'] and l['body1']==c['body1']
  assert np.max(np.abs(np.asarray(l['pos0'])-c['anchor0_m']))<1e-8 and np.max(np.abs(np.asarray(l['pos1'])-c['anchor1_m']))<1e-8
 names=robot.body_names;i0=[names.index(l['body0']) for l in loops];i1=[names.index(l['body1']) for l in loops]
 write('ACTUAL_CONFIG.json',{'dt':env.physics_dt,'control_dt':env.step_dt,'decimation':cfg.decimation,'body_count':robot.num_bodies,'tree_joint_count':robot.num_joints,'loop_joints':loops,'solver':solvers,'enabled_loop_paths':enabled,'config':cfg.to_dict(),'task_contract':task.contract_report(),'sensor_recipe':env._sensor_mild.receipt(),'checkpoint_sha256':digest,'USD_sha256':sha(task.USD_PATH),'initial_parameters':initial_params,'initial_root':initial_root,'initial_q':initial_q,'production_RslRlVecEnvWrapper_clip_actions':6.,'diagnostic_closure_reset_suppressed':True,'other_termination_terms_preserved':env.termination_manager.active_terms,'PPO_updates':0})
 frames=[];validation=[];resets=[];events=[];commands=[];actions=[];omega=[];joint_q=[];joint_qd=[];root_states=[];efforts=[];innovations=[];control=0
 oldupdate=env.scene.update
 def capture(dt):
  oldupdate(dt);assert abs(dt-.0025)<1e-12
  errors=task.closure_errors(env);value=torch.stack([tv(errors[l['name']]) for l in loops],dim=-1).detach().cpu().numpy()
  assert np.isfinite(value).all()
  # Independently verify every physics frame against raw PhysX transforms / float64 geometry.
  raw=tv(robot.root_view.get_link_transforms()).detach().cpu().numpy().astype(np.float64)
  pos=tv(robot.data.body_link_pos_w).detach().cpu().numpy().astype(np.float64);q=tv(robot.data.body_link_quat_w).detach().cpu().numpy().astype(np.float64)
  assert raw.shape==(n,len(names),7)
  pose=float(np.max(np.abs(raw[...,:3]-pos)));quat=float(np.max(np.abs(raw[...,3:]-q)))
  def anchor(ids,local):
   qq=raw[:,ids,3:];v=np.broadcast_to(np.asarray(local,dtype=np.float64),(n,6,3));t=2*np.cross(qq[...,:3],v)
   return raw[:,ids,:3]+v+qq[...,3:4]*t+np.cross(qq[...,:3],t)
  ref=np.linalg.norm(anchor(i0,[l['pos0'] for l in loops])-anchor(i1,[l['pos1'] for l in loops]),axis=-1)
  err=float(np.max(np.abs(ref-value)));assert pose<1e-6 and quat<1e-6 and err<1e-5,(pose,quat,err)
  validation.append([pose,quat,err]);frames.append(value)
 env.scene.update=capture
 oldreset=env._reset_idx
 def reset(ids):
  if ids is not None and len(ids):resets.append({'control':control,'physics_frames_before_reset':len(frames),'envs':tv(ids).cpu().tolist()})
  return oldreset(ids)
 env._reset_idx=reset
 started=time.time();nonfinite=False;tick0=env._integrated_contact.tick
 for control in range(args.steps):
  with torch.inference_mode():
   feedback=env.observation_manager.compute_group('policy');mean_action=actor(TensorDict({'policy':feedback},batch_size=[n]));assert torch.isfinite(mean_action).all()
   if replay is not None:
    action=torch.as_tensor(replay[control],device=env.device);assert torch.isfinite(action).all() and float(action.abs().max())<=6.
   else:
    innovation=torch.randn(mean_action.shape,device=env.device,generator=action_rng)
    innovations.append(innovation.cpu().numpy());action=(mean_action+std*innovation).clamp(-6.,6.)
   commands.append(tv(env.command_manager.get_term('twist').command).cpu().numpy().copy());actions.append(action.cpu().numpy())
   observation,reward,terminated,truncated,extra=env.step(action)
   omega.append(tv(robot.data.root_ang_vel_b).cpu().numpy().copy())
   joint_q.append(tv(robot.data.joint_pos).cpu().numpy().copy());joint_qd.append(tv(robot.data.joint_vel).cpu().numpy().copy());root_states.append(tv(robot.data.root_state_w).cpu().numpy().copy())
   effort=getattr(robot.data,'applied_torque',None)
   if effort is not None:efforts.append(tv(effort).cpu().numpy().copy())
   if terminated.any() or truncated.any():
    causes={name:tv(env.termination_manager.get_term(name)).nonzero().flatten().cpu().tolist() for name in env.termination_manager.active_terms}
    events.append({'control':control,'terminated':terminated.nonzero().flatten().cpu().tolist(),'timeout':truncated.nonzero().flatten().cpu().tolist(),'causes':causes})
   nonfinite=not bool(torch.isfinite(tv(robot.data.joint_pos)).all() and torch.isfinite(tv(robot.data.root_state_w)).all() and torch.isfinite(action).all() and torch.isfinite(reward).all())
   if nonfinite:
    fields={'root_state':tv(robot.data.root_state_w),'joint_pos':tv(robot.data.joint_pos),'joint_vel':tv(robot.data.joint_vel),'action':action,'reward':reward,'critic':observation['critic'],'policy':observation['policy']}
    detail={k:{'nonfinite_count':int((~torch.isfinite(v)).sum()),'indices':(~torch.isfinite(v)).nonzero().cpu().tolist(),'finite_max_abs':float(torch.nan_to_num(v).abs().max())} for k,v in fields.items()}
    term_reward=getattr(env.reward_manager,'_step_reward',None)
    if term_reward is not None:
     detail['reward_terms']={'names':env.reward_manager.active_terms,'nonfinite_indices':(~torch.isfinite(term_reward)).nonzero().cpu().tolist()}
    write('NONFINITE_DETAIL.json',{'control':control,'fields':detail})
    break
  if control%100==0:write('PROGRESS.json',{'controls':control+1,'physics_frames':len(frames),'max_closure_mm':float(np.max(frames))*1000,'wall_seconds':time.time()-started})
 e=np.stack(frames);completed=control+1;assert len(frames)==completed*4 and env._integrated_contact.tick-tick0==completed*4
 above=e>.002;run=np.zeros((n,6),dtype=np.int64);longest=0;location=None;boundaries={}
 for r in resets:boundaries.setdefault(r['physics_frames_before_reset'],[]).extend(r['envs'])
 for tick,b in enumerate(above):
  for row in boundaries.get(tick,[]):run[row]=0
  run=np.where(b,run+1,0)
  if int(run.max())>longest:
   longest=int(run.max());idx=np.unravel_index(run.argmax(),run.shape);location={'env':int(idx[0]),'joint':loops[idx[1]]['name'],'end_frame':tick,'start_frame':tick-longest+1}
 raw=out.with_suffix('.npz');np.savez_compressed(raw,closure_m=e,validation=np.asarray(validation),commands=np.stack(commands),actions=np.stack(actions),root_omega_body=np.stack(omega),joint_q=np.stack(joint_q),joint_qd=np.stack(joint_qd),root_state_w=np.stack(root_states),applied_torque=np.stack(efforts) if efforts else np.empty((0,)),standard_normal_innovation=np.stack(innovations) if innovations else np.empty((0,)))
 maximum=np.unravel_index(e.argmax(),e.shape)
 result={'phase':'partial_nonfinite' if nonfinite else 'complete','model':'MOD4 detailed production USD','checkpoint_iteration':24061,'checkpoint_sha256':digest,'physics_dt_s':.0025,'policy_dt_s':.01,'solver_position':args.solver_pos,'solver_velocity':4,'num_envs':n,'simulated_seconds':completed*.01,'physics_frames':len(frames),'total_samples':int(e.size),'percentile_mm':{str(v):float(np.percentile(e.astype(np.float64),v))*1000 for v in (50,95,99,99.9)},'max_closure_mm':float(e.max())*1000,'rms_closure_mm':float(np.sqrt(np.mean(e.astype(np.float64)**2)))*1000,'over_2mm_samples':int(above.sum()),'over_2mm_fraction':float(above.mean()),'longest_contiguous_over_2mm_seconds':longest*.0025,'longest_location':location,'maximum_location':{'frame':int(maximum[0]),'env':int(maximum[1]),'joint':loops[maximum[2]]['name']},'per_joint_max_mm':dict(zip([l['name'] for l in loops],(e.max(axis=(0,1))*1000).tolist())),'measurement_validation_max':np.max(validation,axis=0).tolist(),'reset_events':resets,'termination_events':events,'closure_would_terminate':shadow,'closure_reset_suppressed_only_in_this_diagnostic':True,'nonfinite':nonfinite,'max_mimic_rad':float(getattr(env,'_mod4_max_mimic',float('nan'))),'initial_parameters':initial_params,'final_parameters':parameter_audit(env),'sensor_recipe':env._sensor_mild.receipt(),'command_min':np.stack(commands).min(axis=(0,1)).tolist(),'command_max':np.stack(commands).max(axis=(0,1)).tolist(),'wall_seconds':time.time()-started,'raw_sha256':sha(raw),'PPO_updates':0,'production_admission':False,'scope':'isolated 2.5ms/4 TGS position iterations sweep, exact copied task/white_v3/D1+D2 and checkpoint24061; physical loop constraints enabled, closure termination shadow recorded for uncensored diagnostics only; no admission or optimizer updates','action_mode':args.mode,'saved_std':std.cpu().tolist(),'action_seed':args.action_seed,'action_trace_sha256':hashlib.sha256(np.stack(actions).tobytes()).hexdigest(),'innovation_sha256':hashlib.sha256(np.stack(innovations).tobytes()).hexdigest() if innovations else None,'solver_type':cfg.sim.physics.solver_type,'body_joint_names':robot.joint_names,'torque_trace_available':bool(efforts),'fixed_control_dt_and_hardware_envelope':True}
 out.write_text(json.dumps(result,indent=2),encoding='utf8');print('MOD4_CLOSURE_RESULT '+json.dumps({k:result[k] for k in ('percentile_mm','max_closure_mm','over_2mm_fraction','longest_contiguous_over_2mm_seconds','nonfinite')}),flush=True)
 env.close()
except Exception:
 out.with_suffix('.error.txt').write_text(traceback.format_exc(),encoding='utf8');raise
finally:app.close()
