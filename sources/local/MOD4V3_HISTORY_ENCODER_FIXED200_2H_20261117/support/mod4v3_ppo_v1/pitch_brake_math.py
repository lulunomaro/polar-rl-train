"""Training-only pitch brake labels and exact heading-plane reward velocities."""
import torch

def heading_velocity(velocity_b,gravity_b):
    g=gravity_b/torch.linalg.vector_norm(gravity_b,dim=-1,keepdim=True).clamp_min(1e-6)
    forward=torch.zeros_like(g);forward[:,0]=1.
    forward=forward-g[:,0:1]*g
    forward=forward/torch.linalg.vector_norm(forward,dim=-1,keepdim=True).clamp_min(1e-6)
    lateral=torch.linalg.cross(-g,forward,dim=-1)
    return torch.stack(((velocity_b*forward).sum(-1),(velocity_b*lateral).sum(-1)),dim=-1)

def horizontal_reward_terms(velocity_b,gravity_b,command,cfg):
    xy=heading_velocity(velocity_b,gravity_b)
    stand=(command[:,0].abs()<float(cfg.stand_still_deadzone_threshold))if cfg.stand_still_deadzone_enabled else torch.zeros(len(command),dtype=torch.bool,device=command.device)
    target=torch.where(stand,torch.zeros_like(command[:,0]),command[:,0])
    error=target-xy[:,0]
    clipped=error.clamp(-float(cfg.lin_vel_err_constraint),float(cfg.lin_vel_err_constraint))if cfg.lin_vel_err_constraint is not None else error
    e2=clipped.square()
    return dict(track_lin_vel_xy=torch.exp(-e2/float(cfg.lin_vel_xy_sigma)),track_lin_vel_xy_soft=torch.exp(-e2/float(cfg.lin_vel_xy_soft_sigma)),track_lin_vel_xy_tight=torch.exp(-e2/float(cfg.lin_vel_xy_tight_sigma)),track_lin_vel_xy_square=(error*float(cfg.lin_vel_xy_square_sigma)).square(),track_lin_vel_xy_huge_gap=(e2>float(cfg.lin_vel_xy_torlarance_gap)).to(error.dtype),pen_high_speed=((target.abs()-xy[:,0].abs()).clamp_max(0)*float(cfg.high_speed_pen_sigma)).square(),stand_still_lin_vel=xy.abs().sum(-1)*stand)

def brake_hint_mask(age,speed,height,target):
    tick=torch.round(age/.02).long();phase=(tick-100).clamp_min(0).remainder(150)
    return target&(tick>=150)&(phase>=50)&(phase<55)&(speed.abs()>=2.)&(height>=.38)

def wheel_brake_targets(reference_actions,policy):
    # Published35D layout: wheel velocities at20:22, scale0.1; only causal current observations.
    wheel_mean=policy[:,20:22].mean(-1)
    valid=(wheel_mean.abs()>.5)&(policy[:,0].abs()<.1)&(policy[:,2].abs()<.1)
    target=reference_actions.detach().clone()
    target[:,4:6]=(target[:,4:6]+wheel_mean.sign().unsqueeze(-1)).clamp(-6,6)
    return target,valid
