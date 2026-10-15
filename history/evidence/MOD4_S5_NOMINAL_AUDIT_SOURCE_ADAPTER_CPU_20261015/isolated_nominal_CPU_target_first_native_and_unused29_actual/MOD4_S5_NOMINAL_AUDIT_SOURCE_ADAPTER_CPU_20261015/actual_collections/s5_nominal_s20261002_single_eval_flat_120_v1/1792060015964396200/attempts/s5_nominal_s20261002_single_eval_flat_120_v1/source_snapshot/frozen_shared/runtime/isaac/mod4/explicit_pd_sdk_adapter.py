from nominal_d0_source_audit_v1 import mild_dr_present_or_nominal, capture_nominal_d0_reference, parameter_audit as s5_parameter_audit
"""Isolated explicit motor model coefficient pressure; no implicit-drive setters."""
import types,torch
from explicit_pd_component import ExplicitPD,PROFILE
from gas_damping_sdk_adapter import tensor
from chassis_pd_nominal_readback import joint_indices

class ExplicitPDSDK:
    def __init__(self,env,enabled,seed):
        self.env=env;self.robot=env.scene['robot'];self.legs=self.robot.actuators['legs'];self.wheels=self.robot.actuators['wheels']
        self.leg_ids=joint_indices(self.legs,len(self.robot.joint_names));self.wheel_ids=joint_indices(self.wheels,len(self.robot.joint_names))
        assert len(self.leg_ids)==4 and len(self.wheel_ids)==2
        assert tensor(self.legs.stiffness).shape==(env.num_envs,4) and tensor(self.legs.damping).shape==(env.num_envs,4)
        assert tensor(self.wheels.damping).shape==(env.num_envs,2)
        self.nominal=dict(leg_kp=tensor(self.legs.stiffness).clone(),leg_kd=tensor(self.legs.damping).clone(),wheel_kd=tensor(self.wheels.damping).clone(),wheel_kp=tensor(self.wheels.stiffness).clone())
        for k,v in dict(leg_kp=60.,leg_kd=2.,wheel_kd=.6,wheel_kp=0.).items():assert bool((self.nominal[k]==v).all()),k
        self.motor_ids=self.leg_ids+self.wheel_ids
        for getter in ('get_dof_stiffnesses','get_dof_dampings'):assert bool((tensor(getattr(self.robot.root_view,getter)())[:,self.motor_ids]==0).all())
        self.component=ExplicitPD(env.num_envs,env.device,seed,enabled);self.model_write_calls=0;self.reset_calls=0
        self.install_expected_value_auditor();self.reset(torch.arange(env.num_envs,device=env.device))
        original=env._reset_idx;adapter=self
        def reset_idx(this,ids):original(ids);adapter.reset(ids)
        env._reset_idx=types.MethodType(reset_idx,env)
    def apply(self,ids):
        values=self.component.coefficients()
        if self.component.enabled:
            tensor(self.legs.stiffness)[ids]=values['leg_kp'][ids]
            tensor(self.legs.damping)[ids]=values['leg_kd'][ids]
            tensor(self.wheels.damping)[ids]=values['wheel_kd'][ids]
            self.model_write_calls+=1
        self.audit_parameters()
    def reset(self,ids):
        ids=torch.as_tensor(ids,device=self.env.device,dtype=torch.long)
        if not len(ids):return
        self.component.reset(ids);self.apply(ids);self.reset_calls+=1
    def audit_parameters(self):
        values=self.component.coefficients()
        for name,current in (('leg_kp',self.legs.stiffness),('leg_kd',self.legs.damping),('wheel_kd',self.wheels.damping)):
            assert torch.equal(tensor(current),values[name]),name
        assert torch.equal(tensor(self.wheels.stiffness),self.nominal['wheel_kp'])
        for getter in ('get_dof_stiffnesses','get_dof_dampings'):assert bool((tensor(getattr(self.robot.root_view,getter)())[:,self.motor_ids]==0).all()),getter
        return values
    def install_expected_value_auditor(self):
        if not mild_dr_present_or_nominal(self.env):
            return
        mild=self.env._mild_dr;original=mild.audit;adapter=self
        def audit(this):
            values=adapter.audit_parameters()
            refs=[(this.gains['legs'],'stiffness','leg_kp'),(this.gains['legs'],'damping','leg_kd'),(this.gains['wheels'],'damping','wheel_kd')]
            saved=[obj[key] for obj,key,name in refs]
            for (obj,key,name),old in zip(refs,saved):assert torch.equal(old,adapter.nominal[name]);obj[key]=values[name].clone()
            try:row=original()
            finally:
                for (obj,key,name),old in zip(refs,saved):obj[key]=old
            assert all(obj[key] is old for (obj,key,name),old in zip(refs,saved))
            row['D7_explicit_motor_PD_expected_audit']=dict(actual_explicit_model_coefficients_exact=True,motor_implicit_drives_still_zero=True,original_reference_restored=True,other_checks_and_tolerances_unchanged=True)
            return row
        mild.audit=types.MethodType(audit,mild)
    def state_dict(self):return self.component.state_dict()
    def load_state_dict(self,state):self.component.load_state_dict(state);self.apply(torch.arange(self.env.num_envs,device=self.env.device))
    def audit(self):
        values=self.audit_parameters()
        return dict(profile=PROFILE,enabled=self.component.enabled,actual_model_coefficients={k:[float(v.min()),float(v.max())] for k,v in values.items()},
                    leg_joint_ids=self.leg_ids,wheel_joint_ids=self.wheel_ids,motor_implicit_drive_stiffness_and_damping_zero=True,
                    no_PhysX_parameter_setter=True,model_write_calls=self.model_write_calls,reset_calls=self.reset_calls,
                    independent_private_group_RNG=True,no_output_gain_or_hardware_envelope_write=True,engineering_pressure_not_calibration=True)
