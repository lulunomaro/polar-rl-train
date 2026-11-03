"""Isaac MOD4 bridge. Import only after the application starts.

Managers keep the original PD/DC actuator, physical delay and D0-D7 wrappers.
SCUT reward/done hooks run on the same pre-reset endpoint. Ray queries use the
actual scene mesh; the policy is never given analytic platform coordinates.
"""
import math
from types import SimpleNamespace
import numpy as np
import torch

from .config import WHEEL_BODIES, observation_component, ground_scan_config
from .math_ops import euler_xyz_from_quat, quat_apply, detect_sdk_quaternion_order
from .rewards import ScutRewards, indices
from .acceptance import Strict270, wheel_bounds

MESH = '/World/ground/scut_step270'
COURSE_N = 80


def layout(n):
    side = math.ceil(math.sqrt(n))
    return np.array([[(i//side)*8., (i % side)*8., 0.] for i in range(n)], np.float32)


def spawn_course(prim_path, cfg, **kwargs):
    from pxr import UsdGeom, UsdPhysics
    from isaaclab.sim import get_current_stage, define_collision_properties, bind_physics_material
    points, faces = [], []
    for ox, oy, _ in layout(COURSE_N):
        start = len(points)
        points.extend((ox+x, oy+y, 0.) for x, y in [(-3,-3),(4,-3),(4,3),(-3,3)])
        faces.extend([(start,start+1,start+2),(start,start+2,start+3)])
        start = len(points)
        points.extend((ox+.8+x, oy+y, z) for z in (0., .27)
                      for x, y in [(0,-1),(3,-1),(3,1),(0,1)])
        box = [(0,3,2),(0,2,1),(4,5,6),(4,6,7),(0,4,7),(0,7,3),
               (1,2,6),(1,6,5),(0,1,5),(0,5,4),(3,7,6),(3,6,2)]
        faces.extend(tuple(start+x for x in f) for f in box)
    stage = get_current_stage()
    root = UsdGeom.Xform.Define(stage, prim_path).GetPrim()
    mesh = UsdGeom.Mesh.Define(stage, MESH)
    mesh.CreatePointsAttr().Set(points)
    mesh.CreateFaceVertexCountsAttr().Set([3]*len(faces))
    mesh.CreateFaceVertexIndicesAttr().Set([x for f in faces for x in f])
    mesh.CreateSubdivisionSchemeAttr().Set('none')
    UsdPhysics.CollisionAPI.Apply(mesh.GetPrim())
    UsdPhysics.MeshCollisionAPI.Apply(mesh.GetPrim()).CreateApproximationAttr().Set('none')
    if cfg.collision_props is not None:
        define_collision_properties(MESH, cfg.collision_props, stage=stage)
    if cfg.physics_material is not None:
        material = prim_path+'/physicsMaterial'
        cfg.physics_material.func(material, cfg.physics_material)
        bind_physics_material(MESH, material, stage=stage)
    return root


def placeholder_reward(env):
    return torch.zeros(env.num_envs, device=env.device)


def configure(cfg, n):
    global COURSE_N
    from isaaclab.sensors import ContactSensorCfg, RayCasterCfg, patterns
    from isaaclab.managers import RewardTermCfg
    COURSE_N = n
    cfg.scene.num_envs, cfg.scene.env_spacing = n, 8.
    cfg.scene.ground.spawn.func = spawn_course
    cfg.scene.ground.init_state.pos = (0., 0., 0.)
    cfg.scene.scut_contacts = ContactSensorCfg(
        prim_path='{ENV_REGEX_NS}/Robot/links/.*', update_period=.005,
        history_length=3, track_air_time=False)
    cfg.scene.scut_current = ContactSensorCfg(
        prim_path='{ENV_REGEX_NS}/Robot/links/.*', update_period=0.,
        history_length=1, track_air_time=False)
    for side in ('left', 'right'):
        setattr(cfg.scene, 'scut_top_'+side, ContactSensorCfg(
            prim_path='{ENV_REGEX_NS}/Robot/links/'+side+'_wheel', update_period=0.,
            history_length=1, track_air_time=False, filter_prim_paths_expr=[MESH],
            max_contact_data_count_per_prim=64))
    scan = ground_scan_config()
    cfg.scene.scut_ground = RayCasterCfg(
        prim_path='{ENV_REGEX_NS}/Robot/links/chassis', update_period=0.,
        offset=RayCasterCfg.OffsetCfg(pos=scan['offset']), ray_alignment=scan['ray_alignment'],
        pattern_cfg=patterns.GridPatternCfg(resolution=scan['resolution'], size=scan['size'],
            direction=scan['direction'], ordering=scan['ordering']),
        mesh_prim_paths=[MESH], max_distance=scan['max_distance'])
    cfg.rewards = SimpleNamespace(scut=RewardTermCfg(func=placeholder_reward, weight=1.))
    cfg.curriculum = None
    cfg.episode_length_s = 8.
    cfg.decimation, cfg.sim.dt, cfg.sim.render_interval = 8, .0025, 8
    cfg.sim.physics.solver_type = 1  # target SDK uses physics, never physx
    cfg.scene.robot.spawn.articulation_props.solver_position_iteration_count = 32
    cfg.scene.robot.spawn.articulation_props.solver_velocity_iteration_count = 4
    cfg.terminations.closure.params['threshold'] = .01
    cfg.terminations.mimic.params['threshold'] = .01
    # Keep the physical source's chassis termination, now filtered to this course.
    cfg.scene.chassis_contact.filter_prim_paths_expr = [MESH]
    cfg.events.reset_base.params.update(
        pose_range={'x':(-.05,.05), 'y':(-.03,.03), 'yaw':(-.05,.05)},
        velocity_range={k:(0.,0.) for k in ('x','y','z','roll','pitch','yaw')})
    cmd = cfg.commands.twist
    cmd.ranges.lin_vel_x, cmd.ranges.lin_vel_y, cmd.ranges.ang_vel_z = (.6,.6), (0.,0.), (0.,0.)
    cmd.rel_standing_envs, cmd.heading_command = 0., False
    return cfg


class ScutBridge:
    def __init__(self, env, task, contract, tensor, profile='trained_stair'):
        self.env, self.task, self.tensor = env, task, tensor
        self.robot = env.scene['robot']
        self.quaternion_order, self.quaternion_readback = detect_sdk_quaternion_order(self.robot.data, tensor)
        self.reward = ScutRewards(self.robot, contract, env.num_envs, env.device,
                                  profile=profile, tensor=tensor, quaternion_order=self.quaternion_order)
        self.n, self.device = env.num_envs, env.device
        self.sensor = env.scene['scut_contacts']
        self.current_sensor = env.scene['scut_current']
        self.contact_order = indices(self.sensor.body_names, self.robot.body_names)
        self.current_contact_order = indices(self.current_sensor.body_names, self.robot.body_names)
        counts = [self.robot._physics_sim_view.create_rigid_body_view(path).max_shapes
                  for path in self.robot.root_view.link_paths[0]]
        if sum(counts) != self.robot.root_view.max_shapes:
            raise RuntimeError('MOD4 collider/material indexing mismatch')
        self.wheel_material_ids = [list(range(sum(counts[:bid]), sum(counts[:bid+1])))
                                   for bid in self.reward._wheel_link_idx]
        self.top_sensors = [env.scene['scut_top_'+s] for s in ('left', 'right')]
        self.top_force = torch.zeros(self.n, 2, device=self.device)
        self.ground_force = self.top_force.clone()
        self.physics_ticks = 0
        self.terminal_snapshot = None
        self.pending_actions = torch.zeros(self.n, 6, device=self.device)
        self.last_reward = torch.zeros(self.n, device=self.device)
        self.reset_scan_pending = torch.ones(self.n, dtype=torch.bool, device=self.device)
        self.scan_max_distance = ground_scan_config()['max_distance']
        self.acceptance = Strict270(self.n, self.device)
        self.completed_episodes = 0
        self.completed_strict = 0
        self.ready = False
        self.original_update = env.scene.update
        self.original_reward = env.reward_manager.compute
        self.original_done = env.termination_manager.compute
        self.original_reset = env._reset_idx
        env.scene.env_origins.copy_(torch.as_tensor(layout(self.n), device=self.device))
        self.install_hooks()

    def install_hooks(self):
        env = self.env
        def update(dt):
            self.original_update(dt)
            if not self.ready:
                return
            if abs(float(dt)-.0025) > 1.e-9:
                raise RuntimeError('Strict270 requires each actual 2.5ms physics endpoint')
            self.physics_ticks += 1
            if self.physics_ticks % 2 == 0:
                _ = self.sensor.data  # exactly the original 5ms/three-sample history
            self.read_manifold()
            self.measure_acceptance()
        env.scene.update = update

        def done(*args, **kwargs):
            result = self.original_done(*args, **kwargs)
            self.prepare_endpoint()
            terminated, timeout = self.resolve_done(env.termination_manager.terminated.clone(),
                                                   env.termination_manager.time_outs.clone())
            # ManagerBasedRLEnv consumes both the return and these buffers.
            env.termination_manager._terminated_buf.copy_(terminated)
            env.termination_manager._truncated_buf.copy_(timeout)
            self.reward.reset_terminated.copy_(terminated)
            self.terminal_snapshot = self.snapshot(terminated, timeout)
            return terminated | timeout
        env.termination_manager.compute = done

        def compute_reward(dt):
            self.original_reward(dt)  # keep manager episode counters, placeholder is zero
            if abs(float(dt)-.02) > 1.e-9:
                raise ValueError('SCUT reward dt must be applied exactly once at 50Hz')
            self.last_reward = self.reward.compute()
            return self.last_reward
        env.reward_manager.compute = compute_reward

        def reset(ids):
            saved_log = {}
            if self.ready:
                self.completed_episodes += len(ids)
                self.completed_strict += int(self.acceptance.success[ids].sum())
                saved_log = self.log_reset(ids)
            self.reward.reset(ids)
            self.top_force[ids] = 0
            self.ground_force[ids] = 0
            self.acceptance.reset(ids)
            result = self.original_reset(ids)
            # Read sensors after the manager has flushed reset poses to PhysX,
            # when it constructs the returned observation (no extra sim step).
            self.reset_scan_pending[ids] = True
            # ManagerBasedRLEnv replaces extras['log'] inside its reset. Merge
            # the pre-reset reward/state values only after that replacement.
            env.extras.setdefault('log', {}).update(saved_log)
            self.reward.height_cmd[ids] = self.task.height_cmd(env)[ids, 0]
            return result
        env._reset_idx = reset

    def resolve_done(self, terminated, timeout):
        r = self.reward
        body = r.robot.data
        bad = torch.zeros_like(terminated)
        for key in ('joint_pos', 'joint_vel', 'root_pos_w', 'root_quat_w',
                    'root_lin_vel_b', 'root_ang_vel_b'):
            bad |= ~torch.isfinite(getattr(body, key)).flatten(1).all(-1)
        # These are the pinned upstream numerical-safety limits, not new gates.
        for value, key, default in (
            (body.joint_vel[:, r._actuate_idx], 'terminate_joint_vel_abs', 500.),
            (body.root_lin_vel_b, 'terminate_root_lin_vel_abs', 100.),
            (body.root_ang_vel_b, 'terminate_root_ang_vel_abs', 200.)):
            bad |= value.abs().amax(-1) > float(getattr(r.cfg, key, default))
        r._numerical_safety_reset_buf.copy_(bad)
        terminated, timeout = r.state_machine_manager.apply_done_masks(r, terminated, timeout)
        # A wall event may change a task failure into a timeout in SCUT. It must
        # never suppress the user's mandatory MOD4 closure/mimic reset or NaNs.
        hard = bad.clone()
        for name in ('closure', 'mimic'):
            hard |= self.env.termination_manager.get_term(name)
        return terminated | hard, timeout

    def log_reset(self, ids):
        """Log original weighted reward sums before resetting only these episodes."""
        r = self.reward
        log = {}
        duration = self.env.max_episode_length_s
        for name, value in r._episode_sums.items():
            log['Episode_Reward/scut_'+name] = value[ids].mean()/duration
        r.state_machine_manager.append_reset_logs(r, log, ids)
        log['Metrics/strict270_completed'] = self.completed_strict
        log['Metrics/episodes_completed'] = self.completed_episodes
        return log

    def measure_acceptance(self):
        r = self.reward
        body = r.robot.data
        low, high = wheel_bounds(body.body_pos_w[:, r._wheel_link_idx],
                                 body.body_quat_w[:, r._wheel_link_idx], r.contract)
        offset = self.env.scene.env_origins.clone()
        offset[:, 0] += .8
        low[..., :2] -= offset[:, None, :2]
        high[..., :2] -= offset[:, None, :2]
        contact = self.tensor(self.current_sensor.data.net_forces_w)[:, self.current_contact_order]
        # Strict support uses current400Hz force, separate from SCUT5ms history.
        nonwheel = contact[:, r._undesired_contact_link_idx].norm(dim=-1).amax(-1)
        self.acceptance.update(low, high, self.top_force, self.ground_force,
            contact[:, r._wheel_link_idx], nonwheel, body.root_lin_vel_w,
            body.root_quat_w, torch.ones(self.n, dtype=torch.bool, device=self.device))

    def raycast(self, points, fallback_z):
        """Actual scene mesh rays, never analytic course GT in reward/observation."""
        from isaaclab.utils.warp import raycast_mesh
        from isaaclab.sensors.ray_caster.ray_caster import RayCaster
        mesh = RayCaster.meshes[MESH]
        starts = points.clone()
        starts[..., 2] += 5.
        direction = torch.zeros_like(starts)
        direction[..., 2] = -1.
        hits = raycast_mesh(starts, direction, mesh, max_dist=self.scan_max_distance)[0]
        # Pinned env.py:266-270 falls back to chassis ground for a missed ray.
        fallback = points.clone()
        fallback[..., 2] = fallback_z[:, None]
        return starts, torch.where(torch.isfinite(hits).all(-1, keepdim=True), hits, fallback)

    def read_reward_scans(self, ids=None):
        """Read reset poses selectively; retain other envs' temporal scan cache."""
        r = self.reward
        body = r.robot.data
        select = slice(None) if ids is None else ids
        wheels = body.body_pos_w[select][:, r._wheel_link_idx]
        ground_hits = self.tensor(self.env.scene['scut_ground'].data.ray_hits_w)[select]
        finite = torch.isfinite(ground_hits[..., 2])
        ground = (ground_hits[..., 2].masked_fill(~finite, 0).sum(-1)
                  / finite.sum(-1).clamp_min(1))
        ground = torch.where(finite.any(-1), ground, self.env.scene.env_origins[select, 2])
        # Saved SCUT recipe has no per-wheel scanners; its helper falls back to
        # chassis ground for both wheels. Direct wheel rays change this reward.
        wheel_ground = ground[:, None].expand(-1, 2).clone()
        _, _, yaw = euler_xyz_from_quat(body.root_quat_w[select])
        commands = self.env.command_manager.get_command('twist')[select]
        direction = torch.where(commands[:, 0] >= 0, 1., -1.)
        heading = torch.stack((torch.cos(yaw)*direction, torch.sin(yaw)*direction,
                               torch.zeros_like(yaw)), -1)
        far = wheels + heading[:, None, :]*float(r.cfg.wheel_forward_scan_cfg.get('scan', {}).get('forward_offset', .10))
        near = wheels + heading[:, None, :]*float(r.cfg.stair_state_machine_cfg.get('scan', {}).get('forward_offset', .2))
        if r.cfg.wheel_forward_scan_cfg.get('enabled', False):
            far, far_hits = self.raycast(far, ground)
            near, near_hits = self.raycast(near, ground)
        else:
            far_hits, near_hits = far.clone(), near.clone()
            far_hits[..., 2] = ground[:, None]
            near_hits[..., 2] = ground[:, None]
        return ground, wheel_ground, far, far_hits, near, near_hits

    def prepare_endpoint(self):
        r = self.reward
        body = r.robot.data
        ground, wheel_ground, far, far_hits, near, near_hits = self.read_reward_scans()
        commands = self.env.command_manager.get_command('twist')
        contacts = self.tensor(self.sensor.data.net_forces_w_history)[:, :, self.contact_order]
        bad = torch.zeros(self.n, dtype=torch.bool, device=self.device)
        for key in ('joint_pos', 'joint_vel', 'root_pos_w', 'root_quat_w'):
            bad |= ~torch.isfinite(getattr(body, key)).flatten(1).all(-1)
        r.begin(self.pending_actions, commands, self.task.height_cmd(self.env),
                self.env.termination_manager.terminated, bad,
                self.env.episode_length_buf, contacts, ground, wheel_ground,
                far, far_hits, near, near_hits)

    def refresh_observation_context(self):
        """Original post-reward observation hook, once per returned observation."""
        r = self.reward
        r._cached_wheel_kinematics_valid = False
        r.command = self.env.command_manager.get_command('twist').clone()
        r.height_cmd = self.task.height_cmd(self.env).reshape(-1).clone()
        r.episode_length_buf.copy_(self.env.episode_length_buf)
        ids = self.reset_scan_pending.nonzero(as_tuple=False).flatten()
        if len(ids):
            r.refresh_reset_scans(ids, *self.read_reward_scans(ids))
            self.reset_scan_pending[ids] = False
        r._on_command_updated()
        r.state_machine_manager.on_observation_step(r)

    def read_manifold(self):
        """Read actual400Hz normal force, points and normals for strict evaluation."""
        import warp as wp
        for wi, sensor in enumerate(self.top_sensors):
            if list(sensor.body_names) != [WHEEL_BODIES[wi]] or sensor.contact_view.filter_count != 1:
                raise RuntimeError('Expected one explicit wheel/course manifold filter')
            force, point, normal, separation, counts, starts = sensor.contact_view.get_contact_data(dt=.0025)
            f = wp.to_torch(force).flatten().abs()
            p = wp.to_torch(point.view(wp.vec3))
            normal = wp.to_torch(normal.view(wp.vec3))
            count = wp.to_torch(counts.view(wp.int32)).reshape(self.n).long()
            start = wp.to_torch(starts.view(wp.int32)).reshape(self.n).long()
            if not bool(((count >= 0) & (count <= 64) & (start >= 0) & (start+count <= len(f))).all()):
                raise RuntimeError('Manifold buffer capacity/count mismatch')
            self.top_force[:, wi] = 0
            self.ground_force[:, wi] = 0
            if len(f) == 0:
                continue
            offset = torch.arange(64, device=self.device)[None]
            valid = offset < count[:, None]
            ids = (start[:, None]+offset).clamp(0, len(f)-1)
            pts = p[ids]-self.env.scene.env_origins[:, None]
            upward = normal[ids, 2].abs() > .8
            top = valid & upward & ((pts[..., 2]-.27).abs() < .001) & (pts[..., 0] >= .799) & (pts[..., 0] <= 3.801) & (pts[..., 1].abs() <= 1.001)
            ground = valid & upward & (pts[..., 2].abs() < .001)
            self.top_force[:, wi] = torch.where(top, f[ids], 0.).sum(-1)
            self.ground_force[:, wi] = torch.where(ground, f[ids], 0.).sum(-1)

    def snapshot(self, terminated, timeout):
        r = self.reward
        return dict(root_pos=r.robot.data.root_pos_w.clone(),
                    root_quat=r.robot.data.root_quat_w.clone(),
                    wheels=r.robot.data.body_pos_w[:, r._wheel_link_idx].clone(),
                    top_force=self.top_force.clone(), ground_force=self.ground_force.clone(),
                    terminated=terminated.clone(), time_out=timeout.clone(),
                    strict270=self.acceptance.success.clone(),
                    first_flight_wholeclear=self.acceptance.wholeclear.clone(),
                    first_flight_leading=self.acceptance.leading.clone(),
                    longest_stable_seconds=self.acceptance.stable_peak.clone()*.0025,
                    longest_valid_top_seconds=self.acceptance.support_peak.clone()*.0025,
                    physics_ticks=self.physics_ticks)

    def observations(self, raw):
        """35 actor; 78 critic with actual MOD4 equivalents of SCUT privileged fields."""
        r = self.reward
        self.refresh_observation_context()
        part = lambda key, value, stream='critic': observation_component(r.cfg, key, value, stream=stream)
        mode = r._get_ctrl_mode_obs_raw()
        actor, critic = raw['policy'].clone(), raw['critic'].clone()
        if actor.shape != (self.n, 35) or critic.shape != (self.n, 38):
            raise ValueError('Unexpected MOD4 observation layout')
        for value, stream in ((actor, 'policy'), (critic, 'critic')):
            value[:, -7:] = part('ctrl_mode_obs', mode, stream)
            value[:, :3] = part('command', r.command, stream)
            value[:, 3] = part('height_cmd', r._get_effective_height_cmd(), stream)
        # MOD4 clean critic layout differs from SCUT: reorder base38 into the same
        # 35 actor fields plus privileged base velocity(3) and measured height(1).
        clean = torch.cat((critic[:, :7], critic[:, 10:]), -1)
        for value, stream in ((actor, 'policy'), (clean, 'critic')):
            # Original MOD4 managers already apply these scales. Undo only that
            # known scale before the pinned clip -> scale transform.
            for key, span, old_scale in (
                ('root_ang_vel_b', slice(4, 7), .5),
                ('projected_gravity_b', slice(7, 10), 1.),
                ('joint_pos', slice(10, 16), 1.),
                ('joint_vel_leg', slice(16, 20), .1),
                ('joint_vel_wheel', slice(20, 22), .1),
                ('actions', slice(22, 28), 1.)):
                value[:, span] = part(key, value[:, span]/old_scale, stream)
        height = part('obs_height', r._get_observed_height()[:, None])
        velocity = part('root_lin_vel_b', r.robot.data.root_lin_vel_b)
        obs = torch.cat((clean, velocity, height), -1)  # 39
        ids = r._actuate_idx
        pd = self.env._explicit_pd
        pd_order = indices(pd.leg_ids+pd.wheel_ids, ids)
        stiffness = torch.cat((self.tensor(pd.legs.stiffness), self.tensor(pd.wheels.stiffness)), -1)[:, pd_order]
        damping = torch.cat((self.tensor(pd.legs.damping), self.tensor(pd.wheels.damping)), -1)[:, pd_order]
        torque = r.robot.data.applied_torque[:, ids]
        # Pinned obs delays contain angular velocity, gravity, position, velocity(4); action
        # delays contain leg and wheel target groups (2). Keep actual MOD4 clocks.
        delay = self.env._feedback_delay_mild.delay.float()[:, None].expand(-1, 4)
        queue = self.env._physics_action_delay.queue
        act_delay = torch.stack([queue.groups[k]['lag_steps'].float() for k in ('legs', 'wheels')], -1)
        _, _, _, wheel_vel, _ = r._get_root_quat_inv_and_wheel_pos_b()
        contacts = (r._get_wheel_contact_force_peaks(r.contact_sensor.data.net_forces_w_history)
                    > r.cfg.desired_contact_force_threshold).float()
        masses = self.tensor(self.robot.root_view.get_masses()).to(self.device)
        chassis = indices(self.robot.body_names, ('chassis',))[0]
        mass_ratio = masses[:, chassis:chassis+1]/self.env._mild_dr.mass[:, chassis:chassis+1].to(self.device)
        materials = self.tensor(self.robot.root_view.get_material_properties()).to(self.device)
        # Resolve collider indices from the existing MOD4 material map, not body IDs.
        material_ids = self.wheel_material_ids
        material = torch.stack([materials[:, ids_, :3].mean(1) for ids_ in material_ids], 1).flatten(1)
        fields = [('joint_stiffness', stiffness), ('joint_damping', damping),
                  ('joint_torque', torque), ('obs_delay_steps', delay),
                  ('act_delay_steps', act_delay), ('wheel_body_lin_vel', wheel_vel.flatten(1)),
                  ('wheel_contact_state', contacts), ('body_mass_scale', mass_ratio),
                  ('body_material', material)]
        extra = torch.cat([part(name, value) for name, value in fields], -1)
        if extra.shape[-1] != 39:
            raise ValueError('SCUT privileged39 field layout mismatch')
        return dict(policy=actor, critic=torch.cat((obs, extra), -1))

    def close(self):
        self.env.scene.update = self.original_update
        self.env.reward_manager.compute = self.original_reward
        self.env.termination_manager.compute = self.original_done
        self.env._reset_idx = self.original_reset
