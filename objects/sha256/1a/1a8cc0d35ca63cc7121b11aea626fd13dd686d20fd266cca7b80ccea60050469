import io, os
import numpy as np
import trimesh

stl = r"D:/claude2/fangzhen/robot/out_cc/meshes/base_00.stl"
m = trimesh.load(stl, force="mesh")
print("base_00.stl: verts=%d faces=%d  bbox=%s" % (len(m.vertices), len(m.faces), np.round(m.bounds, 3).tolist()))
parts = m.split(only_watertight=False)
print("disconnected shells: %d" % len(parts))
tot = m.area
rows = []
for i, p in enumerate(parts):
    c = p.centroid
    rows.append((p.area, c, p.bounds))
rows.sort(key=lambda r: -r[0])
print("  top shells by surface area (area m^2, centroid mm, zmin..zmax mm):")
for area, c, b in rows[:14]:
    print("    %9.4f  c=(%7.1f,%7.1f,%7.1f)  z %6.1f..%6.1f  x %6.1f..%6.1f" %
          (area, c[0] * 1000, c[1] * 1000, c[2] * 1000, b[0][2] * 1000, b[1][2] * 1000, b[0][0] * 1000, b[1][0] * 1000))
hi = [r for r in rows if r[1][2] > 0.16]
print("shells with centroid above z=160 mm (the floating cluster): %d, total area %.4f of %.4f (%.1f%%)" %
      (len(hi), sum(r[0] for r in hi), tot, 100 * sum(r[0] for r in hi) / tot))