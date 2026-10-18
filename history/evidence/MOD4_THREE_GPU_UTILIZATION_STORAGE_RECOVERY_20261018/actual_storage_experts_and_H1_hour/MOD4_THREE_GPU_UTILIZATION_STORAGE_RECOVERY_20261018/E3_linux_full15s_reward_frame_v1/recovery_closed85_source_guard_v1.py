"""E3 actual closed85 full-source guard; no E2/E1 metadata fabrication."""
import torch
def validate_E3_source(ck):
 assert ck['E3_phase']=='production' and ck['E3_production_updates']==85 and ck['E3_task']['kind']=='E3_PUBLIC_RECOVERY'
 assert ck['E3_task']['num_envs']==20000 and ck['E3_public_recovery_state']['version']==1
 assert len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and len(ck['optimizer_state_dict']['state'])==17
 assert {int(v['step']) for v in ck['optimizer_state_dict']['state'].values()}=={657660}
 sd=ck['actor_state_dict'];assert [list(sd[k].shape) for k in ('mlp.0.weight','mlp.2.weight','mlp.4.weight','mlp.6.weight')]==[[256,35],[128,256],[64,128],[6,64]]
 assert ck['critic_state_dict']['mlp.0.weight'].shape[1]==38 and sd['distribution.std_param'].shape==(6,) and torch.isfinite(sd['distribution.std_param']).all() and (sd['distribution.std_param']>0).all()
 for name in ('sensor_DR_state','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state','feedback_delay_state','physical_action_delay_state','spring_pressure_state','gas_damping_state','chassis_PD_state'):assert name in ck,name
 def finite(x):
  if torch.is_tensor(x):assert not x.is_floating_point() or torch.isfinite(x).all()
  elif isinstance(x,dict):
   for v in x.values():finite(v)
  elif isinstance(x,(tuple,list)):
   for v in x:finite(v)
 finite(ck);return True
