"""Fudan STAIRS3 curriculum/mesh and measured MOD4 fields; reward is external literal source.
Only standard reset placement changes to terrain origins. No mid-episode state/force writes.
"""
from types import SimpleNamespace
import hashlib, json, numpy as np, torch
from isaaclab.managers import RewardTermCfg, CurriculumTermCfg
from isaaclab.envs.mdp.commands.velocity_command import UniformVelocityCommand
from isaaclab.envs.mdp.commands.commands_cfg import UniformVelocityCommandCfg
from isaaclab.utils import configclass
from chassis_pd_training_env import ChassisPDMod4Env
from spring_nominal_sdk_readback import tensor
from literal_stairs3_original_config import OriginalStairs3Cfg,class_to_dict
from literal_stairs3_original_terrain import Terrain
from stairs3_measured_boundary188 import LiteralStairs3Kernel
import literal_stairs3_original_methods as original_module
import mod4_task as task

DATA={}

def yaw_apply(q,v):
    shape=v.shape;q=q.reshape(-1,4);v=v.reshape(-1,3)
    x,y,z,w=q.unbind(-1);angle=torch.atan2(2*(w*z+x*y),1-2*(y*y+z*z))
    c,s=angle.cos(),angle.sin();a,b,d=v.unbind(-1)
    return torch.stack((c*a-s*b,s*a+c*b,d),-1).reshape(shape)

original_module.quat_apply_yaw=yaw_apply

def spawn_original_stairs(prim_path,cfg,translation=None,orientation=None,**kwargs):
    from pxr import UsdGeom,UsdPhysics
    from isaaclab.sim import get_current_stage,define_collision_properties,bind_physics_material
    terrain_cfg=SimpleNamespace(**class_to_dict(OriginalStairs3Cfg.terrain))
    assert terrain_cfg.mesh_type=='trimesh' and terrain_cfg.terrain_proportions==[0.,0.,0.,.5,.5,0.]
    terrain=Terrain(terrain_cfg,DATA['num_envs'])
    vertices=np.asarray(terrain.vertices,dtype=np.float32).copy();faces=np.asarray(terrain.triangles,dtype=np.int32)
    vertices[:,:2]-=terrain_cfg.border_size
    assert vertices.ndim==2 and vertices.shape[1]==3 and faces.ndim==2 and faces.shape[1]==3
    assert np.isfinite(vertices).all()
    stage=get_current_stage();root=UsdGeom.Xform.Define(stage,prim_path).GetPrim()
    path=prim_path+'/original_Fudan_STAIRS3';mesh=UsdGeom.Mesh.Define(stage,path)
    mesh.CreatePointsAttr().Set(vertices.tolist());mesh.CreateFaceVertexCountsAttr().Set([3]*len(faces));mesh.CreateFaceVertexIndicesAttr().Set(faces.reshape(-1).tolist());mesh.CreateSubdivisionSchemeAttr().Set('none')
    UsdPhysics.CollisionAPI.Apply(mesh.GetPrim());UsdPhysics.MeshCollisionAPI.Apply(mesh.GetPrim()).CreateApproximationAttr().Set('none')
    if cfg.collision_props is not None:define_collision_properties(path,cfg.collision_props,stage=stage)
    if cfg.physics_material is not None:
        material=prim_path+'/physicsMaterial';cfg.physics_material.func(material,cfg.physics_material);bind_physics_material(path,material,stage=stage)
    DATA.update(terrain=terrain,geometry=dict(source='pinned plane/utils/terrain.py and selected 上台阶3 config',
        mesh_type='trimesh',heightfield_shape=list(terrain.height_field_raw.shape),vertices=len(vertices),triangles=len(faces),
        raw_heightfield_SHA=hashlib.sha256(terrain.height_field_raw.tobytes()).hexdigest(),
        terrain_rows=10,terrain_cols=20,up_down_stairs_proportion=[.5,.5],nominal_step_width=.7,
        nominal_step_height_formula='.05+.18*difficulty',physical_quantization_m=.005,
        highest_nominal_course_step_m=.212,highest_quantized_course_step_m=.21,
        original_ground_friction=.5,original_ground_restitution=.5,
        SDK_mapping='original Terrain class, raw SDK staircase algorithm and installed heightfield-to-triangle converter'))
    return root

