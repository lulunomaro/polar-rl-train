"""Bind the unchanged Fudan methods to a differentiable imagined measured frame.

This adapter supplies no contact or torque oracle. A learned own-plant model must
predict every required measurement; the old127-state WM alone is insufficient.
"""
from dataclasses import dataclass
import torch

POLICY_TO_REWARD_MOTOR=(0,1,4,2,3,5)

@dataclass
class RewardMemory:
    base_air_time:torch.Tensor
    last_contacts:torch.Tensor
    last_actions:torch.Tensor

def snapshot_actual(env):
    return RewardMemory(env.literal.base_air_time.detach().clone(),
        env.literal.last_contacts.detach().clone(),env.last_actions.detach().clone())

def imagined_step(frame,motor_actions,memory,*,literal_class,body_names,tick,reset_after=None):
    """Exactly one original19-method reward call, with isolated per-branch buffers.

    Input is the same measured-frame ABI as LiteralJump194. Values in imagination
    must come from the own-plant WM, differentiable ownFK or known commands. No
    future PhysX/depth data is accepted by this function as a hidden fallback.
    Hard contact/flight tests retain the upstream piecewise gradient semantics.
    """
    required={'commands','root_states','base_lin_vel','base_ang_vel','projected_gravity',
        'L0','theta0','torques','contact_forces'}
    if set(frame)!=required:raise ValueError('Complete predicted Fudan measurement frame required')
    n=motor_actions.shape[0]
    if motor_actions.shape!=(n,6)or memory.last_actions.shape!=(n,6,2):raise ValueError('Wrong six-motor action history')
    obj=literal_class(n,motor_actions.device,.02,body_names)
    # A new scratch buffer per imagined step avoids aliasing earlier autograd
    # nodes. These clones preserve gradients; the original methods are unedited.
    obj.base_air_time=memory.base_air_time.clone()
    obj.last_contacts=memory.last_contacts.clone()
    reward=obj.measured_step(dict(frame,actions=motor_actions,last_actions=memory.last_actions),tick).clone()
    history=torch.stack((motor_actions,memory.last_actions[:,:,0]),dim=-1)
    if reset_after is not None:
        if reset_after.shape!=(n,)or reset_after.dtype!=torch.bool:raise ValueError('Typed per-env reset mask required')
        # Original SDK reset clears history then restores the current action in
        # slot0. Original contact and base_air_time memory survives reset.
        history=torch.stack((motor_actions,torch.where(reset_after[:,None],torch.zeros_like(motor_actions),memory.last_actions[:,:,0])),dim=-1)
    return reward,RewardMemory(obj.base_air_time.clone(),obj.last_contacts.clone(),history)
