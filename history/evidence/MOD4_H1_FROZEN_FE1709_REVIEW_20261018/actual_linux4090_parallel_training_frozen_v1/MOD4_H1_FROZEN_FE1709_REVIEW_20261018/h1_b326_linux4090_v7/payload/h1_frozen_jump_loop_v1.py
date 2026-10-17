"""Frozen source H1 zero-twist normal100/request4-next80/normal, no learning."""
from pathlib import Path
import json,torch,numpy as np,time,sys
from h1_frozen_witness_v1 import CONTEXT,create_observed_env,build_observed_frozen_policy,finalize_observer,SMALL_EVAL_CAPACITY,cpu
@torch.inference_mode()
def run_jump(args):
 import h1_external_operator_command_v1
 sys.modules['directional_spin_runtime']=h1_external_operator_command_v1
 import mod4_task as task
 from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
 torch.manual_seed(args.seed);cfg=task.Mod4EnvCfg();cfg.seed=args.seed;cfg.scene.num_envs=80;cfg.sim.device=args.device;cfg.sim.enable_scene_query_support=True
 for key,value in SMALL_EVAL_CAPACITY.items():setattr(cfg.sim.physics,key,value)
 cfg.scene.wheel_contact_scut.filter_prim_paths_expr=['/World/ground/geometry/mesh'];cfg.scene.wheel_contact_scut.max_contact_data_count_per_prim=64
 env=create_observed_env(args,cfg);vec=RslRlVecEnvWrapper(env,clip_actions=6.0);vec,policy,observer=build_observed_frozen_policy(vec,args.checkpoint,env.device)
 env.reset();env._h1_publish_external_request();assert not env.h1_phase.age_control.any() and not env._mod4_mode_bit.any()
 CONTEXT['save']('H1_FRESH80_ORIGINAL_GROUND_RESET_ACTUAL.json',dict(source_SHA=args.checkpoint_sha,fresh80_DR_not_source20000_restore=True,actual_q30=cpu(env.scene['robot'].data.joint_pos).tolist(),actual_root13=cpu(env.scene['robot'].data.root_state_w).tolist(),body_names=env.h1_body_names,contact_names=env.h1_contact_names,authored34_shapes=env.h1_shapes,sourcegeometry_not_cookedShapeLocal=True))
 for tick in range(args.steps):
  env._h1_publish_external_request();assert not env.command_manager.get_term('twist').command.any()
  action=policy(vec.get_observations());vec.step(action)
 from nominal_parameter_audit import parameter_audit
 audit=parameter_audit(env);assert audit['profile']=='white_v3' and audit['actual_parameters_pass']
 CONTEXT['save']('H1_ACTUAL_WHITE_V3_AND_DR_READBACK.json',dict(actual_parameter_audit=audit,physical_action_delay=env._physics_action_delay.audit(),chassis_PD=env.chassis_pd_audit(),sensor_recipe=env._sensor_mild.receipt(),feedback_delay=env.feedback_delay_recipe(),fresh80_DR_not_source20000_restore=True))
 result=dict(case_id=args.case_id,source_SHA=args.checkpoint_sha,seed=args.seed,profile=args.dr_profile,steps=args.steps,callbacks=4*args.steps,original_source_public100_80_clock=True,skill_qualification_claimed=False,no_PPO=True,frozen_architecture_audit=observer.audit(),physical_saved_every_callback=True,actual_fresh80_not_source20k_restore=True)
 finalize_observer(env,result);return result
