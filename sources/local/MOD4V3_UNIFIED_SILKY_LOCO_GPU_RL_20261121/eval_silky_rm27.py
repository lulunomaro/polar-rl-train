"""Independent MuJoCo rollouts with per-physics-step contact adjudication."""
from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor
from itertools import product
import json
import math
import os
from pathlib import Path
import sys
from xml.etree import ElementTree as ET

import mujoco as mj
import numpy as np
import torch

from train_silky_loco import put, sha256
from silky_geometry import (PHYSICS_DT as DT, POLICY_SUBSTEPS, SUPPORT_FORCE_N as FORCE,
                            SUPPORT_STEPS as HOLD_STEPS, TRANSITION_SUPPORT_STEPS,
                            oblique_edge, rm27_profile)
from unified_soft_moe import EXPERTS, UnifiedSoftMoEActor

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent
R61 = LOCAL/'MOD4V3_AUTONOMOUS_MOE_REPAIR_20261120'
E0 = LOCAL/'MOD4V3_E0_FLAT_ROUGH_REPAIR_20261120'
MAP_CACHE = LOCAL/'MOD4V3_AUTONOMOUS_MOE_ALL_MAPS_20261120/runtime_cache'
sys.path[:0] = [str(R61), str(E0)]
import play_repaired_r61 as legacy
from play_e0_candidate import manifest_drive

ANGLE = math.pi/180.
CONTROL = ('R61', 'SELECTED_E0')
HEIGHTS = (.20, .28, .36, .42)
HIGH_SPEED_COMMANDS = (2.4, 2.8)
HIGH_SPEED_SEED = 2712828
RM = {'rm27_west': (-16.8, -4.0, 1), 'rm27_east': (-5.6, -5.9, -1)}
AA = {'rm27_west_400': (0., 0., 1), 'rm27_east_400': (0., 0., 1)}
DOUBLE = {**RM, **AA}
LEVELS = {'curb_11': (.11,), 'step_20': (.20,), 'oblique_20': (.20,),
          **{key: (.20, .35) for key in RM}, **{key: (.20, .40) for key in AA}}
TRACE_COLUMNS = ('time_s', 'command_m_s', 'forward_com_m_s', 'course_progress_m', 'pitch_deg',
                 'yaw_error_deg', 'tilt_deg', 'left_leg_m', 'right_leg_m', 'left_wheel_s_m',
                 'right_wheel_s_m', 'left_first_edge_m', 'right_first_edge_m', 'left_second_edge_m',
                 'right_second_edge_m', 'riser_contact_step1', 'riser_contact_step2',
                 'left_torque_abs_nm', 'right_torque_abs_nm', 'height_above_start_m', 'yaw_rate_rad_s',
                 'step1_left_normal_z_n', 'step1_right_normal_z_n', 'step2_left_normal_z_n', 'step2_right_normal_z_n',
                 *[f'router_weight_{i}' for i in range(len(EXPERTS))])


class PolicyLoco:
    def __init__(self, checkpoint):
        self.checkpoint = checkpoint
        payload = torch.load(checkpoint, map_location='cpu', weights_only=False)
        if payload['format'] != 'mod4v3_unified_soft_moe_v1':
            raise ValueError('Expected a UnifiedSoftMoEActor checkpoint')
        raw = payload['actor_state_dict']
        self.layers = UnifiedSoftMoEActor()
        self.layers.load_state_dict({key.removeprefix('mlp.'): value
                                     for key, value in raw.items() if key.startswith('mlp.')})
        self.layers.eval()
        self.sha = sha256(checkpoint)
        self.reset_history()

    def reset_history(self):
        self.history = None

    @torch.inference_mode()
    def act(self, obs):
        if self.history is None:
            self.history = np.repeat(obs[None], 12, axis=0)
        else:
            self.history[:-1] = self.history[1:]
            self.history[-1] = obs
        signature = np.concatenate((obs, self.history.ravel()))
        action = self.layers(torch.from_numpy(signature)[None]).clamp(-6., 6.).numpy()[0]
        weights = self.layers.last_weights.numpy()[0]
        return action, {f'expert_{i}': float(v) for i, v in enumerate(weights)}


class E0Policy:
    def __init__(self):
        parent, sha, _ = legacy.load_manifest(R61/'CANDIDATE_R61_RAISED_READY.json')
        manifest = E0/'SELECTED_E0.json'
        config = json.loads(manifest.read_text(encoding='utf-8'))
        self.actor = manifest_drive(parent.stair.e0, manifest, config)
        self.sha = config['e0_sha256']

    def reset_history(self):
        pass

    @torch.inference_mode()
    def act(self, obs):
        action = self.actor(torch.from_numpy(obs)[None, :]).clamp(-6., 6.).numpy()[0]
        return action, {'e0': 1.}


