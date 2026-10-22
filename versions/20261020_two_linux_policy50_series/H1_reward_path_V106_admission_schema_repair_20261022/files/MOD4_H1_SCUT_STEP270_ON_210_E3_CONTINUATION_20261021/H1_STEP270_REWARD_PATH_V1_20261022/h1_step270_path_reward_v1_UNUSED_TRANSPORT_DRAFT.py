"""Reward-only shaping for the human-authorized 270mm step task.

No action, command, physics, termination, success contract, RNG or optimizer
access. Callback transport uses measured collider motion, not a ballistic
prediction or a root/COM proxy for wheel clearance. Constants are reward scales,
not new qualification, health or success thresholds.
"""
import torch

RECIPE = dict(version='step270_forward_clearance_path_reward_v1',
    approach_event_scale=4., clearance_transport_event_scale=8.,
    forward_takeoff_event_scale=.25, actual_edge_event_scale=6.,
    actual_landing_event_scale=8., actual_stable_recovery_event_scale=16.,
    requested_forward_rate_weight=3., air_zero_torque_weight=.5,
    leg_tuck_weight=.5, wheel_below_base_weight=.5,
    clearance_target_m=.270, existing_forward_command_m_s=.8,
    path_start_x_m=-.10, path_target_x_m=.60,
    strict_goal_and_command_publisher_unchanged=True)


def path_increment(*, previous_front, current_front, wheel_bottom, origin_x,
                   active, airborne, launched, clean_upright, vx,
                   takeoff, edge_event, landing, recovery):
    """Control-independent callback contribution; no positive-only delta.

    Signed horizontal potential change prevents repeated back/forth approach
    farming. The clearance transport term is a signed path integral; holding a
    high vertical jump stationary earns zero transport. Vertical progress alone
    and takeoff alone no longer receive the old event reward. Actual edge,
    landing and stable-recovery events retain their strict original witnesses.
    """
    start=RECIPE['path_start_x_m']; end=RECIPE['path_target_x_m']
    previous=previous_front.amin(-1)-origin_x
    current=current_front.amin(-1)-origin_x
    initialized=(previous_front > -1.e5).all(-1)
    delta=((current.clamp(start,end)-previous.clamp(start,end))/(end-start))
    gate=active & clean_upright & initialized
    approach=gate.to(vx.dtype)*delta*RECIPE['approach_event_scale']
    clearance=(wheel_bottom.amin(-1)/RECIPE['clearance_target_m']).clamp(0.,1.)
    transport=gate.to(vx.dtype)*(airborne & launched).to(vx.dtype)*delta*clearance.square()*RECIPE['clearance_transport_event_scale']
    takeoff_value=takeoff.to(vx.dtype)*(vx/RECIPE['existing_forward_command_m_s']).clamp(0.,1.)*RECIPE['forward_takeoff_event_scale']
    events=(takeoff_value+edge_event.to(vx.dtype)*RECIPE['actual_edge_event_scale']
            +landing.to(vx.dtype)*RECIPE['actual_landing_event_scale']
            +recovery.to(vx.dtype)*RECIPE['actual_stable_recovery_event_scale'])
    return dict(approach=approach,clearance_transport=transport,strict_events=events,
                total=approach+transport+events)


def requested_forward_rate(*, request, attempt, landed, vx, vy, roll, pitch):
    # Reward actual world-x transport toward the authored step. No force or
    # command is generated; reverse/sideways motion cannot earn this term.
    active=request & attempt & ~landed
    alignment=torch.exp(-(vy/.3).square()-(roll/.3).square()-(pitch/.3).square())
    return active.to(vx.dtype)*(vx/RECIPE['existing_forward_command_m_s']).clamp(0.,1.)*alignment


def measured_rate(env,name):
    p=env.h1_phase
    if name=='path_progress':return p.progress_control/float(env.step_dt)
    if name=='requested_forward':
        from h1_takeoff_progress_environment_v2 import tensor
        from isaaclab.utils.math import euler_xyz_from_quat
        root=tensor(env.scene['robot'].data.root_state_w)
        roll,pitch,_=euler_xyz_from_quat(root[:,3:7])
        return requested_forward_rate(request=p.request_for_action,attempt=p.attempt,
            landed=p.landed,vx=root[:,7],vy=root[:,8],roll=roll,pitch=pitch)
    raise ValueError(name)


def configure(cfg):
    from isaaclab.managers import RewardTermCfg
    # Keep original event/height progress in diagnostics and checkpoint state;
    # replace only its contribution to the scalar learning reward.
    cfg.rewards.h1_control_events.weight=0.
    cfg.rewards.h1_scut_fudan_air_wheel_zero_torque.weight=RECIPE['air_zero_torque_weight']
    cfg.rewards.h1_scut_fudan_leg_tuck.weight=RECIPE['leg_tuck_weight']
    cfg.rewards.h1_scut_fudan_wheel_below_base.weight=RECIPE['wheel_below_base_weight']
    for name,weight in [('path_progress',1.),('requested_forward',RECIPE['requested_forward_rate_weight'])]:
        setattr(cfg.rewards,'h1_step270_'+name,RewardTermCfg(func=measured_rate,weight=weight,params={'name':name}))
    cfg._h1_step270_path_reward_recipe=dict(RECIPE)
    return cfg
