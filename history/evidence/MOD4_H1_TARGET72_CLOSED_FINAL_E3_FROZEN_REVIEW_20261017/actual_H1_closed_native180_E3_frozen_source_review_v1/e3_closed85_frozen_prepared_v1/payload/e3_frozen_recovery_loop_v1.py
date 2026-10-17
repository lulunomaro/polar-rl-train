"""Frozen original recovery public-request/pose recipe; no learning."""
from pathlib import Path
import json,torch,numpy as np,hashlib,time
from e3_native_witness_v1 import CONTEXT,create_observed_env,build_observed_frozen_policy,finalize_observer,SMALL_EVAL_CAPACITY,tensor,cpu
@torch.inference_mode()
def run_recovery(args):
 import mod4_task as task
 from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
 torch.manual_seed(args.seed);cfg=task.Mod4EnvCfg();cfg.seed=args.seed;cfg.scene.num_envs=104;cfg.sim.device=args.device;cfg.sim.enable_scene_query_support=True
 for k,v in SMALL_EVAL_CAPACITY.items():setattr(cfg.sim.physics,k,v)
 cfg.scene.wheel_contact_scut.filter_prim_paths_expr=['/World/ground/geometry/mesh'];cfg.scene.wheel_contact_scut.max_contact_data_count_per_prim=64
 env=create_observed_env(args,cfg);vec=RslRlVecEnvWrapper(env,clip_actions=6.0);vec,policy,observer=build_observed_frozen_policy(vec,args.checkpoint,env.device)
 env.reset();env.e3_reset_enabled=True;env.place_declared_fall(torch.arange(104,device=env.device));env.publish()
 phase=env.recovery;assert torch.equal(phase.recipe,torch.arange(104,device=env.device)%13) and not phase.age.any()
 CONTEXT['save']('E3_FRESH104_EXPLICIT_LEGAL_FALL_RESET_ACTUAL.json',dict(reset=env.e3_reset_receipt,recipe=cpu(phase.recipe).tolist(),public_modes=cpu(phase.mode()).tolist(),fresh104_DR_draws_not_restored20k=True,actual_q30=cpu(env.scene['robot'].data.joint_pos).tolist(),actual_root13=cpu(env.scene['robot'].data.root_state_w).tolist(),body_names=env.e3_body_names,contact_names=env.e3_contact_names,authored34_shapes=env.e3_shapes,sourcegeometry_not_cookedShapeLocal=True))
 for tick in range(args.steps):
  env.publish();assert not env.command_manager.get_term('twist').command.any()
  action=policy(vec.get_observations());vec.step(action)
 w=env._retention_native_witness;rows=w.rows
 # These are original source-event diagnostics, not an invented graduation gate.
 events=np.stack([r['E3_event_delta'] for r in rows]);first_failure=np.full(104,args.steps,dtype=np.int64)
 for tick,r in enumerate(rows):first_failure=np.where((first_failure==args.steps)&(r['terminated']|r['truncated']),tick,first_failure)
 result=dict(case_id=args.case_id,source_SHA=args.checkpoint_sha,steps=args.steps,callbacks=4*args.steps,recipe_ids=cpu(phase.recipe).tolist(),original_source_event_delta_sum=events.sum(0).tolist(),first_ordinary_or_truncation_step=first_failure.tolist(),skill_qualification_claimed=False,no_PPO=True,frozen_architecture_audit=observer.audit(),physical_saved_every_callback=True,actual_new_recipe_not_source20k_restore=True)
 finalize_observer(env,result);return result
