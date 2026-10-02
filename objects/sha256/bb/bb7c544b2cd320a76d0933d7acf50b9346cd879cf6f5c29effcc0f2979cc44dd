import numpy as np
import mujoco
for xml in (r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml",
            r"D:/claude2/fangzhen/robot/out_cc_legacy54/scene_cc.xml"):
    m = mujoco.MjModel.from_xml_path(xml)
    d = mujoco.MjData(m)
    mujoco.mj_forward(m, d)
    grp = {}
    for i in range(m.ngeom):
        grp[(int(m.geom_type[i]), int(m.geom_group[i]))] = grp.get((int(m.geom_type[i]), int(m.geom_group[i])), 0) + 1
    r = mujoco.Renderer(m, 360, 640)
    r.update_scene(d, camera="front")
    img = r.render()
    bg = np.median(img.reshape(-1, 3), axis=0)
    frac = float(np.mean(np.abs(img.astype(int) - bg).sum(axis=2) > 24))
    print(xml.split("/")[-2], "geom (type,group)->count:", grp)
    print("   drawn-pixel fraction vs background = %.4f  (0.0000 before the fix)" % frac)
    r.close()