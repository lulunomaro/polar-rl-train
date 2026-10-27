"""Future actual target read-only memory/drive admission. No SDK setters.

Inputs are the actual new environment and existing readonly tensor-view
adapter. This source has not run on a real SDK/scene/GPU. Tiny metadata fixtures
do not set any actual admission flags. Limits must come from the NEW asset.
"""
from gas400_source_patcher_v1 import GAS,QHI,require
def check_actual_new_gas(env,*,expected_joint_names,tensor,require_active_preload=False):
 import torch
 robot=env.scene['robot'];n=env.num_envs;names=list(robot.joint_names)
 require(names==list(expected_joint_names) and len(names)==30 and len(set(names))==30,'actual ordered30 unchanged')
 ids=[names.index(name) for name in GAS];adapter=env._spring_pressure
 require(adapter.ids==ids and list(adapter.names)==list(GAS),'actual gas actuator/runtime order')
 nominal=tensor(adapter.nominal);require(nominal.shape==(2,) and bool((nominal==2000).all()),'new nominal2000 required; old3500 source refused')
 require(env.physics_dt==.0025 and env.step_dt==.01 and env.cfg.decimation==4,'original physical clock')
 expected_k=adapter.component.actual_stiffness(nominal);expected_d=env._gas_damping.component.actual_damping_Ns_per_m()
 for label,actual,expected in [('buffer_k',robot.data.joint_stiffness,expected_k),('buffer_d',robot.data.joint_damping,expected_d)]:
  value=tensor(actual);require(value.shape==(n,30) and torch.equal(value[:,ids],expected),label+' new actual episode law mismatch')
 for label,actual,expected in [('implicit_k',robot.actuators['gas_springs'].stiffness,expected_k),('implicit_d',robot.actuators['gas_springs'].damping,expected_d)]:
  require(torch.equal(tensor(actual),expected),label+' new actual episode law mismatch')
 # Both root_view getters are already used by the old saved runtime/audit.
 # If their returned object lacks the existing readonly Tensor/.torch view,
 # reject and request actual static source/type evidence; never as_tensor/cast.
 drive_k=tensor(robot.root_view.get_dof_stiffnesses());drive_d=tensor(robot.root_view.get_dof_dampings());backend_limits=tensor(robot.root_view.get_dof_limits())
 require(torch.equal(drive_k[:,ids].to(expected_k.device),expected_k) and torch.equal(drive_d[:,ids].to(expected_d.device),expected_d),'actual PhysX new gas k/d backend disagreement')
 cap=tensor(robot.root_view.get_dof_max_forces());armature=tensor(robot.root_view.get_dof_armatures())
 require(bool((cap[:,ids]==2000.).all()) and bool((armature[:,ids]==.002).all()),'original gas force cap/armature changed')
 buffered_limits=tensor(robot.data.joint_pos_limits)
 require(buffered_limits.shape==(n,30,2) and backend_limits.shape==(n,30,2),'actual hard limit shape')
 expected=buffered_limits.new_tensor([-.0267046843609,QHI]).expand(n,2,2)
 require(torch.equal(buffered_limits[:,ids],expected) and torch.equal(backend_limits[:,ids].to(expected.device),expected),'actual hard200mm upper/original lower not installed; soft factor is insufficient')
 target=env.cfg.events.gas_spring_preload.params
 require(list(target['joint_names'])==list(GAS),'preload names changed')
 require(target['targets']==[.22063944109012937,.2206394410901294],'original preload q targets unchanged')
 actual_target=tensor(robot.data.joint_pos_target)[:,ids]
 require(bool((tensor(robot.data.joint_vel_target)[:,ids]==0).all()),'original gas target velocity0 required')
 active=torch.equal(actual_target,actual_target.new_tensor(target['targets']).expand(n,2))
 if require_active_preload:require(active,'original step preload has not yet become active')
 props=env.cfg.scene.robot.spawn.articulation_props
 require(env.cfg.sim.physics.solver_type==1 and props.solver_position_iteration_count==32 and props.solver_velocity_iteration_count==4,'original TGS32/4')
 return dict(actual_new_gas_parameters_passed=True,nominal_force_approximation_N=400.,nominal_stiffness_N_m=2000.,damping_engineering_only=True,hardware_force_curve_calibrated=False,
  actual_hardlimits_backend_and_buffer_passed=True,original_q_target_config_exact=True,actual_original_preload_active=active,
  preload_may_be_initial_zero_until_original_step_event=True,first_newPi_still_requires_original_preload_active_readback=True,
  not_same700N_physics=True,actual_new_method_source_CPU_resource_and_whole_model_qualification_independent=True)
