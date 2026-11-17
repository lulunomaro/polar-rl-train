"""E1-only zeroDR probe, restoring actual native nominal values; E0 untouched."""
import torch
from .scut_flat_env import tensor

def force_e1_zero_dr(env):
    dr=env.full_dr;ids=env.continuous_stair_mask.nonzero().flatten()
    env.reference_nominal_env_mask=dr.nominal_env_mask.clone()
    dr.nominal_env_mask=dr.nominal_env_mask|env.continuous_stair_mask
    dr.body_mass_scale[ids]=1.;dr.total_mass_scale[ids]=1.;dr.startup_com_delta[ids]=0.
    dr.startup_materials[ids.cpu()]=dr.materials[ids.cpu()]
    fr=dr.startup_joint_friction
    fr[ids,:,0]=dr.static_friction_default[ids]
    fr[ids,:,1]=(dr.dynamic_friction_default if dr.dynamic_friction_default is not None else dr.static_friction_default)[ids]
    fr[ids,:,2]=0. if dr.viscous_friction_default is None else dr.viscous_friction_default[ids]
    env.robot.write_joint_friction_coefficient_to_sim(joint_friction_coeff=fr[ids,:,0],joint_dynamic_friction_coeff=fr[ids,:,1],joint_viscous_friction_coeff=fr[ids,:,2],joint_ids=dr.joint_ids,env_ids=ids)
    dr._write_body_mass_inertia(ids);dr._write_startup_materials(ids)
    dr(env,ids);env._resample_delays(ids)
    env.velocity_push_time_left[ids]=1e9;env._external_timer[ids]=1e9
    env._external_force[ids]=0.;env._external_torque[ids]=0.;env._external_hold[ids]=0
    assert bool((dr.body_mass_scale[ids]==1).all()) and bool((dr.startup_com_delta[ids]==0).all())
    assert bool((env._action_delay_ticks[ids]==0).all())and bool((env._sensor_delay_ticks[ids]==0).all())
    return dict(E1_envs=len(ids),E1_DR_scale=0.,E1_observation_noise=False,E1_action_and_sensor_delay_ticks=0,E1_mass_gain_effort_material_friction_COM_native_nominal=True,E0_unchanged=True)
