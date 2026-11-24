"""Full-width solid platforms with native MuJoCo course measurements."""
import math
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
import xml.etree.ElementTree as ET

import numpy as np

from jump360_scene import JumpPlant, make_scene
from jump380_r5_scene import HEIGHTS, KINDS, LENGTHS, PLATFORMS, Jump380Plant as PlatformPlant
from jump380_r6_policy import RUN

HALF_WIDTH = 11.
Y_LIMIT = .70
YAW_LIMIT_DEG = 25.
APPROACH_Y_LIMIT = .15
APPROACH_YAW_LIMIT_DEG = 8.


def prepare_scene(visual):
    folder = RUN / "scenes"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / ("jump360_solid_visual.xml" if visual else "jump360_solid_physics.xml")
    if path.is_file():
        return path
    with NamedTemporaryFile(dir=folder, suffix=".partial", delete=False) as stream:
        temporary = Path(stream.name)
    try:
        tree = ET.parse(make_scene(temporary, visual))
        world = tree.getroot().find("worldbody")
        colors = (".30 .56 .73 1", ".35 .60 .48 1", ".82 .43 .19 1")
        for index, (height, length, color) in enumerate(zip(HEIGHTS[1:], LENGTHS[1:], colors)):
            geom = world.find(f"body/geom[@name='dyn_hurdle_{index}']")
            geom.set("size", f"{length/2} {HALF_WIDTH} {height/2}")
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


def yaw_degrees(qpos):
    w, x, y, z = qpos[3:7]
    return math.degrees(math.atan2(2. * (w*z + x*y), 1. - 2. * (y*y + z*z)))


class Jump380Plant(PlatformPlant):
    def __init__(self, seed=0, visual=False):
        JumpPlant.__init__(self, seed=seed, visual=visual, scene_dir=prepare_scene(visual).parent)
        self.wall_height, self.surface_gid = 0., -1
        self.approach_face = self.approach_obstacle = 0.
        sizes = self.m.geom_size[self.hurdle_gids]
        expected = np.column_stack((np.asarray(LENGTHS[1:])/2., [HALF_WIDTH]*3, np.asarray(HEIGHTS[1:])/2.))
        if not np.array_equal(sizes, expected):
            raise ValueError("R6 solid obstacle dimensions are inconsistent")
        self.measure_course = False

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        self.key_seen = False
        self.max_abs_y = self.approach_max_abs_y = abs(float(self.d.qpos[1]))
        self.max_abs_yaw = self.approach_max_abs_yaw = abs(yaw_degrees(self.d.qpos))

    def advance(self, action, callback=None):
        if not self.measure_course:
            super().advance(action, callback)
            return
        self.key_seen |= self.key
        near_face = self.wall_edge - float(self.d.qpos[0]) < .65

        def measure(frame):
            lateral, yaw = abs(float(self.d.qpos[1])), abs(yaw_degrees(self.d.qpos))
            self.max_abs_y = max(self.max_abs_y, lateral)
            self.max_abs_yaw = max(self.max_abs_yaw, yaw)
            if not self.key_seen:
                self.approach_max_abs_y = max(self.approach_max_abs_y, lateral)
                self.approach_max_abs_yaw = max(self.approach_max_abs_yaw, yaw)
            if callback is not None:
                callback(frame)
            elif near_face:
                self.approach_face = max(self.approach_face, frame.face_force)
                self.approach_obstacle = max(self.approach_obstacle, frame.obstacle_force)

        super().advance(action, measure)
