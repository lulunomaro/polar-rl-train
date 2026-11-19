# SPDX-License-Identifier: MIT
"""Scene builders & MJB caching for the MOD4v3 Unified 3-Expert MoE All-Maps Playground.

Merges the unmodified MOD4v3_HW300N60_R3 plant (SHA256 = 77904c00...) with:
  1. All-Skills 3-Expert Proving Ground (COD Forward Leap + 16/20/24cm Step-Jump + 20/40cm Stair Climb)
  2. Official RoboMaster RMUC2027 Full 3D Arena (visual meshes + tiled collision + 7 tactical spawns, MJB-cached)
  3. Open-Source Sirina / rc_mjlab Parkour Arena (T-stairs, wood bridges, 10° ramps, height bar, slalom, hfields)
  4. Open-Source Serial_Leg_Simulation Courses (17° ramp + gravel hfield, 5/7/10/15/20cm steps)
  5. Stair & High-Platform Difficulty Matrix (5cm -> 24cm single steps + 20+20cm continuous 2-step)
  6. SCUT Rough-v1 120m Matrix (11 terrain families x Levels 0..9 + full 750-tile overview launcher)
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import struct
from typing import Any
import xml.etree.ElementTree as ET

import mujoco as mj
import numpy as np

HERE = Path(__file__).resolve().parent
CACHE_DIR = HERE / "runtime_cache"
REPO = HERE.parents[2]
FANGZHEN = REPO.parent

D_BEST = REPO / "deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112"
PLANT_DIR = D_BEST / "plant/MOD4v3_HW300N60_R3"
ROBOT_XML = PLANT_DIR / "mjcf/scene.xml"
EXPECTED_ROBOT_XML_SHA256 = "77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f"

SERIAL_LEG_DIR = FANGZHEN / "playgrounds/Serial_Leg_Simulation"
RMUC_DIR = SERIAL_LEG_DIR / "RMUC2027"
RC_MJLAB_TERRAIN_DIR = FANGZHEN / "third_party/rc_mjlab/sim2sim/terrain"
ROUGH_VIEWER_DIR = D_BEST / "viewer"

ROUGH_MANIFEST = json.loads((ROUGH_VIEWER_DIR / "MAP_MANIFEST.json").read_text(encoding="utf-8"))
ROUGH_FAMILIES: list[str] = ROUGH_MANIFEST["families"]
ROUGH_CN: list[str] = [
    "低速宽台阶",
    "栅格小凸条",
    "正向坡面",
    "反向坡面",
    "高速宽台阶",
    "密集浅台阶",
    "浅反阶",
    "高反阶",
    "平地",
    "随机起伏",
    "阶梯落差",
]
ROUGH_COLS = {f: next(t["col"] for t in ROUGH_MANIFEST["tiles"] if t["family"] == f) for f in ROUGH_FAMILIES}
ROUGH_COLORS = [
    ".72 .51 .29 1",
    ".36 .59 .64 1",
    ".39 .63 .42 1",
    ".30 .56 .48 1",
    ".78 .47 .28 1",
    ".48 .53 .73 1",
    ".44 .57 .67 1",
    ".60 .46 .68 1",
    ".48 .52 .56 1",
    ".64 .61 .39 1",
    ".70 .41 .48 1",
]

SUITE_NAMES = [
    "1 · 三专家全技能综合试炼场 (跳扑+上阶+双阶)",
    "2 · RM 官方赛场 RMUC2027 (全尺寸3D地图)",
    "3 · 开源 Sirina / rc_mjlab 综合跑酷场",
    "4 · 开源 Serial_Leg 坡道碎石与台阶跑图",
    "5 · 台阶与高台专项难度矩阵 (5cm~24cm/双阶)",
    "6 · Rough Terrain 崎岖地形矩阵 (11类 × L0~L9)",
]


def _load_base_robot_tree() -> tuple[ET.ElementTree, ET.Element]:
    sha = hashlib.sha256(ROBOT_XML.read_bytes()).hexdigest()
    if sha != EXPECTED_ROBOT_XML_SHA256:
        raise RuntimeError(f"MOD4v3 MJCF SHA256 mismatch: {sha}")
    tree = ET.parse(ROBOT_XML)
    root = tree.getroot()
    root.find("compiler").set("meshdir", str(ROBOT_XML.parent / "assets"))
    vis_global = root.find("visual/global")
    if vis_global is not None:
        vis_global.set("offwidth", "1600")
        vis_global.set("offheight", "1000")
    return tree, root


def _add_checker_sky_and_floor(root: ET.Element, floor_size: str = "30 30 0.05", add_floor: bool = True) -> None:
    asset = root.find("asset")
    wb = root.find("worldbody")
    old_ground = wb.find("geom[@name='ground']")
    if old_ground is not None:
        wb.remove(old_ground)

    ET.SubElement(
        asset,
        "texture",
        name="arena_sky",
        type="skybox",
        builtin="gradient",
        rgb1="0.22 0.34 0.48",
        rgb2="0.06 0.09 0.14",
        width="512",
        height="3072",
    )
    ET.SubElement(
        asset,
        "texture",
        name="arena_grid",
        type="2d",
        builtin="checker",
        mark="edge",
        rgb1="0.19 0.24 0.30",
        rgb2="0.14 0.18 0.23",
        markrgb="0.32 0.40 0.48",
        width="300",
        height="300",
    )
    ET.SubElement(
        asset,
        "material",
        name="arena_floor_mat",
        texture="arena_grid",
        texuniform="true",
        texrepeat="4 4",
        reflectance="0.08",
    )
    if wb.find("light") is None:
        ET.SubElement(wb, "light", pos="0 0 6", dir="0 0 -1", directional="true", diffuse="0.85 0.85 0.85", ambient="0.45 0.45 0.45")
    if add_floor:
        ET.SubElement(
            wb,
            "geom",
            name="ground",
            type="plane",
            size=floor_size,
            material="arena_floor_mat",
            contype="1",
            conaffinity="2",
            friction="0.9 0.005 0.0001",
        )


def build_proving_ground() -> dict[str, Any]:
    """Multi-lane proving ground showcasing E0 + E1 (200mm stair climb) + E2 (COD forward leap & 16/20/24cm step-jump)."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    xml_path = CACHE_DIR / "scene_proving_ground_v1.xml"
    tree, root = _load_base_robot_tree()
    _add_checker_sky_and_floor(root, floor_size="35 35 0.05", add_floor=True)
    wb = root.find("worldbody")

    # Lane 0 (y = 0.0): Continuous All-Skills Course (Dive marker -> 20cm wide step -> 40cm 2nd step -> descent steps)
    ET.SubElement(wb, "geom", name="lane0_dive_line", type="box", pos="0.55 0.0 0.002", size="0.025 0.95 0.002", contype="0", conaffinity="0", rgba="0.15 0.85 1.0 0.95")
    ET.SubElement(wb, "geom", name="lane0_step1_20cm", type="box", pos="3.10 0.0 0.10", size="1.00 1.05 0.10", contype="1", conaffinity="2", friction="0.9 0.005 0.0001", rgba="0.28 0.40 0.54 1.0")
    ET.SubElement(wb, "geom", name="lane0_step2_40cm", type="box", pos="5.00 0.0 0.20", size="0.90 1.05 0.20", contype="1", conaffinity="2", friction="0.9 0.005 0.0001", rgba="0.35 0.50 0.65 1.0")
    ET.SubElement(wb, "geom", name="lane0_down_20cm", type="box", pos="6.50 0.0 0.10", size="0.60 1.05 0.10", contype="1", conaffinity="2", friction="0.9 0.005 0.0001", rgba="0.28 0.40 0.54 1.0")

    # Lane +1 (y = +2.8): Direct Stand-to-Step Jump Platforms (20cm -> 40cm) — press Space right at spawn!
    ET.SubElement(wb, "geom", name="lane_jump20_step1", type="box", pos="1.82 2.80 0.10", size="1.075 0.95 0.10", contype="1", conaffinity="2", friction="0.9 0.005 0.0001", rgba="0.22 0.58 0.46 1.0")
    ET.SubElement(wb, "geom", name="lane_jump20_step2", type="box", pos="3.80 2.80 0.20", size="0.95 0.95 0.20", contype="1", conaffinity="2", friction="0.9 0.005 0.0001", rgba="0.28 0.68 0.54 1.0")

    # Lane +2 (y = +5.4): 24cm Extreme Step-Jump Platform — press Space right at spawn!
    ET.SubElement(wb, "geom", name="lane_jump24_step", type="box", pos="1.765 5.40 0.12", size="1.075 0.95 0.12", contype="1", conaffinity="2", friction="0.9 0.005 0.0001", rgba="0.76 0.44 0.24 1.0")

    # Lane -1 (y = -2.8): Official 200mm Single-Step Climb & Park Lane (step front at x = 1.20m)
    ET.SubElement(wb, "geom", name="lane_stair200", type="box", pos="2.20 -2.80 0.10", size="1.00 1.05 0.10", contype="1", conaffinity="2", friction="0.9 0.005 0.0001", rgba="0.46 0.38 0.62 1.0")

    # Lane -2 (y = -5.4): Low-clearance 31cm Tunnel Bar (press 1 for 0.20m low stance!) + progressive 8/16/24cm staircase
    ET.SubElement(wb, "geom", name="tunnel_post_l", type="cylinder", pos="1.60 -4.65 0.16", size="0.03 0.16", contype="1", conaffinity="2", rgba="0.85 0.25 0.25 1.0")
    ET.SubElement(wb, "geom", name="tunnel_post_r", type="cylinder", pos="1.60 -6.15 0.16", size="0.03 0.16", contype="1", conaffinity="2", rgba="0.85 0.25 0.25 1.0")
    ET.SubElement(wb, "geom", name="tunnel_bar_top", type="box", pos="1.60 -5.40 0.335", size="0.12 0.78 0.02", contype="1", conaffinity="2", rgba="0.95 0.80 0.20 1.0")
    for idx, h_step in enumerate([0.08, 0.16, 0.24]):
        ET.SubElement(
            wb,
            "geom",
            name=f"lane_prog_step_{idx}",
            type="box",
            pos=f"{3.20 + idx * 0.85:.2f} -5.40 {h_step / 2:.3f}",
            size=f"0.425 0.90 {h_step / 2:.3f}",
            contype="1",
            conaffinity="2",
            friction="0.9 0.005 0.0001",
            rgba="0.52 0.48 0.36 1.0",
        )

    tree.write(xml_path, encoding="utf-8", xml_declaration=True)
    spawns = [
        {"name": "全技能主赛道 (前扑 + 20/40cm 台阶)", "x": 0.0, "y": 0.0, "yaw_deg": 0.0, "z_ray": 2.0, "hint": "先按 Space 前向跳扑，再按 C 切上阶模式爬 20cm 台阶！"},
        {"name": "20cm 高台原地直跳位 (按 Space 直接跳上)", "x": 0.0, "y": 2.80, "yaw_deg": 0.0, "z_ray": 2.0, "hint": "正前方 0.745m 即 20cm 高台，直接按 Space 一跃登顶！"},
        {"name": "24cm 极限高台直跳位 (按 Space 直接跳上)", "x": 0.0, "y": 5.40, "yaw_deg": 0.0, "z_ray": 2.0, "hint": "正前方 0.725m 即 24cm 高台，按 Space 平机身跃上！"},
        {"name": "200mm 标准单阶攀爬位 (按 C + W 优雅上阶)", "x": 0.0, "y": -2.80, "yaw_deg": 0.0, "z_ray": 2.0, "hint": "按 C 开启 E1 上阶专家，按住 W 以 0.47m/s 稳定攀爬并驻车！"},
        {"name": "限高杆钻洞 + 连续阶梯道 (按 1 钻杆)", "x": 0.0, "y": -5.40, "yaw_deg": 0.0, "z_ray": 2.0, "hint": "先按 1 压低至 0.20m 钻过 31.5cm 限高杆，再按 2 恢复！"},
    ]
    return {"xml_path": str(xml_path), "mjb_path": None, "spawns": spawns, "hide_group5": False, "hfield_array": None}


