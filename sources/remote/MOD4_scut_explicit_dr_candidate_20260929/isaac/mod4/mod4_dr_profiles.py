"""Opt-in DR on top of a DR_OFF=1 baseline. Never changes reward or spring."""
import os,json,hashlib
from pathlib import Path
import torch

def profile():
    p=os.environ.get('MOD4_DR_PROFILE_PATH')
    if not p: raise RuntimeError('Explicit MOD4_DR_PROFILE_PATH is required in candidate workspace')
    d=json.loads(Path(p).read_text())
    if os.environ.get('RM_DR_OFF')!='1':raise RuntimeError('Legacy bundled DR must remain disabled')
    if set(d)-{'name','mass_scale','effort_scale','friction','description'}:raise ValueError('Unknown DR fields')
    for k in ['mass_scale','effort_scale']:
        lo,hi=d[k]
        if not (0.5<=lo<=hi<=1.5):raise ValueError('Invalid scale '+k)
    if d['friction'] is not None:
        f=d['friction']
        for k in ['static','dynamic']:
            lo,hi=f[k]
            if not 0<lo<=hi<=2:raise ValueError('Invalid friction')
        if f['dynamic'][1]>f['static'][0]:raise ValueError('Require dynamic maximum <= static minimum')
        if not 1<=f['buckets']<=64:raise ValueError('Invalid material bucket count')
        if not f.get('nominal_material_audit'):raise ValueError('Friction needs a nominal material audit file')
        audit=json.loads(Path(f['nominal_material_audit']).read_text())
        if not audit.get('approved_for_profile'):raise ValueError('Material audit not approved')
    return d

def _tensor(v):
    return v if torch.is_tensor(v) else v.torch

def mass_startup(env,env_ids=None):
    d=profile();r=env.scene['robot'];dev=env.device
    ids=torch.arange(env.num_envs,device=dev) if env_ids is None else env_ids.to(dev)
    if not hasattr(env,'_explicit_dr_base_mass'):
        env._explicit_dr_base_mass=_tensor(r.data.body_mass).detach().clone().to(dev)
        env._explicit_dr_base_inertia=_tensor(r.data.body_inertia).detach().clone().to(dev)
        env._explicit_dr_mass_scale=torch.ones(env.num_envs,device=dev)
    scale=torch.empty(len(ids),device=dev).uniform_(*d['mass_scale'])
    m=env._explicit_dr_base_mass[ids]*scale[:,None]
    inertia=env._explicit_dr_base_inertia[ids]*scale[:,None,None]
    if not torch.isfinite(m).all() or (m<=0).any():raise RuntimeError('Invalid mass')
    if not torch.isfinite(inertia).all():raise RuntimeError('Invalid inertia')
    # A single positive density scale preserves each original inertia's positive definiteness.
    bodyids=list(range(len(r.body_names)))
    r.set_masses_index(masses=m,body_ids=bodyids,env_ids=ids)
    r.set_inertias_index(inertias=inertia,body_ids=bodyids,env_ids=ids)
    env._explicit_dr_mass_scale[ids]=scale

def effort_reset(env,env_ids=None):
    d=profile()
    for group in ['legs','wheels']:
        env.scene['robot'].actuators[group].resample_episode_scale(env_ids,*d['effort_scale'])

def configure(cfg):
    from isaaclab.managers import EventTermCfg,SceneEntityCfg
    from isaaclab.envs.mdp import events
    d=profile()
    forbidden=['mass_inertia','base_com','wheel_friction','gas_spring_params','actuator_gains',
      'leg_joint_params','wheel_joint_params','leg_frictionloss','wheel_frictionloss',
      'push_velocity','push_wrench','leg_effort_scale','wheel_effort_scale','leg_effort_noise','wheel_effort_noise',
      'leg_encoder_bias','wheel_encoder_bias']
    active=[name for name in forbidden if getattr(cfg.events,name,None) is not None]
    if active:raise RuntimeError('Legacy randomization unexpectedly active: '+str(active))
    if d['mass_scale']!=[1.,1.]:cfg.events.explicit_dr_mass=EventTermCfg(func=mass_startup,mode='startup')
    if d['effort_scale']!=[1.,1.]:cfg.events.explicit_dr_effort=EventTermCfg(func=effort_reset,mode='reset')
    if d['friction'] is not None:
        f=d['friction']
        cfg.events.explicit_dr_material=EventTermCfg(func=events.randomize_rigid_body_material,mode='startup',params={
          'asset_cfg':SceneEntityCfg('robot',body_names=['left_wheel','right_wheel']),
          'static_friction_range':tuple(f['static']),'dynamic_friction_range':tuple(f['dynamic']),
          'restitution_range':(0.,0.),'num_buckets':f['buckets'],'make_consistent':True})

def audit(env):
    """Read back physical data and actuator scales; fail rather than claim a no-op succeeded."""
    d=profile();r=env.scene['robot'];actual=_tensor(r.data.body_mass).to(env.device)
    result={'profile':d,'backend':env.sim.physics_manager.__name__,'num_envs':env.num_envs,
      'total_mass_min_kg':float(actual.sum(1).min()),'total_mass_max_kg':float(actual.sum(1).max()),
      'event_terms':env.event_manager.active_terms,'legacy_DR_OFF':True,'spring_randomized':False}
    if d['mass_scale']!=[1.,1.]:
        expected=env._explicit_dr_base_mass*env._explicit_dr_mass_scale[:,None]
        result['mass_readback_max_abs_error']=float((actual-expected).abs().max())
        assert result['mass_readback_max_abs_error']<1e-4,'mass readback mismatch'
        scale=env._explicit_dr_mass_scale
        assert scale.min()>=d['mass_scale'][0]-1e-5 and scale.max()<=d['mass_scale'][1]+1e-5
        if env.num_envs>=16:assert scale.std()>1e-4,'mass DR is a no-op'
        actual_i=_tensor(r.data.body_inertia).to(env.device)
        expected_i=env._explicit_dr_base_inertia*scale[:,None,None]
        result['inertia_readback_max_abs_error']=float((actual_i-expected_i).abs().max())
        assert result['inertia_readback_max_abs_error']<1e-4,'inertia readback mismatch'
    result['actuator_scales']={}
    for name in ['legs','wheels']:
        a=r.actuators[name]
        scale=a.episode_scale
        result['actuator_scales'][name]={'min':float(scale.min()),'max':float(scale.max())}
        lo,hi=d['effort_scale']
        assert scale.min()>=lo-1e-5 and scale.max()<=hi+1e-5,'effort out of bounds'
        if lo!=hi and env.num_envs>=16:assert scale.std()>1e-4,'effort DR is a no-op'
    if d['friction'] is not None:
        raise RuntimeError('Friction profile blocked until shape-level material readback adapter and 20k bucket audit are implemented; do not claim success')
    result['parameters_pass']=True
    return result
