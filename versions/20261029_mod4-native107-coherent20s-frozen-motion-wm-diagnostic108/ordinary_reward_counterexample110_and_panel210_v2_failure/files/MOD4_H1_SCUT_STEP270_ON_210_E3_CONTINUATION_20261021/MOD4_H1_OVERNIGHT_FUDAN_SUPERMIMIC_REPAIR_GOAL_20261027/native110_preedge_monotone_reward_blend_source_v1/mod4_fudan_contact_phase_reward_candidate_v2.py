"""MOD4 adaptation, not a claim of the upstream controller or a learned skill.

Instantaneous formulas/weights derive from yly-true/fudan_rl_wheel_leg@8204e853.
Upstream original BSD headers and complete source are preserved in pinned_exact_v2.
No force/action override, learner, model, physics, reset, or success gate lives here.
The native127 representation lacks prior-prior action, prior dq and nonwheel
contact forces. Those upstream terms are explicitly omitted, never forged zero.
"""
from dataclasses import dataclass
import torch

UPSTREAM_COMMIT='8204e853dfd2ed06d85a322e1a998c3d20a3be2c'
NATIVE_UNAVAILABLE_OR_STATEFUL_ORIGINAL_TERMS=(
    'encourage_jump_history_accumulator','collision_nonwheel_contact_force',
    'dof_acc_prior_velocity','action_smooth_prior_prior_action')

@dataclass(frozen=True)
class BoundOwnStepReward:
    extension_length_m: float
    tuck_length_m: float
    standing_body_height_m: float
    apex_body_height_m: float
    step_edge_x_m: float
    platform_end_x_m: float
    step_top_z_m: float
    goal_root_x_m: float
    approach_speed_m_s: float=.5
    control_dt_s: float=.01
    def __post_init__(self):
        assert 0<self.tuck_length_m<self.extension_length_m
        assert 0<self.standing_body_height_m<self.apex_body_height_m
        assert self.step_edge_x_m<self.goal_root_x_m<self.platform_end_x_m
        assert self.step_top_z_m>0 and self.control_dt_s==.01

def _weighted(terms,weights,clip,dt):
    assert set(terms)==set(weights)
    weighted={k:(terms[k]*weights[k]).clamp(-clip,clip)*dt for k in terms}
    return torch.stack(tuple(weighted.values()),-1).sum(-1),weighted

def instantaneous_jump_terms(m,p):
    """Original memory-free jump formulas; contact switches supplied per step."""
    flight=m['flight'];takeoff=m['takeoff'];L0=m['virtual_leg_length'];theta=m['virtual_leg_angle'];vz=m['world_vertical_velocity']
    e=(m['body_forward_velocity']-m['command_forward_velocity']).square()
    return dict(
        tracking_lin_vel=2*torch.exp(-e/.25),
        tracking_lin_vel_enhance=2*(torch.exp(-e/2.5)-1),
        tracking_ang_vel=torch.exp(-(m['body_yaw_velocity']-m['command_yaw_velocity']).square()/.25),
        flight=flight,
        encourage_jump_upward_only=.15*vz.clamp_min(0),
        base_height_flight=torch.exp(-(m['root_height']-p.apex_body_height_m).abs()*6)*flight,
        leg_tuck=torch.exp(-(L0-p.tuck_length_m).abs().sum(-1)*4)*flight,
        takeoff_extend=torch.exp(-(L0-p.extension_length_m).abs().sum(-1)*4)*takeoff,
        line_z=vz.clamp_min(0)*flight,
        pen_theta_no0=theta.square().sum(-1),
        action_rate=(m['action']-m['previous_action']).square().sum(-1),
        torques=m['actuated_torque'].square().sum(-1),
        orientation=m['projected_gravity'][...,:2].square().sum(-1),
        ang_vel_xy=m['body_angular_velocity'][...,:2].square().sum(-1),
        nominal_state=(theta[...,0]-theta[...,1]).square()+10*(L0[...,0]-L0[...,1]).square())

JUMP_WEIGHTS=dict(tracking_lin_vel=1.,tracking_lin_vel_enhance=1.,tracking_ang_vel=1.,flight=.15,
    encourage_jump_upward_only=1.,base_height_flight=6.,leg_tuck=1.7,takeoff_extend=.5,line_z=6.,
    pen_theta_no0=-2.,action_rate=-.04,torques=-.00005,orientation=-25.,ang_vel_xy=-.1,nominal_state=-1.)

