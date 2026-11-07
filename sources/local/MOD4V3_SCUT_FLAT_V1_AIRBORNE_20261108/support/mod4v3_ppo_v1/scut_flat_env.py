"""Direct nominal task using the released USD and the pinned standing rewards."""
import math
from types import SimpleNamespace
import torch
import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg
from isaaclab.envs import DirectRLEnv, DirectRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import ContactSensorCfg, RayCasterCfg, patterns
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.utils.configclass import configclass
from isaaclab.sim import SimulationCfg
from isaaclab_physx.physics import PhysxCfg
from mod4v1_scut.config import observation_component
from mod4v1_scut.math_ops import detect_sdk_quaternion_order, euler_xyz_from_quat, wrap_to_pi
from semantics import ScutRobotView
from kinematics import mechanical_delta_bounds
from .scut_flat_rewards import make_reward_class
from .scut_mild_dr import MildDRv3

SCUT_ORDER = ['left_front1_joint', 'left_rear1_joint', 'right_front1_joint', 'right_rear1_joint', 'left_wheel_joint', 'right_wheel_joint']


def tensor(x):
    if torch.is_tensor(x): return x
    if hasattr(x,'torch'): return x.torch
    import warp as wp
    return wp.to_torch(x)


class TorchData:
    """Unpack SDK Warp proxies before querying scalar/packed tensor shapes."""
    def __init__(self,data):self.data=data
    def __getattr__(self,name):return tensor(getattr(self.data,name))


