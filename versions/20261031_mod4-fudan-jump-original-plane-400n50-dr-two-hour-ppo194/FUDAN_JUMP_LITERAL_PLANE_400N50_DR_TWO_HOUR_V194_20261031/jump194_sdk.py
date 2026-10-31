"""Own MOD4 measurements and original JUMP command/plane at the approved50Hz clock.
No reward formulas, constants, weights, clipping or flight mutations live here.
"""
import torch
from isaaclab.managers import RewardTermCfg
from isaaclab.sensors import ContactSensorCfg
from isaaclab.envs.mdp.commands.velocity_command import UniformVelocityCommand
from isaaclab.envs.mdp.commands.commands_cfg import UniformVelocityCommandCfg
from isaaclab.utils import configclass
from chassis_pd_training_env import ChassisPDMod4Env
from spring_nominal_sdk_readback import tensor
from jump194_boundary import LiteralJump194
from mod4_literal_math184_v2 import rotation_xyzw, own_virtual_legs, GEOMETRY_DEFINITION
import mod4_task as task

def reward_rate(env):
    assert env._jump_ready
    return env.original_jump_once()/env.step_dt  # cancels Lab's outer dt only

@configclass
class LiteralJumpRewards:
    original_jump=RewardTermCfg(func=reward_rate,weight=1.)

class OriginalJumpCommand(UniformVelocityCommand):
    def _resample_command(self,env_ids):
        super()._resample_command(env_ids)
        ids=torch.as_tensor(env_ids,device=self.device,dtype=torch.long)
        task.height_cmd(self._env)[ids,0]=torch.empty(len(ids),device=self.device).uniform_(.12,.15)
        self._env._mod4_mode_bit=torch.ones(self._env.num_envs,device=self.device,dtype=torch.long)

def configure(cfg):
    cfg.scene.env_spacing=3.
    material=cfg.scene.ground.spawn.physics_material
    material.static_friction=.5; material.dynamic_friction=.5; material.restitution=.5
    cfg.scene.full_robot_contact=ContactSensorCfg(prim_path='{ENV_REGEX_NS}/Robot/links/.*',update_period=0.,history_length=1,track_air_time=False,debug_vis=False)
    cfg.commands.twist=UniformVelocityCommandCfg(asset_name='robot',class_type=OriginalJumpCommand,
        resampling_time_range=(20.,20.),heading_command=False,rel_standing_envs=0.,rel_heading_envs=0.,debug_vis=False,
        ranges=UniformVelocityCommandCfg.Ranges(lin_vel_x=(-2.1,2.1),lin_vel_y=(0.,0.),ang_vel_z=(-2.,2.),heading=(-3.14,3.14)))
    cfg.rewards=LiteralJumpRewards()
    for name in ('skill_cmds','air_state','jump_state','landing_state','tunnel_state','route_spawn_term','route_cmd_term','skill_lanes'):
        if hasattr(cfg.events,name):setattr(cfg.events,name,None)
    cfg.curriculum.gyro_window=None
    cfg.terminations.mimic.params={**cfg.terminations.mimic.params,'threshold':.01}
    assert cfg.terminations.closure.params['threshold']==.002
    assert cfg.sim.dt==.0025 and cfg.decimation==8 and cfg.episode_length_s==20.
    task.ground_height=lambda env:torch.zeros(env.num_envs,device=env.device)
    return cfg

