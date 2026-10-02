import io,re
p=r"D:/claude2/fangzhen/robot/vehicle.spec.yaml"
t=io.open(p,encoding="utf-8").read()
t=t.replace("visual_faces: 9000","visual_faces: 14000")
t=t.replace("visual_faces: 22000","visual_faces: 45000")
t=t.replace("visual_faces: 30000","visual_faces: 90000")
t=t.replace("visual_faces: 70000","visual_faces: 260000")
io.open(p,"w",encoding="utf-8").write(t)
print("visual faces raised")
p2=r"D:/claude2/fangzhen/sim_mujoco/sim_baseline.py"
t2=io.open(p2,encoding="utf-8").read()
t2=t2.replace("cam.distance, cam.azimuth, cam.elevation = 2.2, 92, -9","cam.distance, cam.azimuth, cam.elevation = 1.45, 96, -7")
t2=t2.replace("cam.lookat = [d.qpos[0], 0.0, 0.26]","cam.lookat = [d.qpos[0], 0.0, 0.33]")
io.open(p2,"w",encoding="utf-8").write(t2)
print("camera tuned")
p3=r"D:/claude2/fangzhen/scripts/build_robot.py"
t3=io.open(p3,encoding="utf-8").read()
t3=t3.replace('rgb1="0.35 0.38 0.42" ','rgb1="0.42 0.45 0.50" ').replace('rgb2="0.5 0.53 0.57"','rgb2="0.62 0.65 0.70"')
t3=t3.replace('reflectance="0.05"','reflectance="0.0"')
t3=t3.replace('diffuse="0.9 0.9 0.9"','diffuse="1.0 1.0 1.0"')
io.open(p3,"w",encoding="utf-8").write(t3)
print("floor/light tuned")
