# SPDX-License-Identifier: MIT
"""Interactive MuJoCo WASD + Deep-Crouch High Jump & Moving Jump Playground (MOD4v3 + c874).

Controls (in Control Panel window):
  W / S          Forward / Backward drive (c874 locomotion)
  A / D          Turn Left / Right
  Q / E          Lower / Raise target stance height (0.22 - 0.42 m)
  Space or J     1-Key Auto Deep-Crouch + High Jump (works standing & moving!)
  C (Hold/Rel)   Manual Hold-Crouch Charge -> Release to Launch High Jump!
  1 / 2 / 3      Switch Terrain Scene:
                   1 = Flat Benchmark Arena
                   2 = Multi-Hurdle Jump Course (14 / 20 / 25 cm hurdles)
                   3 = Stepped Platform Course (18 / 34 cm platforms)
  R              Reset robot to standing
  X              Zero linear/yaw velocity commands
  P              Pause / Resume simulation
  Esc            Exit cleanly

Headless smoke test (no GUI windows opened):
  python play_high_jump_wasd.py --headless --steps 600
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
from pathlib import Path
import queue
import time
from typing import Any

import mujoco

from high_jump_controller import (
    CONTROL_DT,
    EXPECTED_CKPT_SHA256,
    EXPECTED_XML_SHA256,
    HERE,
    HighJumpConfig,
    HighJumpSimulation,
)

SCENE_KEYS = {"1": "flat", "2": "hurdles", "3": "platforms"}
SCENE_LABELS = {
    "flat": "1 · Flat Benchmark Arena (平地大跳标尺场)",
    "hurdles": "2 · Multi-Hurdle Course (14/20/25cm 连续跨栏场)",
    "platforms": "3 · Platform Jump Course (18/34cm 台阶高台场)",
}


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_headless_smoke(steps: int, scene: str, speed: float, out_path: Path | None) -> dict[str, Any]:
    """Non-blocking headless verification of WASD driving, 1-key moving jump, hold-charge jump, and resets."""
    sim = HighJumpSimulation(scene_name=scene, visible=False)
    sim.drive_speed = float(speed)
    t0 = time.perf_counter()
    max_rim_cm = 0.0
    phases_seen: set[str] = set()

    try:
        for step_idx in range(max(1, steps)):
            now = float(sim.env.d.time)
            pressed: set[str] = set()
            # 0.0 - 1.2s: stand up smoothly
            # 1.2 - 3.6s: drive forward ('w') + trigger 1-key moving jump at step 90 (t=1.80s)
            if 1.20 <= now < 4.20:
                pressed.add("w")
            if step_idx == 90:
                sim.controller.request_jump(now, hold_charge=False)
            # Test Hold-Crouch ('c') at step 220 (t=4.40s) -> release at step 252 (t=5.04s) while moving!
            if 220 <= step_idx < 252:
                pressed.add("w")
                if step_idx == 220:
                    sim.controller.request_jump(now, hold_charge=True)
            elif step_idx == 252:
                pressed.add("w")
                sim.controller.release_charge(now)
            elif step_idx > 252:
                pressed.add("w")

            tel = sim.step_keys(pressed)
            phases_seen.add(tel["phase"])
            max_rim_cm = max(max_rim_cm, float(tel["world_rim_cm"]))

        final_tel = sim.telemetry()
        summary = {
            "headless_smoke_passed": bool(
                final_tel["resets"] == 0
                and max_rim_cm >= 30.0
                and {"DRIVE", "CROUCH", "PUSH", "FLIGHT_TUCK", "LANDING_EXTEND", "SKYHOOK_ABSORB"} <= phases_seen
            ),
            "steps_executed": sim.steps,
            "simulated_seconds": round(float(sim.env.d.time), 3),
            "wall_seconds": round(time.perf_counter() - t0, 3),
            "scene": scene,
            "mjcf_sha256": EXPECTED_XML_SHA256,
            "c874_sha256": EXPECTED_CKPT_SHA256,
            "phases_visited": sorted(phases_seen),
            "peak_world_rim_clearance_cm": round(max_rim_cm, 2),
            "completed_jumps": sim.controller.completed_jumps,
            "max_closure_mm": final_tel["max_closure_mm"],
            "resets": final_tel["resets"],
            "final_telemetry": final_tel,
        }
        if out_path is not None:
            save_json(out_path, summary)
        print(json.dumps(summary, indent=2, ensure_ascii=False), flush=True)
        if not summary["headless_smoke_passed"]:
            raise RuntimeError("Headless smoke test did not meet all pass criteria!")
        return summary
    finally:
        sim.close()


def run_interactive_gui(args: argparse.Namespace) -> None:
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

    runtime_dir = args.output or (HERE / "runtime_logs" / time.strftime("play_%Y%m%d_%H%M%S"))
    runtime_dir.mkdir(parents=True, exist_ok=True)

    root = tk.Tk()
    sim = HighJumpSimulation(scene_name=args.scene, visible=True)
    sim.drive_speed = float(args.speed)
    sim.set_target_height(float(args.height))

    class HighJumpControlPanel:
        def __init__(self) -> None:
            self.keys: set[str] = set()
            self.key_queue: queue.Queue[tuple[str, bool]] = queue.Queue()
            self.closed = False
            self.last_event = "Ready — press W/S to drive, Space/J to High Jump, Hold C to Charge!"
            self.next_tick = time.perf_counter()
            self.last_status_write = 0.0
            self._build_ui()
            root.update_idletasks()
            self.hwnd = int(root.winfo_id())

            self.listener = keyboard.Listener(on_press=self._on_global_press, on_release=self._on_global_release)
            self.listener.daemon = True
            self.listener.start()

            root.protocol("WM_DELETE_WINDOW", self.close)
            root.bind_all("<KeyPress>", self._tk_key_down)
            root.bind_all("<KeyRelease>", self._tk_key_up)
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
            root.title("MOD4v3 · 压低姿态蓄力大跳 + 边移动边跳 (c874)")
            root.geometry("535x820+25+25")
            root.minsize(500, 770)
            root.configure(bg=BG)

            outer = tk.Frame(root, bg=BG, padx=16, pady=12)
            outer.pack(fill="both", expand=True)

            tk.Label(
                outer,
                text="MOD4v3 · 蓄力大跳 + 移动连跳",
                bg=BG,
                fg=CYAN,
                font=("Microsoft YaHei UI", 16, "bold"),
                anchor="w",
            ).pack(fill="x")
            tk.Label(
                outer,
                text="Base: c874a1af (Low-Pitch PPO) | Plant: HW300N60_R3 (400Hz / 40Nm + 2000N/m Gas Spring)",
                bg=BG,
                fg=MUTED,
                font=("Consolas", 8),
                anchor="w",
            ).pack(fill="x", pady=(2, 8))

            # Scene selector buttons (1 / 2 / 3)
            scene_frame = tk.Frame(outer, bg=BG)
            scene_frame.pack(fill="x", pady=(0, 8))
            for k, sname in SCENE_KEYS.items():
                short = {"flat": "1 平地标尺", "hurdles": "2 连续跨栏", "platforms": "3 高台地形"}[sname]
                self._btn(scene_frame, short, lambda s=sname: self.switch_scene(s), CYAN).pack(
                    side="left", fill="x", expand=True, padx=2
                )

            # Live telemetry panel
            tel_box = tk.Frame(outer, bg=PANEL, padx=12, pady=8)
            tel_box.pack(fill="x")
            self.vars: dict[str, tk.StringVar] = {}
            rows = [
                ("当前场景 (Scene)", "scene", CYAN),
                ("状态阶段 (Jump Phase)", "phase", GREEN),
                ("前进速度 指令 / 实测", "speed", TEXT),
                ("机身高度 z / 目标站高", "height", YELLOW),
                ("双轮离地净空 实时 / 本跳峰值", "clearance", ORANGE),
                ("姿态角 Pitch / Roll", "pose", TEXT),
                ("闭链误差 / 累计跳跃 / 复位", "stats", MUTED),
            ]
            for r_i, (lbl, key, col) in enumerate(rows):
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

            # Speed & Height sliders
            self.speed_var = tk.DoubleVar(value=sim.drive_speed)
            self.turn_var = tk.DoubleVar(value=sim.turn_speed)
            self.height_var = tk.DoubleVar(value=sim.target_height)
            for label, var, lo, hi, res in (
                ("巡航速度 Drive Speed (m/s)", self.speed_var, 0.2, 1.4, 0.05),
                ("转向角速度 Turn Rate (rad/s)", self.turn_var, 0.3, 1.8, 0.05),
                ("目标站立高度 Stance Height (m)", self.height_var, 0.22, 0.42, 0.005),
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

            # WASD + Jump Pad
            pad = tk.Frame(outer, bg=BG)
            pad.pack(pady=8)
            for text, k, r_i, c_i in (("W", "w", 0, 1), ("A", "a", 1, 0), ("S", "s", 1, 1), ("D", "d", 1, 2)):
                btn = self._btn(pad, text, lambda: None, TEXT, width=6)
                btn.grid(row=r_i, column=c_i, padx=3, pady=2)
                btn.bind("<ButtonPress-1>", lambda _e, key=k: self._key_down(key))
                btn.bind("<ButtonRelease-1>", lambda _e, key=k: self._key_up(key))
                btn.bind("<Leave>", lambda _e, key=k: self._key_up(key))

            jump_row = tk.Frame(outer, bg=BG)
            jump_row.pack(fill="x", pady=(2, 6))
            self._btn(jump_row, "SPACE / J · 一键深蹲蓄力大跳", self.trigger_auto_jump, GREEN).pack(
                side="left", fill="x", expand=True, padx=(0, 4)
            )
            charge_btn = self._btn(jump_row, "按住 C 压低蓄力 · 松开起跳", lambda: None, ORANGE)
            charge_btn.pack(side="left", fill="x", expand=True, padx=(4, 0))
            charge_btn.bind("<ButtonPress-1>", lambda _e: self._key_down("c"))
            charge_btn.bind("<ButtonRelease-1>", lambda _e: self._key_up("c"))

            ctrl_row = tk.Frame(outer, bg=BG)
            ctrl_row.pack(fill="x", pady=(0, 6))
            self._btn(ctrl_row, "P 暂停/继续", self.toggle_pause, TEXT).pack(side="left", fill="x", expand=True, padx=2)
            self._btn(ctrl_row, "X 停车指令", self.stop_drive, YELLOW).pack(side="left", fill="x", expand=True, padx=2)
            self._btn(ctrl_row, "R 复位站立", self.reset_robot, CYAN).pack(side="left", fill="x", expand=True, padx=2)
            self._btn(ctrl_row, "Esc 退出", self.close, RED).pack(side="left", fill="x", expand=True, padx=2)

            help_lbl = tk.Label(
                outer,
                text=(
                    "快捷键：W/S 前进后退 | A/D 转向 | Q/E 升降站高 | Space/J 一键蓄力大跳 (支持原地&移动连跳)\n"
                    "        按住 C 保持深蹲移动瞄准，松开 C 瞬间爆发蹬伸！ | 1/2/3 切换地形 | R 复位 | P 暂停"
                ),
                bg=PANEL,
                fg=MUTED,
                justify="left",
                anchor="w",
                padx=10,
                pady=8,
                font=("Microsoft YaHei UI", 8),
            )
            help_lbl.pack(fill="x")

            self.event_var = tk.StringVar(value=self.last_event)
            tk.Label(
                outer, textvariable=self.event_var, bg=BG, fg=CYAN, font=("Consolas", 9, "bold"), anchor="w"
            ).pack(fill="x", pady=(6, 0))

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

        def _tk_key_down(self, event):
            self._key_down(event.keysym.lower())
            return "break"

        def _tk_key_up(self, event):
            self._key_up(event.keysym.lower())
            return "break"

        def _set_event(self, msg: str) -> None:
            self.last_event = msg
            self.event_var.set(msg)

        def trigger_auto_jump(self) -> None:
            sim.paused = False
            if sim.controller.request_jump(float(sim.env.d.time), hold_charge=False):
                self._set_event(f"Jump #{sim.controller.jump_requests} triggered (v={sim.env.vx:+.2f} m/s)")

        def switch_scene(self, scene_name: str) -> None:
            nonlocal sim
            self.keys.clear()
            spd, trn, hgt = self.speed_var.get(), self.turn_var.get(), self.height_var.get()
            sim.close()
            sim = HighJumpSimulation(scene_name=scene_name, visible=True)
            sim.drive_speed = spd
            sim.turn_speed = trn
            sim.set_target_height(hgt)
            self._set_event(f"Switched scene -> {SCENE_LABELS[scene_name]}")
            root.lift()
            root.focus_force()

        def toggle_pause(self) -> None:
            sim.paused = not sim.paused
            self._set_event("Paused" if sim.paused else "Running")

        def stop_drive(self) -> None:
            for k in ("w", "s", "a", "d"):
                self.keys.discard(k)
            sim.cmd_vx = 0.0
            sim.cmd_wz = 0.0
            self._set_event("Velocity commands zeroed")

        def reset_robot(self) -> None:
            self.keys.clear()
            sim.reset_standing()
            self._set_event("Reset to standing")

        def _key_down(self, key: str) -> None:
            if key == "escape":
                self.close()
                return
            if key in self.keys:
                return
            self.keys.add(key)
            if key in ("space", "j"):
                self.trigger_auto_jump()
            elif key == "c":
                sim.paused = False
                if sim.controller.request_jump(float(sim.env.d.time), hold_charge=True):
                    self._set_event("Hold-Crouch Charging... release C to launch!")
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
            if key == "c":
                if sim.controller.release_charge(float(sim.env.d.time)):
                    self._set_event(f"Released charge -> PUSH! (v={sim.env.vx:+.2f} m/s)")

        def _refresh_ui(self, tel: dict[str, Any]) -> None:
            self.vars["scene"].set(SCENE_LABELS.get(tel["scene"], tel["scene"]))
            ph_txt = tel["phase"] + (" [HOLD CHARGE]" if tel["hold_charge"] else "")
            if tel["paused"]:
                ph_txt = "PAUSED"
            self.vars["phase"].set(ph_txt)
            self.vars["speed"].set(f"{tel['cmd_vx_m_s']:+.2f} / {tel['vx_m_s']:+.2f} m/s")
            self.vars["height"].set(f"{tel['z_m']:.3f} / {tel['target_height_m']:.3f} m")
            self.vars["clearance"].set(f"{tel['rim_clearance_cm']:5.1f} / {tel['peak_rim_cm']:5.1f} cm")
            self.vars["pose"].set(f"P {tel['pitch_deg']:+5.1f}°  R {tel['roll_deg']:+5.1f}°")
            self.vars["stats"].set(
                f"{tel['closure_mm']:.2f} mm  |  Jumps {tel['completed_jumps']}  |  Resets {tel['resets']}"
            )
            if abs(self.height_var.get() - sim.target_height) > 1e-4:
                self.height_var.set(sim.target_height)

            if time.monotonic() - self.last_status_write > 0.25:
                save_json(runtime_dir / "PLAYER_STATUS.json", tel)
                self.last_status_write = time.monotonic()

        def tick(self) -> None:
            if self.closed:
                return
            if sim.viewer is not None and not sim.viewer.is_running():
                self.close()
                return
            while True:
                try:
                    k, is_down = self.key_queue.get_nowait()
                except queue.Empty:
                    break
                if is_down:
                    self._key_down(k)
                else:
                    self._key_up(k)

            if not self._is_foreground():
                for move_k in ("w", "s", "a", "d", "q", "e"):
                    self.keys.discard(move_k)

            sim.drive_speed = float(self.speed_var.get())
            sim.turn_speed = float(self.turn_var.get())
            if "q" not in self.keys and "e" not in self.keys:
                sim.set_target_height(float(self.height_var.get()))

            tel = sim.step_keys(self.keys)
            if sim.viewer is not None:
                sim.viewer.sync()
            self._refresh_ui(tel)

            self.next_tick += CONTROL_DT
            now_p = time.perf_counter()
            if self.next_tick < now_p - 0.12:
                self.next_tick = now_p
            delay_ms = max(1, int((self.next_tick - now_p) * 1000))
            root.after(delay_ms, self.tick)

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

    panel = HighJumpControlPanel()
    root.after(180, lambda: (root.lift(), root.focus_force()))
    save_json(
        runtime_dir / "READY.json",
        {
            "epoch": time.time(),
            "pid": os.getpid(),
            "scene": args.scene,
            "mjcf_sha256": EXPECTED_XML_SHA256,
            "c874_sha256": EXPECTED_CKPT_SHA256,
            "viewer_running": bool(sim.viewer and sim.viewer.is_running()),
        },
    )
    root.mainloop()


def main() -> None:
    p = argparse.ArgumentParser(description="MOD4v3 WASD + Deep-Crouch High Jump & Moving Jump Player")
    p.add_argument("--scene", choices=["flat", "hurdles", "platforms"], default="flat")
    p.add_argument("--speed", type=float, default=0.80, help="Default WASD drive speed (m/s)")
    p.add_argument("--height", type=float, default=0.365, help="Default target stance height (m)")
    p.add_argument("--headless", action="store_true", help="Run non-blocking headless smoke verification")
    p.add_argument("--steps", type=int, default=400, help="Steps for --headless mode (50Hz, 20ms/step)")
    p.add_argument("--output", type=Path, default=None, help="Optional JSON output path / runtime dir")
    args = p.parse_args()

    if args.headless:
        out_file = args.output or (HERE / "evidence" / "headless_player_smoke.json")
        run_headless_smoke(args.steps, args.scene, args.speed, out_file)
    else:
        run_interactive_gui(args)


if __name__ == "__main__":
    main()
