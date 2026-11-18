# SPDX-License-Identifier: MIT
"""Interactive Pure-RL WASD + High-Jump & Moving-Jump Playground (MOD4v3 MoE RL).

Runs weights/model_rl_best.pt via StatefulMoEJumpActor (obs_35 -> act_6, internal 12x35 HistoryQueue):
  - ZERO hand-coded state machine, ZERO external timers, ZERO privileged world-z inputs!
  - Pressing Space or J ONLY sets standard mode bit obs[30] = 1.0 for 1.44s (72 policy steps),
    routing from frozen E0 (c874) to trained pure-neural E_jump.

Controls:
  W / S          Forward / Backward drive
  A / D          Turn Left / Right
  Q / E          Lower / Raise stance height (0.26 - 0.38 m)
  Space or J     Trigger Pure-RL Deep-Crouch High Jump (standing or moving!)
  1 / 2          Switch Scene:
                   1 = Flat Benchmark Arena
                   2 = 3D Multi-Hurdle Course (16 cm / 18 cm / 20 cm solid hurdles)
  R              Reset robot to standing
  X              Zero velocity commands
  P              Pause / Resume
  Esc            Exit cleanly

Headless smoke test (non-blocking):
  python play_rl_high_jump_wasd.py --headless --steps 360
"""
from __future__ import annotations

import argparse
import ctypes
import json
import math
import os
from pathlib import Path
import queue
import sys
import time
from typing import Any

import mujoco
import mujoco.viewer
import numpy as np
import torch

from moe_jump_model import (
    EXPECTED_C874_SHA256,
    HERE,
    JUMP_MODE_BIT_INDEX,
    MoEJumpActorCritic,
    StatefulMoEJumpActor,
)
from rl_jump_env import (
    CONTROL_DT,
    EXPECTED_XML_SHA256,
    JUMP_GATE_DURATION_S,
    Mod4v3RLJumpEnv,
)

