"""First approved D6 subset: actual gas damping, independently of D5 stiffness.

No joint-friction, motor PD, preload, armature or force-cap writes. This
adapter has no learning/launch authority. SDK buffer/model/drive must agree.
"""
import types,torch
from gas_damping_factor import GasDamping,PROFILE

def tensor(value):
    if torch.is_tensor(value):return value
    if hasattr(value,'torch'):return value.torch
    import warp as wp
    return wp.to_torch(value)

class GasDampingSDK:
    def __init__(self,env,enabled,seed):
        self.env=env;self.robot=env.scene['robot'];self.actuator=self.robot.actuators['gas_springs']
        self.ids=[self.robot.joint_names.index(n) for n in env.cfg.events.gas_spring_preload.params['joint_names']]
        indices=self.actuator.joint_indices
        if torch.is_tensor(indices):indices=indices.detach().cpu().tolist()
        elif hasattr(indices,'numpy'):indices=indices.numpy().tolist()
        assert list(indices)==self.ids
        self.original_damping=tensor(self.robot.root_view.get_dof_dampings()).clone().to(env.device)
        assert bool((self.original_damping[:,self.ids]==3.).all())
        assert bool((tensor(self.robot.data.joint_damping)[:,self.ids]==3.).all())
        assert bool((tensor(self.actuator.damping)==3.).all())
        self.other_ids=[j for j in range(self.original_damping.shape[1]) if j not in self.ids]
        self.fixed={k:tensor(getattr(self.robot.root_view,k)()).clone().to(env.device)
                    for k in ('get_dof_max_forces','get_dof_armatures')}
        self.component=GasDamping(env.num_envs,env.device,seed,enabled)
        self.reset_calls=0;self.selected_reset_samples=0;self.setter_calls=0
        self.install_expected_value_auditors()
        self.reset(torch.arange(env.num_envs,device=env.device))
        original=env._reset_idx;adapter=self
        def reset_idx(this,ids):
            original(ids);adapter.reset(ids)
        env._reset_idx=types.MethodType(reset_idx,env)
    def expected_full_damping(self):
        full=self.original_damping.clone();full[:,self.ids]=self.component.actual_damping_Ns_per_m()
        return full
    def apply(self,ids):
        values=self.component.actual_damping_Ns_per_m()
        self.robot.write_joint_damping_to_sim_index(damping=values[ids].contiguous(),joint_ids=self.ids,env_ids=ids,full_data=False)
        tensor(self.actuator.damping)[ids]=values[ids]
        drive=tensor(self.robot.root_view.get_dof_dampings()).to(values.device)
        assert torch.equal(drive[ids][:,self.ids],values[ids])
        assert torch.equal(tensor(self.robot.data.joint_damping)[ids][:,self.ids],values[ids])
        assert torch.equal(tensor(self.actuator.damping)[ids],values[ids])
        assert torch.equal(drive[:,self.other_ids],self.original_damping[:,self.other_ids])
        for key,old in self.fixed.items():assert torch.equal(tensor(getattr(self.robot.root_view,key)()).to(old.device),old),key
        self.setter_calls+=1
    def reset(self,ids):
        ids=torch.as_tensor(ids,device=self.env.device,dtype=torch.long)
        if ids.numel()==0:return
        self.component.reset(ids);self.apply(ids)
        self.reset_calls+=1;self.selected_reset_samples+=int(ids.numel())
    def state_dict(self):return self.component.state_dict()
    def load_state_dict(self,state):
        self.component.load_state_dict(state)
        self.apply(torch.arange(self.env.num_envs,device=self.env.device))
    def install_expected_value_auditors(self):
        mild=self.env._mild_dr;original=mild.audit;adapter=self
        def audit(this):
            adapter.audit_parameters()
            nominal=this.gains['gas_springs']['damping']
            assert bool((nominal==3.).all()),'Original damping audit reference changed'
            this.gains['gas_springs']['damping']=adapter.component.actual_damping_Ns_per_m().clone()
            try:row=original()
            finally:this.gains['gas_springs']['damping']=nominal
            assert this.gains['gas_springs']['damping'] is nominal
            row['D6_actual_gas_damping_expected_value_audit']=dict(PhysX_buffer_implicit_model_exact=True,original_reference_restored=True,other_checks_and_tolerances_unchanged=True)
            return row
        mild.audit=types.MethodType(audit,mild)
        pressure=self.env._spring_pressure;original_spring=pressure.audit
        def spring_audit(this):
            adapter.audit_parameters();nominal=this.initial_other['damping']
            assert torch.equal(nominal.to(adapter.original_damping.device),adapter.original_damping)
            this.initial_other['damping']=adapter.expected_full_damping().to(nominal.device)
            try:row=original_spring()
            finally:this.initial_other['damping']=nominal
            row['D6_gas_damping_varies_separately']=True
            row['preload_damping_force_limit_armature_unchanged']=False
            row['preload_force_limit_armature_unchanged']=True
            return row
        pressure.audit=types.MethodType(spring_audit,pressure)
    def audit_parameters(self):
        expected=self.component.actual_damping_Ns_per_m();full=self.expected_full_damping()
        actual=tensor(self.robot.root_view.get_dof_dampings()).to(expected.device)
        assert torch.equal(actual,full)
        assert torch.equal(tensor(self.robot.data.joint_damping)[:,self.ids],expected)
        assert torch.equal(tensor(self.actuator.damping),expected)
        pressure=self.env._spring_pressure
        expected_k=pressure.component.actual_stiffness(pressure.nominal)
        assert torch.equal(tensor(self.robot.root_view.get_dof_stiffnesses()).to(expected.device)[:,self.ids],expected_k)
        assert torch.equal(tensor(self.robot.data.joint_stiffness)[:,self.ids],expected_k)
        assert torch.equal(tensor(pressure.actuator.stiffness),expected_k)
        for key,old in self.fixed.items():assert torch.equal(tensor(getattr(self.robot.root_view,key)()).to(old.device),old),key
        return expected
    def audit(self):
        expected=self.audit_parameters()
        return dict(profile=PROFILE,enabled=self.component.enabled,actual_PhysX_buffer_implicit_model_exact=True,
                    actual_damping_range_Ns_m=[float(expected.min()),float(expected.max())],factor_bounds=[.9,1.1],
                    reset_calls=self.reset_calls,selected_reset_samples=self.selected_reset_samples,setter_calls=self.setter_calls,
                    nominal_damping_Ns_m=3.,only_two_gas_damping_columns_changed=True,D5_stiffness_expected_state_exact=True,
                    motor_PD_passive_damping_friction_preload_force_cap_armature_unchanged=True,
                    independent_episode_two_RNG=True,engineering_pressure_not_hardware_calibration=True,
                    not_full_D6_joint_friction_coverage=True)

