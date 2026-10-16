"""Source-only guard for a future3060 frozen evaluator; no E1 metadata fabrication."""
import torch
def validate_E2_source(ck,expected_step=651640):
 assert len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and len(ck['optimizer_state_dict']['state'])==17
 assert {int(v['step']) for v in ck['optimizer_state_dict']['state'].values()}=={expected_step}
 task=ck['owned_new_expert_task'];state=ck['E2_moving4_command_state'];assert task['kind']==state['kind']=='E2_WORLD_MOVING_SIGNED4' and task['per_GPU_envs']==20000 and state['version']==1 and state['moving_yaw_cap']==4.0
 assert ck['sensor_DR_state']['n']==20000 and ck['owned_phase']=='production' and ck['owned_phase_complete_updates']==112
 for key in ('sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state','feedback_delay_state','physical_action_delay_state','spring_pressure_state','gas_damping_state','chassis_PD_state'):assert key in ck,key
 sd=ck['actor_state_dict'];assert sd['mlp.0.weight'].shape[1]==35 and sd['mlp.6.weight'].shape[0]==6 and sd['distribution.std_param'].shape==(6,) and (sd['distribution.std_param']>0).all();assert ck['critic_state_dict']['mlp.0.weight'].shape[1]==38
 def finite(x):
  if torch.is_tensor(x):assert not x.is_floating_point() or torch.isfinite(x).all()
  elif isinstance(x,dict):
   for v in x.values():finite(v)
  elif isinstance(x,(tuple,list)):
   for v in x:finite(v)
 finite(ck)
 return dict(kind='actual_E2_signed4_worldV0p5_source',source_Adamstep=expected_step,source20k_complete_CPU=True,source_model_loaded_on_GPU=False,future_frozen_GPU_actor9_only_not_optimizer_critic_or_full20k_DRrestore=True,no_fake_E1_terrain_group_required_or_added=True,normal35_lastactualclipped6_selectedreset_required=True,not_a_target_native_or_signed4_skill_pass=True)
