# SPDX-License-Identifier: MIT
"""MOD4v3 Manual-FSM All-Maps Interactive WASD Playground (External MuJoCo 3D Viewer + Console HUD)."""
from __future__ import annotations

from argparse import ArgumentParser
import ctypes
from ctypes import wintypes
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import tkinter as tk
from tkinter import ttk
import traceback
from typing import Any

import numpy as np
import torch

from fsm_paths import HERE, JUMP_PATH, donor_imports
from fsm_io import put, sha256
from fsm_maps import MAPS, metadata, reference
from manual_fsm_runtime import CONTROL_DT, ManualPolicy, ManualSimulation
from manual_fsm_core import LABELS, Phase

donor_imports()
from play_unified_moe_all_maps import ROUGH_VIEWER_DIR, SERIAL_SUB_SCENES, VK_MAP  # noqa: E402

STAIR_MATRIX_SCENES = (
    "20 cm 单阶",
    "24 cm 高台",
    "16 cm 高台",
    "15 cm 单阶",
    "10 cm 单阶",
    "5 cm 单阶",
    "20 + 20 cm 连续双阶",
)

PLAYER_SUITES: tuple[tuple[str, str], ...] = (
    ("1 · 综合试炼场 · 五车道 (秒开·单阶/双阶/高台)", "suite_proving"),
    ("2 · RMUC2027 官方全赛场 (MJB秒载·9大出生点)", "suite_rmuc2027"),
    ("3 · A–A 西入口 400/360 mm 双阶", "rm27_west_400"),
    ("4 · A–A 东入口 400/360 mm 双阶", "rm27_east_400"),
    ("5 · RMUC2027 西入口双阶专测", "rm27_west"),
    ("6 · RMUC2027 东入口双阶专测", "rm27_east"),
    ("7 · 380 mm 实体宽台 (1.6~2.8m/s 助跑大跳)", "platform_380"),
    ("8 · 360 mm 实体宽台 (1.6~2.8m/s 助跑大跳)", "platform_360"),
    ("9 · 200 mm 单阶 (直入 / ±25° 斜入)", "step_20"),
    ("10 · 200 mm 正斜沿 (+25°)", "oblique_20"),
    ("11 · 200 mm 反斜沿 (-25°)", "oblique_20_negative"),
    ("12 · 110 mm 路沿坎", "curb_11"),
    ("13 · 平地全速巡航 (0~3.0 m/s)", "flat"),
    ("14 · L9 长距离崎岖地形", "rough_L9"),
    ("15 · Sirina · 开源综合跑酷场", "suite_sirina"),
    ("16 · Serial_Leg · 17°陡坡与台阶", "suite_serial"),
    ("17 · 台阶与高台专项难度矩阵", "suite_stairs"),
    ("18 · Rough-v1 · 崎岖地形矩阵 (11类×L0~L9)", "suite_rough"),
)

CONT_KEYS = {"w", "s", "a", "d", "q", "e", "f"}