def instantaneous_stair_recovery_terms(m,p):
    e=(m['body_forward_velocity']-m['command_forward_velocity']).square()
    z=(m['relative_base_height']-p.standing_body_height_m).square()
    return dict(tracking_lin_vel=torch.exp(-e/.25),tracking_lin_vel_enhance=torch.exp(-e/2.5)-1,
        tracking_ang_vel=torch.exp(-(m['body_yaw_velocity']-m['command_yaw_velocity']).square()/.25),
        base_height=1.5*torch.exp(-z*1000),base_height_enhance=torch.exp(-z/.01)-1,
        nominal_state=(m['virtual_leg_angle'][...,0]-m['virtual_leg_angle'][...,1]).square(),
        lin_vel_z=m['body_vertical_velocity'].square(),ang_vel_xy=m['body_angular_velocity'][...,:2].square().sum(-1),
        orientation=m['projected_gravity'][...,:2].square().sum(-1),dof_vel=m['actuated_leg_dq'].square().sum(-1),
        torques=m['actuated_torque'].square().sum(-1),action_rate=(m['action']-m['previous_action']).square().sum(-1),
        dof_pos_limits=m['actuated_soft_limit_violation'])

RECOVERY_WEIGHTS=dict(tracking_lin_vel=1.5,tracking_lin_vel_enhance=1.5,tracking_ang_vel=1.,base_height=1.,
    base_height_enhance=1.,nominal_state=-1.,lin_vel_z=-.1,ang_vel_xy=-.05,orientation=-10.,dof_vel=-.00005,
    torques=-.0001,action_rate=-.05,dof_pos_limits=-1.)

def contact_and_step_modes(wheel_low,wheel_high,force_z,root_x,root_vz,p):
    """Refresh from each actual/predicted state. These are planning surrogates."""
    support=torch.sigmoid((force_z-1.)/1.)
    flight=(1-support).prod(-1)
    ground=1-flight
    front_gap=p.step_edge_x_m-wheel_high[...,0].amax(-1)
    full_rear_gap=wheel_low[...,0].amin(-1)-p.step_edge_x_m
    far_gap=p.platform_end_x_m-wheel_high[...,0].amax(-1)
    footprint=torch.sigmoid(full_rear_gap/.02)*torch.sigmoid(far_gap/.02)
    top_height=torch.exp(-((wheel_low[...,2]-p.step_top_z_m)/.02).square().mean(-1))
    top_support=footprint*top_height*support.prod(-1)
    # Before the leading wheel edge crosses, approach gating is monotone.
    # Preserve a continuous decay after the edge rather than fading beforehand.
    post_edge_decay=torch.where(front_gap>=0,torch.ones_like(front_gap),
        torch.sigmoid((front_gap+.10)/.03)/torch.sigmoid(front_gap.new_tensor(.10/.03)))
    near=torch.sigmoid((.18-front_gap)/.03)*post_edge_decay
    jump=(near+flight).clamp(0,1)*(1-top_support)
    recovery=1-jump
    takeoff=ground*torch.sigmoid((root_vz-.15)/.05)
    return dict(flight=flight,takeoff=takeoff,jump=jump,recovery=recovery,top_support=top_support,
                footprint=footprint,full_rear_gap=full_rear_gap,
                command_forward_velocity=p.approach_speed_m_s*(1-top_support),
                support_surface_height=p.step_top_z_m*footprint)

def combined_reward(m,p,modes):
    """Native110 common baseline plus mode advantages; declared MOD4 adaptation."""
    j,jparts=_weighted(instantaneous_jump_terms(m,p),JUMP_WEIGHTS,2.5,p.control_dt_s)
    r,rparts=_weighted(instantaneous_stair_recovery_terms(m,p),RECOVERY_WEIGHTS,1.,p.control_dt_s)
    quiet=torch.exp(-m['root_planar_velocity'].square().sum(-1)/.15**2-m['body_angular_velocity'].square().sum(-1)/.3**2)
    placement=modes['top_support']*quiet
    # All six bonuses are nonnegative. The recovery-specific residual is
    # nonpositive: base_height is capped at dt, other two terms are costs.
    jump_bonus=sum(jparts[k] for k in
        ('flight','encourage_jump_upward_only','base_height_flight','leg_tuck','takeoff_extend','line_z'))
    recovery_extra=rparts['base_height']+rparts['base_height_enhance']+rparts['lin_vel_z']-p.control_dt_s
    mode_advantage=jump_bonus-recovery_extra
    # Equivalent to common + jump*bonus + recovery*extra + dt.
    # At jump=0 this is exactly the original recovery reward (no new alive offset).
    total=r+modes['jump']*mode_advantage+p.control_dt_s*placement
    assert torch.isfinite(total).all()
    return dict(total=total,jump_reward=j,recovery_reward=r,jump_terms=jparts,recovery_terms=rparts,
                own_top_support_quiet_placement=placement,unsupported_original_terms=NATIVE_UNAVAILABLE_OR_STATEFUL_ORIGINAL_TERMS,
                actual_success_not_inferred=True,nonnegative_jump_bonus=jump_bonus,
                nonpositive_recovery_extra=recovery_extra,mode_advantage=mode_advantage)
