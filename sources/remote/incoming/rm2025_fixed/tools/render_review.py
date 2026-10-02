"""Offscreen native MuJoCo QA images, without opening a viewer."""
from pathlib import Path
import sys
import mujoco
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from kinematics import set_configuration
m=mujoco.MjModel.from_xml_path(str(ROOT/'scene.xml'));d=mujoco.MjData(m)
renderer=mujoco.Renderer(m,height=900,width=1300)
opt=mujoco.MjvOption();opt.geomgroup[3]=0;opt.sitegroup[:]=0
for name,left,right in [('neutral',(0.,0.),(0.,0.)),('articulated',(.12,-.3),(-.10,.3))]:
    mujoco.mj_resetData(m,d);set_configuration(m,d,left,right)
    wheel_floor=min(d.geom_xpos[m.geom(s+'_tire').id,2]-.0625 for s in ['left','right'])
    d.qpos[2]+=.002-wheel_floor;mujoco.mj_forward(m,d)
    camera=mujoco.MjvCamera();camera.lookat[:]=[0,0,.18];camera.distance=1.05;camera.azimuth=132;camera.elevation=-12
    renderer.update_scene(d,camera,scene_option=opt)
    Image.fromarray(renderer.render()).save(ROOT/'reports'/('review_'+name+'.png'))
renderer.close()