def build_player_scene(course_key: str, sub_scene: str = "", level: int = 4) -> dict[str, Any]:
    cache = HERE / "maps" / "wasd"
    cache.mkdir(parents=True, exist_ok=True)
    maps_mod = reference.legacy.maps
    maps_mod.CACHE_DIR = cache

    if course_key == "suite_proving":
        meta = maps_mod.build_proving_ground()
        labels = (
            ("20 / 40 cm 连续双阶", "提前按 C 开启上阶预备（未触阶保持直立），按住 W 上双阶。"),
            ("20 cm 高台跳跃道", "助跑或近阶按 Space / J 触发大跳。"),
            ("24 cm 高台跳跃道", "助跑或近阶按 Space / J 触发大跳。"),
            ("20 cm 单阶攀爬道", "提前按 C 开启上阶预备，按住 W 撞阶自动攀爬，登顶自动回 E0。"),
            ("限高杆与连续阶梯", "按 1 切低姿钻杆，按 2/3 恢复巡航站高。"),
        )
        for sp, (name, hint) in zip(meta["spawns"], labels):
            sp.update(name=name, hint=hint)
        meta["course"] = "suite_proving"
        return meta

    if course_key in ("suite_rmuc2027", "rm27_west", "rm27_east"):
        import xml.etree.ElementTree as ET
        import mujoco as mj

        stiff_xml = cache / "rmuc2027_stiff_v1.xml"
        stiff_mjb = cache / "rmuc2027_stiff_v1.mjb"
        if not stiff_mjb.is_file() or not stiff_xml.is_file():
            base_meta = metadata("rm27_west", cache)
            tree = ET.parse(base_meta["xml_path"])
            for g in tree.getroot().iter("geom"):
                if g.get("contype") not in (None, "0") and (
                    g.get("name", "").startswith("rmuc") or g.get("type") == "hfield"
                ):
                    g.set("solref", "0.0012 1")
                    g.set("friction", "0.9 0.005 0.0001")
            tree.write(stiff_xml, encoding="utf-8", xml_declaration=True)
            m_tmp = mj.MjModel.from_xml_path(str(stiff_xml))
            mj.mj_saveModel(m_tmp, str(stiff_mjb), None)

        wx, _, _ = reference.RM["rm27_west"]
        ex, ey, _ = reference.RM["rm27_east"]
        west_spawn = dict(
            x=wx,
            y=-4.85,
            yaw_deg=0.0,
            name="中央高地 · 西侧正对双阶 (-16.8, -4.85)",
            hint="已修复地面刚度(solref=0.0012)与正中心对准！提前按 C 开启上阶预备，建议速度 1.5~1.6 m/s 按住 W 冲双阶！",
        )
        east_spawn = dict(
            x=ex,
            y=ey,
            yaw_deg=180.0,
            name="中央高地 · 东侧正对双阶 (-5.6, -5.90)",
            hint="已修复地面刚度(solref=0.0012)！提前按 C 开启上阶预备，建议速度 1.2~1.5 m/s 按住 W 冲双阶！",
        )
        if course_key == "rm27_west":
            return dict(xml_path=str(stiff_xml), mjb_path=str(stiff_mjb), spawns=[west_spawn], course="rm27_west", hide_group5=True)
        if course_key == "rm27_east":
            return dict(xml_path=str(stiff_xml), mjb_path=str(stiff_mjb), spawns=[east_spawn], course="rm27_east", hide_group5=True)

        spawns = [
            west_spawn,
            east_spawn,
            {"name": "红方前场大道 (-1.8, -3.0)", "x": -1.80, "y": -3.00, "yaw_deg": 180.0, "z_ray": 4.5, "hint": "视野开阔主干道：按住 W 助跑后按 Space/J 即可体验 50cm 净空大跳！"},
            {"name": "蓝方前场大道 (-20.5, -4.0)", "x": -20.50, "y": -4.00, "yaw_deg": 0.0, "z_ray": 4.5, "hint": "蓝方主干道：自由巡航、助跑大跳与冲高地"},
            {"name": "中央高地 30cm 平台顶 (-10.0, -3.0)", "x": -10.00, "y": -3.00, "yaw_deg": -90.0, "z_ray": 4.5, "hint": "位于中央 30cm 高台内场顶部，可测试巡航与下台阶"},
            {"name": "红方狗洞隧道入口 (-13.6, +0.99)", "x": -13.60, "y": 0.99, "yaw_deg": 0.0, "z_ray": 0.80, "hint": "按 1 压低站高即可钻过低矮隧道"},
            {"name": "蓝方 40cm 高台出发区 (-23.5, -2.0)", "x": -23.50, "y": -2.00, "yaw_deg": 0.0, "z_ray": 4.5, "hint": "位于 40cm 高台区，可体验飞跃下阶"},
        ]
        return dict(xml_path=str(stiff_xml), mjb_path=str(stiff_mjb), spawns=spawns, course="rm27_west", hide_group5=True)

    if course_key == "suite_sirina":
        meta = maps_mod.build_parkour_sirina()
        meta["course"] = "suite_sirina"
        return meta

    if course_key == "suite_serial":
        meta = maps_mod.build_serial_leg_course(sub_scene or SERIAL_SUB_SCENES[0])
        for sp in meta["spawns"]:
            sp.setdefault("hint", "平地/坡道直接 W 巡航；遇台阶提前按 C 开启上阶预备；Space/J 大跳。")
        meta["course"] = "suite_serial"
        return meta

    if course_key == "suite_stairs":
        meta = maps_mod.build_stairs_matrix(sub_scene or STAIR_MATRIX_SCENES[0])
        for sp in meta["spawns"]:
            sp.setdefault("hint", "提前按 C 开启上阶预备（未触阶直立），撞阶自动攀爬；也可按 Space/J 直跳。")
        meta["course"] = "suite_stairs"
        return meta

    if course_key == "suite_rough":
        meta = maps_mod.build_rough_v1_tile(sub_scene or maps_mod.ROUGH_CN[0], level)
        meta["course"] = "suite_rough"
        return meta

    meta = metadata(course_key, cache)
    default_hint = (
        "站高0.28m，1.6m/s在380mm台前约0.25m、360mm台前约0.35m；2.8m/s约0.70m前按Space/J。"
        if course_key.startswith("platform_")
        else "默认 C 关闭为纯 E0 巡航；提前按 C 开启上阶预备（未撞阶绝不下蹲），撞阶自动攀爬！"
    )
    for sp in meta["spawns"]:
        sp.setdefault("hint", default_hint)
    return meta


