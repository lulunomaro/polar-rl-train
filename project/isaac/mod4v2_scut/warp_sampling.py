"""Device-resident sampling path on the current PhysX simulator.

Follows basic_loco_lib's Warp equivalents and preallocated outputs, with CUDA
graphs for the contact+acceptance work. This does not label PhysX as Newton.
Actual simulation, sensors, actions, DR and reset ordering remain upstream.
"""
import types
import torch
import warp as wp
from . import warp_kernels as kernels


def array(value):
    return wp.from_torch(value if torch.is_tensor(value) else wp.to_torch(value))


class Dispatch:
    def __init__(self, device, graphs=True):
        wp.init()
        self.device = str(device)
        self.graphs = graphs and self.device.startswith('cuda')
        self.cache = {}
        self.captures = {}
        self.stream = wp.Stream(self.device) if self.device.startswith('cuda') else None
        wp.load_module(module=kernels, device=self.device)

    def run(self, name, calls, count):
        torch_stream = wp.stream_from_torch(torch.cuda.current_stream(self.device)) if self.stream else None
        stream = self.stream
        if stream:
            stream.wait_stream(torch_stream)
        def launch():
            for kernel, args in calls:
                wp.launch(kernel, dim=count, inputs=args, device=self.device, stream=stream)
        if not self.graphs:
            launch()
            if stream:
                torch_stream.wait_stream(stream)
            return
        signature = tuple((kernel.key, tuple((arg.ptr, arg.shape, arg.strides, str(arg.dtype))
                          if isinstance(arg, wp.array) else arg for arg in args)) for kernel, args in calls)
        previous = self.cache.get(name)
        if previous is None or previous[0] != signature:
            with wp.ScopedCapture(stream=stream, force_module_load=True) as capture:
                launch()
            previous = signature, capture.graph
            self.cache[name] = previous
            self.captures[name] = self.captures.get(name, 0) + 1
        wp.capture_launch(previous[1], stream=stream)
        torch_stream.wait_stream(stream)


class FudanReward:
    def __init__(self, reward, dispatch):
        self.reward, self.dispatch = reward, dispatch
        n, device = reward.num_envs, reward.device
        if set(reward.cfg.rewards) != set(kernels.TERMS):
            raise ValueError('Warp sampling requires the pinned 16-term Fudan recipe')
        self.raw = torch.empty(n, 16, device=device)
        self.raw_flight = torch.empty(n, dtype=torch.bool, device=device)
        self.weighted = torch.empty_like(self.raw)
        self.sums = torch.stack([reward._episode_sums.get(name, torch.zeros(n, device=device))
                                 for name in kernels.TERMS], -1)
        self.total = torch.empty(n, device=device)
        self.weights = torch.tensor([reward.cfg.rewards[name] for name in kernels.TERMS], device=device)
        self.wheels = torch.tensor(reward._wheel_link_idx, dtype=torch.int32, device=device)
        self.collisions = torch.tensor(reward._reset_contact_link_idx, dtype=torch.int32, device=device)
        self.motors = torch.tensor(reward._actuate_idx, dtype=torch.int32, device=device)
        self.anchors = torch.tensor([reward.contract['joints'][side+'_hip']['local_pos0']
                                     for side in ('left', 'right')], device=device)
        self.inputs = {}
        # Keep all original checkpoint-visible fields and per-term dictionary names.
        for k, name in enumerate(kernels.TERMS):
            reward._episode_sums[name] = self.sums[:, k]
        reward.raw_terms = {name: self.raw[:, k] for k, name in enumerate(kernels.TERMS)}
        reward.raw_terms['flight'] = self.raw_flight
        reward._last_reward_terms = {name: self.weighted[:, k] for k, name in enumerate(kernels.TERMS)}

    def compute(self):
        r, d = self.reward, self.reward.robot.data
        args = [d.root_pos_w, d.root_quat_w, d.root_lin_vel_w, d.root_lin_vel_b,
                d.root_ang_vel_b, d.projected_gravity_b, d.body_pos_w,
                r.contact_sensor.data.net_forces_w, self.wheels, self.collisions,
                self.motors, self.anchors, d.applied_torque, r._actions, r._previous_actions,
                r.command, r.fudan_last_contacts, r.fudan_contact_filt, r.fudan_was_in_flight,
                r.fudan_base_air_time, r.fudan_leg_length, r.fudan_leg_theta,
                self.weights, self.raw, self.weighted, self.sums, self.total]
        # Upstream clones commands/actions and refreshes simulator data each
        # control. Stage those changing inputs into stable addresses once; the
        # fused graph can then replay instead of recapturing every control.
        for k in (0, 1, 2, 3, 4, 5, 6, 7, 12, 13, 14, 15):
            value = args[k]
            if k not in self.inputs:
                self.inputs[k] = torch.empty_like(value)
            self.inputs[k].copy_(value)
            args[k] = self.inputs[k]
        self.dispatch.run('fudan_reward', [(kernels.fudan, [array(v) for v in args])], r.num_envs)
        self.raw_flight.copy_(r.fudan_was_in_flight)
        # Retain the exact source command-tail order and one update per control.
        r.command_generator.compute(r.step_dt)
        r._resample_custom_cmd(r.command_generator.command_counter)
        r.command = r.command_generator.command.clone()
        r._on_command_updated()
        r._last_total_reward = self.total.detach()
        return self.total


