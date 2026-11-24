"""Warp dynamics and training-only rewards for the R4 solid platforms."""
import math

import mujoco_warp as mjw
import numpy as np
import torch
import warp as wp

from jump360_gpu import JumpGpu, extent, motor
from jump360_scene import CLOSURE_LIMIT, HURDLE_THICKNESS, mujoco
from jump380_r4_scene import HEIGHTS, KINDS, Jump380Plant

DR_LEVELS = (0., .50, 1.)
SPEED_CENTERS = (.8, 1., 1.2, 1.4, 1.6, 1.8, 2.)
FIELDS = ("trials", "falls", "landed_running", "qualified", "clearance_385",
          "forward", "wheel_crossing_in_main_flight", "valid_platform_support",
          "hold_50", "hold_50_landed_running")
PHASES = ("key_down", "released_before_first_support", "held_after_first_support",
          "platform_380_both_support", "platform_360_both_support", "platform_beyond_before_chassis",
          "nonfinite_world_resets", "platform_approach", "platform_push", "stable_cruise")


@wp.kernel
def gather_contacts(
    nacon: wp.array(dtype=wp.int32), ids: wp.array(dtype=wp.vec2i),
    world: wp.array(dtype=wp.int32), frames: wp.array(dtype=wp.mat33),
    pos: wp.array(dtype=wp.vec3), dim: wp.array(dtype=wp.int32),
    address: wp.array2d(dtype=wp.int32), nefc: wp.array(dtype=wp.int32),
    force: wp.array2d(dtype=float), classifications: wp.array(dtype=wp.int32),
    wall_height: wp.array(dtype=float), out: wp.array2d(dtype=float),
):
    i = wp.tid()
    if i >= nacon[0]:
        return
    ab = ids[i]
    a = int(classifications[ab[0]])
    b = int(classifications[ab[1]])
    if (a < 0) == (b < 0) or address[i, 0] < 0:
        return
    w = world[i]
    limit = wp.min(nefc[w], force.shape[1])
    normal_index = address[i, 0]
    if normal_index >= limit:
        return
    frame = wp.mat33(frames[i])
    normal = wp.vec3(frame[0, 0], frame[0, 1], frame[0, 2])
    # Elliptic cone: each local force component uses its own world-local row.
    local_force = wp.vec3(force[w, normal_index], 0., 0.)
    for axis in range(1, wp.min(dim[i], 3)):
        index = address[i, axis]
        if index >= 0 and index < limit:
            local_force[axis] = force[w, index]
    f = wp.length(local_force)
    if not wp.isfinite(f):
        wp.atomic_add(out, w, 8, 1.)
        return
    fixed = int(a)
    robot = int(b)
    if b < 0:
        fixed = b
        robot = a
    wp.atomic_add(out, w, 0, f)
    if robot == 1 or robot == 2:
        support = wp.abs(local_force[0] * normal[2])
        wp.atomic_add(out, w, robot, support)
        if (fixed == -2 or fixed == -3) and wp.abs(normal[2]) > .65 and pos[i][2] >= wall_height[w] - .012:
            wp.atomic_add(out, w, robot+5, support)
    if robot == 3:
        wp.atomic_add(out, w, 3, f)
    if fixed <= -2:
        wp.atomic_add(out, w, 5, f)
        if wp.abs(normal[0]) > .35 and pos[i][2] < wall_height[w] - .004:
            wp.atomic_add(out, w, 4, f)


