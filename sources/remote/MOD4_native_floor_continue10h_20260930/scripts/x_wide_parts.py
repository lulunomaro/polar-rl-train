import json,numpy as np,yaml
ROOT=r"D:\claude2\fangzhen"
spec=yaml.safe_load(open(ROOT+r"\robot\vehicle.spec.yaml",encoding="utf-8"))
R=np.array(spec["frame"]["rot"],float); t=-R@np.array(spec["frame"]["origin_cad"],float)
sol=json.load(open(ROOT+r"\cad\out\vehicle\manifest.json",encoding="utf-8"))["solids"]
def rf(b):
    b=np.array(b,float).reshape(2,3); w=(R@b.T).T+t; return w
rows=[]
for s in sol:
    lo,hi=rf(s["bbox_world"])
    rows.append((s,lo,hi))
def show(tag,cond,limit=28):
    sel=[(s,lo,hi) for s,lo,hi in rows if cond(lo,hi)]
    print("\n### %s : %d solids, %.1f cm3, %d tris"%(tag,len(sel),sum(s["volume_mm3"] for s,_,_ in sel)/1000,sum(s["ntris"] for s,_,_ in sel)))
    for s,lo,hi in sorted(sel,key=lambda r:-r[0]["volume_mm3"])[:limit]:
        print("   vol %8.1f cm3  y[%7.1f,%7.1f] x[%7.1f,%7.1f] z[%7.1f,%7.1f] tris %6d  %s"%(s["volume_mm3"]/1000,lo[1],hi[1],lo[0],hi[0],lo[2],hi[2],s["ntris"],s["product"].strip()[:52]))
show("WIDEST |y|>290", lambda lo,hi: hi[1]>290 or lo[1]<-290)
show("LONGEST |x|>330", lambda lo,hi: hi[0]>330 or lo[0]<-330)
show("LOWEST z<-40 (below chassis)", lambda lo,hi: lo[2]<-40)