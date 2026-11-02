"""Proposed ToF simulator facade, NOT installed hardware/BSP.
Only this measurement facade may inspect MuJoCo pose/geometry. Output is range,
clock/quality and explicit mount metadata; no root/contact/terrain id is exposed.
"""
from dataclasses import dataclass
from collections import deque
import math
import numpy as np
import mujoco


@dataclass(frozen=True)
class RangePacket:
    sampled_s: float
    arrival_s: float
    sequence: int
    range_m: float | None
    valid: bool
    origin_B: tuple
    direction_B: tuple
    range_error_bound_m: float
    synthetic_fixture: bool = True
    hardware_binding: bool = False


class ProposedToF:
    def __init__(self, model, origin_B=(.30, 0., .10), angle_down_deg=40.,
                 max_range_m=1.5, noise_half_m=.005, delay_samples=1, seed=4201):
        self.model = model
        self.scratch = mujoco.MjData(model)
        self.body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, 'chassis')
        assert self.body_id >= 0
        self.origin_B = np.asarray(origin_B, float)
        angle = math.radians(angle_down_deg)
        self.direction_B = np.array([math.cos(angle), 0., -math.sin(angle)])
        self.max_range = float(max_range_m)
        self.noise = float(noise_half_m)
        self.delay = int(delay_samples)
        assert self.delay >= 0 and self.noise >= 0
        self.rng = np.random.default_rng(seed)
        self.history = deque(maxlen=self.delay + 1)
        self.sequence = 0
        self.groups = np.array([1, 0, 0, 0, 0, 0], dtype=np.uint8)

    def sample(self, data, now_s):
        # A scratch pose avoids silently using the last .5ms-old dynamics cache.
        self.scratch.qpos[:] = data.qpos
        mujoco.mj_kinematics(self.model, self.scratch)
        rotation = self.scratch.xmat[self.body_id].reshape(3, 3)
        point = self.scratch.xpos[self.body_id] + rotation @ self.origin_B
        direction = rotation @ self.direction_B
        geom_id = np.array([-1], dtype=np.int32)
        distance = float(mujoco.mj_ray(self.model, self.scratch, point, direction,
                                     self.groups, 1, self.body_id, geom_id))
        robot_group = np.array([0, 0, 0, 1, 0, 0], dtype=np.uint8)
        robot_id = np.array([-1], dtype=np.int32)
        self_distance = float(mujoco.mj_ray(self.model, self.scratch, point, direction,
                                          robot_group, 1, -1, robot_id))
        occluded = self_distance >= 0 and (distance < 0 or self_distance < distance)
        value = distance + self.rng.uniform(-self.noise, self.noise) if not occluded and 0 <= distance <= self.max_range else None
        self.sequence += 1
        packet = RangePacket(float(now_s), float(now_s), self.sequence, value,
                             value is not None, tuple(self.origin_B), tuple(self.direction_B), self.noise)
        self.history.append(packet)
        if len(self.history) <= self.delay:
            return None
        old = self.history[-1 - self.delay]
        return RangePacket(old.sampled_s, float(now_s), old.sequence, old.range_m, old.valid,
                           old.origin_B, old.direction_B, old.range_error_bound_m)
