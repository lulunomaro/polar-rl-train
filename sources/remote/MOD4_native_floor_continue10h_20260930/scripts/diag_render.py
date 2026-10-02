import os
import numpy as np
import mujoco

for xml in (r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml",
            r"D:/claude2/fangzhen/sim2sim_cc/rm_vehicle_cc/mjcf/scene_field.xml"):
    print("\n########", xml)
    m = mujoco.MjModel.from_xml_path(xml)
    d = mujoco.MjData(m)
    base = os.path.dirname(xml)
    md = m.meshdir.decode() if hasattr(m, "meshdir") else ""
    print("nmesh=%d  fullmesh=%s  meshdir=%r" % (m.nmesh, getattr(m, "nfullmesh", "?"), md))
    missing = 0
    for i in range(m.nmesh):
        f = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_MESH, i)
        # asset files are resolved against meshdir
        p = os.path.normpath(os.path.join(base, md, f + ".STL"))
        ok = os.path.exists(p)
        if not ok:
            cands = [x for x in os.listdir(os.path.join(base, md)) if x.lower() == (f.lower() + ".stl")]
            ok = bool(cands)
        if not ok:
            missing += 1
            if missing < 6:
                print("   MESH FILE MISSING:", f, "->", p)
    print("   missing mesh files: %d / %d" % (missing, m.nmesh))
    print("nbody=%d ngeom=%d njoint=%d nu=%d mass=%.2f" % (m.nbody, m.ngeom, m.njoint, m.nu, sum(m.body_mass)))
    print("nq=%d qpos0 head=%s" % (m.nq, np.round(d.qpos[:8], 4)))
    grp = {}
    for g in range(m.ngeom):
        key = (int(m.geom_group[g]), int(m.geom_contype[g]), int(m.geom_conaffinity[g]), float(m.geom_rgba[g][3]))
        grp[key] = grp.get(key, 0) + 1
    print("geom (group,contype,conaffinity,alpha) -> count:")
    for k, v in sorted(grp.items()):
        print("   ", k, "->", v)
    # does the robot root have a free joint?
    fj = [i for i in range(m.njnt) if m.jnt_type[i] == mujoco.mjtJoint.mjJNT_FREE]
    print("free joints:", [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i) for i in fj])
    mujoco.mj_forward(m, d)
    print("base xpos after forward:", np.round(d.xpos[1], 4) if m.nbody > 1 else "n/a")
    r = mujoco.Renderer(m, 360, 640)
    mujoco.mj_forward(m, d)
    r.update_state(d)
    r.update_scene(d)
    img = r.render()
    uniq = len(np.unique(img.reshape(-1, 3), axis=0))
    nonbg = float(np.mean(np.abs(img.astype(int) - np.median(img.reshape(-1, 3), axis=0)).sum(axis=2) > 24))
    print("render: unique colors=%d  non-background pixel fraction=%.4f" % (uniq, nonbg))
    r.close()