SCENE_KEYS = {"1": "flat", "2": "hurdles"}
SCENE_LABELS = {
    "flat": "1 · Flat Benchmark Arena (纯RL平地大跳标尺场)",
    "hurdles": "2 · 3D Multi-Hurdle Course (16/18/20cm 实体跨栏场)",
}


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class PureRLJumpInteractiveSim:
    """Interactive simulation wrapper driving MOD4v3 purely with StatefulMoEJumpActor."""

    def __init__(self, ckpt_path: Path, scene_name: str = "flat", visible: bool = True):
        if "stage1_bc_dagger" in sys.modules:
            raise RuntimeError("Forbidden teacher module loaded in pure-RL playground!")
        self.ckpt_path = ckpt_path
        self.model = MoEJumpActorCritic.load_from_checkpoint(ckpt_path, device="cpu")
        self.actor = StatefulMoEJumpActor(self.model)

        self.scene_name = scene_name
        self.env = Mod4v3RLJumpEnv(seed=2026)
        self.drive_speed = 0.85
        self.turn_speed = 1.00
        self.target_height = 0.28
        self.paused = False
        self.steps = 0
        self.resets = 0
        self.jump_triggers = 0
        self.peak_rim_cm = 0.0
        self.jump_gate_until = -99.0
        self._first_obs = True

        self._configure_scene(scene_name)
        self.viewer = None
        if visible:
            self.viewer = mujoco.viewer.launch_passive(
                self.env.m,
                self.env.d,
                show_left_ui=False,
                show_right_ui=False,
            )
            self.viewer.cam.azimuth = 96.0
            self.viewer.cam.elevation = -13.0
            self.viewer.cam.distance = 2.75
            self.viewer.cam.lookat[:] = [0.2, 0.0, 0.34]

    def _configure_scene(self, scene_name: str) -> None:
        self.scene_name = scene_name
        hurdles = [(1.80, 0.16), (4.40, 0.18), (7.10, 0.20)] if scene_name == "hurdles" else []
        self.env.reset(
            dr_scale=0.0,
            v_cmd=0.0,
            wz_cmd=0.0,
            h_nom=self.target_height,
            jump_times=(),
            max_episode_s=1e6,
            hurdles=hurdles,
        )
        self.jump_gate_until = -99.0
        self._first_obs = True
        self.actor.reset_history()

    def reset_standing(self) -> None:
        self._configure_scene(self.scene_name)

    def set_target_height(self, h: float) -> None:
        self.target_height = float(np.clip(h, 0.25, 0.38))
        self.env.h_nom = self.target_height

    def trigger_rl_jump(self) -> bool:
        now = float(self.env.d.time)
        if now < self.jump_gate_until - 0.12:
            return False
        self.jump_gate_until = now + JUMP_GATE_DURATION_S
        self.env.jump_times = (*self.env.jump_times, now)
        self.jump_triggers += 1
        return True

    def step_keys(self, pressed: set[str]) -> dict[str, Any]:
        if self.paused:
            return self.telemetry()

        vx_goal = 0.0
        if "w" in pressed and "s" not in pressed:
            vx_goal = self.drive_speed
        elif "s" in pressed and "w" not in pressed:
            vx_goal = -min(0.60, self.drive_speed)

        wz_goal = 0.0
        if "a" in pressed and "d" not in pressed:
            wz_goal = self.turn_speed
        elif "d" in pressed and "a" not in pressed:
            wz_goal = -self.turn_speed

        if "e" in pressed and "q" not in pressed:
            self.set_target_height(self.target_height + 0.08 * CONTROL_DT)
        elif "q" in pressed and "e" not in pressed:
            self.set_target_height(self.target_height - 0.08 * CONTROL_DT)

        self.env.v_cmd_target = vx_goal
        self.env.wz_cmd_target = wz_goal

        obs_np = self.env._compute_obs()
        obs_t = torch.from_numpy(obs_np).unsqueeze(0)
        if self._first_obs:
            self.actor.queue.reset(obs_t)
            with torch.inference_mode():
                act = self.actor.core.act_deterministic(obs_t, self.actor.queue.buffer.flatten(-2))[0].numpy()
            self._first_obs = False
        else:
            act = self.actor(obs_t)[0].numpy()

        _st, _rew, done, info = self.env.step(act)
        self.steps += 1
        self.peak_rim_cm = max(self.peak_rim_cm, info["ep_peak_rim_cm"])

        if self.viewer is not None:
            self.viewer.cam.lookat[0] = float(self.env.d.qpos[0]) + 0.12
            self.viewer.cam.lookat[1] = float(self.env.d.qpos[1])

        if done and info["fell_reason"] != "":
            self.resets += 1
            self.reset_standing()

        return self.telemetry()

    def telemetry(self) -> dict[str, Any]:
        R = self.env.d.xmat[self.env.base_id].reshape(3, 3)
        pitch_d = math.degrees(math.asin(float(np.clip(-R[2, 0], -1.0, 1.0))))
        roll_d = math.degrees(math.atan2(float(R[2, 1]), float(R[2, 2])))
        now = float(self.env.d.time)
        jump_active = now < self.jump_gate_until
        return {
            "scene": self.scene_name,
            "paused": self.paused,
            "active_expert": "E_jump (Pure RL 35+420->6)" if jump_active else "E0 (Frozen c874 35->6)",
            "jump_bit": 1 if jump_active else 0,
            "time_s": round(now, 3),
            "cmd_vx_m_s": round(self.env.cmd_vx, 3),
            "vx_m_s": round(self.env.body_vx, 3),
            "z_m": round(float(self.env.d.qpos[2]), 3),
            "target_height_m": round(self.target_height, 3),
            "rim_clearance_cm": round(max(0.0, self.env.last_rim_m * 100.0), 2),
            "peak_rim_cm": round(self.peak_rim_cm, 2),
            "pitch_deg": round(pitch_d, 2),
            "roll_deg": round(roll_d, 2),
            "closure_mm": round(self.env.max_closure_m * 1000.0, 3),
            "completed_jumps": self.env.ep_completed_jumps,
            "jump_triggers": self.jump_triggers,
            "resets": self.resets,
        }

    def close(self) -> None:
        if self.viewer is not None:
            try:
                self.viewer.close()
            except Exception:
                pass
            self.viewer = None


