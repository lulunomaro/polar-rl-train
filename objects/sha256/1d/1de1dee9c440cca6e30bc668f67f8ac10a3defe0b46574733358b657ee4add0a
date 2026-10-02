import json,os,numpy as np,trimesh
ROOT=r"D:\claude2\fangzhen"; FINE=os.path.join(ROOT,"cad","out","vehicle","meshes"); COARSE=os.path.join(ROOT,"cad","out","vehicle_coarse","meshes")
man=json.load(open(os.path.join(ROOT,"cad","out","vehicle","manifest.json"),encoding="utf-8"))["solids"]
cman=json.load(open(os.path.join(ROOT,"cad","out","vehicle_coarse","manifest.json"),encoding="utf-8"))["solids"]
CSUB={(s["path"],round(s["volume_mm3"],1)):s["obj"] for s in cman}
def bbox(f):
    m=trimesh.load(f,process=False); return np.round(m.bounds[0],1),np.round(m.bounds[1],1),len(m.faces)
print("Does FINE/<own obj> match the manifest bbox?  (10 random solids)")
rng=np.random.default_rng(0); ok=0
for s in [man[i] for i in rng.choice(len(man),10,replace=False)]:
    lo,hi,n=bbox(os.path.join(FINE,s["obj"]))
    want=np.round(s["mesh_bbox"],1)
    good=np.allclose(lo,want[:3],atol=0.5) and np.allclose(hi,want[3:],atol=0.5)
    ok+=good
    print("  id %s own=%-18s faces %6d  bbox %s %s  manifest %s %s  %s"%(s["id"],s["obj"],n,lo,hi,want[:3],want[3:],"OK" if good else "MISMATCH"))
print("  -> %d/10 OK with its OWN obj name"%ok)
print("\nWhat does the CSUB-selected file actually contain?")
for s in man[:0]+[x for x in man if "大装甲板.step" in x["product"]][:3]:
    o=CSUB.get((s["path"],round(s["volume_mm3"],1)),s["obj"])
    lo,hi,n=bbox(os.path.join(FINE,o))
    print("  solid id %s (%s) manifest bbox %s"%(s["id"],s["product"].strip()[:22],np.round(s["mesh_bbox"],1)))
    print("     loads FINE/%s -> faces %6d bbox %s %s   <-- WRONG PART" % (o,n,lo,hi))
print("\ncoarse-vs-fine id drift: first 6 coarse ids for the same path")
for s in [x for x in man if "大装甲板.step" in x["product"]][:2]:
    cs=[c for c in cman if c["path"]==s["path"] and abs(c["volume_mm3"]-s["volume_mm3"])<0.05]
    print("  fine id %s -> coarse %s"%(s["id"],[(c["id"],c["obj"],c["ntris"]) for c in cs]))