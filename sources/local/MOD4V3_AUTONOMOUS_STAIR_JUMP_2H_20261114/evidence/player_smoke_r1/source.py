"""Reuse the existing WASD/Space player with the autonomous observation schema."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import time
import tkinter as tk

import mujoco
import numpy as np
import torch

T = Path(__file__).resolve().parent
R = T.parents[2]
sys.path.insert(0, str(R / 'sources/local/MOD4V3_FORWARD_JUMP_MANUAL_20261114'))
import manual_jump as old
from autonomous_stair.objective import SCHEMA, Outcome, scan_target, task_slots


class AutonomousSimulation(old.JumpSimulation):
    def __init__(self, checkpoint, *, visible=False, row=0):
        self.autonomous_ready = False
        checkpoint = Path(checkpoint).resolve()
        data = torch.load(checkpoint, map_location='cpu', weights_only=False)
        assert data.get('observation_schema') == SCHEMA, 'This player requires the new autonomous schema'
        old.JUMP, old.JUMP_SHA = checkpoint, hashlib.sha256(checkpoint.read_bytes()).hexdigest()
        old.PHASES = ['READY', 'AUTO JUMP', 'AUTO JUMP', 'AUTO JUMP', 'AUTO JUMP']
        super().__init__(visible=visible, terrain=True, terrain_row=row, terrain_family=0)
        self.outcome = Outcome(1, 'cpu')
        self.edge_anchor = torch.zeros(1, 2)
        self.target_direction = torch.tensor([[1., 0.]])
        self.observed_height, self.tread = torch.zeros(1), torch.full((1,), 1.5)
        self.autonomous_ready = True
        self.reset_standing()

    def reset_standing(self):
        super().reset_standing()
        if self.autonomous_ready:
            self.outcome.reset(torch.tensor([0]))

    def _scan(self):
        model, data = self.env.m, self.env.d
        rotation = data.xmat[self.env.base_id].reshape(3, 3)
        yaw = math.atan2(rotation[1, 0], rotation[0, 0])
        direction = np.array([math.cos(yaw), math.sin(yaw)])
        hits = []
        geomgroup = np.zeros(6, dtype=np.uint8)
        geomgroup[5] = 1
        for distance in np.arange(0., 2.401, .05):
            start = np.r_[data.qpos[:2] + distance * direction, data.qpos[2] + 5.]
            hit_id = np.array([-1], dtype=np.int32)
            depth = mujoco.mj_ray(model, data, start, np.array([0., 0., -1.]),
                                  geomgroup, True, -1, hit_id)
            hits.append(start + np.array([0., 0., -depth]) if depth >= 0. else np.full(3, np.nan))
        root = torch.tensor(data.qpos[:3].copy(), dtype=torch.float32)[None]
        distance, height, tread = scan_target(torch.tensor(np.array(hits), dtype=torch.float32)[None],
                                              root, torch.tensor([yaw]))
        return root, torch.tensor(direction, dtype=torch.float32)[None], distance, height, tread

    def request_jump(self):
        accepted = super().request_jump()
        if accepted:
            self.outcome.reset(torch.tensor([0]))
            root, direction, distance, height, tread = self._scan()
            self.edge_anchor = root[:, :2] + direction * distance[:, None]
            self.target_direction = direction
            self.observed_height, self.tread = height, tread
        return accepted

    def _observation(self):
        raw = super()._observation()
        if self.autonomous_ready and self.phase:
            root = torch.tensor(self.env.d.qpos[:2].copy(), dtype=torch.float32)[None]
            distance = ((self.edge_anchor - root) * self.target_direction).sum(-1)
            raw[:, 28:35] = task_slots(torch.ones(1), torch.tensor([self.no_support]), distance,
                self.observed_height, self.tread, torch.tensor([float(self.env.d.qvel[2])]))
        return raw

    def _finish_jump(self, reason):
        self.last_jump = dict(request=self.requests, reason=reason, accepted=bool(self.outcome.success[0]),
            air_s=float(self.outcome.max_air[0]), rim_peak_m=float(self.outcome.rim_peak[0]),
            air_pitch_deg=math.degrees(float(self.outcome.air_pitch[0])),
            air_roll_deg=math.degrees(float(self.outcome.air_roll[0])),
            crouched=False, extended=False, retracted=False, landed=bool(self.outcome.landed[0]),
            stable_hold_s=float(self.outcome.max_stable[0]),
            duration_s=float(self.env.d.time) - self.jump_start, observation_schema=SCHEMA,
            pose_sequence_checked=False)
        self.completed_jumps.append(self.last_jump.copy())
        self.events.append(dict(event='end', **self.last_jump))
        self.phase = 0

    def _advance_jump(self):
        if not self.phase:
            return
        model, data = self.env.m, self.env.d
        force = torch.zeros(1, 2, 3)
        total = 0.
        contact_force = np.zeros(6)
        for i in range(data.ncon):
            c = data.contact[i]
            bodies = [int(model.geom_bodyid[g]) for g in (c.geom1, c.geom2)]
            if 0 not in bodies:
                continue
            mujoco.mj_contactForce(model, data, i, contact_force)
            world = c.frame.reshape(3, 3).T @ contact_force[:3]
            total += float(np.linalg.norm(world))
            for side, body in enumerate(self.wheel_bodies):
                if body in bodies:
                    force[0, side, 2] += abs(float(world[2]))
        tile = self.terrain.tile()['name']
        top = model.geom('map_step_' + tile + '_1').id
        upper = model.geom('map_step_' + tile + '_2').id
        edge = float(model.geom_pos[top, 0] - model.geom_size[top, 0])
        next_edge = float(model.geom_pos[upper, 0] - model.geom_size[upper, 0])
        height = float(model.geom_pos[top, 2] + model.geom_size[top, 2])
        all_force = torch.zeros(1, 1, 3)
        all_force[0, 0, 2] = total
        roll, pitch = self._angles()
        self.outcome.update(requested=torch.ones(1, dtype=torch.bool),
            wheel=torch.tensor(data.xpos[self.wheel_bodies].copy(), dtype=torch.float32)[None],
            forces=force, all_force=all_force, edge=torch.tensor([edge]), next_edge=torch.tensor([next_edge]),
            ground=torch.zeros(1), height=torch.tensor([height]), vz=torch.tensor([float(data.qvel[2])]),
            vx=torch.tensor([float(self.env.vx)]), command_vx=torch.tensor([self.jump_speed]),
            roll=torch.tensor([roll]), pitch=torch.tensor([pitch]),
            angular=torch.tensor(data.qvel[3:6].copy(), dtype=torch.float32)[None],
            terminated=torch.tensor([self.forbidden or self.closure > .01 or self.mimic > .01]))
        self.air_s, self.rim_peak = float(self.outcome.max_air[0]), float(self.outcome.rim_peak[0])
        self.stable_hold = float(self.outcome.stable[0])
        self.air_pitch, self.air_roll = float(self.outcome.air_pitch[0]), float(self.outcome.air_roll[0])
        self.landed = bool(self.outcome.landed[0])
        if bool(self.outcome.success[0]):
            self._finish_jump('upper_tread_stable_and_returned_to_drive')
        elif float(data.time) - self.jump_start >= 8.:
            self._finish_jump('autonomous_attempt_timeout')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--checkpoint', type=Path, required=True)
    p.add_argument('--row', type=int, choices=[0, 3], default=0)
    p.add_argument('--smoke', action='store_true')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    sim = AutonomousSimulation(a.checkpoint, visible=not a.smoke, row=a.row)
    if a.smoke:
        for i in range(85):
            sim.step({'w'} if i >= 20 else set())
        start_vx = float(sim.env.vx)
        assert start_vx > .1, 'The Space test must start while moving forward'
        assert sim.request_jump()
        assert not sim.request_jump()
        observed = sim._observation().clone()
        assert observed.shape == (1, 35) and bool(torch.isfinite(observed).all())
        assert float(observed[0, 29]) == 1. and abs(float(observed[0, 32]) - (.165 if a.row == 0 else .22)) < .015
        for _ in range(405):
            sim.step({'w'})
        assert sim.requests == 1, 'A single Space press must not repeat requests'
        report = dict(epoch=time.time(), schema=SCHEMA, checkpoint=str(a.checkpoint.resolve()),
            checkpoint_sha256=old.JUMP_SHA, moving_request_vx=start_vx,
            single_space_accepted=True, duplicate_request_rejected=True,
            request_observation=observed.tolist(), requests=sim.requests,
            map_tiles=1, last_jump=sim.last_jump, events=sim.events,
            task_success_claimed=bool(sim.last_jump and sim.last_jump['accepted']))
        old.save_json(a.output / 'RESULT.json', report)
        print(json.dumps(report, indent=2))
        sim.close()
        return
    root = tk.Tk()
    sim.paused = True
    old.JumpControl(root, sim, a.output)
    old.save_json(a.output / 'READY.json', dict(epoch=time.time(), checkpoint=str(a.checkpoint.resolve()),
        observation_schema=SCHEMA, map_tiles=1, single_space_request=True, manual=True))
    root.mainloop()


if __name__ == '__main__':
    main()
