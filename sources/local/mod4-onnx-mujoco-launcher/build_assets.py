"""Build a self-contained MuJoCo scene around the corrected rolling MOD4 model."""
from __future__ import annotations

import copy
import math
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent
SOURCE_XML = WORKSPACE / "chassis_mod4_work" / "folded_pose_sim" / "scene_tunnel_247p2_drive.xml"
SOURCE_ASSETS = WORKSPACE / "chassis_mod4" / "assets"
MODEL_DIR = ROOT / "model"


def f(values) -> str:
    return " ".join(f"{float(v):.9g}" for v in values)


def add_box(world, name, full_size, pos, rgba, quat=None, friction=(0.9, 0.003, 0.0001)):
    attrs = {
        "name": name, "type": "box", "size": f([x / 2 for x in full_size]),
        "pos": f(pos), "rgba": f(rgba), "contype": "1", "conaffinity": "2",
        "friction": f(friction), "solref": ".0012 1", "solimp": ".99 .999 .0001",
    }
    if quat is not None:
        attrs["quat"] = f(quat)
    return ET.SubElement(world, "geom", attrs)


def add_ramp(world, name, start_x, y, width, run, rise, direction, color):
    angle = math.atan2(rise, run) * direction
    length = math.hypot(run, rise)
    # A thin box whose local +X follows the incline.  R_y(-angle) rises towards +X.
    quat = (math.cos(angle / 2), 0.0, -math.sin(angle / 2), 0.0)
    center_x = start_x + direction * run / 2
    add_box(world, name, (length, width, 0.05), (center_x, y, rise / 2), color, quat)


def add_field(world):
    # Measured RMUC2026 dimensions used by the Isaac training map.  The layout is compact so it
    # is practical to drive by hand, while each obstacle keeps its task dimension and collision.
    ET.SubElement(world, "geom", {
        "name": "arena_floor", "type": "plane", "size": "15 8 .1", "rgba": ".24 .27 .31 1",
        "contype": "1", "conaffinity": "2", "friction": ".9 .003 .0001",
        "solref": ".0012 1", "solimp": ".99 .999 .0001",
    })
    # Lane markings are visual-only and make navigation in the free camera easier.
    for y, color in ((0.0, (.85, .75, .18, .5)), (-2.5, (.28, .65, .95, .35)),
                     (2.5, (.30, .85, .45, .35)), (-4.8, (.95, .45, .22, .35)),
                     (4.8, (.70, .45, .90, .35))):
        ET.SubElement(world, "geom", {"name": f"lane_{str(y).replace('.', '_').replace('-', 'm')}",
            "type": "box", "size": "14.5 .018 .001", "pos": f((0, y, .001)),
            "rgba": f(color), "contype": "0", "conaffinity": "0", "group": "1"})

    # 247.2 mm clear dog hole, 800 mm clear width, 300 mm deep.
    tx, ty, depth, hole_w, hole_h, total_w = 1.5, 0.0, .30, .80, .2472, 1.50
    side_w = (total_w - hole_w) / 2
    wall_h = 1.00
    add_box(world, "tunnel_left", (depth, side_w, wall_h),
            (tx, ty + hole_w / 2 + side_w / 2, wall_h / 2), (.82, .30, .20, 1))
    add_box(world, "tunnel_right", (depth, side_w, wall_h),
            (tx, ty - hole_w / 2 - side_w / 2, wall_h / 2), (.82, .30, .20, 1))
    add_box(world, "tunnel_roof", (depth, total_w, .18),
            (tx, ty, hole_h + .09), (.90, .38, .22, 1))

    # Two-step lane: 100/200 mm levels and mirrored descent.
    sx, sy, run, width = -1.7, -2.5, .38, 1.35
    for i, h in enumerate((.10, .20, .20, .10)):
        add_box(world, f"stair_{i+1}", (run, width, h),
                (sx + (i + .5) * run, sy, h / 2), (.34, .55, .78, 1))

    # 25 degree climb, platform, and measured 12.1 degree descent.
    ry, h = 2.5, .20
    run_up = h / math.tan(math.radians(25.0))
    add_ramp(world, "ramp_25_up", -2.0, ry, 1.35, run_up, h, +1, (.30, .70, .43, 1))
    px = -2.0 + run_up + .55
    add_box(world, "ramp_platform", (1.1, 1.35, h), (px, ry, h / 2), (.34, .63, .43, 1))
    run_down = h / math.tan(math.radians(12.1))
    add_ramp(world, "ramp_12_down", px + .55, ry, 1.35, run_down, h, -1, (.36, .68, .46, 1))

    # Fly-ramp lane.  The arena floor is the 180 mm-deep bottom and the banks define the gap.
    fy, bank_h = -4.8, .18
    add_box(world, "fly_bank_before", (3.0, 1.35, bank_h), (-3.3, fy, bank_h / 2), (.62, .46, .28, 1))
    launch_run = bank_h / math.tan(math.radians(20.0))
    add_ramp(world, "fly_launch", -1.8, fy, 1.35, launch_run, bank_h, +1, (.84, .48, .20, 1))
    landing_start = -1.8 + launch_run + .34
    add_box(world, "fly_bank_after", (3.2, 1.35, bank_h),
            (landing_start + 1.6, fy, bank_h / 2), (.62, .46, .28, 1))

    # Continuous-looking rough lane from shallow 20--60 mm blocks.
    bx, by = -4.8, 4.8
    for i in range(12):
        h = .02 + .02 * (i % 3)
        add_box(world, f"rough_{i:02d}", (.30, 1.20, h),
                (bx + i * .32, by, h / 2), (.58, .42 + .02 * (i % 3), .70, 1))

    # Two-level centre island and the extra 50 mm ring on its upper deck.
    ix, iy, l1, l2 = 5.0, 3.1, .18, .36
    add_box(world, "island_level1", (2.0, 2.0, l1), (ix, iy, l1 / 2), (.42, .52, .60, 1))
    add_box(world, "island_level2", (1.30, 1.30, l2), (ix, iy, l2 / 2), (.35, .47, .56, 1))
    lip_h, lip_t = .05, .05
    for name, size, pos in (
        ("island_lip_n", (1.30, lip_t, lip_h), (ix, iy + .625, l2 + lip_h / 2)),
        ("island_lip_s", (1.30, lip_t, lip_h), (ix, iy - .625, l2 + lip_h / 2)),
        ("island_lip_e", (lip_t, 1.20, lip_h), (ix + .625, iy, l2 + lip_h / 2)),
        ("island_lip_w", (lip_t, 1.20, lip_h), (ix - .625, iy, l2 + lip_h / 2)),
    ):
        add_box(world, name, size, pos, (.72, .44, .20, 1))

    # Real-height 416 mm barricade used for avoidance / jump experiments.
    add_box(world, "barricade_416", (.24, 1.60, .416), (5.0, -3.0, .208), (.72, .20, .18, 1))


