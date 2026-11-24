"""Pinned MOD4v3 plant, physical obstacles, and independent 400 Hz measurement."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import mujoco
import numpy as np
import torch

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "MOD4V3_RL_HIGH_MOVING_JUMP_20261118"
sys.path.insert(0, str(OLD))
from rl_jump_env import (
    ACTION_SCALE_LEG, ACTION_SCALE_WHEEL, EXPECTED_XML_SHA256, NO_LOAD, PEAK,
    STALL, WHEEL_VEL_LIMIT, XML_SOURCE, Mod4v3RLJumpEnv,
)
from moe_jump_model import MoEJumpActorCritic, StatefulMoEJumpActor, verify_c874_checkpoint

DT = .0025
SUBSTEPS = 8
COMMAND_DT = DT * SUBSTEPS
WALL_HEIGHT = .360
PLATFORM_LENGTH = 5.
HURDLE_THICKNESS = .040
NAV_WIDTH = 2.6
HOLD_TICKS = 46
CLOSURE_LIMIT = .010
PARENT_SHA = "9bad1458"
PARENT = OLD / "weights/model_rl_best.pt"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_save(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def model_from(path):
    path = Path(path)
    if path == PARENT and not sha(path).startswith(PARENT_SHA):
        raise ValueError("Jump parent no longer matches 9bad1458")
    return MoEJumpActorCritic.load_from_checkpoint(path, "cpu").eval()


def make_scene(path, visual):
    """Terrain only. The robot, contacts, solver settings and dynamics come from the pinned scene."""
    if sha(XML_SOURCE) != EXPECTED_XML_SHA256:
        raise ValueError("Pinned MJCF digest changed")
    tree = ET.parse(XML_SOURCE)
    root = tree.getroot()
    root.find("compiler").set("meshdir", str(XML_SOURCE.parent / "assets"))
    world = root.find("worldbody")
    ground = world.find("geom[@name='ground']")
    ground.set("size", "22 22 .1")
    for index, length, height, color in (
        (0, PLATFORM_LENGTH, WALL_HEIGHT, ".28 .49 .65 1"),
        (1, HURDLE_THICKNESS, WALL_HEIGHT, ".82 .43 .19 1"),
        (2, HURDLE_THICKNESS, .340, ".74 .56 .28 1"),
    ):
        # The inactive colliders are below z=0. The mover translates the box only.
        collider = ET.SubElement(world, "body", name=f"jump_obstacle_{index}", mocap="true", pos=f"4 0 {-2-index}")
        ET.SubElement(collider, "geom", name=f"dyn_hurdle_{index}", type="box",
                      size=f"{length/2} {NAV_WIDTH/2} {height/2}",
                      contype="1", conaffinity="2", friction=".9 .005 .0001", rgba=color, group="0")
    if visual:
        settings = root.find("visual/global")
        settings.set("offwidth", "1280")
        settings.set("offheight", "720")
        ET.SubElement(root.find("asset"), "texture", name="jump_grid", type="2d",
                      builtin="checker", rgb1=".18 .22 .26", rgb2=".24 .29 .33", width="128", height="128")
        ET.SubElement(root.find("asset"), "material", name="jump_ground", texture="jump_grid",
                      texrepeat="24 24", texuniform="true", reflectance=".04")
        ground.set("material", "jump_ground")
    else:
        # Mesh geoms with both collision masks zero are purely graphical.
        for body in world.iter("body"):
            for geom in list(body.findall("geom")):
                if geom.get("class") == "visual":
                    body.remove(geom)
        referenced = {geom.get("mesh") for geom in world.iter("geom")}
        asset = root.find("asset")
        for mesh in list(asset.findall("mesh")):
            if mesh.get("name") not in referenced:
                asset.remove(mesh)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(path, encoding="utf-8", xml_declaration=True)
    return path


def geom_groups(model, base_id):
    names = [model.geom(i).name for i in range(model.ngeom)]
    tires = [names.index(name) for name in ("left_tire", "right_tire")]
    guides = [i for i, name in enumerate(names) if (name or "").startswith("guide_wheel_")]
    chassis = [i for i in range(model.ngeom) if model.geom_bodyid[i] == base_id
               and (model.geom_contype[i] or model.geom_conaffinity[i])]
    if len(guides) != 8 or len(chassis) != 8:
        raise ValueError((tires, guides, chassis))
    cylinder, box = int(mujoco.mjtGeom.mjGEOM_CYLINDER), int(mujoco.mjtGeom.mjGEOM_BOX)
    assert np.all(model.geom_type[tires + guides] == cylinder)
    assert np.all(model.geom_type[chassis] == box)
    return tires, guides, chassis


def geom_extent(size, matrix, cylinder_count):
    """Projection of a finite cylinder or oriented box onto a world axis."""
    cyl = matrix[..., :cylinder_count, 2]
    r, length = size[:cylinder_count, :2].T
    radial = np.sqrt(np.maximum(0., 1. - cyl ** 2))
    cyl_extent = r * radial + length * np.abs(cyl)
    box_extent = (np.abs(matrix[..., cylinder_count:, :]) * size[cylinder_count:]).sum(axis=-1)
    return np.concatenate((cyl_extent, box_extent), axis=-1)


@dataclass
class Frame:
    time: float
    x: float
    z: float
    vx: float
    vz: float
    pitch: float
    roll: float
    lowest: float
    tire_low: float
    guide_low: float
    chassis_low: float
    min_x: float
    max_x: float
    lagging_wheel_x: float
    total_force: float
    wheel_up_force: tuple[float, float]
    wheel_top_force: tuple[float, float]
    face_force: float
    obstacle_force: float
    scrape_force: float
    closure: float
    mimic: float


class JumpPlant(Mod4v3RLJumpEnv):
    """Uses the previous motor/DR/observation implementation with a direct operator bit."""

    def __init__(self, seed=0, visual=False, scene_dir=HERE / "scenes"):
        self.key = False
        suffix = "visual" if visual else "physics"
        scene_path = Path(scene_dir) / f"jump360_solid_{suffix}.xml"
        if not scene_path.exists():
            make_scene(scene_path, visual)
        super().__init__(seed=seed, xml_path=scene_path)
        self.groups = geom_groups(self.m, self.base_id)
        self.measured_gids = np.array(sum((list(group) for group in self.groups), []))
        self.sizes = self.m.geom_size[self.measured_gids].copy()
        self.pairs_np = np.array(self.pairs)
        self.mimics_np = np.array(self.mimics)
        self.colliders = set(self.hurdle_gids)
        self.tire_map = {gid: i for i, gid in enumerate(self.tire_gids)}
        self.scrape_gids = set(self.groups[1] + self.groups[2])
        self.wall_edge = math.inf
        self.wall_scene = "flat"

    def _is_jump_bit_on(self, now):
        return self.key

    def setup(self, height, dr=0., init_pose=(0., 0., 0.)):
        self.key = False
        super().reset(dr_scale=dr, h_nom=height, jump_times=(), init_pose=init_pose)
        self.height_cmd = height
        self.wall("flat")
        self.tilt_fault = False

    def configure_hurdles(self, hurdles):
        # Preserve compiled collision sizes and broadphase bounds.
        if hurdles:
            raise ValueError("Use wall() to position an obstacle of known size.")
        self.active_hurdles = []
        self.cleared_hurdles.clear()
        for index, gid in enumerate(self.hurdle_gids):
            self.d.mocap_pos[self.m.body_mocapid[self.m.geom_bodyid[gid]]] = [4., 0., -2.-index]

    def wall(self, kind, edge=0.):
        self.configure_hurdles([])
        self.wall_scene = kind
        self.wall_edge = edge if kind != "flat" else math.inf
        if kind != "flat":
            index = ("platform", "hurdle", "hurdle340").index(kind)
            gid = self.hurdle_gids[index]
            half = self.m.geom_size[gid]
            self.d.mocap_pos[self.m.body_mocapid[self.m.geom_bodyid[gid]]] = [edge + half[0], 0., half[2]]
        mujoco.mj_forward(self.m, self.d)

    def command(self, vx, height, key, wz=0.):
        self.cmd_vx, self.height_cmd, self.key, self.cmd_wz = vx, height, bool(key), wz
        return self._compute_obs()

    def _compute_motor_torque(self, action):
        leg_q = self.d.qpos[self.qadr_all[self.leg_ids]].astype(np.float32)
        leg_v = self.d.qvel[self.dadr_all[self.leg_ids]].astype(np.float32)
        wheel_v = self.d.qvel[self.dadr_all[self.wheel_ids]].astype(np.float32)
        goal = self.default_leg_q + ACTION_SCALE_LEG * action[:4]
        # Keep the pinned target unwrap. The MJCF now supplies the travel limits.
        for front, rear in ((0, 2), (1, 3)):
            delta = float(goal[front] - goal[rear])
            delta += round((float(leg_q[front] - leg_q[rear]) - delta) / math.tau) * math.tau
            goal[rear] += round(float(leg_q[rear] - goal[rear]) / math.tau) * math.tau
            goal[front] = goal[rear] + delta
        wheel_goal = np.clip(ACTION_SCALE_WHEEL * action[4:], -WHEEL_VEL_LIMIT, WHEEL_VEL_LIMIT)
        leg_tau = (60. * self.kp_scale) * (goal - leg_q) - (2. * self.kd_scale) * leg_v
        wheel_tau = (.6 * self.kv_scale) * (wheel_goal - wheel_v)
        velocity = np.concatenate((leg_v, wheel_v))
        upper = np.clip(STALL * (1. - velocity / NO_LOAD), 0., PEAK) * self.effort_scale
        lower = np.clip(-STALL * (1. + velocity / NO_LOAD), -PEAK, 0.) * self.effort_scale
        return np.clip(np.concatenate((leg_tau, wheel_tau)), lower, upper)

    def advance(self, action, callback=None):
        action = np.asarray(action, dtype=np.float32).reshape(6).clip(-6., 6.)
        env_action = action[self.ppo_to_env_np]
        for i in range(SUBSTEPS):
            self.action_delay_fifo.append(env_action)
            torque = self._compute_motor_torque(self.action_delay_fifo[0])
            if i % 4 == 0:
                self.d.ctrl[self.act_ids[:4]] = torque[:4]
            self.d.ctrl[self.act_ids[4:]] = torque[4:]
            mujoco.mj_step(self.m, self.d)
            if callback is not None:
                callback(self.frame())
            if self.cos_tilt < .5 or self.d.qpos[2] < .12:
                self.tilt_fault = True
        self.a_prev = action.copy()

    def frame(self):
        model, data = self.m, self.d
        rotation = data.xmat[self.base_id].reshape(3, 3)
        gmat = data.geom_xmat[self.measured_gids].reshape(-1, 3, 3)
        centers = data.geom_xpos[self.measured_gids]
        bottom = centers[:, 2] - geom_extent(self.sizes, gmat[:, 2], 10)
        hx = geom_extent(self.sizes, gmat[:, 0], 10)
        total = scrape = face = obstacle = 0.
        wheel = [0., 0.]
        top = [0., 0.]
        for ci in range(data.ncon):
            c = data.contact[ci]
            g1, g2 = int(c.geom1), int(c.geom2)
            b1, b2 = model.geom_bodyid[[g1, g2]]
            fixed1, fixed2 = b1 == 0 or g1 in self.colliders, b2 == 0 or g2 in self.colliders
            if fixed1 == fixed2:
                continue
            fixed, robot = (g1, g2) if fixed1 else (g2, g1)
            mujoco.mj_contactForce(model, data, ci, self._local_force)
            norm = float(np.linalg.norm(self._local_force[:3]))
            total += norm
            normal = np.asarray(c.frame)[:3]
            if fixed in self.colliders:
                obstacle += norm
                if abs(normal[0]) > .35 and c.pos[2] < WALL_HEIGHT - .002:
                    face += norm
            if robot in self.scrape_gids:
                scrape += norm
            if robot in self.tire_map:
                # Include only upward surface support in the programmed landing check.
                tire = self.tire_map[robot]
                vertical = abs(float(self._local_force[0] * normal[2]))
                wheel[tire] += vertical
                if (fixed == self.hurdle_gids[0] and abs(normal[2]) > .65
                        and c.pos[2] >= WALL_HEIGHT - .010 and c.pos[0] >= self.wall_edge - .005):
                    top[tire] += vertical
        pair = self.pairs_np
        mimic = self.mimics_np
        return Frame(
            float(data.time), float(data.qpos[0]), float(data.qpos[2]), self.body_vx, float(data.qvel[2]),
            math.degrees(math.asin(float(np.clip(-rotation[2, 0], -1., 1.)))),
            math.degrees(math.atan2(float(rotation[2, 1]), float(rotation[2, 2]))),
            float(bottom.min()), float(bottom[:2].min()), float(bottom[2:10].min()), float(bottom[10:].min()),
            float((centers[:, 0] - hx).min()), float((centers[:, 0] + hx).max()),
            float(centers[:2, 0].min()), total, tuple(wheel), tuple(top), face, obstacle, scrape,
            float(np.linalg.norm(data.site_xpos[pair[:, 0]] - data.site_xpos[pair[:, 1]], axis=1).max()),
            float(np.abs(data.qpos[mimic[:, 0]] - data.qpos[mimic[:, 1]]).max()),
        )


def cruise_actor(checkpoint):
    state = (torch.load(checkpoint, map_location="cpu", weights_only=False)["actor_state_dict"]
             if checkpoint else verify_c874_checkpoint()["actor_state_dict"])
    from moe_jump_model import build_c874_mlp
    actor = build_c874_mlp()
    actor.load_state_dict({key[4:]: value for key, value in state.items() if key.startswith("mlp.")})
    return actor.eval().requires_grad_(False)
