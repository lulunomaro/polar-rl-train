import numpy as np, mujoco
from PIL import Image
m = mujoco.MjModel.from_xml_path(r"D:/claude2/fangzhen/robot/out_cc/scene_cc.xml")
d = mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m, d, mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_KEY, "stand")); mujoco.mj_forward(m, d)
r = mujoco.Renderer(m, 460, 420)
tiles = []
for az, el, dist, lz in ((0, -8, 1.15, 0.05), (0, -8, 0.75, 0.05), (180, -8, 1.15, 0.05), (0, 25, 1.4, 0.10)):
    cam = mujoco.MjvCamera(); cam.type = mujoco.mjtCamera.mjCAMERA_FREE
    cam.lookat[:] = [0.0, -0.20, lz]; cam.distance = dist; cam.azimuth = az; cam.elevation = el
    r.update_scene(d, camera=cam); im = Image.fromarray(r.render())
    tiles.append(im); print("az%4d el%3d d%.2f -> mean %.1f" % (az, el, dist, float(np.asarray(im).mean())))
for c in range(m.ncam):
    r.update_scene(d, camera=mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_CAMERA, mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_CAMERA, c)))
    im = Image.fromarray(r.render()); tiles.append(im)
    print("fixed", mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_CAMERA, c), "mean %.1f" % float(np.asarray(im).mean()))
W = 420 * 3 + 20; H = 460 * 2 + 10
sheet = Image.new("RGB", (W, H), "white")
for i, t in enumerate(tiles): sheet.paste(t, ((i % 3) * (420 + 10), (i // 3) * (460 + 10)))
sheet.save(r"D:/claude2/fangzhen/docs/crops/_camdbg.png"); print("wrote _camdbg.png")