def build_rmuc2027() -> dict[str, Any]:
    """Official RMUC2027 full 3D visual + tiled collision map with binary .mjb cache for instant reload."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    xml_path = CACHE_DIR / "scene_rmuc2027_mod4v3_v1.xml"
    mjb_path = CACHE_DIR / "scene_rmuc2027_mod4v3_v1.mjb"

    if not xml_path.exists() or not mjb_path.exists():
        tree, root = _load_base_robot_tree()
        ET.SubElement(root, "size", memory="96M")
        wb = root.find("worldbody")
        old_ground = wb.find("geom[@name='ground']")
        if old_ground is not None:
            wb.remove(old_ground)
        asset = root.find("asset")
        ET.SubElement(
            asset,
            "texture",
            name="rmuc_sky",
            type="skybox",
            builtin="gradient",
            rgb1="0.25 0.36 0.50",
            rgb2="0.06 0.08 0.12",
            width="512",
            height="3072",
        )

        f_tree = ET.parse(RMUC_DIR / "scene_rmuc_tiled.xml")
        f_root = f_tree.getroot()
        rmuc_prefix = RMUC_DIR.as_posix().rstrip("/") + "/"
        for el in f_root.find("asset"):
            if "file" in el.attrib:
                el.set("file", rmuc_prefix + el.get("file"))
            asset.append(el)
        for el in f_root.find("worldbody"):
            geoms = [el] if el.tag == "geom" else list(el.iter("geom"))
            for g in geoms:
                if g.get("contype") not in (None, "0"):
                    g.set("contype", "1")
                    g.set("conaffinity", "3")
                    g.set("group", "5")
                    g.set("rgba", "0.2 0.4 0.6 0.05")
            wb.append(el)

        tree.write(xml_path, encoding="utf-8", xml_declaration=True)
        m_tmp = mj.MjModel.from_xml_path(str(xml_path))
        mj.mj_saveModel(m_tmp, str(mjb_path), None)

    spawns = [
        {"name": "红方前场大道 (-1.8, -3.0)", "x": -1.80, "y": -3.00, "yaw_deg": 180.0, "z_ray": 4.5, "hint": "RMUC2027 红方主干道，视野开阔可自由跑图与跳扑"},
        {"name": "蓝方前场大道 (-20.5, -4.0)", "x": -20.50, "y": -4.00, "yaw_deg": 0.0, "z_ray": 4.5, "hint": "RMUC2027 蓝方主干道，直通中央资源岛与坡道"},
        {"name": "中央高地西坡台阶口 (-16.8, -4.0)", "x": -16.80, "y": -4.00, "yaw_deg": 0.0, "z_ray": 4.5, "hint": "正对中央高地坡道/台阶入口"},
        {"name": "中央高地东坡台阶口 (-5.6, -5.9)", "x": -5.60, "y": -5.90, "yaw_deg": 180.0, "z_ray": 4.5, "hint": "正对东侧高地台阶与坡道"},
        {"name": "中央高地 30cm 平台顶 (-10.0, -3.0)", "x": -10.00, "y": -3.00, "yaw_deg": -90.0, "z_ray": 4.5, "hint": "位于中央 30cm 高台顶部，可测试巡航与下台阶"},
        {"name": "红方狗洞隧道入口 (-13.6, +0.99)", "x": -13.60, "y": 0.99, "yaw_deg": 0.0, "z_ray": 0.80, "hint": "按 1 将站高压低至 0.20m 即可钻入低矮隧道！"},
        {"name": "蓝方 40cm 高台出发区 (-23.5, -2.0)", "x": -23.50, "y": -2.00, "yaw_deg": 0.0, "z_ray": 4.5, "hint": "位于 40cm 高台区，可体验高台飞跃下阶"},
    ]
    return {"xml_path": str(xml_path), "mjb_path": str(mjb_path), "spawns": spawns, "hide_group5": True, "hfield_array": None}


def build_parkour_sirina() -> dict[str, Any]:
    """Open-source Sirina / rc_mjlab multi-obstacle parkour arena."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    xml_path = CACHE_DIR / "scene_parkour_sirina_mod4v3_v1.xml"
    tree, root = _load_base_robot_tree()
    wb = root.find("worldbody")
    old_ground = wb.find("geom[@name='ground']")
    if old_ground is not None:
        wb.remove(old_ground)
    asset = root.find("asset")

    p_tree = ET.parse(RC_MJLAB_TERRAIN_DIR / "scene_terrain.xml")
    p_root = p_tree.getroot()
    terrain_dir = RC_MJLAB_TERRAIN_DIR.as_posix().rstrip("/") + "/"

    for el in p_root.find("asset"):
        if el.tag == "hfield" and "file" in el.attrib:
            fname = Path(el.get("file")).name
            el.set("file", terrain_dir + fname)
        asset.append(el)

    for el in p_root.find("worldbody"):
        if el.tag == "geom":
            if el.get("contype") == "0" and el.get("conaffinity") == "0":
                wb.append(el)
                continue
            el.set("contype", "1")
            el.set("conaffinity", "2")
            if "friction" not in el.attrib:
                el.set("friction", "0.9 0.005 0.0001")
        wb.append(el)

    tree.write(xml_path, encoding="utf-8", xml_declaration=True)
    spawns = [
        {"name": "跑酷出发区广场 (3.7, -9.0)", "x": 3.70, "y": -9.00, "yaw_deg": 90.0, "z_ray": 3.0, "hint": "Sirina 跑酷标准出发区：周边有 10° 宽斜坡、限高杆、T 型台阶与绕杆桩"},
        {"name": "T 型 10cm 梯形台阶前 (1.8, -5.6)", "x": 1.80, "y": -5.60, "yaw_deg": 90.0, "z_ray": 3.0, "hint": "正对 3 级 10cm T 型楼梯（总高 40cm）"},
        {"name": "斜坡木桥挑战口 (1.8, -1.75)", "x": 1.80, "y": -1.75, "yaw_deg": 90.0, "z_ray": 3.0, "hint": "上坡进入断续木桥 A/B 与高台折返走廊"},
        {"name": "32.5cm 限高杆前 (4.35, -9.0)", "x": 4.35, "y": -9.00, "yaw_deg": 0.0, "z_ray": 3.0, "hint": "按 1 压低站高至 0.20m 从限高杆下钻过！"},
        {"name": "5cm 连续双向阶梯前 (0.2, +2.0)", "x": 0.20, "y": 2.00, "yaw_deg": 0.0, "z_ray": 3.0, "hint": "正对 8 级 5cm 连续升降阶梯（顶高 40cm）"},
        {"name": "10° 宽幅双斜坡前 (3.4, -5.0)", "x": 3.40, "y": -5.00, "yaw_deg": 0.0, "z_ray": 3.0, "hint": "正对 4m 宽 10° 上下坡道"},
        {"name": "碎石块与起伏高度场 (-2.8, +4.0)", "x": -2.80, "y": 4.00, "yaw_deg": 0.0, "z_ray": 3.0, "hint": "前方为 Perlin 起伏地形与随机倾角乱石阵"},
    ]
    return {"xml_path": str(xml_path), "mjb_path": None, "spawns": spawns, "hide_group5": False, "hfield_array": None}


