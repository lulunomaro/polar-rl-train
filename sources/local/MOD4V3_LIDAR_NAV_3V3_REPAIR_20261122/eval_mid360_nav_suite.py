"""End-to-End 400 Hz Verification Suite for Livox Mid-360 Point-Cloud Mapping, Stair Detection & Dynamic Replanning."""
from __future__ import annotations

import json
import math
import time
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import mujoco as mj
from PIL import Image, ImageDraw
import imageio.v2 as imageio

from nav_common import HERE, put
from nav4d_runtime import Nav4DPolicy, Nav4DSimulation


class Mid360VideoRecorder:
    """25 fps (1x) MuJoCo renderer overlaying live 3D Mid-360 point cloud, planned A* path, and telemetry."""

    def __init__(self, path: Path, title: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.writer = imageio.get_writer(self.path, fps=25, codec="libx264", quality=8, macro_block_size=16)
        self.renderer = None
        self.counter = 0
        self.frames = 0
        self.title = title

    def __call__(self, sim: Nav4DSimulation):
        self.counter += 1
        if self.counter % 16 != 0:
            return
        if self.renderer is None:
            self.renderer = mj.Renderer(sim.m, height=720, width=1280)
        option = mj.MjvOption()
        option.geomgroup[4] = 1
        option.geomgroup[1] = 1
        option.geomgroup[3] = 0 if sim.scene_meta.get("course") == "suite_rmul2027" else 1
        if sim.scene_meta.get("hide_group5"):
            option.geomgroup[5] = 0

        x, y, yaw = sim.pose()
        m = sim.measure()
        cam = mj.MjvCamera()
        cam.type = mj.mjtCamera.mjCAMERA_FREE
        cam.lookat[:] = [x + 0.35 * math.cos(yaw), y + 0.35 * math.sin(yaw), float(sim.d.qpos[2]) + 0.12]
        cam.distance = 3.8
        cam.azimuth = 132.0
        cam.elevation = -28.0

        self.renderer.update_scene(sim.d, camera=cam, scene_option=option)
        scn = self.renderer.scene
        # Overlay planned A* waypoints + live 3D Mid-360 point cloud into offscreen MjvScene
        eye9 = np.eye(3).ravel()
        for p in sim.planned_path[:120]:
            if scn.ngeom >= scn.maxgeom - 6:
                break
            zp = float(sim.elevation.sample(*p)) + 0.035
            if not np.isfinite(zp):
                continue
            mj.mjv_initGeom(
                scn.geoms[scn.ngeom],
                mj.mjtGeom.mjGEOM_SPHERE,
                np.array([0.03, 0.03, 0.03]),
                np.array([p[0], p[1], zp], dtype=np.float64),
                eye9,
                np.array([0.2, 0.95, 0.65, 0.9], dtype=np.float32),
            )
            scn.ngeom += 1

        det = sim.mid360_detector
        if det is not None and len(det.last_points_world) > 0:
            pw = det.last_points_world
            d2 = (pw[:, 0] - x) ** 2 + (pw[:, 1] - y) ** 2
            near = pw[(d2 <= 10.0) & (pw[:, 2] <= 1.0)]
            if len(near) > 0:
                step_k = max(1, len(near) // 130)
                z0 = float(sim.ground_z(x, y))
                for pt in near[::step_k]:
                    if scn.ngeom >= scn.maxgeom - 4:
                        break
                    rz = float(pt[2]) - z0
                    if 0.06 <= rz <= 0.265:
                        rgba = np.array([0.18, 0.95, 1.0, 0.88], dtype=np.float32)
                    elif rz > 0.265:
                        rgba = np.array([1.0, 0.36, 0.36, 0.90], dtype=np.float32)
                    else:
                        rgba = np.array([0.35, 0.85, 0.70, 0.55], dtype=np.float32)
                    mj.mjv_initGeom(
                        scn.geoms[scn.ngeom],
                        mj.mjtGeom.mjGEOM_SPHERE,
                        np.array([0.015, 0.015, 0.015]),
                        pt.astype(np.float64),
                        eye9,
                        rgba,
                    )
                    scn.ngeom += 1

        img = Image.fromarray(self.renderer.render().copy())
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, 1280, 72), fill=(14, 23, 32))
        draw.text((18, 12), self.title, fill=(123, 230, 214))
        dyn_c = int(det.last_dyn_cells_count) if det else 0
        st_pts = int(det.last_stair_pts_count) if det else 0
        draw.text(
            (18, 36),
            f"t={sim.d.time:.2f}s  vx={m['vx']:+.2f}m/s  pitch={math.degrees(m['pitch']):+.1f}deg  "
            f"g_step={np.round(sim.last_g, 2)}  Mid360_stair_pts={st_pts}  dyn_cells={dyn_c}  replans={sim.replan_count}",
            fill=(230, 238, 244),
        )
        self.writer.append_data(np.asarray(img))
        self.frames += 1

    def close(self) -> dict:
        self.writer.close()
        if self.renderer is not None:
            self.renderer.close()
        return dict(path=str(self.path), frames=self.frames, fps=25, duration_s=round(self.frames / 25.0, 2))