def model_policy(name):
    if name == 'SELECTED_E0':
        policy = E0Policy()
        return policy, policy.sha
    if name == 'R61':
        manifest = R61/'CANDIDATE_R61_RAISED_READY.json'
        policy, _, _ = legacy.load_manifest(manifest)
        if policy.runtime_sha != json.loads(manifest.read_text(encoding='utf-8'))['runtime_sha256']:
            raise ValueError('R61 runtime hash mismatch')
        return policy, policy.runtime_sha
    policy = PolicyLoco(Path(name))
    return policy, policy.sha


def metadata(course, cache):
    maps = legacy.maps
    maps.CACHE_DIR = cache
    if course in RM:
        return dict(xml_path=str(MAP_CACHE/'scene_rmuc2027_mod4v3_v1.xml'),
                    mjb_path=str(MAP_CACHE/'scene_rmuc2027_mod4v3_v1.mjb'),
                    spawns=[dict(x=0., y=0., yaw_deg=0.)], hide_group5=True)
    if course in AA:
        return build_aa(course, cache)
    if course == 'rough_L9':
        return maps.build_rough_v1_tile('随机起伏', 9)
    if course in ('flat60', 'flat') or course.startswith('oblique_20'):
        tree, root = maps._load_base_robot_tree()
        maps._add_checker_sky_and_floor(root, floor_size='30 30 .1')
        cache.mkdir(parents=True, exist_ok=True)
        if course.startswith('oblique_20'):
            sign = -1 if course.endswith('_negative') else 1
            width = 2.
            polygon = [(1.+oblique_edge(-width, sign), -width), (5., -width),
                       (5., width), (1.+oblique_edge(width, sign), width)]
            vertices = ' '.join(f'{x} {y} {z}' for z in (0., .20) for x, y in polygon)
            ET.SubElement(root.find('asset'), 'mesh', name='oblique_tread', vertex=vertices)
            ET.SubElement(root.find('worldbody'), 'geom', name='oblique_tread', type='mesh',
                          mesh='oblique_tread', contype='1', conaffinity='2', rgba='.34 .49 .58 1')
        path = cache/f'{course}.xml'
        tree.write(path, encoding='utf-8', xml_declaration=True)
        return dict(xml_path=str(path), spawns=[dict(x=0., y=0., yaw_deg=0.)], hide_group5=False)
    return maps.build_serial_leg_course('11cm' if course == 'curb_11' else '20cm')


def entrance_edges(course, y):
    floor, offset, lip = rm27_profile('west' in course)
    return np.clip(offset+.70*y, floor, lip-.31), np.full_like(y, lip)


def build_aa(course, cache):
    """Construct an independent A–A section fixture with surveyed entry angles."""
    maps = legacy.maps
    tree, root = maps._load_base_robot_tree()
    maps._add_checker_sky_and_floor(root)
    asset, world = root.find('asset'), root.find('worldbody')
    lip = float(entrance_edges(course, np.zeros(1))[1][0])
    floor, offset, _ = rm27_profile('west' in course)
    kink = (floor-offset)/.70
    # Convex footprint for the 200 mm tread, including the oblique face.
    width = .80
    profile = [(floor, -width), (lip, -width), (lip, width), (offset+.70*width, width), (floor, kink)]
    positions = [f'{x} {y} {z}' for z in (0., .20) for x, y in profile]
    ET.SubElement(asset, 'mesh', name='aa_tread', vertex=' '.join(positions))
    ET.SubElement(world, 'geom', name='aa_tread', type='mesh', mesh='aa_tread',
                  contype='1', conaffinity='2', rgba='.34 .49 .58 1')
    for name, lo, hi, height, rgba in (
            ('aa_lip', lip, lip+.15, .40, '.91 .70 .23 1'),
            ('aa_deck', lip+.15, lip+2.4, .36, '.41 .50 .56 1')):
        ET.SubElement(world, 'geom', name=name, type='box', pos=f'{(lo+hi)/2} 0 {height/2}',
                      size=f'{(hi-lo)/2} {width} {height/2}', contype='1', conaffinity='2', rgba=rgba)
    cache.mkdir(parents=True, exist_ok=True)
    path = cache/f'{course}.xml'
    tree.write(path, encoding='utf-8', xml_declaration=True)
    return dict(xml_path=str(path), spawns=[dict(x=-.2, y=0., yaw_deg=0.)], hide_group5=False)