def build_serial_leg_course(sub_scene: str) -> dict[str, Any]:
    """Open-source Serial_Leg_Simulation courses: 17° ramp + gravel hfield, or 5/7/10/15/20cm step scenes."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    safe_tag = sub_scene.split()[0].replace("°", "deg")
    xml_path = CACHE_DIR / f"scene_serial_{safe_tag}_v1.xml"
    tree, root = _load_base_robot_tree()
    _add_checker_sky_and_floor(root, floor_size="25 25 0.05", add_floor=True)
    asset = root.find("asset")
    wb = root.find("worldbody")

    if "17°" in sub_scene:
        ET.SubElement(
            asset,
            "mesh",
            name="ramp_17deg",
            vertex="0 -1.5 0  0 1.5 0  1.144798416 -1.5 0  1.144798416 1.5 0  1.144798416 -1.5 .35  1.144798416 1.5 .35",
            face="0 1 3  0 3 2  0 4 5  0 5 1  2 3 5  2 5 4  0 2 4  1 5 3",
        )
        gravel_png = (SERIAL_LEG_DIR / "mjcf/ramp17_gravel.png").as_posix()
        ET.SubElement(asset, "hfield", name="gravel_height", file=gravel_png, size="2.5 2.5 0.08 0.04")
        ET.SubElement(wb, "geom", name="ramp_up", type="mesh", mesh="ramp_17deg", pos="1.4 0 0", contype="1", conaffinity="2", rgba="0.58 0.63 0.67 1")
        ET.SubElement(wb, "geom", name="ramp_plat", type="box", pos="3.35 0 0.175", size="0.805 1.5 0.175", contype="1", conaffinity="2", rgba="0.50 0.56 0.62 1")
        ET.SubElement(wb, "geom", name="gravel_zone", type="hfield", hfield="gravel_height", pos="3.2 3.2 0", contype="1", conaffinity="2", rgba="0.48 0.53 0.59 1")
        spawns = [
            {"name": "17° 陡坡正前方 (0.0, 0.0)", "x": 0.0, "y": 0.0, "yaw_deg": 0.0, "z_ray": 2.0, "hint": "正对开源 Serial_Leg 17° 坡道 + 35cm 高台"},
            {"name": "碎石高度场入口 (0.2, 3.2)", "x": 0.20, "y": 3.20, "yaw_deg": 0.0, "z_ray": 2.0, "hint": "正对 ramp17_gravel 碎石起伏区"},
        ]
    else:
        cm = int(sub_scene.split("cm")[0].strip())
        h_m = cm / 100.0
        ET.SubElement(
            wb,
            "geom",
            name=f"serial_step_{cm}cm",
            type="box",
            pos=f"2.00 0.0 {h_m / 2:.4f}",
            size=f"1.00 1.40 {h_m / 2:.4f}",
            contype="1",
            conaffinity="2",
            friction="0.9 0.005 0.0001",
            rgba="0.36 0.52 0.66 1.0",
        )
        spawns = [
            {"name": f"Serial_Leg {cm}cm 台阶前 (0.0, 0.0)", "x": 0.0, "y": 0.0, "yaw_deg": 0.0, "z_ray": 2.0, "hint": f"前方 x=1.0m 为 {cm}cm 台阶，可试 E0 直冲 / E1 攀爬 / Space 跳扑"},
        ]

    tree.write(xml_path, encoding="utf-8", xml_declaration=True)
    return {"xml_path": str(xml_path), "mjb_path": None, "spawns": spawns, "hide_group5": False, "hfield_array": None}


def build_stairs_matrix(preset_label: str) -> dict[str, Any]:
    """Dedicated stair & platform difficulty scene (5cm..24cm + continuous 2-step 20+20cm)."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tree, root = _load_base_robot_tree()
    _add_checker_sky_and_floor(root, floor_size="25 25 0.05", add_floor=True)
    wb = root.find("worldbody")

    if "连续双阶" in preset_label:
        tag = "2step_20_40"
        ET.SubElement(wb, "geom", name="step_1_20cm", type="box", pos="1.95 0 0.10", size="0.75 1.30 0.10", contype="1", conaffinity="2", friction="0.9 0.005 0.0001", rgba="0.30 0.44 0.58 1")
        ET.SubElement(wb, "geom", name="step_2_40cm", type="box", pos="3.60 0 0.20", size="0.90 1.30 0.20", contype="1", conaffinity="2", friction="0.9 0.005 0.0001", rgba="0.38 0.54 0.68 1")
        spawns = [
            {"name": "攀爬起点 (距一级阶 1.20m)", "x": 0.0, "y": 0.0, "yaw_deg": 0.0, "z_ray": 2.0, "hint": "20cm + 20cm (1.5m 踏面) 连续双台阶：可按 C 上阶或 Space 连续跳扑！"},
            {"name": "原地直跳起点 (距一级阶 0.745m)", "x": 0.455, "y": 0.0, "yaw_deg": 0.0, "z_ray": 2.0, "hint": "直接按 Space 跃上一级 20cm 台，再前移按 Space 跃上 40cm 台！"},
        ]
    else:
        cm = int(preset_label.split("cm")[0].strip())
        tag = f"single_{cm}cm"
        h_m = cm / 100.0
        front_x = 1.20
        half_l = 1.20
        ET.SubElement(
            wb,
            "geom",
            name=f"matrix_step_{cm}cm",
            type="box",
            pos=f"{front_x + half_l:.3f} 0.0 {h_m / 2:.4f}",
            size=f"{half_l:.3f} 1.30 {h_m / 2:.4f}",
            contype="1",
            conaffinity="2",
            friction="0.9 0.005 0.0001",
            rgba="0.32 0.48 0.62 1.0",
        )
        jump_dist = 0.72 if cm <= 20 else 0.69
        spawns = [
            {"name": f"标准助跑/攀爬位 (距阶沿 1.20m)", "x": 0.0, "y": 0.0, "yaw_deg": 0.0, "z_ray": 2.0, "hint": f"{cm}cm 单阶：按 C+W 用 E1 轮腿攀爬，或助跑按 Space 跳上"},
            {"name": f"原地直跳黄金位 (距阶沿 {jump_dist:.3f}m)", "x": round(front_x - jump_dist, 3), "y": 0.0, "yaw_deg": 0.0, "z_ray": 2.0, "hint": f"无需助跑，原地直接按 Space 用 E2 平机身跃上 {cm}cm 高台！"},
            {"name": "五起点测试: -60mm 偏置", "x": -0.060, "y": 0.0, "yaw_deg": 0.0, "z_ray": 2.0, "hint": "官方评测 -60mm 起点"},
            {"name": "五起点测试: +60mm 偏置", "x": 0.060, "y": 0.0, "yaw_deg": 0.0, "z_ray": 2.0, "hint": "官方评测 +60mm 起点"},
        ]

    xml_path = CACHE_DIR / f"scene_stairs_{tag}_v1.xml"
    tree.write(xml_path, encoding="utf-8", xml_declaration=True)
    return {"xml_path": str(xml_path), "mjb_path": None, "spawns": spawns, "hide_group5": False, "hfield_array": None}