def run_pcd_prior_missions(policy: Nav4DPolicy) -> dict:
    """Test full A* missions using maps reconstructed PURELY from Livox Mid-360 `.pcd` files."""
    sim = Nav4DSimulation(policy, sensor_mode="mid360_fusion", use_pcd_prior=True)
    suite_goals = {
        "suite_rmul2027": (0, [(-2.5, 0.8), (-2.5, 2.1), (-4.7, 2.1), (-4.9, -2.3)]),
        "suite_rmuc2027": (0, [(-14.0, -4.80), (-13.6, -4.45), (-16.8, -4.85)]),
    }
    results = {}
    for course, (spawn_idx, goals) in suite_goals.items():
        sim.load_scene(course, spawn_idx=spawn_idx, height=0.28)
        assert "mid360_prior" in sim.elevation.npz_path, f"Expected PCD prior map, got {sim.elevation.npz_path}"
        leg_rows = []
        for gx, gy in goals:
            sim.navigate_to(gx, gy, speed=1.05)
            max_pitch = 0.0
            max_roll = 0.0
            e1_ticks = 0
            reached = False
            for _ in range(1100):  # up to 22s per leg
                sim.step(set())
                m = sim.measure()
                max_pitch = max(max_pitch, abs(math.degrees(m["pitch"])))
                max_roll = max(max_roll, abs(math.degrees(m["roll"])))
                if sim.route["e1"] > 0.5:
                    e1_ticks += 1
                if sim.follower is not None and sim.follower.done:
                    reached = True
                    break
                if max_pitch > 65.0 or max_roll > 60.0:
                    break
            x, y, _ = sim.pose()
            dist_goal = math.hypot(x - gx, y - gy)
            leg_rows.append(
                dict(
                    goal=[gx, gy],
                    reached=bool(reached and dist_goal <= 0.35 and max_pitch < 55.0 and max_roll < 45.0),
                    final_dist_m=round(dist_goal, 3),
                    max_pitch_deg=round(max_pitch, 2),
                    max_roll_deg=round(max_roll, 2),
                    e1_ticks=e1_ticks,
                )
            )
        results[course] = dict(
            npz_used=sim.elevation.npz_path,
            passed=sum(1 for r in leg_rows if r["reached"]),
            total=len(leg_rows),
            legs=leg_rows,
        )
    return results