def cases():
    rng = np.random.default_rng(2711286)
    rows = []

    def add(course, speed, height, yaw, offset, duration, settle=.50, wz=0., task=None):
        rows.append(dict(id=f'{course}_{len(rows):03d}', course=course, speed=speed, height=height,
                         yaw_deg=yaw, offset=offset, seconds=duration, settle_s=settle, wz=wz, task=task))

    classic = [('forward20', 2., 0., .28), ('forward22', 2.2, 0., .28),
               ('reverse15', -1.5, 0., .28), ('yaw14137', 0., 4.5*math.pi, .28),
               ('height020', 0., 0., .20), ('height040', 0., 0., .40)]
    for seed in range(10):
        for task, speed, wz, height in classic:
            add('flat60', speed, height, float(rng.uniform(-3, 3)),
                [float(rng.uniform(-.09, .09)), float(rng.uniform(-.10, .10))], 12., 0., wz, task)
            rows[-1]['seed'] = seed
    for course, height, (speed, wz) in product(('flat', 'rough_L9'), HEIGHTS,
                                               ((-.6, 0.), (1., 0.), (0., -1.8), (0., 1.8))):
        add(course, speed, height, float(rng.uniform(-6, 6)), list(rng.uniform(-.25, .25, 2)), 2.5, wz=wz)
    for course, speeds, heights, angles in (
            ('curb_11', (.60, 1., 1.5), (.28, .42), (0.,)),
            ('step_20', (.60, 1., 1.5), HEIGHTS, (-25., -20., 0., 20., 25.)),
            ('rm27_west', (.60, 1., 1.4), (.28, .42), (0.,)),
            ('rm27_east', (.60, 1., 1.4), (.28, .42), (0.,)),
            ('rm27_west_400', (.60, 1., 1.4), (.28, .42), (0.,)),
            ('rm27_east_400', (.60, 1., 1.4), (.28, .42), (0.,))):
        for speed, height, yaw, sign in product(speeds, heights, angles, (-1., 1.)):
            if course in DOUBLE:
                offset = [float(rng.uniform(-.23, -.12)), float(sign*rng.uniform(.044, .115))]
                angle = yaw + float(rng.uniform(-1.8, 1.8))
            else:
                offset = [float(rng.uniform(-.20, -.055)), float(sign*rng.uniform(.21, .39))]
                angle = yaw
            add(course, speed, height, angle, offset, 5.6 if course in DOUBLE else 4.7)
    for speed, height, yaw, sign in product((.60, 1., 1.5), (.28, .42), (-20., 0., 20.), (-1, 1)):
        add('oblique_20', speed, height, yaw, list(rng.uniform(-.16, -.075, 2)), 4.7)
        rows[-1]['edge_sign'] = sign
    return rows


def high_speed_cases():
    """Pair both commands at the same four heights and two held-out starts per course."""
    rng = np.random.default_rng(HIGH_SPEED_SEED)
    rows = []
    for course, height, side in product(('flat', 'rough_L9', *LEVELS), HEIGHTS, (-1, 1)):
        if course in DOUBLE:
            offset = [float(rng.uniform(-.23, -.12)), float(side*rng.uniform(.044, .115))]
            yaw, seconds = float(rng.uniform(-1.8, 1.8)), 5.6
        elif course == 'oblique_20':
            offset = list(map(float, rng.uniform(-.16, -.075, 2)))
            yaw, seconds = side*20., 4.7
        elif course in LEVELS:
            offset = [float(rng.uniform(-.20, -.055)), float(side*rng.uniform(.21, .39))]
            yaw, seconds = 0., 4.7
        else:
            # Leave a full-speed run inside the nine-metre L9 tile.
            x = -1.6 if course == 'rough_L9' else 0.
            offset = [x+float(rng.uniform(-.09, .09)), float(side*rng.uniform(.09, .21))]
            yaw, seconds = float(rng.uniform(-3., 3.)), 2.4
        for speed in HIGH_SPEED_COMMANDS:
            case = dict(id=f'hs_{course}_{len(rows):03d}', course=course, speed=speed, height=height,
                        yaw_deg=yaw, offset=offset, seconds=seconds, settle_s=.50, wz=0., task=None,
                        independent_standing_pose=True)
            if course == 'oblique_20':
                case['edge_sign'] = side
            rows.append(case)
    return rows


def tire_radii(sim):
    ids = sim.tire_gids
    if not np.all(sim.m.geom_type[ids] == mj.mjtGeom.mjGEOM_CYLINDER):
        raise ValueError('Expected main-wheel cylinder collision geometry')
    return sim.m.geom_size[ids, 0].copy()


