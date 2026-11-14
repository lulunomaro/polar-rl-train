"""Interactive MuJoCo driving and one-shot learned jumps in the existing player."""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET

import mujoco
import mujoco.viewer
import numpy as np
import torch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
TRAIN = REPO / "sources/local/MOD4V3_FORWARD_JUMP_REPAIR_2H_20261114"
DELIVERY = REPO / "deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112"
sys.path.insert(0, str(DELIVERY / "runtime/core"))
from args_for import args_for
from play_mod4v3 import _q_from_bank
from play_ppo_flatv1 import ActorMLP
from play_ppo_flatv1_control import ControlApp, Simulation

JUMP = TRAIN / "weights/train7200__model_085m.pt"
DRIVE = TRAIN / "weights/root_five_minute.pt"
JUMP_SHA = "c4d0328472e8642c497f113e37fb8940d92435cd8d96f547b8f1f4aa15cc1dfe"
DRIVE_SHA = "03884d680c0fcb4c5216f8aeaa42c319473ea1cbc7261df089f42c1136b07edd"
DT = .02
PHASES = ["READY", "CROUCH", "PUSH", "FLIGHT", "LAND"]


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class JumpSimulation(Simulation):
    def __init__(self, visible=False, terrain=False, terrain_row=3, terrain_family=0):
        for path, expected in ((JUMP, JUMP_SHA), (DRIVE, DRIVE_SHA)):
            assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, str(path)
        args = args_for(str(JUMP))
        args.xml = str(TRAIN / "native_package/mjcf/scene.xml")
        args.runtime = str(TRAIN / "native_package/runtime_config.json")
        args.semantics = str(TRAIN / "native_package/semantics.json")
        args.bank = str(TRAIN / "dependencies/reset_bank.json")
        args.height, args.vx, args.wz = .36, .6, 1.
        self.terrain = None
        if terrain:
            from map_terrain import SavedMap
            self.terrain = SavedMap(row=terrain_row, family=terrain_family)
            args.xml = str(self.terrain.build())
        super().__init__(args)
        if self.terrain:
            self.terrain.populate(self.env.m)
        self.jump_actor = self.actor
        self.drive_actor = ActorMLP().eval()
        checkpoint = torch.load(DRIVE, map_location="cpu", weights_only=False)
        missing, unexpected = self.drive_actor.load_state_dict(checkpoint["actor_state_dict"], strict=False)
        assert not missing and set(unexpected) <= {"distribution.std_param"}
        bank = json.loads(Path(args.bank).read_bytes())
        semantics = json.loads(Path(args.semantics).read_bytes())
        self.env.bank_q, self.env.bank_z = _q_from_bank(bank, semantics, self.env.spec.joint_names, .26)
        model = self.env.m
        self.pairs = [(model.site(e.get("site1")).id, model.site(e.get("site2")).id)
                      for e in ET.parse(args.xml).getroot().findall("equality/connect")]
        self.mimics = [(model.joint(s + "_" + drive).qposadr[0], model.joint(s + "_" + main).qposadr[0])
                       for s in ("left", "right")
                       for drive, main in (("rear1_drive_joint", "rear1_joint"), ("front1_drive_joint", "front1_joint"))]
        self.wheel_bodies = [model.body(s + "_wheel_link").id for s in ("left", "right")]
        self.requests = self.resets = 0
        self.completed_jumps, self.events = [], []
        self.reason, self.last_jump = "", None
        self.reset_standing()
        self.paused = False
        model.vis.headlight.ambient[:] = [.65, .65, .65]
        model.vis.headlight.diffuse[:] = [.8, .8, .8]
        model.vis.headlight.specular[:] = [.08, .08, .08]
        if visible:
            self.viewer = mujoco.viewer.launch_passive(model, self.env.d)
            self.viewer.cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
            self.viewer.cam.trackbodyid = self.env.base_id
            self.viewer.cam.distance = 1.7
            self.viewer.cam.azimuth, self.viewer.cam.elevation = 115., -18.
            self.viewer.opt.geomgroup[3] = self.viewer.opt.geomgroup[5] = 0

    def reset_standing(self):
        super().reset_standing()
        if self.terrain:
            x, y = self.terrain.start()
            ground = self.terrain.ground(self.env.m, self.env.d, x, y)
            self.env.d.qpos[:3] = [x, y, ground+self.env.bank_z]
            mujoco.mj_forward(self.env.m, self.env.d)
        self.env.d.time = 0.
        self.phase, self.phase_time = 0, 0.
        self.closure = self.mimic = 0.
        self.resets = getattr(self, "resets", 0) + 1
        self.support_history = np.ones((25, 2), dtype=bool)
        self.support_slot = 0
        self._clear_jump()
        self._contacts()
        self.z = self.local_height()

    def local_height(self):
        data = self.env.d
        ground = self.terrain.ground(self.env.m, data, *data.qpos[:2]) if self.terrain else 0.
        return float(self.env.z) - ground

    def _clear_jump(self):
        self.crouched = self.extended = self.retracted = self.landed = False
        self.air_count = self.air_s = self.stable_hold = 0.
        self.rim_peak = self.air_pitch = self.air_roll = 0.
        self.jump_start = float(self.env.d.time)

    def _angles(self):
        r = self.env.d.xmat[self.env.base_id].reshape(3, 3)
        return abs(math.atan2(r[2, 1], r[2, 2])), abs(math.asin(np.clip(-r[2, 0], -1., 1.)))

    def _contacts(self):
        model, data = self.env.m, self.env.d
        self.support, total, forbidden = np.zeros(2, dtype=bool), 0., False
        force = np.zeros(6)
        for i in range(data.ncon):
            contact = data.contact[i]
            bodies = [int(model.geom_bodyid[g]) for g in (contact.geom1, contact.geom2)]
            if 0 not in bodies:
                continue
            robot_body = bodies[1] if bodies[0] == 0 else bodies[0]
            mujoco.mj_contactForce(model, data, i, force)
            normal = abs(float(force[0]))
            total += float(np.linalg.norm(force[:3]))
            if robot_body in self.wheel_bodies:
                self.support[self.wheel_bodies.index(robot_body)] |= normal > 5.
            elif normal > 1.:
                forbidden = True
        self.no_support, self.forbidden = total < 1., forbidden
        wheels = data.xpos[self.wheel_bodies]
        ground = [self.terrain.ground(model, data, *wheel[:2]) if self.terrain else 0. for wheel in wheels]
        self.rim = float((wheels[:, 2]-ground-.0625).min())
        self.support_history[self.support_slot] = self.support
        self.support_slot = (self.support_slot + 1) % len(self.support_history)

    def request_jump(self):
        if self.phase != 0:
            return False
        self.paused = False
        self._clear_jump()
        self.phase, self.phase_time = 1, float(self.env.d.time)
        self.reference_height = float(self.env.z)
        self.jump_speed = float(np.clip(self.cmd_vx if self.cmd_vx > .1 else self.args.vx, .4, .8))
        self.cmd_vx, self.cmd_vy, self.cmd_wz = self.jump_speed, 0., 0.
        self.requests += 1
        self.events.append(dict(event="request", request=self.requests, time=float(self.env.d.time),
                                root=self.env.d.qpos[:3].tolist(), vx=float(self.env.vx)))
        return True

    def _finish_jump(self, reason):
        accepted = bool(self.landed and self.extended and self.retracted and self.air_s >= .16
                        and self.rim_peak >= .12 and self.air_pitch <= math.radians(10)
                        and self.air_roll <= math.radians(5) and self.stable_hold >= .5)
        self.last_jump = dict(request=self.requests, reason=reason, accepted=accepted,
                              air_s=self.air_s, rim_peak_m=self.rim_peak,
                              air_pitch_deg=math.degrees(self.air_pitch), air_roll_deg=math.degrees(self.air_roll),
                              crouched=self.crouched, extended=self.extended, retracted=self.retracted,
                              landed=self.landed, stable_hold_s=self.stable_hold,
                              duration_s=float(self.env.d.time) - self.jump_start)
        self.completed_jumps.append(self.last_jump.copy())
        self.events.append(dict(event="end", **self.last_jump))
        self.phase = 0

    def _advance_jump(self):
        if self.phase == 0:
            return
        data = self.env.d
        elapsed = float(data.time) - self.phase_time
        q, _ = self._current_active()
        delta = float((q[0] - q[1] + q[2] - q[3]) * .5)
        roll, pitch = self._angles()
        if self.phase == 1:
            self.crouched |= delta < .8 or float(self.env.z) < self.reference_height - .05
            if elapsed >= .32 - 1e-7:
                self.phase, self.phase_time = 2, float(data.time)
        self.air_count = self.air_count + DT if self.no_support else 0.
        if self.phase == 2:
            self.extended |= self.crouched and delta > 1.25
            if self.crouched and self.air_count >= .04 and data.qvel[2] > .1 and self.env.vx > .1 and self.rim > .005:
                self.phase, self.phase_time = 3, float(data.time)
            elif elapsed > .8:
                self._finish_jump("takeoff_timeout")
                return
        if self.phase == 3:
            if self.no_support:
                self.air_s += DT
                self.rim_peak = max(self.rim_peak, self.rim)
                self.air_pitch, self.air_roll = max(self.air_pitch, pitch), max(self.air_roll, roll)
                self.retracted |= self.extended and delta < .9
            if self.air_s >= .08 and self.support.any() and data.qvel[2] < .3:
                self.phase, self.phase_time = 4, float(data.time)
                self.landed = True
        if self.phase == 4:
            stable = (roll < math.radians(15) and pitch < math.radians(15)
                      and abs(data.qvel[2]) < .3 and self.support_history.mean(0).min() >= .8
                      and not self.forbidden and self.env.vx > .1)
            self.stable_hold = self.stable_hold + DT if stable else 0.
            if self.stable_hold >= .5:
                self._finish_jump("landed_and_returned_to_drive")
        if self.phase and float(data.time) - self.jump_start > 4.:
            self._finish_jump("recovery_timeout")

    def _observation(self):
        q, qd = self._current_active()
        rotation = torch.tensor(self.env.d.xmat[self.env.base_id].reshape(3, 3).copy(), dtype=torch.float32)
        joint = q - self.default_active
        joint[4:] = 0.
        mode = torch.zeros(7)
        mode[0] = 1.
        if self.phase:
            elapsed = float(self.env.d.time) - self.phase_time
            duration = .32 if self.phase == 1 else .8 if self.phase == 2 else .4
            mode[1] = 1.
            mode[2] = float(self.phase == 3 and self.air_count > 0)
            mode[3] = float(self.landed or (self.phase == 3 and self.retracted and self.env.d.qvel[2] < -.1))
            mode[4], mode[5] = float(self.phase == 1), float(self.phase == 2)
            mode[6] = min(1., max(0., elapsed / duration)) if self.phase <= 3 else 0.
        return torch.cat((torch.tensor([self.cmd_vx, self.cmd_vy, self.cmd_wz, self.height * 5]),
                          torch.tensor(self.env.d.qvel[3:6].copy(), dtype=torch.float32) * .5,
                          rotation.T @ torch.tensor([0., 0., -1.]), joint,
                          qd * .1, self.a_prev[0], mode)).unsqueeze(0)

    def _physics(self, action):
        env = self.env
        for j in range(env.decim):
            tau = env._torque(action[:, self.ppo_to_env]).detach().numpy().ravel()
            if j % 4 == 0:
                env.d.ctrl[env.act_ids[:4]] = tau[:4]
            env.d.ctrl[env.act_ids[4:]] = tau[4:]
            mujoco.mj_step(env.m, env.d)
            if not np.isfinite(env.d.qpos).all() or not np.isfinite(env.d.qvel).all():
                raise ValueError("nonfinite_state")
            self.closure = max(float(np.linalg.norm(env.d.site_xpos[u] - env.d.site_xpos[v])) for u, v in self.pairs)
            self.mimic = max(abs(float(env.d.qpos[u] - env.d.qpos[v])) for u, v in self.mimics)
            if self.closure > .01 or self.mimic > .01:
                raise ValueError("closure_or_mimic_guard")
        self.a_prev = action.detach()
        env.a_prev = action[:, self.ppo_to_env].detach()

    def step(self, pressed):
        if self.paused:
            return self.telemetry()
        if not self.phase:
            alpha = DT / .22
            target_vx = self.args.vx * (int("w" in pressed) - int("s" in pressed))
            target_wz = self.args.wz * (int("a" in pressed) - int("d" in pressed))
            self.cmd_vx += (target_vx - self.cmd_vx) * alpha
            self.cmd_wz += (target_wz - self.cmd_wz) * alpha
        else:
            self.cmd_vx, self.cmd_vy, self.cmd_wz = self.jump_speed, 0., 0.
        actor = self.jump_actor if self.phase else self.drive_actor
        try:
            with torch.inference_mode():
                action = actor(self._observation()).clamp(-6., 6.)
            self._physics(action)
            self._contacts()
            self._advance_jump()
            if self.env.cos_tilt < .5 or self.local_height() < .12:
                raise ValueError("fall_guard")
        except ValueError as exc:
            self.reason = str(exc)
            if self.phase:
                self._finish_jump(self.reason)
            self.events.append(dict(event="reset", reason=self.reason, time=float(self.env.d.time)))
            self.reset_standing()
        self.steps += 1
        self.z, self.cos_tilt = self.local_height(), float(self.env.cos_tilt)
        return self.telemetry()

    def telemetry(self):
        value = super().telemetry()
        value.update(phase=PHASES[self.phase], requests=self.requests, resets=self.resets - 1,
                     rim_m=self.rim, rim_peak_m=self.rim_peak, air_s=self.air_s,
                     retracted=self.retracted, closure_m=self.closure, mimic_rad=self.mimic,
                     last_jump=self.last_jump, root_xyz=self.env.d.qpos[:3].tolist(),
                     simulation_time_s=float(self.env.d.time))
        if self.terrain:
            value.update(terrain_tiles=1, terrain_tile=self.terrain.tile()["name"],
                         terrain_family=self.terrain.families[self.terrain.family],
                         terrain_difficulty=self.terrain.row)
        return value