def smoke(checkpoint=None):
    p = ManualPolicy(checkpoint)
    sim = ManualSimulation(p, show_viewer=False)
    rows = []
    try:
        for label, course in MAPS:
            sim.load_map(metadata(course))
            sim.target_h = 0.39
            for _ in range(35):
                sim.step(set())
            for keys in ({"w"}, {"s"}, {"a"}, {"d"}):
                for _ in range(6):
                    sim.step(keys)
                    assert sim.route["e1"] == 0.0 and np.isfinite(sim.prev_a).all()
            rows.append(
                dict(
                    course=course,
                    finite=True,
                    cruise_stair_weight=sim.route["e1"],
                    physics_hz=1.0 / sim.m.opt.timestep,
                    tire_radius_m=sim.m.geom_size[sim.tire_gids, 0].tolist(),
                )
            )
            print(label, "OK", flush=True)
        sim.load_map(metadata("flat"))
        sim.step({"c", "w"})
        assert sim.mode_latched and sim.route["e1"] == 0.0
        sim.step({"w", "v"})
        assert sim.route["e1"] == 1.0
        sim.step({"s"})
        assert sim.route["e1"] == 0.0 and p.fsm.phase[0] == Phase.CRUISE_E0
        sim.step({"c"})
        assert not sim.mode_latched and sim.route["e1"] == 0.0
        sim.load_map(metadata("flat"))
        sim.cmd_vx = 0.0
        sim.step({"w", "v"})
        assert sim.route["e1"] == 1.0, "V must force climb on the first W tick"
        sim.step(set())
        assert sim.route["e1"] == 0.0 and p.fsm.phase[0] == Phase.CRUISE_E0
        sim.mode_latched = False
        sim.step({"w", "f", "v"})
        assert sim.route["e1"] == 1.0 and not sim.mode_latched
        sim.step({"w"})
        assert sim.route["e1"] == 0.0 and p.fsm.phase[0] == Phase.CRUISE_E0
        put(
            HERE / "evidence/PLAYER_SMOKE.json",
            dict(
                passed=True,
                maps=rows,
                stair_sha256=p.sha,
                external_mujoco_viewer=True,
                same_tick_reverse_and_mode_off=True,
                same_tick_forward_release=True,
                same_tick_temporary_release=True,
                force_on_first_forward_tick=True,
                force_key=True,
                jump_sha256=sha256(JUMP_PATH),
            ),
        )
    finally:
        sim.close()


