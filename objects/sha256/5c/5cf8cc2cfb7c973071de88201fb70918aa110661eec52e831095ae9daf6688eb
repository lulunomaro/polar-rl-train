import os,json,numpy as np,trimesh,yaml
ROOT=r"D:\claude2\fangzhen"; MD=os.path.join(ROOT,"robot","out_cc","meshes")
def b(files):
    lo=np.full(3,1e18);hi=np.full(3,-1e18);n=0
    for f in files:
        m=trimesh.load(os.path.join(MD,f),process=False); n+=len(m.faces)
        lo=np.minimum(lo,m.bounds[0]);hi=np.maximum(hi,m.bounds[1])
    return lo,hi,n
groups={"base":["base_%02d.stl"%i for i in range(15)],
 "thigh":["thigh_l.stl","thigh_r.stl"],"shank":["shank_l.stl","shank_r.stl"],
 "wheel":["wheel_l.stl","wheel_r.stl"],"crank":["crank_l.stl","crank_r.stl"],
 "link2":["link2_l.stl","link2_r.stl"],"link3":["link3_l.stl","link3_r.stl"],
 "link4":["link4_l.stl","link4_r.stl"],"spring":["spring1_l.stl","spring1_r.stl","spring2_l.stl","spring2_r.stl"]}
print("%-7s %8s   %-34s %-34s %s"%("set","tris","min(mm)","max(mm)","extent(mm)"))
alllo=np.full(3,1e18);allhi=np.full(3,-1e18);tot=0
for k,v in groups.items():
    lo,hi,n=b(v); tot+=n
    alllo=np.minimum(alllo,lo);allhi=np.maximum(allhi,hi)
    print("%-7s %8d   [%7.1f %7.1f %7.1f]      [%7.1f %7.1f %7.1f]     [%6.1f %6.1f %6.1f]"%(k,n,lo[0],lo[1],lo[2],hi[0],hi[1],hi[2],*(hi-lo)))
print("%-7s %8d   [%7.1f %7.1f %7.1f]      [%7.1f %7.1f %7.1f]     [%6.1f %6.1f %6.1f]"%("MODEL",tot,allo[0],allo[1],allo[2],allhi[0],allhi[1],allhi[2],*(allhi-allo)))
print("%-7s %8s   [%7.1f %7.1f %7.1f]      [%7.1f %7.1f %7.1f]     [%6.1f %6.1f %6.1f]"%("CAD",733,-357,-370.6,-73,357.1,370.5,685.4,714.1,741.1,758.4))