def reset(sim, case):
    d, m = sim.d, sim.m
    course = case['course']
    motion_sign = 1 if case['speed'] >= 0 else -1
    if course in DOUBLE:
        x, y, direction = DOUBLE[course]
        x += direction*case['offset'][0]
        y += direction*case['offset'][1]
    elif course in LEVELS:
        x, y = case['offset']
        direction = 1
    else:
        direction = 1
        x, y = case['offset']
        if course != 'flat60':
            x -= motion_sign*1.4
    yaw = case['yaw_deg']*ANGLE + (0. if direction > 0 else math.pi)
    h = case['height']
    mj.mj_resetData(m, d)
    mj.mj_forward(m, d)
    z_ground = sim.ground_z(x, y, 4.5)
    length = np.clip(h-float(tire_radii(sim).mean()), .14, .35)
    fit = sim.ik.fit(np.hypot(length, sim.ik.lateral_offset), 0.)['qpos']
    d.qpos[:] = fit
    d.qpos[:3] = [x, y, z_ground+h+.003]
    d.qpos[3:7] = [math.cos(yaw/2), 0, 0, math.sin(yaw/2)]
    if course == 'flat60':
        rng = np.random.default_rng(case['seed'])
        d.qvel[:6] = rng.uniform(-.015, .015, 6)
    mj.mj_forward(m, d)
    sim.unified.reset_history()
    sim.prev_a[:] = 0.
    sim.target_h = h
    sim.cmd_wz = sim.cmd_vx = 0.
    return yaw, direction, z_ground


