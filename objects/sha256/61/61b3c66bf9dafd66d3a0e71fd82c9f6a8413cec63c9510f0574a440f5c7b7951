import os, numpy as np, mujoco
from scipy.spatial.transform import Rotation
ROOT=r"D:\claude2\fangzhen"
m=mujoco.MjModel.from_xml_path(os.path.join(ROOT,"robot","out_cc","scene_cc.xml"))
d=mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m,d,0); mujoco.mj_forward(m,d)
print("ngeom",m.ngeom,"nbody",m.nbody,"nq",m.nq,"mass %.3f"%m.body_mass.sum())
rows=[]; tot=0
for g in range(m.ngeom):
    if m.geom_group[g]!=2 or m.geom_type[g]!=mujoco.mjtGeom.mjGEOM_MESH: continue
    mi=m.geom_dataid[g]; nvert=m.mesh_vertnum[mi]; nface=m.mesh_facenum[mi]; tot+=nface
    a=m.mesh_vertadr[mi]; v=m.mesh_vert[a:a+nvert]
    b=m.geom_bodyid[g]; Rb=d.xmat[b].reshape(3,3)
    pb=d.xpos[b]+Rb@m.geom_pos[g]
    Rg=Rotation.from_quat(m.geom_quat[g][[1,2,3,0]]).as_matrix()
    w=(v)@((Rb@Rg).T)+pb
    nm=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_GEOM,g) or str(g)
    mn=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_MESH,mi)
    rows.append((nm,mn,nvert,nface,w.min(0),w.max(0)))
print("total visual triangles",tot)
lo=np.min([r[4] for r in rows],0); hi=np.max([r[5] for r in rows],0)
print("union AABB mm lo",np.round(lo*1000,1),"hi",np.round(hi*1000,1),"extent",np.round((hi-lo)*1000,1))
print("")
print("%-14s %-11s %8s %8s  center(mm)                 extent(mm)"%("geom","mesh","nvert","nface"))
for nm,mn,nv,nf,l,h in rows:
    c=(l+h)/2*1000; e=(h-l)*1000
    f=""
    if nv<60: f="  <-- TINY"
    print("%-14s %-11s %8d %8d  [%7.1f %7.1f %7.1f] [%7.1f %7.1f %7.1f]%s"%(nm,mn,nv,nf,c[0],c[1],c[2],e[0],e[1],e[2],f))