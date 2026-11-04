"""Isaac MOD4 bridge. Import only after the application starts.

Managers keep the original PD/DC actuator, physical delay and D0-D7 wrappers.
SCUT reward/done hooks run on the same pre-reset endpoint. Ray queries use the
actual scene mesh; the policy is never given analytic platform coordinates.
"""
import math
from types import SimpleNamespace
import numpy as np
import torch

from .config import WHEEL_BODIES, observation_component, ground_scan_config, reward_config
from .commands import build_command_cfg, RewardTailCommand
from .math_ops import euler_xyz_from_quat, quat_apply, detect_sdk_quaternion_order
from .rewards import ScutRewards, indices
from .target_limits import limited_action_type
from .acceptance import Strict270, wheel_bounds
from .course import BOXES, HEIGHT, POSE_RANGE, SPAWN_HEIGHT, FourSideStrict270, top_mask

MESH = '/World/ground/scut_step270'
COURSE_N = 80


def layout(n):
    side = math.ceil(math.sqrt(n))
    return np.array([[(i//side)*8., (i % side)*8., 0.] for i in range(n)], np.float32)


def spawn_course(prim_path, cfg, **kwargs):
    from pxr import UsdGeom, UsdPhysics, Gf, Vt
    from isaaclab.sim import get_current_stage, define_collision_properties, bind_physics_material
    points, faces = [], []
    for ox, oy, _ in layout(COURSE_N):
        start = len(points)
        points.extend((ox+x, oy+y, 0.) for x, y in [(-3.6,-3.6),(3.6,-3.6),(3.6,3.6),(-3.6,3.6)])
        faces.extend([(start,start+1,start+2),(start,start+2,start+3)])
        box = [(0,3,2),(0,2,1),(4,5,6),(4,6,7),(0,4,7),(0,7,3),
               (1,2,6),(1,6,5),(0,1,5),(0,5,4),(3,7,6),(3,6,2)]
        for xmin,xmax,ymin,ymax in BOXES:
            start = len(points)
            points.extend((ox+x,oy+y,z) for z in (0.,HEIGHT)
                          for x,y in [(xmin,ymin),(xmax,ymin),(xmax,ymax),(xmin,ymax)])
            faces.extend(tuple(start+x for x in f) for f in box)
    stage = get_current_stage()
    root = UsdGeom.Xform.Define(stage, prim_path).GetPrim()
    mesh = UsdGeom.Mesh.Define(stage, MESH)
    mesh.CreatePointsAttr().Set(Vt.Vec3fArray([Gf.Vec3f(*map(float,p)) for p in points]))
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


def configure(cfg, n, profile='trained_stair', contract=None):
    global COURSE_N, MESH
    from isaaclab.sensors import ContactSensorCfg, RayCasterCfg, patterns
    from isaaclab.managers import RewardTermCfg
    COURSE_N = n
    if contract is None:
        raise ValueError('Bind enhanced MOD4 contract before constructing action targets')
    cfg.actions.legs.class_type = limited_action_type(cfg.actions.legs.class_type, contract)
    cfg.scene.num_envs, cfg.scene.env_spacing = n, 8.
    cfg.scene.ground.spawn.func = spawn_course
    cfg.scene.ground.init_state.pos = (0., 0., 0.)
    if profile == 'scut_stairs':
        from .stairs import terrain_cfg, MESH as stair_mesh
        cfg.scene.ground = terrain_cfg(cfg.seed)
        MESH = stair_mesh
    cfg.scene.robot.init_state.pos = (0.,0.,SPAWN_HEIGHT)
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
    cfg.episode_length_s = reward_config(profile).episode_length_s
    cfg.decimation, cfg.sim.dt, cfg.sim.render_interval = 8, .0025, 8
    cfg.sim.physics.solver_type = 1  # target SDK uses physics, never physx
    cfg.scene.robot.spawn.articulation_props.solver_position_iteration_count = 32
    cfg.scene.robot.spawn.articulation_props.solver_velocity_iteration_count = 4
    cfg.terminations.closure.params['threshold'] = .01
    cfg.terminations.mimic.params['threshold'] = .01
    # Only model-specific mandatory guards remain in the manager. Contact,
    # orientation, timeout and consecutive duration come from pinned _get_dones.
    cfg.terminations = SimpleNamespace(closure=cfg.terminations.closure,
                                      mimic=cfg.terminations.mimic)
    cfg.scene.chassis_contact.filter_prim_paths_expr = [MESH]
    cfg.events.reset_base.params.update(
        pose_range=dict(POSE_RANGE),
        velocity_range={k:(0.,0.) for k in ('x','y','z','roll','pitch','yaw')})
    cfg.commands.twist = build_command_cfg(profile)
    return cfg


class ScutBridge:
    def __init__(self, env, task, contract, tensor, profile='trained_stair'):
        self.env, self.task, self.tensor = env, task, tensor
        self.profile = profile
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
        self.surface_force = self.top_force.clone()
        self.surface_height = self.top_force.clone()
        self.physics_ticks = 0
        self.terminal_snapshot = None
        self.pending_actions = torch.zeros(self.n, 6, device=self.device)
        self.last_reward = torch.zeros(self.n, device=self.device)
        self.reset_scan_pending = torch.ones(self.n, dtype=torch.bool, device=self.device)
        self.scan_max_distance = ground_scan_config()['max_distance']
        if profile == 'scut_stairs':
            from .stairs import StairTraversal
            self.acceptance = StairTraversal(self.n, self.device)
        else:
            self.acceptance = FourSideStrict270(self.n, self.device)
        self.physics_observer = None
        self.completed_episodes = 0
        self.completed_strict = 0
        self.ready = False
        self.original_update = env.scene.update
        self.original_reward = env.reward_manager.compute
        self.original_done = env.termination_manager.compute
        self.original_reset = env._reset_idx
        self.original_command_compute = env.command_manager.compute
        self.command_term = env.command_manager.get_term('twist')
        self.reward.command_generator = RewardTailCommand(self.command_term, self.original_command_compute)
        self.reward.command_counter = self.command_term.command_counter.clone()
        self.reward.command_height_sink = self.write_height_command
        self.reward.forward_scan_provider = self.read_forward_scan
        self.reward.max_episode_length = env.max_episode_length
        if profile != 'scut_stairs':
            env.scene.env_origins.copy_(torch.as_tensor(layout(self.n), device=self.device))
        self.install_hooks()

    def install_hooks(self):
        env = self.env
        # DirectRLEnv's source advances commands inside _get_rewards, before
        # resets. Do not advance them again in ManagerBasedRLEnv after resets.
        env.command_manager.compute = lambda dt: None
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
            if self.physics_observer is not None:
                self.physics_observer(self)
        env.scene.update = update

        def done(*args, **kwargs):
            result = self.original_done(*args, **kwargs)
            self.prepare_endpoint()
            terminated, timeout = self.resolve_done()
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
            # The MOD4 constraint-consistent bank supplies valid JOINT poses,
            # then overrides root z to its old flat height. Apply the selected
            # SCUT spawn height after it, retaining closure/mimic coordinates
            # and the sampled original roll/pitch/yaw from reset_base.
            root=self.tensor(self.robot.data.root_state_w)[ids].clone()
            root[:,2]=self.env.scene.env_origins[ids,2]+SPAWN_HEIGHT
            root[:,7:]=0.
            self.robot.write_root_state_to_sim(root,env_ids=ids)
            if isinstance(self.acceptance, FourSideStrict270):
                q = root[:,3:7]
                if self.quaternion_order == 'xyzw':
                    q = q[:,[3,0,1,2]]
                self.acceptance.set_spawn_orientation(ids, q)
            # Read sensors after the manager has flushed reset poses to PhysX,
            # when it constructs the returned observation (no extra sim step).
            self.reset_scan_pending[ids] = True
            # ManagerBasedRLEnv replaces extras['log'] inside its reset. Merge
            # the pre-reset reward/state values only after that replacement.
            env.extras.setdefault('log', {}).update(saved_log)
            self.reward.resample_height(ids)
            self.reward.command_counter[ids] = self.command_term.command_counter[ids]
            return result
        env._reset_idx = reset

    def write_height_command(self, ids, height):
        self.task.height_cmd(self.env)[ids, 0] = height

    def resolve_done(self, *_unused):
        r = self.reward
        body = r.robot.data
        terminated, timeout = r._get_dones()
        bad = r._numerical_safety_reset_buf.clone()
        for key in ('joint_pos', 'joint_vel', 'root_pos_w', 'root_quat_w',
                    'root_lin_vel_b', 'root_ang_vel_b'):
            bad |= ~torch.isfinite(getattr(body, key)).flatten(1).all(-1)
        r._numerical_safety_reset_buf.copy_(bad)
        # A wall event may change a task failure into a timeout in SCUT. It must
        # never suppress the user's mandatory MOD4 closure/mimic reset or NaNs.
        hard = bad.clone()
        for name in ('closure', 'mimic'):
            hard |= self.env.termination_manager.get_term(name)
        # Preserve SCUT timeout/bootstrap semantics for its own task failures.
        # Mandatory model/numerical resets alone cannot bootstrap a timeout.
        return terminated | hard, timeout & ~hard

    def log_reset(self, ids):
        """Log original weighted reward sums before resetting only these episodes."""
        r = self.reward
        log = {}
        duration = self.env.max_episode_length_s
        for name, value in r._episode_sums.items():
            log['Episode_Reward/scut_'+name] = value[ids].mean()/duration
        r.state_machine_manager.append_reset_logs(r, log, ids)
        metric = 'Metrics/scut_stair_recovered' if self.profile == 'scut_stairs' else 'Metrics/strict270_completed'
        log[metric] = self.completed_strict
        log['Metrics/episodes_completed'] = self.completed_episodes
        return log

    def measure_acceptance(self):
        r = self.reward
        body = r.robot.data
        if self.profile == 'scut_stairs':
            contact = self.tensor(self.current_sensor.data.net_forces_w)[:,self.current_contact_order]
            nonwheel = contact[:,r._nonwheel_contact_link_idx].norm(dim=-1).amax(-1)
            self.acceptance.update(body.body_pos_w[:,r._wheel_link_idx], self.surface_height,
                self.surface_force, nonwheel, body.root_lin_vel_w, body.root_quat_w, body.root_pos_w,
                r.ground_z_est)
            return
        if hasattr(self.acceptance, 'update_world'):
            contact = self.tensor(self.current_sensor.data.net_forces_w)[:,self.current_contact_order]
            nonwheel = contact[:,r._nonwheel_contact_link_idx].norm(dim=-1).amax(-1)
            self.acceptance.update_world(body.body_pos_w[:,r._wheel_link_idx],
                body.body_quat_w[:,r._wheel_link_idx],r.contract,self.env.scene.env_origins,
                self.top_force,self.ground_force,contact[:,r._wheel_link_idx],nonwheel,
                body.root_lin_vel_w,body.root_quat_w,torch.ones(self.n,dtype=torch.bool,device=self.device))
            return
        low, high = wheel_bounds(body.body_pos_w[:, r._wheel_link_idx],
                                 body.body_quat_w[:, r._wheel_link_idx], r.contract)
        offset = self.env.scene.env_origins.clone()
        offset[:, 0] += .8
        low[..., :2] -= offset[:, None, :2]
        high[..., :2] -= offset[:, None, :2]
        contact = self.tensor(self.current_sensor.data.net_forces_w)[:, self.current_contact_order]
        # Strict support uses current400Hz force, separate from SCUT5ms history.
        nonwheel = contact[:, r._nonwheel_contact_link_idx].norm(dim=-1).amax(-1)
        self.acceptance.update(low, high, self.top_force, self.ground_force,
            contact[:, r._wheel_link_idx], nonwheel, body.root_lin_vel_w,
            body.root_quat_w, torch.ones(self.n, dtype=torch.bool, device=self.device))

    def raycast(self, points, fallback_z):
        """Actual scene mesh rays, never analytic course GT in reward/observation."""
        from isaaclab.utils.warp import raycast_mesh
        sensor = self.env.scene['scut_ground']
        mesh = sensor.meshes[(MESH,sensor._device)]
        starts = points.clone()
        starts[..., 2] += 5.
        direction = torch.zeros_like(starts)
        direction[..., 2] = -1.
        hits = raycast_mesh(starts, direction, mesh, max_dist=self.scan_max_distance)[0]
        # Pinned env.py:266-270 falls back to chassis ground for a missed ray.
        fallback = points.clone()
        fallback[..., 2] = fallback_z[:, None]
        return starts, torch.where(torch.isfinite(hits).all(-1, keepdim=True), hits, fallback)

    def read_forward_scan(self, stair):
        """Query lazily in the original helper order, after any command resample."""
        r = self.reward
        cfg = r.cfg.stair_state_machine_cfg if stair else r.cfg.wheel_forward_scan_cfg
        if not r.cfg.wheel_forward_scan_cfg.get('enabled', False) or not cfg.get('enabled', False):
            return None, None
        body = r.robot.data
        wheels = body.body_pos_w[:, r._wheel_link_idx]
        _, _, yaw = euler_xyz_from_quat(body.root_quat_w)
        direction = torch.where(r.command[:,0] < 0, -1., 1.)
        heading = torch.stack((torch.cos(yaw)*direction, torch.sin(yaw)*direction, torch.zeros_like(yaw)), -1)
        offset = float(cfg.get('scan', {}).get('forward_offset', .2 if stair else .1))
        return self.raycast(wheels + heading[:,None,:]*offset, r.ground_z_est)

    def read_reward_scans(self, ids=None, forward=True):
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
        commands = r.command[select]
        direction = torch.where(commands[:, 0] >= 0, 1., -1.)
        heading = torch.stack((torch.cos(yaw)*direction, torch.sin(yaw)*direction,
                               torch.zeros_like(yaw)), -1)
        far = wheels + heading[:, None, :]*float(r.cfg.wheel_forward_scan_cfg.get('scan', {}).get('forward_offset', .10))
        near = wheels + heading[:, None, :]*float(r.cfg.stair_state_machine_cfg.get('scan', {}).get('forward_offset', .2))
        if forward and r.cfg.wheel_forward_scan_cfg.get('enabled', False):
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
        ground, wheel_ground, far, far_hits, near, near_hits = self.read_reward_scans(forward=False)
        commands = r.command
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
        r.finish_observation()  # env.py:3107-3108, before command/state hooks
        r.command = self.env.command_manager.get_command('twist').clone()
        r.height_cmd = self.task.height_cmd(self.env).reshape(-1).clone()
        r.episode_length_buf.copy_(self.env.episode_length_buf)
        ids = self.reset_scan_pending.nonzero(as_tuple=False).flatten()
        if len(ids):
            r.refresh_reset_scans(ids, *self.read_reward_scans(ids))
            self.reset_scan_pending[ids] = False
        r._on_command_updated()

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
            self.surface_force[:, wi] = 0
            self.surface_height[:, wi] = 0
            if len(f) == 0:
                continue
            offset = torch.arange(64, device=self.device)[None]
            valid = offset < count[:, None]
            ids = (start[:, None]+offset).clamp(0, len(f)-1)
            pts = p[ids]-self.env.scene.env_origins[:, None]
            upward = normal[ids, 2].abs() > .8
            horizontal = valid & upward
            self.surface_force[:, wi] = torch.where(horizontal, f[ids], 0.).sum(-1)
            peak = torch.where(horizontal, f[ids], -1.).argmax(-1)
            world_height = p[ids, 2].gather(1, peak[:,None]).squeeze(1)
            self.surface_height[:, wi] = torch.where(horizontal.any(-1), world_height, 0.)
            if self.profile == 'scut_stairs':
                self.ground_force[:, wi] = self.surface_force[:, wi]
                above_birth = self.surface_height[:,wi] > self.acceptance.birth_support[:,wi]+.0049
                self.top_force[:,wi] = torch.where(above_birth, self.surface_force[:,wi], 0.)
                continue
            top = valid & upward & top_mask(pts)
            ground = valid & upward & (pts[..., 2].abs() < .001)
            self.top_force[:, wi] = torch.where(top, f[ids], 0.).sum(-1)
            self.ground_force[:, wi] = torch.where(ground, f[ids], 0.).sum(-1)

    def snapshot(self, terminated, timeout):
        r = self.reward
        threshold = r._terminate_obs_abs if r._terminate_obs_abs > 0 else float(getattr(r.cfg, 'debug_obs_alert_threshold', 0.))
        raw_bad = r._obs_raw_policy_has_nonfinite.clone()
        if threshold > 0:
            raw_bad |= r._obs_raw_policy_max_abs > threshold
        if r.cfg.state_space is not None:
            raw_bad |= r._obs_raw_critic_has_nonfinite
            if threshold > 0:
                raw_bad |= r._obs_raw_critic_max_abs > threshold
        raw_bad &= bool(r._terminate_on_obs_outlier and r._value_debug_step > 10)
        reset_contact_force = torch.linalg.vector_norm(
            r.contact_sensor.data.net_forces_w[:, r._reset_contact_link_idx], dim=-1)
        roll, pitch, _ = euler_xyz_from_quat(r.robot.data.root_quat_w)
        roll_pitch = torch.stack((roll, pitch), -1)
        snapshot = dict(root_pos=r.robot.data.root_pos_w.clone(),
                    root_quat=r.robot.data.root_quat_w.clone(),
                    wheels=r.robot.data.body_pos_w[:, r._wheel_link_idx].clone(),
                    top_force=self.top_force.clone(), ground_force=self.ground_force.clone(),
                    terminated=terminated.clone(), time_out=timeout.clone(),
                    strict270=self.acceptance.success.clone(),
                    first_flight_wholeclear=self.acceptance.wholeclear.clone(),
                    first_flight_leading=self.acceptance.leading.clone(),
                    longest_stable_seconds=self.acceptance.stable_peak.clone()*.0025,
                    longest_valid_top_seconds=self.acceptance.support_peak.clone()*.0025,
                    physics_ticks=self.physics_ticks,
                    applied_action=self.pending_actions.clone(),
                    joint_target=r.robot.data.joint_pos_target[:,r._legs_act_idx].clone(),
                    raw_policy_max_abs=r._obs_raw_policy_max_abs.clone(),
                    raw_critic_max_abs=r._obs_raw_critic_max_abs.clone(),
                    observation_outlier=raw_bad,
                    closure_reset=self.env.termination_manager.get_term('closure').clone(),
                    mimic_reset=self.env.termination_manager.get_term('mimic').clone(),
                    numerical_reset=r._numerical_safety_reset_buf.clone(),
                    reset_body_contact_force=reset_contact_force.clone(),
                    roll_pitch_rad=roll_pitch.clone(),
                    termination_raw=r._termination_duration_raw_buf.clone(),
                    command=r.command.clone(),
                    command_height=r.height_cmd.clone(),
                    effective_height=r._get_effective_height_cmd().clone(),
                    termination_duration_counter=r._termination_duration_counter.clone(),
                    observation_debug_step=r._value_debug_step,
                    observation_debug_enabled=r._value_debug_enabled)
        if self.profile == 'scut_stairs':
            snapshot.update(strict270=torch.zeros_like(self.acceptance.success),
                first_flight_wholeclear=torch.zeros_like(self.acceptance.success),
                first_flight_leading=torch.zeros_like(self.acceptance.success),
                scut_stair_recovered=self.acceptance.success.clone(),
                scut_stair_both_up=self.acceptance.wholeclear.clone(),
                scut_stair_any_up=self.acceptance.leading.clone(),
                scut_stair_max_rise=self.acceptance.max_rise.clone(),
                surface_support_height=self.surface_height.clone(),
                surface_support_force=self.surface_force.clone(),
                actual_motor_position=r.robot.data.joint_pos[:,r._actuate_idx].clone(),
                actual_motor_velocity=r.robot.data.joint_vel[:,r._actuate_idx].clone(),
                actual_motor_torque=r.robot.data.applied_torque[:,r._actuate_idx].clone(),
                ground_height=r.ground_z_est.clone(),
                observed_height=r._get_observed_height().clone())
        return snapshot

    def observations(self, raw):
        """35 actor; 78 critic with actual MOD4 equivalents of SCUT privileged fields."""
        r = self.reward
        self.refresh_observation_context()
        # env.py:3123-3131 captures height before the observation-state update.
        # A machine may change its effective target on this very observation.
        height_cmd = r._get_effective_height_cmd().clone()[:, None]
        obs_height = r._get_observed_height()[:, None]
        r.wheel_relative_ground_heights = r._get_wheel_relative_ground_heights_raw()
        r.state_machine_manager.on_observation_step(r)
        mode = r._get_ctrl_mode_obs_raw()
        actor, critic = raw['policy'], raw['critic']
        if actor.shape != (self.n, 35) or critic.shape != (self.n, 38):
            raise ValueError('Unexpected MOD4 observation layout')
        # Unscale only the known MOD4 measurement fields; command/height/actions
        # come from the exact SCUT lifecycle, not stale manager placeholders.
        clean = torch.cat((critic[:, :7], critic[:, 10:]), -1)
        def blocks(value):
            return dict(command=r.command, height_cmd=height_cmd,
                root_ang_vel_b=value[:, 4:7]/.5, projected_gravity_b=value[:, 7:10],
                joint_pos=value[:, 10:16], joint_vel_leg=value[:, 16:20]/.1,
                joint_vel_wheel=value[:, 20:22]/.1, actions=r._actions)
        policy_blocks = blocks(actor)
        policy_blocks['ctrl_mode_obs'] = mode
        critic_blocks = blocks(clean)
        # env.py:3262-3295: 28 base, velocity3, height1, mode7, privileged39.
        # Placing mode before velocity/height preserves width78 but changes slots.
        critic_blocks.update(root_lin_vel_b=r.robot.data.root_lin_vel_b,
                             obs_height=obs_height, ctrl_mode_obs=mode)
        r.cache_raw_observations(policy_blocks, critic_blocks)
        def encode(blocks_, stream):
            return torch.cat([observation_component(r.cfg, key, value, stream)
                              for key, value in blocks_.items()], -1)
        policy = encode(policy_blocks, 'policy')
        obs = encode(critic_blocks, 'critic')
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
        extra = encode(dict(fields), 'critic')
        if extra.shape[-1] != 39:
            raise ValueError('SCUT privileged39 field layout mismatch')
        return dict(policy=torch.nan_to_num(policy, nan=0., posinf=0., neginf=0.),
                    critic=torch.nan_to_num(torch.cat((obs, extra), -1), nan=0., posinf=0., neginf=0.))

    def close(self):
        self.env.scene.update = self.original_update
        self.env.reward_manager.compute = self.original_reward
        self.env.termination_manager.compute = self.original_done
        self.env._reset_idx = self.original_reset
        self.env.command_manager.compute = self.original_command_compute