def run_online_mapless_stair_and_false_trigger_suite(policy: Nav4DPolicy) -> dict:
    """Test pure live Mid-360 3D point-cloud stair climbing & ramp/flat non-false-trigger with `prior_map=None`."""
    sim = Nav4DSimulation(policy, sensor_mode="mid360_online", use_pcd_prior=False)
    climb_cases = [
        dict(name="step20_v0.9_h0.28", course="step_20", x=-0.35, y=0.0, yaw=0.0, speed=0.90, height=0.28, target_dz=0.17, steps=280, wasd=True),
        dict(name="step20_v1.6_h0.35", course="step_20", x=-0.65, y=0.0, yaw=0.0, speed=1.60, height=0.35, target_dz=0.17, steps=240, wasd=True),
        dict(name="step20_v2.4_h0.28_highspeed", course="step_20", x=-2.00, y=0.0, yaw=0.0, speed=2.40, height=0.28, target_dz=0.17, steps=260, wasd=True),
        dict(name="oblique20_pos25_v1.1", course="oblique_20", x=-0.35, y=0.0, yaw=0.0, speed=1.10, height=0.28, target_dz=0.17, steps=280, wasd=True),
        dict(name="oblique20_neg25_v1.1", course="oblique_20_negative", x=-0.35, y=0.0, yaw=0.0, speed=1.10, height=0.28, target_dz=0.17, steps=280, wasd=True),
        dict(name="curb11_v1.2", course="curb_11", x=-0.35, y=0.0, yaw=0.0, speed=1.20, height=0.28, target_dz=0.085, steps=240, wasd=True),
        dict(name="rmul2027_west_highland_v1.1", course="suite_rmul2027", x=-2.50, y=-2.30, yaw=90.0, speed=1.10, height=0.28, target_dz=0.17, steps=210, wasd=True),
        dict(name="rmul2027_east_highland_v1.4", course="suite_rmul2027", x=2.50, y=2.30, yaw=-90.0, speed=1.40, height=0.35, target_dz=0.17, steps=190, wasd=True),
    ]
    rows = []
    for tc in climb_cases:
        sim.load_scene(tc["course"], spawn_idx=0, height=tc["height"])
        sim.scene_meta["spawns"] = [dict(x=tc["x"], y=tc["y"], yaw_deg=tc["yaw"], name=tc["name"])]
        sim.reset_at_spawn(0)
        assert sim.mid360_detector.prior_map is None, "Must run with prior_map=None in online_pc mode!"
        z0 = float(sim.measure()["tire_low"])
        max_pitch = 0.0
        max_roll = 0.0
        e1_ticks = 0
        max_stair_pts = 0
        flip = False
        sim.max_vx = tc["speed"]
        for k in range(tc["steps"]):
            active_drive = k < tc["steps"] - 45
            if tc["wasd"]:
                sim.step({"w"} if active_drive else set())
            else:
                sim.step(set(), command=(tc["speed"] if active_drive else 0.0, 0.0))
            m = sim.measure()
            max_pitch = max(max_pitch, abs(math.degrees(m["pitch"])))
            max_roll = max(max_roll, abs(math.degrees(m["roll"])))
            if sim.route["e1"] > 0.5:
                e1_ticks += 1
            max_stair_pts = max(max_stair_pts, sim.mid360_detector.last_stair_pts_count)
            if max_pitch > 68.0 or max_roll > 60.0:
                flip = True
                break
        zf = float(sim.measure()["tire_low"])
        dz = zf - z0
        ok = (not flip) and (dz >= tc["target_dz"]) and (e1_ticks >= 8)
        rows.append(
            dict(
                name=tc["name"],
                passed=bool(ok),
                dz_m=round(dz, 4),
                e1_ticks=e1_ticks,
                max_mid360_stair_pts=max_stair_pts,
                max_pitch_deg=round(max_pitch, 2),
                max_roll_deg=round(max_roll, 2),
            )
        )

    # Zero-false-trigger verification on flat ground (2.5 m/s) & 17-deg ramp (`serial_17`) under noisy Mid-360 scans
    false_checks = []
    for cname, spd in (("flat", 2.50), ("serial_17", 1.10), ("rough_L9", 1.00)):
        sim.load_scene(cname, spawn_idx=0, height=0.28)
        false_e1 = 0
        max_p = 0.0
        for _ in range(250):
            sim.step(set(), command=(spd, 0.0))
            m = sim.measure()
            max_p = max(max_p, abs(math.degrees(m["pitch"])))
            if sim.route["e1"] > 0.5:
                false_e1 += 1
        false_checks.append(dict(course=cname, speed=spd, false_e1_ticks=false_e1, max_pitch_deg=round(max_p, 2), passed=(false_e1 == 0 and max_p < 45.0)))

    return dict(
        online_climbs_passed=sum(1 for r in rows if r["passed"]),
        online_climbs_total=len(rows),
        online_climb_cases=rows,
        zero_false_trigger_passed=sum(1 for r in false_checks if r["passed"]),
        zero_false_trigger_total=len(false_checks),
        zero_false_trigger_cases=false_checks,
    )


