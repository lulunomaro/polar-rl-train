"""SCUT flat reward equations plus MOD4 closed-loop feasible reset adapter.

Reference: wheelbipe25_v3/env.py and env_cfg.py in the frozen upstream checkout.
The scalar called sigma in SCUT is the exponential DENOMINATOR, not std.
"""
import hashlib
import json
import os
from pathlib import Path
import torch


def exponential(error_squared, sigma):
    if sigma <= 0:
        raise ValueError('SCUT sigma must be positive')
    return torch.exp(-error_squared / sigma)


def forward_error(env, command_name='twist'):
    robot = env.scene['robot']
    # sin(pitch) = projected gravity x, independent of roll.
    cos_pitch = (1.0-robot.data.projected_gravity_b[:,0].square()).clamp_min(0).sqrt()
    return env.command_manager.get_command(command_name)[:,0] - robot.data.root_lin_vel_b[:,0]*cos_pitch


def linear_exp(env, command_name='twist', std=.25):
    # Keep the legacy parameter name for the Isaac manager interface only.
    return exponential(forward_error(env,command_name).square(),std)


def linear_square(env, command_name='twist', sigma=.25):
    return (sigma*forward_error(env,command_name)).square()


def linear_gap(env, command_name='twist', gap=.5):
    return (forward_error(env,command_name).square()>gap).float()


def yaw_exp(env, command_name='twist', std=.25):
    error=env.command_manager.get_command(command_name)[:,2]-env.scene['robot'].data.root_ang_vel_b[:,2]
    return exponential(error.square(),std)


def orientation(env, mode='pitch'):
    g=env.scene['robot'].data.projected_gravity_b
    if mode=='pitch':return (2*g[:,0]).square()
    c=env.command_manager.get_command('twist')[:,0]
    gain=2*torch.exp(-c.square())+2
    return (gain*g[:,0 if mode=='pitch_velocity' else 1]).square()


def wheel_positions_body(env):
    from isaaclab.utils.math import quat_apply_inverse
    robot=env.scene['robot']
    ids=[list(robot.body_names).index(n) for n in ['left_wheel','right_wheel']]
    delta=robot.data.body_pos_w[:,ids,:]-robot.data.root_pos_w[:,None,:]
    q=robot.data.root_quat_w[:,None,:].expand(-1,2,-1)
    return quat_apply_inverse(q.reshape(-1,4),delta.reshape(-1,3)).reshape(-1,2,3)


def no_fork(env, axis=0, threshold=.05):
    p=wheel_positions_body(env)
    return ((p[:,0,axis]-p[:,1,axis]).abs()>threshold).float()


def leg_gravity_alignment(env, sigma=.01):
    import mod4_task as task
    p=wheel_positions_body(env).clone()
    # Use MOD4 neutral wheel lateral offsets, never the other robot's 0.217 m.
    refs=p.new_tensor([task.CONTRACT['bodies'][n]['neutral_position_m'][1] for n in ['left_wheel','right_wheel']])
    p[:,:,1]-=refs
    directions=p/p.norm(dim=-1,keepdim=True).clamp_min(1e-6)
    g=env.scene['robot'].data.projected_gravity_b
    cos=(directions*g[:,None,:]).sum(-1).clamp(-1,1)
    return exponential((1-cos.square()).clamp_min(0).mean(1),sigma)


def wheel_power(env):
    robot=env.scene['robot']
    ids,_=robot.find_joints(['left_wheel_spin','right_wheel_spin'],preserve_order=True)
    return (robot.data.applied_torque[:,ids]*robot.data.joint_vel[:,ids]).clamp_min(0).sum(1)


def consistent_reset(env, env_ids):
    """Write a complete valid closed-loop pose AFTER ordinary root/reset events."""
    import mod4_task as task
    if task.TERRAIN!='flat':raise RuntimeError('rescue reset is flat-only')
    robot=env.scene['robot']
    ids=torch.arange(env.num_envs,device=env.device) if env_ids is None else env_ids
    if len(ids)==0:return
    bank=getattr(env,'_rescue_reset_bank',None)
    if bank is None:
        source=Path(__file__).with_name('reset_bank.json')
        raw=json.loads(source.read_text(encoding='utf8'))
        actual=hashlib.sha256((task.MOD4_ISAAC/'import_contract.json').read_bytes()).hexdigest()
        if actual!=raw['contract_sha256']:
            from gas400_reset_bank_exact_compatibility_v1 import require_exact_gas400_reset_bank
            env._gas400_reset_bank_compatibility_receipt = require_exact_gas400_reset_bank(source, task.MOD4_ISAAC/'import_contract.json', raw, actual_contract_SHA=actual)
        poses=[p for p in raw['poses'] if .24<=p['root_height_m']<=.272]
        if not poses:raise RuntimeError('empty feasible reset library')
        q=torch.tensor([[p['joint_pos'].get(n,0.) for n in robot.joint_names] for p in poses],device=env.device,dtype=torch.float32)
        h=torch.tensor([p['root_height_m'] for p in poses],device=env.device,dtype=torch.float32)
        bank=(q,h);env._rescue_reset_bank=bank
    qbank,hbank=bank
    pick=torch.randint(len(hbank),(len(ids),),device=env.device)
    q=qbank[pick];v=torch.zeros_like(q)
    robot.write_joint_state_to_sim(q,v,env_ids=ids)
    root=robot.data.root_state_w[ids].clone()
    root[:,2]=env.scene.env_origins[ids,2]+hbank[pick]
    root[:,7:]=0.0
    robot.write_root_state_to_sim(root,env_ids=ids)
    task.height_cmd(env)[ids]=float(os.environ.get('RM_NOMINAL_HEIGHT','.25'))
    # Diagnostic expectations are saved before any constraint solver projection.
    if not hasattr(env,'_rescue_reset_q'):
        env._rescue_reset_q=torch.zeros((env.num_envs,len(robot.joint_names)),device=env.device)
    env._rescue_reset_q[ids]=q
