import io,ast
p=r"D:/claude2/fangzhen/sim_mujoco/sim_baseline.py"
t=io.open(p,encoding="utf-8").read()
a="""        cam = None
    if record:
        global rend
        rend = mujoco.Renderer(m, 480, 832)
        cam = mujoco.MjvCamera()
        cam.distance, cam.azimuth, cam.elevation = 2.2, 92, -9"""
b="""        cam = None
    if record:
        global rend, vopt
        rend = mujoco.Renderer(m, 480, 832)
        cam = mujoco.MjvCamera()
        cam.distance, cam.azimuth, cam.elevation = 2.2, 92, -9
        vopt = mujoco.MjvOption()
        vopt.geomgroup[:] = (1, 1, 1, 1, 0, 1)   # hide the collision hulls (group 4)"""
assert a in t; t=t.replace(a,b)
a="            rend.update_scene(d, camera=cam)\n            frames.append(rend.render())"
b="            rend.update_scene(d, camera=cam, scene_option=vopt)\n            frames.append(rend.render())"
assert a in t; t=t.replace(a,b)
io.open(p,"w",encoding="utf-8").write(t); ast.parse(t); print("ok")