def run_dynamic_obstacle_avoidance_and_veto(policy: Nav4DPolicy, video_path: Path | None = None) -> dict:
    """Inject an unmapped 0.46x0.46x0.48m enemy robot on the default A* path in `suite_rmul2027`!"""
    sim = Nav4DSimulation(policy, sensor_mode="mid360_fusion", use_pcd_prior=True)

    # Default path from Southwest (-4.9, -2.3) -> West Highland Top (-2.5, +0.8) runs along (-4.38, -0.54) -> (-2.84, -0.54).
    # Place an unmapped enemy Sentinel robot right on (-3.60, -0.54, 0.25) so Mid-360 detects it & triggers live A* replanning!
    enemy_xy = (-3.60, -0.54)

    def inject_enemy_robot(meta: dict) -> dict:
        src_xml = Path(meta["xml_path"])
        tree = ET.parse(src_xml)
        root = tree.getroot()
        comp = root.find("compiler")
        if comp is not None and not Path(comp.get("meshdir", "")).is_dir():
            for cand_dir in (
                HERE.parents[2] / "deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/plant/MOD4v3_HW300N60_R3/mjcf/assets",
                Path("/home/lc01/Zonglin Li/zonglin2/plant/MOD4v3_HW300N60_R3/mjcf/assets"),
                Path("/home/lc01/Zonglin Li/zonglin2/assets"),
            ):
                if cand_dir.is_dir():
                    comp.set("meshdir", str(cand_dir))
                    break
        for elem in root.findall(".//mesh"):
            f_attr = elem.get("file", "")
            if "assets/rmul2027/" in f_attr.replace("\\", "/"):
                elem.set("file", str(HERE / "assets/rmul2027" / Path(f_attr.replace("\\", "/")).name))
        wb = root.find("worldbody")
        body = ET.SubElement(wb, "body", name="unmapped_enemy_sentinel", mocap="true", pos=f"{enemy_xy[0]} {enemy_xy[1]} 0.25")
        ET.SubElement(
            body,
            "geom",
            name="enemy_chassis_box",
            type="box",
            size="0.23 0.23 0.24",
            rgba="0.92 0.25 0.28 1.0",
            contype="1",
            conaffinity="3",
            group="1",
        )
        tmp_xml = HERE / "maps" / "wasd" / "_tmp_rmul2027_with_enemy.xml"
        tmp_mjb = HERE / "maps" / "wasd" / "_tmp_rmul2027_with_enemy.mjb"
        tree.write(tmp_xml, encoding="utf-8", xml_declaration=True)
        m_tmp = mj.MjModel.from_xml_path(str(tmp_xml))
        mj.mj_saveModel(m_tmp, str(tmp_mjb), None)
        out = dict(meta)
        out["xml_path"] = str(tmp_xml)
        out["mjb_path"] = str(tmp_mjb)
        return out

    sim.load_scene("suite_rmul2027", spawn_idx=0, height=0.28, extra_xml_mutator=inject_enemy_robot)
    # Start enemy hidden below floor so initial A* plans straight through (-3.55, -2.20),
    # then pop enemy onto the corridor at step 12 (t=0.24s) to verify live mid-drive Mid-360 detection & A* replanning!
    sim.d.mocap_pos[0] = [enemy_xy[0], enemy_xy[1], -2.0]
    mj.mj_forward(sim.m, sim.d)
    sim.mid360_detector.reset(*sim.pose()[:2])
    goal = (-2.5, 0.8)
    sim.navigate_to(*goal, speed=1.00)

    rec = Mid360VideoRecorder(video_path, "Livox Mid-360: Sudden Enemy Pop-Up Detour + 200mm Highland Climb (1x)") if video_path else None
    if rec is not None:
        sim.physics_observer = rec

    min_enemy_clearance_m = 99.0
    false_e1_near_enemy = 0
    climbed_e1_ticks = 0
    max_dyn_cells = 0
    max_pitch = 0.0
    reached = False

    for step_i in range(900):  # up to 18s
        if step_i == 12:
            sim.d.mocap_pos[0] = [enemy_xy[0], enemy_xy[1], 0.25]
            mj.mj_forward(sim.m, sim.d)
        sim.step(set())
        x, y, _ = sim.pose()
        m = sim.measure()
        max_pitch = max(max_pitch, abs(math.degrees(m["pitch"])))
        d_enemy_cur = math.hypot(x - enemy_xy[0], y - enemy_xy[1])
        if step_i >= 12:
            min_enemy_clearance_m = min(min_enemy_clearance_m, d_enemy_cur)
        max_dyn_cells = max(max_dyn_cells, sim.mid360_detector.last_dyn_cells_count)
        if sim.route["e1"] > 0.5:
            if step_i >= 12 and d_enemy_cur < 0.85:
                false_e1_near_enemy += 1
            else:
                climbed_e1_ticks += 1
        if sim.follower is not None and sim.follower.done:
            reached = True
            # Record 0.5s stable parking on highland top
            for _ in range(25):
                sim.step(set())
            break

    vid_meta = rec.close() if rec is not None else None
    sim.physics_observer = None
    # Clean temporary scene files
    for suffix in (".xml", ".mjb"):
        p = HERE / "maps" / "wasd" / f"_tmp_rmul2027_with_enemy{suffix}"
        p.unlink(missing_ok=True)

    fx, fy, _ = sim.pose()
    final_dist = math.hypot(fx - goal[0], fy - goal[1])
    final_z = float(sim.measure()["tire_low"])
    passed = (
        reached
        and final_dist <= 0.35
        and final_z >= 0.17
        and min_enemy_clearance_m >= 0.44
        and false_e1_near_enemy == 0
        and max_dyn_cells >= 4
        and sim.replan_count >= 1
        and max_pitch < 48.0
    )
    return dict(
        passed=bool(passed),
        reached=bool(reached),
        final_pose=[round(fx, 3), round(fy, 3), round(final_z, 3)],
        final_dist_to_goal_m=round(final_dist, 3),
        min_enemy_center_dist_m=round(min_enemy_clearance_m, 3),
        max_detected_dyn_cells=max_dyn_cells,
        astar_replan_count=sim.replan_count,
        false_stair_ticks_near_enemy=false_e1_near_enemy,
        highland_stair_e1_ticks=climbed_e1_ticks,
        max_pitch_deg=round(max_pitch, 2),
        video=vid_meta,
    )


