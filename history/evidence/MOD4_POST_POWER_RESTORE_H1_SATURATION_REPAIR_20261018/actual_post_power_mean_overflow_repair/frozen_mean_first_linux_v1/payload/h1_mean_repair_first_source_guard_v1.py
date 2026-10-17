"""Exact H1 mean-repair immutable first1/Adam645640 source; legacy GPU labels are historical."""
import torch
from h1_takeoff_progress_phase_v2 import PROFILE, H1TakeoffProgressPhaseV2
EXPECTED = 'f3d239c40000ce185286fb91532ae05049a80748f1bba3b68b391530206f85be'
def validate_H1_source(ck):
 assert ck['owned_H1_phase']=='production' and ck['owned_H1_completed_updates']==1 and ck['failed_partial_prefix'] is False
 task=ck['owned_H1_learning_task']
 assert task['optimization_candidate']['name']=='mean_overflow_regularizer' and task['optimization_candidate']['coefficient']==.001
 assert task['kind']=='E5_H1_GROUND_PRELAUNCH_PROGRESS_V2' and task['num_envs']==20000
 assert task['public_normal_controls']==100 and task['public_jump_controls']==80 and task['then_normal_until_reset'] is True
 assert task['physics_dt']==.0025 and task['decimation']==4 and task['steps_per_update']==24
 assert len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and len(ck['optimizer_state_dict']['state'])==17
 assert {int(v['step']) for v in ck['optimizer_state_dict']['state'].values()}=={645640}
 sd=ck['actor_state_dict'];assert [list(sd[k].shape) for k in ('mlp.0.weight','mlp.2.weight','mlp.4.weight','mlp.6.weight')]==[[256,35],[128,256],[64,128],[6,64]]
 assert ck['critic_state_dict']['mlp.0.weight'].shape[1]==38 and sd['distribution.std_param'].shape==(6,) and torch.isfinite(sd['distribution.std_param']).all() and (sd['distribution.std_param']>0).all()
 state=ck['H1_public_request_phase_state'];phase=state['phase']
 assert state['version']==1 and phase['profile']==PROFILE and phase['num_envs']==20000
 reference=H1TakeoffProgressPhaseV2(20000,'cpu').tensors();assert phase['tensors'].keys()==reference.keys()
 for key, value in reference.items():assert phase['tensors'][key].shape==value.shape and phase['tensors'][key].dtype==value.dtype
 for key in ('sensor_DR_state','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state','feedback_delay_state','physical_action_delay_state','spring_pressure_state','gas_damping_state','chassis_PD_state'):assert key in ck,key
 def finite(x):
  if torch.is_tensor(x):assert not (x.is_floating_point() or x.is_complex()) or torch.isfinite(x).all()
  elif isinstance(x,dict):
   for value in x.values():finite(value)
  elif isinstance(x,(tuple,list)):
   for value in x:finite(value)
 finite(ck);return True