@wp.kernel
def gather_frame(
    qvel: wp.array2d(dtype=float), points: wp.array2d(dtype=wp.vec3),
    frames: wp.array2d(dtype=wp.mat33), xmat: wp.array2d(dtype=wp.mat33),
    size: wp.array(dtype=wp.vec3), geometry: wp.array(dtype=wp.int32),
    contact: wp.array2d(dtype=float), sites: wp.array2d(dtype=wp.vec3),
    left_site: wp.array(dtype=wp.int32), right_site: wp.array(dtype=wp.int32),
    pair_count: int, base_id: int, press: wp.array(dtype=wp.int64),
    edge: wp.array(dtype=float), wall_height: wp.array(dtype=float),
    arc: wp.array2d(dtype=float), tick_stats: wp.array2d(dtype=float),
):
    w = wp.tid()
    low = float(99.)
    least_x = float(99.)
    lagging_wheel_x = float(99.)
    tires = float(99.)
    for j in range(geometry.shape[0]):
        g = geometry[j]
        origin = wp.vec3(points[w, g])
        rotation = wp.mat33(frames[w, g])
        radius = wp.vec3(size[g])
        axis_z = wp.vec3(rotation[2,0],rotation[2,1],rotation[2,2])
        axis_x = wp.vec3(rotation[0,0],rotation[0,1],rotation[0,2])
        lowest = origin[2] - extent(radius, axis_z, j < 10)
        low = wp.min(low, lowest)
        least_x = wp.min(least_x, origin[0] - extent(radius, axis_x, j < 10))
        if j < 2:
            tires = wp.min(tires, lowest)
            lagging_wheel_x = wp.min(lagging_wheel_x, origin[0])
    r = xmat[w, base_id]
    pitch = wp.abs(wp.asin(wp.clamp(r[2, 0], -1., 1.)))
    normal = wp.sqrt(r[0, 0]**2.+r[1, 0]**2.)
    vx = (qvel[w, 0]*r[0, 0]+qvel[w, 1]*r[1, 0])/wp.max(normal, .0001)
    if press[w] >= 0 and arc[w, 1] < 2.:
        airborne = contact[w, 0] < 1. and low > .006
        if airborne:
            count = arc[w, 0]
            if count > 0. and arc[w, 6] < -8. and wall_height[w] > 0.:
                before = arc[w, 4]
                if before <= edge[w] and lagging_wheel_x > edge[w]:
                    alpha = (edge[w] - before) / (lagging_wheel_x - before)
                    arc[w, 6] = arc[w, 5] + alpha * (low - arc[w, 5]) - wall_height[w]
            arc[w, 0] = count + 1.
            arc[w, 2] = wp.max(arc[w, 2], low)
            arc[w, 3] = wp.max(arc[w, 3], pitch)
            arc[w, 4] = lagging_wheel_x
            arc[w, 5] = low
            if count >= 11.:
                arc[w, 1] = 1.
        elif arc[w, 1] == 1.:
            arc[w, 1] = 2.
        else:
            arc[w, 0] = 0.
            arc[w, 2] = 0.
            arc[w, 3] = 0.
            arc[w, 6] = -9.
        if arc[w, 1] == 0.:
            tick_stats[w, 10] = wp.min(tick_stats[w, 10], vx)
            tick_stats[w, 3] = wp.max(tick_stats[w, 3], contact[w, 3])
    if arc[w, 1] > 0.:
        tick_stats[w, 0] = arc[w, 2]
        tick_stats[w, 2] = arc[w, 3]
    tick_stats[w, 1] = wp.min(tick_stats[w, 1], vx)
    tick_stats[w, 4] = wp.max(tick_stats[w, 4], contact[w, 4])
    tick_stats[w, 5] = least_x
    tick_stats[w, 6] = tires
    close = float(0.)
    for j in range(pair_count):
        close = wp.max(close, wp.length(sites[w, left_site[j]] - sites[w, right_site[j]]))
    tick_stats[w, 7] = wp.max(tick_stats[w, 7], close)
    tick_stats[w, 8] = wp.max(tick_stats[w, 8], qvel[w, 2])
    tick_stats[w, 9] = wp.max(tick_stats[w, 9], contact[w, 5])
    tick_stats[w, 11] = vx
    tick_stats[w, 12] = wp.max(tick_stats[w, 12], contact[w, 8])
    tick_stats[w, 13] = lagging_wheel_x
    tick_stats[w, 14] = wp.max(tick_stats[w, 14], wp.abs(qvel[w, 2]))


