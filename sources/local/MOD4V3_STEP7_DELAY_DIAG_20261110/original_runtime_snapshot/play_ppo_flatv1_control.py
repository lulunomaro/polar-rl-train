# SPDX-License-Identifier: MIT
"""Separate control panel for the MOD4v3 Flat-v1 MuJoCo player.

The MuJoCo window is deliberately left untouched: no embedded text and no
key callback.  Keyboard input is handled only by this Tk control window, so
MuJoCo's native keyboard shortcuts keep working when that window is focused.

Control panel:
  W / S          forward / backward
  A / D          yaw left / right
  Q / E          lower / raise standing height
  1 / 2 / 3      height presets 0.20 / 0.28 / 0.40 m
  F              random fall / recovery test
  G              toggle automatic random falls
  R              reset to standing
  Space          stop linear and yaw commands
  P              pause / resume
  Esc            exit
"""
from __future__ import annotations

import argparse
import ctypes
import json
import math
import queue
import random
import sys
import time
import tkinter as tk
from pathlib import Path

import mujoco
import mujoco.viewer
import numpy as np
import torch
from pynput import keyboard

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from play_mod4v3 import Mod4v3Mujoco, RobotSpec, _q_from_bank, _q_from_runtime  # noqa: E402
from play_ppo_flatv1 import ActorMLP, CONTROL_DT, _map  # noqa: E402

ROOT = Path(r"D:\claude2\fangzhen")
DEFAULT_XML = ROOT / r"tmp\mod4v3_r3_extract_20261107\MOD4v3_HW300N60_R3\mjcf\scene.xml"
DEFAULT_RUNTIME = ROOT / r"tmp\mod4v3_r3_extract_20261107\MOD4v3_HW300N60_R3\runtime_config.json"
DEFAULT_SEMANTICS = ROOT / r"tmp\mod4v3_r3_extract_20261107\MOD4v3_HW300N60_R3\semantics.json"
DEFAULT_BANK = ROOT / r"tmp\mod4v3_asset\reset_bank.json"
DEFAULT_TEMPLATE = HERE / "ckpt_013000.pt"
DEFAULT_CKPT = HERE / "ckpt_smooth30_final.pt"

ACTION_CLIP = 6.0
HEIGHT_MIN = 0.20
HEIGHT_MAX = 0.42
HEIGHT_RATE = 0.14
CMD_SLEW = 0.22


def _quat_from_euler_xyz(roll: float, pitch: float, yaw: float) -> np.ndarray:
    q = np.zeros(4, dtype=np.float64)
    mujoco.mju_euler2Quat(q, np.array([roll, pitch, yaw], dtype=np.float64), "xyz")
    return q


class FallTracker:
    def __init__(self):
        self.active = False
        self.hold = 0
        self.falls = 0
        self.recovered = 0
        self.failed = 0

    def start(self):
        # Starting another fall before the previous attempt resolves means the
        # previous attempt did not reach the 0.6 s recovery hold.
        if self.active:
            self.failed += 1
        self.active = True
        self.hold = 0
        self.falls += 1

    def update(self, z: float, cos_tilt: float):
        if not self.active:
            return
        if z > 0.24 and cos_tilt > 0.90:
            self.hold += 1
            if self.hold >= 30:
                self.active = False
                self.recovered += 1
        else:
            self.hold = 0

    def fail(self):
        if self.active:
            self.active = False
            self.failed += 1

    def reset(self):
        self.active = False
        self.hold = 0


