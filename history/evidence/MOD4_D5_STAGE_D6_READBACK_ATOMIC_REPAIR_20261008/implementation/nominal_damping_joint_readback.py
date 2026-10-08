"""Actual D5-scene joint parameter inspection; no parameter writes or learning."""
import torch
from spring_nominal_sdk_readback import tensor
def read_joint_parameters(env):
    r=env.scene['robot'];names=list(r.joint_names)
    gas=list(env.cfg.events.gas_spring_preload.params['joint_names']);ids=[names.index(n) for n in gas]
    drive=tensor(r.root_view.get_dof_dampings()).clone()
    buffer=tensor(r.data.joint_damping).clone()
    friction=tensor(r.root_view.get_dof_friction_properties()).clone()
    static=tensor(r.data.joint_friction_coeff).clone()
    dynamic=tensor(r.data.joint_dynamic_friction_coeff).clone()
    viscous=tensor(r.data.joint_viscous_friction_coeff).clone()
    model=tensor(r.actuators['gas_springs'].damping).clone()
    assert bool((drive[:,ids]==3).all()) and bool((buffer[:,ids]==3).all()) and bool((model==3).all())
    assert friction.shape==(env.num_envs,len(names),3)
    assert torch.equal(friction[:,:,0].to(static.device),static)
    assert torch.equal(friction[:,:,1].to(dynamic.device),dynamic)
    assert torch.equal(friction[:,:,2].to(viscous.device),viscous)
    assert all(torch.isfinite(x).all() for x in (drive,buffer,friction,static,dynamic,viscous,model))
    return dict(joint_names=names,gas_joint_names=gas,gas_damping_drive_buffer_implicit_model_exact=True,
        physx_damping=drive.cpu().tolist(),buffered_damping=buffer.cpu().tolist(),
        actuator_model_damping={k:dict(joint_indices=tensor(a.joint_indices).cpu().tolist() if torch.is_tensor(a.joint_indices) or hasattr(a.joint_indices,'torch') else list(a.joint_indices),values=tensor(a.damping).cpu().tolist()) for k,a in r.actuators.items()},
        friction_property_shape=list(friction.shape),static_dynamic_viscous_physx_buffer_exact=True,
        static_friction=static.cpu().tolist(),dynamic_friction=dynamic.cpu().tolist(),viscous_friction=viscous.cpu().tolist(),
        property_order_source='InstalledSDK write_joint_friction_data_to_buffer static,dynamic,viscous slots; actual buffer equality independently checked',
        PD_model_damping_not_identical_to_passive_physics_damping_claim=True,
        parameter_setter_calls=0,hardware_calibrated=False,D6_randomization_deployed=False)
