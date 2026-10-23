"""Reward-only shaping for the human-authorized 270mm step task.

No action, command, physics, termination, success contract, RNG or optimizer
access. Callback transport uses measured collider motion, not a ballistic
prediction or a root/COM proxy for wheel clearance. Constants are reward scales,
not new qualification, health or success thresholds.
"""
import torch

RECIPE = dict(version='step270_current_clearance_airborne_tuck_v4',
    approach_event_scale=4., clearance_transport_event_scale=8.,
    forward_takeoff_event_scale=.25, actual_edge_event_scale=6.,
    actual_landing_event_scale=8., actual_stable_recovery_event_scale=16.,
    requested_forward_rate_weight=3., air_zero_torque_weight=.5,
    leg_tuck_weight=1.7, wheel_below_base_weight=.5,
    clearance_target_m=.270, existing_forward_command_m_s=.8,
    path_start_x_m=-.10, path_target_x_m=.60,
    strict_goal_and_command_publisher_unchanged=True,
    signed_reverse_rate=True, measured_clearance_carry_gain=2.,
    clearance_carry_start_front_x_m=0., clearance_carry_full_front_x_m=.35,
    takeoff_gate_start_front_x_m=-.05, takeoff_gate_full_front_x_m=.15,
    keep_forward_reward_during_measured_flight_after_request=True)


