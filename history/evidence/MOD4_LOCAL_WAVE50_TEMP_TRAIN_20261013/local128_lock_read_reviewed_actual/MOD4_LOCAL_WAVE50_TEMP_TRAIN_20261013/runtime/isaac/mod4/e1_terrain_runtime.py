"""Explicit low-speed rough intro task; unchanged observations and plant.

Ground is queried after actual physics before termination/reward; no scan is
secretly supplied to the policy. World-Z impulse is retained with its original
meaning. No pure/moving spin is requested on this new terrain lesson.
"""
import sys, torch
from pathlib import Path
A=Path(__file__).resolve().parent
sys.path.insert(0,str(A))
from e1_rough_recipe import make_terrain_cfg
from e1_full_pose_reset import query, full_reset
from chassis_pd_training_env import ChassisPDMod4Env
from directional_spin_runtime import DirectionalSpinCommand
import mod4_task as task
from isaaclab.managers import TerminationTermCfg
from e1_chunked_terrain import ChunkedTerrainImporter

class RoughStraightCommand(DirectionalSpinCommand):
    """20% stand, remaining uniform BODY vx[-.3,.3]; vy/yaw exactly zero."""
    def _resample_command(self, env_ids):
        super()._resample_command(env_ids)
        ids=torch.as_tensor(env_ids,device=self.device,dtype=torch.long)
        self.is_pure_spin[ids]=False
        self.is_moving_spin[ids]=False
        self.is_transition_spin[ids]=False
        self.signed_yaw[ids]=0.
        self.vel_command_b[ids,:]=0.
        self.vel_command_b[ids,0]=.6*torch.rand(len(ids),generator=self._mode_rng,device=self.device)-.3
        self.vel_command_b[self.is_standing_env,:]=0.

def boundary_timeout(env):
    # Explicit finite route boundary is a truncation, never hidden task success.
    xy=env.scene['robot'].data.root_pos_w[:,:2]
    anchor=getattr(env,'_rough_spawn_xy',env.scene.env_origins[:,:2])
    return (xy-anchor).abs().max(-1).values > 2.

def inactive_rolling(env, speed_scale=.15, yaw_min=3.5, support_weight=.25):
    cmd=env.command_manager.get_command('twist')
    if bool((cmd[:,2].abs()>1e-6).any()) or bool((cmd[:,1].abs()>1e-6).any()):
        raise RuntimeError('Intro command contract violated; flat rolling proxy not valid for terrain spin')
    # Original pure-yaw mask is false on EVERY new terrain command. Do not
    # instantiate a flat-circle contact proxy and claim terrain material slip.
    return torch.zeros(env.num_envs,device=env.device)

def configure_intro(cfg):
    terrain,recipe=make_terrain_cfg(cfg.scene.num_envs,seed=cfg.seed,profile='intro_v1')
    terrain.terrain_generator.num_rows=40
    terrain.terrain_generator.num_cols=40
    terrain.terrain_generator.use_cache=False
    # Rows cover the independent grid; use an explicitly easier first lesson.
    terrain.terrain_generator.difficulty_range=(0.,.25)
    # New explicit MOD4 gentle-entry geometry; upstream bytes remain untouched.
    terrains=terrain.terrain_generator.sub_terrains
    terrains['tiny_step'].bar_height_range=(.01,.02)
    terrains['slope_for_rm_high'].slope_range=(.03,.08)
    terrains['inv_slope_for_rm_low'].slope_range=(.02,.05)
    terrains['random_uniform_for_rm'].noise_range=(0.,.01)
    recipe['profile']='mod4_intro_gentle_v1'
    recipe['actual_geometry_ranges']=dict(tiny_bar_height_m=[.01,.02],positive_slope=[.03,.08],inverted_slope=[.02,.05],random_height_m=[0.,.01])
    recipe['original_upstream_ranges_retained_in_source_not_current_lesson']=True
    terrain.use_terrain_origins=False
    terrain.env_spacing=cfg.scene.env_spacing
    cfg.scene.ground=None
    terrain.class_type=ChunkedTerrainImporter
    cfg.scene.terrain=terrain
    # Reward/integral use get_net_contact_forces, independent of partner filters.
    # Disable unused partner matrix for the partitioned terrain, preserving net forces.
    cfg.scene.wheel_contact_scut.filter_prim_paths_expr=[]
    cfg.scene.wheel_contact_scut.max_contact_data_count_per_prim=64
    cfg.events.consistent_start.func=full_reset
    cfg.events.ground_track=None
    cfg.events.skill_cmds=None
    cfg.commands.twist.class_type=RoughStraightCommand
    cfg.commands.twist.rel_standing_envs=.2
    cfg.commands.twist.ranges.lin_vel_x=(-.3,.3)
    cfg.commands.twist.ranges.lin_vel_y=(0.,0.)
    cfg.commands.twist.ranges.ang_vel_z=(0.,0.)
    cfg.commands.twist.resampling_time_range=(12.,16.)
    cfg.curriculum.gyro_window=None
    cfg.rewards.spin_contact_consistency.func=inactive_rolling
    cfg.terminations.rough_route_boundary=TerminationTermCfg(func=boundary_timeout,time_out=True)
    cfg.sim.enable_scene_query_support=True
    cfg.sim.physx.enable_scene_query_support=True
    recipe.update(actual_layout_rows=40,actual_layout_columns=40,terrain_origins_used=False,env_spacing=cfg.scene.env_spacing,
        geometric_difficulty_envelope=[0.,.25],former_two_row_entry_envelope_preserved=False,allocation_review=True)
    return recipe

