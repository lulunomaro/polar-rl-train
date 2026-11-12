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
from .acceptance import Strict270, wheel_bounds
from .course import BOXES, HEIGHT, POSE_RANGE, SPAWN_HEIGHT, FourSideStrict270, top_mask
from .rough_terrain import scut_rough_terrain_cfg

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


def configure(cfg, n, profile='trained_stair'):
    """Attach either the pinned SCUT rough terrain or the legacy fixed 270 course.

    For ``trained_stair`` the only task substitution is the MOD4V1 USD/plant;
    the saved SCUT terrain generator, command recipe, reward dict and state
    configuration are read from the pinned 2026-07-30 env.yaml.  The fixed
    270 mm course remains available only under the explicitly different
    ``jump270`` profile.
    """
    global COURSE_N, MESH
    from isaaclab.sensors import ContactSensorCfg, RayCasterCfg, patterns
    from isaaclab.managers import RewardTermCfg

    COURSE_N = n
    if profile == 'trained_stair':
        MESH = '/World/ground'
        cfg.scene.num_envs = n
        cfg.scene.env_spacing = 4.0
        cfg.scene.ground = scut_rough_terrain_cfg(n)
        cfg.scene.robot.init_state.pos = (0., 0., SPAWN_HEIGHT)
    else:
        MESH = '/World/ground/scut_step270'
        cfg.scene.num_envs, cfg.scene.env_spacing = n, 8.
        cfg.scene.ground.spawn.func = spawn_course
        cfg.scene.ground.init_state.pos = (0., 0., 0.)
        cfg.scene.robot.init_state.pos = (0., 0., SPAWN_HEIGHT)

    cfg.scene.scut_contacts = ContactSensorCfg(
        prim_path='{ENV_REGEX_NS}/Robot/links/.*', update_period=.005,
        history_length=3, track_air_time=False)
    cfg.scene.scut_current = ContactSensorCfg(
        prim_path='{ENV_REGEX_NS}/Robot/links/.*', update_period=0.,
        history_length=1, track_air_time=False)
    if profile != 'trained_stair':
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
    # Keep the deployed MOD4 plant's validated 400 Hz physics and 50 Hz policy
    # clock.  SCUT's stored 200 Hz sample is not replayed on a different plant.
    cfg.decimation, cfg.sim.dt, cfg.sim.render_interval = 8, .0025, 8
    cfg.sim.physics.solver_type = 1
    cfg.scene.robot.spawn.articulation_props.solver_position_iteration_count = 32
    cfg.scene.robot.spawn.articulation_props.solver_velocity_iteration_count = 4
    cfg.terminations.closure.params['threshold'] = .01
    cfg.terminations.mimic.params['threshold'] = .01
    cfg.terminations = SimpleNamespace(closure=cfg.terminations.closure,
                                      mimic=cfg.terminations.mimic)
    cfg.scene.chassis_contact.filter_prim_paths_expr = [MESH]
    cfg.events.reset_base.params.update(
        pose_range=dict(POSE_RANGE),
        velocity_range={k: (0., 0.) for k in ('x', 'y', 'z', 'roll', 'pitch', 'yaw')})
    cfg.commands.twist = build_command_cfg(profile)
    return cfg