class JumpControl(ControlApp):
    def __init__(self, root, sim, runtime):
        self.runtime = runtime
        self._last_write = 0.
        super().__init__(root, sim)

    def _build(self):
        self.root.title("MOD4 | Single Terrain + Space Jump")
        self.root.geometry("470x720+20+25")
        self.root.minsize(450, 700)
        self.root.configure(bg=self.BG)
        outer = tk.Frame(self.root, bg=self.BG, padx=18, pady=16)
        outer.pack(fill="both", expand=True)
        tk.Label(outer, text="MOD4  /  DRIVE + JUMP", bg=self.BG, fg=self.CYAN,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", pady=(0, 12))
        if self.sim.terrain:
            from map_terrain import NAMES
            row = tk.Frame(outer, bg=self.BG)
            row.pack(fill="x", pady=(0, 8))
            self.family_var = tk.StringVar(value=NAMES[self.sim.terrain.family])
            self.level_var = tk.IntVar(value=self.sim.terrain.row)
            ttk.Combobox(row, textvariable=self.family_var, values=NAMES, state="readonly",
                         width=23, takefocus=False).pack(side="left")
            ttk.Combobox(row, textvariable=self.level_var, values=list(range(10)), state="readonly",
                         width=3, takefocus=False).pack(side="left", padx=5)
            self._button(row, "Go", self.go_to_terrain, self.TEXT).pack(side="left", fill="x", expand=True)
            row = tk.Frame(outer, bg=self.BG)
            row.pack(fill="x", pady=(0, 8))
            self._button(row, "Terrain view", self.show_map, self.CYAN).pack(side="left", fill="x", expand=True, padx=2)
            self._button(row, "Follow robot", self.follow_robot, self.CYAN).pack(side="left", fill="x", expand=True, padx=2)
        self.speed_var = tk.DoubleVar(value=.6)
        self.turn_var = tk.DoubleVar(value=1.)
        for text, variable, low, high in (("Drive speed (m/s)", self.speed_var, .2, .8),
                                           ("Turn speed (rad/s)", self.turn_var, .2, 1.5)):
            tk.Scale(outer, label=text, variable=variable, from_=low, to=high, resolution=.1,
                     orient="horizontal", takefocus=False, bg=self.BG, fg=self.TEXT,
                     troughcolor="#30363d", highlightthickness=0).pack(fill="x")
        pad = tk.Frame(outer, bg=self.BG)
        pad.pack(pady=10)
        for text, key, row, col in (("W", "w", 0, 1), ("A", "a", 1, 0),
                                     ("S", "s", 1, 1), ("D", "d", 1, 2)):
            button = self._button(pad, text, lambda: None, self.TEXT)
            button.configure(width=5)
            button.grid(row=row, column=col, padx=3, pady=3)
            button.bind("<ButtonPress-1>", lambda event, k=key: self._handle_key_down(k))
            button.bind("<ButtonRelease-1>", lambda event, k=key: self._handle_key_up(k))
            button.bind("<Leave>", lambda event, k=key: self._handle_key_up(k))
        self._button(outer, "SPACE  /  JUMP", self.jump, self.GREEN).pack(fill="x", pady=(0, 8))
        row = tk.Frame(outer, bg=self.BG)
        row.pack(fill="x")
        for text, command in (("P  Pause", self._toggle_pause), ("R  Reset", self._reset), ("X  Stop", self._stop)):
            self._button(row, text, command, self.TEXT).pack(side="left", fill="x", expand=True, padx=2)
        self.status_var = tk.StringVar(value="READY")
        self.status_label = tk.Label(outer, textvariable=self.status_var, bg=self.PANEL,
                                    fg=self.CYAN, font=("Consolas", 11), anchor="w", justify="left", padx=10, pady=12)
        self.status_label.pack(fill="x", pady=(14, 0))

    def _is_control_foreground(self):
        try:
            user32 = ctypes.windll.user32
            pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), ctypes.byref(pid))
            return pid.value == os.getpid()
        except (AttributeError, OSError):
            return super()._is_control_foreground()

    def jump(self):
        if self.sim.request_jump():
            self._event("Jump requested")

    def go_to_terrain(self):
        from map_terrain import NAMES
        self.keys.clear()
        visible = self.sim.viewer is not None
        self.sim.close()
        self.sim = JumpSimulation(visible=visible, terrain=True, terrain_row=self.level_var.get(),
                                  terrain_family=NAMES.index(self.family_var.get()))
        self.sim.args.vx, self.sim.args.wz = self.speed_var.get(), self.turn_var.get()
        self.sim.paused = True
        self.follow_robot()
        self._focus_control()

    def show_map(self):
        if self.sim.viewer:
            with self.sim.viewer.lock():
                cam = self.sim.viewer.cam
                cam.type = mujoco.mjtCamera.mjCAMERA_FREE
                cam.lookat[:] = [0., 0., .2]
                cam.distance, cam.azimuth, cam.elevation = 13., 115., -55.

    def follow_robot(self):
        if self.sim.viewer:
            with self.sim.viewer.lock():
                cam = self.sim.viewer.cam
                cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
                cam.trackbodyid = self.sim.env.base_id
                cam.distance, cam.azimuth, cam.elevation = 2.4, 115., -18.

    def _handle_key_down(self, key):
        if key not in {"w", "s", "a", "d", "space", "p", "r", "x", "escape"} or key in self.keys:
            return
        if key == "space":
            self.keys.add(key)
            self.jump()
        elif key == "x":
            self.keys.add(key)
            self._stop()
        else:
            if key in {"w", "s", "a", "d"}:
                self.sim.paused = False
            super()._handle_key_down(key)

    def _global_release(self, key):
        ch = self._pynput_key(key)
        if ch is not None:
            self._key_queue.put((ch, False))
        return True

    def _update_ui(self):
        self.sim.args.vx, self.sim.args.wz = self.speed_var.get(), self.turn_var.get()
        if not self._is_control_foreground():
            self.keys.clear()
        t = self.sim.telemetry()
        state = "PAUSED" if self.sim.paused else t["phase"]
        last = t["last_jump"]
        last_line = "" if last is None else f"\nLast jump {last['rim_peak_m']*100:.1f} cm / {last['air_s']:.2f} s"
        self.status_var.set(f"{state}    jumps {t['requests']}\n"
                            f"Drive {t['cmd_vx']:+.2f} / actual {t['vx']:+.2f} m/s\n"
                            f"Turn  {t['cmd_wz']:+.2f} rad/s\n"
                            f"Wheel clearance {max(0.,t['rim_m'])*100:5.1f} cm\n"
                            f"Air {t['air_s']:.2f} s / tuck {t['retracted']}"
                            f"{last_line}\nResets {t['resets']}")
        if time.monotonic() - self._last_write > .2:
            save_json(self.runtime / "STATUS.json", dict(epoch=time.time(), keys=sorted(self.keys), **t))
            self._last_write = time.monotonic()


