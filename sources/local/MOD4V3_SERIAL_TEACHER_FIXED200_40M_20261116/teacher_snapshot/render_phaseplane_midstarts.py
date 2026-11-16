"""Render stored actual teacher states; rendering never runs control or changes scores."""
from pathlib import Path
import json,sys
import numpy as np,mujoco as mj
from PIL import Image,ImageDraw,ImageFont
import imageio.v2 as imageio
P=Path(__file__).resolve().parent
OUT=P/'replays_step200_phaseplane';OUT.mkdir(exist_ok=True)
cases=[('step200_capture_phaseplane_minus30','start_minus030_FAIL'),('step200_capture_phaseplane_plus30','start_plus030_PASS')]
font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',19)
for name,label in cases:
 src=P/'tests'/name;data=np.load(src/'trace.npz');trace=data['trace'];m=mj.MjModel.from_xml_path(str(src/'scene.xml'));d=mj.MjData(m);m.vis.global_.offwidth=960;m.vis.global_.offheight=540;m.vis.headlight.ambient[:]=.5;m.vis.headlight.diffuse[:]=.8;m.vis.headlight.specular[:]=.1
 camera=mj.MjvCamera();camera.lookat[:]=[1.25,0.,.30];camera.distance=2.2;camera.azimuth=105.;camera.elevation=-16.
 renderer=mj.Renderer(m,height=540,width=960);result=json.loads((src/'RESULT.json').read_text());video=OUT/(label+'.mp4')
 with imageio.get_writer(video,fps=25,codec='libx264',quality=8,macro_block_size=2)as writer:
  for i in range(0,len(trace),2):
   d.qpos[:]=data['qpos'][i];d.qvel[:]=data['qvel'][i];mj.mj_forward(m,d);camera.lookat[:]=[.5*d.qpos[0]+.65,0.,.30];renderer.update_scene(d,camera=camera);img=Image.fromarray(renderer.render());draw=ImageDraw.Draw(img);draw.rectangle((0,0,960,76),fill=(15,22,30))
   draw.text((12,8),f'MOD4v3 native LQR/VMC | 200 mm | command 0.47 m/s | {label} | teacher only',font=font,fill=(255,255,255));draw.text((12,38),f't={trace[i,0]:5.2f}s   phase={data["phases"][i,0]}   pitch={np.rad2deg(trace[i,5]):6.2f} deg   yaw={np.rad2deg(trace[i,6]):6.2f} deg',font=font,fill=(225,235,244));writer.append_data(np.asarray(img))
   if abs(trace[i,0]-4.8)<.03:img.save(OUT/(label+'.png'))
 renderer.close();print(video,video.stat().st_size,flush=True)