def configuration(meta,bank,n,seed,terrain_selection='flat'):
    rt = meta['runtime']; order = rt['policy_action_order']
    passive = [name for name in rt['initial_joint_positions']
               if name not in order and name not in meta['gas_springs']]
    dynamics = meta['dynamics']
    active = ImplicitActuatorCfg(joint_names_expr=order,stiffness=0.,damping=0.,
        effort_limit_sim=1e6,velocity_limit_sim=1000.,
        armature={name:dynamics[name]['armature'] for name in order})
    robot = ArticulationCfg(prim_path='{ENV_REGEX_NS}/Robot',
        spawn=sim_utils.UsdFileCfg(usd_path=meta['package']+'/assets/robot_physx.usda',
            copy_from_source=False,activate_contact_sensors=True,
            rigid_props=sim_utils.RigidBodyPropertiesCfg(disable_gravity=False,
                max_depenetration_velocity=1.,linear_damping=0.,angular_damping=0.,
                enable_gyroscopic_forces=True),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(enabled_self_collisions=True,
                solver_position_iteration_count=32,solver_velocity_iteration_count=4)),
        init_state=ArticulationCfg.InitialStateCfg(pos=(0.,0.,.337742301121),
            joint_pos=rt['initial_joint_positions'],joint_vel={'.*':0.}),
        soft_joint_pos_limit_factor=1.,actuators=dict(active=active,
            passive=ImplicitActuatorCfg(joint_names_expr=passive,stiffness=0.,
                damping={name:dynamics[name]['damping'] for name in passive},
                armature={name:dynamics[name]['armature'] for name in passive},
                effort_limit_sim=1e6,velocity_limit_sim=1000.),
            gas=ImplicitActuatorCfg(joint_names_expr=list(meta['gas_springs']),
                stiffness=2000.,damping=3.,armature=.002,
                effort_limit_sim=2000.,velocity_limit_sim=1000.)))
    if terrain_selection != 'flat':
        raise ValueError('This run is flat-only, got terrain selection: '+terrain_selection)
    from flat_terrain import generator
    terrain_generator = generator()
    # Distribute isolated envs within the selected tiles before physics loads.
    # The earlier V41 overlap caused huge broadphase allocations.
    from isaaclab.terrains import TerrainImporter
    original_origins=TerrainImporter._compute_env_origins_curriculum
    def origins(self,num_envs,terrain_origins):
        result=original_origins(self,num_envs,terrain_origins)
        tile=self.terrain_levels*terrain_origins.shape[1]+self.terrain_types
        for value in tile.unique():
            ids=(tile==value).nonzero().flatten();k=torch.arange(len(ids),device=self.device)
            if num_envs <= 4096:
                result[ids,0]+=-2.7+(k%10)*.6
                result[ids,1]+=-2.7+torch.div(k,10,rounding_mode='floor')*.6
            else:
                columns=math.ceil(math.sqrt(len(ids)))
                rows=math.ceil(len(ids)/columns)
                width,length=terrain_generator.size
                result[ids,0]+=(k%columns-(columns-1)/2.)*((width-1.)/columns)
                result[ids,1]+=(torch.div(k,columns,rounding_mode='floor')-(rows-1)/2.)*((length-1.)/rows)
        return result
    TerrainImporter._compute_env_origins_curriculum=origins
    if terrain_selection == 'flat':
        terrain_generator.use_cache = True
    else:
        # Roots share terrain tiles but have distinct XY positions. Their local
        # support heights must come from this newly selected collision mesh.
        original_mesh=TerrainImporter.import_mesh
        def remember_mesh(self,name,mesh):
            self._standing_terrain_mesh=mesh
            return original_mesh(self,name,mesh)
        TerrainImporter.import_mesh=remember_mesh
        def supported_origins(self,num_envs,terrain_origins):
            result=origins(self,num_envs,terrain_origins)
            from isaaclab.utils.warp import convert_to_warp_mesh,raycast_mesh
            mesh=self._standing_terrain_mesh
            wp_mesh=convert_to_warp_mesh(mesh.vertices,mesh.faces,self.device)
            starts=result.clone();starts[:,2]+=5.
            directions=torch.zeros_like(starts);directions[:,2]=-1.
            hit=raycast_mesh(starts,directions,wp_mesh,max_dist=10.)[0]
            if not bool(torch.isfinite(hit).all()):
                raise ValueError('Official rough terrain spawn ray missed')
            result[:,2]=hit[:,2]
            return result
        TerrainImporter._compute_env_origins_curriculum=supported_origins
    @configclass
    class Scene(InteractiveSceneCfg):
        robot = None
        terrain = TerrainImporterCfg(prim_path='/World/ground',terrain_type='generator',
            terrain_generator=terrain_generator,max_init_terrain_level=None,collision_group=-1,
            physics_material=sim_utils.RigidBodyMaterialCfg(static_friction=.9,dynamic_friction=.9,
                restitution=0.,friction_combine_mode='multiply',restitution_combine_mode='multiply'))
        contacts = ContactSensorCfg(prim_path='{ENV_REGEX_NS}/Robot/links/.*',
            update_period=.005,history_length=3,track_air_time=False)
        ground = RayCasterCfg(prim_path='{ENV_REGEX_NS}/Robot/links/base_link',
            offset=RayCasterCfg.OffsetCfg(pos=(0.,0.,5.)),ray_alignment='yaw',
            pattern_cfg=patterns.GridPatternCfg(resolution=.1,size=(.2,.2)),
            mesh_prim_paths=['/World/ground/terrain'],max_distance=20.,update_period=.02)
    scene = Scene(num_envs=n,env_spacing=8.,replicate_physics=True,filter_collisions=True)
    scene.robot = robot
    @configclass
    class Cfg(DirectRLEnvCfg):
        decimation = 8
        episode_length_s = 20.
        action_space = 6
        observation_space = 35
        state_space = 78
        sim = SimulationCfg(dt=.0025,render_interval=8,device='cuda:0')
        scene = None
    cfg = Cfg();cfg.scene=scene;cfg.seed=seed
    cfg.sim.physics=PhysxCfg(solver_type=1,max_position_iteration_count=32,max_velocity_iteration_count=4)
    # 20k official rough measured up to 696124 patches; the SDK default
    # 163840 overflowed. Keep the other PhysX capacities unchanged.
    if n >= 20000:
        cfg.sim.physics.gpu_max_rigid_patch_count = 2**18
    return cfg


