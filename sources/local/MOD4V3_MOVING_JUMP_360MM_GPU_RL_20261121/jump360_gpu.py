"""2048-world GPU dynamics for the same welded/closed-chain MuJoCo plant."""
from __future__ import annotations

import math

import mujoco_warp as mjw
import numpy as np
import torch
import warp as wp

from jump360_scene import CLOSURE_LIMIT, HOLD_TICKS, HURDLE_THICKNESS, JumpPlant, WALL_HEIGHT, mujoco


@wp.kernel
def motor(
    action: wp.array2d(dtype=float), fifo: wp.array3d(dtype=float), delay: wp.array(dtype=wp.int32),
    adr_q: wp.array(dtype=wp.int32), adr_v: wp.array(dtype=wp.int32), default: wp.array(dtype=float),
    qpos: wp.array2d(dtype=float), qvel: wp.array2d(dtype=float), ctrl: wp.array2d(dtype=float),
    kp: wp.array2d(dtype=float), kd: wp.array2d(dtype=float), effort: wp.array2d(dtype=float),
    slot: wp.array(dtype=wp.int32), offset: int,
):
    w, i = wp.tid()
    idx = (slot[0] + offset) % 9
    fifo[w, idx, i] = wp.clamp(action[w, i], -6., 6.)
    instant = (idx + 9 - delay[w]) % 9
    if i < 4 and offset % 4 != 0:
        return
    speed = qvel[w, adr_v[i]]
    drive = fifo[w, instant, i]
    plateau = 40.
    stall = 53.333333333
    no_load = 16.755160819
    feet = 0.
    if i < 4:
        rear = i + 1 - i % 2
        ahead = rear - 1
        # Implement the existing motor target unwrap in the PPO joint order.
        front_goal = default[ahead] + .5 * wp.clamp(action[w, ahead], -6., 6.)
        rear_goal = default[rear] + .5 * wp.clamp(action[w, rear], -6., 6.)
        if delay[w] > 0:
            front_goal = default[ahead] + .5 * fifo[w, instant, ahead]
            rear_goal = default[rear] + .5 * fifo[w, instant, rear]
        front_q = qpos[w, adr_q[ahead]]
        rear_q = qpos[w, adr_q[rear]]
        delta = front_goal - rear_goal
        radians = 6.283185307179586
        delta = delta + wp.round((front_q - rear_q - delta) / radians) * radians
        rear_goal = rear_goal + wp.round((rear_q - rear_goal) / radians) * radians
        goal = rear_goal
        if i % 2 == 0:
            goal += delta
        feet = 60. * kp[w, i] * (goal - qpos[w, adr_q[i]]) - 2. * kd[w, i] * speed
    else:
        plateau = 5.775909774
        stall = 28.185253756
        no_load = 55.355731878
        feet = .6 * kp[w, i] * (10. * drive - speed)
    scale = effort[w, i]
    lower = wp.max(wp.min(-stall * (1. + speed/no_load), 0.), -plateau)*scale
    upper = wp.min(wp.max(stall * (1. - speed/no_load), 0.), plateau)*scale
    # Actuator order is LF, RF, LR, RR, LW, RW in the pinned MJCF.
    actuator = i
    if i == 1:
        actuator = 2
    elif i == 2:
        actuator = 1
    ctrl[w, actuator] = wp.clamp(feet, lower, upper)


