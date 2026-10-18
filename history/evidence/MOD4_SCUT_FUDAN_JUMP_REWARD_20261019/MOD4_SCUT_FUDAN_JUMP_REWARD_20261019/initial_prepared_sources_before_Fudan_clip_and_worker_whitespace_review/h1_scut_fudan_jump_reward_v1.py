"""SCUT jump/airborne formulae + Fudan jump shaping, on MOD4 measured state.

SCUTRobotLab portions: Copyright (c) 2026 SCUTRobotLab, SPDX-License-Identifier: MIT.
Reference source snapshots, exact parameter attribution and differential checks
are in this experiment's source index. This module changes reward only.
"""
import torch

PROFILE = dict(
    version='scut_fudan_jump_reward_v1',
    tuck_leg_length_m=.22,
    extend_leg_length_m=.31, leg_exp_l1_gain=4.,
    zero_wheel_torque_sigma=1.5,
    weights={'push_vz':1., 'flight_vz':6., 'flight':.15,
             'leg_tuck':1.7, 'takeoff_extend':.5,
             'wheel_below_base':2., 'air_wheel_zero_torque':20.,
             'orientation':-25., 'angular_velocity_xy':-.1},
    geometry_adaptation='body-to-wheel 3D lengths from actual MOD4 link poses; tuck .22 SCUT default, extend .31 Fudan target',
    no_assist_force_or_air_reset_or_privileged_actor_observation=True,
)

def terms(*, active, airborne, supported, vz, leg_lengths, wheel_bottom_relative_z,
          wheel_torque, projected_gravity, angular_velocity_body):
    """Unweighted reward rates; caller supplies current measured states only."""
    af=active.float(); ff=(active & airborne).float()
    push=(active & ~airborne & supported)
    # SCUT takeoff_vel_z. Fudan encourage_jump's positive-vz component (.15)
    # is not stacked: this explicit push-only component has MOD4 weight 1.
    result={'push_vz':push.float()*torch.clamp(vz,min=0.),
            'flight_vz':ff*(vz>0).float()*vz,
            'flight':ff,
            # Fudan exp(-4*sum(abs(L0-target))) on MOD4 measured leg lengths.
            'leg_tuck':ff*torch.exp(-torch.sum(torch.abs(leg_lengths-PROFILE['tuck_leg_length_m']),dim=1)*4.),
            'takeoff_extend':(push & (vz>.15)).float()*torch.exp(-torch.sum(torch.abs(leg_lengths-.31),dim=1)*4.),
            # SCUT wheel_height_below_base_exp (target .22, sigma .01).
            'wheel_below_base':ff*torch.exp(-torch.square(wheel_bottom_relative_z+.22)/.01).mean(dim=1),
            # SCUT enabled airborne weight 20 and sigma 1.5.
            'air_wheel_zero_torque':ff*torch.exp(-torch.square(torch.abs(wheel_torque).max(dim=1).values/1.5)),
            # Fudan's actual orientation and body angular speed, not term-name inference.
            'orientation':af*torch.sum(torch.square(projected_gravity[:,:2]),dim=1),
            'angular_velocity_xy':af*torch.sum(torch.square(angular_velocity_body[:,:2]),dim=1)}
    return result

def _tensor(v):
    if hasattr(v,'torch'):return v.torch
    if torch.is_tensor(v):return v
    import warp as wp
    return wp.to_torch(v)

def _current(env):
    p=getattr(env,'h1_phase',None)
    if p is None:return {k:torch.zeros(env.num_envs,device=env.device) for k in PROFILE['weights']}
    # A single callback snapshot is shared by all reward terms in this control.
    cache=getattr(env,'_h1_scut_reward_cache',None);clock=int(env._sim_step_counter)
    if cache is not None and cache[0]==clock:return cache[1]
    r=env.scene['robot'];data=r.data;root=_tensor(data.root_state_w)
    ids=[r.body_names.index(x) for x in ('left_wheel','right_wheel')]
    wheelpos=_tensor(data.body_pos_w)[:,ids];delta=wheelpos-root[:,None,:3]
    wheel_ids=[r.joint_names.index(x) for x in ('left_wheel_spin','right_wheel_spin')]
    # Actual authored collider bottom, evaluated in the inherited physical callback.
    wc=env._h1_scut_last_wheel_clearance
    forces=env._integrated_contact.history[:,0].norm(dim=-1)
    airborne=(forces<=1.).all(-1)&(wc>0.).all(-1)
    active=p.attempt & (p.request_for_action | (p.launched & ~p.landed))
    # Exact original request/attempt/strict event truth and physical dynamics are untouched.
    rel_bottom=wc-root[:,2,None]
    v=terms(active=active,airborne=airborne,supported=(forces>1.).any(-1),
        vz=root[:,9],leg_lengths=delta.norm(dim=-1),wheel_bottom_relative_z=rel_bottom,
        wheel_torque=_tensor(data.applied_torque)[:,wheel_ids],
        projected_gravity=_tensor(data.projected_gravity_b),
        angular_velocity_body=_tensor(data.root_ang_vel_b))
    env._h1_scut_reward_cache=(clock,v)
    env._h1_scut_reward_last=dict(active=active,airborne=airborne,terms=v)
    return v

def measured_reward(env,name):return _current(env)[name]

def mask_replaced_jump_cost(env,original_func,original_params):
    value=original_func(env,**original_params);p=getattr(env,'h1_phase',None)
    if p is None:return value
    active=p.attempt & (p.request_for_action | (p.launched & ~p.landed))
    return torch.where(active,torch.zeros_like(value),value)

def configure(cfg):
    from isaaclab.managers import RewardTermCfg
    from h1_takeoff_progress_reward_v2 import configure as original
    original(cfg)
    # Replace the old orientation/legacy-rate costs only on this jump attempt.
    # Normal rows retain the exact original function, params, weight and value.
    replaced=[]
    for name in ('flat_orientation_y','flat_orientation_y_v','flat_orientation_x_v','ang_vel_xy'):
        t=getattr(cfg.rewards,name,None)
        if t is not None:
            replaced.append(dict(name=name,weight=t.weight,func=t.func.__module__+'.'+t.func.__qualname__))
            t.params=dict(original_func=t.func,original_params=dict(t.params));t.func=mask_replaced_jump_cost
    for name,weight in PROFILE['weights'].items():
        setattr(cfg.rewards,'h1_scut_fudan_'+name,RewardTermCfg(func=measured_reward,weight=weight,params={'name':name}))
    cfg._h1_scut_fudan_recipe=dict(PROFILE,replaced_original_jump_costs=replaced)
    return cfg

def loaded_recipe(env):
    """Read actual live RewardManager terms without altering a manager or trajectory."""
    rows=[]
    for name,cfg in zip(env.reward_manager._term_names,env.reward_manager._term_cfgs):
        if name.startswith('h1_scut_fudan_') or name in ('flat_orientation_y','flat_orientation_y_v','flat_orientation_x_v','ang_vel_xy'):
            rows.append(dict(name=name,weight=float(cfg.weight),func=cfg.func.__module__+'.'+cfg.func.__qualname__,params=repr(cfg.params)))
    assert {r['name'] for r in rows if r['name'].startswith('h1_scut_fudan_')}=={'h1_scut_fudan_'+k for k in PROFILE['weights']}
    return dict(profile=PROFILE,actual_loaded_terms=rows,no_new_actor_input=True)