def refresh_ground(env):
    tick=int(env._sim_step_counter)
    if getattr(env,'_rough_query_tick',None)==tick:
        return env._mod4_ground_z
    robot=env.scene['robot'];ray=query(env)
    if not hasattr(env,'_rough_body_ids'):
        env._rough_body_ids=robot.find_bodies(['chassis','left_wheel','right_wheel'],preserve_order=True)[0]
    points=torch.cat((robot.data.root_pos_w[:,None,:],robot.data.body_link_pos_w[:,env._rough_body_ids]),dim=1).clone()
    points[:,:,2]+=1.
    out=ray.cast(points.contiguous(),4.)
    if not bool(out['hit'].all()) or not bool(torch.isfinite(out['normal']).all()) or not bool((out['normal'][...,2]>0).all()):
        raise RuntimeError('Actual root/body/wheel terrain query missing or invalid; no cached-floor fallback')
    env._mod4_ground_z=out['height'][:,0]
    env._rough_ground_normal=out['normal']
    env._rough_ground_heights=out['height']
    env._rough_query_tick=tick
    env._rough_query_updates=getattr(env,'_rough_query_updates',0)+1
    return env._mod4_ground_z

class E1ChassisTerrainEnv(ChassisPDMod4Env):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        termination=self.termination_manager.compute
        reward=self.reward_manager.compute
        def actual_termination(*a,**k):
            refresh_ground(self)
            self._rough_termination_query_tick=self._rough_query_tick
            result=termination(*a,**k)
            robot=self.scene['robot'];root=robot.data.root_state_w.clone();fresh=query(self).cast((root[:,:3,None].transpose(1,2)+torch.tensor([0.,0.,1.],device=self.device)).contiguous(),4.)
            if not bool(fresh['hit'].all()):raise RuntimeError('Independent E1 ground query missing')
            self._e1_pre_reset_frame=dict(root=root,q=robot.data.joint_pos.clone(),ground=self._rough_ground_heights.clone(),normal=self._rough_ground_normal.clone(),closure=torch.stack(list(task.closure_errors(self).values())).amax(0),mimic=torch.stack(list(task.mimic_errors(self).values())).amax(0),independent_ground_error=float((fresh['height'][:,0]-self._mod4_ground_z).abs().max()))
            return result
        def actual_reward(*a,**k):
            refresh_ground(self)
            self._rough_reward_query_tick=self._rough_query_tick
            value=reward(*a,**k)
            robot=self.scene['robot'];expected=torch.exp(-(robot.data.root_pos_w[:,2]-self._mod4_ground_z-task.height_cmd(self)).square()/task.SCUT_H_SIGMA)
            self._e1_height_formula_error=float((expected-task.height_track(self,sigma=task.SCUT_H_SIGMA)).abs().max())
            return value
        self.termination_manager.compute=actual_termination
        self.reward_manager.compute=actual_reward
        self._rough_query_tick=None

    def _reset_idx(self,env_ids):
        super()._reset_idx(env_ids)
        self._rough_query_tick=None

    def step(self,action):
        result=super().step(action)
        if self._rough_reward_query_tick != int(self._sim_step_counter):
            raise RuntimeError('Reward computed from stale terrain phase')
        if self._rough_termination_query_tick != self._rough_reward_query_tick:
            raise RuntimeError('Termination/reward terrain phases disagree')
        return result

def forward_readback(env):
    robot=env.scene['robot'];heading=robot.data.heading_w.torch
    grid=torch.cartesian_prod(torch.linspace(0.,.8,5,device=env.device),torch.tensor([-.25,0.,.25],device=env.device))
    starts=torch.empty((env.num_envs,len(grid),3),device=env.device)
    starts[:,:,0]=robot.data.root_pos_w[:,0,None]+torch.cos(heading)[:,None]*grid[None,:,0]-torch.sin(heading)[:,None]*grid[None,:,1]
    starts[:,:,1]=robot.data.root_pos_w[:,1,None]+torch.sin(heading)[:,None]*grid[None,:,0]+torch.cos(heading)[:,None]*grid[None,:,1]
    starts[:,:,2]=robot.data.root_pos_w[:,2,None]+1.
    out=query(env).cast(starts.contiguous(),4.)
    if not bool(out['hit'].all()):
        raise RuntimeError('Forward scan outside actual mesh; not filled with stale/default height')
    return out
