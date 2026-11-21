# -*- coding: utf-8 -*-
import os, sys, math, time, gc
sys.path.insert(0, r"C:\Users\lulunomaro\.gemini\antigravity\brain\4d0b8052-9ea6-4a9e-8fed-3c4b4567c700\scratch\pylibs")
sys.path.insert(0, r"C:\Users\lulunomaro\.gemini\antigravity\brain\4d0b8052-9ea6-4a9e-8fed-3c4b4567c700\scratch\mod4v4_audit")
sys.path.insert(0, r"C:\Users\lulunomaro\.gemini\antigravity\brain\4d0b8052-9ea6-4a9e-8fed-3c4b4567c700\scratch\mod4v4_audit\MOD4v4")

import numpy as np
import trimesh
import mujoco
from scipy.spatial import cKDTree, ConvexHull
import kinematics
from gemini_patch import SRC, LEG_BODIES, GIMBAL_BODIES, fold_mass_properties

m0 = mujoco.MjModel.from_xml_path(os.path.join(SRC, "mjcf", "scene.xml"))
name = lambda m, t, i: mujoco.mj_id2name(m, t, i)

def get_body_vis_meshes(m, body_name):
    bid = m.body(body_name).id
    out = []
    for g in range(m.ngeom):
        if m.geom_bodyid[g] == bid and m.geom_contype[g] == 0 and m.geom_type[g] == mujoco.mjtGeom.mjGEOM_MESH:
            mid = m.geom_dataid[g]
            v = m.mesh_vert[m.mesh_vertadr[mid]:m.mesh_vertadr[mid] + m.mesh_vertnum[mid]].copy()
            f = m.mesh_face[m.mesh_faceadr[mid]:m.mesh_faceadr[mid] + m.mesh_facenum[mid]].copy()
            gm = np.zeros(9); mujoco.mju_quat2Mat(gm, m.geom_quat[g])
            v = v @ gm.reshape(3, 3).T + m.geom_pos[g]
            out.append(trimesh.Trimesh(vertices=v, faces=f, process=True))
    return out

def safe_hull_vol(pts):
    if len(pts) < 4:
        return 0.0
    if np.any((pts.max(0) - pts.min(0)) < 2e-4):
        return 0.0
    try:
        return float(ConvexHull(pts).volume)
    except Exception:
        return 0.0

def decimate_hull(pts, max_verts=36):
    try:
        ch0 = ConvexHull(pts)
    except Exception:
        rng = np.random.default_rng(0)
        pts = pts + rng.uniform(-5e-5, 5e-5, size=pts.shape)
        ch0 = ConvexHull(pts)
    hv = pts[ch0.vertices]
    if len(hv) <= max_verts:
        return trimesh.PointCloud(hv).convex_hull
    dirs = [[dx, dy, dz] for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1) if dx or dy or dz]
    dirs = np.array(dirs, dtype=np.float64)
    dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
    chosen = list({int(np.argmax(hv @ d)) for d in dirs})
    while len(chosen) < max_verts:
        dmin = np.min(np.linalg.norm(hv[:, None, :] - hv[chosen][None, :, :], axis=-1), axis=1)
        nxt = int(np.argmax(dmin))
        if dmin[nxt] < 2e-4:
            break
        chosen.append(nxt)
    return trimesh.PointCloud(hv[chosen]).convex_hull