class StrictJudge:
    def __init__(self, sim, case, yaw, direction, ground):
        self.sim = sim
        self.case = case
        self.course = case['course']
        self.levels = LEVELS.get(self.course, ())
        self.ground = ground
        self.direction = direction
        self.yaw = yaw
        self.tick = 0
        self.trace = []
        self.track = np.zeros(max(1, len(self.levels)), dtype=np.int64)
        self.support_required = (TRANSITION_SUPPORT_STEPS, HOLD_STEPS) if self.course in DOUBLE else (HOLD_STEPS,)
        self.track50 = self.track.copy()
        self.longest = self.track.copy()
        self.longest50 = self.track.copy()
        self.first_support = [None] * len(self.track)
        self.first_support50 = [None] * len(self.track)
        self.lip = np.zeros(2, dtype=bool)
        self.deck_top = .36 if self.course in AA else .30
        self.weights = np.full(len(EXPERTS), np.nan)
        self.tire_radii = tire_radii(sim)
        self.loaded_center_z = []
        m = sim.m
        self.robot_side = {int(g): i for i, g in enumerate(sim.tire_gids)}
        self.tires = set(self.robot_side)
        for g in range(m.ngeom):
            if m.geom(g).name.startswith('guide_wheel_'):
                self.robot_side[g] = int(m.body(m.geom_bodyid[g]).name.startswith('right_'))
        def static_body(body):
            while body:
                if m.body_jntnum[body]:
                    return False
                body = m.body_parentid[body]
            return True

        self.terrain = {g for g in range(m.ngeom) if m.geom_contype[g] and static_body(m.geom_bodyid[g])}
        self.force_buffer = np.zeros(6)

    def edge(self, xy):
        if self.course == 'oblique_20':
            return 1.+oblique_edge(xy[:, 1], self.case['edge_sign']), np.full(len(xy), 99.)
        if self.course not in DOUBLE:
            return np.full(len(xy), 1.), np.full(len(xy), 99.)
        _, y, sign = DOUBLE[self.course]
        local_y = (xy[:, 1]-y)*sign
        return entrance_edges(self.course, local_y)

    def progress(self, xy):
        x = DOUBLE[self.course][0] if self.course in DOUBLE else 0.
        return self.direction*(xy[..., 0]-x)

    def observe(self, progress_command, yaw_command):
        m, d = self.sim.m, self.sim.d
        self.tick += 1
        rotation = d.xmat[self.sim.env.base_id].reshape(3, 3)
        yaw = math.atan2(rotation[1, 0], rotation[0, 0])
        tilt = math.degrees(math.acos(float(np.clip(rotation[2, 2], -1, 1))))
        pitch = math.degrees(math.asin(float(np.clip(-rotation[2, 0], -1, 1))))
        yaw_error = math.degrees(math.remainder(yaw-self.yaw-yaw_command, 2*math.pi))
        # Whole-articulation CoM velocity, including leg/wheel motion.
        mj.mj_subtreeVel(m, d)
        velocity = d.subtree_linvel[self.sim.env.base_id]
        vx = float(velocity[:2] @ [math.cos(yaw), math.sin(yaw)])
        pos = d.subtree_com[self.sim.env.base_id].copy()
        progress = float(self.progress(pos[:2]))
        wheel_pos = d.geom_xpos[self.sim.tire_gids]
        wheel_s = self.progress(wheel_pos[:, :2])
        edge, lip_start = self.edge(wheel_pos[:, :2])
        lengths = np.linalg.norm(wheel_pos - d.xpos[self.sim.env.base_id], axis=1)
        force = np.zeros((len(self.track), 2))
        lip = np.zeros(2, dtype=bool)
        wall = np.zeros((len(self.levels), 2), dtype=bool)
        for i in range(d.ncon):
            contact = d.contact[i]
            a, b = map(int, contact.geom)
            if a in self.robot_side and b in self.terrain:
                robot, sign = a, -1
            elif b in self.robot_side and a in self.terrain:
                robot, sign = b, 1
            else:
                continue
            mj.mj_contactForce(m, d, i, self.force_buffer)
            normal = sign*contact.frame[:3]
            vertical = self.force_buffer[0]*normal[2]
            side = self.robot_side[robot]
            if not self.levels:
                if robot in self.tires and vertical > 0.:
                    force[0, side] += vertical
                continue
            p = self.progress(contact.pos[:2])
            z = contact.pos[2]-self.ground
            c_edge, c_lip = self.edge(contact.pos[None, :2])
            for k, top in enumerate(self.levels):
                limit = float((c_edge if k == 0 else c_lip)[0])
                if (self.force_buffer[0] > FORCE and self.direction*normal[0] < -.70
                        and abs(p-limit) < .18 and wheel_pos[side, 2]-self.ground < top):
                    wall[k, side] = True
                if robot not in self.tires or vertical <= 0. or p < limit-.025:
                    continue
                if k == 0 and abs(z-top) <= .026 and p < c_lip[0]+.017:
                    force[k, side] += vertical
                if k == 1:
                    if abs(z-top) <= .021 and p < c_lip[0]+.175:
                        force[k, side] += vertical
                        lip[side] |= vertical >= FORCE
                    elif abs(z-self.deck_top) <= .020 and p > c_lip[0]+.12:
                        force[k, side] += vertical
        torque = np.abs(d.ctrl[self.sim.env.act_ids[4:]])
        if not self.levels or progress_command >= .55:
            self.lip |= lip
            for k, required in enumerate(self.support_required):
                measured = bool((force[k] >= FORCE).all()) and (k == 0 or bool(self.lip.all()))
                good = measured and (k == 0 or self.first_support[0] is not None)
                self.track[k] = self.track[k]+1 if good else 0
                self.longest[k] = max(self.longest[k], self.track[k])
                if self.track[k] >= required and self.first_support[k] is None:
                    self.first_support[k] = self.tick-required
                if self.tick % POLICY_SUBSTEPS == 0:
                    good50 = measured and (k == 0 or self.first_support50[0] is not None)
                    self.track50[k] = self.track50[k]+1 if good50 else 0
                    self.longest50[k] = max(self.longest50[k], self.track50[k])
                    if self.track50[k] >= required//POLICY_SUBSTEPS and self.first_support50[k] is None:
                        self.first_support50[k] = self.tick-required
        if self.course == 'flat60' and (force[0] >= FORCE).all():
            self.loaded_center_z.append(wheel_pos[:, 2]-self.ground)
        normal_n = np.full(4, np.nan)
        normal_n[:force.size] = force.ravel()
        wall_flags = np.zeros(2, dtype=bool)
        wall_flags[:len(wall)] = wall.any(1)
        self.trace.append([self.tick*DT, progress_command, vx, progress, pitch, yaw_error, tilt,
                           *lengths, *wheel_s, *edge, *lip_start, *wall_flags, *torque,
                           float(d.qpos[2]-self.ground), float(d.qvel[5]), *normal_n, *self.weights])

    def result(self, failure, closure):
        trace = np.asarray(self.trace, dtype=np.float64)
        speed = self.case['speed']
        tail_duration = 4. if self.course == 'flat60' else 1.
        tail = trace[-round(tail_duration/DT):]
        moving = trace[trace[:, 1] >= .55]
        stalls, cycles, momentum, rollback, unload, entry = [], [], [], [], [], []
        for k in range(len(self.levels)):
            start = np.maximum(moving[:, 9]-(moving[:, 11] if k == 0 else moving[:, 13]),
                               moving[:, 10]-(moving[:, 12] if k == 0 else moving[:, 14]))
            in_zone = np.flatnonzero((start >= -.22) | moving[:, 15+k].astype(bool))
            if k and self.first_support[0] is None:
                in_zone = in_zone[start[in_zone] >= -.22]
            if not len(in_zone):
                stalls.append(None)
                cycles.append(None)
                momentum.append(None)
                rollback.append(None)
                unload.append(None)
                entry.append(None)
                continue
            end = self.first_support[k]
            begin = in_zone[0]
            portion = moving[begin:] if end is None else moving[begin:][moving[begin:, 0] <= end*DT+DT]
            if not len(portion):
                portion = moving[begin:begin+1]
            stalls.append(float((portion[:, 2] < .10).sum()*DT))
            momentum.append(float((portion[:, 2] >= .20).mean()))
            rollback.append(float(100.*(np.maximum.accumulate(portion[:, 3])-portion[:, 3]).max()))
            wall = portion[:, 15+k].astype(bool)
            unload.append(dict(riser_contact_s=float(wall.sum()*DT),
                               wheel_abs_torque_peak_nm=float(portion[wall, 17:19].max()) if wall.any() else None))
            entry.append(float(portion[0, 2]))
            cycles.append([count_retractions(portion[:, j]) for j in (7, 8)])
        stable = bool((self.longest >= self.support_required).all())
        moving_rollback = float(100.*(np.maximum.accumulate(moving[:, 3])-moving[:, 3]).max()) if len(moving) else 0.
        relaxed_pump = [max(row) if row is not None else None for row in cycles]
        travel_pass = failure is None and stable and (
            all(v is not None and v < .25 for v in stalls)
            and all(v == 1 for v in relaxed_pump) and moving_rollback < 3.)
        criteria = None
        if self.course == 'flat60':
            task = self.case['task']
            if task.startswith('height'):
                criteria = abs(float(tail[:, 19].mean())-self.case['height']) <= .02
            elif self.case['wz']:
                criteria = abs(float(tail[:, 20].mean())-self.case['wz']) <= abs(self.case['wz'])*.02
            else:
                criteria = abs(float(tail[:, 2].mean())-speed) <= (.20 if speed < 0 else .15)
        if self.course in ('flat', 'rough_L9'):
            criteria = (float(np.abs(tail[:, 2]-speed).mean()) <= .25 and
                        abs(float(tail[:, 20].mean())-self.case['wz']) <= .60)
        router = trace[:, -len(EXPERTS):]
        return dict(**self.case, passed=bool((criteria and failure is None) if criteria is not None else travel_pass),
            failure=failure, physical_both_wheels_400hz=stable, stable_seconds_400hz=(self.longest*DT).tolist(),
            required_support_ticks_400hz=self.support_required,
            stable_seconds_50hz=(self.longest50*.020).tolist(),
            wheel_collision_radius_m=self.tire_radii.tolist(),
            flat_loaded_wheel_center_z_m=np.median(self.loaded_center_z, axis=0).tolist() if self.loaded_center_z else None,
            rm27_lip_support_each_wheel=self.lip.tolist() if self.course in DOUBLE else None,
            stall_time_lt_0p1=[None if v is None else round(v, 6) for v in stalls],
            momentum_fraction_ge_0p2=momentum, riser_unloading=unload, entry_speed_m_s=entry,
            retraction_cycles_per_step=relaxed_pump, retraction_cycles_per_wheel=cycles, per_step_rollback_cm=rollback,
            max_rollback_cm=moving_rollback, max_abs_pitch_deg=float(np.abs(trace[:, 4]).max()),
            max_yaw_err_deg=float(np.abs(trace[:, 5]).max()),
            max_closure_m=closure, max_tilt_deg=float(trace[:, 6].max()), simulated_s=float(trace[-1, 0]),
            tail_forward_m_s=float(tail[:, 2].mean()), tail_mean_abs_speed_error_m_s=float(np.abs(tail[:, 2]-speed).mean()),
            tail_yaw_rad_s=float(tail[:, 20].mean()), tail_height_m=float(tail[:, 19].mean()),
            router_mean=router.mean(0).tolist() if np.isfinite(router).all() else None)