class Jump380Gpu(JumpGpu):
    def __init__(self, count, seed, timing):
        self.device = "cuda:0"
        wp.set_device(self.device)
        self.warp_stream = wp.Stream(device=self.device)
        stream = torch.cuda.ExternalStream(self.warp_stream.cuda_stream, device=self.device)
        stream.wait_stream(torch.cuda.current_stream())
        torch.cuda.set_stream(stream)
        wp.set_stream(self.warp_stream)
        cpu = Jump380Plant(seed=seed)
        cpu.setup(.28)
        if cpu.m.opt.cone != mujoco.mjtCone.mjCONE_ELLIPTIC:
            raise ValueError("Expected the pinned elliptic contact cone")
        self.cpu = cpu
        self.m = mjw.put_model(cpu.m)
        self.m.opt.graph_conditional = False
        self.n = count
        self.d = mjw.put_data(cpu.m, cpu.d, nworld=count, nconmax=48, njmax=192)
        d, m = self.d, self.m
        self.index = torch.arange(count, device=self.device)
        tf = lambda value, dtype=torch.float32: torch.as_tensor(value, device=self.device, dtype=dtype)
        arr_i = lambda x: wp.array(x, dtype=wp.int32, device=self.device)
        self.tf = tf
        self.p = wp.to_torch(d.qpos)
        self.v = wp.to_torch(d.qvel)
        self.rot = wp.to_torch(d.xmat)[:, cpu.base_id]
        self.goal = tf(cpu.default_active)
        self.action_rom = wp.zeros((count, 6), device=self.device, dtype=float)
        self.action = wp.to_torch(self.action_rom)
        self.fifo = wp.zeros((count, 9, 6), device=self.device, dtype=float)
        self.fifo_t = wp.to_torch(self.fifo)
        self.stats_w = wp.zeros((count, 15), device=self.device, dtype=float)
        self.aux_w = wp.zeros((count, 9), device=self.device, dtype=float)
        self.stats = wp.to_torch(self.stats_w)
        self.contacts = wp.to_torch(self.aux_w)
        self.slot_wp = wp.zeros(1, dtype=wp.int32, device=self.device)
        self.slot = wp.to_torch(self.slot_wp)
        self.delay_wp = wp.zeros(count, dtype=wp.int32, device=self.device)
        self.delay = wp.to_torch(self.delay_wp)
        self.action_gain = tf(np.ones((count, 6), dtype=np.float32))
        self.derivative_gain = self.action_gain.clone()
        self.effort_scale = self.action_gain.clone()
        self.qadr, self.vadr = tf(cpu.active_qadr, torch.long), tf(cpu.active_dadr, torch.long)
        self.reset_q = tf(cpu.d.qpos.copy())
        self.nom_mass = tf(cpu.m.body_mass.copy())
        self.nom_ipos = tf(cpu.m.body_ipos.copy())
        self.nom_friction = tf(cpu.m.geom_friction.copy())
        m.body_mass = wp.array(np.tile(cpu.m.body_mass, (count, 1)), dtype=wp.float32)
        m.body_ipos = wp.array(np.tile(cpu.m.body_ipos, (count, 1, 1)), dtype=wp.vec3)
        m.geom_friction = wp.array(np.tile(cpu.m.geom_friction, (count, 1, 1)), dtype=wp.vec3)
        self.mass, self.ipos, self.friction = [wp.to_torch(x) for x in (m.body_mass, m.body_ipos, m.geom_friction)]
        self.mocap = wp.to_torch(d.mocap_pos)
        gen = torch.Generator(device=self.device)
        self.rng = gen.manual_seed(seed)
        self.previous = torch.zeros_like(self.action)
        self.obs = tf(np.zeros((count, 35)))
        self.hist = tf(np.zeros((count, 12, 35)))
        self.dr_probability = 0.
        self.dr = torch.zeros(count, device=self.device, dtype=torch.bool)
        self.tick = torch.zeros(count, device=self.device, dtype=torch.long)
        self.press = torch.full_like(self.tick, -1)
        self.kind = self.tick.clone()
        self.cmd = tf(np.zeros(count))
        self.speed = self.cmd.clone()
        self.height = self.cmd.clone()
        self.edge = self.cmd.clone()
        self.wall_height = self.cmd.clone()
        self.key_hold = self.tick.clone()
        self.lead = self.cmd.clone()
        self.timing_speed = tf(timing["speeds"])
        self.timing_height = tf(timing["heights"])
        self.timing_values = tf([timing[kind] for kind in KINDS[1:]])
        # Air samples, phase, peak, pitch, previous wheel x/low, margin at edge.
        self.arc = tf(np.zeros((count, 7)))
        self.peak = self.cmd.clone()
        self.max_pitch = self.cmd.clone()
        self.worst_vx = self.cmd.clone()
        self.begin_tick = self.tick.clone()
        self.episode_stage = self.tick.clone()
        self.support_streak = self.tick.clone()
        self.first_touch_tick = self.tick.clone()
        self.stable = torch.zeros_like(self.dr)
        self.platform_acquired = torch.zeros_like(self.dr)
        self.air_progress = self.cmd.clone()
        self.press_speed = self.cmd.clone()
        self.stage = 0
        self.heights_by_kind = tf(HEIGHTS)
        self.by_stage = torch.zeros((3, 2, 4, len(SPEED_CENTERS), len(FIELDS)), device=self.device)
        self.population_steps = torch.zeros((3, 2), dtype=torch.long, device=self.device)
        self.terrain_resets = torch.zeros(4, dtype=torch.long, device=self.device)
        self.hold_samples = torch.zeros(51, dtype=torch.long, device=self.device)
        self.phase_samples = torch.zeros(len(PHASES), dtype=torch.long, device=self.device)
        self.range_min = tf([99., 99., 99.])
        self.range_max = tf([-99., -99., -99.])
        self.face_events = torch.zeros(4, dtype=torch.long, device=self.device)
        self.scrape = self.cmd.clone()
        self.hits = self.cmd.clone()
        self.closure = self.cmd.clone()
        self.late_support = self.tick.clone()
        self.immediate = tf(np.zeros(8))
        lookup = np.zeros(cpu.m.ngeom, dtype=np.int32)
        lookup[cpu.ground_gid] = -1
        lookup[cpu.hurdle_gids] = [-2, -3, -4]
        lookup[cpu.groups[0]] = [1, 2]
        lookup[cpu.groups[1]+cpu.groups[2]] = 3
        self.wp_motor = [self.action_rom, self.fifo, self.delay_wp, arr_i(cpu.active_qadr), arr_i(cpu.active_dadr),
                         wp.from_torch(self.goal), d.qpos, d.qvel, d.ctrl, wp.from_torch(self.action_gain),
                         wp.from_torch(self.derivative_gain), wp.from_torch(self.effort_scale), self.slot_wp]
        self.wp_contact = [d.nacon, d.contact.geom, d.contact.worldid, d.contact.frame, d.contact.pos,
                           d.contact.dim, d.contact.efc_address, d.nefc, d.efc.force, arr_i(lookup),
                           wp.from_torch(self.wall_height), self.aux_w]
        self.wp_frame = [d.qvel, d.geom_xpos, d.geom_xmat, d.xmat, wp.array(cpu.m.geom_size, dtype=wp.vec3),
                         arr_i(cpu.measured_gids), self.aux_w, d.site_xpos,
                         arr_i(cpu.pairs_np[:, 0]), arr_i(cpu.pairs_np[:, 1]), len(cpu.pairs), cpu.base_id,
                         wp.from_torch(self.press), wp.from_torch(self.edge), wp.from_torch(self.wall_height),
                         wp.from_torch(self.arc), self.stats_w]
        self.reset(torch.ones(count, device=self.device, dtype=torch.bool))
        with wp.ScopedStream(self.warp_stream):
            self.substeps()
            wp.synchronize_device(self.device)
            with wp.ScopedCapture(device=self.device, stream=self.warp_stream) as capture:
                self.substeps()
            self.graph = capture.graph
        self.reset(torch.ones(count, device=self.device, dtype=torch.bool))
        self.observe()
        self.hist[:] = self.obs[:, None, :]

    def substeps(self):
        for offset in range(8):
            wp.launch(motor, (self.n, 6), self.wp_motor + [offset])
            mjw.step(self.m, self.d)
            self.aux_w.zero_()
            wp.launch(gather_contacts, self.d.naconmax, self.wp_contact)
            wp.launch(gather_frame, self.n, self.wp_frame)

    def lead_opt(self, speed, height, kind):
        def axis(grid, value):
            value = value.contiguous().clamp(grid[0], grid[-1])
            i = torch.searchsorted(grid, value, right=True).clamp(1, len(grid)-1)-1
            return i, (value-grid[i])/(grid[i+1]-grid[i])

        i, a = axis(self.timing_speed, speed)
        j, b = axis(self.timing_height, height)
        scene = (kind - 1).clamp_min(0)
        v = self.timing_values
        return torch.lerp(torch.lerp(v[scene, i, j], v[scene, i, j+1], b),
                          torch.lerp(v[scene, i+1, j], v[scene, i+1, j+1], b), a)

    def reset(self, done):
        ids = self.index[done]
        n = ids.numel()
        if not n:
            return
        d, m = self.d, self.m
        with wp.ScopedStream(self.warp_stream):
            mjw.reset_data(m, d, wp.from_torch(done.contiguous(), dtype=wp.bool))
        self.p[ids] = self.reset_q
        yaw = (self.rand(n)-.5)*.020
        self.p[ids, 3] = torch.cos(yaw*.5)
        self.p[ids, 6] = torch.sin(yaw*.5)
        self.p[ids, 1] = (self.rand(n)-.5)*.030
        self.previous[ids] = 0.
        self.fifo_t[ids] = 0.
        self.dr[ids] = self.rand(n) < self.dr_probability
        dr = self.dr[ids, None].float()
        self.mass[ids] = self.nom_mass*(1.+(self.rand(n, self.nom_mass.numel())-.5)*.24*dr)
        self.ipos[ids] = self.nom_ipos
        self.ipos[ids, self.cpu.base_id] += .05*(self.rand(n, 3)-.5)*dr
        self.friction[ids] = self.nom_friction
        mu = .9 + (self.rand(n)*.60-.35)*dr[:, 0]
        for g in [self.cpu.ground_gid, *self.cpu.hurdle_gids, *self.cpu.tire_gids]:
            self.friction[ids, g, 0] = torch.where(self.dr[ids], mu, self.nom_friction[g, 0])
        self.action_gain[ids] = 1.+.24*(self.rand(n, 6)-.5)*dr
        self.derivative_gain[ids] = 1.+.24*(self.rand(n, 6)-.5)*dr
        self.effort_scale[ids] = 1.+.20*(self.rand(n, 6)-.5)*dr
        self.delay[ids] = ((self.rand(n)*9.).long()*self.dr[ids]).to(torch.int32)
        self.speed[ids] = .80+1.20*self.rand(n)
        self.height[ids] = .24+.18*self.rand(n)
        # Include the minimum and maximum command values in each substantial reset.
        if n >= 16:
            self.speed[ids[:2]] = .80
            self.speed[ids[2:4]] = 2.
            self.height[ids[4:6]] = .24
            self.height[ids[6:8]] = .42
        self.cmd[ids] = 0.
        self.press[ids] = -1
        terrain = torch.randint(100, (n,), generator=self.rng, device=self.device)
        kind = torch.bucketize(terrain, terrain.new_tensor([20, 65, 90]), right=True)
        self.kind[ids] = kind
        self.wall_height[ids] = self.heights_by_kind[kind]
        self.terrain_resets.scatter_add_(0, kind, torch.ones_like(kind))
        hold = torch.randint(12, 51, (n,), generator=self.rng, device=self.device)
        self.key_hold[ids] = hold
        self.hold_samples.scatter_add_(0, hold, torch.ones_like(hold))
        jitter = .24*self.rand(n)-.12
        self.lead[ids] = self.lead_opt(self.speed[ids], self.height[ids], kind) + jitter
        self.range_min = torch.minimum(self.range_min, torch.stack((
            self.speed[ids].min(), self.height[ids].min(), jitter.min())))
        self.range_max = torch.maximum(self.range_max, torch.stack((
            self.speed[ids].max(), self.height[ids].max(), jitter.max())))
        self.begin_tick[ids] = 115 + (46*self.rand(n)).long()
        self.edge[ids] = (1.25 + .60*self.rand(n))*self.speed[ids] + self.lead[ids]
        self.episode_stage[ids] = self.stage
        self.support_streak[ids] = 0
        self.first_touch_tick[ids] = -1
        self.stable[ids] = False
        self.platform_acquired[ids] = False
        self.air_progress[ids] = 0.
        self.press_speed[ids] = 0.
        for j in range(3):
            active = self.kind[ids] == j+1
            half = self.cpu.m.geom_size[self.cpu.hurdle_gids[j]]
            self.mocap[ids, j, 0] = torch.where(active, self.edge[ids]+half[0], 4.)
            self.mocap[ids, j, 1] = 0.
            self.mocap[ids, j, 2] = torch.where(active, float(half[2]), -2.-j)
        self.tick[ids] = 0
        self.peak[ids] = 0.
        self.scrape[ids] = 0.
        self.hits[ids] = 0.
        self.closure[ids] = 0.
        self.max_pitch[ids] = 0.
        self.worst_vx[ids] = 20.
        self.late_support[ids] = 0
        self.arc[ids] = 0.
        self.arc[ids, 6] = -9.
        self.stats[ids] = 0.
        self.contacts[ids] = 0.


    def set_stage(self, stage):
        self.stage = stage
        self.dr_probability = DR_LEVELS[stage]

    def mode_target(self):
        # Supervision comes from physics. The deployed network receives only obs and history.
        return (self.press >= 0) & (self.arc[:, 1] < 2.) & ((self.tick - self.press) < 55)

    def annotate(self, done, failed, success, strict):
        speed_bin = ((self.speed - .70)*5.).floor().long().clamp(0, len(SPEED_CENTERS) - 1)
        group = (((self.episode_stage*2 + self.dr.long())*4 + self.kind)*len(SPEED_CENTERS) + speed_bin)
        forward = (self.worst_vx > 0.) & (self.press_speed > 0.) & (self.press >= 0)
        long_hold = self.key_hold == 50
        values = torch.stack((done, done & failed, success, strict, done & (self.peak >= .385),
                              done & forward, done & (self.arc[:, 6] >= 0.), done & self.platform_acquired,
                              done & long_hold, success & long_hold), dim=1).float()
        self.by_stage.flatten(0, 3).index_add_(0, group, values)
        self.population_steps.flatten().scatter_add_(0, self.episode_stage*2 + self.dr.long(),
                                                      torch.ones_like(group))

    def step(self, action):
        self.action.copy_(action.clamp(-6., 6.))
        self.stats.zero_()
        self.stats[:, 1] = 99.
        self.stats[:, 10] = 99.
        with wp.ScopedStream(self.warp_stream):
            wp.capture_launch(self.graph, self.warp_stream)
        self.slot.add_(8).remainder_(9)
        self.tick += 1

        broken = (~torch.isfinite(self.p).all(1) | ~torch.isfinite(self.v).all(1)
                  | ~torch.isfinite(self.rot).all(dim=(1, 2)) | ~torch.isfinite(self.stats).all(1)
                  | ~torch.isfinite(self.contacts).all(1) | (self.stats[:, 12] > 0.))
        info = torch.where(broken[:, None], 0., self.stats)
        obstacle = self.kind != 0
        platform = (self.kind == 1) | (self.kind == 2)
        hurdle = self.kind == 3
        triggered = self.press >= 0
        bit = self.obs[:, 30] > .5
        air = self.arc[:, 1] == 1.
        first_flight_ended = self.arc[:, 1] == 2.
        charge = triggered & ~broken & (info[:, 10] < 99.)
        upright = torch.where(broken, 0., self.rot[:, 2, 2])
        vx = info[:, 11]

        # Shaping only rewards new height on the main flight, relative to its floor.
        peak = torch.maximum(self.peak, info[:, 0])
        height_value = lambda height: (height / .385).clamp(0., 1.28).square()
        reward = torch.where(obstacle, 3.2, 6.)*(height_value(peak) - height_value(self.peak))
        self.peak.copy_(peak)
        self.scrape = torch.maximum(self.scrape, info[:, 3]*charge)
        self.worst_vx = torch.minimum(self.worst_vx, torch.where(charge, info[:, 10], 99.))
        self.max_pitch = torch.maximum(self.max_pitch, info[:, 2])
        self.closure = torch.maximum(self.closure, info[:, 7])

        face = torch.where(hurdle, info[:, 9], info[:, 4])
        first_hit = (self.hits < 1.) & (face >= 1.)
        self.face_events.scatter_add_(0, self.kind, first_hit.long())
        self.hits = torch.maximum(self.hits, face)
        reward -= .52*(face >= 1.) + 2.4*first_hit

        on_top = self.contacts[:, 6:8].min(1).values > 1.
        one_on_top = self.contacts[:, 6:8].max(1).values > 1.
        wheel_beyond = info[:, 13] > self.edge + .02
        whole_car_beyond = info[:, 5] > self.edge + hurdle.float()*HURDLE_THICKNESS
        valid_platform_support = platform & on_top & wheel_beyond
        both = self.contacts[:, 1:3].min(1).values > 1.
        floor_support = both & (info[:, 6] < .020)
        correct_surface = torch.where(platform, valid_platform_support, floor_support & (~obstacle | whole_car_beyond))
        recovery = first_flight_ended & ~broken
        forward_running = (vx > .35*self.speed) & (upright > .95)
        landing = recovery & correct_surface & forward_running
        clean = (self.hits < 1.) & (self.scrape < 1.)
        acquired = recovery & valid_platform_support & forward_running & clean
        reward += 1.8*(acquired & ~self.platform_acquired)
        self.platform_acquired |= acquired
        self.support_streak.copy_(torch.where(landing, self.support_streak + 1, 0))
        stable_now = self.support_streak >= 18
        reward += (stable_now & ~self.stable & clean)*torch.where(platform, 3., 1.)
        self.stable |= stable_now

        # Limit speed only while approaching or after at least 18 stable support samples.
        cruise = ~triggered | self.stable
        overspeed = (vx - self.cmd - .18).clamp(0., 2.5)
        tracking_error = (vx - self.cmd).abs().clamp_max(3.)
        reward += .012 - cruise*(.079*tracking_error + .115*overspeed.square())
        push_target = torch.where(obstacle, self.speed.clamp_min(1.75), .60*self.speed)
        reward -= charge*(.23*(push_target - info[:, 10]).clamp(0., 3.) +
                          .42*(-info[:, 10]).clamp(0., 3.) + .24*(info[:, 3] > 1.))
        reward -= .10*air*((info[:, 2] - .175).clamp_min(0.)/.10).square()

        # The wheel-centre distance gives approach credit only while clearing the wall in flight.
        advance = ((info[:, 13] - self.edge + .42)/.44).clamp(0., 1.)
        high_enough = info[:, 6] > self.wall_height - .008
        progress = torch.maximum(self.air_progress, advance*(obstacle & air & high_enough & ~broken))
        reward += 3.2*(progress - self.air_progress)
        self.air_progress.copy_(progress)
        reward += .08*(recovery & platform & one_on_top & clean & (vx > 0.))
        reward += landing*torch.where(platform, .24, .055)

        # Touchdown labels consume upward loads. The training objective damps rebound and pitch.
        loaded = recovery & (one_on_top | floor_support)
        first_support = loaded & (self.first_touch_tick < 0)
        self.first_touch_tick.copy_(torch.where(first_support, self.tick, self.first_touch_tick))
        absorbing = recovery & (self.first_touch_tick >= 0) & ((self.tick - self.first_touch_tick) < 18)
        pitch_rate = torch.where(broken, 0., self.v[:, 4]).abs().clamp_max(8.)
        rebound = info[:, 8].clamp(0., 4.)
        reward -= absorbing*(.057*info[:, 14].clamp_max(4.) + .10*rebound + .020*pitch_rate
                             + .10*(1. - upright).clamp(0., 1.))

        failed = broken | (upright < .5) | (self.p[:, 2] < .12) | (info[:, 7] >= CLOSURE_LIMIT)
        age = self.tick - self.press
        timeout = (triggered & (age >= 115)) | (self.tick >= 345)
        done = failed | timeout
        forward = (self.worst_vx > 0.) & (self.press_speed > 0.)
        success = (done & ~failed & triggered & stable_now & forward & clean
                   & (~obstacle | whole_car_beyond))
        strict = success & (self.peak >= .385) & (self.max_pitch <= math.radians(12.))
        reward += success*torch.where(platform, 7., 2.) + strict*torch.where(platform, 2., 1.5)
        reward -= 4.*failed + 1.2*(done & triggered & (self.peak < .22))
        reward = torch.where(broken, -4., reward)
        self.annotate(done, failed, success, strict)
        self.phase_samples += torch.stack((
            bit.sum(), (triggered & ~bit & ~first_flight_ended).sum(), (bit & loaded).sum(),
            ((self.kind == 1) & on_top).sum(), ((self.kind == 2) & on_top).sum(),
            (acquired & ~whole_car_beyond).sum(), broken.sum(), (platform & ~triggered).sum(),
            (platform & charge).sum(), (stable_now & triggered).sum(),
        ))
        self.immediate[0] = torch.maximum(self.immediate[0], info[:, 7].max())
        self.immediate[1] = torch.maximum(self.immediate[1], wp.to_torch(self.d.nacon)[0].float())
        self.immediate[2] = torch.maximum(self.immediate[2], wp.to_torch(self.d.nefc).max().float())
        self.immediate[5] = torch.maximum(self.immediate[5], self.peak.max())
        self.previous.copy_(self.action)
        self.reset(done)

        nominated = torch.where(self.kind == 0, self.tick >= self.begin_tick, self.p[:, 0] >= self.edge - self.lead)
        press_now = (self.press < 0) & (self.tick >= 59) & nominated
        self.press_speed.copy_(torch.where(press_now, vx, self.press_speed))
        self.press.copy_(torch.where(press_now, self.tick, self.press))
        self.cmd += (torch.where(self.tick >= 30, self.speed, 0.) - self.cmd)/12.
        self.observe()
        self.hist = torch.cat((self.hist[:, 1:], self.obs[:, None, :]), dim=1)
        self.hist[done] = self.obs[done, None, :]
        return self.obs, self.hist.flatten(1), reward, done

    def audit(self):
        return dict(
            fields=FIELDS, categories=KINDS, stages=DR_LEVELS, speed_centers_m_s=SPEED_CENTERS,
            by_stage_dr_terrain_speed=self.by_stage.long().tolist(), full_dr_envs=int(self.dr.sum()),
            population_env_steps_by_stage_and_dr=self.population_steps.tolist(),
            commanded_terrain_mix=(.20, .45, .25, .10), obstacle_heights_m=HEIGHTS,
            terrain_reset_counts=self.terrain_resets.tolist(), holds_by_ticks=self.hold_samples.tolist(),
            reset_range_columns=("speed_m_s", "stance_m", "lead_offset_m"),
            sampled_reset_min=self.range_min.tolist(), sampled_reset_max=self.range_max.tolist(),
            phase_columns=PHASES, phase_samples=self.phase_samples.tolist(),
            first_face_events=self.face_events.tolist(),
            max_closure_m=float(self.immediate[0]), max_contacts_global=int(self.immediate[1]),
            contact_capacity=self.d.naconmax, max_constraints_per_world=int(self.immediate[2]),
            constraint_capacity=self.d.njmax, measured_all_car_peak_m=float(self.immediate[5]),
        )
