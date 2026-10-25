"""Reward-only shaping for the human-authorized 270mm step task.

No action, command, physics, termination, success contract, RNG or optimizer
writes. The new cost reads only the already delayed leg target. Callback transport uses measured collider motion, not a ballistic
prediction or a root/COM proxy for wheel clearance. Constants are reward scales,
not new qualification, health or success thresholds.
"""
import torch

RECIPE = dict(version='step270_sampled_leg_excess_v8_reward_only',
    approach_event_scale=4., clearance_transport_event_scale=8.,
    forward_takeoff_event_scale=.25, actual_edge_event_scale=6.,
    actual_landing_event_scale=8., actual_stable_recovery_event_scale=16.,
    requested_forward_rate_weight=3., air_zero_torque_weight=.5,
    leg_tuck_weight=1.7, wheel_below_base_weight=.5,
    airborne_leg_target_overdrive_weight=-.05,
    clearance_target_m=.270, existing_forward_command_m_s=.8,
    path_start_x_m=-.10, path_target_x_m=.60,
    strict_goal_and_command_publisher_unchanged=True,
    signed_reverse_rate=True, measured_clearance_carry_gain=2.,
    clearance_carry_start_front_x_m=0., clearance_carry_full_front_x_m=.35,
    takeoff_gate_start_front_x_m=.10, takeoff_gate_full_front_x_m=.25,
    sampled_leg_action_excess_weight=-.002,
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


def sagittal_leg_lengths(*, delta_world, root_quaternion_xyzw):
    """Actual chassis-frame XZ extension, excluding fixed mounting width.

    Quaternion is the existing measured root orientation. No guessed lateral
    offset, target pose, joint command or actor-visible signal is introduced.
    """
    q=root_quaternion_xyzw[:,None,:3]
    qw=root_quaternion_xyzw[:,None,3:4]
    # Inverse rotate measured vectors: q^-1 v q, for source unit xyzw q.
    t=2.*torch.cross(q.expand_as(delta_world),delta_world,dim=-1)
    local=delta_world-qw*t+torch.cross(q.expand_as(delta_world),t,dim=-1)
    return local[:,:,(0,2)].norm(dim=-1)


def airborne_tuck_rate(env):
    from h1_takeoff_progress_environment_v2 import tensor
    p=env.h1_phase;r=env.scene['robot'];data=r.data
    root=tensor(data.root_state_w)
    ids=[r.body_names.index(x) for x in ('left_wheel','right_wheel')]
    delta=tensor(data.body_pos_w)[:,ids]-root[:,None,:3]
    current_clear=(p.last_measured['step_wheel_min'][:,:,2]>.005).all(-1)
    active=p.attempt & (p.air_ticks>0) & current_clear & ~p.landed & ~p.crossed.all(-1)
    # .22m is the measured sagittal extension target. MOD4's fixed
    # .2188m lateral wheel mounting distance is excluded from leg extension.
    # Existing phase mask, target scalar, gain and weight are retained.
    length=sagittal_leg_lengths(delta_world=delta,root_quaternion_xyzw=root[:,3:7])
    compact=torch.exp(-torch.sum(torch.abs(length-.22),dim=1)*4.)
    return active.to(root.dtype)*compact



def infeasible_leg_target_cost(*, raw_actions, scale, offset, lower, upper, diff_min, diff_max):
    # A reward reference only. Never replace or edit the applied action.
    # The measured delayed action term retains the original scale/default offset.
    target=raw_actions*scale+offset
    feasible=torch.maximum(torch.minimum(target,upper),lower)
    cranks=[]
    for crank,hip in ((0,1),(2,3)):
        lo=torch.maximum(lower[crank],feasible[:,hip]+diff_min)
        hi=torch.minimum(upper[crank],feasible[:,hip]+diff_max)
        cranks.append(torch.maximum(torch.minimum(feasible[:,crank],hi),lo))
    feasible=torch.stack((cranks[0],feasible[:,1],cranks[1],feasible[:,3]),dim=-1)
    return ((target-feasible)/scale).square().mean(-1)


def airborne_leg_target_overdrive_rate(env):
    from h1_takeoff_progress_environment_v2 import tensor
    from mod4_task import CONTRACT, LEG_ORDER
    p=env.h1_phase
    term=env.action_manager.get_term('legs')
    if tuple(term._joint_names)!=tuple(LEG_ORDER):
        raise RuntimeError('Unexpected leg action order')
    raw=tensor(term.raw_actions)
    lower=raw.new_tensor([CONTRACT['joints'][n]['limits_si'][0] for n in LEG_ORDER])
    upper=raw.new_tensor([CONTRACT['joints'][n]['limits_si'][1] for n in LEG_ORDER])
    # raw_actions is AFTER the original delay line; _offset is the actual
    # default pose captured by the installed SDK JointPositionAction.
    cost=infeasible_leg_target_cost(raw_actions=raw,scale=term._scale,offset=term._offset,
        lower=lower,upper=upper,diff_min=term.diff_min,diff_max=term.diff_max)
    current_clear=(p.last_measured['step_wheel_min'][:,:,2]>.005).all(-1)
    active=p.attempt & (p.air_ticks>0) & current_clear & ~p.landed & ~p.crossed.all(-1)
    return active.to(raw.dtype)*cost


def policy_sampled_leg_excess_cost(raw):
    # Original policy action units. Never edit the sampled or executed action.
    if raw.ndim!=2 or raw.shape[1]!=6 or not torch.isfinite(raw).all():
        raise RuntimeError('Expected finite original six-action policy sample')
    return (raw[:,:4].abs()-6.).clamp_min(0.).square().mean(-1)

def sampled_leg_action_excess_rate(env):
    # Initial source/SDK probes are outside an actor control step.
    if not getattr(env,'h1_stepping',False):
        return torch.zeros(env.num_envs,device=env.device)
    raw=getattr(env,'_h1_sampled_actions_for_reward',None)
    if raw is None or raw.shape[0]!=env.num_envs:
        raise RuntimeError('Missing current policy sample during H1 control reward')
    return policy_sampled_leg_excess_cost(raw)


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
    cfg.rewards.h1_step270_airborne_leg_target_overdrive=RewardTermCfg(
        func=airborne_leg_target_overdrive_rate,weight=RECIPE['airborne_leg_target_overdrive_weight'],params={})
    cfg.rewards.h1_step270_sampled_leg_action_excess=RewardTermCfg(func=sampled_leg_action_excess_rate,weight=RECIPE['sampled_leg_action_excess_weight'],params={})
    cfg._h1_step270_path_reward_recipe=dict(RECIPE)
    return cfg
