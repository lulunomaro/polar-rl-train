"""One Tk window, native MuJoCo Renderer, 30-joint closed-chain pose editor.

Static editing only: mj_forward, zero velocity, no integration/policy/training.
The original robot assets and physical limits are never changed. Importing this
module creates no window and imports no simulator. main() is the GUI entry point.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
DEFAULT_IK = Path("F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package/kinematics_v2.py")
MODE = "STATIC_KINEMATIC_MJ_FORWARD_NO_INTEGRATION"
PASSIVE = ("rocker_pin", "coupler_pin", "knee", "distal_pin", "gas_pin", "gas_slide")
LEG_PARTS = ("hip", "crank", "rocker_pin", "coupler_pin", "knee", "distal_pin",
             "gas_pin", "gas_slide", "drive_hip_spin", "drive_input_spin", "wheel_spin")


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, payload):
    """Atomically publish a small metadata file in its explicitly selected folder."""
    path = Path(path).resolve()
    temporary = path.with_name(path.name + ".tmp")
    if temporary.parent != path.parent or temporary == path:
        raise ValueError("Invalid metadata destination")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_ik(path):
    path = Path(path).resolve()
    name = "_mod4_joint_step_ik_" + hashlib.sha256(str(path).encode()).hexdigest()[:12]
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError("Invalid v2 IK module path")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


def quat_from_rpy(roll, pitch, yaw):
    cr, sr = math.cos(roll / 2), math.sin(roll / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    return [cr * cp * cy + sr * sp * sy, sr * cp * cy - cr * sp * sy,
            cr * sp * cy + sr * cp * sy, cr * cp * sy - sr * sp * cy]


def rpy_from_quat(quat):
    w, x, y, z = (float(v) for v in quat)
    return [math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y)),
            math.asin(max(-1., min(1., 2 * (w * y - z * x)))),
            math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))]


def build_lookup(ik, side, count=256):
    if not 16 <= count <= 256:
        raise ValueError("lookup-points must be between 16 and 256")
    low, high = ik.mechanical_delta_bounds(side)
    deltas = [low + (high - low) * i / (count - 1) for i in range(count)]
    columns = {name: [] for name in PASSIVE}
    for delta in deltas:
        values, _ = ik.leg_configuration(0., delta, side=side, check_limits=True)
        for name in PASSIVE:
            columns[name].append(float(values[name]))
    return {"delta": deltas, "values": columns}


def solve_passive_delta(ik, side, joint, target, current_delta, table):
    """Finite lookup + local bisection; choose the root nearest the current delta.

    No independent passive qpos is assigned and no physical bound is relaxed.
    Near a tangent not bracketed by the finite lookup we explicitly report that
    this editor did not find a solution, rather than inventing a reachable pose.
    """
    if joint not in PASSIVE or not math.isfinite(target):
        raise ValueError("Invalid passive joint target")
    tolerance = 1e-10 if joint == "gas_slide" else 1e-9
    current = ik.leg_configuration(0., current_delta, side=side)[0][joint]
    if abs(current - target) <= tolerance:
        return current_delta
    deltas, values = table["delta"], table["values"][joint]
    roots = [deltas[i] for i, value in enumerate(values) if abs(value - target) <= tolerance]
    for i in range(len(deltas) - 1):
        fa, fb = values[i] - target, values[i + 1] - target
        if fa * fb >= 0:
            continue
        a, b = deltas[i], deltas[i + 1]
        for _ in range(48):
            middle = .5 * (a + b)
            fm = ik.leg_configuration(0., middle, side=side)[0][joint] - target
            if abs(fm) <= tolerance or b - a <= 2e-13:
                a = b = middle
                break
            if fa * fm <= 0:
                b = middle
            else:
                a, fa = middle, fm
        roots.append(.5 * (a + b))
    if not roots:
        if joint == "gas_slide":
            eye0 = float(ik.PARAMS["neutral_gas_eye_length_m"][side])
            minimum = 1000 * (eye0 + min(values))
            maximum = 1000 * (eye0 + max(values))
            raise ValueError(f"当前机构支路眼距约 {minimum:.6f}–{maximum:.6f} mm；气缸虽为140–200 mm，机构止挡可能先到。保持最后合法姿态。")
        raise ValueError("有限查表未在当前连续机械支路找到此值；保持最后合法姿态，不放宽限位。")
    result = min(roots, key=lambda value: abs(value - current_delta))
    ik.leg_configuration(0., result, side=side, check_limits=True)
    return result


class JointStepViewer:
    """Public API: set_joint_target(name, SI), set_root_pose(**SI), run().

    Gas set_joint_target uses the model's relative slide coordinate in metres;
    its GUI row instead presents actual eye distance in millimetres.
    """
    def __init__(self, scene, ik_path=DEFAULT_IK, width=1000, height=760,
                 fps=15, lookup_points=256):
        global np, mujoco, tk, ttk, Image, ImageTk
        import numpy as np
        import mujoco
        import tkinter as tk
        from tkinter import ttk
        from PIL import Image, ImageTk

        self.scene = Path(scene).resolve()
        self.ik_path = Path(ik_path).resolve()
        self.metadata_dir = self.scene.parent
        self.width, self.height = int(width), int(height)
        self.interval_ms = max(33, int(1000 / fps))
        self.ik = load_ik(self.ik_path)
        self.model = mujoco.MjModel.from_xml_path(str(self.scene))
        self.data = mujoco.MjData(self.model)
        free = [i for i in range(self.model.njnt)
                if self.model.jnt_type[i] == mujoco.mjtJoint.mjJNT_FREE]
        if len(free) != 1:
            raise ValueError("Expected exactly one robot free joint")
        self.free_id = free[0]
        self.root_address = int(self.model.jnt_qposadr[self.free_id])
        self.root_body = int(self.model.jnt_bodyid[self.free_id])
        self.joints = {}
        for jid in range(self.model.njnt):
            if jid == self.free_id:
                continue
            if self.model.jnt_type[jid] not in (mujoco.mjtJoint.mjJNT_HINGE, mujoco.mjtJoint.mjJNT_SLIDE):
                raise ValueError("This editor expects scalar non-root joints")
            name = mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_JOINT, jid)
            if not name:
                raise ValueError("All editable joints must be named")
            self.joints[name] = (jid, int(self.model.jnt_qposadr[jid]))
        self.joint_names = list(self.joints)
        if len(self.joint_names) != 30:
            raise ValueError(f"Expected 30 non-root joints, got {len(self.joint_names)}")
        expected = {side + "_" + part for side in ("left", "right") for part in LEG_PARTS}
        if not expected.issubset(self.joints):
            raise ValueError("Model does not contain the expected HW300N60 leg joints")
        self.direct_names = [name for name in self.joints
                             if name not in expected or name.endswith("_wheel_spin")]
        self.active = {side: [self._joint_value(side + "_hip"), self._joint_value(side + "_crank")]
                       for side in ("left", "right")}
        self.direct = {name: self._joint_value(name) for name in self.direct_names}
        address = self.root_address
        rpy = rpy_from_quat(self.data.qpos[address + 3:address + 7])
        self.root_pose = dict(zip(("x", "y", "z", "roll", "pitch", "yaw"),
                                  list(self.data.qpos[address:address + 3]) + rpy))
        self.tables = {side: build_lookup(self.ik, side, lookup_points) for side in ("left", "right")}
        self.initial = copy.deepcopy((self.active, self.direct, self.root_pose))
        self.controls = {}
        self._syncing = True
        self._last_synced_scale = {}
        self._dirty = True
        self._closed = False
        self._last_current = 0.
        self._last_rejection = None
        self._drag = None
        self._render_count = 0
        self._apply(self.active, self.direct, self.root_pose, sync=False)
        self.supports = self._support_geometries()
        floors = [item["z"] for item in self.supports if item["kind"] == "plane"]
        floor = max(floors) if floors else 0.
        self.step_tops = [item["z"] for item in self.supports if item["kind"] == "box"
                          and abs(item["z"] - floor - .2) < 1e-6]
        if not self.step_tops:
            raise ValueError("interactive_scene.xml must contain a horizontal collision step 200 mm above the floor")
        self.site_pairs = []
        for side in ("left", "right"):
            for a, b in (("proximal_a", "proximal_b"), ("distal_a", "distal_b"), ("gas_end", "gas_mount")):
                first = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_SITE, side + "_" + a)
                second = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_SITE, side + "_" + b)
                if first >= 0 and second >= 0:
                    self.site_pairs.append((side + "_" + a, first, second))
        self.window = tk.Tk()
        self.window.title("MOD4v2 HW300N60 关节位置探针 | 200mm台阶 | 静态")
        self.window.geometry(f"{self.width + 475}x{self.height + 155}")
        self.window.minsize(1150, 650)
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=1)
        self.notice = tk.StringVar(value="静态模式：只 mj_forward，不积分；root 不自动抬高。接触不代表动态平衡。")
        self.status = tk.StringVar()
        self.keep_delta = {side: tk.BooleanVar(value=True) for side in ("left", "right")}
        self.markers = tk.BooleanVar(value=False)
        self.colliders = tk.BooleanVar(value=False)
        self._build_ui()
        self.camera = mujoco.MjvCamera()
        self.options = mujoco.MjvOption()
        self.options.sitegroup[:] = 0
        self.options.geomgroup[3] = 0
        self.reset_camera()
        try:
            self.renderer = mujoco.Renderer(self.model, height=self.height, width=self.width)
        except Exception:
            self.window.destroy()
            raise
        self._sync_controls()
        self._syncing = False
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.report_callback_exception = self._callback_error
        write_json(self.metadata_dir / "STARTED.json", self._base_metadata())

    def _base_metadata(self):
        return {"schema": "mod4v2.joint_step_probe.v1", "timestamp_utc": utc_now(),
                "mode": MODE, "scene": str(self.scene), "ik_source": str(self.ik_path),
                "joint_names30": self.joint_names, "joint_count": len(self.joint_names),
                "step_height_m": .2, "step_geometry_verified": bool(self.step_tops),
                "source_asset_modified": False, "automatic_root_lift": False,
                "integration_enabled": False, "policy_or_training": False}

    def _joint_value(self, name):
        return float(self.data.qpos[self.joints[name][1]])

    def _apply(self, active, direct, root, sync=True):
        """Transactional closed-chain pose update; the original model is read-only."""
        active, direct, root = copy.deepcopy((active, direct, root))
        if any(not math.isfinite(float(value)) for value in root.values()):
            raise ValueError("Root pose must be finite")
        candidate = self.data.qpos.copy()
        assignments = dict(direct)
        for side in ("left", "right"):
            values, _ = self.ik.leg_configuration(*active[side], side=side, check_limits=True)
            for part, value in values.items():
                if part != "wheel_spin":
                    assignments[side + "_" + part] = value
        for name, value in assignments.items():
            jid, address = self.joints[name]
            value = float(value)
            if not math.isfinite(value):
                raise ValueError("Joint target must be finite")
            if self.model.jnt_limited[jid]:
                low, high = self.model.jnt_range[jid]
                if not low - 1e-9 <= value <= high + 1e-9:
                    raise ValueError(f"加载模型的真实范围不匹配：{name}={value:.9g}, [{low}, {high}]")
            candidate[address] = value
        address = self.root_address
        candidate[address:address + 3] = [root[key] for key in ("x", "y", "z")]
        candidate[address + 3:address + 7] = quat_from_rpy(root["roll"], root["pitch"], root["yaw"])
        previous = self.data.qpos.copy()
        try:
            self.data.qpos[:] = candidate
            self.data.qvel[:] = 0.
            self.data.ctrl[:] = 0.
            mujoco.mj_forward(self.model, self.data)
        except Exception:
            self.data.qpos[:] = previous
            mujoco.mj_forward(self.model, self.data)
            raise
        self.active, self.direct, self.root_pose = active, direct, root
        self._dirty = True
        if sync and hasattr(self, "controls"):
            self._sync_controls()

    def set_joint_target(self, name, value_si):
        """Set one requested joint through its leader/closed-chain mapping."""
        if name not in self.joints or not math.isfinite(float(value_si)):
            raise ValueError("Unknown joint or nonfinite target")
        value_si = float(value_si)
        active, direct = copy.deepcopy((self.active, self.direct))
        if name in self.direct_names:
            direct[name] = value_si
        else:
            side = "left" if name.startswith("left_") else "right"
            part = name[len(side) + 1:]
            part = {"drive_hip_spin": "hip", "drive_input_spin": "crank"}.get(part, part)
            hip, crank = active[side]
            if part == "hip":
                active[side][0] = value_si
                if self.keep_delta[side].get():
                    active[side][1] += value_si - hip
            elif part == "crank":
                active[side][1] = value_si
            elif part in PASSIVE:
                delta = solve_passive_delta(self.ik, side, part, value_si, crank - hip, self.tables[side])
                active[side][1] = hip + delta
            else:
                raise ValueError("Unsupported joint mapping")
        self._apply(active, direct, self.root_pose)

    def set_root_pose(self, **values_si):
        proposed = dict(self.root_pose)
        if not set(values_si).issubset(proposed):
            raise ValueError("Unknown root coordinate")
        proposed.update(values_si)
        self._apply(self.active, self.direct, proposed)

    def _build_ui(self):
        toolbar = ttk.Frame(self.window, padding=6)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        for label, command in (("Reset 姿态", self.reset_pose), ("相机复位", self.reset_camera),
                               ("落到地面/台阶（几何）", self.drop_to_support), ("保存姿态", self.save_pose)):
            ttk.Button(toolbar, text=label, command=lambda fn=command: self._guard(fn)).pack(side="left", padx=3)
        ttk.Checkbutton(toolbar, text="锚点", variable=self.markers, command=self._camera_dirty).pack(side="left")
        ttk.Checkbutton(toolbar, text="碰撞体", variable=self.colliders, command=self._camera_dirty).pack(side="left")
        ttk.Label(toolbar, text="台阶200mm | 静态编辑，无策略/积分").pack(side="right", padx=8)
        self.image_label = tk.Label(self.window, bg="#20242b")
        self.image_label.grid(row=1, column=0, sticky="nsew")
        self.image_label.bind("<ButtonPress-1>", lambda event: setattr(self, "_drag", (event.x, event.y)))
        self.image_label.bind("<ButtonRelease-1>", lambda event: setattr(self, "_drag", None))
        self.image_label.bind("<B1-Motion>", self._orbit)
        self.image_label.bind("<MouseWheel>", self._zoom)
        self.image_label.bind("<Button-4>", lambda event: self._zoom(event, 1))
        self.image_label.bind("<Button-5>", lambda event: self._zoom(event, -1))
        right = ttk.Frame(self.window)
        right.grid(row=1, column=1, sticky="ns")
        scroll = tk.Canvas(right, width=440, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right, orient="vertical", command=scroll.yview)
        scroll.configure(yscrollcommand=scrollbar.set)
        scroll.pack(side="left", fill="y", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.panel = ttk.Frame(scroll, padding=8)
        item = scroll.create_window((0, 0), window=self.panel, anchor="nw")
        self.panel.bind("<Configure>", lambda event: scroll.configure(scrollregion=scroll.bbox("all")))
        scroll.bind("<Configure>", lambda event: scroll.itemconfigure(item, width=event.width))
        def panel_wheel(event):
            scroll.yview_scroll(-1 if event.delta > 0 else 1, "units")
            return "break"
        scroll.bind("<MouseWheel>", panel_wheel)
        self.panel.bind("<MouseWheel>", panel_wheel)
        ttk.Label(self.panel, text="Root：位置输入mm，角度输入rad；不自动落轮", wraplength=410).pack(anchor="w")
        for key in ("x", "y", "z", "roll", "pitch", "yaw"):
            linear = key in ("x", "y", "z")
            self._add_row("root:" + key, "root " + key, -1500 if linear else -180,
                          1500 if linear else 180, "mm" if linear else "rad", 1. if linear else .1)
        for side, label in (("left", "左腿"), ("right", "右腿")):
            ttk.Separator(self.panel).pack(fill="x", pady=8)
            ttk.Label(self.panel, text=label + "：全部关节（被动项闭链反求）").pack(anchor="w")
            ttk.Checkbutton(self.panel, text="hip 保持δ整腿联动", variable=self.keep_delta[side]).pack(anchor="w")
            for part in LEG_PARTS:
                name = side + "_" + part
                if part == "gas_slide":
                    low, high, unit, resolution = 140., 200., "mm eye", .05
                elif part in PASSIVE:
                    column = self.tables[side]["values"][part]
                    low, high = math.degrees(min(column)), math.degrees(max(column))
                    if high - low < .01:
                        high = low + .01
                    unit, resolution = "rad", .01
                else:
                    low, high, unit, resolution = -360., 360., "rad", .1
                self._add_row(name, name, low, high, unit, resolution)
            ttk.Label(self.panel, text="±360°仅是滑块显示窗口；rad输入可更大，不是电机硬范围。\n眼距140–200mm；低折机构约152.606mm先止挡。", wraplength=410).pack(anchor="w")
        ttk.Separator(self.panel).pack(fill="x", pady=8)
        ttk.Label(self.panel, text="独立 guide 转角；滑块° / 输入rad").pack(anchor="w")
        for name in self.direct_names:
            if not name.endswith("_wheel_spin"):
                self._add_row(name, name, -360., 360., "rad", .1)
        ttk.Label(self.window, textvariable=self.status, justify="left", padding=6).grid(row=2, column=0, columnspan=2, sticky="ew")
        ttk.Label(self.window, textvariable=self.notice, foreground="#a33b20", wraplength=self.width + 420,
                  justify="left", padding=6).grid(row=3, column=0, columnspan=2, sticky="ew")

    def _add_row(self, key, label, low, high, unit, resolution):
        frame = ttk.Frame(self.panel, padding=(0, 4))
        frame.pack(fill="x")
        ttk.Label(frame, text=label + (" [eye mm]" if unit == "mm eye" else "")).pack(anchor="w")
        line = ttk.Frame(frame)
        line.pack(fill="x")
        scale = tk.Scale(line, from_=low, to=high, resolution=resolution, orient="horizontal",
                         showvalue=False, length=245, highlightthickness=0,
                         command=lambda value, k=key: self._scale_changed(k, value))
        scale.pack(side="left", fill="x", expand=True)
        variable = tk.StringVar()
        entry = ttk.Entry(line, textvariable=variable, width=14)
        entry.pack(side="left", padx=4)
        ttk.Label(line, text=unit).pack(side="left")
        entry.bind("<Return>", lambda event, k=key: self._entry_changed(k))
        entry.bind("<FocusOut>", lambda event, k=key: self._entry_changed(k))
        self.controls[key] = {"scale": scale, "entry": variable, "unit": unit}

    def _ui_value(self, key):
        if key.startswith("root:"):
            part = key[5:]
            value = self.root_pose[part]
            return value * 1000 if part in ("x", "y", "z") else value
        value = self._joint_value(key)
        if key.endswith("_gas_slide"):
            side = key.split("_", 1)[0]
            return 1000 * (value + self.ik.PARAMS["neutral_gas_eye_length_m"][side])
        return value

    def _sync_controls(self):
        before = self._syncing
        self._syncing = True
        try:
            for key, control in self.controls.items():
                value = self._ui_value(key)
                control["entry"].set(f"{value:.9f}")
                slider = value if control["unit"] in ("mm", "mm eye") else math.degrees(value)
                control["scale"].set(slider)
                self._last_synced_scale[key] = float(control["scale"].get())
        finally:
            self._syncing = before

    def _scale_changed(self, key, raw):
        value = float(raw)
        if self._syncing or abs(value - self._last_synced_scale.get(key, value)) < 1e-10:
            return
        unit = self.controls[key]["unit"]
        self._request(key, value if unit in ("mm", "mm eye") else math.radians(value))

    def _entry_changed(self, key):
        if self._syncing:
            return
        self._guard(lambda: self._request(key, float(self.controls[key]["entry"].get())))

    def _request(self, key, value):
        def apply():
            if not math.isfinite(value):
                raise ValueError("输入必须是有限数值")
            if key.startswith("root:"):
                part = key[5:]
                self.set_root_pose(**{part: value / 1000 if part in ("x", "y", "z") else value})
            else:
                target = value
                if key.endswith("_gas_slide"):
                    side = key.split("_", 1)[0]
                    if not 140 - 1e-7 <= value <= 200 + 1e-7:
                        raise ValueError("已确认气缸眼距范围140–200mm；保持最后合法姿态")
                    target = value / 1000 - self.ik.PARAMS["neutral_gas_eye_length_m"][side]
                self.set_joint_target(key, target)
            self._last_rejection = None
            self.notice.set("已更新合法闭链姿态；静态位置编辑不执行碰撞纠正或动力学。")
        self._guard(apply)

    def _guard(self, function):
        try:
            return function()
        except (ValueError, KeyError) as error:
            self._last_rejection = str(error)
            self.notice.set("保持最后合法态：" + str(error))
            self._sync_controls()
            return None

    def _robot_body(self, body):
        while body > 0:
            if body == self.root_body:
                return True
            body = int(self.model.body_parentid[body])
        return False

    def _support_geometries(self):
        supports = []
        for gid in range(self.model.ngeom):
            if self._robot_body(int(self.model.geom_bodyid[gid])):
                continue
            if not (self.model.geom_contype[gid] or self.model.geom_conaffinity[gid]):
                continue
            rotation = self.data.geom_xmat[gid].reshape(3, 3).copy()
            if abs(abs(float(rotation[2, 2])) - 1.) > 1e-7:
                continue
            kind = self.model.geom_type[gid]
            position = self.data.geom_xpos[gid].copy()
            if kind == mujoco.mjtGeom.mjGEOM_PLANE:
                supports.append({"kind": "plane", "z": float(position[2])})
            elif kind == mujoco.mjtGeom.mjGEOM_BOX:
                supports.append({"kind": "box", "z": float(position[2] + self.model.geom_size[gid, 2]),
                                 "center": position, "rotation": rotation,
                                 "halfsize": self.model.geom_size[gid].copy()})
        return supports

    def drop_to_support(self):
        """Explicit geometric wheel-centre/R vertical support, not a contact solver."""
        shifts = []
        radius = float(self.ik.PARAMS["wheel_motor"]["wheel_radius_m"])
        for side in ("left", "right"):
            site = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_SITE, side + "_wheel_center")
            if site < 0:
                raise ValueError("缺少轮心site；几何落地按钮未应用")
            center = self.data.site_xpos[site]
            heights = []
            for support in self.supports:
                if support["kind"] == "plane":
                    heights.append(support["z"])
                else:
                    offset = center - support["center"]
                    local = support["rotation"].T @ offset
                    if all(abs(local[i]) <= support["halfsize"][i] + 1e-9 for i in (0, 1)):
                        heights.append(support["z"])
            if not heights:
                raise ValueError("轮心XY下未发现水平支撑面；保持当前root")
            shifts.append(max(heights) + radius - float(center[2]))
        self.set_root_pose(z=self.root_pose["z"] + max(shifts))
        self.notice.set("仅执行轮心−R的竖直几何落地近似；未解全身接触、轮倾斜形状或动力学平衡。")

    def reset_pose(self):
        self._apply(*copy.deepcopy(self.initial))
        self._last_rejection = None
        self.notice.set("已恢复场景初始合法姿态；root未自动抬高。")

    def reset_camera(self):
        if not hasattr(self, "camera"):
            return
        self.camera.lookat[:] = [self.root_pose["x"] + .15, self.root_pose["y"], .27]
        self.camera.distance = 1.6
        self.camera.azimuth = 135.
        self.camera.elevation = -23.
        self._dirty = True

    def _camera_dirty(self):
        self._dirty = True

    def _orbit(self, event):
        if self._drag is not None:
            x, y = self._drag
            self.camera.azimuth += (event.x - x) * .4
            self.camera.elevation = float(np.clip(self.camera.elevation + (event.y - y) * .3, -89., 45.))
            self._drag = (event.x, event.y)
            self._dirty = True

    def _zoom(self, event, direction=None):
        direction = (1 if event.delta > 0 else -1) if direction is None else direction
        self.camera.distance = float(np.clip(self.camera.distance * (.90 if direction > 0 else 1.10), .15, 10.))
        self._dirty = True

    def _metrics(self):
        closure = {name: float(np.linalg.norm(self.data.site_xpos[a] - self.data.site_xpos[b]))
                   for name, a, b in self.site_pairs}
        gas, delta = {}, {}
        for side in ("left", "right"):
            gas[side] = self.ik.PARAMS["neutral_gas_eye_length_m"][side] + self._joint_value(side + "_gas_slide")
            delta[side] = self._joint_value(side + "_crank") - self._joint_value(side + "_hip")
        distances = [float(self.data.contact[i].dist) for i in range(self.data.ncon)]
        contacts = []
        for i in range(min(int(self.data.ncon), 6)):
            contact = self.data.contact[i]
            contacts.append({"geom1": mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_GEOM, int(contact.geom1)),
                             "geom2": mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_GEOM, int(contact.geom2)),
                             "distance_m": float(contact.dist)})
        return {"gas_eye_length_m": gas, "delta_rad": delta, "closure_errors_m": closure,
                "closure_max_m": max(closure.values()) if closure else None,
                "contact_count": int(self.data.ncon), "contact_min_distance_m": min(distances) if distances else None,
                "contacts_first6": contacts}

    def _current_metadata(self):
        payload = self._base_metadata()
        payload.update(self._metrics())
        payload.update(root_pose_SI={k: float(v) for k, v in self.root_pose.items()},
                       root_qpos_xyz_quat=self.data.qpos[self.root_address:self.root_address + 7].tolist(),
                       joint_positions_SI={name: self._joint_value(name) for name in self.joint_names},
                       last_input_rejection=self._last_rejection, render_count=self._render_count)
        return payload

    def save_pose(self):
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        path = self.metadata_dir / ("POSE_" + stamp + ".json")
        payload = self._current_metadata()
        payload["qpos"] = self.data.qpos.tolist()
        write_json(path, payload)
        self.notice.set("姿态已保存：" + path.name + "；没有修改原始资产。")
        return path

    def _callback_error(self, exception_type, value, tb):
        write_json(self.metadata_dir / "ERROR.json", {**self._base_metadata(), "fatal": True,
                   "phase": "Tk_callback", "error": str(value),
                   "traceback": "".join(traceback.format_exception(exception_type, value, tb))[-10000:]})
        self.notice.set("运行错误已写ERROR.json：" + str(value))

    def _refresh(self):
        if self._closed:
            return
        try:
            if self._dirty:
                self.options.sitegroup[:] = int(self.markers.get())
                self.options.geomgroup[3] = int(self.colliders.get())
                self.renderer.update_scene(self.data, self.camera, scene_option=self.options)
                frame = ImageTk.PhotoImage(Image.fromarray(self.renderer.render()))
                self.image_label.configure(image=frame)
                self.image_label.image = frame
                self._render_count += 1
                self._dirty = False
            metrics = self._metrics()
            closure = "未找到锚点" if metrics["closure_max_m"] is None else f"{metrics['closure_max_m'] * 1000:.9f}mm"
            penetration = max(0., -(metrics["contact_min_distance_m"] or 0.)) * 1000
            self.status.set(f"静态 | root实际z={self.data.qpos[self.root_address + 2] * 1000:.3f}mm | 台阶200mm\n"
                            f"L/R eye={metrics['gas_eye_length_m']['left'] * 1000:.6f}/{metrics['gas_eye_length_m']['right'] * 1000:.6f}mm  "
                            f"δ={metrics['delta_rad']['left']:.9f}/{metrics['delta_rad']['right']:.9f}rad\n"
                            f"闭链max={closure} | contacts={metrics['contact_count']}，最大穿透={penetration:.6f}mm（仅检测，无纠正）")
            now = time.monotonic()
            if now - self._last_current >= 1.:
                write_json(self.metadata_dir / "CURRENT.json", self._current_metadata())
                self._last_current = now
        except Exception:
            exception_type, value, tb = sys.exc_info()
            self._callback_error(exception_type, value, tb)
            return
        self.window.after(self.interval_ms, self._refresh)

    def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            payload = self._current_metadata()
            write_json(self.metadata_dir / "CURRENT.json", payload)
            write_json(self.metadata_dir / "CLOSED.json", {**payload, "reason": "window_closed"})
        finally:
            try:
                self.renderer.close()
            finally:
                self.window.destroy()

    def run(self):
        self._refresh()
        try:
            self.window.mainloop()
        finally:
            if not self._closed:
                self.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", type=Path, default=HERE / "interactive_scene.xml")
    parser.add_argument("--ik", type=Path, default=DEFAULT_IK)
    parser.add_argument("--render-width", type=int, default=1000)
    parser.add_argument("--render-height", type=int, default=760)
    parser.add_argument("--fps", type=float, default=15.)
    parser.add_argument("--lookup-points", type=int, default=256)
    args = parser.parse_args(argv)
    if not (320 <= args.render_width <= 1600 and 240 <= args.render_height <= 1200 and 1 <= args.fps <= 30
            and 16 <= args.lookup_points <= 256):
        parser.error("render width320..1600, height240..1200, fps1..30, lookup-points16..256 required")
    try:
        app = JointStepViewer(args.scene, args.ik, args.render_width, args.render_height,
                              args.fps, args.lookup_points)
        app.run()
    except Exception as error:
        path = args.scene.resolve().parent / "ERROR.json"
        write_json(path, {"schema": "mod4v2.joint_step_probe.v1", "timestamp_utc": utc_now(),
                         "mode": MODE, "fatal": True, "phase": "startup_or_mainloop",
                         "scene": str(args.scene.resolve()), "step_height_m": .2,
                         "source_asset_modified": False, "error": str(error),
                         "traceback": traceback.format_exc()[-10000:]})
        raise


if __name__ == "__main__":
    main()