class ScutBridge:
    def __init__(self, env, task, contract, tensor, profile='trained_stair'):
        self.env, self.task, self.tensor = env, task, tensor
        self.profile = profile
        self.rough = profile == 'trained_stair'
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
        self.top_sensors = ([] if self.rough else
                            [env.scene['scut_top_'+s] for s in ('left', 'right')])
        self.top_force = torch.zeros(self.n, 2, device=self.device)
        self.ground_force = self.top_force.clone()
        self.physics_ticks = 0
        self.terminal_snapshot = None
        self.pending_actions = torch.zeros(self.n, 6, device=self.device)
        self.last_reward = torch.zeros(self.n, device=self.device)
        # Exact SCUT predefined-air reset command limits.  These are execution
        # limits from the saved run, not reward terms.
        self.air_cmd_remaining = torch.zeros(self.n, device=self.device)
        self.air_cmd_vx = torch.stack((torch.full((self.n,), float('-inf'), device=self.device),
                                       torch.full((self.n,), float('inf'), device=self.device)), -1)
        self.air_cmd_vy = self.air_cmd_vx.clone()
        self.air_cmd_wz = self.air_cmd_vx.clone()
        self.air_cmd_h = self.air_cmd_vx.clone()
        self.reset_scan_pending = torch.ones(self.n, dtype=torch.bool, device=self.device)
        self.scan_max_distance = ground_scan_config()['max_distance']
        self.acceptance = None if self.rough else FourSideStrict270(self.n, self.device)
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
        if not self.rough:
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
            if not self.rough:
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
                if not self.rough:
                    self.completed_strict += int(self.acceptance.success[ids].sum())
                saved_log = self.log_reset(ids)
            self.reward.reset(ids)
            self.top_force[ids] = 0
            self.ground_force[ids] = 0
            if not self.rough:
                self.acceptance.reset(ids)
            result = self.original_reset(ids)
            self._reset_predefined_air(ids)
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
        log['Metrics/strict270_completed'] = self.completed_strict
        log['Metrics/episodes_completed'] = self.completed_episodes
        return log

    def measure_acceptance(self):
        if self.rough:
            return
        r = self.reward
        body = r.robot.data
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
        from isaaclab.sensors.ray_caster.ray_caster import RayCaster
        mesh = RayCaster.meshes.get(MESH)
        if mesh is None:
            candidates = []
            for key in RayCaster.meshes:
                path = key[0] if isinstance(key, tuple) and len(key) > 0 else key
                if isinstance(path, str) and (path == MESH or path.startswith(MESH)):
                    candidates.append(key)
            if len(candidates) != 1:
                raise KeyError(f'Cannot resolve RayCaster mesh under {MESH}: {list(RayCaster.meshes)}')
            mesh = RayCaster.meshes[candidates[0]]
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

    @staticmethod
    def _range_pair(value, default=(0.0, 0.0)):
        if value is None:
            return float(default[0]), float(default[1])
        return float(value[0]), float(value[1])

    def _inverse_kinematics(self, leg_length, leg_angle):
        """SCUT leg inverse kinematics, using the saved link lengths/offsets."""
        cfg = self.reward.cfg
        links = torch.tensor(cfg.links_length, dtype=torch.float, device=self.device)
        offsets = torch.tensor(cfg.alpha_offset, dtype=torch.float, device=self.device)
        l2 = links.square()
        ll2 = leg_length.square()
        solve_arg = (
            (l2[0] * ll2 + l2[2] * (l2[0] - l2[1]))
            / (2. * links[2] * l2[0] * leg_length)
        ).clamp(-1. + 1.e-6, 1. - 1.e-6)
        solve = torch.arccos(solve_arg)
        alpha = torch.zeros((*leg_length.shape, 6), dtype=torch.float, device=self.device)
        alpha[..., 0] = leg_angle + .5 * torch.pi - solve
        alpha[..., 1] = leg_angle + .5 * torch.pi + solve
        inner_arg = (
            (l2[0] + l2[1] - l2[0] * ll2 / l2[2])
            / (2. * links[0] * links[1])
        ).clamp(-1. + 1.e-6, 1. - 1.e-6)
        alpha[..., 2] = torch.arccos(inner_arg)
        alpha[..., 3] = 2. * torch.pi - (alpha[..., 1] - alpha[..., 0]) - 2. * alpha[..., 2]
        alpha[..., 4] = alpha[..., 2]
        alpha[..., 5] = alpha[..., 2]
        alpha[..., 0] -= offsets[0]
        alpha[..., 1] -= offsets[1]
        alpha[..., 2] = -(alpha[..., 2] - offsets[2])
        alpha[..., 3] = -(alpha[..., 3] - offsets[3])
        alpha[..., 4] = -(alpha[..., 4] - offsets[4])
        alpha[..., 5] -= offsets[5]
        return alpha

    def _randomize_reset_joints(self, ids, air_mask=None, air_length_range=None, air_angle_range=None):
        cfg = self.reward.cfg
        if not bool(getattr(cfg, 'mod4_scut_ik_reset_enabled', False)):
            return
        if not bool(getattr(cfg, 'use_leg_random_start', False)):
            return
        n = len(ids)
        base_length = self._range_pair(getattr(cfg, 'leg_length_range', (0.13, 0.32)))
        base_angle = self._range_pair(getattr(cfg, 'leg_angle_range', (-1.57, 2.35)))
        length = torch.empty((n, 2), device=self.device).uniform_(*base_length)
        angle = torch.empty((n, 2), device=self.device).uniform_(*base_angle)
        if air_mask is not None and bool(air_mask.any()):
            air_length = self._range_pair(air_length_range or base_length)
            air_angle = self._range_pair(air_angle_range or base_angle)
            length[air_mask] = torch.empty((int(air_mask.sum()), 2), device=self.device).uniform_(*air_length)
            angle[air_mask] = torch.empty((int(air_mask.sum()), 2), device=self.device).uniform_(*air_angle)
        joint12 = torch.nan_to_num(
            self._inverse_kinematics(length, angle).transpose(-2, -1).reshape(n, 12),
            nan=0.0, posinf=0.0, neginf=0.0,
        )
        active_legs = joint12[:, [0, 2, 1, 3]]
        # MOD4 actuator limits are tighter than SCUT's sampled IK range.  Clamp
        # only the reset target to the shipped contract to prevent a solver NaN;
        # reward/state-machine values remain pinned.
        limits = self.robot.data.joint_pos_limits[ids][:, self.reward._legs_act_idx]
        active_legs = torch.minimum(torch.maximum(active_legs, limits[..., 0]), limits[..., 1])
        valid = torch.isfinite(active_legs).all(-1)
        defaults = self.robot.data.default_joint_pos[ids][:, self.reward._legs_act_idx]
        active_legs = torch.where(valid[:, None], active_legs, defaults)
        self.robot.write_joint_state_to_sim(active_legs, torch.zeros_like(active_legs),
                                            self.reward._legs_act_idx, ids)
        wheel_angle = self._range_pair(getattr(cfg, 'wheel_angle_range', (-6.283, 6.283)))
        wheels = torch.empty((n, 2), device=self.device).uniform_(*wheel_angle)
        self.robot.write_joint_state_to_sim(wheels, torch.zeros_like(wheels),
                                            self.reward._wheel_idx, ids)
        if bool(getattr(cfg, 'use_joint_vel_random_start', False)):
            leg_vel = torch.empty((n, 4), device=self.device).uniform_(*self._range_pair(getattr(cfg, 'leg_joint_vel_range', (-1.57, 1.57))))
            wheel_vel = torch.empty((n, 2), device=self.device).uniform_(*self._range_pair(getattr(cfg, 'wheel_joint_vel_range', (-50., 50.))))
            self.robot.write_joint_velocity_to_sim(leg_vel, self.reward._legs_act_idx, ids)
            self.robot.write_joint_velocity_to_sim(wheel_vel, self.reward._wheel_idx, ids)

    def _reset_predefined_air(self, ids):
        """Apply the saved SCUT predefined airborne reset modes.

        The original SCUT run samples z/roll/pitch/yaw, body-frame velocity and
        a short command window for a fraction of resets.  This method only
        changes reset state; reward/state-machine configuration remains pinned.
        """
        cfg = getattr(self.reward.cfg, 'predefined_reset_air', {})
        self.air_cmd_remaining[ids] = 0.0
        if not isinstance(cfg, dict) or not bool(cfg.get('enabled', False)):
            self._randomize_reset_joints(ids)
            return
        raw_modes = cfg.get('modes', ())
        if isinstance(raw_modes, dict):
            raw_modes = [raw_modes]
        modes = [m for m in (raw_modes or ()) if isinstance(m, dict)]
        if not modes:
            return
        fn = getattr(self.env, '_get_training_iteration', None)
        iteration = int(fn()) if callable(fn) else int(getattr(self.env, '_training_iteration', 0))
        modes = [m for m in modes
                 if iteration >= int(m.get('iteration_start', 0))
                 and (int(m.get('iteration_end', -1)) < 0
                      or iteration < int(m.get('iteration_end', -1)))]
        if not modes:
            return
        sample = torch.rand(len(ids), device=self.device)
        air_mask = torch.zeros(len(ids), dtype=torch.bool, device=self.device)
        air_length_range = modes[0].get('leg_length_range', getattr(self.reward.cfg, 'leg_length_range', None))
        air_angle_range = modes[0].get('leg_angle_range', getattr(self.reward.cfg, 'leg_angle_range', None))
        cursor = 0.0
        for mode in modes:
            prob = min(max(float(mode.get('prob', 0.0)), 0.0), 1.0)
            nxt = min(cursor + prob, 1.0)
            mask = (sample >= cursor) & (sample < nxt)
            cursor = nxt
            air_mask[mask] = True
            selected = ids[mask]
            if selected.numel() == 0:
                continue
            from isaaclab.utils.math import (
                quat_apply as q_apply,
                quat_from_euler_xyz as q_euler,
                quat_mul as q_mul,
            )
            base = self.robot.data.default_root_state[selected].clone()
            base[:, :3] += self.env.scene.env_origins[selected]
            n = selected.numel()
            pose_range = mode.get('pose_range', {})
            pose_keys = ('x', 'y', 'z', 'roll', 'pitch', 'yaw')
            pose_lo = torch.tensor([self._range_pair(pose_range.get(k), (0., 0.))[0]
                                    for k in pose_keys], device=self.device)
            pose_hi = torch.tensor([self._range_pair(pose_range.get(k), (0., 0.))[1]
                                    for k in pose_keys], device=self.device)
            pose = pose_lo + torch.rand((n, 6), device=self.device) * (pose_hi - pose_lo)
            pos = base[:, :3] + pose[:, :3]
            root_q = base[:, 3:7]
            delta_q = q_euler(pose[:, 3], pose[:, 4], pose[:, 5])
            new_q = q_mul(root_q, delta_q)
            yaw_q = q_euler(torch.zeros(n, device=self.device),
                            torch.zeros(n, device=self.device), pose[:, 5])
            vel_q = q_mul(root_q, yaw_q)
            vrange = mode.get('velocity_range', {})
            vkeys = ('x', 'y', 'z', 'roll', 'pitch', 'yaw')
            vlo = torch.tensor([self._range_pair(vrange.get(k), (0., 0.))[0]
                                for k in vkeys], device=self.device)
            vhi = torch.tensor([self._range_pair(vrange.get(k), (0., 0.))[1]
                                for k in vkeys], device=self.device)
            vel = vlo + torch.rand((n, 6), device=self.device) * (vhi - vlo)
            vel[:, :3] = q_apply(vel_q, vel[:, :3])
            vel = base[:, 7:13] + vel
            self.robot.write_root_pose_to_sim(torch.cat((pos, new_q), -1), env_ids=selected)
            self.robot.write_root_velocity_to_sim(vel, env_ids=selected)
            limits = mode.get('command_limits', {})
            duration = max(float(limits.get('duration_s', 0.0)), 0.0)
            if duration <= 0.0:
                continue
            self.air_cmd_remaining[selected] = duration
            for key, buf in (('lin_vel_x', self.air_cmd_vx),
                             ('lin_vel_y', self.air_cmd_vy),
                             ('ang_vel_z', self.air_cmd_wz),
                             ('height', self.air_cmd_h)):
                pair = limits.get(key, None)
                if pair is not None:
                    buf[selected, 0] = float(pair[0])
                    buf[selected, 1] = float(pair[1])
            if cursor >= 1.0:
                break

        self._randomize_reset_joints(ids, air_mask, air_length_range, air_angle_range)

    def _apply_air_command_limits(self):
        active = self.air_cmd_remaining > 0.0
        if not bool(active.any()):
            return
        r = self.reward
        r.command[:, 0] = torch.maximum(torch.minimum(r.command[:, 0], self.air_cmd_vx[:, 1]),
                                         self.air_cmd_vx[:, 0])
        r.command[:, 1] = torch.maximum(torch.minimum(r.command[:, 1], self.air_cmd_vy[:, 1]),
                                         self.air_cmd_vy[:, 0])
        r.command[:, 2] = torch.maximum(torch.minimum(r.command[:, 2], self.air_cmd_wz[:, 1]),
                                         self.air_cmd_wz[:, 0])
        r.height_cmd = torch.maximum(torch.minimum(r.height_cmd, self.air_cmd_h[:, 1]),
                                     self.air_cmd_h[:, 0])
        self.air_cmd_remaining[active] -= .02
        self.air_cmd_remaining.clamp_min_(0.0)

    def refresh_observation_context(self):
        """Original post-reward observation hook, once per returned observation."""
        r = self.reward
        r._cached_wheel_kinematics_valid = False
        r.finish_observation()  # env.py:3107-3108, before command/state hooks
        r.command = self.env.command_manager.get_command('twist').clone()
        r.height_cmd = self.task.height_cmd(self.env).reshape(-1).clone()
        self._apply_air_command_limits()
        r.episode_length_buf.copy_(self.env.episode_length_buf)
        ids = self.reset_scan_pending.nonzero(as_tuple=False).flatten()
        if len(ids):
            r.refresh_reset_scans(ids, *self.read_reward_scans(ids))
            self.reset_scan_pending[ids] = False
        r._on_command_updated()

    def read_manifold(self):
        """Read actual400Hz normal force, points and normals for strict evaluation."""
        if self.rough:
            return
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
            top = valid & upward & top_mask(pts)
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
                    strict270=(torch.zeros(self.n, dtype=torch.bool, device=self.device)
                               if self.rough else self.acceptance.success.clone()),
                    first_flight_wholeclear=(torch.zeros(self.n, dtype=torch.bool, device=self.device)
                                             if self.rough else self.acceptance.wholeclear.clone()),
                    first_flight_leading=(torch.zeros(self.n, dtype=torch.bool, device=self.device)
                                          if self.rough else self.acceptance.leading.clone()),
                    longest_stable_seconds=(torch.zeros(self.n, device=self.device)
                                            if self.rough else self.acceptance.stable_peak.clone()*.0025),
                    longest_valid_top_seconds=(torch.zeros(self.n, device=self.device)
                                               if self.rough else self.acceptance.support_peak.clone()*.0025),
                    physics_ticks=self.physics_ticks)

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
