"""Explicit one-time lefthead initialization AFTER completeoldGPUresume, never a live coupling."""
from pathlib import Path
import copy,json,sys,hashlib,torch
from local_state_projection import same,H
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D/'immutable_repair_operator'))
import left_head_exploration_migration_cpu_v1 as op
CPU_KEY='LOCAL_LEFT_HEAD_EXPLORATION_MIGRATION'
GPU_KEY='LOCAL_LEFT_HEAD_EXPLORATION_ACTUAL'

def rng_snapshot(env):
 values={};seen=set()
 def collect(obj,path,depth):
  if isinstance(obj,torch.Generator):values[path]=obj.get_state().cpu().clone();return
  if depth>4 or id(obj) in seen:return
  seen.add(id(obj))
  if isinstance(obj,dict):
   for k,v in obj.items():collect(v,path+'/'+str(k),depth+1)
  elif isinstance(obj,(tuple,list)):
   for k,v in enumerate(obj):collect(v,path+'/'+str(k),depth+1)
  elif hasattr(obj,'__dict__') and not isinstance(obj,torch.Tensor):
   for k,v in vars(obj).items():collect(v,path+'/'+k,depth+1)
 collect(env.command_manager.get_term('twist'),'command',0)
 for name,value in vars(env).items():collect(value,'env/'+name,0)
 return dict(cpu=torch.random.get_rng_state().clone(),cuda=[x.clone() for x in torch.cuda.get_rng_state_all()],named_private=values)

def apply_or_verify(runner,env,source_checkpoint,args,O,write):
 assert str(env.device).startswith('cuda'),'Actual migration GPU proof requires realCUDA runtime'
 source_path=Path(args.local_init_checkpoint);source=torch.load(source_path,map_location='cpu',weights_only=False)
 op.validate_source(source)
 assert same(runner.alg.actor.state_dict(),source['actor_state_dict']) and same(runner.alg.critic.state_dict(),source['critic_state_dict'])
 assert same(runner.alg.optimizer.state_dict(),source['optimizer_state_dict'])
 before=rng_snapshot(env);robot=env.scene['robot']
 physical=dict(root=robot.data.root_state_w.clone(),q=robot.data.joint_pos.clone(),qd=robot.data.joint_vel.clone(),control=int(env.common_step_counter))
 if args.repair_mode=='initial':
  assert H(source_path)==op.APPROVED_SOURCE_SHA and CPU_KEY not in source and GPU_KEY not in source
  repaired,old=op.migrate(source_path);assert same(old,source)
  runner.alg.actor.load_state_dict(repaired['actor_state_dict'],strict=True)
  runner.alg.optimizer.load_state_dict(repaired['optimizer_state_dict'])
  cpu_metadata=copy.deepcopy(repaired[CPU_KEY])
 else:
  assert args.repair_mode=='sameidentity' and CPU_KEY in source and GPU_KEY in source
  assert source[CPU_KEY]['profile']==op.PROFILE and source[CPU_KEY]['source_sha256']==op.APPROVED_SOURCE_SHA
  assert source[GPU_KEY]['profile']==op.PROFILE and source[GPU_KEY]['operator_sha256']==H(D/'immutable_repair_operator/left_head_exploration_migration_cpu_v1.py')
  repaired=source;cpu_metadata=copy.deepcopy(source[CPU_KEY])
 assert same(runner.alg.actor.state_dict(),repaired['actor_state_dict']) and same(runner.alg.optimizer.state_dict(),repaired['optimizer_state_dict'])
 assert same(runner.alg.critic.state_dict(),source['critic_state_dict'])
 assert same(before,rng_snapshot(env)),'Migration must not draw or reset anyglobal/privateRNG'
 assert torch.equal(physical['root'],robot.data.root_state_w) and torch.equal(physical['q'],robot.data.joint_pos) and torch.equal(physical['qd'],robot.data.joint_vel)
 assert physical['control']==int(env.common_step_counter),'No physics/control permitted in migration'
 after=rng_snapshot(env)
 actual=dict(actor=runner.alg.actor.state_dict(),critic=runner.alg.critic.state_dict(),optimizer=runner.alg.optimizer.state_dict(),captured_rng_before=before,captured_rng_after=after)
 p=O/'LEFT_HEAD_ACTUAL_CUDA_MIGRATION_ROUNDTRIP.pt';assert not p.exists();torch.save(actual,p)
 back=torch.load(p,map_location=env.device,weights_only=False);assert same(back,actual)
 gpu_metadata=dict(profile=op.PROFILE,operator_sha256=H(D/'immutable_repair_operator/left_head_exploration_migration_cpu_v1.py'),initial_source_sha256=op.APPROVED_SOURCE_SHA,
  complete_old_actorcriticstdoptimizer_identity_exact_before_explicit_axis=True,
  all12_original_CPUCUDA_startup_predecessor_markers_verified=True,actual_GPU_parameter_load_and_disk_roundtrip_exact=True,
  actor35_critic38_action6_unchanged=True,only_single_left_head_std_and_Adam_row_initialization=True,
  no_live_action_coupling_or_new_actor_truth_input=True,no_global_or_named_private_rng_change=True,
  captured_private_RNG_paths_only_no_unobserved_coverage_claim=True,
  initial_new_axis=args.repair_mode=='initial',sameidentity_no_recenter_no_momentclear=args.repair_mode=='sameidentity',
  deterministic_guarded_target_preserved_only_on_previous_observed_baseline_domain=True,future_other_five_action_physical_behavior_not_claimed_unchanged=True,
  future_floating_schema107_required=True,not_PhysX_exact_resume=True,qualified50mm=False)
 write('LEFT_HEAD_EXPLICIT_AXIS_ACTUAL_GPU_STARTUP_VERIFIED.json',dict(epoch=__import__('time').time(),pid=__import__('os').getpid(),passed=True,
  source_checkpoint_sha256=H(source_path),roundtrip=dict(path=str(p),sha256=H(p)),CPU_candidate_provenance_preserved=cpu_metadata,
  actual_GPU_axis=gpu_metadata,actual_named_private_rng_paths_compared=list(before['named_private']),actual_control_counter_unchanged=True,no_PPO_at_migration=True))
 return {CPU_KEY:cpu_metadata,GPU_KEY:gpu_metadata}