class JumpMod4Env(ChassisPDMod4Env):
    def __init__(self,*args,**kwargs):
        self._jump_ready=False
        super().__init__(*args,**kwargs)
        robot=self.scene['robot'];n=self.num_envs;d=self.device
        self.body_names194=list(robot.body_names)
        self.literal=LiteralJump194(n,d,self.step_dt,self.body_names194)
        self.contacts194=self.scene.sensors['full_robot_contact']
        names=list(self.contacts194.body_names)
        assert set(names)==set(self.body_names194) and len(names)==31
        self.contact_order194=[names.index(x) for x in self.body_names194]
        self.motor_names194=['left_crank','left_hip','left_wheel_spin','right_crank','right_hip','right_wheel_spin']
        self.motor_ids194=[list(robot.joint_names).index(x) for x in self.motor_names194]
        self.action_order194=[0,1,4,2,3,5]
        self.hip_anchors194=torch.tensor([task.CONTRACT['joints'][s+'_hip']['local_pos0'] for s in ('left','right')],device=d,dtype=torch.float32)
        self.last_root=tensor(robot.data.root_pos_w).clone()
        self.last_actions=torch.zeros(n,6,2,device=d)
        self.stats194=dict(completed_controls=0,flight_environment_controls=0,terminations={},maximum_root_height_m=0.)
        self._jump_ready=True

    def original_jump_once(self):
        r=self.scene['robot'];root=tensor(r.data.root_state_w)
        R=rotation_xyzw(root[:,3:7])
        body_velocity=(R.transpose(1,2)@((root[:,:3]-self.last_root)/self.step_dt)[:,:,None]).squeeze(-1)
        L0,theta0=own_virtual_legs(tensor(r.data.body_pos_w),R,self.body_names194,self.hip_anchors194)
        c=self.command_manager.get_command('twist')
        frame=dict(commands=torch.stack((c[:,0],c[:,2],task.height_cmd(self)[:,0],torch.zeros(self.num_envs,device=self.device)),-1),
            root_states=root,base_lin_vel=body_velocity,base_ang_vel=tensor(r.data.root_ang_vel_b),
            projected_gravity=tensor(r.data.projected_gravity_b),L0=L0,theta0=theta0,
            torques=tensor(r.data.applied_torque)[:,self.motor_ids194],actions=self.action_manager.action[:,self.action_order194],
            last_actions=self.last_actions,contact_forces=tensor(self.contacts194.data.net_forces_w)[:,self.contact_order194])
        out=self.literal.measured_step(frame,int(self.common_step_counter))
        self.last_actions[:,:,1]=self.last_actions[:,:,0]
        self.last_actions[:,:,0]=frame['actions']
        self.last_root.copy_(root[:,:3])
        self.stats194['completed_controls']+=1
        self.stats194['flight_environment_controls']+=int(self.literal.was_in_flight.sum())
        self.stats194['maximum_root_height_m']=max(self.stats194['maximum_root_height_m'],float(root[:,2].max()))
        for name in self.termination_manager.active_terms:
            count=int(self.termination_manager.get_term(name).sum())
            self.stats194['terminations'][name]=self.stats194['terminations'].get(name,0)+count
        return out

    def _reset_idx(self,ids):
        previous_action=self.last_actions[ids,:,0].clone() if self._jump_ready else None
        out=super()._reset_idx(ids)
        if self._jump_ready:
            self.literal.reset_sums(ids)
            self.last_actions[ids]=0
            # Pinned upstream writes last_actions[:,:,0]=actions AFTER reset_idx.
            self.last_actions[ids,:,0]=previous_action
            self.last_root[ids]=tensor(self.scene['robot'].data.root_pos_w)[ids]
            self._mod4_mode_bit=torch.ones(self.num_envs,device=self.device,dtype=torch.long)
        return out

    def binding_receipt(self):
        return dict(body_names=self.body_names194,contact_body_order=self.contact_order194,
            original_penalized_patterns=['lf','rf','base'],MOD4_equivalent_nonwheel_bodies=[x for x in self.body_names194 if x not in ('left_wheel','right_wheel')],
            geometry=GEOMETRY_DEFINITION,hip_anchors_m=self.hip_anchors194.tolist(),
            quaternion_order='actual installed SDK xyzw',base_linear_velocity='position finite difference rotated into currentBODY as pinned original',
            root_vertical_velocity='actual SDK WORLD root_state_w[:,9]',
            torque='SDK applied_torque named six efforts, not measured hardware torque',
            source_original_methods_unchanged=True,source_reward_dt_once=True,outer_Lab_dt_cancelled_only=True,
            command_vx=[-2.1,2.1],command_yaw=[-2.,2.],command_height=[.12,.15],resample_s=20.,
            original_contact_filter_and_base_air_time_preserved_across_reset=True,
            physical_guard_terminations_are_MOD4_not_Fudan_original_and_unchanged=True)
