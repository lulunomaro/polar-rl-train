import io, ast
p = r"D:/claude2/fangzhen/scripts/scan_workspace.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace("""Gb_c = dilate(Gb, CLEAR)""",
"""# The assembly is connected: leg and chassis clouds necessarily touch inside the joint
# bosses, so exclude a 30 mm cylinder around every joint axis before testing.
AXES = [(hip_c, (0, 1, 0)), (knee_c, (0, 1, 0)),
        (np.array([-0.0009, -0.27025, 0.0]), (0, 1, 0))]
def near_joint(P, r=0.030):
    m = np.zeros(len(P), dtype=bool)
    for c, a in AXES:
        a = np.asarray(a, float); v = P - c
        d = np.linalg.norm(v - np.outer(v @ a, a), axis=1)
        m |= (d < r)
    return m
base_f = base[~near_joint(base)]
thigh_f = thigh[~near_joint(thigh)]
shank_f = shank[~near_joint(shank)]
wheel_f = wheel[~near_joint(wheel)]
print("after removing 30 mm joint bosses: base %d->%d, thigh %d->%d, shank %d->%d, wheel %d->%d"
      % (len(base), len(base_f), len(thigh), len(thigh_f), len(shank), len(shank_f),
         len(wheel), len(wheel_f)))
Gb = np.zeros(int(DIMS.prod()), dtype=bool); Gb[to_grid(base_f)] = True
Gb_c = dilate(Gb, CLEAR)""")
t = t.replace("""        bad = Gb_c[to_grid(th)].any() or Gb_c[to_grid(sk)].any() or Gb_c[to_grid(wh)].any()
        row.append(bool(bad))""",
"""        n = (int(Gb_c[to_grid(thigh_f)].any()) and 0)  # placeholder
        cnt = (Gb_c[to_grid(rot_about(hip_c, (0, 1, 0), thigh_f, q1))].sum()
               + Gb_c[to_grid(rot_about(hip_c, (0, 1, 0),
                    rot_about(knee_c, (0, 1, 0), shank_f, q2), q1))].sum()
               + Gb_c[to_grid(rot_about(hip_c, (0, 1, 0),
                    rot_about(knee_c, (0, 1, 0), wheel_f, q2), q1))].sum())
        row.append(cnt >= 5)
        overlap.append(cnt)""")
t = t.replace("hits = []\nHIP =", "hits, overlap = [], []\nHIP =")
t = t.replace("""free = ~hits
print("\\nfree fraction: %.1f%%   hip range with >=1 free knee: [%.2f, %.2f]"
      % (100 * free.mean(), HIP[free.any(1)].min(), HIP[free.any(1)].max()))""",
"""hits = np.array(hits, dtype=bool)
free = ~hits
print("\\nfree fraction: %.1f%%" % (100 * free.mean()))
if free.any():
    print("hip angles with >=1 free knee: [%.2f, %.2f] rad"
          % (HIP[free.any(1)].min(), HIP[free.any(1)].max()))
    print("knee angles with >=1 free hip: [%.2f, %.2f] rad"
          % (KNEE[free.any(0)].min(), KNEE[free.any(0)].max()))
ov = np.array(overlap).reshape(len(HIP), len(KNEE))
print("worst overlap (voxel count) at hip/knee = %.2f / %.2f : %d"
      % (HIP[np.unravel_index(ov.argmax(), ov.shape)[0]],
         KNEE[np.unravel_index(ov.argmax(), ov.shape)[1]], ov.max()))
print("overlap at the zero (CAD) pose: %d voxels" % ov[len(HIP)//2, np.argmin(abs(KNEE))])""")
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
try:
    ast.parse(t); print("patched")
except SyntaxError as e:
    print("SYNTAX", e)
