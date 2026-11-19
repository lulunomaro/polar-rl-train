# SPDX-License-Identifier: MIT
"""MOD4v3 autonomous three-expert MuJoCo and WASD player."""
from __future__ import annotations

import json
import math
import os
import time
import tkinter as tk
from tkinter import ttk
import traceback

from autonomous_three_expert import HERE, load
from all_maps_runtime import (
    CONTROL_DT, HEIGHT_MAX, HEIGHT_MIN, MOTION_KEYS, SERIAL_SUB_SCENES,
    STAIR_SCENES, AutonomousMapSimulation, map_for, maps,
)
from play_unified_moe_all_maps import AllMapsPlayerApp, VK_MAP

STATUS_PATH = HERE / "PLAYER_STATUS.json"
ERROR_PATH = HERE / "PLAYER_ERROR.txt"
SUITE_LABELS = (
    "综合试炼场 · 单阶 / 双阶 / 高台", "RMUC2027 · 全赛场", "Sirina · 跑酷场",
    "Serial_Leg · 坡道与台阶", "单阶与高台专项", "Rough-v1 · 崎岖地形",
)


class AutonomousPlayer(AllMapsPlayerApp):
    def _build_ui(self) -> None:
        root = self.root
        root.title(f"MOD4v3 自动 MoE · 全地图 WASD 控制台 · {self.sim.ckpt_sha[:8]}")
        root.geometry("546x652+18+25")
        root.minsize(510, 634)
        root.configure(bg=self.BG)
        panel = tk.Frame(root, bg=self.BG, padx=16, pady=14)
        panel.pack(fill="both", expand=True)

        def label(parent, text, **opts):
            return tk.Label(parent, text=text, bg=self.BG, fg=self.TEXT, anchor="w",
                            font=("Microsoft YaHei UI", 9), **opts)

        tk.Label(panel, text="MOD4v3 自动混合 MoE", bg=self.BG, fg=self.CYAN, anchor="w",
                 font=("Microsoft YaHei UI", 17, "bold")).pack(fill="x")
        label(panel, "WASD 驾驶   ·   台阶自动识别   ·   空格跳跃").pack(fill="x", pady=(0, 10))

        selectors = tk.Frame(panel, bg=self.BG)
        selectors.pack(fill="x")
        selectors.columnconfigure(1, weight=1)
        self.suite_var = tk.StringVar(value=SUITE_LABELS[0])
        self.sub_var = tk.StringVar()
        self.level_var = tk.StringVar(value="L4")
        self.spawn_var = tk.StringVar()
        self.suite_cb = ttk.Combobox(selectors, state="readonly", values=SUITE_LABELS, textvariable=self.suite_var)
        self.sub_cb = ttk.Combobox(selectors, state="disabled", textvariable=self.sub_var)
        self.spawn_cb = ttk.Combobox(selectors, state="readonly", textvariable=self.spawn_var)
        self.level_cb = ttk.Combobox(selectors, state="disabled", width=4, values=[f"L{i}" for i in range(10)], textvariable=self.level_var)
        for index, name, widget in (
            (0, "地图", self.suite_cb), (1, "子场景", self.sub_cb), (2, "出生点", self.spawn_cb),
        ):
            label(selectors, name, width=7).grid(row=index, column=0, sticky="w", pady=3)
            widget.grid(row=index, column=1, sticky="ew", pady=3)
        self.level_cb.grid(row=1, column=2, padx=(6, 0))
        self.suite_cb.bind("<<ComboboxSelected>>", lambda _event: self.on_suite_changed())
        self.sub_cb.bind("<<ComboboxSelected>>", lambda _event: self.apply_suite_selection())
        self.level_cb.bind("<<ComboboxSelected>>", lambda _event: self.apply_suite_selection())
        self.spawn_cb.bind("<<ComboboxSelected>>", lambda _event: self.on_spawn_selected())
        self.hint_var = tk.StringVar()
        label(panel, "", textvariable=self.hint_var, wraplength=494, justify="left").pack(fill="x", pady=(4, 8))

        self.live_var = tk.StringVar()
        tk.Label(panel, textvariable=self.live_var, bg=self.PANEL, fg=self.TEXT, justify="left", anchor="w",
                 font=("Microsoft YaHei UI", 10), padx=11, pady=10).pack(fill="x")

        sliders = tk.Frame(panel, bg=self.BG)
        sliders.pack(fill="x", pady=(6, 4))
        self.h_slider_var = tk.DoubleVar(value=0.28)
        self.v_slider_var = tk.DoubleVar(value=self.sim.max_vx)
        for title, var, lo, hi, resolution, change in (
            ("站高 Q/E (m)", self.h_slider_var, HEIGHT_MIN, HEIGHT_MAX, 0.005, self.on_height_slider),
            ("W 速度 (m/s)", self.v_slider_var, 0.3, 2.2, 0.05, self.on_speed_slider),
        ):
            column = tk.Frame(sliders, bg=self.BG)
            column.pack(side="left", fill="x", expand=True, padx=4)
            label(column, title).pack(fill="x")
            tk.Scale(column, from_=lo, to=hi, resolution=resolution, orient="horizontal", variable=var,
                     bg=self.BG, fg=self.CYAN, troughcolor=self.CARD, highlightthickness=0,
                     takefocus=False, command=change).pack(fill="x")

        buttons = tk.Frame(panel, bg=self.BG)
        buttons.pack(fill="x", pady=(0, 5))
        for text, action, color in (
            ("空格 / J  跳跃", self.action_jump, self.GREEN),
            ("R  重置", self.action_reset, self.CYAN),
            ("P  暂停", self.action_pause, self.YELLOW),
        ):
            self._btn(buttons, text, action, color).pack(side="left", expand=True, fill="x", padx=3)

        self.follow_cam_var = tk.BooleanVar(value=True)
        self.chase_cam_var = tk.BooleanVar(value=False)
        cameras = tk.Frame(panel, bg=self.BG)
        cameras.pack(fill="x")
        for text, var in (("镜头跟随", self.follow_cam_var), ("车尾视角", self.chase_cam_var)):
            tk.Checkbutton(cameras, text=text, variable=var, bg=self.BG, fg=self.TEXT,
                           selectcolor=self.PANEL, activebackground=self.BG, takefocus=False).pack(side="left")
        self._btn(cameras, "全地形总览", self.open_rough_overview, self.MUTED, pad=(5, 3)).pack(side="right")

        label(panel, "W/S 前后　A/D 转向　Q/E 站高　[ / ] 切出生点\n"
                     "1/2/3 站高预设　4/5/6 速度档　X 清速度", justify="left").pack(fill="x", pady=8)
        self.status_var = tk.StringVar()
        tk.Label(panel, textvariable=self.status_var, bg=self.BG, fg=self.CYAN, anchor="w").pack(fill="x")
        self.hotkeys = {
            "space": self.action_jump, "j": self.action_jump, "r": self.action_reset, "p": self.action_pause,
            "[": lambda: self.cycle_spawn(-1), "]": lambda: self.cycle_spawn(1), "x": self.action_stop,
        }
        for key, height in {"1": 0.20, "2": 0.28, "3": 0.40}.items():
            self.hotkeys[key] = lambda value=height: self.set_height_preset(value)
        for key, speed in {"4": 0.5, "5": 0.9, "6": 1.6}.items():
            self.hotkeys[key] = lambda value=speed: self.set_speed(value)

    def on_suite_changed(self) -> None:
        suite = self.suite_cb.current()
        choices = {3: SERIAL_SUB_SCENES, 4: STAIR_SCENES, 5: maps.ROUGH_CN}.get(suite, ())
        self.sub_cb.configure(values=choices, state="readonly" if choices else "disabled")
        self.sub_var.set(choices[0] if choices else "")
        self.level_cb.configure(state="readonly" if suite == 5 else "disabled")
        self.apply_suite_selection()

    def apply_suite_selection(self, initial: bool = False) -> None:
        suite = self.suite_cb.current()
        self.status_var.set("正在载入地图…")
        self.root.update_idletasks()
        meta = map_for(suite, self.sub_var.get(), int(self.level_var.get()[1:]))
        self.sim.load_map(meta, spawn_idx=0)
        self.waiting_for_input = True
        names = [f"{index + 1}. {spawn['name']}" for index, spawn in enumerate(meta["spawns"])]
        self.spawn_cb.configure(values=names)
        self.spawn_cb.current(0)
        self.hint_var.set(meta["spawns"][0].get("hint", ""))
        self.h_slider_var.set(self.sim.target_h)
        self.deadline = time.perf_counter()
        self.event_msg = "地图已载入"
        if not initial:
            self.focus_console()

    def on_height_slider(self, value: str) -> None:
        self.sim.target_h = float(value)

    def on_speed_slider(self, value: str) -> None:
        self.sim.max_vx = float(value)

    def set_height_preset(self, height: float) -> None:
        self.sim.target_h = height
        self.h_slider_var.set(height)

    def set_speed(self, speed: float) -> None:
        self.sim.max_vx = speed
        self.v_slider_var.set(speed)

    def on_spawn_selected(self) -> None:
        super().on_spawn_selected()
        self.waiting_for_input = True

    def action_reset(self) -> None:
        super().action_reset()
        self.waiting_for_input = True

    def action_pause(self) -> None:
        if self.waiting_for_input:
            self.waiting_for_input = False
            self.sim.paused = False
            self.deadline = time.perf_counter()
        else:
            super().action_pause()

    def action_jump(self) -> None:
        if self.sim.request_jump():
            self.waiting_for_input = False
            self.event_msg = "已发出跳跃指令"

    def action_stop(self) -> None:
        self.sim.cmd_vx = self.sim.cmd_wz = 0.0

    def poll_keys(self) -> set[str]:
        if not self.is_console_foreground():
            self.prev_vk_down.clear()
            return set()
        down = {key for key in MOTION_KEYS | self.hotkeys.keys() if self.user32.GetAsyncKeyState(VK_MAP[key]) & 0x8000}
        new_keys = down - self.prev_vk_down
        self.prev_vk_down = down
        # Iterating the dispatch table keeps simultaneous presses deterministic.
        for key, action in self.hotkeys.items():
            if key in new_keys:
                action()
        motion = down & MOTION_KEYS
        if motion:
            self.waiting_for_input = False
        return motion

    def tick(self) -> None:
        if self.closed or self.sim.viewer is None or not self.sim.viewer.is_running():
            self.close()
            return
        try:
            pressed = self.poll_keys()
            now = time.perf_counter()
            active = not self.sim.paused and not self.waiting_for_input
            if not active:
                self.deadline = now
            due = 0
            if active and self.deadline <= now:
                due = min(4, int((now - self.deadline) / CONTROL_DT) + 1)
            viewer = self.sim.viewer
            if due or now - self.last_ui_time >= 0.05:
                with viewer.lock():
                    if active:
                        for _ in range(due):
                            self.sim.step(pressed)
                        self.deadline += due * CONTROL_DT
                        if self.deadline < now - 0.10:
                            self.deadline = now
                    if self.follow_cam_var.get():
                        r = self.sim.d.xmat[self.sim.env.base_id].reshape(3, 3)
                        x, y, z = self.sim.d.qpos[:3]
                        viewer.cam.lookat[:] = [x + 0.32 * r[0, 0], y + 0.32 * r[1, 0], z + 0.03]
                        if self.chase_cam_var.get():
                            viewer.cam.azimuth = math.degrees(math.atan2(r[1, 0], r[0, 0])) + 180.0
                viewer.sync()
            if now - self.last_ui_time >= 0.05:
                self.last_ui_time = now
                self.refresh_hud(pressed)
            self.root.after(2, self.tick)
        except Exception:
            ERROR_PATH.write_text(traceback.format_exc(), encoding="utf-8")
            self.close()
            raise

    def refresh_hud(self, pressed: set[str]) -> None:
        data = self.sim.telemetry()
        r = data["router"]
        self.live_var.set(
            f"E0 巡航 {r['e0']:.0%}   E1 上阶 {r['e1']:.0%}   E2 跳跃 {r['e2']:.0%}\n"
            f"速度 {data['vx']:+.2f} / {data['cmd_vx']:+.2f} m/s   地面 {data['ground_z']:+.2f} m\n"
            f"站高 {data['rel_z']:.3f} / {data['target_h']:.3f} m   俯仰 {data['pitch_deg']:+.1f}°\n"
            f"上次跳跃净空 {data['peak_rim_cm']:.1f} cm   闭链误差 {data['closure_mm']:.3f} mm"
        )
        if pressed & {"q", "e"}:
            self.h_slider_var.set(self.sim.target_h)
        focus = "键盘已激活" if self.is_console_foreground() else "点本窗口激活键盘"
        run = self.event_msg
        if data["paused"]:
            run = "已暂停"
        elif self.waiting_for_input:
            run = "按 W 开始"
        self.status_var.set(f"{focus}   ·   {run}")
        now = time.perf_counter()
        if now - self.last_status_dump >= 0.5:
            self.last_status_dump = now
            payload = dict(data, suite=self.suite_var.get(), spawn=self.spawn_var.get(), pressed=sorted(pressed),
                           pid=os.getpid(), checkpoint_sha256=self.sim.ckpt_sha, updated_epoch=time.time(),
                           waiting_for_input=self.waiting_for_input)
            STATUS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    policy, sha = load()
    sim = AutonomousMapSimulation(policy, sha)
    root = tk.Tk()
    try:
        AutonomousPlayer(root, sim)
        root.mainloop()
    finally:
        sim.close()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        ERROR_PATH.write_text(traceback.format_exc(), encoding="utf-8")
        raise