class ExternalMuJoCoFSMApp:
    """Original external MuJoCo 3D viewer (`launch_passive`) + left hardware-polled WASD console."""

    BG = "#0d1117"
    PANEL = "#161b22"
    CARD = "#1f2630"
    TEXT = "#e6edf3"
    MUTED = "#8b949e"
    CYAN = "#39d5ff"
    GREEN = "#4be38a"
    YELLOW = "#ffd166"
    ORANGE = "#ff9f43"
    PINK = "#ff6b81"

    def __init__(self, root: tk.Tk, sim: ManualSimulation, initial_course: str = "flat", ui_smoke: bool = False):
        self.root = root
        self.sim = sim
        self.ui_smoke = ui_smoke
        self.closed = False
        self.waiting_for_input = True
        self.prev_vk_down: set[str] = set()
        self.mouse_held_keys: set[str] = set()
        self.last_ui_time = 0.0
        self.last_status_dump = 0.0
        self.drawn = 0
        self.deadline = time.perf_counter()
        self.event_msg = "已就绪：右侧原生 MuJoCo 3D 窗口自由拖拽视角，点本面板即可 WASD / C / Space 操控！"

        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.user32.GetForegroundWindow.restype = wintypes.HWND
        self.user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
        self.user32.GetAncestor.restype = wintypes.HWND
        self.user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
        self.user32.GetAsyncKeyState.restype = ctypes.c_short

        self._initial_course = initial_course
        self._build_ui()
        self.root.update_idletasks()
        self.control_hwnd = int(self.root.winfo_id())
        self.top_hwnd = int(self.user32.GetAncestor(self.control_hwnd, 2) or self.control_hwnd)
        try:
            imm32 = ctypes.WinDLL("imm32", use_last_error=True)
            imm32.ImmAssociateContext.argtypes = [wintypes.HWND, wintypes.HANDLE]
            imm32.ImmAssociateContext(self.top_hwnd, 0)
            imm32.ImmAssociateContext(self.control_hwnd, 0)
        except Exception:
            pass

        self.apply_suite_selection(initial=True)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(2, self.tick)
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(600, lambda: (not self.closed) and (self.root.attributes("-topmost", False), self.focus_console()))

        if self.ui_smoke:
            self.root.after(1800, self._run_ui_smoke_check)

    def _btn(self, parent, text: str, cmd, fg_color: str, pad=(8, 5)) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=lambda: (cmd(), self.focus_console()),
            bg=self.PANEL,
            fg=fg_color,
            activebackground="#30363d",
            activeforeground=fg_color,
            relief="flat",
            font=("Microsoft YaHei UI", 9, "bold"),
            padx=pad[0],
            pady=pad[1],
            takefocus=False,
        )

    def _build_ui(self) -> None:
        r = self.root
        r.title(f"MOD4v3 手工状态机 · 原生外置 MuJoCo 3D 控制台 · {self.sim.unified.sha[:8]}")
        r.geometry("560x820+18+25")
        r.minsize(530, 770)
        r.configure(bg=self.BG)

        o = tk.Frame(r, bg=self.BG, padx=14, pady=10)
        o.pack(fill="both", expand=True)

        tk.Label(
            o,
            text="MOD4v3 · 手工状态机全地图控制台",
            bg=self.BG,
            fg=self.CYAN,
            font=("Microsoft YaHei UI", 15, "bold"),
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            o,
            text=f"外置 MuJoCo 3D 视窗  |  E_stair: {self.sim.unified.sha[:8]}  |  未触阶直立零误蹲 + 380mm 跑跳",
            bg=self.BG,
            fg=self.MUTED,
            font=("Microsoft YaHei UI", 8),
            anchor="w",
        ).pack(fill="x", pady=(2, 8))

        mcard = tk.Frame(o, bg=self.PANEL, padx=10, pady=8)
        mcard.pack(fill="x", pady=(0, 8))
        tk.Label(mcard, text="地图套件", bg=self.PANEL, fg=self.YELLOW, font=("Microsoft YaHei UI", 9, "bold")).grid(
            row=0, column=0, sticky="w"
        )

        suite_labels = [label for label, _ in PLAYER_SUITES]
        default_idx = next((i for i, (_, k) in enumerate(PLAYER_SUITES) if k == self._initial_course), 0)
        self.suite_var = tk.StringVar(value=suite_labels[default_idx])
        self.suite_cb = ttk.Combobox(
            mcard, textvariable=self.suite_var, values=suite_labels, state="readonly", font=("Microsoft YaHei UI", 9)
        )
        self.suite_cb.grid(row=0, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=2)
        self.suite_cb.bind("<<ComboboxSelected>>", lambda _e: self.on_suite_changed())

        tk.Label(mcard, text="子场景", bg=self.PANEL, fg=self.TEXT, font=("Microsoft YaHei UI", 9)).grid(
            row=1, column=0, sticky="w", pady=2
        )
        self.sub_var = tk.StringVar(value="（当前地图默认）")
        self.sub_cb = ttk.Combobox(
            mcard, textvariable=self.sub_var, values=["（当前地图默认）"], state="disabled", font=("Microsoft YaHei UI", 9)
        )
        self.sub_cb.grid(row=1, column=1, sticky="ew", padx=(8, 4), pady=2)
        self.sub_cb.bind("<<ComboboxSelected>>", lambda _e: self.apply_suite_selection())

        self.level_var = tk.StringVar(value="L4")
        self.level_cb = ttk.Combobox(
            mcard,
            textvariable=self.level_var,
            values=[f"L{i}" for i in range(10)],
            state="disabled",
            width=5,
            font=("Microsoft YaHei UI", 9),
        )
        self.level_cb.grid(row=1, column=2, sticky="ew", pady=2)
        self.level_cb.bind("<<ComboboxSelected>>", lambda _e: self.apply_suite_selection())

        tk.Label(mcard, text="出生点 [ / ]", bg=self.PANEL, fg=self.TEXT, font=("Microsoft YaHei UI", 9)).grid(
            row=2, column=0, sticky="w", pady=2
        )
        self.spawn_var = tk.StringVar(value="")
        self.spawn_cb = ttk.Combobox(
            mcard, textvariable=self.spawn_var, values=[], state="readonly", font=("Microsoft YaHei UI", 9)
        )
        self.spawn_cb.grid(row=2, column=1, sticky="ew", padx=(8, 4), pady=2)
        self.spawn_cb.bind("<<ComboboxSelected>>", lambda _e: self.on_spawn_selected())
        self._btn(mcard, "重新载入", self.apply_suite_selection, self.CYAN, pad=(8, 3)).grid(
            row=2, column=2, sticky="ew", pady=2
        )
        mcard.columnconfigure(1, weight=1)

        self.hint_var = tk.StringVar(value="")
        tk.Label(
            o,
            textvariable=self.hint_var,
            bg=self.CARD,
            fg=self.GREEN,
            font=("Microsoft YaHei UI", 9),
            anchor="w",
            padx=8,
            pady=5,
            wraplength=520,
            justify="left",
        ).pack(fill="x", pady=(0, 8))

        tbox = tk.Frame(o, bg=self.PANEL, padx=12, pady=7)
        tbox.pack(fill="x", pady=(0, 8))
        self.tvars: dict[str, tk.StringVar] = {}
        rows = [
            ("状态机阶段 / 上阶开关", "phase", self.GREEN),
            ("专家路由权重 (E0/上阶/大跳)", "route", self.CYAN),
            ("前进实速 / 指令速度", "speed", self.YELLOW),
            ("离地净高 / 有效站高", "height", self.TEXT),
            ("机身俯仰 / 横滚 / 航向", "angles", self.TEXT),
            ("四连杆误差 / 跳跃峰值净空", "closure", self.ORANGE),
        ]
        for idx, (label_txt, key, color) in enumerate(rows):
            tk.Label(tbox, text=label_txt, bg=self.PANEL, fg=self.MUTED, font=("Microsoft YaHei UI", 9), anchor="w").grid(
                row=idx, column=0, sticky="w", pady=1
            )
            sv = tk.StringVar(value="—")
            self.tvars[key] = sv
            tk.Label(tbox, textvariable=sv, bg=self.PANEL, fg=color, font=("Consolas", 10, "bold"), anchor="e").grid(
                row=idx, column=1, sticky="e", pady=1
            )
        tbox.columnconfigure(1, weight=1)

        srow = tk.Frame(o, bg=self.BG)
        srow.pack(fill="x", pady=(0, 6))
        self.stair_btn = self._btn(srow, "C · 开启上阶预备 (未触阶直立)", self.action_toggle_stair, self.CYAN)
        self.stair_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=2)
        self._btn(srow, "Space / J · 380mm 大跳", self.action_jump, self.GREEN).grid(
            row=0, column=1, sticky="ew", padx=(4, 0), pady=2
        )
        self._btn(srow, "V · 贴阶零速强制攀爬", self.action_force_climb, self.YELLOW).grid(
            row=1, column=0, sticky="ew", padx=(0, 4), pady=2
        )
        self._btn(srow, "R · 重置回出生点", self.action_reset, self.ORANGE).grid(
            row=1, column=1, sticky="ew", padx=(4, 0), pady=2
        )
        srow.columnconfigure((0, 1), weight=1)

        sframe = tk.Frame(o, bg=self.BG)
        sframe.pack(fill="x", pady=(0, 4))
        self.h_slider_var = tk.DoubleVar(value=0.28)
        self.v_slider_var = tk.DoubleVar(value=1.60)
        self.sim.max_vx = 1.60
        self.sim.target_h = 0.28

        h_col = tk.Frame(sframe, bg=self.BG)
        h_col.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Label(h_col, text="巡航站高 Q↓ / E↑ (m)", bg=self.BG, fg=self.TEXT, font=("Microsoft YaHei UI", 9, "bold")).pack(
            anchor="w"
        )
        h_scale = tk.Scale(
            h_col,
            from_=0.24,
            to=0.42,
            resolution=0.005,
            orient="horizontal",
            variable=self.h_slider_var,
            command=lambda val: setattr(self.sim, "target_h", float(val)),
            bg=self.BG,
            fg=self.YELLOW,
            troughcolor="#30363d",
            highlightthickness=0,
            takefocus=False,
        )
        h_scale.pack(fill="x")

        v_col = tk.Frame(sframe, bg=self.BG)
        v_col.pack(side="left", fill="x", expand=True, padx=(6, 0))
        tk.Label(v_col, text="W/S 速度上限 (0.3~3.0 m/s)", bg=self.BG, fg=self.TEXT, font=("Microsoft YaHei UI", 9, "bold")).pack(
            anchor="w"
        )
        v_scale = tk.Scale(
            v_col,
            from_=0.30,
            to=3.00,
            resolution=0.10,
            orient="horizontal",
            variable=self.v_slider_var,
            command=lambda val: setattr(self.sim, "max_vx", float(val)),
            bg=self.BG,
            fg=self.CYAN,
            troughcolor="#30363d",
            highlightthickness=0,
            takefocus=False,
        )
        v_scale.pack(fill="x")

        prow = tk.Frame(o, bg=self.BG)
        prow.pack(fill="x", pady=(2, 6))
        for txt, fn in (
            ("4 · 低速 0.8", lambda: self.set_speed(0.8)),
            ("5 · 常用 1.6", lambda: self.set_speed(1.6)),
            ("6 · 极速 2.8", lambda: self.set_speed(2.8)),
            ("P · 暂停", self.action_pause),
        ):
            self._btn(prow, txt, fn, self.MUTED, pad=(4, 4)).pack(side="left", fill="x", expand=True, padx=2)

        dpad = tk.Frame(o, bg=self.BG)
        dpad.pack(fill="x", pady=(0, 6))
        pad_left = tk.Frame(dpad, bg=self.BG)
        pad_left.pack(side="left", expand=True)
        for txt, k, r_i, c_i in (
            ("W 前进", "w", 0, 1),
            ("A 左转", "a", 1, 0),
            ("S 后退", "s", 1, 1),
            ("D 右转", "d", 1, 2),
        ):
            b = tk.Button(
                pad_left,
                text=txt,
                width=10,
                bg=self.PANEL,
                fg=self.TEXT,
                activebackground="#30363d",
                activeforeground=self.CYAN,
                relief="flat",
                font=("Microsoft YaHei UI", 9, "bold"),
                pady=4,
                takefocus=False,
            )
            b.grid(row=r_i, column=c_i, padx=2, pady=2)
            b.bind(
                "<ButtonPress-1>",
                lambda _e, key=k: (setattr(self, "waiting_for_input", False), self.mouse_held_keys.add(key), self.focus_console()),
            )
            b.bind("<ButtonRelease-1>", lambda _e, key=k: self.mouse_held_keys.discard(key))
            b.bind("<Leave>", lambda _e, key=k: self.mouse_held_keys.discard(key))

        crow = tk.Frame(o, bg=self.BG)
        crow.pack(fill="x", pady=(0, 4))
        self.follow_cam_var = tk.BooleanVar(value=True)
        self.chase_cam_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            crow,
            text="镜头平移跟随",
            variable=self.follow_cam_var,
            bg=self.BG,
            fg=self.MUTED,
            selectcolor=self.PANEL,
            activebackground=self.BG,
            takefocus=False,
        ).pack(side="left")
        tk.Checkbutton(
            crow,
            text="车尾追尾旋转视角",
            variable=self.chase_cam_var,
            bg=self.BG,
            fg=self.MUTED,
            selectcolor=self.PANEL,
            activebackground=self.BG,
            takefocus=False,
        ).pack(side="left", padx=8)
        self._btn(crow, "750块全地形图", self.open_rough_overview, self.MUTED, pad=(6, 2)).pack(side="right")

        help_txt = (
            "操作说明（外置原生 MuJoCo 窗口自由鼠标拖视角；点击本面板激活硬件键盘直读）：\n"
            "• W/S 前后 | A/D 转向 | Q/E 站高 | 1/2/3 站高档(0.24/0.28/0.38m) | 4/5/6 速度档(0.8/1.6/2.8m/s)\n"
            "• C 切换上阶预备(或按住 F)：未撞台阶保持 0.39m 直立，触阶自动攀爬 | W+V 贴阶强起 | Space/J 大跳"
        )
        tk.Label(
            o,
            text=help_txt,
            bg=self.PANEL,
            fg=self.TEXT,
            font=("Microsoft YaHei UI", 8),
            justify="left",
            anchor="w",
            padx=9,
            pady=6,
        ).pack(fill="x")

        self.status_var = tk.StringVar(value=self.event_msg)
        tk.Label(o, textvariable=self.status_var, bg=self.BG, fg=self.CYAN, font=("Microsoft YaHei UI", 9), anchor="w", pady=4).pack(
            fill="x"
        )

        self.hotkeys = {
            "c": self.action_toggle_stair,
            "v": self.action_force_climb,
            "space": self.action_jump,
            "j": self.action_jump,
            "r": self.action_reset,
            "p": self.action_pause,
            "x": self.action_stop,
            "[": lambda: self.cycle_spawn(-1),
            "]": lambda: self.cycle_spawn(1),
            "1": lambda: self.set_height_preset(0.24),
            "2": lambda: self.set_height_preset(0.28),
            "3": lambda: self.set_height_preset(0.38),
            "4": lambda: self.set_speed(0.8),
            "5": lambda: self.set_speed(1.6),
            "6": lambda: self.set_speed(2.8),
        }

    def focus_console(self) -> None:
        try:
            self.root.lift()
            self.root.focus_force()
        except Exception:
            pass

    def is_console_foreground(self) -> bool:
        try:
            fg = int(self.user32.GetForegroundWindow())
            top = int(self.user32.GetAncestor(self.control_hwnd, 2) or self.control_hwnd)
            return fg != 0 and fg == top
        except Exception:
            return False

    def current_course_key(self) -> str:
        idx = max(0, self.suite_cb.current())
        return PLAYER_SUITES[idx][1]

    def on_suite_changed(self) -> None:
        key = self.current_course_key()
        maps_mod = reference.legacy.maps
        if key == "suite_serial":
            self.sub_cb.configure(state="readonly", values=SERIAL_SUB_SCENES)
            self.sub_var.set(SERIAL_SUB_SCENES[0])
            self.level_cb.configure(state="disabled")
        elif key == "suite_stairs":
            self.sub_cb.configure(state="readonly", values=STAIR_MATRIX_SCENES)
            self.sub_var.set(STAIR_MATRIX_SCENES[0])
            self.level_cb.configure(state="disabled")
        elif key == "suite_rough":
            self.sub_cb.configure(state="readonly", values=maps_mod.ROUGH_CN)
            self.sub_var.set(maps_mod.ROUGH_CN[0])
            self.level_cb.configure(state="readonly")
        else:
            self.sub_cb.configure(state="disabled", values=["（当前地图默认）"])
            self.sub_var.set("（当前地图默认）")
            self.level_cb.configure(state="disabled")
        self.apply_suite_selection()

    def _arrange_external_viewer(self) -> None:
        """Place the external MuJoCo GLFW window side-by-side on the right and ensure it is visible."""
        try:
            my_pid = os.getpid()
            WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

            def _cb(hwnd, _lp):
                pid = wintypes.DWORD()
                self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                if pid.value == my_pid and self.user32.IsWindowVisible(hwnd):
                    ln = self.user32.GetWindowTextLengthW(hwnd)
                    if ln > 0:
                        buf = ctypes.create_unicode_buffer(ln + 1)
                        self.user32.GetWindowTextW(hwnd, buf, ln + 1)
                        if "MuJoCo" in buf.value:
                            self.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                            self.user32.SetWindowPos(hwnd, 0, 582, 25, 1310, 960, 0x0040)  # SWP_SHOWWINDOW
                return True

            self.user32.EnumWindows(WNDENUMPROC(_cb), 0)
        except Exception:
            pass

    def apply_suite_selection(self, initial: bool = False) -> None:
        key = self.current_course_key()
        self.status_var.set(f"正在载入地图并启动外置 MuJoCo 3D 视窗：{self.suite_var.get()} …")
        self.root.update_idletasks()
        lvl = int(self.level_var.get().lstrip("L") or "4")
        meta = build_player_scene(key, self.sub_var.get(), lvl)
        self.sim.load_map(meta, spawn_idx=0)
        self.sim.target_h = float(self.h_slider_var.get())
        self.sim.max_vx = float(self.v_slider_var.get())
        self.waiting_for_input = True
        spawn_names = [f"{i + 1}. {s['name']}" for i, s in enumerate(meta["spawns"])]
        self.spawn_cb.configure(values=spawn_names)
        self.spawn_cb.current(0)
        self.hint_var.set("💡 " + meta["spawns"][0].get("hint", ""))
        self._update_stair_btn()
        self.deadline = time.perf_counter()
        self.event_msg = "地图已载入（按 W 出发）"
        self.root.after(120, lambda: (self._arrange_external_viewer(), self.focus_console()))

    def on_spawn_selected(self) -> None:
        idx = max(0, self.spawn_cb.current())
        sp = self.sim.reset_at_spawn(idx)
        self.sim.target_h = float(self.h_slider_var.get())
        self.sim.max_vx = float(self.v_slider_var.get())
        self.waiting_for_input = True
        if self.sim.viewer is not None:
            with self.sim.viewer.lock():
                yaw_r = math.radians(float(sp["yaw_deg"]))
                self.sim.viewer.cam.lookat[:] = [
                    float(self.sim.d.qpos[0]) + 0.35 * math.cos(yaw_r),
                    float(self.sim.d.qpos[1]) + 0.35 * math.sin(yaw_r),
                    float(self.sim.d.qpos[2]) + 0.04,
                ]
                self.sim.viewer.cam.azimuth = float(sp["yaw_deg"]) + 135.0
        self.hint_var.set("💡 " + sp.get("hint", ""))
        self._update_stair_btn()
        self.deadline = time.perf_counter()
        self.event_msg = f"已切至出生点：{sp['name']}"
        self.focus_console()

    def cycle_spawn(self, delta: int) -> None:
        spawns = self.sim.scene_meta.get("spawns", [])
        if len(spawns) <= 1:
            return
        nxt = (self.sim.spawn_idx + delta) % len(spawns)
        self.spawn_cb.current(nxt)
        self.on_spawn_selected()

    def _update_stair_btn(self) -> None:
        if self.sim.mode_latched:
            self.stair_btn.configure(text="C · 关闭上阶预备 (回纯 E0)", fg=self.PINK)
        else:
            self.stair_btn.configure(text="C · 开启上阶预备 (未触阶直立)", fg=self.CYAN)

    def action_toggle_stair(self) -> None:
        on = self.sim.toggle_stair_mode()
        self.waiting_for_input = False
        self._update_stair_btn()
        self.event_msg = "🪜 上阶预备已开启：未触阶保持 0.39m 直立，撞阶自动切 E_stair！" if on else "已关闭上阶预备，锁死纯 E0 巡航"

    def action_force_climb(self) -> None:
        self.sim.mode_latched = True
        self.sim.unified.intent["force"] = True
        self.waiting_for_input = False
        self._update_stair_btn()
        self.event_msg = "⚡ 已触发贴阶强制攀爬（配合按住 W 前进）"

    def action_jump(self) -> None:
        if self.sim.target_h > 0.30:
            self.sim.target_h = 0.28
            self.h_slider_var.set(0.28)
        if self.sim.request_jump():
            self.waiting_for_input = False
            self._update_stair_btn()
            self.event_msg = "🚀 触发 380mm / 原地大跳！"

    def action_reset(self) -> None:
        sp = self.sim.reset_at_spawn()
        self.sim.target_h = float(self.h_slider_var.get())
        self.sim.max_vx = float(self.v_slider_var.get())
        self.waiting_for_input = True
        self._update_stair_btn()
        self.deadline = time.perf_counter()
        self.event_msg = f"🔄 已复位：{sp['name']}"

    def action_pause(self) -> None:
        if self.waiting_for_input:
            self.waiting_for_input = False
            self.sim.paused = False
        else:
            self.sim.paused = not self.sim.paused
        self.deadline = time.perf_counter()
        self.event_msg = "⏸ 已暂停" if self.sim.paused else "▶ 继续运行"

    def action_stop(self) -> None:
        self.sim.cmd_vx = 0.0
        self.sim.cmd_wz = 0.0
        self.event_msg = "已清零速度指令"

    def set_height_preset(self, h: float) -> None:
        self.sim.target_h = h
        self.h_slider_var.set(h)
        self.event_msg = f"巡航站高 -> {h:.2f} m"

    def set_speed(self, v: float) -> None:
        self.sim.max_vx = v
        self.v_slider_var.set(v)
        self.event_msg = f"速度上限 -> {v:.1f} m/s"

    def open_rough_overview(self) -> None:
        log = (HERE / "evidence" / "rough_overview.log").open("w", encoding="utf-8")
        subprocess.Popen(
            [sys.executable, "-X", "utf8", "-u", str(ROUGH_VIEWER_DIR / "showcase.py"), "--mode", "map"],
            cwd=str(ROUGH_VIEWER_DIR),
            stdout=log,
            stderr=subprocess.STDOUT,
            creationflags=0x08000000,
        )
        self.event_msg = "已打开 750 块全地形总览窗口"

    def poll_keys(self) -> set[str]:
        if not self.is_console_foreground():
            self.prev_vk_down.clear()
            return set(self.mouse_held_keys)
        all_keys = CONT_KEYS | set(self.hotkeys.keys())
        down = {k for k in all_keys if self.user32.GetAsyncKeyState(VK_MAP[k]) & 0x8000}
        new_keys = down - self.prev_vk_down
        self.prev_vk_down = down
        for k, fn in self.hotkeys.items():
            if k in new_keys:
                fn()
        held = (down & CONT_KEYS) | self.mouse_held_keys
        if held:
            self.waiting_for_input = False
        return held

    def refresh_hud(self, pressed: set[str]) -> None:
        data = self.sim.telemetry()
        phase_idx = int(self.sim.unified.fsm.phase[0])
        mode_on = self.sim.mode_latched or ("f" in pressed)
        phase_txt = "上阶预备(停车直立)" if (mode_on and phase_idx == Phase.CRUISE_E0) else LABELS[phase_idx]
        mode_txt = "开启" if mode_on else "关闭"
        r = self.sim.route
        eff_h = getattr(self.sim.unified, "last_effective_height", self.sim.target_h)

        self.tvars["phase"].set(f"{phase_txt}  |  [C:{mode_txt}]")
        self.tvars["route"].set(f"E0 {r['e0']:.0%}  |  上阶 {r['e1']:.0%}  |  大跳 {r['e2']:.0%}")
        self.tvars["speed"].set(f"{data['vx']:+.2f} m/s  /  {data['cmd_vx']:+.2f} m/s (上限 {self.sim.max_vx:.1f})")
        self.tvars["height"].set(f"{data['rel_z']:.3f} m  /  有效 {eff_h:.3f} m")
        self.tvars["angles"].set(f"俯仰 {data['pitch_deg']:+.1f}° | 横滚 {data['roll_deg']:+.1f}° | 航向 {data['yaw_deg']:+.0f}°")
        self.tvars["closure"].set(f"{data['closure_mm']:.3f} mm  |  跳峰 {data['peak_rim_cm']:.1f} cm")

        if pressed & {"q", "e"}:
            self.h_slider_var.set(self.sim.target_h)
        self._update_stair_btn()

        focus = "🟢 键盘已激活" if self.is_console_foreground() else "⚪ 点本面板激活键盘"
        run = "⏸ 已暂停" if data["paused"] else ("按 W 出发" if self.waiting_for_input else self.event_msg)
        self.status_var.set(f"{focus}  ·  {run}")

        now = time.perf_counter()
        if now - self.last_status_dump >= 0.5:
            self.last_status_dump = now
            put(
                HERE / "evidence/PLAYER_LIVE_STATUS.json",
                dict(
                    data,
                    phase=phase_txt,
                    stair_mode_on=mode_on,
                    suite=self.suite_var.get(),
                    spawn=self.spawn_var.get(),
                    pressed=sorted(pressed),
                    pid=os.getpid(),
                    stair_sha256=self.sim.unified.sha,
                    external_viewer_running=bool(self.sim.viewer is not None and self.sim.viewer.is_running()),
                ),
            )

    def _run_ui_smoke_check(self) -> None:
        widgets = []

        def visit(w):
            for child in w.winfo_children():
                if child.winfo_ismapped():
                    box = [
                        child.winfo_rootx() - self.root.winfo_rootx(),
                        child.winfo_rooty() - self.root.winfo_rooty(),
                        child.winfo_width(),
                        child.winfo_height(),
                    ]
                    try:
                        text = child.cget("text")
                    except tk.TclError:
                        text = ""
                    widgets.append(
                        dict(
                            kind=child.winfo_class(),
                            text=text,
                            box=box,
                            clipped=box[0] < 0
                            or box[1] < 0
                            or box[0] + box[2] > self.root.winfo_width()
                            or box[1] + box[3] > self.root.winfo_height(),
                        )
                    )
                visit(child)

        visit(self.root)
        viewer_ok = bool(self.sim.viewer is not None and self.sim.viewer.is_running())
        put(
            HERE / "evidence/UI_LAYOUT_SMOKE.json",
            dict(
                window=[self.root.winfo_width(), self.root.winfo_height()],
                rendered_frames=self.drawn,
                external_mujoco_viewer_running=viewer_ok,
                widgets=widgets,
                clipped=sum(w["clipped"] for w in widgets),
                passed=viewer_ok and self.drawn > 0 and not any(w["clipped"] for w in widgets),
            ),
        )
        self.close()

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
            if due or now - self.last_ui_time >= 0.04:
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
                self.drawn += 1
            if now - self.last_ui_time >= 0.05:
                self.last_ui_time = now
                self.refresh_hud(pressed)
            self.root.after(2, self.tick)
        except Exception:
            (HERE / "evidence/PLAYER_ERROR.txt").write_text(traceback.format_exc(), encoding="utf-8")
            self.close()
            raise

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        self.sim.close()
        try:
            self.root.destroy()
        except Exception:
            pass


def play(checkpoint=None, initial_course: str = "suite_proving", ui_smoke: bool = False) -> None:
    policy = ManualPolicy(checkpoint)
    sim = ManualSimulation(policy, show_viewer=True)
    root = tk.Tk()
    try:
        ExternalMuJoCoFSMApp(root, sim, initial_course=initial_course, ui_smoke=ui_smoke)
        root.mainloop()
    finally:
        sim.close()


def main() -> None:
    all_choices = sorted({c for _, c in MAPS} | {k for _, k in PLAYER_SUITES})
    p = ArgumentParser(description=__doc__)
    p.add_argument("--checkpoint")
    p.add_argument("--scene", choices=all_choices, default="suite_proving")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--ui-smoke", action="store_true")
    args = p.parse_args()
    torch.set_num_threads(1)
    try:
        if args.smoke:
            smoke(args.checkpoint)
        else:
            play(args.checkpoint, args.scene, args.ui_smoke)
    except Exception:
        (HERE / "evidence/PLAYER_START_ERROR.txt").write_text(traceback.format_exc(), encoding="utf-8")
        raise


if __name__ == "__main__":
    main()
