"""Read actual gas-drive parameters and SDK approximate effort at each write.

The installed ImplicitActuator explicitly computes approximate effort; PhysX
does not expose the separate implicit drive force there. This reader never
equates that estimate with a measured drive/constraint/hardware force.
No action, parameter, random-number state or physical reset is written.
"""
import torch
import warp as wp

def tensor(value):
    if torch.is_tensor(value): return value
    if hasattr(value,'torch'): return value.torch
    return wp.to_torch(value)

class NominalSpringReadback:
    def __init__(self,env):
        self.env=env;self.robot=env.scene['robot'];self.names=list(env.cfg.events.gas_spring_preload.params['joint_names'])
        self.ids=[self.robot.joint_names.index(n) for n in self.names]
        self.targets=torch.tensor(env.cfg.events.gas_spring_preload.params['targets'],device=env.device,dtype=torch.float32)
        self.calls=0;self.rows=[];self.computed_error=0.;self.applied_error=0.;self.cache_position_error=0.
        self.preload_rows=0;self.neutral_warmup_rows=0
        self.initial=self.parameters();self.old_write=self.robot.write_data_to_sim
        self.robot.write_data_to_sim=self.read_write
    def parameters(self):
        robot=self.robot;ids=self.ids
        values=dict(physx_stiffness_N_m=tensor(robot.root_view.get_dof_stiffnesses())[:,ids],
            physx_damping_N_s_m=tensor(robot.root_view.get_dof_dampings())[:,ids],
            physx_drive_effort_limit_N=tensor(robot.root_view.get_dof_max_forces())[:,ids],
            physx_armature=tensor(robot.root_view.get_dof_armatures())[:,ids],
            buffered_stiffness_N_m=tensor(robot.data.joint_stiffness)[:,ids],
            buffered_damping_N_s_m=tensor(robot.data.joint_damping)[:,ids])
        assert all(torch.isfinite(x).all() for x in values.values())
        assert torch.equal(values['physx_stiffness_N_m'].to(self.env.device),values['buffered_stiffness_N_m'])
        assert torch.equal(values['physx_damping_N_s_m'].to(self.env.device),values['buffered_damping_N_s_m'])
        assert bool((values['physx_stiffness_N_m']==3500).all()) and bool((values['physx_damping_N_s_m']==3).all())
        assert bool((values['physx_drive_effort_limit_N']==2000).all())
        return {k:x.detach().cpu().tolist() for k,x in values.items()}
    def read_write(self):
        robot=self.robot;ids=self.ids;data=robot.data
        q=tensor(data.joint_pos)[:,ids].clone();qd=tensor(data.joint_vel)[:,ids].clone()
        target=tensor(data.joint_pos_target)[:,ids].clone();target_qd=tensor(data.joint_vel_target)[:,ids].clone()
        ff=tensor(data.joint_effort_target)[:,ids].clone()
        k=tensor(data.joint_stiffness)[:,ids].clone();d=tensor(data.joint_damping)[:,ids].clone()
        q_physx=tensor(robot.root_view.get_dof_positions())[:,ids].to(q.device)
        self.cache_position_error=max(self.cache_position_error,float((q_physx-q).abs().max()))
        elastic=k*(target-q);viscous=d*(target_qd-qd);estimated_total=elastic+viscous+ff
        ret=self.old_write()
        computed=tensor(data.computed_torque)[:,ids].clone();applied=tensor(data.applied_torque)[:,ids].clone()
        error=float((computed-estimated_total).abs().max());clipped=estimated_total.clamp(-2000,2000)
        self.computed_error=max(self.computed_error,error)
        self.applied_error=max(self.applied_error,float((applied-clipped).abs().max()))
        assert self.computed_error<=.001 and self.applied_error<=.001
        assert all(torch.isfinite(x).all() for x in (q,qd,target,target_qd,ff,elastic,viscous,computed,applied))
        active=(target-self.targets).abs().amax(-1)<=1e-7
        self.preload_rows+=int(active.sum());self.neutral_warmup_rows+=int((~active).sum())
        row=dict(physics_counter=int(self.env._sim_step_counter),control_tick=int(self.env.common_step_counter),
            q_m=q,qd_m_s=qd,actual_target_m=target,actual_target_qd_m_s=target_qd,feedforward_N=ff,
            elastic_estimate_N=elastic,viscous_estimate_N=viscous,SDK_computed_approximate_total_N=computed,
            SDK_clipped_approximate_total_N=applied,preload_active=active)
        self.rows.append({k:v.detach().cpu().tolist() if torch.is_tensor(v) else v for k,v in row.items()})
        self.calls+=1
        return ret
    def audit(self):
        return dict(joint_names=self.names,readback_calls=self.calls,initial_parameters=self.initial,final_parameters=self.parameters(),
            nominal_preload_target_m=self.targets.detach().cpu().tolist(),preload_active_environment_writes=self.preload_rows,
            initial_or_reset_neutral_warmup_environment_writes=self.neutral_warmup_rows,
            SDK_computed_approximate_formula_error_N=self.computed_error,SDK_clipped_approximate_formula_error_N=self.applied_error,
            cache_vs_direct_physx_joint_position_error_m=self.cache_position_error,
            per_physical_write=self.rows,gas_prismatic_effort_unit='N; coordinate m; velocity m/s',
            SDK_implicit_effort_is_approximate_not_separate_PhysX_drive_force=True,
            constraint_reaction_force_not_measured_or_equated=True,hardware_force_stroke_measurement=False,
            nominal_parameters_changed=False,PPO_updates=0,no_D5_randomization_or_training=True)