def build(headless: bool) -> Path:
    tree = ET.parse(SOURCE_XML)
    root = tree.getroot()
    root.set("model", "MOD4 ONNX RMUC2026 manual arena" + (" headless" if headless else ""))
    compiler = root.find("compiler")
    compiler.set("meshdir", "assets")
    visual = root.find("visual")
    if visual is not None:
        visual.find("global").set("azimuth", "145")
        visual.find("global").set("elevation", "-24")
    stat = root.find("statistic")
    stat.set("center", "0 0 .3")
    stat.set("extent", "8")
    world = root.find("worldbody")
    for geom in list(world.findall("geom")):
        if geom.get("name") in {"ground", "tunnel_roof_247p2"}:
            world.remove(geom)
    chassis = world.find("body[@name='chassis']")
    world.remove(chassis)
    add_field(world)
    # Spawn on the straight lane before the tunnel; user can teleport to other lanes.
    chassis.set("pos", "-4 0 0.337742301121")
    if not headless:
        ET.SubElement(chassis, "camera", {"name": "follow", "mode": "trackcom",
            "pos": "-2.5 -3 1.5", "xyaxes": ".75 -.66 0 .22 .25 .94"})
    world.append(chassis)

    if headless:
        # Collision/inertia/topology remain identical; only 277 CAD render geoms and their mesh
        # assets are removed.  This makes the randomized batch test load and step much faster.
        for parent in root.iter():
            for child in list(parent):
                if child.tag == "geom" and child.get("class") == "visual":
                    parent.remove(child)
        asset = root.find("asset")
        for child in list(asset):
            if child.tag == "mesh":
                asset.remove(child)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    out = MODEL_DIR / ("rm_training_arena_headless.xml" if headless else "rm_training_arena.xml")
    ET.indent(tree, space="  ")
    tree.write(out, encoding="utf-8", xml_declaration=True)
    return out


def main():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    dest_assets = MODEL_DIR / "assets"
    if dest_assets.exists():
        shutil.rmtree(dest_assets)
    shutil.copytree(SOURCE_ASSETS, dest_assets)
    shutil.copy2(SOURCE_XML, MODEL_DIR / "source_rolling_model.xml")
    print(build(False))
    print(build(True))


if __name__ == "__main__":
    main()
