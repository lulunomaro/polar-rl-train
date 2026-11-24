"""COMMANDER-AUTHORED 4,096-World `mujoco_warp` CUDA Graph 400 Hz Perception-Guided Jump Environment.

Trains `JumpWarpPerceptionActor` (`459D = obs35 + hist420 + g_jump4 -> action6`) across 3 cohorts:
1. Cohort 0 (25%): Open Flat All-Regime High Jump (`h in [0.24, 0.42] m`, `v in [0.0, 2.85] m/s`,
   keep-W & abrupt/smoothed release-W, `r_peak` scaled to `0.42 m` + `380 mm` milestone bonus).
2. Cohort 1 (38%): Solid `200..390 mm` (`380 mm` focus!) 3D High Platform (`dyn_hurdle_0`, `5.0 m` deck),
   with random manual `Space` press distance `d_press in [0.46, 2.05] m` before front face.
3. Cohort 2 (37%): `RMUL 2027 3v3` Orange-Tip Bridge Hurdle (`dyn_hurdle_1`: exact `352 mm` span,
   `dyn_hurdle_2`: `480 mm` wide/oblique span, `z_top in [0.24, 0.35] m`), with random manual `Space`
   press distance `d_press in [0.46, 2.05] m` before front face, requiring zero beam contact and
   clean 2-tire floor landing beyond the back face.

Zero Sim2Sim Gap Guarantees:
- Pre-`Space` runup (`press < 0`) is driven by exact frozen `SymmetricE0` (`E0_CALIBRATION.json`).
- 400 Hz Warp `motor` law matches `JumpPlant._compute_motor_torque` (`Nav4DSimulation` `e2` branch).
- `g_jump` is computed via exact `extract_jump_feature_torch` from `terrain_sensor_4d.py`.
- `obs[:, 30]` arming law matches `Nav4DPolicy.act` bit-for-bit.
"""
from __future__ import annotations

import math
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
import xml.etree.ElementTree as ET

import mujoco
import mujoco_warp as mjw
import numpy as np
import torch
import warp as wp

from jump360_gpu import motor
from jump360_scene import CLOSURE_LIMIT, JumpPlant, make_scene
from jump380_r4_gpu import gather_contacts
from jump380_r6_gpu import gather_frame
from terrain_sensor_4d import S_GRID_NP, extract_jump_feature_torch

PLAT_LEN = 5.00
PLAT_BOX_H = 0.40
BRIDGE_NARROW_LEN = 0.352  # Exact RMUL 2027 3v3 orange-tip bridge beam width (rmul_box_3 = 352 mm)!
BRIDGE_WIDE_LEN = 0.480    # Oblique / wide bridge hurdle span
BRIDGE_BOX_H = 0.38
HALF_WIDTH = 8.0


def prepare_jump_warp_scene(cache_dir: Path) -> Path:
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / "jump360_solid_physics.xml"
    if path.is_file():
        return path
    with NamedTemporaryFile(dir=cache_dir, suffix=".partial", delete=False) as stream:
        tmp = Path(stream.name)
    try:
        tree = ET.parse(make_scene(tmp, False))
        world = tree.getroot().find("worldbody")
        ground = world.find("geom[@name='ground']")
        ground.set("size", "26 26 .1")
        specs = (
            (0, PLAT_LEN, PLAT_BOX_H, ".30 .56 .73 1"),
            (1, BRIDGE_NARROW_LEN, BRIDGE_BOX_H, ".88 .48 .16 1"),
            (2, BRIDGE_WIDE_LEN, BRIDGE_BOX_H, ".76 .56 .24 1"),
        )
        for idx, length, height, color in specs:
            geom = world.find(f"body/geom[@name='dyn_hurdle_{idx}']")
            geom.set("size", f"{length / 2.0:.4f} {HALF_WIDTH:.1f} {height / 2.0:.4f}")
            geom.set("rgba", color)
        tree.write(tmp, encoding="utf-8", xml_declaration=True)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)
    return path