def run_headless_smoke(ckpt_path: Path, steps: int, scene: str, speed: float, out_path: Path) -> dict[str, Any]:
    sim = PureRLJumpInteractiveSim(ckpt_path=ckpt_path, scene_name=scene, visible=False)
    sim.drive_speed = float(speed)
    t0 = time.perf_counter()
    experts_seen: set[str] = set()

    try:
        for step_i in range(max(1, steps)):
            now = float(sim.env.d.time)
            pressed: set[str] = set()
            if now >= 0.80:
                pressed.add("w")
            # Trigger 2 consecutive moving pure-RL jumps (step 80 and step 200)
            if step_i in (80, 200):
                sim.trigger_rl_jump()
            tel = sim.step_keys(pressed)
            experts_seen.add(tel["active_expert"])

        final_tel = sim.telemetry()
        summary = {
            "headless_smoke_passed": bool(
                final_tel["resets"] == 0
                and final_tel["peak_rim_cm"] >= 30.0
                and final_tel["completed_jumps"] >= 2
                and len(experts_seen) == 2
                and "stage1_bc_dagger" not in sys.modules
            ),
            "checkpoint": str(ckpt_path),
            "steps_executed": sim.steps,
            "simulated_seconds": round(float(sim.env.d.time), 3),
            "wall_seconds": round(time.perf_counter() - t0, 3),
            "mjcf_sha256": EXPECTED_XML_SHA256,
            "c874_sha256": EXPECTED_C874_SHA256,
            "experts_visited": sorted(experts_seen),
            "peak_rim_cm": final_tel["peak_rim_cm"],
            "completed_jumps": final_tel["completed_jumps"],
            "resets": final_tel["resets"],
            "final_telemetry": final_tel,
        }
        save_json(out_path, summary)
        print(json.dumps(summary, indent=2, ensure_ascii=False), flush=True)
        if not summary["headless_smoke_passed"]:
            raise RuntimeError("Pure-RL headless player smoke test failed criteria!")
        return summary
    finally:
        sim.close()


