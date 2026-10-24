"""Passive speed/timebase measurements; never advances physics or changes commands."""
from collections import deque
import math


class WallClockSpeed:
    def __init__(self, window_seconds=1.0):
        self.window_seconds = float(window_seconds)
        self.reset()

    def reset(self):
        self.samples = deque()
        self.previous = None
        self.distance = 0.0

    def observe(self, wall_time, sim_time, position, running, step_ms=0.0, sync_ms=0.0):
        if not running:
            self.reset()
            return
        point = (float(wall_time), float(sim_time), float(position[0]), float(position[1]))
        if not all(math.isfinite(x) for x in point):
            self.reset()
            return
        if self.previous is not None:
            old = self.previous
            if point[0] <= old[0] or point[1] < old[1]:
                self.reset()
            else:
                self.distance += math.hypot(point[2] - old[2], point[3] - old[3])
        self.previous = point
        self.samples.append((point[0], point[1], self.distance, float(step_ms), float(sync_ms)))
        while len(self.samples) > 2 and point[0] - self.samples[1][0] >= self.window_seconds:
            self.samples.popleft()

    def metrics(self):
        result = dict(realtime_factor=None, ground_speed_wall_mps=None,
                      timing_window_wall_s=0.0, timing_window_sim_s=0.0,
                      timing_active_only=True, step_control_wall_ms=None,
                      viewer_sync_wall_ms=None)
        if len(self.samples) < 2:
            return result
        first, last = self.samples[0], self.samples[-1]
        wall, sim = last[0] - first[0], last[1] - first[1]
        result.update(timing_window_wall_s=wall, timing_window_sim_s=sim)
        if wall < 0.2:
            return result
        count = len(self.samples)
        result.update(realtime_factor=sim / wall,
                      ground_speed_wall_mps=(last[2] - first[2]) / wall,
                      step_control_wall_ms=sum(x[3] for x in self.samples) / count,
                      viewer_sync_wall_ms=sum(x[4] for x in self.samples) / count)
        return result
