import io
p = r"D:/claude2/fangzhen/sim2real/mock_h7.py"
t = io.open(p, encoding="utf-8").read()
a = """            cs = ("cmd L=[%+.2f,%+.2f]k60 w=[%.1f,%.1f]k%.2f"
                  % (c[0][0], c[1][0], c[0][3], c[4][1], c[5][1], c[4][4])) if c else "no-cmd\""""
b = """            cs = ("cmd=" + ",".join("%.2f/%.1f" % (j[0], j[1]) for j in c)
                  + " kp=" + ",".join("%.0f/%.2f" % (j[3], j[4]) for j in c)) if c else "no-cmd\""""
assert a in t
t = t.replace(a, b)
a2 = """            print("[h7] t=%5.1f z=%+.4f x=%+.3f pitch=%+.2fdeg wvel=%+.1f/%+.1f %s "
                  "rx=%d bad=%d tx=%d"
                  % (now - t_start, d.qpos[2], d.qpos[0],
                     math.degrees(math.asin(np.clip(grav[0], -1, 1))),
                     d.qvel[VADR[4]], d.qvel[VADR[5]], cs,
                     stats["rx"], stats["rx_bad"], stats["tx"]), flush=True)"""
b2 = """            print("[h7] t=%5.1f z=%+.4f x=%+.3f roll=%+.1f pitch=%+.1f "
                  "legq=%s wvel=%+.1f/%+.1f %s rx=%d bad=%d"
                  % (now - t_start, d.qpos[2], d.qpos[0],
                     math.degrees(math.asin(np.clip(-grav[1], -1, 1))),
                     math.degrees(math.asin(np.clip(grav[0], -1, 1))),
                     np.round(d.qpos[7:11], 2).tolist(),
                     d.qvel[VADR[4]], d.qvel[VADR[5]], cs,
                     stats["rx"], stats["rx_bad"]), flush=True)"""
assert a2 in t
t = t.replace(a2, b2)
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("mock trace enriched")