def install_action_trace(vec,env,O):
 """Observeronly hooks record true requested/clip/guarded actions beforephysics."""
 import numpy as np
 rows=[];written=0;files=[];legs=env.action_manager.get_term('legs');original_process=legs.process_actions
 def process(actions):
  result=original_process(actions);env._local_repair_guarded_leg_beforephysics=legs.processed_actions.clone();return result
 legs.process_actions=process
 original_step=vec.step
 def step(actions):
  requested=actions.detach().clone();episode=env._e1_terrain_episode.clone() if hasattr(env,'_e1_terrain_episode') else None
  result=original_step(actions)
  assert hasattr(env,'_local_repair_guarded_leg_beforephysics')
  row=dict(requested=requested.cpu().numpy(),clip6=requested.clamp(-6,6).cpu().numpy(),guarded_leg=env._local_repair_guarded_leg_beforephysics.cpu().numpy(),terminated=env.termination_manager.terminated.cpu().numpy(),truncated=env.termination_manager.time_outs.cpu().numpy())
  if episode is not None:row['episode_before']=episode.cpu().numpy()
  assert all(np.isfinite(v).all() for v in row.values())
  rows.append(row);return result
 vec.step=step
 def save():
  nonlocal written
  if len(rows)>written:
   p=O/('LEFT_HEAD_ACTION_ACTUAL_'+str(written)+'_'+str(len(rows))+'.npz');assert not p.exists()
   np.savez_compressed(p,**{k:np.stack([r[k] for r in rows[written:]]) for k in rows[0]});files.append(dict(path=str(p),bytes=p.stat().st_size,sha256=H(p),control_begin=written,control_end=len(rows)));written=len(rows)
  (O/'LEFT_HEAD_ACTION_TRACE_ACTUAL.json').write_text(json.dumps(dict(actual_controls=len(rows),files=files,requested_before_wrapper_clip=True,guarded_leg_targets_beforephysics=True,observations_and_actions_not_changed=True,no_physical_stop_contact_inferred_from_targets=True),indent=2),encoding='utf-8')
 return save