def path_increment(*, previous_front, current_front, wheel_bottom, origin_x,
                   active, airborne, launched, clean_upright, vx,
                   takeoff, edge_event, landing, recovery, previous_joint_potential=None):
    """Control-independent callback contribution; no positive-only delta.

    Signed, bounded potential differences prevent repeated back/forth farming.
    The joint potential is zero when the wheels are still far from the step;
    holding a high vertical jump stationary earns zero potential increment.
    Vertical progress far from the edge no longer receives the old event reward. Actual edge,
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
    joint=((current-.10)/.25).clamp(0.,1.)*clearance.square()
    old_joint=joint if previous_joint_potential is None else previous_joint_potential
    transport=gate.to(vx.dtype)*(joint-old_joint)*RECIPE['clearance_transport_event_scale']
    takeoff_value=takeoff.to(vx.dtype)*(vx/RECIPE['existing_forward_command_m_s']).clamp(0.,1.)*RECIPE['forward_takeoff_event_scale']
    events=(takeoff_value+edge_event.to(vx.dtype)*RECIPE['actual_edge_event_scale']
            +landing.to(vx.dtype)*RECIPE['actual_landing_event_scale']
            +recovery.to(vx.dtype)*RECIPE['actual_stable_recovery_event_scale'])
    return dict(approach=approach,clearance_transport=transport,strict_events=events,
                total=approach+transport+events,next_joint_potential=joint)


def requested_forward_rate(*, request, attempt, landed, vx, vy, roll, pitch,
                           airborne=None, wheel_bottom=None, wheel_front=None,
                           origin_x=None):
    # Measured wheel clearance and forward motion must coincide. No command,
    # force, action, success flag or physics state is written here.
    airborne=torch.zeros_like(request) if airborne is None else airborne
    active=(request | airborne) & attempt & ~landed
    alignment=torch.exp(-(vy/.3).square()-(roll/.3).square()-(pitch/.3).square())
    quality=torch.ones_like(vx)
    if wheel_bottom is not None and wheel_front is not None and origin_x is not None:
        front=wheel_front.amin(-1)-origin_x
        near=((front-RECIPE['clearance_carry_start_front_x_m']) /
              (RECIPE['clearance_carry_full_front_x_m']-RECIPE['clearance_carry_start_front_x_m'])).clamp(0.,1.)
        clearance=(wheel_bottom.amin(-1)/RECIPE['clearance_target_m']).clamp(0.,1.)
        quality=quality+RECIPE['measured_clearance_carry_gain']*near*clearance.square()
    return active.to(vx.dtype)*(vx/RECIPE['existing_forward_command_m_s']).clamp(-1.,1.)*alignment*quality


def forward_takeoff_factor(*, wheel_front, origin_x, vx):
    front=wheel_front.amin(-1)-origin_x
    near=((front-RECIPE['takeoff_gate_start_front_x_m']) /
          (RECIPE['takeoff_gate_full_front_x_m']-RECIPE['takeoff_gate_start_front_x_m'])).clamp(0.,1.)
    return near*(vx/RECIPE['existing_forward_command_m_s']).clamp(0.,1.)


def forward_takeoff_rate(env,original_func,original_params):
    from h1_takeoff_progress_environment_v2 import tensor
    value=original_func(env,**original_params)
    root=tensor(env.scene['robot'].data.root_state_w)
    return value*forward_takeoff_factor(wheel_front=env.h1_phase.previous_front,
        origin_x=env.scene.env_origins[:,0],vx=root[:,7])


def measured_rate(env,name):
    p=env.h1_phase
    if name=='path_progress':return p.progress_control/float(env.step_dt)
    if name=='requested_forward':
        from h1_takeoff_progress_environment_v2 import tensor
        root=tensor(env.scene['robot'].data.root_state_w)
        x,y,z,w=root[:,3:7].unbind(-1)
        roll=torch.atan2(2*(w*x+y*z),1-2*(x*x+y*y))
        pitch=torch.asin((2*(w*y-z*x)).clamp(-1.,1.))
        return requested_forward_rate(request=p.request_for_action,attempt=p.attempt,
            landed=p.landed,vx=root[:,7],vy=root[:,8],roll=roll,pitch=pitch,
            airborne=p.air_ticks>0,wheel_front=p.previous_front,
            wheel_bottom=p.last_measured['step_wheel_min'][:,:,2] if 'step_wheel_min' in p.last_measured else None,
            origin_x=env.scene.env_origins[:,0])
    raise ValueError(name)


def airborne_tuck_rate(env):
    from h1_takeoff_progress_environment_v2 import tensor
    p=env.h1_phase;r=env.scene['robot'];data=r.data
    root=tensor(data.root_state_w)
    ids=[r.body_names.index(x) for x in ('left_wheel','right_wheel')]
    delta=tensor(data.body_pos_w)[:,ids]-root[:,None,:3]
    current_clear=(p.last_measured['step_wheel_min'][:,:,2]>.005).all(-1)
    active=p.attempt & (p.air_ticks>0) & current_clear & ~p.landed & ~p.crossed.all(-1)
    # Same original SCUT/Fudan measured body-to-wheel length formula.
    # Request expiry must not end retraction shaping during measured flight.
    # Stop before landing extension once both wheels actually crossed.
    compact=torch.exp(-torch.sum(torch.abs(delta.norm(dim=-1)-.22),dim=1)*4.)
    return active.to(root.dtype)*compact


def configure(cfg):
    from isaaclab.managers import RewardTermCfg
    # Keep original event/height progress in diagnostics and checkpoint state;
    # replace only its contribution to the scalar learning reward.
    cfg.rewards.h1_control_events.weight=0.
    cfg.rewards.h1_scut_fudan_air_wheel_zero_torque.weight=RECIPE['air_zero_torque_weight']
    cfg.rewards.h1_scut_fudan_leg_tuck.weight=RECIPE['leg_tuck_weight']
    cfg.rewards.h1_scut_fudan_leg_tuck.func=airborne_tuck_rate
    cfg.rewards.h1_scut_fudan_leg_tuck.params={}
    cfg.rewards.h1_scut_fudan_wheel_below_base.weight=RECIPE['wheel_below_base_weight']
    for name,weight in [('path_progress',1.),('requested_forward',RECIPE['requested_forward_rate_weight'])]:
        setattr(cfg.rewards,'h1_step270_'+name,RewardTermCfg(func=measured_rate,weight=weight,params={'name':name}))
    push=cfg.rewards.h1_scut_fudan_push_vz
    push.params=dict(original_func=push.func,original_params=dict(push.params));push.func=forward_takeoff_rate
    cfg._h1_step270_path_reward_recipe=dict(RECIPE)
    return cfg
