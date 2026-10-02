import numpy as np
import mujoco
from PIL import Image

m = mujoco.MjModel.from_xml_path(r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml")
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, m.key("stand").id)
mujoco.mj_forward(m, d)
print("mesh geoms on base_link:", [mujoco.mj_id2name(m, 0, i) for i in range(m.ngeom) if m.geom_bodyid[i] == 1])
r = mujoco.Renderer(m, 700, 980)
cam = mujoco.MjvCamera()
for tag, az, el, dist, lz in (("full_side", 90, -6, 2.5, 0.30), ("full_front", 0, -8, 2.5, 0.30),
                              ("full_3q", 135, -18, 2.6, 0.28)):
    cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
    cam.trackbodyid = 1
    cam.azimuth, cam.elevation, cam.distance = az, el, dist
    cam.lookat[:] = [0.0, 0.0, lz]
    r.update_scene(d, camera=cam)
    Image.fromarray(r.render()).save(r"D:/claude2/fangzhen/docs/crops/fig_H_%s.png" % tag)
    print("wrote fig_H_%s.png" % tag)
r.close()