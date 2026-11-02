"""Isolated D5 stiffness-only engineering pressure and actual SDK readback.

This is not a learning entry or hardware calibration. The nominal law stays
3500N/m with original preload, damping, force cap and armature. Actual PhysX
and the implicit-actuator approximate effort model receive the same factor.
"""
import torch,types
from spring_pressure_component import SpringPressure
from spring_nominal_sdk_readback import NominalSpringReadback,tensor

class SpringPressureSDK:
    def __init__(self,env,enabled,seed):
        self.env=env;self.robot=env.scene['robot']
        self.names=list(env.cfg.events.gas_spring_preload.params['joint_names'])
        self.ids=[self.robot.joint_names.index(n) for n in self.names]
        self.actuator=self.robot.actuators['gas_springs']
        indices=self.actuator.joint_indices
        if torch.is_tensor(indices):indices=indices.detach().cpu().tolist()
        elif hasattr(indices,'numpy'):indices=indices.numpy().tolist()
        assert list(indices)==self.ids,'Gas actuator/model order must match actual articulation'
        self.nominal=torch.tensor([3500.,3500.],device=env.device)
        assert bool((tensor(self.robot.data.joint_stiffness)[:,self.ids]==self.nominal).all())
        assert bool((tensor(self.actuator.stiffness)==self.nominal).all())
        self.component=SpringPressure(env.num_envs,env.device,seed,enabled)
        self.reset_rows=[];self.setter_calls=0;self.stiffness_error=0.;self.roundtrip=None
        self.initial_other=self.other_parameters()
        self.reset(torch.arange(env.num_envs,device=env.device),initial=True)
        original=env._reset_idx;adapter=self
        def reset_idx(this,ids):
            original(ids)
            adapter.reset(ids)
        env._reset_idx=types.MethodType(reset_idx,env)
    def other_parameters(self):
        r=self.robot
        return dict(damping=tensor(r.root_view.get_dof_dampings()).clone(),
            force_limit=tensor(r.root_view.get_dof_max_forces()).clone(),
            armature=tensor(r.root_view.get_dof_armatures()).clone())
    def apply(self,ids):
        values=self.component.actual_stiffness(self.nominal)
        # The SDK parameter setter updates the articulation/PhysX buffers, but
        # does not update ImplicitActuator's approximate-effort model tensor.
        self.robot.write_joint_stiffness_to_sim_index(stiffness=values[ids].contiguous(),joint_ids=self.ids,env_ids=ids,full_data=False)
        tensor(self.actuator.stiffness)[ids]=values[ids]
        drive=tensor(self.robot.root_view.get_dof_stiffnesses())[:,self.ids].to(values.device)
        buffered=tensor(self.robot.data.joint_stiffness)[:,self.ids]
        estimate=tensor(self.actuator.stiffness)
        self.stiffness_error=max(self.stiffness_error,float((drive-values).abs().max()),float((buffered-values).abs().max()),float((estimate-values).abs().max()))
        assert self.stiffness_error==0
        assert all(torch.equal(v,self.initial_other[k]) for k,v in self.other_parameters().items())
        self.setter_calls+=1
    def reset(self,ids,initial=False):
        ids=torch.as_tensor(ids,device=self.env.device,dtype=torch.long)
        old=self.component.state_dict();oldk=tensor(self.robot.root_view.get_dof_stiffnesses()).clone()
        tick=int(self.env.common_step_counter);physical=int(self.env._sim_step_counter)
        cpu=torch.random.get_rng_state().clone();cuda=torch.cuda.get_rng_state(self.env.device).clone() if torch.cuda.is_initialized() else None
        self.component.reset(ids);self.apply(ids)
        selected=torch.zeros(self.env.num_envs,device=self.env.device,dtype=torch.bool);selected[ids]=True
        others=~selected
        assert torch.equal(self.component.factor[others],old['factor'][others]) and torch.equal(self.component.episode[others],old['episode'][others])
        current=tensor(self.robot.root_view.get_dof_stiffnesses());assert torch.equal(current[others.cpu()],oldk[others.cpu()])
        assert tick==self.env.common_step_counter and physical==self.env._sim_step_counter
        assert torch.equal(cpu,torch.random.get_rng_state())
        if cuda is not None:assert torch.equal(cuda,torch.cuda.get_rng_state(self.env.device))
        self.reset_rows.append(dict(ids=ids.cpu().tolist(),initial=initial,other_rows_parameter_state_exact=True,global_CPU_CUDA_RNG_untouched=True,global_physical_control_clock_unchanged=True))
    def state_dict(self):return self.component.state_dict()
    def load_state_dict(self,state):
        self.component.load_state_dict(state)
        self.apply(torch.arange(self.env.num_envs,device=self.env.device))
    def audit(self):
        return dict(enabled=self.component.enabled,engineering_pressure_not_hardware_calibration=True,
            stiffness_only_independent_two_episode_factors=[.9,1.1],actual_factor=self.component.factor.cpu().tolist(),
            episode=self.component.episode.cpu().tolist(),actual_stiffness_N_m=self.component.actual_stiffness(self.nominal).cpu().tolist(),
            actual_PhysX_buffer_and_implicit_model_error_N_m=self.stiffness_error,setter_calls=self.setter_calls,
            preload_damping_force_limit_armature_unchanged=True,reset_rows=self.reset_rows,CUDA_disk_roundtrip=self.roundtrip,
            actual_separate_drive_or_constraint_force_not_measured=True,no_PPO_or_hardware_calibration=True)

class PressureSpringReadback(NominalSpringReadback):
    def parameters(self):
        robot=self.robot;ids=self.ids
        values=dict(physx_stiffness_N_m=tensor(robot.root_view.get_dof_stiffnesses())[:,ids],
            physx_damping_N_s_m=tensor(robot.root_view.get_dof_dampings())[:,ids],
            physx_drive_effort_limit_N=tensor(robot.root_view.get_dof_max_forces())[:,ids],
            physx_armature=tensor(robot.root_view.get_dof_armatures())[:,ids],
            buffered_stiffness_N_m=tensor(robot.data.joint_stiffness)[:,ids],
            buffered_damping_N_s_m=tensor(robot.data.joint_damping)[:,ids])
        expected=self.env._spring_pressure.component.actual_stiffness(self.env._spring_pressure.nominal)
        assert torch.equal(values['physx_stiffness_N_m'].to(expected.device),expected)
        assert torch.equal(values['buffered_stiffness_N_m'],expected)
        assert bool((values['physx_damping_N_s_m']==3).all()) and bool((values['physx_drive_effort_limit_N']==2000).all())
        assert all(torch.isfinite(x).all() for x in values.values())
        return {k:x.cpu().tolist() for k,x in values.items()}
    def read_write(self):
        k=tensor(self.robot.data.joint_stiffness)[:,self.ids].clone();d=tensor(self.robot.data.joint_damping)[:,self.ids].clone()
        result=super().read_write()
        self.rows[-1].update(stiffness_N_m=k.cpu().tolist(),damping_N_s_m=d.cpu().tolist())
        return result
    def audit(self):
        row=super().audit()
        row.update(nominal_parameters_changed=False,no_D5_randomization_or_training=False,
            D5_stiffness_engineering_randomization=self.env._spring_pressure.component.enabled,no_D5_learning=True,
            no_D5_randomization_or_training_field_from_nominal_is_superseded=True)
        return row