def run_interactive_gui(args: argparse.Namespace, ckpt_path: Path) -> None:
    import tkinter as tk
    from pynput import keyboard

    BG = "#0d1117"
    PANEL = "#161b22"
    TEXT = "#e6edf3"
    MUTED = "#8b949e"
    CYAN = "#39d5ff"
    GREEN = "#4be38a"
    YELLOW = "#ffd166"
    ORANGE = "#ff9f43"
    RED = "#ff6b81"

    root = tk.Tk()
    sim = PureRLJumpInteractiveSim(ckpt_path=ckpt_path, scene_name=args.scene, visible=True)
    sim.drive_speed = float(args.speed)
    sim.set_target_height(float(args.height))

    class RLJumpPanel:
        def __init__(self) -> None:
            self.keys: set[str] = set()
            self.key_queue: queue.Queue[tuple[str, bool]] = queue.Queue()
            self.closed = False
            self.next_tick = time.perf_counter()
            self._build_ui()
            root.update_idletasks()
            self.listener = keyboard.Listener(on_press=self._on_global_press, on_release=self._on_global_release)
            self.listener.daemon = True
            self.listener.start()
            root.protocol("WM_DELETE_WINDOW", self.close)
            root.bind_all("<KeyPress>", lambda e: (self._key_down(e.keysym.lower()), "break")[1])
            root.bind_all("<KeyRelease>", lambda e: (self._key_up(e.keysym.lower()), "break")[1])
            root.after(25, self.tick)

        def _btn(self, parent, label: str, cmd, fg: str = TEXT, width: int | None = None):
            b = tk.Button(
                parent,
                text=label,
                command=cmd,
                bg=PANEL,
                fg=fg,
                activebackground="#21262d",
                activeforeground=fg,
                relief=tk.FLAT,
                bd=0,
                padx=10,
                pady=7,
                font=("Microsoft YaHei UI", 9, "bold"),
                cursor="hand2",
            )
            if width is not None:
                b.configure(width=width)
            return b

        def _build_ui(self) -> None:
            root.title("MOD4v3 · 纯神经网络 RL 大跳 + 移动连跳 (MoE E0=c874 + E_jump)")
            root.geometry("540x760+25+25")
            root.configure(bg=BG)

            outer = tk.Frame(root, bg=BG, padx=16, pady=12)
            outer.pack(fill="both", expand=True)

            tk.Label(
                outer,
                text="MOD4v3 · 纯 RL 蓄力大跳 + 移动连跳",
                bg=BG,
                fg=CYAN,
                font=("Microsoft YaHei UI", 15, "bold"),
                anchor="w",
            ).pack(fill="x")
            tk.Label(
                outer,
                text="Zero State-Machine | E0: Frozen c874 | E_jump: Pure Neural (35+420 -> 6)",
                bg=BG,
                fg=MUTED,
                font=("Consolas", 8),
                anchor="w",
            ).pack(fill="x", pady=(2, 8))

            sc_row = tk.Frame(outer, bg=BG)
            sc_row.pack(fill="x", pady=(0, 8))
            self._btn(sc_row, "1 纯RL平地标尺场", lambda: self.switch_scene("flat"), CYAN).pack(
                side="left", fill="x", expand=True, padx=2
            )
            self._btn(sc_row, "2 实体 16/18/20cm 连续跨栏场", lambda: self.switch_scene("hurdles"), ORANGE).pack(
                side="left", fill="x", expand=True, padx=2
            )

            tel_box = tk.Frame(outer, bg=PANEL, padx=12, pady=8)
            tel_box.pack(fill="x")
            self.vars: dict[str, tk.StringVar] = {}
            for r_i, (lbl, key, col) in enumerate(
                [
                    ("当前场景 (Scene)", "scene", CYAN),
                    ("激活专家 (Active MoE)", "expert", GREEN),
                    ("速度 指令 / 实测", "speed", TEXT),
                    ("高度 z / 目标站高", "height", YELLOW),
                    ("双轮离地净空 实时 / 峰值", "clearance", ORANGE),
                    ("姿态 Pitch / Roll", "pose", TEXT),
                    ("闭链误差 / 完成跳数 / 复位", "stats", MUTED),
                ]
            ):
                tk.Label(tel_box, text=lbl, bg=PANEL, fg=MUTED, font=("Microsoft YaHei UI", 9), anchor="w").grid(
                    row=r_i, column=0, sticky="w", pady=2
                )
                v = tk.StringVar(value="—")
                self.vars[key] = v
                tk.Label(tel_box, textvariable=v, bg=PANEL, fg=col, font=("Consolas", 10, "bold"), anchor="e").grid(
                    row=r_i, column=1, sticky="e", pady=2
                )
            tel_box.columnconfigure(0, weight=1)
            tel_box.columnconfigure(1, weight=1)

            self.speed_var = tk.DoubleVar(value=sim.drive_speed)
            self.turn_var = tk.DoubleVar(value=sim.turn_speed)
            self.height_var = tk.DoubleVar(value=sim.target_height)
            for label, var, lo, hi, res in (
                ("巡航速度 Drive Speed (m/s)", self.speed_var, 0.2, 1.3, 0.05),
                ("转向角速度 Turn Rate (rad/s)", self.turn_var, 0.3, 1.6, 0.05),
                ("目标站高 Stance Height (m)", self.height_var, 0.25, 0.38, 0.005),
            ):
                tk.Scale(
                    outer,
                    label=label,
                    variable=var,
                    from_=lo,
                    to=hi,
                    resolution=res,
                    orient=tk.HORIZONTAL,
                    takefocus=False,
                    bg=BG,
                    fg=TEXT,
                    troughcolor="#30363d",
                    activebackground=CYAN,
                    highlightthickness=0,
                    font=("Microsoft YaHei UI", 8),
                ).pack(fill="x", pady=(4, 0))

            pad = tk.Frame(outer, bg=BG)
            pad.pack(pady=8)
            for text, k, r_i, c_i in (("W", "w", 0, 1), ("A", "a", 1, 0), ("S", "s", 1, 1), ("D", "d", 1, 2)):
                btn = self._btn(pad, text, lambda: None, TEXT, width=6)
                btn.grid(row=r_i, column=c_i, padx=3, pady=2)
                btn.bind("<ButtonPress-1>", lambda _e, key=k: self._key_down(key))
                btn.bind("<ButtonRelease-1>", lambda _e, key=k: self._key_up(key))

            self._btn(outer, "SPACE / J · 触发纯神经网络 RL 大跳 (obs[30]=1)", self.trigger_jump, GREEN).pack(
                fill="x", pady=(2, 6)
            )

            ctrl_row = tk.Frame(outer, bg=BG)
            ctrl_row.pack(fill="x", pady=(0, 6))
            self._btn(ctrl_row, "P 暂停/继续", self.toggle_pause, TEXT).pack(side="left", fill="x", expand=True, padx=2)
            self._btn(ctrl_row, "X 停车", self.stop_drive, YELLOW).pack(side="left", fill="x", expand=True, padx=2)
            self._btn(ctrl_row, "R 复位", self.reset_robot, CYAN).pack(side="left", fill="x", expand=True, padx=2)
            self._btn(ctrl_row, "Esc 退出", self.close, RED).pack(side="left", fill="x", expand=True, padx=2)

            self.event_var = tk.StringVar(value="Ready — W/S 移动, Space/J 触发纯神经网络 RL 大跳!")
            tk.Label(outer, textvariable=self.event_var, bg=BG, fg=CYAN, font=("Consolas", 9, "bold"), anchor="w").pack(
                fill="x", pady=(6, 0)
            )

        def _is_foreground(self) -> bool:
            try:
                user32 = ctypes.windll.user32
                pid = ctypes.c_ulong()
                user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), ctypes.byref(pid))
                return pid.value == os.getpid()
            except Exception:
                return True

        @staticmethod
        def _decode_pynput(key) -> str | None:
            if key == keyboard.Key.esc:
                return "escape"
            if key == keyboard.Key.space:
                return "space"
            try:
                return key.char.lower() if key.char else None
            except AttributeError:
                return None

        def _on_global_press(self, key) -> bool:
            if self._is_foreground():
                ch = self._decode_pynput(key)
                if ch:
                    self.key_queue.put((ch, True))
            return True

        def _on_global_release(self, key) -> bool:
            ch = self._decode_pynput(key)
            if ch:
                self.key_queue.put((ch, False))
            return True

        def trigger_jump(self) -> None:
            sim.paused = False
            if sim.trigger_rl_jump():
                self.event_var.set(f"Pure-RL Jump #{sim.jump_triggers} -> obs[30]=1 (vx={sim.env.body_vx:+.2f} m/s)")

        def switch_scene(self, sname: str) -> None:
            self.keys.clear()
            sim._configure_scene(sname)
            self.event_var.set(f"Switched scene -> {SCENE_LABELS[sname]}")

        def toggle_pause(self) -> None:
            sim.paused = not sim.paused
            self.event_var.set("Paused" if sim.paused else "Running")

        def stop_drive(self) -> None:
            for k in ("w", "s", "a", "d"):
                self.keys.discard(k)
            sim.env.cmd_vx = 0.0
            sim.env.cmd_wz = 0.0

        def reset_robot(self) -> None:
            self.keys.clear()
            sim.reset_standing()
            self.event_var.set("Reset to standing")

        def _key_down(self, key: str) -> None:
            if key == "escape":
                self.close()
                return
            if key in self.keys:
                return
            self.keys.add(key)
            if key in ("space", "j"):
                self.trigger_jump()
            elif key in SCENE_KEYS:
                self.switch_scene(SCENE_KEYS[key])
            elif key == "r":
                self.reset_robot()
            elif key == "p":
                self.toggle_pause()
            elif key == "x":
                self.stop_drive()
            elif key in ("w", "s", "a", "d"):
                sim.paused = False

        def _key_up(self, key: str) -> None:
            self.keys.discard(key)

        def tick(self) -> None:
            if self.closed:
                return
            if sim.viewer is not None and not sim.viewer.is_running():
                self.close()
                return
            while True:
                try:
                    k, down = self.key_queue.get_nowait()
                except queue.Empty:
                    break
                if down:
                    self._key_down(k)
                else:
                    self._key_up(k)

            if not self._is_foreground():
                for mk in ("w", "s", "a", "d", "q", "e"):
                    self.keys.discard(mk)

            sim.drive_speed = float(self.speed_var.get())
            sim.turn_speed = float(self.turn_var.get())
            if "q" not in self.keys and "e" not in self.keys:
                sim.set_target_height(float(self.height_var.get()))

            tel = sim.step_keys(self.keys)
            if sim.viewer is not None:
                sim.viewer.sync()

            self.vars["scene"].set(SCENE_LABELS.get(tel["scene"], tel["scene"]))
            self.vars["expert"].set(tel["active_expert"])
            self.vars["speed"].set(f"{tel['cmd_vx_m_s']:+.2f} / {tel['vx_m_s']:+.2f} m/s")
            self.vars["height"].set(f"{tel['z_m']:.3f} / {tel['target_height_m']:.3f} m")
            self.vars["clearance"].set(f"{tel['rim_clearance_cm']:5.1f} / {tel['peak_rim_cm']:5.1f} cm")
            self.vars["pose"].set(f"P {tel['pitch_deg']:+5.1f}°  R {tel['roll_deg']:+5.1f}°")
            self.vars["stats"].set(
                f"{tel['closure_mm']:.2f} mm  |  Jumps {tel['completed_jumps']}  |  Resets {tel['resets']}"
            )

            self.next_tick += CONTROL_DT
            now_p = time.perf_counter()
            if self.next_tick < now_p - 0.12:
                self.next_tick = now_p
            root.after(max(1, int((self.next_tick - now_p) * 1000)), self.tick)

        def close(self) -> None:
            if self.closed:
                return
            self.closed = True
            try:
                self.listener.stop()
            except Exception:
                pass
            sim.close()
            try:
                root.destroy()
            except Exception:
                pass

    RLJumpPanel()
    root.mainloop()


def main() -> None:
    p = argparse.ArgumentParser(description="MOD4v3 Pure-RL High Jump & Moving Jump WASD Playground")
    p.add_argument("--ckpt", type=Path, default=HERE / "weights/model_rl_best.pt")
    p.add_argument("--scene", choices=["flat", "hurdles"], default="flat")
    p.add_argument("--speed", type=float, default=0.85)
    p.add_argument("--height", type=float, default=0.28)
    p.add_argument("--headless", action="store_true")
    p.add_argument("--steps", type=int, default=360)
    p.add_argument("--output", type=Path, default=HERE / "evidence/rl_player_headless_smoke.json")
    args = p.parse_args()

    if args.headless:
        run_headless_smoke(args.ckpt, args.steps, args.scene, args.speed, args.output)
    else:
        run_interactive_gui(args, args.ckpt)


if __name__ == "__main__":
    main()
