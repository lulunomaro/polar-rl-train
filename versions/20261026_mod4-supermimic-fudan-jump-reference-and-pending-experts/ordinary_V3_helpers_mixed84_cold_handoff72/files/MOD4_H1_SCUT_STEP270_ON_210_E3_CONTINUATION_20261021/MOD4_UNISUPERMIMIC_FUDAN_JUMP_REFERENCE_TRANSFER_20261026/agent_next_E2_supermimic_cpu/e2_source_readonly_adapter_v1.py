"""Concrete readonly field mapping for the current original E2 source.

No hooks are installed, command updaters called, RNG touched, capture enabled,
or simulation run. Owner must supply actual ground height and joint-name proof.
"""
import torch
from e2_native_supermimic_candidate_v1 import (
    ActualSnapshot,CONTROL_DT,PHYSICS_DT,DECIMATION,FLAG_ORDER,KIND,pack_actual_root_xyzw,require,
)


def tensor(value):
    if torch.is_tensor(value):return value
    result=getattr(value,"torch",None)
    require(torch.is_tensor(result),"source readback must expose its actual torch tensor")
    return result


def actual_snapshot_from_source(env,ground_world_z,*,expected_joint_names,source_kind=KIND):
    require(source_kind==KIND,"actual E2 source kind required")
    require(float(env.step_dt)==CONTROL_DT and float(env.physics_dt)==PHYSICS_DT and int(env.cfg.decimation)==DECIMATION,
            "source E2 clock changed")
    robot=env.scene["robot"];names=list(robot.joint_names)
    require(len(names)==30 and len(set(names))==30 and names==list(expected_joint_names),"actual native joint-name readback mismatch")
    term=env.command_manager.get_term("twist")
    # Actual current source ActionsCfg terms are named legs/wheels; their delay
    # queues are pre-action state. Raw actionmanager input is not motor torque.
    legs=env.action_manager.get_term("legs");wheels=env.action_manager.get_term("wheels")
    require(hasattr(env,"_mod4_height_cmd"),"readonly reader will not lazily create a source height command")
    root=tensor(robot.data.root_state_w);n=len(root);dev=root.device
    vector=lambda value:torch.as_tensor(value,device=dev,dtype=root.dtype).expand(n).detach().clone()
    origins=tensor(env.scene.env_origins)
    return ActualSnapshot(
      packed73=pack_actual_root_xyzw(root,tensor(robot.data.joint_pos),tensor(robot.data.joint_vel),origins),
      mean_force_history=tensor(env._integrated_contact.history).detach().clone(),
      applied_torque30=tensor(robot.data.applied_torque).detach().clone(),
      command_body3=tensor(term.command).detach().clone(),
      flags5=torch.stack([tensor(getattr(term,k)).to(root.dtype) for k in FLAG_ORDER],-1).detach().clone(),
      world_direction=tensor(term.world_direction).detach().clone(),signed_yaw=tensor(term.signed_yaw).detach().clone(),
      phase_elapsed=tensor(term.phase_elapsed).detach().clone(),progress_goal=vector(term.progress_goal),
      body_speed_limit=vector(term.body_limit),height_command=tensor(env._mod4_height_cmd)[:,0].detach().clone(),
      manual_mode=vector(term.manual_evaluation_mode),command_time_left=tensor(term.time_left).detach().clone(),
      ground_local_z=tensor(ground_world_z).detach().clone()-origins[:,2],
      leg_delay_history=tensor(legs._hist).detach().clone(),leg_delay_lag=tensor(legs._lag).to(root.dtype).detach().clone(),
      leg_delay_age=tensor(legs._age).to(root.dtype).detach().clone(),wheel_delay_history=tensor(wheels._hist).detach().clone(),
      wheel_delay_lag=tensor(wheels._lag).to(root.dtype).detach().clone(),wheel_delay_age=tensor(wheels._age).to(root.dtype).detach().clone(),
      processed_targets6=torch.cat((tensor(legs.processed_actions),tensor(wheels.processed_actions)),-1).detach().clone(),
      source_stage="actual_current_pre_action",source_kind=source_kind).validate()


def actual_pre_reset_frame_from_source(env,*,expected_joint_names):
    """Use the source's existing E2H1FlatEnv pre-reset capture; never enable it here."""
    require(list(env.scene["robot"].joint_names)==list(expected_joint_names),"terminal native joint names changed")
    frame=env._own_flat_frame
    require(frame is not None,"owner must admit/enable its source pre-reset capture before any learning")
    packed=pack_actual_root_xyzw(tensor(frame["root13"]),tensor(frame["q30"]),tensor(frame["joint_vel"]),tensor(env.scene.env_origins))
    return dict(source_stage="termination_manager_compute_pre_reset",packed73=packed,
                action_manager_ingress6=tensor(frame["executed6"]).detach().clone(),
                original_field_alias="executed6 is source ActionManager ingress, not measured applied torque",
                applied_torque30=tensor(frame["applied_torque"]).detach().clone(),
                raw_physical_contact_source="existing source callback; not a declared reference")