@wp.kernel
def gather_contacts(
    nacon: wp.array(dtype=wp.int32), ids: wp.array(dtype=wp.vec2i),
    world: wp.array(dtype=wp.int32), frames: wp.array(dtype=wp.mat33),
    pos: wp.array(dtype=wp.vec3), dim: wp.array(dtype=wp.int32),
    address: wp.array2d(dtype=wp.int32), nefc: wp.array(dtype=wp.int32),
    force: wp.array2d(dtype=float), classifications: wp.array(dtype=wp.int32),
    out: wp.array2d(dtype=float),
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
        if fixed == -2 and wp.abs(normal[2]) > .65 and pos[i][2] >= .350:
            wp.atomic_add(out, w, robot+5, support)
    if robot == 3:
        wp.atomic_add(out, w, 3, f)
    if fixed <= -2:
        wp.atomic_add(out, w, 5, f)
        if fixed == -2 and wp.abs(normal[0]) > .35 and pos[i][2] < .358:
            wp.atomic_add(out, w, 4, f)


@wp.func
def extent(size: wp.vec3, axis: wp.vec3, cylinder: bool):
    if cylinder:
        nz = axis[2]
        return size[0] * wp.sqrt(wp.max(0., 1.-nz*nz)) + size[1]*wp.abs(nz)
    return size[0]*wp.abs(axis[0])+size[1]*wp.abs(axis[1])+size[2]*wp.abs(axis[2])


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


class JumpGpu:
    def __init__(self, count, seed, timing):
        self.device = "cuda:0"
        wp.set_device(self.device)
        self.warp_stream = wp.Stream(device=self.device)
        stream = torch.cuda.ExternalStream(self.warp_stream.cuda_stream, device=self.device)
        stream.wait_stream(torch.cuda.current_stream())
        torch.cuda.set_stream(stream)
        wp.set_stream(self.warp_stream)
        cpu = JumpPlant(seed=seed)
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
        self.stats_w = wp.zeros((count, 13), device=self.device, dtype=float)
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
        self.timing_values = tf([timing["platform"], timing["hurdle"]])
        # Air samples, phase, peak, pitch, previous wheel x/low, margin at edge.
        self.arc = tf(np.zeros((count, 7)))
        self.peak = self.cmd.clone()
        self.max_pitch = self.cmd.clone()
        self.worst_vx = self.cmd.clone()
        self.scrape = self.cmd.clone()
        self.hits = self.cmd.clone()
        self.closure = self.cmd.clone()
        self.late_support = self.tick.clone()
        self.counters = tf(np.zeros((2, 4, 8)))
        self.all_peak = tf(np.zeros((2, 4)))
        self.all_margin = tf(np.full((2, 4), -9.))
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
                           d.contact.dim, d.contact.efc_address, d.nefc, d.efc.force, arr_i(lookup), self.aux_w]
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

    def rand(self, *shape):
        return torch.rand(shape, generator=self.rng, device=self.device)

    def lead_opt(self, speed, height, kind):
        def axis(grid, value):
            value = value.contiguous().clamp(grid[0], grid[-1])
            i = torch.searchsorted(grid, value, right=True).clamp(1, len(grid)-1)-1
            return i, (value-grid[i])/(grid[i+1]-grid[i])

        i, a = axis(self.timing_speed, speed)
        j, b = axis(self.timing_height, height)
        scene = (kind >= 2).long()
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
        self.speed[ids] = .60+1.40*self.rand(n)
        self.height[ids] = .22+.20*self.rand(n)
        # Include the minimum and maximum command values in each substantial reset.
        if n >= 16:
            self.speed[ids[:2]] = .60
            self.speed[ids[2:4]] = 2.
            self.height[ids[4:6]] = .22
            self.height[ids[6:8]] = .42
        self.cmd[ids] = 0.
        self.press[ids] = -1
        # 50% flat, 25% full solid platform, 12.5% each of 360/340 mm hurdles.
        terrain = torch.randint(8, (n,), generator=self.rng, device=self.device)
        self.kind[ids] = torch.where(terrain < 4, 0, torch.where(terrain < 6, 1, terrain-4))
        self.wall_height[ids] = torch.where(self.kind[ids] == 3, .340, self.kind[ids].ne(0).float()*WALL_HEIGHT)
        self.lead[ids] = self.lead_opt(self.speed[ids], self.height[ids], self.kind[ids]) + .16*self.rand(n)-.08
        self.key_hold[ids] = HOLD_TICKS - 4 + (9*self.rand(n)).long()
        # Keep the wall solid and fixed from reset. Leave time to settle into a run.
        self.edge[ids] = (1.28+self.rand(n)*.22)*self.speed[ids] + self.lead[ids]
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

    def observe(self):
        out = self.obs
        # Derive body gravity from the orientation. No root location or velocity
        # goes into the actor, including at reset.
        q = self.p[:, 3:7]
        qw,qx,qy,qz = q.unbind(1)
        gravity = torch.stack((2.*(qw*qy-qx*qz), -2.*(qw*qx+qy*qz),
                               -1.+2.*(qx.square()+qy.square())), dim=-1)
        out[:, 0] = self.cmd
        out[:, 3] = self.height*5.
        out[:, 4:7] = self.v[:, 3:6]*.5
        out[:, 7:10] = gravity
        out[:, 10:14] = self.p[:, self.qadr[:4]] - self.goal[:4]
        out[:, 16:22] = self.v[:, self.vadr]*.1
        out[:, 22:28] = self.previous
        out[:, 28] = 1.
        out[:, 30] = (self.press >= 0) & ((self.tick-self.press) < self.key_hold)
        return out

    def extra(self):
        # The reset quaternion is current even before Warp refreshes xmat.
        qw, qx, qy, qz = self.p[:, 3:7].unbind(1)
        forward = torch.stack((1.-2.*(qy.square()+qz.square()), 2.*(qx*qy+qw*qz)), dim=1)
        lateral = torch.stack((2.*(qx*qy-qw*qz), 1.-2.*(qx.square()+qz.square())), dim=1)
        vx = (self.v[:, :2]*forward).sum(1)/forward.norm(dim=1).clamp_min(.01)
        vy = (self.v[:, :2]*lateral).sum(1)/lateral.norm(dim=1).clamp_min(.01)
        clearance = self.stats[:, 6].clamp(-.1, 1.)
        return torch.stack((self.p[:, 2], self.v[:, 2], vx, vy, clearance,
                            (self.contacts[:,1:3].min(1).values>1.).float(), (self.peak>.02).float(),
                            torch.where(self.press>=0, (self.tick-self.press).clamp(0,100)*.02, 2.),
                            (self.peak>.04).float(), self.peak, (self.edge-self.p[:,0]).clamp(-2.,3.),
                            self.wall_height,
                            self.mass[:,self.cpu.base_id]/self.nom_mass[self.cpu.base_id],
                            self.friction[:,self.cpu.ground_gid,0]), dim=1)

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
                  | ~torch.isfinite(self.contacts).all(1) | (self.stats[:, 12] > 0))
        info = torch.where(broken[:, None], 0., self.stats)
        active = self.obs[:, 30] > .5
        triggered = self.press >= 0
        pre_lift = triggered & (~broken) & (info[:, 10] < 99.)
        peak = torch.maximum(self.peak, info[:, 0])
        # Potential difference gives credit only once for each increment in height.
        height_value = lambda height: 2.*height.clamp(0., .48) + 8.*((height-.26)/.15).clamp(0., 1.35).pow(3)
        delta = height_value(peak)-height_value(self.peak)
        self.peak.copy_(peak)
        self.scrape = torch.maximum(self.scrape, info[:, 3] * pre_lift)
        wall_force = torch.where(self.kind >= 2, info[:, 9], info[:, 4])
        self.hits = torch.maximum(self.hits, wall_force*triggered)
        self.worst_vx = torch.minimum(self.worst_vx, torch.where(pre_lift, info[:, 10], 99.))
        self.max_pitch = torch.maximum(self.max_pitch, info[:, 2])
        self.closure = torch.maximum(self.closure, info[:, 7])
        main_landed = self.arc[:, 1] == 2.
        support = self.contacts[:, 1:3].min(dim=1).values > 1.
        platform_support = self.contacts[:, 6:8].min(dim=1).values > 1.
        base_running = (info[:, 11]>.35*self.speed)&(self.rot[:, 2, 2]>.92)
        platform = (self.kind==1)&platform_support&(info[:, 5]>self.edge)
        hurdle = (self.kind>=2)&support&(info[:,5]>self.edge+HURDLE_THICKNESS)&(info[:,6]<.020)
        floor = (self.kind==0)&support&(info[:,6]<.020)
        landing = (~broken)&main_landed&(self.peak>.12)&base_running&(platform|hurdle|floor)
        self.late_support = torch.where(landing, self.late_support+1, torch.zeros_like(self.late_support))
        good = (self.late_support==12)&(self.worst_vx>0.)&(self.scrape<1.)&(self.hits<1.)
        failure = broken | (self.rot[:,2,2]<.5) | (self.p[:,2]<.12) | (info[:,7]>=CLOSURE_LIMIT)
        reward = .008 - .015*(info[:,11]-self.cmd).abs()
        reward += delta - (self.arc[:, 1]==1.)*.07*((info[:,2]-.175).clamp_min(0.)/.10).square()
        reward -= pre_lift*(.18*(.50*self.speed-info[:,10]).clamp_min(0.)+.27*(-info[:,10]).clamp_min(0.))
        reward -= pre_lift*.14*(info[:,3]>1.) + triggered*.18*(wall_force>1.)
        reward += .055*landing + good*(1.+(self.kind>0)*2.) - 3.*failure
        enough_recovery = triggered & (self.tick-self.press >= 100)
        timeout = enough_recovery | (self.tick >= 345)
        done = failure|timeout
        eligible = done & triggered
        success = eligible & (~failure) & (self.late_support>=12) & (self.worst_vx>0.) & (self.scrape<1.) & (self.hits<1.)
        compliant = success & (self.peak>=.385) & (self.max_pitch<=math.radians(12)) & (self.closure<CLOSURE_LIMIT)
        reward -= 1.2*(eligible&(self.peak<.22))
        reward = torch.where(broken, -4., reward)
        for i in range(2):
            for j in range(4):
                pool = eligible & (self.dr==bool(i)) & (self.kind==j)
                self.counters[i, j] += torch.stack(((pool).sum(), (pool&failure).sum(), (pool&success).sum(),
                                                   (pool&compliant).sum(), (pool&(self.peak>=.385)).sum(),
                                                   (pool&(self.worst_vx>0.)).sum(), (pool&(self.scrape<1.)).sum(),
                                                   (pool&(self.arc[:, 6] >= 0.)).sum()))
                self.all_peak[i,j] = torch.maximum(self.all_peak[i,j], (self.peak*pool).max())
                margin = torch.where(pool & ~broken, self.arc[:, 6], -9.).max()
                self.all_margin[i,j] = torch.maximum(self.all_margin[i,j], margin)
        self.immediate[0] = torch.maximum(self.immediate[0], info[:,7].max())
        self.immediate[1] = torch.maximum(self.immediate[1], wp.to_torch(self.d.nacon)[0].float())
        self.immediate[2] = torch.maximum(self.immediate[2], wp.to_torch(self.d.nefc).max().float())
        self.immediate[3] += active.sum()
        self.immediate[4] += failure.sum()
        self.immediate[5] = torch.maximum(self.immediate[5], self.peak.max())
        self.immediate[6] += broken.sum()
        first_world = torch.where(broken, self.index+1, self.n+1).min()
        self.immediate[7] = torch.where((self.immediate[7]==0.) & (first_world<=self.n), first_world, self.immediate[7])
        self.previous.copy_(self.action)
        self.reset(done)
        # Presses are generated by the rollout driver. The actor sees only the key.
        nominated = ((self.kind==0)&(self.tick>=132)) | ((self.kind!=0)&(self.p[:,0]>=self.edge-self.lead))
        press_now = (self.press<0)&(self.tick>=59)&nominated
        self.press.copy_(torch.where(press_now, self.tick, self.press))
        self.cmd += (torch.where(self.tick>=30, self.speed, 0.)-self.cmd)/12.
        self.observe()
        self.hist = torch.cat((self.hist[:,1:], self.obs[:,None,:]), dim=1)
        self.hist[done] = self.obs[done,None,:]
        return self.obs, self.hist.flatten(1), reward, done

    def statistics(self):
        return dict(
            categories=["flat", "platform_360", "hurdle_360", "hurdle_340"],
            columns=["trials", "falls", "landed_running", "all_gates", "clearance_gate", "forward",
                     "zero_charge_scrape", "nonnegative_wall_margin"],
            results_0_dr_full_dr=self.counters.int().tolist(), max_all_car_clearance_m=self.all_peak.tolist(),
            maximum_closure_m=float(self.immediate[0]), max_contacts_global=int(self.immediate[1]),
            max_constraints_per_world=int(self.immediate[2]), triggered_samples=int(self.immediate[3]),
            terminations=int(self.immediate[4]), measured_all_car_peak_any_m=float(self.immediate[5]),
            best_wall_margin_m=[[None if value < -8. else value for value in row] for row in self.all_margin.tolist()],
            nonfinite_world_resets=int(self.immediate[6]), first_nonfinite_world_index=(
                int(self.immediate[7])-1 if self.immediate[7]>0. else None),
            current_full_dr=int(self.dr.sum()), contact_capacity=self.d.naconmax, constraint_capacity=self.d.njmax,
            current_root_x_m_range=[float(self.p[:,0].min()),float(self.p[:,0].max())],
            current_root_z_m_range=[float(self.p[:,2].min()),float(self.p[:,2].max())],
            current_physics_time_s_range=[float(wp.to_torch(self.d.time).min()),float(wp.to_torch(self.d.time).max())],
        )
