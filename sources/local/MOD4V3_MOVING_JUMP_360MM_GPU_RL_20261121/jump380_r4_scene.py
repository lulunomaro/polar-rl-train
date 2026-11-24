"""R4 solid obstacles and independent native-MuJoCo contact measurements."""
from dataclasses import dataclass
import math
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
import xml.etree.ElementTree as ET

import numpy as np

from jump360_scene import Frame, HERE, HURDLE_THICKNESS, JumpPlant, geom_extent, make_scene, mujoco

RUN = HERE / "evidence/jump380_r4"
PARENT = HERE / "evidence/jump360_r3/ppo/model_004m.pt"
PARENT_SHA = "3580b7587e5feeaf417ae43739dce128187771ee3b2599d8d946eeadc6c07bc7"
KINDS = ("flat", "platform_380", "platform_360", "hurdle_380")
HEIGHTS = (0., .380, .360, .380)
LENGTHS = (0., 5., 5., HURDLE_THICKNESS)
PLATFORMS = KINDS[1:3]


def prepare_scene(visual):
    folder = RUN / "scenes"
    folder.mkdir(parents=True, exist_ok=True)
    suffix = "visual" if visual else "physics"
    # JumpPlant accepts a scene directory and looks for this filename in it.
    path = folder / f"jump360_solid_{suffix}.xml"
    if path.exists():
        return path
    with NamedTemporaryFile(dir=folder, suffix=".partial", delete=False) as stream:
        temporary = Path(stream.name)
    try:
        tree = ET.parse(make_scene(temporary, visual))
        world = tree.getroot().find("worldbody")
        for index, (height, length, color) in enumerate(zip(
                HEIGHTS[1:], LENGTHS[1:], (".30 .56 .73 1", ".35 .60 .48 1", ".82 .43 .19 1"))):
            geom = world.find(f"body/geom[@name='dyn_hurdle_{index}']")
            size = geom.get("size").split()
            geom.set("size", f"{length / 2} {size[1]} {height / 2}")
            geom.set("rgba", color)
        tree.write(temporary, encoding="utf-8", xml_declaration=True)
        try:
            os.replace(temporary, path)
        except PermissionError:
            if not path.is_file():
                raise
    finally:
        temporary.unlink(missing_ok=True)
    return path


@dataclass
class R4Frame(Frame):
    leading_tire_x: float
    trailing_tire_x: float
    low_front_360: float | None
    low_front_380: float | None


class Jump380Plant(JumpPlant):
    def __init__(self, seed=0, visual=False):
        super().__init__(seed=seed, visual=visual, scene_dir=prepare_scene(visual).parent)
        self.wall_height = 0.
        self.surface_gid = -1
        dimensions = self.m.geom_size[self.hurdle_gids]
        if not np.array_equal(2. * dimensions[:, (0, 2)], np.column_stack((LENGTHS[1:], HEIGHTS[1:]))):
            raise ValueError("R4 obstacle dimensions do not match the declared heights and lengths")
        self.approach_face = 0.
        self.approach_obstacle = 0.

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        self.approach_face = self.approach_obstacle = 0.

    def wall(self, kind, edge=0.):
        index = KINDS.index(kind)
        self.configure_hurdles([])
        self.wall_scene = kind
        self.wall_edge = edge if index else math.inf
        self.wall_height = HEIGHTS[index]
        self.surface_gid = self.hurdle_gids[index - 1] if index else -1
        if index:
            geom = self.surface_gid
            mocap = self.m.body_mocapid[self.m.geom_bodyid[geom]]
            half = self.m.geom_size[geom]
            self.d.mocap_pos[mocap] = [edge + half[0], 0., half[2]]
        mujoco.mj_forward(self.m, self.d)

    def advance(self, action, callback=None):
        if callback is None and self.wall_edge - float(self.d.qpos[0]) < .65:
            def measure_approach(frame):
                self.approach_face = max(self.approach_face, frame.face_force)
                self.approach_obstacle = max(self.approach_obstacle, frame.obstacle_force)
            callback = measure_approach
        super().advance(action, callback)

    def frame(self):
        data, model = self.d, self.m
        rotation = data.xmat[self.base_id].reshape(3, 3)
        geometry = data.geom_xmat[self.measured_gids].reshape(-1, 3, 3)
        centers = data.geom_xpos[self.measured_gids]
        bottom = centers[:, 2] - geom_extent(self.sizes, geometry[:, 2], 10)
        half_x = geom_extent(self.sizes, geometry[:, 0], 10)
        front, rear = centers[:, 0] + half_x, centers[:, 0] - half_x
        total = face = obstacle = scrape = 0.
        wheel, top = [0., 0.], [0., 0.]
        for i in range(data.ncon):
            contact = data.contact[i]
            a, b = int(contact.geom1), int(contact.geom2)
            fixed_a = a == self.ground_gid or a in self.colliders
            fixed_b = b == self.ground_gid or b in self.colliders
            if fixed_a == fixed_b:
                continue
            surface, robot = (a, b) if fixed_a else (b, a)
            mujoco.mj_contactForce(model, data, i, self._local_force)
            force = float(np.linalg.norm(self._local_force[:3]))
            normal = contact.frame[:3]
            total += force
            if surface == self.surface_gid:
                obstacle += force
                if abs(normal[0]) > .35 and contact.pos[2] < self.wall_height - .004:
                    face += force
            if robot in self.scrape_gids:
                scrape += force
            if robot in self.tire_map:
                tire = self.tire_map[robot]
                load = abs(float(self._local_force[0] * normal[2]))
                wheel[tire] += load
                if (surface == self.surface_gid and self.wall_scene in PLATFORMS and abs(normal[2]) > .65
                        and contact.pos[2] >= self.wall_height - .012):
                    top[tire] += load
        pair, mimic = self.pairs_np, self.mimics_np
        below_360, below_380 = bottom <= .360, bottom <= .380
        return R4Frame(
            float(data.time), float(data.qpos[0]), float(data.qpos[2]), self.body_vx, float(data.qvel[2]),
            math.degrees(math.asin(float(np.clip(-rotation[2, 0], -1., 1.)))),
            math.degrees(math.atan2(float(rotation[2, 1]), float(rotation[2, 2]))),
            float(bottom.min()), float(bottom[:2].min()), float(bottom[2:10].min()), float(bottom[10:].min()),
            float(rear.min()), float(front.max()), float(centers[:2, 0].min()), total, tuple(wheel), tuple(top),
            face, obstacle, scrape,
            float(np.linalg.norm(data.site_xpos[pair[:, 0]] - data.site_xpos[pair[:, 1]], axis=1).max()),
            float(np.abs(data.qpos[mimic[:, 0]] - data.qpos[mimic[:, 1]]).max()),
            float(front[:2].max()), float(rear[:2].min()),
            float(front[below_360].max()) if below_360.any() else None,
            float(front[below_380].max()) if below_380.any() else None,
        )