def _rough_meshfile(tile: str) -> Path:
    p = ROUGH_VIEWER_DIR / "mesh" / f"{tile}.msh"
    if p.exists():
        return p
    out_dir = CACHE_DIR / "rough_mesh"
    out_dir.mkdir(parents=True, exist_ok=True)
    p_local = out_dir / f"{tile}.msh"
    if not p_local.exists():
        a = np.load(ROUGH_VIEWER_DIR / "tiles" / f"{tile}.npz")
        v, f = a["vertices"], a["faces"]
        if np.ptp(v[:, 2]) < 1e-7:
            n = len(v)
            v = np.vstack((v, [[0, 0, -0.02], [0.01, 0, -0.02], [0, 0.01, -0.02], [0, 0, -0.03]])).astype(np.float32)
            f = np.vstack((f, [[n, n + 1, n + 2], [n, n + 3, n + 1], [n, n + 2, n + 3], [n + 1, n + 3, n + 2]])).astype(np.int32)
        with p_local.open("wb") as fh:
            fh.write(struct.pack("<4i", len(v), 0, 0, len(f)))
            fh.write(v.astype("<f4").tobytes())
            fh.write(f.astype("<i4").tobytes())
    return p_local


def _rough_heightfield(tile: str) -> np.ndarray:
    orig_cache = ROUGH_VIEWER_DIR / f"{tile}_hf_v2.npz"
    if orig_cache.exists():
        return np.load(orig_cache)["h"]
    local_cache = CACHE_DIR / f"{tile}_hf_v2.npz"
    if local_cache.exists():
        return np.load(local_cache)["h"]
    mpath = _rough_meshfile(tile)
    m = mj.MjModel.from_xml_string(
        f'<mujoco><asset><mesh name="t" file="{mpath.as_posix()}"/></asset>'
        f'<worldbody><geom type="mesh" mesh="t"/></worldbody></mujoco>'
    )
    d = mj.MjData(m)
    mj.mj_forward(m, d)
    grid = np.linspace(-4.5, 4.5, 181)
    h = np.zeros((181, 181))
    vec = np.array([0.0, 0.0, -1.0])
    pt = np.array([0.0, 0.0, 10.0])
    gid = np.zeros(1, dtype=np.int32)
    for iy, y in enumerate(grid):
        for ix, x in enumerate(grid):
            pt[:2] = np.clip([x + 1.7e-5, y + 2.9e-5], -4.5 + 1e-4, 4.5 - 1e-4)
            dist = mj.mj_ray(m, d, pt, vec, None, True, -1, gid)
            h[iy, ix] = 10.0 - dist if dist >= 0 else 0.0
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(local_cache, h=h)
    return h