class JumpWarpGpu:
    def __init__(self, count: int, seed: int, e0: torch.nn.Module, cache_dir: Path):
        self.device = "cuda:0"
        self.e0 = e0.to(self.device).eval()
        wp.set_device(self.device)
        self.warp_stream = wp.Stream(device=self.device)
        stream = torch.cuda.ExternalStream(self.warp_stream.cuda_stream, device=self.device)
        stream.wait_stream(torch.cuda.current_stream())
        torch.cuda.set_stream(stream)
        wp.set_stream(self.warp_stream)

        prepare_jump_warp_scene(cache_dir)
        cpu = JumpPlant(seed=seed, visual=False, scene_dir=cache_dir)
        cpu.setup(0.28)
        if cpu.m.opt.cone != mujoco.mjtCone.mjCONE_ELLIPTIC:
            raise ValueError("Expected pinned elliptic contact cone")
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
        self.stats_w = wp.zeros((count, 22), device=self.device, dtype=float)
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
        self.qadr = tf(cpu.active_qadr, torch.long)
        self.vadr = tf(cpu.active_dadr, torch.long)
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
        self.g_jump = tf(np.tile([2.50, 2.50, 0.0, 0.0], (count, 1)))
        self.s_grid = tf(S_GRID_NP)

        self.dr_probability = 0.0
        self.stage = 0
        self.dr = torch.zeros(count, device=self.device, dtype=torch.bool)
        self.tick = torch.zeros(count, device=self.device, dtype=torch.long)
        self.press = torch.full_like(self.tick, -1)
        self.fired_tick = torch.full_like(self.tick, -1)
        self.kind = self.tick.clone()  # 0=flat, 1=platform(200..390mm), 2=bridge_352mm, 3=bridge_480mm
        self.is_overhead_beam = torch.zeros_like(self.dr)

        self.cmd = tf(np.zeros(count))
        self.turn = tf(np.zeros(count))
        self.speed = tf(np.zeros(count))
        self.height = tf(np.zeros(count))
        self.edge = tf(np.zeros(count))
        self.wall_height = tf(np.zeros(count))
        self.obs_span = tf(np.zeros(count))
        self.press_dist = tf(np.zeros(count))
        self.key_hold = self.tick.clone()
        self.begin_tick = self.tick.clone()

        self.perturb_kind = self.tick.clone()
        self.perturb_tick = self.tick.clone()
        self.abrupt_cmd = torch.zeros_like(self.dr)
        self.post_vx = tf(np.zeros(count))
        self.post_wz = tf(np.zeros(count))
        self.g_noise = tf(np.zeros((count, 4)))

        self.arc = tf(np.zeros((count, 7)))
        self.peak = tf(np.zeros(count))
        self.hits = tf(np.zeros(count))
        self.air_progress = tf(np.zeros(count))
        self.press_speed = tf(np.zeros(count))
        self.takeoff_vx = tf(np.zeros(count))
        self.min_crouch_z = tf(np.full(count, 0.45))
        self.first_land_tick = torch.full_like(self.tick, -1)
        self.late_support = torch.zeros_like(self.tick)
        self.paid_success = torch.zeros_like(self.dr)
        self.paid_380_peak = torch.zeros_like(self.dr)
        self.paid_edge_margin = torch.zeros_like(self.dr)

        self.counts = torch.zeros(14, device=self.device, dtype=torch.long)
        self.range_low = tf([99.0, 99.0, 99.0])
        self.range_high = tf([-99.0, -99.0, -99.0])

        lookup = np.zeros(cpu.m.ngeom, dtype=np.int32)
        lookup[cpu.ground_gid] = -1
        lookup[cpu.hurdle_gids] = [-2, -3, -4]
        lookup[cpu.groups[0]] = [1, 2]
        lookup[cpu.groups[1] + cpu.groups[2]] = 3

        self.wp_motor = [
            self.action_rom,
            self.fifo,
            self.delay_wp,
            arr_i(cpu.active_qadr),
            arr_i(cpu.active_dadr),
            wp.from_torch(self.goal),
            d.qpos,
            d.qvel,
            d.ctrl,
            wp.from_torch(self.action_gain),
            wp.from_torch(self.derivative_gain),
            wp.from_torch(self.effort_scale),
            self.slot_wp,
        ]
        self.wp_contact = [
            d.nacon,
            d.contact.geom,
            d.contact.worldid,
            d.contact.frame,
            d.contact.pos,
            d.contact.dim,
            d.contact.efc_address,
            d.nefc,
            d.efc.force,
            arr_i(lookup),
            wp.from_torch(self.wall_height),
            self.aux_w,
        ]
        self.wp_frame = [
            d.qpos,
            d.qvel,
            d.geom_xpos,
            d.geom_xmat,
            d.xmat,
            wp.array(cpu.m.geom_size, dtype=wp.vec3),
            arr_i(cpu.measured_gids),
            self.aux_w,
            d.site_xpos,
            arr_i(cpu.pairs_np[:, 0]),
            arr_i(cpu.pairs_np[:, 1]),
            len(cpu.pairs),
            cpu.base_id,
            wp.from_torch(self.press),
            wp.from_torch(self.edge),
            wp.from_torch(self.wall_height),
            wp.from_torch(self.arc),
            self.stats_w,
        ]

        self.reset(torch.ones(count, device=self.device, dtype=torch.bool))
        with wp.ScopedStream(self.warp_stream):
            self.substeps()
            wp.synchronize_device(self.device)
            with wp.ScopedCapture(device=self.device, stream=self.warp_stream) as capture:
                self.substeps()
            self.graph = capture.graph
        self.reset(torch.ones(count, device=self.device, dtype=torch.bool))
        self.update_g_jump()
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

    def set_stage(self, stage: int):
        probs = (0.0, 0.25, 0.55, 1.00)
        self.dr_probability = probs[min(stage, 3)]
        self.stage = min(stage, 3)

    def reset(self, done: torch.Tensor):
        ids = self.index[done]
        n = int(ids.numel())
        if not n:
            return
        with wp.ScopedStream(self.warp_stream):
            mjw.reset_data(self.m, self.d, wp.from_torch(done.contiguous(), dtype=wp.bool))

        self.p[ids] = self.reset_q
        yaw_init = (self.rand(n) - 0.5) * 0.08  # +-2.3 deg initial yaw variation
        self.p[ids, 3] = torch.cos(0.5 * yaw_init)
        self.p[ids, 6] = torch.sin(0.5 * yaw_init)
        self.p[ids, 1] = (self.rand(n) - 0.5) * 0.06
        self.previous[ids] = 0.0
        self.fifo_t[ids] = 0.0

        self.dr[ids] = self.rand(n) < self.dr_probability
        dr = self.dr[ids, None].float()
        self.mass[ids] = self.nom_mass * (1.0 + (self.rand(n, self.nom_mass.numel()) - 0.5) * 0.22 * dr)
        self.ipos[ids] = self.nom_ipos
        self.ipos[ids, self.cpu.base_id] += 0.04 * (self.rand(n, 3) - 0.5) * dr
        self.friction[ids] = self.nom_friction
        mu = 0.90 + (self.rand(n) * 0.55 - 0.30) * dr[:, 0]
        for g in [self.cpu.ground_gid, *self.cpu.hurdle_gids, *self.cpu.tire_gids]:
            self.friction[ids, g, 0] = torch.where(self.dr[ids], mu, self.nom_friction[g, 0])
        self.action_gain[ids] = 1.0 + 0.20 * (self.rand(n, 6) - 0.5) * dr
        self.derivative_gain[ids] = 1.0 + 0.20 * (self.rand(n, 6) - 0.5) * dr
        self.effort_scale[ids] = 1.0 + 0.18 * (self.rand(n, 6) - 0.5) * dr
        self.delay[ids] = ((self.rand(n) * 8.0).long() * self.dr[ids]).to(torch.int32)

        # Cohort draw: 25% flat (0), 38% solid platform 200..390mm (1), 26% bridge 352mm (2), 11% bridge 480mm (3)
        c_draw = self.rand(n)
        kind = torch.where(
            c_draw < 0.25,
            0,
            torch.where(c_draw < 0.63, 1, torch.where(c_draw < 0.89, 2, 3)),
        )
        self.kind[ids] = kind
        is_flat = kind == 0
        is_plat = kind == 1
        is_hurdle = kind >= 2

        # Obstacle heights:
        # - Platform (kind==1): 60% in [0.355, 0.390] m (380mm focus!), 40% in [0.200, 0.355] m (RMUL 200mm + mid)
        # - Bridge 352mm (kind==2): 55% in [0.255, 0.295] m (RMUL 270mm orange-tip beam!), 45% in [0.295, 0.355] m
        # - Bridge 480mm (kind==3): [0.245, 0.335] m (oblique/wide bridge beam)
        p_hi = self.rand(n) < 0.60
        z_plat = torch.where(p_hi, 0.355 + 0.035 * self.rand(n), 0.200 + 0.155 * self.rand(n))
        b_rmul = self.rand(n) < 0.55
        z_b352 = torch.where(b_rmul, 0.255 + 0.040 * self.rand(n), 0.295 + 0.060 * self.rand(n))
        z_b480 = 0.245 + 0.090 * self.rand(n)
        wh = torch.where(is_flat, 0.0, torch.where(is_plat, z_plat, torch.where(kind == 2, z_b352, z_b480)))
        self.wall_height[ids] = wh
        span = torch.where(is_flat, 0.0, torch.where(is_plat, PLAT_LEN, torch.where(kind == 2, BRIDGE_NARROW_LEN, BRIDGE_WIDE_LEN)))
        self.obs_span[ids] = span
        self.is_overhead_beam[ids] = is_hurdle & (self.rand(n) < 0.55)

        # Speeds:
        # - Flat: [0.0, 2.85] m/s across full human matrix
        # - Platform: [0.95, 2.85] m/s (higher minimum speed for >=355mm platforms: >=1.15 m/s)
        # - Bridge hurdle: [1.20, 2.85] m/s (must carry horizontal momentum across 352..480mm span!)
        su = self.rand(n)
        sv = self.rand(n)
        flat_sp = torch.where(su < 0.28, 0.30 * sv, torch.where(su < 0.62, 0.30 + 1.15 * sv, 1.45 + 1.40 * sv))
        plat_min = torch.where(wh >= 0.350, 1.15, 0.90)
        plat_sp = plat_min + (2.85 - plat_min) * sv
        hurd_sp = 1.20 + 1.65 * sv
        speed = torch.where(is_flat, flat_sp, torch.where(is_plat, plat_sp, hurd_sp))
        self.speed[ids] = speed

        # Stances: 48% explicitly in tall [0.35, 0.42] m, 52% in [0.24, 0.35] m
        hu = self.rand(n)
        hv = self.rand(n)
        height = torch.where(hu < 0.48, 0.35 + 0.07 * hv, 0.24 + 0.11 * hv)
        self.height[ids] = height

        # Manual Space press distance before obstacle front face: uniform in [0.46, 2.05] m!
        d_press = 0.46 + 1.59 * self.rand(n)
        self.press_dist[ids] = d_press
        self.key_hold[ids] = torch.randint(5, 42, (n,), generator=self.rng, device=self.device)
        self.begin_tick[ids] = 80 + (40 * self.rand(n)).long()

        # Post-Space human command behavior:
        # - On flat: 42% keep W, 42% release W -> 0 (half abrupt like eval_jump_all_regimes, half smoothed!), 8% feather S, 8% steer
        # - On obstacles: 82% keep W (normal jump-over), 18% release W after takeoff
        pk_draw = self.rand(n)
        pk_flat = torch.where(pk_draw < 0.42, 0, torch.where(pk_draw < 0.84, 1, torch.where(pk_draw < 0.92, 2, 3)))
        pk_obs = torch.where(pk_draw < 0.82, 0, 1)
        pk = torch.where(is_flat, pk_flat, pk_obs)
        self.perturb_kind[ids] = pk
        self.perturb_tick[ids] = torch.where(is_flat & (pk == 1), (self.rand(n) * 6.0).long(), (10 + self.rand(n) * 14.0).long())
        self.abrupt_cmd[ids] = is_flat & (self.rand(n) < 0.55)
        self.post_vx[ids] = torch.where(pk == 1, 0.0, torch.where(pk == 2, -0.30 * self.rand(n), speed))
        self.post_wz[ids] = torch.where(pk == 3, (2.0 * self.rand(n) - 1.0) * 0.9, 0.0)

        # Position active mocap obstacle so robot reaches (edge - d_press) after steady-speed settle (~1.55..1.85s)
        edge = speed * (1.55 + 0.35 * self.rand(n)) + d_press
        self.edge[ids] = torch.where(is_flat, torch.full_like(edge, 30.0), edge)

        half_lens = (PLAT_LEN * 0.5, BRIDGE_NARROW_LEN * 0.5, BRIDGE_WIDE_LEN * 0.5)
        half_hs = (PLAT_BOX_H * 0.5, BRIDGE_BOX_H * 0.5, BRIDGE_BOX_H * 0.5)
        for j in range(3):
            act_j = kind == (j + 1)
            self.mocap[ids, j, 0] = torch.where(act_j, edge + half_lens[j], 24.0)
            self.mocap[ids, j, 1] = 0.0
            self.mocap[ids, j, 2] = torch.where(act_j, wh - half_hs[j], -3.0 - j)

        # Per-episode LiDAR elevation discretization/range bias under DR
        n4 = (self.rand(n, 4) - 0.5) * 2.0 * dr
        self.g_noise[ids, 0] = 0.020 * n4[:, 0]
        self.g_noise[ids, 1] = 0.020 * n4[:, 1]
        self.g_noise[ids, 2] = 0.010 * n4[:, 2]
        self.g_noise[ids, 3] = 0.010 * n4[:, 3]

        self.cmd[ids] = 0.0
        self.turn[ids] = 0.0
        self.tick[ids] = 0
        self.press[ids] = -1
        self.fired_tick[ids] = -1
        self.press_speed[ids] = 0.0
        self.takeoff_vx[ids] = 0.0
        self.min_crouch_z[ids] = height
        self.first_land_tick[ids] = -1
        self.late_support[ids] = 0
        self.paid_success[ids] = False
        self.paid_380_peak[ids] = False
        self.paid_edge_margin[ids] = False
        self.peak[ids] = 0.0
        self.hits[ids] = 0.0
        self.air_progress[ids] = 0.0
        self.arc[ids] = 0.0
        self.arc[ids, 6] = -9.0
        self.stats[ids] = 0.0
        self.contacts[ids] = 0.0

        self.range_low = torch.minimum(self.range_low, torch.stack((speed.min(), height.min(), d_press.min())))
        self.range_high = torch.maximum(self.range_high, torch.stack((speed.max(), height.max(), d_press.max())))

    def update_g_jump(self):
        q = self.p[:, 3:7]
        qw, qx, qy, qz = q.unbind(1)
        yaw = torch.atan2(2.0 * (qw * qz + qx * qy), 1.0 - 2.0 * (qy * qy + qz * qz))
        cos_y = torch.cos(yaw)[:, None]
        rx = self.p[:, 0:1] + cos_y * self.s_grid[None, :]  # (N, 153)

        in_obs = (self.kind[:, None] > 0) & (rx >= self.edge[:, None]) & (rx <= (self.edge + self.obs_span)[:, None])
        wh2 = self.wall_height[:, None]
        z_eff = torch.where(in_obs, wh2, torch.zeros_like(rx))
        z_gnd = torch.where(in_obs & ~self.is_overhead_beam[:, None], wh2, torch.zeros_like(rx))
        z_ref = torch.zeros(self.n, device=self.device, dtype=torch.float32)

        g = extract_jump_feature_torch(self.s_grid, z_eff, z_gnd, z_ref=z_ref)
        has_o = (g[:, 2] > 0.05) & (g[:, 0] <= 2.25)
        # Keep obstacle context latched after crossing edge (rx > edge + 0.35m) just like Nav4DPolicy!
        crossed_o = (self.kind > 0) & (self.press >= 0) & ~has_o & ((self.p[:, 0] - self.edge) > -0.35)
        latched = torch.stack(
            (
                torch.full_like(self.wall_height, -0.40),
                -0.40 + self.obs_span.clamp(0.08, 0.90),
                self.wall_height,
                torch.where(self.kind == 1, self.wall_height, torch.zeros_like(self.wall_height)),
            ),
            dim=1,
        )
        noisy = g + self.g_noise
        noisy[:, 2:4] = noisy[:, 2:4].clamp(0.0, 0.42)
        noisy[:, 1] = torch.maximum(noisy[:, 1], noisy[:, 0] + 0.04)
        g_out = torch.where(has_o[:, None], noisy, g)
        self.g_jump = torch.where(crossed_o[:, None], latched, g_out)
        return self.g_jump

    def observe(self):
        out = self.obs
        q = self.p[:, 3:7]
        qw, qx, qy, qz = q.unbind(1)
        gravity = torch.stack(
            (
                2.0 * (qw * qy - qx * qz),
                -2.0 * (qw * qx + qy * qz),
                -1.0 + 2.0 * (qx.square() + qy.square()),
            ),
            dim=-1,
        )
        out.zero_()
        out[:, 0] = self.cmd
        out[:, 2] = self.turn
        out[:, 3] = self.height * 5.0
        out[:, 4:7] = self.v[:, 3:6] * 0.5
        out[:, 7:10] = gravity
        out[:, 10:14] = self.p[:, self.qadr[:4]] - self.goal[:4]
        out[:, 16:22] = self.v[:, self.vadr] * 0.1
        out[:, 22:28] = self.previous
        out[:, 28] = 1.0

        fire_age = (self.tick - self.fired_tick).clamp_min(0)
        pulse_len = torch.where(self.kind == 0, self.key_hold, torch.full_like(self.key_hold, 26))
        out[:, 30] = ((self.fired_tick >= 0) & (fire_age < pulse_len)).float()

        if hasattr(self, "dr"):
            noise = (self.rand(self.n, 18) - 0.5) * 0.012 * self.dr[:, None].float()
            out[:, 4:22] += noise
        return out

    def actor_input(self) -> torch.Tensor:
        return torch.cat((self.obs, self.hist.flatten(1), self.g_jump), dim=1)

    def active_mask(self) -> torch.Tensor:
        return self.fired_tick >= 0

    def anchor_mask(self) -> torch.Tensor:
        return (self.fired_tick >= 0) & (self.kind == 0) & (self.height <= 0.31) & (self.speed >= 1.15) & (self.perturb_kind == 0)

    def extra(self) -> torch.Tensor:
        return torch.cat(
            (
                self.p[:, 2:3],
                self.v[:, :6],
                self.arc[:, :4],
                self.arc[:, 6:7].clamp(-1.0, 1.0),
                self.height[:, None],
                self.speed[:, None],
                self.wall_height[:, None],
                self.obs_span[:, None],
                (self.edge - self.p[:, 0]).clamp(-2.0, 3.0)[:, None],
                (self.press >= 0).float()[:, None],
                (self.kind == 1).float()[:, None],
                (self.kind >= 2).float()[:, None],
            ),
            dim=1,
        )

    def step(self, actor_action: torch.Tensor):
        fired_pre = self.fired_tick >= 0
        armed_runup = (self.press >= 0) & ~fired_pre
        with torch.no_grad():
            obs_e0 = self.obs.clone()
            min_v_obs = torch.where(self.kind >= 2, 1.75, torch.where(self.wall_height >= 0.34, 1.55, 1.25))
            obs_e0[:, 0] = torch.where(armed_runup & (self.kind > 0), torch.maximum(obs_e0[:, 0], min_v_obs), obs_e0[:, 0])
            e0_act = self.e0(obs_e0)
        exec_act = torch.where(fired_pre[:, None], actor_action, e0_act).clamp(-6.0, 6.0)
        self.action.copy_(exec_act)

        had_air = self.arc[:, 1] > 0.0
        self.stats.zero_()
        self.stats[:, 1] = 99.0
        self.stats[:, 10] = 99.0
        with wp.ScopedStream(self.warp_stream):
            wp.capture_launch(self.graph, self.warp_stream)
        self.slot.add_(8).remainder_(9)
        self.tick += 1

        broken = (
            ~torch.isfinite(self.p).all(1)
            | ~torch.isfinite(self.v).all(1)
            | ~torch.isfinite(self.rot).all(dim=(1, 2))
            | ~torch.isfinite(self.stats).all(1)
            | ~torch.isfinite(self.contacts).all(1)
            | (self.stats[:, 12] > 0.0)
        )
        info = torch.where(broken[:, None], 0.0, self.stats)

        vx = info[:, 11]
        upright = torch.where(broken, 0.0, self.rot[:, 2, 2])
        pitch = torch.asin(torch.where(broken, 0.0, self.rot[:, 2, 0]).clamp(-1.0, 1.0)).abs()
        roll = torch.asin(torch.where(broken, 0.0, self.rot[:, 2, 1]).clamp(-1.0, 1.0)).abs()
        wx = torch.where(broken, 0.0, self.v[:, 3])
        wy = torch.where(broken, 0.0, self.v[:, 4])
        vz = torch.where(broken, 0.0, self.v[:, 2])
        pos_z = torch.where(broken, 0.25, self.p[:, 2])

        active = fired_pre
        age = (self.tick - self.fired_tick).clamp_min(0)
        air = self.arc[:, 1] == 1.0
        landed = self.arc[:, 1] == 2.0
        is_flat = self.kind == 0
        is_plat = self.kind == 1
        is_hurdle = self.kind >= 2

        first_air = air & ~had_air & ~broken
        self.takeoff_vx = torch.where(first_air, vx, self.takeoff_vx)

        # --- 1. Pre-takeoff deep crouch (down to 0.205 m) & upward launch vz ---
        pre_air = active & (self.arc[:, 1] == 0.0) & ~broken
        new_crouch = torch.where(pre_air & (age <= 14), torch.minimum(self.min_crouch_z, pos_z), self.min_crouch_z)
        crouch_delta = (self.min_crouch_z.clamp_max(0.42) - new_crouch.clamp_min(0.205)).clamp_min(0.0)
        need_deep = ((self.height > 0.30) | (self.wall_height >= 0.26)).float()
        r_crouch = 5.5 * crouch_delta * need_deep * pre_air.float()
        self.min_crouch_z.copy_(new_crouch)

        r_push_vz = (
            0.18
            * vz.clamp(0.0, 3.0)
            * (pre_air & (age <= 18) & (pitch < math.radians(18.0)) & (roll < math.radians(12.0))).float()
        )
        early_air_pen = torch.zeros_like(r_push_vz)

        # --- 2. True All-Geom Airborne Clearance Potential (scaled to 0.42 m -> up to 47 cm!) ---
        true_air_clear = info[:, 0].clamp_min(0.0) * active.float() * (~broken).float()
        new_peak = torch.maximum(self.peak, true_air_clear)
        r_peak = 9.5 * (
            (new_peak / 0.42).clamp(0.0, 1.12).square() - (self.peak / 0.42).clamp(0.0, 1.12).square()
        )
        cross_380 = (new_peak >= 0.380) & ~self.paid_380_peak & active & ~broken
        self.paid_380_peak |= cross_380
        r_peak = r_peak + 3.0 * cross_380.float()
        self.peak.copy_(new_peak)

        # --- 3. Level-Chassis Flight (<=10 deg pitch, <=8 deg roll) & Horizontal Velocity Conservation ---
        r_air_level = air.float() * (
            0.10 * torch.exp(-((pitch / 0.14).square() + (roll / 0.12).square()))
            - 0.30 * ((pitch - math.radians(10.0)).clamp_min(0.0) / 0.10).square().clamp_max(12.0)
            - 0.35 * ((roll - math.radians(8.0)).clamp_min(0.0) / 0.08).square().clamp_max(12.0)
            - 0.12 * (vx - self.takeoff_vx).square().clamp_max(4.0)
            - 0.015 * (wx.square() + wy.square()).clamp_max(25.0)
        )

        # --- 4. Obstacle Crossing (Platform & Bridge Hurdle): Zero Vertical Face Impact or Chassis Scrape! ---
        face_or_scrape = (~is_flat) & ((info[:, 4] >= 1.0) | ((info[:, 3] >= 5.0) & (self.p[:, 0] >= self.edge - 0.15)))
        obs_first_hit = face_or_scrape & (self.hits < 1.0)
        self.hits = torch.maximum(self.hits, torch.where(~is_flat, info[:, 4], torch.zeros_like(self.hits)))
        r_hit_pen = 3.5 * obs_first_hit.float() + 0.45 * face_or_scrape.float()

        edge_cleared_now = (~is_flat) & (self.arc[:, 6] > 0.008) & ~self.paid_edge_margin & ~broken
        self.paid_edge_margin |= edge_cleared_now
        r_edge_clear = 3.5 * edge_cleared_now.float()

        plat_adv = ((info[:, 13] - self.edge + 0.25) / 0.58).clamp(0.0, 1.0)
        hurd_adv = ((info[:, 13] - self.edge + 0.20) / (self.obs_span + 0.38).clamp_min(0.40)).clamp(0.0, 1.0)
        high_plat = info[:, 6] > (self.wall_height - 0.012)
        high_hurd = (info[:, 6] > (self.wall_height - 0.012)) & (self.hits < 1.0)
        cand_prog = torch.where(
            is_plat,
            plat_adv * (air & high_plat & ~broken).float(),
            torch.where(is_hurdle, hurd_adv * ((air | (info[:, 13] > self.edge + self.obs_span)) & high_hurd & ~broken).float(), torch.zeros_like(plat_adv)),
        )
        new_prog = torch.maximum(self.air_progress, cand_prog)
        r_obs_prog = torch.where(is_hurdle, 7.5, 6.5) * (new_prog - self.air_progress)
        self.air_progress.copy_(new_prog)

        # --- 5. Compliant Skyhook Touchdown & Qualified Success ---
        floor_both = (info[:, 15:17].min(1).values > 5.0) & (info[:, 6] < 0.028)
        plat_both = is_plat & (info[:, 17:19].min(1).values > 5.0) & (info[:, 13] > self.edge + 0.03) & (self.hits < 1.0)
        hurd_land = (
            is_hurdle
            & floor_both
            & (info[:, 13] > self.edge + self.obs_span + 0.04)
            & (self.hits < 1.0)
        )
        valid_support = torch.where(is_plat, plat_both, torch.where(is_hurdle, hurd_land, floor_both))

        just_touched = landed & valid_support & (self.first_land_tick < 0)
        self.first_land_tick = torch.where(just_touched, self.tick, self.first_land_tick)
        absorbing = landed & (self.first_land_tick >= 0) & ((self.tick - self.first_land_tick) < 16)
        r_absorb_pen = absorbing.float() * (
            0.06 * info[:, 14].clamp_max(4.0)
            + 0.025 * (wx.abs() + wy.abs()).clamp_max(10.0)
            + 0.15 * (pitch.square() + roll.square())
        )

        stable_land = landed & valid_support & (pitch < math.radians(12.0)) & (roll < math.radians(10.0)) & (vz.abs() < 0.38)
        self.late_support = torch.where(stable_land, self.late_support + 1, torch.zeros_like(self.late_support))
        req_peak = torch.where(is_flat, torch.full_like(self.peak, 0.24), (self.wall_height + 0.005).clamp_min(0.22))
        qualified_now = (self.late_support >= 10) & (self.peak >= req_peak) & ~self.paid_success & ~broken
        self.paid_success |= qualified_now
        succ_bonus = torch.where(
            is_plat & (self.wall_height >= 0.355),
            14.0,
            torch.where(is_plat, 10.0, torch.where(is_hurdle, 13.0, 6.5)),
        )
        r_success = succ_bonus * qualified_now.float() + 0.10 * stable_land.float()

        post_rec = landed & (self.late_support >= 8)
        r_track = -0.06 * post_rec.float() * (vx - self.cmd).square().clamp_max(5.0)

        straight = (self.turn.abs() < 0.05).float()
        leg_asym = ((exec_act[:, 0:2] - exec_act[:, 2:4]).square().mean(1)) * straight
        act_smooth = (exec_act - self.previous).square().mean(1)
        r_reg = 0.008 * leg_asym + 0.002 * act_smooth

        ground_under = torch.where(
            (is_plat & (self.p[:, 0] > self.edge + 0.02))
            | (is_hurdle & (self.p[:, 0] > self.edge - 0.02) & (self.p[:, 0] < self.edge + self.obs_span + 0.02)),
            self.wall_height,
            torch.zeros_like(pos_z),
        )
        failed = (
            broken
            | (upright < 0.52)
            | (pitch > math.radians(44.0))
            | (roll > math.radians(35.0))
            | ((pos_z - ground_under) < 0.120)
            | (info[:, 7] >= CLOSURE_LIMIT)
        )
        press_age = (self.tick - self.press).clamp_min(0)
        max_press_age = torch.where(is_flat, torch.full_like(press_age, 118), torch.full_like(press_age, 185))
        timeout = ((self.press >= 0) & (press_age >= max_press_age)) | (self.tick >= 380) | (active & (self.late_support >= 22))
        done = failed | timeout

        missed_jump = done & (self.press >= 0) & ~failed & ~self.paid_success
        miss_pen = torch.where(is_flat, 2.0, 3.0) * missed_jump.float()

        reward = (
            r_crouch
            + r_push_vz
            + r_peak
            + r_air_level
            + r_edge_clear
            + r_obs_prog
            + r_success
            + r_track
            - early_air_pen
            - r_hit_pen
            - r_absorb_pen
            - r_reg
            - 10.0 * failed.float()
            - miss_pen
        )
        reward = torch.where(broken, torch.full_like(reward, -10.0), reward)

        tall = self.height >= 0.35
        rel_w = self.perturb_kind == 1
        plat380 = is_plat & (self.wall_height >= 0.355)
        succ_ep = done & ~failed & self.paid_success
        self.counts += torch.stack(
            (
                done.sum(),
                (done & failed).sum(),
                succ_ep.sum(),
                (done & (self.peak >= 0.380)).sum(),
                (done & is_flat).sum(),
                (succ_ep & is_flat).sum(),
                (done & is_flat & tall & (self.peak >= 0.360)).sum(),
                (done & rel_w).sum(),
                (succ_ep & rel_w).sum(),
                (done & is_plat).sum(),
                (succ_ep & is_plat).sum(),
                (done & plat380).sum(),
                (succ_ep & plat380).sum(),
                (succ_ep & is_hurdle).sum(),
            )
        ).long()

        self.previous.copy_(exec_act)
        self.reset(done)

        # Trigger manual Space press at sampled human distance d_press (or begin_tick on flat)
        ready = (self.press < 0) & (self.tick >= 45) & ~done
        at_obs_press = (self.p[:, 0] >= self.edge - self.press_dist) & ((self.edge - self.p[:, 0]) >= 0.25)
        press_now = ready & torch.where(
            self.kind == 0,
            self.tick >= self.begin_tick,
            at_obs_press | (self.tick >= self.begin_tick + 60),
        )
        self.press.copy_(torch.where(press_now, self.tick, self.press))
        self.press_speed.copy_(torch.where(press_now, vx, self.press_speed))

        changed = (self.fired_tick >= 0) & ((self.tick - self.fired_tick) >= self.perturb_tick)
        vx_goal = torch.where(changed, self.post_vx, torch.where(self.tick >= 18, self.speed, 0.0))
        wz_goal = torch.where(changed, self.post_wz, 0.0)
        self.cmd = torch.where(changed & self.abrupt_cmd, vx_goal, self.cmd + (vx_goal - self.cmd) / 10.0)
        self.turn = self.turn + (wz_goal - self.turn) / 10.0

        self.update_g_jump()

        # Exact rising-edge firing law matching JumpWarpPerceptionActor.fire_ready & Nav4DPolicy!
        armed_wait = (self.press >= 0) & (self.fired_tick < 0)
        h_m = self.height.clamp(0.20, 0.42)
        min_v_f = torch.where(self.kind >= 2, 1.75, torch.where(self.wall_height >= 0.34, 1.55, 1.25))
        v_eff = torch.maximum(vx.clamp(0.0, 3.2), 0.75 * torch.maximum(self.cmd, min_v_f)).clamp(1.0, 3.0)
        span_c = (self.g_jump[:, 1] - self.g_jump[:, 0]).clamp(0.0, 0.90)
        d_plat = 0.34 * v_eff + 0.55 * (h_m - 0.28) + 0.06
        d_hurd = 0.40 * v_eff + 0.50 * (h_m - 0.28) - 0.36 * span_c + 0.08
        d_sweet = torch.where(self.kind >= 2, d_hurd, d_plat).clamp(0.38, 1.28)
        speed_ok = vx >= (min_v_f - 0.30).clamp_max(2.10)
        fire_now = armed_wait & (
            (self.kind == 0)
            | ((self.g_jump[:, 0] <= d_sweet) & (speed_ok | (self.g_jump[:, 0] <= 0.52)))
            | ((self.tick - self.press) >= 85)
        )
        self.fired_tick.copy_(torch.where(fire_now, self.tick, self.fired_tick))

        self.observe()
        self.hist = torch.cat((self.hist[:, 1:], self.obs[:, None, :]), dim=1)
        self.hist[done] = self.obs[done, None, :]
        return self.obs, self.hist.flatten(1), reward, done

    def statistics(self) -> dict:
        return dict(
            columns=[
                "episodes",
                "falls",
                "qualified_success",
                "peak_ge_380mm",
                "flat_eps",
                "flat_succ",
                "flat_tall_ge360",
                "relW_eps",
                "relW_succ",
                "plat_eps",
                "plat_succ",
                "plat380_eps",
                "plat380_succ",
                "bridge_hurdle_succ",
            ],
            counts=self.counts.tolist(),
            sample_min=self.range_low.tolist(),
            sample_max=self.range_high.tolist(),
            full_dr_envs=int(self.dr.sum()),
            key_hold_range=[int(self.key_hold.min()), int(self.key_hold.max())],
        )