def cad_part_convex_hulls(m, body_name, target_hulls=5, tol_mm=3.5):
    t0 = time.time()
    vis_list = get_body_vis_meshes(m, body_name)
    full_tm = trimesh.util.concatenate(vis_list)
    surf_pts = trimesh.sample.sample_surface(full_tm, 5000, seed=42)[0]
    tree_full = cKDTree(surf_pts)

    raw_comps = []
    for vm in vis_list:
        raw_comps.extend(vm.split(only_watertight=False))
    # Sort components by bbox diagonal descending, keep at most top 24 structural parts
    comp_info = []
    for c in raw_comps:
        diag = float(np.linalg.norm(c.bounds[1] - c.bounds[0]))
        comp_info.append((diag, c))
    comp_info.sort(key=lambda x: -x[0])

    big_pts = []
    small_pts = []
    for idx, (diag, c) in enumerate(comp_info):
        v = c.vertices
        if len(v) > 250:
            v = v[np.linspace(0, len(v) - 1, 250, dtype=int)]
        sp = trimesh.sample.sample_surface(c, 200, seed=1)[0] if len(c.faces) > 0 and c.area > 1e-8 else np.empty((0, 3))
        pts = np.vstack([sp, v]) if len(sp) else v
        if idx < 22 and diag >= 0.022 and safe_hull_vol(pts) > 1e-8:
            big_pts.append(pts)
        elif diag >= 0.008:
            small_pts.append(pts[:60])

    if not big_pts:
        big_pts = [surf_pts[:800]]
    elif small_pts:
        all_small = np.vstack(small_pts)
        trees = [cKDTree(bp) for bp in big_pts]
        dmat = np.column_stack([t.query(all_small)[0] for t in trees])
        nearest = np.argmin(dmat, axis=1)
        for k in range(len(big_pts)):
            sel = (nearest == k) & (dmat[:, k] < 0.010)
            if np.any(sel):
                big_pts[k] = np.vstack([big_pts[k], all_small[sel][:150]])

    def hull_err_from_pts(pts):
        h = decimate_hull(pts, max_verts=36)
        hs = trimesh.sample.sample_surface(h, 350, seed=3)[0]
        d_mm = tree_full.query(hs)[0] * 1000.0
        return h, float(np.percentile(d_mm, 96)), float(h.volume)

    # Split any concave structural part BEFORE converting to compact hulls
    clusters = [[p, *hull_err_from_pts(p)] for p in big_pts]
    for _ in range(10):
        idx_worst = max(range(len(clusters)), key=lambda i: clusters[i][2])
        pts, h, err, vol = clusters[idx_worst]
        if err <= tol_mm or len(clusters) >= max(len(big_pts) + 6, target_hulls + 5) or len(pts) < 32:
            break
        centered = pts - pts.mean(0)
        _, _, vt = np.linalg.svd(centered, full_matrices=False)
        axes = np.vstack([vt, np.eye(3)])
        best_split, best_vsum = None, vol * 10.0
        for ax in axes:
            proj = pts @ ax
            if proj.max() - proj.min() < 0.008:
                continue
            for q in (0.25, 0.4, 0.5, 0.6, 0.75):
                cut = np.quantile(proj, q)
                mL = proj <= cut
                mR = ~mL
                if mL.sum() < 10 or mR.sum() < 10:
                    continue
                vL, vR = safe_hull_vol(pts[mL]), safe_hull_vol(pts[mR])
                if vL > 0 and vR > 0 and vL + vR < best_vsum:
                    best_vsum = vL + vR
                    best_split = (pts[mL], pts[mR])
        if best_split is None or best_vsum >= 0.98 * vol:
            clusters[idx_worst][2] = 0.0
            continue
        pL, pR = best_split
        clusters.pop(idx_worst)
        clusters.append([pL, *hull_err_from_pts(pL)])
        clusters.append([pR, *hull_err_from_pts(pR)])

    # Now discard dense point arrays and merge ONLY using hull vertices (<=36 verts each -> zero RAM, 500x faster!)
    compact = [[c[1], c[2], c[3]] for c in clusters]   # [hull, err_mm, vol]
    while len(compact) > target_hulls:
        best_pair = None
        best_cost = 1e18
        for i in range(len(compact)):
            vi = compact[i][0].vertices
            for j in range(i + 1, len(compact)):
                pm = np.vstack([vi, compact[j][0].vertices])
                hm, em, vm = hull_err_from_pts(pm)
                dv = max(0.0, vm - (compact[i][2] + compact[j][2]))
                cost = dv * 1e6 + max(0.0, em - tol_mm) * 2.5 + em * 0.2
                if cost < best_cost:
                    best_cost = cost
                    best_pair = (i, j, [hm, em, vm])
        i, j, merged = best_pair
        compact.pop(j)
        compact.pop(i)
        compact.append(merged)

    hulls = [c[0] for c in compact]
    dt = time.time() - t0
    all_hv = np.vstack([trimesh.sample.sample_surface(h, 800, seed=1)[0] for h in hulls])
    d_h2v = tree_full.query(all_hv)[0] * 1000.0
    d_v2h = cKDTree(all_hv).query(surf_pts)[0] * 1000.0
    print(f"  {body_name:24s}: {len(hulls):2d} hulls (from {len(big_pts):2d} parts), {sum(len(h.vertices) for h in hulls):3d} verts ({dt:.2f}s) | hull->vis p95={np.percentile(d_h2v,95):.2f}mm p99={np.percentile(d_h2v,99):.2f}mm | vis->hull p95={np.percentile(d_v2h,95):.2f}mm")
    del vis_list, full_tm, raw_comps, comp_info
    gc.collect()
    return hulls

if __name__ == "__main__":
    print("=== 1. PART-AWARE EXACT-CAD CONVEX HULLS ===")
    hull_spec = {
        "gimbal_yaw_link": (6, 3.5),
        "gimbal_fold_link": (5, 3.0),
        "gimbal_pitch_link": (8, 3.5),
        "gimbal_uwb_tray_link": (4, 3.0),
        "gimbal_uwb_arm_link": (2, 2.5),
        "left_rear1_link": (3, 3.0),
        "right_rear1_link": (3, 3.0),
        "left_rear2_link": (4, 3.5),
        "right_rear2_link": (4, 3.5),
        "left_front1_link": (4, 2.5),
        "right_front1_link": (4, 2.5),
        "left_front3_link": (2, 3.0),
        "right_front3_link": (2, 3.0),
        "left_spring1_link": (1, 3.0),
        "right_spring1_link": (1, 3.0),
        "left_spring2_link": (1, 3.0),
        "right_spring2_link": (1, 3.0),
    }
    cache_dir = r"C:\Users\lulunomaro\.gemini\antigravity\brain\4d0b8052-9ea6-4a9e-8fed-3c4b4567c700\scratch\mod4v4_audit\hulls_cache"
    os.makedirs(cache_dir, exist_ok=True)
    hulls = {}
    for bn, (mh, tol) in hull_spec.items():
        hs = cad_part_convex_hulls(m0, bn, mh, tol)
        hulls[bn] = hs
        for hi, h in enumerate(hs):
            h.export(os.path.join(cache_dir, f"v4_col_{bn}_{hi:02d}.stl"))
    print("Saved all STL hulls to", cache_dir)