def build_rough_v1_tile(family_cn: str, level: int) -> dict[str, Any]:
    """Build any of the 11 Rough-v1 terrain families x Levels 0..9 without touching frozen viewer files."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    idx = ROUGH_CN.index(family_cn) if family_cn in ROUGH_CN else 0
    family = ROUGH_FAMILIES[idx]
    level = int(np.clip(level, 0, 9))
    tile = f"r{level:02d}_c{ROUGH_COLS[family]:02d}"

    a = np.load(ROUGH_VIEWER_DIR / "tiles" / f"{tile}.npz")
    v = a["vertices"]

    tree, root = _load_base_robot_tree()
    wb = root.find("worldbody")
    old_ground = wb.find("geom[@name='ground']")
    if old_ground is not None:
        wb.remove(old_ground)
    asset = root.find("asset")
    ET.SubElement(
        asset,
        "texture",
        name="rough_sky",
        type="skybox",
        builtin="gradient",
        rgb1="0.22 0.32 0.44",
        rgb2="0.06 0.09 0.14",
        width="512",
        height="3072",
    )
    ET.SubElement(asset, "mesh", name="tile_visual", file=str(_rough_meshfile(tile)))
    ET.SubElement(wb, "geom", type="mesh", mesh="tile_visual", contype="0", conaffinity="0", rgba=ROUGH_COLORS[idx], group="1")
    # Safety surrounding apron outside the 9x9m tile
    ET.SubElement(wb, "geom", name="safety_apron", type="plane", pos="0 0 -0.8", size="20 20 0.05", contype="1", conaffinity="2", rgba="0.12 0.15 0.18 1")

    hf_arr = None
    if family in (ROUGH_FAMILIES[0], ROUGH_FAMILIES[4]):
        ET.SubElement(wb, "geom", name="ground", type="box", pos="0 0 -0.10", size="4.5 4.5 0.10", contype="1", conaffinity="2", group="5")
        for k, z in enumerate(np.unique(v[:, 2])):
            if z <= 1e-6:
                continue
            top = v[v[:, 2] >= z - 1e-6]
            lo = top[:, :2].min(0)
            hi = top[:, :2].max(0)
            center = (lo + hi) * 0.5
            half = (hi - lo) * 0.5
            ET.SubElement(
                wb,
                "geom",
                name=f"step_{k}",
                type="box",
                pos=f"{center[0]} {center[1]} {z / 2}",
                size=f"{half[0]} {half[1]} {z / 2}",
                contype="1",
                conaffinity="2",
                group="5",
            )
    else:
        hf_arr = _rough_heightfield(tile)
        mn = float(hf_arr.min())
        span = max(float(hf_arr.max() - mn), 0.001)
        ET.SubElement(asset, "hfield", name="tile_collision", nrow="181", ncol="181", size=f"4.5 4.5 {span} 0.2")
        ET.SubElement(wb, "geom", name="ground", type="hfield", hfield="tile_collision", pos=f"0 0 {mn}", contype="1", conaffinity="2", group="5")

    xml_path = CACHE_DIR / f"scene_rough_{tile}_v1.xml"
    tree.write(xml_path, encoding="utf-8", xml_declaration=True)
    spawns = [
        {"name": "边缘上行 / 跑图起点 (-3.85, 0.0)", "x": -3.85, "y": 0.0, "yaw_deg": 0.0, "z_ray": 4.0, "hint": f"Rough-v1 [{family_cn}] 难度 L{level}：向 +X 穿越地形块"},
        {"name": "中心高点 / 下行起点 (+0.25, 0.0)", "x": 0.25, "y": 0.0, "yaw_deg": 0.0, "z_ray": 4.0, "hint": f"Rough-v1 [{family_cn}] 难度 L{level}：从中心高台出发下阶/下坡"},
    ]
    return {"xml_path": str(xml_path), "mjb_path": None, "spawns": spawns, "hide_group5": True, "hfield_array": hf_arr}
