import io
p=r"D:/claude2/fangzhen/sim_mujoco/onnx_play.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace('ap.add_argument("--model", default=r"D:/claude2/fangzhen/robot/out/rm_vehicle.xml")',
            'ap.add_argument("--model", default=r"D:/claude2/fangzhen/robot/out/scene.xml")')
t=t.replace('''        pitch = math.degrees(math.asin(np.clip(d.site_xmat[site].reshape(3, 3).T[2][0]
                                               * -1.0, -1, 1)))''',
            '''        gv = d.site_xmat[site].reshape(3, 3).T @ np.array([0.0, 0.0, -1.0])
        pitch = math.degrees(math.asin(np.clip(gv[0], -1, 1)))''')
io.open(p,"w",encoding="utf-8").write(t); print("ok")