class ScutFlatEnv(DirectRLEnv):
    def __init__(self,cfg,meta,bank):
        self.meta,self.bank = meta,bank
        self.reward = None
        super().__init__(cfg)
        self.robot = self.scene['robot']
        self.order = SCUT_ORDER
        self.active_ids = [self.robot.joint_names.index(n) for n in self.order]
        self.gas_ids = [self.robot.joint_names.index(n) for n in meta['gas_springs']]
        self.qorder = detect_sdk_quaternion_order(self.robot.data,tensor)[0]
        raw=SimpleNamespace(data=TorchData(self.robot.data),joint_names=self.robot.joint_names,
                            body_names=self.robot.body_names)
        self.view = ScutRobotView(raw,meta['package'],
            quaternion_order=self.qorder,position_basis='usd_absolute')
        self.reward = self._make_reward(meta)
        self.sensor_ids = [self.scene['contacts'].body_names.index(n) for n in self.robot.body_names]
        self.actions = torch.zeros(self.num_envs,6,device=self.device)
        self.targets = self.robot.data.default_joint_pos[:,self.active_ids].clone()
        self.torque = torch.zeros_like(self.targets)
        self.command = torch.zeros(self.num_envs,3,device=self.device)
        self.height = torch.full((self.num_envs,),.25,device=self.device)
        self.command_timer = torch.zeros(self.num_envs,device=self.device)
        self.command_vx = (-2.7,2.7)
        self.command_wz = (-2.0*math.pi,2.0*math.pi)
        self.heading_range = (-math.pi,math.pi)
        self.heading_control_stiffness = 5.0
        self.command_resample = (5.0,15.0)
        self.standing_fraction = 0.10
        self.heading_fraction = 0.50
        self.heading_env = torch.zeros(self.num_envs,dtype=torch.bool,device=self.device)
        self.standing_env = torch.zeros_like(self.heading_env)
        self.heading_target = torch.zeros(self.num_envs,device=self.device)
        self.height_range = (0.20,0.42)
        self.closure_error = torch.zeros(self.num_envs,device=self.device)
        self.mimic_error = self.closure_error.clone()
        self.numeric = torch.zeros(self.num_envs,dtype=torch.bool,device=self.device)
        self.closure_reset = self.numeric.clone(); self.mimic_reset=self.numeric.clone()
        self.done_totals = dict(episodes=0,closure=0,mimic=0,numerical=0,timeout=0)
        self._bank_q = torch.tensor(bank['positions'],device=self.device)
        self._bank_h = torch.tensor(bank['heights'],device=self.device)
        self._bank_ids = [bank['names'].index(n) for n in self.robot.joint_names]
        self.reset_generator = torch.Generator(device=self.device).manual_seed(int(cfg.seed)+179)
        self.delta_bounds = [mechanical_delta_bounds(side) for side in ('left','right')]
        self.terminal_observations = None
        self.snapshots = None
        self.sample = None
        self.gas_targets = torch.full((self.num_envs,2),.1706394410901294,device=self.device)
        self.mild_dr = MildDRv3(self)

    def _make_reward(self,meta):
        return make_reward_class(meta)(self.view,self.num_envs,self.device)

    def _setup_scene(self):
        # InteractiveScene constructs the declared articulation, terrain and sensors.
        pass

    def _height_observation(self):
        height=self.reward._get_observed_height()
        if not (self.reward._use_absolute_height() or self.reward._use_leg_length_height()):
            height=height-self.reward.ground_z_est
        return height

    def _sample_command(self,ids):
        ids=torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten()
        n=int(ids.numel())
        if n==0:return
        vx=torch.empty(n,device=self.device).uniform_(*self.command_vx)
        standing=torch.rand(n,device=self.device)<self.standing_fraction
        heading=(torch.rand(n,device=self.device)<self.heading_fraction)&(~standing)
        wz=torch.empty(n,device=self.device).uniform_(*self.command_wz)
        heading_target=torch.empty(n,device=self.device).uniform_(*self.heading_range)
        vx[standing]=0.0
        wz[standing]=0.0
        self.command[ids,0]=vx
        self.command[ids,1]=0.0
        self.command[ids,2]=wz
        self.heading_env[ids]=heading
        self.standing_env[ids]=standing
        self.heading_target[ids]=heading_target
        self.height[ids]=torch.empty(n,device=self.device).uniform_(*self.height_range)
        self.command_timer[ids]=torch.empty(n,device=self.device).uniform_(*self.command_resample)

    def _pre_physics_step(self,actions):
        yaw=euler_xyz_from_quat(self.view.data.root_quat_w)[2]
        heading_error=wrap_to_pi(self.heading_target-yaw)
        heading_wz=(self.heading_control_stiffness*heading_error).clamp(*self.command_wz)
        self.command[self.heading_env,2]=heading_wz[self.heading_env]
        self.command_timer -= 0.02
        expired=self.command_timer<=0
        if bool(expired.any()):
            self._sample_command(expired.nonzero().flatten())
        self.actions.copy_(actions)
        self.targets[:,:4] = self.robot.data.default_joint_pos[:,self.active_ids[:4]] + .5*actions[:,:4]
        current = tensor(self.robot.data.joint_pos)[:,self.active_ids]
        for side,front,rear in ((0,0,1),(1,2,3)):
            low,high = self.delta_bounds[side]
            delta = self.targets[:,front]-self.targets[:,rear]
            delta += ((current[:,front]-current[:,rear]-delta)/(2*math.pi)).round()*(2*math.pi)
            delta.clamp_(low,high)
            hip = self.targets[:,rear]
            hip += ((current[:,rear]-hip)/(2*math.pi)).round()*(2*math.pi)
            self.targets[:,front] = hip+delta
        self.targets[:,4:] = 10.*actions[:,4:]

    def _apply_action(self):
        # Same 100 Hz explicit PD feedback and DC voltage envelopes as V40.
        if (self._sim_step_counter-1)%4 == 0:
            q = tensor(self.robot.data.joint_pos)[:,self.active_ids]
            v = tensor(self.robot.data.joint_vel)[:,self.active_ids]
            raw = torch.cat((60.*(self.targets[:,:4]-q[:,:4])*self._leg_gain_scale-2.*v[:,:4],
                             .6*(self.targets[:,4:]-v[:,4:])*self._wheel_gain_scale),dim=-1)
            stall = raw.new_tensor([53.333333333333336]*4+[28.18525375641699]*2)
            no_load = raw.new_tensor([16.755160819145562]*4+[55.35573187814664]*2)
            peak = raw.new_tensor([40.]*4+[5.775909774436091]*2)
            upper = (stall*(1-v/no_load)).clamp_min(0).minimum(peak)
            lower = (-stall*(1+v/no_load)).clamp_max(0).maximum(-peak)
            self.torque.copy_(raw.minimum(upper).maximum(lower))
        self.robot.set_joint_effort_target(self.torque,joint_ids=self.active_ids)
        self.robot.set_joint_position_target(self.gas_targets,joint_ids=self.gas_ids)

    def prepare_endpoint(self):
        r = self.reward
        contacts = tensor(self.scene['contacts'].data.net_forces_w_history)[:,:,self.sensor_ids]
        hits = tensor(self.scene['ground'].data.ray_hits_w)
        finite = torch.isfinite(hits[...,2]);z=hits[...,2].masked_fill(~finite,0.)
        ground = torch.where(finite.any(-1),z.sum(-1)/finite.sum(-1).clamp_min(1),self.scene.env_origins[:,2])
        wheels = self.view.data.body_pos_w[:,r._wheel_link_idx]
        r.begin(self.actions,self.command,self.height,self.reset_terminated,self.numeric,
            self.episode_length_buf,contacts,ground,ground[:,None].expand(-1,2),
            wheels,wheels,wheels,wheels)

    def _get_dones(self):
        if self.sample is not None:
            self.sample.run()
        self.prepare_endpoint()
        r = self.reward; d = self.view.data
        self.numeric.copy_(~torch.isfinite(d.joint_pos).all(-1)|~torch.isfinite(d.joint_vel).all(-1)|
            ~torch.isfinite(d.root_state_w).all(-1))
        r._numerical_safety_reset_buf.copy_(self.numeric)
        terminated,timeout = r._get_dones()
        self.closure_reset.copy_(self.closure_error>.002)
        self.mimic_reset.copy_(self.mimic_error>.01)
        terminated |= self.closure_reset|self.mimic_reset|self.numeric
        timeout &= ~terminated
        # Wire the final termination into the reward at the same pre-reset state.
        r.reset_terminated.copy_(terminated)
        return terminated,timeout

    def _get_rewards(self):
        value = self.reward.compute()
        self.terminal_observations = self._encode()
        d = self.view.data
        self.snapshots = dict(root_pos=d.root_pos_w.clone(),root_quat=d.root_quat_w.clone(),
            body_pos=d.body_pos_w.clone(),body_quat=d.body_quat_w.clone(),
            velocity=d.root_lin_vel_b.clone(),command=self.command.clone(),height=self.height.clone(),
            height_obs=self._height_observation().clone(),
            length=self.reward.length.clone(),theta=self.reward.theta.clone(),
            closure=self.closure_error.clone(),mimic=self.mimic_error.clone(),
            terminated=self.reset_terminated.clone(),timeout=self.reset_time_outs.clone())
        self.reward.finish_observation()
        return value

    def _encode(self):
        r=self.reward;d=self.view.data
        q=(d.joint_pos-d.default_joint_pos)[:,r._actuate_idx]
        # The established policy leaves wheel position slots at zero.
        q=q.clone();q[:,4:]=0.
        v=d.joint_vel[:,r._actuate_idx]
        def encode(blocks,stream):
            return torch.cat([observation_component(r.cfg,k,x,stream) for k,x in blocks.items()],-1)
        command=getattr(r,'command',self.command);height_cmd=getattr(r,'height_cmd',self.height)
        blocks=dict(command=command,height_cmd=height_cmd[:,None],root_ang_vel_b=d.root_ang_vel_b,
            projected_gravity_b=d.projected_gravity_b,joint_pos=q,joint_vel_leg=v[:,:4],
            joint_vel_wheel=v[:,4:],actions=self.actions)
        if getattr(r.cfg,'enable_state_machines',False):
            mode=r._get_ctrl_mode_obs_raw()
        else:
            mode=torch.zeros((self.num_envs,7),device=self.device);mode[:,0]=1.0
        policy=encode(dict(**blocks,ctrl_mode_obs=mode),'policy')
        critic=encode(dict(**blocks,root_lin_vel_b=d.root_lin_vel_b,
            obs_height=self._height_observation()[:,None],ctrl_mode_obs=mode),'critic')
        _,_,_,wheel_v,_=r._get_root_quat_inv_and_wheel_pos_b()
        contacts=(r._get_wheel_contact_force_peaks(r.contact_sensor.data.net_forces_w_history)>
            r.cfg.desired_contact_force_threshold).float()
        zeros=q.new_zeros;ones=q.new_ones
        extra=encode(dict(joint_stiffness=q.new_tensor([60.]*4+[0.]*2).expand(self.num_envs,-1),
            joint_damping=q.new_tensor([2.]*4+[.6]*2).expand(self.num_envs,-1),
            joint_torque=d.applied_torque[:,r._actuate_idx],obs_delay_steps=zeros((self.num_envs,4)),
            act_delay_steps=zeros((self.num_envs,2)),wheel_body_lin_vel=wheel_v.flatten(1),
            wheel_contact_state=contacts,body_mass_scale=ones((self.num_envs,1)),
            body_material=q.new_tensor([.9,.9,.9,.9,0.,0.]).expand(self.num_envs,-1)),'critic')
        r.cache_raw_observations(dict(policy=policy),dict(critic=critic,extra=extra))
        return dict(policy=policy,critic=torch.cat((critic,extra),-1))

    def _get_observations(self):
        if self.reward is None:
            return dict(policy=torch.zeros(self.num_envs,35,device=self.device),
                        critic=torch.zeros(self.num_envs,78,device=self.device))
        self.reward._invalidate_step_caches()
        return self._encode()

    def _reset_idx(self,ids):
        if self.reward is None:
            return super()._reset_idx(ids)
        ids=ids.long()
        if self.snapshots is not None:
            self.done_totals['episodes']+=len(ids)
            for key,buf in [('closure',self.closure_reset),('mimic',self.mimic_reset),
                            ('numerical',self.numeric),('timeout',self.reset_time_outs)]:
                self.done_totals[key]+=int(buf[ids].sum())
        super()._reset_idx(ids)
        pick=torch.randint(len(self._bank_h),(len(ids),),device=self.device,generator=self.reset_generator)
        q=self._bank_q[pick][:,self._bank_ids]
        root=tensor(self.robot.data.default_root_state)[ids].clone()
        root[:,:3]+=self.scene.env_origins[ids];root[:,2]=self.scene.env_origins[ids,2]+self._bank_h[pick]
        root[:,7:]=0.
        self.robot.write_root_state_to_sim(root,env_ids=ids)
        self.robot.write_joint_state_to_sim(q,torch.zeros_like(q),env_ids=ids)
        self.mild_dr(self,ids)
        self.actions[ids]=0.;self.torque[ids]=0.
        self.reward.reset(ids)
        self._sample_command(ids)
        self.reward.command.copy_(self.command);self.reward.height_cmd.copy_(self.height)
        self.reward._invalidate_step_caches()



