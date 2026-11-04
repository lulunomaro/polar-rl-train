"""D5 independent episode stiffness; inherit the original D1-D4 learning plant."""
import os,torch
from action_delay_training_env import ActionDelayMod4Env
from spring_pressure_audit_runtime import SpringPressureSDK
from spring_nominal_sdk_readback import tensor

PROFILE='gas_stiffness_independent_episode_090_110_v1'

class LearningSpringPressure(SpringPressureSDK):
    # The SDK fixture retains every reset row. Learning instead keeps bounded
    # counts and validates selected actual parameters without building a trace.
    def reset(self,ids,initial=False):
        ids=torch.as_tensor(ids,device=self.env.device,dtype=torch.long)
        if ids.numel()==0:return
        self.component.reset(ids);self.apply(ids)
        self.reset_count=getattr(self,'reset_count',0)+1
        self.selected_reset_count=getattr(self,'selected_reset_count',0)+ids.numel()
    def apply(self,ids):
        values=self.component.actual_stiffness(self.nominal)
        self.robot.write_joint_stiffness_to_sim_index(stiffness=values[ids].contiguous(),joint_ids=self.ids,env_ids=ids,full_data=False)
        tensor(self.actuator.stiffness)[ids]=values[ids]
        drive=tensor(self.robot.root_view.get_dof_stiffnesses())[:,self.ids].to(values.device)
        assert torch.equal(drive[ids],values[ids])
        assert torch.equal(tensor(self.robot.data.joint_stiffness)[ids][:,self.ids],values[ids])
        assert torch.equal(tensor(self.actuator.stiffness)[ids],values[ids])
        self.setter_calls+=1
    def audit(self):
        expected=self.component.actual_stiffness(self.nominal)
        drive=tensor(self.robot.root_view.get_dof_stiffnesses())[:,self.ids].to(expected.device)
        assert torch.equal(drive,expected) and torch.equal(tensor(self.robot.data.joint_stiffness)[:,self.ids],expected)
        assert torch.equal(tensor(self.actuator.stiffness),expected)
        for key,actual in [('damping',self.robot.root_view.get_dof_dampings()),('force_limit',self.robot.root_view.get_dof_max_forces()),('armature',self.robot.root_view.get_dof_armatures())]:
            assert torch.equal(tensor(actual),self.initial_other[key]),key
        return dict(profile=PROFILE,enabled=self.component.enabled,actual_PhysX_buffer_implicit_model_exact=True,
            actual_stiffness_range_N_m=[float(expected.min()),float(expected.max())],factor_bounds=[.9,1.1],
            reset_calls=self.reset_count,selected_reset_samples=self.selected_reset_count,
            preload_damping_force_limit_armature_unchanged=True,independent_episode_two_CUDA_RNG=True,
            engineering_pressure=True,hardware_force_stroke_calibration=False,actual_drive_or_constraint_force_measured=False)

class SpringPressureMod4Env(ActionDelayMod4Env):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        assert os.environ.get('RM_SPRING_PRESSURE_PROFILE')==PROFILE
        self._spring_pressure=LearningSpringPressure(self,True,int(self.cfg.seed))
    def spring_pressure_recipe(self):
        return dict(profile=PROFILE,nominal_stiffness_N_m=2000,independent_two_episode_factor_bounds=[.9,1.1],
            actual_stiffness_bounds_N_m=[1800,2200],preload_damping_force_limit_armature_unchanged=True,
            actor_critic_observations_unchanged=True,hardware_force_stroke_calibration=False,
            SDK_computed_applied_effort_is_approximate_not_measured_drive_force=True)
