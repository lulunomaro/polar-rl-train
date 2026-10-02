import os,numpy as np,mujoco
from PIL import Image
ROOT=r"D:\claude2\fangzhen"
m=mujoco.MjModel.from_xml_path(os.path.join(ROOT,"robot","out_cc","scene_cc.xml"))
d=mujoco.MjData(m); mujoco.mj_resetDataKeyframe(m,d,0); mujoco.mj_forward(m,d)
print("geom groups present:",sorted(set(m.geom_group.tolist())))
r=mujoco.Renderer(m,height=700,width=1100)
cam=mujoco.MjvCamera(); cam.type=mujoco.mjtCamera.mjCAMERA_FREE
cam.lookat=[0,0,0.30]; cam.distance=1.7; cam.elevation=20; cam.azimuth=55
for tag,hide in (("allgroups",False),("hide3",True)):
    o=mujoco.MjvOption()
    if hide: o.geomgroup[3]=0
    r.update_scene(d,camera=cam,scene_option=o)
    img=r.render(); Image.fromarray(img).save(os.path.join(ROOT,"docs","audit","grp_%s.png"%tag))
    print("wrote",tag)