def smoke(output):
    output.mkdir(parents=True, exist_ok=False)
    (output / "source.py").write_bytes(Path(__file__).read_bytes())
    cases = []
    sim = JumpSimulation()
    with (output / "trajectory.jsonl").open("w", encoding="utf-8") as log:
        for name, speed, pressed in (("forward_04", .4, {"w"}), ("forward_06", .6, {"w"}),
                                      ("forward_08", .8, {"w"}), ("rest", .6, set())):
            sim.reset_standing()
            sim.args.vx = speed
            before = sim.resets
            for i in range(125):
                sim.step(pressed if i >= 40 else set())
            start_vx = float(sim.env.vx)
            assert sim.request_jump()
            first = sim.requests
            phases = set()
            for i in range(225):
                if sim.phase:
                    assert not sim.request_jump()
                sim.step(pressed)
                phases.add(sim.phase)
                log.write(json.dumps(dict(case=name, step=i, **sim.telemetry())) + "\n")
            cases.append(dict(name=name, start_vx=start_vx, phases=sorted(phases),
                              resets=sim.resets-before, last_jump=sim.last_jump,
                              requests_during_run=sim.requests-first, final=sim.telemetry()))
    report = dict(epoch=time.time(), plant="MOD4v3_HW300N60_R3", dt_s=sim.env.dt,
                  policy_hz=50, leg_hz=100, wheel_hz=400, jump_sha256=JUMP_SHA,
                  drive_sha256=DRIVE_SHA, real_time_physics=True, teacher_executed=False,
                  cases=cases, events=sim.events)
    save_json(output / "RESULT.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    sim.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.smoke:
        smoke(args.output or HERE / "evidence" / ("smoke_" + time.strftime("%Y%m%d_%H%M%S")))
        return
    runtime = args.output or HERE / "runtime" / time.strftime("%Y%m%d_%H%M%S")
    root = tk.Tk()
    sim = JumpSimulation(visible=True, terrain=True)
    sim.paused = True
    app = JumpControl(root, sim, runtime)
    root.after(200, app._focus_control)
    ready = dict(epoch=time.time(), pid=os.getpid(), jump=str(JUMP), jump_sha256=JUMP_SHA,
                 drive=str(DRIVE), drive_sha256=DRIVE_SHA, viewer_running=sim.viewer.is_running(),
                 manual=True, autoplay=False, paused=True, reused_controller="play_ppo_flatv1_control.ControlApp",
                 map_tiles=1, map_rows=1, map_cols=1, map_tile=sim.terrain.tile()["name"],
                 map_source="One original tile from adjacent player's saved Isaac Lab Rough-v1 map",
                 space="one-shot jump, retained WASD, return to drive after landing", runtime=str(runtime))
    save_json(runtime / "READY.json", ready)
    print("MANUAL_JUMP_READY " + json.dumps(ready), flush=True)
    root.mainloop()


if __name__ == "__main__":
    main()
