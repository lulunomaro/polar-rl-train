import json, os, sys
import numpy as np, trimesh
d = sys.argv[1]
m = json.load(open(os.path.join(d, "manifest.json"), encoding="utf8"))
bad = 0
for s in m["solids"]:
    me = trimesh.load(os.path.join(d, "meshes", s["obj"]), process=False)
    lo, hi = me.vertices.min(0), me.vertices.max(0)
    bb = s["bbox_world"]
    err = max(abs(lo[0]-bb[0]), abs(lo[1]-bb[1]), abs(lo[2]-bb[2]), abs(hi[0]-bb[3]), abs(hi[1]-bb[4]), abs(hi[2]-bb[5]))
    if err > 2.0:
        bad += 1
        if bad <= 6:
            print("MISMATCH", s["id"], repr(s["product"]), "mesh_lo", np.round(lo,1), "brep", bb)
    s["_ext"] = [float(x) for x in (hi-lo)]
print("mismatched:", bad, "/", len(m["solids"]))
print("total tris", sum(s["ntris"] for s in m["solids"]))
vs = sorted(m["solids"], key=lambda s: -s["volume_mm3"])
print("\n%-6s %-34s %-10s %-22s %s" % ("id","product","vol_cm3","size_mm","path"))
for s in vs[:25]:
    print("%-6s %-34s %-10.1f %-22s %s" % (s["id"], s["product"][:34], s["volume_mm3"]/1000, str(s["size"]), s["path"][:50]))
