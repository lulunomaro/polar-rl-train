"""Candidate116 reward API. Legacy equations are retained for diagnostics/off-request.
Every training term is explicitly present in selected_optimization_terms.
"""
import torch
from legacy_fudan111_reward_diagnostics_v1 import (
    BoundOwnStepReward,UPSTREAM_COMMIT,NATIVE_UNAVAILABLE_OR_STATEFUL_ORIGINAL_TERMS,
    _weighted,instantaneous_jump_terms,instantaneous_stair_recovery_terms,JUMP_WEIGHTS,RECOVERY_WEIGHTS,
    contact_and_step_modes as legacy_modes)
from direct_wheel_height_command_reward_v1 import CommandReward,modes as command_modes,evaluate
PARAMETERS=CommandReward()

def contact_and_step_modes(low,high,force_z,root_x,root_vz,p):
    assert p.step_top_z_m==PARAMETERS.step_height and p.step_edge_x_m==PARAMETERS.edge_x and p.platform_end_x_m==PARAMETERS.far_x
    old=legacy_modes(low,high,force_z,root_x,root_vz,p)
    new=command_modes(low,high,force_z,root_x,PARAMETERS)
    old.update(new,top_support=new['top_support'],jump=new['near']*(1-new['top_support']),recovery=1-new['near']*(1-new['top_support']),
        command_forward_velocity=new['base_command_vx']*(1-new['top_support']),wheel_bottom2=low[...,2],
        command_reward116=True,legacy_flight_is_diagnostic_only=True)
    return old

def combined_reward(m,p,mode):
    j,jparts=_weighted(instantaneous_jump_terms(m,p),JUMP_WEIGHTS,2.5,p.control_dt_s)
    r,rparts=_weighted(instantaneous_stair_recovery_terms(m,p),RECOVERY_WEIGHTS,1.,p.control_dt_s)
    # Preserve original penalty magnitudes only as a small bounded attenuation;
    # they cannot turn all task rewards negative and incentivize early falling.
    effort_names=('action_rate','torques','dof_pos_limits','nominal_state','orientation','ang_vel_xy','dof_vel')
    penalty=sum(rparts[k] for k in effort_names)/p.control_dt_s
    assert bool((penalty<=1e-6).all())
    effort=torch.exp(.05*penalty.clamp_min(-10.))
    data=dict(wheel_bottom2=mode['wheel_bottom2'],world_velocity3=torch.cat((m['task_planar_velocity'],m['world_vertical_velocity'][...,None]),-1),
        world_angular_velocity3=m['world_angular_velocity'],request_active=m['request_active'],heading_cos=m['heading_cos'],upright_cos=m['upright_cos'],root_y=m['root_lateral_position'])
    out=evaluate(data,mode,r,effort,PARAMETERS)
    assert bool(((out['total']>=-1e-7)|(m['request_active']==0)).all())
    return dict(total=out['total'],selected_optimization_terms=out['selected_terms'],
        command_tracking116=dict(command_vx=out['command_vx'],target_each_wheel_bottom_m=PARAMETERS.step_height,
            actual_wheel_bottom2=mode['wheel_bottom2'],both_wheel_height_score=out['both_wheel_height_score'],
            forward_command_fraction_squared=out['forward_command_fraction_squared'],near_both_wheels=mode['near'],effort_quality=effort,
            original_leg_length_flight_height_bonuses_not_selected=True,original_flight_is_not_airborne_truth=True),
        jump_reward=j,recovery_reward=r,jump_terms=jparts,recovery_terms=rparts,
        legacy_jump_reward_is_diagnostic_not_optimization=True,actual_success_not_inferred=True,
        own_top_support_quiet_placement=mode['top_support']*out['quiet'],top_quiet=out['quiet'],
        contact_step_modes=mode,unsupported_original_terms=NATIVE_UNAVAILABLE_OR_STATEFUL_ORIGINAL_TERMS)