class Simulation:
    def __init__(self, args):
        self.args = args
        torch.set_num_threads(1)
        ck = torch.load(args.ckpt, map_location=args.device, weights_only=False)
        template = torch.load(args.template, map_location="cpu", weights_only=False)
        spec = RobotSpec(**template["spec"])
        runtime = json.loads(Path(args.runtime).read_text(encoding="utf-8"))
        semantics = json.loads(Path(args.semantics).read_text(encoding="utf-8"))
        bank = json.loads(Path(args.bank).read_text(encoding="utf-8"))
        self.default_q = _q_from_runtime(runtime, spec.joint_names)
        self.bank_q, self.bank_z = _q_from_bank(bank, semantics, spec.joint_names)
        order = list(ck["action_order"])
        expected = [
            "left_front1_joint", "left_rear1_joint", "right_front1_joint",
            "right_rear1_joint", "left_wheel_joint", "right_wheel_joint",
        ]
        if order != expected:
            raise ValueError(f"unexpected PPO action order: {order}")
        self.actor = ActorMLP().to(args.device)
        self.actor.load_state_dict(ck["actor_state_dict"], strict=False)
        self.actor.eval()
        self.env = Mod4v3Mujoco(
            args.xml, spec, self.default_q, self.bank_q, self.bank_z,
            device=args.device, action_clip=ACTION_CLIP,
        )
        self.ppo_to_env = torch.tensor([0, 2, 1, 3, 4, 5], dtype=torch.long, device=args.device)
        self.active_names = order
        self.default_active = _map(self.default_q, spec.joint_names, order).to(args.device)
        self.a_prev = torch.zeros(1, 6, device=args.device)
        self.tracker = FallTracker()
        self.cmd_vx = 0.0
        self.cmd_vy = 0.0
        self.cmd_wz = 0.0
        self.height = float(np.clip(args.height, HEIGHT_MIN, HEIGHT_MAX))
        self.drop_height = float(args.drop_height)
        self.drop_tilt = float(args.drop_tilt)
        self.action_ema = float(args.action_ema)
        self._action_filter = None
        self.paused = False
        self.auto_fall = bool(args.auto_fall)
        self.fall_interval = max(2.0, float(args.fall_interval))
        self.next_auto_fall = time.monotonic() + self.fall_interval
        self.steps = 0
        self.z = float(self.env.z)
        self.cos_tilt = float(self.env.cos_tilt)
        self.viewer = None
        if not args.headless:
            self.viewer = mujoco.viewer.launch_passive(self.env.m, self.env.d)
            self.viewer.cam.type = 1
            self.viewer.cam.trackbodyid = self.env.base_id
            self.viewer.cam.distance = 1.65
            self.viewer.cam.azimuth = 120.0
            self.viewer.cam.elevation = -15.0
        if args.start_fall:
            self.trigger_random_fall()

    def _current_active(self):
        q_all = torch.tensor(self.env.d.qpos[self.env.qadr_all], dtype=torch.float32, device=self.args.device)
        qd_all = torch.tensor(self.env.d.qvel[self.env.dadr_all], dtype=torch.float32, device=self.args.device)
        return _map(q_all, self.env.spec.joint_names, self.active_names), _map(
            qd_all, self.env.spec.joint_names, self.active_names
        )

    def set_height(self, value: float):
        self.height = float(np.clip(value, HEIGHT_MIN, HEIGHT_MAX))

    def reset_standing(self):
        self.env.reset()
        self.a_prev.zero_()
        self._action_filter = None
        self.cmd_vx = 0.0
        self.cmd_vy = 0.0
        self.cmd_wz = 0.0
        self.tracker.reset()
        self.z = float(self.env.z)
        self.cos_tilt = float(self.env.cos_tilt)

    def trigger_random_fall(self):
        # Match the training air-reset envelope: a random airborne pose and a
        # small root velocity, then let the policy attempt recovery.
        self.env.reset()
        roll = random.uniform(-self.drop_tilt, self.drop_tilt)
        pitch = random.uniform(-0.80 * self.drop_tilt, 0.80 * self.drop_tilt)
        yaw = random.uniform(-math.pi, math.pi)
        self.env.d.qpos[0] = random.uniform(-0.50, 0.50)
        self.env.d.qpos[1] = random.uniform(-0.50, 0.50)
        self.env.d.qpos[2] = max(0.50, self.drop_height + random.uniform(-0.03, 0.03))
        self.env.d.qpos[3:7] = _quat_from_euler_xyz(roll, pitch, yaw)
        self.env.d.qvel[0] = random.uniform(-1.8, 1.8)
        self.env.d.qvel[1] = random.uniform(-0.6, 0.6)
        self.env.d.qvel[2] = random.uniform(-0.25, 0.20)
        self.env.d.qvel[3] = random.uniform(-0.55, 0.55)
        self.env.d.qvel[4] = random.uniform(-0.55, 0.55)
        self.env.d.qvel[5] = random.uniform(-1.0, 1.0)
        mujoco.mj_forward(self.env.m, self.env.d)
        self.env.a_prev.zero_()
        self.a_prev.zero_()
        self._action_filter = None
        self.tracker.start()
        self.z = float(self.env.z)
        self.cos_tilt = float(self.env.cos_tilt)

    def toggle_auto_fall(self):
        self.auto_fall = not self.auto_fall
        self.next_auto_fall = time.monotonic() + self.fall_interval

    def toggle_pause(self):
        self.paused = not self.paused

    def telemetry(self):
        return {
            "z": self.z,
            "cos_tilt": self.cos_tilt,
            "vx": float(self.env.vx),
            "cmd_vx": self.cmd_vx,
            "cmd_vy": self.cmd_vy,
            "cmd_wz": self.cmd_wz,
            "height": self.height,
            "falls": self.tracker.falls,
            "recovered": self.tracker.recovered,
            "failed": self.tracker.failed,
            "paused": self.paused,
            "auto_fall": self.auto_fall,
            "steps": self.steps,
        }

    def step(self, pressed: set[str]):
        if self.paused:
            return self.telemetry()
        now = time.monotonic()
        if self.auto_fall and now >= self.next_auto_fall:
            self.trigger_random_fall()
            self.next_auto_fall = now + self.fall_interval

        vx_target = (self.args.vx if "w" in pressed else 0.0) + (-self.args.vx if "s" in pressed else 0.0)
        vy_target = (getattr(self.args, "vy", 0.5) if "j" in pressed else 0.0) + (-getattr(self.args, "vy", 0.5) if "l" in pressed else 0.0)
        wz_target = (self.args.wz if "a" in pressed else 0.0) + (-self.args.wz if "d" in pressed else 0.0)
        if "space" in pressed:
            vx_target = 0.0
            vy_target = 0.0
            wz_target = 0.0
        if "q" in pressed:
            self.set_height(self.height - HEIGHT_RATE * CONTROL_DT)
        if "e" in pressed:
            self.set_height(self.height + HEIGHT_RATE * CONTROL_DT)

        alpha = min(1.0, CONTROL_DT / CMD_SLEW)
        self.cmd_vx += (vx_target - self.cmd_vx) * alpha
        self.cmd_vy += (vy_target - self.cmd_vy) * alpha
        self.cmd_wz += (wz_target - self.cmd_wz) * alpha
        q, qd = self._current_active()
        R = torch.tensor(
            np.array(self.env.d.xmat[self.env.base_id], dtype=np.float64).reshape(3, 3),
            dtype=torch.float32,
        )
        gravity_b = R.T @ torch.tensor([0.0, 0.0, -1.0], dtype=torch.float32)
        root_ang_vel_b = torch.tensor(self.env.d.qvel[3:6], dtype=torch.float32)
        joint_pos = q - self.default_active
        joint_pos[4:] = 0.0
        mode = torch.zeros(7, dtype=torch.float32)
        mode[0] = 1.0
        obs = torch.cat((
            torch.tensor([self.cmd_vx, self.cmd_vy, self.cmd_wz], dtype=torch.float32),
            torch.tensor([self.height * 5.0], dtype=torch.float32),
            root_ang_vel_b * 0.5,
            gravity_b,
            joint_pos,
            qd[:4] * 0.1,
            qd[4:] * 0.1,
            self.a_prev[0],
            mode * torch.tensor([1, 1, 1, 1, 1, 5, 1], dtype=torch.float32),
        ), 0).unsqueeze(0).to(self.args.device)
        with torch.no_grad():
            raw_action = self.actor(obs).clamp(-ACTION_CLIP, ACTION_CLIP)
            if self.action_ema > 0.0:
                if self._action_filter is None:
                    a_ppo = raw_action
                else:
                    a_ppo = self.action_ema * self._action_filter + (1.0 - self.action_ema) * raw_action
                self._action_filter = a_ppo.detach().clone()
            else:
                a_ppo = raw_action
                self._action_filter = None
        self.env.step(a_ppo[:, self.ppo_to_env])
        self.a_prev = a_ppo.detach()
        self.steps += 1
        self.z = float(self.env.z)
        self.cos_tilt = float(self.env.cos_tilt)
        self.tracker.update(self.z, self.cos_tilt)
        # Do not terminate a tilted robot while it is still falling from a
        # high drop.  Tilt termination only applies near the ground; this lets
        # a 1 m random-drop test actually reach the landing/recovery phase.
        if (self.z < self.args.term_height or
                (self.z < 0.30 and self.cos_tilt < 0.766) or
                not np.isfinite(self.z)):
            self.tracker.fail()
            print(f"[term] step={self.steps} z={self.z:.3f} cos={self.cos_tilt:.3f}; reset")
            self.reset_standing()
            self.next_auto_fall = time.monotonic() + self.fall_interval
        return self.telemetry()

    def close(self):
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None


