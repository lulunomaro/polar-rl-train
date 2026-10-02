import io, ast
p = r"D:/claude2/fangzhen/sim2real/mock_h7.py"
t = io.open(p, encoding="utf-8").read()
a = """            print("[h7] t=%5.1f z=%+.4f pitch=%+.2fdeg wheel vel=%+.2f/%+.2f "
                  "rx=%d bad=%d tx=%d"
                  % (now - t_start, d.qpos[2],
                     math.degrees(math.asin(np.clip(grav[0], -1, 1))),
                     d.qvel[VADR[4]], d.qvel[VADR[5]],
                     stats["rx"], stats["rx_bad"], stats["tx"]), flush=True)"""
b = """            c = last_cmd["joints"] if last_cmd else None
            cs = ("cmd L=[%+.2f,%+.2f]k%.0f w=[%.1f,%.1f]k%.2f"
                  % (c[0][0], c[1][0], c[0][3], c[4][1], c[5][1], c[4][4])) if c else "no-cmd"
            print("[h7] t=%5.1f z=%+.4f x=%+.3f pitch=%+.2fdeg wvel=%+.1f/%+.1f %s "
                  "rx=%d bad=%d tx=%d"
                  % (now - t_start, d.qpos[2], d.qpos[0],
                     math.degrees(math.asin(np.clip(grav[0], -1, 1))),
                     d.qvel[VADR[4]], d.qvel[VADR[5]], cs,
                     stats["rx"], stats["rx_bad"], stats["tx"]), flush=True)"""
assert a in t
t = t.replace(a, b)
t = t.replace('        u = float(np.clip(u, -54.0, 54.0))',
              '        lim = 30.0 if k < 4 else 8.0\n        u = float(np.clip(u, -lim, lim))')
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
ast.parse(t); print("mock now logs the received commands")
