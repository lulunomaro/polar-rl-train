import io
p=r"D:/claude2/fangzhen/sim_mujoco/sim_baseline.py"
t=io.open(p,encoding="utf-8").read()
a="        u -= kw * float(np.mean([d.qpos[a] for a in WQ]))"
b="        u -= KTAU * kw * float(np.mean([d.qpos[a] for a in WQ]))"
assert a in t; t=t.replace(a,b)
a='ap.add_argument("--kw", type=float, default=0.0)'
b='ap.add_argument("--kw", type=float, default=0.015)'
assert a in t; t=t.replace(a,b)
t=t.replace("for bp in (1.5, 2.5, 4.0, 6.0):","for bp in (4.0,):")
t=t.replace("for bd in (0.12, 0.25, 0.45):","for bd in (0.30, 0.45, 0.60):")
t=t.replace("for kw in (0.0, 6.0, 20.0):","for kw in (0.0, 0.01, 0.02, 0.05, 0.10):")
t=t.replace("hist, _, _, _ = run(10.0, 0.30, 1.2, bp, bd, 0.03, kw, 700.0, 45.0)","hist, _, _, _ = run(14.0, 0.30, 1.2, bp, bd, kl, kw, 700.0, 45.0)")
t=t.replace("    for bp in (4.0,):\n        for bd in (0.30, 0.45, 0.60):\n            for kw in (0.0, 0.01, 0.02, 0.05, 0.10):",
            "    for bp in (4.0,):\n        for bd in (0.45,):\n          for kl in (0.03, 0.06, 0.10):\n            for kw in (0.0, 0.01, 0.02, 0.05, 0.10):")
t=t.replace("                hist, _, _, _ = run(14.0, 0.30, 1.2, bp, bd, kl, kw, 700.0, 45.0)","                hist, _, _, _ = run(14.0, 0.30, 1.2, bp, bd, kl, kw, 700.0, 45.0)")
t=t.replace('print(" %5.2f  %5.3f  %5.3f  %5.1f  | %9.2f %9.2f %9.3f %7.2f   %s"\n                      % (bp, bd, 0.03, kw, p, r, xr, v, ok))','print(" %5.2f  %5.3f  %5.3f  %5.3f | %9.2f %9.2f %9.3f %7.2f   %s"\n                      % (bp, bd, kl, kw, p, r, xr, v, ok))')
io.open(p,"w",encoding="utf-8").write(t)
import ast; ast.parse(t); print("ok")
