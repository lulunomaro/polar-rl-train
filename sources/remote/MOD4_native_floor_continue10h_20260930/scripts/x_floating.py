import json,numpy as np,yaml,itertools
ROOT=r"D:\claude2\fangzhen"
spec=yaml.safe_load(open(ROOT+r"\robot\vehicle.spec.yaml",encoding="utf-8"))
R=np.array(spec["frame"]["rot"],float); t=-R@np.array(spec["frame"]["origin_cad"],float)
sol=json.load(open(ROOT+r"\cad\out\vehicle\manifest.json",encoding="utf-8"))["solids"]
B=[]
for s in sol:
    b=np.array(s["bbox_world"],float).reshape(2,3); w=(R@b.T).T+t
    B.append((s,w[0],w[1]))
n=len(B)
# union-find on bbox proximity (gap <= 6 mm on all axes)
par=list(range(n))
def find(a):
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
def uni(a,b):
    ra,rb=find(a),find(b)
    if ra!=rb: par[rb]=ra
G=6.0
for i in range(n):
    si,li,hi=B[i]
    for j in range(i+1,n):
        sj,lj,hj=B[j]
        if all(hi[k]-lj[k]>=-G and hj[k]-li[k]>=-G for k in range(3)): uni(i,j)
import collections
comp=collections.defaultdict(list)
for i in range(n): comp[find(i)].append(i)
big=max(comp,key=lambda k:sum(B[i][0]["volume_mm3"] for i in comp[k]))
print("components: %d   main has %d solids"%((len(comp)),len(comp[big])))
main_lo=np.min([B[i][1] for i in comp[big]],0); main_hi=np.max([B[i][2] for i in comp[big]],0)
print("main cluster bbox mm lo",np.round(main_lo,1),"hi",np.round(main_hi,1))
odd=[(k,v) for k,v in comp.items() if k!=big]
odd.sort(key=lambda kv:-sum(B[i][0]["volume_mm3"] for i in kv[1]))
print("\n--- %d OTHER clusters (potential floating parts) ---"%len(odd))
for k,v in odd[:22]:
    lo=np.min([B[i][1] for i in v],0); hi=np.max([B[i][2] for i in v],0)
    vol=sum(B[i][0]["volume_mm3"] for i in v)/1000
    d=max(np.maximum(np.maximum(lo-main_hi,main_lo-hi),0))
    print("  n=%3d vol=%7.1f cm3 gap=%6.1fmm bbox[%7.1f,%7.1f][%7.1f,%7.1f][%7.1f,%7.1f]  %s"%(len(v),vol,d,lo[0],hi[0],lo[1],hi[1],lo[2],hi[2],
        " | ".join(sorted(set(B[i][0]["product"].strip()[:26] for i in v)))[:120]))