def count_retractions(length):
    """Count shortening strokes of at least 12 mm, with 8 mm recovery hysteresis."""
    peak = trough = float(length[0])
    count = 0
    retracting = False
    for reading in length[1:]:
        if retracting:
            trough = min(trough, reading)
            if reading-trough >= .008:
                retracting = False
                peak = reading
        else:
            peak = max(peak, reading)
            if peak-reading >= .012:
                count += 1
                retracting = True
                trough = reading
    return count


class Replay:
    def __init__(self, name, course, cache, edge_sign=1):
        policy, self.sha = model_policy(name)
        self.name = name
        self.sim = legacy.AutonomousMapSimulation(policy, self.sha, show_viewer=False)
        fixture = f'{course}_negative' if course == 'oblique_20' and edge_sign < 0 else course
        meta = metadata(fixture, cache)
        if course in RM:
            x, y, sign = RM[course]
            meta['spawns'][0].update(x=x, y=y, yaw_deg=0. if sign > 0 else 180.)
        self.sim.load_map(meta)
        self.standing_pose_seed = self.sim.ik.q.copy()

    def run(self, case, frames=None, policy_sample=None):
        sim = self.sim
        m, d, env = sim.m, sim.d, sim.env
        if case.get('independent_standing_pose', False):
            sim.ik.q = self.standing_pose_seed.copy()
        yaw, direction, ground = reset(sim, case)
        judge = StrictJudge(sim, case, yaw, direction, ground)
        closure = 0.
        failure = None
        settle = round(case['settle_s']/.020)
        n = round(case['seconds']/.020)
        policy = sim.unified
        actual_yaw = 0.
        for count in range(n+settle):
            moving = count >= settle
            vx = case['speed'] if moving else 0.
            wz = case['wz'] if moving else 0.
            sim.cmd_vx += (vx-sim.cmd_vx)*.020/.14
            sim.cmd_wz += (wz-sim.cmd_wz)*.020/.14
            if self.name == 'R61':
                policy.allow_stair = vx > 0. and not wz
                policy.stair_driver_speed = vx if policy.allow_stair else None
            observation = sim._observe(False)
            action, weights = policy.act(observation)
            if policy_sample is not None:
                policy_sample(observation, action, judge)
            if isinstance(policy, PolicyLoco):
                judge.weights = np.array([weights[f'expert_{i}'] for i in range(len(EXPERTS))])
            if not np.isfinite(action).all():
                raise FloatingPointError('nonfinite deterministic action')
            native = torch.from_numpy(np.asarray(action, dtype=np.float32)[PPO_TO_NATIVE]).reshape(1, 6)
            for substep in range(POLICY_SUBSTEPS):
                effort = env._torque(native).numpy().reshape(-1)
                if substep % 4 == 0:
                    d.ctrl[env.act_ids[:4]] = effort[:4]
                d.ctrl[env.act_ids[4:]] = effort[4:]
                mj.mj_step(m, d)
                if not (np.isfinite(d.qpos).all() and np.isfinite(d.qvel).all()):
                    raise FloatingPointError('nonfinite physics')
                actual_yaw += wz*DT
                judge.observe(vx, actual_yaw)
                closure = max(closure, *(float(np.linalg.norm(d.site_xpos[a]-d.site_xpos[b])) for a, b in sim.pairs))
                if closure > 1.:
                    failure = 'catastrophic_closure'
                elif judge.trace[-1][6] > 67. or d.qpos[2] < ground+.085:
                    failure = 'fall'
                if failure:
                    break
            sim.prev_a = action
            if frames is not None:
                frames(sim, judge, failure)
            if failure:
                break
        raw = np.array(judge.trace, dtype=np.float64)
        if raw.shape[1] != len(TRACE_COLUMNS) or not np.isfinite(raw[:, :21]).all():
            raise ValueError(f'Invalid raw physics trace for {case["id"]}')
        self.last_support_tick = judge.first_support
        return judge.result(failure, closure), raw


