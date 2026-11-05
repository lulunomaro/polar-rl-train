"""Verify the actual local MuJoCo render and 200mm terrain before opening controls."""
from pathlib import Path
import sys,json,mujoco
from PIL import Image
D=Path(__file__).resolve().parent;out=D/'INITIAL_SCENE_PREVIEW.png';assert not out.exists();P=D.parent/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package';sys.path.insert(0,str(P));import kinematics_v2 as kin
m=mujoco.MjModel.from_xml_path(str(D/'interactive_scene.xml'));d=mujoco.MjData(m);kin.set_configuration(m,d,left=(0.,0.),right=(0.,0.));r=mujoco.Renderer(m,760,1000);o=mujoco.MjvOption();o.geomgroup[3]=0;o.sitegroup[:]=0;c=mujoco.MjvCamera();c.lookat[:]=[.3,0,.22];c.distance=1.9;c.azimuth=135;c.elevation=-20
try:r.update_scene(d,c,scene_option=o);Image.fromarray(r.render()).save(out)
finally:r.close()
print(json.dumps(dict(preview=str(out),actual_mujoco_render=True,step_height_m=.2,physics_integration_steps=0,policy_or_training=False)))