class PhysicsEndpoints:
    def __init__(self, bridge, dispatch):
        self.bridge, self.dispatch = bridge, dispatch
        r, device = bridge.reward, bridge.device
        self.wheels = torch.tensor(r._wheel_link_idx, dtype=torch.int32, device=device)
        self.nonwheels = torch.tensor(r._nonwheel_contact_link_idx, dtype=torch.int32, device=device)
        self.error = torch.zeros(1, dtype=torch.int32, device=device)
        from .math_ops import quat_apply
        geometry = [r.contract['geometry'][side+'_tire'] for side in ('left', 'right')]
        for g in geometry:
            if g['type'] != 5:
                raise ValueError('Expected authored MOD4 tire cylinders')
        q = torch.tensor([g['quat_wxyz'] for g in geometry], device=device)
        self.axes = quat_apply(q, q.new_tensor([[0., 0., 1.], [0., 0., 1.]]))
        self.offsets = q.new_tensor([g['position_m'] for g in geometry])
        self.radii = q.new_tensor([g['size'][0] for g in geometry])
        self.widths = q.new_tensor([g['size'][1] for g in geometry])
        self.calls = []
        for i, sensor in enumerate(bridge.top_sensors):
            if list(sensor.body_names) != [('left', 'right')[i]+'_wheel'] or sensor.contact_view.filter_count < 1:
                raise ValueError('Expected explicit wheel/course manifold filters')
        self.contacts = torch.empty(bridge.n, len(bridge.current_contact_order), 3, device=device)
        self.contact_order = torch.tensor(bridge.current_contact_order, device=device)
        self.body_pos = torch.empty_like(r.robot.data.body_pos_w)
        self.body_quat = torch.empty_like(r.robot.data.body_quat_w)
        self.root_quat = torch.empty_like(r.robot.data.root_quat_w)
        self.velocity = torch.empty_like(r.robot.data.root_lin_vel_w)
        self.active = torch.ones(bridge.n,dtype=torch.bool,device=device)

    def read_manifold(self):
        b = self.bridge
        self.calls = []
        for wi, sensor in enumerate(b.top_sensors):
            force, point, normal, separation, counts, starts = sensor.contact_view.get_contact_data(dt=.0025)
            force = wp.to_torch(force).flatten()
            point, normal = point.view(wp.vec3), normal.view(wp.vec3)
            count = wp.to_torch(counts.view(wp.int32)).reshape(b.n, -1)
            start = wp.to_torch(starts.view(wp.int32)).reshape(b.n, -1)
            self.calls.append((kernels.manifold, [array(force), point, normal, array(count), array(start),
                array(b.env.scene.env_origins), wi, array(b.top_force), array(b.ground_force),
                array(b.surface_force), array(b.surface_height), array(self.error)]))

    def measure_acceptance(self):
        b, a, r = self.bridge, self.bridge.acceptance, self.bridge.reward
        d = r.robot.data
        torch.index_select(b.tensor(b.current_sensor.data.net_forces_w), 1,
                           self.contact_order, out=self.contacts)
        self.body_pos.copy_(d.body_pos_w)
        self.body_quat.copy_(d.body_quat_w)
        self.root_quat.copy_(d.root_quat_w)
        self.velocity.copy_(d.root_lin_vel_w)
        args = [self.body_pos, self.body_quat, self.root_quat, self.velocity,
                b.env.scene.env_origins, self.contacts, self.wheels, self.nonwheels, self.axes,
                self.offsets, self.radii, self.widths, b.top_force, b.ground_force,
                a.success, a.wholeclear, a.leading, a.ground_seen, a.previous_air, a.up,
                a.current_clear, a.failed_return, a.landed_top, a.flight_id,
                a.stable_ticks, a.stable_peak, a.support_ticks, a.support_peak, a.initial_yaw,self.active]
        calls = [*self.calls, (kernels.acceptance, [array(v) for v in args])]
        self.dispatch.run('physics_endpoint', calls, b.n)

    def check_manifold(self):
        # Source synchronized twice per physics tick. Keep its actual bound
        # check before a control endpoint can reach PPO, with one read per control.
        if bool(self.error.any()):
            raise RuntimeError('Manifold buffer capacity/count mismatch')


def install(bridge, graphs=True):
    if bridge.profile != 'jump200' or not getattr(bridge.reward.cfg, 'fudan_jump_reward', False):
        raise ValueError('This sampling path is only for current MOD4v2 Fudan jump200')
    dispatch = Dispatch(bridge.device, graphs=graphs)
    endpoints = PhysicsEndpoints(bridge, dispatch)
    reward = FudanReward(bridge.reward, dispatch)
    bridge.read_manifold = endpoints.read_manifold
    bridge.measure_acceptance = endpoints.measure_acceptance
    original_prepare = bridge.prepare_endpoint
    def prepare():
        endpoints.check_manifold()
        return original_prepare()
    bridge.prepare_endpoint = prepare
    bridge.reward.compute = reward.compute
    bridge.warp_sampling = types.SimpleNamespace(dispatch=dispatch, endpoints=endpoints, reward=reward)
    return dict(implementation='MOD4V2_FUDAN_WARP_SAMPLING_V1', physics_backend='PhysX_TGS32_4',
        basic_loco_lib_commit='e4181af587330d0b70ca72e0d36b49be32e12a65',
        fused=['400Hz_manifold', '400Hz_jump200_acceptance', '50Hz_Fudan16terms'],
        cuda_graphs=dispatch.graphs, preallocated_GPU_outputs=True,
        unchanged=['physics', 'CAD', 'actuators', 'DR', 'policy', 'commands', 'reward_equations'],
        full_Newton_backend_migrated=False)