from play_unified_moe_all_maps import PPO_TO_NATIVE


def evaluate_group(task):
    name, chunk, directory = task
    torch.set_num_threads(1)
    cache = directory/'maps'/f'{os.getpid()}'
    replays = {}
    rows, traces = [], {}
    for case in chunk:
        key = (case['course'], case.get('edge_sign', 1))
        if key not in replays:
            replays.clear()
            replays[key] = Replay(name, key[0], cache, key[1])
        replay = replays[key]
        row, trace = replay.run(case)
        rows.append(row)
        traces[row['id']] = trace
    return replay.sha, rows, traces


def add_high_speed_metrics(row, trace):
    moving = trace[trace[:, 1] >= .55]
    vx = moving[:, 2]
    best = None
    if len(vx) >= HOLD_STEPS:
        distance = np.concatenate(([0.], np.cumsum(vx)))
        best = float(((distance[HOLD_STEPS:] - distance[:-HOLD_STEPS]) / HOLD_STEPS).max())
    row.update(peak_forward_com_m_s=float(vx.max()) if len(vx) else None,
               best_400ms_mean_forward_com_m_s=best, reached_command_for_400ms=best is not None and best >= row['speed'])

    # Ground support in the legacy judge can come from the stationary settle.
    seconds = row['stable_seconds_400hz']
    if row['course'] not in LEVELS:
        loaded = (moving[:, 21:23] >= FORCE).all(1)
        bounds = np.flatnonzero(np.diff(np.r_[False, loaded, False]))
        seconds = [float(np.max(bounds[1::2]-bounds[::2], initial=0)*DT)]
    row['driving_support_seconds_400hz'] = seconds
    row['driving_supported_400hz'] = all(span >= ticks*DT for span, ticks in
                                       zip(seconds, row['required_support_ticks_400hz'], strict=True))


