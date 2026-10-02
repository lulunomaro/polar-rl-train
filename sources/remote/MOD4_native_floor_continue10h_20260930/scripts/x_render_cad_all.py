import os, json, numpy as np, mujoco, yaml
from PIL import Image
from scipy.spatial.transform import Rotation
ROOT=r"D:\claude2\fangzhen"; FINE=os.path.join(ROOT,"cad","out","vehicle")
spec=yaml.safe_load(open(os.path.join(ROOT,"robot","vehicle.spec.yaml"),encoding="utf-8"))
R=np.array(spec["frame"]["rot"],float); t=-R@np.array(spec["frame"]["origin_cad"],float)
q=Rotation.from_matrix(R).as_quat()
sol=json.load(open(os.path.join(FINE,"manifest.json"),encoding="utf-8"))["solids"]
sol=[s for s in sol if s["ntris"]>0]
print("solids with tris:",len(sol),"total tris",sum(s["ntris"] for s in sol))
L=[]
L.append('<mujoco><compiler angle="radian" meshdir="%s" autolimits="true"/>'%(os.path.join(FINE,"meshes")).replace("\\","/"))
L.append('<option timestep="0.001"/><visual><global offwidth="1280" offheight="720"/><map znear="0.02"/></visual>')
L.append('<asset>')
for s in sol: L.append('  <mesh name="m%s" file="%s.obj" scale="0.001 0.001 0.001"/>'%(s["id"],s["obj"].split(".")[0]))
L.append('</asset><worldbody>')
L.append('<geom name="floor" type="plane" size="0 0 0.05" rgba="0.5 0.5 0.5 1" contype="0" conaffinity="0"/>')
L.append('  <body name="all" pos="%.6f %.6f %.6f" quat="%.9f %.9f %.9f %.9f">'%(t[0]/1000,t[1]/1000,t[2]/1000,q[3],q[0],q[1],q[2]))
for s in sol: L.append('    <geom type="mesh" mesh="m%s" contype="0" conaffinity="0" group="2" density="0" rgba="0.75 0.75 0.78 1"/>'%s["id"])
L.append('  </body></worldbody></mujoco>')
tmp=os.path.join(ROOT,"docs","audit","cad_all.xml"); open(tmp,"w",encoding="utf-8").write("\n".join(L))
m=mujoco.MjModel.from_xml_path(tmp); d=mujoco.MjData(m); mujoco.mj_forward(m,d)
lo=np.full(3,1e9); hi=np.full(3,-1e9)
for g in range(m.ngeom):
    if m.geom_type[g]!=mujoco.mjtGeom.mjGEOM_MESH: continue
    mi=m.geom_dataid[g]; a=m.mesh_vertadr[mi]; v=m.mesh_vert[a:a+m.mesh_vertnum[mi]]
    b=m.geom_bodyid[g]; Rb=d.xmat[b].reshape(3,3); pb=d.xpos[b]
    w=v@Rb.T+pb; lo=np.minimum(lo,w.min(0)); hi=np.maximum(hi,w.max(0))
print("CAD assembly in ROBOT frame: mm lo",np.round(lo*1000,1),"hi",np.round(hi*1000,1),"extent",np.round((hi-lo)*1000,1))
r=mujoco.Renderer(m,height=700,width=1244)
c=lo*0+np.array([0,0,0.35])
for name,(dist,elev,azim) in {"side":(1.9,5,90),"iso":(2.0,25,30),"front":(2.0,5,0)}.items():
    cam=mujoco.MjvCamera(); cam.type=mujoco.mjtCamera.mjCAMERA_FREE; cam.lookat=c; cam.distance=dist; cam.elevation=elev; cam.azimuth=azim
    r.update_scene(d,camera=cam); Image.fromarray(r.render()).save(os.path.join(ROOT,"docs","audit","cad_%s.png"%name))
print("ok")