def main() -> None:
    t0 = time.perf_counter()
    policy = Nav4DPolicy()
    print("[1/3] Running .pcd-reconstructed prior map missions (RMUL 3v3 & RMUC 5v5)...", flush=True)
    pcd_missions = run_pcd_prior_missions(policy)
    print("[2/3] Running pure online mapless Mid-360 3D point-cloud stair & zero-false-trigger suite...", flush=True)
    online_suite = run_online_mapless_stair_and_false_trigger_suite(policy)
    print("[3/3] Running dynamic enemy-robot point-cloud veto + live A* replanning + 1x video...", flush=True)
    dyn_avoid = run_dynamic_obstacle_avoidance_and_veto(
        policy,
        video_path=HERE / "media" / "mid360_live_pointcloud_nav_stair_avoid_1X.mp4",
    )

    all_passed = (
        pcd_missions["suite_rmul2027"]["passed"] == pcd_missions["suite_rmul2027"]["total"]
        and pcd_missions["suite_rmuc2027"]["passed"] == pcd_missions["suite_rmuc2027"]["total"]
        and online_suite["online_climbs_passed"] == online_suite["online_climbs_total"]
        and online_suite["zero_false_trigger_passed"] == online_suite["zero_false_trigger_total"]
        and dyn_avoid["passed"]
    )
    report = dict(
        passed=bool(all_passed),
        elapsed_s=round(time.perf_counter() - t0, 2),
        pcd_reconstructed_prior_missions=pcd_missions,
        online_mapless_pointcloud_suite=online_suite,
        dynamic_obstacle_veto_and_astar_replan=dyn_avoid,
    )
    put(HERE / "evidence" / "MID360_NAV_SUITE_AUDIT.json", report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
