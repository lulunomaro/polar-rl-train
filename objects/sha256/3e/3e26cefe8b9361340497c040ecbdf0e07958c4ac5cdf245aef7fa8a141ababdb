import io
p = r"D:/claude2/fangzhen/sim_mujoco/onnx_play.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace("cam.distance, cam.azimuth, cam.elevation = 1.45, 96, -8",
              "cam.distance, cam.azimuth, cam.elevation = 2.6, 118, -12")
t = t.replace("cam.lookat = [d.qpos[0], 0.0, 0.28]", "cam.lookat = [d.qpos[0], 0.0, 0.30]")
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("camera reframed")
