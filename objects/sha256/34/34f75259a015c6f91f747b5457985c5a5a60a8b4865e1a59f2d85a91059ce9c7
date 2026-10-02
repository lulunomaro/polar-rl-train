import json,os,numpy as np,trimesh
ROOT=r"D:\claude2\fangzhen"; FINE=os.path.join(ROOT,"cad","out","vehicle","meshes"); COARSE=os.path.join(ROOT,"cad","out","vehicle_coarse","meshes")
man=json.load(open(os.path.join(ROOT,"cad","out","vehicle","manifest.json"),encoding="utf-8"))["solids"]
cman=json.load(open(os.path.join(ROOT,"cad","out","vehicle_coarse","manifest.json"),encoding="utf-8"))["solids"]
CSUB={(s["path"],round(s["volume_mm3"],1)):s["obj"] for s in cman}
fl=set(os.listdir(FINE)); cl=set(os.listdir(COARSE))
same=diff=missfine=0; lost=0; tot=0
for s in man:
    obj=CSUB.get((s["path"],round(s["volume_mm3"],1)),s["obj"]); tot+=s["ntris"]
    if obj!=s["obj"]:
        diff+=1
        if obj not in fl: missfine+=1
        else:
            try:
                n=len(trimesh.load(os.path.join(FINE,obj),process=False).faces)
                if n!=s["ntris"]: lost+=abs(n-s["ntris"])
            except Exception: pass
    else: same+=1
print("FINE solids %d  CSUB->same name %d  DIFFERENT name %d  (of which not present in FINE: %d)"%(len(man),same,diff,missfine))
print("sum FINE ntris %d   face-count mismatch caused by wrong obj name: %d"%(tot,lost))
# the 16 大装甲板
big=[s for s in man if "大装甲板.step" in s["product"]]
print("\n大装甲板.step instances in FINE: %d, ntris each %s"%(len(big),sorted(set(s["ntris"] for s in big))))
for s in big[:4]:
    obj=CSUB.get((s["path"],round(s["volume_mm3"],1)),s["obj"])
    print("   id %s own obj %s (%d tris) -> CSUB obj %s exists_in_FINE=%s"%(s["id"],s["obj"],s["ntris"],obj,obj in fl))