class ControlApp:
    BG = "#0d1117"
    PANEL = "#161b22"
    TEXT = "#e6edf3"
    MUTED = "#8b949e"
    CYAN = "#39d5ff"
    GREEN = "#4be38a"
    RED = "#ff6b81"
    YELLOW = "#ffd166"

    def __init__(self, root, sim: Simulation):
        self.root = root
        self.sim = sim
        self.keys: set[str] = set()
        self.last_event = "ready"
        self._syncing_slider = False
        self._next_tick = time.perf_counter()
        self._closed = False
        self._key_queue: queue.Queue[tuple[str, bool]] = queue.Queue()
        self._build()
        self.root.update_idletasks()
        self._control_hwnd = int(self.root.winfo_id())
        self._listener = keyboard.Listener(
            on_press=self._global_press,
            on_release=self._global_release,
        )
        self._listener.daemon = True
        self._listener.start()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.bind_all("<KeyPress>", self._key_down)
        self.root.bind_all("<KeyRelease>", self._key_up)
        self.root.after(30, self.tick)

    def _build(self):
        self.root.title("MOD4v3 · Flat-v1 控制器")
        self.root.geometry("500x670+30+70")
        self.root.minsize(460, 620)
        self.root.configure(bg=self.BG)

        outer = tk.Frame(self.root, bg=self.BG, padx=16, pady=14)
        outer.pack(fill="both", expand=True)

        title = tk.Label(
            outer, text="MOD4v3  /  FLAT-v1 PLAYER", bg=self.BG, fg=self.CYAN,
            font=("Microsoft YaHei UI", 18, "bold"), anchor="w",
        )
        title.pack(fill="x")
        subtitle = tk.Label(
            outer, text="点击本窗口后使用 WASD；MuJoCo 窗口保留原生快捷键",
            bg=self.BG, fg=self.MUTED, font=("Microsoft YaHei UI", 9), anchor="w",
        )
        subtitle.pack(fill="x", pady=(2, 12))

        metrics = tk.Frame(outer, bg=self.PANEL, padx=12, pady=10)
        metrics.pack(fill="x")
        self.vars = {}
        rows = [
            ("高度 z", "z", self.CYAN),
            ("倾斜 cos", "cos_tilt", self.GREEN),
            ("速度 vx", "vx", self.TEXT),
            ("前进指令", "cmd_vx", self.TEXT),
            ("横移指令", "cmd_vy", self.TEXT),
            ("转向指令", "cmd_wz", self.TEXT),
            ("站立高度", "height", self.YELLOW),
            ("跌倒 / 恢复 / 失败", "fall_stats", self.TEXT),
            ("累计步数", "steps", self.MUTED),
        ]
        for i, (label, key, color) in enumerate(rows):
            tk.Label(metrics, text=label, bg=self.PANEL, fg=self.MUTED,
                     font=("Microsoft YaHei UI", 9), anchor="w").grid(row=i, column=0, sticky="w", padx=(0, 18), pady=2)
            var = tk.StringVar(value="—")
            self.vars[key] = var
            tk.Label(metrics, textvariable=var, bg=self.PANEL, fg=color,
                     font=("Consolas", 10, "bold"), anchor="e").grid(row=i, column=1, sticky="e", pady=2)
        metrics.columnconfigure(0, weight=1)
        metrics.columnconfigure(1, weight=1)

        height_box = tk.Frame(outer, bg=self.BG)
        height_box.pack(fill="x", pady=(14, 4))
        tk.Label(height_box, text="站立高度", bg=self.BG, fg=self.TEXT,
                 font=("Microsoft YaHei UI", 10, "bold")).pack(side="left")
        self.height_value = tk.StringVar(value="0.280 m")
        tk.Label(height_box, textvariable=self.height_value, bg=self.BG, fg=self.YELLOW,
                 font=("Consolas", 10, "bold")).pack(side="right")
        self.height_scale = tk.Scale(
            outer, from_=HEIGHT_MIN, to=HEIGHT_MAX, resolution=0.005,
            orient=tk.HORIZONTAL, showvalue=False, command=self._height_changed,
            bg=self.BG, fg=self.TEXT, troughcolor="#30363d",
            activebackground=self.CYAN, highlightthickness=0, bd=0,
            sliderrelief=tk.FLAT, length=440, takefocus=False,
        )
        self.height_scale.set(self.sim.height)
        self.height_scale.pack(fill="x", pady=(0, 10))

        buttons = tk.Frame(outer, bg=self.BG)
        buttons.pack(fill="x")
        self._button(buttons, "F  1m 随机跌落", self._random_fall, self.RED).grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=4)
        self._button(buttons, "G  自动跌倒", self._toggle_auto, self.YELLOW).grid(row=0, column=1, sticky="ew", padx=(6, 0), pady=4)
        self._button(buttons, "R  复位站立", self._reset, self.GREEN).grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=4)
        self._button(buttons, "Space  急停", self._stop, self.CYAN).grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=4)
        self._button(buttons, "P  暂停 / 继续", self._toggle_pause, self.TEXT).grid(row=2, column=0, sticky="ew", padx=(0, 6), pady=4)
        self._button(buttons, "Esc  退出", self.close, self.MUTED).grid(row=2, column=1, sticky="ew", padx=(6, 0), pady=4)
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)

        help_box = tk.Frame(outer, bg=self.PANEL, padx=12, pady=10)
        help_box.pack(fill="x", pady=(12, 0))
        help_text = (
            "W / S   前进 / 后退      A / D   左转 / 右转      J / L   左移 / 右移\n"
            "Q / E   降低 / 升高高度    1 / 2 / 3   0.20 / 0.28 / 0.40 m\n"
            "4 / 5 / 6   前进速度 0.9 / 1.5 / 2.0 m/s\n"
            "F   1m 随机跌落恢复测试   G   自动跌落开关   P   暂停"
        )
        tk.Label(help_box, text=help_text, justify="left", bg=self.PANEL, fg=self.MUTED,
                 font=("Microsoft YaHei UI", 9), anchor="w").pack(fill="x")
        self.smooth_var = tk.BooleanVar(value=self.sim.action_ema > 0.0)
        tk.Checkbutton(
            help_box, text="回放动作平滑（仅显示，不改变训练策略）",
            variable=self.smooth_var, command=self._toggle_smoothing,
            bg=self.PANEL, fg=self.CYAN, activebackground=self.PANEL,
            activeforeground=self.CYAN, selectcolor=self.BG,
            font=("Microsoft YaHei UI", 9), anchor="w",
        ).pack(fill="x", pady=(6, 0))

        bottom = tk.Frame(outer, bg=self.BG)
        bottom.pack(fill="x", pady=(10, 0))
        self.status_var = tk.StringVar(value="ready")
        self.status_label = tk.Label(bottom, textvariable=self.status_var, bg=self.BG,
                                     fg=self.CYAN, font=("Consolas", 9, "bold"), anchor="w")
        self.status_label.pack(fill="x")
        tk.Label(bottom, text="点击控制器窗口后 WASD 才会接管；点击 MuJoCo 则使用其原生快捷键",
                 bg=self.BG, fg=self.MUTED, font=("Microsoft YaHei UI", 8), anchor="w").pack(fill="x", pady=(2, 0))

    def _button(self, parent, text, command, color):
        return tk.Button(
            parent, text=text, command=command, bg=self.PANEL, fg=color,
            activebackground="#21262d", activeforeground=color,
            relief=tk.FLAT, bd=0, padx=10, pady=8,
            font=("Microsoft YaHei UI", 10, "bold"), cursor="hand2",
        )

    def _event(self, text):
        self.last_event = text
        self.status_var.set(f"event: {text}")

    def _focus_control(self):
        self.root.lift()
        self.root.focus_force()

    def _height_changed(self, value):
        if self._syncing_slider:
            return
        self.sim.set_height(float(value))
        self.height_value.set(f"{self.sim.height:.3f} m")
        self._event(f"height {self.sim.height:.3f}")

    def _is_control_foreground(self) -> bool:
        """Return True only while this control window owns keyboard focus."""
        try:
            user32 = ctypes.windll.user32
            foreground = int(user32.GetForegroundWindow())
            control = int(user32.GetAncestor(self._control_hwnd, 2) or self._control_hwnd)
            return foreground != 0 and foreground == control
        except Exception:
            return True

    @staticmethod
    def _pynput_key(key):
        if key == keyboard.Key.esc:
            return "escape"
        if key == keyboard.Key.space:
            return "space"
        try:
            ch = key.char
            return ch.lower() if ch else None
        except AttributeError:
            return None

    def _global_press(self, key):
        if not self._is_control_foreground():
            return True
        ch = self._pynput_key(key)
        if ch is not None:
            self._key_queue.put((ch, True))
        return True

    def _global_release(self, key):
        if not self._is_control_foreground():
            return True
        ch = self._pynput_key(key)
        if ch is not None:
            self._key_queue.put((ch, False))
        return True

    def _key_down(self, event):
        self._handle_key_down(event.keysym.lower())
        return "break"

    def _key_up(self, event):
        self._handle_key_up(event.keysym.lower())
        return "break"

    def _handle_key_down(self, key):
        if key == "escape":
            self.close()
            return
        if key in self.keys:
            return
        self.keys.add(key)
        if key == "f":
            self.sim.trigger_random_fall()
            self._event("random fall")
        elif key == "g":
            self.sim.toggle_auto_fall()
            self._event(f"auto fall {'ON' if self.sim.auto_fall else 'OFF'}")
        elif key == "r":
            self.sim.reset_standing()
            self._event("reset standing")
        elif key == "p":
            self.sim.toggle_pause()
            self._event("paused" if self.sim.paused else "running")
        elif key == "space":
            self.sim.cmd_vx = 0.0
            self.sim.cmd_vy = 0.0
            self.sim.cmd_wz = 0.0
            self._event("stop")
        elif key == "1":
            self.sim.set_height(0.20)
            self._event("height 0.20")
        elif key == "2":
            self.sim.set_height(0.28)
            self._event("height 0.28")
        elif key == "3":
            self.sim.set_height(0.40)
            self._event("height 0.40")
        elif key == "4":
            self.sim.args.vx = 0.9
            self._event("speed 0.9 m/s")
        elif key == "5":
            self.sim.args.vx = 1.5
            self._event("speed 1.5 m/s")
        elif key == "6":
            self.sim.args.vx = 2.0
            self._event("speed 2.0 m/s")

    def _handle_key_up(self, key):
        self.keys.discard(key)

    def _random_fall(self):
        self._focus_control()
        self.sim.trigger_random_fall()
        self._event("random fall")

    def _toggle_auto(self):
        self._focus_control()
        self.sim.toggle_auto_fall()
        self._event(f"auto fall {'ON' if self.sim.auto_fall else 'OFF'}")

    def _reset(self):
        self._focus_control()
        self.sim.reset_standing()
        self._event("reset standing")

    def _stop(self):
        self._focus_control()
        self.keys.discard("w")
        self.keys.discard("s")
        self.keys.discard("a")
        self.keys.discard("d")
        self.keys.discard("j")
        self.keys.discard("l")
        self.sim.cmd_vx = 0.0
        self.sim.cmd_vy = 0.0
        self.sim.cmd_wz = 0.0
        self._event("stop")

    def _toggle_pause(self):
        self._focus_control()
        self.sim.toggle_pause()
        self._event("paused" if self.sim.paused else "running")

    def _toggle_smoothing(self):
        self._focus_control()
        self.sim.action_ema = 0.35 if self.smooth_var.get() else 0.0
        self.sim._action_filter = None
        self._event(f"playback smoothing {'ON' if self.sim.action_ema else 'OFF'}")

    def _sync_height_widgets(self):
        self.height_value.set(f"{self.sim.height:.3f} m")
        if abs(self.height_scale.get() - self.sim.height) > 1e-6:
            self._syncing_slider = True
            self.height_scale.set(self.sim.height)
            self._syncing_slider = False

    def _update_ui(self):
        t = self.sim.telemetry()
        self.vars["z"].set(f"{t['z']:.3f} m")
        self.vars["cos_tilt"].set(f"{t['cos_tilt']:.3f}")
        self.vars["vx"].set(f"{t['vx']:+.2f} m/s")
        self.vars["cmd_vx"].set(f"{t['cmd_vx']:+.2f} m/s")
        self.vars["cmd_vy"].set(f"{t['cmd_vy']:+.2f} m/s")
        self.vars["cmd_wz"].set(f"{t['cmd_wz']:+.2f} rad/s")
        self.vars["height"].set(f"{t['height']:.3f} m")
        self.vars["fall_stats"].set(f"{t['falls']} / {t['recovered']} / {t['failed']}")
        self.vars["steps"].set(str(t["steps"]))
        mode = []
        if t["paused"]:
            mode.append("PAUSED")
        if t["auto_fall"]:
            mode.append("AUTO-FALL")
        if mode:
            self.status_label.configure(fg=self.YELLOW)
            self.status_var.set("  |  ".join(mode) + f"  |  event: {self.last_event}")
        else:
            self.status_label.configure(fg=self.CYAN)
            self.status_var.set(f"running  |  event: {self.last_event}")
        self._sync_height_widgets()

    def tick(self):
        if self._closed:
            return
        if self.sim.viewer is not None and not self.sim.viewer.is_running():
            self.close()
            return
        try:
            while True:
                try:
                    key, down = self._key_queue.get_nowait()
                except queue.Empty:
                    break
                if self._closed:
                    return
                if down:
                    self._handle_key_down(key)
                else:
                    self._handle_key_up(key)
            self.sim.step(self.keys)
            if self.sim.viewer is not None:
                self.sim.viewer.sync()
            self._update_ui()
        except Exception as exc:
            self._event(f"error: {exc}")
            print(f"[error] {exc}")
            self.close()
            return
        self._next_tick += CONTROL_DT
        now = time.perf_counter()
        if self._next_tick < now - 0.15:
            self._next_tick = now
        delay_ms = max(1, int((self._next_tick - time.perf_counter()) * 1000))
        self.root.after(delay_ms, self.tick)

    def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            self._listener.stop()
        except Exception:
            pass
        self.sim.close()
        try:
            self.root.destroy()
        except tk.TclError:
            pass


