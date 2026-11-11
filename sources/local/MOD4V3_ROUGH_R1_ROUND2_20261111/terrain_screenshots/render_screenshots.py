from pathlib import Path
import importlib.util,shutil,json,hashlib
import numpy as np,mujoco
from PIL import Image,ImageDraw,ImageFont
T=Path(r'D:\claude2\fangzhen\_mod4v2_src_20261106\sources\local\MOD4V3_ROUGH_R1_ROUND2_20261111');old=T.parent/'MOD4V3_ROUGH_START_DIAG_20261111';out=T/'terrain_screenshots';(out/'evidence').mkdir(parents=True,exist_ok=True)
shutil.copyfile(old/'evidence/terrain_heightfields.npz',out/'evidence/terrain_heightfields.npz')
spec=importlib.util.spec_from_file_location('r1_existing_viewer',old/'open_rough_mujoco.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.BASE=out
font=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',28);small=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',20)
records=[]
for family,cn in [('mid','中级正阶'),('inv_mid','中级反阶')]:
 sim=mod.RoughSimulation(label='R1 square 010m',family=family,spawn='slope',show_viewer=False)
 m,d=sim.env.m,sim.env.d;m.vis.global_.offwidth=1500;m.vis.global_.offheight=960;m.vis.headlight.ambient[:]=[.65,.65,.65];m.vis.headlight.diffuse[:]=[.8,.8,.8];m.vis.headlight.specular[:]=[.15,.15,.15]
 x=-1.2;d.qpos[0]=x;d.qpos[1]=0.;d.qpos[2]=sim.ground(x,0.)+sim.env.bank_z;mujoco.mj_forward(m,d)
 with mujoco.Renderer(m,height=900,width=1500) as renderer:
  for view in ['overview','close']:
   cam=mujoco.MjvCamera();cam.type=mujoco.mjtCamera.mjCAMERA_FREE
   if view=='overview':cam.lookat[:]=[0.,0.,float((sim.terrain.max()+sim.terrain.min())*.5)];cam.distance=12.0;cam.azimuth=125.;cam.elevation=-30.
   else:cam.lookat[:]=[-.8,0.,sim.ground(-.8,0.)+.17];cam.distance=3.2;cam.azimuth=95.;cam.elevation=-17.
   renderer.update_scene(d,camera=cam);renderer.scene.flags[mujoco.mjtRndFlag.mjRND_SHADOW]=False;rgb=renderer.render();im=Image.fromarray(rgb);draw=ImageDraw.Draw(im)
   draw.rectangle((0,0,1500,98),fill=(20,25,32))
   draw.text((24,13),f'当前 R1 最高档 Level 3｜{cn}｜'+('全景' if view=='overview' else '机器人比例近景'),font=font,fill=(244,247,251))
   draw.text((24,57),'MuJoCo 地形回放截图 · 根据 PhysX level3 实际网格的 5 cm 采样重建 · 地块 9 × 9 m',font=small,fill=(180,197,210))
   name=f'r1_level3_{family}_{view}.png';im.save(out/name)
   records.append(dict(file=name,bytes=(out/name).stat().st_size,sha256=hashlib.sha256((out/name).read_bytes()).hexdigest(),family=family,terrain_level=3,camera=dict(distance=cam.distance,azimuth=cam.azimuth,elevation=cam.elevation,lookat=cam.lookat.tolist()),scope='Local MuJoCo rendering of existing5cm PhysX level3 heightfield samples; original MOD4 robot and parent pose; not a live PhysX training screenshot'))
 sim.close()
(out/'evidence/SCREENSHOT_MANIFEST.json').write_text(json.dumps(dict(images=records,terrain_source=str(old/'evidence/terrain_heightfields.npz'),terrain_sha256=hashlib.sha256((out/'evidence/terrain_heightfields.npz').read_bytes()).hexdigest()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(output=str(out),images=[x['file'] for x in records]),ensure_ascii=False))