def literal_reward_rate(env):
    if not getattr(env,'_stairs_ready',False):raise RuntimeError('Literal STAIRS3 actual state binding not ready')
    # Original compute_reward includes exactly one dt. RewardManager applies its
    # own dt; this boundary cancels only that outer SDK multiplication.
    return env.literal_reward_once()/env.step_dt

@configclass
class LiteralRewards:
    original_stairs3=RewardTermCfg(func=literal_reward_rate,weight=1.)

def terrain_levels(env,env_ids):
    if not getattr(env,'_stairs_ready',False):return 0.
    k=env.literal;k.root_states=tensor(env.scene['robot'].data.root_state_w)
    k._update_terrain_curriculum(env_ids)
    return k.terrain_levels.float().mean()

class OriginalStairs3Velocity(UniformVelocityCommand):
    def _resample_command(self,env_ids):
        super()._resample_command(env_ids)
        ids=torch.as_tensor(env_ids,device=self.device,dtype=torch.long)
        task.height_cmd(self._env)[ids,0]=torch.empty(len(ids),device=self.device).uniform_(.23,.33)

def configure(cfg):
    DATA['num_envs']=cfg.scene.num_envs
    cfg.scene.ground.spawn.func=spawn_original_stairs;cfg.scene.ground.init_state.pos=(0.,0.,0.)
    mat=cfg.scene.ground.spawn.physics_material
    mat.static_friction=.5;mat.dynamic_friction=.5;mat.restitution=.5
    cfg.commands.twist=UniformVelocityCommandCfg(asset_name='robot',class_type=OriginalStairs3Velocity,
        resampling_time_range=(5.,5.),heading_command=False,rel_standing_envs=0.,rel_heading_envs=0.,debug_vis=False,
        ranges=UniformVelocityCommandCfg.Ranges(lin_vel_x=(-2.3,2.3),lin_vel_y=(0.,0.),ang_vel_z=(-2.,2.),heading=(-3.14,3.14)))
    cfg.rewards=LiteralRewards()
    cfg.events.skill_cmds=None
    cfg.curriculum.gyro_window=None
    cfg.curriculum.stairs3_levels=CurriculumTermCfg(func=terrain_levels)
    cfg.terminations.mimic.params={**cfg.terminations.mimic.params,'threshold':.01}
    assert cfg.terminations.closure.params['threshold']==.002
    # Original SDK low-base/height terms must use the actual Fudan terrain.
    task.ground_height=lambda env:env.current_original_heights().mean(-1)
    return cfg