def high_speed_summary(rows):
    report = []
    for course, command in product(('flat', 'rough_L9', *LEVELS), HIGH_SPEED_COMMANDS):
        group = [row for row in rows if row['course'] == course and row['speed'] == command]
        if group:
            peak = [r['peak_forward_com_m_s'] for r in group if r['peak_forward_com_m_s'] is not None]
            sustained = [r['best_400ms_mean_forward_com_m_s'] for r in group
                         if r['best_400ms_mean_forward_com_m_s'] is not None]
            entry = [r['entry_speed_m_s'][0] for r in group if r['entry_speed_m_s'] and r['entry_speed_m_s'][0] is not None]
            report.append(dict(course=course, command_m_s=command, cases=len(group),
                               passed=sum(r['passed'] for r in group), falls=sum(r['failure'] == 'fall' for r in group),
                               driving_supported_400hz=sum(r['driving_supported_400hz'] for r in group),
                               median_tail_forward_com_m_s=float(np.median([r['tail_forward_m_s'] for r in group])),
                               median_first_riser_entry_com_m_s=float(np.median(entry)) if entry else None,
                               median_peak_forward_com_m_s=float(np.median(peak)) if peak else None,
                               median_best_400ms_mean_forward_com_m_s=float(np.median(sustained)) if sustained else None,
                               max_best_400ms_mean_forward_com_m_s=max(sustained) if sustained else None,
                               reached_command_for_400ms=sum(r['reached_command_for_400ms'] for r in group)))
    return report


def evaluate(names, output, workers, quick=False, courses=None, high_speed=False):
    selected = [case for case in (high_speed_cases() if high_speed else cases())
                if courses is None or case['course'] in courses]
    if not selected:
        raise ValueError('No matching evaluation cases')
    if quick:
        selected = [next(c for c in selected if c['course'] == key)
                    for key in sorted({c['course'] for c in selected})]
    report, trajectories = {}, {}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for name in names:
            chunks = [selected[i:i+8] for i in range(0, len(selected), 8)]
            rows = []
            for sha, group, raw in pool.map(evaluate_group, ((name, c, output.parent) for c in chunks)):
                if high_speed:
                    for row in group:
                        add_high_speed_metrics(row, raw[row['id']])
                rows.extend(group)
                trajectories.update({f"{Path(name).stem}_{k}": v for k, v in raw.items()})
                print(Path(name).stem, len(rows), '/', len(selected), flush=True)
            report[name] = dict(sha256=sha, rows=rows, summary={
                course: dict(cases=len(subset), passed=sum(row['passed'] for row in subset),
                             supported_400hz=sum(row['physical_both_wheels_400hz'] for row in subset),
                             falls=sum(row['failure'] == 'fall' for row in subset))
                for course in sorted({r['course'] for r in rows})
                for subset in [[row for row in rows if row['course'] == course]]
            })
            if high_speed:
                report[name]['by_terrain_and_command'] = high_speed_summary(rows)
    np.savez_compressed(output.with_suffix('.npz'), **trajectories)
    payload = dict(physics_hz=400, policy_hz=50, contact_normal_force_n=FORCE,
        continuity_s=HOLD_STEPS*DT, double_transition_continuity_s=TRANSITION_SUPPORT_STEPS*DT,
        seed=HIGH_SPEED_SEED if high_speed else 2711286, quick=quick, cases_per_model=len(selected), policies=report,
        trace_columns=TRACE_COLUMNS, router_experts=EXPERTS,
        rm27_fixture={'350_300_mm': 'Published full-map tiled collision, east / west',
                      '400_360_mm': 'A-A section fixture, east / west front profile'})
    if high_speed:
        payload.update(suite='HIGH_SPEED_2P8MS', command_speeds_m_s=HIGH_SPEED_COMMANDS,
                       forward_speed_window_s=HOLD_STEPS*DT, standing_pose_initialization='map_ik_seed_per_case')
    put(output, payload)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--models', nargs='+', default=CONTROL)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--quick', action='store_true')
    parser.add_argument('--courses', nargs='+')
    parser.add_argument('--high-speed', action='store_true')
    args = parser.parse_args()
    output = args.out or HERE/('HIGH_SPEED_2P8MS.json' if args.high_speed else 'BASELINE_AUDIT.json')
    output.parent.mkdir(parents=True, exist_ok=True)
    evaluate(args.models, output, args.workers, args.quick, args.courses, args.high_speed)


if __name__ == '__main__':
    main()
