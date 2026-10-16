"""Reset-bound public approach command; no live policy feedback or action changes."""
import torch
from independent_expert_axis_v1 import bind_after_restore,cache
def bind(env):
 assert not hasattr(env,'_curb35_approach_axis_bound')
 result=bind_after_restore(env,'CURB20');env._curb35_approach_axis_bound=True
 term=env.command_manager.get_term('twist');x=cache(env);selected=x['target']&~term.is_standing_env
 assert torch.equal(term.vel_command_b[selected,0],.3*x['reset_direction'][selected])
 assert not term.vel_command_b[selected,1:].any()
 env._curb35_approach_command_receipt=dict(axis='CURB35_reset_bound_approach_signed0point3_yaw0',actual_target_rows=int(x['target'].sum()),actual_nonstanding_rows=int(selected.sum()),positive=int((term.vel_command_b[selected,0]>0).sum()),negative=int((term.vel_command_b[selected,0]<0).sum()),reset_direction_fixed_before_control=True,private_RNG_no_additional_draw=True,actor_inputs_no_assignment_or_live_heading_position_correction=True)
 return result