def run_headless(args):
    sim = Simulation(args)
    try:
        for n in range(max(1, args.steps)):
            sim.step(set())
            if n % args.log_every == 0:
                t = sim.telemetry()
                print(
                    f"step={t['steps']:5d} z={t['z']:.3f} cos={t['cos_tilt']:.3f} "
                    f"vx={t['vx']:+.2f} h={t['height']:.3f} "
                    f"falls={t['falls']} recovered={t['recovered']} failed={t['failed']}"
                )
        t = sim.telemetry()
        print(f"[done] steps={t['steps']} falls={t['falls']} recovered={t['recovered']} failed={t['failed']}")
    finally:
        sim.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default=str(DEFAULT_CKPT))
    ap.add_argument("--xml", default=str(DEFAULT_XML))
    ap.add_argument("--runtime", default=str(DEFAULT_RUNTIME))
    ap.add_argument("--semantics", default=str(DEFAULT_SEMANTICS))
    ap.add_argument("--bank", default=str(DEFAULT_BANK))
    ap.add_argument("--template", default=str(DEFAULT_TEMPLATE))
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--height", type=float, default=0.28)
    ap.add_argument("--vx", type=float, default=0.90)
    ap.add_argument("--vy", type=float, default=0.50)
    ap.add_argument("--wz", type=float, default=1.20)
    ap.add_argument("--term_height", type=float, default=0.18)
    ap.add_argument("--fall_interval", type=float, default=7.0)
    ap.add_argument("--drop_height", type=float, default=1.0, help="random drop height in metres")
    ap.add_argument("--drop_tilt", type=float, default=0.75, help="random roll/pitch tilt envelope in radians")
    ap.add_argument("--action_ema", type=float, default=0.0, help="playback-only action smoothing; 0 disables it")
    ap.add_argument("--start_fall", action="store_true")
    ap.add_argument("--auto_fall", action="store_true")
    ap.add_argument("--headless", action="store_true")
    ap.add_argument("--steps", type=int, default=0)
    ap.add_argument("--log_every", type=int, default=25)
    args = ap.parse_args()
    if args.headless:
        run_headless(args)
        return
    root = tk.Tk()
    sim = Simulation(args)
    app = ControlApp(root, sim)
    root.after(100, app._focus_control)
    root.mainloop()


if __name__ == "__main__":
    main()
