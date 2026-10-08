"""Isolated D7 chassis COM subgroup; model coefficients and mass/inertia stay untouched."""
import types,torch
from chassis_com_component import ChassisCOM,PROFILE
from gas_damping_sdk_adapter import tensor

def transform_array(value):
    import warp as wp
    return wp.from_torch(value.contiguous(),dtype=wp.transformf)

class ChassisCOMSDK:
    def __init__(self,env,enabled,seed):
        self.env=env;self.robot=env.scene['robot'];names=list(self.robot.body_names)
        if names.count('chassis')!=1:raise ValueError('Exactly one actual chassis body required')
        self.body_id=names.index('chassis');self.original_pose=tensor(self.robot.root_view.get_coms()).clone().to(env.device)
        assert torch.equal(tensor(self.robot.data.body_com_pose_b).to(env.device),self.original_pose)
        self.orientation_after_parent_reset=self.original_pose[...,3:].clone()
        self.component=ChassisCOM(env.num_envs,env.device,seed,enabled)
        self.setter_calls=0;self.reset_calls=0;self.cache_invalidations=0
        self.install_expected_value_auditor()
        self.reset(torch.arange(env.num_envs,device=env.device))
        original=env._reset_idx;adapter=self
        def reset_idx(this,ids):original(ids);adapter.reset(ids)
        env._reset_idx=types.MethodType(reset_idx,env)
    def expected_full_pose(self):
        value=self.original_pose.clone();value[...,3:]=self.orientation_after_parent_reset
        value[:,self.body_id,:3]+=self.component.delta_m
        return value
    def invalidate_COM_dependent_cache(self):
        # Installed setter writes local pose buffer/PhysX but does not invalidate these derived caches.
        # Global time and physical state do not change; unchanged rows recompute identical values.
        names=('_body_com_pose_w','_root_com_pose_w','_body_link_vel_w','_root_link_vel_w',
               '_root_link_lin_vel_b','_root_link_ang_vel_b')
        for name in names:
            if hasattr(self.robot.data,name):getattr(self.robot.data,name).timestamp=-float('inf')
        self.cache_invalidations+=1
    def apply(self,ids):
        expected=self.expected_full_pose()
        if self.component.enabled:
            before_orientation=tensor(self.robot.root_view.get_coms()).to(expected.device)[...,3:].clone()
            self.robot.set_coms_index(coms=transform_array(expected[ids][:,[self.body_id],:].contiguous()),
                                      body_ids=[self.body_id],env_ids=ids,full_data=False)
            assert torch.equal(tensor(self.robot.root_view.get_coms()).to(expected.device)[...,3:],before_orientation)
            self.setter_calls+=1;self.invalidate_COM_dependent_cache()
        self.audit_parameters()
    def reset(self,ids):
        ids=torch.as_tensor(ids,device=self.env.device,dtype=torch.long)
        if not len(ids):return
        # D0 inertia reset may update PhysX principal-axis pose representation.
        # Preserve its CURRENT orientation; never restore a constructor-time principal-axis quaternion.
        current=tensor(self.robot.root_view.get_coms()).to(self.env.device)
        assert torch.equal(current[...,:3][:,[i for i in range(current.shape[1]) if i!=self.body_id]],
                           self.original_pose[...,:3][:,[i for i in range(current.shape[1]) if i!=self.body_id]])
        self.orientation_after_parent_reset[ids]=current[ids,...,3:]
        self.component.reset(ids);self.apply(ids);self.reset_calls+=1
    def audit_parameters(self):
        expected=self.expected_full_pose()
        actual=tensor(self.robot.root_view.get_coms()).to(expected.device)
        buffered=tensor(self.robot.data.body_com_pose_b).to(expected.device)
        assert torch.equal(actual,expected) and torch.equal(buffered,expected)
        assert torch.equal(actual[...,3:],self.orientation_after_parent_reset),'Current D0 principal-axis orientation must stay exact'
        other=[i for i in range(expected.shape[1]) if i!=self.body_id]
        assert torch.equal(actual[:,other,:3],self.original_pose[:,other,:3]),'Other body COM translation must stay exact'
        return actual
    def install_expected_value_auditor(self):
        mild=self.env._mild_dr;original=mild.audit;adapter=self
        def audit(this):
            adapter.audit_parameters();nominal=this.com
            assert torch.equal(nominal.to(adapter.original_pose.device),adapter.original_pose[...,:3])
            this.com=adapter.expected_full_pose()[...,:3].clone()
            try:row=original()
            finally:this.com=nominal
            assert this.com is nominal
            row['D7_actual_chassis_only_COM_expected_audit']=dict(actual_PhysX_buffer_exact=True,
                original_nominal_reference_restored=True,all_other_parameter_checks_tolerances_unchanged=True)
            return row
        mild.audit=types.MethodType(audit,mild)
    def state_dict(self):return self.component.state_dict()
    def load_state_dict(self,state):
        self.component.load_state_dict(state)
        self.orientation_after_parent_reset=tensor(self.robot.root_view.get_coms()).to(self.env.device)[...,3:].clone()
        self.apply(torch.arange(self.env.num_envs,device=self.env.device))
    def audit(self):
        self.audit_parameters();mass=tensor(self.robot.root_view.get_masses()).to(self.env.device)
        fraction=mass[:,self.body_id]/mass.sum(1)
        return dict(profile=PROFILE,enabled=self.component.enabled,chassis_body_index=self.body_id,chassis_body_name='chassis',
                    delta_range_m=[float(self.component.delta_m.min()),float(self.component.delta_m.max())],
                    actual_PhysX_local_pose_and_buffer_exact=True,other_body_COM_quaternions_unchanged=True,
                    no_mass_inertia_or_PD_parameter_setters=True,COM_frame='body link-local meters; quaternion xyzw retained',
                    chassis_mass_fraction=fraction.cpu().tolist(),whole_robot_COM_delta_is_mass_weighted_not_5mm=True,
                    private_axis_RNG=True,reset_calls=self.reset_calls,setter_calls=self.setter_calls,
                    COM_dependent_cache_invalidations=self.cache_invalidations,hardware_calibrated=False)