class Stairs3Mod4Env(ChassisPDMod4Env):
    def __init__(self,*args,**kwargs):
        self._stairs_ready=False
        super().__init__(*args,**kwargs)
        terrain=DATA['terrain'];n=self.num_envs;d=self.device
        k=self.literal=LiteralStairs3Kernel(n,d,self.step_dt)
        k.terrain=terrain;k.height_samples=torch.as_tensor(terrain.height_field_raw.astype(np.int32),device=d)
        k.terrain_origins=torch.tensor(terrain.env_origins,device=d,dtype=torch.float32)
        k.terrain_levels=torch.randint(0,6,(n,),device=d)
        k.terrain_types=torch.div(torch.arange(n,device=d),n/20,rounding_mode='floor').long().clamp_max(19)
        k.max_terrain_level=10;k.max_episode_length_s=20.;k.init_done=False
        k.env_origins=self.scene.env_origins
        k.env_origins.copy_(k.terrain_origins[k.terrain_levels,k.terrain_types])
        x=torch.tensor(k.cfg.terrain.measured_points_x,device=d);y=torch.tensor(k.cfg.terrain.measured_points_y,device=d)
        a,b=torch.meshgrid(x,y,indexing='ij');points=torch.stack((a.flatten(),b.flatten(),torch.zeros(a.numel(),device=d)),-1)
        k.height_points=points[None].expand(n,-1,-1).clone();k.num_height_points=points.shape[0]
        names=list(self.scene['robot'].joint_names)
        self.original6_names=['left_hip','left_crank','left_wheel_spin','right_hip','right_crank','right_wheel_spin']
        self.original6=[names.index(name) for name in self.original6_names]
        self.action_permutation=[1,0,4,3,2,5]
        robot=self.scene['robot'];limits=tensor(robot.root_view.get_dof_limits())[0,self.original6].to(d).clone()
        mid=limits[:,0]*.5+limits[:,1]*.5;half=limits[:,1]*.5-limits[:,0]*.5
        k.dof_pos_limits=torch.stack((mid-half*.97,mid+half*.97),-1)
        self.last_actions=torch.zeros(n,6,2,device=d)
        self.last_velocity=torch.zeros(n,6,device=d)
        self.last_root=tensor(robot.data.root_pos_w).clone()
        self.body_ids=[list(robot.body_names).index(name) for name in ('left_thigh','right_thigh','left_wheel','right_wheel')]
        self.empty_contact=torch.empty(n,0,3,device=d)
        self.empty_contact_indices=torch.empty(0,dtype=torch.long,device=d)
        self.literal_summary={};self._stairs_ready=True

    def current_original_heights(self):
        if not self._stairs_ready:
            # No reward is evaluated here. During initial manager construction,
            # no reset/physics has occurred; the actual terrain binding follows.
            raise RuntimeError('Terrain heights requested before actual STAIRS3 binding')
        r=self.scene['robot'];k=self.literal;k.root_states=tensor(r.data.root_state_w);k.base_quat=tensor(r.data.root_quat_w)
        return k._get_heights()

    def literal_reward_once(self):
        r=self.scene['robot'];k=self.literal;root=tensor(r.data.root_state_w)
        q=root[:,3:7];x,y,z,w=q.unbind(-1)
        R=torch.stack((torch.stack((1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)),-1),torch.stack((2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)),-1),torch.stack((2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)),-1)),-2)
        world_velocity=(root[:,:3]-self.last_root)/self.step_dt
        body_velocity=(R.transpose(1,2)@world_velocity[:,:,None]).squeeze(-1)
        pos=tensor(r.data.body_pos_w);delta=pos[:,self.body_ids[:2]]-pos[:,self.body_ids[2:]]
        body_delta=torch.einsum('bij,bkj->bki',R.transpose(1,2),delta)
        theta=torch.atan2(body_delta[:,:,0],body_delta[:,:,2])
        velocity=tensor(r.data.joint_vel)[:,self.original6]
        action=self.action_manager.action[:,self.action_permutation]
        command=self.command_manager.get_command('twist')
        commands=torch.stack((command[:,0],command[:,2],task.height_cmd(self)[:,0],torch.zeros(self.num_envs,device=self.device)),-1)
        frame=dict(commands=commands,base_lin_vel=body_velocity,base_ang_vel=tensor(r.data.root_ang_vel_b),
            projected_gravity=tensor(r.data.projected_gravity_b),base_height=(root[:,2,None]-self.current_original_heights()).mean(-1),
            torques=tensor(r.data.applied_torque)[:,self.original6],dof_vel=velocity,
            dof_acc=(self.last_velocity-velocity)/self.step_dt,dof_pos=tensor(r.data.joint_pos)[:,self.original6],dof_pos_limits=k.dof_pos_limits,
            actions=action,last_actions=self.last_actions,theta0=theta,contact_forces=self.empty_contact,penalised_contact_indices=self.empty_contact_indices)
        out=k.bind_and_compute_once(frame,int(self.common_step_counter))
        self.last_actions[:,:,1]=self.last_actions[:,:,0];self.last_actions[:,:,0]=action
        self.last_velocity.copy_(velocity);self.last_root.copy_(root[:,:3])
        return out

    def _reset_idx(self,ids):
        out=super()._reset_idx(ids)
        if self._stairs_ready:
            self.literal.reset_sums(ids)
            self.last_actions[ids]=0;self.last_velocity[ids]=0
            self.last_root[ids]=tensor(self.scene['robot'].data.root_pos_w)[ids]
            task.height_cmd(self)[ids,0]=torch.empty(len(ids),device=self.device).uniform_(.23,.33)
            self._mod4_mode_bit=torch.ones(self.num_envs,device=self.device,dtype=torch.long)
            self.literal.init_done=True
        return out
