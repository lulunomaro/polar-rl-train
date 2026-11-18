# SPDX-License-Identifier: MIT
"""Interactive Pure-RL WASD + COD Forward Leap & Jump-Onto-Step Playground (MOD4v3).

Runs weights/model_rl_forward_leap_best.pt via StatefulMoEForwardLeapActor (obs_35 -> act_6):
  - ZERO hand-coded state machine, ZERO external timers, ZERO privileged world-z / step inputs!
  - Pressing Space or J sets standard mode bit obs[30] = 1.0 for 1.60s, executing a pure-neural
    forward lunge leap (from standstill OR while moving) directly across ground or onto 20/24/40cm steps!

Controls:
  W / S          Forward / Backward drive (E0 = c874)
  A / D          Turn Left / Right
  Q / E          Lower / Raise stance height (0.25 - 0.38 m)
  Space or J     Trigger Pure-RL COD Forward Leap / Jump-Onto-Step (obs[30] = 1)
  1 / 2 / 3 / 4  Switch Terrain Scene:
                   1 = Flat COD Forward-Leap Arena (平地前向跳扑标尺场)
                   2 = 20 cm High Step Platform (20cm 实体高台直跳场)
                   3 = 24 cm High Step Platform (24cm 实体高台直跳场)
                   4 = Continuous 2-Step 20cm+40cm Platforms (20+40cm 连续双高台场)
  R              Reset robot
  X              Zero velocity commands
  P              Pause / Resume
  Esc            Exit cleanly
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

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import mujoco
import mujoco.viewer
import numpy as np
import torch

from forward_leap_env import (
    CONTROL_DT,
    EXPECTED_XML_SHA256,
    JUMP_GATE_DURATION_S,
    Mod4v3ForwardLeapEnv,
)
from moe_forward_leap_model import (
    EXPECTED_C874_SHA256,
    HERE,
    MoEForwardLeapActorCritic,
    StatefulMoEForwardLeapActor,
)

SCENE_KEYS = {"1": "flat", "2": "step20", "3": "step24", "4": "twostep"}
SCENE_LABELS = {
    "flat": "1 · Flat Forward-Leap Arena (平地前向跳扑场)",
    "step20": "2 · 20cm High Step (20cm 高台直跳场)",
    "step24": "3 · 24cm High Step (24cm 高台直跳场)",
    "twostep": "4 · 20cm + 40cm 2-Step Platforms (双级高台连跳场)",
}


def scene_steps(scene_name: str) -> list[tuple[float, float, float]]:
    if scene_name == "step20":
        return [(Mod4v3ForwardLeapEnv.step_front_for_stand_jump(0.20), 3.60, 0.20)]
    if scene_name == "step24":
        return [(Mod4v3ForwardLeapEnv.step_front_for_stand_jump(0.24), 3.60, 0.24)]
    if scene_name == "twostep":
        return [(0.745, 2.15, 0.20), (2.18, 2.50, 0.40)]
    return []


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class PureRLForwardLeapSim:
    def __init__(self, ckpt_path: Path, scene_name: str = "step20", visible: bool = True):
        if "stage1_forward_leap_dagger" in sys.modules:
            raise RuntimeError("Forbidden teacher module loaded in pure-RL playground!")
        self.ckpt_path = ckpt_path
        self.model = MoEForwardLeapActorCritic.load_from_checkpoint(ckpt_path, device="cpu")
        self.actor = StatefulMoEForwardLeapActor(self.model)

        self.scene_name = scene_name
        self.env = Mod4v3ForwardLeapEnv(seed=2026)
        self.drive_speed = 0.80
        self.turn_speed = 1.00
        self.target_height = 0.28
        self.paused = False
        self.steps = 0
        self.resets = 0
        self.jump_triggers = 0
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
            self.viewer.cam.azimuth = 102.0
            self.viewer.cam.elevation = -14.0
            self.viewer.cam.distance = 2.80
            self.viewer.cam.lookat[:] = [0.4, 0.0, 0.34]

    def _configure_scene(self, scene_name: str) -> None:
        self.scene_name = scene_name
        self.env.reset(
            dr_scale=0.0,
            v_cmd=0.0,
            wz_cmd=0.0,
            h_nom=self.target_height,
            jump_times=(),
            max_episode_s=1e6,
            steps=scene_steps(scene_name),
        )
        self.jump_gate_until = -99.0
        self._first_obs = True
        self.actor.reset_history()

    def reset_standing(self) -> None:
        self._configure_scene(self.scene_name)

    def set_target_height(self, h: float) -> None:
        self.target_height = float(np.clip(h, 0.25, 0.38))
        self.env.h_nom = self.target_height

    def trigger_forward_leap(self) -> bool:
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

        # Allow normal E0 reverse driving when not jumping; during jump v_cmd_pre >= 0
        now = float(self.env.d.time)
        if now < self.jump_gate_until:
            self.env.v_cmd_pre = max(0.0, vx_goal)
            self.env.v_cmd_post = max(0.0, vx_goal)
        else:
            self.env.v_cmd_pre = vx_goal
            self.env.v_cmd_post = vx_goal
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

        if self.viewer is not None:
            self.viewer.cam.lookat[0] = float(self.env.d.qpos[0]) + 0.25
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
        wx_now = float(self.env.d.xpos[self.env.wheels, 0].mean())
        return {
            "scene": self.scene_name,
            "paused": self.paused,
            "active_expert": "E_jump (Pure RL Forward Leap)" if jump_active else "E0 (Frozen c874)",
            "time_s": round(now, 3),
            "wheel_x_m": round(wx_now, 3),
            "mean_leap_dx_m": round(float(np.mean(self.env.ep_leap_dxs)), 3) if self.env.ep_leap_dxs else 0.0,
            "cmd_vx_m_s": round(self.env.cmd_vx, 3),
            "vx_m_s": round(self.env.body_vx, 3),
            "world_rim_cm": round(max(0.0, self.env.last_world_rim_m * 100.0), 2),
            "peak_world_rim_cm": round(self.env.ep_peak_world_rim_m * 100.0, 2),
            "steps_mounted": f"{sum(1 for b in self.env.step_both_on if b)}/{len(self.env.active_steps)}",
            "pitch_deg": round(pitch_d, 2),
            "max_air_pitch_deg": round(self.env.ep_max_air_pitch_deg, 2),
            "max_episode_pitch_deg": round(self.env.ep_max_episode_pitch_deg, 2),
            "roll_deg": round(roll_d, 2),
            "closure_mm": round(self.env.max_closure_m * 1000.0, 3),
            "completed_leaps": self.env.ep_completed_leaps,
            "resets": self.resets,
        }

    def close(self) -> None:
        if self.viewer is not None:
            try:
                self.viewer.close()
            except Exception:
                pass
            self.viewer = None


def run_headless_smoke(ckpt_path: Path, steps: int, scene: str, out_path: Path) -> dict[str, Any]:
    sim = PureRLForwardLeapSim(ckpt_path=ckpt_path, scene_name=scene, visible=False)
    t0 = time.perf_counter()
    experts_seen: set[str] = set()

    try:
        for step_i in range(max(1, steps)):
            pressed: set[str] = set()
            # Trigger stand-to-step forward leap at t=1.0s (step 50) with v_cmd=0, then park on step top!
            if step_i == 50:
                sim.trigger_forward_leap()
            tel = sim.step_keys(pressed)
            experts_seen.add(tel["active_expert"])

        final_tel = sim.telemetry()
        step_ok = final_tel["steps_mounted"] == "1/1" if scene in ("step20", "step24") else True
        summary = {
            "headless_smoke_passed": bool(
                final_tel["resets"] == 0
                and step_ok
                and final_tel["mean_leap_dx_m"] >= 0.55
                and final_tel["peak_world_rim_cm"] >= 30.0
                and final_tel["max_air_pitch_deg"] <= 10.0
                and final_tel["max_episode_pitch_deg"] <= 13.0
                and len(experts_seen) == 2
                and "stage1_forward_leap_dagger" not in sys.modules
            ),
            "checkpoint": str(ckpt_path),
            "scene": scene,
            "steps_executed": sim.steps,
            "wall_seconds": round(time.perf_counter() - t0, 3),
            "mjcf_sha256": EXPECTED_XML_SHA256,
            "c874_sha256": EXPECTED_C874_SHA256,
            "experts_visited": sorted(experts_seen),
            "final_telemetry": final_tel,
        }
        save_json(out_path, summary)
        print(json.dumps(summary, indent=2, ensure_ascii=False), flush=True)
        if not summary["headless_smoke_passed"]:
            raise RuntimeError("Pure-RL Forward-Leap headless smoke test failed!")
        return summary
    finally:
        sim.close()


def run_interactive_gui(args: argparse.Namespace, ckpt_path: Path) -> None:
    import tkinter as tk
    from pynput import keyboard

    BG, PANEL, TEXT, MUTED = "#0d1117", "#161b22", "#e6edf3", "#8b949e"
    CYAN, GREEN, YELLOW, ORANGE, RED = "#39d5ff", "#4be38a", "#ffd166", "#ff9f43", "#ff6b81"

    root = tk.Tk()
    sim = PureRLForwardLeapSim(ckpt_path=ckpt_path, scene_name=args.scene, visible=True)
    sim.drive_speed = float(args.speed)

    class ForwardLeapPanel:
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
                padx=8,
                pady=7,
                font=("Microsoft YaHei UI", 9, "bold"),
                cursor="hand2",
            )
            if width is not None:
                b.configure(width=width)
            return b

        def _build_ui(self) -> None:
            root.title("MOD4v3 · 纯RL COD前向跳扑 + 直接跳上高台 (20/24/40cm)")
            root.geometry("560x760+25+25")
            root.configure(bg=BG)

            outer = tk.Frame(root, bg=BG, padx=16, pady=12)
            outer.pack(fill="both", expand=True)

            tk.Label(
                outer,
                text="MOD4v3 · 纯RL前向跳扑 + 跳上高台",
                bg=BG,
                fg=CYAN,
                font=("Microsoft YaHei UI", 15, "bold"),
                anchor="w",
            ).pack(fill="x")
            tk.Label(
                outer,
                text="Zero State-Machine | E0: Frozen c874 | E_jump: Pure Forward Leap & Step Vault",
                bg=BG,
                fg=MUTED,
                font=("Consolas", 8),
                anchor="w",
            ).pack(fill="x", pady=(2, 8))

            sc_row = tk.Frame(outer, bg=BG)
            sc_row.pack(fill="x", pady=(0, 8))
            for k, lbl, col in (
                ("flat", "1 平地跳扑", CYAN),
                ("step20", "2 20cm高台", GREEN),
                ("step24", "3 24cm高台", ORANGE),
                ("twostep", "4 双级高台", YELLOW),
            ):
                self._btn(sc_row, lbl, lambda s=k: self.switch_scene(s), col).pack(
                    side="left", fill="x", expand=True, padx=2
                )

            tel_box = tk.Frame(outer, bg=PANEL, padx=12, pady=8)
            tel_box.pack(fill="x")
            self.vars: dict[str, tk.StringVar] = {}
            for r_i, (lbl, key, col) in enumerate(
                [
                    ("当前场景 (Scene)", "scene", CYAN),
                    ("激活专家 (Active MoE)", "expert", GREEN),
                    ("前跃位移 Wheel X / 单跳 dx", "dx", YELLOW),
                    ("速度 指令 / 实测", "speed", TEXT),
                    ("轮底世界高度 实时 / 峰值", "rim", ORANGE),
                    ("上台状态 / 姿态角", "step_pose", TEXT),
                    ("闭链误差 / 完成跳扑 / 复位", "stats", MUTED),
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
            tk.Scale(
                outer,
                label="助跑速度 Approach Speed (m/s)",
                variable=self.speed_var,
                from_=0.2,
                to=1.2,
                resolution=0.05,
                orient=tk.HORIZONTAL,
                takefocus=False,
                bg=BG,
                fg=TEXT,
                troughcolor="#30363d",
                activebackground=CYAN,
                highlightthickness=0,
                font=("Microsoft YaHei UI", 8),
            ).pack(fill="x", pady=(6, 6))

            self._btn(outer, "SPACE / J · 触发 COD 式前向跳扑 / 直接跳上高台", self.trigger_leap, GREEN).pack(
                fill="x", pady=(4, 6)
            )

            ctrl_row = tk.Frame(outer, bg=BG)
            ctrl_row.pack(fill="x", pady=(0, 6))
            self._btn(ctrl_row, "P 暂停/继续", self.toggle_pause, TEXT).pack(side="left", fill="x", expand=True, padx=2)
            self._btn(ctrl_row, "R 复位", self.reset_robot, CYAN).pack(side="left", fill="x", expand=True, padx=2)
            self._btn(ctrl_row, "Esc 退出", self.close, RED).pack(side="left", fill="x", expand=True, padx=2)

            self.event_var = tk.StringVar(value="Ready — 原地或按 W 助跑时按 Space/J 执行纯RL前向跳扑上台！")
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

        def trigger_leap(self) -> None:
            sim.paused = False
            if sim.trigger_forward_leap():
                self.event_var.set(f"Forward Leap #{sim.jump_triggers} triggered! (vx={sim.env.body_vx:+.2f} m/s)")

        def switch_scene(self, sname: str) -> None:
            self.keys.clear()
            sim._configure_scene(sname)
            self.event_var.set(f"Scene -> {SCENE_LABELS[sname]}")

        def toggle_pause(self) -> None:
            sim.paused = not sim.paused

        def reset_robot(self) -> None:
            self.keys.clear()
            sim.reset_standing()

        def _key_down(self, key: str) -> None:
            if key == "escape":
                self.close()
                return
            if key in self.keys:
                return
            self.keys.add(key)
            if key in ("space", "j"):
                self.trigger_leap()
            elif key in SCENE_KEYS:
                self.switch_scene(SCENE_KEYS[key])
            elif key == "r":
                self.reset_robot()
            elif key == "p":
                self.toggle_pause()
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
            tel = sim.step_keys(self.keys)
            if sim.viewer is not None:
                sim.viewer.sync()

            self.vars["scene"].set(SCENE_LABELS.get(tel["scene"], tel["scene"]))
            self.vars["expert"].set(tel["active_expert"])
            self.vars["dx"].set(f"X={tel['wheel_x_m']:+.2f} m  |  Leap dx={tel['mean_leap_dx_m']:+.2f} m")
            self.vars["speed"].set(f"{tel['cmd_vx_m_s']:+.2f} / {tel['vx_m_s']:+.2f} m/s")
            self.vars["rim"].set(f"{tel['world_rim_cm']:5.1f} / {tel['peak_world_rim_cm']:5.1f} cm")
            self.vars["step_pose"].set(
                f"Steps {tel['steps_mounted']} | P {tel['pitch_deg']:+4.1f}° (Air {tel['max_air_pitch_deg']:.1f}°/Ep {tel['max_episode_pitch_deg']:.1f}°)"
            )
            self.vars["stats"].set(f"{tel['closure_mm']:.2f} mm  |  Leaps {tel['completed_leaps']}  |  Resets {tel['resets']}")

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

    ForwardLeapPanel()
    root.mainloop()


def main() -> None:
    p = argparse.ArgumentParser(description="MOD4v3 Pure-RL Forward Leap & Jump-Onto-Step Playground")
    p.add_argument("--ckpt", type=Path, default=HERE / "weights/model_rl_forward_leap_best.pt")
    p.add_argument("--scene", choices=["flat", "step20", "step24", "twostep"], default="step20")
    p.add_argument("--speed", type=float, default=0.80)
    p.add_argument("--headless", action="store_true")
    p.add_argument("--steps", type=int, default=240)
    p.add_argument("--output", type=Path, default=HERE / "evidence/rl_forward_leap_player_smoke.json")
    args = p.parse_args()

    if args.headless:
        run_headless_smoke(args.ckpt, args.steps, args.scene, args.output)
    else:
        run_interactive_gui(args, args.ckpt)


if __name__ == "__main__":
    main()
