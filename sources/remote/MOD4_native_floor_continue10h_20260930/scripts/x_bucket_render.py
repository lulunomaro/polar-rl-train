import os,numpy as np,mujoco
from PIL import Image
ROOT=r"D:\claude2\fangzhen"
XML=r"""<mujoco><compiler angle="radian" meshdir="MESHDIR" autolimits="true"/>
<option timestep="0.001"/>
<visual><global offwidth="1200" offheight="800"/><map znear="0.05" fogstart="99" fogend="100"/>
 <rgba fog="0 0 0 0"/></visual>
<statistic meansize="0.5" extent="1.5"/>
<asset>
%s
</asset>
<worldbody>
<geom name="fl" type="plane" size="5 5 0.05" rgba="0.30 0.32 0.35 1" contype="0" conaffinity="0"/>
<light pos="2 -2 3" dir="-0.4 0.4 -0.8" diffuse="1 1 1" specular="0.3 0.3 0.3" type="directional"/>
<light pos="-2 2 1.5" dir="0.5 -0.4 -0.3" diffuse="0.4 0.4 0.45" type="directional"/>
<body name="b" pos="0 0 0">%s</body>
</worldbody></mujoco>"""
MD=os.path.join(ROOT,"robot","out_cc","meshes").replace("\\","/")
import re
src=open(os.path.join(ROOT,"robot","out_cc","rm_vehicle_cc.xml"),encoding="utf-8").read()
meshes=re.findall(r'<mesh name="(base_\w+?_\d+)" file="([^"]+)"[^/]*/>',src)
geoms=re.findall(r'<geom type="mesh"[^>]*mesh="(base_\w+?_\d+)"[^>]*rgba="([^"]+)"',src)
G={n:(f,c) for n,f,c in [(n,f,c) for n,f in meshes for _,_,c in [0]] } if False else {}
mf={n:f for n,f in meshes}; gc={n:c for n,c in geoms}
groups={}
for n in mf: groups.setdefault(n.split("_")[1],[]).append(n)
print("buckets:",{k:len(v) for k,v in groups.items()})
for gk,names in sorted(groups.items()):
    A="\n".join('  <mesh name="%s" file="%s" scale="0.001 0.001 0.001"/>'%(n,mf[n]) for n in names)
    B="\n".join('  <geom type="mesh" mesh="%s" contype="0" conaffinity="0" density="0" group="2" rgba="%s"/>'%(n,gc.get(n,"0.7 0.7 0.75 1")) for n in names)
    p=os.path.join(ROOT,"docs","audit","bk_%s.xml"%gk)
    open(p,"w",encoding="utf-8").write(XML.replace("MESHDIR",MD).replace("%s\n%s"%(A and "%s",A),"%s") if False else (XML.replace("MESHDIR",MD) % (A,B)))
    m=mujoco.MjModel.from_xml_path(p); d=mujoco.MjData(m); mujoco.mj_forward(m,d)
    r=mujoco.Renderer(m,height=800,width=1200)
    cam=mujoco.MjvCamera(); cam.type=mujoco.mjtCamera.mjCAMERA_FREE; cam.lookat=[0,0,0.25]; cam.distance=1.6; cam.elevation=15; cam.azimuth=60
    r.update_scene(d,camera=cam); img=r.render()
    Image.fromarray(img).save(os.path.join(ROOT,"docs","audit","bk_%s.png"%gk))
    nonbg=np.abs(img.astype(int)-np.array([77,82,89])).sum(2)>40
    print("  %-7s geoms %2d  on-screen coverage %.1f%%"%(gk,len(names),100*nonbg.mean()))