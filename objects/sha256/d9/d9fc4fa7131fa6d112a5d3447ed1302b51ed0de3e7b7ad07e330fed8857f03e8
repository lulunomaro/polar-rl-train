import numpy as np
import trimesh
import mujoco
from PIL import Image

# ---------- A) is there an empty z-band inside the chassis mesh? ----------
mm = trimesh.load(r"D:/claude2/fangzhen/robot/out_cc/meshes/base_00.stl", process=False)
z = mm.triangles_center[:, 2]
print("base mesh z range: %.1f .. %.1f mm, faces=%d" % (z.min(), z.max(), len(z)))
hist, edges = np.histogram(z, bins=62, range=(z.min(), z.max()))
print("z-histogram (20 mm bins, '.'=empty):")
for h, e in zip(hist, edges):
    bar = "#" * min(40, int(40 * h / max(1, hist.max())))
    print("   %6.0f mm %5d %s" % (e, h, bar or "."))
empty = [(edges[i], edges[i + 1]) for i in range(len(hist)) if hist[i] == 0]
print("empty 20mm bands:", ["%.0f-%.0f" % (a, b) for a, b in empty])

# ---------- B) clean render of the standing robot ----------
m = mujoco.MjModel.from_xml_path(r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml")
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, m.key("stand").id)
mujoco.mj_forward(m, d)
print("standing: base z=%.4f  wheels z=%.4f/%.4f" % (d.xpos[1][2], d.xpos[3][2], d.xpos[4][2]))
r = mujoco.Renderer(m, 720, 960)
for name in ("side", "front"):
    i = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_CAMERA, name)
    if i >= 0:
        r.update_scene(d, camera=name)
        Image.fromarray(r.render()).save(r"D:/claude2/fangzhen/docs/crops/fig_G_stand_%s.png" % name)
        print("  wrote fig_G_stand_%s.png" % name)
cam = mujoco.MjvCamera()
cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
cam.trackbodyid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "base_link")
cam.distance, cam.elevation, cam.azimuth = 1.5, -12, 125
r.update_scene(d, camera=cam)
Image.fromarray(r.render()).save(r"D:/claude2/fangzhen/docs/crops/fig_G_stand_track.png")
print("  wrote fig_G_stand_track.png")
r.close()